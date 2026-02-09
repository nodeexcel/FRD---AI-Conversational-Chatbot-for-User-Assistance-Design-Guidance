// Language Selector Component
import React from 'react';
import { Globe } from 'lucide-react';

interface LanguageSelectorProps {
  selectedLang: string;
  onLangChange: (lang: string) => void;
  disabled?: boolean;
}

const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
  { code: 'te', name: 'తెలుగు', flag: '🇮🇳' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
];

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  selectedLang,
  onLangChange,
  disabled = false,
}) => {
  const currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLang);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <select
        value={selectedLang}
        onChange={(e) => onLangChange(e.target.value)}
        disabled={disabled}
        style={{
          padding: '8px 12px 8px 36px',
          fontSize: '14px',
          border: '1px solid #ddd',
          borderRadius: '20px',
          backgroundColor: 'white',
          cursor: disabled ? 'not-allowed' : 'pointer',
          appearance: 'none',
          minWidth: '150px',
        }}
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
      <Globe
        size={16}
        style={{
          position: 'absolute',
          left: '10px',
          top: '50%',
          transform: 'translateY(-50%)',
          color: '#666',
        }}
      />
    </div>
  );
};

export default LanguageSelector;
export { SUPPORTED_LANGUAGES };
