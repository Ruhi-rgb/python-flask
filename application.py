import os
import time
import requests
import json
from helpers import *

from flask import Flask, session, logging, render_template, request, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
#from passlib.hash importpbkdf2_sha256
from datetime import date
from datetime import datetime

app = Flask(__name__)

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

goodreads_key = 'v0gMvbiAs39z7uZnf2y2dA'
app.run()
book1 = "global"

if __name__ == "__main__":

    app.secret_key="v0gMvbiAs39z7uZnf2y2dA"
    app.run(debug=True)
    session.clear()

#index (main route)
@app.route("/")
def index():
    try:
        id = session["user_id"]
    except:
        return render_template("index.html", info_msg="You are not logged in")
    return render_template("index.html")

#login user_id
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()

        if usernamedata is None:
            flash("No username","danger")
            return render_template("login.html")
        else:
            for password_data in passworddata:
                if sha256_crypt.verify(password,password_data):
                    session["username"] = username

                    flash("You are now login","success")
                    return render_template("search.html")
                else:
                    flash("incorrect password","danger")
                    return render_template("login.html")

    return render_template('login.html', error = error)

#Register USer
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")
        secure_password = sha256_crypt.encrypt(str(password))

        if password == confirmpassword:
            db.execute("INSERT INTO users(username, fullname, password) VALUES(:username, :fullname, :password)", {"username": username, "fullname":fullname, "password":secure_password})
            db.commit()
            flash("You are Registered and can Login Now","success")
            return render_template("login.html")
        else:
            flash("password does not match", "danger")
            return render_template("register.html")

    return render_template("register.html")


#Logout User
@app.route("/logout")
def logout():
    #session.clear()
    session["username"] = null
    flash("You are now logged out", "success")
    return redirect(url_for('login'))

#search for a book
@app.route("/search")
def search():
    return render_template("search.html")
    """
    if request.method == "POST":
        if request.form.get("search"):
            search = request.form.get("search").lower()
            if request.args.get("search"):
                search = request.args.get("search").lower()
                search1 = "%" + search + "%"
                books = db.execute("SELECT * FROM books WHERE lower(title) LIKE :search OR lower(author) LIKE:search OR lower(isbn) LIKE :search", {"search": search1}).fetchall()
                return render_template("search.html", books=books)
    """
#My account page
@app.route("/account", methods=["GET"])
def account():
    user = db.execute("SELECT * FROM users WHERE id = :user_id", {"user_id":session["user_id"]}).fetchone()
    return render_template("account.html", user = user)

#Book page
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        id = request.args.get("id")
        book = db.execute("SELECT * FROM books WHERE id = :id", {"id":id}).fetchall()
        isbn = book[0]['isbn']
        global book1
        book1=book[0]
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_key, "isbns":isbn})
        book_id = book[0]['id']
        reviews = db.execute("SELECT * FROM reviews WHERE book_id= :book_id", {"book_id": book_id}).fetchall()
        names=[]
        for review in reviews:
            userid = review['user_id']
            username = db.execute("SELECT * FROM users WHERE id = :id", {"id": userid}).fetchone()['username']
            names.append(username)
            print(reviews)
            return render_template("book.html", book=book[0], review=res.json()['books'][0], reviews=reviews, names=names)

#search for or write a review
@app.route("/review", methods=["GET", "POST"])
def review():
    if request.method == "POST":
        global book1
        bookid = book1['id']
        try:
            user_id = session["user_id"]
            comment = request.form.get("comment")
            stars = int(request.form.get("stars"))
            res = request.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_key, "isbns": book1['isbn']})
            reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": bookid}).fetchall()
            names = []
            for review in reviews:
                userid = review['user_id']
                username = db.execute("SELECT * FROM users WHERE id = :id", {"id": userid}).fetchone()['username']
                names.append(username)
                reviews1 = db.execute("SELECT * FROM reviews WHERE user_id= :user_id AND book_id=:book_id;", {"user_id": user_id, "book_id":bookid}).fetchone()
                if reviews1 is None:
                    db.execute("INSERT INTO reviews (book_id, user_id, comment, postdate,stars) VALUES (:book_id, :user_id, :comment, :postdate, :stars);", {"book_id": bookid, "user_id": user_id, "comment": comment, "postdate": postdate, "stars": stars})
                    username1 = db.execute("SELECT * FROM users WHERE id = :id", {"id": session["user_id"]}).fetchone()
                    print(username)
                    db.execute("UPDATE users SET review_count = count WHERE id= :user_id", {"count":username1['review_count'] + 1, "user_id": user_id})
                    db.commit()
                    reviews = db.execute("SELECT * FROM reviews WHERE book_id = : book_id", {"book_id": bookid}).fetchall()
                    names = []
                    for review in reviews:
                        userid= review['user_id']
                        username = db.execute("SELECT * FROM users WHERE id = :id", {"id" : userid}).fetchone()['username']
                        names.append(username)
                        return render_template("book.html", book=book1, review=res.json()['books'][0], reviews = reviews, names=names, success_msg="You have successfully written a review for this book")
                    else:
                        return render_template("book.html", book=book1, review=res.json()['books'][0], reviews = reviews, names=names, danger_msg="You have already written a review for this book.you can not write another review")

        except KeyError:
            res = request.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_key,"isbns":book1['isbn']})
            reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id":bookid}).fetchall()
            names = []
            for review in reviews:
                userid = review['user_id']
                username = db.execute("SELECT * FROM users WHERE id = :id", {"id":userid}).fetchone()['username']
                names.append(username)
                return render_template("book.html", book=book1, review=res.json()['books'][0], reviews = reviews, name=names, danger_msg="ERROR! you are not loggedin.Need to Login to post a review")

#Return information about book when api is given
@app.route("/api/<path>", methods=["GET","POST"])
def api(path):
    book1 = db.execute("SELECT * FROM books WHERE isbn = isbn", {"isbn": path}).fetchone()
    if book1 is None:
        abort(404)
    book = list(book1)
    try:
        avg = db.execute("SELECT AVG(stars) FROM review WHERE book_id = :id", {"id":book[0]}).fetchone()[0]

    except:
        avg = 0
    try:
        rev = db.execute("SELECT COUNT(comment) FROM reviews WHERE book_id = :id", {"id": book[0]}).fetchone()[0]

    except:
        rev = 0
    book.append(path)
    book.append(rev)
    try:
        book.append(round(float(avg),2))
    except:
        book.append(0)
    list1 = ['title', 'author', 'year', 'isbn', 'review_count', 'average_score']
    book.pop(0)
    book.pop(0)
    ans = dict(zip(list1, book))
    return ans

if __name__ == "__main__":
    app.run(debug=True)
    main()
