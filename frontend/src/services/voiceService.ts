// Voice Service for Speech-to-Text and Text-to-Speech
import axios from 'axios';

const API_URL = 'http://localhost:8001/api/voice';

export interface VoiceConfig {
  voice?: string;
  avatarId?: string;
  speed: number;
}

export interface AvatarVoicePair {
  avatar_id: string;
  avatar_name: string;
  voice: string;
  style: string;
}

export interface VoiceResponse {
  audio_url?: string;
  audio_data?: string;
  voice_id?: string;
}

class VoiceService {
  private token: string | null = null;
  private recognition: any = null;
  private synthesis: SpeechSynthesis | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  // Speech-to-Text using Web Speech API (browser-native)
  async startSpeechToText(
    onResult: (text: string) => void,
    onError: (error: string) => void,
    lang: string = 'en-US'
  ): Promise<void> {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      onError('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = lang;

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
    };

    this.recognition.onerror = (event: any) => {
      onError(event.error);
    };

    this.recognition.start();
  }

  stopSpeechToText(): void {
    if (this.recognition) {
      this.recognition.stop();
    }
  }

  // Text-to-Speech using Web Speech API (browser-native)
  async textToSpeech(
    text: string,
    config?: VoiceConfig
  ): Promise<void> {
    if (!('speechSynthesis' in window)) {
      throw new Error('Text-to-speech not supported in this browser');
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set voice configuration
    if (config) {
      const voices = window.speechSynthesis.getVoices();
      
      // First try to find by avatar voice
      if (config.avatarId) {
        const avatarVoices: Record<string, string> = {
          'sophia': 'alloy',
          'emma': 'echo',
          'james': 'fable',
          'aria': 'nova',
          'default': 'shimmer'
        };
        const voiceId = avatarVoices[config.avatarId] || config.voice || 'shimmer';
        const voice = voices.find((v: any) => v.name.toLowerCase().includes(voiceId.toLowerCase()));
        if (voice) {
          utterance.voice = voice;
        }
      } else if (config.voice) {
        const voice = voices.find((v: any) => v.name.toLowerCase().includes(config.voice!.toLowerCase()));
        if (voice) {
          utterance.voice = voice;
        }
      }
      utterance.rate = config.speed;
    }

    return new Promise((resolve, reject) => {
      utterance.onend = () => resolve();
      utterance.onerror = (event) => reject(event.error);
      
      window.speechSynthesis.speak(utterance);
    });
  }

  // Server-side TTS using OpenAI with avatar support
  async serverTextToSpeech(
    text: string, 
    config?: VoiceConfig
  ): Promise<HTMLAudioElement> {
    try {
      const response = await axios.post(
        `${API_URL}/synthesize`,
        { 
          text, 
          voice: config?.voice,
          avatar_id: config?.avatarId,
          speed: config?.speed || 1.0
        },
        { headers: this.getHeaders() }
      );

      const audioData = response.data.audio_data;
      const audio = new Audio(`data:audio/mp3;base64,${audioData}`);
      return audio;
    } catch (error) {
      console.error('Server TTS error:', error);
      // Fallback to browser TTS
      return this.browserTextToSpeech(text, config);
    }
  }

  // New: TTS with avatar using the dedicated endpoint
  async textToSpeechWithAvatar(
    text: string,
    avatarId: string,
    speed: number = 1.0
  ): Promise<HTMLAudioElement> {
    try {
      const response = await axios.post(
        `${API_URL}/synthesize-with-avatar`,
        null,
        {
          params: { text, avatar_id: avatarId, speed },
          headers: this.getHeaders()
        }
      );

      const audioData = response.data.audio_data;
      const audio = new Audio(`data:audio/mp3;base64,${audioData}`);
      return audio;
    } catch (error) {
      console.error('Avatar TTS error:', error);
      // Fallback to browser TTS
      return this.browserTextToSpeech(text, { avatarId, speed });
    }
  }

  async browserTextToSpeech(text: string, config?: VoiceConfig): Promise<HTMLAudioElement> {
    await this.textToSpeech(text, config);
    // Return a dummy audio element since browser TTS doesn't return one
    return new Audio();
  }

  // Get available voices
  async getAvailableVoices(): Promise<any[]> {
    return new Promise((resolve) => {
      if ('speechSynthesis' in window) {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          resolve(voices);
          return;
        }
        // Some browsers load voices asynchronously
        window.speechSynthesis.onvoiceschanged = () => {
          resolve(window.speechSynthesis.getVoices());
        };
      }
      resolve([]);
    });
  }

  // Get server-supported voices and avatar pairs
  async getServerVoices(): Promise<{
    voices: string[];
    avatar_pairs: AvatarVoicePair[];
  }> {
    try {
      const response = await axios.get(`${API_URL}/voices`, {
        headers: this.getHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching server voices:', error);
      return {
        voices: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        avatar_pairs: [
          { avatar_id: 'sophia', avatar_name: 'Sophia', voice: 'alloy', style: 'professional' },
          { avatar_id: 'emma', avatar_name: 'Emma', voice: 'echo', style: 'friendly' },
          { avatar_id: 'james', avatar_name: 'James', voice: 'fable', style: 'professional' },
          { avatar_id: 'aria', avatar_name: 'Aria', voice: 'nova', style: 'elegant' },
          { avatar_id: 'default', avatar_name: 'Default', voice: 'shimmer', style: 'casual' }
        ]
      };
    }
  }

  // Check if speech recognition is supported
  isSpeechRecognitionSupported(): boolean {
    return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  }

  // Check if speech synthesis is supported
  isSpeechSynthesisSupported(): boolean {
    return 'speechSynthesis' in window;
  }

  // Get voice for avatar from server
  async getVoiceForAvatar(avatarId: string): Promise<{ avatar_id?: string; voice_id?: string }> {
    try {
      const response = await axios.get(`${API_URL}/avatar/${avatarId}`, {
        headers: this.getHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching voice for avatar:', error);
      // Return default voice mapping
      const defaultVoices: Record<string, string> = {
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
      return { voice_id: defaultVoices[avatarId.toLowerCase()] || 'alloy' };
    }
  }

  // Speak text with callback for onEnd
  async speak(text: string, lang: string = 'en', onEnd?: () => void): Promise<void> {
    if (!('speechSynthesis' in window)) {
      throw new Error('Text-to-speech not supported in this browser');
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 1.0;

    utterance.onend = () => {
      if (onEnd) onEnd();
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  }

  // Stop speaking
  stopSpeaking(): void {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }

  // Play audio from URL with callback
  async playAudio(url: string, onEnd?: () => void): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(url);
      
      audio.onended = () => {
        if (onEnd) onEnd();
        resolve();
      };

      audio.onerror = (error) => {
        console.error('Audio playback error:', error);
        if (onEnd) onEnd();
        reject(error);
      };

      audio.play().catch((error) => {
        console.error('Audio play error:', error);
        if (onEnd) onEnd();
        reject(error);
      });
    });
  }
}

export const voiceService = new VoiceService();
