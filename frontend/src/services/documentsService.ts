// Documents Service for RAG Knowledge Base
import axios from 'axios';

const API_URL = 'http://localhost:8001/api/documents';

export interface Document {
  id: string;
  title: string;
  document_type: string;
  file_path: string | null;
  file_size: number | null;
  content_hash: string | null;
  status: string;
  chunk_count: number;
  metadata: Record<string, any>;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  indexed_at: string | null;
}

export interface DocumentUploadResponse {
  id: string;
  title: string;
  document_type: string;
  chunk_count: number;
  status: string;
  message: string;
}

export interface DocumentStats {
  total_documents: number;
  indexed_documents: number;
  processing_documents: number;
  failed_documents: number;
  total_chunks: number;
  documents_by_type: Record<string, number>;
}

class DocumentsService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async getDocuments(): Promise<{ documents: Document[] }> {
    const response = await axios.get(`${API_URL}/`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await axios.get(`${API_URL}/${documentId}`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async uploadDocument(
    file: File,
    title: string,
    documentType: string
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('document_type', documentType);

    const response = await axios.post(`${API_URL}/upload`, formData, {
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    await axios.delete(`${API_URL}/${documentId}`, {
      headers: this.getAuthHeaders(),
    });
  }

  async getDocumentTypes(): Promise<{ types: { value: string; label: string; description: string }[] }> {
    const response = await axios.get(`${API_URL}/types`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getDocumentStats(): Promise<DocumentStats> {
    const response = await axios.get(`${API_URL}/stats`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }
}

export const documentsService = new DocumentsService();
export default documentsService;
