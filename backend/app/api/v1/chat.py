"""Chat API endpoints with real OpenAI integration, RAG, and enhanced error handling."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import logging

from app.agents.nlu.nlu_agent import nlu_agent
from app.agents.knowledge.rag_agent import knowledge_agent
from app.agents.sql.text2sql_agent import sql_agent
from app.core.llm.openai_client_v3 import openai_client_v3 as openai_client

logger = logging.getLogger(__name__)

router = APIRouter()


# Low confidence threshold
LOW_CONFIDENCE_THRESHOLD = 0.6


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[str]] = None
    products: Optional[List[Dict[str, Any]]] = None
    database_results: Optional[Dict[str, Any]] = None
    needs_clarification: Optional[bool] = False
    clarifying_question: Optional[str] = None
    handoff_available: Optional[bool] = False


class ConversationHistory(BaseModel):
    """Conversation history model."""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


# In-memory session storage (replace with Redis in production)
sessions: Dict[str, Dict] = {}


def get_session_messages(session_id: str) -> List[Dict]:
    """Get messages for a session."""
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [
                {
                    "role": "assistant",
                    "content": "Hello! I'm your dress design assistant. How can I help you today? I can help you find dresses, get style recommendations, learn about fabric care, and more!",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    return sessions[session_id]["messages"]


def generate_clarifying_question(intent: str) -> str:
    """Generate a clarifying question based on intent."""
    questions = {
        "dress_design": "What occasion are you designing for? (wedding, party, casual, office)",
        "product_search": "What type of product are you looking for?",
        "fabric_care": "What type of fabric is the garment made of?",
        "pricing": "Which specific product are you asking about?",
        "general": "Could you please provide more details about what you're looking for?"
    }
    return questions.get(intent, questions["general"])


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the chatbot with NLU, RAG, and OpenAI."""
    try:
        # Generate or get session ID
        session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
        
        # Get conversation history
        messages = get_session_messages(session_id)
        
        # Step 1: NLU - Extract intent and entities using OpenAI
        try:
            nlu_result = await nlu_agent.process(
                message=request.message,
                conversation_history=messages
            )
            logger.info(f"NLU Result: {nlu_result}")
        except Exception as nlu_error:
            logger.error(f"NLU processing failed: {nlu_error}")
            # Fallback to basic extraction
            nlu_result = {
                "intent": "general",
                "confidence": 0.3,
                "entities": [],
                "context": ""
            }
        
        intent = nlu_result.get("intent", "general")
        entities = nlu_result.get("entities", [])
        confidence = nlu_result.get("confidence", 0.5)
        context = nlu_result.get("context", "")
        
        logger.info(f"NLU Result: intent={intent}, entities={entities}, confidence={confidence}")
        
        # Step 2: Handle low confidence scenarios
        needs_clarification = False
        clarifying_question = None
        handoff_available = False
        
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            logger.info(f"Low confidence ({confidence}) detected, generating clarifying question")
            needs_clarification = True
            clarifying_question = generate_clarifying_question(intent)
            handoff_available = True
        
        # Step 3: Route to appropriate agent
        response_text = ""
        sources = []
        products = []
        database_results = {}
        
        # Design keywords (these are truly design-specific, not product-related)
        design_keywords = [
            "create a design", "new design", "design a", "design help",
            "i want to design", "help me design", "start a design",
            "make a design", "design something"
        ]
        
        message_lower = request.message.lower()
        is_design_query = intent in ["design_help", "recommendation", "style_advice"] or any(kw in message_lower for kw in design_keywords)
        
        if is_design_query:
            logger.info(f"Routing to Design Agent (design_help: {intent})")
            route = "design"
        elif intent in ["database_query", "product_info", "inventory_check"]:
            # Product/Database query → ALWAYS route to SQL (ignore RAG)
            logger.info(f"[ROUTING] Product query detected → routing to SQL")
            route = "sql"
        elif intent in ["knowledge_query", "care", "comparison"]:
            # Knowledge query → Check RAG
            logger.info(f"[ROUTING] Knowledge query → checking RAG for content")
            try:
                rag_for_routing = await knowledge_agent.process({
                    "query": request.message,
                    "filters": {},
                    "conversation_history": messages
                })
                rag_sources = rag_for_routing.get("sources", [])
                rag_retrieved_count = rag_for_routing.get("retrieved_count", 0)
                rag_has_content = len(rag_sources) > 0 and rag_retrieved_count > 0
                
                if rag_has_content:
                    route = "knowledge"
                    rag_result = rag_for_routing
                else:
                    # No RAG content found
                    if confidence >= LOW_CONFIDENCE_THRESHOLD:
                        route = "general"
                    else:
                        # Low confidence + no content = ask for clarification
                        needs_clarification = True
                        clarifying_question = "I couldn't find specific information about that. " + generate_clarifying_question(intent)
                        route = "clarification"
            except Exception as e:
                logger.error(f"[ROUTING] RAG error: {e}")
                route = "general"
        else:
            # General query → Route to General
            logger.info(f"[ROUTING] General query → routing to general")
            route = "general"
        
        logger.info(f"[ROUTING] Final route: {route} (intent: {intent}, confidence: {confidence})")
        
        # Process based on route
        if route == "clarification":
            response_text = clarifying_question or "Could you please clarify what you're looking for?"
        elif route == "design":
            try:
                rag_result = await knowledge_agent.process({
                    "query": request.message,
                    "filters": {},
                    "conversation_history": messages
                })
                response_text = rag_result.get("response", "I'd be happy to help you create a new design!")
                sources = rag_result.get("sources", [])
                logger.info(f"Design Result: {len(sources)} sources")
            except Exception as e:
                logger.error(f"Design agent error: {e}")
                response_text = "I'd be happy to help you create a new design! What type of dress are you thinking of?"
        
        elif route == "sql":
            try:
                sql_result = await sql_agent.execute(
                    natural_query=request.message,
                    entities=entities
                )
            except Exception as e:
                logger.error(f"SQL agent execution failed: {e}")
                sql_result = {"error": str(e), "results": [], "row_count": 0}
            
            if "error" not in sql_result:
                database_results = {
                    "sql_query": sql_result.get("sql_query", ""),
                    "results": sql_result.get("results", []),
                    "columns": sql_result.get("columns", []),
                    "row_count": sql_result.get("row_count", 0),
                    "intent": sql_result.get("intent", "")
                }
                
                # Format database results into readable response
                if sql_result.get("results"):
                    result_count = sql_result.get("row_count", 0)
                    response_text = f"I found {result_count} result(s) from the database:\n\n"
                    
                    for idx, row in enumerate(sql_result.get("results", [])[:5], 1):
                        row_text = ", ".join([f"{k}: {v}" for k, v in row.items() if v is not None])
                        response_text += f"{idx}. {row_text}\n"
                    
                    if result_count > 5:
                        response_text += f"...and {result_count - 5} more results"
                else:
                    response_text = "I couldn't find any matching results in the database."
            else:
                response_text = f"Database query error: {sql_result.get('error', 'Unknown error')}"
                
            logger.info(f"SQL Result: {sql_result.get('row_count', 0)} rows")
        
        elif route == "knowledge":
            # Use RAG Knowledge Agent result (already fetched in routing)
            logger.info(f"Routing to Knowledge Agent (intent: {intent})")
            
            try:
                rag_result = await knowledge_agent.process({
                    "query": request.message,
                    "filters": {},
                    "conversation_history": messages
                })
                
                logger.info(f"[CHAT-RAG] Result: success={rag_result.get('success', False)}, sources={rag_result.get('sources', [])}")
                
                response_text = rag_result.get("response", "I couldn't find that information.")
                sources = rag_result.get("sources", [])
                
                # Extract products from retrieved documents
                retrieved_count = rag_result.get("retrieved_count", 0)
                if retrieved_count > 0:
                    products = [
                        {"id": s, "name": s, "description": "Product from knowledge base"}
                        for s in sources
                    ]
                
                logger.info(f"RAG Result: {len(sources)} sources, {len(products)} products found")
            except Exception as e:
                logger.error(f"RAG agent error: {e}")
                response_text = "I couldn't find that information in my knowledge base. Could you try rephrasing your question?"
        
        else:  # route == "general"
            # Use general OpenAI response generation with fallback
            logger.info(f"Using General OpenAI response (NLU intent: {intent})")
            try:
                conversation_history = [msg for msg in messages[-10:]]
                
                response_text = await openai_client.generate_response(
                    user_message=request.message,
                    intent=intent,
                    entities=entities,
                    context=context,
                    conversation_history=conversation_history
                )
            except Exception as e:
                logger.warning(f"OpenAI response generation failed: {e}")
                response_text = f"I understand you're asking about '{request.message}'. "
                if entities:
                    entity_text = ", ".join([f"{e.get('type')}: {e.get('value')}" for e in entities])
                    response_text += f"I found some {entity_text} items that might interest you. "
                response_text += "For detailed information, please try asking about specific products or browse our catalog."
        
        # Add clarifying question if needed
        if clarifying_question and not response_text.endswith("?"):
            response_text = f"{response_text} {clarifying_question}"
        
        # Store user message
        messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "intent": intent,
                "entities": entities,
                "confidence": confidence
            }
        })
        
        # Store assistant response
        messages.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "intent": intent,
                "entities": entities,
                "sources": sources,
                "products": products,
                "database_results": database_results,
                "needs_clarification": needs_clarification,
                "handoff_available": handoff_available
            }
        })
        
        # Update session
        sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            intent=intent,
            entities=entities,
            sources=sources,
            products=products,
            database_results=database_results,
            needs_clarification=needs_clarification,
            clarifying_question=clarifying_question,
            handoff_available=handoff_available
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        error_response = (
            "I apologize, but I encountered an unexpected error. "
            "Could you please try rephrasing your question?"
        )
        return ChatResponse(
            response=error_response,
            session_id=request.session_id or "error-session",
            needs_clarification=True,
            clarifying_question="Would you like to rephrase your question?"
        )


