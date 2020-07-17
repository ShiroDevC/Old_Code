'''
Module for the urls in this app. The urlpatterns define
which view can be accessed with which path. This allows
for easy routing in the app.

@author: Christian Breu <cbreu0@icloud.com>
'''
from django.urls import path

from . import views

# define app name to have a clear namespace when searchin urls (avoid doubles)
app_name = "blog"
urlpatterns = [path("", views.index, name="index"),
               path('<int:pk>/', views.DetailView.as_view(), name="detail"),
               path("register", views.RegisterView.as_view(), name="register"),
               path("login", views.LoginView.as_view(), name="login"),
               path("logout", views.logout, name="logout"),
               path("user", views.UserView.as_view(), name="user"),
               path("userchange", views.ChangeUserView.as_view(), name="userchange"),
               path("passwordchange", views.ChangePasswordView.as_view(), name="passwordchange")
               ]