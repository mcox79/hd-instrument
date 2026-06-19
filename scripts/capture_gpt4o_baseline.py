"""Capture gpt-4o-mini responses for the 3 decisive-test queries (one-shot; <$0.001 total)."""
import os
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

env = ROOT / ".env.local"
if env.exists():
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

from backend.llm.openai_client import ask_bare

QUERIES = [
    "Who founded Anthropic and when?",
    "What does the EU AI Act require?",
    "Who is the current President of France?",
]

system = (
    "You are a helpful assistant. Answer the user's question directly and concisely. "
    "If you do not know, say 'I don't know' rather than guessing."
)

results = []
total_cost = 0.0
for q in QUERIES:
    print(f"\n=== Q: {q} ===")
    r = ask_bare(q, system=system, max_tokens=150, temperature=0.1)
    print(f"A: {r.text}")
    print(f"   {r.input_tokens}in + {r.output_tokens}out = ${r.cost_usd:.6f}  ({r.latency_ms:.0f}ms)")
    total_cost += r.cost_usd
    results.append({
        "question": q,
        "answer": r.text,
        "model": r.model,
        "input_tokens": r.input_tokens,
        "output_tokens": r.output_tokens,
        "cost_usd": r.cost_usd,
        "latency_ms": r.latency_ms,
    })

out = ROOT / "data" / "gpt4o_baseline_responses.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results, indent=2))
print(f"\n=== TOTAL COST: ${total_cost:.6f} ===")
print(f"Wrote {out}")
