import json
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from orders.forms import RegistrationForm
from .models import Dishes, Orders, Toppings
import datetime

def index(request):
    if not request.user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})
    # Get and render all items in pizza shop
    dishes = Dishes.objects.all()
    toppings = Toppings.objects.all()

    # Get regular pizza
    res_regular = Dishes.objects.filter(name__contains="Regular pizza")
    regular = extract(2, res_regular)

    # Get Sicilian pizza
    res_sicilian = Dishes.objects.filter(name__contains="Sicilian pizza")
    sicilian = extract(2, res_sicilian)
    res_special = Dishes.objects.filter(name__contains="Special")
    sicilian.extend(extract(0, res_special))

    # Get subs
    res_subs = Dishes.objects.filter(name__startswith="Sub")
    res_add =  Dishes.objects.filter(name__startswith="+")
    res_cheese = Dishes.objects.filter(name__startswith="Extra")
    l = extract(1, res_subs)
    add = extract(0, res_add)
    subs =  []
    # Place addings below the steak
    for i in l:
        subs.append(i)
        if i[0] == "Steak + Cheese":
            for j in add:
                subs.append(j)
    subs.extend(extract(0, res_cheese))

    # Get salad and pasta
    res_salad = Dishes.objects.filter(size="normal")
    salad = extract(0, res_salad)

    # Get dinner platters
    res_platters = Dishes.objects.filter(name__startswith="Dinner Platter")
    platters = extract(2, res_platters)

    context = {
        "user": request.user,
        "dishes": dishes,
        "toppings": toppings,
        "regular": regular,
        "sicilian": sicilian,
        "subs": subs,
        "salad": salad,
        "platters": platters,
        }
    return render(request, "orders/user.html", context)

def registration_view(request):
    if request.method == 'POST':
        # Send registration form to server with data if it is valid
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "orders/login.html", {"message": "Registration successful."})
        # Reder registration form and message with invalid credentials
        form = RegistrationForm()
        args = {'form':form, 'message': 'Invalid credentials.'}
        return render(request, "orders/registration.html", args)
    else:
        # Reder registration form
        form = RegistrationForm()
        args = {'form':form}
        return render(request, "orders/registration.html", args)

def login_view(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        # Get user credentials and try to login
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "orders/login.html", {"message": "Invalid credentials."})

def logout_view(request):
    # Log out user and reder index with a message
    logout(request)
    return render(request, "orders/login.html", {"message": "Logged out."})

def cart_view(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        # Get the user\'s order
        order = json.loads(request.POST.get("order"))
        if len(order) == 0:
            message = "To place an order you must add item to your cart."
        else:
            try:
                order_items = ''
                order_price = 0
                for i in order:
                    # Check if user ordered special pizza
                    if len(i) == 3:
                        item = Dishes.objects.get(pk = i[1])
                        order_items += str(item) + '; '
                        order_price += item.price
                        # Add toppings to special pizza
                        for e in [3, 4, 6, 9, 11]:
                            item = Toppings.objects.get(pk = e)
                            order_items += str(item) + '; '
                    # For dishes add price to total price and name to order's items
                    elif i[0] == 'Dishes':
                        item = Dishes.objects.get(pk = i[1])
                        order_items += str(item) + '; '
                        order_price += item.price
                    # For toppings add only name to order's items
                    else:
                        item = Toppings.objects.get(pk = i[1])
                        order_items += str(item) + '; '

                #Add date to the order
                d = datetime.datetime.now()
                date = d.strftime("%y %b %d %H:%M")
                #Create and save order to data base
                o = Orders(date=date, user=request.user, order=order_items, order_price=order_price)
                o.save()
                # Check database that everything is ok
                check = Orders.objects.last()
                if check.order == order_items:
                    message = 'Your order has been placed.'
                else:
                    message = 'Something went wrong. Please try again.'
            except:
                message = 'We can\'t connect data base. Please try again.'
    return HttpResponse(message)

def status_view(request):
    # Get user's orders with status
    user = request.user
    orders = Orders.objects.filter(user = user).order_by('-date')
    return render(request, "orders/status.html", {"user": user, "orders": orders})

# Extract data
def extract(n, res):
    l = []
    for i in res:
        if i.size == "large":
            l[-1].append(i)
        else:
            l.append([' '.join(i.name.split()[n:]), i])
    return l
