"""
exp_speculative_decoding_qwen_v1.py

Speculative decoding pre-test on the hotpot_3baseline answer path.

Per Exp-Dev routing (exp_dev_to_testbed_speculative_decoding_handoff_2026-06-07.md)
and Research closure (research_to_testbed_colbert_path_closed_v1_2026-06-07.md):
- HARD-PASS: >= 2.0x latency speedup at equal answer F1 (|delta_F1| < 0.02)
- BORDER:    1.5x <= speedup < 2.0x  (still helpful but below the gate)
- HARD-FAIL: speedup < 1.5x OR |delta_F1| >= 0.02 (quality regression)

DEVIATION FROM HANDOFF: The handoff suggested Llama-1B as draft for Qwen2.5-1.5B target,
but HF's standard assistant_model speculative decoding requires draft + target share
vocabulary. Qwen and Llama have different tokenizers. Using Qwen2.5-0.5B-Instruct as
draft instead -- same family, matching tokenizer, smaller than Llama-1B so possibly
even better speedup. Flagged in Research note.

Method:
- Load Qwen2.5-1.5B-Instruct (target) + Qwen2.5-0.5B-Instruct (draft) on same GPU in bf16
- Load HotpotQA distractor dev split; filter to type=='bridge'; sample --n-questions
- For each question, build instruct prompt with flattened context
- Baseline: target-only greedy decode; measure tokens/sec + answer F1
- Speculative: target + assistant_model=draft greedy decode; measure tokens/sec + answer F1
- Report: speedup, F1 delta, per-metric verdicts

Hardening (per 2026-06-07 lessons):
- try/except wraps main(); emits FAILURE metrics.json on crash
- Per-question latency JSONL streamed with fsync (progress save)
- Corpus + baseline + speculative results saved to disk before metric calc
- GPU memory logged pre-decode
"""

import argparse
import gc
import json
import math
import os
import re
import string
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402


# =============================================================================
# Config + constants
# =============================================================================

ANCHOR_NAME = "speculative_decoding_qwen_v1"

HP_SPEEDUP = 2.0    # HARD-PASS threshold
MID_SPEEDUP = 1.5   # BORDER lower edge
F1_DELTA_TOLERANCE = 0.02   # |F1_spec - F1_baseline| must be <= this; else quality regression -> HARD_FAIL

TARGET_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DRAFT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
HOTPOT_REPO = "hotpotqa/hotpot_qa"
HOTPOT_CONFIG = "distractor"
HOTPOT_SPLIT = "validation"

MAX_NEW_TOKENS = 64    # short answer; HotpotQA answers are usually <20 tokens
WARMUP_QUESTIONS = 5   # first N questions used for warmup, not measured

# =============================================================================
# CLI
# =============================================================================

_ap = argparse.ArgumentParser()
_ap.add_argument("--n-questions", type=int, default=100,
                  help="Number of bridge questions to evaluate (excluding warmup)")
_ap.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
_ap.add_argument("--self-test", action="store_true",
                  help="Run lightweight PROT-022 import + signature check; exit 0")
_ARGS = _ap.parse_args()


# =============================================================================
# PROT-022 self-test
# =============================================================================

