from django.contrib import admin
from django.urls import path, include


from . import views

# /student/..

urlpatterns = [
    path('', views.studentDashboard, name="student_dashboard"),
    path('postad/<str:pk>/', views.postAd, name="post_ad"),
    path('ads/', views.Ads, name="ads"),
    path('<str:pk>/ads/', views.AdsDelete, name="ads_delete"),
    path('tutors/', views.allTutors, name="all_tutors"),
    path('tutors/<int:id>', views.SpecificTutor, name="specific_tutor"),
    path('tutors/<int:id>/', views.inviteFordemo, name="tutor_invite"),
    path('tutors/invited/', views.invited, name="invited"),
    path('invitaions/', views.invitations, name="invitations_student"),
    path("confirminvite/<int:id>/", views.acceptInvitation , name="accept_invite"),
    path("rejectinvite/<int:id>/", views.rejectInvite , name="reject_invite_std"),
    path("about/", views.aboutStudent , name="student_about"),
    path("delaccount/", views.del_account_student , name="del_account"),
    path("yourad/<int:id>/", views.view_your_ad, name="view_your_ad_std"),
]


