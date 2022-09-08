from django.db import models

# Create your models here.


class Author(models.Model):
    author_id = models.BigIntegerField(primary_key=True,unique=True)
    name = models.CharField(max_length=255,null=True,unique=True)
    screen_name = models.CharField(max_length=255,null=True)
    followers = models.IntegerField(default=0,null=True)
    following = models.IntegerField(default=0,null=True)
    created_at = models.CharField(null=True,max_length=255)
    location = models.CharField(max_length=255,null=True)
    bio = models.TextField(null=True)

    def __str__(self):
        return self.screen_name

  
class Keyword(models.Model):
    keyword_text = models.CharField(max_length=255,null=True)
    is_hashtag = models.BooleanField(default=False)
    counter = models.IntegerField(default=0)

    
    def __str__(self):
        return self.keyword_text


class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True,unique=True)
    author = models.ForeignKey(Author,on_delete=models.CASCADE,null=True)
    keyword = models.ManyToManyField(Keyword,blank=True,related_name='tweets')  
    message = models.TextField(max_length=280,null=True)
    created_at = models.CharField(null=True,max_length=255)
    retweet_count = models.IntegerField(null=True,default=0)
    favorite_count = models.IntegerField(null=True,default=0)
    reply_count = models.IntegerField(null=True,default=0)
    quote_count = models.IntegerField(null=True,default=0)

    def __str__(self):
        return self.user


 