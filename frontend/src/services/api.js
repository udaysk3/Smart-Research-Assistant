// Real API service for Smart Research Assistant
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Determine if we're sending FormData
    const isFormData = options.body instanceof FormData;
    
    const config = {
      headers: {
        // Only set Content-Type for JSON, let browser handle FormData
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication API
  async login(usernameOrEmail, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username_or_email: usernameOrEmail,
        password: password
      }),
    });
  }

  async register(username, email, password) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username,
        email,
        password
      }),
    });
  }

  async getCurrentUser() {
    return this.request('/api/auth/me');
  }

  async logout() {
    return this.request('/api/auth/logout', {
      method: 'POST'
    });
  }

  // Research API
  async generateResearchReport(question, options = {}) {
    const payload = {
      question,
      include_web_search: options.includeWebSearch !== false,
      include_live_data: options.includeLiveData !== false,
    };

    return this.request('/api/research', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // File Upload API
  async uploadDocuments(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    return this.request('/api/upload', {
      method: 'POST',
      body: formData,
    });
  }

  // Usage Stats API
  async getUsageStats() {
    return this.request('/api/usage');
  }

  // Health Check API
  async healthCheck() {
    return this.request('/api/health');
  }

  // Billing API
  async purchaseCredits(userId, amount, paymentMethod) {
    return this.request('/api/billing/purchase', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        amount,
        payment_method: paymentMethod,
      }),
    });
  }

  // Pathway Live Data API
  async getLiveData(query) {
    return this.request('/api/pathway/live-data', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // Document Management API
  async getUserDocuments(userId = 'default_user') {
    return this.request(`/api/documents/${userId}`);
  }

  async deleteDocument(documentId, userId = 'default_user') {
    return this.request(`/api/documents/${documentId}`, {
      method: 'DELETE',
      body: JSON.stringify({ user_id: userId }),
    });
  }
}

export default new ApiService();
