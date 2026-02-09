export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  id: string;
  user_id: string;
  theme: string;
  language: string;
  notifications: boolean;
  saved_designs: string[];
  chat_history_limit: number;
  created_at: string;
  updated_at: string;
}

export interface Entity {
  type: string;
  value: string;
  confidence: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    agent?: string;
    intent?: string;
    entities?: Entity[];
    confidence?: number;
    translated_from?: string;
    translated_to?: string;
    original_content?: string;
    avatar?: string;
  };
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface ConversationContext {
  entities: Record<string, any>;
  previousTopics: string[];
}

export interface TranslationRequest {
  text: string;
  source_language?: string;
  target_language: string;
}

export interface TranslationResponse {
  original_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
}

export interface LanguageDetectionResponse {
  language: string;
  confidence: number;
}

export interface LanguageDetection {
  language: string;
  confidence: number;
}

export interface DocumentUploadResponse {
  id: string;
  filename: string;
  file_type: string;
  chunks_count: number;
  status: 'success' | 'failed';
  message: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  target_language?: string;
}

export interface ChatResponse {
  session_id: string;
  message: Message;
  suggestions: string[];
  context: ConversationContext;
}

export interface DesignSession {
  id: string;
  user_id: string;
  current_step: number;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  color: string;
  size: string;
  image_url?: string;
  stock: number;
}

export interface RAGDocument {
  id: string;
  user_id: string;
  filename: string;
  file_type: string;
  content: string;
  chunks_count: number;
  created_at: string;
}

export interface LearningAnalytics {
  id: string;
  user_id: string;
  session_id: string;
  message_id: string;
  feedback_type: 'helpful' | 'not_helpful' | null;
  suggested_response?: string;
  created_at: string;
}
