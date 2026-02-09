import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { addMessage, setLoading, setTyping, setSuggestions, setError, createNewSession } from '../store/chatSlice';
import { chatService } from '../services/chatService';
import { wsService } from '../services/websocketService';
import { ChatRequest, Message } from '../types';
import { v4 as uuidv4 } from 'uuid';

export const useChat = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { messages, currentSession, isLoading, isTyping, suggestions, context } = useSelector(
    (state: RootState) => state.chat
  );

  const sendMessage = useCallback(async (content: string, language?: string) => {
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
      language,
    };

    dispatch(addMessage(userMessage));
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      const request: ChatRequest = {
        message: content,
        sessionId: currentSession?.id,
        language,
        context,
      };

      const response = await chatService.sendMessage(request);

      const aiMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.message.content,
        timestamp: new Date(),
        language: response.message.language,
        richContent: response.message.richContent,
        metadata: response.message.metadata,
      };

      dispatch(addMessage(aiMessage));

      if (response.suggestions) {
        dispatch(setSuggestions(response.suggestions));
      }
    } catch (error) {
      dispatch(setError(error instanceof Error ? error.message : 'Failed to send message'));
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, currentSession, context]);

  const sendVoiceMessage = useCallback(async (audioBlob: Blob, language?: string) => {
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      if (language) {
        formData.append('language', language);
      }

      const response = await chatService.sendVoiceMessage(formData);

      const aiMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.message.content,
        timestamp: new Date(),
        language: response.message.language,
        audioUrl: response.message.audioUrl,
        richContent: response.message.richContent,
        metadata: response.message.metadata,
      };

      dispatch(addMessage(aiMessage));

      if (response.suggestions) {
        dispatch(setSuggestions(response.suggestions));
      }
    } catch (error) {
      dispatch(setError(error instanceof Error ? error.message : 'Failed to process voice message'));
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch]);

  const connectWebSocket = useCallback((sessionId: string) => {
    wsService.connect(sessionId);

    wsService.onMessage((message) => {
      if (message.type === 'message') {
        const aiMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: (message.payload as { content: string }).content,
          timestamp: new Date(),
        };
        dispatch(addMessage(aiMessage));
      }
    });

    wsService.onTyping((typing) => {
      dispatch(setTyping(typing));
    });
  }, [dispatch]);

  const disconnectWebSocket = useCallback(() => {
    wsService.disconnect();
  }, []);

  const newChat = useCallback(() => {
    createNewSession();
  }, []);

  return {
    messages,
    isLoading,
    isTyping,
    suggestions,
    sendMessage,
    sendVoiceMessage,
    connectWebSocket,
    disconnectWebSocket,
    newChat,
  };
};
