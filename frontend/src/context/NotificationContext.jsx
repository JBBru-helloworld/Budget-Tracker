import React, { createContext, useState, useEffect, useContext } from "react";
import { useAuth } from "./AuthContext";
import apiService from "../services/apiService";

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const { currentUser } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // Fetch notifications
  const fetchNotifications = async (includeRead = false) => {
    if (!currentUser) return;

    setLoading(true);
    try {
      const token = await currentUser.getIdToken();
      const response = await apiService.getWithParams(
        "/notifications",
        { include_read: includeRead },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setNotifications(response.data);
    } catch (error) {
      console.error("Error fetching notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  // Get unread notification count
  const fetchUnreadCount = async () => {
    if (!currentUser) return;

    try {
      const token = await currentUser.getIdToken();
      const response = await apiService.get("/notifications/count", {
        headers: { Authorization: `Bearer ${token}` },
      });

      setUnreadCount(response.data);
    } catch (error) {
      console.error("Error fetching notification count:", error);
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    if (!currentUser) return;

    try {
      const token = await currentUser.getIdToken();
      await apiService.put(
        `/notifications/${notificationId}/read`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Update local state
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n))
      );

      // Update count
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    if (!currentUser) return;

    try {
      const token = await currentUser.getIdToken();
      await apiService.put(
        "/notifications/read-all",
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Update local state
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
    }
  };

  // Refresh notifications on user change
  useEffect(() => {
    if (currentUser) {
      fetchNotifications();
      fetchUnreadCount();

      // Set up polling for new notifications
      const interval = setInterval(() => {
        fetchUnreadCount();
      }, 30000); // Check every 30 seconds

      return () => clearInterval(interval);
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [currentUser]);

  const value = {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export const useNotifications = () => useContext(NotificationContext);
