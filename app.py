from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, seed_db, get_db
from dotenv import load_dotenv
import stripe
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'quickbite-secret-key'

STRIPE_PUBLIC_KEY = 'pk_test_51TfBaWGbV3hTYFZylFLXTOcYVMNCtUoK76H0kwUOAwQq9Dn47Jn6KZl3o4E67QPwiORbTwCuro9WHcWPKGOhMFfK00FXv7343e'
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY

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
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
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
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
    item = cursor.fetchone()
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
        total = sum(float(item['price']) * int(item['quantity']) for item in cart)

        conn = get_db()
        cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
        cursor.execute(
            'INSERT INTO orders (customer_name, customer_phone, customer_address, total) VALUES (%s,%s,%s,%s) RETURNING id',
            (customer_name, customer_phone, customer_address, total)
        )
        order_id = cursor.fetchone()['id']

        for item in cart:
            cursor.execute(
                'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)',
                (order_id, item['id'], item['quantity'], item['price'])
            )

        conn.commit()
        conn.close()
        session['cart'] = []
        return redirect(url_for('payment', order_id=order_id))

    return render_template('checkout.html')

@app.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    cursor.execute('''
        SELECT p.name, oi.quantity, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    ''', (order_id,))
    items = cursor.fetchall()
    conn.close()
    return render_template('confirmation.html', order=order, items=items)

# ─── CART API ───────────────────────────────────────────────

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    cart = session.get('cart', [])
    for item in cart:
        if int(item['id']) == int(data['id']):
            item['quantity'] = int(item['quantity']) + 1
            session['cart'] = cart
            session.modified = True
            return jsonify({'success': True, 'cart': cart})
    cart.append({
        'id': data['id'],
        'name': data['name'],
        'price': float(data['price']),
        'quantity': 1
    })
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/add-multiple', methods=['POST'])
def add_multiple_to_cart():
    data = request.json
    cart = session.get('cart', [])
    for item in cart:
        if int(item['id']) == int(data['id']):
            item['quantity'] = int(item['quantity']) + int(data['quantity'])
            session['cart'] = cart
            session.modified = True
            return jsonify({'success': True, 'cart': cart})
    cart.append({
        'id': data['id'],
        'name': data['name'],
        'price': float(data['price']),
        'quantity': int(data['quantity'])
    })
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    cart = session.get('cart', [])
    cart = [item for item in cart if int(item['id']) != int(data['id'])]
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    cart = session.get('cart', [])
    for item in cart:
        if int(item['id']) == int(data['id']):
            item['quantity'] = int(data['quantity'])
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', [])
    return jsonify({'cart': cart})

# ─── PAYMENT ───────────────────────────────────────────────

@app.route('/payment/<int:order_id>')
def payment(order_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    conn.close()
    return render_template('payment.html', order=order, public_key=STRIPE_PUBLIC_KEY)

@app.route('/payment/process', methods=['POST'])
def process_payment():
    order_id = request.form['order_id']
    token = request.form['stripeToken']
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    try:
        charge = stripe.Charge.create(
            amount=int(order['total'] * 100),
            currency='rwf',
            source=token,
            description=f'QuickBite Order #{order_id}'
        )
        cursor.execute('UPDATE orders SET status = %s WHERE id = %s', ('paid', order_id))
        cursor.execute('SELECT * FROM order_items WHERE order_id = %s', (order_id,))
        order_items = cursor.fetchall()
        for item in order_items:
            cursor.execute('UPDATE products SET stock = GREATEST(0, stock - %s) WHERE id = %s',
                          (item['quantity'], item['product_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('confirmation', order_id=order_id))
    except stripe.error.StripeError as e:
        conn.close()
        return render_template('payment.html', error=str(e), order=order, public_key=STRIPE_PUBLIC_KEY)

# ─── ADMIN ROUTES ───────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password))
        admin = cursor.fetchone()
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
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT COUNT(*) as count FROM orders')
    total_orders = cursor.fetchone()['count']
    cursor.execute('SELECT SUM(total) as total FROM orders')
    total_revenue = cursor.fetchone()['total'] or 0
    cursor.execute('SELECT COUNT(DISTINCT customer_phone) as count FROM orders')
    total_customers = cursor.fetchone()['count']
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    cursor.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT 10')
    recent_orders = cursor.fetchall()
    cursor.execute('''
        SELECT p.name, SUM(oi.quantity) as total_sold
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sold DESC
        LIMIT 6
    ''')
    popular_items = cursor.fetchall()
    cursor.execute('''
        SELECT p.category, SUM(oi.quantity * oi.price) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.category
    ''')
    category_revenue = cursor.fetchall()
    conn.close()

    popular_labels = [item['name'] for item in popular_items]
    popular_data = [item['total_sold'] for item in popular_items]
    category_labels = [item['category'] for item in category_revenue]
    category_data = [item['revenue'] for item in category_revenue]

    return render_template('admin/dashboard.html',
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_customers=total_customers,
        avg_order_value=avg_order_value,
        recent_orders=recent_orders,
        popular_labels=popular_labels,
        popular_data=popular_data,
        category_labels=category_labels,
        category_data=category_data
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/update-status', methods=['POST'])
def update_order_status():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    order_id = request.form['order_id']
    status = request.form['status']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/inventory')
def inventory():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()

    inventory = []
    for p in products:
        stock = p['stock']
        percentage = stock
        if stock >= 50:
            status = 'green'
        elif stock >= 20:
            status = 'yellow'
        else:
            status = 'red'
        inventory.append({
            'id': p['id'],
            'name': p['name'],
            'category': p['category'],
            'stock': stock,
            'percentage': percentage,
            'status': status
        })

    return render_template('admin/inventory.html', inventory=inventory)

@app.route('/admin/update-inventory', methods=['POST'])
def update_inventory():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    product_id = request.form['product_id']
    stock = int(request.form['stock'])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET stock = %s WHERE id = %s', (stock, product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('inventory'))

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        image = request.form['image']
        stock = int(request.form['stock'])
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, description, price, category, image, stock) VALUES (%s,%s,%s,%s,%s,%s)',
            (name, description, price, category, image, stock)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_products'))
    return render_template('admin/add_product.html')

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        image = request.form['image']
        stock = int(request.form['stock'])
        cursor.execute(
            'UPDATE products SET name=%s, description=%s, price=%s, category=%s, image=%s, stock=%s WHERE id=%s',
            (name, description, price, category, image, stock, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_products'))
    cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
    product = cursor.fetchone()
    conn.close()
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_products'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    success = False
    error = None

    if request.method == 'POST':
        name = request.form['name']
        rating = request.form.get('rating')
        feedback = request.form['feedback']

        if not rating:
            error = 'Please select a rating.'
        else:
            cursor.execute(
                'INSERT INTO reviews (name, rating, feedback) VALUES (%s, %s, %s)',
                (name, int(rating), feedback)
            )
            conn.commit()
            success = True

    cursor.execute('SELECT * FROM reviews ORDER BY created_at DESC')
    reviews = cursor.fetchall()
    conn.close()
    return render_template('about.html', reviews=reviews, success=success, error=error)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)