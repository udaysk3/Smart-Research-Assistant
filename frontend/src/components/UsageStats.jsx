import React, { useState, useEffect } from 'react';
import { BarChart3, FileText, CreditCard, TrendingUp, Clock, CheckCircle } from 'lucide-react';
import ApiService from '../services/api';

const UsageStats = () => {
  const [stats, setStats] = useState({
    currentCredits: 10,
    reportsGenerated: 3,
    creditsUsedToday: 2,
    creditsUsedThisMonth: 7,
    estimatedRemainingQueries: 10
  });

  const [usageBreakdown, setUsageBreakdown] = useState([
    { action: 'research_query', count: 3, total_credits: 3 },
    { action: 'document_upload', count: 5, total_credits: 0 }
  ]);

  const [recentActivity, setRecentActivity] = useState([
    {
      action: 'research_query',
      credits_used: 1,
      timestamp: '2024-01-15T10:30:00Z',
      details: 'Generated report: "Latest AI trends"'
    },
    {
      action: 'research_query',
      credits_used: 1,
      timestamp: '2024-01-15T09:15:00Z',
      details: 'Generated report: "Market analysis"'
    },
    {
      action: 'document_upload',
      credits_used: 0,
      timestamp: '2024-01-15T08:45:00Z',
      details: 'Uploaded 3 documents'
    }
  ]);

  useEffect(() => {
    fetchUsageStats();
  }, []);

  const fetchUsageStats = async () => {
    try {
      // Fetch real usage stats from API
      const usageData = await ApiService.getUsageStats('default_user');
      
      setStats({
        currentCredits: usageData.current_credits || 0,
        reportsGenerated: usageData.total_reports_generated || 0,
        creditsUsedToday: 0, // This would need to be calculated
        creditsUsedThisMonth: 0, // This would need to be calculated
        estimatedRemainingQueries: usageData.current_credits || 0
      });

      setUsageBreakdown(usageData.usage_breakdown || []);
      setRecentActivity(usageData.recent_activity || []);
    } catch (error) {
      console.error('Error fetching usage stats:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours} hours ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} days ago`;
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'research_query':
        return <FileText size={16} color="#667eea" />;
      case 'document_upload':
        return <CheckCircle size={16} color="#10b981" />;
      default:
        return <Clock size={16} color="#64748b" />;
    }
  };

  const getActionLabel = (action) => {
    switch (action) {
      case 'research_query':
        return 'Research Query';
      case 'document_upload':
        return 'Document Upload';
      case 'credit_purchase':
        return 'Credit Purchase';
      default:
        return action;
    }
  };

  return (
    <div className="usage-stats">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Usage Statistics</h1>
        </div>
        <p className="mb-3">
          Track your usage, credits, and billing information for the Smart Research Assistant.
        </p>
      </div>

      {/* Current Status */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#10b981' }}>
            {stats.currentCredits}
          </div>
          <div className="stat-label">Current Credits</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#667eea' }}>
            {stats.reportsGenerated}
          </div>
          <div className="stat-label">Reports Generated</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#f59e0b' }}>
            {stats.creditsUsedToday}
          </div>
          <div className="stat-label">Credits Used Today</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#ef4444' }}>
            {stats.creditsUsedThisMonth}
          </div>
          <div className="stat-label">Credits Used This Month</div>
        </div>
      </div>

      {/* Usage Breakdown */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Usage Breakdown</h2>
        </div>
        <div>
          {usageBreakdown.map((item, index) => (
            <div key={index} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '1rem',
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              marginBottom: '0.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {getActionIcon(item.action)}
                <div>
                  <div style={{ fontWeight: '500' }}>
                    {getActionLabel(item.action)}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
                    {item.count} {item.count === 1 ? 'time' : 'times'}
                  </div>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '500', color: '#667eea' }}>
                  {item.total_credits} credits
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Activity</h2>
        </div>
        <div>
          {recentActivity.map((activity, index) => (
            <div key={index} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '1rem',
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              marginBottom: '0.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {getActionIcon(activity.action)}
                <div>
                  <div style={{ fontWeight: '500' }}>
                    {getActionLabel(activity.action)}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
                    {activity.details}
                  </div>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
                  {formatTimestamp(activity.timestamp)}
                </div>
                {activity.credits_used > 0 && (
                  <div style={{ fontSize: '0.8rem', color: '#ef4444' }}>
                    -{activity.credits_used} credit{activity.credits_used !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Billing Information */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Billing Information</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <CreditCard size={32} color="#667eea" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Per Report</div>
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              1 credit per research report
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <TrendingUp size={32} color="#667eea" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Usage Tracking</div>
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Real-time usage monitoring
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <BarChart3 size={32} color="#667eea" style={{ marginBottom: '0.5rem' }} />
            <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Analytics</div>
            <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Detailed usage analytics
            </div>
          </div>
        </div>
      </div>

      {/* Credit Purchase */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Need More Credits?</h2>
        </div>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '0.5rem' }}>
              {stats.estimatedRemainingQueries} reports remaining
            </div>
            <div style={{ color: '#64748b' }}>
              Based on your current credit balance
            </div>
          </div>
          <button className="btn btn-primary">
            Purchase Credits
          </button>
        </div>
      </div>
    </div>
  );
};

export default UsageStats;

