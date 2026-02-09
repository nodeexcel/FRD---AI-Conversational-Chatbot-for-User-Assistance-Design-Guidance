// Chat window component with NLU metadata and voice playback
import React from 'react';
import MessageBubble from './MessageBubble';

interface Entity {
  type: string;
  value: string;
  confidence: number;
}

interface Message {
  role: string;
  content: string;
  metadata?: {
    intent?: string;
    entities?: Entity[];
    confidence?: number;
    avatar?: string;
  };
}

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onVoicePlayback?: (content: string, avatar?: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading, onVoicePlayback }) => {
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((msg, index) => (
        <MessageBubble 
          key={index} 
          role={msg.role} 
          content={msg.content} 
          metadata={msg.metadata}
          onVoicePlayback={onVoicePlayback}
        />
      ))}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
