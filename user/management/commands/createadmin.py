#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from user.models import User

class Command(BaseCommand):
    help = "Creates an admin user"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str)
        parser.add_argument("username", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        admin = User()
        admin.username = options["username"]
        admin.name = options["name"]
        admin.email = options["email"]
        admin.password = make_password(options["password"])
        admin.role = User.Role.ADMIN
        admin.save()