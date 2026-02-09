// Analytics Service for Learning Loop
import axios from 'axios';

const API_URL = 'http://localhost:8001/api/analytics';

export interface ChatMessage {
  id: string;
  session_id: string;
  user_message: string;
  ai_response: string;
  agent_used: string;
  agent_label?: string;
  response_time_ms: number;
  tokens_used: number | null;
  was_helpful: boolean | null;
  feedback: string | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  started_at: string;
  ended_at: string | null;
  message_count: number;
  total_response_time_ms: number;
  agents_used: string[];
  topics_discussed: string[];
}

export interface UserAnalytics {
  total_sessions: number;
  total_messages: number;
  average_response_time_ms: number;
  favorite_agents: { agent: string; count: number; label?: string }[];
  daily_message_counts: { date: string; count: number }[];
  weekly_activity: Record<string, number>;
  top_topics: { topic: string; count: number }[];
  average_rating: number;
  total_designs_created: number;
  documents_uploaded: number;
}

export interface ActivityData {
  activity: { date: string; messages: number }[];
  total_messages: number;
}

export interface AgentUsageData {
  agents: { agent: string; count: number; label: string; percentage: number }[];
  total_requests: number;
}

export interface LearningFeedback {
  session_id?: string;
  category: string;
  rating: number;
  comment?: string;
  suggested_improvement?: string;
}

class AnalyticsService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async logMessage(
    sessionId: string,
    userMessage: string,
    aiResponse: string,
    agentUsed: string,
    responseTimeMs: number,
    tokensUsed?: number
  ): Promise<void> {
    await axios.post(`${API_URL}/messages`, {
      session_id: sessionId,
      user_message: userMessage,
      ai_response: aiResponse,
      agent_used: agentUsed,
      response_time_ms: responseTimeMs,
      tokens_used: tokensUsed,
    }, {
      headers: this.getAuthHeaders(),
    });
  }

  async startSession(sessionId: string): Promise<void> {
    await axios.post(`${API_URL}/sessions/${sessionId}/start`, {}, {
      headers: this.getAuthHeaders(),
    });
  }

  async endSession(sessionId: string): Promise<void> {
    await axios.post(`${API_URL}/sessions/${sessionId}/end`, {}, {
      headers: this.getAuthHeaders(),
    });
  }

  async getMessages(limit: number = 50): Promise<ChatMessage[]> {
    const response = await axios.get(`${API_URL}/messages`, {
      params: { limit },
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getSessions(limit: number = 30): Promise<ChatSession[]> {
    const response = await axios.get(`${API_URL}/sessions`, {
      params: { limit },
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async updateMessageFeedback(
    messageId: string,
    wasHelpful: boolean,
    feedback?: string
  ): Promise<void> {
    await axios.put(`${API_URL}/messages/${messageId}/feedback`, null, {
      params: { was_helpful: wasHelpful, feedback },
      headers: this.getAuthHeaders(),
    });
  }

  async submitLearningFeedback(data: LearningFeedback): Promise<void> {
    await axios.post(`${API_URL}/learning-feedback`, data, {
      headers: this.getAuthHeaders(),
    });
  }

  async getSummary(): Promise<UserAnalytics> {
    const response = await axios.get(`${API_URL}/summary`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getActivity(days: number = 7): Promise<ActivityData> {
    const response = await axios.get(`${API_URL}/activity`, {
      params: { days },
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getAgentUsage(): Promise<AgentUsageData> {
    const response = await axios.get(`${API_URL}/agent-usage`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }
}

export const analyticsService = new AnalyticsService();
export default analyticsService;
