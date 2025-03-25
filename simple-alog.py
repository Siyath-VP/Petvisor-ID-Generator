import time

NODE_BITS = 10
SEQ_BITS = 12
MAX_NODE_ID = (1 << NODE_BITS) - 1   # 1023
MAX_SEQUENCE = (1 << SEQ_BITS) - 1   # 4095
NODE_SHIFT = SEQ_BITS                # 12
TIMESTAMP_SHIFT = NODE_BITS + SEQ_BITS  # 22

# State
last_timestamp = -1
sequence = 0


node_id = 1
epoch = 1710000000000

def current_millis():
    return int(time.time() * 1000)

def generate_snowflake_id():
    global last_timestamp, sequence

    current_ts = current_millis()

    if current_ts < last_timestamp:
        wait_ms = last_timestamp - current_ts
        time.sleep(wait_ms / 1000.0)
        current_ts = current_millis()
        if current_ts < last_timestamp:
            raise RuntimeError("Clock moved backwards. Refusing to generate ID.")

    if current_ts == last_timestamp:
        sequence = (sequence + 1) & MAX_SEQUENCE
        if sequence == 0:
            while current_ts <= last_timestamp:
                current_ts = current_millis()
    else:
        sequence = 0

    last_timestamp = current_ts

    return ((current_ts - epoch) << TIMESTAMP_SHIFT) | (node_id << NODE_SHIFT) | sequence))




new_id = generate_snowflake_id()
print(new_id)


