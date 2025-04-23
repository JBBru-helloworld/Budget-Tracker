// frontend/src/pages/Receipts.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Receipts = () => {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { currentUser } = useAuth();

  // Mock receipt data - replace with actual API call
  useEffect(() => {
    const fetchReceipts = async () => {
      try {
        // Replace with actual API call
        // const response = await apiService.get(`/api/receipts?userId=${currentUser.uid}`);
        // setReceipts(response.data);

        // Mock data
        setReceipts([
          {
            id: "1",
            merchant: "Grocery Store",
            date: "2025-04-15",
            total: 45.67,
            category: "Groceries",
          },
          {
            id: "2",
            merchant: "Gas Station",
            date: "2025-04-12",
            total: 35.25,
            category: "Transportation",
          },
          {
            id: "3",
            merchant: "Coffee Shop",
            date: "2025-04-10",
            total: 12.5,
            category: "Food",
          },
        ]);
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch receipts");
        setLoading(false);
      }
    };

    fetchReceipts();
  }, [currentUser]);

  if (loading) {
    return <div className="text-center p-8">Loading receipts...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Receipts</h1>
        <Link
          to="/scan"
          className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
        >
          Scan New Receipt
        </Link>
      </div>

      {receipts.length === 0 ? (
        <div className="text-center p-8 bg-gray-100 rounded-lg">
          <p className="mb-4">You haven't added any receipts yet.</p>
          <Link to="/scan" className="text-blue-500 hover:underline">
            Add your first receipt
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-3 px-4 text-left">Merchant</th>
                <th className="py-3 px-4 text-left">Date</th>
                <th className="py-3 px-4 text-left">Category</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {receipts.map((receipt) => (
                <tr key={receipt.id} className="hover:bg-gray-50">
                  <td className="py-3 px-4">{receipt.merchant}</td>
                  <td className="py-3 px-4">
                    {new Date(receipt.date).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4">{receipt.category}</td>
                  <td className="py-3 px-4 text-right">
                    ${receipt.total.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <Link
                      to={`/receipts/${receipt.id}`}
                      className="text-blue-500 hover:underline mr-2"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Receipts;
