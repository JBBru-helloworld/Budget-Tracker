import React, { useEffect, useState } from "react";
import { useNotifications } from "../context/NotificationContext";
import { format } from "date-fns";
import {
  CheckCircle,
  AlertTriangle,
  Receipt,
  Lightbulb,
  Bell,
  CheckCheck,
} from "lucide-react";
import { Link } from "react-router-dom";

const Notifications = () => {
  const {
    notifications,
    loading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
  } = useNotifications();

  const [includeRead, setIncludeRead] = useState(false);

  useEffect(() => {
    fetchNotifications(includeRead);
  }, [includeRead]);

  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case "receipt":
        return <Receipt className="h-6 w-6 text-primary" />;
      case "budget":
        return <AlertTriangle className="h-6 w-6 text-amber-500" />;
      case "tip":
        return <Lightbulb className="h-6 w-6 text-accent" />;
      case "alert":
        return <AlertTriangle className="h-6 w-6 text-red-500" />;
      default:
        return <Bell className="h-6 w-6 text-neutral-600" />;
    }
  };

  const handleMarkAsRead = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    await markAsRead(id);
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-neutral-800">Notifications</h1>

        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={includeRead}
              onChange={(e) => setIncludeRead(e.target.checked)}
              className="form-checkbox h-5 w-5 text-primary rounded"
            />
            <span className="ml-2 text-sm text-neutral-600">
              Show read notifications
            </span>
          </label>

          <button
            className="btn-outline py-1 px-3"
            onClick={markAllAsRead}
            disabled={loading}
          >
            <CheckCheck className="h-4 w-4 mr-1" />
            Mark all read
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="spinner" />
        </div>
      ) : notifications.length === 0 ? (
        <div className="card p-8 text-center">
          <Bell className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-neutral-600">
            No notifications
          </h3>
          <p className="text-neutral-500 mt-2">You're all caught up!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map((notification) => (
            <Link
              key={notification.id}
              to={notification.link || "#"}
              className={`card p-4 border-l-4 flex items-center hover:shadow-md transition-all ${
                notification.is_read
                  ? "border-l-neutral-300 bg-white"
                  : "border-l-primary bg-blue-50"
              }`}
              onClick={() =>
                !notification.is_read && markAsRead(notification.id)
              }
            >
              <div className="mr-4">
                {getNotificationIcon(notification.type)}
              </div>

              <div className="flex-1">
                <h3 className="font-medium text-neutral-800">
                  {notification.title}
                </h3>
                <p className="text-neutral-600">{notification.message}</p>
                <p className="text-xs text-neutral-500 mt-1">
                  {format(
                    new Date(notification.created_at),
                    "MMM d, yyyy • h:mm a"
                  )}
                </p>
              </div>

              {!notification.is_read && (
                <button
                  className="text-primary hover:text-primary-dark ml-2"
                  onClick={(e) => handleMarkAsRead(notification.id, e)}
                >
                  <CheckCircle className="h-5 w-5" />
                </button>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notifications;
