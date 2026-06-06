# QuickBite Kigali — Project Report

**Course:** EWA408510 – E-Commerce and Web Application  
**Academic Year:** 2025-2026  
**Instructor:** Eric Maniraguha

---

## 1. Introduction

QuickBite Kigali is a modern restaurant ordering platform built for a local food business in Kigali, Rwanda. The platform allows customers to browse a menu, add items to a cart, place orders, and pay securely online. The system also includes a full admin panel for managing orders, tracking inventory, and analyzing business performance.

---

## 2. Problem Statement

Many local restaurants in Kigali still rely on phone calls or walk-in orders. This limits their reach and makes order management difficult. There is a need for a simple, affordable web platform that allows customers to order food online and helps restaurant owners manage their business digitally.

---

## 3. Objectives

- Build a responsive e-commerce web application for a restaurant
- Allow customers to browse products by category, add items to cart, and place orders
- Implement secure online payment using Stripe
- Provide an admin dashboard with analytics, charts, and order management
- Track inventory automatically and allow manual stock updates
- Deploy the application online using Docker and CI/CD

---

## 4. System Features

- Homepage with restaurant branding and navigation
- Mobile responsive design with hamburger menu
- Dark mode toggle
- Menu page with product categories (Burgers, Pizza, Sides, Drinks)
- Real food images on all product cards
- Product detail page with quantity selector
- Shopping cart with add, remove, and update functionality
- Checkout form with customer details and order summary
- Stripe test payment gateway
- Order confirmation page with full order details
- About Us page with contact information
- Customer reviews and star rating system
- 404 error page
- Admin login with session-based authentication
- Enhanced analytics dashboard with bar and doughnut charts
- Order status management (Pending, Preparing, On the Way, Delivered, Paid)
- Inventory tracker with color indicators (Green, Yellow, Red)
- Automatic stock decrease when an order is paid

---

## 5. Technologies Used

| Technology     | Purpose                          |
| -------------- | -------------------------------- |
| Python 3.13    | Backend programming language     |
| Flask          | Web framework                    |
| SQLite         | Database                         |
| HTML/CSS       | Frontend structure and styling   |
| JavaScript     | Cart interactivity and dark mode |
| Chart.js       | Analytics charts on dashboard    |
| Stripe         | Test payment processing          |
| python-dotenv  | Environment variable management  |
| Docker         | Containerization                 |
| GitHub Actions | CI/CD pipeline                   |
| Render.com     | Live deployment                  |

---

## 6. System Architecture

The application follows a three-layer architecture:

- **Frontend:** HTML templates rendered by Flask using Jinja2, styled with CSS and JavaScript
- **Backend:** Flask handles routing, session management, and business logic
- **Database:** SQLite stores products, orders, order items, admin credentials, reviews, and inventory

User requests flow from the browser → Flask routes → database → back to the browser as rendered HTML pages.

---

## 7. Screenshots

_(Add screenshots of: Homepage, Menu, Cart, Checkout, Payment, Confirmation, About Us, Admin Dashboard, Inventory)_

---

## 8. GitHub Repository

https://github.com/fidel-23/restaurant-app

---

## 9. Deployment Link

https://restaurant-app-0oya.onrender.com

---

## 10. CI/CD Description

The project uses GitHub Actions for CI/CD. Every time code is pushed to the `main` branch, the pipeline automatically:

1. Checks out the code
2. Sets up Python 3.13
3. Installs all dependencies
4. Tests that the app loads successfully
5. Builds the Docker image

This ensures that broken code is never deployed without being tested first.

---

## 11. Challenges Encountered

- Configuring Docker to bind to `0.0.0.0` instead of `127.0.0.1` so the app was accessible outside the container
- Managing Flask sessions for the shopping cart across multiple pages
- Fixing ID type mismatches between integers and strings in cart operations
- Setting up Stripe environment variables securely on Render
- Making the app fully responsive on mobile devices

---

## 12. Future Work

- Integrate Mobile Money payment gateway (MTN MoMo or Airtel Money)
- Add real-time order tracking for customers
- Allow restaurant admin to update product details and add new menu items
- Add product image upload functionality
- Build a mobile app version
- Add email notifications for order confirmation

---

## 13. Conclusion

QuickBite Kigali demonstrates a complete e-commerce web application built with modern tools and best practices. The platform is fully functional, containerized with Docker, tested with CI/CD, and deployed live. It solves a real problem for local businesses in Rwanda by bringing their operations online in a simple and affordable way.
