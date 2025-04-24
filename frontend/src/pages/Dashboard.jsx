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

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    totalSpent: 0,
    totalReceipts: 0,
    recentTransactions: [],
    spendingByCategory: [],
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Get the auth token
        const token = await currentUser.getIdToken();

        // Fetch dashboard data from API
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/api/dashboard`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const data = await response.json();
        setDashboardData(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        // Load some fallback data in case of error
        setDashboardData({
          totalSpent: 0,
          totalReceipts: 0,
          recentTransactions: [],
          spendingByCategory: [],
        });
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchDashboardData();
    }
  }, [currentUser]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-semibold mb-6">
        Welcome back, {currentUser.displayName || "User"}!
      </h1>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 text-blue-500 mr-4">
              <CurrencyDollarIcon className="h-8 w-8" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Spent (This Month)</p>
              <p className="text-2xl font-semibold">
                ${dashboardData.totalSpent.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 text-purple-500 mr-4">
              <TrendingUpIcon className="h-8 w-8" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Highest Spending Category</p>
              <p className="text-2xl font-semibold">
                {dashboardData.spendingByCategory[0]?.name || "N/A"}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-500 mr-4">
              <TrendingDownIcon className="h-8 w-8" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Receipts Processed</p>
              <p className="text-2xl font-semibold">
                {dashboardData.totalReceipts}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <h2 className="text-lg font-semibold">Recent Transactions</h2>
            <Link
              to="/receipts"
              className="text-blue-500 hover:text-blue-700 text-sm"
            >
              View All
            </Link>
          </div>
          <div className="p-4">
            {dashboardData.recentTransactions.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {dashboardData.recentTransactions.map((transaction) => (
                  <li key={transaction.id} className="py-3">
                    <div className="flex justify-between">
                      <div>
                        <p className="font-medium">{transaction.store}</p>
                        <p className="text-sm text-gray-500">
                          {transaction.date}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">
                          ${transaction.amount.toFixed(2)}
                        </p>
                        <p className="text-sm text-gray-500">
                          {transaction.category}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No recent transactions
              </p>
            )}
          </div>
          <div className="p-4 bg-gray-50">
            <Link
              to="/scan"
              className="flex items-center justify-center w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              <PlusCircleIcon className="h-5 w-5 mr-2" />
              Add New Receipt
            </Link>
          </div>
        </div>

        {/* Spending by Category */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Spending by Category</h2>
          </div>
          <div className="p-4">
            {dashboardData.spendingByCategory.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.spendingByCategory.map((category) => (
                  <div key={category.name} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">
                        {category.name}
                      </span>
                      <span className="text-sm text-gray-500">
                        ${category.amount.toFixed(2)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className={`${category.color} h-2.5 rounded-full`}
                        style={{
                          width: `${
                            (category.amount / dashboardData.totalSpent) * 100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No spending data available
              </p>
            )}
          </div>
          <div className="p-4 bg-gray-50">
            <Link
              to="/analytics"
              className="flex items-center justify-center w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              View Detailed Analytics
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
