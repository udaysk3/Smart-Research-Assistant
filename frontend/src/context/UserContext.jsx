import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({
    id: 'default_user',
    email: 'user@example.com',
    credits: 10,
    reportsGenerated: 0,
    documentsUploaded: 0
  });

  const [isLoading, setIsLoading] = useState(false);

  const updateCredits = (newCredits) => {
    setUser(prev => ({ ...prev, credits: newCredits }));
  };

  const incrementReports = () => {
    setUser(prev => ({ ...prev, reportsGenerated: prev.reportsGenerated + 1 }));
  };

  const incrementDocuments = () => {
    setUser(prev => ({ ...prev, documentsUploaded: prev.documentsUploaded + 1 }));
  };

  const value = {
    user,
    setUser,
    updateCredits,
    incrementReports,
    incrementDocuments,
    isLoading,
    setIsLoading
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

