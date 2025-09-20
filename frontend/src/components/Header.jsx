import React, { useState, useEffect } from 'react';
import { Search, FileText, BarChart3, User, Menu, X, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ApiService from '../services/api';

const Header = ({ currentView, setCurrentView }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [userCredits, setUserCredits] = useState(10);
  const { user, logout } = useAuth();

  useEffect(() => {
    // Fetch user credits
    const fetchCredits = async () => {
      try {
        const stats = await ApiService.getUsageStats();
        setUserCredits(stats.current_credits || user?.credits || 10);
      } catch (error) {
        console.error('Error fetching credits:', error);
        setUserCredits(user?.credits || 10); // Default fallback
      }
    };

    if (user) {
      fetchCredits();
    }
  }, [user]);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'research', label: 'Research', icon: Search },
    { id: 'usage', label: 'Usage', icon: FileText },
  ];

  const handleNavClick = (id) => {
    setCurrentView(id);
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <Search size={24} />
          <span className="logo-text">Smart Research Assistant</span>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="nav desktop-nav">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${currentView === id ? 'active' : ''}`}
              onClick={() => handleNavClick(id)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        
        <div className="header-right">
          <div className="user-info">
            <span className="username">{user?.username}</span>
            <div className="credits-badge">
              <User size={16} />
              <span>Credits: {userCredits}</span>
            </div>
          </div>
          <button
            onClick={logout}
            className="logout-btn"
            title="Logout"
          >
            <LogOut size={16} />
          </button>
          
          {/* Mobile Menu Button */}
          <button 
            className="mobile-menu-btn"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <nav className="mobile-nav">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`mobile-nav-item ${currentView === id ? 'active' : ''}`}
              onClick={() => handleNavClick(id)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      )}
    </header>
  );
};

export default Header;

