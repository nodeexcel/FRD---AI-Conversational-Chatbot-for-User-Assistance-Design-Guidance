// Chat header component with user info, avatar selection and voice controls
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../services/authService';
import AvatarSelector from './AvatarSelector';

interface AvatarInfo {
  id: string;
  name: string;
  voiceId: string;
  voiceName: string;
  style: 'professional' | 'friendly' | 'elegant';
}

interface HeaderProps {
  selectedAvatar?: AvatarInfo;
  onAvatarChange?: (avatar: AvatarInfo) => void;
  isSpeaking?: boolean;
  onStopSpeaking?: () => void;
}

const Header: React.FC<HeaderProps> = ({ 
  selectedAvatar, 
  onAvatarChange,
  isSpeaking,
  onStopSpeaking
}) => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleAvatarChange = (avatarId: string) => {
    if (onAvatarChange) {
      // Create a default avatar object with the selected ID
      const avatar: AvatarInfo = {
        id: avatarId,
        name: avatarId.charAt(0).toUpperCase() + avatarId.slice(1),
        voiceId: 'alloy',
        voiceName: 'Alloy',
        style: 'professional'
      };
      onAvatarChange(avatar);
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h1 className="text-lg font-semibold text-gray-900">AI Chatbot</h1>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Avatar Selector */}
        {onAvatarChange && (
          <div className="flex items-center gap-2">
            <AvatarSelector
              value={selectedAvatar?.id || 'sophia'}
              onChange={handleAvatarChange}
            />
          </div>
        )}
        
        {/* Voice Status */}
        {isSpeaking && onStopSpeaking && (
          <button
            onClick={onStopSpeaking}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-600 rounded-full hover:bg-red-200 transition-colors animate-pulse"
          >
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
            Speaking...
          </button>
        )}
        
        {/* User info */}
        {user && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
              <span className="text-indigo-600 font-medium text-xs">
                {user.name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="hidden sm:inline">{user.name || user.email}</span>
          </div>
        )}
        
        {/* Logout button */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          title="Logout"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
