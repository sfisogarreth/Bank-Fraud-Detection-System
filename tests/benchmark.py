import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:5000/api/v1/transactions"
TOTAL_REQUESTS = 200
CONCURRENT_THREADS = 10

def send_single_request(req_id):
    payload = {
        "account_number": f"TEST_ACC_{req_id}",
        "amount": float(random.randint(10, 5000)),
        "location": "Digital Twin Test Lab"
    }
    
    start_time = time.perf_counter()
    try:
        response = requests.post(API_URL, json=payload, timeout=5.0)
        latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        return response.status_code == 201, latency
    except Exception:
        return False, 0.0

def run_performance_test():
    print(f"--- STARTING DIGITAL TWIN PERFORMANCE TEST ---")
    print(f"Target: {TOTAL_REQUESTS} requests across {CONCURRENT_THREADS} concurrent threads...\n")

    latencies = []
    success_count = 0
    
    start_total_time = time.perf_counter()

    # Execute requests concurrently using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        futures = [executor.submit(send_single_request, i) for i in range(TOTAL_REQUESTS)]
        
        for future in as_completed(futures):
            success, latency = future.result()
            if success:
                success_count += 1
                latencies.append(latency)

    total_duration = time.perf_counter() - start_total_time
    rps = success_count / total_duration

    # Summary Metrics Calculation
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    latencies.sort()
    p95_latency = latencies[int(len(latencies) * 0.95)] if latencies else 0

    print("--- BENCHMARK RESULTS ---")
    print(f"Successful Requests: {success_count}/{TOTAL_REQUESTS}")
    print(f"Total Test Time:     {total_duration:.2f} seconds")
    print(f"Throughput:          {rps:.2f} Requests/Sec")
    print(f"Average Latency:     {avg_latency:.2f} ms")
    print(f"95th Percentile:     {p95_latency:.2f} ms")
    print("-------------------------")

if __name__ == "__main__":
    import random
    run_performance_test()