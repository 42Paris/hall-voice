import configparser
import json
import os
import sys
from confluent_kafka import Consumer, KafkaException, KafkaError
from random import *
from playsound import playsound
from gtts import gTTS

def say(txt, lang):
    tts = gTTS(text=txt, lang=lang)
    tts.save("/tmp/tts.mp3")
    playsound("/tmp/tts.mp3")
    os.remove("/tmp/tts.mp3")

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)

    # Accessing values from the configuration file
    kafka_servers = config.get("kafka_conf", "kafka_servers")
    topic = []
    topic.append(config.get("kafka_conf", "topic"))
    group_id = config.get("kafka_conf", "group_id")
    username = config.get("kafka_conf", "username")
    password = config.get("kafka_conf", "password")
    building = config.get("building", "name")
    welcome = []
    goodbye = []
    for welcomeMsg in config.items("welcome"):
        welcome.append(welcomeMsg)
    for goodbyMmsg in config.items("goodbye"):
        goodbye.append(goodbyMmsg)
    return kafka_servers, topic, group_id, username, password, building, welcome, goodbye

def create_consumer(kafka_servers, topic, group_id, username, password):
    # Consumer configuration
    conf = {
        'bootstrap.servers': kafka_servers,
        'group.id': group_id,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'SCRAM-SHA-512',
        'sasl.username': username,
        'sasl.password': password,
        'auto.offset.reset': 'latest',
        'enable.auto.commit': True
    }

    # Create Kafka consumer instance
    consumer = Consumer(conf)

    # Subscribe to the topic
    consumer.subscribe(topic)

    return consumer

def consume_messages(consumer, building, welcome, goodbye):
    try:
        while True:
            # Poll for messages
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write(
                        '%% %s [%d] reached end at offset %d\n' % (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Process the message
                processMessage(msg.value().decode('utf-8'), building, welcome, goodbye)
    except KeyboardInterrupt:
        # Handle keyboard interrupt
        pass
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def playCustomSound(kind, login, jsonFile):
    io = "welcome" if kind == "in" else "goodbye"
    with open(jsonFile, 'r') as custom_file:
        j = json.loads(custom_file.read())
        if "mp3" in j[io]:
            if os.path.isdir("mp3/" + j[io]["mp3"]) is True:
                playsound("mp3/" + j[io]["mp3"] + "/" + choice(os.listdir("mp3/" + j[io]["mp3"])))
            elif os.path.isfile("mp3/" + j[io]["mp3"]) is True:
                playsound("mp3/" + j[io]["mp3"])
        elif "txt" in j[io]:
            lang = j[io]["lang"] if "lang" in j[io] else "fr"
            say(j[io]["txt"], lang)

def genericWelcome(prenom, welcome):
    tts = welcome[randint(0, 7)][1].replace("<name>", prenom)
    print(tts)
    say(tts, "fr")

def genericGoodbye(prenom, goodbye):
    tts = goodbye[randint(0, 7)][1].replace("<name>", prenom)
    print(tts)
    say(tts, "fr")

def processMessage(msg, building, welcome, goodbye):
    print("NEW MESSAGE: " + msg)
    data = json.loads(msg)
    if building != data["building"]:
        return
    kind = data['kind']
    prenom = data['firstname']
    login = data['login']

    jsonFile = "custom/" + login + ".json"
    if os.path.isfile(jsonFile):
        print("Custom HallVoice for " + login)
        playCustomSound(kind, login, jsonFile)
        return
    else:
        genericWelcome(prenom, welcome) if kind == "in" else genericGoodbye(prenom, goodbye)

if __name__ == "__main__":
    config_file_path = 'conf.ini'

    try:
        (kafka_servers,
         topic,
         group_id,
         username,
         password,
         building,
         welcome,
         goodbye) = read_config(config_file_path)
        consumer = create_consumer(kafka_servers, topic, group_id, username, password)
        consume_messages(consumer, building, welcome, goodbye)
    except configparser.Error as e:
        print(f"Error reading configuration file: {e}")
