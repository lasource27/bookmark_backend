from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):
    
    title = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=600, null=True)
    page_url = models.CharField(max_length=600, null=True)
    date_created = models.DateField(auto_now_add=True, null=True)
    time_created = models.TimeField(auto_now_add=True, null=True)
    preview_image = models.CharField(max_length=600, blank=True, null=True)
    domain = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    

    def __str__(self):
        return f"{self.title}"

class Folder(models.Model):
    bookmark = models.ManyToManyField(Bookmark,related_name="folders")
    name = models.CharField(max_length=60, null=True)

    def __str__(self):
        return f"{self.name}"

class Tag(models.Model):
    bookmark = models.ManyToManyField(Bookmark,related_name="tags")
    name = models.CharField(max_length=60, null=True)

    def __str__(self):
        return f"{self.name}"



