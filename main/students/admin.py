from django.contrib import admin
from .models import Student, PostAnAd, TutorInvitaions,WishList
# Register your models here.


class StudentAdmin(admin.ModelAdmin):
    list_display = ("username", "id" , "email", "profile_complete", "total_ads")
    search_fields = ("username", "id", "email")
    list_filter = ("profile_complete",)


class TutorInvitationsAdmin(admin.ModelAdmin):
    list_display = ("inivitaion_by_tutor", "accepted" , "rejected", "student_ad")
    list_filter = ("accepted","rejected")

class PostAnAdAdmin(admin.ModelAdmin):
    list_display = ("studentUser","subject","tuition_level","estimated_fees","views")
    search_fields = ("subject","tuition_level")


admin.site.register(Student, StudentAdmin)
admin.site.register(PostAnAd, PostAnAdAdmin)
admin.site.register(TutorInvitaions,TutorInvitationsAdmin)
admin.site.register(WishList)