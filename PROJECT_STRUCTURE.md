# Smart Research Assistant - Project Structure

This document provides a comprehensive overview of the project structure and organization.

## 📁 Root Directory Structure

```
smart-research-assistant/
├── README.md                    # Main project documentation
├── PROJECT_STRUCTURE.md         # This file
├── setup.py                     # Automated setup script
├── frontend/                    # React frontend application
└── backend/                     # FastAPI backend application
```

## 🎨 Frontend Structure (`frontend/`)

```
frontend/
├── README.md                    # Frontend documentation
├── package.json                 # Node.js dependencies and scripts
├── public/
│   └── index.html              # Main HTML template
└── src/
    ├── App.jsx                 # Main React application
    ├── App.css                 # Global styles
    ├── index.js                # React entry point
    ├── index.css               # Base styles
    ├── components/             # React components
    │   ├── AuthPage.jsx        # Authentication page
    │   ├── Dashboard.jsx       # Main dashboard
    │   ├── Header.jsx          # Navigation header
    │   ├── Login.jsx           # Login form
    │   ├── Register.jsx        # Registration form
    │   ├── ResearchInterface.jsx # Research query interface
    │   └── UsageStats.jsx      # Usage statistics
    ├── context/                # React context providers
    │   ├── AuthContext.jsx     # Authentication context
    │   └── UserContext.jsx     # User data context
    └── services/               # API services
        └── api.js              # Centralized API client
```

## 🔧 Backend Structure (`backend/`)

```
backend/
├── README.md                    # Backend documentation
├── requirements.txt             # Python dependencies
├── main.py                      # FastAPI application entry point
├── env.example                  # Environment variables template
├── .env                         # Environment variables (created during setup)
├── models/                      # Database models and configuration
│   ├── database.py             # SQLAlchemy models and database setup
│   └── research_assistant.db   # SQLite database file
├── services/                    # Business logic services
│   ├── auth_service.py         # Authentication logic
│   ├── document_processor.py   # Document parsing and processing
│   ├── research_agent.py       # AI research agent
│   ├── real_billing_service.py # Flexprice billing integration
│   ├── real_pathway_service.py # Live data integration
│   ├── vector_store.py         # ChromaDB vector operations
│   └── web_search.py           # Web search capabilities
├── routes/                      # API route handlers
│   ├── __init__.py             # Package initialization
│   └── auth.py                 # Authentication endpoints
├── middleware/                  # FastAPI middleware
│   ├── __init__.py             # Package initialization
│   └── auth_middleware.py      # Authentication middleware
├── templates/                   # HTML templates
│   └── admin_dashboard.html    # Admin interface template
├── uploads/                     # User uploaded files
│   └── [user_id]_[filename]    # User-specific file storage
├── chroma_db/                   # ChromaDB vector storage
│   ├── chroma.sqlite3          # ChromaDB database
│   └── [collection_id]/        # Vector collection data
├── venv/                        # Python virtual environment
│   ├── Scripts/                # Windows activation scripts
│   ├── bin/                    # Unix activation scripts
│   └── Lib/site-packages/      # Installed packages
├── pathway_live_data.py         # Live data ingestion script
├── setup_pathway.py            # Pathway setup script
├── admin.py                     # Database admin interface
├── billing.db                   # Billing database
├── research_assistant.db        # Main application database
└── live_data.json              # Cached live data
```

## 🔄 Data Flow Architecture

### 1. User Authentication Flow
```
Frontend (Login) → Backend (/api/auth/login) → AuthService → Database → JWT Token → Frontend
```

### 2. Document Upload Flow
```
Frontend (Upload) → Backend (/api/upload) → DocumentProcessor → VectorStore → Database
```

### 3. Research Query Flow
```
Frontend (Query) → Backend (/api/research) → ResearchAgent → {
    VectorStore (Document Search)
    PathwayService (Live Data)
    WebSearch (Additional Context)
    Gemini (AI Synthesis)
} → Response → Frontend
```

