import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Order, PickupRequest
from forms import RegistrationForm, LoginForm, PickupForm, ContactForm

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_development_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Seed function for products
def seed_products():
    if Product.query.count() == 0:
        products_data = [
            {"name": "EcoBench", "price": 120.00, "description": "A durable, weather-resistant park bench made from 100% recycled plastic. Perfect for parks, gardens, and patios.", "image": "img/bench.png"},
            {"name": "Green Planter Box", "price": 45.00, "description": "Sleek and vibrant planters that are perfect for indoor and outdoor plants. Helps reduce plastic waste with every purchase.", "image": "img/planter.png"},
            {"name": "Interlocking Floor Tiles", "price": 30.00, "description": "Sturdy interlocking tiles made from recycled polymers. Ideal for walkways, patios, and outdoor spaces.", "image": "img/tiles.png"},
            {"name": "Compost & Recycling Bin", "price": 60.00, "description": "A robust, multi-compartment dustbin designed to encourage proper recycling and waste management at home.", "image": "img/dustbin.png"},
            {"name": "Eco-Friendly Bird Feeder", "price": 25.00, "description": "A sleek, weather-resistant bird feeder designed to withstand the elements and keep seed fresh.", "image": "img/birdfeeder.png"},
            {"name": "Recycled Picnic Table", "price": 250.00, "description": "A sturdy, modern outdoor picnic table perfect for parks and gardens, never rots or splinters.", "image": "img/picnictable.png"},
            {"name": "Premium Doghouse", "price": 180.00, "description": "Provide luxury and safety for your furry friend with this eco-friendly, weather-resistant outdoor doghouse.", "image": "img/doghouse.png"},
            {"name": "Outdoor Decking Boards", "price": 40.00, "description": "Sleek and beautiful modern decking boards made from recycled plastic. Impervious to moisture and simple to clean.", "image": "img/decking.png"}
        ]
        for p in products_data:
            db.session.add(Product(**p))
        
        # Also seed a default admin
        admin = User(username='admin', password=generate_password_hash('password123'), is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login Successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    product_str_id = str(product_id)
    if product_str_id in cart:
        cart[product_str_id]['quantity'] += 1
    else:
        product = Product.query.get(product_id)
        if product:
            cart[product_str_id] = {
                'name': product.name,
                'price': product.price,
                'quantity': 1,
                'image': product.image
            }
    session['cart'] = cart
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

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Cart is empty', 'warning')
        return redirect(url_for('cart'))
        
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    order = Order(user_id=current_user.id, total_price=total_price, status='Completed')
    db.session.add(order)
    db.session.commit()
    
    session.pop('cart', None)
    flash('Checkout successful! Your order has been placed.', 'success')
    return redirect(url_for('home'))

@app.route('/pickup', methods=['GET', 'POST'])
def pickup():
    form = PickupForm()
    if form.validate_on_submit():
        req = PickupRequest(name=form.name.data, address=form.address.data, phone=form.phone.data)
        db.session.add(req)
        db.session.commit()
        flash('Thank you! Your pickup request has been received.', 'success')
        return redirect(url_for('pickup'))
    return render_template('pickup.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Store message or print for now
        print(f"Message from {form.name.data}: {form.message.data}")
        flash('Your message has been sent to our team!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('home'))
        
    pickups = PickupRequest.query.order_by(PickupRequest.date_requested.desc()).all()
    orders = Order.query.order_by(Order.date_created.desc()).all()
    return render_template('admin.html', pickups=pickups, orders=orders)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_products()
    os.makedirs(os.path.join(app.root_path, 'static', 'img'), exist_ok=True)
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=debug_mode, port=port)
