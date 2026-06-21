"""Skunkworks 2026-06-21 -- CPU MECHANISM-PROBE (de-risks the continual-write lever; NOT the cell). HEAT-SAFE (small).
THE LEVER MAKE-OR-BREAK (my SCHEMA-VET C1 + lever-design 99392cca): (1) does naive write-all genuinely FORGET
(old-fact recall drops past capacity = a real cost)? (2) does a capacity-aware evict policy BEAT BOTH write-all
(overflow-corrupts) AND FIFO (drops still-needed-old) -- in a regime where the old facts are RE-QUERIED (C1)?
If write-all never forgets in-regime OR FIFO suffices -> lever collapses to MM. If cap-aware beats both -> genuine
chain-grade cost.
Substrate: Hopfield-style associative store W = sum_i v_i k_i^T (bipolar); recall v = sign(W k_q) -> nearest value.
Evict = subtract the bound outer-product. "Important-old" held-out set is re-queried throughout (so FIFO genuinely
fails by dropping them). READ-ONLY (no Store write). ASCII. Hands result to Exp-Dev to inform the lever build.
"""
from __future__ import annotations
import numpy as np


def make_codebook(n, N, rng):
    return np.sign(rng.standard_normal((n, N)))  # bipolar +-1


def recall_acc(W, keys, vals, valcb, rng, noise=0.3):
    # query each (key,val) with noise; recover sign(W k_q); match to nearest value in codebook; acc = correct id
    if len(keys) == 0:
        return 1.0
    K = np.array(keys); V = np.array(vals)
    Q = K + noise * rng.standard_normal(K.shape)
    rec = np.sign(Q @ W.T)  # (n, N)
    sims = rec @ valcb.T     # (n, n_vals)
    pred = np.argmax(sims, axis=1)
    return float((pred == V).mean())


def run(policy, M, N, cap, rng, important_idx):
    valcb = make_codebook(M, N, rng)
    keycb = make_codebook(M, N, rng)
    W = np.zeros((N, N))
    active = []  # list of (fact_id) currently stored
    imp = set(important_idx)
    margins = {}  # fact_id -> last recall margin (for cap-aware)
    for i in range(M):
        k, v = keycb[i], valcb[i]
        W = W + np.outer(v, k)
        active.append(i)
        if len(active) > cap:
            if policy == 'write_all':
                pass  # never evict -> W keeps growing -> crosstalk corrupts
            elif policy == 'fifo':
                victim = active.pop(0)            # drop OLDEST (incl. important-old)
                W = W - np.outer(valcb[victim], keycb[victim])
            elif policy == 'cap_aware':
                # evict the NON-important fact with the lowest recall-margin (least-needed); never evict important-old
                cands = [a for a in active if a not in imp]
                if not cands:
                    cands = active[:]
                # cheap proxy: oldest non-important (age) -- but PROTECT important; this is the lever's policy
                victim = cands[0]
                active.remove(victim)
                W = W - np.outer(valcb[victim], keycb[victim])
    # measure recall on: all-active, and the important-old subset (re-queried throughout)
    act_keys = [keycb[a] for a in active]; act_vals = [a for a in active]
    imp_active = [a for a in important_idx if (policy == 'write_all' or a in active)]
    imp_keys = [keycb[a] for a in imp_active]; imp_vals = [a for a in imp_active]
    rr = np.random.default_rng(12345)
    all_rec = recall_acc(W, act_keys, act_vals, valcb, rr)
    # important-old recall: for write_all all are "active" (never evicted but maybe corrupted); for evict policies
    # only those still active can recall (dropped ones = 0 by definition)
    n_imp = len(important_idx)
    imp_rec_active = recall_acc(W, imp_keys, imp_vals, valcb, rr) if imp_keys else 0.0
    imp_present = len(imp_active) / n_imp
    imp_rec_overall = imp_rec_active * imp_present  # recall over ALL important-old (dropped ones count as miss)
    return {'all_active_recall': all_rec, 'important_old_recall': imp_rec_overall,
            'important_present_frac': imp_present, 'n_active': len(active)}


def main():
    # de-risk needs a CROWDING regime where write-all genuinely forgets (else the probe can't test the lever's cost).
    # Sweep M at N=256 to LOCATE write-all's forgetting onset (all-active recall drops). Heat-safe: O(M*N^2), no M x M.
    N = 256
    cap = int(0.30 * N)  # evict threshold for fifo/cap_aware
    n_imp = 30
    print("CONTINUAL-WRITE LEVER DE-RISK PROBE v2 (heat-safe): LOCATE write-all forgetting onset, then compare policies.")
    print(f"  N={N}, cap={cap}, {n_imp} important-old re-queried throughout, 3 seeds; M-sweep to find crowding\n")
    print(f"  {'M':>6} {'write_all_all':>14} {'fifo_imp':>9} {'cap_aware_imp':>14} {'write_all_imp':>14}")
    best = None
    for M in (300, 600, 1200, 2400, 4800):
        agg = {}
        for pol in ('write_all', 'fifo', 'cap_aware'):
            rows = []
            for s in (1, 2, 3):
                rng = np.random.default_rng(s)
                rows.append(run(pol, M, N, cap, rng, list(range(n_imp))))
            agg[pol] = {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}
        wa_all = agg['write_all']['all_active_recall']
        wa_i = agg['write_all']['important_old_recall']; fi_i = agg['fifo']['important_old_recall']; ca_i = agg['cap_aware']['important_old_recall']
        print(f"  {M:>6} {wa_all:>14.3f} {fi_i:>9.3f} {ca_i:>14.3f} {wa_i:>14.3f}")
        if wa_all < 0.7 and best is None:
            best = (M, wa_all, wa_i, fi_i, ca_i)
    print()
    if best is None:
        print("  INCONCLUSIVE: write-all all-active recall NEVER dropped below 0.7 across M-sweep -> the store+cleanup")
        print("  scheme does NOT crowd in this regime (high capacity via codebook-cleanup) -> can't test forgetting-cost")
        print("  here. The genuine continual-write cost (if any) needs the REAL substrate-KV + a3f473dd crowding (Exp-Dev cell).")
    else:
        M, wa_all, wa_i, fi_i, ca_i = best
        forgets = True; beats_both = (ca_i > wa_i + 0.1) and (ca_i > fi_i + 0.1)
        print(f"  CROWDING LOCATED at M={M} (write-all all-active recall {wa_all:.3f} < 0.7 = genuine forgetting).")
        print(f"  At M={M}: cap_aware important-old {ca_i:.3f} vs write-all {wa_i:.3f} vs FIFO {fi_i:.3f}")
        verdict = ("GENUINE COST -> lever chain-grade-eligible (cap-aware beats BOTH in the crowding regime)"
                   if beats_both else "cap-aware does NOT beat both even when crowded -> lever -> MM")
        print(f"  VERDICT: {verdict}")
    print("\nNOTE: synthetic Hopfield store + age-proxy cap-aware policy (protect-important); CPU mechanism-probe to inform")
    print("the lever build, NOT the cell. Hand to Exp-Dev. Real cell uses the substrate KV + a3f473dd envelope threshold.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
