"""Command-line interface."""
import argparse
import json
import sys
from pathlib import Path
from .client import AIClientError, ChatCompletionsClient
from .tasks import run_task

def build_parser():
    parser = argparse.ArgumentParser(prog="ai-workflow", description="AI-powered text workflows")
    parser.add_argument("task", choices=["summarize", "action-items", "classify"])
    parser.add_argument("input", type=Path, help="UTF-8 text file to process")
    parser.add_argument("-o", "--output", type=Path, help="Optional output file")
    parser.add_argument("--model", help="Override AI_MODEL")
    parser.add_argument("--base-url", help="Override AI_BASE_URL")
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        source = args.input.read_text(encoding="utf-8")
        client = ChatCompletionsClient(model=args.model, base_url=args.base_url)
        result = run_task(client, args.task, source)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, (dict, list)) else result
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print("Saved result to " + str(args.output))
        else:
            print(rendered)
        return 0
    except FileNotFoundError:
        print("Input file not found: " + str(args.input), file=sys.stderr)
    except (OSError, UnicodeError, AIClientError, ValueError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
