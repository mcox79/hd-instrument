"""Hard-negative tuple generator: teacher-model bootstrap for Stage 1 training.

Per `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
Update 2 (external-reviewer feedback locked-in):

> "Bootstrap Stage 1 training data via teacher-model synthesis. Use
> Anthropic API to generate (query, ground-truth retrieval trace,
> hard-negative trace, final answer) tuples. The teacher model is
> provided with a graph snapshot of the substrate's stored facts/chains
> and asked to construct queries where the hard-negative is plausible-
> but-wrong (e.g., adjacent fact with the same predicate; off-by-one-hop
> chain; correct entities but wrong relation)."
>
> "Volume: ~50K tuples for Stage 1 training (~$50-150 Anthropic spend).
>  Reuse path: tuple-generation pipeline becomes infrastructure for the
>  reasoning-amortization experiment; not throwaway."

This module is the SCAFFOLDING. A smoke at small N (~5-20 tuples) gates
the full 50K generation. Tuples written JSONL-style for append-safety
and easy validation sampling (`validate_hard_negatives.py`).

Schema (one JSON object per line):
  {
    "tuple_id": str,             # stable id derived from query
    "query": str,                # natural-language question
    "gt_trace": [                # ground-truth retrieval steps
      {"step": int, "key": str, "expected_value": str},
      ...
    ],
    "hard_negative_trace": [     # plausible-but-wrong steps
      {"step": int, "key": str, "wrong_value": str,
       "why_plausible": str},   # short reason this is a hard negative
      ...
    ],
    "answer": str,               # final ground-truth answer
    "negative_kind": str,        # one of: "same_predicate_wrong_entity",
                                 #         "off_by_one_hop",
                                 #         "right_entities_wrong_relation",
                                 #         "other"
    "model": str,                # generator model id
    "tokens_in": int,
    "tokens_out": int,
    "generated_at": str,         # ISO-8601 local time
  }

Run (smoke):
  .venv\\Scripts\\python.exe -m testbed.training_data.hard_negative_tuple_gen \\
    --n-tuples 5 --out data/hard_neg_smoke.jsonl

Run (full):
  ... --n-tuples 50000 --out data/hard_neg_full.jsonl
  (full run: ~$50-150 + ~6h wall; manually inspect 50 random tuples
   after generation; if <80% pass quality bar, re-prompt with sharper
   instructions and re-run from the failed index.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


_TEACHER_SYSTEM_PROMPT = """You generate training data for a substrate-LLM bridge. The substrate is a fact-graph with simple key=value lookups; the bridge learns to convert LLM hidden states to substrate queries.

Your job: given a small substrate fact-graph snapshot and a target hop count, construct ONE training tuple consisting of:

  1. A natural-language query that requires the specified hop count to answer.
  2. The ground-truth retrieval trace: the sequence of (key, expected_value) steps a perfect retriever would take.
  3. A HARD-NEGATIVE retrieval trace: the same number of steps, ending at a WRONG value, but where each step is PLAUSIBLE (adjacent fact with same predicate, off-by-one-hop chain, or correct entities but wrong relation). Avoid trivially random negatives.
  4. The final ground-truth answer.

OUTPUT FORMAT (strict): respond with ONLY a JSON object matching this exact schema:

{
  "query": "natural language question",
  "gt_trace": [
    {"step": 1, "key": "k1", "expected_value": "v1"},
    {"step": 2, "key": "k2", "expected_value": "v2"}
  ],
  "hard_negative_trace": [
    {"step": 1, "key": "k1", "wrong_value": "v1_wrong", "why_plausible": "same predicate as gt, different person"},
    {"step": 2, "key": "k2_wrong", "wrong_value": "v2_wrong", "why_plausible": "off-by-one-hop chain"}
  ],
  "answer": "final ground-truth value",
  "negative_kind": "same_predicate_wrong_entity"  /* OR "off_by_one_hop" OR "right_entities_wrong_relation" */
}

