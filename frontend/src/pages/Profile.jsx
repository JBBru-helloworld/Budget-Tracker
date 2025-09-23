import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getUserProfile,
  updateUserProfile,
  uploadAvatar,
} from "../services/profileService";
// import { toast } from "react-hot-toast";

// Temporary toast replacement
const toast = {
  error: (msg) => console.error(msg),
  success: (msg) => console.log(msg),
};

const ProfilePage = () => {
  const { currentUser } = useAuth();
  const [profile, setProfile] = useState({
    display_name: "",
    email: "",
    first_name: "",
    last_name: "",
    monthly_budget: "",
    avatar: null,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);

  // Helper function to get full avatar URL
  const getAvatarUrl = (avatarPath) => {
    if (!avatarPath) return null;
    if (avatarPath.startsWith("http")) return avatarPath; // Already a full URL
    if (avatarPath.startsWith("static/")) {
      return `${
        import.meta.env.VITE_API_URL?.replace("/api", "") ||
        "http://localhost:8000"
      }/${avatarPath}`;
    }
    return avatarPath;
  };

  useEffect(() => {
    const fetchProfile = async () => {
      if (currentUser?.uid) {
        try {
          const profileData = await getUserProfile(currentUser.uid);
          setProfile({
            display_name:
              profileData.display_name || currentUser.displayName || "",
            email: profileData.email || currentUser.email || "",
            first_name: profileData.first_name || "",
            last_name: profileData.last_name || "",
            monthly_budget: profileData.monthly_budget?.toString() || "",
            avatar: profileData.avatar || currentUser.photoURL,
          });
        } catch (error) {
          console.error("Error fetching profile:", error);
          toast.error("Failed to load profile");
          // If profile doesn't exist yet, use Firebase auth data
          setProfile({
            display_name: currentUser.displayName || "",
            email: currentUser.email || "",
            first_name: "",
            last_name: "",
            monthly_budget: "",
            avatar: currentUser.photoURL,
          });
        } finally {
          setLoading(false);
        }
      }
    };

    fetchProfile();
  }, [currentUser]);

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
        first_name: profile.first_name,
        last_name: profile.last_name,
        monthly_budget: profile.monthly_budget
          ? parseFloat(profile.monthly_budget)
          : null,
      };

      console.log("Sending profile update:", updateData);
      const updatedProfile = await updateUserProfile(
        currentUser.uid,
        updateData
      );
      console.log("Received updated profile:", updatedProfile);

      // Update local state with the response
      setProfile((prevProfile) => ({
        ...prevProfile,
        display_name: updatedProfile.display_name || prevProfile.display_name,
        first_name: updatedProfile.first_name || prevProfile.first_name,
        last_name: updatedProfile.last_name || prevProfile.last_name,
        monthly_budget:
          updatedProfile.monthly_budget?.toString() ||
          prevProfile.monthly_budget,
        avatar: updatedProfile.avatar || prevProfile.avatar,
      }));

      // Upload avatar if selected
      if (file) {
        const avatarPath = await uploadAvatar(currentUser.uid, file);
        setProfile((prevProfile) => ({
          ...prevProfile,
          avatar: avatarPath,
        }));
        setFile(null);
        setFilePreview(null);
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
                src={
                  filePreview ||
                  getAvatarUrl(profile.avatar) ||
                  "/default-avatar.png"
                }
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
                htmlFor="first_name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                First Name
              </label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={profile.first_name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label
                htmlFor="last_name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Last Name
              </label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={profile.last_name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

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
                disabled
                title="Email cannot be changed"
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
