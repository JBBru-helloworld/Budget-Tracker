// frontend/src/services/apiService.js
import axios from "axios";

// Create a base axios instance with common configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token in requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API service methods
const apiService = {
  // Generic GET request
  get: async (url, params = {}) => {
    try {
      const response = await apiClient.get(url, { params });
      return response;
    } catch (error) {
      console.error(`GET error for ${url}:`, error);
      throw error;
    }
  },

  // Generic POST request
  post: async (url, data = {}) => {
    try {
      const response = await apiClient.post(url, data);
      return response;
    } catch (error) {
      console.error(`POST error for ${url}:`, error);
      throw error;
    }
  },

  // Generic PUT request
  put: async (url, data = {}) => {
    try {
      const response = await apiClient.put(url, data);
      return response;
    } catch (error) {
      console.error(`PUT error for ${url}:`, error);
      throw error;
    }
  },

  // Generic DELETE request
  delete: async (url) => {
    try {
      const response = await apiClient.delete(url);
      return response;
    } catch (error) {
      console.error(`DELETE error for ${url}:`, error);
      throw error;
    }
  },
};

export default apiService;
