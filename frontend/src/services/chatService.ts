// Chat API service with RAG and Translation support
import axios from 'axios';
import { Message, Entity } from '../types';
import { translationService } from './translationService';

const API_URL = 'http://localhost:8001/api/chat';

export interface ChatRequest {
  message: string;
  session_id?: string;
  context?: Record<string, unknown>;
  language?: string;
  avatar?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  intent?: string;
  entities?: Entity[];
  sources?: Array<{
    title: string;
    relevance: number;
    id: string;
  }>;
  products?: Array<{
    id: string;
    title: string;
    description: string;
    relevance: number;
  }>;
  database_results?: {
    sql_query: string;
    results: Array<Record<string, unknown>>;
    columns: string[];
    row_count: number;
    intent: string;
  };
}

class ChatService {
  private sessionId: string | null = null;

  async sendMessage(request: ChatRequest, targetLanguage: string = 'en'): Promise<{
    message: Message;
    intent?: string;
    entities?: Entity[];
    sources?: Array<{ title: string; relevance: number; id: string }>;
    products?: Array<{ id: string; title: string; description: string; relevance: number }>;
    database_results?: {
      sql_query: string;
      results: Array<Record<string, unknown>>;
      columns: string[];
      row_count: number;
      intent: string;
    };
    detectedLanguage?: string;
  }> {
    try {
      let messageToSend = request.message;
      let detectedLanguage = 'en';

      // Detect language and translate to English if needed
      if (targetLanguage !== 'en') {
        try {
          const detection = await translationService.detectLanguage(request.message);
          detectedLanguage = detection.detected;
          
          // If message is not in English, translate it
          if (detectedLanguage !== 'en') {
            const translation = await translationService.translate(request.message, detectedLanguage, 'en');
            messageToSend = translation.translated_text;
            console.log(`Translated from ${detectedLanguage} to English: "${messageToSend}"`);
          }
        } catch (error) {
          console.error('Translation error:', error);
          // Continue with original message if translation fails
        }
      }

      const response = await axios.post<ChatResponse>(`${API_URL}/send`, {
        message: messageToSend,
        session_id: this.sessionId || request.session_id,
        context: request.context,
        language: 'en', // Always send in English for processing
        avatar: request.avatar
      });

      // Store session ID for follow-up messages
      if (response.data.session_id) {
        this.sessionId = response.data.session_id;
      }

      let responseContent = response.data.response;
      let originalContent = undefined;

      // Translate response back to target language if needed
      if (targetLanguage !== 'en' && detectedLanguage !== 'en') {
        try {
          const translation = await translationService.translate(responseContent, 'en', targetLanguage);
          originalContent = responseContent;
          responseContent = translation.translated_text;
          console.log(`Translated response to ${targetLanguage}: "${responseContent}"`);
        } catch (error) {
          console.error('Response translation error:', error);
          // Continue with English response if translation fails
        }
      }

      const message: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date().toISOString(),
        metadata: {
          intent: response.data.intent,
          entities: response.data.entities,
          confidence: 0.9,
          translated_from: detectedLanguage !== 'en' ? detectedLanguage : undefined,
          translated_to: targetLanguage !== 'en' ? targetLanguage : undefined,
          original_content: originalContent,
        },
      };

      return {
        message,
        intent: response.data.intent,
        entities: response.data.entities,
        sources: response.data.sources,
        products: response.data.products,
        database_results: response.data.database_results,
        detectedLanguage,
      };
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  }

  async getHistory(sessionId: string): Promise<Message[]> {
    try {
      const response = await axios.get(`${API_URL}/history/${sessionId}`);
      return response.data.messages;
    } catch (error) {
      console.error('Get history error:', error);
      throw error;
    }
  }

  async clearHistory(sessionId: string): Promise<void> {
    try {
      await axios.delete(`${API_URL}/history/${sessionId}`);
      if (this.sessionId === sessionId) {
        this.sessionId = null;
      }
    } catch (error) {
      console.error('Clear history error:', error);
      throw error;
    }
  }

  async detectIntent(message: string): Promise<{
    intent: string;
    confidence: number;
    entities: Entity[];
  }> {
    try {
      const response = await axios.post(`${API_URL}/intent`, { message });
      return response.data;
    } catch (error) {
      console.error('Intent detection error:', error);
      throw error;
    }
  }

  async checkHealth(): Promise<{
    status: string;
    nlu: Record<string, unknown>;
    knowledge: Record<string, unknown>;
    openai: Record<string, unknown>;
    active_sessions: number;
  }> {
    try {
      const response = await axios.get(`${API_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }
}

export const chatService = new ChatService();
