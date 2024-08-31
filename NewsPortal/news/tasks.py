from celery import shared_task
import logging
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import LastSend, Subscription, Post, PostCategory

logger = logging.getLogger(__name__)


@shared_task
def send_notifies():
    last_send = LastSend.objects.last().date

    users_to_send = Subscription.objects.filter().values_list('user_id', flat=True)
    users_to_send = list(set(users_to_send))

    emails = {}
    for user in users_to_send:
        user_obj = User.objects.get(id=user)
        subs = list(Subscription.objects.filter(user_id=user).values_list('category_id', flat=True))
        emails[user_obj.email] = subs

    for email in emails:
        sent_posts = []  # для избежания дубликатов если у поста несколько категорий

        for category in emails[email]:
            posts_to_notify = list(Post.objects.filter(category=category, add_date__gt=last_send))

            if posts_to_notify:

                for post in posts_to_notify:

                    if post not in sent_posts:
                        subject = f'Новый пост в избранных категориях'
                        text_content = (f'Пост: {post.title}\n'
                                        f'Ссылка на пост: http://127.0.0.1:8000{post.get_absolute_url()}')

                        msg = EmailMultiAlternatives(subject, text_content, None, [email])
                        msg.send()

                        sent_posts.append(post)

    LastSend().save()


@shared_task
@receiver(m2m_changed, sender=PostCategory)
def post_created(instance, action, **kwargs):
    if action == 'post_add':
        latest_post = PostCategory.objects.filter(post_id=instance.id)

        subs = []
        for obj in latest_post:
            subs.extend(i for i in list(Subscription.objects.filter(category=obj.category_id)))

        emails = []
        for obj in subs:
            emails.append(User.objects.get(id=obj.user_id).email)
        emails = list(set(emails))

        subject = f'Новый пост в избранных категориях'
        text_content = (
            f'Пост: {instance.title}\n'
            f'Ссылка на пост: http://127.0.0.1:8000{instance.get_absolute_url()}'
        )

        for email in emails:
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.send()
