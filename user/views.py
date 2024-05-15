from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import User

def login(request):
    return render(request, "login.html")

def register(request):
    if request.method == 'POST':
        new_user = User()
        new_user.name = request.POST.get("name")
        new_user.username = request.POST.get("username")
        new_user.email = request.POST.get("email")
        new_user.password = make_password(request.POST.get("password"))
        new_user.save()
        data = User.objects.all()
        context = {"user":data}
        return redirect('login')
    return render(request,"register.html")
