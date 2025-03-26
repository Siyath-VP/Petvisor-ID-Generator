import time
import threading

# Bit allocations
NODE_BITS = 10
SEQUENCE = 12
MAX_NODE_ID = (1 << NODE_BITS) - 1   # 1023
MAX_SEQUENCE = (1 << SEQUENCE) - 1   # 4095
NODE_SHIFT = SEQUENCE                # 12
TIMESTAMP_SHIFT = NODE_BITS + SEQUENCE  # 22

# Shared state
last_timestamp = -1
sequence = 0

# Thread lock for thread-safe access
lock = threading.Lock()

# Configuration
node_id = 1
starting_time = 1710000000000  # Custom epoch (e.g., March 2024)

def current_millis():
    return int(time.time() * 1000)

def generate_snowflake_id():
    global last_timestamp, sequence

    with lock:
        current_ts = current_millis()

        # Handle clock rollback
        if current_ts < last_timestamp:
            wait_ms = last_timestamp - current_ts
            time.sleep(wait_ms / 1000.0)
            current_ts = current_millis()
            if current_ts < last_timestamp:
                raise RuntimeError("Clock moved backwards. Refusing to generate ID.")

        if current_ts == last_timestamp:
            sequence = (sequence + 1) & MAX_SEQUENCE
            if sequence == 0:
                # Sequence exhausted; wait for next millisecond
                while current_ts <= last_timestamp:
                    current_ts = current_millis()
        else:
            sequence = 0

        last_timestamp = current_ts

        snowflake_id = ((current_ts - starting_time) << TIMESTAMP_SHIFT) | (node_id << NODE_SHIFT) | sequence
        return snowflake_id

# Example usage
if __name__ == "__main__":
    new_id = generate_snowflake_id()
    print(new_id)