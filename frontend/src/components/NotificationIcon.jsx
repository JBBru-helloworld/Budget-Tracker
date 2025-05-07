import React from "react";
import { Bell } from "lucide-react";
import { useNotifications } from "../../context/NotificationContext";
import { Link } from "react-router-dom";

const NotificationIcon = () => {
  const { unreadCount } = useNotifications();

  return (
    <Link to="/notifications" className="relative">
      <Bell className="h-6 w-6 text-neutral-600 hover:text-primary transition-colors" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-accent text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {unreadCount > 9 ? "9+" : unreadCount}
        </span>
      )}
    </Link>
  );
};

export default NotificationIcon;
