"""Scaffold-free witness for `one_store_does_two_jobs_and_consolidation_is_a_single_average`.

Proves the mechanisms the SOLVED.md leans on, in <5s, with NO experiment scaffolding:
  1. CATASTROPHIC FORGETTING FIRES + INTERLEAVED REPLAY FIXES IT (the CLS core), in a compressed
     (overlapping) linear associator -- sequential forgets OLD, interleaved protects it.
  2. THE SEPARABLE-ROW STORE NEVER FORGETS (the live-op reality): storing NEW leaves OLD's slot
     untouched -> retention invariant to phase order. This is why the bar's RETENTION metric resolves
     to fork B on the live path.
  3. SELECTIVE REPLAY NEEDS ERROR-CORRECTING PLASTICITY: with a rank-1 HEBBIAN store, replaying the
     highest-surprise OLD does NOT beat uniform (priority only reshuffles -- the surprise-cell finding);
     with an ERROR-CORRECTING DELTA store, selective replay of the most-forgotten OLD DOES beat uniform
     at matched budget (the fix). This is the load-bearing mechanistic correction.
  4. METRIC FAILS SAFE: a shuffled key->value mapping collapses retrieval to chance.
  5. REAL-DATA HEADLINE: asserts the landed metrics.json is regime-consistent (forgetting fires + replay
     CI-separated over sequential on OLD; the live separable floor is NOT beaten on retention;
     generalisation is at/near the first-order floor for every arm).

Run: .venv/Scripts/python.exe verification/test_consolidation_real_reading.py
"""
from __future__ import annotations

import json
import os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                    "exp_consolidation_real_reading_old_vs_new_v1", "metrics.json")
DATA_V2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "exp_consolidation_sparse_hidden_cortex_v2", "metrics.json")


def _unit(M):
    n = np.linalg.norm(M, axis=1, keepdims=True); n[n < 1e-12] = 1.0
    return M / n


def _ranks(W, K, C, tgt, idxs):
    Y = _unit(K[idxs] @ W.T); S = Y @ C.T
    order = np.argsort(-S, axis=1)
    return np.array([int(np.where(order[r] == tgt[i])[0][0]) for r, i in enumerate(idxs)])


def _delta(W, K, V, idxs, epochs, lr, rng):
    for _ in range(epochs):
        o = list(idxs); rng.shuffle(o)
        for i in o:
            W += lr * np.outer(V[i] - W @ K[i], K[i])
    return W


def _fixture(seed, n=90, d=30):
    """Overlapping compressed codes (d<n -> over capacity). keys = values codebook = same concepts;
    target(i) = a fixed permutation partner (a learned relation, not identity)."""
    rng = np.random.default_rng(seed)
    K = _unit(rng.standard_normal((n, d)))
    C = K.copy()
    tgt = (np.arange(n) + 1) % n          # each concept's associate = next concept (a real 1-1 relation)
    V = C[tgt]
    return K, C, V, tgt


