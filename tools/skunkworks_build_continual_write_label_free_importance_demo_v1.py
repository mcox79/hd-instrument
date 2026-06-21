"""Skunkworks 2026-06-21 -- BUILD the continual-write lever's DISTINCTIVE AXIS (label-free importance inference) on CPU.
My continual-write de-risk (eb2cb71d) showed a genuine cost (write-all forgets, FIFO drops-needed) but used a
PROTECT-BY-LABEL policy (circular). The REAL lever question (my distinctive-axis flag -> Research v3 adopted): does a
LABEL-FREE importance policy work? Here: LRU (evict LEAST-RECENTLY-ACCESSED -- importance INFERRED from access-frequency,
NO labels) vs FIFO (evict oldest) vs write-all (no-evict) vs ORACLE-protect (upper bound, knows the important set).
THE CLAIM: LRU (label-free) preserves the re-queried important-old WITHOUT being told which they are -> beats FIFO+write-all,
approaches oracle. Faithful store: Hopfield-style W=sum v_i k_i^T + sign-readout (the v2 crowding regime, N=256). HEAT-SAFE.
"""
from __future__ import annotations
import numpy as np


def codebook(n, N, rng):
    return np.sign(rng.standard_normal((n, N)))


def recall_frac(W, keycb, valcb, ids, rng, noise=0.3):
    if not ids:
        return 1.0
    K = keycb[ids]; Q = K + noise * rng.standard_normal(K.shape)
    rec = np.sign(Q @ W.T); bitacc = (rec == valcb[ids]).mean(axis=1)
    return float((bitacc >= 0.9).mean())


def run(policy, M, N, cap, rng, important, requery_every=3):
    """Stream M writes; the `important` set is RE-QUERIED throughout (so its facts stay 'accessed'). Eviction policy
    decides what to drop when active > cap. LRU = evict least-recently-accessed (label-free importance proxy)."""
    keycb = codebook(M, N, rng); valcb = codebook(M, N, rng)
    W = np.zeros((N, N)); active = []; last_access = {}
    imp = set(important)
    for i in range(M):
        W = W + np.outer(valcb[i], keycb[i]); active.append(i); last_access[i] = i
        # re-query the important-old set periodically (they get 'accessed' -> recent) -- label-free signal
        if i % requery_every == 0:
            for j in important:
                if j in last_access and j in active:
                    last_access[j] = i  # access updates recency (LRU sees this; FIFO/write-all don't use it)
        if len(active) > cap:
            if policy == 'write_all':
                continue
            elif policy == 'fifo':
                victim = active.pop(0)
            elif policy == 'lru':
                victim = min(active, key=lambda x: last_access[x])   # least-recently-accessed (label-free)
                active.remove(victim)
            elif policy == 'oracle':
                cands = [a for a in active if a not in imp] or active
                victim = cands[0]; active.remove(victim)
            W = W - np.outer(valcb[victim], keycb[victim])
    rr = np.random.default_rng(999)
    imp_active = [j for j in important if (policy == 'write_all' or j in active)]
    imp_present = len(imp_active) / max(1, len(important))
    imp_rec = recall_frac(W, keycb, valcb, imp_active, rr) * imp_present  # dropped important = miss
    all_rec = recall_frac(W, keycb, valcb, active, rr)
    return imp_rec, all_rec


def main():
    N, cap, M, n_imp = 256, 76, 2400, 30
    print("CONTINUAL-WRITE LABEL-FREE IMPORTANCE DEMO (the distinctive axis): does LRU (label-free) beat FIFO+write-all?")
    print(f"  N={N} cap={cap} M={M} writes, {n_imp} important-old RE-QUERIED throughout (label-free access signal), 3 seeds\n")
    agg = {}
    for pol in ('write_all', 'fifo', 'lru', 'oracle'):
        rows = [run(pol, M, N, cap, np.random.default_rng(s), list(range(n_imp))) for s in (1, 2, 3)]
        agg[pol] = (float(np.mean([r[0] for r in rows])), float(np.mean([r[1] for r in rows])))
    for pol in ('write_all', 'fifo', 'lru', 'oracle'):
        print(f"  {pol:10s} important_old_recall={agg[pol][0]:.3f}   all_active_recall={agg[pol][1]:.3f}")
    wa, fi, lru, orc = agg['write_all'][0], agg['fifo'][0], agg['lru'][0], agg['oracle'][0]
    beats = (lru > wa + 0.1) and (lru > fi + 0.1)
    approaches = lru >= 0.8 * orc
    print(f"\n  LABEL-FREE LRU important-old={lru:.3f} vs write-all={wa:.3f} vs FIFO={fi:.3f} vs ORACLE={orc:.3f}")
    v = ("GREEN: label-free LRU BEATS write-all+FIFO" + (" + approaches oracle -> distinctive axis HOLDS (label-free importance works)" if approaches else " but below oracle (partial)")
         if beats else "label-free LRU does NOT beat both -> access-frequency is too weak a signal; needs a recall-error proxy")
    print(f"  VERDICT: {v}")
    print("\nNOTE: CPU demo of the continual-write distinctive axis (label-free importance via access-recency = LRU). Extends my")
    print("de-risk (eb2cb71d) past the protect-by-label circularity. Hand to Exp-Dev for the cell (real substrate-KV + a3f473dd envelope).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
