// frontend/src/pages/ScanReceipt.jsx
import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  CameraIcon,
  UploadIcon,
  DocumentTextIcon,
} from "@heroicons/react/outline";
import {
  getStorage,
  ref,
  uploadBytesResumable,
  getDownloadURL,
} from "firebase/storage";
import { useAuth } from "../context/AuthContext";
import { app } from "../firebase";

const ScanReceipt = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [scannedData, setScannedData] = useState(null);
  const [error, setError] = useState("");
  const [step, setStep] = useState(1); // 1: Upload, 2: Review, 3: Assign
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const storage = getStorage(app);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file type
      if (
        !["image/jpeg", "image/jpg", "image/png"].includes(selectedFile.type)
      ) {
        setError("Please select a valid image file (JPG, JPEG, or PNG)");
        return;
      }

      setFile(selectedFile);
      setError("");

      // Create preview URL
      const reader = new FileReader();
      reader.onload = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleScanReceipt = async () => {
    if (!file) {
      setError("Please select an image to scan");
      return;
    }

    setScanning(true);
    setError("");

    try {
      // 1. Upload file to Firebase Storage
      const storageRef = ref(
        storage,
        `receipts/${currentUser.uid}/${Date.now()}-${file.name}`
      );
      const uploadTask = uploadBytesResumable(storageRef, file);

      uploadTask.on(
        "state_changed",
        (snapshot) => {
          const progress =
            (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
          setUploadProgress(progress);
        },
        (error) => {
          setError("Upload failed: " + error.message);
          setScanning(false);
        },
        async () => {
          // Upload complete, get download URL
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);

          // 2. Send to backend for AI text extraction
          const response = await fetch(
            `${import.meta.env.VITE_API_URL}/api/receipts/scan`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${await currentUser.getIdToken()}`,
              },
              body: JSON.stringify({ imageUrl: downloadURL }),
            }
          );

          if (!response.ok) {
            throw new Error("Failed to scan receipt");
          }

          const data = await response.json();
          setScannedData(data);
          setStep(2); // Move to review step
          setScanning(false);
        }
      );
    } catch (error) {
      console.error("Error scanning receipt:", error);
      setError("Failed to scan receipt: " + error.message);
      setScanning(false);
    }
  };

  const handleSaveReceipt = async () => {
    try {
      // Save the receipt data to the backend
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/receipts`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${await currentUser.getIdToken()}`,
          },
          body: JSON.stringify({
            ...scannedData,
            imageUrl: scannedData.imageUrl,
            items: scannedData.items.map((item) => ({
              ...item,
              assignedTo: item.assignedTo || "self",
            })),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to save receipt");
      }

      const savedReceipt = await response.json();

      // Navigate to the receipt detail page
      navigate(`/receipts/${savedReceipt.id}`);
    } catch (error) {
      console.error("Error saving receipt:", error);
      setError("Failed to save receipt: " + error.message);
    }
  };

  const assignItemTo = (itemIndex, person) => {
    setScannedData((prevData) => {
      const updatedItems = [...prevData.items];
      updatedItems[itemIndex] = {
        ...updatedItems[itemIndex],
        assignedTo: person,
      };

      return {
        ...prevData,
        items: updatedItems,
      };
    });
  };

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Scan Receipt</h1>

      {error && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
          role="alert"
        >
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {step === 1 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div
            className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer hover:border-blue-500 mb-4"
            onClick={() => fileInputRef.current.click()}
          >
            {previewUrl ? (
              <div className="w-full flex justify-center">
                <img
                  src={previewUrl}
                  alt="Receipt preview"
                  className="max-w-full max-h-64 rounded"
                />
              </div>
            ) : (
              <>
                <UploadIcon className="h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500 text-center">
                  Click to upload or drag and drop
                  <br />
                  <span className="text-sm">JPG, JPEG, or PNG</span>
                </p>
              </>
            )}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/jpeg,image/jpg,image/png"
              className="hidden"
            />
          </div>

          <div className="flex justify-center">
            <button
              onClick={handleScanReceipt}
              disabled={!file || scanning}
              className={`flex items-center justify-center px-4 py-2 rounded-md text-white font-medium 
                ${
                  !file || scanning
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                }`}
            >
              {scanning ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-2"></div>
                  Scanning ({Math.round(uploadProgress)}%)
                </>
              ) : (
                <>
                  <CameraIcon className="h-5 w-5 mr-2" />
                  Scan Receipt
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {step === 2 && scannedData && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium mb-4">Review Scanned Items</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Receipt Image
              </h3>
              <div className="border rounded overflow-hidden">
                <img src={previewUrl} alt="Receipt" className="w-full" />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Receipt Details
              </h3>
              <div className="border rounded p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-gray-500">Store</label>
                    <input
                      type="text"
                      value={scannedData.store}
                      onChange={(e) =>
                        setScannedData({
                          ...scannedData,
                          store: e.target.value,
                        })
                      }
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Date</label>
                    <input
                      type="date"
                      value={scannedData.date}
                      onChange={(e) =>
                        setScannedData({ ...scannedData, date: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Category</label>
                    <select
                      value={scannedData.category}
                      onChange={(e) =>
                        setScannedData({
                          ...scannedData,
                          category: e.target.value,
                        })
                      }
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    >
                      <option value="Food">Food</option>
                      <option value="Transportation">Transportation</option>
                      <option value="Clothing">Clothing</option>
                      <option value="Entertainment">Entertainment</option>
                      <option value="Utilities">Utilities</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Total</label>
                    <input
                      type="number"
                      value={scannedData.total}
                      onChange={(e) =>
                        setScannedData({
                          ...scannedData,
                          total: parseFloat(e.target.value),
                        })
                      }
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                      step="0.01"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <h3 className="text-md font-medium mb-2">Items</h3>
          <div className="border rounded overflow-hidden mb-6">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Item
                  </th>
                  <th
                    scope="col"
                    className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Quantity
                  </th>
                  <th
                    scope="col"
                    className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Price
                  </th>
                  <th
                    scope="col"
                    className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Assigned To
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {scannedData.items.map((item, index) => (
                  <tr key={index}>
                    <td className="px-3 py-2 text-sm">
                      <input
                        type="text"
                        value={item.name}
                        onChange={(e) => {
                          const updatedItems = [...scannedData.items];
                          updatedItems[index].name = e.target.value;
                          setScannedData({
                            ...scannedData,
                            items: updatedItems,
                          });
                        }}
                        className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                      />
                    </td>
                    <td className="px-3 py-2 text-sm">
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => {
                          const updatedItems = [...scannedData.items];
                          updatedItems[index].quantity = parseInt(
                            e.target.value
                          );
                          setScannedData({
                            ...scannedData,
                            items: updatedItems,
                          });
                        }}
                        className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                        min="1"
                      />
                    </td>
                    <td className="px-3 py-2 text-sm">
                      <input
                        type="number"
                        value={item.price}
                        onChange={(e) => {
                          const updatedItems = [...scannedData.items];
                          updatedItems[index].price = parseFloat(
                            e.target.value
                          );
                          setScannedData({
                            ...scannedData,
                            items: updatedItems,
                          });
                        }}
                        className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                        step="0.01"
                      />
                    </td>
                    <td className="px-3 py-2 text-sm">
                      <select
                        value={item.assignedTo || "self"}
                        onChange={(e) => assignItemTo(index, e.target.value)}
                        className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                      >
                        <option value="self">Me</option>
                        <option value="roommate">Roommate</option>
                        <option value="partner">Partner</option>
                        <option value="other">Other</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 font-medium hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={handleSaveReceipt}
              className="px-4 py-2 rounded-md text-white font-medium bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              Save Receipt
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanReceipt;
