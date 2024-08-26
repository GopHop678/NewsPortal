import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from news import models

logger = logging.getLogger(__name__)


def my_job():
    last_send = models.LastSend.objects.last().date

    users_to_send = models.Subscription.objects.filter().values_list('user_id', flat=True)
    users_to_send = list(set(users_to_send))

    emails = {}
    for user in users_to_send:
        user_obj = User.objects.get(id=user)
        subs = list(models.Subscription.objects.filter(user_id=user).values_list('category_id', flat=True))
        emails[user_obj.email] = subs

    for email in emails:
        sent_posts = []  # для избежания дубликатов если у поста несколько категорий

        for category in emails[email]:
            posts_to_notify = list(models.Post.objects.filter(category=category, add_date__gt=last_send))

            if posts_to_notify:

                for post in posts_to_notify:

                    if post not in sent_posts:
                        subject = f'Новый пост в избранных категориях'
                        text_content = (f'Пост: {post.title}\n'
                                        f'Ссылка на пост: http://127.0.0.1:8000{post.get_absolute_url()}')

                        msg = EmailMultiAlternatives(subject, text_content, None, [email])
                        msg.send()

                        sent_posts.append(post)

    models.LastSend().save()
    logger.info('Notifies are sent...')


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="fri", hour="18", minute="00"),
            # trigger=IntervalTrigger(seconds=3),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")
        logger.info("Starting scheduler...")
        scheduler.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")