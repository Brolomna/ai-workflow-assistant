AI Workflow Assistant
=====================

A practical Python CLI for summaries, action-item extraction, and text classification using an OpenAI-compatible chat completions API.

Features
--------
- Python CLI and package structure
- Standard-library HTTP client
- Structured JSON parsing and useful error messages
- Offline unit tests and GitHub Actions CI (Python 3.10-3.13)

Install
-------

    git clone https://github.com/Brolomna/ai-workflow-assistant.git
    cd ai-workflow-assistant
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .

Set credentials in your shell. Never commit API keys:

    export OPENAI_API_KEY="your-api-key"
    export AI_MODEL="gpt-4o-mini"
    export AI_BASE_URL="https://api.openai.com/v1"

Usage
-----

    ai-workflow summarize examples/meeting_notes.txt
    ai-workflow action-items examples/meeting_notes.txt --output action-items.json
    ai-workflow classify examples/meeting_notes.txt
    ai-workflow summarize notes.txt --model your-model --base-url https://provider.example/v1

Run `python -m ai_workflow.cli --help` for options. Structured tasks return JSON; summaries return Markdown text. Results print to the terminal unless --output is supplied.

Tests
-----

The test suite is fully offline and requires no API key:

    python -m unittest discover -s tests -v

GitHub Actions runs the tests on pushes and pull requests.

Security and limitations
------------------------

- Keep credentials in environment variables. The .gitignore excludes .env.
- Input text is sent to the configured AI provider. Do not submit confidential data unless authorized and after checking provider data policies.
- Model outputs can be inaccurate. Review owners, dates, priorities, and classifications.
- JSON syntax is validated, but semantic correctness is not guaranteed.
- The tool does not execute tasks or connect to external business systems.

Roadmap
-------

Batch processing, configurable output schemas, report templates, and local-model support.

License
-------

MIT. See LICENSE.
