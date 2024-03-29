import configparser
import json
import os
import sys
from confluent_kafka import Consumer, KafkaException, KafkaError, OFFSET_END
from random import *
from playsound import playsound
from gtts import gTTS


def say(txt, lang):
    tts = gTTS(text=txt, lang=lang)
    tts.save("/tmp/tts.mp3")
    playsound("/tmp/tts.mp3")
    os.remove("/tmp/tts.mp3")


def read_config(file_path):
    try:
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
        for goodbyeMsg in config.items("goodbye"):
            goodbye.append(goodbyeMsg)
        return kafka_servers, topic, group_id, username, password, building, welcome, goodbye
    except Exception as err:
        print(f"Cannot open config.ini or error while reading config.ini:\n{err}")


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

    # Go to last message
    def my_assign(consumer, partitions):
        for p in partitions:
            p.offset = OFFSET_END
        print('assign', partitions)
        consumer.assign(partitions)

    # Subscribe to the topic
    consumer.subscribe(topic, on_assign=my_assign)
    return consumer


def consume_messages(consumer, building, welcome, goodbye):
    try:
        while True:
            # Poll for messages
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
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


def playCustomSound(kind, jsonFile):
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


def genericWelcome(firstname, welcomeMsg):
    tts = welcomeMsg[randint(0, 7)][1].replace("<name>", firstname)
    print(tts)
    say(tts, "fr")


def genericGoodbye(firstname, goodbyeMsg):
    tts = goodbyeMsg[randint(0, 7)][1].replace("<name>", firstname)
    print(tts)
    say(tts, "fr")


def processMessage(msg, buildingName, welcomeMsg, goodbyeMsg):
    print("NEW MESSAGE: " + msg)
    data = json.loads(msg)
    if buildingName != data["building"]:
        return
    kind = data['kind']
    firstname = data['firstname']
    login = data['login']

    jsonFile = "custom/" + login + ".json"
    if os.path.isfile(jsonFile):
        print("Custom HallVoice for " + login)
        playCustomSound(kind, jsonFile)
        return
    else:
        genericWelcome(firstname, welcomeMsg) if kind == "in" else genericGoodbye(firstname, goodbyeMsg)


if __name__ == "__main__":
    config_file_path = 'config.ini'
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
    except Exception as err:
        print(f"Error reading/opening configuration file: {err}")
