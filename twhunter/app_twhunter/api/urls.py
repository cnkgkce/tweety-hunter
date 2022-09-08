from django.urls import path
from . import views

urlpatterns = [
path('tweets/',views.TweetListAPIView.as_view(),name='tweet-list'),
path('keywords/',views.KeywordListAPIView.as_view(),name='keywords-list'),
path('keyword/<int:pk>',views.KeywordDetailAPIView.as_view(),name='keyword-detail'),
path('keywords/top',views.TopKeywordsListAPIView.as_view(),name='top-keywords-list'),
path('tweets/top/affected',views.AffectedTopTweetsListAPIView.as_view(),name='top-tweets-affected-list'),
]
