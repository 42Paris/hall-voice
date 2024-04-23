#!/bin/bash
amixer sset PCM 100%
python3 /hallvoice/porte.py /hallvoice/conf/config.ini
