import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Message, ChatSession, ConversationContext } from '../types';

interface ChatState {
  messages: Message[];
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  isLoading: boolean;
  isTyping: boolean;
  context: ConversationContext;
  suggestions: string[];
  error: string | null;
  // Multilingual support
  detectedLanguage: string;
  targetLanguage: string;
  isTranslating: boolean;
}

const initialState: ChatState = {
  messages: [],
  sessions: [],
  currentSession: null,
  isLoading: false,
  isTyping: false,
  context: {
    entities: {},
    previousTopics: [],
  },
  suggestions: [],
  error: null,
  // Multilingual support
  detectedLanguage: 'en',
  targetLanguage: 'en',
  isTranslating: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
      if (state.currentSession) {
        state.currentSession.messages = state.messages;
      }
    },
    setMessages: (state, action: PayloadAction<Message[]>) => {
      state.messages = action.payload;
    },
    setCurrentSession: (state, action: PayloadAction<ChatSession | null>) => {
      state.currentSession = action.payload;
      if (action.payload) {
        state.messages = action.payload.messages;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    setContext: (state, action: PayloadAction<Partial<ConversationContext>>) => {
      state.context = { ...state.context, ...action.payload };
    },
    clearContext: (state) => {
      state.context = initialState.context;
    },
    setSuggestions: (state, action: PayloadAction<string[]>) => {
      state.suggestions = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    createNewSession: (state) => {
      state.currentSession = null;
      state.messages = [];
      state.context = initialState.context;
      state.suggestions = [];
      state.error = null;
    },
    // Multilingual reducers
    setDetectedLanguage: (state, action: PayloadAction<string>) => {
      state.detectedLanguage = action.payload;
    },
    setTargetLanguage: (state, action: PayloadAction<string>) => {
      state.targetLanguage = action.payload;
    },
    setIsTranslating: (state, action: PayloadAction<boolean>) => {
      state.isTranslating = action.payload;
    },
  },
});

export const {
  addMessage,
  setMessages,
  setCurrentSession,
  setLoading,
  setTyping,
  setContext,
  clearContext,
  setSuggestions,
  setError,
  createNewSession,
  setDetectedLanguage,
  setTargetLanguage,
  setIsTranslating,
} = chatSlice.actions;

export default chatSlice.reducer;
