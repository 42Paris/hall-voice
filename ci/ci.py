
import signal
import sys, os, time
import subprocess

from flask import Flask
from flask import request
from flask_hookserver import Hooks

import urllib2
import requests
import json
import logging
logging.captureWarnings(True)
import git

config = {}

def signal_handler(signal, frame):
    global ngrok
    print('Exiting...')
    ngrok.terminate()
    sys.exit(0)

def read_config(cf):
    global config
    with open(cf) as json_data_file:
        config = json.load(json_data_file)
        print config

def start_ngrok():
    global ngrok
    FNULL = open(os.devnull, 'w')
    ngrok = subprocess.Popen(["./ngrok", "start", "--none", "-config", "./ngrok.yml"])
    time.sleep(2)
    assert ngrok.poll() is None, "ngrok terminated abrutly"

def create_tunnel(name, port, inspect = False):
    headers = {"Content-Type": "application/json" }
    datas = {
        "name": name,
        "addr": str(port),
        "proto": "http",
        "inspect": inspect
        }
    print datas
    r = requests.post('http://localhost:4040/api/tunnels',  headers=headers, data=json.dumps(datas))
    try:
        j = r.json()
    except:
        j = {}
    return j

def get_public_url():
    try:
        response = urllib2.urlopen('http://localhost:4040/api/tunnels')
        data = json.load(response)   
    except:
        data = {}
    tuns = data.get('tunnels', [])
    public_url = ''
    for t in tuns:
        if (t.get('name', '') == 'dash'):
            print "Dashboard url: " + t.get('public_url', '')
        if (t.get('name', '') == 'http'):
            public_url = t.get('public_url', '')
    return public_url

def get_github_webhooks(url, headers):
    r = requests.get(url, headers=headers)
    return r.json()

def add_github_webhooks(url, headers, pu):
    datas = {'name': 'web',
             'active': True,
             'events': ['*'],
             'config': {'url': pu,
                        'content_type': 'json'}
             }
    print datas
    r = requests.post(url, headers=headers, data=json.dumps(datas))
    print r.text
    return r.json()

def edit_github_webhooks(url, headers, pu, w):
    datas = {
        'config': {'url': pu, 'content_type': 'json'}
        }
    r = requests.patch(url + '/' + str(w.get('id', 0)), headers=headers, data=json.dumps(datas))
    print r.text

def update_github_webhook(token, owner, repo, pu):
    headers = {'Authorization': 'token ' + token}
    url = 'https://api.github.com/repos/' + owner + '/' + repo + '/hooks'
    print url
    wh = get_github_webhooks(url, headers)
    for w in wh:
        if (w.get('name') == 'web'):
            print "Hook already exists on github"
            if (w.get('config', {}).get('url', '') != pu):
                print "Updating hook to " + pu
                edit_github_webhooks(url, headers, pu, w)
            else:
                print "Hook already set to " + pu
            return
    print "Creating hook on github"
    add_github_webhooks(url, headers, pu)

read_config('config.json')

start_ngrok()
time.sleep(1)

create_tunnel("http", 5000, True)
time.sleep(1)
create_tunnel("dash", 4040, False)
time.sleep(1)

pu = get_public_url()
print pu

if (pu != ''):
    update_github_webhook(config.get('github-token'),
                          config.get('github-owner'),
                          config.get('github-repo'), pu)
else:
    print "Fatal: unable to retrieve ngrok tunnel url"
    ngrok.terminate()
    sys.exit(0)


app = Flask(__name__)
app.config['VALIDATE_IP'] = False
app.config['VALIDATE_SIGNATURE'] = False
hooks = Hooks(app, url='/')

@hooks.hook('ping')
def ping(data, guid):
    return 'pong'

@hooks.hook('push')
def push(data, guid):
    g = git.cmd.Git('/root/porte42/')
    print "pulling..."
    g.pull()
    print "done."
    return 'pull'

signal.signal(signal.SIGINT, signal_handler)
app.run()
