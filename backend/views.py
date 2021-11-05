from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
import json
import tldextract

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
    # page_url = request.GET.get('page_url', '')
    # preview_data = generate_preview(page_url)
    # serializer = BookmarkSerializer(data=preview_data)
    # if serializer.is_valid():
    #     serializer.save()
    # return JsonResponse(preview_data)


    # json.loads: Deserialize string to a Python object
    url = json.loads(request.body)
    preview_data = generate_preview(url)
    serializer = BookmarkSerializer(data=preview_data)
    if serializer.is_valid():
        serializer.save()
    return JsonResponse(preview_data)

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

# =============================================================================================================================================================================


def generate_preview(page_url):
    headers = {
        'Access-Control-Allow-Origin': "http://localhost:3000",
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(page_url, headers)
    html = BeautifulSoup(req.content, 'html.parser')
    # requests will provide us with our target’s HTML, and beautifulsoup4 will parse that data.

    if get_domain(html) == None:
        extract = tldextract.extract(page_url)
        get_domain(html) = extract.domain + extract.suffix

    meta_data = {
        'title': get_title(html),
        'description': get_desc(html),
        'page_url': page_url,
        'domain': get_domain(html)
    }
    return meta_data


def get_title(html):
    title = None
    if html.title.string:
        title = html.title.string
    elif html.find("meta", property="og:title"):
        title = html.find("meta", property="og:title").get('content')
    elif html.find("meta", property="twitter:title"):
        title = html.find("meta", property="twitter:title").get('content')
    elif html.find("h1"):
        title = html.find("h1").string
    return title

def get_desc(html):
    desc = None
    if html.find("meta", property="og:description"):
        desc = html.find("meta", property="og:description").get('content')
    elif html.find("meta", property="twitter:description"):
        desc = html.find("meta", property="twitter:description").get('content')
    elif html.find("meta", property="description"):
        desc = html.find("meta", property="description").get('content')
    else:
        desc = html.find_all("p")[0].string
    return desc

def get_image(html):
    image = None
    if html.find("meta", property="og:image"):
        image = html.find("meta", property="og:image").get('content')
    elif html.find("link", rel="image_src"):
        image = html.find("link", rel="image_src"").get('content')
    else:
        images = html.find_all("image")
        
    return image

def get_domain(html):
    domain = None
    if html.find("link", rel="canonical"):
        domain = html.find("link", rel="canonical").get('content')
    elif html.find("meta", property="og:url"):
        domain = html.find("meta", property="og:url").get('content')
    else:
        return None
    return domain

