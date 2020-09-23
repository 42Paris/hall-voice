#!/usr/bin/env python

import os, json, signal, sys, urllib, urllib2, time, subprocess, hashlib, glob
from random import *

CONFIG_FILE = 'config.json'

"""
Open and load a file at the json format
"""

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print "File [%s] doesn't exist, aborting." % (CONFIG_FILE)
        sys.exit(1)

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

def say(txt, lang):
    t = txt.encode('utf-8')
    tmp = (txt + " / " + lang)
    hash = hashlib.md5(tmp.encode('utf-8')).hexdigest()
    fname = "cache/" + hash + ".mp3"
    if ((os.path.isfile(fname) == False) or (os.stat(fname).st_size == 0)):
        urltts = config["tts"] + "?" + urllib.urlencode({'t':t, 'l':lang})
        print urltts
        urllib.urlretrieve(urltts, fname)
    cmd = config["player"] + [fname]
    print cmd
    subprocess.call(cmd)

def welcome(login, prenom):
    msg = ""
    mp3 = ""
    lang = "fr"
    jname = "custom/" + login + ".json"
    if (os.path.isfile(jname)):
        with open(jname, 'r') as custom_file:
            print jname
            try:
                j = json.loads(custom_file.read())
                if (m  in j.keys()):
                    j = j[m]
                print j
                if ("txt" in j.keys()):
                    msg = j["txt"]
                if ("lang" in j.keys()):
                    lang = j["lang"]
                if ("mp3" in j.keys()):
                    mp3 = "mp3/" + j["mp3"]
                    if (os.path.isdir(mp3)):
                        mp3 = choice(glob.glob(mp3 + "/*.mp3"))
                    print mp3
            except:
                print "cannot load json"
    if (msg == "" and mp3 == ""):
        msg = choice(config["msgs"][m]) + " " + prenom
    if (msg != ""):
        print msg
        say(msg, lang)
    if (mp3 != ""):
        cmd = config["player"] + [mp3]
        print cmd
        subprocess.call(cmd)
    
"""
Main
"""

if __name__ == "__main__":
    porte = sys.argv[1]
    m = sys.argv[2]
    signal.signal(signal.SIGINT, signal_handler)
    config = open_and_load_config()
    last_id = ""
    url = config["host"] + "?pid=" + config["doors"][porte] + "&eid=0"
    while 1:
        try:
            res = json.loads(urllib2.urlopen(url).read())
            if ((res["id"] != last_id) and ("login" in res.keys()) and ("firstname" in res.keys())):
                if (("pin" in res.keys()) and (res["pin"] != "") and ("rpin" in res.keys()) and (res["pin"] != res["rpin"])):
                    print "game over"
                    print "pid: %s, rpid: %s" % (res["pin"],  res["rpin"])
                    say("game over", "en")
                else:
                    if ("usual_first_name" in res.keys()):
                        welcome(res["login"], res["usual_first_name"])
                    else:
                        welcome(res["login"], res["firstname"])
                last_id = res["id"]
        except:
            pass
        time.sleep(1)
