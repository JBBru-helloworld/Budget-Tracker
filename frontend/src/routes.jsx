// frontend/src/routes.jsx
import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Receipts from "./pages/Receipts";
import ReceiptDetail from "./pages/ReceiptDetail";
import ScanReceipt from "./pages/ScanReceipt";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import Tips from "./pages/Tips";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";

// Routes component
function AppRoutes() {
  const { currentUser } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Close sidebar on small screens by default
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };

    handleResize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {currentUser && (
        <Navbar
          isSidebarOpen={isSidebarOpen}
          toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        />
      )}

      <div className="flex">
        {currentUser && <Sidebar isOpen={isSidebarOpen} />}

        <main
          className={`flex-1 p-4 transition-all duration-300 ${
            currentUser ? "pt-16" : ""
          }`}
        >
          <Routes>
            <Route
              path="/login"
              element={currentUser ? <Navigate to="/" /> : <Login />}
            />
            <Route
              path="/register"
              element={currentUser ? <Navigate to="/" /> : <Register />}
            />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/receipts"
              element={
                <ProtectedRoute>
                  <Receipts />
                </ProtectedRoute>
              }
            />

            <Route
              path="/receipts/:id"
              element={
                <ProtectedRoute>
                  <ReceiptDetail />
                </ProtectedRoute>
              }
            />

            <Route
              path="/scan"
              element={
                <ProtectedRoute>
                  <ScanReceipt />
                </ProtectedRoute>
              }
            />

            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />

            <Route
              path="/tips"
              element={
                <ProtectedRoute>
                  <Tips />
                </ProtectedRoute>
              }
            />

            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default AppRoutes;