No preamble, no markdown, no explanation outside the JSON. The JSON must parse with json.loads."""


def _make_corpus_snapshot_text(corpus, max_facts: int = 60) -> str:
    """Render a subset of corpus facts as the teacher-input graph snapshot."""
    lines = [f"FACT GRAPH SNAPSHOT (showing up to {max_facts} facts):", ""]
    for f in corpus.facts[:max_facts]:
        lines.append(f"  {f.key} = {f.value}")
    if len(corpus.facts) > max_facts:
        lines.append(f"  ... ({len(corpus.facts) - max_facts} more facts)")
    return "\n".join(lines)


def _build_user_prompt(corpus_text: str, hop_count: int, rng: random.Random) -> str:
    """Random-walk the hop_count + negative_kind to vary the training set."""
    kind_choices = [
        "same_predicate_wrong_entity",
        "off_by_one_hop",
        "right_entities_wrong_relation",
    ]
    target_kind = rng.choice(kind_choices)
    return (
        f"{corpus_text}\n\n"
        f"Construct ONE tuple with EXACTLY {hop_count} retrieval hops.\n"
        f"Target hard-negative kind: {target_kind}\n"
        f"Remember: output ONLY the JSON object."
    )


def _load_env_anthropic() -> None:
    env_path = _REPO_ROOT / ".env.anthropic"
    if not env_path.is_file():
        raise RuntimeError(f".env.anthropic not found at {env_path}")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)


def _generate_one(llm, corpus_text: str, hop_count: int,
                  rng: random.Random) -> dict[str, Any] | None:
    """Call the teacher; return parsed JSON dict or None on failure."""
    from hdlab_service.baselines.llm_client import LLMMessage
    user_prompt = _build_user_prompt(corpus_text, hop_count, rng)
    resp = llm.call(
        system_prompt=_TEACHER_SYSTEM_PROMPT,
        messages=[LLMMessage(role="user", content=user_prompt)],
        max_tokens=1024,
    )
    raw_text = (resp.text or "").strip()
    try:
        body = json.loads(raw_text)
    except Exception:
        # Try to extract JSON from a code-fence wrapper if the model
        # ignored the strict-format instruction.
        if "```" in raw_text:
            inner = raw_text.split("```", 2)[1]
            if inner.startswith("json"):
                inner = inner[4:]
            try:
                body = json.loads(inner.strip())
            except Exception:
                return None
        else:
            return None
    body["model"] = getattr(llm, "model", "unknown")
    body["tokens_in"] = resp.tokens_in
    body["tokens_out"] = resp.tokens_out
    body["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    qstr = body.get("query", "")
    body["tuple_id"] = hashlib.sha1(qstr.encode("utf-8")).hexdigest()[:12]
    return body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hard-negative tuple generator (Anthropic teacher-bootstrap)")
    parser.add_argument("--n-tuples", type=int, required=True,
                        help="How many tuples to generate (smoke: 5-20; full: ~50000)")
    parser.add_argument("--out", required=True,
                        help="Output JSONL path (append-safe)")
    parser.add_argument("--corpus", default="small",
                        choices=("small",),
                        help="Corpus to use as fact-graph snapshot")
    parser.add_argument("--hop-counts", default="1,2,3",
                        help="Comma-separated hop counts; rotated round-robin")
    parser.add_argument("--max-facts-in-snapshot", type=int, default=60,
                        help="Cap on facts shown to the teacher (token budget)")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--model", default="claude-sonnet-4-5-20250929",
                        help="Anthropic model id for the teacher")
    parser.add_argument("--max-failures", type=int, default=5,
                        help="Abort if N consecutive teacher responses fail to parse")
    args = parser.parse_args()

    _load_env_anthropic()

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = _REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from hdlab_service.baselines.llm_client import AnthropicLLMClient
    if args.corpus == "small":
        from hdlab_service.corpora.synthetic_corpus import small_corpus
        corpus = small_corpus()
    else:
        raise NotImplementedError(args.corpus)
    corpus_text = _make_corpus_snapshot_text(corpus, args.max_facts_in_snapshot)
    llm = AnthropicLLMClient(model=args.model)
    hop_counts = [int(h.strip()) for h in args.hop_counts.split(",") if h.strip()]
    rng = random.Random(args.seed)

    print(f"[hard_neg_gen] model={args.model}")
    print(f"[hard_neg_gen] corpus_facts={len(corpus.facts)}  "
          f"snapshot_lines={corpus_text.count(chr(10))}")
    print(f"[hard_neg_gen] target tuples: {args.n_tuples}  "
          f"hop_rotation: {hop_counts}")
    print(f"[hard_neg_gen] out: {out_path}")
    print()

    n_ok = 0
    n_fail = 0
    consec_fail = 0
    tokens_in_total = 0
    tokens_out_total = 0
    t0 = time.perf_counter()
    with out_path.open("a", encoding="utf-8") as f_out:
        for i in range(args.n_tuples):
            hop = hop_counts[i % len(hop_counts)]
            body = _generate_one(llm, corpus_text, hop, rng)
            if body is None:
                n_fail += 1
                consec_fail += 1
                print(f"  [{i+1:>4}/{args.n_tuples}] FAIL parse (consec={consec_fail})",
                      flush=True)
                if consec_fail >= args.max_failures:
                    print(f"\n[ERROR] {consec_fail} consecutive teacher failures; "
                          f"aborting", flush=True)
                    break
                continue
            consec_fail = 0
            n_ok += 1
            tokens_in_total += body.get("tokens_in", 0)
            tokens_out_total += body.get("tokens_out", 0)
            f_out.write(json.dumps(body, ensure_ascii=True) + "\n")
            f_out.flush()
            if i < 3 or (i + 1) % 25 == 0:
                # Sample: print the first few tuples and every 25th for sanity.
                print(f"  [{i+1:>4}/{args.n_tuples}] hop={hop} "
                      f"kind={body.get('negative_kind', '?')[:24]} "
                      f"q={body.get('query', '')[:50]!r}", flush=True)

    wall_s = time.perf_counter() - t0
    cost_in = tokens_in_total * 3 / 1_000_000
    cost_out = tokens_out_total * 15 / 1_000_000
    est_cost = cost_in + cost_out
    print()
    print("=" * 70)
    print(f"Tuple generation report")
    print("=" * 70)
    print(f"  Tuples ok: {n_ok}/{args.n_tuples}  fail: {n_fail}  "
          f"({100*n_ok/max(1,args.n_tuples):.1f}% success rate)")
    print(f"  Wall: {wall_s:.1f}s  (~{wall_s/max(1,n_ok):.2f}s per ok tuple)")
    print(f"  Tokens: in={tokens_in_total:,}  out={tokens_out_total:,}")
    print(f"  Estimated cost: ${est_cost:.4f}")
    print(f"  Output: {out_path}")
    print()
    print(f"  Next step: validate with "
          f"`python -m testbed.training_data.validate_hard_negatives "
          f"--in {out_path.name} --sample 50`")
    return 0 if n_ok > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
