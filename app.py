from crypt import methods
from tokenize import Name
from xxlimited import new
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mysqldb import MySQL
import re


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'SuperMarket'

#app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql://root:''@localhost:3306/SuperMarket')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

mysql = MySQL(app)

class User(db.Model):
    Name = db.Column(db.String(50))
    Email = db.Column(db.String(50), primary_key = True)
    Password = db.Column(db.String(50))

    customer = db.relationship('Details', backref = 'User')
    receipt = db.relationship('Order', backref = 'User')

    def __repr__(self):
        return f'<User: {self.Email,self.Password}>'

class Products(db.Model):
    ID = db.Column(db.Integer(), primary_key = True)
    Product_Name = db.Column(db.String(50))
    Description = db.Column(db.String(50))
    Price = db.Column(db.Integer())
    Product_Image = db.Column(db.String(50))

    details = db.relationship('Details', backref = 'Products')
    def __repr__(self):
        return f'<Products: {self.ID, self.Product_Name, self.Price, self.Product_Image}>'

class Details(db.Model):
    Cart_ID = db.Column(db.Integer(), primary_key = True)
    Quantity = db.Column(db.Integer())
    Total_Price = db.Column(db.Integer())

    User_Email = db.Column(db.String(50), db.ForeignKey('user.Email'))
    Products_ID = db.Column(db.Integer(), db.ForeignKey('products.ID'))

    item = db.relationship('Order', backref = 'Details')


    def __repr__(self):
        return f'<Details: {self.User_Email,self.Products_ID, self.Cart_ID, self.Quantity, self.Total_Price}'

class Order(db.Model):
    Email = db.Column(db.String(50))
    Order_ID = db.Column(db.Integer(), primary_key = True)

    Purchasing_Date = db.Column(db.DateTime) 

    User_Email = db.Column(db.String(50), db.ForeignKey('user.Email'))
    Cart_ID = db.Column(db.Integer(), db.ForeignKey('details.Cart_ID')) 


    def __repr__(self):
        return f'<Order: {self.Email, self.Cart_ID, self.Cart_ID, self.Purchasing_Date}>'



@app.route('/')
def greeting():
    return "Welcome to the Super Market"


@app.route('/userlogin', methods =['POST'])
def login():
    credentials = request.get_json()
    user = User.objects.get(Email = credentials["Email"])
    if user and user.Password == credentials["Password"]:
        return jsonify({'Login Successfully': True})
    else:
        return ('Invalid Entry')
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('Name', None)
    session.pop('Email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['POST'])
def register():
    name = request.json['Name']
    email = request.json['Email']
    password = request.json['Password']

    new_user = User(name, email, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user)
    '''if not request.json['Name'] or not request.json['Email'] or not request.json['Password']:
        return ("Invalid Entry")
    else:
        user = User(request.json['Name'], request.json['Email'], request.json['Password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"Account Created": True})'''
    '''account = request.get_json()
    user = User.objects.post(Name = account["Name"])
    user = User.objects.post(Email = account["Email"])
    user = User.objects.post(Password = account["Password"])
    credential = user
    if credential:
        return ('Account already exists !')
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', user):
        return ('Invalid email address !')
    else:
        return ('Account registered.')'''

    

@app.route('/users/products', methods = ["GET"])
def items():
    product = request.get_json()
    info = product.fetchall()
    return jsonify(info)


@app.route('/admin/products', methods = ["POST"])
def add_items():
    if not request.json['ID'] or not request.json['Product_Name'] or not request.json['Description'] or not request.json['Price']:
        return ("Invalid Entry")
    else:
        product = Products(request.json['ID'], request.json['Product_Name'], request.json['Description'], request.json['Price'])
        db.session.add(product)
        db.session.commit()
        return jsonify({"Product Added": True})

@app.route('/user/order-details', methods = ["GET", "POST"])
def order_details():
    grand_total = 0
    index = 0
    total_quantity = 0

    for item in session['cart']:
        product = Products.query.filter_by(id=item['id'])

        quantity = int(item['quantity'])
        total = quantity * product.Price

        grand_total +=total
        total_quantity += quantity

        Products.append({'ID' : Products.ID, 'Product_Name': Products.Product_Name, 'Description': Products.Description, 'Price': Products.Price})
        index +=1
    
    grand_total_shipping_charges = grand_total + 250
    return Products, grand_total, grand_total_shipping_charges, total_quantity

@app.route('/cart')
def cart():
    Products, grand_total, grand_total_shipping_charges, total_quantity = order_details()

    return render_template('cart.html', products=Products, grand_total=grand_total, grand_total_plus_shipping=grand_total_shipping_charges, total_quantity=total_quantity)


if __name__ == "__main__":
    app.run(debug=True)