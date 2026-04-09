import time
import requests


def run_probe(rounds: int = 20):
    url = "http://127.0.0.1:8000/api/v1/chat/operate"
    payload = {"sessionId": "perf-s1", "employeeId": "perf-u1", "message": "帮我请明天年假"}
    costs = []
    for i in range(rounds):
        payload["idempotencyKey"] = f"perf-{i}"
        start = time.perf_counter()
        resp = requests.post(url, json=payload, timeout=15)
        costs.append(time.perf_counter() - start)
        if resp.status_code != 200:
            raise RuntimeError(f"request failed: {resp.status_code} {resp.text}")
    costs.sort()
    p95 = costs[int(len(costs) * 0.95) - 1]
    return {"rounds": rounds, "p95_ms": round(p95 * 1000, 2), "avg_ms": round(sum(costs) / len(costs) * 1000, 2)}


if __name__ == "__main__":
    print(run_probe())
