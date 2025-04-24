/* analytics.jsx */
import React, { useState, useEffect } from "react";
import apiService from "../services/apiService";
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

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await apiService.get(
          `/api/analytics?userId=${currentUser.uid}&range=${view}`
        );
        setData((prev) => ({ ...prev, [view]: res.data }));
      } catch (err) {
        console.error("Error fetching analytics:", err);
      }
    };

    if (currentUser) fetchAnalytics();
  }, [currentUser, view]);

  const chartData = data[view];

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
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
    </div>
  );
};

export default Analytics;
