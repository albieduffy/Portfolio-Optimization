import os
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, format_resp
from optimization import optimize

# Configure application
app = Flask(__name__)

# Templates are auto reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set local DB
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://upcdplssufzmnh:a4212931c2892c03fbdf8ef6d5e7ad24f299ee43569d61c892daad37011cfbfe@ec2-54-247-103-43.eu-west-1.compute.amazonaws.com:5432/d9ft8c6v3j3am2"

db = SQLAlchemy(app)

@app.route('/')
def running():
    return render_template('landing.html')

@app.route('/portfolio')
@login_required
def portfolio():
    try:
        result = format_resp(db.session.execute('SELECT ticker FROM positions WHERE user_id = :user_id ORDER BY ticker ASC', {'user_id': session['user_id']}))
        db.session.commit()

        symbols = [item['ticker'] for item in result]
        optimal_allocation = optimize(symbols)
        pie_data = [*optimal_allocation.values()]
        return render_template('portfolio.html', optimal_allocation=optimal_allocation, symbols=symbols, pie_data=pie_data)
    except:

        return render_template('portfolio.html')



@app.route('/update', methods=['POST'])
@login_required
def update():

    # POST
    if request.method == 'POST':

        result = format_resp(db.session.execute('INSERT INTO positions (ticker, user_id) VALUES(:ticker, :user_id) RETURNING ticker', {'ticker': request.form.get('ticker').upper(), 'user_id': session['user_id']}))
        db.session.commit()

        if not result:
            return redirect('/portfolio')

        else:
            return redirect('/portfolio')

@app.route('/delete', methods=['POST'])
@login_required
def delete():

    # POST
    if request.method == 'POST':

        result = format_resp(db.session.execute('DELETE FROM positions WHERE ticker = :ticker AND user_id = :user_id RETURNING :user_id', {'ticker': request.form.get('ticker').upper(), 'user_id': session['user_id']}))
        db.session.commit()

        if not result:
            return redirect('/portfolio')

        else:
            return redirect('/portfolio')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Clear user_id
    session.clear()

    # POST
    if request.method == 'POST':
        if request.method == "POST":
            if request.form.get("password") != request.form.get("confirmation"):
                return jsonify('Passwords do not match', 400)

            result = format_resp(db.session.execute("INSERT INTO users (username, password) VALUES(:username, :password) RETURNING id", {'username':request.form.get("username"), 'password':generate_password_hash(request.form.get("password"))}))
            db.session.commit()

            if not result:
                return redirect('/register')

            else:
                session["user_id"] = result

                return redirect("/portfolio")

    # GET
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear user_id
    session.clear()

    # POST route from form submission
    if request.method == 'POST':

        rows = format_resp(db.session.execute("SELECT * FROM users WHERE username = :username",
                          {'username':request.form.get("username")}))

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return redirect('/login')

        session["user_id"] = rows[0]["id"]

        return redirect("/portfolio")

    # GET route presents login form
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session
    session.clear()

    # Redirect to landing page
    return redirect('/')


if __name__ == "__main__":
    app.run()
