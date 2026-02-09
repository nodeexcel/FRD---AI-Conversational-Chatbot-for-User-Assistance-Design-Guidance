// Analytics Dashboard Page
import React, { useState, useEffect } from 'react';
import ChatLayout from '../components/Layout/ChatLayout';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/analytics';

interface DashboardData {
  overview: {
    total_conversations: number;
    total_users: number;
    avg_response_time_ms: number;
    satisfaction_rate: number;
  };
  top_intents: Array<{ intent: string; count: number }>;
  completion_rates: {
    design_workflow: number;
    product_search: number;
    general_conversation: number;
  };
  knowledge_gaps_identified: number;
  human_handoffs: number;
}

const AnalyticsDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(7);

  useEffect(() => {
    fetchDashboard();
  }, [period]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/dashboard?days=${period}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    { label: 'Total Conversations', value: dashboard?.overview.total_conversations || 0, icon: '💬' },
    { label: 'Active Users', value: dashboard?.overview.total_users || 0, icon: '👥' },
    { label: 'Avg Response Time', value: `${dashboard?.overview.avg_response_time_ms || 0}ms`, icon: '⚡' },
    { label: 'Satisfaction Rate', value: `${((dashboard?.overview.satisfaction_rate || 0) * 100).toFixed(1)}%`, icon: '😊' },
  ];

  return (
    <ChatLayout>
      <div className="p-6 max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600">Track chatbot performance and user engagement</p>
          </div>
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : dashboard ? (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => (
                <div key={index} className="bg-white rounded-xl border border-gray-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">{stat.label}</p>
                      <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                    </div>
                    <span className="text-3xl">{stat.icon}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Completion Rates */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Completion Rates</h2>
              <div className="space-y-4">
                {Object.entries(dashboard.completion_rates).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize">{key.replace('_', ' ')}</span>
                      <span className="font-medium">{(value * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Intents */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Top User Intents</h2>
              <div className="space-y-3">
                {dashboard.top_intents.slice(0, 5).map((intent, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </span>
                      <span className="capitalize">{intent.intent.replace('_', ' ')}</span>
                    </div>
                    <span className="font-medium text-gray-600">{intent.count} queries</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Issues */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Knowledge Gaps Identified</h2>
                <p className="text-4xl font-bold text-orange-500">{dashboard.knowledge_gaps_identified}</p>
                <p className="text-sm text-gray-500 mt-2">Topics requiring additional content</p>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Human Handoffs</h2>
                <p className="text-4xl font-bold text-red-500">{dashboard.human_handoffs}</p>
                <p className="text-sm text-gray-500 mt-2">Queries escalated to human support</p>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No data available
          </div>
        )}
      </div>
    </ChatLayout>
  );
};

export default AnalyticsDashboard;
