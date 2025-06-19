import React from "react";
import { NavLink } from "react-router-dom";
import {
  HomeIcon,
  ReceiptRefundIcon,
  CameraIcon,
  ChartBarIcon,
  LightBulbIcon,
  CogIcon,
} from "@heroicons/react/outline";

const Sidebar = ({ isOpen }) => {
  const navItems = [
    { name: "Dashboard", path: "/", icon: HomeIcon },
    { name: "Receipts", path: "/receipts", icon: ReceiptRefundIcon },
    { name: "Scan Receipt", path: "/scan", icon: CameraIcon },
    { name: "Analytics", path: "/analytics", icon: ChartBarIcon },
    { name: "Tips & Tricks", path: "/tips", icon: LightBulbIcon },
    { name: "Settings", path: "/settings", icon: CogIcon },
  ];

  return (
    <aside
      className={`fixed md:relative left-0 top-16 h-[calc(100vh-4rem)] bg-white shadow-md transition-all duration-300 ease-in-out z-30 ${
        isOpen ? "w-64" : "w-0 md:w-20 overflow-hidden"
      }`}
    >
      <div className="h-full py-4 overflow-y-auto">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center p-2 rounded-lg ${
                    isActive
                      ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  } ${isOpen ? "mx-3" : "mx-2 justify-center"}`
                }
              >
                <item.icon className={`h-6 w-6 ${isOpen ? "mr-3" : ""}`} />
                {isOpen && <span>{item.name}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
