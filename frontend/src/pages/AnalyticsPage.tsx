// Analytics Dashboard Page - Learning Loop & User Insights
import React, { useState, useEffect } from 'react';
import ChatLayout from '../components/Layout/ChatLayout';
import analyticsService, { UserAnalytics, AgentUsageData, ChatMessage } from '../services/analyticsService';

const AGENT_LABELS: Record<string, string> = {
  nlu: '🤖 General Assistant',
  rag: '📚 Knowledge Base',
  sql: '🗄️ Database',
  design: '🎨 Design Studio',
  voice: '🎤 Voice',
  translation: '🌍 Translator',
  feedback: '📝 Feedback',
};

const AnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [agentUsage, setAgentUsage] = useState<AgentUsageData | null>(null);
  const [recentMessages, setRecentMessages] = useState<ChatMessage[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'activity' | 'agents' | 'history'>('overview');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [analyticsRes, agentRes, messagesRes] = await Promise.all([
        analyticsService.getSummary(),
        analyticsService.getAgentUsage(),
        analyticsService.getMessages(20),
      ]);
      setAnalytics(analyticsRes);
      setAgentUsage(agentRes);
      setRecentMessages(messagesRes);
    } catch (error) {
      console.error('Error loading analytics:', error);
      setMessage({ type: 'error', text: 'Failed to load analytics data' });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const StatCard = ({ 
    title, 
    value, 
    icon, 
    subtitle 
  }: { 
    title: string; 
    value: string | number; 
    icon: string; 
    subtitle?: string;
  }) => (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );

  return (
    <ChatLayout>
      <div className="p-6 max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
            <p className="text-gray-600">Track your learning progress and usage patterns</p>
          </div>
          <button
            onClick={loadAnalytics}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'activity', label: 'Activity', icon: '📈' },
            { id: 'agents', label: 'Agents', icon: '🤖' },
            { id: 'history', label: 'History', icon: '📜' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
                activeTab === tab.id
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && analytics && (
              <div className="space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatCard
                    title="Total Messages"
                    value={analytics.total_messages}
                    icon="💬"
                    subtitle="Chat interactions"
                  />
                  <StatCard
                    title="Chat Sessions"
                    value={analytics.total_sessions}
                    icon="💭"
                    subtitle="Conversation threads"
                  />
                  <StatCard
                    title="Avg Response Time"
                    value={formatDuration(analytics.average_response_time_ms)}
                    icon="⚡"
                    subtitle="AI response speed"
                  />
                  <StatCard
                    title="Designs Created"
                    value={analytics.total_designs_created}
                    icon="🎨"
                    subtitle="Design sessions"
                  />
                </div>

                {/* Second Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 Knowledge Base</h3>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Documents Uploaded</span>
                      <span className="text-2xl font-bold text-indigo-600">{analytics.documents_uploaded}</span>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">⭐ User Rating</h3>
                    <div className="flex items-center gap-2">
                      <span className="text-4xl font-bold text-yellow-500">{analytics.average_rating.toFixed(1)}</span>
                      <div className="flex gap-0.5">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <svg
                            key={star}
                            className={`w-6 h-6 ${star <= Math.round(analytics.average_rating) ? 'text-yellow-400' : 'text-gray-200'}`}
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">🏆 Top Agent</h3>
                    {analytics.favorite_agents.length > 0 ? (
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{analytics.favorite_agents[0].label?.split(' ')[0] || '🤖'}</span>
                        <div>
                          <p className="font-medium text-gray-900">{analytics.favorite_agents[0].label || 'General'}</p>
                          <p className="text-sm text-gray-500">{analytics.favorite_agents[0].count} uses</p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-500">No data yet</p>
                    )}
                  </div>
                </div>

                {/* Agent Usage */}
                {agentUsage && agentUsage.agents.length > 0 && (
                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 Agent Usage Breakdown</h3>
                    <div className="space-y-4">
                      {agentUsage.agents.map((agent) => (
                        <div key={agent.agent} className="flex items-center gap-4">
                          <span className="text-2xl w-8">{agent.label?.split(' ')[0] || '🤖'}</span>
                          <div className="flex-1">
                            <div className="flex justify-between text-sm mb-1">
                              <span className="font-medium text-gray-700">{agent.label || agent.agent}</span>
                              <span className="text-gray-500">{agent.percentage}%</span>
                            </div>
                            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-indigo-600 rounded-full"
                                style={{ width: `${agent.percentage}%` }}
                              />
                            </div>
                          </div>
                          <span className="text-sm text-gray-500 w-12 text-right">{agent.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Activity Tab */}
            {activeTab === 'activity' && (
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">📈 Weekly Activity</h3>
                {analytics?.daily_message_counts && analytics.daily_message_counts.length > 0 ? (
                  <div className="space-y-3">
                    {analytics.daily_message_counts.map((day) => (
                      <div key={day.date} className="flex items-center gap-4">
                        <span className="text-sm text-gray-500 w-24">
                          {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                        </span>
                        <div className="flex-1 h-8 bg-gray-100 rounded-lg overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg"
                            style={{ width: `${Math.min(100, (day.count / Math.max(...analytics.daily_message_counts.map(d => d.count))) * 100)}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700 w-12 text-right">{day.count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <div className="text-4xl mb-4">📊</div>
                    <p>No activity data yet. Start chatting to see your activity!</p>
                  </div>
                )}
              </div>
            )}

            {/* Agents Tab */}
            {activeTab === 'agents' && agentUsage && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agentUsage.agents.map((agent) => (
                  <div key={agent.agent} className="bg-white rounded-xl border border-gray-200 p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center text-2xl">
                        {agent.label?.split(' ')[0] || '🤖'}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{agent.label || agent.agent}</h3>
                        <p className="text-sm text-gray-500">{agent.count} interactions</p>
                      </div>
                    </div>
                    <div className="mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-500">Usage</span>
                        <span className="font-medium">{agent.percentage}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-600 rounded-full"
                          style={{ width: `${agent.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
                {agentUsage.agents.length === 0 && (
                  <div className="col-span-3 text-center py-12 text-gray-500">
                    <div className="text-4xl mb-4">🤖</div>
                    <p>No agent usage data yet. Start chatting!</p>
                  </div>
                )}
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">📜 Recent Messages</h3>
                {recentMessages.length > 0 ? (
                  <div className="space-y-4">
                    {recentMessages.slice(0, 10).map((msg) => (
                      <div key={msg.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">
                              {AGENT_LABELS[msg.agent_used]?.split(' ')[0] || '🤖'}
                            </span>
                            <span className="text-sm font-medium text-gray-700">
                              {AGENT_LABELS[msg.agent_used] || msg.agent_used}
                            </span>
                          </div>
                          <span className="text-xs text-gray-400">{formatDate(msg.created_at)}</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-gray-50 rounded-lg p-3">
                            <p className="text-xs text-gray-500 mb-1">You</p>
                            <p className="text-sm text-gray-900 line-clamp-2">{msg.user_message}</p>
                          </div>
                          <div className="bg-indigo-50 rounded-lg p-3">
                            <p className="text-xs text-indigo-500 mb-1">AI Response</p>
                            <p className="text-sm text-gray-900 line-clamp-2">{msg.ai_response}</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                          <span className="text-xs text-gray-400">
                            {formatDuration(msg.response_time_ms)}
                          </span>
                          <div className="flex items-center gap-2">
                            {msg.was_helpful !== null && (
                              <span className={`text-xs px-2 py-1 rounded ${
                                msg.was_helpful ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                              }`}>
                                {msg.was_helpful ? '👍 Helpful' : '👎 Not helpful'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <div className="text-4xl mb-4">📜</div>
                    <p>No chat history yet. Start a conversation!</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Learning Tips */}
        <div className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Learning Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { icon: '📚', title: 'Upload Documents', desc: 'Add your knowledge base for better answers' },
              { icon: '🎨', title: 'Try Design Studio', desc: 'Create custom designs with guided steps' },
              { icon: '⭐', title: 'Give Feedback', desc: 'Rate responses to improve AI accuracy' },
            ].map((tip, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-2xl">{tip.icon}</span>
                <div>
                  <p className="font-medium text-gray-900">{tip.title}</p>
                  <p className="text-sm text-gray-600">{tip.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </ChatLayout>
  );
};

export default AnalyticsPage;
