from django_filters import FilterSet
from .models import Post

# Создаем свой набор фильтров для модели.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class NewsFilter(FilterSet):
   class Meta:
       # В Meta классе мы должны указать Django модель,
       # в которой будем фильтровать записи.
       model = Post
       # В fields мы описываем по каким полям модели
       # будет производиться фильтрация.
       fields = {
           # поиск по названию
           'title': ['icontains'],
           'text': ['icontains'],
           # количество товаров должно быть больше или равно
           'rating': ['gt'],
       }
