"""Tests for the local browser demo server."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ai_workflow.web import WorkflowHandler


class WebDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), WorkflowHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = "http://127.0.0.1:%s" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def post_json(self, payload):
        request = Request(
            self.base_url + "/api/process",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urlopen(request)

    def test_home_page_is_served(self):
        with urlopen(self.base_url + "/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"AI Workflow Assistant", response.read())

    def test_action_items_endpoint(self):
        with self.post_json({
            "task": "action-items",
            "text": "Maya will send the report by Friday.",
        }) as response:
            payload = json.loads(response.read())
        self.assertEqual(payload["mode"], "offline-demo")
        self.assertEqual(payload["result"][0]["owner"], "Maya")

    def test_invalid_workflow_is_rejected(self):
        with self.assertRaises(HTTPError) as caught:
            self.post_json({"task": "unknown", "text": "Some notes."})
        self.assertEqual(caught.exception.code, 400)
        payload = json.loads(caught.exception.read())
        self.assertIn("valid workflow", payload["error"])

    def test_empty_text_is_rejected(self):
        with self.assertRaises(HTTPError) as caught:
            self.post_json({"task": "summarize", "text": "   "})
        self.assertEqual(caught.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
