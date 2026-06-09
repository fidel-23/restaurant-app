import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')

def send_order_confirmation(customer_email, customer_name, order_id, items, total):
    items_html = ''.join([f'<tr><td>{item["name"]}</td><td>x{item["quantity"]}</td><td>RWF {item["price"]}</td></tr>' for item in items])
    
    html_content = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #070d1b; color: white; padding: 30px; border-radius: 10px;">
        <h1 style="color: #f4a200;">🍔 QuickBite Kigali</h1>
        <h2>Order Confirmed! ✅</h2>
        <p>Hi <strong>{customer_name}</strong>, your order has been placed successfully.</p>
        
        <div style="background: #0f1c35; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #f4a200;">Order #{order_id}</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="color: #a0aec0;">
                    <th style="text-align:left; padding: 8px;">Item</th>
                    <th style="text-align:left; padding: 8px;">Qty</th>
                    <th style="text-align:left; padding: 8px;">Price</th>
                </tr>
                {items_html}
            </table>
            <hr style="border-color: #1a2d4f; margin: 15px 0;">
            <h3 style="color: #f4a200;">Total: RWF {total}</h3>
        </div>
        
        <p style="color: #a0aec0;">We are preparing your order. You will receive an update when it is on the way.</p>
        <p style="color: #a0aec0;">Thank you for choosing QuickBite Kigali!</p>
    </div>
    '''
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=customer_email,
        subject=f'QuickBite Order #{order_id} Confirmed ✅',
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f'Email error: {e}')
        return False

def send_order_status_update(customer_email, customer_name, order_id, status):
    status_messages = {
        'preparing': 'Your order is being prepared 👨‍🍳',
        'on the way': 'Your order is on the way 🚗',
        'delivered': 'Your order has been delivered 🎉',
        'paid': 'Your payment was confirmed ✅'
    }
    
    message_text = status_messages.get(status, f'Your order status has been updated to: {status}')
    
    html_content = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #070d1b; color: white; padding: 30px; border-radius: 10px;">
        <h1 style="color: #f4a200;">🍔 QuickBite Kigali</h1>
        <h2>Order Update 📦</h2>
        <p>Hi <strong>{customer_name}</strong>,</p>
        <div style="background: #0f1c35; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
            <h2 style="color: #f4a200;">{message_text}</h2>
            <p style="color: #a0aec0;">Order #{order_id}</p>
        </div>
        <p style="color: #a0aec0;">Thank you for choosing QuickBite Kigali!</p>
    </div>
    '''
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=customer_email,
        subject=f'QuickBite Order #{order_id} Update',
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f'Email error: {e}')
        return False

def send_password_reset(customer_email, customer_name, reset_link):
    html_content = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #070d1b; color: white; padding: 30px; border-radius: 10px;">
        <h1 style="color: #f4a200;">🍔 QuickBite Kigali</h1>
        <h2>Password Reset Request 🔐</h2>
        <p>Hi <strong>{customer_name}</strong>,</p>
        <p>We received a request to reset your password. Click the button below to reset it.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background: #f4a200; color: #070d1b; padding: 15px 30px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1rem;">Reset Password</a>
        </div>
        <p style="color: #a0aec0;">This link expires in 1 hour. If you did not request this, ignore this email.</p>
    </div>
    '''
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=customer_email,
        subject='QuickBite Password Reset Request',
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f'Email error: {e}')
        return False