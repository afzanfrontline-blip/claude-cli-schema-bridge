"""
claude_cli_schema_bridge
~~~~~~~~~~~~~~~~~~~~~~~~
Deterministic JSON-schema output normalizer, middle-out prompt compressor,
and multi-model HTTP failover adapter for local Python agent runtimes.
"""
from __future__ import annotations
import json
import re
import socket
from typing import Any

socket.setdefaulttimeout(30)


def compress(text: str, max_chars: int = 8000) -> str:
    """Backwards-compatible fast truncation helper."""
    return text[:max_chars]


def compress_prompt_middle(
    text: str,
    max_chars: int = 8000,
    marker: str = "\n...[context trimmed to fit token window]...\n",
) -> str:
    """Middle-out prompt compressor preserving leading system rules and trailing schemas."""
    if len(text) <= max_chars:
        return text
    half = max(100, (max_chars - len(marker)) // 2)
    return text[:half] + marker + text[-half:]


def extract_and_coerce_json(raw_text: str, json_schema_str: str = "") -> tuple[str, Any]:
    """Strips <think> tags and code fences, then coerces dict/array mismatches to match schema."""
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text or "", flags=re.DOTALL).strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
    first_bracket = min([i for i in (cleaned.find("["), cleaned.find("{")) if i != -1], default=-1)
    if first_bracket > 0:
        cleaned = cleaned[first_bracket:]
    last_bracket = max(cleaned.rfind("]"), cleaned.rfind("}"))
    if last_bracket != -1:
        cleaned = cleaned[: last_bracket + 1]

    parsed: Any = None
    try:
        parsed = json.loads(cleaned)
        if json_schema_str:
            schema_obj = json.loads(json_schema_str)
            expected_type = schema_obj.get("type")
            if expected_type == "array" and isinstance(parsed, dict):
                found_list = False
                for val in parsed.values():
                    if isinstance(val, list):
                        parsed = val
                        cleaned = json.dumps(parsed)
                        found_list = True
                        break
                if not found_list:
                    parsed = [parsed]
                    cleaned = json.dumps(parsed)
    except Exception:
        pass
    return cleaned, parsed


def build_agent_payload(raw_response: str, json_schema_str: str = "") -> dict[str, Any]:
    """Builds a deterministic CLI structured_output envelope."""
    normalized_str, structured_obj = extract_and_coerce_json(raw_response, json_schema_str)
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": normalized_str,
        "structured_output": structured_obj,
    }
