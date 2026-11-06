"""Deterministic local examples for trying the CLI without an API key."""
import re


def _sentences(text):
    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", text.strip())
        if part.strip()
    ]


def _contains_word(text, words):
    return any(
        re.search(r"\b" + re.escape(word) + r"\b", text, re.IGNORECASE)
        for word in words
    )


def _deadline_from(action):
    match = re.search(
        r"\b(?:by|before|due|on)\s+"
        r"((?:next\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
        r"today|tomorrow|tonight|the\s+demo|the\s+launch|"
        r"\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+"
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
        r"|\d{4}-\d{2}-\d{2}))",
        action,
        re.IGNORECASE,
    )
    if not match:
        return action.strip(), None
    cleaned = (action[:match.start()] + action[match.end():]).strip(" ,;")
    return cleaned, match.group(1).strip()


def _normalise_action(action):
    action = action.strip(" ,;")
    if not action:
        return action
    return action[0].upper() + action[1:]


def _extract_action_items(sentences):
    items = []
    seen = set()
    named_pattern = re.compile(
        r"^(?P<owner>[A-Z][\w'-]*)\s+"
        r"(?P<modal>will|needs to|must|should|has to)\s+"
        r"(?P<action>.+?)[.!?]?$",
        re.IGNORECASE,
    )
    passive_pattern = re.compile(
        r"^(?P<subject>.+?)\s+"
        r"(?P<modal>should|needs to|must|has to)\s+"
        r"be\s+(?P<verb>reviewed|updated|fixed|checked|tested|documented|"
        r"completed|sent|created|removed|approved|rewritten|investigated)"
        r"(?P<tail>.*?)[.!?]?$",
        re.IGNORECASE,
    )
    active_pattern = re.compile(
        r"^(?P<subject>.+?)\s+"
        r"(?P<modal>should|needs to|must|has to)\s+"
        r"(?P<action>review|update|fix|check|test|document|complete|send|create|"
        r"remove|approve|rewrite|investigate)\b(?P<tail>.*?)[.!?]?$",
        re.IGNORECASE,
    )
    past_to_base = {
        "reviewed": "Review", "updated": "Update", "fixed": "Fix",
        "checked": "Check", "tested": "Test", "documented": "Document",
        "completed": "Complete", "sent": "Send", "created": "Create",
        "removed": "Remove", "approved": "Approve", "rewritten": "Rewrite",
        "investigated": "Investigate",
    }

    def add(task, owner, modal, deadline=None):
        task, extracted_deadline = _deadline_from(task)
        deadline = deadline or extracted_deadline
        task = _normalise_action(task)
        if not task:
            return
        key = (task.casefold(), (owner or "").casefold())
        if key in seen:
            return
        seen.add(key)
        priority = "high" if modal.lower() == "must" else (
            "medium" if modal.lower() in ("needs to", "has to") else "unknown"
        )
        items.append({
            "task": task,
            "owner": owner,
            "deadline": deadline,
            "priority": priority,
        })

    for sentence in sentences:
        match = named_pattern.match(sentence)
        if match:
            owner = match.group("owner")
            modal = match.group("modal")
            action = match.group("action")
            # Strip an obvious trailing conjunction fragment rather than
            # presenting it as part of the task.
            action = re.sub(r"\s+(?:and|but)\s*$", "", action, flags=re.IGNORECASE)
            add(action, owner, modal)
            continue

        match = passive_pattern.match(sentence)
        if match:
            subject = match.group("subject")
            # Remove a preceding descriptive clause: "X is confusing and..."
            subject = re.sub(
                r"\s+(?:is|are|was|were)\s+[^,;]+?\s+and$",
                "",
                subject,
                flags=re.IGNORECASE,
            ).strip()
            verb = past_to_base[match.group("verb").lower()]
            tail = match.group("tail").strip()
            add(f"{verb} {subject}{tail}", None, match.group("modal"))
            continue

        match = active_pattern.match(sentence)
        if match:
            subject = match.group("subject").strip()
            action = match.group("action").strip()
            tail = match.group("tail").strip()
            if action.lower() == "include":\n                task = f"Include{tail} in {subject}"\n            else:\n                task = f"{action.capitalize()} {subject}{tail}"\n            add(task, None, match.group("modal"))

    return items


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
        return _extract_action_items(sentences)

    if task == "classify":
        urgency_high = ("urgent", "asap", "immediately", "critical", "right away")
        urgency_medium = ("soon", "deadline", "time-sensitive")
        lowered = text.lower()
        if _contains_word(lowered, urgency_high):
            urgency = "high"
        elif _contains_word(lowered, urgency_medium) or re.search(
            r"\b(?:due|by)\s+(?:today|tomorrow)\b", lowered
        ):
            urgency = "medium"
        else:
            urgency = "low"

        negative_words = ("confusing", "problem", "issue", "failed", "bad", "broken", "disappointed")
        positive_words = ("great", "excellent", "success", "thanks", "good", "pleased")
        negative_sentences = sum(
            _contains_word(sentence, negative_words) for sentence in sentences
        )
        positive_sentences = sum(
            _contains_word(sentence, positive_words) for sentence in sentences
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

        if _contains_word(lowered, ("meeting", "standup", "sync", "agenda")):
            category = "meeting notes"
        elif _contains_word(lowered, ("bug", "error", "crash", "payment", "login", "integration")):
            category = "technical update"
        elif _contains_word(lowered, ("customer", "client", "support", "refund", "complaint")):
            category = "customer support"
        elif _contains_word(lowered, ("team", "demo", "project", "launch", "sprint")):
            category = "project update"
        else:
            category = "general"

        return {
            "category": category,
            "sentiment": sentiment,
            "urgency": urgency,
            "rationale": (
                "Offline heuristic: category, sentiment, and urgency are estimated "
                "from keyword patterns. Review this result before acting on it."
            ),
        }

    raise ValueError("Unsupported task: " + task)
