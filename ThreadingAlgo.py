import time
import threading

# Bit allocations
NODE_BITS = 10
SEQUENCE_BITS = 12
MAX_NODE_ID = (1 << NODE_BITS) - 1   # 1023
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1   # 4095
NODE_SHIFT = SEQUENCE_BITS                # 12
TIMESTAMP_SHIFT = NODE_BITS + SEQUENCE_BITS  # 22

# Global shared state
last_timestamp = -1
sequence = 0

# Thread lock for thread-safe access
lock = threading.Lock()

# Configuration
node_id = 1
starting_time = 1710000000000  # Custom epoch

# Mock thread ID handling like original threading algo
def get_thread_id():
    return threading.get_ident() % (1 << 6)  # 6 bits = max 64 thread IDs

def current_millis():
    return int(time.time() * 1000)

def generate_snowflake_id():
    global last_timestamp, sequence

    with lock:
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

        snowflake_id = ((current_ts - starting_time) << TIMESTAMP_SHIFT) | (node_id << NODE_SHIFT) | sequence
        return snowflake_id

# New helper function for bulk ID generation
def generate_ids(count):
    """
    Generate a list of `count` snowflake IDs.
    """
    return [generate_snowflake_id() for _ in range(count)]

# Example usage
if __name__ == "__main__":
    new_id = generate_snowflake_id()
    print(new_id)
