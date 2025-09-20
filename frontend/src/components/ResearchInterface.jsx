import React, { useState, useRef, useEffect } from 'react';
import { Search, Upload, FileText, Loader, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ApiService from '../services/api';

const ResearchInterface = () => {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [fileInputKey, setFileInputKey] = useState(0);
  const fileInputRef = useRef(null);
  const { user } = useAuth();

  // Ensure file input is properly initialized
  useEffect(() => {
    if (fileInputRef.current) {
      console.log('File input initialized');
    }
  }, [fileInputKey]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    try {
      // Real API call to generate research report
      const reportData = await ApiService.generateResearchReport(question, {
        includeWebSearch: true,
        includeLiveData: true
      });
      
      setReport(reportData);
    } catch (error) {
      console.error('Error generating report:', error);
      // Show error to user
      setReport({
        id: 'error',
        question: question,
        answer: `Error generating report: ${error.message}. Please try again or check your connection.`,
        citations: [],
        sources: [],
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    
    // Add files to local state immediately for UI feedback
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading'
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    
    try {
      // Upload files to backend
      const uploadResult = await ApiService.uploadDocuments(Array.from(files));
      
      // Update file status to uploaded
      setUploadedFiles(prev => 
        prev.map(file => 
          newFiles.some(newFile => newFile.id === file.id) 
            ? { ...file, status: 'uploaded' }
            : file
        )
      );
    } catch (error) {
      console.error('Error uploading files:', error);
      // Update file status to error
      setUploadedFiles(prev => 
        prev.map(file => 
          newFiles.some(newFile => newFile.id === file.id) 
            ? { ...file, status: 'error' }
            : file
        )
      );
    }
  };

  const resetFileInput = () => {
    setFileInputKey(prev => prev + 1);
    console.log('File input reset with new key');
  };

  const handleFileInputChange = (e) => {
    console.log('File input changed:', e.target.files);
    const files = e.target.files;
    if (files && files.length > 0) {
      console.log('Files selected:', Array.from(files).map(f => f.name));
      handleFileUpload(files);
    } else {
      console.log('No files selected or dialog cancelled');
    }
    // Reset the file input after a short delay to ensure it's ready for next use
    setTimeout(() => {
      resetFileInput();
    }, 100);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  return (
    <div className="research-interface">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Research Assistant</h1>
        </div>
        
        {/* File Upload Section */}
        <div className="form-group">
          <label className="form-label">Upload Documents (PDF, DOCX, TXT)</label>
          <div
            className={`file-upload ${dragActive ? 'dragover' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => {
              console.log('File upload area clicked');
              if (fileInputRef.current) {
                console.log('Triggering file input click');
                fileInputRef.current.click();
              } else {
                console.log('File input ref not available, resetting...');
                resetFileInput();
              }
            }}
          >
            <Upload size={48} color="#667eea" />
            <div style={{ marginTop: '1rem' }}>
              <strong>Click to upload</strong> or drag and drop files here
            </div>
            <div style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '0.5rem' }}>
              Supports PDF, DOCX, and TXT files
            </div>
          </div>
          <input
            key={fileInputKey}
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="form-group">
            <label className="form-label">Uploaded Files</label>
            <div>
              {uploadedFiles.map((file) => (
                <div key={file.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem',
                  border: '1px solid #e2e8f0',
                  borderRadius: '0.5rem',
                  marginBottom: '0.5rem',
                  backgroundColor: file.status === 'uploading' ? '#fef3c7' : 
                                 file.status === 'error' ? '#fee2e2' : '#f0fdf4'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <FileText size={16} color={
                      file.status === 'uploading' ? '#f59e0b' :
                      file.status === 'error' ? '#ef4444' : '#10b981'
                    } />
                    <span>{file.name}</span>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                    {file.status === 'uploading' && (
                      <span style={{ fontSize: '0.8rem', color: '#f59e0b' }}>
                        Uploading...
                      </span>
                    )}
                    {file.status === 'error' && (
                      <span style={{ fontSize: '0.8rem', color: '#ef4444' }}>
                        Upload failed
                      </span>
                    )}
                    {file.status === 'uploaded' && (
                      <span style={{ fontSize: '0.8rem', color: '#10b981' }}>
                        ✓ Uploaded
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => removeFile(file.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      padding: '0.25rem',
                      borderRadius: '0.25rem',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#fee2e2'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Question Input */}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">What would you like to research?</label>
            <textarea
              className="form-input form-textarea"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask any question and get a comprehensive research report with citations..."
              rows={4}
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading || !question.trim()}
            >
              {isLoading ? (
                <>
                  <Loader size={18} className="spinner" />
                  Generating Report...
                </>
              ) : (
                <>
                  <Search size={18} />
                  Generate Report
                </>
              )}
            </button>
            
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Cost: 1 credit per report
            </div>
          </div>
        </form>
      </div>

      {/* Report Display */}
      {report && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Research Report</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle size={16} color="#10b981" />
              <span style={{ fontSize: '0.9rem', color: '#10b981' }}>
                Generated {new Date(report.timestamp).toLocaleString()}
              </span>
            </div>
          </div>

          <div className="report-content">
            <div className="report-section">
              <h3>Question</h3>
              <p style={{ fontStyle: 'italic', color: '#64748b' }}>{report.question}</p>
            </div>

            <div className="report-section">
              <h3>Answer</h3>
              <div style={{ whiteSpace: 'pre-line' }}>{report.answer}</div>
            </div>

            {report.citations && report.citations.length > 0 && (
              <div className="report-section">
                <h3>Citations</h3>
                {report.citations.map((citation) => (
                  <div key={citation.id} className="citation">
                    <div style={{ fontWeight: '500', marginBottom: '0.25rem' }}>
                      [{citation.id}] {citation.title}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '0.25rem' }}>
                      {citation.snippet}
                    </div>
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="citation-link"
                    >
                      {citation.source}
                    </a>
                  </div>
                ))}
              </div>
            )}

            {report.sources && report.sources.length > 0 && (
              <div className="report-section">
                <h3>Sources Used</h3>
                <ul>
                  {report.sources.map((source, index) => (
                    <li key={index}>{source}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Tips for Better Results</h3>
        </div>
        <ul style={{ paddingLeft: '1.5rem' }}>
          <li>Upload relevant documents before asking questions</li>
          <li>Be specific in your questions for more targeted results</li>
          <li>Include context about what you're looking for</li>
          <li>Check the citations to verify information</li>
        </ul>
      </div>
    </div>
  );
};

export default ResearchInterface;

