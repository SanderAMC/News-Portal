from django_filters import *
import django_filters
from .models import Post, Category
from django import forms


class NewsFilter(FilterSet):

    post_type = django_filters.ChoiceFilter(choices=Post.TYPES, label="Тип поста ", lookup_expr='iexact')
    creation = django_filters.DateFilter(widget=forms.DateInput(attrs={'type': 'date'}),
                                         label="Создано позднее, чем ", lookup_expr='date__gt')
    category = django_filters.ChoiceFilter(choices=[[c.id, c.name] for c in Category.objects.all().order_by('name')], label="Категория новости ")


    class Meta:
       model = Post
       fields = {
           'title': ['icontains'],
       }



