# QuickBite Kigali — Project Report

**Course:** EWA408510 – E-Commerce and Web Application  
**Academic Year:** 2025-2026  
**Instructor:** Eric Maniraguha  
**Student:** Fidel K. Worjloh  
**Institution:** University of Lay Adventists of Kigali (UNILAK)

---

## 1. Introduction

QuickBite Kigali is a modern, fully functional restaurant ordering platform designed and developed for a local food business in Kigali, Rwanda. The platform enables customers to create accounts, browse a categorized and searchable menu, add items to a shopping cart, place orders, pay securely online, track their orders in real time, and get instant answers through a built-in chatbot. The system also features a complete admin panel for managing orders, products, inventory, and analyzing business performance through real-time charts, advanced reports, and exportable data.

The application was built using Python and Flask as the backend framework, PostgreSQL (hosted on Supabase) as the database, and HTML, CSS, and JavaScript for the frontend. It uses a custom "Emerald & Cream" visual identity, pairing deep emerald green with antique gold and a serif/sans-serif font pairing, to give the platform a premium, professional feel suitable for commercial use. The application is fully containerized using Docker, tested through a CI/CD pipeline powered by GitHub Actions, and deployed live on Render.com. The architecture is designed to be multi-tenant ready, allowing the platform to scale to support multiple restaurants in the future.

---

## 2. Problem Statement

Many local restaurants in Kigali still rely on phone calls, walk-in orders, or informal messaging to receive customer orders. This approach limits their reach, makes order management difficult, and provides no visibility into business performance or customer behavior. There is a clear need for a simple, affordable, and professional web platform that allows customers to order food online, track their orders, get quick answers to common questions, and build loyalty with the restaurant, while giving restaurant owners full control and insight into their operations digitally.

---

## 3. Objectives

- Design and develop a responsive e-commerce web application for a restaurant, with a polished, professional visual identity
- Allow customers to create accounts, browse products by category, search and filter the menu, add items to cart, and place orders
- Implement a secure online payment system using Stripe
- Provide customers with real-time order tracking, email notifications, and a self-service chatbot for common questions
- Build an admin dashboard with analytics, charts, advanced reporting, order management, and inventory tracking
- Secure the application and admin access with industry-standard practices, including hashed credentials and disabled debug mode in production
- Automatically decrease inventory stock when an order is paid
- Design a multi-tenant database architecture to support future expansion to multiple restaurants
- Containerize the application with Docker and deploy it live using CI/CD

---

## 4. System Features

### Customer-Facing Features

- Homepage with hero section, feature highlights, and call-to-action
- Responsive navigation with hamburger menu for mobile devices
- Light/Dark mode toggle with an animated sliding sun-and-moon switch
- Custom "Emerald & Cream" color identity with Playfair Display and Inter typography
- Customer accounts: registration, login, logout, and profile page
- Form validation with real-time feedback (email format, password strength, phone format)
- Guest checkout with automatic linking of guest orders to a new account upon registration
- Menu page with categories, real food images, search bar, category filters, and price range filter
- Product detail page with quantity selector and toast notification on add to cart
- Shopping cart with add, remove, increase, and decrease quantity functionality
- Checkout form with auto-filled customer details for logged-in users
- Stripe test payment gateway integration
- Order confirmation page with full order details
- Real-time order tracking with a visual progress bar (Pending → Preparing → On the Way → Delivered)
- Order history and one-click reorder from the profile page
- Email notifications for order confirmation and order status updates
- A built-in chatbot that answers questions about hours, location, delivery, payment, account help, and menu items; checks order status by number; recommends popular items; and performs typo-tolerant menu item price lookups using fuzzy text matching
- Forgot password and reset password flow
- About Us page with restaurant story and contact information
- Customer review and star rating system, accessible from both the About page and customer profile
- Custom 404 error page

### Admin Features

- Secure admin login with session-based authentication and bcrypt-hashed credentials
- Self-service password change from an admin Settings page
- Analytics dashboard with total orders, revenue, customers, average order value, and charts (bar chart of popular items, doughnut chart of revenue by category)
- Advanced analytics page with time-frame filters (today, this week, this month, all time, and custom date range)
- Top customers report and top-selling items report
- Detailed order table showing customer, items ordered, total, status, and timestamp
- CSV export of orders for any selected time period
- Order management with status updates (Pending, Preparing, On the Way, Delivered, Paid), which trigger customer email notifications
- Chat log review page, showing questions the chatbot could not answer so responses can be improved over time
- Inventory tracker with color indicators (green/yellow/red) and manual stock updates
- Automatic stock decrease when an order is paid
- Full product management: add, edit, and delete menu items directly from the dashboard

---

## 5. Technologies Used

| Technology                             | Purpose                                                                                               |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Python 3.13                            | Backend programming language                                                                          |
| Flask                                  | Web framework                                                                                         |
| PostgreSQL (Supabase)                  | Persistent, cloud-hosted database                                                                     |
| psycopg2                               | PostgreSQL database driver                                                                            |
| pg_trgm                                | PostgreSQL extension for fuzzy text matching, used in chatbot typo tolerance                          |
| bcrypt                                 | Secure password hashing for customers and admin                                                       |
| HTML/CSS                               | Frontend structure and styling                                                                        |
| Google Fonts (Playfair Display, Inter) | Typography for the brand identity                                                                     |
| JavaScript                             | Cart interactivity, dark mode, hamburger menu, live order tracking, menu search/filter, chatbot logic |
| Chart.js                               | Analytics charts on admin dashboard                                                                   |
| Stripe                                 | Test payment processing                                                                               |
| SendGrid                               | Transactional email notifications                                                                     |
| python-dotenv                          | Secure environment variable management                                                                |
| Docker                                 | Application containerization                                                                          |
| GitHub Actions                         | CI/CD pipeline                                                                                        |
| Render.com                             | Live cloud deployment                                                                                 |

