from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from library.forms import RegistrationForm
from .models import books
from .models import borrowings
import csv
import random
import json
import datetime
# Create your views here.

def index_view(request):
    ## Upload books to database from csv file

    # with open("library/books.csv") as file:
    #     reader = csv.reader(file)
    #     for a, b, c, d in reader:
    #         o = books(isbn=a, title=b, author=c, year=d, quantity=5)
    #         o.save()

    # If user is not logged render index.html
    if not request.user.is_authenticated:
        return render(request, "library/index.html", {"message": None})
    else:
        #Load user books and send to user page
        context = load_user_books(request)
        context["message"] = None
        return render(request, "library/user.html", context)
    return render(request, "library/index.html")

def user_view(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        # Get user credentials and try to login
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #Redirect to index to load user books
            return HttpResponseRedirect(reverse("index"))
        else:
            message = {"message": "Invalid credentials."}
            return render(request, "library/index.html", {"message": "Invalid credentials."})


def search_view(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        query = request.POST.get("query").strip()
        #Load user books and send to user page
        context = load_user_books(request)
        # If return message if query was empty
        if len(query) == 0:
            context["message"] = "Type something to search for books."
            context["result"] = None
            return render(request, "library/user.html", context)

        else:
            try:
                # Search database and return result and message
                result = books.objects.filter(title__contains=query) | books.objects.filter(author__contains=query) |\
                books.objects.filter(isbn__contains=query)
                if result:
                    context["message"] = None
                    context["result"] = result
                else:
                    context["message"] = 'There was no matches.'
                    context["result"] = None
            except:
                context["message"] = 'There is something wrong. Please try again.'
                context["result"] = None
            return render(request, "library/user.html", context)


def book_view(request, i_isbn):
    # Get book details using isbn
    try:
        book = books.objects.get(isbn=i_isbn)
        return render(request, "library/book.html", {"book": book})
    except:
        return HttpResponse('You must click link from a user page to see book\'s details.')



def borrow_view(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        isbn = request.POST.get("isbn")
        try:
            book = books.objects.get(isbn=isbn)
            
            # Check how many books has been borrowed by the user (10 are allowed)
            borrowed_books = borrowings.objects.filter(user=request.user)
            if len(borrowed_books) >= 10:
                message = 'You can\'t borrow more than 10 books.'
                return HttpResponse(json.dumps({"message": message, "bookQuantity": book.quantity}))

            # Check if user has borrowed the book and haven't it returned
            user_books = borrowings.objects.filter(user=request.user).filter(book=book)
            if user_books:
                for i in user_books:
                    if i.status != 'returned':
                        message = 'You can\'t borrow the same book twice.'
                        return HttpResponse(json.dumps({"message": message, "bookQuantity": book.quantity}))

            # Check if there are books available
            num_of_books = book.quantity
            if num_of_books > 0:
                return_date = datetime.date.today() + datetime.timedelta(days=14)
                o = borrowings(user=request.user, book=book, return_date=return_date)
                o.save()
                book.quantity = num_of_books - 1
                book.save()
                book = books.objects.get(isbn=isbn)
                if (book.quantity + 1) == num_of_books:
                    message = 'You have borrowed the book: "' + str(book) + ' ".'
                else:
                    message = 'Something went wrong, please try again.'
            else:
                message = 'There is no book available.'
        except:
             message = 'Something went wrong, please try again.'

        return HttpResponse(json.dumps({"message": message, "bookQuantity": book.quantity}))


def history_view(request):
    # Get and render all books user have borrowed up to now
    history = borrowings.objects.filter(user=request.user)
    return render(request, "library/history.html", {"history": history})


def registration_view(request):
    if request.method == 'POST':
        # Send registration form to server with data if it is valid
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "library/index.html", {"message": "Registration successful. You can login now."})
        # Reder registration form and message with invalid credentials
        form = RegistrationForm()
        args = {'form':form, 'message': 'Invalid credentials.'}
        return render(request, "library/registration.html", args)
    # Reder registration form
    else:
        form = RegistrationForm()
        args = {'form':form}
        return render(request, "library/registration.html", args)

def logout_view(request):
    # Log out user and reder index with a message
    logout(request)
    return render(request, "library/index.html", {"message": "Logged out."})

# Helper function to get today's date and user's book with pending and borrowed status
def load_user_books(request):
    date = datetime.date.today()
    borrowed_books = borrowings.objects.filter(user=request.user).exclude(status="returned")
    if borrowed_books:
        context = {"borrowed_books": borrowed_books, "message_books": None, "date": date}
    else:
        context = {"borrowed_books": None, "message_books": "You have no books in your account.", "date": date}
    return context
