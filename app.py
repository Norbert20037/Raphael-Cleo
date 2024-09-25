from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurace databáze - zde používáme SQLite, ale můžeš změnit na PostgreSQL/MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raphael_cleo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializace SQLAlchemy
db = SQLAlchemy(app)

# Model pro produkty
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)

# Model pro recenze
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('reviews', lazy=True))

# Model pro položky v košíku
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='cart_items')
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # Unikátní ID session pro košík

# Vytvoření tabulek v databázi
with app.app_context():
    db.create_all()

@app.before_request
def ensure_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Vytvoření unikátního session ID

# Route pro hlavní stránku
@app.route('/')
def index():
    products = Product.query.all()  # Načítání všech produktů z databáze
    return render_template('index.html', products=products)

# Dočasná route pro přidání produktů
@app.route('/add_products')
def add_products():
    product1 = Product(name='Raphael Cleo Black T-Shirt', price=1200, stock=20, image='/static/images/Tshirts/Black/raphael_cleo_back_cropped.jpg')
    product2 = Product(name='Raphael Cleo Purple T-Shirt', price=1300, stock=15, image='/static/images/Tshirts/Purple/raphael_cleo_front_cropped.jpg')
    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()
    return "Produkty byly úspěšně přidány!"

# Dočasná route pro kontrolu produktů
@app.route('/check_products')
def check_products():
    products = Product.query.all()
    if not products:
        return "Žádné produkty nebyly nalezeny v databázi!"
    return "<br>".join([f"{product.name} - Cena: {product.price} Kč" for product in products])

# Přidání produktu do košíku
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size')
    session_id = session['session_id']  # Unikátní session ID pro košík

    product = Product.query.get(product_id)

    if product:
        cart_item = CartItem(product_id=product.id, quantity=quantity, size=size, session_id=session_id)
        db.session.add(cart_item)
        db.session.commit()

        flash(f'Přidali jste {quantity}x {product.name} do košíku.', 'success')

    return redirect(url_for('index'))

# Zobrazení košíku
@app.route('/kosik')
def kosik():
    session_id = session['session_id']
    cart_items = CartItem.query.filter_by(session_id=session_id).all()

    for item in cart_items:
        if item.product:
            print(f"Product: {item.product.name}, Price: {item.product.price}, Quantity: {item.quantity}")
        else:
            print(f"CartItem without product: {item.id}, Quantity: {item.quantity}")
    
    total = sum(item.product.price * item.quantity for item in cart_items if item.product)
    
    return render_template('kosik.html', cart=cart_items, total=total)


# Odstranění položky z košíku
@app.route('/remove_from_cart/<int:product_id>/<string:size>')
def remove_from_cart(product_id, size):
    session_id = session['session_id']
    cart_item = CartItem.query.filter_by(product_id=product_id, size=size, session_id=session_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

        flash('Položka byla odstraněna z košíku.', 'success')

    return redirect(url_for('kosik'))

# Úprava množství položek v košíku
@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    new_quantity = int(request.form.get('quantity'))
    session_id = session['session_id']
    cart_item = CartItem.query.filter_by(product_id=product_id, session_id=session_id).first()

    if cart_item:
        cart_item.quantity = new_quantity
        db.session.commit()
        flash('Množství bylo aktualizováno.', 'success')

    return redirect(url_for('kosik'))

# Formulář pro přidání a úpravu produktů
class ProductForm(FlaskForm):
    name = StringField('Název produktu', validators=[DataRequired()])
    price = IntegerField('Cena', validators=[DataRequired()])
    stock = IntegerField('Počet kusů', validators=[DataRequired()])
    image = StringField('URL obrázku', validators=[DataRequired()])
    submit = SubmitField('Uložit')

# Přidání nového produktu
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            stock=form.stock.data,
            image=form.image.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Produkt byl přidán!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_product.html', form=form)

# Úprava existujícího produktu
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.image = form.image.data
        db.session.commit()
        flash('Produkt byl úspěšně aktualizován.', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_product.html', form=form, product=product)

# Mazání produktu
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produkt byl úspěšně odstraněn.', 'success')
    return redirect(url_for('index'))

# Stránka Kontakt
@app.route('/kontakt')
def kontakt():
    return render_template('kontakt.html')

# Stránka O nás
@app.route('/onas')
def onas():
    return render_template('onas.html')

# Zobrazení detailu produktu
@app.route('/produkt/<int:product_id>')
def produkt_detail(product_id):
    product = Product.query.get(product_id)
    if product:
        reviews = Review.query.filter_by(product_id=product.id).all()
        return render_template('produkt_detail.html', product=product, reviews=reviews)
    else:
        flash('Produkt nebyl nalezen.', 'danger')
        return redirect(url_for('index'))

# Přidání recenze
@app.route('/submit_review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    author = request.form['author']
    content = request.form['content']
    rating = int(request.form['rating'])

    new_review = Review(author=author, content=content, rating=rating, product_id=product_id)
    db.session.add(new_review)
    db.session.commit()

    flash('Recenze byla úspěšně odeslána.', 'success')
    return redirect(url_for('produkt_detail', product_id=product_id))

if __name__ == '__main__':
    app.run(debug=True)
