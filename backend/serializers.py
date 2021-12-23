from .models import Bookmark, Folder, Tag
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50,min_length=6,write_only=True)

    class Meta:
        model = User
        fields = ['email','username','password']
 
    def validate(self, attrs):
        email = attrs.get('email','')
        username = attrs.get('username','')
        
        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric characters.')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)