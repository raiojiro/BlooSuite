from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from bloosuite import settings
from .models import *
from functools import wraps
from django.http import HttpResponseNotAllowed, FileResponse
import google.generativeai as gemini
from dotenv import load_dotenv
import os
import inspect
import random, string

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
        
        elif request.POST.get("deletegroup"):
            group_id = request.POST.get("delete_group_id")
            group = User_group.objects.get(id=group_id)
            try:
                group.delete()
            except:
                pass      
        elif request.POST.get("addgroup"):
            name = request.POST.get("groupname")
            users = request.POST.getlist("userlist[]")
            print(users)
            new_group = User_group.objects.create(name=name)
            new_group.save()
            new_group.users.add(request.session["user_id"])
            for user in users:
                print(user)
                if user is not None:
                    if User.objects.filter(id=user).exists():
                        new_group.users.add(user)
            new_group.save()
        elif request.POST.get("addproject"):
            name = request.POST.get("projectname")
            description = request.POST.get("projectdescription")
            group_id = request.POST.get("group")
            group = User_group.objects.get(id=group_id)
            list = request.POST.getlist("projectlist[]")
            new_project = Project.objects.create(name=name, description = description, group=group)
            new_project.save
            for item in list:
                list = ToDoItem(title=item)
                list.save()
                new_project.list.add(list.id)
            new_project.save()
    groups = User_group.objects.filter(users=request.session["user_id"])
    projects = Project.objects.filter(group__users=request.session["user_id"], status=False).order_by('created_at')
    users = User.objects.only("id" , "name").order_by("name")
    context = {"groups":groups, "projects":projects, "users":users}

    if request.method == "POST":
        if request.POST.get("updategroup"):
            group_id = request.POST.get("group_id")
            group = User_group.objects.get(id=group_id)
            group_users = group.users.all()
            if request.POST.getlist("updategroup_userlist[]"):
                group.name = request.POST.get("group_name")
                users = request.POST.getlist("updategroup_userlist[]")
                group.users.clear()
                group.users.add(request.session["user_id"])
                for user in users:
                    if User.objects.filter(id=user).exists():
                        group.users.add(user)
                group.save()
            else:
                context["group_to_update"] = group
                context["group_users"] = group_users
            group.save()
    return render(request, "home.html", context)

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            return render(request, "login.html", {"error": "Invalid username or password"})
        
        if check_password(password, user.password):
            request.session["user_id"] = user.id
            match user.role:
                case User.Role.USER:
                    request.session["user_role"] = "user"
                    return redirect("home")
                case User.Role.ADMIN:
                    request.session["user_role"] = "admin"
                    return redirect("admin")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        activation_code = request.POST.get("activation_code")
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            new_user = User.objects.get(activation_code=activation_code)
        except:
            return render(request, {"error" : "Invalid activation code. Please contact the administrator."})
        else:   
            if User.objects.filter(username=username).exists():
                context = {"error" :"Username already exists"}
                return render(request, "register.html", context)
            else:
                new_user.username = username
                new_user.password = make_password(password)
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
def payroll(request, user, id=None, file=None):

    if request.method == "POST":
        if user.role != User.Role.ADMIN:
            return redirect("login")
        if request.POST.get("download"):
            file = Payroll.objects.get(id=request.POST.get("download")).payslip
            response = FileResponse(file.open(mode='rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{file.name}"'
            return response
        payroll_user = User.objects.get(id=request.POST.get("user_id"))
        amount = request.POST.get("amount")
        payroll = Payroll.objects.create(amount=amount, user=payroll_user)
        print(request.FILES.get("payslip"))
        if request.FILES.get("payslip") is not None:
            payroll.payslip = request.FILES.get("payslip")
        payroll.save()

    payrolls = []
    if id is not None:
        payrolls = Payroll.objects.filter(user__id=id).order_by("-created_at")
    else:
        payrolls = Payroll.objects.filter(user__id=request.session["user_id"]).order_by("-created_at")

    context = { "payrolls": payrolls }
    if user.role == User.Role.ADMIN:
        context["users"] = User.objects.only("id", "name")

    return render(request, "payroll.html", context=context)


@custom_login_required
def tickets(request):
    if request.method == "POST":
        if request.POST.get("solved"):
            ticket = Ticket.objects.get(id=request.POST.get("solved"))
            ticket.delete()

    if request.session["user_role"] == "admin":
        tickets = Ticket.objects.all().order_by("-created_at")
    else:
        tickets = Ticket.objects.filter(user=request.session["user_id"]).order_by("-created_at")

    context = { "tickets": tickets }
    return render(request, "tickets.html", context=context)

@custom_login_required
def ticket(request):
    if request.method != "POST":
        return redirect(tickets)

    title = request.POST.get("title")
    content = request.POST.get("content")
    user = User.objects.get(id=request.session["user_id"])
    new_ticket = Ticket(title=title, content=content, user=user)
    new_ticket.save()

    return redirect("tickets")

@custom_login_required
def admin(request):
    error, new_activation_code = None, None
    user = User.objects.get(id=request.session["user_id"])
    if user.role != User.Role.ADMIN:
        return redirect("login")
    if request.method == "POST":
        if request.POST.get("createuser"):
            name = request.POST.get("name")
            email = request.POST.get("email")
            activation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            while User.objects.filter(activation_code=activation_code).exists():
                activation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            try:
                new_user = User.objects.create(name=name, email=email, activation_code=activation_code, role=User.Role.USER)
                new_user.save()
                new_activation_code = new_user.activation_code
            except Exception as e:
                error = e
        if request.POST.get("deleteuser"):
            if User.objects.filter(id=request.POST.get("id")).exists():
                user = User.objects.get(id=request.POST.get("id"))
                user.delete()

    users = User.objects.all()

    context = { "users": users }
    if error is not None:
        context["error"] = error
    elif new_activation_code is not None:
        context["activation_code"] = new_activation_code

    return render(request, "admin.html", context)

@custom_login_required
def projects(request, id=None):
    project = Project.objects.get(id=id, group__users=request.session["user_id"])
    if request.method == "POST":
        todoitem = project.list.get(id=request.POST.get("id"))
        if request.POST.get("download"):
            file = todoitem.file
            response = FileResponse(file.open(mode='rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{file.name}"'
            return response
        todoitem.title = request.POST.get("title")
        todoitem.description = request.POST.get("description")
        if request.FILES.get("file") is not None:
            file = request.FILES.get("file")
            if todoitem.file is not None:
                todoitem.file.delete()
            todoitem.file = file
            todoitem.save()
        status = request.POST.get("status")
        print(status)
        if status == "True":
            todoitem.status = True
        else:
            todoitem.status = False
        todoitem.save()
    user = User.objects.get(id=request.session["user_id"])    
    if project is not None:
        context = { "project": project }
        return render(request, "projects.html", context)
    else:
        return redirect("home")
    
@custom_login_required
def account(request):
    user = User.objects.get(id=request.session["user_id"])
    context = {"user": user}
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        user.name = name
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            context["email_error"] = "Email already exists"
        else:
            user.email = email
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            context["username_error"] = "Username already exists"
        else:
            user.username = username
        if password is not None:
            user.password = make_password(password)
        user.save()
    return render(request, "account.html", context)


        