@router.post("/stream")
async def stream_message(request: ChatRequest):
    """Stream a response from the chatbot."""
    return {"message": "Streaming endpoint - to be implemented"}


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    messages = get_session_messages(session_id)
    session_data = sessions.get(session_id, {})
    
    return ConversationHistory(
        session_id=session_id,
        messages=[ChatMessage(**msg) for msg in messages],
        created_at=datetime.fromisoformat(session_data.get("created_at", datetime.utcnow().isoformat())),
        updated_at=datetime.fromisoformat(session_data.get("updated_at", datetime.utcnow().isoformat()))
    )


@router.delete("/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session."""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "cleared", "session_id": session_id}


@router.post("/intent")
async def detect_intent(message: str):
    """Detect intent from user message."""
    result = await nlu_agent.process(message)
    return {
        "intent": result.get("intent"),
        "confidence": result.get("confidence"),
        "entities": result.get("entities", [])
    }


@router.get("/health")
async def health_check():
    """Check chat service health."""
    # Check NLU agent (sync method)
    try:
        nlu_health = nlu_agent.health_check()
    except Exception as e:
        nlu_health = {"status": "error", "error": str(e)}
    
    # Check Knowledge/RAG agent (async method)
    try:
        knowledge_health = await knowledge_agent.health_check()
    except Exception as e:
        knowledge_health = {"status": "error", "error": str(e)}
    
    # Check OpenAI client (simple API key check)
    try:
        from app.config import settings
        openai_health = {
            "status": "ok" if settings.openai_api_key else "error",
            "api_key_configured": bool(settings.openai_api_key),
            "model": settings.openai_model
        }
    except Exception as e:
        openai_health = {"status": "error", "error": str(e)}
    
    return {
        "status": "healthy",
        "nlu": nlu_health,
        "knowledge": knowledge_health,
        "openai": openai_health,
        "active_sessions": len(sessions)
    }
