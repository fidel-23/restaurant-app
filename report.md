# QuickBite Kigali — Project Report

**Course:** EWA408510 – E-Commerce and Web Application  
**Academic Year:** 2025-2026  
**Instructor:** Eric Maniraguha

---

## 1. Introduction

QuickBite Kigali is a modern restaurant ordering platform built for a local food business in Kigali, Rwanda. The platform allows customers to browse a menu, add items to a cart, place orders, and receive confirmation — all from their browser. The system also includes an admin dashboard for monitoring orders and revenue.

---

## 2. Problem Statement

Many local restaurants in Kigali still rely on phone calls or walk-in orders. This limits their reach and makes order management difficult. There is a need for a simple, affordable web platform that allows customers to order food online and helps restaurant owners manage their business digitally.

---

## 3. Objectives

- Build a responsive e-commerce web application for a restaurant
- Allow customers to browse products by category, add items to cart, and place orders
- Provide an admin dashboard with analytics on orders and revenue
- Deploy the application online using Docker and CI/CD
- Implement secure admin authentication

---

## 4. System Features

- Homepage with restaurant branding and navigation
- Menu page with product categories (Burgers, Pizza, Sides, Drinks)
- Product detail page with quantity selector
- Shopping cart with add, remove, and update functionality
- Checkout form with customer details and order summary
- Order confirmation page with full order details
- Admin login with session-based authentication
- Analytics dashboard showing total orders, revenue, and popular items

---

## 5. Technologies Used

| Technology     | Purpose                        |
| -------------- | ------------------------------ |
| Python 3.13    | Backend programming language   |
| Flask          | Web framework                  |
| SQLite         | Database                       |
| HTML/CSS       | Frontend structure and styling |
| JavaScript     | Cart interactivity             |
| Docker         | Containerization               |
| GitHub Actions | CI/CD pipeline                 |
| Render.com     | Live deployment                |

---

## 6. System Architecture

The application follows a three-layer architecture:

- **Frontend:** HTML templates rendered by Flask using Jinja2, styled with CSS
- **Backend:** Flask handles routing, session management, and business logic
- **Database:** SQLite stores products, orders, order items, and admin credentials

User requests flow from the browser → Flask routes → database → back to the browser as rendered HTML pages.

---

## 7. Screenshots

_(Added screenshots of: Homepage, Menu, Cart, Checkout, Confirmation, Admin Dashboard)_

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
- Setting up GitHub Actions to correctly build and test the application

---

## 12. Future Work

- Integrate Mobile Money payment gateway (MTN MoMo or Airtel Money)
- Add real-time order tracking for customers
- Allow restaurant admin to update order status from the dashboard
- Add product image upload functionality
- Build a mobile app version

---

## 13. Conclusion

QuickBite Kigali demonstrates a complete e-commerce web application built with modern tools and best practices. The platform is fully functional, containerized with Docker, tested with CI/CD, and deployed live. It solves a real problem for local businesses in Rwanda by bringing their operations online in a simple and affordable way.
