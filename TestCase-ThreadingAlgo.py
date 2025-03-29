import unittest
import threading
from ThreadingAlgo import generate_snowflake_id, NODE_SHIFT, TIMESTAMP_SHIFT, MAX_SEQUENCE, MAX_NODE_ID, starting_time
import time

class TestSnowflakeIDGenerator(unittest.TestCase):

    def test_id_uniqueness(self):
        """Ensure multiple calls generate unique IDs"""
        ids = set()
        for _ in range(1000):
            new_id = generate_snowflake_id()
            self.assertNotIn(new_id, ids)
            ids.add(new_id)

    def test_id_monotonicity(self):
        """Ensure IDs are increasing (timestamp-based)"""
        prev_id = generate_snowflake_id()
        for _ in range(1000):
            curr_id = generate_snowflake_id()
            self.assertGreater(curr_id, prev_id)
            prev_id = curr_id
            print(prev_id, curr_id)

    def test_thread_safety(self):
        """Generate IDs from multiple threads and ensure uniqueness"""
        results = set()
        threads = []
        lock = threading.Lock()

        def generate_in_thread():
            local_ids = [generate_snowflake_id() for _ in range(100)]
            with lock:
                for _id in local_ids:
                    self.assertNotIn(_id, results)
                    results.add(_id)
                    #print(_id)

        for _ in range(50):
            t = threading.Thread(target=generate_in_thread)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(results), 5000)

    def test_id_structure(self):
        """Check whether the node ID and sequence bits fall within range"""
        _id = generate_snowflake_id()

        # Extract components
        sequence = _id & ((1 << NODE_SHIFT) - 1)
        node_id = (_id >> NODE_SHIFT) & ((1 << (TIMESTAMP_SHIFT - NODE_SHIFT)) - 1)
        timestamp = (_id >> TIMESTAMP_SHIFT) + starting_time

        self.assertLessEqual(sequence, MAX_SEQUENCE)
        self.assertLessEqual(node_id, MAX_NODE_ID)
        self.assertGreaterEqual(timestamp, starting_time)
        self.assertLessEqual(timestamp, int(time.time() * 1000))

    def test_latency(self):
        """Measure latency of generating 1000 IDs"""
        iterations = 1000
        start_time = time.perf_counter()
        for _ in range(iterations):
            generate_snowflake_id()
        end_time = time.perf_counter()

        total_ms = (end_time - start_time) * 1000
        avg_us = (total_ms / iterations) * 1000

        print(f" Latency Test Results:")
        print(f" Total Time: {total_ms:.3f} ms for {iterations} IDs")
        print(f" Average Latency per ID: {avg_us:.3f} µs")

if __name__ == '__main__':
    unittest.main()