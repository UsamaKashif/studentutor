from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "date_joined", "last_login")



admin.site.unregister(User)
admin.site.register(User,UserAdmin)



admin.site.site_header = "StudenTutor ADMIN"
