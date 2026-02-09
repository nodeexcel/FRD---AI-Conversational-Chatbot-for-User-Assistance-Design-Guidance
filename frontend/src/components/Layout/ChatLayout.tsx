// Chat layout component with avatar and voice support
import React from 'react';
import Header from '../Chat/Header';
import Sidebar from '../Chat/Sidebar';

interface AvatarInfo {
  id: string;
  name: string;
  voiceId: string;
  voiceName: string;
  style: 'professional' | 'friendly' | 'elegant';
}

interface ChatLayoutProps {
  children: React.ReactNode;
  selectedAvatar?: AvatarInfo;
  onAvatarChange?: (avatar: AvatarInfo) => void;
  isSpeaking?: boolean;
  onStopSpeaking?: () => void;
}

const ChatLayout: React.FC<ChatLayoutProps> = ({ 
  children, 
  selectedAvatar, 
  onAvatarChange,
  isSpeaking,
  onStopSpeaking
}) => {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header 
        selectedAvatar={selectedAvatar}
        onAvatarChange={onAvatarChange}
        isSpeaking={isSpeaking}
        onStopSpeaking={onStopSpeaking}
      />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
};

export default ChatLayout;
