// Chat page component with RAG, SQL, multilingual and voice support
import React, { useState, useEffect, useRef } from 'react';
import ChatLayout from '../components/Layout/ChatLayout';
import ChatWindow from '../components/Chat/ChatWindow';
import InputArea from '../components/Chat/InputArea';
import { chatService } from '../services/chatService';
import { voiceService } from '../services/voiceService';
import { Message } from '../types';
import { AVATARS } from '../utils/i18n';

// Generate unique ID for messages
const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { 
      id: generateId(),
      role: 'assistant', 
      content: 'Hello! I am your dress design assistant. How can I help you today? I can help you find dresses, get style recommendations, learn about fabric care, and more!',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [selectedAvatar, setSelectedAvatar] = useState(AVATARS[0]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleVoicePlayback = async (content: string, avatarId?: string) => {
    try {
      // Stop any current playback
      voiceService.stopSpeaking();
      
      const avatar = avatarId ? AVATARS.find(a => a.id === avatarId) : selectedAvatar;
      
      // Use browser TTS with client-side avatar-voice mapping
      setIsSpeaking(true);
      
      // Client-side avatar to browser voice mapping
      const avatarVoices: Record<string, string> = {
        'sophia': 'alloy',
        'emma': 'echo',
        'james': 'fable',
        'aria': 'nova',
        'default': 'shimmer',
        'female': 'alloy',
        'male': 'fable',
        'friendly': 'shimmer',
        'professional': 'alloy'
      };
      
      const voiceId = avatarVoices[avatar?.id || 'sophia'] || 'alloy';
      
      await voiceService.textToSpeech(content, { voice: voiceId, speed: 1.0 });
      setIsSpeaking(false);
    } catch (error) {
      console.error('Voice playback error:', error);
      setIsSpeaking(false);
      // Fallback to browser TTS without voice
      try {
        voiceService.stopSpeaking();
        await voiceService.speak(content, targetLanguage);
      } catch (ttsError) {
        console.error('Browser TTS error:', ttsError);
      }
    }
  };

  const handleStopSpeaking = () => {
    voiceService.stopSpeaking();
    setIsSpeaking(false);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Stop speaking when user sends a new message
    handleStopSpeaking();

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { 
      id: generateId(),
      role: 'user', 
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        message: userMessage,
        session_id: sessionId || undefined,
        avatar: selectedAvatar?.id
      }, targetLanguage);

      setSessionId(chatService.getSessionId());

      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: response.message.content,
        timestamp: new Date().toISOString(),
        metadata: {
          ...response.message.metadata,
          avatar: selectedAvatar?.id
        }
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatLayout 
      selectedAvatar={selectedAvatar}
      onAvatarChange={setSelectedAvatar}
      isSpeaking={isSpeaking}
      onStopSpeaking={handleStopSpeaking}
    >
      <ChatWindow 
        messages={messages} 
        isLoading={isLoading}
        onVoicePlayback={handleVoicePlayback}
      />
      <div ref={messagesEndRef} />
      <InputArea 
        value={input}
        onChange={setInput}
        onSend={handleSend}
        isLoading={isLoading}
        targetLanguage={targetLanguage}
        onTargetLanguageChange={setTargetLanguage}
      />
    </ChatLayout>
  );
};

export default ChatPage;
