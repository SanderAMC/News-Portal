from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()

    def update_rating(self):
        pass


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pass


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.BooleanField()
    creation = models.DateTimeField()
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.FloatField()


    def like(self):
        pass


    def dislike(self):
        pass


    def preview(self):
        pass


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pass


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    creation = models.DateTimeField()
    rating = models.FloatField()

    def like(self):
        pass


    def dislike(self):
        pass
