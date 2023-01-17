from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author, CategoryUser, NewsCreated
from .filters import NewsFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import django.db.models
from datetime import date
from django.shortcuts import redirect

class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-creation'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'post_list.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'post_list'
    paginate_by = 10


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'news' in self.request.path.split('/'):
            context['post_count'] = Post.objects.filter(post_type='N').count
            context['obj_type1'] = 'Новости'
            context['obj_type2'] = 'Новостей'
        else:
            context['post_count'] = Post.objects.filter(post_type='A').count
            context['obj_type1'] = 'Статьи'
            context['obj_type2'] = 'Статей'
        if self.request.user.is_authenticated:
            context['user_name'] = self.request.user
        # Добавляем в контекст объект фильтрации.
        return context

    def get_queryset(self):
# Получаем обычный запрос
        if 'news' in self.request.path.split('/'):
            queryset = Post.objects.order_by('-creation').filter(post_type='N')
        else:
            queryset = Post.objects.order_by('-creation').filter(post_type='A')
        self.filterset = NewsFilter(self.request.GET, queryset)

# Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

class NewsListFiltered(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-creation'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news_search.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news_flist'
    paginate_by = 10

    @staticmethod
    def is_subscribed(cat, query: django.db.models.query.QuerySet):
        for i in range(len(query)):
            if cat == str(query[i]['category_id']):
                return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_count'] = self.filterset.qs.count()
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        context['sub_button'] = False
        if self.request.user.is_authenticated:
            context['user_name'] = self.request.user
            if 'category' in self.filterset.data.keys():
                context['subscribed'] = self.is_subscribed(self.filterset.data['category'],
                                                           CategoryUser.objects.filter(user_id=self.request.user).values('category_id'))
                if self.filterset.data['category'] != '':
                    context['sub_button'] = True

        return context

   # Переопределяем функцию получения списка новостей
    def get_queryset(self):
        queryset = Post.objects.order_by('-creation').filter(post_type='N')
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs


class OnePost(DetailView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'post.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'one_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'news' in self.request.path.split('/'):
            context['obj_type'] = 'Новость'
        else:
            context['obj_type'] = 'Статья'
        if self.request.user.is_authenticated:
            context['user_name'] = self.request.user
        return context

    def get_queryset(self):
# Получаем обычный запрос
        post_id = self.request.path.split('/')[-1]
        if 'news' in self.request.path.split('/'):
            queryset = Post.objects.order_by('-creation').filter(post_type='N', id=post_id)
        else:
            queryset = Post.objects.order_by('-creation').filter(post_type='A', id=post_id)
        self.filterset = NewsFilter(self.request.GET, queryset)

# Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

class PostCreate(PermissionRequiredMixin, CreateView):
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'
    permission_required = ('news.add_post', )

    def post(self, request, *args, **kwargs):

        if not (NewsCreated.objects.filter(user_id=self.request.user.id, date=date.today()).exists() and
                NewsCreated.objects.filter(user_id=self.request.user.id,
                                           date=date.today()).values('count')[0]['count'] < 3):
            return redirect(request.META.get('HTTP_REFERER'))

        return super().post(self, request, *args, **kwargs)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = Author.objects.get(user_id=self.request.user.id)

        if 'news' in self.request.path.split('/'):
            post.post_type = 'N'
            self.success_url = reverse_lazy('news_list')
        else:
            post.post_type = 'A'
            self.success_url = reverse_lazy('arts_list')

        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'news' in self.request.path.split('/'):
            context['obj_type'] = 'Новость'
        else:
            context['obj_type'] = 'Статья'
        if self.request.user.is_authenticated:
            context['user_name'] = self.request.user
            if NewsCreated.objects.filter(user_id=self.request.user.id, date=date.today()).exists():
                context['posts_today'] = NewsCreated.objects.filter(user_id=self.request.user.id,
                                                                    date=date.today()).values('count')[0]['count']
            else:
                context['posts_today'] = 0
        # Добавляем в контекст объект фильтрации.
        return context

class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'
    permission_required = ('news.change_post', )


    def get_queryset(self):
# Получаем обычный запрос
        post_id = self.request.path.split('/')[-3]

        if 'news' in self.request.path.split('/'):
            queryset = Post.objects.order_by('-creation').filter(post_type='N', id=post_id)
        else:
            queryset = Post.objects.order_by('-creation').filter(post_type='A', id=post_id)
        self.filterset = NewsFilter(self.request.GET, queryset)

# Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_name'] = self.request.user
            context['posts_today'] = -1
        return context

    def form_valid(self, form):
        if 'news' in self.request.path.split('/'):
            self.success_url = reverse_lazy('news_list')
        else:
            self.success_url = reverse_lazy('arts_list')
        return super().form_valid(form)


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'news' in self.request.path.split('/'):
            context['obj_type'] = 'новости'
        else:
            context['obj_type'] = 'статьи'
        # Добавляем в контекст объект фильтрации.
        if self.request.user.is_authenticated:
            context['user_name'] = self.request.user
        return context

    def form_valid(self, form):
        if 'news' in self.request.path.split('/'):
            self.success_url = reverse_lazy('news_list')
        else:
            self.success_url = reverse_lazy('arts_list')
        return super().form_valid(form)

    def get_queryset(self):
# Получаем обычный запрос
        post_id = self.request.path.split('/')[-3]
        if 'news' in self.request.path.split('/'):
            queryset = Post.objects.order_by('-creation').filter(post_type='N', id=post_id)
        else:
            queryset = Post.objects.order_by('-creation').filter(post_type='A', id=post_id)
        self.filterset = NewsFilter(self.request.GET, queryset)

# Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

