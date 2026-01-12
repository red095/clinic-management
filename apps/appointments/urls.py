from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.BookAppointmentView.as_view(), name='book_appointment'),
    path('<uuid:pk>/<str:action>/', views.AppointmentActionView.as_view(), name='appointment_action'),
]
