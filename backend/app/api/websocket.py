"""
WebSocket Endpoint for Real-time Chat
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from typing import Optional
import json
from datetime import datetime
import asyncio

from app.core.auth.jwt_handler import verify_token
from app.core.websocket.connection_manager import ws_manager
from app.agents import get_agent_response

router = APIRouter(prefix="/ws", tags=["WebSocket"])

async def get_current_user_from_token(token: str) -> dict:
    """Verify JWT token and return user info."""
    try:
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {
            "id": payload.get("sub") or payload.get("user_id"),
            "email": payload.get("email"),
            "name": payload.get("name"),
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@router.websocket("/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: str = Query(default="default")
):
    """
    WebSocket endpoint for real-time chat.
    
    Query Parameters:
    - token: JWT authentication token
    - session_id: Chat session ID (optional, defaults to "default")
    
    Message Types:
    - send: Send a message to the AI
    - typing: Update typing status
    - stop: Stop AI response generation
    """
    # Authenticate user
    try:
        current_user = await get_current_user_from_token(token)
        user_id = current_user["id"]
    except HTTPException as e:
        await websocket.close(code=4001, reason=str(e.detail))
        return
    
    # Connect
    await ws_manager.connect(websocket, user_id, session_id)
    
    # Notify others in session
    await ws_manager.broadcast_to_session({
        "type": "user_joined",
        "user_id": user_id,
        "user_name": current_user.get("name", "User"),
        "timestamp": datetime.utcnow().isoformat(),
        "online_users": ws_manager.get_online_users(session_id),
    }, session_id, exclude_user=user_id)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to real-time chat",
        "session_id": session_id,
        "user_id": user_id,
        "online_users": ws_manager.get_online_users(session_id),
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "message")
                
                if message_type == "message" or message_type == "send":
                    # Handle chat message
                    user_message = message_data.get("content", "")
                    use_rag = message_data.get("use_rag", True)
                    
                    if not user_message.strip():
                        continue
                    
                    # Send acknowledgment
                    await websocket.send_json({
                        "type": "message_received",
                        "content": user_message,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    
                    # Send "AI is thinking" indicator
                    await websocket.send_json({
                        "type": "thinking",
                        "status": True,
                        "message": "AI is thinking...",
                    })
                    
                    # Process with AI agent (non-blocking)
                    try:
                        response = await get_agent_response(
                            message=user_message,
                            user_id=user_id,
                            use_rag=use_rag,
                        )
                        
                        # Send response
                        await websocket.send_json({
                            "type": "ai_response",
                            "content": response,
                            "timestamp": datetime.utcnow().isoformat(),
                        })
                        
                    except Exception as agent_error:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error processing message: {str(agent_error)}",
                        })
                    
                    # Clear thinking indicator
                    await websocket.send_json({
                        "type": "thinking",
                        "status": False,
                    })
                
                elif message_type == "typing":
                    # Handle typing indicator
                    is_typing = message_data.get("is_typing", False)
                    await ws_manager.send_typing_indicator(user_id, session_id, is_typing)
                
                elif message_type == "stop":
                    # Handle stop request
                    await websocket.send_json({
                        "type": "stopped",
                        "message": "AI response stopped",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
                elif message_type == "ping":
                    # Handle ping (keep-alive)
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
                else:
                    # Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Disconnect and notify
        await ws_manager.disconnect(websocket, user_id)
        
        await ws_manager.broadcast_to_session({
            "type": "user_left",
            "user_id": user_id,
            "user_name": current_user.get("name", "User"),
            "timestamp": datetime.utcnow().isoformat(),
            "online_users": ws_manager.get_online_users(session_id),
        }, session_id)

@router.websocket("/session/{session_id}")
async def websocket_session(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for a specific chat session.
    Alternative endpoint with session in path instead of query.
    """
    # Authenticate user
    try:
        current_user = await get_current_user_from_token(token)
        user_id = current_user["id"]
    except HTTPException as e:
        await websocket.close(code=4001, reason=str(e.detail))
        return
    
    # Delegate to main chat handler
    await websocket_chat(websocket, token, session_id)

@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Get status of a chat session."""
    return {
        "session_id": session_id,
        "online_users": ws_manager.get_online_users(session_id),
        "total_connections": ws_manager.get_connection_count(),
    }

@router.get("/online-users")
async def get_online_users():
    """Get all online users."""
    return {
        "online_users": ws_manager.get_online_users(),
        "total_connections": ws_manager.get_connection_count(),
    }
