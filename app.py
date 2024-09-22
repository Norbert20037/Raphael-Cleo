from flask import Flask, render_template, request
from flask_babel import Babel

app = Flask(__name__)

# Nastavení Flask-Babel pro vícejazyčnou podporu
app.config['BABEL_DEFAULT_LOCALE'] = 'cs'
app.config['BABEL_SUPPORTED_LOCALES'] = ['cs', 'en']

babel = Babel(app)

# Opravený způsob nastavení locale selector
babel.init_app(app)

@babel.locale_selector_func
def get_locale():
    # Automatická detekce jazyka na základě IP adresy nebo preferencí prohlížeče
    return request.accept_languages.best_match(['cs', 'en'])

# Route pro hlavní stránku (index)
@app.route('/')
def index():
    products = [
        {'name': 'Raphael Cleo Black T-Shirt', 'stock': 20, 'price': 1200},
        {'name': 'Raphael Cleo Purple T-Shirt', 'stock': 15, 'price': 1300}
    ]
    return render_template('index.html', products=products)

# Route pro stránku kontakt
@app.route('/kontakt')
def kontakt():
    return render_template('kontakt.html')

# Route pro stránku košík
@app.route('/kosik')
def kosik():
    return render_template('kosik.html')

# Route pro stránku o nás
@app.route('/onas')
def onas():
    return render_template('onas.html')

if __name__ == '__main__':
    app.run(debug=True)
