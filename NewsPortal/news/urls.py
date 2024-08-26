from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    # path('news/', views.news, name='news'),
    path('posts/', PostList.as_view(), name='posts'),
    path('subscriptions/', subscriptions, name='subs'),
    path('posts/create', PostCreate.as_view(), name='post_create'),
    path('posts/<int:pk>', PostDetails.as_view(), name='post_detailed'),
    path('posts/<int:pk>/edit', PostUpdate.as_view(), name='post_edit'),
    path('posts/<int:pk>/delete', PostDelete.as_view(), name='post_delete'),
]
