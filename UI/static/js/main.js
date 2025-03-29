document.addEventListener("DOMContentLoaded", function () {
    const methodRadios = document.getElementsByName("method");
    const directConfigDiv = document.getElementById("direct-config");
    const threadBitsInput = document.getElementById("thread_bits");
    const maxThreadsInfo = document.getElementById("max_threads_info");

    // Toggle display of DirectGenerate config based on method selection
    methodRadios.forEach(radio => {
        radio.addEventListener("change", function () {
            if (this.value === "DirectGenerate") {
                directConfigDiv.style.display = "block";
                updateMaxThreadsInfo();
            } else {
                directConfigDiv.style.display = "none";
            }
        });
    });

    // Update max threads info when thread bits input changes
    threadBitsInput.addEventListener("input", updateMaxThreadsInfo);

    function updateMaxThreadsInfo() {
        let threadBits = parseInt(threadBitsInput.value) || 6;
        let maxThreads = 1 << threadBits;
        maxThreadsInfo.textContent = `Maximum allowed threads: ${maxThreads}`;
    }

    // Generate IDs button event
    document.getElementById("generate-btn").addEventListener("click", function () {
        // Show loading state
        document.getElementById("terminal-output").textContent = "Generating IDs...";
        document.getElementById("total-ids").textContent = "-";
        document.getElementById("unique-ids").textContent = "-";
        document.getElementById("duplicate-ids").textContent = "-";
        document.getElementById("duplicate-percentage-container").style.display = "none";

        let selectedMethod = document.querySelector('input[name="method"]:checked').value;
        let numThreads = parseInt(document.getElementById("num_threads").value);
        let requestsPerThread = parseInt(document.getElementById("requests_per_thread").value);

        let payload = {
            method: selectedMethod,
            num_threads: numThreads,
            requests_per_thread: requestsPerThread
        };

        if (selectedMethod === "DirectGenerate") {
            payload.thread_bits = parseInt(document.getElementById("thread_bits").value);
            payload.node_bits = parseInt(document.getElementById("node_bits").value);
            payload.sequence_bits = parseInt(document.getElementById("sequence_bits").value);
        }

        fetch("/api/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById("terminal-output").textContent = data.terminal_output;
                document.getElementById("total-ids").textContent = data.total;
                document.getElementById("unique-ids").textContent = data.unique;
                document.getElementById("duplicate-ids").textContent = data.duplicates;

                // Calculate and show duplicate percentage
                const total = data.total;
                const duplicates = data.duplicates;
                const percentageContainer = document.getElementById("duplicate-percentage-container");
                const percentageSpan = document.getElementById("duplicate-percentage");

                if (total && total > 0) {
                    const percent = ((duplicates / total) * 100).toFixed(2);
                    percentageSpan.textContent = `${percent}%`;
                    percentageContainer.style.display = "flex";
                } else {
                    percentageContainer.style.display = "none";
                }
            })
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("terminal-output").textContent = "Error: " + error;
            });
    });

    // Run tests button event
    document.getElementById("run-tests-btn").addEventListener("click", function () {
        document.getElementById("test-output").textContent = "Running tests...";

        let selectedMethod = document.querySelector('input[name="method"]:checked').value;
        let payload = { method: selectedMethod };

        fetch("/api/run_tests", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById("test-output").textContent = data.test_output;
            })
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("test-output").textContent = "Error: " + error;
            });
    });

    // Initialize UI
    updateMaxThreadsInfo();
});
