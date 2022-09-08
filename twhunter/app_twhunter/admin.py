from django.contrib import admin
from .models import Keyword,Tweet,Author



# Register your models here.
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id','keyword_text','is_hashtag','counter')


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('tweet_id','author')
    readonly_fields = ('author_id',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('screen_name',)

