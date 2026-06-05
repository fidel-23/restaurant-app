import sqlite3

def get_db():
    conn = sqlite3.connect('restaurant.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Beef Burger', 'Juicy beef burger with lettuce and tomato', 3500, 'Burgers', 'burger.jpg'),
            ('Chicken Burger', 'Crispy chicken with special sauce', 3000, 'Burgers', 'chicken_burger.jpg'),
            ('Margherita Pizza', 'Classic tomato and mozzarella', 5000, 'Pizza', 'pizza.jpg'),
            ('Chicken Pizza', 'Grilled chicken with peppers', 5500, 'Pizza', 'chicken_pizza.jpg'),
            ('Fries', 'Crispy golden french fries', 1500, 'Sides', 'fries.jpg'),
            ('Coleslaw', 'Fresh creamy coleslaw', 1000, 'Sides', 'coleslaw.jpg'),
            ('Coca Cola', 'Chilled 500ml bottle', 800, 'Drinks', 'cola.jpg'),
            ('Fresh Juice', 'Mixed fruit juice', 1200, 'Drinks', 'juice.jpg'),
        ]
        cursor.executemany(
            'INSERT INTO products (name, description, price, category, image) VALUES (?,?,?,?,?)',
            products
        )

    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO admin (username, password) VALUES (?, ?)',
            ('admin', 'quickbite2024')
        )

    conn.commit()
    conn.close()