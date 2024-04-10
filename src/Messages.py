import datetime
import os
import json
import redis
from io import BytesIO
from random import choice, randint
from gtts import gTTS, gTTSError
from pygame import mixer


class Messages(object):
    def __init__(self, conf, api) -> None:
        self.redis = redis.Redis(host='127.0.0.1', port=6379, db=0)
        self.welcomeMsg = conf.getWelcome()
        self.goodbyeMsg = conf.getGoodbye()
        self.buildingName = conf.getBuilding()
        self.api = api
        mixer.init()

    def processMessage(self, msg: str) -> None:
        data = json.loads(msg)
        if data["firstname"] == "chantier":
            return
        if self.buildingName != data["building"]:
            return
        print(f"[{datetime.datetime.now()}] NEW MESSAGE: {msg}")
        kind = data['kind']
        login = data['login']
        firstname = ""
        if login is not None and login != "":
            firstname = self.api.getUsualName(login)
        if firstname is None or firstname == "":
            firstname = data["firstname"]
        jsonFile = "custom/" + login + ".json"
        if os.path.isfile(jsonFile):
            print(f"[{datetime.datetime.now()}] Custom HallVoice for " + login)
            self.playCustomSound(kind, jsonFile, firstname)
            return
        else:
            self.genericMessage(firstname, kind)

    def playCustomSound(self, kind: str, jsonFile: str, firstname: str) -> None:
        kind = "welcome" if kind == "in" else "goodbye"
        try:
            with open(jsonFile, 'r') as custom_file:
                j = json.loads(custom_file.read())
                if kind in j:
                    if "mp3" in j[kind]:
                        if os.path.isdir("mp3/" + j[kind]["mp3"]) is True:
                            mixer.music.load("mp3/" + j[kind]["mp3"] + "/" + choice(os.listdir("mp3/" + j[kind]["mp3"])))
                        elif os.path.isfile("mp3/" + j[kind]["mp3"]) is True:
                            mixer.music.load("mp3/" + j[kind]["mp3"])
                        mixer.music.play()
                        while mixer.music.get_busy():
                            pass
                    elif "txt" in j[kind]:
                        lang = j[kind]["lang"] if "lang" in j[kind] else "fr"
                        if isinstance(j[kind]["txt"], list):
                            self.say(j[kind]["txt"][randint(0, len(j[kind]["txt"]) - 1)], lang)
                        elif isinstance(j[kind]["txt"], str):
                            self.say(j[kind]["txt"], lang)
                else:
                    self.genericMessage(firstname, kind)
        except FileNotFoundError as e:
            print(f"Custom HallVoice for {firstname} not found:\n{e}")

    def genericMessage(self, firstname: str, kind: str) -> None:
        tts = ""
        if kind == "welcome" or kind == "in":
            tts = self.welcomeMsg[randint(0, len(self.welcomeMsg) - 1)][1].replace("<name>", firstname)
        elif kind == "goodbye" or kind == "out":
            tts = self.goodbyeMsg[randint(0, len(self.goodbyeMsg) - 1)][1].replace("<name>", firstname)
        print(f"[{datetime.datetime.now()}] {tts}")
        self.say(tts, "fr")

    def say(self, txt: str, lang: str) -> None:
        mp3_fp = BytesIO()
        if txt is not None and txt != "":
            cache = self.redis.get(txt+lang)  # Get the TTS from cache
            if cache:  # If TTS is cached, play it
                print(f"[{datetime.datetime.now()}] TTS cache getted!")
                mp3_fp.write(cache)
                mp3_fp.seek(0)  # Reset the file pointer to the beginning
                self.playMP3(mp3_fp)
            else:  # If TTS is NOT cached, cache it AND play it...
                print(f"[{datetime.datetime.now()}] TTS cache not found, putting in cache")
                try:
                    # Generate speech using gTTS and save to a BytesIO object
                    tts = gTTS(text=txt, lang=lang)
                    # Create and write the TTS to a BytesIO
                    mp3_fp = BytesIO()
                    tts.write_to_fp(mp3_fp)
                    # Convert the MP3 BytesIO object to WAV format in memory
                    mp3_fp.seek(0)  # Reset the file pointer to the beginning
                    self.redis.set(txt+lang, mp3_fp.read())
                    mp3_fp.seek(0)  # Reset the file pointer to the beginning, again...
                    self.playMP3(mp3_fp)
                except gTTSError as e:  # If we break gTTS API with rate-limit
                    print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS error:\n{e}")
        else:
            print(f"[{datetime.datetime.now()}] Cannot TTS, var txt is None")
            cache = self.redis.get("HallvoiceERROR")
            if cache:
                print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS cached")
                self.playMP3(cache)
            else:
                print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS not cached, caching him")
                try:
                    tts = gTTS(text="Hallvoice Error, please contact staff member", lang="en")
                    tts.write_to_fp(mp3_fp)
                    # Convert the MP3 BytesIO object to WAV format in memory
                    mp3_fp.seek(0)  # Reset the file pointer to the beginning
                    self.redis.set("HallvoiceERROR", mp3_fp.read())
                    mp3_fp.seek(0)
                    self.playMP3(mp3_fp)
                except gTTSError as e:
                    print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS error:\n{e}")

    @staticmethod
    def playMP3(mp3) -> None:
        mixer.music.load(mp3)
        mixer.music.play()
        while mixer.music.get_busy():
            pass
