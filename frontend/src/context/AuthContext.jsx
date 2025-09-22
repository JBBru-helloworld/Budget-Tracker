import React, { createContext, useContext, useState, useEffect } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
} from "firebase/auth";
import { auth } from "../firebase";
import apiService from "../services/apiService";

// Create context
const AuthContext = createContext();

// Auth provider component
export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Update token in localStorage and API headers
  const updateToken = async (user) => {
    if (user) {
      const token = await user.getIdToken();
      localStorage.setItem("authToken", token);
    } else {
      localStorage.removeItem("authToken");
    }
  };

  // Register function
  const register = async (email, password, displayName) => {
    try {
      setError(null);
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

      // Update token
      await updateToken(userCredential.user);

      // Create user profile in the backend
      await apiService.post("/api/auth/register", {
        user_id: userCredential.user.uid,
        email,
        display_name: displayName,
      });

      return userCredential.user;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Login function
  const login = async (email, password) => {
    try {
      setError(null);
      const userCredential = await signInWithEmailAndPassword(
        auth,
        email,
        password
      );

      // Update token
      await updateToken(userCredential.user);

      return userCredential.user;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setError(null);
      await signOut(auth);
      localStorage.removeItem("authToken");
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Get current user data from backend
  const fetchUserData = async (userId) => {
    try {
      const response = await apiService.get(`/api/profile/`);
      return response.data;
    } catch (error) {
      console.error("Error fetching user data:", error);
      return null;
    }
  };

  // Update user profile
  const updateProfile = async (userId, userData) => {
    try {
      const response = await apiService.put(`/api/profile/`, userData);
      return response.data;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Reset password
  const resetPassword = async (email) => {
    try {
      setError(null);
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Set up auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        await updateToken(user);
        setCurrentUser(user);
      } else {
        setCurrentUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const value = {
    currentUser,
    loading,
    error,
    register,
    login,
    logout,
    fetchUserData,
    updateProfile,
    resetPassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

// Custom hook for using auth context
export function useAuth() {
  return useContext(AuthContext);
}

// Default export
export default AuthContext;
