import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "../services/categoryService";
import { toast } from "react-hot-toast";
import { PlusIcon, PencilIcon, TrashIcon } from "@heroicons/react/outline";

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

const CategoriesPage = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentCategory, setCurrentCategory] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      if (user?.uid) {
        try {
          const data = await getCategories();
          setCategories(data);
        } catch (error) {
          console.error("Error fetching categories:", error);
          toast.error("Failed to load categories");
        } finally {
          setLoading(false);
        }
      }
    };

    fetchCategories();
  }, [user]);

  const handleOpenModal = (category = null) => {
    setCurrentCategory(category);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setCurrentCategory(null);
  };

  const handleSaveCategory = async (categoryData) => {
    try {
      if (currentCategory) {
        // Update existing category
        const updated = await updateCategory(currentCategory._id, categoryData);
        setCategories(
          categories.map((cat) =>
            cat._id === currentCategory._id ? updated : cat
          )
        );
        toast.success("Category updated");
      } else {
        // Create new category
        const created = await createCategory({
          ...categoryData,
          user_id: user.uid,
        });
        setCategories([...categories, created]);
        toast.success("Category created");
      }
      handleCloseModal();
    } catch (error) {
      console.error("Error saving category:", error);
      toast.error("Failed to save category");
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm("Are you sure you want to delete this category?")) {
      try {
        await deleteCategory(categoryId);
        setCategories(categories.filter((cat) => cat._id !== categoryId));
        toast.success("Category deleted");
      } catch (error) {
        console.error("Error deleting category:", error);
        toast.error("Failed to delete category");
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Categories</h1>
        <button
          onClick={() => handleOpenModal()}
          className="bg-gradient-to-r from-blue-500 to-purple-600 text-white flex items-center py-2 px-4 rounded-lg hover:opacity-90"
        >
          <PlusIcon className="h-5 w-5 mr-1" />
          New Category
        </button>
      </div>

      {categories.length === 0 ? (
        <div className="bg-white rounded-xl shadow-md p-8 text-center">
          <p className="text-gray-500 mb-4">
            You haven't created any categories yet.
          </p>
          <button
            onClick={() => handleOpenModal()}
            className="inline-flex items-center text-purple-600 hover:text-purple-800"
          >
            <PlusIcon className="h-5 w-5 mr-1" />
            Create your first category
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <div
              key={category._id}
              className="bg-white rounded-xl shadow-md p-4 flex flex-col"
              style={{ borderLeft: `4px solid ${category.color}` }}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-medium">{category.name}</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleOpenModal(category)}
                    className="text-gray-500 hover:text-blue-600 p-1"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDeleteCategory(category._id)}
                    className="text-gray-500 hover:text-red-600 p-1"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {category.budget && (
                <div className="text-sm text-gray-600 mt-1">
                  Monthly Budget: ${category.budget.toFixed(2)}
                </div>
              )}

              <div className="mt-2 pt-2 border-t border-gray-100 text-sm text-gray-500">
                {category.created_at &&
                  new Date(category.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}

      <CategoryModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveCategory}
        category={currentCategory}
      />

      {/* Budget Utilization Section */}
      {categories.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Budget Utilization
          </h2>
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="space-y-4">
              {categories
                .filter((cat) => cat.budget)
                .map((category) => (
                  <div key={`budget-${category._id}`} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{category.name}</span>
                      <span>${category.budget.toFixed(2)}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded overflow-hidden">
                      <div
                        className="h-full rounded"
                        style={{
                          width: `${Math.min(Math.random() * 100, 100)}%`,
                          backgroundColor: category.color,
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoriesPage;
