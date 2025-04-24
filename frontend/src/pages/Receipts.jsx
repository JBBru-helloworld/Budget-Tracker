// frontend/src/pages/Receipts.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  PlusCircleIcon,
  SearchIcon,
  FilterIcon,
  SortAscendingIcon,
  SortDescendingIcon,
  ExclamationCircleIcon,
} from "@heroicons/react/outline";
import { useAuth } from "../context/AuthContext";

const Receipts = () => {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [sortBy, setSortBy] = useState("date"); // 'date', 'amount', 'store'
  const [sortDirection, setSortDirection] = useState("desc"); // 'asc', 'desc'
  const { currentUser } = useAuth();

  const categories = [
    "All",
    "Food",
    "Transportation",
    "Clothing",
    "Entertainment",
    "Utilities",
    "Other",
  ];

  useEffect(() => {
    const fetchReceipts = async () => {
      try {
        // Get the auth token
        const token = await currentUser.getIdToken();

        // Fetch receipts from API
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/api/receipts`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch receipts");
        }

        const data = await response.json();
        setReceipts(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching receipts:", error);
        setError(error.message);
        setReceipts([]);
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchReceipts();
    }
  }, [currentUser]);

  // Filter and sort receipts
  const filteredReceipts = receipts
    .filter((receipt) => {
      const matchesSearch = receipt.store
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesCategory =
        filterCategory === "" ||
        filterCategory === "All" ||
        receipt.category === filterCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortBy === "date") {
        return sortDirection === "asc"
          ? new Date(a.date) - new Date(b.date)
          : new Date(b.date) - new Date(a.date);
      } else if (sortBy === "amount") {
        return sortDirection === "asc"
          ? a.amount - b.amount
          : b.amount - a.amount;
      } else if (sortBy === "store") {
        return sortDirection === "asc"
          ? a.store.localeCompare(b.store)
          : b.store.localeCompare(a.store);
      }
      return 0;
    });

  const toggleSortDirection = () => {
    setSortDirection(sortDirection === "asc" ? "desc" : "asc");
  };

  const formatDate = (dateString) => {
    const options = { year: "numeric", month: "short", day: "numeric" };
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

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-semibold mb-4 md:mb-0">Receipts</h1>
        <Link
          to="/scan"
          className="flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
        >
          <PlusCircleIcon className="h-5 w-5 mr-2" />
          Add Receipt
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 mb-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <SearchIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search receipts..."
              className="pl-10 w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Category Filter */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FilterIcon className="h-5 w-5 text-gray-400" />
            </div>
            <select
              className="pl-10 w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {sortDirection === "asc" ? (
                <SortAscendingIcon className="h-5 w-5 text-gray-400" />
              ) : (
                <SortDescendingIcon className="h-5 w-5 text-gray-400" />
              )}
            </div>
            <select
              className="pl-10 w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="date">Sort by Date</option>
              <option value="amount">Sort by Amount</option>
              <option value="store">Sort by Store</option>
            </select>
            <button
              onClick={toggleSortDirection}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {sortDirection === "asc" ? (
                <SortAscendingIcon className="h-5 w-5 text-gray-500 hover:text-blue-500" />
              ) : (
                <SortDescendingIcon className="h-5 w-5 text-gray-500 hover:text-blue-500" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
          <div className="flex items-center">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2" />
            <p className="text-red-700">Error loading receipts: {error}</p>
          </div>
        </div>
      )}

      {/* Receipts List */}
      {filteredReceipts.length > 0 ? (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Date
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Store
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Category
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Amount
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredReceipts.map((receipt) => (
                  <tr key={receipt.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(receipt.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {receipt.store}
                      </div>
                      {receipt.description && (
                        <div className="text-sm text-gray-500 truncate max-w-xs">
                          {receipt.description}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(receipt.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/receipt/${receipt.id}`}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        View
                      </Link>
                      <Link
                        to={`/receipt/${receipt.id}/edit`}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Edit
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white p-8 rounded-lg shadow text-center">
          {searchTerm || (filterCategory !== "" && filterCategory !== "All") ? (
            <div>
              <p className="text-gray-500 mb-4">
                No receipts match your search criteria.
              </p>
              <button
                onClick={() => {
                  setSearchTerm("");
                  setFilterCategory("");
                }}
                className="text-blue-500 hover:text-blue-700"
              >
                Clear filters
              </button>
            </div>
          ) : (
            <div>
              <p className="text-gray-500 mb-4">
                You haven't added any receipts yet.
              </p>
              <Link
                to="/scan"
                className="inline-flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusCircleIcon className="h-5 w-5 mr-2" />
                Scan your first receipt
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Receipts;
