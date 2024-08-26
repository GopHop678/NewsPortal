from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, default=0)

    def update_rating(self):
        to_add = 0
        query = Post.objects.filter(author=self.id)
        query = query.values('rating')
        for i in query:
            to_add += i['rating']

        query = Comment.objects.filter(user=User.objects.get(username=self.user))
        query = query.values('rating')
        for i in query:
            to_add += i['rating']

        self.rating = to_add
        self.save()


class Category(models.Model):
    CATEGORIES = [
        ('SP', 'Спорт'),
        ('PLT', 'Политика'),
        ('EDU', 'Образование'),
        ('ECO', 'Экономика')
    ]
    category = models.CharField(max_length=255, unique=True)
    # category = models.CharField(max_length=10, choices=CATEGORIES, unique=True)
    users = models.ManyToManyField(User, through='Subscription')

    def __str__(self):
        return self.category


class Post(models.Model):
    post_type = models.CharField(max_length=31, choices=[('News', 'Новость'), ('Article', 'Статья')])
    add_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(null=True, auto_created=0)

    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    category = models.ManyToManyField(Category, through='PostCategory')

    def get_absolute_url(self):
        return reverse('post_detailed', args=[str(self.id)])

    def like(self):
        self.rating = self.rating + 1
        self.save()

    def dislike(self):
        self.rating = self.rating - 1
        self.save()

    def preview(self):
        return self.content[:125] + '...'

    def __str__(self):
        return self.title


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class LastSend(models.Model):
    date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    add_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating = self.rating + 1
        self.save()

    def dislike(self):
        self.rating = self.rating - 1
        self.save()
