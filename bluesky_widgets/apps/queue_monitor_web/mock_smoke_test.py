#!/usr/bin/env python3
"""Smoke test for mock_qserver: queue add -> start -> SSE capture -> fetch run documents

Run this while mock_qserver.py is running on port 9000.
"""
import requests
import time
import threading


def sse_listener(url, out_list, stop_event):
    with requests.get(url, stream=True) as r:
        for line in r.iter_lines(decode_unicode=True):
            if stop_event.is_set():
                break
            if line and line.startswith("data: "):
                out_list.append(line[len("data: "):])


def main():
    base = "http://127.0.0.1:9000"
    # queue two plans
    for i in (1, 2):
        requests.post(base + "/queue/add", json={"name": f"smoke-{i}", "plan": f"print({i})"})

    # start SSE listener
    events = []
    stop_event = threading.Event()
    t = threading.Thread(target=sse_listener, args=(base + "/events", events, stop_event), daemon=True)
    t.start()

    # start the queue
    requests.post(base + "/queue/start")

    # wait until we see stop documents in history
    for _ in range(60):
        resp = requests.get(base + "/queue/status").json()
        if not resp.get("running") and not resp.get("queue"):
            break
        time.sleep(0.5)

    stop_event.set()
    time.sleep(0.2)
    print("Captured SSE messages:")
    for e in events[:50]:
        print(e)

    runs = requests.get(base + "/runs").json()
    print("Runs:", runs)
    # fetch documents for each run
    for uid in runs.get("runs", [])[:3]:
        docs = requests.get(base + f"/runs/{uid}/documents").json()
        print(f"Documents for {uid}:", len(docs.get("documents", [])))


if __name__ == '__main__':
    main()
