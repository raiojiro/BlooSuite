from django.db import models

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
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('completed', 'Completed')))

class Project(models.Model):
    name = models.TextField()
    description = models.TextField()
    list = models.ManyToManyField(ToDoItem)
    users = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

class User_group(models.Model):
    name = models.TextField()
    users = models.ManyToManyField(User)
