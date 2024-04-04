from confluent_kafka import Consumer, KafkaException, KafkaError, OFFSET_END


class Kafka(object):
    def __init__(self, conf):
        # Consumer configuration
        kafkaConf = {
            'bootstrap.servers': conf.getKafkaServer(),
            'group.id': conf.getGroupID(),
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'SCRAM-SHA-512',
            'sasl.username': conf.getUsername(),
            'sasl.password': conf.getPassword(),
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True
        }

        # Create Kafka consumer instance
        consumer = Consumer(kafkaConf)

        # Go to last message
        def my_assign(consumer, partitions):
            for p in partitions:
                p.offset = OFFSET_END
            print('assign', partitions)
            consumer.assign(partitions)

        # Subscribe to the topic
        consumer.subscribe(conf.getTopic(), on_assign=my_assign)
        self.consumer = consumer

    def getConsumer(self):
        return self.consumer
