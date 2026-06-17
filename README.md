# 🍔 QuickBite Kigali

A modern, full-stack restaurant ordering platform built for local businesses in Kigali, Rwanda. Customers can browse the menu, create accounts, order food, pay online, track their delivery in real time, and chat with an AI-free assistant for instant answers. Restaurant admins get a complete dashboard with analytics, inventory management, and order control.

**Live Site:** [restaurant-app-0oya.onrender.com](https://restaurant-app-0oya.onrender.com)

---

## ✨ Features

### For Customers

- 🔐 Account registration, login, and profile with order history
- 🔍 Searchable and filterable menu (by category and price)
- 🛒 Shopping cart with live updates
- 💳 Secure checkout with Stripe payment (test mode)
- 📦 Real-time order tracking with visual progress bar
- 📧 Email notifications for order confirmation and status updates
- 💬 Built-in chatbot for FAQs, order tracking, item prices, and popular picks — with typo-tolerant search
- ⭐ Customer reviews and star ratings
- 🌙 Light / Dark mode with an animated sun-moon toggle switch
- 📱 Fully responsive with mobile hamburger menu

### For Admins

- 📊 Analytics dashboard with charts (Chart.js)
- 📈 Advanced reports with custom date ranges and CSV export
- 🏆 Top customers and top-selling items reports
- 📦 Inventory tracker with color-coded stock levels
- 🍽️ Full product management (add, edit, delete menu items)
- 📋 Order status management with automatic customer notifications
- 💬 Chat log review for questions the chatbot couldn't answer
- ⚙️ Self-service password change, with bcrypt-hashed credentials

---

## 🛠️ Tech Stack

| Layer            | Technology            |
| ---------------- | --------------------- |
| Backend          | Python, Flask         |
| Database         | PostgreSQL (Supabase) |
| Frontend         | HTML, CSS, JavaScript |
| Charts           | Chart.js              |
| Payments         | Stripe                |
| Email            | SendGrid              |
| Containerization | Docker                |
| CI/CD            | GitHub Actions        |
| Hosting          | Render                |

---

## 🎨 Design

QuickBite uses a custom "Emerald & Cream" visual identity — deep emerald green paired with warm antique gold, set in Playfair Display (headings) and Inter (body text). The palette and fonts are controlled centrally through CSS variables in `static/css/style.css`, so the entire site's look can be restyled from one place.

---

## 🚀 Running Locally

```bash
# Clone the repository
git clone https://github.com/fidel-23/restaurant-app.git
cd restaurant-app

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create a .env file with:
# DATABASE_URL=your_postgresql_connection_string
# STRIPE_SECRET_KEY=your_stripe_secret_key
# SENDGRID_API_KEY=your_sendgrid_api_key

# Run the app
python app.py
```

Visit `http://127.0.0.1:5000`

---

## 🐳 Running with Docker

```bash
docker build -t restaurant-app .
docker run -p 5000:5000 restaurant-app
```

---

## 📁 Project Structure

restaurant-app/

├── app.py # Main Flask application

├── database.py # Database connection and schema

├── email_service.py # Email notification logic

├── Dockerfile

├── docker-compose.yml

├── requirements.txt

├── .github/workflows/ # CI/CD pipeline

├── templates/ # HTML pages

│ ├── chat_widget.html # Chatbot UI, included on every page

│ └── admin/ # Admin panel pages

└── static/

├── css/ # Styling, including chatbot.css

└── js/ # Cart, dark mode, tracking, chatbot logic

---

## 🔑 Admin Access

URL: /admin/login
Credentials are set during initial database seeding and can be changed any time from **Admin → Settings** once logged in.

---

## 📄 License

Built as a final examination project for EWA408510 — E-Commerce and Web Application, University of Lay Adventists of Kigali (UNILAK).

---

## 👤 Author

**Fidel K. Worjloh**  
Management Information Systems Student, UNILAK
