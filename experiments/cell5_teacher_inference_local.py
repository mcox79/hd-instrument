"""CELL-5 teacher inference: pull 5K instruction prompts (Dolly-15k subset) and
call Together AI's Llama-3.1-405B-Instruct-Turbo to generate gold responses.

This is the LOCAL-runner step of CELL-5 (Path X + Option 4 SFT-internal-FD).
Output: data/cell5_teacher/{prompts.jsonl, responses.jsonl, manifest.json}.

Cost estimate (Together 405B-Instruct-Turbo $5/M tokens):
  5K prompts x ~(256 in + 500 out) tok = ~3.8M tokens -> ~\$19-25.

Wall: ~20-40 min wall depending on latency (concurrent requests via thread pool).

Once this completes, the cloud cell (exp_substrate_cascade_distillation_fd_smoke_v1.py)
will load the runner's responses.jsonl and run the FD pipeline on Lambda H100:1.

USAGE:
  --smoke               -> 50 prompts only (~\$0.20; quick API validation)
  --dry-run             -> 5 prompts (~\$0.02; sanity check the API connection)
  default               -> 5000 prompts (full ~\$19-25)
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse, json, time
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import urllib.error

REPO = Path(__file__).resolve().parent.parent

TEACHER_MODEL = "meta-llama/Llama-3.1-405B-Instruct"  # Together's full 405B Instruct (not "-Turbo" -- doesn't exist for 405B)
TOGETHER_CHAT_URL = "https://api.together.xyz/v1/chat/completions"
DEFAULT_PROMPTS = 5000
SMOKE_PROMPTS = 50
DRY_RUN_PROMPTS = 5

MAX_RESP_TOK = 512
TEMPERATURE = 0.0
TOP_P = 1.0
CONCURRENCY = 8       # parallel API calls
REQUEST_TIMEOUT_S = 60
MAX_RETRIES = 3

DOLLY_DATASET = "databricks/databricks-dolly-15k"


def load_together_token() -> str:
    p = REPO / ".together_token"
    if not p.exists():
        raise RuntimeError(f"Together token file missing at {p}")
    v = p.read_text(encoding="utf-8").strip().split("\n")[0].strip()
    if not v or v.startswith("PASTE"):
        raise RuntimeError(f"Together token file at {p} not populated; replace placeholder with actual key")
    return v


def load_prompts(n: int) -> List[Dict]:
    """Load Dolly-15k instructions; first N. Each prompt: {id, instruction, context, category}."""
    from datasets import load_dataset
    print(f"[data] loading {DOLLY_DATASET} (first {n} examples)...", flush=True)
    ds = load_dataset(DOLLY_DATASET, split="train", streaming=False, trust_remote_code=False)
    out = []
    for i, ex in enumerate(ds):
        if i >= n:
            break
        out.append({
            "id": str(i),
            "instruction": ex.get("instruction", ""),
            "context": ex.get("context", ""),
            "category": ex.get("category", "general_qa"),
        })
    print(f"[data] loaded {len(out)} prompts", flush=True)
    return out


def render_prompt(p: Dict) -> str:
    """Build a chat-style user message. Dolly has instruction + optional context."""
    instruction = p["instruction"].strip()
    context = p.get("context", "").strip()
    if context:
        return f"Context: {context}\n\nInstruction: {instruction}"
    return instruction


def call_together(token: str, prompt_text: str, prompt_id: str) -> Optional[Dict]:
    body = {
        "model": TEACHER_MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": MAX_RESP_TOK,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        TOGETHER_CHAT_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "hd-instrument/cell5",
        },
    )
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as r:
                resp = json.loads(r.read())
            content = resp["choices"][0]["message"]["content"]
            usage = resp.get("usage", {})
            return {
                "id": prompt_id,
                "response": content,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")[:200]
            last_err = f"HTTP {e.code}: {body_text}"
            if e.code in (429, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return {"id": prompt_id, "error": last_err}
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(2 ** attempt)
    return {"id": prompt_id, "error": last_err or "unknown failure"}


def run(n_prompts: int, dry_run: bool):
    out_dir = REPO / "data" / "cell5_teacher"
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts_path = out_dir / "prompts.jsonl"
    responses_path = out_dir / "responses.jsonl"
    manifest_path = out_dir / "manifest.json"

    token = load_together_token()
    print(f"[auth] Together token prefix: {token[:10]}...", flush=True)

    prompts = load_prompts(n_prompts)

    with open(prompts_path, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps(p) + "\n")
    print(f"[prompts] wrote {len(prompts)} to {prompts_path}", flush=True)

    rendered = {p["id"]: render_prompt(p) for p in prompts}

    print(f"[run] calling Together API ({TEACHER_MODEL}); concurrency={CONCURRENCY}", flush=True)
    t0 = time.time()
    responses_buf = {}
    failures = 0
    total_tokens_used = 0

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {pool.submit(call_together, token, txt, pid): pid
                   for pid, txt in rendered.items()}
        for i, fut in enumerate(as_completed(futures), start=1):
            res = fut.result()
            pid = res["id"]
            if "error" in res:
                failures += 1
                print(f"  [fail {pid}] {res['error'][:120]}", flush=True)
            else:
                responses_buf[pid] = res
                total_tokens_used += res.get("total_tokens", 0)
            if i % 25 == 0 or i == len(rendered):
                elapsed = time.time() - t0
                rate = i / max(elapsed, 1e-9)
                eta = (len(rendered) - i) / max(rate, 1e-9)
                est_cost = total_tokens_used * 5 / 1_000_000
                print(f"  [progress] {i}/{len(rendered)} | rate={rate:.1f}/s | "
                      f"failures={failures} | tokens={total_tokens_used} | "
                      f"est_cost=${est_cost:.2f} | eta={eta/60:.1f}min", flush=True)

    # Write responses
    with open(responses_path, "w", encoding="utf-8") as f:
        for pid in sorted(responses_buf.keys(), key=lambda s: int(s)):
            f.write(json.dumps(responses_buf[pid]) + "\n")

    elapsed = time.time() - t0
    est_cost = total_tokens_used * 5 / 1_000_000
    manifest = {
        "model": TEACHER_MODEL,
        "n_prompts_requested": len(rendered),
        "n_responses_successful": len(responses_buf),
        "n_failures": failures,
        "total_tokens_used": total_tokens_used,
        "est_cost_usd": round(est_cost, 4),
        "elapsed_s": round(elapsed, 1),
        "rate_per_sec": round(len(rendered) / max(elapsed, 1e-9), 2),
        "dry_run": dry_run,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n=== TEACHER INFERENCE COMPLETE ===", flush=True)
    print(f"Wrote prompts:   {prompts_path}", flush=True)
    print(f"Wrote responses: {responses_path}", flush=True)
    print(f"Wrote manifest:  {manifest_path}", flush=True)
    print(f"Success: {len(responses_buf)}/{len(rendered)} | Failures: {failures}", flush=True)
    print(f"Tokens: {total_tokens_used} | Cost (est.): ${est_cost:.2f} | Wall: {elapsed/60:.1f} min", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help=f"Run on {SMOKE_PROMPTS} prompts (~$0.20)")
    ap.add_argument("--dry-run", action="store_true", help=f"Run on {DRY_RUN_PROMPTS} prompts (~$0.02; API sanity)")
    ap.add_argument("--n", type=int, default=None, help="Override default prompt count")
    args = ap.parse_args()

    if args.n is not None:
        n = args.n
    elif args.dry_run:
        n = DRY_RUN_PROMPTS
    elif args.smoke:
        n = SMOKE_PROMPTS
    else:
        n = DEFAULT_PROMPTS

    print(f"=== CELL-5 teacher inference: n={n} prompts; model={TEACHER_MODEL} ===", flush=True)
    run(n, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
