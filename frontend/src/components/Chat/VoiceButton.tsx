// Voice Button Component for Speech-to-Text
import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { voiceService } from '../../services/voiceService';

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

const VoiceButton: React.FC<VoiceButtonProps> = ({ onTranscript, disabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    setIsSupported(voiceService.isSpeechRecognitionSupported());
  }, []);

  const handleVoiceInput = () => {
    if (isListening) {
      voiceService.stopSpeechToText();
      setIsListening(false);
    } else {
      voiceService.startSpeechToText(
        (text) => {
          onTranscript(text);
          setIsListening(false);
        },
        (error) => {
          console.error('Speech recognition error:', error);
          setIsListening(false);
        }
      );
      setIsListening(true);
    }
  };

  if (!isSupported) {
    return null;
  }

  return (
    <button
      onClick={handleVoiceInput}
      disabled={disabled}
      className={`p-2 rounded-lg transition-all duration-200 ${
        isListening
          ? 'bg-red-500 text-white animate-pulse'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      title={isListening ? 'Stop listening' : 'Start voice input'}
    >
      {isListening ? (
        <Mic className="w-5 h-5" />
      ) : (
        <MicOff className="w-5 h-5" />
      )}
    </button>
  );
};

export default VoiceButton;
