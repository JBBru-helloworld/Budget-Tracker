# Budget Tracker - Setup and Troubleshooting Guide

## Quick Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.11+ (for local development)
- Firebase project with Authentication enabled
- Google Gemini API key
- MongoDB (or use Docker MongoDB service)

### 0. Docker Setup (First Time Users)

#### Install Docker Desktop

If you don't have Docker installed:

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Install the downloaded `.dmg` file
3. Launch Docker Desktop from Applications folder

#### Start Docker Desktop

Before running any Docker commands, make sure Docker Desktop is running:

1. **Open Docker Desktop** from Applications or Spotlight search
2. **Wait for Docker to start** - you'll see the Docker whale icon in your menu bar
3. **Verify Docker is running** with these commands:

```bash
docker --version
docker-compose --version
```

#### Common Docker Issues on macOS

- **Error: "Cannot connect to Docker daemon"** → Docker Desktop isn't running
- **Solution:** Open Docker Desktop app and wait for it to fully start
- **Check status:** Look for the Docker whale icon in your menu bar (should be solid, not animated)

### 1. Environment Variables Setup

#### Root directory (.env)

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

#### Frontend (.env)

Copy `frontend/.env.example` to `frontend/.env` and fill in your values:

```bash
cp frontend/.env.example frontend/.env
```

#### Backend (.env)

Copy `backend/.env.example` to `backend/.env` and fill in your values:

```bash
cp backend/.env.example backend/.env
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Recent Fixes Applied

### Backend Fixes

1. ✅ **Added missing scan_controller** - Created scan controller for receipt processing
2. ✅ **Fixed main.py API routing** - Added main API router to include all endpoints
3. ✅ **Updated Firebase token handling** - Improved token verification to return user data
4. ✅ **Fixed authentication dependencies** - Created proper dependency functions
5. ✅ **Added missing imports** - Fixed datetime and other missing imports
6. ✅ **Added ProcessedReceiptResponse model** - Required for scan controller

### Frontend Fixes

1. ✅ **Updated Dockerfile environment variables** - Added all required Firebase variables
2. ✅ **Verified all page components exist** - All routes in App.jsx have corresponding files
3. ✅ **Verified service files exist** - API service and Firebase config are properly set up

### Docker Fixes

1. ✅ **Updated docker-compose.yml** - Added frontend Firebase environment variables
2. ✅ **Created comprehensive environment examples** - Added .env.example files

### Configuration Fixes

1. ✅ **Fixed CORS settings** - Updated allowed origins
2. ✅ **Standardized environment variable names** - Consistent naming across services
3. ✅ **Added proper error handling** - Authentication and API error handling

## API Endpoints Structure

### Authentication (`/api/auth`)

- POST `/register` - Register new user
- GET `/me` - Get current user profile
- PUT `/profile` - Update user profile

### Receipts (`/api/receipts`)

- POST `/scan` - Scan receipt image
- POST `/` - Create receipt
- GET `/` - List user receipts
- GET `/{id}` - Get receipt details
- PUT `/{id}` - Update receipt
- DELETE `/{id}` - Delete receipt

### Categories (`/api/categories`)

- GET `/` - List categories
- POST `/` - Create category
- PUT `/{id}` - Update category
- DELETE `/{id}` - Delete category

### Analytics (`/api/analytics`)

- GET `/overview` - Spending overview
- GET `/trends` - Spending trends
- GET `/categories` - Category breakdown

### Tips (`/api/tips`)

- GET `/` - Get money-saving tips
- POST `/generate` - Generate personalized tips

### Notifications (`/api/notifications`)

- GET `/` - List notifications
- GET `/count` - Unread count
- PUT `/{id}/read` - Mark as read
- PUT `/read-all` - Mark all as read

## Troubleshooting

### Common Issues

1. **Firebase Authentication Error**

   - Verify all Firebase environment variables are set correctly
   - Check Firebase project settings and service account key
   - Ensure Firebase Authentication is enabled in Firebase Console

2. **MongoDB Connection Error**

   - If using Docker: `docker-compose down && docker-compose up -d mongodb`
   - Check MongoDB URI format in environment variables
   - Verify MongoDB service is running

3. **Gemini API Error**

   - Verify GEMINI_API_KEY is set correctly
   - Check API key permissions in Google AI Studio
   - Ensure billing is enabled for your Google Cloud project

4. **CORS Errors**

   - Verify frontend URL is in CORS_ORIGINS in backend settings
   - Check API_URL environment variable in frontend

5. **Docker Build Issues**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild with no cache: `docker-compose build --no-cache`

### Development Mode

To run services individually for development:

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### MongoDB (if not using Docker)

```bash
mongod --dbpath /path/to/your/db
```

## File Structure Verification

All critical files are in place:

- ✅ Controllers: auth, receipts, categories, analytics, tips, settings, user_profile, scan
- ✅ Models: user, receipt, category, notifications, tip, settings
- ✅ Services: firebase, user, receipt, category, analytics, tip, storage, ai, ocr, notification
- ✅ Routes: auth, receipts, categories, notifications, analytics, tips
- ✅ Frontend pages: Dashboard, Login, Register, Profile, Categories, Receipts, ScanReceipt, ReceiptDetail
- ✅ Context: AuthContext, NotificationContext
- ✅ Components: Layout, Sidebar, ProtectedRoute, NotificationIcon

The application should now work correctly with all endpoints functional and proper error handling in place.
