import redis
from redis.exceptions import ResponseError

# Set up Redis connection
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Print number of messages in the stream
print(f'{r.xlen('decoded-can')} messages in stream')

# Create consumer group for this if it doesn't exist
try:
    r.xgroup_create(
            'decoded-can', 
            'streamer-group', 
            id='0'
    )
except ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

# Get all the messages that our consumer received but didn't ack (will probably include unsent messages that we requested before crashing) and process them
while (unacked_received := r.xreadgroup(
    groupname='streamer-group',
    consumername='streamer',
    streams={'decoded-can':'0'},
    count=30
)) and unacked_received[0][1]:
    print(f'unacked_received is NOT EMPTY!')
    for stream, message_list in unacked_received:
        for message_id, data in message_list:
            r.xack('decoded-can', 'streamer-group', message_id)
            print(f'acked {message_id}, {data}')

# then work through unprocessed messages
while True:
    unprocessed_messages = r.xreadgroup(
        groupname='streamer-group',
        consumername='streamer',
        streams={'decoded-can':'>'},
        count=30
    )

    for stream, message_list in unprocessed_messages:
        for message_id, data in message_list:
            r.xack('decoded-can', 'streamer-group', message_id)
            print(f'acked {message_id}')

