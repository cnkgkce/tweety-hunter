from app_twhunter.models import Keyword, Tweet
from .serializers import TweetSerializer,KeywordSerializer
from .utils import CrawlTwitter
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView, ListAPIView
from django.db.models import Q 
from django.core.cache import cache
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


CACHE_TTL = getattr(settings,'CACHE_TTL',300)


class TweetListAPIView(ListAPIView):
    """
    This class is responsible for listing the tweets relevant to given keyword. 
    
    
    """
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self,*args,**kwargs):
        #tweets = cache.get('tweets')  ## check the cache on redis server... if there is any data, you can return it or continue
        #if tweets:
         #   print("cacheden twitt aldı")
          #  return tweets
    
        params = self.request.query_params
        tweets = None
        if params:
            q  = params.get("q",None) ### keyword
            username = params.get("username",None)
            location = params.get("location",None)
            hashtag  = params.get("hashtag",False)
            created_at = params.get("created_at",None)
            
            crawler = CrawlTwitter()
            crawler.login_twitter()
            crawler.crawler(keyword = q,is_hashtag = hashtag)
            
            ## Now I should return relevant tweets
            tweets = Tweet.objects.filter(Q(keyword__keyword_text = q.encode('utf-8')) | Q(author__screen_name = username) | Q(author__name = username) |Q(author__location=location) | Q(keyword__is_hashtag = hashtag)| Q(created_at = created_at))
            tweets = Tweet.objects.filter(keyword__keyword_text = q.encode('utf-8'))
            cache.set("tweets",tweets,CACHE_TTL)
            return tweets

        tweets = Tweet.objects.all()
        cache.set("tweets",tweets,CACHE_TTL)
        return tweets
        
class KeywordListAPIView(ListCreateAPIView):
    """
    This class is responsible for listing keywords 
    """
    serializer_class = KeywordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def get_queryset(self,*args,**kwargs):
        #keywords = cache.get("keywords")
        #if keywords:
         #   return keywords
        if self.request.query_params.get('hashtag'):    
            if self.request.query_params.get('hashtag',None) == 'true':
                keywords = Keyword.objects.filter(is_hashtag = True).order_by('-counter')
                cache.set("keywords",keywords,CACHE_TTL)
                return keywords
            elif self.request.query_params.get('hashtag',None) == 'false':
                keywords = Keyword.objects.filter(is_hashtag = False).order_by('-counter')
                cache.set("keywords",keywords,CACHE_TTL)
                return keywords
        keywords = Keyword.objects.all().order_by('-counter')
        cache.set("keywords",keywords,CACHE_TTL) ## I cached all keywords if there is no any params and my cache is null...
        return keywords

class KeywordDetailAPIView(RetrieveUpdateDestroyAPIView):

    """
    We can retrieve, update and destroy keyword data easily.
    
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = KeywordSerializer
    queryset = Keyword.objects.all()
 

class TopKeywordsListAPIView(ListAPIView):
    """
    We will list keywords in descending order by counter value
    
    """
    serializer_class = KeywordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        is_hashtag = self.request.GET.get('hashtag')
        tweets = None
        if is_hashtag:
            tweets = Keyword.objects.filter(is_hashtag = is_hashtag).order_by('-counter').values()
            cache.set("top-tweets",tweets,CACHE_TTL)
            return tweets
        tweets = Keyword.objects.all().order_by('-counter').values()
        cache.set("top-tweets",tweets,CACHE_TTL)
        return tweets

class AffectedTopTweetsListAPIView(ListAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get_queryset(self):
        keyword = str(self.request.query_params.get('q',None)).encode('utf-8')
        if keyword:
            return Tweet.objects.filter(keyword__keyword_text = keyword).order_by('-author__followers')
    