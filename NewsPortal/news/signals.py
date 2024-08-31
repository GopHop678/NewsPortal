from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from .models import Subscription, PostCategory


# @receiver(m2m_changed, sender=PostCategory)
def post_created(instance, action, **kwargs):
    if action == 'post_add':
        latest_post = PostCategory.objects.filter(post_id=instance.id)

        subs = []
        for obj in latest_post:
            subs.extend(i for i in list(Subscription.objects.filter(category=obj.category_id)))
            # subs.append(User.objects.filter(subscription__category=obj.category_id)
            #             .values_list('email', flat=True))

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
