from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from .models import User, Ticket
from functools import wraps
from django.http import HttpResponseNotAllowed
from openai import OpenAI
import os

#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def custom_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.__contains__("user_id"):
            return function(request, *args, **kwargs)
        else:
            return redirect("login")

    return wrap

@custom_login_required
def index(request):
    if request.method == "POST":

        return render(request, "home.html")
    return render(request, "home.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.get(username=username)

        if check_password(password, user.password):
            request.session["user_id"] = user.id
            return redirect("home")

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        new_user = User()
        new_user.username = request.POST.get("username")
        new_user.password = make_password(request.POST.get("password"))
        new_user.save()
        return redirect("login")

    return render(request, "register.html")

@custom_login_required
def logout(request):
    try:
        del request.session["user_id"]
    except KeyError:
        pass

    return redirect(login)

@custom_login_required
def payroll(request):
    return render(request, "payroll.html")

@custom_login_required
def tickets(request):
    tickets = Ticket.objects.all()
    context = { "tickets": tickets }
    return render(request, "tickets.html", context=context)

@custom_login_required
def ticket(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    title = request.POST.get("title")
    content = request.POST.get("content")

    new_ticket = Ticket(title=title, content=content)
    new_ticket.save()

    return redirect("tickets")
