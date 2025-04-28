// frontend/src/pages/Dashboard.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  PlusCircleIcon,
  CurrencyDollarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
} from "@heroicons/react/outline";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [budget, setBudget] = useState(0);
  const [spent, setSpent] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!currentUser) {
        setLoading(false);
        return;
      }

      try {
        // Get the auth token
        const token = await currentUser.getIdToken();

        // Fetch dashboard data from API
        const response = await axios.get(`${API_URL}/dashboard`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        const { transactions, budget, total_spent } = response.data;
        setTransactions(transactions);
        setBudget(budget);
        setSpent(total_spent);
        setError(null);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [currentUser]);

  const handleSetBudget = async (newBudget) => {
    if (!currentUser) return;

    try {
      const token = await currentUser.getIdToken();
      await axios.post(
        `${API_URL}/budget`,
        { amount: parseFloat(newBudget) },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      setBudget(parseFloat(newBudget));
      setError(null);
    } catch (error) {
      console.error("Error setting budget:", error);
      setError("Failed to update budget");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="text-sm text-gray-600">
          Welcome, {currentUser?.displayName || currentUser?.email}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Monthly Budget</h2>
          <p className="text-3xl font-bold text-blue-600">
            ${budget.toFixed(2)}
          </p>
          <button
            onClick={() => handleSetBudget(prompt("Enter new budget amount:"))}
            className="mt-2 text-sm text-blue-600 hover:text-blue-800"
          >
            Update Budget
          </button>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Total Spent</h2>
          <p className="text-3xl font-bold text-red-600">${spent.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Remaining</h2>
          <p className="text-3xl font-bold text-green-600">
            ${(budget - spent).toFixed(2)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
          {transactions.length > 0 ? (
            <div className="space-y-4">
              {transactions
                .sort((a, b) => new Date(b.date) - new Date(a.date))
                .slice(0, 5)
                .map((transaction) => (
                  <div
                    key={transaction._id}
                    className="flex justify-between items-center"
                  >
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-gray-500">
                        {transaction.category} •{" "}
                        {new Date(transaction.date).toLocaleDateString()}
                      </p>
                    </div>
                    <p
                      className={`font-semibold ${
                        transaction.amount > 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      ${Math.abs(transaction.amount).toFixed(2)}
                    </p>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-gray-500">No recent transactions</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <span className="block text-blue-600 font-medium">
                Add Transaction
              </span>
            </button>
            <button className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
              <span className="block text-green-600 font-medium">
                Set Budget
              </span>
            </button>
            <button className="p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
              <span className="block text-purple-600 font-medium">
                View Reports
              </span>
            </button>
            <button className="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors">
              <span className="block text-orange-600 font-medium">
                Manage Categories
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
