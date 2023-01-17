from datetime import *
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Post, NewsCreated, PostCategory, CategoryUser, Category, Author
from django.db.models import F


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(post_save, sender=Post)
def notify_managers_post(sender, instance, created, **kwargs):
    print('POST signal')
    if created:
        if not NewsCreated.objects.filter(user_id=instance.author_id, date=date.today()).exists():
            NewsCreated.objects.create(user_id=instance.author_id, date=date.today(), count=1)
        else:
            NewsCreated.objects.filter(user_id=instance.author_id, date=date.today()).update(count=F('count') + 1)


@receiver(m2m_changed, sender=PostCategory)
def notify_managers_post(sender, instance, action, reverse, model, pk_set, **kwargs):
    print('M2M POST signal')
    if action == 'post_add':
        user_ = Author.objects.filter(id=instance.author_id).values('user__username')[0]['user__username']
        title = instance.title
        text = instance.text

        url = f"http://127.0.0.1:8000/{'news/' if instance.post_type == 'N' else 'articles/'}{instance.id}"

        for cat_ in PostCategory.objects.filter(post_id=instance.id).values('category_id'):
            id_to_send = CategoryUser.objects.filter(category_id=cat_['category_id']).values('user_id')
            category = Category.objects.filter(id=cat_['category_id']).values('name')[0]['name']

            Post.send_email_to_subscribers(user_, category, title, text, id_to_send, url)
