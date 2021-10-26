from django.contrib import admin
from .models import Bookmark, Folder, Tag


admin.site.register(Bookmark)
admin.site.register(Folder)
admin.site.register(Tag)

# Register your models here.
