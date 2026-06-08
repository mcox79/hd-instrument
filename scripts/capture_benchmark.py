"""
Capture 30 queries across both substrate-tier5a and gpt-4o-mini for the benchmark page.

Categories (per SPEC v5 honesty requirement):
  - 6 factual where substrate has it and both should agree (substrate wins on provenance)
  - 6 post-cutoff facts substrate has + gpt-4o-mini may miss / hallucinate
  - 6 niche / compliance specifics where substrate is precise + gpt-4o-mini generic
  - 6 honest-abstention cases where substrate refuses + gpt-4o-mini answers from training
  - 6 multi-hop / composition where substrate's algebra helps + gpt-4o-mini may guess

Cost target: ~$0.005 in gpt-4o-mini API. Substrate side is free.

Usage on runner:
    cd C:\\dev\\hd-instrument && .venv-demo\\Scripts\\python.exe scripts\\capture_benchmark.py
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load .env.local
env_path = ROOT / ".env.local"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

import httpx
from backend.llm.openai_client import ask_bare


BACKEND_URL = "http://127.0.0.1:8000"

QUERIES = [
    # ============================================================
    # CATEGORY 1: Factual where both should pass (HONESTY; show substrate wins on provenance)
    # ============================================================
    ("factual_both", "Who founded OpenAI and when?"),
    ("factual_both", "Where is Anthropic headquartered?"),
    ("factual_both", "When was the Attention Is All You Need paper published?"),
    ("factual_both", "Who invented the World Wide Web?"),
    ("factual_both", "What is the speed of light in vacuum?"),
    ("factual_both", "When did the Berlin Wall fall?"),

    # ============================================================
    # CATEGORY 2: Post-cutoff facts substrate has; gpt-4o-mini may miss
    # ============================================================
    ("post_cutoff", "What is Claude Sonnet 4.6?"),
    ("post_cutoff", "When was Claude 4 released?"),
    ("post_cutoff", "What is Claude Haiku 4.5?"),
    ("post_cutoff", "Tell me about Mixtral 8x7B."),
    ("post_cutoff", "What is Gemini 2.5 Pro?"),
    ("post_cutoff", "When did Ilya Sutskever co-found a new company and what is it called?"),

    # ============================================================
    # CATEGORY 3: Niche / compliance specifics substrate has precise; gpt-4o-mini generic
    # ============================================================
    ("compliance", "What does the EU AI Act Article 12 require?"),
    ("compliance", "When did the EU AI Act enter into force?"),
    ("compliance", "What is NIST AI Risk Management Framework version 1.0 about and when was it published?"),
    ("compliance", "What is ISO 42001 and when was it published?"),
    ("compliance", "What happened with California Senate Bill 1047?"),
    ("compliance", "What is the Bletchley Declaration on AI safety?"),

    # ============================================================
    # CATEGORY 4: Honest-abstention (substrate refuses; gpt-4o-mini answers from training)
    # ============================================================
    ("abstain", "Who is the current President of France?"),
    ("abstain", "What is the population of Beijing?"),
    ("abstain", "When did Apple release the iPhone 16?"),
    ("abstain", "Who won the FIFA World Cup in 2022?"),
    ("abstain", "What is the chemical formula for caffeine?"),
    ("abstain", "What is the capital of Mongolia?"),

    # ============================================================
    # CATEGORY 5: Multi-hop or composition where substrate's algebra helps
    # ============================================================
    ("composition", "Tell me about Aidan Gomez and what he co-authored."),
    ("composition", "What did Tim Berners-Lee invent and where did he work?"),
    ("composition", "Who founded DeepMind and when was it acquired?"),
    ("composition", "What is AlphaFold 2 and who developed it?"),
    ("composition", "What is the EU AI Act and when does Article 12 take effect?"),
    ("composition", "When was the Higgs boson confirmed and where?"),
]


def query_substrate(question: str):
    """Hit /query/tier5a/baseline so we get BOTH substrate + gpt-4o-mini in one call."""
    t0 = time.perf_counter()
    r = httpx.post(
        f"{BACKEND_URL}/query/tier5a/baseline",
        json={"question": question, "top_k": 3, "max_new_tokens": 80, "temperature": 0.1},
        timeout=60.0,
    )
    elapsed = time.perf_counter() - t0
    r.raise_for_status()
    return r.json(), elapsed


def main():
    results = []
    total_cost = 0.0
    print(f"Capturing {len(QUERIES)} queries via /query/tier5a/baseline...")
    for i, (category, q) in enumerate(QUERIES):
        try:
            t0 = time.perf_counter()
            data, _ = query_substrate(q)
            elapsed = time.perf_counter() - t0
            substrate_ans = data.get("substrate", {}).get("answer", "")[:300]
            facts = data.get("substrate", {}).get("facts_used", [])
            bare = data.get("bare_llm", {})
            bare_ans = bare.get("answer", "")[:400]
            bare_cost = float(bare.get("cost_usd", 0.0))
            total_cost += bare_cost
            substrate_lat = data.get("substrate", {}).get("total_latency_ms", 0)
            bare_lat = bare.get("latency_ms", 0)
            results.append({
                "i": i + 1,
                "category": category,
                "question": q,
                "substrate_answer": substrate_ans,
                "substrate_facts": [{"fact": f["fact"], "score": f["score"]} for f in facts[:3]],
                "substrate_latency_ms": substrate_lat,
                "bare_answer": bare_ans,
                "bare_cost_usd": bare_cost,
                "bare_latency_ms": bare_lat,
                "bare_model": bare.get("model", "gpt-4o-mini"),
                "audit_chain_root": data.get("substrate", {}).get("audit_chain_root", "")[:16],
            })
            print(f"  [{i+1:2d}/{len(QUERIES)}] {category:13s} {elapsed:.2f}s ${bare_cost:.6f}: {q[:50]}")
        except Exception as e:
            print(f"  [{i+1:2d}/{len(QUERIES)}] FAILED: {q[:50]} -> {type(e).__name__}: {e}")
            results.append({"i": i + 1, "category": category, "question": q, "error": str(e)})
    out = ROOT / "data" / "benchmark_responses.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nTotal gpt-4o-mini API cost: ${total_cost:.6f}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
