"""
Hybrid LLM Engine: Claude CLI (via HTTP) + Ollama fallback.

Priority order:
1. Claude CLI via subprocess (claude --print) -- uses your existing Claude Code auth
2. Ollama local models (qwen2.5:14b, deepseek-r1:14b, llama3, gemma2)
"""

import subprocess
import json
import requests
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODELS = ["qwen2.5:14b", "deepseek-r1:14b", "llama3:latest", "gemma2:latest"]


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str  # "claude_cli" or "ollama"
    success: bool
    error: str = ""


def _call_claude_cli(prompt: str, system: str = "", max_tokens: int = 4096) -> LLMResponse:
    """Call Claude via CLI subprocess using `claude --print`."""
    try:
        cmd = ["claude", "--print"]
        if system:
            cmd.extend(["--system", system])

        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
        )

        if result.returncode == 0 and result.stdout.strip():
            return LLMResponse(
                text=result.stdout.strip(),
                model="claude-cli",
                provider="claude_cli",
                success=True,
            )
        else:
            error = result.stderr.strip() if result.stderr else "Empty response"
            logger.warning(f"Claude CLI failed: {error}")
            return LLMResponse(
                text="", model="claude-cli", provider="claude_cli",
                success=False, error=error,
            )
    except FileNotFoundError:
        return LLMResponse(
            text="", model="claude-cli", provider="claude_cli",
            success=False, error="Claude CLI not found in PATH",
        )
    except subprocess.TimeoutExpired:
        return LLMResponse(
            text="", model="claude-cli", provider="claude_cli",
            success=False, error="Claude CLI timed out (120s)",
        )
    except Exception as e:
        return LLMResponse(
            text="", model="claude-cli", provider="claude_cli",
            success=False, error=str(e),
        )


def _call_ollama(prompt: str, system: str = "", model: str = None) -> LLMResponse:
    """Call Ollama local model."""
    if model is None:
        model = _get_best_ollama_model()
        if model is None:
            return LLMResponse(
                text="", model="none", provider="ollama",
                success=False, error="No Ollama models available",
            )

    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096},
        }
        if system:
            payload["system"] = system

        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("response", "").strip()

        if text:
            return LLMResponse(
                text=text, model=model, provider="ollama", success=True,
            )
        else:
            return LLMResponse(
                text="", model=model, provider="ollama",
                success=False, error="Empty response from Ollama",
            )
    except requests.ConnectionError:
        return LLMResponse(
            text="", model=model or "unknown", provider="ollama",
            success=False, error="Ollama not running (connection refused)",
        )
    except requests.Timeout:
        return LLMResponse(
            text="", model=model or "unknown", provider="ollama",
            success=False, error="Ollama timed out (180s)",
        )
    except Exception as e:
        return LLMResponse(
            text="", model=model or "unknown", provider="ollama",
            success=False, error=str(e),
        )


def _get_best_ollama_model() -> str | None:
    """Check which Ollama models are available and return the best one."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        available = [m["name"] for m in resp.json().get("models", [])]
        # Priority order
        for preferred in OLLAMA_MODELS:
            if preferred in available:
                return preferred
        return available[0] if available else None
    except Exception:
        return None


def get_available_providers() -> dict:
    """Check which LLM providers are available."""
    status = {"claude_cli": False, "ollama": False, "ollama_models": []}

    # Check Claude CLI
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        status["claude_cli"] = result.returncode == 0
    except Exception:
        pass

    # Check Ollama
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            status["ollama"] = True
            status["ollama_models"] = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass

    return status


def query(
    prompt: str,
    system: str = "",
    prefer: str = "auto",
    ollama_model: str = None,
) -> LLMResponse:
    """
    Hybrid LLM query with automatic fallback.

    prefer: "auto" (Claude first, Ollama fallback), "claude", "ollama"
    """
    if prefer == "claude":
        return _call_claude_cli(prompt, system)

    if prefer == "ollama":
        return _call_ollama(prompt, system, ollama_model)

    # Auto: try Claude first, fallback to Ollama
    response = _call_claude_cli(prompt, system)
    if response.success:
        return response

    logger.info(f"Claude CLI failed ({response.error}), falling back to Ollama")
    return _call_ollama(prompt, system, ollama_model)


def query_streaming(
    prompt: str,
    system: str = "",
    model: str = None,
) -> iter:
    """Stream response from Ollama (Claude CLI doesn't support streaming easily)."""
    if model is None:
        model = _get_best_ollama_model()
    if model is None:
        yield "Error: No Ollama models available"
        return

    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.3, "num_predict": 4096},
        }
        if system:
            payload["system"] = system

        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=180,
        )
        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                token = data.get("response", "")
                if token:
                    yield token
                if data.get("done", False):
                    break
    except Exception as e:
        yield f"\n\nError: {str(e)}"
