from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("home/", views.index , name="home"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("payroll/", views.payroll, name="payroll"),
    path("payroll/<int:id>/", views.payroll, name="payroll"),
    path("tickets/", views.tickets, name="tickets"),
    path("ticket/", views.ticket, name="ticket"),
    path("logout/", views.logout, name="logout"),
    path("admin/", views.admin, name="admin"),
    path("projects/<int:id>/", views.projects, name="projects"),
]
