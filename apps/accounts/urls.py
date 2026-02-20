from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('set-password/', views.set_password_view, name='set_password'),
    path('create-doctor/', views.AdminCreateDoctorView.as_view(), name='admin_create_doctor'),
]
