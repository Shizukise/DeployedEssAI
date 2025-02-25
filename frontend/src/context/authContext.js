import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PageSpinner from '../components/PageSpinner/PageSpinner';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [jwtoken, setJWToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const nav = useNavigate();

  const [loading, setLoading] = useState(true);

  // Load user state from localStorage on app load
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const storedToken = localStorage.getItem("jwtoken");
    const storedRefreshToken = localStorage.getItem("refreshToken");

    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setJWToken(storedToken);
      setRefreshToken(storedRefreshToken);
    }

    // After attempting to load from localStorage, set loading to false
    setLoading(false);
  }, []);

  const login = (username, token, refreshJWToken) => {
    setUser(username);
    setJWToken(token);
    setRefreshToken(refreshJWToken);

    // Persist to localStorage
    localStorage.setItem("user", JSON.stringify(username));
    localStorage.setItem("jwtoken", token);
    localStorage.setItem("refreshToken", refreshJWToken);
  };

  const logout = () => {
    setUser(null);
    setJWToken(null);
    setRefreshToken(null);

    // Clear localStorage
    localStorage.removeItem("user");
    localStorage.removeItem("jwtoken");
    localStorage.removeItem("refreshToken");
    nav("/");
  };

  const refreshJWToken = (token) => {
    localStorage.setItem("jwtoken", token);
    setJWToken(token);
  };

  return !loading ? (
    <AuthContext.Provider value={{ user, jwtoken, refreshToken, login, logout, refreshJWToken }}>
      {children}
    </AuthContext.Provider>
  ) : (
    <PageSpinner />
  );
};

export const useAuth = () => useContext(AuthContext);
