# Porte42 - Hall Voice
Bonjour la porte

# Requirments
## Studs
- Buy Hall Voice Change on [intra shop](https://shop.intra.42.fr/)
- Make a [Pull Request](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) to add your files
  - Add a .json file with your configuration (Also see `custom/_Example.json`)
  - No sound during more than 10 seconds
  - No more than 20 sounds
  - No sound over 1 Mo
  - No troll, insults, too loud sound, etc

PR might be refused if one of those requirements are missing

You can find an example PR [here](https://github.com/42Paris/hall-voice/pull/3/files)

## Staff
- Buy one RPI and a pretty good audio speaker
- In Raspbian, clone this repository
- Goto the repository and type
  - `pip3 install -r requirements.txt`
- Install a Redis server
  - `sudo apt-get install redis`
- How to run?
  - You can use systemctl
    - `sudo cp hallvoice.service /etc/systemd/system`
    - `sudo systemctl enable --now hallvoice.service`
  - You can use Docker (WIP)
    - `docker-compose build --no-cache`
    - `docker-compose up -d`
- Copy and fill-up the config file in
  - `cp config/config.ini.example config/config.ini`
- Kafka:
  - The RPI must be in bocal's network so it can access Redpanda
  - You messages must be JSONised like so
    - `{"building":"<where>","firstname":"<name>","kind":"<in/out>","login":"<login>"}`
- You can pre-fill the redis cache with
  - `goinfre-firstname-redis.py`
    - to get all firstname from list of logins in `login.list`
  - `goinfre-tts-redis.py`
    - to cache all gTTS from a list of firstname in `firstname.list`
      - This can take a very long time, generate one tts per second to avoid Google rate-limit
- All data stored in redis have a TTL of 6 months

# QnA
## Studs
- Q: Will the hallvoice use Usualname if I have one?
  - A: Yes! Hallvoice use 42API to get your Usualname from your login, if there is no Usualname find, legal firstname will be used and cached
- Q: I juste set a Usualname but the old legal firstname is still in use, how to "force" the hallvoice to use the my Usualname?
  - A: Firstname is cached in Redis, you need to ask the bocal in [Slack](https://42born2code.slack.com/archives/C7P0Z4F3L) #42paris_staff_it or [Discord](https://discord.com/channels/774300457157918772/839426887171440671) #staff_it to purge it.
- Q: I bought hallvoice, how to use it?
  - A: As written in `Requirements`: You can find an example [PR](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) [here](https://github.com/42Paris/hall-voice/pull/3/files), also see `custom/_Example.json`
- Q: I want to change a song, do I have to buy hallvoice again?
  - A: No
- Q: Code is garbage, can I improve it?
  - I guess... Yes you can? You can try to do a [PR](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork)

## Staff
- Q: I am the bocal, how to purge cache from a login?
  - A: From bocal's network, make GET call at `http://<rpi-IP>/?purge=<login>`
- Q: Something's f*cky, need to debug!
  - A: Logs can be found in folder `logs/<date>-hallvoice.log`
- Q: How to update?
  - A: Hmmm, Are you pisciner? A simple `git pull` should do the trick :)

# Fun fact
- When redis cache is fully pre-filled:
  - it consume ~300M of disk space
  - 39888 TTS cached (2493 firstname * 16 welcome and goodbye message)
  - ~5300 login is used to cache firstnames
- Volume is at maximum in `alsamixer`

###### Made with love by 42Paris team SI
