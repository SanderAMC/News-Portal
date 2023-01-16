from datetime import *
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import mail_managers
from .models import Post, NewsCreated
from django.db.models import F

# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(post_save, sender=Post)
def notify_managers_post(sender, instance, created, **kwargs):
    if created:
        if instance.post_type == 'N':
            if not NewsCreated.objects.filter(user_id=instance.author_id, date=date.today()).exists():
                NewsCreated.objects.create(user_id=instance.author_id, date=date.today(), count=1)
            else:
                NewsCreated.objects.filter(user_id=instance.author_id, date=date.today()).update(count=F('count') + 1)
