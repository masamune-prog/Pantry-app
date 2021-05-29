import os
import json
import random
import re 

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from datetime import datetime


from helpers import apology, login_required


# Configure application
app = Flask(__name__)
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
mail = Mail(app)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("DATABASE_URL"))
if db.startswith("postgres://"):
    db = db.replace("postgres://", "postgresql://", 1)

# Make sure API key is set
if not os.environ.get("MAIL_DEFAULT_SENDER"):
    raise RuntimeError("MAIL_DEFAULT_SENDER not set")


@app.route("/", methods=["GET", 'POST'])
@login_required
def index():
    """Show food in storeroom"""
    if request.method == 'POST':

        #For handling button presses for cancelling food item
        return apology('TODO')


    else:
        items = db.execute('SELECT item,user_id,time,expiry_date,item_id FROM items WHERE family_id = ?', session['family_id'])
        num_food = db.execute('SELECT COUNT(item) FROM items WHERE family_id = ?', session['family_id'])[0]['COUNT(item)']
        for i in range(int(num_food)):
            item = items[i]['item']
            user_id = items[i]['user_id']
            time = items[i]['time']
            expiry_date = items[i]['expiry_date']
        return render_template("index.html", items = items)

@app.route('/delete', methods = ["GET", "POST"])
@login_required
def delete():
    brought_user_id = db.execute("SELECT user_id FROM items WHERE item_id = ? AND family_id = ?", request.form['item_to_delete'], session['family_id'])[0]['user_id']
    db.execute('DELETE FROM items where item_id = ? AND family_id = ? AND user_id = ?', request.form['item_to_delete'], session['family_id'], brought_user_id)


    return redirect(url_for('index'))

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():

    """Show history of food in storeroom"""
    items = db.execute('SELECT item,user_id,time_brought,expiry_date FROM history WHERE family_id = ?', session['family_id'])
    num_food = db.execute('SELECT COUNT(item) FROM history WHERE family_id = ?', session['family_id'])[0]['COUNT(item)']
    for i in range(int(num_food)):
        item = items[i]['item']
        user_id = items[i]['user_id']
        time = items[i]['time_brought']
        expiry_date = items[i]['expiry_date']
    return render_template("history.html", items=items)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register for account"""
    if request.method == "POST":
        family_id = request.form.get('family_id')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('verify')
        #Implement input checking
        if not request.form.get('family_id'):
            return apology('no family id')
        if not request.form.get('username'):
            return apology('no username')
        if not request.form.get('password'):
            return apology('no password')
        if request.form.get('password') != request.form.get('verify'):
            return apology('no matching password')
        check_username = db.execute('SELECT COUNT(user_id) FROM users WHERE user_id = ? AND family_id = ?',username, family_id)
        if int(check_username[0]['COUNT(user_id)']) != 0:
            return apology('username is already used by someone in family')
        check_fam_id = db.execute('SELECT COUNT(family_id) FROM users WHERE  family_id = ?',family_id)
        if int(check_fam_id[0]['COUNT(family_id)']) != 0:
            return apology('Family Id used by someone')


        #Register user
        get_hash = generate_password_hash(password)
        db.execute('INSERT INTO users(family_id,user_id,hash,email) VALUES(:family_id,:user_id,:hash,:email)', family_id = family_id , user_id = username, hash = get_hash, email = email)
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        family_id = request.form.get('family_id')

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE user_id = ? AND family_id = ?", request.form.get("username"),family_id)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        session['family_id'] = family_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/brought', methods = ["GET", "POST"])
@login_required
def brought():
    '''Input Stuff brought'''
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        item = request.form.get('item')
        expiry = request.form.get('expiry')
        #Handle errors
        if not item:
            return apology('Enter Item Name')
        if not quantity:
            return apology('Enter quantity')
        if not expiry:
            return apology('Enter Expiry Date')
        if int(quantity)<=0:
            return apology('Enter Valid Quantity')
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(int(quantity)):
            db.execute('INSERT INTO items(item,family_id,user_id,time,expiry_date) VALUES(:item,:family_id,:user_id,:time,:expiry_date)', item = item, family_id = session['family_id'], user_id = session['user_id'], time = time, expiry_date = expiry)
            db.execute('INSERT INTO history(item,family_id,user_id,time_brought,expiry_date) VALUES(:item,:family_id,:user_id,:time_brought,:expiry_date)', item = item, family_id = session['family_id'], user_id = session['user_id'], time_brought = time, expiry_date = expiry)

        return redirect('/')

    else:
        return render_template('brought.html')



@app.route("/reset", methods=["GET", "POST"])
def reset():
    """RESET Password using email"""
    if request.method == "POST":
        reset_family_id = request.form.get('family_id')
        reset_user_id = request.form.get('username')
        family_id_exists = db.execute('SELECT COUNT(family_id) FROM users WHERE family_id = ?',reset_family_id)[0]['COUNT(family_id)']
        user_id_exists = db.execute('SELECT COUNT(user_id) FROM users WHERE family_id = ? AND user_id = ?',reset_family_id,reset_user_id)[0]['COUNT(user_id)']
        if not reset_family_id:
            return apology ('no family_id')
        if not reset_user_id:
            return apology ('no username')
        if int(family_id_exists) == 0:
            return apology ('no family_id')
        if int(user_id_exists) == 0:
            return apology ('no family_id')


        else:
            reset_email = db.execute('SELECT email FROM users WHERE user_id = ? AND family_id = ?', reset_user_id, reset_family_id)[0]['email']
            verify_code = random.randint(1000, 9999)
            message = Message("Here is your reset code:" + str(verify_code) + "!", recipients=[reset_email])
            mail.send(message)
            db.execute('UPDATE users SET reset_code = ? WHERE user_id = ? AND family_id = ?', verify_code, reset_user_id, reset_family_id)
            session['reset_username'] = reset_user_id
            session['reset_family_id'] = reset_family_id
            return render_template('reset_confirmed.html')

    else:
        return render_template('reset.html')
@app.route("/reset_confirmed", methods=["GET", "POST"])
def reset_confirmed():
    """Verify code and update the database"""
    if request.method == "POST":
        verification = request.form.get('verify')
        new_password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        if not verification:
            return apology('Enter verification code')
        if not new_password:
            return apology('Enter password')
        code = db.execute('SELECT reset_code FROM users WHERE user_id = ? AND family_id = ?', session['reset_username'], session['reset_family_id'])[0]['reset_code']
        if int(code) == int(verification) and new_password == repeat_password:
            hashed = generate_password_hash(new_password)
            db.execute('UPDATE users SET hash = ? WHERE user_id = ? AND family_id = ?',hashed ,session['reset_username']  ,session['reset_family_id'])
            session.clear()
            return render_template('login.html')
        elif int(code) != int(verification):
            return apology('Wrong code')
        elif new_password != repeat_password:
            return apology('Password not matched')





    else:
        return render_template('login.html')

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('verify')
        if not request.form.get('username'):
            return apology('no username')
        if not request.form.get('password'):
            return apology('no password')
        if request.form.get('password') != request.form.get('verify'):
            return apology('no matching password')
        check_username = db.execute('SELECT COUNT(user_id) FROM users WHERE user_id = ? AND family_id = ?',username, session['family_id'])
        if check_username[0]['COUNT(user_id)'] != 0:
            return apology('username is already used by someone in family')
        #Register user
        get_hash = generate_password_hash(password)
        db.execute('INSERT INTO users(family_id,user_id,hash,email) VALUES(:family_id,:user_id,:hash,:email)', family_id = session['family_id'] , user_id = username, hash = get_hash, email = email)
        return redirect("")


    else:
        return render_template('add.html')



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