def _selftest():
    """Lightweight checks: imports, signature consistency, F1 calc on fake data."""
    print("[selftest] starting", flush=True)
    # Verify thresholds match Research/Exp-Dev routing
    assert abs(HP_SPEEDUP - 2.0) < 1e-9, "HP speedup drift"
    assert abs(MID_SPEEDUP - 1.5) < 1e-9, "BORDER speedup drift"
    assert abs(F1_DELTA_TOLERANCE - 0.02) < 1e-9, "F1 delta tolerance drift"

    # Mini main-path test: F1 calculation on fake examples
    f1 = answer_f1("the great wall of china", "Great Wall of China")
    assert abs(f1 - 1.0) < 1e-6, f"F1 should be 1.0 for word-match, got {f1}"

    f1_partial = answer_f1("eiffel tower paris", "Eiffel Tower")
    # pred = {eiffel, tower, paris}; gold = {eiffel, tower}; common = 2
    # prec = 2/3, recall = 2/2 = 1, F1 = 2*0.667*1/(0.667+1) = 0.8
    assert abs(f1_partial - 0.8) < 1e-3, f"F1 partial expected 0.8, got {f1_partial}"

    f1_none = answer_f1("apple", "banana")
    assert abs(f1_none - 0.0) < 1e-9, f"F1 should be 0.0 for no overlap, got {f1_none}"

    # Verdict logic on synthetic numbers
    v = decide_verdict(speedup=2.1, f1_delta=0.005)
    assert v == "HARD_PASS", f"HP synth: {v}"
    v = decide_verdict(speedup=1.7, f1_delta=0.005)
    assert v == "MID", f"MID synth: {v}"
    v = decide_verdict(speedup=1.2, f1_delta=0.005)
    assert v == "HARD_FAIL", f"HF speed synth: {v}"
    v = decide_verdict(speedup=2.5, f1_delta=0.05)
    assert v == "HARD_FAIL", f"HF quality regression synth: {v}"

    # Verify datasets import path (not transformers/torch — those break local)
    try:
        from datasets import load_dataset  # noqa: F401
    except Exception as e:
        print(f"[selftest] WARNING: datasets not importable locally: {e} (OK; installed at setup)",
              flush=True)

    print(f"[selftest] PASS: F1 calc verified on fake data; HP/MID/HF thresholds intact "
          f"(HP speedup >= {HP_SPEEDUP}; F1 delta tolerance {F1_DELTA_TOLERANCE}); "
          f"n_questions default={_ARGS.n_questions}", flush=True)


# =============================================================================
# Data preparation
# =============================================================================

def load_bridge_questions(n: int) -> List[Dict]:
    """Load first n+WARMUP HotpotQA distractor dev BRIDGE questions.

    Prefers a pre-extracted JSONL at ~/sky_workdir/data/hotpot_distractor_bridge.jsonl
    (written once during setup) BEFORE falling back to HF script-mode loader.
    """
    need = n + WARMUP_QUESTIONS
    cached = Path(os.environ.get("HOME", "/root")) / "sky_workdir/data/hotpot_distractor_bridge.jsonl"
    if cached.is_file():
        print(f"[data] using cached bridge JSONL at {cached}", flush=True)
        bridge = []
        with open(cached) as f:
            for line in f:
                bridge.append(json.loads(line))
                if len(bridge) >= need:
                    break
        if len(bridge) < need:
            print(f"[WARN] cached has only {len(bridge)} bridge questions (wanted {need})", flush=True)
        return bridge

    print(f"[data] loading hotpot_qa distractor/validation via HF (slow path)", flush=True)
    from datasets import load_dataset
    ds = load_dataset(HOTPOT_REPO, HOTPOT_CONFIG, split=HOTPOT_SPLIT, trust_remote_code=True)
    print(f"[data] loaded {len(ds)} dev examples; filtering to type=='bridge'", flush=True)

    bridge = []
    for ex in ds:
        if ex.get("type") == "bridge":
            bridge.append(ex)
            if len(bridge) >= need:
                break
    if len(bridge) < need:
        print(f"[WARN] only {len(bridge)} bridge questions; proceeding", flush=True)
    print(f"[data] collected {len(bridge)} bridge questions", flush=True)
    return bridge


def build_prompt(question_obj: Dict, max_context_chars: int = 4000) -> str:
    """Build an instruct-style prompt for the hotpot answer task.

    Context = flatten all 10 docs' sentences. Truncate to max_context_chars so we
    don't exceed Qwen's context window for 100s of questions.
    """
    ctx = question_obj["context"]
    titles = ctx["title"]
    sentences_lists = ctx["sentences"]

    context_pieces = []
    for title, sents in zip(titles, sentences_lists):
        joined = " ".join(sents)
        context_pieces.append(f"{title}: {joined}")
    full_context = "\n".join(context_pieces)
    if len(full_context) > max_context_chars:
        full_context = full_context[:max_context_chars] + "..."

    user = (f"Use the context below to answer the question with a short answer "
            f"(typically 1-5 words).\n\n"
            f"Context:\n{full_context}\n\n"
            f"Question: {question_obj['question']}\n\n"
            f"Answer:")
    return user


