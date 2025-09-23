import axios from "axios";

// Create a base axios instance with common configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
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
  get: async (url, config = {}) => {
    try {
      const response = await apiClient.get(url, config);
      return response;
    } catch (error) {
      console.error(`GET error for ${url}:`, error);
      throw error;
    }
  },

  // GET request with query parameters
  getWithParams: async (url, params = {}, config = {}) => {
    try {
      const response = await apiClient.get(url, { ...config, params });
      return response;
    } catch (error) {
      console.error(`GET error for ${url}:`, error);
      throw error;
    }
  },

  // Generic POST request
  post: async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.post(url, data, config);
      return response;
    } catch (error) {
      console.error(`POST error for ${url}:`, error);
      throw error;
    }
  },

  // Generic PUT request
  put: async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.put(url, data, config);
      return response;
    } catch (error) {
      console.error(`PUT error for ${url}:`, error);
      throw error;
    }
  },

  // Generic DELETE request
  delete: async (url, config = {}) => {
    try {
      const response = await apiClient.delete(url, config);
      return response;
    } catch (error) {
      console.error(`DELETE error for ${url}:`, error);
      throw error;
    }
  },
};

export default apiService;
