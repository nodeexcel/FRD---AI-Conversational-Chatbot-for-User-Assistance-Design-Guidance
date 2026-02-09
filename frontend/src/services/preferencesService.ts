// User Preferences Service
import axios from 'axios';
import { UserPreferences } from '../types';

const API_URL = 'http://localhost:8001/api/preferences';

// Extended preferences interface for design-specific preferences
export interface DesignPreferences {
  preferred_colors: string[];
  preferred_fabrics: string[];
  preferred_styles: string[];
  preferred_occasions: string[];
  body_type?: string;
  fit_preference?: string;
  size_preference?: string;
  budget_min?: number;
  budget_max?: number;
  budget_currency?: string;
  language_preference?: string;
  preferred_brands?: string[];
  avoid_colors?: string[];
  avoid_fabrics?: string[];
}

export interface PreferencesUpdate {
  theme?: string;
  language?: string;
  notifications?: boolean;
  chat_history_limit?: number;
  design_preferences?: DesignPreferences;
}

export const AVAILABLE_OPTIONS = {
  bodyTypes: ['Slim', 'Athletic', 'Average', 'Curvy', 'Plus Size'],
  colors: [
    'Black', 'White', 'Navy', 'Blue', 'Red', 'Green', 'Yellow', 
    'Pink', 'Purple', 'Orange', 'Brown', 'Gray', 'Beige', 'Burgundy'
  ],
  fabrics: [
    'Cotton', 'Silk', 'Linen', 'Wool', 'Polyester', 'Denim', 
    'Velvet', 'Chiffon', 'Satin', 'Leather', 'Rayon', 'Modal'
  ],
  styles: [
    'Casual', 'Formal', 'Business', 'Sporty', 'Boho', 'Classic',
    'Modern', 'Vintage', 'Streetwear', 'Minimalist', 'Romantic'
  ],
  occasions: [
    'Daily Wear', 'Work', 'Party', 'Wedding', 'Beach', 'Workout',
    'Date Night', 'Travel', 'Home', 'Special Events'
  ],
  fits: ['Slim', 'Regular', 'Loose', 'Oversized', 'Tailored'],
  sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'],
  languages: [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'hi', name: 'Hindi' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
  ],
  themes: ['light', 'dark', 'system']
};

class PreferencesService {
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

  async getPreferences(): Promise<UserPreferences | null> {
    try {
      const response = await axios.get(`${API_URL}/`, {
        headers: this.getHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching preferences:', error);
      return null;
    }
  }

  async updatePreferences(preferences: PreferencesUpdate): Promise<UserPreferences | null> {
    try {
      const response = await axios.put(`${API_URL}/`, preferences, {
        headers: this.getHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error updating preferences:', error);
      return null;
    }
  }

  async updateLanguage(language: string): Promise<boolean> {
    try {
      await axios.put(`${API_URL}/`, { language }, {
        headers: this.getHeaders()
      });
      return true;
    } catch (error) {
      console.error('Error updating language preference:', error);
      return false;
    }
  }

  async updateDesignPreferences(designPrefs: DesignPreferences): Promise<boolean> {
    try {
      await axios.put(`${API_URL}/`, { design_preferences: designPrefs }, {
        headers: this.getHeaders()
      });
      return true;
    } catch (error) {
      console.error('Error updating design preferences:', error);
      return false;
    }
  }

  async getLanguage(): Promise<string> {
    const prefs = await this.getPreferences();
    return prefs?.language || 'en';
  }

  async resetPreferences(): Promise<boolean> {
    try {
      await axios.delete(`${API_URL}/reset`, {
        headers: this.getHeaders()
      });
      return true;
    } catch (error) {
      console.error('Error resetting preferences:', error);
      return false;
    }
  }
}

export const preferencesService = new PreferencesService();
