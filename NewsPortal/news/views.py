from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from .models import Post, Subscription, Category
from .filters import PostFilter
from .forms import PostForm
from .tasks import *


class PostList(ListView):
    # queryset = Post.objects.filter(post_type='News')
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'

    ordering = 'add_date'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetails(DetailView):
    model = Post
    template_name = 'news/post_detailed.html'
    context_object_name = 'post'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['time_now'] = datetime.utcnow()
    #     context['next_sale'] = "Распродажа в среду!"
    #     return context


class PostCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news/post_create.html'

    raise_exception = True
    permission_required = ('news.add_post',)
    success_url = reverse_lazy('posts')


class PostUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'news/post_create.html'

    raise_exception = True
    permission_required = ('news.change_post',)
    success_url = reverse_lazy('posts')


class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('posts')

    raise_exception = True
    permission_required = ('news.delete_post',)


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('category')
    return render(request, 'news/subscriptions.html', {'categories': categories_with_subscriptions},)


def index(request):
    # send_notifies.delay()
    return render(request, 'news/index.html')


def news(request):
    obj = Post.objects.all()
    return render(request, 'news/posts.html', {'posts': obj})
