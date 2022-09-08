from app_twhunter.models import Author,Tweet,Keyword
from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'



class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'


class TweetSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many = True,read_only=True)
    author = AuthorSerializer(read_only = True)


    class Meta:
        model = Tweet
        fields = '__all__'
        read_only_fields = ['tweet_id','created_at','keyword']
