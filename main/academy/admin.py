from django.contrib import admin

from .models import Academy, PostAnAd, Invitations

# Register your models here.

admin.site.register(Academy)
admin.site.register(PostAnAd)
admin.site.register(Invitations)
