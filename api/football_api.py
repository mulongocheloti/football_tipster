import requests
import time
from config.settings import API_TOKEN, MAX_CALLS_PER_MINUTE

class FootballAPI:

    def __init__(self):

        self.headers={"X-Auth-Token":API_TOKEN}
        self.calls=0

    def get(self,url,params=None):

        if self.calls>=MAX_CALLS_PER_MINUTE:

            print("API call limit reached safely")
            exit()

        r=requests.get(url,headers=self.headers,params=params)

        if r.status_code!=200:

            print("API error",r.status_code)
            exit()

        self.calls+=1

        time.sleep(6)

        return r.json()