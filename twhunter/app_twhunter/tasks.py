from __future__ import absolute_import, unicode_literals
from typing import Any, Dict, List
from celery import shared_task
from .models import Keyword



@shared_task     ## I prefered shared_task decorator because I don't want to initialize Celery app in every task. It can be used for reusable apps.
def test_task(x,y):
    return x+y

    
@shared_task
def check_keywords() -> List[Dict[str,Any]]:  ### it returns Queryset.. queryset is not a list but behaves like a list
    """
     This function checks keywords recorded in database and returns a queryset
    
    """
    return Keyword.objects.filter(is_hashtag = False)



@shared_task
def check_hashtags() -> List[Dict[str,Any]]:
    """
    This function checks hashtags recorded in database and returns a queryset

    """
    return Keyword.objects.filter(is_hashtag = True)