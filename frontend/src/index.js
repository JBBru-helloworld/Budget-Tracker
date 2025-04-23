// frontend/src/index.js

import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// At the top of your index.js
const originalConsoleError = console.error;
console.error = (...args) => {
  if (args[0] && args[0].includes("Warning:")) {
    originalConsoleError(...args);
  }
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
