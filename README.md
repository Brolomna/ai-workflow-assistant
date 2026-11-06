<div align="center">

# AI Workflow Assistant

**A small, practical Python CLI for turning plain-text notes into useful outputs.**

Summaries · Action items · Text classification · Offline demo

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tests](https://github.com/Brolomna/ai-workflow-assistant/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-14B8A6)

</div>

---

## What it does

AI Workflow Assistant accepts a UTF-8 text file and runs one of three workflows:

| Command | Output |
| --- | --- |
| `summarize` | A concise Markdown summary |
| `action-items` | JSON tasks with owner, deadline, and priority |
| `classify` | JSON category, sentiment, urgency, and rationale |

It supports OpenAI-compatible Chat Completions APIs and includes a **local offline demo mode**. You can explore every command without an API key, paid credits, or a network connection.

## Quick start

### 1. Install

Python 3.10 or newer is required.

```bash
git clone https://github.com/Brolomna/ai-workflow-assistant.git
cd ai-workflow-assistant

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
```

### 2. Try it free in offline demo mode

No API key is needed:

```bash
ai-workflow summarize examples/meeting_notes.txt --demo
ai-workflow action-items examples/meeting_notes.txt --demo
ai-workflow classify examples/meeting_notes.txt --demo
```

If `OPENAI_API_KEY` is not set, the CLI automatically selects offline demo mode. If the provider reports a quota/credit/billing error, it falls back to the demo and prints a clear notice.

> **Demo limitation:** Offline mode uses simple local heuristics and sentence extraction. It is deterministic and useful for demonstrating the interface, but it is not an LLM and its results are not equivalent to AI-generated analysis.

### 3. Enable AI mode (optional)

Add a valid API key and choose a model supported by your provider:

```bash
export OPENAI_API_KEY="your-api-key"
export AI_MODEL="gpt-4o-mini"
export AI_BASE_URL="https://api.openai.com/v1"
```

Then run a command without `--demo`:

```bash
ai-workflow summarize examples/meeting_notes.txt
ai-workflow action-items examples/meeting_notes.txt
ai-workflow classify examples/meeting_notes.txt
```

API usage may incur charges. ChatGPT subscriptions and API billing are separate. Check your provider's pricing and account balance before running live requests.

## Browser demo

Launch a polished local browser interface without an API key or external service:

```bash
ai-workflow-web
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Paste notes, choose a workflow, and view or copy the result. Stop the server with `Ctrl+C`.

The web interface uses the same deterministic offline heuristics as `--demo`. It binds to localhost by default, accepts requests up to 1 MB, uses no external services, and does not send submitted text to an AI provider. It is intended as a local portfolio demo, not a public production deployment.

To choose another local port:

```bash
ai-workflow-web --port 8080
```

## Output to a file

Use `--output` (or `-o`) to save results:

```bash
ai-workflow action-items examples/meeting_notes.txt --demo --output output/action-items.json
ai-workflow classify examples/meeting_notes.txt --demo --output output/classification.json
ai-workflow summarize examples/meeting_notes.txt --demo --output output/summary.md
```

Parent directories are created automatically.

## CLI reference

```text
ai-workflow {summarize,action-items,classify} INPUT
            [--output PATH]
            [--model MODEL]
            [--base-url URL]
            [--demo]
```

- `--demo`: force local offline mode, even if an API key is configured.
- `--model`: override `AI_MODEL` for a live request.
- `--base-url`: override `AI_BASE_URL` for a live request.
- `--output`: write the result to a file instead of printing it.

## Example input

The included `examples/meeting_notes.txt` contains a short project sync:

```text
Maya will send revised landing page copy by Friday.
The team agreed to move the demo to next Wednesday.
Omar needs to check the payment integration before the demo.
The signup flow is confusing and should be reviewed.
No owner was assigned to the documentation update.
```

## Run the tests

The test suite uses Python's standard library and does not call an API:

```bash
python -m unittest discover -s tests -v
```

The CLI integration tests exercise all three commands in offline mode. GitHub Actions also runs the suite on Python 3.10, 3.11, 3.12, and 3.13 for pushes and pull requests.

## Project structure

```text
ai-workflow-assistant/
├── ai_workflow/
│   ├── __init__.py
│   ├── cli.py          # Arguments, execution, and fallback behavior
│   ├── client.py       # OpenAI-compatible HTTP client
│   ├── demo.py         # Local heuristic demo workflows
│   └── tasks.py        # Prompts and result validation
├── examples/
│   └── meeting_notes.txt
├── tests/
│   ├── test_cli.py     # Offline CLI integration tests
│   └── test_tasks.py   # Task and JSON validation tests
├── .github/workflows/
│   └── tests.yml       # Python-version CI matrix
├── pyproject.toml
└── README.md
```

## Design notes

- **Low dependency footprint:** HTTP requests use Python's standard library.
- **Provider flexibility:** the client targets the OpenAI-compatible Chat Completions format.
- **Credential hygiene:** API keys are read from environment variables and should never be committed.
- **Input safety:** task instructions tell the model to treat source text as untrusted input.
- **Output validation:** structured workflows parse JSON and return a clear error for malformed responses.
- **Human review:** model-generated owners, dates, priorities, and classifications should be checked before use.

Input text is sent to the configured AI provider in live mode. Do not submit confidential or personal data unless you are authorized to do so and have reviewed the provider's data policies.

## Roadmap

- [x] Three text workflows
- [x] OpenAI-compatible API client
- [x] Offline demo mode
- [x] Automated tests for all three offline CLI commands
- [x] Python-version CI workflow
- [ ] Batch processing
- [ ] Configurable output schemas
- [ ] Local LLM provider examples

## License

MIT. See [LICENSE](LICENSE).
