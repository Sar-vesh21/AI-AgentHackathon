// AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';

interface User {
  id: string;
  email?: string;
  name?: string;
  iat?: number;
  exp?: number;
}

interface AuthContextType {
  user: User | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  isTokenExpired: () => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const isTokenExpired = () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return true;
    
    try {
      const decoded = jwtDecode<User>(token);
      if (!decoded.exp) return true;
      
      // exp is in seconds, Date.now() is in milliseconds
      return decoded.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const verifyToken = async () => {
      if (token) {
        await verifyAndSetUser(token);
      }
      setLoading(false);
    };
    verifyToken();
  }, []);

  const verifyAndSetUser = async (token: string) => {
    try {
      // First verify the token with our backend
      const verifyResponse = await fetch('http://localhost:3001/auth/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!verifyResponse.ok) {
        throw new Error('Token verification failed');
      }

      const { user: verifiedUser } = await verifyResponse.json();
      
      // If verification successful, store the token and set the user
      localStorage.setItem('auth_token', token);
      setUser(verifiedUser);
    } catch (error) {
      console.error('Token verification error:', error);
      localStorage.removeItem('auth_token');
      setUser(null);
    }
  };

  const login = async (token: string) => {
    await verifyAndSetUser(token);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isTokenExpired }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};