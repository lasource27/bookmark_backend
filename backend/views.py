from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view
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
        print(html)
        desc = html.find_all("p")[0].string
    return desc

def get_image(html):
    image = None
    # if html.find("meta", property="og:image"):
    #     image = html.find("meta", property="og:image").get('content')
    # elif html.find("link", rel="image_src"):
    #     image = html.find("link", rel="image_src").get('content')
    # else:
    images = html.find_all("img")
    src_list = []
    for image in images:
        if image['src']:
            image_raw = image['src']
        elif image['data-src']:
            image_raw = image['data-src']
        else:
            pass
        
        if image_raw.startswith('https://'):
            # print(image_raw)
            fd = urllib.request.urlopen(image_raw)
            image_file = io.BytesIO(fd.read())
            im = Image.open(image_file)
            print(im.size)

        
        # print(image_raw)
        # image = Image.open(image_raw)
        # print(image.size)
        
    # def proportion(image):
    #     return image.naturalWidth / image.naturalHeight < 3 or image.naturalHeight / image.naturalWidth < 3
    # def area(image):
    #     return image.naturalWidth*image.naturalHeight
    # filtered_images = list[filter(proportion,images)]
    # # print(filtered_images)
    # # print("1231231312313")
    # # print(filtered_images)
    # new_images = []
    # for image in filtered_images:
    #     new_images.append(area(image))
    # image = max(new_images)
    return image.src

def get_domain(html):
    domain = None
    if html.find("link", rel="canonical"):
        domain = html.find("link", rel="canonical").get('content')
    elif html.find("meta", property="og:url"):
        domain = html.find("meta", property="og:url").get('content')
    else:
        domain = None
    return domain

