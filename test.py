#!/usr/bin/env python

import os, json, signal, sys, urllib, urllib2, time, subprocess, hashlib, glob
from random import *

def say(txt, lang):
    t = txt.encode('utf-8')
    tmp = (txt + " / " + lang)
    hash = hashlib.md5(tmp.encode('utf-8')).hexdigest()
    fname = "cache/" + hash + ".mp3"
    print fname

with open("custom/sb.json", 'r') as custom_file:
    try:
        j = json.loads(custom_file.read())
        j = j['welcome']
        print j
        if ("txt" in j.keys()):
            msg = j["txt"]
        if ("lang" in j.keys()):
            lang = j["lang"]
        if ("mp3" in j.keys()):
            mp3 = "mp3/" + j["mp3"]
            if (os.path.isdir(mp3)):
                mp3 = choice(glob.glob(mp3 + "*.mp3"))
            print mp3
    except:
        print "cannot load json"
    if (msg != ""):
        print msg
        say(msg, lang)

