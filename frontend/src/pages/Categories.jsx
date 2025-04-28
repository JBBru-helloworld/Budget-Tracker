import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { toast } from "react-hot-toast";
import { PlusIcon, PencilIcon, TrashIcon } from "@heroicons/react/outline";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const CategoryModal = ({ isOpen, onClose, onSave, category = null }) => {
  const [formData, setFormData] = useState({
    name: "",
    color: "#3B82F6",
    icon: "tag",
    budget: "",
  });

  useEffect(() => {
    if (category) {
      setFormData({
        name: category.name || "",
        color: category.color || "#3B82F6",
        icon: category.icon || "tag",
        budget: category.budget?.toString() || "",
      });
    } else {
      setFormData({
        name: "",
        color: "#3B82F6",
        icon: "tag",
        budget: "",
      });
    }
  }, [category, isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const categoryData = {
      name: formData.name,
      color: formData.color,
      icon: formData.icon,
      budget: formData.budget ? parseFloat(formData.budget) : null,
    };

    onSave(categoryData);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
        <h2 className="text-2xl font-bold mb-4">
          {category ? "Edit Category" : "New Category"}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Category Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label
                htmlFor="color"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Color
              </label>
              <div className="flex items-center">
                <input
                  type="color"
                  id="color"
                  name="color"
                  value={formData.color}
                  onChange={handleChange}
                  className="h-10 w-10 border-0 p-0"
                />
                <input
                  type="text"
                  value={formData.color}
                  onChange={handleChange}
                  name="color"
                  className="ml-2 flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="icon"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Icon
              </label>
              <select
                id="icon"
                name="icon"
                value={formData.icon}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="tag">Tag</option>
                <option value="shopping-bag">Shopping</option>
                <option value="utensils">Food</option>
                <option value="home">Home</option>
                <option value="car">Transport</option>
                <option value="medical">Health</option>
                <option value="book">Education</option>
                <option value="gamepad">Entertainment</option>
                <option value="suitcase">Travel</option>
                <option value="gift">Gifts</option>
              </select>
            </div>

            <div>
              <label
                htmlFor="budget"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Monthly Budget ($)
              </label>
              <input
                type="number"
                id="budget"
                name="budget"
                value={formData.budget}
                onChange={handleChange}
                step="0.01"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:opacity-90"
              >
                {category ? "Update" : "Create"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

const Categories = () => {
  const { currentUser } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentCategory, setCurrentCategory] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    if (!currentUser) return;

    try {
      const token = await currentUser.getIdToken();
      const response = await axios.get(`${API_URL}/categories`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setCategories(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching categories:", error);
      toast.error("Failed to load categories");
      setLoading(false);
    }
  };

  const handleAddCategory = async (categoryData) => {
    if (!currentUser) return;

    try {
      const token = await currentUser.getIdToken();
      const response = await axios.post(`${API_URL}/categories`, categoryData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      setCategories([...categories, response.data]);
      toast.success("Category created successfully");
    } catch (error) {
      console.error("Error creating category:", error);
      toast.error("Failed to create category");
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!currentUser) return;

    if (!window.confirm("Are you sure you want to delete this category?"))
      return;

    try {
      const token = await currentUser.getIdToken();
      await axios.delete(`${API_URL}/categories/${categoryId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setCategories(categories.filter((cat) => cat._id !== categoryId));
      toast.success("Category deleted successfully");
    } catch (error) {
      console.error("Error deleting category:", error);
      toast.error("Failed to delete category");
    }
  };

  const handleOpenModal = (category = null) => {
    setCurrentCategory(category);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setCurrentCategory(null);
  };

  const handleSaveCategory = async (categoryData) => {
    if (currentCategory) {
      // Update existing category
      try {
        const token = await currentUser.getIdToken();
        const response = await axios.put(
          `${API_URL}/categories/${currentCategory._id}`,
          categoryData,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );
        setCategories(
          categories.map((cat) =>
            cat._id === currentCategory._id ? response.data : cat
          )
        );
        toast.success("Category updated successfully");
      } catch (error) {
        console.error("Error updating category:", error);
        toast.error("Failed to update category");
      }
    } else {
      // Create new category
      handleAddCategory(categoryData);
    }
    handleCloseModal();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Categories</h1>
          <button
            onClick={() => handleOpenModal()}
            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:opacity-90 flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Category
          </button>
        </div>

        <div className="space-y-4">
          {categories.map((category) => (
            <div
              key={category._id}
              className="flex items-center justify-between p-4 bg-white rounded-lg shadow"
            >
              <div className="flex items-center">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center mr-4"
                  style={{ backgroundColor: category.color }}
                >
                  <span className="text-white">{category.icon}</span>
                </div>
                <div>
                  <h3 className="font-medium">{category.name}</h3>
                  {category.budget && (
                    <p className="text-sm text-gray-500">
                      Budget: ${category.budget.toFixed(2)}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleOpenModal(category)}
                  className="p-2 text-blue-500 hover:text-blue-600"
                >
                  <PencilIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleDeleteCategory(category._id)}
                  className="p-2 text-red-500 hover:text-red-600"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}

          {categories.length === 0 && (
            <p className="text-center text-gray-500">
              No categories yet. Add your first category above!
            </p>
          )}
        </div>
      </div>

      <CategoryModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveCategory}
        category={currentCategory}
      />
    </div>
  );
};

export default Categories;
