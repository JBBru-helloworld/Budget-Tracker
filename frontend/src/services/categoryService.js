import axios from "axios";
import { auth } from "../utils/firebase";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// Helper to get auth token
const getAuthToken = async () => {
  const user = auth.currentUser;
  if (user) {
    return user.getIdToken();
  }
  throw new Error("User not authenticated");
};

export const getCategories = async () => {
  const token = await getAuthToken();
  const response = await axios.get(`${API_URL}/categories/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const getCategoryById = async (categoryId) => {
  const token = await getAuthToken();
  const response = await axios.get(`${API_URL}/categories/${categoryId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const createCategory = async (categoryData) => {
  const token = await getAuthToken();
  const response = await axios.post(`${API_URL}/categories/`, categoryData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const updateCategory = async (categoryId, categoryData) => {
  const token = await getAuthToken();
  const response = await axios.put(
    `${API_URL}/categories/${categoryId}`,
    categoryData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );
  return response.data;
};

export const deleteCategory = async (categoryId) => {
  const token = await getAuthToken();
  const response = await axios.delete(`${API_URL}/categories/${categoryId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};
