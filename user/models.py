from django.db import models
from datetime import date

# Create your models here.

class User(models.Model):
    class Role(models.TextChoices):
        USER = "USER"
        ADMIN = "ADMIN"
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=5, choices=Role.choices, default=Role.USER)
    activation_code = models.CharField(unique=True, max_length=100, blank=True, null=True)

class Ticket(models.Model):
    title = models.TextField()
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ToDoItem(models.Model):
    title = models.TextField()
    description = models.TextField()
    file = models.FileField(upload_to='', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False, choices=((False, "pending"),(True, "completed")))

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
    payslip = models.FileField(upload_to='', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)