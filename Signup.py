#for manually inserting value in DB.

'''import mysql.connector

conn = mysql.connector.connect(
   user='root', password='', host='localhost', database='SuperMarket')


cursor = conn.cursor()


insert = ("INSERT INTO user(Name, Email, Password) VALUES (%s, %s, %s)")
data = ("Ahmed", "ahmedyz@gmail.com", "functions")

cursor.execute(insert, data)
conn.commit()

print(cursor.rowcount, "Record Entered")

conn.close()'''

from crypt import methods
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import MySQLdb
import re
from app import migrate, app

app = Flask(__name__)
   
app.secret_key = ''
  
'''app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'SuperMarket'
migrate = Migrate(app) 
mysql = MySQL(app)'''

app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql://root:''@localhost:3306/SuperMarket')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#login/signup

@app.route('/')
@app.route('/userlogin', methods =['POST'])
def login():
    message = ''
    #if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        #Email = request.form['Email']
        #Password = request.form['Password']
        #print(Email, Password)
    credentials = request.get_json()
    cursor = MySQLdb.connection.cursor()
    cursor.execute('SELECT * FROM user WHERE Email = % s', (credentials))
    user = cursor.fetchone()
    if user:
        session['loggedin'] = True
        session['Name'] = user['Name']
        session['Email'] = user['Email']
        session['Password'] = user['Password']
        message = 'Logged in successfully !'
    return jsonify({'success': True})
            #return render_template('user.html', message = message)
        #else:
    #    message = 'Please enter correct Email / Password !'
    #return render_template('login.html', message = message)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('Name', None)
    session.pop('Email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['POST'])
def register():
    Name = request.get_json['Name']
    Email = request.get_json['Email']
    Password = request.get_json['Password']
    a = 'INSERT INTO user VALUES (% s, % s, %s)', (Name, Email, Password)
    db.session.add(a)
    db.session.commit()
    '''message = ''
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
    # return render_template('register.html', message = message)'''

if __name__ == "__main__":
    app.run(debug=True)