import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.db.models import Q
from datetime import date, timedelta
from news.models import Post, CategoryUser, User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

# наша задача по выводу текста на экран
def inform_for_new_posts():
    #  Your job processing logic here...
    print('Дайджест начал работу')
    date_from = date.today()-timedelta(days=8)
    date_to = date.today()-timedelta(days=1)
    post_source = Post.objects.filter(Q(creation__gte=date_from) & Q(creation__lt=date_to))
    users = CategoryUser.objects.all().values('user_id').distinct()
    title = f'Дайджест новых постов'
#    print(post_source)

    for i in range(users.count()):
#        print(users[i]['user_id'])
        categories = CategoryUser.objects.filter(user_id=users[i]['user_id']).values('category_id', 'category_id__name')
        user = User.objects.filter(id=users[i]['user_id']).values('first_name', 'last_name', 'username', 'email')
        user_name = f"{user[0]['first_name']} {user[0]['last_name']} ({user[0]['username']})"
        for c in range(categories.count()):
            category_name = categories[c]['category_id__name']
#            print(user)
#            print(category_name)
            posts = post_source.filter(category__id=categories[c]['category_id'])
            if posts.count() == 0:
                continue
#            print(posts)
            html_content = render_to_string(
                        'post_digest.html',
                        {
                            'date_from': date_from,
                            'date_to': date_to,
                            'title': title,
                            'user': user_name,
                            'category': category_name,
                            'posts': posts,
                            'url_start': 'http://127.0.0.1:8000/',
                        }
                    )
#            print(html_content)
            msg = EmailMultiAlternatives(
                subject=title,
                body=f'Дайджест новых постов с {date_from} по {date_to}.',  # это то же, что и message
                from_email='hollyhome@yandex.ru',
                to=[user[0]['email']],  # это то же, что и recipients_list
            )

            msg.attach_alternative(html_content, "text/html")  # добавляем html
            msg.send()

    print('Рассылка дайджеста завершена')

def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Runs NEW POST INFORMER."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            inform_for_new_posts,
            trigger=CronTrigger(week="*/1"),
#            trigger=CronTrigger(second="*/20"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="Post Informer",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'New posts informer'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
