import time
import threading

# Bit allocations for 64-bit architecture using the Thread-Aware approach:
# Format: [Timestamp (41 bits)] [Node ID (N bits)] [Thread ID (T bits)] [Sequence (S bits)]
EPOCH = 1710000000000          # Custom epoch (in ms)
node_id = 1                    # Configuration: Node ID

# Default bit allocations:
THREAD_BITS = 6
NODE_BITS = 7
SEQUENCE_BITS = 9             # Reduced to 9 bits for 64-bit fit

# Derived values based on defaults:
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1  # 511
THREAD_SHIFT = SEQUENCE_BITS                 # 9
NODE_SHIFT = THREAD_SHIFT + THREAD_BITS      # 9 + 6 = 15
TIMESTAMP_SHIFT = NODE_SHIFT + NODE_BITS     # 15 + 7 = 22

# Thread-local state (lock-free)
thread_data = threading.local()

def update_config(new_thread_bits, new_node_bits, new_sequence_bits):
    """
    Update the bit allocation configuration for DirectGenerate.
    This function recalculates the derived values based on the new bit allocations.
    """
    global THREAD_BITS, NODE_BITS, SEQUENCE_BITS, MAX_SEQUENCE, THREAD_SHIFT, NODE_SHIFT, TIMESTAMP_SHIFT
    THREAD_BITS = new_thread_bits
    NODE_BITS = new_node_bits
    SEQUENCE_BITS = new_sequence_bits
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1
    THREAD_SHIFT = SEQUENCE_BITS
    NODE_SHIFT = THREAD_SHIFT + THREAD_BITS
    TIMESTAMP_SHIFT = NODE_SHIFT + NODE_BITS

def current_millis():
    return int(time.time() * 1000)

def get_thread_id():
    return threading.get_ident() % (1 << THREAD_BITS)

def generate_snowflake_id():
    """
    Optimized thread-aware Snowflake ID generator:
      - Lock-free: uses thread-local state
      - Structure: [41-bit timestamp][N-bit node ID][T-bit thread ID][S-bit sequence]
    """
    if not hasattr(thread_data, 'last_timestamp'):
        thread_data.last_timestamp = -1
        thread_data.sequence = 0

    current_ts = current_millis()

    if current_ts < thread_data.last_timestamp:
        current_ts = thread_data.last_timestamp

    if current_ts == thread_data.last_timestamp:
        thread_data.sequence = (thread_data.sequence + 1) & MAX_SEQUENCE
        if thread_data.sequence == 0:
            while current_ts <= thread_data.last_timestamp:
                time.sleep(0.000001)  # Yield CPU briefly
                current_ts = current_millis()
    else:
        thread_data.sequence = 0

    thread_data.last_timestamp = current_ts
    thread_id = get_thread_id()

    return ((current_ts - EPOCH) << TIMESTAMP_SHIFT) | \
           (node_id << NODE_SHIFT) | \
           (thread_id << THREAD_SHIFT) | \
           thread_data.sequence
