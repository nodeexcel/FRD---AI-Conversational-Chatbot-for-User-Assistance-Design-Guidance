// Voice Test Page - Test STT, TTS, and Avatar features
import React, { useState, useEffect } from 'react';
import { voiceService, AvatarVoicePair } from '../services/voiceService';
import { authService } from '../services/authService';

const VoiceTestPage: React.FC = () => {
  const [text, setText] = useState('Hello! This is a test of the voice synthesis system.');
  const [avatarId, setAvatarId] = useState('sophia');
  const [voiceId, setVoiceId] = useState('alloy');
  const [speed, setSpeed] = useState(1.0);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [voices, setVoices] = useState<{ voices: string[]; avatar_pairs: AvatarVoicePair[] } | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  // Avatar options
  const avatarOptions = [
    { id: 'sophia', name: 'Sophia', style: 'Professional' },
    { id: 'emma', name: 'Emma', style: 'Friendly' },
    { id: 'james', name: 'James', style: 'Professional' },
    { id: 'aria', name: 'Aria', style: 'Elegant' },
    { id: 'default', name: 'Default', style: 'Casual' },
  ];

  useEffect(() => {
    loadVoices();
  }, []);

  const loadVoices = async () => {
    try {
      const voiceData = await voiceService.getServerVoices();
      setVoices(voiceData);
      console.log('Loaded voices:', voiceData);
    } catch (error) {
      console.error('Error loading voices:', error);
      // Set fallback voices
      setVoices({
        voices: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        avatar_pairs: [
          { avatar_id: 'sophia', avatar_name: 'Sophia', voice: 'alloy', style: 'professional' },
          { avatar_id: 'emma', avatar_name: 'Emma', voice: 'echo', style: 'friendly' },
          { avatar_id: 'james', avatar_name: 'James', voice: 'fable', style: 'professional' },
          { avatar_id: 'aria', avatar_name: 'Aria', voice: 'nova', style: 'elegant' },
          { avatar_id: 'default', avatar_name: 'Default', voice: 'shimmer', style: 'casual' },
        ],
      });
    }
  };

  const handleTextToSpeech = async () => {
    if (!text.trim()) {
      alert('Please enter text to synthesize');
      return;
    }

    setLoading(true);
    setAudioUrl(null);
    try {
      // Use the avatar-based TTS
      const audio = await voiceService.textToSpeechWithAvatar(
        text,
        avatarId,
        speed
      );
      
      // Create URL for audio playback
      const audioData = voices?.avatar_pairs 
        ? await fetch(`data:audio/mp3;base64,${await (await voiceService.serverTextToSpeech(text, { avatarId, speed })).src.split(',')[1]}`)
        : null;
      
      // For now, just show success
      setResult({
        success: true,
        message: 'Audio generated successfully',
        avatar: avatarId,
        voice: voices?.avatar_pairs?.find(a => a.avatar_id === avatarId)?.voice || 'alloy',
        speed: speed
      });
      
      // Try to play the audio
      try {
        const audioWithAvatar = await voiceService.textToSpeechWithAvatar(text, avatarId, speed);
        const url = URL.createObjectURL(await (await fetch(`data:audio/mp3;base64,${await (await voiceService.serverTextToSpeech(text, { avatarId, speed })).src.split(',')[1] || ''}`)).blob());
        setAudioUrl(url);
      } catch (playError) {
        console.log('Audio generated but playback not available in browser');
      }
    } catch (error: any) {
      console.error('TTS error:', error);
      setResult({
        error: true,
        message: `TTS failed: ${error.message}`,
        hint: 'Make sure backend is running and you have an OpenAI API key'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBrowserTTS = () => {
    if (!('speechSynthesis' in window)) {
      alert('Browser TTS not supported');
      return;
    }
    
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set voice based on avatar
    const voiceMap: Record<string, string> = {
      'sophia': 'alloy',
      'emma': 'echo',
      'james': 'fable',
      'aria': 'nova',
      'default': 'shimmer'
    };
    
    const voices = window.speechSynthesis.getVoices();
    const targetVoice = voiceMap[avatarId] || 'alloy';
    const voice = voices.find(v => v.name.toLowerCase().includes(targetVoice));
    if (voice) {
      utterance.voice = voice;
    }
    
    utterance.rate = speed;
    window.speechSynthesis.speak(utterance);
    
    setResult({
      success: true,
      message: 'Browser TTS started',
      avatar: avatarId,
      note: 'Using browser\'s built-in voices'
    });
  };

  const handleSpeechToText = () => {
    if (!voiceService.isSpeechRecognitionSupported()) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    setIsRecording(true);
    setResult(null);

    voiceService.startSpeechToText(
      (text) => {
        setResult({
          success: true,
          type: 'STT',
          transcript: text
        });
        setIsRecording(false);
      },
      (error) => {
        setResult({
          error: true,
          type: 'STT',
          message: `Speech recognition error: ${error}`
        });
        setIsRecording(false);
      }
    );
  };

  const stopRecording = () => {
    voiceService.stopSpeechToText();
    setIsRecording(false);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <h1>🎤 Voice & Avatar Test Page</h1>
      
      {/* Avatar Selection */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Select Avatar:</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {avatarOptions.map((avatar) => (
            <button
              key={avatar.id}
              onClick={() => setAvatarId(avatar.id)}
              style={{
                padding: '10px 20px',
                fontSize: '14px',
                backgroundColor: avatarId === avatar.id ? '#007bff' : '#f8f9fa',
                color: avatarId === avatar.id ? 'white' : '#333',
                border: avatarId === avatar.id ? 'none' : '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              {avatar.name} ({avatar.style})
            </button>
          ))}
        </div>
      </div>

      {/* Text Input */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Text to Synthesize:
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to convert to speech..."
          style={{
            width: '100%',
            height: '100px',
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '4px',
          }}
        />
      </div>

      {/* Speed Control */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Speed: {speed.toFixed(1)}x
        </label>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
          style={{ width: '200px' }}
        />
      </div>

      {/* Voice Selection */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Voice (OpenAI):
        </label>
        <select
          value={voiceId}
          onChange={(e) => setVoiceId(e.target.value)}
          style={{
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            width: '200px',
          }}
        >
          <option value="alloy">Alloy (Neutral)</option>
          <option value="echo">Echo (Warm)</option>
          <option value="fable">Fable (British)</option>
          <option value="onyx">Onyx (Deep)</option>
          <option value="nova">Nova (Female)</option>
          <option value="shimmer">Shimmer (Light)</option>
        </select>
      </div>

      {/* Action Buttons */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          onClick={handleTextToSpeech}
          disabled={loading}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: loading ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Generating...' : '🔊 Generate Speech (OpenAI)'}
        </button>

        <button
          onClick={handleBrowserTTS}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: '#17a2b8',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          🔊 Browser TTS
        </button>

        <button
          onClick={isRecording ? stopRecording : handleSpeechToText}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: isRecording ? '#dc3545' : '#6f42c1',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {isRecording ? '⏹️ Stop Recording' : '🎤 Speech to Text'}
        </button>
      </div>

      {/* Result Display */}
      {result && (
        <div
          style={{
            padding: '20px',
            backgroundColor: result.error ? '#f8d7da' : '#d4edda',
            borderRadius: '4px',
            border: `1px solid ${result.error ? '#f5c6cb' : '#c3e6cb'}`,
          }}
        >
          <h3>Result:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
          
          {result.transcript && (
            <div style={{ marginTop: '10px' }}>
              <strong>Transcript:</strong> {result.transcript}
            </div>
          )}
        </div>
      )}

      {/* Audio Player */}
      {audioUrl && (
        <div style={{ marginTop: '20px' }}>
          <h3>Generated Audio:</h3>
          <audio controls src={audioUrl} style={{ width: '100%' }} />
        </div>
      )}

      {/* Voice Info */}
      {voices && (
        <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h3>Available Voices & Avatars:</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
            {voices.avatar_pairs.map((pair) => (
              <div
                key={pair.avatar_id}
                style={{
                  padding: '10px',
                  backgroundColor: avatarId === pair.avatar_id ? '#e3f2fd' : 'white',
                  borderRadius: '4px',
                  border: '1px solid #dee2e6',
                }}
              >
                <strong>{pair.avatar_name}</strong>
                <br />
                <small>Voice: {pair.voice}</small>
                <br />
                <small>Style: {pair.style}</small>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Test Examples */}
      <div style={{ marginTop: '30px' }}>
        <h3>Test Examples:</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setText('Hello! Welcome to the AI Dress Design Assistant. How can I help you today?')}
            style={{ padding: '8px 16px', cursor: 'pointer' }}
          >
            Welcome Message
          </button>
          <button
            onClick={() => setText('I recommend a silk saree in royal blue for your wedding ceremony.')}
            style={{ padding: '8px 16px', cursor: 'pointer' }}
          >
            Product Recommendation
          </button>
          <button
            onClick={() => setText('For a summer wedding, consider light fabrics like chiffon or georgette.')}
            style={{ padding: '8px 16px', cursor: 'pointer' }}
          >
            Fabric Advice
          </button>
        </div>
      </div>
    </div>
  );
};

export default VoiceTestPage;
