from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

from students.views import studentRegister


from tutors.views import tutorRegister

from academy.views import academyRegister




urlpatterns = [
    path('', views.home, name="home_page"),
    path('registeras/', views.registerAs, name="register_as"),
    path('registeras/student/', studentRegister, name="student_register"),
    path('registeras/tutor/', tutorRegister, name="tutor_register"),
    path("registeras/academy/", academyRegister, name="academy_register" ),
    path('signin/', views.signIn, name="sign_in"),
    path('signout/', views.signOut, name="sign_out"),
    path('tutors/', views.tutors, name="tutors"),
    path('privacy-policy/', views.privcy_policy, name="privacy_policy"),
    path('terms-of-use/', views.terms_of_use, name="terms"),
    path('tutors/<int:id>/', views.tutorDetail, name="tutor_detail"),
    path('ad-detail/<int:id>/', views.ads_detail, name="ads_detail_tutor"),
    path("activate-student/<uidb64>/<token>/<id>/", views.activate_invite_view, name="activate_invite"),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="home/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="home/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="home/reset.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="home/reset_complete.html"), name="password_reset_complete"),
]
