from django.contrib import admin

# Register your models here.
from .models import Audit, AttachedFolder,Document

# Register your models here.

admin.site.register(Audit)
admin.site.register(AttachedFolder)



   
