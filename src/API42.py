import datetime
import requests
import redis
import time


class API42(object):
    def __init__(self, conf) -> None:
        self.redis = redis.Redis(host=conf.getRedisHost(), port=conf.getRedisPort(), db=0)
        self.redis_ttl: int = conf.getRedisTTL()
        apiKey: list[str] = conf.getAPIkeys()
        self.apiUID: str = apiKey[0]
        self.apiSEC: str = apiKey[1]
        self.token: str = self.getToken()

    def getToken(self) -> str | None:
        print(f"[{datetime.datetime.now()}] Getting token")
        r = requests.post(
            "https://api.intra.42.fr/oauth/token?grant_type=client_credentials&client_id=" + self.apiUID +
            "&client_secret=" + self.apiSEC)
        if r.status_code == 200:
            print(f"[{datetime.datetime.now()}] Token getted")
            return r.json()["access_token"]
        else:
            print(f"[{datetime.datetime.now()}] Error while getting token")
            return None

    def getUsualName(self, login) -> str | None:
        if self.token is None:
            self.getToken()
        url = "https://api.intra.42.fr/v2/users/" + login + "?access_token=" + self.token
        cached_data = self.redis.get(f"login: {login}")
        if cached_data:
            print(f"[{datetime.datetime.now()}] API cache data found for {login}")
            # Return firstname if it is in redis cache
            return str(cached_data.decode('utf-8'))
        else:
            print(f"[{datetime.datetime.now()}] API cache data not found for {login}, putting in cache")
            intra = requests.get(url)
            if intra.status_code == 404:
                print(f"[{datetime.datetime.now()}] API Error 404, returning None, Firstname in CA will be use")
                return None
            elif intra.status_code == 429:
                print(f"[{datetime.datetime.now()}] API42 rate limited, waiting {intra.headers['Retry-After']} seconds")
                time.sleep(int(intra.headers['Retry-After']))
                self.getToken()
                time.sleep(3)
                intra = requests.get(url)
            if intra.status_code != 200:
                print(f"[{datetime.datetime.now()}] Error while getting user name for {login},"
                      f" getting new token and retry")
                # Get new token if status code != 200
                self.getToken()
                # Retry call
                intra = requests.get(url)
            # If 42api return stuff and status code is 200
            if intra is not None and intra.status_code == 200:
                # Get the usual name
                firstname = intra.json()["usual_first_name"]
                # If there is no usual name, take the first_name
                if firstname is None:
                    firstname = intra.json()["first_name"]
                    # Putting in redis cache
                self.redis.set(f"login: {login}", firstname, ex=self.redis_ttl)  # Cache the firstname for 6 month
                return firstname