def apply_chat_template(tokenizer, user_msg: str) -> str:
    """Wrap user message in Qwen's chat template."""
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": user_msg}],
        tokenize=False,
        add_generation_prompt=True,
    )


# =============================================================================
# Answer F1 (squad-style)
# =============================================================================

def normalize_answer(s: str) -> str:
    """Lower, remove punctuation/articles/extra whitespace (SQuAD convention)."""
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)
    def white_space_fix(text):
        return " ".join(text.split())
    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)
    def lower(text):
        return text.lower()
    return white_space_fix(remove_articles(remove_punc(lower(s))))


def answer_f1(prediction: str, gold: str) -> float:
    """SQuAD-style word-level F1."""
    pred_toks = normalize_answer(prediction).split()
    gold_toks = normalize_answer(gold).split()
    if not pred_toks or not gold_toks:
        return 1.0 if pred_toks == gold_toks else 0.0
    common = Counter(pred_toks) & Counter(gold_toks)
    n_same = sum(common.values())
    if n_same == 0:
        return 0.0
    precision = n_same / len(pred_toks)
    recall = n_same / len(gold_toks)
    return 2 * precision * recall / (precision + recall)


# =============================================================================
# Verdict logic
# =============================================================================

def decide_verdict(speedup: float, f1_delta: float) -> str:
    """HP if speedup >= 2.0 AND |f1_delta| <= 0.02.
    HF if speedup < 1.5 OR |f1_delta| > 0.02.
    Otherwise MID.
    """
    if abs(f1_delta) > F1_DELTA_TOLERANCE:
        return "HARD_FAIL"
    if speedup >= HP_SPEEDUP:
        return "HARD_PASS"
    if speedup >= MID_SPEEDUP:
        return "MID"
    return "HARD_FAIL"


# =============================================================================
# Generation + timing
# =============================================================================

def run_generation_pass(
    tokenizer,
    target_model,
    draft_model,
    questions: List[Dict],
    pass_name: str,
    use_speculative: bool,
    max_new_tokens: int,
    progress_jsonl: Path,
) -> List[Dict]:
    """Run greedy decode on `questions`; return list of {qid, predicted, gold, latency_s, n_new_tokens}.

    Streams per-question results to progress_jsonl so a mid-run crash preserves partial work.
    """
    import torch

    results = []
    progress_f = open(progress_jsonl, "a")
    try:
        for i, q in enumerate(questions):
            qid = q["id"]
            gold = q.get("answer", "")  # HotpotQA distractor has gold answer
            prompt_user = build_prompt(q)
            prompt = apply_chat_template(tokenizer, prompt_user)

            inputs = tokenizer(prompt, return_tensors="pt").to(target_model.device)
            n_prompt_tokens = inputs["input_ids"].shape[1]

            gen_kwargs = {
                "max_new_tokens": max_new_tokens,
                "do_sample": False,
                "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
            }
            if use_speculative and draft_model is not None:
                gen_kwargs["assistant_model"] = draft_model

            torch.cuda.synchronize()
            t0 = time.time()
            with torch.inference_mode():
                out = target_model.generate(**inputs, **gen_kwargs)
            torch.cuda.synchronize()
            t1 = time.time()

            n_new = out.shape[1] - n_prompt_tokens
            new_tokens = out[0, n_prompt_tokens:]
            predicted = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            latency = t1 - t0

            row = {
                "qid": qid,
                "predicted": predicted,
                "gold": gold,
                "latency_s": latency,
                "n_new_tokens": int(n_new),
                "tokens_per_sec": (n_new / latency) if latency > 0 else 0.0,
            }
            results.append(row)
            progress_f.write(json.dumps({"pass": pass_name, **row}) + "\n")
            if (i + 1) % 10 == 0:
                progress_f.flush()
                os.fsync(progress_f.fileno())
            if (i + 1) % 25 == 0:
                print(f"  [{pass_name}] q{i+1}/{len(questions)} | "
                      f"latency={latency:.3f}s n_new={n_new} "
                      f"tok/s={row['tokens_per_sec']:.1f}", flush=True)
    finally:
        progress_f.flush()
        os.fsync(progress_f.fileno())
        progress_f.close()
    return results


