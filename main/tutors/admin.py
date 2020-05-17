from django.contrib import admin
from .models import Tutor, Invitaions, PostAnAd, AboutAndQualifications, Verify
# Register your models here.


class TutorAdmin(admin.ModelAdmin):
    list_display = ("username", "id","gender", "email" , "verified", "verification_sent", "about_complete", "qual_complete")


class InvitaionsAdmin(admin.ModelAdmin):
    list_display = ("inivitaion_by_student","tutor_ad", "accepted", "rejected")


admin.site.register(Tutor, TutorAdmin)
admin.site.register(Invitaions, InvitaionsAdmin)
admin.site.register(PostAnAd)
admin.site.register(AboutAndQualifications)
admin.site.register(Verify)