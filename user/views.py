from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from .models import User, Ticket, Payroll
from functools import wraps
from openai import OpenAI
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
import os
import inspect

#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def custom_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.__contains__("user_id"):
            if "user" in inspect.getfullargspec(function).args:
                user = User.objects.get(id=request.session["user_id"])
                kwargs["user"] = user
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

            match user.role:
                case User.Role.USER:
                    return redirect("home")
                case User.Role.ADMIN:
                    return redirect("admin")
                case _:
                    raise ValueError(f"Invalid user role: {user.role}")

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
def payroll(request, user, id=None):
    if request.method == "POST":
        if user.role != User.Role.ADMIN:
            return redirect("login")

        payroll = Payroll()
        payroll_user = User.objects.get(id=request.POST.get("user_id"))
        payroll.amount = request.POST.get("amount")
        payroll.user = payroll_user
        payroll.save()

        return redirect("admin")

    payrolls = []

    if id is not None:
        payrolls = Payroll.objects.filter(user__id=id)
    else:
        payrolls = Payroll.objects.filter(user__id=request.session["user_id"])

    context = { "payrolls": payrolls }

    return render(request, "payroll.html", context=context)

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

@custom_login_required
def admin(request):
    user = User.objects.get(id=request.session["user_id"])
    if user.role != User.Role.ADMIN:
        return redirect("login")

    users = User.objects.all()

    context = { "users": users }

    return render(request, "admin.html", context)
