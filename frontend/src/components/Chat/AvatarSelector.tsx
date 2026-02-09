// Avatar Selector Component
import React from 'react';
import { AVATAR_PRESETS } from './Avatar';

interface AvatarSelectorProps {
  value: string;
  onChange: (avatarId: string) => void;
  disabled?: boolean;
}

const AvatarSelector: React.FC<AvatarSelectorProps> = ({ value, onChange, disabled = false }) => {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Chat Avatar
      </label>
      <div className="flex flex-wrap gap-3">
        {AVATAR_PRESETS.map((avatar) => (
          <button
            key={avatar.id}
            onClick={() => onChange(avatar.id)}
            disabled={disabled}
            className={`relative w-16 h-16 rounded-full bg-gradient-to-br ${avatar.color} 
              flex items-center justify-center shadow-md transition-all duration-200
              ${value === avatar.id ? 'ring-4 ring-indigo-500 scale-110' : 'hover:scale-105'}
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            title={avatar.name}
          >
            <span className="text-2xl">{avatar.emoji}</span>
            {value === avatar.id && (
              <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full">
                ✓
              </div>
            )}
          </button>
        ))}
      </div>
      <p className="text-sm text-gray-500">
        Selected: {AVATAR_PRESETS.find(a => a.id === value)?.name || 'Default'}
      </p>
    </div>
  );
};

export default AvatarSelector;
