/* settings.jsx */
import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

const Settings = () => {
  const { currentUser, updateProfile, resetPassword } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (currentUser) {
      setDisplayName(currentUser.display_name || "");
      setEmail(currentUser.email || "");
    }
  }, [currentUser]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      await updateProfile(currentUser.uid, { display_name: displayName });
      setMessage("Profile updated successfully.");
    } catch (err) {
      setError(err.message);
    }
  };

  const handlePasswordReset = async () => {
    try {
      setError(null);
      await resetPassword(email);
      setMessage("Password reset email sent.");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-6">
      <h2 className="text-2xl font-semibold">Account Settings</h2>
      {message && (
        <div className="p-2 bg-green-100 text-green-800 rounded">{message}</div>
      )}
      {error && (
        <div className="p-2 bg-red-100 text-red-800 rounded">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Display Name</label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Email</label>
          <input
            type="email"
            value={email}
            disabled
            className="mt-1 block w-full bg-gray-100 border-gray-300 rounded-md shadow-sm"
          />
        </div>

        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-500"
        >
          Save Changes
        </button>
      </form>

      <div className="pt-4 border-t">
        <h3 className="text-lg font-medium">Password</h3>
        <button
          onClick={handlePasswordReset}
          className="mt-2 text-blue-600 hover:text-blue-500"
        >
          Send Password Reset Email
        </button>
      </div>
    </div>
  );
};

export default Settings;
