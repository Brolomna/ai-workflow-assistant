"""OpenAI-compatible Chat Completions client using only the standard library."""
import json
import os
import urllib.error
import urllib.request

class AIClientError(RuntimeError):
    pass

class ChatCompletionsClient:
    def __init__(self, api_key=None, model=None, base_url=None, timeout=45):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("AI_MODEL", "gpt-4o-mini")
        self.base_url = (base_url or os.getenv("AI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.timeout = timeout
        if not self.api_key:
            raise AIClientError("Missing API key. Set OPENAI_API_KEY in your environment.")

    def complete(self, system_prompt, user_prompt):
        payload = json.dumps({"model": self.model, "temperature": 0.2, "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]}).encode("utf-8")
        request = urllib.request.Request(self.base_url + "/chat/completions", data=payload,
            headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise AIClientError("Provider returned HTTP " + str(exc.code) + ": " + detail) from exc
        except urllib.error.URLError as exc:
            raise AIClientError("Could not reach AI provider: " + str(exc.reason)) from exc
        except (TimeoutError, json.JSONDecodeError) as exc:
            raise AIClientError("Provider response failed: " + str(exc)) from exc
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIClientError("Provider response did not contain a chat completion.") from exc
        if not isinstance(content, str) or not content.strip():
            raise AIClientError("Provider returned an empty response.")
        return content.strip()
