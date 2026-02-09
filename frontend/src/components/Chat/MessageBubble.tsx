// Message bubble component with NLU + RAG product display + Voice playback
import React, { useState } from 'react';
import { Brain, Tag, TrendingUp, Package, Volume2, VolumeX, Play, Pause } from 'lucide-react';
import { ProductList } from './ProductCard';
import { DatabaseResults } from './DatabaseResults';

interface Entity {
  type: string;
  value: string;
  confidence: number;
}

interface Product {
  id: string;
  title: string;
  description: string;
  relevance: number;
}

interface MessageBubbleProps {
  role: string;
  content: string;
  metadata?: {
    intent?: string;
    entities?: Entity[];
    confidence?: number;
    sources?: Array<{ title: string; relevance: number; id: string }>;
    products?: Product[];
    database_results?: {
      sql_query: string;
      results: Array<Record<string, unknown>>;
      columns: string[];
      row_count: number;
      intent: string;
    };
    avatar?: string; // Avatar used for TTS
  };
  onVoicePlayback?: (content: string, avatar?: string) => void; // Callback for voice playback
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, metadata, onVoicePlayback }) => {
  const isUser = role === 'user';
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  
  // Helper to get confidence color
  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.8) return 'text-green-600 bg-green-100';
    if (conf >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const handleVoiceToggle = () => {
    if (isPlaying) {
      setIsPlaying(false);
      // Stop playback logic would go here
    } else {
      setIsPlaying(true);
      if (onVoicePlayback) {
        onVoicePlayback(content, metadata?.avatar);
      }
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] rounded-2xl ${
        isUser 
          ? 'bg-indigo-600 text-white' 
          : 'bg-white border border-gray-200 text-gray-900'
      }`}>
        {/* Message Content */}
        <div className="px-4 py-3 flex items-start gap-3">
          {/* Voice Playback Button (only for assistant) */}
          {!isUser && onVoicePlayback && (
            <button
              onClick={handleVoiceToggle}
              className={`mt-1 p-1.5 rounded-full transition-colors ${
                isPlaying 
                  ? 'bg-indigo-100 text-indigo-600 animate-pulse' 
                  : 'text-gray-400 hover:text-indigo-600 hover:bg-indigo-50'
              }`}
              title={isPlaying ? 'Stop voice' : 'Play voice'}
            >
              {isPlaying ? (
                <Pause size={14} className="fill-current" />
              ) : (
                <Play size={14} className="fill-current" />
              )}
            </button>
          )}
          
          <div className="flex-1">
            <p className="text-sm leading-relaxed">{content}</p>
          </div>
          
          {/* Mute Toggle (only when playing) */}
          {!isUser && isPlaying && (
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="mt-1 p-1.5 rounded-full text-indigo-600 hover:bg-indigo-50 transition-colors"
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} className="fill-current" />}
            </button>
          )}
        </div>

        {/* Products from RAG (only for assistant messages) */}
        {!isUser && metadata?.products && metadata.products.length > 0 && (
          <div className="border-t border-gray-100 px-4 py-3 bg-gradient-to-r from-indigo-50/50 to-purple-50/50">
            <ProductList products={metadata.products} />
          </div>
        )}

        {/* Database Results from SQL Agent */}
        {!isUser && metadata?.database_results && (
          <div className="border-t purple-200 px-4 py-3 bg-purple-50">
            <DatabaseResults results={metadata.database_results} />
          </div>
        )}

        {/* NLU Analysis (only for assistant messages) */}
        {!isUser && metadata && (metadata.intent || metadata.entities) && (
          <div className="border-t border-gray-200 px-4 py-3 bg-gray-50 rounded-b-xl">
            <p className="text-xs font-semibold text-gray-500 mb-2 flex items-center gap-1">
              <Brain size={12} /> Analysis
            </p>
            
            {/* Intent */}
            {metadata.intent && (
              <div className="flex items-center gap-2 mb-2">
                <Tag size={12} className="text-indigo-600" />
                <span className="text-xs text-gray-600">Intent:</span>
                <span className="text-xs font-medium text-indigo-600 bg-indigo-100 px-2 py-0.5 rounded-full capitalize">
                  {metadata.intent.replace('_', ' ')}
                </span>
              </div>
            )}

            {/* Confidence Score */}
            {metadata.confidence !== undefined && (
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp size={12} className="text-green-600" />
                <span className="text-xs text-gray-600">Confidence:</span>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${getConfidenceColor(metadata.confidence)}`}>
                  {(metadata.confidence * 100).toFixed(0)}%
                </span>
              </div>
            )}

            {/* Entities */}
            {metadata.entities && metadata.entities.length > 0 && (
              <div className="mt-2">
                <span className="text-xs text-gray-600">Entities:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {metadata.entities.map((entity, idx) => (
                    <span 
                      key={idx}
                      className="text-xs bg-white border border-gray-300 px-2 py-1 rounded-full"
                    >
                      <span className="font-medium text-indigo-600">{entity.type}:</span> {entity.value}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Sources from RAG */}
            {metadata.sources && metadata.sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <span className="text-xs text-gray-500">Sources:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {metadata.sources.slice(0, 3).map((source, idx) => (
                    <span 
                      key={idx}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full flex items-center gap-1"
                    >
                      <Package size={10} />
                      {source.title}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
