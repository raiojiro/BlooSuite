from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from .models import *
from functools import wraps
from django.http import HttpResponseNotAllowed
import google.generativeai as gemini
from dotenv import load_dotenv
import os
import inspect

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
        if request.POST.get("mark_done") is not None:
            project_id = request.POST.get("project_id")
            project = Project.objects.get(id=project_id)
            project.status = True
            project.save()
        
        if request.POST.get("deletegroup") is not None:
            group_id = request.POST.get("updategroup")
            print(group_id)
            group = User_group.objects.filter(id=group_id)
            group.delete()

        if request.POST.get("updategroup") is not None:
            group_id = request.POST.get("group_id")
            group = User_group.objects.get(id=group_id)
            group.users.all().delete()
            users = request.POST.getlist("userlist[]")
            for user in users:
                if user is not None:
                    if User.objects.filter(id=user).exists():
                        b = User.objects.get(id=user)
                        group.users.add(b.id)
            group.save()
 
        if request.POST.get("selectgroup") is not None:
            group_id = request.POST.get("group_id")
            group = User_group.objects.get(id=group_id)
            users = User.objects.all()
            return render(request, "home.html", {"updategroup":group, "users":users})
        
        if request.POST.get("formtype") == "group":
            name = request.POST.get("groupname")
            users = request.POST.getlist("userlist[]")
            new_group = User_group.objects.create(name=name)
            new_group.save()
            new_group.users.add(request.session["user_id"])
            for user in users:
                if user is not None:
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
    projects = Project.objects.filter(group__users=request.session["user_id"], status=False).order_by('created_at')
    users = User.objects.order_by("name").only("id" , "name")
    return render(request, "home.html", {'projects':projects, "groups":groups, "users":users})

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

