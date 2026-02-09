// Translation Service
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/translate';

export interface TranslationResult {
  original_text: string;
  translated_text: string;
  source_lang: string;
  source_lang_name: string;
  target_lang: string;
  target_lang_name: string;
  success: boolean;
  error?: string;
}

export interface LanguageDetection {
  detected: string;
  code: string;
  confidence: number;
}

class TranslationService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  async getSupportedLanguages(): Promise<Record<string, string>> {
    try {
      const response = await axios.get(`${API_URL}/languages`);
      return response.data.languages;
    } catch (error) {
      console.error('Error fetching languages:', error);
      return {};
    }
  }

  async detectLanguage(text: string): Promise<LanguageDetection> {
    try {
      const response = await axios.post(
        `${API_URL}/detect`,
        { text },
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error detecting language:', error);
      return { detected: 'English', code: 'en', confidence: 0.5 };
    }
  }

  async translate(
    text: string,
    targetLang: string,
    sourceLang?: string
  ): Promise<TranslationResult> {
    try {
      const response = await axios.post(
        API_URL,
        {
          text,
          target_lang: targetLang,
          source_lang: sourceLang,
        },
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error: any) {
      console.error('Translation error:', error);
      return {
        original_text: text,
        translated_text: text,
        source_lang: sourceLang || 'en',
        source_lang_name: 'English',
        target_lang: targetLang,
        target_lang_name: targetLang,
        success: false,
        error: error.response?.data?.detail || 'Translation failed',
      };
    }
  }

  async translateConversation(
    messages: Array<{ role: string; content: string }>,
    targetLang: string
  ): Promise<Array<{ role: string; content: string; original_content?: string }>> {
    try {
      const response = await axios.post(
        `${API_URL}/conversation`,
        {
          messages,
          target_lang: targetLang,
        },
        { headers: this.getHeaders() }
      );
      return response.data.translated_messages;
    } catch (error) {
      console.error('Conversation translation error:', error);
      return messages.map((msg) => ({
        ...msg,
        original_content: msg.content,
      }));
    }
  }
}

export const translationService = new TranslationService();
