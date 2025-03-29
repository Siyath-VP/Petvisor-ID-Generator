from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import time
import subprocess
import sys
import os

# Add root directory to import custom modules
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

import DirectGenerate
import ThreadingAlgo

# Flask app pointing to templates and static files inside UI/
app = Flask(
    __name__,
    static_folder=os.path.join(ROOT_DIR, 'UI', 'static'),
    template_folder=os.path.join(ROOT_DIR, 'UI')
)

@app.route('/')
def index():
    return render_template('index.html')

def generate_ids_concurrently(method, num_threads, requests_per_thread):
    all_ids = []
    lock = threading.Lock()

    def worker(generate_func):
        local_ids = [generate_func() for _ in range(requests_per_thread)]
        with lock:
            all_ids.extend(local_ids)

    generate_func = (
        DirectGenerate.generate_snowflake_id
        if method == "DirectGenerate"
        else ThreadingAlgo.generate_snowflake_id
    )

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(generate_func,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return all_ids

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    method = data.get('method')
    num_threads = data.get('num_threads')
    requests_per_thread = data.get('requests_per_thread')

    if not method or num_threads is None or requests_per_thread is None:
        return jsonify({"error": "Missing required parameters."}), 400

    if method == "DirectGenerate":
        thread_bits = data.get('thread_bits', 6)
        node_bits = data.get('node_bits', 7)
        sequence_bits = data.get('sequence_bits', 9)

        max_threads = 1 << thread_bits
        if num_threads > max_threads:
            return jsonify({
                "error": f"Number of threads exceeds maximum allowed ({max_threads}) based on thread bits allocation."
            }), 400

        DirectGenerate.update_config(thread_bits, node_bits, sequence_bits)

    ids = generate_ids_concurrently(method, num_threads, requests_per_thread)
    total = len(ids)
    unique_ids = len(set(ids))
    duplicates = total - unique_ids
    terminal_output = "\n".join(str(_id) for _id in ids)

    return jsonify({
        "ids": ids,
        "total": total,
        "unique": unique_ids,
        "duplicates": duplicates,
        "terminal_output": terminal_output
    })

@app.route('/api/run_tests', methods=['POST'])
def api_run_tests():
    data = request.get_json()
    method = data.get('method')

    if not method:
        return jsonify({"error": "Test method not specified."}), 400

    if method == "DirectGenerate":
        test_file = os.path.join(ROOT_DIR, 'TestCase-DirectGenerate.py')
    elif method == "ThreadingAlgo":
        test_file = os.path.join(ROOT_DIR, 'TestCase-ThreadingAlgo.py')
    else:
        return jsonify({"error": "Invalid method specified."}), 400

    try:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", test_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        output = result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        output = "Test execution timed out."

    return jsonify({"test_output": output})

# Serve static files manually if needed (optional)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(ROOT_DIR, 'UI', 'static'), filename)

if __name__ == '__main__':
    app.run(debug=True)
