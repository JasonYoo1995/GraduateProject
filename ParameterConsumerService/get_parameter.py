import argparse
import json
import time
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from confluent_kafka.serialization import Deserializer, Serializer
import socket
from pymongo import MongoClient

import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP

mongo_ip = IP('../ips','mongo')
kafka_ip = IP('../ips','kafka')

LABEL_ACC_GOOD_TOPIC = 'good_acc_label'
LABEL_ACC_BAD_TOPIC = 'bad_acc_label'

def msg_process(msg):  
    # parameter 모델에 적용  

    file = open('test.pt','wb')
    file.write(msg.value())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of the Kafka topic to stream.')
    
    args = parser.parse_args()
    
    topic = args.topic
    
    consumer_conf = {
        'bootstrap.servers' : f'{kafka_ip}:9092',
        'auto.offset.reset' : 'earliest',
        'group.id' : 'streams-wordcount',
        'fetch.message.max.bytes' : '100000000'
    }
    
    consumer = Consumer(consumer_conf)
    
    running = True
    try:
        consumer.subscribe([args.topic])
        
        while running:
            
            msg = consumer.poll(1)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    sys.stderr.write('Topic unknown, creating %s topic\n' %
                                     (args.topic))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
        
    except KeyboardInterrupt:
        pass
    
    finally:
        consumer.close()

if __name__ == "__main__":
    main()