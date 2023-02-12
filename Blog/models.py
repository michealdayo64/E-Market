from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class Post(models.Model):
    #user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'author')
    title = models.CharField(max_length = 30)
    description = models.TextField()
    image = models.ImageField(upload_to='media')
    created = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name = 'comment_post', on_delete = models.CASCADE)
    author = models.CharField(max_length = 20)
    email = models.EmailField()
    comment = models.TextField()
    created = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.author
