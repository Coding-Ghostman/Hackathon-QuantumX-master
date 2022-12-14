# Main project file involving Routes, MySQL connection, etc.

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from parser_1 import ResumeParser
import MySQLdb.cursors
import re
import os

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config["MYSQL_PORT"] = 3300
app.config['MYSQL_DB'] = 'pythonlogin'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

parser = ResumeParser('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')

# Intialize MySQL
mysql = MySQL(app)


# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['username'] = account['username']
            session['password'] = account['password']
            if session['username'] == "admin":
                return redirect(url_for('admin'))
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/upload')
def upload():
   return render_template('profile.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

	
@app.route('/uploader', methods = ['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@app.route("/resume", methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
       # check if the post request has the file part
       if 'file' not in request.files:
           flash('No file part')
           return redirect(url_for('profile'))
       
       file = request.files['file']
       
       if file.filename == '':
            flash('No selected file')
            return redirect(url_for('profile'))
        
       if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('display_resume', name=filename))
        
       return render_template('profile.html')
  
@app.route('/resume/<name>')
def display_resume(name):
    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], name)
    resume_dict = parser.query_resume(resume_path)
    session["resume"] = resume_dict
    basic_info = resume_dict.get('basic_info')
    project_experience = resume_dict.get('project_experience')
    work_experience = resume_dict.get('work_experience')
    basic_info_cols = list(basic_info.keys());
    
    
    sorted_column_values_string = ', '.join(basic_info_cols)
    print(sorted_column_values_string)
    
    # # Check if account exists using MySQL
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('ALTER INTO applicants ADD COLUMN(%s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30), %s varchar(30)',([sorted_column_values_string]))
    # account = cursor.fetchone()
    
    # # If account exists show error and validation checks
    # if account:
    #     msg = 'Account already exists!'
    # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
    #     msg = 'Invalid email address!'
    # elif not re.match(r'[A-Za-z0-9]+', username):
    #     msg = 'Username must contain only characters and numbers!'
    # elif not username or not password or not email:
    #     msg = 'Please fill out the form!'
    # else:
    #     # Account doesnt exists and the form data is valid, now insert new account into accounts table
    #     cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
    #     mysql.connection.commit()
    #     msg = 'You have successfully registered!'
    
    return resume_dict

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!' 
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'],      email = session['email'])
        
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/admin')
def admin():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('admin.html', username=session['username'],email = session['email'], password=session['password'])
        
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/admin_profile')
def admin_profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('admin_profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()

