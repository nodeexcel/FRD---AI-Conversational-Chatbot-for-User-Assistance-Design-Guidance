// Guided Design Flow Page with Step-by-Step Wizard
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ChatLayout from '../components/Layout/ChatLayout';
import designService, { DesignType, DesignStep, DesignSession, DesignSummary } from '../services/designService';

const DESIGN_ICONS: Record<string, string> = {
  dress: '👗',
  tops: '👚',
  pants: '👖',
  jacket: '🧥',
  skirt: '🎀',
  saree: '🥻',
  lehenga: '💃',
  suit: '👔',
  other: '✨',
};

const STEPS_ORDER = ['concept', 'measurements', 'fabric', 'style', 'details', 'review'];

const DesignPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  
  // View states: 'list', 'create', 'wizard'
  const [view, setView] = useState<'list' | 'create' | 'wizard'>('list');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Data
  const [sessions, setSessions] = useState<DesignSession[]>([]);
  const [designTypes, setDesignTypes] = useState<DesignType[]>([]);
  const [designSteps, setDesignSteps] = useState<DesignStep[]>([]);
  const [currentSession, setCurrentSession] = useState<DesignSession | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  // Create form
  const [newDesignName, setNewDesignName] = useState('');
  const [newDesignType, setNewDesignType] = useState('dress');
  const [newDesignDesc, setNewDesignDesc] = useState('');
  
  // Wizard form data
  const [formData, setFormData] = useState<Record<string, any>>({});

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId);
    }
  }, [sessionId]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [typesRes, stepsRes, sessionsRes] = await Promise.all([
        designService.getDesignTypes(),
        designService.getDesignSteps(),
        designService.getSessions(),
      ]);
      setDesignTypes(typesRes.types);
      setDesignSteps(stepsRes);
      setSessions(sessionsRes);
    } catch (error) {
      console.error('Error loading data:', error);
      setMessage({ type: 'error', text: 'Failed to load design data' });
    } finally {
      setLoading(false);
    }
  };

  const loadSession = async (id: string) => {
    try {
      setLoading(true);
      const session = await designService.getSession(id);
      setCurrentSession(session);
      setView('wizard');
      
      // Determine current step index
      const stepIndex = STEPS_ORDER.indexOf(session.current_step);
      setCurrentStepIndex(stepIndex >= 0 ? stepIndex : 0);
      
      // Load existing form data
      setFormData(session.user_inputs || {});
    } catch (error) {
      console.error('Error loading session:', error);
      setMessage({ type: 'error', text: 'Failed to load design session' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async () => {
    if (!newDesignName) {
      setMessage({ type: 'error', text: 'Please enter a design name' });
      return;
    }

    try {
      setLoading(true);
      const session = await designService.createSession(newDesignName, newDesignType, newDesignDesc);
      setMessage({ type: 'success', text: 'Design session created!' });
      setNewDesignName('');
      setNewDesignDesc('');
      await loadInitialData();
      setView('wizard');
      setCurrentSession(session);
      setCurrentStepIndex(0);
      setFormData({});
      navigate(`/design/${session.id}`);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to create session' });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (id: string) => {
    if (!confirm('Are you sure you want to delete this design session?')) return;
    
    try {
      await designService.deleteSession(id);
      setMessage({ type: 'success', text: 'Session deleted' });
      await loadInitialData();
      if (sessionId === id) {
        navigate('/design');
        setView('list');
        setCurrentSession(null);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete session' });
    }
  };

  const handleStepSubmit = async (stepId: string, data: any) => {
    if (!currentSession) return;

    try {
      setLoading(true);
      const updated = await designService.submitStep(currentSession.id, stepId, data);
      setCurrentSession(updated);
      
      // Move to next step or complete
      const nextIndex = STEPS_ORDER.indexOf(stepId) + 1;
      if (nextIndex < STEPS_ORDER.length) {
        setCurrentStepIndex(nextIndex);
      }
      
      setMessage({ type: 'success', text: 'Step saved!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save step' });
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!currentSession) return;

    try {
      setLoading(true);
      const completed = await designService.completeSession(currentSession.id);
      setCurrentSession(completed);
      setMessage({ type: 'success', text: 'Design completed!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to complete design' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-700',
      in_progress: 'bg-blue-100 text-blue-700',
      pending_review: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-green-100 text-green-700',
      approved: 'bg-purple-100 text-purple-700',
    };
    return styles[status] || 'bg-gray-100 text-gray-700';
  };

  // Wizard Step Component
  const WizardStep = ({ step, index }: { step: DesignStep; index: number }) => {
    const [answers, setAnswers] = useState<Record<string, string>>(
      formData[step.id]?.answers || {}
    );

    const handleAnswer = (question: string, value: string) => {
      setAnswers(prev => ({ ...prev, [question]: value }));
    };

    const handleSubmit = () => {
      handleStepSubmit(step.id, { answers });
    };

    const handleBack = () => {
      if (currentStepIndex > 0) {
        setCurrentStepIndex(currentStepIndex - 1);
      }
    };

    const currentStep = designSteps[index];
    const isLastStep = index === STEPS_ORDER.length - 1;

    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-8">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">{currentStep.title}</h2>
            <span className="text-sm text-gray-500">Step {index + 1} of {STEPS_ORDER.length}</span>
          </div>
          <div className="flex gap-2 mb-4">
            {STEPS_ORDER.map((s, i) => (
              <div
                key={s}
                className={`h-2 flex-1 rounded-full transition-colors ${
                  i <= index ? 'bg-indigo-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-gray-600">{currentStep.description}</p>
        </div>

        {/* Questions */}
        <div className="space-y-6 mb-8">
          {currentStep.questions.map((question, qIndex) => (
            <div key={qIndex}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {question}
              </label>
              <textarea
                value={answers[question] || ''}
                onChange={(e) => handleAnswer(question, e.target.value)}
                rows={2}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Type your answer..."
              />
            </div>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={handleBack}
            disabled={index === 0}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>
          
          {isLastStep ? (
            <button
              onClick={handleComplete}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Completing...' : 'Complete Design'}
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? 'Saving...' : 'Save & Continue'}
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>
    );
  };

  // View: Wizard
  if (view === 'wizard' && currentSession) {
    const currentStepData = designSteps[currentStepIndex];
    
    return (
      <ChatLayout>
        <div className="p-6 max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  setView('list');
                  setCurrentSession(null);
                  navigate('/design');
                }}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  {DESIGN_ICONS[currentSession.design_type]} {currentSession.name}
                </h1>
                <p className="text-gray-500 text-sm">{currentSession.design_type} • {currentSession.progress}% complete</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(currentSession.status)}`}>
              {currentSession.status.replace('_', ' ')}
            </span>
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {message.text}
            </div>
          )}

          {/* Wizard */}
          {currentStepData && (
            <WizardStep step={currentStepData} index={currentStepIndex} />
          )}
        </div>
      </ChatLayout>
    );
  }

  // View: Create
  if (view === 'create') {
    return (
      <ChatLayout>
        <div className="p-6 max-w-2xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <button
              onClick={() => setView('list')}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Create New Design</h1>
          </div>

          {message && (
            <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {message.text}
            </div>
          )}

          <div className="bg-white rounded-2xl border border-gray-200 p-8">
            {/* Design Type Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">Design Type</label>
              <div className="grid grid-cols-3 gap-3">
                {designTypes.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => setNewDesignType(type.value)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      newDesignType === type.value
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-2xl mb-1">{type.icon}</div>
                    <div className="text-sm font-medium text-gray-900">{type.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Name */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Design Name</label>
              <input
                type="text"
                value={newDesignName}
                onChange={(e) => setNewDesignName(e.target.value)}
                placeholder="e.g., Summer Collection Dress"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Description */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
              <textarea
                value={newDesignDesc}
                onChange={(e) => setNewDesignDesc(e.target.value)}
                rows={3}
                placeholder="Describe your design vision..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Submit */}
            <button
              onClick={handleCreateSession}
              disabled={loading || !newDesignName}
              className="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Creating...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Start Design Wizard
                </>
              )}
            </button>
          </div>
        </div>
      </ChatLayout>
    );
  }

  // View: List
  return (
    <ChatLayout>
      <div className="p-6 max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Guided Design Flow</h1>
            <p className="text-gray-600">Create stunning designs with AI-powered step-by-step guidance</p>
          </div>
          <button
            onClick={() => setView('create')}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Design
          </button>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {message.text}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : sessions.length === 0 ? (
          <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">✨</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No designs yet</h3>
            <p className="text-gray-500 mb-6">Start creating your first design with our AI-powered wizard</p>
            <button
              onClick={() => setView('create')}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700"
            >
              Create Your First Design
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="bg-white rounded-2xl border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/design/${session.id}`)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{DESIGN_ICONS[session.design_type] || '✨'}</div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(session.status)}`}>
                    {session.status.replace('_', ' ')}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{session.name}</h3>
                <p className="text-sm text-gray-500 mb-4 capitalize">{session.design_type}</p>
                
                {/* Progress bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{session.progress}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-indigo-600 rounded-full transition-all"
                      style={{ width: `${session.progress}%` }}
                    />
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <span className="text-xs text-gray-400">
                    {new Date(session.created_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSession(session.id);
                    }}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* How it works */}
        <div className="mt-12 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">How the Design Wizard Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { step: '1', title: 'Concept', desc: 'Define your vision, occasion, and style preferences' },
              { step: '2', title: 'Measurements', desc: 'Provide sizing details and fit preferences' },
              { step: '3', title: 'Fabric', desc: 'Choose materials, colors, and textures' },
              { step: '4', title: 'Style', desc: 'Select necklines, silhouettes, and embellishments' },
              { step: '5', title: 'Details', desc: 'Add finishing touches and special requirements' },
              { step: '6', title: 'Review', desc: 'Review and submit your complete design' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-3">
                  {item.step}
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </ChatLayout>
  );
};

export default DesignPage;
