from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import requests
from requests import get
from bs4 import BeautifulSoup
from django.http import JsonResponse
import json
import tldextract
import io
from PIL import Image
import urllib

from backend.models import Bookmark, Folder, Tag
from .serializers import BookmarkSerializer, FolderSerializer, TagSerializer

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


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
@permission_classes([IsAuthenticated])
def bookmarkList(request):
    user = request.user
    bookmarks = user.bookmarks.all()
    serializer = BookmarkSerializer(bookmarks,many=True)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def folderList(request):
    folders = Folder.objects.all()
    serializer = FolderSerializer(folders,many=True)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def folderDetail(request, pk):
    folders = Folder.objects.get(id=pk)
    serializer = FolderSerializer(folders,many=False)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def tagList(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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

    my_session = requests.session()
    for_cookies = my_session.get(page_url)
    cookies = for_cookies.cookies
    req = my_session.get(page_url, headers=headers, cookies=cookies)
    html = BeautifulSoup(req.content, 'html.parser')
    # requests will provide us with our target’s HTML, and beautifulsoup4 will parse that data.

    if get_domain(html) != None:
        meta_data = {
            'title': get_title(html),
            'description': get_desc(html),
            'page_url': page_url,
            'preview_image': get_image(html),
            'domain': get_domain(html),
        } 
    else:
        extract = tldextract.extract(page_url)
        domain_name = extract.domain + '.' + extract.suffix
        meta_data = {
            'title': get_title(html),
            'description': get_desc(html),
            'page_url': page_url,
            'preview_image': get_image(html),
            'domain': domain_name,
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
        
        descs = html.find_all("p")
        maximum_length = 1
        desc = None
        for this_desc in descs:
            if this_desc.string != None:
                if len(this_desc.string) > maximum_length:
                    maximum_length = len(this_desc.string)
                    desc = this_desc.string
    return desc

def get_image(html):
    image = None
    if html.find("meta", property="og:image"):
        image = html.find("meta", property="og:image").get('content')
        return image
    elif html.find("link", rel="image_src"):
        image = html.find("link", rel="image_src").get('content')
        return image
    else:
        images = html.find_all("img")
        print(html)
        largest_area = 0
        largest_image_url = None
        for image in images:
            if image['src']:
                image_raw = image['src']
            elif image['data-src']:
                image_raw = image['data-src']
            else:
                pass
            
            if image_raw.startswith('https://'):
                user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
                headers = {'User-Agent': user_agent}
                request = urllib.request.Request(image_raw, headers=headers)
                fd = urllib.request.urlopen(request)
                
                image_file = io.BytesIO(fd.read())
                try:    
                    im = Image.open(image_file)
                    width, height = im.size
                    area = width * height
                    if area > largest_area:
                        largest_area = area
                        largest_image_url = image_raw
                except:
                    pass
            
        return largest_image_url

def get_domain(html):
    domain = None
    if html.find("link", rel="canonical"):
        domain = html.find("link", rel="canonical").get('content')
    elif html.find("meta", property="og:url"):
        domain = html.find("meta", property="og:url").get('content')
    else:
        domain = None
    return domain

