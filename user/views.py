from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import User

def index(request):
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

def payroll(request):
    return render(request, "payroll.html")
