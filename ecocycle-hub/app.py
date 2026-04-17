import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Secure secret key for session management (pulls from environment in production)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_development_key')

# In-memory data store for products
PRODUCTS = [
    {
        "id": 1,
        "name": "EcoBench",
        "price": 120.00,
        "description": "A durable, weather-resistant park bench made from 100% recycled plastic. Perfect for parks, gardens, and patios.",
        "image": "img/bench.png"
    },
    {
        "id": 2,
        "name": "Green Planter Box",
        "price": 45.00,
        "description": "Sleek and vibrant planters that are perfect for indoor and outdoor plants. Helps reduce plastic waste with every purchase.",
        "image": "img/planter.png"
    },
    {
        "id": 3,
        "name": "Interlocking Floor Tiles",
        "price": 30.00,
        "description": "Sturdy interlocking tiles made from recycled polymers. Ideal for walkways, patios, and outdoor spaces.",
        "image": "img/tiles.png"
    },
    {
        "id": 4,
        "name": "Compost & Recycling Bin",
        "price": 60.00,
        "description": "A robust, multi-compartment dustbin designed to encourage proper recycling and waste management at home.",
        "image": "img/dustbin.png"
    },
    {
        "id": 5,
        "name": "Eco-Friendly Bird Feeder",
        "price": 25.00,
        "description": "A sleek, weather-resistant bird feeder designed to withstand the elements and keep seed fresh.",
        "image": "img/birdfeeder.png"
    },
    {
        "id": 6,
        "name": "Recycled Picnic Table",
        "price": 250.00,
        "description": "A sturdy, modern outdoor picnic table perfect for parks and gardens, never rots or splinters.",
        "image": "img/picnictable.png"
    },
    {
        "id": 7,
        "name": "Premium Doghouse",
        "price": 180.00,
        "description": "Provide luxury and safety for your furry friend with this eco-friendly, weather-resistant outdoor doghouse.",
        "image": "img/doghouse.png"
    },
    {
        "id": 8,
        "name": "Outdoor Decking Boards",
        "price": 40.00,
        "description": "Sleek and beautiful modern decking boards made from recycled plastic. Impervious to moisture and simple to clean.",
        "image": "img/decking.png"
    }
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html', products=PRODUCTS)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_str_id = str(product_id)
    
    # Increase quantity or add new item
    if product_str_id in cart:
        cart[product_str_id]['quantity'] += 1
    else:
        # Find product details
        product = next((p for p in PRODUCTS if p['id'] == product_id), None)
        if product:
            cart[product_str_id] = {
                'name': product['name'],
                'price': product['price'],
                'quantity': 1,
                'image': product['image']
            }
            
    session['cart'] = cart
    # Make sure session is saved
    session.modified = True
    flash('Product added to your cart!', 'success')
    
    return redirect(url_for('products'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart=cart_items, total=total_price)

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('Cart has been cleared.', 'info')
    return redirect(url_for('cart'))

@app.route('/pickup', methods=['GET', 'POST'])
def pickup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Backend Validation
        if not name:
            flash('Name is compulsory and cannot be blank.', 'danger')
            return redirect(url_for('pickup'))
            
        if not address:
            flash('Address is compulsory and cannot be blank.', 'danger')
            return redirect(url_for('pickup'))
            
        if not phone.isdigit() or len(phone) != 10:
            flash('Phone number must be exactly 10 digits.', 'danger')
            return redirect(url_for('pickup'))
        
        # In a real app, this would be saved to a database
        print(f"New Pickup Request: {name}, {address}, {phone}")
        
        flash('Thank you! Your pickup request has been received. Our team will contact you shortly.', 'success')
        return redirect(url_for('pickup'))
        
    return render_template('pickup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        # Simulate sending a message
        print(f"Message from {name}: {message}")
        flash('Your message has been sent to our team!', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

if __name__ == '__main__':
    # Ensure static/img directory exists
    os.makedirs(os.path.join(app.root_path, 'static', 'img'), exist_ok=True)
    
    # Check if we should run in debug mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Use environment port if specified, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=debug_mode, port=port)
