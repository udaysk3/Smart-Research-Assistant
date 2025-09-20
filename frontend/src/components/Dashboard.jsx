import React, { useState, useEffect } from 'react';
import { Search, Upload, FileText, TrendingUp, Clock, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    reportsGenerated: 0,
    creditsUsed: 0,
    documentsUploaded: 0,
    lastActivity: 'Never'
  });

  const [recentReports, setRecentReports] = useState([]);

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch real usage stats
      const usageStats = await ApiService.getUsageStats('default_user');
      
      setStats({
        reportsGenerated: usageStats.total_reports_generated || 0,
        creditsUsed: usageStats.current_credits || 0,
        documentsUploaded: 0, // This would need to be implemented
        lastActivity: usageStats.last_activity ? new Date(usageStats.last_activity).toLocaleString() : 'Never'
      });

      // Get recent activity
      const recentActivity = usageStats.recent_activity || [];
      const reports = recentActivity
        .filter(activity => activity.action === 'research_query')
        .slice(0, 5)
        .map(activity => ({
          id: activity.timestamp,
          question: activity.details || 'Research query',
          timestamp: new Date(activity.timestamp).toLocaleString(),
          status: 'completed'
        }));

      setRecentReports(reports);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Fallback to empty state
      setStats({
        reportsGenerated: 0,
        creditsUsed: 0,
        documentsUploaded: 0,
        lastActivity: 'Never'
      });
      setRecentReports([]);
    }
  };

  const quickActions = [
    {
      title: 'Start New Research',
      description: 'Ask a question and get a comprehensive report',
      icon: Search,
      action: () => navigate('/research'),
      color: 'primary'
    },
    {
      title: 'Upload Documents',
      description: 'Add PDFs, DOCX files for research',
      icon: Upload,
      action: () => navigate('/research'),
      color: 'secondary'
    },
    {
      title: 'View Usage Stats',
      description: 'Check your usage and billing information',
      icon: FileText,
      action: () => navigate('/usage'),
      color: 'secondary'
    }
  ];

  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Welcome to Smart Research Assistant</h1>
        </div>
        <p className="mb-3">
          Get comprehensive, evidence-based research reports with citations from your uploaded documents and live web data.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.reportsGenerated}</div>
          <div className="stat-label">Reports Generated</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.creditsUsed}</div>
          <div className="stat-label">Credits Left</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.documentsUploaded}</div>
          <div className="stat-label">Documents Uploaded</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            <Clock size={20} />
          </div>
          <div className="stat-label">Last Activity: {stats.lastActivity}</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Quick Actions</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <div
                key={index}
                className={`btn btn-${action.color}`}
                onClick={action.action}
                style={{ 
                  padding: '1.5rem', 
                  flexDirection: 'column', 
                  textAlign: 'center',
                  cursor: 'pointer',
                  minHeight: '120px',
                  justifyContent: 'center'
                }}
              >
                <Icon size={32} style={{ marginBottom: '0.5rem' }} />
                <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                  {action.title}
                </div>
                <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                  {action.description}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Reports */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Reports</h2>
        </div>
        {recentReports.length > 0 ? (
          <div>
            {recentReports.map((report) => (
              <div key={report.id} style={{ 
                padding: '1rem', 
                border: '1px solid #e2e8f0', 
                borderRadius: '0.5rem', 
                marginBottom: '1rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <div style={{ fontWeight: '500', marginBottom: '0.25rem' }}>
                    {report.question}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
                    {report.timestamp}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircle size={16} color="#10b981" />
                  <span style={{ fontSize: '0.9rem', color: '#10b981' }}>
                    {report.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center" style={{ padding: '2rem', color: '#64748b' }}>
            No reports generated yet. Start your first research!
          </div>
        )}
      </div>

      {/* Features */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Features</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <TrendingUp size={32} color="#667eea" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Live Data</div>
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Get fresh information from live data sources
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <FileText size={32} color="#667eea" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Citations</div>
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Every answer includes proper citations
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <Search size={32} color="#667eea" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Smart Search</div>
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Search across documents and web sources
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

