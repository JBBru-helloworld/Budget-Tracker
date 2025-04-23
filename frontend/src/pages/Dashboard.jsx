// src/pages/Dashboard.jsx
import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import apiService from "../services/apiService";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  Calendar,
  DollarSign,
  TrendingDown,
  TrendingUp,
  PieChart as PieChartIcon,
  BarChart2,
  Activity,
} from "lucide-react";
import SavingTips from "../components/SavingTips/SavingTips";

const Dashboard = () => {
  const { user } = useAuth();
  const [timeRange, setTimeRange] = useState("weekly");
  const [spendingData, setSpendingData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [topExpenses, setTopExpenses] = useState([]);
  const [summary, setSummary] = useState({
    totalSpent: 0,
    averagePerDay: 0,
    comparisonToPrevious: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const COLORS = [
    "#8884d8",
    "#82ca9d",
    "#ffc658",
    "#ff8042",
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
  ];

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange, user]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(
        `/analytics/dashboard?timeRange=${timeRange}`
      );
      setSpendingData(response.data.spendingOverTime);
      setCategoryData(response.data.spendingByCategory);
      setTopExpenses(response.data.topExpenses);
      setSummary(response.data.summary);
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      setError("Failed to load dashboard data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Helper function to determine trend direction and style
  const getTrendDisplay = (value) => {
    if (value > 0) {
      return {
        icon: <TrendingUp className="w-5 h-5" />,
        color: "text-red-500",
        text: `${value.toFixed(1)}% increase`,
      };
    } else if (value < 0) {
      return {
        icon: <TrendingDown className="w-5 h-5" />,
        color: "text-green-500",
        text: `${Math.abs(value).toFixed(1)}% decrease`,
      };
    } else {
      return {
        icon: <Activity className="w-5 h-5" />,
        color: "text-blue-500",
        text: "No change",
      };
    }
  };

  // Get proper label for time range
  const getTimeRangeLabel = () => {
    switch (timeRange) {
      case "weekly":
        return "Week";
      case "monthly":
        return "Month";
      case "yearly":
        return "Year";
      default:
        return "Period";
    }
  };

  const trend = getTrendDisplay(summary.comparisonToPrevious);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 text-red-800 p-4 rounded-md">{error}</div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-bold text-gray-800">
          Your Financial Dashboard
        </h1>

        <div className="mt-4 md:mt-0">
          <div className="inline-flex rounded-md shadow-sm">
            <button
              onClick={() => setTimeRange("weekly")}
              className={`px-4 py-2 text-sm font-medium rounded-l-md ${
                timeRange === "weekly"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              } border border-gray-300`}
            >
              Weekly
            </button>
            <button
              onClick={() => setTimeRange("monthly")}
              className={`px-4 py-2 text-sm font-medium ${
                timeRange === "monthly"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              } border-t border-b border
               // src/pages/Dashboard.jsx (continued)
-r border-l-0 border-gray-300`}
            >
              Monthly
            </button>
            <button
              onClick={() => setTimeRange("yearly")}
              className={`px-4 py-2 text-sm font-medium rounded-r-md ${
                timeRange === "yearly"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              } border border-l-0 border-gray-300`}
            >
              Yearly
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Total Spent</p>
              <p className="text-2xl font-bold text-gray-800">
                {formatCurrency(summary.totalSpent)}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <DollarSign className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <p className={`text-sm flex items-center ${trend.color}`}>
              {trend.icon}
              <span className="ml-1">
                {trend.text} from previous {getTimeRangeLabel().toLowerCase()}
              </span>
            </p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">
                Average Daily Spending
              </p>
              <p className="text-2xl font-bold text-gray-800">
                {formatCurrency(summary.averagePerDay)}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm text-gray-500">
              Based on your spending this {getTimeRangeLabel().toLowerCase()}
            </p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">
                Top Spending Category
              </p>
              <p className="text-2xl font-bold text-gray-800">
                {categoryData.length > 0 ? categoryData[0].name : "No data"}
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <PieChartIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm text-gray-500">
              {categoryData.length > 0
                ? `${formatCurrency(categoryData[0].value)} (${(
                    (categoryData[0].value / summary.totalSpent) *
                    100
                  ).toFixed(1)}%)`
                : "No spending data yet"}
            </p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Spending Over Time Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-700">
              Spending Over Time
            </h2>
            <div className="bg-blue-100 p-2 rounded-full">
              <BarChart2 className="h-5 w-5 text-blue-600" />
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={spendingData}
                margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  formatter={(value) => [formatCurrency(value), "Amount"]}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="amount"
                  stroke="#8884d8"
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-700">
              Spending by Category
            </h2>
            <div className="bg-green-100 p-2 rounded-full">
              <PieChartIcon className="h-5 w-5 text-green-600" />
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {categoryData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Expenses & Tips */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Expenses */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Top Expenses
          </h2>
          {topExpenses.length > 0 ? (
            <div className="space-y-4">
              {topExpenses.map((expense, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-md"
                >
                  <div className="flex items-center">
                    <div
                      className="w-2 h-10 rounded-full"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <div className="ml-3">
                      <p className="font-medium">{expense.name}</p>
                      <p className="text-sm text-gray-500">{expense.date}</p>
                    </div>
                  </div>
                  <p className="font-semibold">
                    {formatCurrency(expense.amount)}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No expense data available</p>
          )}
        </div>

        {/* Money Saving Tips */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Personalized Saving Tips
          </h2>
          <SavingTips categories={categoryData.map((c) => c.name)} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
