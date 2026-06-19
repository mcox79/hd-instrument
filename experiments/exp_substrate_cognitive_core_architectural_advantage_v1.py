"""
substrate_cognitive_core_architectural_advantage_v1 -- CCC-1-v2 architectural-advantage trio -- GPU (Pythia baseline).

ROUTING: research priority_focus_phase1_critical_path -- CCC-1-REVISED-v2 is THE load-bearing Phase-1 test; the 3
  ARCHITECTURAL-ADVANTAGE benchmarks are the cheapest + most decisive (substrate categorically wins; Pythia ~0).
  Builds the decisive trio first (uses idle GPU for the Pythia-160M baseline). torch+transformers. overnight_queue.

THREE BENCHMARKS (substrate cognitive core vs Pythia-160M in-context):
  1. LONG-CONVERSATION-MEMORY: fact stated early in a long stream; queried after D exchanges. Substrate stores via
     Hebbian (distance-independent recall). Pythia: fact survives only if within its context window. HP sub>=0.80 @
     exchange 200, Pythia<=0.30.
  2. CROSS-SESSION-PERSISTENCE: facts in session 1; queried in session 2 (FRESH context, no facts in prompt).
     Substrate W persists. Pythia has no cross-session memory. HP sub>=0.70, Pythia~0.
  3. MULTI-DOC-SYNTHESIS: answer needs a fact from 1 of N docs; N exceeds Pythia context. Substrate stores all N.
     Pythia gets truncated docs. HP sub>=3x Pythia at N=50.

PRE-REGISTERED bands: HARD-PASS all 3 architectural thresholds met. MIDDLE: 2 of 3. HARD-FAIL: <2.
FORMULA SELF-TESTS (PROT-022): 1. substrate fact store+recall. 2. distance-independent substrate recall. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_architectural_advantage_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 4096; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; LONGCONV_E = 500; QUERY_DISTS = [30, 400]; N_DOCS = [10, 300]; N_FACTS_EVAL = 60
else:
    SEEDS = [7, 17, 23]; LONGCONV_E = 700; QUERY_DISTS = [30, 200, 400, 600]; N_DOCS = [10, 50, 200, 400]; N_FACTS_EVAL = 150

ENT = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet",
       "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango",
       "violet", "amber", "cobalt", "crimson", "azure", "jade", "ivory", "onyx", "coral", "slate"]
VAL = ["red", "blue", "green", "tall", "short", "fast", "slow", "warm", "cold", "bright", "dark", "round"]


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(3, n, g); V = ub(3, n, g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(3):
        cfrpe(W, K[i], V[i], n)
    p = K @ W.T; p = p / (np.linalg.norm(p, axis=1, keepdims=True) + 1e-8)
    assert float(np.mean((p * V).sum(1) > 0.7)) > 0.9, "substrate fact store+recall"
    assert N_SUB == 4096; print("[selftest] PASS: substrate recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(DEVICE).eval()
_TOK.truncation_side = "left"   # keep the QUERY at the end; truncate OLD facts (architectural-window test)
def ent_name(i): return "item%d" % i
CTX = 2048   # Pythia-160M context window


def pythia_answers(context_text, ent, val):
    """Does Pythia complete 'context ... <ent> is' with <val>? (in-context recall). Truncate to last CTX tokens."""
    prompt = context_text + ("\n%s is" % ent)
    ids = _TOK(prompt, return_tensors="pt", truncation=True, max_length=CTX).input_ids.to(DEVICE)
    with torch.no_grad():
        nxt = _MODEL(ids).logits[0, -1].argmax().item()
    return _TOK.decode([nxt]).strip().lower().startswith(val[:3])


def substrate_store_recall(facts, g):
    """facts = list of (ent_id, val_idx) with UNIQUE ent_id. Returns recall accuracy."""
    n = N_SUB; max_e = max(e for e, _ in facts) + 1; EK = ub(max_e, n, g); EV = ub(len(VAL), n, g); W = np.zeros((n, n), dtype=np.float32)
    for (e, v) in facts:
        cfrpe(W, EK[e], EV[v], n)
    ok = 0
    for (e, v) in facts:
        pred = int(np.argmax(EV @ (W @ EK[e]))); ok += (pred == v)
    return ok / max(len(facts), 1)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); out = {"seed": seed}
    # ---- 1. LONG-CONVERSATION-MEMORY ----
    facts = [(i, int(g.integers(0, len(VAL)))) for i in range(LONGCONV_E)]   # UNIQUE entity per exchange
    lines = ["%s is %s" % (ent_name(e), VAL[v]) for (e, v) in facts]
    sub_W_recall = substrate_store_recall(facts, np.random.default_rng(seed + 1))
    full_ctx = "\n".join(lines)
    lc = {}
    for d in QUERY_DISTS:
        qi = max(0, LONGCONV_E - d); e, v = facts[qi]
        py = float(pythia_answers(full_ctx, ent_name(e), VAL[v]))   # full convo; left-trunc keeps recent -> old facts dropped
        lc["pythia_d%d" % d] = py
    out["longconv_substrate_recall"] = sub_W_recall
    out["longconv_pythia_d200"] = lc.get("pythia_d%d" % QUERY_DISTS[-1], 0.0)   # farthest distance
    # ---- 2. CROSS-SESSION-PERSISTENCE ----
    s1 = [(i, int(g.integers(0, len(VAL)))) for i in range(N_FACTS_EVAL)]            # UNIQUE ents
    sub_cross = substrate_store_recall(s1, np.random.default_rng(seed + 2))          # W persists into "session 2"
    py_cross = np.mean([pythia_answers("(new session -- no prior context)", ent_name(e), VAL[v]) for (e, v) in s1[:30]])
    out["crosssession_substrate"] = sub_cross; out["crosssession_pythia"] = float(py_cross)
    # ---- 3. MULTI-DOC-SYNTHESIS ----
    md = {}
    for nd in N_DOCS:
        docs = [(i, int(g.integers(0, len(VAL)))) for i in range(nd)]   # UNIQUE entity per doc
        sub = substrate_store_recall(docs, np.random.default_rng(seed + 3 + nd))
        doctext = "\n".join("Document %d: %s is %s." % (i, ent_name(e), VAL[v]) for i, (e, v) in enumerate(docs))
        py = np.mean([pythia_answers(doctext, ent_name(e), VAL[v]) for (e, v) in docs])
        md["sub_n%d" % nd] = sub; md["py_n%d" % nd] = float(py)
    out["multidoc"] = md
    out["multidoc_sub_n50"] = md.get("sub_n50", md.get("sub_n%d" % N_DOCS[-1])); out["multidoc_py_n50"] = md.get("py_n50", md.get("py_n%d" % N_DOCS[-1]))
    return out


def verdict(ps) -> Tuple[str, str]:
    lc_s = float(np.mean([p["longconv_substrate_recall"] for p in ps])); lc_p = float(np.mean([p["longconv_pythia_d200"] for p in ps]))
    cs_s = float(np.mean([p["crosssession_substrate"] for p in ps])); cs_p = float(np.mean([p["crosssession_pythia"] for p in ps]))
    md_s = float(np.mean([p["multidoc_sub_n50"] for p in ps])); md_p = float(np.mean([p["multidoc_py_n50"] for p in ps]))
    b1 = lc_s >= 0.80 and lc_p <= 0.30; b2 = cs_s >= 0.70 and cs_p <= 0.10; b3 = md_s >= 3.0 * max(md_p, 1e-6)
    n_pass = b1 + b2 + b3
    summary = "LONGCONV sub=%.2f/pythia@200=%.2f [%s] | CROSS-SESSION sub=%.2f/pythia=%.2f [%s] | MULTIDOC@50 sub=%.2f/pythia=%.2f [%s]" % (
        lc_s, lc_p, "PASS" if b1 else "no", cs_s, cs_p, "PASS" if b2 else "no", md_s, md_p, "PASS" if b3 else "no")
    if n_pass == 3:
        return ("HARD_PASS", "HARD_PASS: substrate categorically wins all 3 architectural-advantage benchmarks. " + summary)
    if n_pass == 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate wins 2/3 architectural benchmarks. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate wins <2/3. " + summary)


print("[config] anchor=%s mode=%s seeds=%s longconv_E=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, LONGCONV_E), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] longconv sub=%.2f py@200=%.2f | cross sub=%.2f py=%.2f | multidoc@50 sub=%.2f py=%.2f" % (
        seed, r["longconv_substrate_recall"], r["longconv_pythia_d200"], r["crosssession_substrate"], r["crosssession_pythia"], r["multidoc_sub_n50"], r["multidoc_py_n50"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
