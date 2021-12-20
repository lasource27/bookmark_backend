from django.contrib import admin
from .models import Bookmark, Folder, Tag, User


admin.site.register(Bookmark)
admin.site.register(Folder)
admin.site.register(Tag)
admin.site.register(User)


# Register your models here.
