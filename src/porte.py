import datetime
import sys
import os
from Conf import Conf
from API42 import API42
from Kafka import Kafka

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Where conf file? Use me like this!\n\tpython3 porte.py config.yaml")
        exit(1)
    elif "--help" in sys.argv:
        print("Usage: python3 src/porte.py config.yaml")
        print("\tYou can also add --log-in-file in the end to output log in file")
        exit(0)
    elif sys.argv[1] is not None and os.path.exists(sys.argv[1]):
        date = datetime.datetime.now()
        date_str = date.strftime("%Y%m%d-%H%M%S")
        if '--log-in-file' in sys.argv:
            with open(f"logs/{date_str}_hallvoice.log", "w", buffering=1) as f:
                sys.stdout = f
                sys.stderr = f
        conf = Conf(sys.argv[1])
        api = API42(conf)
        consumer = Kafka(conf, api)
        consumer.consume_messages()
    else:
        print("Config path not exists, check your args...")
        print("Path for config file should be the first arg")
        print("Usage: python3 porte.py config.yaml")
        print("\tYou can also add --log-in-file in the end to output log in file")
        exit(1)
