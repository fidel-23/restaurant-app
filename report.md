# QuickBite Kigali — Project Report

**Course:** EWA408510 – E-Commerce and Web Application  
**Academic Year:** 2025-2026  
**Instructor:** Eric Maniraguha  
**Student:** Fidel K. Worjloh  
**Institution:** University of Lay Adventists of Kigali (UNILAK)

---

## 1. Introduction

QuickBite Kigali is a modern, fully functional restaurant ordering platform designed and developed for a local food business in Kigali, Rwanda. The platform enables customers to browse a categorized menu, add items to a shopping cart, place orders, and pay securely online. The system also features a complete admin panel for managing orders, tracking inventory, and analyzing business performance through real-time charts and statistics.

The application was built using Python and Flask as the backend framework, SQLite as the database, and plain HTML, CSS, and JavaScript for the frontend. It is fully containerized using Docker, tested through a CI/CD pipeline powered by GitHub Actions, and deployed live on Render.com.

---

## 2. Problem Statement

Many local restaurants in Kigali still rely on phone calls, walk-in orders, or informal messaging to receive customer orders. This approach limits their reach, makes order management difficult, and provides no visibility into business performance. There is a clear need for a simple, affordable, and professional web platform that allows customers to order food online while giving restaurant owners full control of their operations digitally.

---

## 3. Objectives

- Design and develop a responsive e-commerce web application for a restaurant
- Allow customers to browse products by category, view product details, add items to cart, and place orders
- Implement a secure online payment system using Stripe
- Build an admin dashboard with analytics, charts, order management, and inventory tracking
- Automatically decrease inventory stock when an order is paid
- Containerize the application with Docker and deploy it live using CI/CD

---

## 4. System Features

### Customer-Facing Features
- Homepage with hero section, feature highlights, and call-to-action
- Responsive navigation with hamburger menu for mobile devices
- Light/Dark mode toggle
- Menu page with product categories: Burgers, Pizza, Sides, Drinks
- Real food images on all product cards
- Product detail page with quantity selector and toast notification on add to cart
- Shopping cart with add, remove, increase, and decrease quantity functionality
- Checkout form with customer name, phone number, and delivery address
- Order summary displayed at checkout
- Stripe test payment gateway integration
- Order confirmation page with full order details
- About Us page with restaurant story and contact information
- Customer review and star rating system
- Custom 404 error page

### Admin Features
- Secure admin login with session-based authentication
- Analytics dashboard with:
  - Total orders counter
  - Total revenue
  - Total customers
  - Average order value
  - Bar chart of popular items
  - Doughnut chart of revenue by category
- Order management with status updates (Pending, Preparing, On the Way, Delivered, Paid)
- Inventory tracker with color indicators:
  - 🟢 Green: In Stock (50–100%)
  - 🟡 Yellow: Running Low (20–49%)
  - 🔴 Red: Out of Stock (0–19%)
- Automatic stock decrease when an order is paid
- Manual stock update per product

---

## 5. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend programming language |
| Flask | Web framework |
| SQLite | Database |
| HTML/CSS | Frontend structure and styling |
| JavaScript | Cart interactivity, dark mode, hamburger menu |
| Chart.js | Analytics charts on admin dashboard |
| Stripe | Test payment processing |
| python-dotenv | Secure environment variable management |
| Docker | Application containerization |
| GitHub Actions | CI/CD pipeline |
| Render.com | Live cloud deployment |

---

## 6. System Architecture

The application follows a three-layer architecture:

- **Frontend:** HTML templates rendered by Flask using the Jinja2 templating engine, styled with custom CSS using a dark navy color palette, and made interactive with JavaScript
- **Backend:** Flask handles all routing, session management, cart logic, payment processing, and admin functionality
- **Database:** SQLite stores all application data across five tables: products, orders, order_items, admin, and reviews

**Request Flow:**  
Browser → Flask Route → Database Query → Jinja2 Template → Rendered HTML → Browser

---

## 7. Database Structure

| Table | Purpose |
|---|---|
| products | Stores menu items with name, description, price, category, image, and stock |
| orders | Stores customer orders with name, phone, address, total, and status |
| order_items | Links orders to products with quantity and price |
| admin | Stores admin credentials |
| reviews | Stores customer feedback and star ratings |

---

## 8. Screenshots

*(Screenshots of: Homepage, Menu, Product Detail, Cart, Checkout, Payment, Confirmation, About Us, Admin Dashboard, Inventory Tracker)*

---

## 9. GitHub Repository

https://github.com/fidel-23/restaurant-app

---

## 10. Deployment Link

https://restaurant-app-0oya.onrender.com

---

## 11. Admin Panel

https://restaurant-app-0oya.onrender.com/admin/login

---

## 12. CI/CD Description

The project uses GitHub Actions for continuous integration and deployment. The pipeline is defined in `.github/workflows/deploy.yml` and triggers automatically on every push to the `main` branch.

**Pipeline Steps:**
1. Check out the source code
2. Set up Python 3.13
3. Install all project dependencies from `requirements.txt`
4. Test that the Flask application loads successfully
5. Build the Docker image to verify containerization

This ensures that every code change is automatically tested and verified before it reaches the live server, preventing broken deployments.

---

## 13. Docker

The application is fully containerized using Docker. The `Dockerfile` defines the build process and the `docker-compose.yml` manages the service configuration.

**To run locally with Docker:**
---

## 14. Challenges Encountered

- Configuring Docker to bind to `0.0.0.0` instead of `127.0.0.1` so the app was accessible outside the container
- Managing Flask sessions for the shopping cart and resolving ID type mismatches between integers and strings
- Setting up Stripe environment variables securely on Render without exposing secret keys in the codebase
- Making the application fully responsive on mobile devices
- Fixing dynamically rendered cart buttons that lost their event listeners after re-rendering

---

## 15. Future Work

- Integrate Mobile Money payment gateway (MTN MoMo or Airtel Money) for local customers
- Add real-time order tracking so customers can follow their delivery
- Allow admin to add, edit, and delete menu items directly from the dashboard
- Add email or SMS notifications for order confirmation
- Build a dedicated mobile application
- Implement multi-language support (English, Kinyarwanda, French)

---

## 16. Conclusion

QuickBite Kigali is a complete, production-ready e-commerce web application built from scratch using modern tools and best practices. The platform solves a real problem for local restaurants in Rwanda by bringing their operations online in a simple, affordable, and professional way. Every requirement of the project brief has been met — including responsive UI, database integration, shopping cart, checkout, payment, GitHub version control, Docker containerization, CI/CD pipeline, and live deployment.

The project demonstrates not just technical implementation but also business thinking — from inventory management to analytics — making it a foundation that could realistically be used by a real restaurant in Kigali.
