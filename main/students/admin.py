from django.contrib import admin
from .models import Student, PostAnAd, TutorInvitaions
# Register your models here.


class StudentAdmin(admin.ModelAdmin):
    list_display = ("username", "id" , "email", "profile_complete", "total_ads")
    search_fields = ("username", "id", "email")
    list_filter = ("profile_complete",)


class TutorInvitationsAdmin(admin.ModelAdmin):
    list_display = ("inivitaion_by_tutor", "accepted" , "rejected", "student_ad")
    list_filter = ("accepted","rejected")




admin.site.register(Student, StudentAdmin)
admin.site.register(PostAnAd)
admin.site.register(TutorInvitaions,TutorInvitationsAdmin)