from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mysqldb import MySQL
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql://root:''@localhost:3306/SuperMarket')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

mysql = migrate(app)

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
@app.route('/userlogin', methods =['POST'])
def login():
    message = ''
    if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        Email = request.form['Email']
        Password = request.form['Password']
        print(Email, Password)
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE Email = % s AND Password = % s', (Email, Password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['Name'] = user['Name']
            session['Email'] = user['Email']
            session['Password'] = user['Password']
            message = 'Logged in successfully !'
            return jsonify({'success': True})
            #return render_template('user.html', message = message)
        else:
            message = 'Please enter correct Email / Password !'
    #return render_template('login.html', message = message)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('Name', None)
    session.pop('Email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['POST'])
def register():
    message = ''
    if request.method == 'POST' and 'Name' in request.form and 'Email' in request.form and 'Password' in request.form :
        Name = request.form['Name']
        Email = request.form['Email']
        Password = request.form['Password']
        print(Name, Email, Password)
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE Email = % s', (Email, ))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', Email):
            message = 'Invalid email address !'
        elif not Name or not Password or not Email:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (% s, % s, %s)', (Name, Email, Password))
            mysql.connection.commit()
            message = 'You have successfully registered !'
    return jsonify({'success': True})
    # elif request.method == 'POST':
        # message = 'Please fill out the form !'
    # return render_template('register.html', message = message)

#products:

@app.route('/users/products', methods = ["GET"])
def items():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products")
    info = cursor.fetchall()
    return jsonify(info)

@app.route('/admin/products', methods = ["POST"])
def addproduct():
    if request.method == 'POST' and 'ID' in request.form and 'Product_Name' in request.form and 'Description' in request.form and 'Price' in request.form:
        id = request.form['ID']
        name = request.form['Product_Name']
        description = request.form['Description']
        price = request.form['Price']

        cursor = mysql.conncection.cursor()
        cursor.execute('INSERT INTO products VALUES (% s, % s, % s, % s)', (id,name,description,price))
        mysql.connection.commit()
        cursor.close()
    return jsonify({'success' : True})

#order details
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