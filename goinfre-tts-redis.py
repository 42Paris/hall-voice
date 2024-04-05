import configparser
import datetime
import time
from io import BytesIO
import redis
import threading
from gtts import gTTS
from pygame import mixer

mixer.init()


with open("config.ini", "r"):
    config = configparser.ConfigParser()
    config.read("config.ini")
    apiUID = config.get("42api", "uid")
    apiSEC = config.get("42api", "secret")
    welcome = []
    goodbye = []
    for welcomeMsg in config.items("welcome"):
        welcome.append(welcomeMsg)
    for goodbyeMsg in config.items("goodbye"):
        goodbye.append(goodbyeMsg)


def api_call(start_l, end_l):
    with open("login.list", "r") as f:
        for i, line in enumerate(f):
            if i < start_l:
                continue
            elif i >= end_l:
                break
            else:
                firstname_cache = r.get(f"login: {line.strip()}").decode("utf-8")
                if firstname_cache is not None:
                    for v in welcome:
                        txt = v[1].replace("<name>", firstname_cache)
                        tts_cache = r.get(txt + "fr")
                        if tts_cache:
                            print(f"[{datetime.datetime.now()}] TTS cache getted for: {txt}")
                        else:
                            print(f"[{datetime.datetime.now()}] TTS cache not found for: {txt}")
                            # Generate speech using gTTS and save to a BytesIO object
                            tts = gTTS(text=txt, lang="fr")
                            # Create and write the TTS to a BytesIO
                            mp3_fp = BytesIO()
                            tts.write_to_fp(mp3_fp)
                            # Convert the MP3 BytesIO object to WAV format in memory
                            mp3_fp.seek(0)  # Reset the file pointer to the beginning
                            r.set(txt + "fr", mp3_fp.read())
                    for v in goodbye:
                        txt = v[1].replace("<name>", firstname_cache)
                        tts_cache = r.get(txt + "fr")
                        if tts_cache:
                            print(f"[{datetime.datetime.now()}] TTS cache getted for: {txt}")
                        else:
                            print(f"[{datetime.datetime.now()}] TTS cache not found for: {txt}")
                            # Generate speech using gTTS and save to a BytesIO object
                            tts = gTTS(text=txt, lang="fr")
                            # Create and write the TTS to a BytesIO
                            mp3_fp = BytesIO()
                            tts.write_to_fp(mp3_fp)
                            # Convert the MP3 BytesIO object to WAV format in memory
                            mp3_fp.seek(0)  # Reset the file pointer to the beginning
                            r.set(txt + "fr", mp3_fp.read())
                else:
                    print(f"Cannot cache TTS for {line.strip()}")


print("Successfully getted a token")
nb_threads = 1
r = redis.Redis(host='127.0.0.1', port=6379, db=0)
with open("login.list", "r") as f:
    file = f.readlines()
    chunk_size = len(file) // nb_threads
    threads = []
    for i in range(nb_threads):
        start_line = i * chunk_size
        # Make sure to handle the last chunk properly if it has fewer lines
        end_line = start_line + chunk_size if i < nb_threads - 1 else len(file)
        thread = threading.Thread(target=api_call, args=(start_line, end_line))
        # threads.append(thread)
        time.sleep(2)
        thread.start()
    for thread in threads:
        thread.join()
