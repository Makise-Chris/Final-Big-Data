from kafka import KafkaConsumer

topic_artist = 'tracks'

consumer = KafkaConsumer(topic_artist, bootstrap_servers=["192.168.209.195:9092"], auto_offset_reset='earliest')

for msg in consumer:
    print("-------------------")
    print(msg)