"""Local browser interface for the offline workflow demo."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .tasks import run_task

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
MAX_BODY_BYTES = 1_000_000
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


class WorkflowHandler(BaseHTTPRequestHandler):
    server_version = "AIWorkflowDemo/1.0"

    def do_GET(self):
        path = urlparse(self.path).path
        pages = {
            "/": "index.html",
            "/styles.css": "styles.css",
            "/app.js": "app.js",
        }
        filename = pages.get(path)
        if filename is None:
            self.send_error(404, "Not found")
            return

        file_path = WEB_DIR / filename
        try:
            content = file_path.read_bytes()
        except OSError:
            self.send_error(500, "Web interface files are missing")
            return

        self.send_response(200)
        self.send_header("Content-Type", MIME_TYPES[file_path.suffix])
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if urlparse(self.path).path != "/api/process":
            self.send_error(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid request size."})
            return

        if length < 1 or length > MAX_BODY_BYTES:
            self._send_json(413 if length > MAX_BODY_BYTES else 400, {
                "error": "Please send text smaller than 1 MB."
            })
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            task = payload.get("task")
            source = payload.get("text", "")
            if not isinstance(source, str):
                raise ValueError("Text must be a string.")
            if not source.strip():
                raise ValueError("Paste some text before running a workflow.")
            if task not in ("summarize", "action-items", "classify"):
                raise ValueError("Choose a valid workflow.")

            result = run_task(None, task, source, demo=True)
            self._send_json(200, {"task": task, "result": result, "mode": "offline-demo"})
        except (UnicodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Request must contain valid UTF-8 JSON."})
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception:
            self._send_json(500, {"error": "The workflow could not be completed."})

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print("[web] " + format_string % args)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ai-workflow-web",
        description="Run the local, no-cost AI Workflow Assistant browser demo.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to use (default: 8000)")
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), WorkflowHandler)
    print("AI Workflow Assistant is running at http://%s:%s" % (args.host, args.port))
    print("Offline demo only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
