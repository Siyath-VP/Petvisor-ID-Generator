import time
import threading

# Bit allocations
TIMESTAMP_BITS = 41
THREAD_BITS = 6
SEQUENCE_BITS = 10
NODE_BITS = 7

MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

SEQUENCE_SHIFT = 0
THREAD_SHIFT = SEQUENCE_BITS
NODE_SHIFT = THREAD_SHIFT + THREAD_BITS
TIMESTAMP_SHIFT = NODE_SHIFT + NODE_BITS

# Custom epoch
EPOCH = 1710000000000

# Configuration
node_id = 1

# Thread-local sequence storage
thread_data = threading.local()

def current_millis():
    return int(time.time() * 1000)

def get_thread_id():
    return threading.get_ident() % (1 << THREAD_BITS)

def generate_snowflake_id():
    if not hasattr(thread_data, 'last_timestamp'):
        thread_data.last_timestamp = -1
        thread_data.sequence = 0

    current_ts = current_millis()

    if current_ts < thread_data.last_timestamp:
        current_ts = thread_data.last_timestamp  # Prevent clock rollback issues

    if current_ts == thread_data.last_timestamp:
        thread_data.sequence = (thread_data.sequence + 1) & MAX_SEQUENCE
        if thread_data.sequence == 0:
            # Wait until next millisecond
            while current_ts <= thread_data.last_timestamp:
                current_ts = current_millis()
    else:
        thread_data.sequence = 0

    thread_data.last_timestamp = current_ts

    thread_id = get_thread_id()

    id_value = ((current_ts - EPOCH) << TIMESTAMP_SHIFT) | \
               (node_id << NODE_SHIFT) | \
               (thread_id << THREAD_SHIFT) | \
               (thread_data.sequence << SEQUENCE_SHIFT)

    return id_value

# Test
if __name__ == "__main__":
    print(generate_snowflake_id())
