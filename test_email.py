from email_service import send_order_confirmation

result = send_order_confirmation(
    'worjlohkfidel@gmail.com',
    'Test User',
    1,
    [{'name': 'Beef Burger', 'quantity': 1, 'price': 3500}],
    3500
)
print('Sent:', result)
