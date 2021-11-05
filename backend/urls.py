from django.urls import path
from . import views


urlpatterns = [
    path('', views.apiOverview, name="apiOverview"),
    path('bookmark-list', views.bookmarkList, name="bookmark-list"),
    path('folder-list', views.folderList, name="folder-list"),
    path('folder-detail/<str:pk>', views.folderDetail, name="folder-detail"),
    path('tag-list', views.tagList, name="tag-list"),
    path('tag-detail/<str:pk>', views.tagDetail, name="tag-detail"),
    path('bookmark-detail/<str:pk>', views.bookmarkDetail, name="bookmark-detail"),
    path('bookmark-create/', views.bookmarkCreate, name="bookmark-create"),
    path('bookmark-update/<str:pk>', views.bookmarkUpdate, name="bookmark-update"),
    path('bookmark-delete/<str:pk>', views.bookmarkDelete, name="bookmark-delete"),
    path('generate-preview', views.generate_preview, name="generate-preview"),
]
