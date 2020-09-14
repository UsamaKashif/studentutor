from django.contrib import admin
from django.urls import path, include


from . import views


urlpatterns = [
    path("", views.tutorDashboard , name="tutor_dashboard"),
    path("postad/<str:pk>/", views.postAnAd , name="post_ad_tutor"),
    path("wish-list/", views.wishList , name="wishlist_tut"),
    path("ads/", views.ads , name="ads_tutor"),
    path("invitaions/", views.invitations , name="invitations"),
    path("confirminvite/<int:id>/", views.confirmInvite , name="confirm_invite"),
    path("confirminvite/academy/<int:id>/", views.confirmInviteAcademy , name="confirm_invite_academy"),
    path("rejectinvite/<int:id>/", views.rejectInvite , name="reject_invite"),
    path("rejectinvite/academy/<int:id>/", views.rejectInviteAcademy , name="reject_invite_academy"),
    path("<str:pk>/ads/", views.adsDelete , name="ads_del_tutor"),
    path("students/", views.allStudents , name="all_students"),
    path("academies/", views.allAcademy , name="all_students_acad"),
    path("academy/<int:id>/", views.specificAcademy , name="specific_acad"),
    path("students/<int:id>/", views.specificStudent , name="specific_students"),
    path("students/<int:id>/like/api/", views.PostLikeAPIToggle.as_view() , name="post_like_api_tut"),
    path("students/<int:id>/wish-list/", views.WishlistApi.as_view() , name="wish_list_tut"),
    path("students/invite/<int:id>/", views.inviteForDemo , name="student_invite"),
    path("students/invite/academy/<int:id>/", views.inviteForDemoAcademy , name="academy_invite"),
    path("student/invited/", views.tutorInvited , name="invited_students"),
    path("about/", views.about_qual , name="about_tutor"),
    path("qualifications/", views.qual , name="qual_tutor"),
    path("verification/", views.verifydoc , name="verify_tutor"),
    path("yourad/<int:id>/", views.view_your_ad, name="view_your_ad_tut"),
    path("yourad/academy/<int:id>/", views.view_your_ad_academy, name="view_your_ad_tut_academy"),
    path("deltutor/", views.del_account_student , name="del_tutor"),
    path("activate/<uidb64>/<token>/", views.activate_view, name="activate_tut")
]
