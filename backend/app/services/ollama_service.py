import os
import re
import time

from dotenv import load_dotenv
import requests

load_dotenv()


# ==========================================================
# OLLAMA CONFIGURATION
# ==========================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
).strip().rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b").strip() or "qwen3:4b"
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "600"))
OLLAMA_MAX_OUTPUT_TOKENS = 4096
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
AI_MODEL_ID = f"Ollama:{OLLAMA_MODEL}"


class OllamaTimeoutError(RuntimeError):
    """Raised when Ollama does not finish generating before the timeout."""


class OllamaConnectionError(RuntimeError):
    """Raised when Ollama is not reachable after all retries."""


# ==========================================================
# HEALTH CHECK
# ==========================================================

def check_ollama_health() -> bool:
    """Return True if Ollama is responding."""
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10,
        )
        return response.ok
    except Exception:
        return False


def ensure_model_loaded():
    """Pre-warm the model so the first real request does not timeout."""
    try:
        requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": "Hello",
                "stream": False,
                "options": {"num_predict": 1},
            },
            timeout=120,
        )
    except Exception:
        pass


# ==========================================================
# STRIP QWEN3 THINKING BLOCKS
# ==========================================================

_THINK_PATTERN = re.compile(
    r"<think>.*?</think>",
    re.DOTALL,
)


def _strip_think_blocks(text: str) -> str:
    """
    Qwen3 models emit <think>...</think> blocks before the
    actual response.  Strip them so downstream JSON parsing
    is not broken.
    """
    return _THINK_PATTERN.sub("", text).strip()


# ==========================================================
# GENERATE TEXT
# ==========================================================

def generate_text(
    prompt: str,
    *,
    format: str | dict | None = None,
    max_output_tokens: int | None = None,
) -> str:

    if not prompt or not prompt.strip():

        raise ValueError(
            "Prompt cannot be empty."
        )

    output_token_limit = (
        OLLAMA_MAX_OUTPUT_TOKENS
        if max_output_tokens is None
        else max_output_tokens
    )
    if output_token_limit < 1:
        raise ValueError("max_output_tokens must be greater than zero.")

    # ----------------------------------------------------------
    # For JSON output, tell Qwen3 to skip internal reasoning.
    # This dramatically speeds up responses.
    # ----------------------------------------------------------

    effective_prompt = prompt
    if format is not None:
        effective_prompt = "/no_think\n" + prompt

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": effective_prompt,
        "stream": False,
        "options": {
            "num_predict": output_token_limit,
        },
    }
    if OLLAMA_MODEL.lower().startswith("qwen3"):
        payload["think"] = False
    if format is not None:
        payload["format"] = format

    # ----------------------------------------------------------
    # RETRY LOOP with exponential backoff
    # ----------------------------------------------------------

    last_error = None
    for attempt in range(1, OLLAMA_MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=OLLAMA_TIMEOUT_SECONDS,
            )
            break

        except requests.ConnectionError as error:
            last_error = error
            if attempt < OLLAMA_MAX_RETRIES:
                wait = min(2 ** attempt, 30)
                print(
                    f"[Ollama] Connection failed (attempt {attempt}/{OLLAMA_MAX_RETRIES}), "
                    f"retrying in {wait}s..."
                )
                time.sleep(wait)
                continue
            raise OllamaConnectionError(
                "Cannot connect to Ollama after multiple attempts. "
                "Start the Ollama application or run `ollama serve`, then retry."
            ) from error

        except requests.Timeout as error:
            last_error = error
            if attempt < OLLAMA_MAX_RETRIES:
                wait = min(2 ** attempt, 30)
                print(
                    f"[Ollama] Timeout (attempt {attempt}/{OLLAMA_MAX_RETRIES}), "
                    f"retrying in {wait}s..."
                )
                time.sleep(wait)
                continue
            raise OllamaTimeoutError(
                f"Ollama did not respond within {OLLAMA_TIMEOUT_SECONDS} seconds "
                f"after {OLLAMA_MAX_RETRIES} attempts. "
                "Check that the local model is running and try again."
            ) from error

    if not response.ok:
        try:
            detail = response.json().get("error", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(
            f"Ollama request failed ({response.status_code}): {detail}"
        )

    try:
        result = response.json().get("response")
    except ValueError as error:
        raise RuntimeError("Ollama returned an invalid JSON response.") from error

    if not isinstance(result, str) or not result.strip():
        raise RuntimeError("Ollama returned an empty response.")

    # Strip Qwen3 <think>...</think> blocks
    result = _strip_think_blocks(result)

    if not result:
        raise RuntimeError("Ollama returned only thinking output with no content.")

    if format == "json":
        result = result.replace("```json", "").replace("```", "").strip()
        match = re.search(r"\{.*\}|\[.*\]", result, re.DOTALL)
        if match:
            result = match.group(0)

    return result