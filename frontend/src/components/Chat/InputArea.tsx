// Input area component with multilingual and voice support
import React, { useState } from 'react';
import LanguageSelector from './LanguageSelector';
import { voiceService } from '../../services/voiceService';

interface InputAreaProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
  targetLanguage: string;
  onTargetLanguageChange: (lang: string) => void;
  onVoiceInput?: (text: string) => void;
}

const InputArea: React.FC<InputAreaProps> = ({ 
  value, 
  onChange, 
  onSend, 
  isLoading,
  targetLanguage,
  onTargetLanguageChange,
  onVoiceInput
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [showVoiceOptions, setShowVoiceOptions] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const handleVoiceInput = () => {
    if (!voiceService.isSpeechRecognitionSupported()) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    setIsRecording(true);
    setShowVoiceOptions(false);

    voiceService.startSpeechToText(
      (text) => {
        onChange(text);
        if (onVoiceInput) {
          onVoiceInput(text);
        }
        setIsRecording(false);
      },
      (error) => {
        console.error('Voice input error:', error);
        setIsRecording(false);
      },
      targetLanguage // Use selected language for recognition
    );
  };

  const stopRecording = () => {
    voiceService.stopSpeechToText();
    setIsRecording(false);
  };

  return (
    <div className="border-t border-gray-200 p-3 bg-white">
      {/* Voice Input Options */}
      {showVoiceOptions && (
        <div className="mb-2 p-2 bg-gray-50 rounded-lg">
          <button
            onClick={isRecording ? stopRecording : handleVoiceInput}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
              isRecording 
                ? 'bg-red-100 text-red-600 animate-pulse' 
                : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            {isRecording ? 'Tap to stop recording...' : 'Click to speak'}
          </button>
          <p className="text-xs text-gray-500 mt-1">
            {isRecording ? 'Listening...' : 'Speech will be converted to text'}
          </p>
        </div>
      )}

      <div className="flex items-center gap-2">
        <LanguageSelector
          selectedLang={targetLanguage}
          onLangChange={onTargetLanguageChange}
        />
        
        {/* Voice Toggle Button */}
        <button
          onClick={() => setShowVoiceOptions(!showVoiceOptions)}
          className={`p-2 rounded-lg transition-colors ${
            showVoiceOptions 
              ? 'bg-indigo-100 text-indigo-600' 
              : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
          }`}
          title="Voice input"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>
      </div>

      <div className="flex items-end gap-2 mt-2">
        <div className="flex-1 relative">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isRecording ? "Listening..." : "Type your message..."}
            disabled={isLoading}
            rows={1}
            className="w-full px-3 py-2 pr-20 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            style={{ minHeight: '40px', maxHeight: '100px' }}
          />
          
          {/* Voice Input Button (Alternative) */}
          <button
            onClick={isRecording ? stopRecording : handleVoiceInput}
            className={`absolute right-2 bottom-2 p-1 rounded transition-colors ${
              isRecording 
                ? 'text-red-500 animate-pulse' 
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title={isRecording ? "Stop recording" : "Voice input"}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
        </div>
        
        <button
          onClick={onSend}
          disabled={isLoading || !value.trim()}
          className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
        >
          {isLoading ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default InputArea;
