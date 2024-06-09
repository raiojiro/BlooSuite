from django.db import models
from datetime import date

# Create your models here.

class User(models.Model):
    class Role(models.TextChoices):
        USER = "USER"
        ADMIN = "ADMIN"
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=5, choices=Role.choices, default=Role.USER)

class Ticket(models.Model):
    title = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ToDoItem(models.Model):
    title = models.TextField()
    description = models.TextField()
    file = models.FileField(upload_to='files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD
    status = models.BooleanField(default=False)
=======
    status = models.BooleanField(default=False, choices=((False, "pending"),(True, "completed")))
>>>>>>> c1e2ca526980607ecbc663547c9084e155350b62

class Project(models.Model):
    def getlist(self):
        return ToDoItem.objects.filter(project=self.id)
    name = models.TextField()
    description = models.TextField()
    list = models.ManyToManyField(ToDoItem)
    group = models.ForeignKey('User_group', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class User_group(models.Model):
    name = models.TextField()
    users = models.ManyToManyField(User)

class Payroll(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)