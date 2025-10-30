#!/usr/bin/env python3
"""Mock BlueSky HTTP queueserver for local UI testing.

This implements a lightweight in-memory subset of the bluesky-httpserver API
used by the Queue Monitor web UI. It's intentionally simple and dependency-free
(uses the standard library) and intended for local testing and development only.

Endpoints implemented (minimal, enough for UI testing):
  GET  /status
  GET  /queue/status
  POST /queue/add
  POST /queue/clear
  POST /queue/start
  POST /queue/stop
  POST /environment/destroy
  POST /plans       (save plan text)
  GET  /plans       (list saved plans)

Run:
  python3 mock_qserver.py --port 9000

Then configure the web UI to use http://127.0.0.1:9000 as the queue server URL.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import argparse
import threading
import time
import uuid
from urllib.parse import urlparse
from urllib.parse import urlparse
from event_model import compose_run, pack_event_page, uuid as new_uid
from event_model import Resource, Datum
import queue


class MockQueueServer:
    def __init__(self):
        self.lock = threading.Lock()
        self.queue = []  # list of plan dicts
        self.running = None  # dict or None
        self.history = []  # list of finished plans
        self.plans = {}  # saved named plans
        self.environment_destroy = False
        # documents per run uid: list of document dicts
        self.documents = {}
        # subscribers for server-sent events: list of Queue objects
        self._subscribers = []
        # per-run composition context: run_bundle, descriptor_doc, compose_event_page
        self._run_contexts = {}

    def status(self):
        return {"status": "online", "version": "mock-0.1"}

    def queue_status(self):
        with self.lock:
            return {
                "running": self.running,
                "queue": list(self.queue),
                "history": list(self.history),
            }

    def add_to_queue(self, plan):
        with self.lock:
            uid = plan.get("uid") or str(uuid.uuid4())
            item = {"uid": uid, "name": plan.get("name", "plan"), "plan": plan.get("plan", ""), "state": "queued"}
            self.queue.append(item)
            return item

    def subscribe(self):
        # returns a queue.Queue that will receive document dicts
        q = queue.Queue()
        with self.lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass

    def _publish_doc(self, doc):
        # push a document to all subscribers (non-blocking)
        with self.lock:
            subs = list(self._subscribers)
        for q in subs:
            try:
                q.put_nowait(doc)
            except Exception:
                # ignore subscriber failures
                pass

    def clear_queue(self):
        with self.lock:
            self.queue.clear()

    def start_queue(self):
        with self.lock:
            if self.running is not None:
                return False
            if not self.queue:
                return False
            item = self.queue.pop(0)
            item = dict(item)
            item.update({"state": "running", "progress": 0})
            self.running = item
            # start background thread to simulate execution
            # initialize document storage for this run
            run_uid = str(uuid.uuid4())
            self.documents[item["uid"]] = []
            # compose canonical start document using event_model.compose_run
            # compose_run expects `metadata` not `md`
            run_bundle = compose_run(metadata={"plan_name": item.get("name")})
            start_doc = run_bundle.start_doc
            # ensure the run_start uid matches the queued item's uid for mapping
            start_doc["uid"] = item["uid"]
            start_doc["time"] = time.time()
            self.documents[item["uid"]].append(start_doc)
            self._publish_doc(start_doc)

            # create a simple descriptor for a single stream using the run_bundle composer
            # run_bundle.compose_descriptor(name, data_keys, **kwargs) returns a descriptor bundle
            # compose_descriptor signature: name, data_keys, metadata=None, validate=True
            descriptor_bundle = run_bundle.compose_descriptor(
                name="primary",
                data_keys={"progress": {"dtype": "number", "shape": [], "source": "simulated"}},
                metadata={"stream_name": "primary"},
            )
            descriptor_doc = descriptor_bundle.descriptor_doc
            compose_event_page = descriptor_bundle.compose_event_page
            self.documents[item["uid"]].append(descriptor_doc)
            self._publish_doc(descriptor_doc)
            # Save the composition context so the simulation thread can access it
            self._run_contexts[item["uid"]] = {
                "run_bundle": run_bundle,
                "descriptor_doc": descriptor_doc,
                "compose_event_page": compose_event_page,
            }

            # Add a simulated external resource and datum for one event (example)
            resource_uid = new_uid()
            # create a minimal Resource and Datum (example)
            resource = Resource(
                uid=resource_uid,
                spec="SIM_RESOURCE",
                root="/tmp",
                path="/tmp/data.bin",
                resource_path="/tmp/data.bin",
                resource_kwargs={},
            )
            # event_model Resource exposes the document on `.resource`
            resource_doc = resource.resource
            datum = Datum(uid=new_uid(), resource=resource_uid, datum_id="1", datum_kwargs={})
            # Datum may expose `.datum` or be a dict-like object; normalize
            try:
                datum_doc = datum.datum
            except Exception:
                datum_doc = datum
            # store and publish resource/datum docs
            self.documents[item["uid"]].append(resource_doc)
            self._publish_doc(resource_doc)
            self.documents[item["uid"]].append(datum_doc)
            self._publish_doc(datum_doc)

            t = threading.Thread(target=self._simulate_run, args=(item,), daemon=True)
            t.start()
            return True

    def stop_queue(self):
        with self.lock:
            if self.running is None:
                return False
            # mark as stopped and move to history with failed status
            r = dict(self.running)
            r.update({"state": "stopped", "result": "stopped"})
            self.history.insert(0, r)
            self.running = None
            return True

    def _simulate_run(self, item):
        # Simple simulation: increment progress to 100 over ~5 seconds
        for i in range(20):
            time.sleep(0.25)
            with self.lock:
                if self.running is None or self.running.get("uid") != item.get("uid"):
                    return
                self.running["progress"] = min(100, int((i + 1) * 5))
                # emit an event_page for this progress step using pack_event_page
                data = {"progress": [self.running["progress"]]}
                timestamps = {"progress": [time.time()]}
                # retrieve compose_event_page from run context
                ctx = self._run_contexts.get(item.get("uid"), {})
                compose_event_page = ctx.get("compose_event_page")
                descriptor_doc = ctx.get("descriptor_doc")
                if compose_event_page is not None:
                    ev_page = compose_event_page(data=data, timestamps=timestamps)
                else:
                    # fallback: pack a minimal event_page-like dict
                    ev_page = {"name": "event_page", "data": data, "timestamps": timestamps}
                # ensure minimal fields
                ev_page["uid"] = ev_page.get("uid", str(uuid.uuid4()))
                if descriptor_doc:
                    ev_page["descriptor"] = descriptor_doc["uid"]
                ev_page["time"] = time.time()
                self.documents.setdefault(item["uid"], []).append(ev_page)
                self._publish_doc(ev_page)
        # mark finished and (in production) automatically start the next plan
        with self.lock:
            finished = dict(self.running)
            finished.update({"state": "finished", "result": "success", "progress": 100, "time_stop": time.time()})
            # add time_start (from start_doc) if available
            try:
                finished["time_start"] = self.documents[item["uid"]][0].get("time", None)
            except Exception:
                finished["time_start"] = None
            finished["time_stop"] = time.time()
            self.history.insert(0, finished)
            # clear the running slot
            self.running = None
            # emit a 'stop' (end) document for the finished run
            # compose a canonical stop document
            # compose a canonical stop document using run_bundle from context
            ctx = self._run_contexts.get(item.get("uid"), {})
            run_bundle_ctx = ctx.get("run_bundle")
            if run_bundle_ctx is not None:
                stop_doc = run_bundle_ctx.compose_stop(exit_status="success", reason="")
            else:
                stop_doc = {"uid": new_uid(), "time": time.time(), "exit_status": "success"}
            stop_doc["uid"] = finished.get("uid")
            stop_doc["time"] = time.time()
            self.documents.setdefault(finished.get("uid"), []).append(stop_doc)
            self._publish_doc(stop_doc)

            # If there are more items in the queue, start the next one automatically
            if self.queue:
                next_item = self.queue.pop(0)
                next_item = dict(next_item)
                next_item.update({"state": "running", "progress": 0})
                self.running = next_item
                # initialize document storage for this run
                self.documents[next_item["uid"]] = []
                # emit start document for the next run
                start_doc2 = {"uid": next_item["uid"], "type": "start", "name": next_item.get("name"), "time": time.time(), "plan": next_item.get("plan")}
                self.documents[next_item["uid"]].append(start_doc2)
                self._publish_doc(start_doc2)

                # spawn a new thread to simulate the next run (daemon so server can exit)
                t = threading.Thread(target=self._simulate_run, args=(next_item,), daemon=True)
                t.start()

    def toggle_environment_destroy(self):
        with self.lock:
            self.environment_destroy = not self.environment_destroy
            return self.environment_destroy

    def save_plan(self, name, code):
        with self.lock:
            self.plans[name] = code


MOCK = MockQueueServer()


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, code=200):
        body = json.dumps(data).encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/status":
            self._send_json(MOCK.status())
            return
        if path == "/queue/status":
            self._send_json(MOCK.queue_status())
            return
        # list runs (history + running uid)
        if path == "/runs":
            with MOCK.lock:
                run_uids = [h.get("uid") for h in MOCK.history]
                if MOCK.running:
                    run_uids.insert(0, MOCK.running.get("uid"))
            self._send_json({"runs": run_uids})
            return
        # return documents for a run: /runs/<uid>/documents
        if path.startswith("/runs/") and path.endswith("/documents"):
            parts = path.split("/")
            if len(parts) >= 3:
                uid = parts[2]
                with MOCK.lock:
                    docs = MOCK.documents.get(uid, [])
                self._send_json({"uid": uid, "documents": docs})
                return
        # Server-Sent Events endpoint for live documents
        if path == "/events":
            # Upgrade to SSE
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            q = MOCK.subscribe()
            try:
                while True:
                    doc = q.get()
                    msg = json.dumps(doc)
                    # send SSE 'data:' lines and a blank line
                    try:
                        self.wfile.write(f"data: {msg}\n\n".encode('utf8'))
                        self.wfile.flush()
                    except BrokenPipeError:
                        break
            finally:
                MOCK.unsubscribe(q)
            return
        if path == "/plans":
            with MOCK.lock:
                self._send_json({"plans": list(MOCK.plans.keys())})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        try:
            data = json.loads(body.decode("utf8")) if body else {}
        except Exception:
            data = {}

        if path == "/queue/add":
            item = MOCK.add_to_queue(data or {})
            self._send_json({"result": "ok", "item": item})
            return
        if path == "/queue/clear":
            MOCK.clear_queue()
            self._send_json({"result": "ok"})
            return
        if path == "/queue/start":
            ok = MOCK.start_queue()
            self._send_json({"result": "ok" if ok else "no-op"})
            return
        if path == "/queue/stop":
            ok = MOCK.stop_queue()
            self._send_json({"result": "ok" if ok else "no-op"})
            return
        if path == "/environment/destroy":
            state = MOCK.toggle_environment_destroy()
            self._send_json({"environment_destroy": state})
            return
        if path == "/plans":
            name = data.get("name") or f"plan-{str(uuid.uuid4())[:8]}"
            code = data.get("code", "")
            MOCK.save_plan(name, code)
            self._send_json({"result": "ok", "name": name})
            return

        self.send_response(404)
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="Mock BlueSky HTTP queueserver for UI testing")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), Handler)
    print(f"Mock queueserver running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    main()
