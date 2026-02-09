// Internationalization utilities for the AI Chatbot

export type Language = 'en' | 'es' | 'fr' | 'de' | 'hi' | 'ta' | 'te' | 'zh' | 'ja' | 'ko' | 'ar' | 'pt';

export interface LanguageInfo {
  code: Language;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
}

export const SUPPORTED_LANGUAGES: LanguageInfo[] = [
  { code: 'en', name: 'English', nativeName: 'English', direction: 'ltr' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', direction: 'ltr' },
  { code: 'fr', name: 'French', nativeName: 'Français', direction: 'ltr' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', direction: 'ltr' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', direction: 'ltr' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', direction: 'ltr' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', direction: 'ltr' },
  { code: 'zh', name: 'Chinese', nativeName: '中文', direction: 'ltr' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語', direction: 'ltr' },
  { code: 'ko', name: 'Korean', nativeName: '한국어', direction: 'ltr' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', direction: 'rtl' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', direction: 'ltr' },
];

export interface TranslationDict {
  [key: string]: {
    [lang in Language]?: string;
  };
}

// UI Translations
export const UI_TRANSLATIONS: TranslationDict = {
  welcome: {
    en: 'Hello! I am your dress design assistant. How can I help you today?',
    es: '¡Hola! Soy tu asistente de diseño de vestidos. ¿Cómo puedo ayudarte hoy?',
    hi: 'नमस्ते! मैं आपकी ड्रेस डिज़ाइन सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?',
    ta: 'வணக்கம்! நான் உங்கள் ஆடை வடிவமைப்பு உதவியாளர். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?',
    te: 'నమస్కారం! నేను మీ డ్రెస్ డిజైన్ సహాయకుడిని. నేడు నేను మీకు ఎలా సహాయపడగలను?',
  },
  typing: {
    en: 'Typing...',
    es: 'Escribiendo...',
    hi: 'टाइप कर रहा है...',
    ta: 'தட்டச்சு செய்கிறது...',
    te: 'టైప్ చేస్తోంది...',
  },
  send: {
    en: 'Send',
    es: 'Enviar',
    hi: 'भेजें',
    ta: 'அனுப்பு',
    te: 'పంపు',
  },
  voiceInput: {
    en: 'Voice input',
    es: 'Entrada de voz',
    hi: 'आवाज़ इनपुट',
    ta: 'குரல் உள்ளீடு',
    te: 'వాయిస్ ఇన్పుట్',
  },
  selectLanguage: {
    en: 'Select language',
    es: 'Seleccionar idioma',
    hi: 'भाषा चुनें',
    ta: 'மொழியைத் தேர்ந்தெடு',
    te: 'భాషను ఎంచుకోండి',
  },
  errorGeneric: {
    en: 'I apologize, but I encountered an error. Please try again.',
    es: 'Me disculpo, pero encontré un error. Por favor, inténtalo de nuevo.',
    hi: 'मुझे खेद है, लेकिन मुझे एक त्रुटि मिली। कृपया पुनः प्रयास करें।',
    ta: 'குறிப்பு: ஒரு பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.',
    te: 'క్షమించండి, ఒక లోపం జరిగింది. దయచేసి మళ్ళీ ప్రయత్నించండి.',
  },
  clarifyIntent: {
    en: "I'm not sure I understand. Could you please clarify what you're looking for?",
    es: 'No estoy seguro de entender. ¿Podrías aclarar lo que buscas?',
    hi: 'मुझे समझ नहीं आ रहा। क्या आप स्पष्ट कर सकते हैं कि आप क्या खोज रहे हैं?',
    ta: 'எனக்கு புரியவில்லை. நீங்கள் எதை தேடுகிறீர்கள் என்பதை தெளிவாக்க முடியுமா?',
    te: 'నాకు అర్ధం కాలేదు. మీరు ఏమి వెతుకుతున్నారో స్పష్టం చేయగలరా?',
  },
  lowConfidence: {
    en: "I'm not entirely confident about this answer. Would you like me to connect you with a human expert?",
    es: 'No estoy muy seguro de esta respuesta. ¿Te gustaría que te conectara con un experto humano?',
    hi: 'इस उत्तर के बारे में मुझे पूरा भरोसा नहीं है। क्या आप चाहेंगे कि मैं आपको मानव विशेषज्ञ से जोड़ूं?',
    ta: 'இந்த பதில் பற்றி எனக்கு முழு நம்பிக்கை இல்லை. நீங்கள் ஒரு மனித நிபுணரை தொடர்பு கொள்ள விரும்புகிறீர்களா?',
    te: 'ఈ సమాధానం గురించి నాకు పూర్తి విశ్వాసం లేదు. మీరు మానవ నిపుణుడిని సంప్రదించాలని అనుకుంటున్నారా?',
  },
};

// Translation function
export function translate(key: string, lang: Language, fallback: Language = 'en'): string {
  const translation = UI_TRANSLATIONS[key]?.[lang];
  if (translation) return translation;
  
  // Fallback to English
  const fallbackTranslation = UI_TRANSLATIONS[key]?.[fallback];
  if (fallbackTranslation) return fallbackTranslation;
  
  // Return key if no translation found
  return key;
}

// Get language direction
export function getLanguageDirection(lang: Language): 'ltr' | 'rtl' {
  const language = SUPPORTED_LANGUAGES.find(l => l.code === lang);
  return language?.direction || 'ltr';
}

// Get language name
export function getLanguageName(code: Language): string {
  const language = SUPPORTED_LANGUAGES.find(l => l.code === code);
  return language?.name || code;
}

// Get native language name
export function getNativeLanguageName(code: Language): string {
  const language = SUPPORTED_LANGUAGES.find(l => l.code === code);
  return language?.nativeName || code;
}

// Avatar voice mappings
export interface AvatarInfo {
  id: string;
  name: string;
  voiceId: string;
  voiceName: string;
  style: 'professional' | 'friendly' | 'elegant';
}

export const AVATARS: AvatarInfo[] = [
  { id: 'sophia', name: 'Sophia', voiceId: 'alloy', voiceName: 'Alloy', style: 'professional' },
  { id: 'emma', name: 'Emma', voiceId: 'echo', voiceName: 'Echo', style: 'friendly' },
  { id: 'james', name: 'James', voiceId: 'fable', voiceName: 'Fable', style: 'professional' },
  { id: 'aria', name: 'Aria', voiceId: 'nova', voiceName: 'Nova', style: 'elegant' },
  { id: 'default', name: 'Default', voiceId: 'shimmer', voiceName: 'Shimmer', style: 'friendly' },
];

export function getVoiceForAvatar(avatarId: string): AvatarInfo | undefined {
  return AVATARS.find(a => a.id === avatarId);
}

export function getDefaultAvatar(): AvatarInfo {
  return AVATARS.find(a => a.id === 'default')!;
}
