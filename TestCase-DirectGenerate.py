import unittest
import threading
import time

from DirectGenerate import (
    generate_snowflake_id,
    THREAD_SHIFT, NODE_SHIFT, TIMESTAMP_SHIFT,
    MAX_SEQUENCE, node_id, EPOCH
)

class TestThreadSnowflakeID(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.node_id = node_id

    def test_uniqueness(self):
        """Ensure IDs are unique when generated sequentially"""
        ids = set()
        for _ in range(1000):
            _id = generate_snowflake_id()
            self.assertNotIn(_id, ids, "Duplicate ID detected!")
            ids.add(_id)

    def test_monotonicity_within_thread(self):
        """Ensure IDs are monotonic (strictly increasing) in the same thread"""
        last_id = generate_snowflake_id()
        for _ in range(1000):
            new_id = generate_snowflake_id()
            self.assertGreater(new_id, last_id, "ID not strictly increasing!")
            last_id = new_id

    def test_thread_safety(self):
        """Ensure IDs are unique across multiple threads"""
        generated_ids = set()
        lock = threading.Lock()
        threads = []

        def generate_ids():
            local_ids = [generate_snowflake_id() for _ in range(300)]
            with lock:
                for _id in local_ids:
                    self.assertFalse(_id in generated_ids, "Duplicate ID across threads!")
                    generated_ids.add(_id)

        for _ in range(10):  # 10 threads × 300 = 3000 IDs
            t = threading.Thread(target=generate_ids)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(generated_ids), 3000, "Not all IDs were unique!")

    def test_id_structure(self):
        """Verify that bit fields are within their valid ranges"""
        _id = generate_snowflake_id()

        sequence = _id & ((1 << THREAD_SHIFT) - 1)
        thread_id = (_id >> THREAD_SHIFT) & ((1 << (NODE_SHIFT - THREAD_SHIFT)) - 1)
        node = (_id >> NODE_SHIFT) & ((1 << (TIMESTAMP_SHIFT - NODE_SHIFT)) - 1)
        timestamp = (_id >> TIMESTAMP_SHIFT) + EPOCH

        # Check value bounds
        self.assertLessEqual(sequence, MAX_SEQUENCE, "Sequence value out of range!")
        self.assertEqual(node, self.node_id, "Node ID mismatch!")
        self.assertGreaterEqual(timestamp, EPOCH, "Timestamp is below EPOCH!")
        self.assertLessEqual(timestamp, int(time.time() * 1000), "Timestamp is in the future!")

    def test_latency(self):
        """Measure the latency of generating 1000 Snowflake IDs"""
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            generate_snowflake_id()
        end = time.perf_counter()

        total_ms = (end - start) * 1000
        avg_us = (total_ms / iterations) * 1000

        print(f" Latency Test:")
        print(f" Total Time: {total_ms:.3f} ms for {iterations} IDs")
        print(f" Average Latency per ID: {avg_us:.3f} µs")

if __name__ == "__main__":
    unittest.main()