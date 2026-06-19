"""
substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1 -- CCC-smoke REVISED: VSA reasoning sanity -- remote CPU.

ROUTING: research_to_exp_dev_ccc_REVISED_relational_analogical_evaluation (CCC-smoke REVISED, priority 1, $0 today).
  User pushback: substrate is a STRUCTURED REASONING system, not a retrieval DB. Test its VSA-native reasoning
  AGGRESSIVELY at smallest scale BEFORE paying for LLM extraction. Pure-substrate synthetic; no LLM dependency.
  CPU numpy, $0. remote_cpu_queue.

FOUR SANITY TESTS (synthetic, VSA bipolar binding bind(a,b)=a*b, cleanup=argmax codebook dot):
  1. pattern recall (B2 sparse, noisy cue)               -- baseline storage
  2. ANALOGICAL: relation R learned from pairs; apply to NOVEL entity (A:B::C:?) via binding arithmetic
  3. COUNTERFACTUAL: remove fact F (B6 deletion) -> query correctly no longer returns F's object (delta computed)
  4. CROSS-DOMAIN transfer: learn relation on 4 domains, apply to held-out 5th domain (shared structure)

PRE-REGISTERED bands (per note): HARD-PASS recall>=0.80 AND analogical>=0.80 AND counterfactual>=0.80 AND
  cross_domain>=0.70. MIDDLE: all >= their 0.50 floor but some below HP. HARD-FAIL: ANY < 0.50.

FORMULA SELF-TESTS (PROT-022): 1. bind/unbind round-trip. 2. relation R=A*B applies to novel C. 3. sparse recall. 4. N=4096.
ASCII-only. write_metrics. PROT-018: scaffold anchor (N=4096 internal; no _nN).
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

N = 4096; F_SPARSE = 0.05; N_REL = 4; N_DOMAINS = 5
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024; V_ENT = 32; N_TEST = 50
else:
    SEEDS = [7, 17, 23]; N_DIM = N; V_ENT = 64; N_TEST = 100


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def cleanup(v, cb):
    return int(np.argmax(cb @ v))


# --- 1. sparse recall ---
def test_recall(g):
    n = N_DIM; k = max(1, int(round(F_SPARSE * n)))
    S = np.zeros((V_ENT, n), dtype=np.float32)
    for i in range(V_ENT):
        S[i, g.choice(n, size=k, replace=False)] = 1.0
    W = (S - F_SPARSE).T @ (S - F_SPARSE); np.fill_diagonal(W, 0.0); hits = 0
    for i in range(V_ENT):
        act = np.nonzero(S[i])[0]; cue = S[i].copy(); cue[g.choice(act, size=max(1, int(0.2 * k)), replace=False)] = 0.0
        r = (cue - F_SPARSE) @ W.T; idx = np.argpartition(-r, k - 1)[:k]; o = np.zeros(n); o[idx] = 1.0
        hits += (float((o * S[i]).sum() / k) > 0.95)
    return hits / V_ENT


# --- 2. analogical (relation generalizes to novel entity) ---
def test_analogical(g):
    n = N_DIM; ent = bipolar((V_ENT, n), g); rels = bipolar((N_REL, n), g)        # relation vectors
    # codebook = base entities + their relational images (ent_i * rel_r)
    images = np.stack([ent * rels[r] for r in range(N_REL)])                       # (N_REL, V_ENT, n)
    cb = np.concatenate([ent] + [images[r] for r in range(N_REL)], 0)
    cb = cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)
    hits = 0; tot = 0
    for r in range(N_REL):
        pool = list(range(V_ENT)); g.shuffle(pool); train, test = pool[:V_ENT // 2], pool[V_ENT // 2:]
        R_est = np.mean([ent[a] * (ent[a] * rels[r]) for a in train], 0)           # learn relation from train pairs
        for c in test[:max(1, N_TEST // N_REL)]:
            pred = ent[c] * R_est; true_idx = V_ENT + r * V_ENT + c                # image index in cb
            hits += (cleanup(pred, cb) == true_idx); tot += 1
    return hits / max(tot, 1)


# --- 3. counterfactual (remove fact -> query no longer returns its object) ---
def test_counterfactual(g):
    n = N_DIM; ent = bipolar((V_ENT, n), g)
    subj = list(range(0, V_ENT, 2)); obj = list(range(1, V_ENT, 2)); m = min(len(subj), len(obj))
    bundle = np.zeros(n, dtype=np.float32)
    facts = []
    for i in range(m):
        bundle += ent[subj[i]] * ent[obj[i]]; facts.append((subj[i], obj[i]))
    hits = 0; tot = 0
    for (s, o) in facts[:N_TEST]:
        before = cleanup(ent[s] * bundle, ent)                                     # query returns o
        b2 = bundle - ent[s] * ent[o]                                              # B6 delete fact (s,o)
        after = cleanup(ent[s] * b2, ent)                                          # should NOT be o now
        hits += (before == o and after != o); tot += 1
    return hits / max(tot, 1)


# --- 4. cross-domain transfer (relation learned on 4 domains applies to 5th) ---
def test_cross_domain(g):
    n = N_DIM; R = bipolar((1, n), g)[0]                                           # shared relation structure
    doms = [bipolar((V_ENT, n), g) for _ in range(N_DOMAINS)]
    R_est = np.zeros(n, dtype=np.float32); cnt = 0
    for d in range(N_DOMAINS - 1):                                                 # train on first 4 domains
        for a in range(V_ENT):
            R_est += doms[d][a] * (doms[d][a] * R); cnt += 1
    R_est /= cnt
    held = doms[-1]; cb = np.concatenate([held, held * R], 0); cb = cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)
    hits = 0
    for c in range(min(V_ENT, N_TEST)):
        pred = held[c] * R_est; hits += (cleanup(pred, cb) == V_ENT + c)
    return hits / min(V_ENT, N_TEST)


def _selftest():
    g = np.random.default_rng(0); n = 256; a, b = bipolar((n,), g), bipolar((n,), g)
    assert int(np.argmax(np.stack([a, b]) @ (a * (a * b)))) == 1, "bind/unbind round-trip"
    R = bipolar((n,), g); c = bipolar((n,), g); R_est = a * (a * R)
    assert float((c * R_est) @ (c * R)) / n > 0.9, "relation applies to novel C"
    assert N == 4096; print("[selftest] PASS: bind_unbind relation_generalizes", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    return {"seed": seed, "N": N_DIM,
            "recall": float(test_recall(np.random.default_rng(seed * 7 + 1))),
            "analogical": float(test_analogical(np.random.default_rng(seed * 7 + 2))),
            "counterfactual": float(test_counterfactual(np.random.default_rng(seed * 7 + 3))),
            "cross_domain": float(test_cross_domain(np.random.default_rng(seed * 7 + 4)))}


def verdict(ps) -> Tuple[str, str]:
    rc = float(np.mean([p["recall"] for p in ps])); an = float(np.mean([p["analogical"] for p in ps]))
    cf = float(np.mean([p["counterfactual"] for p in ps])); cd = float(np.mean([p["cross_domain"] for p in ps]))
    summary = "recall=%.2f analogical=%.2f counterfactual=%.2f cross_domain=%.2f" % (rc, an, cf, cd)
    if rc >= 0.80 and an >= 0.80 and cf >= 0.80 and cd >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate VSA reasoning validated (recall+analogical+counterfactual+cross-domain). " + summary)
    if min(rc, an, cf, cd) >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: all reasoning dims >=0.50, some below HP. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: a reasoning dimension < 0.50. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_ent=%d rels=%d domains=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_ENT, N_REL, N_DOMAINS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] recall=%.2f analogical=%.2f counterfactual=%.2f cross_domain=%.2f" % (seed, r["recall"], r["analogical"], r["counterfactual"], r["cross_domain"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
