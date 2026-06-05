from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, seed_db, get_db

app = Flask(__name__)
app.secret_key = 'quickbite-secret-key'

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()

# ─── CUSTOMER ROUTES ───────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    conn = get_db()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    categories = {}
    for product in products:
        cat = product['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(product)
    return render_template('menu.html', categories=categories)

@app.route('/product/<int:id>')
def product(id):
    conn = get_db()
    item = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('product.html', product=item)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        cart = session.get('cart', [])
        if not cart:
            return redirect(url_for('menu'))

        customer_name = request.form['name']
        customer_phone = request.form['phone']
        customer_address = request.form['address']
        total = sum(item['price'] * item['quantity'] for item in cart)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO orders (customer_name, customer_phone, customer_address, total) VALUES (?,?,?,?)',
            (customer_name, customer_phone, customer_address, total)
        )
        order_id = cursor.lastrowid

        for item in cart:
            cursor.execute(
                'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)',
                (order_id, item['id'], item['quantity'], item['price'])
            )

        conn.commit()
        conn.close()
        session['cart'] = []
        return redirect(url_for('confirmation', order_id=order_id))

    return render_template('checkout.html')

@app.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = conn.execute('''
        SELECT p.name, oi.quantity, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    conn.close()
    return render_template('confirmation.html', order=order, items=items)

# ─── CART API ───────────────────────────────────────────────

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == data['id']:
            item['quantity'] += 1
            session['cart'] = cart
            return jsonify({'success': True, 'cart': cart})
    cart.append({'id': data['id'], 'name': data['name'], 'price': data['price'], 'quantity': 1})
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != data['id']]
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == data['id']:
            item['quantity'] = data['quantity']
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', [])
    return jsonify({'cart': cart})

# ─── ADMIN ROUTES ───────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        admin = conn.execute(
            'SELECT * FROM admin WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()
        if admin:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_revenue = conn.execute('SELECT SUM(total) FROM orders').fetchone()[0] or 0
    recent_orders = conn.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT 10').fetchall()
    popular_items = conn.execute('''
        SELECT p.name, SUM(oi.quantity) as total_sold
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sold DESC
        LIMIT 5
    ''').fetchall()
    conn.close()
    return render_template('admin/dashboard.html',
        total_orders=total_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        popular_items=popular_items
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)