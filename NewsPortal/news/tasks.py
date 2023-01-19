from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from news.models import Post, CategoryUser
from datetime import date, timedelta
from django.db.models import Q

@shared_task
def send_email_to_subscribers(user, category, title, text, receiver_id, url):
    to_send = User.objects.filter(id=receiver_id).values('first_name', 'last_name', 'username', 'email')
    html_content = render_to_string(
        'news_created.html',
        {
            'title': title,
            'text': text,
            'cur_user': user,
            'category': category,
            'url': url,
            'user': f"{to_send[0]['first_name']} {to_send[0]['last_name']} ({to_send[0]['username']})"
        }
    )
    msg = EmailMultiAlternatives(
        subject=title,
        body=text[:50],  # это то же, что и message
        from_email='hollyhome@yandex.ru',
        to=[to_send[0]['email']],  # это то же, что и recipients_list
    )
    msg.attach_alternative(html_content, "text/html")  # добавляем html
    msg.send()

    return


@shared_task
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