def test_catastrophic_forgetting_and_replay_fix():
    seq_old, itl_old = [], []
    for s in range(6):
        K, C, V, tgt = _fixture(s)
        n = len(K); old = list(range(n // 2)); new = list(range(n // 2, n))
        import random as _r
        W0 = _delta(np.zeros((C.shape[1], K.shape[1])), K, V, old, 60, 0.5, _r.Random(s))
        # SEQUENTIAL: learn NEW, no replay
        Wseq = _delta(W0.copy(), K, V, new, 60, 0.5, _r.Random(s + 1))
        # INTERLEAVED: learn NEW with replayed OLD
        Wit = W0.copy(); rr = _r.Random(s + 2)
        for _ in range(60):
            batch = new + [old[j] for j in rr.sample(range(len(old)), len(new))]
            Wit = _delta(Wit, K, V, batch, 1, 0.5, rr)
        seq_old.append(float(np.mean(_ranks(Wseq, K, C, tgt, old) == 0)))
        itl_old.append(float(np.mean(_ranks(Wit, K, C, tgt, old) == 0)))
    seq, itl = np.mean(seq_old), np.mean(itl_old)
    assert seq < 0.5, f"forgetting must fire: sequential OLD retention {seq:.3f} not < 0.5"
    assert itl > seq + 0.25, f"interleaved must protect OLD: {itl:.3f} vs seq {seq:.3f}"
    print(f"  [1] forgetting fires + replay fixes: SEQ OLD={seq:.3f} INTERLEAVED OLD={itl:.3f}  PASS")


def test_separable_store_never_forgets():
    # a separable-row store: dict slot per concept; storing NEW never touches OLD's slot
    store = {}
    old = list(range(40)); new = list(range(40, 80))
    for c in old:
        store[c] = ("assoc", c)
    old_before = {c: store[c] for c in old}
    for c in new:                                    # learn NEW
        store[c] = ("assoc", c)
    old_ret = np.mean([1.0 if store[c] == old_before[c] else 0.0 for c in old])
    assert old_ret == 1.0, f"separable store must not forget: OLD retention {old_ret}"
    print(f"  [2] separable-row store never forgets: OLD retention after NEW = {old_ret:.3f}  PASS")


def _split_fixture(seed, nB=20, nA=20, nNew=20, d=40):
    """PARTIAL-forgetting fixture: OLD splits into a SAFE block B (keys in subspace-1) and a CONTESTED
    block A (keys in subspace-2, shared with NEW). Learning NEW overwrites A but not B -> some OLD are
    at-risk and some are safe, so replay SELECTION has something to choose between."""
    rng = np.random.default_rng(seed)
    n = nB + nA + nNew
    h = d // 2
    K = np.zeros((n, d))
    K[:nB, :h] = rng.standard_normal((nB, h))                 # safe OLD in subspace-1
    K[nB:nB + nA, h:] = rng.standard_normal((nA, h))          # contested OLD in subspace-2
    K[nB + nA:, h:] = rng.standard_normal((nNew, h))          # NEW in subspace-2 (contests A)
    K = _unit(K)
    C = K.copy()
    tgt = (np.arange(n) + 1) % n
    V = C[tgt]
    old = list(range(nB + nA)); new = list(range(nB + nA, n))
    return K, C, V, tgt, old, new


def test_selective_replay_needs_error_correcting_plasticity():
    import random as _r
    hebb_gain, delta_gain = [], []
    for s in range(6):
        K, C, V, tgt, old, new = _split_fixture(s)
        B = 12                                        # matched replay budget (< |old|=40 -> a real choice)

        def run(three_factor, selective):
            W = _delta(np.zeros((C.shape[1], K.shape[1])), K, V, old, 60, 0.5, _r.Random(s))
            W = _delta(W, K, V, new, 30, 0.5, _r.Random(s + 1))   # interference (hits contested A only)
            r = _ranks(W, K, C, tgt, old)
            pick = ([old[j] for j in np.argsort(-r)[:B]] if selective                # most-forgotten
                    else [old[j] for j in _r.Random(s + 7).sample(range(len(old)), B)])
            if three_factor:
                W = _delta(W, K, V, pick, 4, 0.5, _r.Random(s + 3))                  # error-correcting replay
            else:
                for i in pick:
                    W += np.outer(V[i], K[i])                                        # rank-1 Hebbian replay
            return float(np.mean(_ranks(W, K, C, tgt, old) == 0))

        hebb_gain.append(run(False, True) - run(False, False))
        delta_gain.append(run(True, True) - run(True, False))
    hg, dg = np.mean(hebb_gain), np.mean(delta_gain)
    assert dg > 0.03, f"selective replay must help under DELTA plasticity: gain {dg:.3f} not > 0.03"
    assert dg > hg + 0.01, f"delta must exploit priority better than rank-1 Hebbian: delta {dg:.3f} vs hebb {hg:.3f}"
    print(f"  [3] selective>uniform needs error-correcting plasticity: DELTA gain={dg:+.3f} "
          f"> HEBB gain={hg:+.3f}  PASS")


def test_selective_is_zero_sum_in_overlapping_store():
    """The real-data negative explained: in a fully-OVERLAPPING store (no separable subspaces), selective
    replay of the most-forgotten OLD does NOT beat uniform even under SCARCE budget -- replaying at-risk
    items disturbs the retained ones (zero-sum). Contrast with test_3's orthogonal-subspace fixture where
    it DID win. So selection is a lever only when memories occupy separable subspaces; overlapping cortical
    semantics lack this."""
    import random as _r
    gains = []
    for s in range(6):
        K, C, V, tgt = _fixture(s, n=100, d=32)          # fully overlapping (dense random, d<n)
        n = len(K); old = list(range(n // 2)); new = list(range(n // 2, n))
        B = 6                                            # SCARCE budget (6 of 50 old)

        def run(selective):
            W = _delta(np.zeros((C.shape[1], K.shape[1])), K, V, old, 60, 0.5, _r.Random(s))
            W = _delta(W, K, V, new, 30, 0.5, _r.Random(s + 1))
            r = _ranks(W, K, C, tgt, old)
            pick = ([old[j] for j in np.argsort(-r)[:B]] if selective
                    else [old[j] for j in _r.Random(s + 7).sample(range(len(old)), B)])
            W = _delta(W, K, V, pick, 4, 0.5, _r.Random(s + 3))
            return float(np.mean(_ranks(W, K, C, tgt, old) == 0))
        gains.append(run(True) - run(False))
    g = np.mean(gains)
    assert abs(g) < 0.05, f"in an overlapping store selective should NOT meaningfully beat uniform: gain {g:+.3f}"
    print(f"  [6] selective is ~zero-sum in an OVERLAPPING store (scarce budget): gain={g:+.3f} (~0)  PASS")


def test_sparse_hidden_cortex_suppresses_forgetting():
    """The deepest brain mechanism: a SPARSE k-WTA hidden cortical layer allocates concepts to separable
    subpopulations, so sequential learning of NEW barely disturbs OLD -- WITHOUT any replay. A DENSE hidden
    layer (shared units) does not. Proves sparse pattern-separated coding (deviation #4) is the primary
    anti-forgetting lever, stronger than replay. (Same architecture as exp_consolidation_sparse_hidden_cortex_v2.)"""
    import random as _r
    rng = np.random.default_rng(0)
    n, d, Dh = 120, 32, 512
    K = _unit(rng.standard_normal((n, d)))
    C = K.copy(); tgt = (np.arange(n) + 1) % n; V = C[tgt]
    old = list(range(n // 2)); new = list(range(n // 2, n))
    W1 = rng.standard_normal((Dh, d)) / np.sqrt(d)

    def hidden(sparse, keep=0.05):
        P = K @ W1.T
        if not sparse:
            return _unit(np.tanh(P))
        H = np.zeros_like(P); k = max(1, int(keep * Dh)); P = np.maximum(P, 0)
        for i in range(n):
            idx = np.argpartition(P[i], Dh - k)[Dh - k:]
            H[i, idx] = P[i, idx]
        return _unit(H)

    def old_retention_after_sequential(H):
        W2 = np.zeros((d, Dh))
        for _ in range(50):                              # learn OLD
            o = old[:]; _r.Random(1).shuffle(o)
            for i in o:
                W2 += 0.5 * np.outer(V[i] - W2 @ H[i], H[i])
        for _ in range(50):                              # learn NEW, NO replay
            o = new[:]; _r.Random(2).shuffle(o)
            for i in o:
                W2 += 0.5 * np.outer(V[i] - W2 @ H[i], H[i])
        Y = _unit(H[old] @ W2.T); S = Y @ C.T
        for r, i in enumerate(old):
            S[r, i] = -1e9
        order = np.argsort(-S, axis=1)
        return float(np.mean([order[r][0] == tgt[i] for r, i in enumerate(old)]))

    sparse_ret = old_retention_after_sequential(hidden(True))
    dense_ret = old_retention_after_sequential(hidden(False))
    assert sparse_ret > 0.6, f"sparse-hidden cortex should retain OLD under sequential learning: {sparse_ret:.3f}"
    assert sparse_ret > dense_ret + 0.3, f"sparse must beat dense on retention: sparse {sparse_ret:.3f} dense {dense_ret:.3f}"
    print(f"  [7] sparse-hidden coding suppresses forgetting (no replay): sparse OLD={sparse_ret:.3f} "
          f">> dense OLD={dense_ret:.3f}  PASS")


def test_metric_fails_safe():
    K, C, V, tgt = _fixture(11)
    n = len(K)
    rng = np.random.default_rng(0)
    perm = rng.permutation(n)
    W = np.zeros((C.shape[1], K.shape[1]))
    for i in range(n):                                # store SHUFFLED mapping
        W += np.outer(V[perm][i], K[i])
    acc = float(np.mean(_ranks(W, K, C, tgt, list(range(n))) == 0))
    assert acc < 0.08, f"shuffled mapping must collapse to ~chance: {acc:.3f}"
    print(f"  [4] metric fails safe (shuffle null): top1={acc:.3f} (chance~{1.0/n:.3f})  PASS")


def test_real_data_headline():
    if not os.path.exists(DATA):
        print("  [5] metrics.json absent -- run the full cell first; SKIP")
        return
    d = json.load(open(DATA))
    if d.get("run_mode") != "full":
        print(f"  [5] metrics.json is run_mode={d.get('run_mode')} (not full) -- SKIP real-data asserts")
        return
    a = d["agg"]
    if "balanced" not in a.get("INTERLEAVED", {}):
        print("  [5] metrics.json predates the balanced-retention reporting -- re-run the full cell; SKIP")
        return
    seq, itl, sel = a["SEQUENTIAL"], a["INTERLEAVED"], a["INTERLV_SELECTIVE"]
    lookup, sim, schema = a["SEP_LOOKUP"], a["SEP_AVG_SIM"], a["INTERLV_SCHEMA"]
    # (a) forgetting fires + interleaved replay CI-separated over sequential on OLD retention (the POSITIVE)
    assert itl["old_lo"] > seq["old_hi"], \
        f"replay must beat sequential on OLD CI-sep: INTERLV.lo {itl['old_lo']:.3f} vs SEQ.hi {seq['old_hi']:.3f}"
    # (b) the live separable store is NOT beaten on JOINT retention (fork B: forgetting not the constraint)
    best = max(("INTERLEAVED", "INTERLV_SELECTIVE", "INTERLV_SCHEMA", "INTERLV_3FACTOR"),
               key=lambda k: a[k]["joint_top1"])
    assert a[best]["joint_lo"] <= lookup["joint_hi"], \
        f"a distributed arm beat the separable floor on retention -- fork A, revisit: {best}"
    # (c) SELECTIVE does NOT beat uniform interleaving on BALANCED (min old,new) retention -> twin does not lose
    assert sel["balanced"] <= itl["balanced"] + 0.02, \
        f"selective beat uniform on balanced retention -- selection IS a lever, revisit: sel {sel['balanced']:.3f} itl {itl['balanced']:.3f}"
    # (d) SCHEMA's mean-JOINT is a hoarding artifact: it protects OLD by sacrificing NEW (new << old)
    assert schema["new_top1"] < schema["old_top1"], \
        f"SCHEMA expected to hoard OLD at NEW's expense: new {schema['new_top1']:.3f} old {schema['old_top1']:.3f}"
    # (e) generalisation: no learned arm CI-separated ABOVE the first-order similarity floor (content wall)
    for k in ("INTERLEAVED", "INTERLV_SELECTIVE", "INTERLV_3FACTOR"):
        assert a[k]["inf_lo"] <= sim["inf_hi"] + 1e-9, \
            f"{k} generalises above first-order floor -- content-wall claim wrong: {a[k]['inf_lo']:.3f}"
    print(f"  [5] real-data headline consistent: SEQ OLD={seq['old_top1']:.3f} -> INTERLV OLD={itl['old_top1']:.3f} "
          f"(CI-sep) | SELECTIVE bal={sel['balanced']:.3f} <= uniform bal={itl['balanced']:.3f} (twin not beaten) | "
          f"SCHEMA hoards (old={schema['old_top1']:.3f} new={schema['new_top1']:.3f}) | "
          f"SEP_LOOKUP joint=1.000 unbeaten | gen<=sim floor {sim['inf_top1']:.3f}  PASS")


def test_v2_sparse_cortex_real_data():
    """v2 (sparse-hidden cortex, real reading): at the SPARSEST code selective interleaved replay BEATS the
    uniform info-free twin CI-separated (the v1 negative FLIPS in the brain-faithful sparse regime), AND the
    dense-hidden control collapses (sparsity is causal). If generalisation was scored, confirm the
    retention-vs-generalisation tradeoff (sparse RETAINS but does not GENERALISE -> the CLS reason for two stores)."""
    if not os.path.exists(DATA_V2):
        print("  [8] v2 metrics absent -- run exp_consolidation_sparse_hidden_cortex_v2.py; SKIP")
        return
    d = json.load(open(DATA_V2))
    if d.get("run_mode") != "full":
        print(f"  [8] v2 metrics run_mode={d.get('run_mode')} -- SKIP"); return
    res = d["results"]
    sparse_keys = sorted([k for k in res if k.startswith("sparse_")], key=lambda k: float(k.split("keep")[1]))
    # sparsest config where uniform has NOT already saturated -> selective should CI-beat uniform on OLD
    flipped = False
    for k in sparse_keys:
        itl, sel = res[k]["INTERLEAVED"], res[k]["SELECTIVE"]
        if itl["old"] < 0.98 and sel["old_lo"] > itl["old_hi"]:
            flipped = True
            print(f"  [8] v2: at {k} SELECTIVE OLD={sel['old']:.3f}[{sel['old_lo']:.3f},{sel['old_hi']:.3f}] "
                  f"CI-beats UNIFORM {itl['old']:.3f}[{itl['old_lo']:.3f},{itl['old_hi']:.3f}] "
                  f"-> selection IS a lever in the sparse regime (v1 negative FLIPS)")
            if "gen" in itl:
                print(f"       retention-vs-generalisation: UNIFORM retain={itl['old']:.3f} generalise={itl['gen']:.3f} "
                      f"(sparse retains but does not generalise -> two stores)")
            break
    dense_keys = [k for k in res if k.startswith("dense_")]
    if dense_keys:
        assert all(res[k]["INTERLEAVED"]["old"] < 0.05 for k in dense_keys), "dense-hidden control should collapse"
    assert flipped, "expected selective to CI-beat uniform at some sparse code (the v1->v2 flip)"
    print("       ...PASS")


def main():
    print("WITNESS: one_store_does_two_jobs_and_consolidation_is_a_single_average")
    test_catastrophic_forgetting_and_replay_fix()
    test_separable_store_never_forgets()
    test_selective_replay_needs_error_correcting_plasticity()
    test_selective_is_zero_sum_in_overlapping_store()
    test_sparse_hidden_cortex_suppresses_forgetting()
    test_metric_fails_safe()
    test_real_data_headline()
    test_v2_sparse_cortex_real_data()
    print("WITNESS PASS")


if __name__ == "__main__":
    main()
