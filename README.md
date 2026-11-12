# claude-cli-schema-bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

MIT-licensed, zero-dependency Python runtime adapter for local CLI agents that enforces deterministic JSON-schema compliance, middle-out prompt compression (`<8,000 TPM`), and resilient socket timeout guards.

## Problem Solved

Autonomous Python agent pipelines frequently fail in production due to three runtime bottlenecks:
1. **Payload Overflows (`HTTP 413` / `HTTP 429`):** Crawled HTML/DOM text exceeds strict `6,000–8,000 TPM` rate windows.
2. **Schema Mismatches (`got dict` / `got NoneType`):** Inference endpoints wrap JSON responses inside `<think>...</think>` blocks, markdown code fences, or return a single JSON object `{...}` when the downstream pipeline requires a root JSON array `[...]`.
3. **Unbounded Socket Hangs:** Stalled network sockets block `asyncio` task groups until 600-second watchdogs cancel the worker cycle.

## Quickstart

```python
from schema_bridge import compress_prompt_middle, build_agent_payload

safe_prompt = compress_prompt_middle(raw_website_dump, max_chars=4000)
payload = build_agent_payload(
    raw_response='<think>drafting...</think>\n{"subject": "quick question"}',
    json_schema_str='{"type": "array", "items": {"type": "object"}}'
)
print(payload["structured_output"])  # [{'subject': 'quick question'}]
```

## License
Released under the [MIT License](LICENSE).
