# Budget Tracker

A modern web application that helps users track and manage their expenses by scanning receipts, allocating costs, and analysing spending patterns.

## 📋 Overview

Budget Tracker is a comprehensive financial management tool that combines receipt scanning technology with expense tracking and budget analytics. Users can upload or scan their receipts, which are then processed using AI to extract individual items. These items can be allocated to different users for shared expenses or categorised for personal budgeting. The application provides visual analytics to help users understand their spending habits and offers personalised money-saving tips.

## ✨ Features

- **Receipt Scanning**: Upload receipt images or scan them directly with your device camera
- **AI-Powered Text Extraction**: Automatically convert receipt images to text data
- **Item Categorisation**: Automatically categorise spending into groups (food, clothing, recreation, etc.)
- **Cost Sharing**: Drag and drop items to allocate expenses between multiple users
- **Visual Analytics**: Track spending with weekly, monthly, and yearly graphs
- **Smart Insights**: Receive personalised money-saving tips based on spending patterns
- **Secure Authentication**: Firebase authentication with email/password and password reset
- **Responsive Design**: Fully functional on mobile, tablet, and desktop devices

## 🛠️ Tech Stack

### Frontend

- **React.js**: UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Firebase Auth**: User authentication
- **Context API**: State management

### Backend

- **FastAPI**: High-performance Python web framework
- **MongoDB**: NoSQL database for storing user and receipt data
- **Docker**: Containerisation for consistent development and deployment
- **Gemini AI**: Text extraction from receipt images and personalised tips

### Security

- **Firebase Authentication**: User authentication and authorisation
- **CSRF Protection**: Cross-Site Request Forgery protection
- **Form Validation**: Client and server-side validation
- **Environment Variable Security**: Protection of API keys and sensitive data

## 🚀 Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- Docker and Docker Compose
- MongoDB
- Firebase account
- Google Gemini API key

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/budget-tracker.git
   cd budget-tracker
   ```

2. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

3. Create a `.env` file in the frontend directory:

   ```
   REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
   REACT_APP_FIREBASE_PROJECT_ID=your_firebase_project_id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
   REACT_APP_FIREBASE_APP_ID=your_firebase_app_id
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Install backend dependencies:

   ```bash
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the backend directory:

   ```
   MONGODB_URI=your_mongodb_connection_string
   GEMINI_API_KEY=your_gemini_api_key
   JWT_SECRET=your_jwt_secret
   FIREBASE_CREDENTIALS=path_to_firebase_credentials.json
   ```

6. Run the application with Docker Compose:

   ```bash
   cd ..
   docker-compose up
   ```

7. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📐 Architecture

The application follows the Client/Server pattern:

- **Client (Frontend)**: The frontend, built with React.js, serves as the user interface layer. It manages user interactions and communicates with the backend via RESTful API calls to retrieve and send data. State management is handled using the Context API, ensuring a consistent and responsive user experience.

- **Server (Backend)**: The backend, developed with FastAPI, acts as the application server. It processes client requests, executes business logic, and interfaces with the database. The server exposes secure API endpoints for the client to interact with.

- **Database**: MongoDB functions as the database layer, storing user information, receipt data, and categorised expenses. The backend employs MongoDB schemas to enforce data structure and integrity.

- **Communication**: The client and server communicate over HTTP using JSON as the data format. Authentication and authorisation are implemented using Firebase Auth tokens, ensuring secure access to API endpoints and user resources.

- **AI Integration**: The backend integrates with Google Gemini AI to perform receipt text extraction and generate personalised insights. This integration enhances the application's functionality by providing advanced data processing capabilities.

### Directory Structure

```
budget-tracker/
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── context/
│       ├── pages/
│       ├── services/
│       ├── App.jsx
│       ├── index.css
│       └── routes.jsx
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🔒 Security

The application implements several security measures:

- **Authentication**: Firebase Auth for secure user authentication
- **Data Validation**: Input validation at both client and server levels
- **CSRF Protection**: Prevention of cross-site request forgery attacks
- **Secure Endpoints**: Protected API routes requiring authentication
- **Environment Variables**: Sensitive information stored in environment variables
- **File Type Validation**: Verification of image file types before processing

## 📱 Responsive Design

The application is fully responsive, providing an optimal experience across various devices:

- **Mobile**: Navigation via a collapsible sidebar, touch-friendly interfaces
- **Tablet**: Adaptive layout with flexible components
- **Desktop**: Full-featured interface with expanded visualisations

## 👥 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Firebase](https://firebase.google.com/)
- [MongoDB](https://www.mongodb.com/)
- [Google Gemini AI](https://ai.google.dev/)
