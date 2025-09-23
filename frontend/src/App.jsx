import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Categories from "./pages/Categories";
import Receipts from "./pages/Receipts";
import ScanReceipt from "./pages/ScanReceipt";
import ReceiptDetail from "./pages/ReceiptDetail";
import Notifications from "./pages/Notifications";
import Analytics from "./pages/Analytics";
import { NotificationProvider } from "./context/NotificationContext";
import "./index.css";

// Main App component
function App() {
  return (
    <Router>
      <AuthProvider>
        <NotificationProvider>
          <Routes>
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="profile" element={<Profile />} />
              <Route path="categories" element={<Categories />} />
              <Route path="receipts" element={<Receipts />} />
              <Route path="receipts/scan" element={<ScanReceipt />} />
              <Route path="receipts/:id" element={<ReceiptDetail />} />
              <Route path="notifications" element={<Notifications />} />
              <Route path="analytics" element={<Analytics />} />
            </Route>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </NotificationProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
