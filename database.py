import bcrypt
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = 'postgresql://postgres.yrbvkavnqqyjpmuqyyns:Quickbite2024@aws-0-eu-west-3.pooler.supabase.com:5432/postgres'


def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(id),
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image TEXT,
            stock INTEGER DEFAULT 100
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(id),
            customer_id INTEGER REFERENCES customers(id),
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER,
            price REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(id),
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(id),
            customer_id INTEGER REFERENCES customers(id),
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(id),
            message TEXT NOT NULL,
            resolved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )     ''')
    conn.commit()
    conn.close()

def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM restaurants")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO restaurants (name, description, address, phone, email) VALUES (%s,%s,%s,%s,%s)',
            ('QuickBite Kigali', 'Fresh food, fast delivery, right to your door.', 'KK 318 St, Kigali, Rwanda', '+250 788 123 456', 'info@quickbitekigali.com')
        )

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Beef Burger', 'Juicy beef burger with lettuce and tomato', 3500, 'Burgers', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 100),
            ('Chicken Burger', 'Crispy chicken with special sauce', 3000, 'Burgers', 'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400', 100),
            ('Veggie Burger', 'Fresh vegetable patty with avocado', 2500, 'Burgers', 'https://images.unsplash.com/photo-1520072959219-c595dc870360?w=400', 100),
            ('Double Smash Burger', 'Double beef patty with cheese and pickles', 4500, 'Burgers', 'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400', 100),
            ('Margherita Pizza', 'Classic tomato and mozzarella', 5000, 'Pizza', 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400', 100),
            ('Chicken Pizza', 'Grilled chicken with peppers', 5500, 'Pizza', 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', 100),
            ('Pepperoni Pizza', 'Loaded with pepperoni and cheese', 6000, 'Pizza', 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400', 100),
            ('BBQ Pizza', 'Smoky BBQ sauce with beef and onions', 6500, 'Pizza', 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400', 100),
            ('Fries', 'Crispy golden french fries', 1500, 'Sides', 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400', 100),
            ('Coleslaw', 'Fresh creamy coleslaw', 1000, 'Sides', 'https://images.unsplash.com/photo-1625938144755-652e08e359b7?w=400', 100),
            ('Onion Rings', 'Crispy battered onion rings', 1800, 'Sides', 'https://images.unsplash.com/photo-1639024471283-03518883512d?w=400', 100),
            ('Chicken Wings', '6 pieces spicy chicken wings', 3000, 'Sides', 'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400', 100),
            ('Grilled Tilapia', 'Fresh grilled tilapia with lemon butter sauce and vegetables', 4500, 'Sides', 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400', 50),
            ('Coca Cola', 'Chilled 500ml bottle', 800, 'Drinks', 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400', 100),
            ('Fresh Juice', 'Mixed fruit juice', 1200, 'Drinks', 'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400', 100),
            ('Mineral Water', '500ml chilled water', 500, 'Drinks', 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400', 100),
            ('Mango Smoothie', 'Fresh blended mango smoothie', 1500, 'Drinks', 'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400', 100),
        ]
        for p in products:
            cursor.execute(
                'INSERT INTO products (restaurant_id, name, description, price, category, image, stock) VALUES (1,%s,%s,%s,%s,%s,%s)',
                p
            )

    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        hashed_admin_password = bcrypt.hashpw('quickbite2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            'INSERT INTO admin (restaurant_id, username, password) VALUES (1, %s, %s)',
            ('admin', hashed_admin_password)
        )

    conn.commit()
    conn.close()