from django.test import SimpleTestCase
from django.urls import reverse,resolve
from app_twhunter.api.views import TweetListAPIView,KeywordListAPIView,KeywordDetailAPIView,TopKeywordsListAPIView,AffectedTopTweetsListAPIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken as jwt_token
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APITestCase

class ApiUrlsTests(SimpleTestCase):
    """
    Ensure we can resolve urls and then their addressed APIViews..

    """

    def test_tweets_is_resolved(self):
        url = reverse('tweet-list')
        self.assertEquals(resolve(url).func.view_class,TweetListAPIView)

    def test_keywords_is_resolved(self):
        url = reverse('keywords-list')
        self.assertEquals(resolve(url).func.view_class,KeywordListAPIView)
    
    def test_keyword_detail_is_resolved(self):
        url = reverse('keyword-detail',kwargs={'pk' : 1})
        self.assertEquals(resolve(url).func.view_class,KeywordDetailAPIView)
    
    def test_top_keywords_is_resolved(self):
        url = reverse('top-keywords-list')
        self.assertEquals(resolve(url).func.view_class,TopKeywordsListAPIView)
    
    def test_affected_top_tweets_is_resolved(self):
        url =  reverse('top-tweets-affected-list')
        self.assertEquals(resolve(url).func.view_class,AffectedTopTweetsListAPIView)
        


class TweetAPIViewTests(APITestCase):
    tweets_url = reverse('tweet-list')
   

    def setUp(self) -> None:
        """
        I wrote this function because usage of my API requires a JWT Authentication token.
        So we should consider that token and other staff... Every time test class is working, setUp function will work like a constructor..
        """
        self.user = User.objects.create_user(username='tester',password='tester')
        self.token_for_jwt = jwt_token.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token_for_jwt))
      


    def test_users_authenticated(self):
        response = self.client.get(self.tweets_url) ## get request tweet-list url
        self.assertEqual(response.status_code,status.HTTP_200_OK)    

    def test_users_unauthenticated(self):
        self.client.force_authenticate(user = None, token=None) ## I deleted authorization header..
        response = self.client.get(self.tweets_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)  ## I will expect 401..
 
    def test_results_for_none_value(self):
        response = self.client.get(self.tweets_url)
        self.assertNotEqual(response,{})


class KeywordAPIViewTests(APITestCase):
    keywords_url = reverse('keywords-list')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username = 'tester',password ='tester')
        self.token = jwt_token.for_user(self.user).access_token
        self.token_for_auth = Token.objects.create(user = self.user).key

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_for_auth))


    def test_users_authenticated(self):
        response = self.client.get(self.keywords_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_users_unauthenticated(self):
        self.client.force_authenticate(user = None, token=None)
        response = self.client.get(self.keywords_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_results_for_none_value(self):
        response = self.client.get(self.keywords_url)
        self.assertNotEqual(response,None)

    def test_keyword_post(self):
        data = {
            "keyword_text" : "test",
            "is_hashtag" : False,
            "counter" : 1,
        }

        response = self.client.post(self.keywords_url,data = data, format = 'json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertNotEqual(response.data,{})
        self.assertEqual(response.data['keyword_text'],"test")


class KeywordDetailAPIViewTests(APITestCase):
    keyword_detail_url = reverse('keyword-detail',args = [1])
   

    def setUp(self) -> None:
        self.user = User.objects.create_user(username = 'admin',password ='admin')
        self.token = jwt_token.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.token_for_auth = Token.objects.create(user = self.user).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_for_auth))



    def test_users_unauthenticated(self):
        self.client.force_authenticate(user = None, token=None)
        response = self.client.get(self.keyword_detail_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)


class TopKeywordsAPIViewTests(APITestCase):
    top_keywords_url = reverse('top-keywords-list')

    def setUp(self) -> None:
        """
        I wrote this function because usage of my API requires a JWT Authentication token.
        So we should consider that token and other staff... Every time test class is working, setUp function will work like a constructor..
        """
        self.user = User.objects.create_user(username='tester',password='tester')
        self.token = jwt_token.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

        self.token_for_auth = Token.objects.create(user = self.user).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_for_auth))



    def test_users_authenticated(self):
        response = self.client.get(self.top_keywords_url) ## get request tweet-list url
        self.assertEqual(response.status_code,status.HTTP_200_OK)    

    def test_users_unauthenticated(self):
        self.client.force_authenticate(user = None, token=None) ## I deleted authorization header..
        response = self.client.get(self.top_keywords_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)  ## I will expect 401..
    
    
    def test_results_for_none_value(self):
        response = self.client.get(self.top_keywords_url)
        self.assertNotEqual(response,{})


class AffectedTopTweetsAPIViewTests(APITestCase):
    affected_top_tweets_url = reverse('top-tweets-affected-list')


    def setUp(self) -> None:
        self.user = User.objects.create_user(username = 'admin',password ='admin')
        self.token = jwt_token.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

    def test_users_authenticated(self):
        response = self.client.get(self.affected_top_tweets_url) ## get request tweet-list url
        self.assertEqual(response.status_code,status.HTTP_200_OK)    

    def test_users_unauthenticated(self):
        self.client.force_authenticate(user = None, token=None) ## I deleted authorization header..
        response = self.client.get(self.affected_top_tweets_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)  ## I will expect 401..
 
    def test_results_for_none_value(self):
        response = self.client.get(self.affected_top_tweets_url)
        self.assertNotEqual(response,{})



### python manage.py test app_twhunter/api


###  curl -X GET http://127.0.0.1:8000/api/keywords/ -H 'Authorization: Token 3bcd8a8cc16c13f75897589ab5d671fe582cd4ed'
