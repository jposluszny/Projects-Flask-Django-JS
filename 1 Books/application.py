from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
   raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create table if it doesn't exist
db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL,\
     password VARCHAR NOT NULL)")
db.commit()

@app.route("/", methods=["POST", "GET"])
def index():
    # Check if user is logged in
    if session.get("started"):
        return render_template("logged.html", name=session["started"])

    # Check if user name was submitted and user exists
    session["message"] = ""
    name = request.form.get("name")
    if name != None:
        password = request.form.get("password")
        if name == "":
            session["message"] = "Enter a name!"
            return render_template("index.html", message=session["message"])
        if password == "":
            session["message"] = "Enter a password!"
            return render_template("index.html", message=session["message"])
        if db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).rowcount == 0:
            session["message"] = "User doesn\'t exists!"
            return render_template("index.html", message=session["message"])
        password_db = db.execute("SELECT password FROM users WHERE name = :name", {"name": name}).fetchone()

        # Validate password
        for i in password_db:
            if i != password:
                session["message"] = "Wrong password!"
                return render_template("index.html", message=session["message"])
            else:
                session["started"] = name
                user_id = db.execute("SELECT id FROM users WHERE name = :name", {"name": name}).fetchone()
                session["user_id"] = user_id.id
                return render_template("logged.html", name=name)
        if session.get("started"):
            return render_template("logged.html", name=name)
    return render_template("index.html")

@app.route("/registration", methods=["POST", "GET"])
def registration():
    # Check if user is logged in
    if session.get("started"):
            return redirect("/")

    # Check if all data were submitted
    session["r_message"] = ""
    name = request.form.get("name")
    if name != None:
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        if name == "":
            session["r_message"] = "Enter a name!"
            return render_template("registration.html", r_message=session["r_message"])
        if password == "":
            session["r_message"] = "Enter a password!"
            return render_template("registration.html", r_message=session["r_message"])
        if repassword == "":
            session["r_message"] = "Repeat password!"
            return render_template("registration.html", r_message=session["r_message"])
        if password != repassword:
            session["r_message"] = "Passwords don\'t match!"
            return render_template("registration.html", r_message=session["r_message"])

        # Check if user doesn't exist
        row_number = db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).rowcount
        if row_number > 0:
            session["r_message"] = "User already exists!"
            return render_template("registration.html", r_message=session["r_message"])

        # Insert new user into database
        if row_number == 0:
            try:
                db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": password})
                db.commit()
                result = db.execute("SELECT name FROM users WHERE name = :name", {"name": name}).fetchone()
                for i in result:
                    name = i
                return render_template("success.html", name=name)
            except:
                session["r_message"] = "Something went wrong, try again."
                return render_template("registration.html", r_message=session["r_message"])
    return render_template("registration.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/search", methods=["POST", "GET"])
def search():
    # If user is logged in and return result of search
    if session.get("started"):
        search = request.form.get("search")
        if search != None:
            query = "%"+search+"%"
            books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn or title LIKE :title or author LIKE :author",
                                {"isbn": query, "title": query, "author": query}).fetchall()
            if books == []:
                message = "There were no matches"
            else:
                message = f"Results of query {search}"
            return render_template("logged.html", books=books, message=message)
    return redirect("/")

@app.route("/book/<int:book_id>", methods=["POST", "GET"])
def book(book_id):
    if session.get("started"):
        # Make sure book exists.
        book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        if book is None:
            message = "No such book."
        else:
              message = "Book\'s details:"

        # Get average rate and number of rates from goodreads
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                   params={"key": "0QFzT7cpHrHc0ZUe95Epg", "isbns": book.isbn})
        if res.status_code != 200:
            raise Exception("ERROR: API request unsuccessful.")
        good_reads_data = res.json()
        average_rating = good_reads_data["books"][0]["average_rating"]
        work_ratings_count = good_reads_data["books"][0]["work_ratings_count"]

        # Get reviews and rating from database
        reviews = db.execute("SELECT comment, rating, name FROM reviews JOIN users ON reviews.user_id = users.id \
                             WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
        rate = db.execute("SELECT rating FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
        rating_sum = 0
        for i in rate:
            for j in i:
                rating_sum += j
        if len(rate) != 0:
            session["ourweb_average_rating"] = round(rating_sum / len(rate), 2)
        else:
            session["ourweb_average_rating"] = 0
        session["ourweb_work_ratings_count"] = len(rate)

        # Get reviews from website
        comment = request.form.get("comment")
        rating = request.form.get("rating")
        instruction = ""
        if comment != None or rating != None:
            if comment == "":
                instruction = "Review the book!"
                return render_template("book.html", average_rating=average_rating, \
                            work_ratings_count=work_ratings_count, instruction=instruction,\
                            book=book, message=message, reviews=reviews)
            if rating not in ["1", "2", "3", "4", "5"]:
                instruction = "Rate the book on a scale of 1 to 5!"
                return render_template("book.html", average_rating=average_rating, \
                            work_ratings_count=work_ratings_count, instruction=instruction,\
                            book=book, message=message, reviews=reviews)

            # Check if user can review the book
            reviewed_books = db.execute("SELECT book_id FROM reviews WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()
            for i in reviewed_books:
                if i.book_id == book_id:
                    instruction = "You can\'t review the same book twice!"
                    return render_template("book.html", average_rating=average_rating, \
                            work_ratings_count=work_ratings_count, instruction=instruction,\
                            book=book, message=message, reviews=reviews)

            # Insert into database new review
            db.execute("INSERT INTO reviews (comment, rating, book_id, user_id) \
                       VALUES (:comment, :rating, :book_id, :user_id)", \
                       {"comment": comment, "rating":rating, "book_id": book_id, "user_id": session["user_id"]})
            db.commit()

            # Update data displayed in browser
            reviews = db.execute("SELECT comment, rating, name FROM reviews JOIN users ON reviews.user_id = users.id \
                             WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
            rate = db.execute("SELECT rating FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
            rating_sum = 0
            for i in rate:
                for j in i:
                    rating_sum += j
            if len(rate) != 0:
                session["ourweb_average_rating"] = round(rating_sum / len(rate), 2)
            else:
                session["ourweb_average_rating"] = 0
            session["ourweb_work_ratings_count"] = len(rate)

        return render_template("book.html", average_rating=average_rating, \
                            work_ratings_count=work_ratings_count, instruction=instruction,\
                            book=book, message=message, reviews=reviews)
    return redirect("/")


@app.route("/api/<isbn>")
def book_api(isbn):
    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422

    # Count rates from our users.
    rate = db.execute("SELECT rating FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
    rating_sum = 0
    for i in rate:
        for j in i:
            rating_sum += j
    if len(rate) != 0:
        ourweb_average_rating = round(rating_sum / len(rate), 2)
    else:
        ourweb_average_rating = 0
    ourweb_work_ratings_count = len(rate)

    # Get average rate and number of rates from goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
               params={"key": "0QFzT7cpHrHc0ZUe95Epg", "isbns": book.isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    good_reads_data = res.json()
    average_rating = good_reads_data["books"][0]["average_rating"]
    work_ratings_count = good_reads_data["books"][0]["work_ratings_count"]

    # Create data for API
    return jsonify({
            "ISBN number": book.isbn,
            "Title": book.title,
            "Author": book.author,
            "Publication year": book.year,
            "Our web average rating": ourweb_average_rating,
            "Our web work ratings count": ourweb_work_ratings_count,
            "Goodreads web average rating": average_rating,
            "Goodreads web work ratings count": work_ratings_count
        })
