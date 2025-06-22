import { useState, useRef } from "react";
import { useAuth } from "../../context/AuthContext";
import apiService from "../../services/apiService";
import { Camera, Upload, Loader, AlertCircle, CheckCircle } from "lucide-react";
import ReceiptItems from "./ReceiptItems";

const ReceiptScanner = () => {
  const { user } = useAuth();
  const [receiptImage, setReceiptImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const [scanSuccess, setScanSuccess] = useState(false);
  const [receiptItems, setReceiptItems] = useState([]);
  const [receiptData, setReceiptData] = useState(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/jpeg", "image/jpg", "image/png"];
    if (!validTypes.includes(file.type)) {
      setError("Please upload a valid image file (JPEG, JPG, or PNG)");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("Image file size must be less than 5MB");
      return;
    }

    setReceiptImage(file);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleCameraCapture = () => {
    cameraInputRef.current.click();
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const scanReceipt = async () => {
    if (!imagePreview) {
      setError("Please upload a receipt image first");
      return;
    }

    setIsScanning(true);
    setError(null);
    setScanSuccess(false);

    try {
      // Convert the image to base64 string - but we already have it in imagePreview
      // Just need to send the base64 string to the backend
      const token = await user.getIdToken();

      const response = await apiService.post(
        "/receipts/scan",
        { image_data: imagePreview },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // Store the complete receipt data
      setReceiptData(response.data);

      // Extract items for display
      setReceiptItems(response.data.items || []);
      setScanSuccess(true);
    } catch (err) {
      console.error("Receipt scanning failed:", err);
      setError(
        err.response?.data?.message ||
          "Failed to scan receipt. Please try again."
      );
    } finally {
      setIsScanning(false);
    }
  };

  const saveReceipt = async () => {
    if (!receiptData) {
      setError("No receipt data to save");
      return;
    }

    setIsScanning(true);
    setError(null);

    try {
      const token = await user.getIdToken();

      // Create receipt data from scan results
      const receipt = {
        store_name: receiptData.store_name || "Unknown Store",
        date: receiptData.date || new Date().toISOString(),
        total_amount: parseFloat(receiptData.total_amount) || 0,
        items: receiptData.items.map((item) => ({
          name: item.name,
          price: parseFloat(item.price),
          quantity: parseFloat(item.quantity || 1),
          category: item.category || "Uncategorized",
        })),
        image_url: imagePreview,
        is_shared: false,
        shared_expenses: [],
      };

      await apiService.post("/receipts", receipt, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      setScanSuccess(true);

      // Optional: redirect to receipts list or show success message
    } catch (err) {
      console.error("Saving receipt failed:", err);
      setError(
        err.response?.data?.message ||
          "Failed to save receipt. Please try again."
      );
    } finally {
      setIsScanning(false);
    }
  };

  const resetScanner = () => {
    setReceiptImage(null);
    setImagePreview(null);
    setReceiptItems([]);
    setReceiptData(null);
    setScanSuccess(false);
    setError(null);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Scan Receipt</h2>

      {/* Hidden file inputs */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/jpeg,image/jpg,image/png"
        className="hidden"
      />
      <input
        type="file"
        ref={cameraInputRef}
        onChange={handleFileChange}
        accept="image/jpeg,image/jpg,image/png"
        capture="environment"
        className="hidden"
      />

      {!imagePreview ? (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex flex-col space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
              <div className="flex flex-col items-center space-y-4">
                <Upload className="h-12 w-12 text-gray-400" />
                <p className="text-gray-500">
                  Upload or take a photo of your receipt
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={handleUploadClick}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center"
                  >
                    <Upload className="w-5 h-5 mr-2" />
                    Upload
                  </button>
                  <button
                    onClick={handleCameraCapture}
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition flex items-center"
                  >
                    <Camera className="w-5 h-5 mr-2" />
                    Take Photo
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex flex-col space-y-4">
            {/* Preview */}
            <div className="flex justify-center mb-4">
              <div className="relative">
                <img
                  src={imagePreview}
                  alt="Receipt preview"
                  className="max-h-80 rounded-lg shadow-sm"
                />
                <button
                  onClick={resetScanner}
                  className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={scanReceipt}
                disabled={isScanning}
                className={`px-6 py-2 ${
                  isScanning ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
                } text-white rounded-md transition flex items-center`}
              >
                {isScanning ? (
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

              {receiptData && (
                <button
                  onClick={saveReceipt}
                  disabled={isScanning}
                  className={`px-6 py-2 ${
                    isScanning
                      ? "bg-gray-400"
                      : "bg-green-600 hover:bg-green-700"
                  } text-white rounded-md transition flex items-center`}
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Save Receipt
                </button>
              )}
            </div>

            {/* Error message */}
            {error && (
              <div className="mt-4 p-3 bg-red-100 text-red-800 rounded-md flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                <span>{error}</span>
              </div>
            )}

            {/* Success message */}
            {scanSuccess && (
              <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-md flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span>Receipt scanned successfully!</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Receipt Items */}
      {receiptItems.length > 0 && (
        <ReceiptItems
          items={receiptItems}
          receiptImage={receiptImage}
          storeInfo={
            receiptData
              ? {
                  store_name: receiptData.store_name || "Unknown Store",
                  date: receiptData.date || new Date().toISOString(),
                  total_amount: receiptData.total_amount || 0,
                }
              : null
          }
        />
      )}
    </div>
  );
};

export default ReceiptScanner;
