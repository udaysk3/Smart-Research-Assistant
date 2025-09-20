# Smart Research Assistant

An AI-powered research tool that combines uploaded documents with live data to generate comprehensive, evidence-based research reports. Built for students, researchers, and professionals who need reliable, up-to-date information with proper citations.

## 🎯 Problem Statement

Current research tools are fragmented:
- Search engines return pages of links, not concise answers
- Chatbots work with single files and can't connect multiple sources
- Summarizers often skip citations, making answers hard to trust
- Information becomes outdated quickly

**Solution**: A Smart Research Assistant that:
1. Takes questions as input
2. Finds answers from uploaded files AND live data
3. Summarizes into short, reliable reports with citations
4. Keeps itself updated with fresh information

## ✨ Key Features

### 🔍 **Intelligent Research**
- **Multi-source Analysis**: Combines uploaded documents with live web data
- **AI-Powered Synthesis**: Uses Google Gemini for intelligent report generation
- **Real-time Data**: Live integration with RSS feeds and news APIs via Pathway
- **Citation Tracking**: Proper source attribution for all information

### 📄 **Document Processing**
- **Multi-format Support**: PDF, DOCX, TXT files
- **Vector Search**: Semantic search through document content
- **Chunking & Embeddings**: Efficient document processing and storage
- **Persistent Storage**: Documents saved for future research

### 🔐 **User Management**
- **Secure Authentication**: JWT-based user authentication
- **User-specific Data**: Isolated document and research history
- **Credit System**: Per-question and per-report billing
- **Usage Analytics**: Detailed usage tracking and statistics

### 💰 **Billing Integration**
- **Flexprice Integration**: Real billing API for credit management
- **Usage Tracking**: Automatic credit deduction and transaction logging
- **Transparent Pricing**: Clear cost breakdown for each operation
- **Billing History**: Complete transaction records

### 🔄 **Live Data Integration**
- **Pathway Integration**: Real-time data ingestion from multiple sources
- **RSS Feeds**: BBC, CNN, O'Reilly, TechCrunch, Wired
- **News APIs**: Latest news and articles
- **Fresh Information**: Reports include up-to-date data

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • Authentication│    │ • AI Research   │    │ • Google Gemini │
│ • Document UI   │    │ • Document Proc │    │ • Flexprice API │
│ • Research UI   │    │ • Vector Store  │    │ • News APIs     │
│ • Usage Stats   │    │ • Live Data     │    │ • RSS Feeds     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Databases     │
                       │                 │
                       │ • SQLite (Users)│
                       │ • ChromaDB (Vec)│
                       │ • Billing DB    │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- Python 3.8+
- API Keys (see setup section)

### 1. Clone Repository
```bash
git clone <repository-url>
cd smart-research-assistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
python main.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8080

## 🔧 Configuration

### Required API Keys

1. **Google Gemini API Key**
   - Get from: https://makersuite.google.com/app/apikey
   - Used for: AI research report generation

2. **Flexprice API Key**
   - Get from: https://flexprice.com
   - Used for: Billing and credit management

3. **News API Key** (Optional)
   - Get from: https://newsapi.org
   - Used for: Additional news data

### Environment Variables
```env
# AI Services
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here

# Billing
FLEXPRICE_API_KEY=your_flexprice_api_key_here

# Live Data
NEWS_API_KEY=your_news_api_key_here
PATHWAY_HOST=localhost
PATHWAY_PORT=8001

# Security
SECRET_KEY=your_secret_key_here
```

## 📱 Usage Guide

### 1. **Registration & Login**
- Create an account with username, email, and password
- Secure authentication with JWT tokens
- User-specific data isolation

### 2. **Document Upload**
- Drag and drop files (PDF, DOCX, TXT)
- Automatic text extraction and processing
- Vector storage for semantic search

### 3. **Research Queries**
- Ask questions in natural language
- System searches uploaded documents + live data
- AI generates comprehensive reports with citations

### 4. **Usage Tracking**
- View credit balance and usage statistics
- Track billing history and transactions
- Monitor research activity

## 🔄 Live Data Integration

### Pathway Setup
```bash
# Install Pathway
pip install pathway

# Run live data ingestion
python pathway_live_data.py
```

### Data Sources
- **RSS Feeds**: Technology news from major sources
- **News APIs**: Latest articles and updates
- **Real-time Processing**: Continuous data updates

## 💰 Billing System

### Credit System
- **Per Question**: Credits deducted for each research query
- **Per Report**: Additional credits for report generation
- **Transparent Pricing**: Clear cost breakdown

### Flexprice Integration
- Real API calls for billing
- Transaction logging and history
- Usage analytics and reporting

## 🗄️ Database Schema

### Core Tables
- **users**: User accounts and authentication
- **user_sessions**: Active user sessions
- **documents**: Uploaded file metadata
- **reports**: Generated research reports
- **billing_transactions**: Payment and usage records

### Vector Storage
- **ChromaDB**: Document embeddings for semantic search
- **Persistent Storage**: Documents available across sessions

## 🔒 Security Features

- **Password Hashing**: PBKDF2 with salt
- **JWT Authentication**: Secure session management
- **Input Validation**: Comprehensive data validation
- **File Security**: MIME type and size validation
- **CORS Protection**: Configured for frontend domain

## 📊 Performance

- **Async Operations**: Non-blocking I/O
- **Vector Caching**: Efficient embedding storage
- **Database Indexing**: Optimized queries
- **Connection Pooling**: Efficient database connections

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Setup
1. Set production environment variables
2. Use production database (PostgreSQL recommended)
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Deploy with Docker or cloud services

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📈 Monitoring

### Health Checks
- API health endpoints
- Database connectivity
- External service status

### Logging
- Structured logging with timestamps
- Error tracking and debugging
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini**: AI language model for research generation
- **Pathway**: Real-time data processing framework
- **Flexprice**: Billing and payment processing
- **FastAPI**: Modern web framework for APIs
- **React**: Frontend framework
- **ChromaDB**: Vector database for embeddings

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/frontend/README.md` and `/backend/README.md`
- Review the API documentation at `http://localhost:8000/docs`

## 🔮 Future Enhancements

- **Multi-language Support**: Support for multiple languages
- **Advanced Analytics**: Enhanced usage analytics and insights
- **Collaboration Features**: Team workspaces and sharing
- **Mobile App**: Native mobile application
- **API Rate Limiting**: Advanced rate limiting and quotas
- **Custom Models**: Fine-tuned models for specific domains

---

**Built with ❤️ for researchers, students, and professionals who need reliable, up-to-date information.**