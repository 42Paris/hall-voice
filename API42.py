import requests


class API42(object):
    def __init__(self, conf):
        apiKey = conf.getAPIkeys()
        self.apiUID = apiKey[0]
        self.apiSEC = apiKey[1]
        self.token = self.getToken()

    def getToken(self):
        print("Getting token")
        r = requests.post(
            "https://api.intra.42.fr/oauth/token?grant_type=client_credentials&client_id=" + self.apiUID + "&client_secret="
            + self.apiSEC)
        if r.status_code == 200:
            print("Token getted")
            return r.json()["access_token"]
        else:
            print("Error while getting token")
            return None

    def getUsualName(self, login) -> str:
        if self.token is None:
            self.getToken()
        url = "https://api.intra.42.fr/v2/users/" + login + "?access_token=" + self.token
        intra = requests.get(url)
        # If 42api return stuff
        if intra is not None and intra.status_code == 200:
            # Get the usual name
            firstname = intra.json()["usual_first_name"]
            # If there is no usual name, take the first_name
            if firstname is None:
                firstname = intra.json()["first_name"]
            return firstname
        else:
            self.getToken()
            return ""
