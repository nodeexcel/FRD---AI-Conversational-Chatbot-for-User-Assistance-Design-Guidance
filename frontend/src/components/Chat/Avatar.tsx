// Avatar Component for voice responses
import React from 'react';

interface AvatarProps {
  voiceEnabled: boolean;
  isSpeaking: boolean;
  avatarType: string;
  size?: 'sm' | 'md' | 'lg';
}

const AVATAR_PRESETS = [
  { id: 'default', name: 'Default', emoji: '🤖', color: 'from-blue-400 to-indigo-500' },
  { id: 'female', name: 'Assistant', emoji: '👩‍💼', color: 'from-pink-400 to-rose-500' },
  { id: 'male', name: 'Advisor', emoji: '👨‍💼', color: 'from-blue-400 to-cyan-500' },
  { id: 'friendly', name: 'Friendly', emoji: '😊', color: 'from-yellow-400 to-orange-500' },
  { id: 'professional', name: 'Professional', emoji: '👔', color: 'from-slate-400 to-gray-600' },
];

const Avatar: React.FC<AvatarProps> = ({ voiceEnabled, isSpeaking, avatarType, size = 'md' }) => {
  const currentPreset = AVATAR_PRESETS.find(a => a.id === avatarType) || AVATAR_PRESETS[0];
  
  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-xl',
    lg: 'w-16 h-16 text-3xl',
  };

  return (
    <div className={`relative ${sizeClasses[size]}`}>
      {/* Avatar Circle with Gradient */}
      <div 
        className={`w-full h-full rounded-full bg-gradient-to-br ${currentPreset.color} flex items-center justify-center shadow-lg transition-all duration-300 ${
          isSpeaking ? 'animate-pulse scale-110' : ''
        } ${voiceEnabled ? '' : 'opacity-50'}`}
      >
        <span className="select-none">{currentPreset.emoji}</span>
      </div>
      
      {/* Speaking Indicator */}
      {voiceEnabled && isSpeaking && (
        <div className="absolute -bottom-1 -right-1 flex space-x-0.5">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        </div>
      )}
      
      {/* Voice Disabled Indicator */}
      {!voiceEnabled && (
        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-gray-400 rounded-full flex items-center justify-center">
          <svg className="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
          </svg>
        </div>
      )}
    </div>
  );
};

export default Avatar;
export { AVATAR_PRESETS };
