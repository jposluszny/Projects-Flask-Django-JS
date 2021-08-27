from flask import Flask
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv, os

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

# Create table books
db.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL,\
    title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL,\
    user_id INTEGER REFERENCES users )")

# Create table reviews
db.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, comment VARCHAR NOT NULL,\
    rating INTEGER NOT NULL, book_id INTEGER REFERENCES books, user_id INTEGER REFERENCES books )")
db.commit()

# Insert data into books' table
with open("books.csv") as file:
    reader = csv.reader(file)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES \
               (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book {title} to database.")
    db.commit()
