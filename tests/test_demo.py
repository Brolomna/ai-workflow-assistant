"""Tests for deterministic offline workflow heuristics."""
import unittest

from ai_workflow.demo import run_demo


class DemoActionItemTests(unittest.TestCase):
    def test_extracts_multiple_named_owners(self):
        result = run_demo(
            "action-items",
            "Maya will send revised copy by Friday. Omar needs to check the payment integration.",
        )
        self.assertEqual([item["owner"] for item in result], ["Maya", "Omar"])
        self.assertEqual(result[0]["deadline"], "Friday")
        self.assertEqual(result[0]["task"], "Send revised copy")

    def test_extracts_unassigned_passive_action(self):
        result = run_demo(
            "action-items",
            "The signup flow is confusing and should be reviewed.",
        )
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["owner"])
        self.assertEqual(result[0]["task"], "Review the signup flow")

    def test_extracts_unassigned_active_action(self):
        result = run_demo("action-items", "The release notes should include the new settings.")
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["owner"])
        self.assertEqual(result[0]["task"], "Include the new settings in the release notes")

    def test_does_not_treat_general_statement_as_action(self):
        result = run_demo("action-items", "The team agreed that the launch was successful.")
        self.assertEqual(result, [])

    def test_deduplicates_repeated_action(self):
        result = run_demo(
            "action-items",
            "Maya will send the report. Maya will send the report.",
        )
        self.assertEqual(len(result), 1)

    def test_must_is_high_priority(self):
        result = run_demo("action-items", "Maya must fix the payment bug.")
        self.assertEqual(result[0]["priority"], "high")


class DemoClassificationTests(unittest.TestCase):
    def test_mixed_sentiment(self):
        result = run_demo("classify", "The launch was excellent. The payment integration failed.")
        self.assertEqual(result["sentiment"], "mixed")

    def test_urgent_word_sets_high_urgency(self):
        result = run_demo("classify", "This is urgent and needs attention.")
        self.assertEqual(result["urgency"], "high")

    def test_due_tomorrow_sets_medium_urgency(self):
        result = run_demo("classify", "The report is due tomorrow.")
        self.assertEqual(result["urgency"], "medium")

    def test_technical_category(self):
        result = run_demo("classify", "The payment integration has an error.")
        self.assertEqual(result["category"], "technical update")


if __name__ == "__main__":
    unittest.main()
