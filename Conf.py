import configparser


class Conf(object):
    def __init__(self, path):
        try:
            with open(path, "r"):
                config = configparser.ConfigParser()
                config.read(path)

                # Accessing values from the configuration file
                self.kafka_servers = config.get("kafka_conf", "kafka_servers")
                self.topic = []
                self.topic.append(config.get("kafka_conf", "topic"))
                self.group_id = config.get("kafka_conf", "group_id")
                self.username = config.get("kafka_conf", "username")
                self.password = config.get("kafka_conf", "password")
                self.building = config.get("building", "name")
                self.apiUID = config.get("42api", "uid")
                self.apiSEC = config.get("42api", "secret")
                self.welcome = []
                self.goodbye = []
                for welcomeMsg in config.items("welcome"):
                    self.welcome.append(welcomeMsg)
                for goodbyeMsg in config.items("goodbye"):
                    self.goodbye.append(goodbyeMsg)
        except FileNotFoundError as e:
            print(f"Cannot open {path}:\n{e}")

    def getKafkaServer(self):
        return self.kafka_servers

    def getTopic(self):
        return self.topic

    def getGroupID(self):
        return self.group_id

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getBuilding(self):
        return self.building

    def getAPIkeys(self):
        return [self.apiUID, self.apiSEC]

    def getWelcome(self):
        return self.welcome

    def getGoodbye(self):
        return self.goodbye
