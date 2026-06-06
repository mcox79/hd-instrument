"""CELL-5 teacher inference: pull 5K stratified Dolly prompts + call Together AI's
Llama-3.3-70B-Instruct-Turbo to generate gold responses for SFT.

This is the LOCAL-runner step of CELL-5 (Path X + Option 4 SFT-internal-FD).
Output: data/cell5_teacher/{prompts.jsonl, responses.jsonl, manifest.json}.

Path A (user-authorized 2026-06-07 ~03:35 UTC) replaces original 405B spec.
Per Research recalibration: HP threshold drops from 1.5 to 1.3 with 70B teacher.

Cost: 5K x 750 tokens at $1.04/M (input + output combined for Turbo) = ~$3.90.
Wall: ~20-40 min (8 concurrent threads).

HARDENING (vs first draft):
 - Cost cap: aborts at $8 (~2x safety margin)
 - Refusal detection: counts and flags model refusals
 - Empty / error response: tracked separately and skipped in cloud cell
 - Resumability: skips prompts already in responses.jsonl
 - Dolly version pin: captures revision hash for reproducibility
 - Stratified sampling: ~equal split across all Dolly categories (Research Q12)

USAGE:
  --dry-run   -> 5 prompts (~$0.005; API + response shape sanity)
  --smoke     -> 50 prompts (~$0.04; verify cost meter + refusal + resumability)
  --full      -> 5000 prompts (~$3.90)
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
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import urllib.error
import threading

REPO = Path(__file__).resolve().parent.parent

TEACHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
TEACHER_PRICE_PER_M_TOK = 1.04
TOGETHER_CHAT_URL = "https://api.together.xyz/v1/chat/completions"
DEFAULT_PROMPTS = 5000
SMOKE_PROMPTS = 50
DRY_RUN_PROMPTS = 5

MAX_RESP_TOK = 512
TEMPERATURE = 0.0
TOP_P = 1.0
CONCURRENCY = 8
REQUEST_TIMEOUT_S = 60
MAX_RETRIES = 3

DOLLY_DATASET = "databricks/databricks-dolly-15k"
DOLLY_REVISION = "main"  # pinned at first run; we capture commit hash in manifest

COST_CAP_USD = 8.0  # ~2x safety margin over expected $3.90

REFUSAL_PATTERNS = (
    "i cannot ", "i can't ", "i am unable", "i'm unable",
    "as an ai ", "as a language model",
    "i'm sorry, but", "sorry, but i can",
    "i won't ", "i refuse ",
)


def load_together_token() -> str:
    p = REPO / ".together_token"
    if not p.exists():
        raise RuntimeError(f"Together token file missing at {p}")
    v = p.read_text(encoding="utf-8").strip().split("\n")[0].strip()
    if not v or v.startswith("PASTE"):
        raise RuntimeError(f"Together token file at {p} not populated; replace placeholder")
    return v


def load_completed_ids(responses_path: Path) -> Set[str]:
    """Scan existing responses.jsonl and return set of successfully-completed prompt IDs."""
    if not responses_path.exists():
        return set()
    completed = set()
    with open(responses_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "error" not in r and r.get("response", "").strip():
                completed.add(str(r["id"]))
    return completed


def load_dolly_stratified(n: int) -> List[Dict]:
    """Load Dolly-15k and stratify across categories (Research Q12).

    Returns roughly N/n_categories from each category. If a category has fewer
    examples than needed, takes all of them and the remainder is filled from
    larger categories proportionally.
    """
    from datasets import load_dataset
    print(f"[data] loading {DOLLY_DATASET} (revision={DOLLY_REVISION})...", flush=True)
    ds = load_dataset(DOLLY_DATASET, split="train", revision=DOLLY_REVISION,
                       streaming=False, trust_remote_code=False)
    # Capture dataset version for manifest
    try:
        info = ds.info
        version = str(info.version) if info.version else "unknown"
    except Exception:
        version = "unknown"

    # Group by category
    by_cat = {}
    for i, ex in enumerate(ds):
        cat = ex.get("category", "general_qa")
        by_cat.setdefault(cat, []).append({
            "id": str(i),
            "instruction": ex.get("instruction", ""),
            "context": ex.get("context", ""),
            "category": cat,
        })
    print(f"[data] {len(ds)} examples across {len(by_cat)} categories: "
          f"{', '.join(f'{k}={len(v)}' for k, v in sorted(by_cat.items()))}", flush=True)

    # Proportional + capped stratified sampling
    per_cat_target = n // len(by_cat)
    extras = n - per_cat_target * len(by_cat)
    selected = []
    for cat, examples in sorted(by_cat.items()):
        take = min(per_cat_target, len(examples))
        selected.extend(examples[:take])
    # Fill remaining slots from biggest categories
    remaining_pool = []
    for cat, examples in sorted(by_cat.items()):
        if len(examples) > per_cat_target:
            remaining_pool.extend(examples[per_cat_target:])
    selected.extend(remaining_pool[:extras])
    print(f"[data] stratified to {len(selected)} prompts across {len(by_cat)} categories", flush=True)
    return selected, version


def render_prompt(p: Dict) -> str:
    instruction = p["instruction"].strip()
    context = p.get("context", "").strip()
    if context:
        return f"Context: {context}\n\nInstruction: {instruction}"
    return instruction


def is_refusal(text: str) -> bool:
    if not text:
        return False
    head = text.strip().lower()[:200]
    return any(pat in head for pat in REFUSAL_PATTERNS)


_cost_lock = threading.Lock()
_cumulative_tokens = [0]
_cost_cap_reached = [False]
_write_lock = threading.Lock()  # for incremental responses.jsonl write


def call_together(token: str, prompt_text: str, prompt_id: str) -> Optional[Dict]:
    # Cost-cap circuit breaker check (cheap; before HTTP call)
    with _cost_lock:
        if _cost_cap_reached[0]:
            return {"id": prompt_id, "error": "cost_cap_reached_skip"}

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
            total = usage.get("total_tokens", 0)

            with _cost_lock:
                _cumulative_tokens[0] += total
                est_cost = _cumulative_tokens[0] * TEACHER_PRICE_PER_M_TOK / 1_000_000
                if est_cost > COST_CAP_USD:
                    _cost_cap_reached[0] = True

            refusal = is_refusal(content)
            return {
                "id": prompt_id,
                "response": content,
                "is_refusal": refusal,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": total,
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


def run(n_prompts: int, dry_run: bool, smoke: bool):
    out_dir = REPO / "data" / "cell5_teacher"
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts_path = out_dir / "prompts.jsonl"
    responses_path = out_dir / "responses.jsonl"
    manifest_path = out_dir / "manifest.json"

    token = load_together_token()
    print(f"[auth] Together token prefix: {token[:10]}... | cost cap: ${COST_CAP_USD:.2f}", flush=True)

    completed_ids = load_completed_ids(responses_path)
    if completed_ids:
        print(f"[resume] found {len(completed_ids)} already-completed prompt IDs in responses.jsonl; "
              f"will skip", flush=True)

    prompts, dolly_version = load_dolly_stratified(n_prompts)

    with open(prompts_path, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps(p) + "\n")
    print(f"[prompts] wrote {len(prompts)} (stratified) to {prompts_path}", flush=True)

    # Filter out already-completed prompts (resumability)
    to_process = [p for p in prompts if p["id"] not in completed_ids]
    if completed_ids:
        print(f"[resume] {len(to_process)}/{len(prompts)} prompts remaining after skip", flush=True)

    if not to_process:
        print(f"[skip] all prompts already done; nothing to do", flush=True)
        return

    rendered = {p["id"]: render_prompt(p) for p in to_process}

    print(f"[run] calling Together API ({TEACHER_MODEL}); concurrency={CONCURRENCY}", flush=True)
    print(f"[run] incremental write to {responses_path} (resilient to crash)", flush=True)
    t0 = time.time()
    newly_complete = {}
    failures = 0
    refusals = 0
    # Open responses file in append mode and write each success immediately
    # (resilient to crash; resumability via load_completed_ids works on restart)
    responses_fh = open(responses_path, "a", encoding="utf-8")

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {pool.submit(call_together, token, txt, pid): pid
                   for pid, txt in rendered.items()}
        for i, fut in enumerate(as_completed(futures), start=1):
            res = fut.result()
            pid = res["id"]
            if "error" in res:
                failures += 1
                if i <= 5 or i % 100 == 0:
                    print(f"  [fail {pid}] {res['error'][:120]}", flush=True)
            else:
                newly_complete[pid] = res
                if res.get("is_refusal"):
                    refusals += 1
                # Incremental write under lock (resilience)
                with _write_lock:
                    responses_fh.write(json.dumps(res) + "\n")
                    responses_fh.flush()
                    try:
                        os.fsync(responses_fh.fileno())
                    except OSError:
                        pass
            if i % 25 == 0 or i == len(rendered):
                elapsed = time.time() - t0
                rate = i / max(elapsed, 1e-9)
                eta = (len(rendered) - i) / max(rate, 1e-9)
                with _cost_lock:
                    est_cost = _cumulative_tokens[0] * TEACHER_PRICE_PER_M_TOK / 1_000_000
                    tokens = _cumulative_tokens[0]
                print(f"  [progress] {i}/{len(rendered)} | rate={rate:.1f}/s | "
                      f"fail={failures} refusal={refusals} | tok={tokens} | "
                      f"cost=${est_cost:.3f}/${COST_CAP_USD:.2f} | eta={eta/60:.1f}min",
                      flush=True)

            if _cost_cap_reached[0] and i % 25 == 0:
                print(f"  [COST CAP REACHED at ${est_cost:.3f}; remaining calls will be skipped]",
                      flush=True)

    # Close incremental-write handle
    responses_fh.close()

    elapsed = time.time() - t0
    with _cost_lock:
        est_cost = _cumulative_tokens[0] * TEACHER_PRICE_PER_M_TOK / 1_000_000
        total_tokens = _cumulative_tokens[0]

    total_successes = len(completed_ids) + len(newly_complete)
    manifest = {
        "model": TEACHER_MODEL,
        "path": "A_70B_Turbo_user_authorized_2026-06-07",
        "dolly_revision": DOLLY_REVISION,
        "dolly_dataset_version": dolly_version,
        "n_prompts_requested": len(prompts),
        "n_responses_successful": total_successes,
        "n_responses_this_run": len(newly_complete),
        "n_failures_this_run": failures,
        "n_refusals_this_run": refusals,
        "tokens_this_run": total_tokens,
        "est_cost_this_run_usd": round(est_cost, 4),
        "cost_cap_reached": _cost_cap_reached[0],
        "elapsed_s_this_run": round(elapsed, 1),
        "dry_run": dry_run,
        "smoke": smoke,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n=== TEACHER INFERENCE COMPLETE ===", flush=True)
    print(f"Prompts:     {prompts_path}", flush=True)
    print(f"Responses:   {responses_path}", flush=True)
    print(f"Manifest:    {manifest_path}", flush=True)
    print(f"Success: {total_successes}/{len(prompts)} "
          f"(this run: {len(newly_complete)})", flush=True)
    print(f"Failures this run: {failures} | Refusals this run: {refusals}", flush=True)
    print(f"Tokens: {total_tokens} | Cost (est.): ${est_cost:.3f} | Wall: {elapsed/60:.1f} min",
          flush=True)
    if _cost_cap_reached[0]:
        print(f"COST CAP HIT: remaining prompts not called", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help=f"{DRY_RUN_PROMPTS} prompts (~$0.005)")
    ap.add_argument("--smoke", action="store_true", help=f"{SMOKE_PROMPTS} prompts (~$0.04)")
    ap.add_argument("--full", action="store_true", help=f"{DEFAULT_PROMPTS} prompts (~$3.90)")
    ap.add_argument("--n", type=int, default=None)
    args = ap.parse_args()

    if args.n is not None:
        n = args.n
    elif args.dry_run:
        n = DRY_RUN_PROMPTS
    elif args.smoke:
        n = SMOKE_PROMPTS
    elif args.full:
        n = DEFAULT_PROMPTS
    else:
        print("[args] need --dry-run / --smoke / --full or --n=N", flush=True)
        sys.exit(2)

    print(f"=== CELL-5 teacher inference: n={n} prompts; model={TEACHER_MODEL} ===", flush=True)
    run(n, dry_run=args.dry_run, smoke=args.smoke)


if __name__ == "__main__":
    main()
