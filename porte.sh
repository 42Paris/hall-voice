#!/bin/sh

echo "Kill remaining hallvoice process"
ps aux | grep python | grep porte.py | awk '{print $2}' | xargs kill
echo "Launching Hallvoice, Hello!"
python3 porte.py config/config.ini
