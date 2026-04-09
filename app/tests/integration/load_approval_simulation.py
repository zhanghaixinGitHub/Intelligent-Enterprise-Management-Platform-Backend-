from concurrent.futures import ThreadPoolExecutor
import requests


def call_once(i: int):
    url = f"http://localhost:8000/api/v1/workflows/wf-{i}/approve"
    payload = {"approverId": f"u{i}", "action": "approve", "comment": "ok"}
    try:
        r = requests.post(url, json=payload, timeout=3)
        return r.status_code
    except Exception:
        return 500


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=20) as pool:
        codes = list(pool.map(call_once, range(1, 101)))
    ok = len([c for c in codes if c == 200])
    print({"total": len(codes), "ok": ok, "fail": len(codes) - ok})
