// Settings page with User Preferences
import React, { useState, useEffect } from 'react';
import ChatLayout from '../components/Layout/ChatLayout';
import { 
  preferencesService, 
  AVAILABLE_OPTIONS, 
  DesignPreferences,
  PreferencesUpdate 
} from '../services/preferencesService';
import { UserPreferences } from '../types';

const SettingsPage: React.FC = () => {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'personal' | 'style' | 'fit' | 'budget'>('personal');

  // Form state for design preferences
  const [designPrefs, setDesignPrefs] = useState<DesignPreferences>({
    preferred_colors: [],
    preferred_fabrics: [],
    preferred_styles: [],
    preferred_occasions: [],
    avoid_colors: [],
    avoid_fabrics: [],
  });

  // Form state for other preferences
  const [otherPrefs, setOtherPrefs] = useState<PreferencesUpdate>({
    theme: 'system',
    language: 'en',
    notifications: true,
    chat_history_limit: 100,
  });

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const prefs = await preferencesService.getPreferences();
      setPreferences(prefs);
      
      if (prefs) {
        // Load design preferences
        setDesignPrefs({
          preferred_colors: (prefs as any).preferred_colors || [],
          preferred_fabrics: (prefs as any).preferred_fabrics || [],
          preferred_styles: (prefs as any).preferred_styles || [],
          preferred_occasions: (prefs as any).preferred_occasions || [],
          body_type: (prefs as any).body_type,
          fit_preference: (prefs as any).fit_preference,
          size_preference: (prefs as any).size_preference,
          budget_min: (prefs as any).budget_min,
          budget_max: (prefs as any).budget_max,
          budget_currency: (prefs as any).budget_currency || 'USD',
          language_preference: (prefs as any).language_preference,
          preferred_brands: (prefs as any).preferred_brands || [],
          avoid_colors: (prefs as any).avoid_colors || [],
          avoid_fabrics: (prefs as any).avoid_fabrics || [],
        });
        
        // Load other preferences
        setOtherPrefs({
          theme: prefs.theme || 'system',
          language: prefs.language || 'en',
          notifications: prefs.notifications ?? true,
          chat_history_limit: prefs.chat_history_limit || 100,
        });
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      setMessage({ type: 'error', text: 'Failed to load preferences' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await preferencesService.updateDesignPreferences(designPrefs);
      await preferencesService.updatePreferences(otherPrefs);
      setMessage({ type: 'success', text: 'Preferences saved successfully!' });
      await loadPreferences();
      
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save preferences' });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    try {
      await preferencesService.resetPreferences();
      setMessage({ type: 'success', text: 'Preferences reset to defaults' });
      await loadPreferences();
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to reset preferences' });
    }
  };

  const toggleArrayItem = (field: keyof DesignPreferences, item: string) => {
    const current = designPrefs[field] as string[] || [];
    const updated = current.includes(item)
      ? current.filter(i => i !== item)
      : [...current, item];
    setDesignPrefs({ ...designPrefs, [field]: updated });
  };

  const isSelected = (field: keyof DesignPreferences, item: string) => {
    const current = designPrefs[field] as string[] || [];
    return current.includes(item);
  };

  const tabs = [
    { id: 'personal', label: 'Personal Info', icon: '👤' },
    { id: 'style', label: 'Style Preferences', icon: '🎨' },
    { id: 'fit', label: 'Fit & Size', icon: '👗' },
    { id: 'budget', label: 'Budget', icon: '💰' },
  ];

  return (
    <ChatLayout>
      <div className="p-6 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600 mb-8">Configure your preferences for personalized recommendations</p>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {message.text}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <>
            <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-white text-indigo-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === 'personal' && (
              <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Personal Information</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Body Type
                    </label>
                    <select
                      value={designPrefs.body_type || ''}
                      onChange={(e) => setDesignPrefs({ ...designPrefs, body_type: e.target.value || undefined })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select body type</option>
                      {AVAILABLE_OPTIONS.bodyTypes.map((type: string) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select
                      value={otherPrefs.language || 'en'}
                      onChange={(e) => setOtherPrefs({ ...otherPrefs, language: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      {AVAILABLE_OPTIONS.languages.map((lang: { code: string; name: string }) => (
                        <option key={lang.code} value={lang.code}>{lang.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'style' && (
              <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Style Preferences</h2>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Preferred Colors
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_OPTIONS.colors.map((color: string) => (
                      <button
                        key={color}
                        onClick={() => toggleArrayItem('preferred_colors', color)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          isSelected('preferred_colors', color)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {color}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Colors to Avoid
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_OPTIONS.colors.map((color: string) => (
                      <button
                        key={color}
                        onClick={() => toggleArrayItem('avoid_colors', color)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          isSelected('avoid_colors', color)
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {color}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Preferred Fabrics
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_OPTIONS.fabrics.map((fabric: string) => (
                      <button
                        key={fabric}
                        onClick={() => toggleArrayItem('preferred_fabrics', fabric)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          isSelected('preferred_fabrics', fabric)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {fabric}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Preferred Styles
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_OPTIONS.styles.map((style: string) => (
                      <button
                        key={style}
                        onClick={() => toggleArrayItem('preferred_styles', style)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          isSelected('preferred_styles', style)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Preferred Occasions
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_OPTIONS.occasions.map((occasion: string) => (
                      <button
                        key={occasion}
                        onClick={() => toggleArrayItem('preferred_occasions', occasion)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          isSelected('preferred_occasions', occasion)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {occasion}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'fit' && (
              <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Fit & Size Preferences</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fit Preference
                    </label>
                    <select
                      value={designPrefs.fit_preference || ''}
                      onChange={(e) => setDesignPrefs({ ...designPrefs, fit_preference: e.target.value || undefined })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select fit</option>
                      {AVAILABLE_OPTIONS.fits.map((fit: string) => (
                        <option key={fit} value={fit}>{fit}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Size Preference
                    </label>
                    <select
                      value={designPrefs.size_preference || ''}
                      onChange={(e) => setDesignPrefs({ ...designPrefs, size_preference: e.target.value || undefined })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select size</option>
                      {AVAILABLE_OPTIONS.sizes.map((size: string) => (
                        <option key={size} value={size}>{size}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'budget' && (
              <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Budget Preferences</h2>
                <p className="text-gray-500 text-sm">Set your budget range for dress recommendations</p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Min Budget ($)
                    </label>
                    <input
                      type="number"
                      value={designPrefs.budget_min || ''}
                      onChange={(e) => setDesignPrefs({ ...designPrefs, budget_min: parseFloat(e.target.value) || undefined })}
                      placeholder="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Budget ($)
                    </label>
                    <input
                      type="number"
                      value={designPrefs.budget_max || ''}
                      onChange={(e) => setDesignPrefs({ ...designPrefs, budget_max: parseFloat(e.target.value) || undefined })}
                      placeholder="1000"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Currency
                    </label>
                    <select
                      value={designPrefs.budget_currency || 'USD'}
                      onChange={(e) => setDesignPrefs({ ...designPrefs, budget_currency: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                      <option value="INR">INR</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6 flex justify-between">
              <button
                onClick={handleReset}
                className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
              >
                Reset to Defaults
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {saving && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                )}
                {saving ? 'Saving...' : 'Save Preferences'}
              </button>
            </div>

            {preferences && (
              <div className="mt-8 bg-gray-50 rounded-xl p-4 text-sm text-gray-600">
                <p>Last updated: {new Date(preferences.updated_at).toLocaleDateString()}</p>
              </div>
            )}
          </>
        )}
      </div>
    </ChatLayout>
  );
};

export default SettingsPage;
