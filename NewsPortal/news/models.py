import django.db.models
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache

# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.user.username})'

    @staticmethod
    def query_rating_sum(query: django.db.models.query.QuerySet):
        summ = 0
        for i in range(len(query)):
            summ += query[i]["rating"]
        return summ

    def update_rating(self):

        posts = Post.objects.filter(author_id=self.user_id)
        posts_ratings = Author.query_rating_sum(posts.values("rating"))
        comments_ratings = Author.query_rating_sum(Comment.objects.filter(user_id=self.user_id).values("rating"))

# или так
#posts_ratings = Post.objects.filter(author_id=1).aggregate(Sum("rating"))['rating__sum']
#comments_ratings1 = Comment.objects.filter(user_id=1).aggregate(Sum('rating'))['rating__sum']

        compost_ratings = 0
        for i in range(len(posts)):
            compost_ratings += Author.query_rating_sum(Comment.objects.filter(post_id=posts[i].id).values("rating"))
# или так
#_ = Comment.objects.prefetch_related('post_id').filter(post_id=posts[i].id).aggregate(Sum('rating'))['rating__sum']
#if _ is not None:
#compost_ratings += Comment.objects.prefetch_related('post_id').filter(post_id=posts[i].id).aggregate(Sum('rating'))['rating__sum']
# или так
# compost_ratings = Authors.objects.get(id=4).comment_set.all().aggregate(Sum('rating'))['rating__sum']

        self.rating = posts_ratings * 3 + comments_ratings + compost_ratings
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, through='CategoryUser')
    pass

    def __str__(self):
        return f'{self.id}: {self.name}'

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
        return self.text[:124] + ' ...'

    def __str__(self):
        return f'{self.id}: {self.author.user.username}: {self.post_type}: {self.creation}: ' \
               f'{self.title}: {self.text[:50]}: rating {self.rating}'

    def get_absolute_url(self):
        return reverse('one_new', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}') # затем удаляем его из кэша, чтобы сбросить его

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pass

    def __str__(self):
        return f'{self.id}: {self.category.name}: {self.post.id}: {self.post.post_type}: {self.post.title}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    creation = models.DateTimeField(auto_now_add = True)
    rating = models.IntegerField(default=0)


    def like(self):
        self.rating += 1
        self.save()


    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
        self.save()

class CategoryUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}: {self.user} - {self.category}'

class NewsCreated(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=False)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.id}: {self.user_id} - {self.user}: {self.date}: {self.count}'
