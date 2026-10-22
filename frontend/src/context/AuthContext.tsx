import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User, LoginCredentials } from '../types/auth';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('bookleaf_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('bookleaf_token');
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Validate session on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('bookleaf_token');
      if (storedToken) {
        try {
          const profile = await api.auth.getMe();
          setUser(profile);
          localStorage.setItem('bookleaf_user', JSON.stringify(profile));
        } catch {
          // Token expired or invalid
          localStorage.removeItem('bookleaf_token');
          localStorage.removeItem('bookleaf_user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();

    // Listen for auth expiration events triggered by API interceptor
    const handleExpired = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener('bookleaf_auth_expired', handleExpired);
    return () => window.removeEventListener('bookleaf_auth_expired', handleExpired);
  }, []);

  const login = async (credentials: LoginCredentials): Promise<User> => {
    setIsLoading(true);
    try {
      const tokenResponse = await api.auth.login(credentials);
      
      const authenticatedUser: User = {
        id: tokenResponse.user_id,
        email: tokenResponse.email,
        full_name: tokenResponse.name,
        role: tokenResponse.role,
        author_id: tokenResponse.author_id,
      };

      localStorage.setItem('bookleaf_token', tokenResponse.access_token);
      localStorage.setItem('bookleaf_user', JSON.stringify(authenticatedUser));
      
      setToken(tokenResponse.access_token);
      setUser(authenticatedUser);
      return authenticatedUser;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('bookleaf_token');
    localStorage.removeItem('bookleaf_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
