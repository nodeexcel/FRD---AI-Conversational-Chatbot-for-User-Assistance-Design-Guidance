// Documents Management Page for RAG Knowledge Base
import React, { useState, useEffect } from 'react';
import ChatLayout from '../components/Layout/ChatLayout';
import axios from 'axios';

const API_URL = 'http://localhost:8001/api/documents';

interface Document {
  id: string;
  title: string;
  document_type: string;
  file_path: string | null;
  file_size: number | null;
  status: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
  indexed_at: string | null;
}

const documentTypes = [
  { value: 'faq', label: 'FAQ', description: 'Frequently Asked Questions' },
  { value: 'manual', label: 'Manual', description: 'Product/Service Manuals' },
  { value: 'guide', label: 'Guide', description: 'How-to Guides' },
  { value: 'process_map', label: 'Process Map', description: 'Process Documentation' },
  { value: 'policy', label: 'Policy', description: 'Company Policies' },
  { value: 'product_guide', label: 'Product Guide', description: 'Product Specifications' },
  { value: 'training_material', label: 'Training', description: 'Training Content' },
  { value: 'other', label: 'Other', description: 'Other Documents' },
];

const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Upload form state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState('faq');
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/`);
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('Error loading documents:', error);
      setMessage({ type: 'error', text: 'Failed to load documents' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file: File) => {
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/markdown',
      'text/html',
      'text/csv',
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setMessage({ type: 'error', text: 'Invalid file type. Please select PDF, DOCX, TXT, MD, HTML, or CSV.' });
      return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'File too large. Maximum size is 50MB.' });
      return;
    }
    
    setSelectedFile(file);
    if (!title) {
      setTitle(file.name.replace(/\.[^/.]+$/, ''));
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !title) {
      setMessage({ type: 'error', text: 'Please select a file and enter a title.' });
      return;
    }

    try {
      setUploading(true);
      setMessage(null);

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title);
      formData.append('document_type', documentType);

      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage({ 
        type: 'success', 
        text: `Document uploaded successfully! ${response.data.chunk_count} chunks indexed.` 
      });
      
      // Reset form
      setSelectedFile(null);
      setTitle('');
      
      // Reload documents
      await loadDocuments();
      
    } catch (error: any) {
      console.error('Upload error:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to upload document' 
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/${documentId}`);
      setMessage({ type: 'success', text: 'Document deleted successfully.' });
      await loadDocuments();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete document.' });
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      indexed: 'bg-green-100 text-green-800',
      processing: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <ChatLayout>
      <div className="p-6 max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Base Documents</h1>
        <p className="text-gray-600 mb-8">Upload documents (PDF, DOCX, TXT, MD, HTML, CSV) for RAG-powered question answering</p>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {message.text}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl border border-gray-200 p-6 sticky top-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h2>
              
              {/* Document Type Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Type
                </label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {documentTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {documentTypes.find(t => t.value === documentType)?.description}
                </p>
              </div>

              {/* Title Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter document title"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              {/* File Drop Zone */}
              <div
                className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors ${
                  dragActive 
                    ? 'border-indigo-500 bg-indigo-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf,.docx,.txt,.md,.html,.csv"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileSelect(e.target.files[0]);
                    }
                  }}
                />
                
                {selectedFile ? (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span className="text-sm text-gray-700">{selectedFile.name}</span>
                    </div>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ) : (
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-600">
                      <span className="font-medium text-indigo-600 hover:text-indigo-500">
                        Upload a file
                      </span>
                      {' or drag and drop'}
                    </p>
                    <p className="text-xs text-gray-500">PDF, DOCX, TXT, MD, HTML, CSV (max 50MB)</p>
                  </label>
                )}
              </div>

              {/* Upload Button */}
              <button
                onClick={handleUpload}
                disabled={!selectedFile || !title || uploading}
                className="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    Upload Document
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Documents List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Uploaded Documents</h2>
                <button
                  onClick={loadDocuments}
                  className="text-sm text-indigo-600 hover:text-indigo-700"
                >
                  Refresh
                </button>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
              ) : documents.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
                  <p className="mt-1 text-sm text-gray-500">Upload your first document to get started.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{doc.title}</p>
                          <div className="flex items-center gap-3 text-sm text-gray-500">
                            <span className="capitalize">{doc.document_type.replace('_', ' ')}</span>
                            <span>•</span>
                            <span>{doc.chunk_count} chunks</span>
                            <span>•</span>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(doc.status)}`}>
                              {doc.status}
                            </span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete document"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ChatLayout>
  );
};

export default DocumentsPage;
