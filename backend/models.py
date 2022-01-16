from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)



class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have an email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Password should not be none')
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        return ''


class Folder(models.Model):
    name = models.CharField(max_length=60, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_fd_user")

    def __str__(self):
        return f"{self.name}"

class Tag(models.Model):
    name = models.CharField(max_length=60, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_tg_user")

    def __str__(self):
        return f"{self.name}"


class Bookmark(models.Model):
    
    title = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=600, null=True)
    page_url = models.CharField(max_length=600, null=True)
    date_created = models.DateField(auto_now_add=True, null=True)
    time_created = models.TimeField(auto_now_add=True, null=True)
    preview_image = models.CharField(max_length=600, blank=True, null=True)
    domain = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_bm_user")
    folder = models.ForeignKey(Folder,related_name="all_bm_folder", null=True, blank=True, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag,related_name="all_bm_tag",null=True, blank=True)
    

    def __str__(self):
        return f"{self.title}"





