import { useState, useEffect } from "react";
import api from "../../services/apiService";
import {
  LightbulbIcon,
  ChevronRight,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Loader,
} from "lucide-react";

const SavingTips = ({ categories = [] }) => {
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [loadingNewTip, setLoadingNewTip] = useState(false);

  useEffect(() => {
    fetchTips();
  }, [categories]);

  const fetchTips = async () => {
    if (categories.length === 0) {
      setTips([
        {
          id: "default",
          content:
            "Start tracking your expenses to get personalized saving tips.",
          category: "general",
          rating: null,
        },
      ]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.get("/tips", {
        params: { categories: categories.join(",") },
      });

      if (response.data.length > 0) {
        setTips(response.data);
      } else {
        setTips([
          {
            id: "default",
            content: "Add more receipt data to get personalized saving tips.",
            category: "general",
            rating: null,
          },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch saving tips:", err);
      setError("Failed to load saving tips.");
      setTips([
        {
          id: "default",
          content: "Unable to load saving tips at the moment.",
          category: "general",
          rating: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const rateTip = async (tipId, isHelpful) => {
    // Skip rating for default tips
    if (tipId === "default") return;

    // Update UI immediately
    setTips(
      tips.map((tip) =>
        tip.id === tipId ? { ...tip, rating: isHelpful } : tip
      )
    );

    try {
      await api.post(`/tips/${tipId}/rate`, {
        helpful: isHelpful,
      });
    } catch (err) {
      console.error("Failed to rate tip:", err);
      // Revert UI if request fails
      setTips(
        tips.map((tip) => (tip.id === tipId ? { ...tip, rating: null } : tip))
      );
    }
  };

  const getNextTip = async () => {
    setLoadingNewTip(true);

    if (currentTipIndex < tips.length - 1) {
      // Show next available tip
      setCurrentTipIndex(currentTipIndex + 1);
      setLoadingNewTip(false);
      return;
    }

    // Request a new tip
    try {
      const response = await api.get("/tips/new", {
        params: { categories: categories.join(",") },
      });

      if (response.data) {
        setTips([...tips, response.data]);
        setCurrentTipIndex(tips.length);
      }
    } catch (err) {
      console.error("Failed to get new tip:", err);
    } finally {
      setLoadingNewTip(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 text-red-800 p-4 rounded-md">{error}</div>
    );
  }

  const currentTip = tips[currentTipIndex];

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border border-blue-100">
        <div className="flex items-start mb-4">
          <div className="bg-blue-100 p-2 rounded-full mr-3">
            <LightbulbIcon className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <p className="text-sm text-blue-800 font-medium">
              {currentTip.category === "general"
                ? "Money Saving Tip"
                : `Tip for ${currentTip.category}`}
            </p>
            <p className="text-gray-800 mt-1">{currentTip.content}</p>
          </div>
        </div>

        {currentTip.id !== "default" && (
          <div className="flex justify-between items-center mt-4">
            <div className="flex space-x-2">
              <button
                onClick={() => rateTip(currentTip.id, true)}
                className={`flex items-center px-2 py-1 rounded ${
                  currentTip.rating === true
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <ThumbsUp className="h-4 w-4 mr-1" />
                <span className="text-sm">Helpful</span>
              </button>
              <button
                onClick={() => rateTip(currentTip.id, false)}
                className={`flex items-center px-2 py-1 rounded ${
                  currentTip.rating === false
                    ? "bg-red-100 text-red-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <ThumbsDown className="h-4 w-4 mr-1" />
                <span className="text-sm">Not helpful</span>
              </button>
            </div>

            <button
              onClick={getNextTip}
              disabled={loadingNewTip}
              className="flex items-center text-blue-600 hover:text-blue-800"
            >
              {loadingNewTip ? (
                <Loader className="h-4 w-4 mr-1 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-1" />
              )}
              <span className="text-sm">Next tip</span>
            </button>
          </div>
        )}
      </div>

      {/* Tip navigation dots */}
      {tips.length > 1 && (
        <div className="flex justify-center space-x-1">
          {tips.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentTipIndex(index)}
              className={`w-2 h-2 rounded-full ${
                index === currentTipIndex ? "bg-blue-600" : "bg-gray-300"
              }`}
              aria-label={`Go to tip ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default SavingTips;
