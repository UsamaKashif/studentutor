from django.contrib import admin
from django.urls import path, include


from . import views

urlpatterns = [
    path("", views.tutorDashboard , name="tutor_dashboard"),
    path("postad/<str:pk>/", views.postAnAd , name="post_ad_tutor"),
    path("ads/", views.ads , name="ads_tutor"),
    path("invitaions/", views.invitations , name="invitations"),
    path("confirminvite/<int:id>/", views.confirmInvite , name="confirm_invite"),
    path("rejectinvite/<int:id>/", views.rejectInvite , name="reject_invite"),
    path("<str:pk>/ads/", views.adsDelete , name="ads_del_tutor"),
    path("students/", views.allStudents , name="all_students"),
    path("students/<int:id>/", views.specificStudent , name="specific_students"),
    path("students/invite/<int:id>/", views.inviteForDemo , name="student_invite"),
    path("student/invited/", views.tutorInvited , name="invited_students"),
    path("about/", views.about_qual , name="about_tutor"),
    path("qualifications/", views.qual , name="qual_tutor"),
    path("verification/", views.verifydoc , name="verify_tutor"),
    path("yourad/<int:id>/", views.view_your_ad, name="view_your_ad_tut"),
    path("deltutor/", views.del_account_student , name="del_tutor"),
    path("activate/<uidb64>/<token>/", views.activate_view, name="activate_tut")
]
