import os

from flask import Flask, session
from flask_session import Session
from flask import Flask, render_template, redirect, url_for, request, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required  


import requests

app = Flask(__name__)

#HEROKU_URI FOR SETTING UP  postgres://exbggyfzvhnnoa:a641263e7716306e5115314f58bd70c7f4ad6790d405a550e762c2e4ed1f8eb9@ec2-34-197-212-240.compute-1.amazonaws.com:5432/dd974uhsrc5dfg



# Check for environment variable
if not os.getenv("DATABASE_URL"):
   raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return "COVID ideation challenge"


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():

    """ Log user in """
    # forget any user_id
    session.clear()

    username = request.form.get("username")
    #password = request.form.get("password") #iski jroort nhi, aage include kr diya hai

    #user reached route via submitting a form through POST
    if request.method == 'POST':

        #ensure that username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="you must provide username")

        #ensure that password was submitted #iski jroort nhi, aage include kr diya hai
        #if not request.form.get("password"):
         #   return render_template("error.html", message="you must provide password")

        rows = db.execute("SELECT * FROM users where username = :username", {"username": username})
        result = rows.fetchone()

        #ensuring username exists and password is correct
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")

        #Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        #redirect user to home page
        return redirect("/")

        #if user reached the route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    """Log user out"""

    #forget any user ID
    session.clear()

    #redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """

    #forget any user_id
    session.clear()
    
    #if user reached route via POST
    if request.method == "POST":

        #ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="you must provide a username")
        
        #quering database for username
        userCheck = db.execute("SELECT * FROM users WHERE username= :username",
                                {"username":request.form.get("username")}).fetchone()

        #check if username already exist
        if userCheck:
            return render_template("error.html", message="this username already exists")

        #ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        #ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="must provide confirmation")

        #checking whether the passwords are equal
        elif not request.form.get("confirmation") == request.form.get("password"):
            return render_template("error.html", message="passwords didn't match")

        #Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        #insert register into DB
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                    {"username":request.form.get("username"),
                    "password":hashedPassword})

        #commiting changes to database
        db.commit()

        flash('Account created', 'info') #ye chla nhi pta nhi kyu, bad me dekhta

        #redirect user to login page
        return redirect("/login")

    #if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


#KAFI MACHAYA, 150 LINES
        


