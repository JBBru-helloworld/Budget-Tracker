import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getUserProfile,
  updateUserProfile,
  uploadAvatar,
} from "../services/profileService";
import { toast } from "react-hot-toast";

const ProfilePage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    display_name: "",
    email: "",
    monthly_budget: "",
    avatar_url: null,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (user?.uid) {
        try {
          const profileData = await getUserProfile(user.uid);
          setProfile({
            display_name: profileData.display_name || user.displayName || "",
            email: profileData.email || user.email || "",
            monthly_budget: profileData.monthly_budget?.toString() || "",
            avatar_url: profileData.avatar_url || user.photoURL,
          });
        } catch (error) {
          console.error("Error fetching profile:", error);
          toast.error("Failed to load profile");
          // If profile doesn't exist yet, use Firebase auth data
          setProfile({
            display_name: user.displayName || "",
            email: user.email || "",
            monthly_budget: "",
            avatar_url: user.photoURL,
          });
        } finally {
          setLoading(false);
        }
      }
    };

    fetchProfile();
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile({
      ...profile,
      [name]: value,
    });
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file type
      if (
        !["image/jpeg", "image/png", "image/jpg"].includes(selectedFile.type)
      ) {
        toast.error("Please select a JPG or PNG image");
        return;
      }

      setFile(selectedFile);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      // Update profile
      const updateData = {
        display_name: profile.display_name,
        email: profile.email,
        monthly_budget: profile.monthly_budget
          ? parseFloat(profile.monthly_budget)
          : null,
      };

      await updateUserProfile(user.uid, updateData);

      // Upload avatar if selected
      if (file) {
        const avatarUrl = await uploadAvatar(user.uid, file);
        setProfile({
          ...profile,
          avatar_url: avatarUrl,
        });
      }

      toast.success("Profile updated successfully");
    } catch (error) {
      console.error("Error updating profile:", error);
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
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
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Your Profile</h1>

      <div className="bg-white rounded-xl shadow-md p-6">
        <form onSubmit={handleSubmit}>
          <div className="flex flex-col items-center mb-6">
            <div className="relative group">
              <img
                src={filePreview || profile.avatar_url || "/default-avatar.png"}
                alt="Profile"
                className="w-32 h-32 rounded-full object-cover border-4 border-purple-100"
              />
              <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                <label className="cursor-pointer text-white font-medium">
                  Change
                  <input
                    type="file"
                    className="hidden"
                    accept="image/jpeg,image/png,image/jpg"
                    onChange={handleFileChange}
                  />
                </label>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="display_name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Display Name
              </label>
              <input
                type="text"
                id="display_name"
                name="display_name"
                value={profile.display_name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={profile.email}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label
                htmlFor="monthly_budget"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Monthly Budget ($)
              </label>
              <input
                type="number"
                id="monthly_budget"
                name="monthly_budget"
                value={profile.monthly_budget}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={saving}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-70 flex justify-center items-center"
              >
                {saving ? (
                  <>
                    <span className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-2"></span>
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
