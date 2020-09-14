from django.contrib import admin
from django.urls import path, include


from . import views

# /student/..


urlpatterns = [
    path('', views.academyDashboard, name="academy_dashboard"),
    path('postad/<str:pk>/', views.postAd, name="post_ad_academy"),
    path('ads/', views.Ads, name="ads_academy"),
    # path('wishlist/', views.wishList, name="wishlist"),
    path('<str:pk>/ads/', views.AdsDelete, name="ads_delete_academy"),
    path('tutors/', views.allTutors, name="all_tutors_academy"),
    path('tutors/<int:id>', views.SpecificTutor, name="specific_tutor_academy"),
    # path('tutors/<int:id>/like/', views.PostLikeToggle.as_view(), name="post_like_std"),
    # path('tutors/<int:id>/like/api/', views.PostLikeAPIToggle.as_view(), name="post_like_api_std"),
    # path('tutors/<int:id>/wish-list/', views.WishlistApi.as_view(), name="wish_list"),
    path('tutors/<int:id>/', views.inviteFordemo, name="tutor_invite_academy"),
    path('tutors/invited/', views.invited, name="invited_academy"),
    path('invitaions/', views.invitationsAcademy, name="invitations_academy"),
    path("confirminvite/<int:id>/", views.acceptInvitationAcademy , name="accept_invite_acad"),
    path("rejectinvite/<int:id>/", views.rejectInviteAcademy , name="reject_invite_acad"),
    path("about/", views.aboutAcademy , name="academy_about"),
    path("delaccount/", views.del_account_acad , name="del_account_acad"),
    path("yourad/<int:id>/", views.view_your_ad_acad, name="view_your_ad_acad"),
    path("activate/<uidb64>/<token>/", views.activate_view, name="activate_academy"),
]


