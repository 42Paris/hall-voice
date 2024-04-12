import datetime
import sys
from Conf import Conf
from API42 import API42
from Kafka import Kafka


if __name__ == "__main__":
    if sys.argv[1] is not None:
        try:
            with open(f"logs/{datetime.datetime.now().strftime("%Y%m%d%H%M")}-hallvoice.log", "w", buffering=1) as f:
                sys.stdout = f
                sys.stderr = f
                conf = Conf(sys.argv[1])
                api = API42(conf)
                consumer = Kafka(conf, api)
                consumer.consume_messages()
        except FileNotFoundError as err:
            print(f"Error reading/opening configuration file: {err}")
    else:
        print("Where conf file? Use me like this!\n\tpython3 porte.py config.yaml")
