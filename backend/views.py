from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.models import Bookmark, Folder, Tag
from .serializers import BookmarkSerializer, FolderSerializer, TagSerializer

# Create your views here.

@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Bookmark List':'/bookmark-list/',
        'Folder List':'/folder-list/',
        'Tag List':'/tag-list/',
        'Bookmark Detail':'bookmark-detail/<str:pk>',
        'Create':'/bookmark-create/<str:pk>',
        'Update':'/bookmark-update/<str:pk>',
        'Delete':'/bookmark-delete/<str:pk>',
    }

    return Response(api_urls)


@api_view(['GET'])
def bookmarkList(request):
    bookmarks = Bookmark.objects.all()
    serializer = BookmarkSerializer(bookmarks,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def folderList(request):
    folders = Folder.objects.all()
    serializer = FolderSerializer(folders,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def folderDetail(request, pk):
    folders = Folder.objects.get(id=pk)
    serializer = FolderSerializer(folders,many=False)
    return Response(serializer.data)

@api_view(['GET'])
def tagList(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tagDetail(request, pk):
    tags = Tag.objects.get(id=pk)
    serializer = FolderSerializer(tags,many=False)
    return Response(serializer.data)

@api_view(['GET'])
def bookmarkDetail(request, pk):
    bookmark = Bookmark.objects.get(id=pk)
    serializer = BookmarkSerializer(bookmark,many=False)
    return Response(serializer.data)

@api_view(['POST'])
def bookmarkCreate(request):
    
    serializer = BookmarkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def bookmarkUpdate(request,pk):
    bookmark = Bookmark.objects.get(id=pk)
    serializer = BookmarkSerializer(instance=bookmark, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
    return Response(serializer.data)
    
@api_view(['DELETE'])
def bookmarkDelete(request, pk):
    bookmark = Bookmark.objects.get(id=pk)
    bookmark.delete()
    return Response('task deleted')