# =============================================================================
# Main
# =============================================================================

def _emit_failure_metrics(reason: str, elapsed: float):
    """Hardening: write a metrics.json on crash so verdict_handler doesn't see silence."""
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": f"UNKNOWN: script crashed; reason={reason}",
            "elapsed_s": elapsed,
            "summary": f"UNKNOWN: script crashed; reason={reason}",
            "error": reason,
        }
        write_metrics(out_dir, metrics, [metrics])
        print(f"[metrics] FAILURE metrics written to {out_dir / 'metrics.json'}", flush=True)
    except Exception as inner:
        print(f"[FATAL] could not write failure metrics: {inner}", flush=True)


def main():
    print(f"[config] anchor={ANCHOR_NAME} target={TARGET_MODEL} draft={DRAFT_MODEL} "
          f"n_questions={_ARGS.n_questions} max_new_tokens={_ARGS.max_new_tokens}",
          flush=True)
    t0 = time.time()

    try:
        # Step 1: load HotpotQA bridge questions (with warmup)
        all_questions = load_bridge_questions(_ARGS.n_questions)
        if len(all_questions) < WARMUP_QUESTIONS + 10:
            raise RuntimeError(f"Only {len(all_questions)} bridge questions; need at least "
                              f"{WARMUP_QUESTIONS + 10} (warmup + min measurement set)")
        warmup_qs = all_questions[:WARMUP_QUESTIONS]
        eval_qs = all_questions[WARMUP_QUESTIONS:WARMUP_QUESTIONS + _ARGS.n_questions]
        print(f"[data] warmup={len(warmup_qs)} eval={len(eval_qs)}", flush=True)

        # Progress save: questions used (cheap)
        out_dir = get_output_dir(ANCHOR_NAME)
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "eval_questions.json", "w") as f:
            json.dump({
                "n_warmup": len(warmup_qs),
                "n_eval": len(eval_qs),
                "warmup_ids": [q["id"] for q in warmup_qs],
                "eval_ids": [q["id"] for q in eval_qs],
            }, f, indent=2)

        # Step 2: load models
        print(f"[models] loading target ({TARGET_MODEL}) + draft ({DRAFT_MODEL}) in bf16", flush=True)
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(TARGET_MODEL)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token

        target_model = AutoModelForCausalLM.from_pretrained(
            TARGET_MODEL, torch_dtype=torch.bfloat16, device_map="cuda"
        ).eval()
        draft_model = AutoModelForCausalLM.from_pretrained(
            DRAFT_MODEL, torch_dtype=torch.bfloat16, device_map="cuda"
        ).eval()

        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            free_mem, total_mem = torch.cuda.mem_get_info(0)
            print(f"[gpu] {props.name} VRAM total={total_mem/1e9:.1f} GB free={free_mem/1e9:.1f} GB "
                  f"AFTER model load", flush=True)

        progress_jsonl = out_dir / "per_question_latencies.jsonl"
        if progress_jsonl.exists():
            progress_jsonl.unlink()

        # Step 3: warmup (compile kernels, build KV cache shapes; not measured)
        print(f"\n=== Warmup ({len(warmup_qs)} questions; not measured) ===", flush=True)
        _ = run_generation_pass(tokenizer, target_model, None, warmup_qs,
                                 pass_name="warmup_baseline", use_speculative=False,
                                 max_new_tokens=_ARGS.max_new_tokens, progress_jsonl=progress_jsonl)
        _ = run_generation_pass(tokenizer, target_model, draft_model, warmup_qs,
                                 pass_name="warmup_spec", use_speculative=True,
                                 max_new_tokens=_ARGS.max_new_tokens, progress_jsonl=progress_jsonl)

        # Step 4: BASELINE pass (target only)
        print(f"\n=== Baseline pass (target only, {len(eval_qs)} questions) ===", flush=True)
        baseline = run_generation_pass(tokenizer, target_model, None, eval_qs,
                                          pass_name="baseline", use_speculative=False,
                                          max_new_tokens=_ARGS.max_new_tokens,
                                          progress_jsonl=progress_jsonl)

        # Step 5: SPECULATIVE pass (target + draft as assistant)
        print(f"\n=== Speculative pass (target + draft, {len(eval_qs)} questions) ===", flush=True)
        speculative = run_generation_pass(tokenizer, target_model, draft_model, eval_qs,
                                              pass_name="speculative", use_speculative=True,
                                              max_new_tokens=_ARGS.max_new_tokens,
                                              progress_jsonl=progress_jsonl)

        # Step 6: aggregate metrics
        baseline_total_tokens = sum(r["n_new_tokens"] for r in baseline)
        baseline_total_latency = sum(r["latency_s"] for r in baseline)
        spec_total_tokens = sum(r["n_new_tokens"] for r in speculative)
        spec_total_latency = sum(r["latency_s"] for r in speculative)

        baseline_tps = baseline_total_tokens / baseline_total_latency if baseline_total_latency > 0 else 0.0
        spec_tps = spec_total_tokens / spec_total_latency if spec_total_latency > 0 else 0.0
        speedup = (spec_tps / baseline_tps) if baseline_tps > 0 else 0.0

        baseline_f1 = sum(answer_f1(r["predicted"], r["gold"]) for r in baseline) / max(len(baseline), 1)
        spec_f1 = sum(answer_f1(r["predicted"], r["gold"]) for r in speculative) / max(len(speculative), 1)
        f1_delta = spec_f1 - baseline_f1

        # Mean per-question latency too (more direct than aggregated tok/s)
        baseline_mean_latency = baseline_total_latency / max(len(baseline), 1)
        spec_mean_latency = spec_total_latency / max(len(speculative), 1)
        wall_speedup = baseline_mean_latency / spec_mean_latency if spec_mean_latency > 0 else 0.0

        verdict = decide_verdict(speedup=wall_speedup, f1_delta=f1_delta)

        elapsed = time.time() - t0
        summary = (f"{verdict}: wall_speedup={wall_speedup:.2f}x "
                   f"(HP>={HP_SPEEDUP}, MID>={MID_SPEEDUP}); "
                   f"F1_delta={f1_delta:+.4f} (tol +/-{F1_DELTA_TOLERANCE}); "
                   f"baseline tok/s={baseline_tps:.1f}, spec tok/s={spec_tps:.1f}; "
                   f"baseline F1={baseline_f1:.3f}, spec F1={spec_f1:.3f}; "
                   f"n_eval={len(eval_qs)}")
        print(f"\n[VERDICT] {summary}", flush=True)

        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": summary,
            "wall_speedup": wall_speedup,
            "tps_speedup": speedup,
            "baseline_tps": baseline_tps,
            "spec_tps": spec_tps,
            "baseline_mean_latency_s": baseline_mean_latency,
            "spec_mean_latency_s": spec_mean_latency,
            "baseline_f1": baseline_f1,
            "spec_f1": spec_f1,
            "f1_delta": f1_delta,
            "hp_speedup": HP_SPEEDUP,
            "mid_speedup": MID_SPEEDUP,
            "f1_delta_tolerance": F1_DELTA_TOLERANCE,
            "n_eval_questions": len(eval_qs),
            "n_warmup_questions": len(warmup_qs),
            "target_model": TARGET_MODEL,
            "draft_model": DRAFT_MODEL,
            "max_new_tokens": _ARGS.max_new_tokens,
            "baseline_total_tokens_generated": baseline_total_tokens,
            "spec_total_tokens_generated": spec_total_tokens,
            "elapsed_s": elapsed,
            "summary": summary,
        }
        write_metrics(out_dir, metrics, [metrics])
        print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)

    except Exception as exc:
        elapsed = time.time() - t0
        reason = f"{type(exc).__name__}: {exc}"
        print(f"\n[FATAL] {reason}", flush=True)
        import traceback
        traceback.print_exc()
        _emit_failure_metrics(reason, elapsed)
        raise


if __name__ == "__main__":
    if _ARGS.self_test:
        _selftest()
        print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
        sys.exit(0)
    main()
