from django.contrib import admin
from .models import *

# создаём новый класс для представления товаров в админке
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'rating']
    list_filter = ['rating']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']


    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.username})"


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post_type', 'creation', 'get_categories', 'title', 'text_wrap', 'rating']
    list_filter = ['author', 'post_type', 'category', 'rating']
    search_fields = ['author__user__username', 'title', 'text']


    def get_categories(self, obj):
        return ", \n".join([c.name for c in obj.category.all()])

    def text_wrap(self, obj):
        return obj.text[:50]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_subs']
    list_filter = ['name', 'subscribers__username']
    search_fields = ['name']


    def get_subs(self, obj):
        return ", \n".join([c.username for c in obj.subscribers.all()])


class CommentAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'user', 'text_wrap', 'creation', 'rating']
    search_fields = ['text', 'creation', 'user__username']
    list_filter = ['user', 'rating']


    def text_wrap(self, obj):
        return obj.text[:150]

class NewsCreatedAdmin(admin.ModelAdmin):
    list_display = [field.name for field in NewsCreated._meta.get_fields()]
    list_filter = ['user', 'date']


class CategoryUserAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'category']
    list_filter = ['user', 'category']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'category__name']

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.username})"


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['get_post', 'category']
    list_filter = ['post__author__user__username', 'category']
    search_fields = ['post__title', 'post__text', 'post__author__user__username', 'post__author__user__first_name',
                     'post__author__user__last_name', 'category__name']

    def get_post(self, obj):
        return f"{obj.post.title[:20]} {obj.post.text[:50]} (от {obj.post.author})"



admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CategoryUser, CategoryUserAdmin)
admin.site.register(NewsCreated, NewsCreatedAdmin)
