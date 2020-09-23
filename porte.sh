#!/bin/sh

cd /root/porte42/

ps aux | grep python | grep ./porte.py | awk '{print $2}' | xargs kill

./play.sh ./mp3/sipass.mp3

sleep 5

/usr/bin/python ./porte.py entree-1 welcome &
sleep 1

/usr/bin/python ./porte.py entree-2 welcome &
sleep 1

/usr/bin/python ./porte.py sortie-1 goodbye &
sleep 1

/usr/bin/python ./porte.py sortie-2 goodbye &

# already laucnhed by supervisord
#cd /root/porte42-api/
#/usr/bin/python ./app.py
