from django.db import models


# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    username = models.CharField(max_length=30, unique=False, null=False)
    password = models.CharField(max_length=30, null=False)
    telephone = models.CharField(max_length=15, null=False)
    email = models.EmailField(max_length=30, null=False)
    introduce = models.CharField(max_length=50, null=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Article(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    title = models.CharField(max_length=30, null=False)
    content = models.TextField(max_length=1000, null=False)
    uid = models.IntegerField(null=False)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Comment(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    uid = models.IntegerField(null=False)
    bid = models.IntegerField(null=False)
    content = models.TextField(max_length=1000, null=False)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content
