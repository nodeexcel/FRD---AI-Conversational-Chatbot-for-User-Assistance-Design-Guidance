import React, { useState } from 'react';
import { authService } from '../services/authService';
import axios from 'axios';

const TranslationTestPage: React.FC = () => {
  const token = authService.getToken();
  const [text, setText] = useState('');
  const [targetLang, setTargetLang] = useState('hi');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const supportedLanguages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'hi', name: 'Hindi' },
    { code: 'te', name: 'Telugu' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ar', name: 'Arabic' },
    { code: 'ru', name: 'Russian' },
  ];

  const handleTranslate = async () => {
    if (!text.trim()) {
      alert('Please enter text to translate');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/translate',
        {
          text: text,
          target_lang: targetLang,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setResult(response.data);
    } catch (error: any) {
      console.error('Translation error:', error);
      alert(`Translation failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDetect = async () => {
    if (!text.trim()) {
      alert('Please enter text to detect language');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/translate/detect',
        { text: text },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setResult(response.data);
    } catch (error: any) {
      console.error('Detection error:', error);
      alert(`Detection failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Translation Agent Test</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Enter Text to Translate:
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text in any language..."
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

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Target Language:
        </label>
        <select
          value={targetLang}
          onChange={(e) => setTargetLang(e.target.value)}
          style={{
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            width: '200px',
          }}
        >
          {supportedLanguages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={handleTranslate}
          disabled={loading}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginRight: '10px',
          }}
        >
          {loading ? 'Translating...' : 'Translate'}
        </button>
        
        <button
          onClick={handleDetect}
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
          {loading ? 'Detecting...' : 'Detect Language'}
        </button>
      </div>

      {result && (
        <div
          style={{
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '4px',
            border: '1px solid #dee2e6',
          }}
        >
          <h3>Result:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
            {JSON.stringify(result, null, 2)}
          </pre>

          {result.translated_text && (
            <div style={{ marginTop: '20px' }}>
              <h4>Translated Text:</h4>
              <div
                style={{
                  padding: '15px',
                  backgroundColor: '#e9ecef',
                  borderRadius: '4px',
                  fontSize: '18px',
                }}
              >
                {result.translated_text}
              </div>
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: '30px' }}>
        <h3>Test Examples:</h3>
        <ul>
          <li>
            <button
              onClick={() => setText('Hello, how are you?')}
              style={{ margin: '5px', padding: '5px 10px' }}
            >
              English → Hindi
            </button>
          </li>
          <li>
            <button
              onClick={() => setText('नमस्ते, आप कैसे हैं?')}
              style={{ margin: '5px', padding: '5px 10px' }}
            >
              Hindi → English
            </button>
          </li>
          <li>
            <button
              onClick={() => setText('Hola, ¿cómo estás?')}
              style={{ margin: '5px', padding: '5px 10px' }}
            >
              Spanish → English
            </button>
          </li>
          <li>
            <button
              onClick={() => setText('Show me blue dresses')}
              style={{ margin: '5px', padding: '5px 10px' }}
            >
              English → Telugu
            </button>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default TranslationTestPage;
