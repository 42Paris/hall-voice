import sys
from Conf import Conf
from API42 import API42
from Kafka import Kafka


if __name__ == "__main__":
    if sys.argv[1] is not None:
        try:
            conf = Conf(sys.argv[1])
            api = API42(conf)
            consumer = Kafka(conf, api)
            consumer.consume_messages()
        except FileNotFoundError as err:
            print(f"Error reading/opening configuration file: {err}")
    else:
        print("Where conf file? Use me like this!\npython3 porte.py config.yaml")
