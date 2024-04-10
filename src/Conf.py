import configparser

class Conf(object):
    def __init__(self, path: str) -> None:
        try:
            with open(path, "r"):
                config = configparser.ConfigParser()
                config.read(path)

                # Accessing values from the configuration file
                self.kafka_servers: str = config.get("kafka_conf", "kafka_servers")
                self.topic: list[str] = []
                self.topic.append(config.get("kafka_conf", "topic"))
                self.group_id: str = config.get("kafka_conf", "group_id")
                self.username: str = config.get("kafka_conf", "username")
                self.password: str = config.get("kafka_conf", "password")
                self.building: str = config.get("building", "name")
                self.apiUID: str = config.get("42api", "uid")
                self.apiSEC: str = config.get("42api", "secret")
                self.welcome: list[tuple[str, str]] = []
                self.goodbye: list[tuple[str, str]] = []
                for welcomeMsg in config.items("welcome"):
                    self.welcome.append(welcomeMsg)
                for goodbyeMsg in config.items("goodbye"):
                    self.goodbye.append(goodbyeMsg)
        except FileNotFoundError as e:
            print(f"Cannot open {path}:\n{e}")

    def getKafkaServer(self) -> str:
        return self.kafka_servers

    def getTopic(self) -> list[str]:
        return self.topic

    def getGroupID(self) -> str:
        return self.group_id

    def getUsername(self) -> str:
        return self.username

    def getPassword(self) -> str:
        return self.password

    def getBuilding(self) -> str:
        return self.building

    def getAPIkeys(self) -> list[str]:
        return [self.apiUID, self.apiSEC]

    def getWelcome(self) -> list[tuple[str, str]]:
        return self.welcome

    def getGoodbye(self) -> list[tuple[str, str]]:
        return self.goodbye
