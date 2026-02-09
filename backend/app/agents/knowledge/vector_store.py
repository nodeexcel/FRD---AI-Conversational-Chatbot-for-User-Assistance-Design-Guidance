"""Real Vector Database implementation using ChromaDB HTTP Client (v1 API)."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import httpx

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document with embedding."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Search result with documents."""
    documents: List[Document]
    distances: List[float]
    total_count: int


class ChromaDBHttpClient:
    """HTTP client for ChromaDB server (v1 API)."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize HTTP client."""
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def heartbeat(self) -> bool:
        """Check if ChromaDB server is running."""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/heartbeat")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"ChromaDB heartbeat failed: {e}")
            return False

    async def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/collections")
            if response.status_code == 200:
                return [c["name"] for c in response.json()]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
        return []

    async def get_collection(self, name: str) -> Optional[Dict]:
        """Get collection by name."""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/collections/{name}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Collection not found: {e}")
        return None

    async def create_collection(self, name: str, metadata: Optional[Dict] = None) -> Dict:
        """Create a new collection."""
        # For ChromaDB 0.6.x, don't send metadata as it's causing issues
        payload = {"name": name}
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/collections",
            json=payload
        )
        if response.status_code == 201:
            return response.json()
        raise Exception(f"Failed to create collection: {response.text}")

    async def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Dict:
        """Get or create a collection."""
        collection = await self.get_collection(name)
        if collection:
            return collection
        return await self.create_collection(name, metadata)

    async def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """Add documents to a collection with embeddings using OpenAI."""
        # First get the collection to get its UUID
        collection = await self.get_collection(collection_name)
        if not collection:
            logger.error(f"Collection '{collection_name}' not found")
            return False
        
        collection_id = collection.get("id")
        logger.info(f"[VECTOR] Adding {len(documents)} documents to collection '{collection_name}' (ID: {collection_id})")
        
        # Create embeddings for documents using OpenAI
        embeddings_list = None
        try:
            from app.core.llm.openai_client_v3 import openai_client_v3
            embeddings_list = openai_client_v3.create_embeddings(documents)
            logger.debug(f"Created embeddings for {len(documents)} documents")
        except Exception as e:
            logger.warning(f"Could not create embeddings: {e}")
        
        payload = {
            "ids": ids,
            "documents": documents
        }
        if metadatas:
            payload["metadatas"] = metadatas
        if embeddings_list:
            payload["embeddings"] = embeddings_list
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/collections/{collection_id}/add",
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to add documents: {response.text}")
        else:
            logger.info(f"Successfully added {len(documents)} documents to ChromaDB")
        
        return response.status_code == 200

    async def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """Query a collection using its UUID."""
        # First get the collection to get its UUID
        logger.info(f"[VECTOR] Searching collection '{collection_name}' for {n_results} results")
        logger.info(f"[VECTOR] Query texts: {query_texts}")
        
        collection = await self.get_collection(collection_name)
        if not collection:
            logger.error(f"[VECTOR] Collection '{collection_name}' not found!")
            raise Exception(f"Collection '{collection_name}' not found")
        
        collection_id = collection.get("id")
        logger.info(f"[VECTOR] Collection ID: {collection_id}")
        
        # Create embeddings for query texts using OpenAI
        embeddings_list = None
        try:
            from app.core.llm.openai_client_v3 import openai_client_v3
            embeddings_list = openai_client_v3.create_embeddings(query_texts)
            logger.debug(f"Created embeddings using OpenAI: {len(embeddings_list)} vectors")
        except Exception as e:
            logger.warning(f"Could not create embeddings with OpenAI: {e}")
        
        payload = {
            "query_texts": query_texts,
            "n_results": n_results
        }
        
        if embeddings_list:
            payload["query_embeddings"] = embeddings_list
        
        if where:
            payload["where"] = where
            
        response = await self.client.post(
            f"{self.base_url}/api/v1/collections/{collection_id}/query",
            json=payload
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"[VECTOR] Query returned: {result.get('ids', [])}")
            return result
        raise Exception(f"Query failed: {response.text}")

    async def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        response = await self.client.delete(f"{self.base_url}/api/v1/collections/{name}")
        return response.status_code == 200

    async def count(self, collection_name: str) -> int:
        """Get document count in a collection using count API."""
        # First get the collection to get its UUID
        collection = await self.get_collection(collection_name)
        if not collection:
            return 0
        
        collection_id = collection.get("id")
        
        # Use count API
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/collections/{collection_id}/count")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback: try to get count from metadata
        return collection.get("document_count", 0)


class VectorStore:
    """ChromaDB HTTP-based vector store for RAG."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize vector store."""
        self.host = host
        self.port = port
        self.client = None
        self.collection_name = "dress_products"
        self._initialized = False

    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        if self._initialized:
            return

        try:
            # Create HTTP client
            self.client = ChromaDBHttpClient(host=self.host, port=self.port)

            # Check if server is running
            if not await self.client.heartbeat():
                raise Exception("ChromaDB server is not responding")

            # Get or create collection
            collection = await self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Dress product knowledge base"}
            )

            self._initialized = True
            logger.info(f"Vector store connected to ChromaDB at {self.host}:{self.port}")

        except ImportError:
            logger.error("httpx not installed. Install with: pip install httpx")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

    async def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        if not self._initialized:
            await self.initialize()

        if not documents:
            return

        # Prepare data for ChromaDB
        ids = []
        contents = []
        metadatas = []

        for doc in documents:
            ids.append(doc.id)
            contents.append(doc.content)
            metadatas.append(doc.metadata)

        # Add to collection
        success = await self.client.add_documents(
            collection_name=self.collection_name,
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )

        if success:
            logger.info(f"Added {len(documents)} documents to vector store")
        else:
            logger.error("Failed to add documents to ChromaDB")

    async def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, str]] = None
    ) -> SearchResult:
        """Search for similar documents."""
        if not self._initialized:
            await self.initialize()

        # Prepare where clause for filters
        where = None
        if filters:
            where = {k: v for k, v in filters.items() if v}

        # Query
        results = await self.client.query(
            collection_name=self.collection_name,
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        # Parse results
        documents = []
        distances = []

        # Handle v1 API response format
        if results.get("ids") and results["ids"][0]:
            for idx, doc_id in enumerate(results["ids"][0]):
                doc = Document(
                    id=doc_id,
                    content=results["documents"][0][idx] if results.get("documents") and results["documents"][0] else "",
                    metadata=results["metadatas"][0][idx] if results.get("metadatas") and results["metadatas"][0] else {}
                )
                documents.append(doc)
                distance = results["distances"][0][idx] if results.get("distances") and results["distances"][0] else 0.0
                distances.append(distance)

        return SearchResult(
            documents=documents,
            distances=distances,
            total_count=len(documents)
        )

    async def delete_all(self):
        """Delete all documents from collection."""
        if not self._initialized:
            await self.initialize()

        # Recreate collection to delete all documents
        try:
            await self.client.delete_collection(self.collection_name)
        except:
            pass
        await self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Dress product knowledge base"}
        )
        logger.info("Deleted all documents from vector store")

    async def count(self) -> int:
        """Get document count."""
        if not self._initialized:
            await self.initialize()

        return await self.client.count(self.collection_name)

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts using sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer

            # Use a lightweight model for embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()

        except ImportError:
            logger.error("sentence-transformers not installed")
            raise

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.close()


# Export singleton instance
vector_store = VectorStore(host="localhost", port=8000)
