"""RAG Agent - Retrieval-Augmented Generation for dress products."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import json

from app.agents.base import Agent, AgentConfig, AgentType
from app.agents.knowledge.vector_store import VectorStore, Document
from app.core.llm.openai_client_v3 import openai_client_v3
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """Result from RAG retrieval."""
    success: bool
    retrieved_documents: List[Document]
    context: str
    sources: List[str]
    message: str = ""


class RAGConfig(AgentConfig):
    """RAG Agent configuration."""
    max_context_docs: int = 10
    min_similarity_score: float = 0.0  # Set to 0 to always use retrieved results
    enable_hybrid_search: bool = True


class RAGAgent(Agent):
    """Retrieval-Augmented Generation Agent for dress products.
    
    This agent:
    1. Loads product data from PostgreSQL
    2. Creates embeddings and stores in ChromaDB
    3. Retrieves relevant products based on user queries
    4. Generates contextual responses
    """

    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize RAG agent."""
        rag_config = config or RAGConfig(
            name="RAG Agent",
            agent_type=AgentType.RAG,
            description="Retrieves product information and generates contextual responses"
        )
        super().__init__(rag_config)

        self.vector_store = VectorStore(
            host=settings.chromadb_host,
            port=settings.chromadb_port
        )
        self.llm = openai_client_v3
        self._db_pool = None

    async def initialize(self):
        """Initialize RAG agent and seed ChromaDB."""
        if self._initialized:
            return

        # Initialize vector store
        await self.vector_store.initialize()

        # Seed vector store with products from PostgreSQL
        await self._seed_products()

        self._initialized = True
        logger.info("RAG Agent initialized successfully")

    async def _get_db_pool(self):
        """Get async PostgreSQL connection pool."""
        if self._db_pool is None:
            import asyncpg
            self._db_pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_size=2,
                max_size=10
            )
        return self._db_pool

    async def _seed_products(self):
        """Load products from PostgreSQL and seed ChromaDB."""
        try:
            pool = await self._get_db_pool()

            # Check if products already exist
            existing_count = await self.vector_store.count()
            if existing_count > 0:
                logger.info(f"ChromaDB already has {existing_count} documents")
                return

            # Fetch all products from PostgreSQL
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT id, name, description, category, color, 
                             fabric_type as fabric, price, occasion, 
                             body_type_suitable, availability, image_url
                        FROM products"""
                )

            if not rows:
                logger.warning("No products found in PostgreSQL")
                return

            # Create documents for each product
            documents = []
            for row in rows:
                # Create rich content for embedding
                content = self._create_product_content(dict(row))
                metadata = {
                    "product_id": str(row["id"]),
                    "name": row["name"],
                    "category": row["category"],
                    "color": row["color"],
                    "fabric": row["fabric"],
                    "price": float(row["price"]) if row["price"] else 0,
                    "occasion": row["occasion"] or "",
                    "body_type": str(row.get("body_type_suitable", [])),
                    "available": row.get("availability", True)
                }

                doc = Document(
                    id=f"product_{row['id']}",
                    content=content,
                    metadata=metadata
                )
                documents.append(doc)

            # Add to vector store
            if documents:
                await self.vector_store.add_documents(documents)
                logger.info(f"Seeded {len(documents)} products into ChromaDB")

        except Exception as e:
            logger.error(f"Failed to seed products: {e}")
            raise

    def _create_product_content(self, product: Dict) -> str:
        """Create rich searchable content for a product."""
        parts = [
            f"Product: {product.get('name', 'Unknown')}",
            f"Category: {product.get('category', 'General')}",
            f"Color: {product.get('color', 'N/A')}",
            f"Fabric: {product.get('fabric', 'N/A')}",
            f"Price: ${product.get('price', 0) if product.get('price') else 0}",
            f"Occasion: {product.get('occasion', 'Any')}",
        ]

        if product.get('description'):
            parts.append(f"Description: {product['description']}")

        if product.get('body_type_suitable'):
            body_types = product['body_type_suitable']
            if isinstance(body_types, list):
                parts.append(f"Body Types: {', '.join(body_types)}")
            else:
                parts.append(f"Body Types: {body_types}")

        if product.get('availability') is not None:
            avail = "Available" if product['availability'] else "Out of Stock"
            parts.append(f"Availability: {avail}")

        return " | ".join(parts)

    async def retrieve(self, query: str, filters: Optional[Dict] = None) -> RAGResult:
        """Retrieve relevant product information."""
        try:
            logger.info(f"[RAG] Searching for: '{query}' with {self.config.max_context_docs} results")
            
            # Search vector store
            results = await self.vector_store.search(
                query=query,
                n_results=self.config.max_context_docs,
                filters=filters
            )
            
            logger.info(f"[RAG] Found {len(results.documents)} documents, {len(results.distances)} distances")
            
            if not results.documents:
                logger.warning(f"[RAG] No documents found in ChromaDB")
                return RAGResult(
                    success=False,
                    retrieved_documents=[],
                    context="",
                    sources=[],
                    message="No matching information found"
                )
            
            # Log distances
            if results.distances:
                logger.info(f"[RAG] Distances: {results.distances[:5]}...")
            
            # Don't filter by similarity - use all retrieved documents
            filtered_docs = results.documents
            
            logger.info(f"[RAG] Using {len(filtered_docs)} documents for context")
            
            # Build context
            context_parts = []
            sources = []
            for doc in filtered_docs[:self.config.max_context_docs]:
                context_parts.append(doc.content)
                sources.append(doc.metadata.get("name", doc.id))

            context = "\n\n".join(context_parts)

            return RAGResult(
                success=True,
                retrieved_documents=filtered_docs,
                context=context,
                sources=sources,
                message=f"Found {len(filtered_docs)} relevant documents"
            )

        except Exception as e:
            logger.error(f"[RAG] Retrieval failed: {e}")
            import traceback
            logger.error(f"[RAG] Traceback: {traceback.format_exc()}")
            return RAGResult(
                success=False,
                retrieved_documents=[],
                context="",
                sources=[],
                message=f"Error retrieving information: {str(e)}"
            )

    async def generate_response(
        self,
        query: str,
        retrieved_context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate a response using the retrieved context."""
        try:
            # Build prompt with context
            prompt = self._build_prompt(query, retrieved_context, conversation_history)

            # Generate response using OpenAI chat
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm.chat(messages, system_prompt="You are a helpful assistant.")

            return response.text

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"I apologize, but I encountered an error generating a response: {str(e)}"

    def _build_prompt(
        self,
        query: str,
        context: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        """Build the RAG prompt."""
        system_prompt = """You are a helpful fashion assistant specializing in dress products.
Use the provided product information to answer customer questions accurately.
Be friendly, professional, and helpful.
If you don't have enough information, say so honestly.

Product Information:
{context}

Previous conversation:
{history}

Current question: {query}

Your response:"""

        history_text = ""
        if history:
            for msg in history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"- {role}: {content}\n"

        return system_prompt.format(
            context=context,
            history=history_text,
            query=query
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user query through RAG."""
        query = input_data.get("query", "")
        filters = input_data.get("filters", {})
        conversation_history = input_data.get("conversation_history", [])

        if not query:
            return {"success": False, "error": "No query provided"}

        # Initialize if needed
        if not self._initialized:
            await self.initialize()

        # Retrieve relevant products
        rag_result = await self.retrieve(query, filters)

        # Even if RAG fails or returns no results, use LLM to generate helpful response
        if not rag_result.success:
            logger.info(f"RAG retrieval failed/no results for query: {query}, using LLM fallback")
            # Use LLM directly to generate a helpful response
            fallback_response = await self._generate_fallback_response(
                query, conversation_history
            )
            return {
                "success": True,  # Consider it success since we have LLM fallback
                "response": fallback_response,
                "sources": [],
                "retrieved_count": 0,
                "is_fallback": True
            }

        # Generate response with RAG context
        prompt = self._build_prompt(
            query,
            rag_result.context,
            conversation_history
        )
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.chat(messages, system_prompt="You are a helpful assistant.")

        return {
            "success": True,
            "response": response.text,
            "sources": rag_result.sources,
            "retrieved_count": len(rag_result.retrieved_documents)
        }

    async def _generate_fallback_response(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate a helpful response when RAG has no documents."""
        # Build a comprehensive prompt for general Q&A
        system_prompt = """You are a helpful assistant that answers questions based on uploaded documents and general knowledge.

Your goal is to:
- Answer questions accurately and helpfully
- If you don't know the answer, say so honestly
- Use your general knowledge when document information is not available
- Be friendly, professional, and conversational

Guidelines:
- Provide detailed, accurate responses
- If the question is about an uploaded document, acknowledge if you cannot find that information
- Ask follow-up questions if needed
- Share relevant general knowledge

Current question: {query}

Your response:"""

        # Build messages list
        messages = [{"role": "user", "content": query}]
        
        # Format history if provided
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"- {role}: {content}\n"
        
        try:
            # Use the chat method with system prompt
            response = await self.llm.chat(
                messages=messages,
                system_prompt=system_prompt.format(query=query, history=history_text),
                max_tokens=500
            )
            return response.text
        except Exception as e:
            logger.error(f"Fallback response generation failed: {e}")
            return self._get_simple_fallback(query)

    def _get_simple_fallback(self, query: str) -> str:
        """Provide a simple fallback response when LLM fails."""
        query_lower = query.lower()
        
        # Design-related queries
        if any(word in query_lower for word in ['design', 'create', 'make', 'new']):
            return """I'd be happy to help you create a new design! Let me ask you a few questions to understand your preferences:

1. **What's the occasion?** (wedding, party, casual, office, festival)
2. **What's your preferred style?** (traditional, modern, fusion, western)
3. **Any fabric preferences?** (silk, cotton, chiffon, georgette, linen)
4. **What colors do you prefer?**
5. **What's your body type?** (petite, plus size, hourglass, etc.)

Please share your preferences so I can help you design the perfect outfit!"""
        
        # Fabric-related queries
        if any(word in query_lower for word in ['fabric', 'material', 'silk', 'cotton', 'rayon']):
            return """I can help you with fabric information! Here are some popular fabric choices for dresses:

• **Silk** - Luxurious, elegant, perfect for formal occasions. Requires dry cleaning.
• **Cotton** - Comfortable, breathable, great for casual wear. Easy to maintain.
• **Chiffon** - Light, flowy, romantic. Perfect for parties and weddings.
• **Georgette** - Similar to chiffon but more opaque. Great for draping.
• **Rayon** - Soft, comfortable, mimics silk. Good for everyday wear.
• **Linen** - Breathable, cool, perfect for summer. Wrinkles easily.

Do you have specific questions about any fabric?"""
        
        # Style-related queries
        if any(word in query_lower for word in ['style', 'wearing', 'pair', 'match']):
            return """Here are some style tips for your outfit:

• **Traditional** - Pair with gold jewelry, juttis, and a matching clutch
• **Modern** - Add statement earrings, sleek heels, and a clutch bag
• **Fusion** - Mix traditional and western elements for a unique look
• **Casual** - Simple jewelry, comfortable flats or sandals

What type of event are you dressing for? I can give more specific recommendations!"""
        
        # Care/wash related
        if any(word in query_lower for word in ['wash', 'clean', 'care', 'maintain', 'store']):
            return """Here are general care instructions for dresses:

• Always check the care label first!
• Silk and delicate fabrics: Dry clean or hand wash in cold water
• Cotton: Machine wash cold, tumble dry low
• Store in a cool, dry place
• Use garment bags for long-term storage
• Avoid direct sunlight to prevent fading

Do you have questions about caring for a specific fabric?"""
        
        # Default helpful response
        return """I'd be happy to help you with that! Could you provide more details about what you're looking for?

You can ask me about:
• Dress design and customization
• Fabric information and care
• Style recommendations
• Matching accessories
• Color combinations

Please share more details so I can assist you better!"""

    async def add_product(self, product: Dict) -> bool:
        """Add a new product to the vector store."""
        try:
            content = self._create_product_content(product)
            doc = Document(
                id=f"product_{product.get('id')}",
                content=content,
                metadata={
                    "product_id": str(product.get("id")),
                    "name": product.get("name", ""),
                    "category": product.get("category", ""),
                    "color": product.get("color", ""),
                    "fabric": product.get("fabric", ""),
                    "price": float(product.get("price", 0)) if product.get("price") else 0,
                    "occasion": product.get("occasion", "")
                }
            )

            await self.vector_store.add_documents([doc])
            return True

        except Exception as e:
            logger.error(f"Failed to add product: {e}")
            return False

    async def close(self):
        """Clean up resources."""
        if self.vector_store:
            await self.vector_store.close()
        if self._db_pool:
            await self._db_pool.close()


# Export singleton instance (alias for knowledge_agent)
rag_agent = RAGAgent()
knowledge_agent = rag_agent  # Alias for API compatibility
