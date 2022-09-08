import logging
from typing import Any, Dict
from requests import Session
from requests.exceptions import HTTPError,ConnectionError,InvalidURL
import re
from pyquery import PyQuery
from app_twhunter.models import Tweet,Author,Keyword


EMAIL = 'test@test.com'
PASSWORD = 'mysupersecretpassword'
SCREEN_NAME = 'tester'

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)



class CrawlTwitter:
    BASE_URL  = 'https://twitter.com'


    def __init__(self):
        self.s = Session()
        self.params = {}
        self.s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"})
   

    def login_twitter(self):
        """
        This function is responsible for authentication processes on Twitter...

        This function can be changed due to Twitter authentication policies.. Keep it update ! 
        
        """
        try:
            pq = PyQuery(self.s.get(self.BASE_URL).text)

            script_url = pq.find("link[href*='/main.']").attr("href")

            resp = self.s.get(script_url)
            bearer_token = re.findall(r"s=\"(A+[^\"]{20,})\"",resp.text)[0]
           
            logging.info(f"[+] Found Bearer token is found  as {bearer_token}")
            self.s.headers.update({"Authorization": f"Bearer {bearer_token}"})

            resp = self.s.post("https://api.twitter.com/1.1/guest/activate.json")
            guest_token = resp.json()["guest_token"]
            
            logging.info(f"[+] Guest token is found as {guest_token}")

            self.s.headers.update({"X-Guest-Token" : guest_token})
            resp = self.s.post("https://twitter.com/i/api/1.1/onboarding/task.json?flow_name=login",json={"input_flow_data":{"flow_context":{"debug_overrides":{},"start_location":{"location":"splash_screen"}}},"subtask_versions":{"contacts_live_sync_permission_prompt":0,"email_verification":1,"topics_selector":1,"wait_spinner":1,"cta":4}})
            flow_token = resp.json()["flow_token"]
       
            logging.info(f"[+] Flow token is found as {flow_token}")
            resp = self.s.post('https://twitter.com/i/api/1.1/onboarding/task.json',json={"flow_token":flow_token,"subtask_inputs":[{"subtask_id":"LoginEnterUserIdentifierSSO","settings_list":{"setting_responses":[{"key":"user_identifier","response_data":{"text_data":{"result":EMAIL}}}],"link":"next_link"}}]})
            flow_token = flow_token.replace(":0",":1")
      
            logging.info(f"[+] Flow token is refreshing as {flow_token}")

            resp = self.s.post('https://twitter.com/i/api/1.1/onboarding/task.json',json={"flow_token":flow_token,"subtask_inputs":[{"subtask_id":"LoginEnterUserIdentifierSSO","settings_list":{"setting_responses":[{"key":"user_identifier","response_data":{"text_data":{"result":EMAIL}}}],"link":"next_link"}}]})
            flow_token = resp.json()["flow_token"]
        
            if flow_token.endswith(":4"):
                logging.info("Uppss capctha!!")
                resp = self.s.post('https://twitter.com/i/api/1.1/onboarding/task.json',json={"flow_token":flow_token,"subtask_inputs":[{"subtask_id":"LoginEnterAlternateIdentifierSubtask","enter_text":{"text":SCREEN_NAME,"link":"next_link"}}]})
                flow_token = resp.json()["flow_token"]

            resp = self.s.post('https://twitter.com/i/api/1.1/onboarding/task.json',json={"flow_token":flow_token,"subtask_inputs":[{"subtask_id":"LoginEnterPassword","enter_password":{"password":PASSWORD,"link":"next_link"}}]})
            flow_token = resp.json()["flow_token"]  ###6
        
            resp = self.s.post('https://twitter.com/i/api/1.1/onboarding/task.json',json={"flow_token":flow_token,"subtask_inputs":[{"subtask_id":"AccountDuplicationCheck","check_logged_in_account":{"link":"AccountDuplicationCheck_false"}}]})
            flow_token = resp.json()["flow_token"]  ###12 
          

            if resp.json()["status"] == "success":
                account_dict = resp.json()["subtasks"][0]["open_account"]
                username_from_resp = account_dict["user"]["name"]
                screen_name_from_resp = account_dict["user"]["screen_name"]
                print(f"[*] Found username is  {username_from_resp}")
                print(f"[*] Found screen name is {screen_name_from_resp}")
                print(" [+] Login Succeed")
            else:
                print(" [!] Login Failed")

            self.s.headers.update({"X-Csrf-Token" : self.s.cookies["ct0"]})
            resp = self.s.get('https://twitter.com/i/api/1.1/account/settings.json?include_mention_filter=true&include_nsfw_user_flag=true&include_nsfw_admin_flag=true&include_ranked_timeline=true&include_alt_text_compose=true&ext=ssoConnections&include_country_code=true&include_ext_dm_nsfw_media_filter=true&include_ext_sharing_audiospaces_listening_data_with_followers=true')

            

        except(HTTPError,ConnectionError,InvalidURL,TimeoutError) as e:
            logging.error(e)

    def create_or_retrieve_keyword_obj(self,keyword:str,is_hashtag:bool,counter:int,*args,**kwargs) -> Keyword:
        """
        This function takes an string argument which name is keyword and controls 
        database whether there is a record in this keyword or not. 
        If there is a record in this keyword, it will retrieve from db and return that object.
        If there is no record in this keyword, it will create a new Keyword object, save database and return that object

        Params:
        >>> keyword (str) = q value, keyword which comes from view
        >>> is_hashtag (bool) = keyword contains # or not
        >>> counter (int) = Number of tweets about given keyword

        Returns:
        Returns Keyword object

        >>> create_or_retrieve_keyword_obj("suriye",False,2)
            <Response [200]>


      """
       
        keyword_from_db = Keyword.objects.filter(keyword_text = str(keyword).encode('utf-8'),is_hashtag = is_hashtag).first()
        if keyword_from_db:
            keyword_from_db.counter = counter
            keyword_from_db.save()
            return keyword_from_db
        keyword_from_db = Keyword(keyword_text = str(keyword).encode('utf-8'),is_hashtag = is_hashtag)
        keyword_from_db.save()
        return keyword_from_db


    def create_author_obj(self,data:Dict[str,Any],*args,**kwargs) -> None:

        """
        This function takes an data in Dict type and fetches relevant fields from data.
        Then, it will check db for every loop iteration whether there is a record about this user or not.
        Finally, it will create an author object and return it.
        
        Params:
        >>> data (Dict[str,Any]) = Dictionary object contains content from API

        """
        for author_id in data:
            name = data[author_id]["name"]
            screen_name = data[author_id]["screen_name"]
            location = data[author_id]["location"]
            bio = data[author_id]["description"]
            followers = data[author_id]["followers_count"]
            following = data[author_id]["friends_count"]
            created_at = data[author_id]["created_at"]

            if not Author.objects.filter(author_id = author_id).first():
                Author(author_id = author_id,name=name,screen_name=screen_name,followers=followers,following=following,created_at=created_at,location = location,bio =bio).save()
            else:
                continue


    def crawler(self,keyword:str,is_hashtag:bool=False,*args,**kwargs) -> None:
        """
        This function takes an keyword and hashtag of tweets as a boolean, which  makes a request to the Twitter.com . After request, it takes an json response and calls 
        relevant functions which names are create_author_obj() and create_or_retrieve_keyword_obj(). 
        After taking some required data from that response, it loops over the data and creates a Tweet object and saves into database.
        
        """
        self.s.headers.update({"Referer":f"{self.BASE_URL}/search?q={keyword}&src=typed_query"})
        self.s.headers.update({"X-Csrf-Token" : self.s.cookies["ct0"]})
        self.s.headers.update({"Content-Type" : "application/x-www-form-urlencoded"})
        self.params = {
            'include_profile_interstitial_type':1,
            'include_blocking':1,
            'include_blocked_by':1,
            'include_followed_by':1,
            'include_want_retweets':1,
            'include_mute_edge':1,
            'include_can_dm':1,
            'include_can_media_tag':1,
            'include_ext_has_nft_avatar':1,
            'skip_status':1,
            'cards_platform':'Web-12', 
            'include_cards' :1,
            'include_ext_alt_text':'true',
            'include_quote_count':'true',
            'include_reply_count':1,
            'tweet_mode':'extended',
            'include_ext_collab_control':'true',
            'include_entities':'true',
            'include_user_entities':'true',
            'include_ext_media_color':'true',
            'include_ext_media_availability':'true',
            'include_ext_sensitive_media_warning':'true',
            'include_ext_trusted_friends_metadata':'true',
            'send_error_codes':'true',
            'simple_quoted_tweet':'true',
            'q':keyword,
            'count':50,
            'query_source':'typed_query',
            'pc':1,
            'spelling_corrections':1,
            'include_ext_edit_control':'true',
            'ext':'mediaStats%2ChighlightedLabel%2ChasNftAvatar%2CvoiceInfo%2Cenrichments%2CsuperFollowMetadata%2CunmentionInfo%2CeditControl%2Ccollab_control%2Cvibe'
        }
        
        resp = self.s.get("https://twitter.com/i/api/2/search/adaptive.json",params=self.params)

        authors_from_resp = resp.json()["globalObjects"]["users"]
        tweets_from_resp  = resp.json()["globalObjects"]["tweets"]
    
        

        self.create_author_obj(data = authors_from_resp)  ## This function creates authors from given dataset


        counter = len(tweets_from_resp)

        keyword_obj = self.create_or_retrieve_keyword_obj(keyword = keyword, is_hashtag=is_hashtag, counter = counter)



        for tweet_id in tweets_from_resp:
            full_text = tweets_from_resp[tweet_id]["full_text"]
            tweet_created_at = tweets_from_resp[tweet_id]["created_at"]
            author_id = tweets_from_resp[tweet_id]["user_id"]
            retweet_count = tweets_from_resp[tweet_id]["retweet_count"]
            favorite_count = tweets_from_resp[tweet_id]["favorite_count"]
            reply_count = tweets_from_resp[tweet_id]["reply_count"]
            quote_count = tweets_from_resp[tweet_id]["quote_count"]


            if Author.objects.filter(author_id = author_id).first(): ### checks author from db, if author exists we can do our staff but if not, we will continue over the loop
                if keyword_obj:                        
                    tweet =Tweet(tweet_id = tweet_id,author=Author.objects.get(author_id = author_id),message = full_text,created_at = tweet_created_at,retweet_count = retweet_count,favorite_count = favorite_count,reply_count = reply_count,quote_count = quote_count)
                    tweet.save()
                    tweet.keyword.set([keyword_obj])        
            else:
                continue

            logging.info("Tweet is created and saved database")



