# Budget-Tracker

## Introduction

Budget-Tracker is a web application that helps users upload or scan receipts, automatically parse each line item via AI, and allocate costs either entirely or shared with other participants. It tallies individual totals and visualizes spending trends with weekly, monthly, and yearly graphs, and offers personalized saving tips powered by Gemini AI.

## Features

- **Receipt Scanning & Parsing**  
  Upload images or scan receipts; AI extracts item names, quantities, and prices.
- **Cost Allocation**  
  Drag-and-drop items to assign expenses to individuals or mark full-amount bearers.
- **Spending Analytics**  
  Interactive charts for weekly, monthly, and annual spending breakdowns.
- **Saving Tips & Tricks**  
  AI-driven suggestions to optimize budgets based on spending patterns.
- **Item Categorization**  
  Automatic grouping into clothing, food, recreation, utilities, and more.
- **User Authentication**  
  Secure sign-up and sign-in via Firebase Auth.
- **Responsive Design**  
  Mobile-first layout with modern animations and gradient palettes.

## Technology Stack

- **AI**: Google Gemini for OCR and natural-language saving tips
- **Backend**: FastAPI with custom middleware for authentication, validation, and AI integration
- **Database**: MongoDB for flexible, document-oriented storage
- **Authentication**: Firebase Auth for end-to-end user identity management
- **Frontend**: React.js with Tailwind CSS for utility-first styling
- **Containerization**: Docker & Docker Compose
- **Environment Configuration**: Secure `.env` via Docker secrets or CI/CD vaults

## Architecture

This project follows the **MVC** pattern:

- **Models**: Pydantic schemas and MongoDB collections
- **Views**: React components and Tailwind-styled pages
- **Controllers**: FastAPI routers handling business logic and AI integration

## Installation

### Prerequisites

- Docker & Docker Compose
- Git CLI

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Budget-Tracker.git
   cd Budget-Tracker
   ```
