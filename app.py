from flask import Flask, render_template

app = Flask(__name__)

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
