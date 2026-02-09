// WebSocket Service for Real-time Chat
// Uses native WebSocket API with React hooks

import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = 'http://localhost:8001/api/ws/chat';

export interface WebSocketMessage {
  type: string;
  content?: string;
  message?: string;
  user_id?: string;
  user_name?: string;
  timestamp?: string;
  session_id?: string;
  online_users?: string[];
  status?: boolean;
  thinking?: boolean;
  error?: string;
  use_rag?: boolean;
  is_typing?: boolean;
}

type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Set<MessageHandler> = new Set();
  private isConnecting = false;

  connect(token: string, sessionId: string = 'default'): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'));
        return;
      }

      this.isConnecting = true;
      
      try {
        this.ws = new WebSocket(`${WS_URL}?token=${token}&session_id=${sessionId}`);
        
        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.notifyHandlers(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.isConnecting = false;
          this.ws = null;
          
          // Attempt reconnect if not a clean close
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect(token, sessionId);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };
        
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private scheduleReconnect(token: string, sessionId: string) {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      this.connect(token, sessionId).catch(console.error);
    }, delay);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.messageHandlers.clear();
    this.reconnectAttempts = 0;
  }

  send(message: WebSocketMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  sendMessage(content: string, useRag: boolean = true) {
    this.send({
      type: 'message',
      content,
      use_rag: useRag,
    });
  }

  sendTyping(isTyping: boolean) {
    this.send({
      type: 'typing',
      is_typing: isTyping,
    });
  }

  sendStop() {
    this.send({
      type: 'stop',
    });
  }

  ping() {
    this.send({
      type: 'ping',
    });
  }

  subscribe(handler: MessageHandler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  private notifyHandlers(message: WebSocketMessage) {
    this.messageHandlers.forEach(handler => handler(message));
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get readyState(): number | null {
    return this.ws?.readyState ?? null;
  }
}

// Singleton instance
export const wsService = new WebSocketService();

// React hook for WebSocket
export const useWebSocket = (token: string | null, sessionId: string = 'default') => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const connectionPromise = useRef<Promise<void> | null>(null);

  const connect = useCallback(async () => {
    if (!token) return;
    
    if (wsService.isConnected) {
      setIsConnected(true);
      return;
    }

    try {
      connectionPromise.current = wsService.connect(token, sessionId);
      await connectionPromise.current;
      setIsConnected(true);
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      setIsConnected(false);
    }
  }, [token, sessionId]);

  const disconnect = useCallback(() => {
    wsService.disconnect();
    setIsConnected(false);
    setOnlineUsers([]);
  }, []);

  const sendMessage = useCallback((content: string, useRag: boolean = true) => {
    wsService.sendMessage(content, useRag);
  }, []);

  const sendTyping = useCallback((isTyping: boolean) => {
    wsService.sendTyping(isTyping);
  }, []);

  const sendStop = useCallback(() => {
    wsService.sendStop();
  }, []);

  useEffect(() => {
    const unsubscribe = wsService.subscribe((message) => {
      setLastMessage(message);

      switch (message.type) {
        case 'connected':
        case 'user_joined':
          setOnlineUsers(message.online_users || []);
          break;
        case 'user_left':
          setOnlineUsers(message.online_users || []);
          break;
        case 'thinking':
          setIsThinking(message.status || false);
          break;
        case 'stopped':
          setIsThinking(false);
          break;
        case 'ai_response':
          setIsThinking(false);
          break;
        default:
          break;
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (token) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      if (!token) {
        disconnect();
      }
    };
  }, [token, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    onlineUsers,
    isThinking,
    connect,
    disconnect,
    sendMessage,
    sendTyping,
    sendStop,
  };
};

export default wsService;
