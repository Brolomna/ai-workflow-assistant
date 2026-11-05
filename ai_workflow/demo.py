"""Deterministic local examples for trying the CLI without an API key."""
import re


def _sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def run_demo(task, text):
    """Run a lightweight heuristic demonstration; this is not an AI model."""
    sentences = _sentences(text)
    if not sentences:
        raise ValueError("Input text is empty.")

    if task == "summarize":
        points = sentences[:4]
        return "## Demo summary\n\n" + " ".join(points) + (
            "\n\n> Offline demo: this is a simple extractive preview, not an AI-generated summary."
        )

    if task == "action-items":
        items = []
        pattern = re.compile(
            r"^([A-Z][\w'-]*)\s+(will|needs to|must|should)\s+(.+?)[.!?]?$",
            re.IGNORECASE,
        )
        for sentence in sentences:
            match = pattern.match(sentence)
            if not match:
                continue
            owner, verb, action = match.groups()
            deadline_match = re.search(r"\bby\s+([^,.]+)", action, re.IGNORECASE)
            deadline = deadline_match.group(1).strip() if deadline_match else None
            task_text = action[:deadline_match.start()].strip() if deadline_match else action.strip()
            items.append({
                "task": task_text[0].upper() + task_text[1:] if task_text else task_text,
                "owner": owner,
                "deadline": deadline,
                "priority": "medium" if verb.lower() in ("must", "needs to") else "unknown",
            })
        return items

    if task == "classify":
        lowered = text.lower()
        urgency = "high" if any(word in lowered for word in ("urgent", "asap", "immediately", "critical")) else "low"
        negative_words = ("confusing", "problem", "issue", "failed", "bad")
        positive_words = ("great", "excellent", "success", "thanks")
        negative_sentences = sum(
            any(word in sentence.lower() for word in negative_words)
            for sentence in sentences
        )
        positive_sentences = sum(
            any(word in sentence.lower() for word in positive_words)
            for sentence in sentences
        )

        if negative_sentences and positive_sentences:
            sentiment = "mixed"
        elif negative_sentences > positive_sentences and (
            negative_sentences >= 2 or len(sentences) == 1
        ):
            sentiment = "negative"
        elif positive_sentences > negative_sentences and (
            positive_sentences >= 2 or len(sentences) == 1
        ):
            sentiment = "positive"
        else:
            sentiment = "neutral"

        category = "meeting notes" if any(word in lowered for word in ("team", "meeting", "demo", "project")) else "general"
        return {
            "category": category,
            "sentiment": sentiment,
            "urgency": urgency,
            "rationale": (
                "Offline heuristic: sentiment is estimated from keyword-bearing "
                "sentences; isolated sentiment in longer text is treated cautiously."
            ),
        }

    raise ValueError("Unsupported task: " + task)
