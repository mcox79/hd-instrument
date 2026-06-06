"""
exp_g5_entity_substitution_kf1_v1 -- Batch G5 (AT-1 adaptive entity-substitution attack) -- CPU.

ROUTING: Batch G Tier-2 (adversarial drill #1). KF-1 paraphrase robustness was confirmed only vs OFF-SHELF MT (designed to
  PRESERVE meaning). The cheapest ADAPTIVE attack swaps a single entity (Lyon for Paris) while keeping all surrounding
  context identical -- changing the FACT while preserving most of the embedding. A KF-1 grounding that keys on context
  would MISS this (the swapped claim still grounds high to the original fact). Synthetic model: claim = bundle(entity_vec,
  context_vec); KB stores true (entity,context) bundles; attack swaps entity, keeps context. KF-1 grounding = max cosine to
  KB. Measures AUC of distinguishing true vs entity-swapped claims (and the drop vs clean random-fabrication AUC). CPU $0.
PRE-REGISTERED: HARD-PASS entity-sub detection AUC drop <= 0.05 vs clean (grounding catches entity swaps). MID 0.05-0.20.
  HARD-FAIL > 0.20 (KF-1 keys on context, misses entity swaps -- needs NLI/entity-aware upgrade).
FORMULA SELF-TESTS (PROT-022): 1. bundle binds entity+context. 2. AUC bounds. 3. swap changes claim.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "g5_entity_substitution_kf1_v1"
W_ENTITY = 0.5   # entity contributes ~half the claim embedding (rest = context); models "8 surrounding bigrams kept"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; N_KB = 400; N_CLAIM = 120; N_ENTITY = 100
else:
    SEEDS = [7, 17, 23]; N = 8192; N_KB = 2000; N_CLAIM = 400; N_ENTITY = 500


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit((g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32))


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def claim(ent, ctx):
    return unit(W_ENTITY * ent + (1 - W_ENTITY) * ctx)


def _selftest():
    g = np.random.default_rng(0); e = rv(1, 256, g)[0]; c = rv(1, 256, g)[0]; cl = claim(e, c)
    assert float(cl @ e) > 0.3 and float(cl @ c) > 0.3, "bundle binds entity+context"
    e2 = rv(1, 256, g)[0]; assert float(claim(e2, c) @ cl) < 0.99, "swap changes claim"
    assert auc([1, 1], [0, 0]) == 1.0, "AUC bounds"
    print("[selftest] PASS: g5-entitysub", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    entities = rv(N_ENTITY, N, g); contexts = rv(N_KB, N, g)
    ent_id = g.integers(0, N_ENTITY, N_KB)
    kb = unit(np.stack([claim(entities[ent_id[i]], contexts[i]) for i in range(N_KB)]))   # true facts
    idx = g.choice(N_KB, N_CLAIM, replace=False)
    real = kb[idx]                                                                          # true claims (in KB)
    # entity-swap attack: same context, DIFFERENT entity
    swapped = unit(np.stack([claim(entities[(ent_id[i] + 1 + g.integers(0, N_ENTITY - 1)) % N_ENTITY], contexts[i]) for i in idx]))
    rand_fab = rv(N_CLAIM, N, g)                                                            # random fabrication (clean baseline)
    def ground(claims):
        return (claims @ kb.T).max(axis=1)
    clean_auc = auc(ground(real), ground(rand_fab))                                         # real vs random fab (easy)
    swap_auc = auc(ground(real), ground(swapped))                                           # real vs entity-swap (hard)
    print("  [seed=%d] clean_AUC=%.3f entity_swap_AUC=%.3f drop=%.3f" % (seed, clean_auc, swap_auc, clean_auc - swap_auc), flush=True)
    return {"seed": seed, "clean_auc": clean_auc, "entity_swap_auc": swap_auc, "drop": clean_auc - swap_auc}


def verdict(ps) -> Tuple[str, str]:
    drop = float(np.mean([p["drop"] for p in ps])); sa = float(np.mean([p["entity_swap_auc"] for p in ps]))
    summary = "clean_AUC=%.3f entity_swap_AUC=%.3f drop=%.3f" % (float(np.mean([p["clean_auc"] for p in ps])), sa, drop)
    if drop <= 0.05:
        return ("HARD_PASS", "HARD_PASS: entity-substitution detection AUC drop <=0.05 -- KF-1 grounding catches entity swaps. " + summary)
    if drop <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: entity-sub degrades grounding (drop 0.05-0.20). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: entity-sub evades grounding (drop>0.20) -- KF-1 keys on context; needs NLI/entity-aware upgrade. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d N_kb=%d w_entity=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_KB, W_ENTITY), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
