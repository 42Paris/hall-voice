import datetime
import os
import json
import sys
import pygame
import redis
from io import BytesIO
from random import choice, randint
from gtts import gTTS, gTTSError


class Messages(object):
    def __init__(self, conf, api) -> None:
        self.redis = redis.Redis(host=conf.getRedisHost(), port=conf.getRedisPort(), db=0)
        self.welcomeMsg: list[tuple[str, str]] = conf.getWelcome()
        self.goodbyeMsg: list[tuple[str, str]] = conf.getGoodbye()
        self.buildingName: str = conf.getBuilding()
        self.redis_ttl: int = conf.getRedisTTL()
        self.mp3Path: str = conf.getMP3Path()
        self.customPath: str = conf.getCustomPath()
        self.api = api
        pygame.mixer.init()

    def processMessage(self, msg: str) -> None:
        data = json.loads(msg)
        if data["firstname"] == "chantier":
            return
        if self.buildingName != data["building"]:
            return
        print(f"[{datetime.datetime.now()}] NEW MESSAGE: {msg}")
        kind: str = data['kind']
        login: str = data['login']
        firstname: str = ""
        if login is not None and login != "":
            firstname: str = self.api.getUsualName(login)
        if firstname is None or firstname == "":
            firstname: str = data["firstname"]
        jsonFile: str = (self.customPath + login + ".json")
        if os.path.isfile(jsonFile):
            print(f"[{datetime.datetime.now()}] Custom HallVoice for " + login + ": " + jsonFile)
            self.playCustomSound(kind, jsonFile, firstname)
            return
        else:
            self.genericMessage(firstname, kind)

    def playCustomSound(self, kind: str, jsonFile: str, firstname: str) -> None:
        kind: str = "welcome" if kind == "in" else "goodbye"
        try:
            with open(jsonFile, 'r') as custom_file:
                j = json.loads(custom_file.read())
                if kind in j:
                    if "mp3" in j[kind]:
                        try:
                            if os.path.isdir(self.mp3Path + j[kind]["mp3"]) is True:
                                customMP3 = (self.mp3Path + j[kind]["mp3"] + "/" + choice(os.listdir(self.mp3Path +
                                                                                                     j[kind]["mp3"])))
                                pygame.mixer.music.load(customMP3)
                            elif os.path.isfile(self.mp3Path + j[kind]["mp3"]) is True:
                                customMP3 = self.mp3Path + j[kind]["mp3"]
                                pygame.mixer.music.load(customMP3)
                            else:
                                self.playError("Error while loading a random mp3 file, please contact staff member")
                                print(f"[{datetime.datetime.now()}] Error for custom hallvoice {jsonFile}"
                                      f", invalid path")
                                return
                            print(f"[{datetime.datetime.now()}] Playing {customMP3}")
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                pass
                        except pygame.error as e:
                            print(f"[{datetime.datetime.now()}] Error while plying a custom song with pygame.mixer():"
                                  f"\n{e}")
                            self.playError("Error while playing a custom song, please contact staff member")
                        except FileNotFoundError as e:
                            self.playError("Error while loading your custom MP3 file, please contact staff member")
                            print(f"[{datetime.datetime.now()}] Custom HallVoice for {firstname} not found:\n{e}")
                    elif "txt" in j[kind]:
                        lang: str = j[kind]["lang"] if "lang" in j[kind] else "fr"
                        if isinstance(j[kind]["txt"], list):
                            self.say(j[kind]["txt"][randint(0, len(j[kind]["txt"]) - 1)], lang)
                        elif isinstance(j[kind]["txt"], str):
                            self.say(j[kind]["txt"], lang)
                else:
                    self.playError(f"Invalide JSON file {jsonFile}, please check your PR")
                    print(f"[{datetime.datetime.now()}] Invalide JSON file {jsonFile}, kind in/out not found")
        except FileNotFoundError as e:
            self.playError("Error while loading your custom JSON, please contact staff member")
            print(f"[{datetime.datetime.now()}] Custom HallVoice for {firstname} not found:\n{e}")
        except Exception as e:
            self.playError("A Serious error happend, please contact staff member")
            print(f"[{datetime.datetime.now()}] Random Exception at playCustomSound():\n{e}")

    def genericMessage(self, firstname: str, kind: str) -> None:
        tts: str = ""
        if kind == "welcome" or kind == "in":
            tts: str = self.welcomeMsg[randint(0, len(self.welcomeMsg) - 1)][1].replace("<name>", firstname)
        elif kind == "goodbye" or kind == "out":
            tts: str = self.goodbyeMsg[randint(0, len(self.goodbyeMsg) - 1)][1].replace("<name>", firstname)
        self.say(tts, "fr")

    def say(self, txt: str, lang: str) -> None:
        mp3_fp = BytesIO()
        if txt is not None and txt != "":
            print(f"[{datetime.datetime.now()}] Playing TTS: {txt}")
            cache = self.redis.get(txt + lang)  # Get the TTS from cache
            if cache:  # If TTS is cached, play it
                print(f"[{datetime.datetime.now()}] TTS cache getted!")
                mp3_fp.write(cache)
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
                    self.redis.set(txt + lang, mp3_fp.read(), ex=self.redis_ttl)
                    self.playMP3(mp3_fp)
                except gTTSError as e:  # If we break gTTS API with rate-limit
                    print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS error:\n{e}")
                    self.playMP3(mp3_fp)
        else:
            self.playError("Error while generating TTS message, please contact staff member")
            print(f"[{datetime.datetime.now()}] TTS messages generation error for txt: {txt}")

    @staticmethod
    def playMP3(mp3: BytesIO) -> None:
        mp3.seek(0)  # Reset the file pointer to the beginning
        pygame.mixer.music.load(mp3)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass

    def playError(self, message: str) -> None:
        mp3_fp = BytesIO()
        cache = self.redis.get(f"HallvoiceERROR+{message}")
        if cache:
            print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS cached")
            mp3_fp.write(cache)
            self.playMP3(mp3_fp)
        else:
            print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS not cached, caching him")
            try:
                tts = gTTS(text=message, lang="en")
                tts.write_to_fp(mp3_fp)
                # Convert the MP3 BytesIO object to WAV format in memory
                mp3_fp.seek(0)  # Reset the file pointer to the beginning
                self.redis.set(f"HallvoiceERROR+{message}", mp3_fp.read(), ex=self.redis_ttl)
                self.playMP3(mp3_fp)
            except gTTSError as e:
                print(f"[{datetime.datetime.now()}] HallvoiceERROR TTS error:\n{e}")
