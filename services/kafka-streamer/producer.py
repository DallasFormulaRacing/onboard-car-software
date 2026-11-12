from confluent_kafka import Producer
import socket

conf = {'bootstrap.servers': 'kafka:9094',
        'client.id': 'ev25'}

producer = Producer(conf)

