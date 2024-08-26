from django_filters import FilterSet
from .models import *


class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'category': ['exact'],
            'add_date': ['lt', 'gt'],
            'post_type': ['exact'],
        }
