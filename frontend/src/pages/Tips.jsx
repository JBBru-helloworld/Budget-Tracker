import React, { useState, useEffect } from "react";
import apiService from "../services/apiService";
import { useAuth } from "../context/AuthContext";

const Tips = () => {
  const { currentUser } = useAuth();
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTips = async () => {
      try {
        setLoading(true);
        const res = await apiService.post(`/api/tips`, {
          userId: currentUser.uid,
        });
        setTips(res.data.tips);
      } catch (err) {
        console.error("Error fetching tips:", err);
        setError("Failed to load tips.");
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) fetchTips();
  }, [currentUser]);

  if (loading) return <p>Loading tips...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Money-Saving Tips</h2>
      <ul className="list-disc list-inside space-y-2">
        {tips.map((tip, idx) => (
          <li key={idx} className="text-gray-700">
            {tip}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Tips;
