import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import axios from "axios";
import { Camera, Upload, Loader, AlertCircle, CheckCircle } from "lucide-react";

const ScanReceipt = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [isLoading, setIsLoading] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      setPreviewImage(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleScan = async () => {
    if (!previewImage) return;

    setIsLoading(true);
    setError("");

    try {
      const token = await currentUser.getIdToken();
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/scan/receipt-base64`,
        { image_data: previewImage },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      setScanResult(response.data.processed_data);
    } catch (err) {
      console.error("Error scanning receipt:", err);
      setError(err.response?.data?.message || "Failed to scan receipt");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!scanResult) return;

    setIsLoading(true);
    try {
      const token = await currentUser.getIdToken();

      // Format the data according to your Receipt model
      const receiptData = {
        store_name: scanResult.store_name,
        date: new Date(scanResult.date).toISOString(),
        total_amount: parseFloat(scanResult.total_amount),
        items: scanResult.items.map((item, index) => ({
          id: null, // Will be generated by backend
          name: item.name,
          price: parseFloat(item.price),
          quantity: item.quantity || 1,
          category: item.category || "food",
          assigned_to: null,
          shared_with: [],
        })),
        image_url: previewImage, // Base64 image data
        is_shared: false,
        shared_expenses: [],
      };

      await axios.post(
        `${import.meta.env.VITE_API_URL}/receipts`,
        receiptData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      navigate("/receipts");
    } catch (err) {
      console.error("Error saving receipt:", err);
      setError(err.response?.data?.message || "Failed to save receipt");
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 fade-in">
      <h2 className="text-2xl font-bold text-neutral-800 mb-6">Scan Receipt</h2>

      {error && (
        <div className="badge-danger p-3 rounded-md mb-4 flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      <div className="mb-6">
        {!previewImage ? (
          <div className="card p-6 slide-in">
            <div className="drop-zone border-neutral-300 bg-neutral-50 text-center">
              <div className="flex flex-col items-center space-y-4 py-8">
                <Upload className="h-12 w-12 text-neutral-400" />
                <p className="text-neutral-500">
                  Upload a receipt image to scan
                </p>
                <button
                  onClick={() => fileInputRef.current.click()}
                  className="btn-primary"
                >
                  Select Image
                </button>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileChange}
                  ref={fileInputRef}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="card p-6 slide-in">
            <div className="flex flex-col items-center">
              <img
                src={previewImage}
                alt="Receipt preview"
                className="max-h-96 object-contain rounded-lg mb-4"
              />
              <div className="flex space-x-4">
                <button
                  onClick={handleScan}
                  disabled={isLoading}
                  className={isLoading ? "btn-ghost" : "btn-primary"}
                >
                  {isLoading ? (
                    <>
                      <Loader className="w-5 h-5 mr-2 animate-spin" />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 mr-2"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                        />
                      </svg>
                      Scan Receipt
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setPreviewImage(null);
                    setScanResult(null);
                  }}
                  className="btn-outline"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {scanResult && (
        <div className="card p-6 slide-in">
          <h3 className="text-xl font-semibold mb-4">Scan Results</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <p className="form-label">Store</p>
              <p className="text-lg">{scanResult.store_name}</p>
            </div>

            <div>
              <p className="form-label">Date</p>
              <p className="text-lg">
                {scanResult.date
                  ? new Date(scanResult.date).toLocaleDateString("en-US", {
                      month: "short",
                      day: "2-digit",
                      year: "numeric",
                    })
                  : "Not detected"}
              </p>
            </div>

            <div>
              <p className="form-label">Total</p>
              <p className="text-lg font-semibold">
                ${parseFloat(scanResult.total_amount).toFixed(2)}
              </p>
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-lg font-medium mb-2">Items</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-200">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Item
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Qty
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                      Category
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {scanResult.items &&
                    scanResult.items.map((item, index) => (
                      <tr
                        key={index}
                        className={
                          index % 2 === 0 ? "bg-white" : "bg-neutral-50"
                        }
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                          {item.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-neutral-900">
                          ${parseFloat(item.price).toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-neutral-900">
                          {item.quantity || 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span
                            className={`category-${
                              item.category?.toLowerCase() || "misc"
                            }`}
                          >
                            {item.category || "Miscellaneous"}
                          </span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={isLoading}
              className={isLoading ? "btn-ghost" : "btn-accent"}
            >
              <CheckCircle className="w-5 h-5 mr-2" />
              {isLoading ? "Saving..." : "Save Receipt"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanReceipt;
