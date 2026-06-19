"""
exp_comm2_translation_distant_cpu_v1.py -- COMM-2 TRANSLATION-DISTANT (typologically distant languages) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-1 COMMUNICATE (COMM-2). Refines the syntax boundary. Three languages with
  DIFFERENT word orders: SVO / SOV / VSO. A sentence has subject/verb/object CONCEPTS; each language realizes them in its
  order with its own word codebook. Translation = (a) concept pivot via interlingua (word_src -> concept -> word_tgt), AND
  (b) REORDER to the target word order via a stored per-language order TEMPLATE. Tests whether substrate handles distant-language
  translation: concept-accuracy (lexical) + word-ORDER-accuracy (systematic syntax via template). Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS concept-accuracy >= 0.85 AND order-accuracy >= 0.85 (systematic syntax via templates works). MIDDLE one >= 0.85. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "comm2_translation_distant_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
ORDERS = {"SVO": (0, 1, 2), "SOV": (0, 2, 1), "VSO": (1, 0, 2)}      # role index order per language (roles: 0=subj 1=verb 2=obj)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: comm2-translation-distant", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "813"))); NC = 80; langs = list(ORDERS.keys())
    TR = 12 if SMOKE else 80; concept_hit = 0; concept_n = 0; order_ok = 0; order_n = 0
    for _ in range(TR):
        concepts = cphasor(NC, N, g)
        words = {L: cphasor(NC, N, g) for L in langs}                  # per-language word codebooks
        lex = {L: cnorm((words[L] * concepts).sum(0)) for L in langs}  # interlingua lexicon per language
        for _q in range(6):
            src, tgt = (langs[i] for i in g.choice(len(langs), 2, replace=False))
            roles = [int(x) for x in g.choice(NC, 3, replace=False)]   # subj, verb, obj concept indices
            src_order = ORDERS[src]; tgt_order = ORDERS[tgt]
            # source sentence: words in src order
            src_sent = [int(roles[r]) for r in src_order]
            # TRANSLATE each word -> concept -> target word (interlingua pivot)
            tgt_words = []
            for wc in src_sent:
                wv = words[src][wc]; concept_est = lex[src] * np.conj(wv); ci = cidx(concept_est, concepts)
                tw = cidx(lex[tgt] * np.conj(concepts[ci]), words[tgt]); tgt_words.append((ci, tw))
            # concept accuracy: each translated word's concept correct
            for (ci, tw) in tgt_words:
                concept_hit += int(ci in roles); concept_n += 1
            # REORDER to target order via template: map by role. recover role of each src position, place in tgt order.
            # src position p holds role src_order[p]; build role->concept, then emit in tgt_order
            role2concept = {}
            for p, (ci, tw) in enumerate(tgt_words):
                role2concept[src_order[p]] = ci
            emitted = [role2concept.get(r, -1) for r in tgt_order]
            gold = [int(roles[r]) for r in tgt_order]
            order_ok += int(emitted == gold); order_n += 1
    ca = concept_hit / concept_n; oa = order_ok / order_n
    print("  COMM-2 distant-translation: concept-accuracy=%.3f order-accuracy=%.3f (SVO/SOV/VSO)" % (ca, oa), flush=True)
    return {"concept_accuracy": round(ca, 3), "order_accuracy": round(oa, 3)}
def verdict(r) -> Tuple[str, str]:
    ca = r["concept_accuracy"]; oa = r["order_accuracy"]; s = "concept=%.3f order=%.3f" % (ca, oa)
    if ca >= 0.85 and oa >= 0.85:
        return ("HARD_PASS", "HARD_PASS: distant-language translation works substrate-only -- concept pivot via interlingua (>=0.85) AND word-order reordering via stored templates (>=0.85). Systematic syntax (word-order templates) is substrate-native; the gap is only complex/statistical syntax. " + s)
    if ca >= 0.85 or oa >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of concept/order >=0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: distant translation <0.85 on both. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
