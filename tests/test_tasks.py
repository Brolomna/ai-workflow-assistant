import json
import unittest
from ai_workflow.tasks import run_task

class FakeClient:
    def __init__(self, response): self.response = response
    def complete(self, system_prompt, user_prompt): return self.response

class TaskTests(unittest.TestCase):
    def test_summary(self):
        self.assertEqual(run_task(FakeClient("Summary"), "summarize", "notes"), "Summary")
    def test_action_items_json(self):
        data = [{"task": "Send report", "owner": None, "deadline": None, "priority": "medium"}]
        self.assertEqual(run_task(FakeClient(json.dumps(data)), "action-items", "notes"), data)
    def test_classification_json(self):
        data = {"category": "support", "sentiment": "neutral", "urgency": "low", "rationale": "Question"}
        self.assertEqual(run_task(FakeClient(json.dumps(data)), "classify", "help"), data)
    def test_empty_input(self):
        with self.assertRaises(ValueError): run_task(FakeClient(""), "summarize", "  ")
    def test_invalid_json(self):
        with self.assertRaises(ValueError): run_task(FakeClient("not json"), "classify", "hello")
    def test_unknown_task(self):
        with self.assertRaises(ValueError): run_task(FakeClient(""), "other", "hello")

if __name__ == "__main__": unittest.main()
