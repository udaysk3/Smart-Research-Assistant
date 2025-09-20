# Smart Research Assistant - Backend

A powerful FastAPI-based backend for the Smart Research Assistant, featuring AI-powered research capabilities, document processing, live data integration, and comprehensive billing system.

## 🚀 Features

- **AI Research Agent**: Gemini-powered question answering with document and live data integration
- **Document Processing**: PDF, DOCX, and text file processing with vector storage
- **Live Data Integration**: Real-time data from RSS feeds and news APIs via Pathway
- **Authentication System**: Secure user management with JWT tokens
- **Billing Integration**: Flexprice API integration for credit-based billing
- **Vector Search**: ChromaDB for semantic document search
- **Database Management**: SQLite with web-based admin interface

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **ChromaDB**: Vector database for embeddings
- **Google Gemini**: AI language model for research generation
- **Pathway**: Real-time data processing
- **Flexprice**: Billing and payment processing
- **SQLite**: Lightweight database
- **Uvicorn**: ASGI server

## 📁 Project Structure

```
backend/
├── models/
│   ├── database.py         # Database models and configuration
│   └── research_assistant.db  # SQLite database
├── services/
│   ├── auth_service.py     # Authentication logic
│   ├── document_processor.py  # Document parsing and processing
│   ├── research_agent.py   # AI research agent
│   ├── real_billing_service.py  # Flexprice billing integration
│   ├── real_pathway_service.py  # Live data integration
│   ├── vector_store.py     # ChromaDB vector operations
│   └── web_search.py       # Web search capabilities
├── routes/
│   └── auth.py            # Authentication endpoints
├── middleware/
│   └── auth_middleware.py # Authentication middleware
├── templates/
│   └── admin_dashboard.html  # Admin interface template
├── uploads/               # User uploaded files
├── chroma_db/            # ChromaDB vector storage
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
├── pathway_live_data.py # Live data ingestion script
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

6. **Initialize database**:
   ```bash
   python -c "from models.database import init_database; init_database()"
   ```

7. **Start the server**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 🔧 Environment Variables

Create a `.env` file with the following variables:

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

# Database
DATABASE_URL=sqlite:///./models/research_assistant.db
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Research Endpoints

- `POST /api/research` - Submit research query
- `POST /api/upload` - Upload documents
- `GET /api/usage` - Get usage statistics

### Admin Endpoints

- `GET /admin` - Database admin interface
- `GET /api/admin/users` - List all users
- `GET /api/admin/documents` - List all documents

## 🔐 Authentication System

### User Registration
```json
POST /api/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```

### User Login
```json
POST /api/auth/login
{
  "username_or_email": "john_doe",
  "password": "secure_password"
}
```

### Protected Endpoints
All research and upload endpoints require authentication:
```bash
Authorization: Bearer <jwt_token>
```

## 📄 Document Processing

### Supported Formats
- **PDF**: Text extraction with page information
- **DOCX**: Word document processing
- **TXT**: Plain text files

### Processing Pipeline
1. File upload and validation
2. Text extraction and cleaning
3. Chunking for vector storage
4. Embedding generation
5. ChromaDB storage
6. Database metadata storage

## 🤖 AI Research Agent

### Capabilities
- **Document Search**: Semantic search through uploaded documents
- **Live Data Integration**: Real-time data from RSS feeds and news APIs
- **Web Search**: Additional context from web search
- **Report Generation**: Structured research reports with citations

### Research Flow
1. Query analysis and intent detection
2. Document retrieval from vector store
3. Live data fetching from Pathway
4. Web search for additional context
5. AI synthesis with Gemini
6. Citation generation and formatting

## 🔄 Live Data Integration

### Pathway Setup
```bash
# Install Pathway
pip install pathway

# Run live data ingestion
python pathway_live_data.py
```

### Data Sources
- **RSS Feeds**: BBC, CNN, O'Reilly, TechCrunch, Wired
- **News APIs**: NewsAPI integration
- **Real-time Processing**: Incremental data updates

## 💰 Billing System

### Flexprice Integration
- **Credit Management**: Per-question and per-report billing
- **Transaction Tracking**: Complete billing history
- **API Integration**: Real Flexprice API calls
- **Usage Analytics**: Detailed usage statistics

### Billing Flow
1. Credit check before processing
2. Credit deduction after completion
3. Transaction logging
4. Usage statistics update

## 🗄️ Database Schema

### Users Table
- `user_id`: Primary key
- `username`: Unique username
- `email`: User email
- `password_hash`: Hashed password
- `credits`: Available credits
- `created_at`: Registration timestamp
- `last_login`: Last login timestamp

### Documents Table
- `document_id`: Primary key
- `user_id`: Foreign key to users
- `filename`: Original filename
- `file_path`: Storage path
- `file_type`: MIME type
- `file_size`: File size in bytes
- `pages`: Number of pages
- `status`: Processing status

### Reports Table
- `report_id`: Primary key
- `user_id`: Foreign key to users
- `query`: Research query
- `response`: AI-generated response
- `sources`: Source citations
- `created_at`: Generation timestamp

## 🔧 Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_auth.py
```

### Database Management
```bash
# Access SQLite admin
sqlite-web models/research_assistant.db

# Or use the built-in admin
python -c "from admin import app; app.run()"
```

### Live Data Updates
```bash
# Fetch latest live data
python pathway_live_data.py

# Or run continuously
python -c "from services.real_pathway_service import RealPathwayService; import asyncio; asyncio.run(RealPathwayService().start_continuous_ingestion())"
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
   ```bash
   export ENVIRONMENT=production
   export DATABASE_URL=postgresql://user:pass@host:port/db
   ```

2. **Install Production Dependencies**:
   ```bash
   pip install gunicorn
   ```

3. **Run with Gunicorn**:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Monitoring

### Health Checks
- `GET /health` - Basic health check
- `GET /api/status` - Detailed system status

### Logging
- Structured logging with timestamps
- Error tracking and debugging
- Performance metrics

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection**: Ensure SQLite file permissions
2. **API Keys**: Verify all required API keys are set
3. **File Uploads**: Check upload directory permissions
4. **Vector Store**: Ensure ChromaDB directory exists

### Debug Mode
```bash
export DEBUG=true
python main.py
```

## 🔒 Security

- **Password Hashing**: PBKDF2 with salt
- **JWT Tokens**: Secure session management
- **Input Validation**: Pydantic models for data validation
- **CORS**: Configured for frontend domain
- **File Validation**: MIME type and size checks

## 📈 Performance

- **Async Operations**: Non-blocking I/O operations
- **Vector Caching**: Efficient embedding storage
- **Database Indexing**: Optimized queries
- **Connection Pooling**: Efficient database connections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is part of the Smart Research Assistant system. See the main project README for license information.

## 🔗 Related

- [Frontend Documentation](../frontend/README.md)
- [Main Project README](../README.md)
- [API Documentation](http://localhost:8000/docs) (when running)

