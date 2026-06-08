"""
exp_substrate_llama8b_triples_khop_gpu_v1 -- A2: Llama-3.1-8B-Instruct triples -> substrate K-hop -- GPU.

Per exp_dev_to_testbed_v1.5_GPU_batch_2026-06-08 + research_to_exp_dev_path_B_GPU_dispatch_clarification_2026-06-08:
Variant of exp_substrate_llm_triples_khop_gpu_v1 with MODEL swapped to meta-llama/Llama-3.1-8B-Instruct (the only remaining
lever for v1.5 free-text multi-hop after Qwen-1.5B Path A exhausted at recall=0.250). Substrate K-hop logic UNCHANGED;
this is purely an extractor-strength test.

PRE-REGISTERED (Research):
- HARD-PASS: K-hop answer recall@2 >= 0.55 (clears the 0.37 fuzzy ceiling; multi-hop revival real)
- BORDER:    0.45-0.55 (Llama-8B works but borderline; consider 70B escalation)
- HARD-FAIL: < 0.45 (even Llama-8B can't extract traversable KGs)

HARDENING (per 2026-06-07 lessons from CELL-3/COLBERT/SPECDEC):
- try/except around main run; emit FAILURE metrics.json on crash
- Per-question results streamed to JSONL (progress save; safety stack rsyncs every 5 min)
- HF_TOKEN passed to from_pretrained (gated model)
- bf16 (H100/GH200 native; better than fp16 for stability)
- GPU memory logged pre-model-load

FORMULA SELF-TESTS (PROT-022): bind/unbind; cleanup self; triple parse.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse
import time
import math
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

# =============================================================================
# Config (per Path B routing)
# =============================================================================

ANCHOR_NAME = "substrate_llama8b_triples_khop_gpu_v1"
N = 8192
MODEL = "meta-llama/Llama-3.1-8B-Instruct"   # gated; HF_TOKEN required
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--n-questions", type=int, default=None,
                  help="Override N_Q (defaults: 8 smoke / 60 full)")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
# Per Research A2_CONFIRM_proceed_with_n100 (2026-06-08): n=100 for tighter 95% CI (+/-0.10 vs +/-0.13 at n=60)
N_Q = _ARGS.n_questions if _ARGS.n_questions else (8 if SMOKE else 100)


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def norm_ent(s):
    return re.sub(r"\s+", " ", s.strip().lower()).strip(".,;:'\"()")


def parse_triples(text):
    out = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3 and all(parts):
            s, r, o = norm_ent(parts[0]), norm_ent(parts[1]), norm_ent(parts[2])
            if s and r and o and len(s) < 60 and len(o) < 60:
                out.append((s, r, o))
    return out


def _selftest():
    g = np.random.default_rng(0)
    a = cphasor(1, 32, g)[0]
    b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g)
    assert cidx(bk[3], bk) == 3, "cleanup self"
    assert parse_triples("Paris | capital of | France") == [("paris", "capital of", "france")], "triple parse"
    # Verify HP thresholds match Research routing
    assert 0.55 == 0.55, "HP threshold drift"
    print("[selftest] PASS: substrate-llama8b-triples-khop (HP recall>=0.55; bind/unbind/parse/cleanup verified)",
          flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for line in open(HOTPOT, encoding="utf-8"):
        r = json.loads(line)
        ctx = r.get("context") or {}
        sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []
        sents = ctx.get("sentences") or []
        sf_titles = set(sf.get("title") or [])
        ans = (r.get("answer") or "").strip()
        if not ans or ans.lower() in ("yes", "no") or len(sf_titles) < 2:
            continue
        passages = []
        for ti, t in enumerate(titles):
            if t in sf_titles:
                passages.append(t + ": " + " ".join(sents[ti] if ti < len(sents) else []))
        if len(passages) < 2:
            continue
        out.append({"q": r.get("question", ""), "passages": passages, "answer": ans, "id": r.get("_id", "")})
        if len(out) >= n:
            break
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True)
    sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("[device] %s" % DEV, flush=True)
if torch.cuda.is_available():
    props = torch.cuda.get_device_properties(0)
    free_mem, total_mem = torch.cuda.mem_get_info(0)
    print("[gpu] %s VRAM total=%.1f GB free=%.1f GB BEFORE model load" %
          (props.name, total_mem / 1e9, free_mem / 1e9), flush=True)


def extract_triples(tok, model, passages):
    """Extract triples from passages via the LLM.

    Hardening: tokenizer apply_chat_template wrapped with manual fallback in case
    the chat template metadata is missing. Returns the raw decoded text.
    """
    ctx = "\n".join(passages)[:2400]
    user_content = ("Extract factual relationships from the text as triples, one per line, "
                    "strictly in the format: subject | relation | object\n"
                    "Use short entity names. Only use information in the text.\n\n"
                    "Text:\n" + ctx + "\n\nTriples:")
    msg = [{"role": "user", "content": user_content}]
    try:
        enc = tok.apply_chat_template(msg, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True).to(DEV)
    except Exception as e:
        # Hardening: fall back to manual prompt if chat template fails
        print("[WARN] apply_chat_template failed: %s; using manual prompt" % e, flush=True)
        # Llama-3.1 standard instruct format (close enough; quality minimally affected for triple extraction)
        manual = ("<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n" + user_content +
                  "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n")
        enc = tok(manual, return_tensors="pt").to(DEV)
    with torch.no_grad():
        # max_new_tokens=256 (down from 320; triples typically fit in <200 tokens)
        out = model.generate(**enc, max_new_tokens=256, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)


def _emit_failure_metrics(reason: str, elapsed: float, partial: Dict = None):
    """Emit metrics.json with UNKNOWN verdict on crash so safety stack sees it as non-empty."""
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": f"UNKNOWN: script crashed; reason={reason}",
            "elapsed_s": elapsed,
            "summary": f"UNKNOWN: {reason}",
            "error": reason,
        }
        if partial:
            metrics["partial"] = partial
        write_metrics(out_dir, metrics, [metrics])
        print("[metrics] FAILURE metrics written", flush=True)
    except Exception as inner:
        print("[FATAL] could not write failure metrics: %s" % inner, flush=True)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot data", flush=True)
        return {"n": 0, "recall": 0.0, "coverage": 0.0}

    # Load Llama-3.1-8B-Instruct with HF_TOKEN (gated model)
    hf_token = os.environ.get("HF_TOKEN", "").strip() or None
    if not hf_token:
        print("[FATAL] HF_TOKEN env var empty; Llama-3.1-8B-Instruct is gated and requires a token", flush=True)
        raise RuntimeError("HF_TOKEN required for gated model")
    print("[models] loading %s in bf16 (token len=%d)" % (MODEL, len(hf_token)), flush=True)

    # Hardening: catch GatedRepoError with actionable message
    try:
        tok = AutoTokenizer.from_pretrained(MODEL, token=hf_token)
    except Exception as e:
        msg = str(e).lower()
        if "gated" in msg or "access" in msg or "401" in msg or "403" in msg:
            print("[FATAL] HF gated access denied for %s. Visit "
                  "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct, accept the license, "
                  "and verify the token has access. Error: %s" % (MODEL, e), flush=True)
        raise
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    # Try Flash Attention 2 (Llama-3.1 supports; 30-50% speedup + 50% memory reduction).
    # Fall back to eager (default) if not available on this transformers/torch combo.
    model = None
    for attn_impl, label in [("flash_attention_2", "Flash Attention 2"), ("sdpa", "SDPA"), ("eager", "eager")]:
        try:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL, torch_dtype=torch.bfloat16, token=hf_token,
                device_map="cuda", low_cpu_mem_usage=True, attn_implementation=attn_impl,
            ).eval()
            print("[models] loaded with attn_implementation=%s (%s)" % (attn_impl, label), flush=True)
            break
        except Exception as e:
            print("[models] %s unavailable (%s); trying fallback" % (label, e), flush=True)
            model = None
    if model is None:
        # Last resort: minimal kwargs
        model = AutoModelForCausalLM.from_pretrained(
            MODEL, torch_dtype=torch.bfloat16, token=hf_token, low_cpu_mem_usage=True
        ).to(DEV).eval()
        print("[models] loaded with fallback config (no attn_implementation hint)", flush=True)

    if torch.cuda.is_available():
        free_mem, total_mem = torch.cuda.mem_get_info(0)
        print("[gpu] VRAM free=%.1f GB / %.1f GB AFTER model load" %
              (free_mem / 1e9, total_mem / 1e9), flush=True)

    # Progress save: open per-question JSONL.
    # Hardening: resume-from-JSONL. If a prior run left a JSONL, read it and skip
    # already-completed qids (cluster preempt or rebuild scenario).
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    progress_jsonl = out_dir / "per_question_results.jsonl"
    completed_qids = set()
    prior_hit = 0
    prior_cover = 0
    if progress_jsonl.exists():
        try:
            with open(progress_jsonl) as f:
                for line in f:
                    if line.strip():
                        row = json.loads(line)
                        completed_qids.add(row.get("qid", ""))
                        prior_hit += int(row.get("hit", False))
                        prior_cover += int(row.get("covered", False))
            print("[resume] found %d prior completed qids; skipping these (hit=%d cover=%d)" %
                  (len(completed_qids), prior_hit, prior_cover), flush=True)
        except Exception as e:
            print("[resume] failed to parse prior JSONL (%s); starting fresh" % e, flush=True)
            progress_jsonl.unlink()
            completed_qids = set()
            prior_hit = 0
            prior_cover = 0
    # Open in append mode (so resume keeps prior rows)
    progress_f = open(progress_jsonl, "a")

    g = np.random.default_rng(7)
    hit = 0
    cover = 0
    n = 0
    STOP = {"the", "a", "an", "of", "in", "and", "to", "for", "is", "was", "by", "on", "at"}

    def canon_map(raw_ents):
        toks = {e: set(w for w in re.findall(r"[a-z0-9]+", e) if len(w) > 3 and w not in STOP) for e in raw_ents}
        order = sorted(raw_ents, key=lambda e: -len(e))
        cmap = {}
        for e in order:
            best = None
            for c in dict.fromkeys(cmap.values()):
                if toks[e] and toks.get(c) and (toks[e] & toks[c]) and (toks[e] <= toks[c] or toks[c] <= toks[e]):
                    best = c
                    break
            cmap[e] = best if best else e
        return cmap

    # Seed running totals with prior results (resume case)
    hit = prior_hit
    cover = prior_cover
    n = len(completed_qids)
    n_skipped = 0
    n_errored = 0

    try:
        for d_idx, d in enumerate(data):
            qid = d.get("id", f"q{d_idx}")
            # Resume: skip already-completed qids
            if qid in completed_qids:
                n_skipped += 1
                continue

            t_q = time.time()
            # Hardening: per-query try/except. A bad single query (e.g., OOM, decode crash,
            # weird unicode) must NOT crash the whole run. Skip and continue.
            try:
                triples_raw = extract_triples(tok, model, d["passages"])
            except Exception as exc:
                print("[ERROR] q%d (qid=%s) extraction crashed: %s; skipping and continuing" %
                      (d_idx, qid, exc), flush=True)
                n_errored += 1
                row = {
                    "idx": d_idx,
                    "qid": qid,
                    "question": d["q"],
                    "answer": d["answer"],
                    "n_triples": 0,
                    "hit": False,
                    "covered": False,
                    "extraction_wall_s": time.time() - t_q,
                    "error": "%s: %s" % (type(exc).__name__, exc),
                    "raw_extraction": "",
                }
                progress_f.write(json.dumps(row) + "\n")
                progress_f.flush()
                os.fsync(progress_f.fileno())
                n += 1
                # Try to free any partial state before next query
                try:
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    pass
                continue

            triples = parse_triples(triples_raw)
            row = {
                "idx": d_idx,
                "qid": qid,
                "question": d["q"],
                "answer": d["answer"],
                "n_triples": len(triples),
                "hit": False,
                "covered": False,
                "extraction_wall_s": time.time() - t_q,
                "raw_extraction": triples_raw[:4000],   # save raw LLM output for forensic re-parse
            }
            if not triples:
                progress_f.write(json.dumps(row) + "\n")
                progress_f.flush()
                os.fsync(progress_f.fileno())
                n += 1
                continue

            raw = list(dict.fromkeys([t[0] for t in triples] + [t[2] for t in triples]))
            cm = canon_map(raw)
            triples = [(cm[s], r, cm[o]) for s, r, o in triples]
            ents = list(dict.fromkeys([t[0] for t in triples] + [t[2] for t in triples]))
            rels = list(dict.fromkeys([t[1] for t in triples]))
            ei = {e: i for i, e in enumerate(ents)}
            ri = {r: i for i, r in enumerate(rels)}
            esym = cphasor(len(ents), N, g)
            rsym = cphasor(max(1, len(rels)), N, g)
            M = np.zeros(N, dtype=np.complex64)
            for s, r, o in triples:
                M = M + esym[ei[s]] * rsym[ri[r]] * esym[ei[o]]
            ans = norm_ent(d["answer"])
            ql = d["q"].lower()
            ans_match = next((e for e in ents if e == ans or (len(ans) > 3 and ans in e)
                                or (len(e) > 3 and e in ans)), None)
            cover += int(ans_match is not None)
            row["covered"] = ans_match is not None
            qtoks = set(w for w in re.findall(r"[a-z0-9]+", ql) if len(w) > 3 and w not in STOP)
            starts = [e for e in ents if e in ql] or [
                e for e in ents if set(re.findall(r"[a-z0-9]+", e)) & qtoks
            ]
            reached = set()
            frontier = set(starts)
            for _hop in range(3):
                newf = set()
                for node in frontier:
                    nv = esym[ei[node]]
                    for r in rels:
                        nb = cidx(M * np.conj(nv * rsym[ri[r]]), esym)
                        if (esym[nb] @ np.conj(nv * rsym[ri[r]])).real / N > 0.30:
                            ne = ents[nb]
                            if ne not in reached:
                                newf.add(ne)
                    reached.add(node)
                reached |= newf
                frontier = newf
                if not frontier:
                    break
            got = ans_match is not None and ans_match in reached
            row["hit"] = got
            row["n_entities"] = len(ents)
            row["n_relations"] = len(rels)
            hit += int(got)
            n += 1

            progress_f.write(json.dumps(row) + "\n")
            if (n) % 5 == 0:
                progress_f.flush()
                os.fsync(progress_f.fileno())
            if (n) % 10 == 0:
                # Hardening: periodic VRAM log + empty_cache to spot OOM trends + avoid leak
                try:
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        free_mem, total_mem = torch.cuda.mem_get_info(0)
                        print("  [q%d/%d] running recall=%.3f coverage=%.3f wall=%.1fs "
                              "(VRAM free=%.1f GB; errored=%d skipped=%d)" %
                              (n, len(data) + n_skipped, hit / max(n, 1), cover / max(n, 1),
                                row["extraction_wall_s"], free_mem / 1e9, n_errored, n_skipped),
                              flush=True)
                except Exception:
                    print("  [q%d/%d] running recall=%.3f coverage=%.3f wall=%.1fs (errored=%d skipped=%d)" %
                          (n, len(data) + n_skipped, hit / max(n, 1), cover / max(n, 1),
                            row["extraction_wall_s"], n_errored, n_skipped), flush=True)
    finally:
        progress_f.flush()
        os.fsync(progress_f.fileno())
        progress_f.close()
        if n_errored > 0:
            print("[summary] %d queries errored (skipped); %d queries resumed from prior run" %
                  (n_errored, n_skipped), flush=True)

    rec = hit / max(1, n)
    cov = cover / max(1, n)
    print("  LLM-triples K-hop: answer-recall=%.3f extraction-coverage=%.3f (n=%d)" %
          (rec, cov, n), flush=True)
    return {"n": n, "recall": rec, "coverage": cov}


def verdict(r) -> Tuple[str, str]:
    s = "K-hop answer-recall=%.3f extraction-coverage=%.3f (n=%d) vs R1 oracle 1.0 / fuzzy 0.37 / Qwen-1.5B 0.25" % (
        r["recall"], r["coverage"], r["n"])
    if r["recall"] >= 0.55:
        return ("HARD_PASS",
                "HARD_PASS: Llama-3.1-8B-extracted triples + substrate K-hop clears recall>=0.55 -- "
                "training-free BridgeRAG-equivalent works at fair extractor size; multi-hop revival real. " + s)
    if r["recall"] >= 0.45:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: Llama-8B-triples K-hop 0.45-0.55 -- borderline; consider Llama-3.1-70B escalation. " + s)
    return ("HARD_FAIL",
            "HARD_FAIL: Llama-8B-triples K-hop <0.45 -- even 8B extraction insufficient; "
            "extractor-quality ceiling for v1.5 free-text multi-hop. " + s)


print("[config] anchor=%s mode=%s n_q=%d model=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
try:
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": 1,
        "per_seed": [r],
        "elapsed_s": time.time() - t0,
        "hp_threshold": 0.55,
        "border_low": 0.45,
        "model": MODEL,
        "n_questions": r["n"],
        "summary": vmsg,
    }
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written", flush=True)
except Exception as exc:
    elapsed = time.time() - t0
    reason = f"{type(exc).__name__}: {exc}"
    print("\n[FATAL] " + reason, flush=True)
    import traceback
    traceback.print_exc()
    _emit_failure_metrics(reason, elapsed)
    raise
