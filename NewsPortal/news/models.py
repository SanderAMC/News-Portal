from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        """
        суммарный рейтинг каждой статьи автора умножается на 3;
        суммарный рейтинг всех комментариев автора;
        суммарный рейтинг всех комментариев к статьям автора.

        """
        posts = Post.objects.filter(Post.author == self.user).values("rating")
        pass


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Post(models.Model):
    TYPES = [
        ('A', 'Article'),
        ('N', 'News')
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=1, choices=TYPES, default='A')
    creation = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField(default=0)


    def like(self):

        self.rating += 1
        self.save()


    def dislike(self):

        if self.rating > 0:
            self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:125] + ' ...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pass


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    creation = models.DateTimeField(auto_now_add = True)
    rating = models.IntegerField(default=0)


    def like(self):
        self.rating += 1


    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