### 4. Billing Flow
```
Research Request → BillingService → Flexprice API → Credit Deduction → Database Log
```

## 🗄️ Database Schema

### Main Database (`research_assistant.db`)
- **users**: User accounts and authentication
- **user_sessions**: Active user sessions
- **documents**: Uploaded file metadata
- **reports**: Generated research reports

### Billing Database (`billing.db`)
- **users**: User billing information
- **billing_transactions**: Payment and usage records
- **usage_logs**: Detailed usage tracking

### Vector Database (`chroma_db/`)
- **Collections**: Document embeddings for semantic search
- **Metadata**: Document and user associations

## 🔌 API Endpoints

### Authentication (`/api/auth/`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /me` - Get current user

### Research (`/api/`)
- `POST /research` - Submit research query
- `POST /upload` - Upload documents
- `GET /usage` - Get usage statistics

### Admin (`/admin/`)
- `GET /` - Database admin interface
- `GET /users` - List all users
- `GET /documents` - List all documents

## 🔧 Configuration Files

### Environment Variables (`.env`)
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

### Package Dependencies

#### Frontend (`package.json`)
- React 18
- React Router
- Axios
- React Scripts

#### Backend (`requirements.txt`)
- FastAPI
- SQLAlchemy
- ChromaDB
- Google Generative AI
- Pathway
- Uvicorn

## 🚀 Startup Scripts

### Unix/Linux/macOS
- `start_backend.sh` - Starts backend server
- `start_frontend.sh` - Starts frontend development server

### Windows
- `start_backend.bat` - Starts backend server
- `start_frontend.bat` - Starts frontend development server

## 📊 Monitoring and Logs

### Log Files
- Backend logs: Console output with structured logging
- Database logs: SQLite query logs
- Vector store logs: ChromaDB operation logs

### Health Checks
- `GET /health` - Basic health check
- `GET /api/status` - Detailed system status

## 🔒 Security Considerations

### File Structure Security
- Uploads directory: User-specific file naming
- Database files: Restricted permissions
- Environment files: Excluded from version control
- Virtual environment: Isolated dependencies

### Authentication Security
- JWT tokens: Secure session management
- Password hashing: PBKDF2 with salt
- Input validation: Pydantic models
- CORS configuration: Frontend domain only

## 📈 Performance Considerations

### File Organization
- Separate databases for different concerns
- Vector storage optimized for search
- Async operations for I/O
- Connection pooling for database

### Caching Strategy
- Vector embeddings cached in ChromaDB
- Live data cached in JSON files
- API responses cached in memory
- Static assets cached by browser

## 🧪 Testing Structure

### Backend Tests
```
backend/tests/
├── test_auth.py
├── test_documents.py
├── test_research.py
└── test_billing.py
```

### Frontend Tests
```
frontend/src/
├── __tests__/
│   ├── components/
│   ├── services/
│   └── utils/
└── setupTests.js
```

## 🔄 Development Workflow

### Local Development
1. Start backend: `./start_backend.sh` or `start_backend.bat`
2. Start frontend: `./start_frontend.sh` or `start_frontend.bat`
3. Access: http://localhost:3000

### Production Deployment
1. Build frontend: `npm run build`
2. Configure production environment
3. Deploy with Docker or cloud services

## 📚 Documentation Structure

- **README.md**: Main project overview
- **PROJECT_STRUCTURE.md**: This file
- **frontend/README.md**: Frontend-specific documentation
- **backend/README.md**: Backend-specific documentation
- **API Documentation**: Auto-generated at `/docs` when running

## 🤝 Contributing Guidelines

### Code Organization
- Follow existing structure patterns
- Add tests for new features
- Update documentation
- Use consistent naming conventions

### File Naming
- Components: PascalCase (e.g., `ResearchInterface.jsx`)
- Services: camelCase (e.g., `authService.py`)
- Files: snake_case (e.g., `document_processor.py`)
- Directories: lowercase (e.g., `services/`)

---

This structure provides a clear separation of concerns, making the codebase maintainable and scalable for future development.