---

## 6. System Architecture

The application follows a three-layer architecture:

- **Frontend:** HTML templates rendered by Flask using the Jinja2 templating engine, styled with a custom Emerald & Cream theme, and made interactive with JavaScript (cart management, live order tracking via polling, menu search and filtering, dark/light mode, chatbot interface)
- **Backend:** Flask handles all routing, session management, authentication, cart logic, payment processing, email notifications, chatbot logic, and admin functionality
- **Database:** PostgreSQL (hosted on Supabase) stores all application data, designed with multi-tenancy in mind via a `restaurant_id` column on relevant tables

**Request Flow:**  
Browser → Flask Route → Database Query (Supabase PostgreSQL) → Jinja2 Template → Rendered HTML → Browser

**Real-Time Tracking Flow:**  
Browser polls `/api/order/<id>/status` every 3 seconds → Flask queries the database → Returns current status as JSON → JavaScript updates the progress bar live

**Chatbot Flow:**  
User message → JavaScript keyword-matching engine → either an instant local response, or a call to a dedicated Flask API endpoint (order status, item search, or popular items) → Database query → JSON response rendered as a chat bubble. Unrecognized messages are logged to the database for admin review.

---

## 7. Database Structure

| Table           | Purpose                                                                                             |
| --------------- | --------------------------------------------------------------------------------------------------- |
| restaurants     | Stores restaurant information (multi-tenant ready)                                                  |
| customers       | Stores customer accounts with hashed passwords                                                      |
| products        | Stores menu items with name, description, price, category, image, and stock, linked to a restaurant |
| orders          | Stores customer orders, linked to both a restaurant and a customer (if registered)                  |
| order_items     | Links orders to products with quantity and price                                                    |
| admin           | Stores admin credentials (bcrypt-hashed), linked to a restaurant                                    |
| reviews         | Stores customer feedback and star ratings                                                           |
| password_resets | Stores secure tokens for password reset requests                                                    |
| chat_logs       | Stores chatbot questions that could not be automatically answered, for admin review                 |

---

## 8. Screenshots

_(Add screenshots of: Homepage, Menu with search/filter, Product Detail, Cart, Checkout, Payment, Confirmation, Order Tracking, Customer Profile, About Us, Chatbot widget, Admin Dashboard, Admin Analytics, Admin Settings, Inventory Tracker, Product Management)_

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
docker build -t restaurant-app .

docker run -p 5000:5000 restaurant-app

---

## 14. Challenges Encountered

- Configuring Docker to bind to `0.0.0.0` instead of `127.0.0.1` so the app was accessible outside the container
- Managing Flask sessions for the shopping cart and resolving ID type mismatches between integers and strings
- Migrating from SQLite to PostgreSQL to solve Render's free-tier data persistence issue, including resolving an IPv6/IPv4 connectivity mismatch by switching to Supabase's session pooler connection string
- Restructuring the database schema for multi-tenant readiness without breaking existing functionality
- Setting up Stripe and SendGrid securely within Render's free-tier environment variable limits, by hardcoding non-sensitive values and using Render's automatically-provided variables where possible
- Implementing real-time order tracking using polling after discovering Server-Sent Events were unreliable on Render's free tier
- Fixing PostgreSQL's non-deterministic row ordering, which caused the menu category order to change unexpectedly
- Diagnosing a CSS specificity conflict where a more specific navigation-link rule silently overrode a button's intended text color, making it unreadable
- Diagnosing a missing closing HTML tag that caused two dashboard sections to visually overlap instead of stacking correctly
- Identifying that custom-built UI markup (a sliding theme toggle) was being overwritten by leftover JavaScript from an earlier version of the feature
- Securing the application for production use by hashing the admin password with bcrypt and disabling Flask's debug mode automatically in the live environment
- Building a rule-based chatbot with typo-tolerant item search using PostgreSQL's fuzzy matching extension
- Making the application fully responsive on mobile devices, including a hamburger navigation menu

---

## 15. Future Work

- Integrate Mobile Money payment gateway (MTN MoMo or Airtel Money) for local customers
- Upgrade the chatbot from rule-based keyword matching to an AI-powered conversational model
- Migrate the admin panel navigation to a left sidebar layout for improved scalability as features are added
- Implement multi-language support (English, Kinyarwanda, French)
- Add SMS notifications for order updates
- Build a dedicated mobile application or Progressive Web App (PWA)
- Evolve the platform into a full multi-tenant SaaS product for multiple restaurants

---

## 16. Conclusion

QuickBite Kigali is a complete, production-ready e-commerce web application built from scratch using modern tools and best practices. The platform solves a real problem for local restaurants in Rwanda by bringing their operations online in a simple, affordable, and professional way. Every requirement of the project brief has been met and substantially exceeded — including customer accounts, real-time order tracking, email notifications, a self-service chatbot, advanced analytics, a persistent cloud database, a polished custom visual identity, hardened security practices, responsive UI, shopping cart, checkout, payment, GitHub version control, Docker containerization, CI/CD pipeline, and live deployment.

The project demonstrates not just technical implementation but also business thinking — from inventory management to customer analytics to multi-tenant architecture to production security — making it a strong foundation for a real SaaS product that could be offered to restaurants across Rwanda and beyond.
