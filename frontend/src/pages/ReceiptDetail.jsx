import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  ExclamationCircleIcon,
} from "@heroicons/react/outline";
import { useAuth } from "../context/AuthContext";

const ReceiptDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    const fetchReceipt = async () => {
      try {
        // Get the auth token
        const token = await currentUser.getIdToken();

        // Fetch receipt from API
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/api/receipts/${id}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Receipt not found");
          }
          throw new Error("Failed to fetch receipt");
        }

        const data = await response.json();
        setReceipt(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching receipt:", error);
        setError(error.message);
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchReceipt();
    }
  }, [currentUser, id]);

  const handleDelete = async () => {
    try {
      setDeleteLoading(true);
      // Get the auth token
      const token = await currentUser.getIdToken();

      // Delete receipt from API
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/receipts/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete receipt");
      }

      // Navigate back to receipts list
      navigate("/receipts");
    } catch (error) {
      console.error("Error deleting receipt:", error);
      setError(error.message);
      setDeleteLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
          <div className="flex items-center">
            <ExclamationCircleIcon className="h-6 w-6 text-red-500 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
        <Link
          to="/receipts"
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-1" />
          Back to Receipts
        </Link>
      </div>
    );
  }

  if (!receipt) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-6 rounded-lg">
          <div className="flex items-center">
            <ExclamationCircleIcon className="h-6 w-6 text-yellow-500 mr-2" />
            <p className="text-yellow-700">Receipt not found</p>
          </div>
        </div>
        <Link
          to="/receipts"
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-1" />
          Back to Receipts
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header with back button */}
      <div className="mb-6">
        <Link
          to="/receipts"
          className="inline-flex items-center text-gray-600 hover:text-blue-600"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-1" />
          Back to Receipts
        </Link>
      </div>

      {/* Receipt card */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600">
          <div className="flex justify-between items-start">
            <h1 className="text-2xl font-bold text-white">{receipt.store}</h1>
            <div className="flex space-x-2">
              <Link
                to={`/receipt/${id}/edit`}
                className="p-2 bg-white bg-opacity-20 rounded-full hover:bg-opacity-30 transition-colors"
              >
                <PencilIcon className="h-5 w-5 text-white" />
              </Link>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="p-2 bg-white bg-opacity-20 rounded-full hover:bg-opacity-30 transition-colors"
              >
                <TrashIcon className="h-5 w-5 text-white" />
              </button>
            </div>
          </div>
          <div className="mt-2 text-white text-opacity-90">
            {formatDate(receipt.date)}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-700 mb-4">
                Receipt Details
              </h2>

              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Amount</p>
                  <p className="text-xl font-bold text-gray-900">
                    {formatCurrency(receipt.amount)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-500">Category</p>
                  <div className="mt-1">
                    <span
                      className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full 
                      ${
                        receipt.category === "Food"
                          ? "bg-green-100 text-green-800"
                          : receipt.category === "Transportation"
                          ? "bg-blue-100 text-blue-800"
                          : receipt.category === "Clothing"
                          ? "bg-purple-100 text-purple-800"
                          : receipt.category === "Entertainment"
                          ? "bg-yellow-100 text-yellow-800"
                          : receipt.category === "Utilities"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {receipt.category}
                    </span>
                  </div>
                </div>

                {receipt.paymentMethod && (
                  <div>
                    <p className="text-sm text-gray-500">Payment Method</p>
                    <p className="text-base text-gray-900">
                      {receipt.paymentMethod}
                    </p>
                  </div>
                )}

                {receipt.tax && (
                  <div>
                    <p className="text-sm text-gray-500">Tax</p>
                    <p className="text-base text-gray-900">
                      {formatCurrency(receipt.tax)}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div>
              {receipt.description && (
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-gray-700 mb-2">
                    Description
                  </h2>
                  <p className="text-gray-600 whitespace-pre-line">
                    {receipt.description}
                  </p>
                </div>
              )}

              {receipt.items && receipt.items.length > 0 && (
                <div>
                  <h2 className="text-lg font-semibold text-gray-700 mb-2">
                    Items
                  </h2>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <ul className="divide-y divide-gray-200">
                      {receipt.items.map((item, index) => (
                        <li key={index} className="py-3 flex justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {item.name}
                            </p>
                            {item.quantity > 1 && (
                              <p className="text-sm text-gray-500">
                                Qty: {item.quantity}
                              </p>
                            )}
                          </div>
                          <p className="text-sm font-medium text-gray-900">
                            {formatCurrency(item.price)}
                          </p>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {receipt.imageUrl && (
          <div className="p-6 bg-gray-50 border-t border-gray-200">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              Receipt Image
            </h2>
            <div className="bg-white p-2 rounded-lg shadow-sm border border-gray-200 inline-block">
              <img
                src={receipt.imageUrl}
                alt="Receipt"
                className="max-h-64 object-contain"
              />
            </div>
          </div>
        )}
      </div>

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Delete Receipt
            </h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this receipt? This action cannot
              be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteLoading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
              >
                {deleteLoading ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReceiptDetail;
