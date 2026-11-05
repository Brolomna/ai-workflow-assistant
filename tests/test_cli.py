"""End-to-end CLI tests that run without credentials or network access."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_workflow.cli import main


class OfflineCliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.input_path = Path(self.temp_dir.name) / "notes.txt"
        self.input_path.write_text(
            "Maya will send revised landing page copy by Friday. "
            "The team agreed to move the demo to next Wednesday. "
            "Omar needs to check the payment integration before the demo. "
            "The signup flow is confusing and should be reviewed.",
            encoding="utf-8",
        )

    def run_cli(self, task, *extra):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.dict(os.environ, {}, clear=True):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main([task, str(self.input_path), *extra])
        self.assertEqual(exit_code, 0, stderr.getvalue())
        self.assertIn("Offline demo mode", stderr.getvalue())
        return stdout.getvalue()

    def test_summarize_command_offline(self):
        output = self.run_cli("summarize")
        self.assertIn("Demo summary", output)
        self.assertIn("Maya will send", output)

    def test_action_items_command_offline(self):
        output = self.run_cli("action-items")
        items = json.loads(output)
        self.assertTrue(any(item["owner"] == "Maya" for item in items))
        self.assertTrue(any(item["owner"] == "Omar" for item in items))

    def test_classify_command_offline(self):
        output = self.run_cli("classify")
        result = json.loads(output)
        self.assertEqual(result["category"], "meeting notes")
        self.assertEqual(result["sentiment"], "negative")

    def test_output_file(self):
        destination = Path(self.temp_dir.name) / "result.json"
        output = self.run_cli("classify", "--output", str(destination))
        self.assertIn("Saved result", output)
        self.assertEqual(json.loads(destination.read_text(encoding="utf-8"))["category"], "meeting notes")


if __name__ == "__main__":
    unittest.main()
