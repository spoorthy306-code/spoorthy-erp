import React, { createContext, useState } from 'react';
import axios from 'axios';

export const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = async (credentials) => {
    const res = await axios.post('/api/auth/login', credentials);
    setUser(res.data.user);
    return res.data;
  };

  const verifyMfa = async (code) => {
    const res = await axios.post('/api/auth/mfa/verify', { code });
    return res.data;
  };

  return <AuthContext.Provider value={{ user, login, verifyMfa }}>{children}</AuthContext.Provider>;
}
