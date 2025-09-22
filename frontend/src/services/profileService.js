import axios from "axios";
import { auth } from "../firebase";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Helper to get auth token
const getAuthToken = async () => {
  const user = auth.currentUser;
  if (user) {
    return user.getIdToken();
  }
  throw new Error("User not authenticated");
};

export const getUserProfile = async (userId) => {
  try {
    const token = await getAuthToken();
    const response = await axios.get(`${API_URL}/api/profile/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      // Profile doesn't exist yet, create one
      const userData = auth.currentUser;
      const newProfile = {
        user_id: userId,
        display_name: userData?.displayName || "",
        email: userData?.email || "",
        avatar_url: userData?.photoURL || null,
      };
      return createUserProfile(newProfile);
    }
    throw error;
  }
};

export const createUserProfile = async (profileData) => {
  const token = await getAuthToken();
  const response = await axios.post(`${API_URL}/api/profile/`, profileData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const updateUserProfile = async (userId, profileData) => {
  const token = await getAuthToken();
  const response = await axios.put(`${API_URL}/api/profile/`, profileData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const uploadAvatar = async (userId, file) => {
  const token = await getAuthToken();

  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(`${API_URL}/api/profile/avatar`, formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data.avatar_url;
};
