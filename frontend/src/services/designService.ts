// Design Service for Guided Design Flow
import axios from 'axios';

const API_URL = 'http://localhost:8001/api/design';

export interface DesignSession {
  id: string;
  name: string;
  description: string | null;
  design_type: string;
  current_step: string;
  status: string;
  progress: number;
  ai_suggestions: Record<string, any> | null;
  user_inputs: Record<string, any> | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface DesignType {
  value: string;
  label: string;
  icon: string;
}

export interface DesignStep {
  id: string;
  title: string;
  description: string;
  questions: string[];
}

export interface DesignSummary {
  session_id: string;
  name: string;
  design_type: string;
  total_steps: number;
  completed_steps: string[];
  progress: number;
  final_design: Record<string, any> | null;
  next_step: string | null;
  feedback_submitted: boolean;
}

export interface DesignFeedback {
  id: string;
  design_session_id: string;
  rating: number;
  comment: string | null;
  what_liked: string | null;
  what_to_improve: string | null;
  created_by: string | null;
  created_at: string;
}

class DesignService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async getDesignTypes(): Promise<{ types: DesignType[] }> {
    const response = await axios.get(`${API_URL}/types`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getDesignSteps(): Promise<DesignStep[]> {
    const response = await axios.get(`${API_URL}/steps`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async createSession(name: string, designType: string, description?: string): Promise<DesignSession> {
    const response = await axios.post(`${API_URL}/sessions`, {
      name,
      design_type: designType,
      description,
    }, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getSessions(status?: string): Promise<DesignSession[]> {
    const params = status ? { status } : {};
    const response = await axios.get(`${API_URL}/sessions`, {
      params,
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getSession(sessionId: string): Promise<DesignSession> {
    const response = await axios.get(`${API_URL}/sessions/${sessionId}`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async updateSession(sessionId: string, data: Partial<DesignSession>): Promise<DesignSession> {
    const response = await axios.put(`${API_URL}/sessions/${sessionId}`, data, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async submitStep(sessionId: string, step: string, data: Record<string, any>): Promise<DesignSession> {
    const response = await axios.post(`${API_URL}/sessions/${sessionId}/step`, {
      step,
      data,
    }, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async completeSession(sessionId: string): Promise<DesignSession> {
    const response = await axios.post(`${API_URL}/sessions/${sessionId}/complete`, {}, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await axios.delete(`${API_URL}/sessions/${sessionId}`, {
      headers: this.getAuthHeaders(),
    });
  }

  async getSummary(sessionId: string): Promise<DesignSummary> {
    const response = await axios.get(`${API_URL}/sessions/${sessionId}/summary`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async submitFeedback(
    sessionId: string,
    rating: number,
    comment?: string,
    whatLiked?: string,
    whatToImprove?: string
  ): Promise<DesignFeedback> {
    const response = await axios.post(`${API_URL}/sessions/${sessionId}/feedback`, {
      rating,
      comment,
      what_liked: whatLiked,
      what_to_improve: whatToImprove,
    }, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getFeedback(sessionId: string): Promise<DesignFeedback> {
    const response = await axios.get(`${API_URL}/sessions/${sessionId}/feedback`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }
}

export const designService = new DesignService();
export default designService;
