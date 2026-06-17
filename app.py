from email_service import send_order_confirmation, send_order_status_update, send_password_reset
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
    cursor.execute('SELECT * FROM products WHERE restaurant_id = 1 ORDER BY id')
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
        customer_id = session['customer']['id'] if session.get('customer') else None

        conn = get_db()
        cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
        cursor.execute(
            'INSERT INTO orders (restaurant_id, customer_id, customer_name, customer_phone, customer_address, total) VALUES (1,%s,%s,%s,%s,%s) RETURNING id',
            (customer_id, customer_name, customer_phone, customer_address, total)
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

    customer = session.get('customer')
    return render_template('checkout.html', customer=customer)

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

        print("Customer session:", session.get('customer'))
        if session.get('customer'):
            cursor.execute('''
                SELECT p.name, oi.quantity, oi.price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            ''', (order_id,))
            email_items = cursor.fetchall()
            send_order_confirmation(
                session['customer']['email'],
                session['customer']['name'],
                order_id,
                email_items,
                order['total']
            )

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
        cursor.execute('SELECT * FROM admin WHERE username = %s', (username,))
        admin = cursor.fetchone()
        if admin and not bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
            admin = None
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
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
    
    cursor.execute('''
        SELECT o.*, c.email, c.name as cname 
        FROM orders o 
        LEFT JOIN customers c ON o.customer_id = c.id 
        WHERE o.id = %s
    ''', (order_id,))
    order = cursor.fetchone()
    
    if order and order['email']:
        send_order_status_update(
            order['email'],
            order['cname'],
            order_id,
            status
        )
    
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

import bcrypt
import secrets
from datetime import datetime, timedelta

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db()
        cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)

        cursor.execute('SELECT id FROM customers WHERE email = %s', (email,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return render_template('register.html', error='An account with this email already exists')

        cursor.execute(
            'INSERT INTO customers (name, email, password, phone, address) VALUES (%s,%s,%s,%s,%s) RETURNING id',
            (name, email, hashed, phone, address)
        )
        customer_id = cursor.fetchone()['id']

        cursor.execute(
            'UPDATE orders SET customer_id = %s WHERE customer_name = %s AND customer_id IS NULL',
            (customer_id, name)
        )

        conn.commit()
        conn.close()

        session['customer'] = {'id': customer_id, 'name': name, 'email': email, 'phone': phone, 'address': address}
        return redirect(url_for('profile'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
        cursor.execute('SELECT * FROM customers WHERE email = %s', (email,))
        customer = cursor.fetchone()
        conn.close()

        if customer and bcrypt.checkpw(password.encode('utf-8'), customer['password'].encode('utf-8')):
            session['customer'] = {
                'id': customer['id'],
                'name': customer['name'],
                'email': customer['email'],
                'phone': customer['phone'],
                'address': customer['address']
            }
            return redirect(url_for('profile'))

        return render_template('customer_login.html', error='Invalid email or password')

    return render_template('customer_login.html')

@app.route('/logout')
def customer_logout():
    session.pop('customer', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('customer'):
        return redirect(url_for('customer_login'))

    customer_id = session['customer']['id']
    feedback_success = False

    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'feedback':
            rating = request.form.get('rating')
            feedback = request.form['feedback']
            if rating and feedback:
                cursor.execute(
                    'INSERT INTO reviews (restaurant_id, customer_id, name, rating, feedback) VALUES (1, %s, %s, %s, %s)',
                    (customer_id, session['customer']['name'], int(rating), feedback)
                )
                conn.commit()
                feedback_success = True

    cursor.execute('SELECT * FROM orders WHERE customer_id = %s ORDER BY created_at DESC', (customer_id,))
    orders = cursor.fetchall()

    orders_with_items = []
    for order in orders:
        cursor.execute('''
            SELECT p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        ''', (order['id'],))
        items = cursor.fetchall()
        order_dict = dict(order)
        order_dict['items'] = items
        orders_with_items.append(order_dict)

    conn.close()
    return render_template('profile.html',
        customer=session['customer'],
        orders=orders_with_items,
        feedback_success=feedback_success
    )

@app.route('/reorder', methods=['POST'])
def reorder():
    if not session.get('customer'):
        return redirect(url_for('customer_login'))

    order_id = request.form['order_id']
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('''
        SELECT p.id, p.name, p.price, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    ''', (order_id,))
    items = cursor.fetchall()
    conn.close()

    cart = session.get('cart', [])
    for item in items:
        found = False
        for cart_item in cart:
            if int(cart_item['id']) == int(item['id']):
                cart_item['quantity'] = int(cart_item['quantity']) + int(item['quantity'])
                found = True
                break
        if not found:
            cart.append({
                'id': item['id'],
                'name': item['name'],
                'price': float(item['price']),
                'quantity': int(item['quantity'])
            })

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
        cursor.execute('SELECT * FROM customers WHERE email = %s', (email,))
        customer = cursor.fetchone()

        if customer:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)
            cursor.execute(
                'INSERT INTO password_resets (customer_id, token, expires_at) VALUES (%s, %s, %s)',
                (customer['id'], token, expires_at)
            )
            conn.commit()
            reset_link = url_for('reset_password', token=token, _external=True)
            send_password_reset(customer['email'], customer['name'], reset_link)

        conn.close()
        return render_template('forgot_password.html', success='If an account exists with that email, a reset link has been sent.')

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute(
        'SELECT * FROM password_resets WHERE token = %s AND expires_at > NOW()',
        (token,)
    )
    reset = cursor.fetchone()

    if not reset:
        conn.close()
        return render_template('reset_password.html', error='This reset link is invalid or has expired.', token=token)

    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            conn.close()
            return render_template('reset_password.html', error='Passwords do not match.', token=token)

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('UPDATE customers SET password = %s WHERE id = %s', (hashed, reset['customer_id']))
        cursor.execute('DELETE FROM password_resets WHERE token = %s', (token,))
        conn.commit()
        conn.close()
        return redirect(url_for('customer_login'))

    conn.close()
    return render_template('reset_password.html', token=token)

    import time
import json

@app.route('/track/<int:order_id>')
def track_order(order_id):
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
    if not order:
        return redirect(url_for('index'))
    return render_template('tracking.html', order=order, items=items)

@app.route('/track/<int:order_id>/stream')
def track_stream(order_id):
    def generate():
        last_status = None
        attempts = 0
        while attempts < 200:
            conn = get_db()
            cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
            cursor.execute('SELECT status FROM orders WHERE id = %s', (order_id,))
            order = cursor.fetchone()
            conn.close()
            if order:
                status = order['status']
                if status != last_status:
                    last_status = status
                    yield f"data: {json.dumps({'status': status})}\n\n"
                if status in ['delivered', 'paid']:
                    break
            time.sleep(3)
            attempts += 1
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/api/order/<int:order_id>/status')
def order_status(order_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT status FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    conn.close()
    return jsonify({'status': order['status'] if order else 'unknown'})

    import csv
import io
from flask import Response

@app.route('/admin/analytics')
def analytics():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    period = request.args.get('period', 'today')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    params = [1]
    if period == 'today':
        date_filter = "AND o.created_at >= CURRENT_DATE"
    elif period == 'week':
        date_filter = "AND o.created_at >= CURRENT_DATE - INTERVAL '7 days'"
    elif period == 'month':
        date_filter = "AND o.created_at >= CURRENT_DATE - INTERVAL '30 days'"
    elif period == 'custom' and start_date and end_date:
        date_filter = "AND o.created_at >= %s AND o.created_at < (%s::date + INTERVAL '1 day')"
        params.extend([start_date, end_date])
    else:
        date_filter = ""
        period = 'all'

    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)

    cursor.execute(f'SELECT COUNT(*) as count FROM orders o WHERE o.restaurant_id = %s {date_filter}', params)
    total_orders = cursor.fetchone()['count']

    cursor.execute(f'SELECT SUM(total) as total FROM orders o WHERE o.restaurant_id = %s {date_filter}', params)
    total_revenue = cursor.fetchone()['total'] or 0

    cursor.execute(f'SELECT COUNT(DISTINCT customer_phone) as count FROM orders o WHERE o.restaurant_id = %s {date_filter}', params)
    unique_customers = cursor.fetchone()['count']

    avg_order = total_revenue / total_orders if total_orders > 0 else 0

    cursor.execute(f'''
        SELECT customer_name, customer_phone, COUNT(*) as order_count, SUM(total) as total_spent
        FROM orders o
        WHERE o.restaurant_id = %s {date_filter}
        GROUP BY customer_name, customer_phone
        ORDER BY total_spent DESC
        LIMIT 5
    ''', params)
    top_customers = cursor.fetchall()

    cursor.execute(f'''
        SELECT p.name, SUM(oi.quantity) as qty_sold, SUM(oi.quantity * oi.price) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.restaurant_id = %s {date_filter}
        GROUP BY p.name
        ORDER BY qty_sold DESC
        LIMIT 5
    ''', params)
    top_items = cursor.fetchall()

    cursor.execute(f'''
        SELECT o.*, string_agg(p.name || ' x' || oi.quantity::text, ', ') as items_summary
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.restaurant_id = %s {date_filter}
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''', params)
    all_orders = cursor.fetchall()

    conn.close()

    return render_template('admin/analytics.html',
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_orders=total_orders,
        total_revenue=total_revenue,
        unique_customers=unique_customers,
        avg_order=avg_order,
        top_customers=top_customers,
        top_items=top_items,
        all_orders=all_orders
    )

@app.route('/admin/export-orders')
def export_orders():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    period = request.args.get('period', 'today')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    params = [1]
    if period == 'today':
        date_filter = "AND created_at >= CURRENT_DATE"
    elif period == 'week':
        date_filter = "AND created_at >= CURRENT_DATE - INTERVAL '7 days'"
    elif period == 'month':
        date_filter = "AND created_at >= CURRENT_DATE - INTERVAL '30 days'"
    elif period == 'custom' and start_date and end_date:
        date_filter = "AND created_at >= %s AND created_at < (%s::date + INTERVAL '1 day')"
        params.extend([start_date, end_date])
    else:
        date_filter = ""

    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute(f'''
        SELECT * FROM orders
        WHERE restaurant_id = %s {date_filter}
        ORDER BY created_at DESC
    ''', params)
    orders = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Customer Name', 'Phone', 'Address', 'Total', 'Status', 'Date'])
    for order in orders:
        writer.writerow([
            order['id'], order['customer_name'], order['customer_phone'],
            order['customer_address'], order['total'], order['status'],
            order['created_at'].strftime('%Y-%m-%d %H:%M')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=orders_{period}.csv'}
    )

@app.route('/api/chatbot/popular')
def chatbot_popular():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('''
        SELECT p.id, p.name, p.price, SUM(oi.quantity) as total_sold
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE p.restaurant_id = 1
        GROUP BY p.id, p.name, p.price
        ORDER BY total_sold DESC
        LIMIT 3
    ''')
    items = cursor.fetchall()
    conn.close()
    return jsonify({'items': [{'name': i['name'], 'price': i['price']} for i in items]})

@app.route('/api/chatbot/search-item')
def chatbot_search_item():
    name = request.args.get('name', '').strip()
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('''
        SELECT id, name, price FROM products
        WHERE restaurant_id = 1 AND LOWER(name) LIKE %s
        LIMIT 1
    ''', (f'%{name.lower()}%',))
    item = cursor.fetchone()

    if not item:
        cursor.execute('''
            SELECT id, name, price FROM products
            WHERE restaurant_id = 1
            ORDER BY similarity(LOWER(name), %s) DESC
            LIMIT 1
        ''', (name.lower(),))
        candidate = cursor.fetchone()
        if candidate:
            item = candidate

    conn.close()
    if item:
        return jsonify({'found': True, 'id': item['id'], 'name': item['name'], 'price': item['price']})
    return jsonify({'found': False})

@app.route('/admin/chat-logs')
def chat_logs_page():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor(cursor_factory=__import__('psycopg2').extras.RealDictCursor)
    cursor.execute('SELECT * FROM chat_logs WHERE restaurant_id = 1 ORDER BY created_at DESC')
    logs = cursor.fetchall()
    conn.close()
    return render_template('admin/chat_logs.html', logs=logs)

@app.route('/admin/chat-logs/resolve/<int:id>', methods=['POST'])
def resolve_chat_log(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE chat_logs SET resolved = TRUE WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('chat_logs_page'))
if __name__ == '__main__':
    debug_mode = os.getenv('RENDER') != 'true'
app.run(host='0.0.0.0', port=5000, debug=debug_mode)