from django.urls import path
# Импортируем созданное нами представление
from .views import *
from django.views.decorators.cache import cache_page

urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем товарам у нас останется пустым,
   # чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.

   path('news/', cache_page(60*5)(PostList.as_view()), name='news_list'),
   path('articles/', cache_page(60*5)(PostList.as_view()), name='arts_list'),

   path('news/search/', cache_page(60*5)(NewsListFiltered.as_view()), name='news_search'),

   path('news/<int:pk>', OnePost.as_view(), name='one_new'),
   path('articles/<int:pk>', OnePost.as_view(), name='one_art'),

   path('news/create/', PostCreate.as_view(), name='news_create'),
   path('articles/create/', PostCreate.as_view(), name='arts_create'),

   path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_update'),
   path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='arts_update'),

   path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
   path('articles/<int:pk>/delete/', PostDelete.as_view(), name='arts_delete'),

]