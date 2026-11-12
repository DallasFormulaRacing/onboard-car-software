import redis


# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Print number of messages in the stream
print(f'{r.xlen('decoded-can')} messages in stream')

# Get all the messages that our consumer received but didn't ack (will probably include unsent messages that we requested before crashing) and process them
unacked_received = r.xreadgroup(
    groupname='streamer-group',
    consumername='streamer',
    streams={'decoded-can':"0"},
    count=30,
    block=2000
)

while unacked_received[0][1]:
    print(f'unacked_received is NOT EMPTY!')
    for stream, message_list in unacked_received:
        for message_id, data in message_list:
            r.xack('decoded-can', 'streamer-group', message_id)
            print(f'acked {message_id}, {data}')
    unacked_received = r.xreadgroup(
        groupname='streamer-group',
        consumername='streamer',
        streams={'decoded-can':"0"},
        count=30,
        block=2000
    )


print(f'\nunacked_received:')

