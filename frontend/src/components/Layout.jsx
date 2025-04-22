import React, { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  HomeIcon,
  ReceiptRefundIcon,
  UserCircleIcon,
  TagIcon,
  MenuIcon,
  XIcon,
  LogoutIcon,
} from "@heroicons/react/outline";

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const navigation = [
    { name: "Dashboard", href: "/", icon: HomeIcon },
    { name: "Receipts", href: "/receipts", icon: ReceiptRefundIcon },
    { name: "Categories", href: "/categories", icon: TagIcon },
    { name: "Profile", href: "/profile", icon: UserCircleIcon },
  ];

  const NavItem = ({ item }) => (
    <NavLink
      to={item.href}
      className={({ isActive }) =>
        `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
          isActive
            ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
            : "text-gray-700 hover:bg-purple-50"
        }`
      }
      onClick={() => setSidebarOpen(false)}
    >
      <item.icon className="h-5 w-5 mr-3" />
      {item.name}
    </NavLink>
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg transform transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 text-transparent bg-clip-text">
            Budget Tracker
          </h1>
          <button
            className="p-1 rounded-md lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <XIcon className="h-6 w-6 text-gray-500" />
          </button>
        </div>

        <div className="px-3 py-4 space-y-1">
          {navigation.map((item) => (
            <NavItem key={item.name} item={item} />
          ))}

          <button
            onClick={handleLogout}
            className="flex items-center w-full px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-red-50 transition-colors"
          >
            <LogoutIcon className="h-5 w-5 mr-3" />
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm z-10">
          <div className="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <button
              className="p-1 rounded-md lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <MenuIcon className="h-6 w-6 text-gray-500" />
            </button>

            <div className="flex items-center">
              {user?.photoURL ? (
                <img
                  src={user.photoURL}
                  alt="Profile"
                  className="h-8 w-8 rounded-full"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
                  {user?.displayName?.[0] || user?.email?.[0] || "?"}
                </div>
              )}
              <span className="ml-2 text-sm font-medium text-gray-700">
                {user?.displayName || user?.email}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-100">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
