"""
exp_chtv_llm_baseline_soundness_gap_gpu_v1.py -- CH-P6: substrate-vs-LLM SOUNDNESS GAP on proof verification -- GPU.

ROUTING: Research-ENDORSED capstone (research_to_exp_dev_PRIORITY_STEER... Anchor 4). Substrate's CHTV verifier + L6-PROOF finder
  are a SOUND find+verify prover (0 false-accepts, precision 1.0, by construction over the checkable typed-derivation graph). This
  cell gives the SAME 24 proof trials to a small instruct LLM (Qwen2.5-0.5B + 1.5B) and measures whether the LLM can match that
  soundness. Substrate-product positioning artifact #21: an LLM has NO checkable ground-truth graph, so it judges dependency
  validity from training-knowledge plausibility and HALLUCINATES (accepts plausible-but-false dependencies) -- it cannot
  guarantee soundness at any scale (arxiv 2401.11817). NO substrate scoring by LLM; the LLM is the BASELINE, substrate is ground truth.

  Trials (built on the laptop's CLEAN graph -> experiments/data/chtv_llm_trials.json; this cell does NOT read substrate atoms,
  avoiding the desktop atom-write race): 12 VALID (real connected derivation chains, all edges true substrate dependencies) +
  12 INVALID (same chains with the LAST dependency replaced by a PLAUSIBLE-but-false math edge). The substrate verifier scores
  these 24/24 correctly (0 false-accepts). The LLM gets each chain as "A depends on B; B depends on C" and answers VALID/INVALID.

PRE-REGISTERED (Research): HARD-PASS the LLM ACCEPTS >= 1/12 INVALID trials as VALID (>=1 hallucinated dependency demonstrates the
  categorical soundness gap; substrate = 0). Report per-model false-accept (hallucination) count + accuracy. MIDDLE: 0 false-accepts
  but LLM accuracy < substrate's 1.0 via false-REJECTS (LLM also rejects valid proofs -> still not a sound matcher). HARD-FAIL:
  LLM matches substrate exactly (0 false-accept AND 0 false-reject on BOTH models) -- would refute the gap. UNKNOWN if model/trials unavailable.
ASCII-only. write_metrics. PROT-020 (import torch). GPU (remote desktop runner). Route via overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "chtv_llm_baseline_soundness_gap_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TRIALS_FP = REPO / "experiments" / "data" / "chtv_llm_trials.json"
MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B")] if SMOKE else [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B"), ("Qwen/Qwen2.5-1.5B-Instruct", "1.5B")]


def _readable(tok: str) -> str:
    return tok.split("/")[-1].replace("_", " ")


def _chain_text(chain) -> str:
    rels = {"DEPENDS_ON": "depends on", "USES": "uses", "INSTANCE_OF": "is an instance of",
            "SPECIALIZES": "specializes", "DEFINED_OVER": "is defined over"}
    return "; ".join("'%s' %s '%s'" % (_readable(s), rels.get(rt, "relates to"), _readable(t)) for s, rt, t in chain)


def _parse(out: str) -> str:
    # whole-word matches only: "INVALID" contains "VALID", so use \b and capture the (IN)? prefix; last verdict wins.
    toks = re.findall(r"\b(IN)?VALID\b", out.upper())
    if not toks:
        return "?"
    return "invalid" if toks[-1] == "IN" else "valid"


def _selftest():
    assert _parse("... so the answer is INVALID") == "invalid"
    assert _parse("VALID") == "valid"
    assert _parse("This is INVALID because... actually VALID") == "valid"  # last token wins
    assert "depends on" in _chain_text([["A", "DEPENDS_ON", "B"]])
    print("[selftest] PASS: chtv_llm_baseline_soundness_gap_gpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] torch/transformers: %s" % e, flush=True); sys.exit(1)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
print("[device] %s" % DEV, flush=True)


def run() -> Dict:
    if not TRIALS_FP.exists():
        return {"error": "trials_missing", "note": str(TRIALS_FP)}
    trials = json.load(open(TRIALS_FP, encoding="utf-8"))["trials"]
    if SMOKE: trials = trials[:6]
    n_valid = sum(1 for t in trials if t["label"] == "valid"); n_invalid = sum(1 for t in trials if t["label"] == "invalid")
    SYS = ("You verify mathematical/conceptual derivations. A derivation is VALID only if EVERY stated dependency is a true, "
           "real prerequisite relationship. If even one dependency is false or fabricated, it is INVALID. Answer with exactly "
           "one word: VALID or INVALID.")
    per_model = []
    for model_id, label in MODELS:
        try:
            tok = AutoTokenizer.from_pretrained(model_id)
            mdl = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
        except Exception as e:
            per_model.append({"model": label, "error": str(e)[:120]}); continue
        print("[model] loaded %s on %s" % (model_id, DEV), flush=True)
        fa = 0; fr = 0; correct = 0; unparsed = 0; rows = []
        for t in trials:
            prompt = ("Derivation: %s.\nIs this derivation VALID (all dependencies true) or INVALID (at least one false)?" % _chain_text(t["chain"]))
            msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": prompt}]
            p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            ins = tok(p, return_tensors="pt").to(DEV)
            with torch.no_grad():
                o = mdl.generate(**ins, max_new_tokens=8, do_sample=False, pad_token_id=tok.eos_token_id)
            ans = _parse(tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True))
            gt = t["label"]
            if ans == "?": unparsed += 1
            elif ans == gt: correct += 1
            if gt == "invalid" and ans == "valid": fa += 1          # FALSE-ACCEPT = hallucinated a false dependency as valid
            if gt == "valid" and ans == "invalid": fr += 1          # false-reject
            rows.append({"gt": gt, "llm": ans})
        acc = round(correct / len(trials), 4)
        print("  [%s] accuracy=%.4f | FALSE-ACCEPTS (hallucinated invalid->valid)=%d/%d | false-rejects=%d/%d | unparsed=%d" % (
            label, acc, fa, n_invalid, fr, n_valid, unparsed), flush=True)
        per_model.append({"model": label, "accuracy": acc, "false_accepts": fa, "n_invalid": n_invalid,
                          "false_rejects": fr, "n_valid": n_valid, "unparsed": unparsed})
        del mdl
        if DEV == "cuda": torch.cuda.empty_cache()
    return {"per_model": per_model, "n_trials": len(trials), "n_valid": n_valid, "n_invalid": n_invalid,
            "substrate_false_accepts": 0, "substrate_accuracy": 1.0}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", "")))
    pm = [m for m in r["per_model"] if "error" not in m]
    if not pm:
        return ("UNKNOWN", "UNKNOWN: no model ran. " + str(r["per_model"]))
    max_fa = max(m["false_accepts"] for m in pm)
    any_exact = any(m["false_accepts"] == 0 and m["false_rejects"] == 0 for m in pm)
    all_exact = all(m["false_accepts"] == 0 and m["false_rejects"] == 0 for m in pm)
    s = "substrate: 0 false-accepts / accuracy 1.0. LLM(s): %s | (n_valid=%d n_invalid=%d)" % (
        [{m["model"]: {"acc": m["accuracy"], "false_accept": m["false_accepts"], "false_reject": m["false_rejects"]}} for m in pm], r["n_valid"], r["n_invalid"])
    if max_fa >= 1:
        return ("HARD_PASS", "HARD_PASS: the LLM HALLUCINATES -- accepts >=1 INVALID derivation (false dependency) as VALID (max false-accepts=%d), while the substrate verifier is sound (0 false-accepts). Empirical substrate-vs-LLM SOUNDNESS GAP: the LLM cannot guarantee proof soundness (no checkable ground truth); the substrate can (typed-derivation graph). Capstone of the prover narrative. " % max_fa + s)
    if not all_exact:
        return ("MIDDLE_BAND", "MIDDLE_BAND: LLM made 0 false-accepts but does NOT match the substrate exactly (false-rejects present -- rejects valid proofs). LLM is conservative-but-imperfect, not a sound matcher. " + s)
    return ("HARD_FAIL", "HARD_FAIL: the LLM matched the substrate exactly (0 false-accept AND 0 false-reject on all models) -- no soundness gap demonstrated on these 24 trials (consider harder/more-plausible fabrications). " + s)


print("[config] anchor=%s mode=%s models=%s" % (ANCHOR_NAME, RUN_MODE, [m[1] for m in MODELS]), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
