from django.contrib import admin
from django.urls import path, include


from . import views

from students.views import studentRegister


from tutors.views import tutorRegister

urlpatterns = [
    path('', views.home, name="home_page"),
    path('registeras/', views.registerAs, name="register_as"),
    path('zohoverify/', views.zoho, name="zoho"),
    path('registeras/student/', studentRegister, name="student_register"),
    path('registeras/tutor/', tutorRegister, name="tutor_register"),
    path('signin/', views.signIn, name="sign_in"),
    path('signout/', views.signOut, name="sign_out"),
    path('tutors/', views.tutors, name="tutors"),
    path('tutors/<int:id>/', views.tutorDetail, name="tutor_detail"),
]
