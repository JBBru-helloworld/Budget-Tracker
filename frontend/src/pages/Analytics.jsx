// analytics.jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const Analytics = () => {
  const { currentUser } = useAuth();
  const [data, setData] = useState({ weekly: [], monthly: [], yearly: [] });
  const [view, setView] = useState("weekly");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!currentUser) return;

      try {
        setLoading(true);
        setError(null);

        const token = await currentUser.getIdToken();
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/analytics?range=${view}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch analytics: ${response.status}`);
        }

        const analyticsData = await response.json();
        setData((prev) => ({ ...prev, [view]: analyticsData }));
      } catch (err) {
        console.error("Error fetching analytics:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [currentUser, view]);

  const chartData = data[view] || [];

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="text-center">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="text-center text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 mt-6 mb-4 ml-6">
        {["weekly", "monthly", "yearly"].map((r) => (
          <button
            key={r}
            onClick={() => setView(r)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              view === r
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            {r.charAt(0).toUpperCase() + r.slice(1)}
          </button>
        ))}
      </div>

      {chartData.length === 0 ? (
        <div className="text-center text-gray-500">
          No data available for the selected period
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#4F46E5"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default Analytics;
