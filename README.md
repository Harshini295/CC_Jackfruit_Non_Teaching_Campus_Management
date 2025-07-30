# 🏫 Campus Non-Teaching Staff Management System

A comprehensive Flask web application built to digitize and automate the administrative workflows surrounding non-teaching staff, contractors, and canteen services within a campus or institutional setting. It streamlines staff tracking, contractor management, inventory monitoring, order processing, and performance reporting — all through a centralized admin dashboard.

---

## 🚀 Key Features

### 🔐 Admin Authentication
- Secure login with password hashing using Werkzeug.
- Session-based access control to restrict unauthorized access.
- Flash messages for login/logout feedback.

### 👷 Contractor Management
- Add, view, update, and delete contractor profiles.
- Upload and track contractor documents.
- Analyze performance based on feedback and contract history.

### 📑 Contract Lifecycle Management
- Create and manage contracts with expiry dates.
- Filter active/expired contracts and send renewal alerts.
- Associate contracts with specific contractors and staff.

### 👥 Staff Management
- Manage canteen and supporting staff records.
- Filter by role, department, or assigned contractor.
- Monitor active vs inactive staff.

### 🍽️ Menu & Food Items
- Add or update menu items with availability status.
- Control prices, quantities, and categorization (breakfast, lunch, etc.).
- Expose menu via public API.

### 🧾 Order Processing
- Allow staff to create daily food orders.
- Automatically update inventory on every order.
- Show order summary and statistics by date range.

### 📦 Inventory Management
- Maintain stock levels of ingredients and resources.
- Set alert thresholds for low stock.
- Monitor usage patterns and restocking needs.

### 📊 Contractor Feedback System
- Submit and track feedback against contractors.
- Calculate and visualize average ratings.
- Identify top and low-performing contractors.

### 📈 Analytics & Reporting
- Visual sales reports using Matplotlib (daily, weekly, monthly).
- Contractor performance dashboards.
- Downloadable or export-ready data tables.

---

## ⚙️ Technology Stack

- **Backend**: Python 3.8+, Flask (microservice architecture)
- **Databases**:
  - MySQL (canteen service)
  - SQLite (hostel service)
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, JavaScript, Jinja2
- **Libraries**: Flask-MySQLdb, MySQL Connector/Python, ConfigParser, Pandas, Matplotlib, Werkzeug
- **DevOps**: Docker, Docker Compose
- **Tools**: Git for version control, pip for dependency management

---

## 🧠 System Architecture & Technical Overview

The system is composed of **two modular Flask microservices**:

-  **Contracts and Canteen Service** (`localhost:5000`): Manages contractors, staff, inventory, orders, menu, feedback, and sales analytics.
-  **Hostel Service** (`localhost:5001`): Handles weekly meal planning and meal-time management using a lightweight SQLite database.

Both services are fully containerized using **Docker** and **Docker Compose**, enabling independent development and deployment. You can run services either individually or together.

- Services are configured via a `config.ini` file.
- Exposed APIs support integration with third-party systems or future extensions.
---



