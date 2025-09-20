# Smart Research Assistant - Frontend

A modern React-based frontend for the Smart Research Assistant, an AI-powered research tool that combines uploaded documents with live data to generate comprehensive research reports.

## 🚀 Features

- **User Authentication**: Secure login/registration system
- **Document Upload**: Drag-and-drop file upload with progress tracking
- **Research Interface**: AI-powered question answering with live data integration
- **Usage Dashboard**: Real-time usage statistics and credit tracking
- **Responsive Design**: Modern, mobile-friendly UI
- **Real-time Updates**: Live data integration with Pathway

## 🛠️ Tech Stack

- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **CSS3**: Custom styling with responsive design
- **Context API**: Global state management for authentication

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── components/         # React components
│   │   ├── AuthPage.jsx    # Authentication page
│   │   ├── Dashboard.jsx   # Main dashboard
│   │   ├── Header.jsx      # Navigation header
│   │   ├── Login.jsx       # Login form
│   │   ├── Register.jsx    # Registration form
│   │   ├── ResearchInterface.jsx  # Research query interface
│   │   └── UsageStats.jsx  # Usage statistics
│   ├── context/            # React context providers
│   │   ├── AuthContext.jsx # Authentication context
│   │   └── UserContext.jsx # User data context
│   ├── services/           # API services
│   │   └── api.js          # Centralized API client
│   ├── App.jsx             # Main App component
│   ├── App.css             # Global styles
│   ├── index.js            # React entry point
│   └── index.css           # Base styles
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

4. **Open your browser**:
   Navigate to `http://localhost:3000`

## 🔧 Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

## 🔐 Authentication Flow

1. **Registration**: Users create accounts with username, email, and password
2. **Login**: Secure authentication with JWT tokens
3. **Session Management**: Automatic token refresh and logout
4. **Protected Routes**: All main features require authentication

## 📱 Key Components

### AuthPage
- Handles user registration and login
- Form validation and error handling
- Responsive design for mobile and desktop

### Dashboard
- Overview of user's research activity
- Quick access to recent reports
- Credit balance display

### ResearchInterface
- Document upload with drag-and-drop
- Question input with AI-powered responses
- Real-time progress indicators
- Citation display and source links

### UsageStats
- Detailed usage analytics
- Credit consumption tracking
- Billing history
- Export capabilities

## 🔌 API Integration

The frontend communicates with the backend through a centralized API service (`src/services/api.js`):

- **Authentication**: Login, register, logout, token validation
- **Documents**: Upload, list, delete documents
- **Research**: Submit queries, get AI responses
- **Usage**: Fetch usage statistics and billing data

### API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/upload` - Upload documents
- `POST /api/research` - Submit research query
- `GET /api/usage` - Get usage statistics

## 🎨 Styling

- **Custom CSS**: Modern, clean design
- **Responsive**: Mobile-first approach
- **Loading States**: Smooth user experience
- **Error Handling**: User-friendly error messages

## 🔒 Security Features

- **Token-based Authentication**: Secure JWT tokens
- **Protected Routes**: Authentication required for all features
- **Input Validation**: Client-side form validation
- **XSS Protection**: Sanitized user inputs

## 📊 State Management

- **AuthContext**: Global authentication state
- **UserContext**: User profile and preferences
- **Local State**: Component-level state management
- **Persistent Storage**: Token storage in localStorage

## 🚀 Deployment

### Production Build

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Deploy the `build` folder** to your hosting service

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for `http://localhost:3000`
2. **API Connection**: Verify backend is running on `http://localhost:8000`
3. **Authentication**: Check token storage and API endpoints
4. **File Upload**: Ensure backend upload directory exists

### Debug Mode

Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## 📈 Performance

- **Code Splitting**: Automatic code splitting with React Router
- **Lazy Loading**: Components loaded on demand
- **Optimized Builds**: Production builds are optimized and minified
- **Caching**: API responses cached for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Smart Research Assistant system. See the main project README for license information.

## 🔗 Related

- [Backend Documentation](../backend/README.md)
- [Main Project README](../README.md)
- [API Documentation](../backend/README.md#api-documentation)

