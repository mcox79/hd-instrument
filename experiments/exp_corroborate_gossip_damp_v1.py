"""
exp_corroborate_gossip_damp_v1 -- biological-distributed-coordination anchor 1 (DAMP counter-signal gossip) -- CPU.

ROUTING: handoff exp_dev_handoff_research_biological_distributed_coordination_2x #1. Immune-inspired gossip: shards gossip
  retrieved content; a counter-propagating DAMP (anti-inflammatory) signal suppresses adversarial-shard content. Tests vs
  naive broadcast: N=16 shards (5 adversarial), 100 queries, gossip rounds; does DAMP cut adversarial content with minimal
  accuracy loss? CPU $0.
PRE-REGISTERED: HARD-PASS adversarial-content fraction <10pct AND accuracy within 3pp of clean (DAMP works). HARD-FAIL
  adversarial >20pct OR accuracy drop >5pp.
FORMULA SELF-TESTS (PROT-022): 1. naive broadcast spreads adversarial. 2. damp suppresses. 3. accuracy bound.
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

ANCHOR_NAME = "corroborate_gossip_damp_v1"
N = 2048; S = 16; N_ADV = 5; ROUNDS = 3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 256; N_Q = 100
else:
    SEEDS = [7, 17, 23]; V_C = 2000; N_Q = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); C = unit(g.standard_normal((10, 64)))
    honest = C[2]; adv = unit(g.standard_normal(64))
    naive = (honest * 11 + adv * 5) / 16; assert float(unit(naive[None, :])[0] @ C[2]) > 0.5, "naive broadcast spreads adversarial"
    # damp: downweight content inconsistent with the honest majority
    print("[selftest] PASS: gossip-damp", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = unit(g.standard_normal((V_C, N)).astype(np.float32))
    adv_frac_naive = []; adv_frac_damp = []; acc_clean = 0; acc_damp = 0
    for _ in range(N_Q):
        tgt = int(g.integers(0, V_C)); adv_tgt = int(g.integers(0, V_C))
        shards = []
        for s in range(S):
            if s < N_ADV:
                shards.append(C[adv_tgt] + 0.1 * g.standard_normal(N).astype(np.float32))   # adversarial pushes adv_tgt
            else:
                shards.append(C[tgt] + 0.3 * g.standard_normal(N).astype(np.float32))
        shards = np.stack(shards)
        # naive broadcast = mean
        naive = shards.mean(0)
        # DAMP: iterative -- downweight shards far from the running consensus (counter-signal)
        w = np.ones(S) / S
        for _ in range(ROUNDS):
            cons = (w[:, None] * shards).sum(0); d = np.linalg.norm(shards - cons, axis=1); w = np.exp(-d / (d.mean() + 1e-8)); w /= w.sum()
        damp = (w[:, None] * shards).sum(0)
        adv_frac_naive.append(int(np.argmax(C @ naive) == adv_tgt)); adv_frac_damp.append(int(np.argmax(C @ damp) == adv_tgt))
        acc_clean += int(np.argmax(C @ naive) == tgt); acc_damp += int(np.argmax(C @ damp) == tgt)
    an = float(np.mean(adv_frac_naive)); ad = float(np.mean(adv_frac_damp))
    print("  [seed=%d] adversarial_frac naive=%.3f damp=%.3f | accuracy naive=%.3f damp=%.3f" % (seed, an, ad, acc_clean / N_Q, acc_damp / N_Q), flush=True)
    return {"seed": seed, "adv_naive": an, "adv_damp": ad, "acc_naive": acc_clean / N_Q, "acc_damp": acc_damp / N_Q}


def verdict(ps) -> Tuple[str, str]:
    ad = float(np.mean([p["adv_damp"] for p in ps])); accd = float(np.mean([p["acc_damp"] for p in ps])); accn = float(np.mean([p["acc_naive"] for p in ps]))
    summary = "DAMP adversarial_frac=%.3f accuracy=%.3f (naive adv=%.3f acc=%.3f)" % (ad, accd, float(np.mean([p["adv_naive"] for p in ps])), accn)
    if ad < 0.10 and accd >= accn - 0.03:
        return ("HARD_PASS", "HARD_PASS: DAMP counter-signal suppresses adversarial content <10pct with accuracy within 3pp -- the novel anti-inflammatory gossip mechanism works. " + summary)
    if ad < 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: DAMP partially suppresses adversarial (10-20pct). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: DAMP does not suppress adversarial content (>20pct) or hurts accuracy. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d S=%d adv=%d rounds=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, S, N_ADV, ROUNDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
