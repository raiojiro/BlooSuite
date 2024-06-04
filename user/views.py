from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from .models import *
from functools import wraps
from django.http import HttpResponseNotAllowed
import google.generativeai as gemini
from dotenv import load_dotenv
import os

'''
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini.configure(api_key=GOOGLE_API_KEY)
model = gemini.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("tell me a joke")
'''

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
        if request.POST.get("mark_done") is not None:
            project_id = request.POST.get("project_id")
            project = Project.objects.get(id=project_id)
            project.completed = True
            project.save()
        
        if request.POST.get("formtype") == "group":
            name = request.POST.get("groupname")
            users = request.POST.getlist("userlist[]")
            new_group = User_group.objects.create(name=name)
            new_group.save()
            new_group.users.add(request.session["user_id"])
            for user in users:
                if User.objects.filter(username=user).exists():
                    b = User.objects.get(username=user)
                    new_group.users.add(b.id)
            new_group.save()
        if request.POST.get("formtype") == "project":
            name = request.POST.get("projectname")
            description = request.POST.get("projectdescription")
            group_id = request.POST.get("group")
            group = User_group.objects.get(id=group_id)
            list = request.POST.getlist("projectlist[]")
            new_project = Project.objects.create(name=name, description = description, group=group)
            new_project.save
            for item in list:
                list = ToDoItem(title=list)
                list.save()
                new_project.list.add(list.id)
            new_project.save()
    groups = User_group.objects.filter(users=request.session["user_id"])
    projects = Project.objects.filter(group = [group for group in groups])
    users = User.objects.only("id" , "name").order_by("name")
    return render(request, "home.html", {'projects':projects, "groups":groups, "users":users})

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.get(username=username)

        if check_password(password, user.password):
            request.session["user_id"] = user.id
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        new_user = User()
        new_user.username = request.POST.get("username")
        if User.objects.filter(username=new_user.username).exists():
            return render(request, "register.html", {"error": "Username already exists"})
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
