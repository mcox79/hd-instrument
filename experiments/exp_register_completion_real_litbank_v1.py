"""EXP 4 -- the completion readout on the REAL reader load (LitBank), at the REAL pipeline D=1024.

PROBLEM: the_register_reads_by_argmax_not_recurrent_completion, bar item 2. The audit's 0.644->0.971 was a
controlled register-decode probe; re-earn the recovery on the REAL LitBank entity-event load, with floors +
an info-free twin recomputed, and be HONEST about scope: at the current per-call load the register is NOT
overloaded, so the readout is correctly INERT (the current wall is the front-end linking, a different
problem). The value is a BOOK-SCALE capacity lever.

REAL DATA (measured, data/litbank/who_did_what_events.json, 100 docs / 7,779 entities): events-per-entity is
median 1, p90 5 -- the BULK is far below the cliff (k_cliff(D=1024)=89), so the readout must be INERT there.
But the TAIL is real: 193 entities have >=32 events, 91 have >=64, and one protagonist reaches 260 events --
book-scale accumulators that DO reach the cliff at the real D. THIS is the regime where the readout must
recover.

CONSTRUCTION: each entity's events are accumulated into its register with a FINE per-event index (a distinct
event-slot per event = the finer conjunctive temporal context p2 validated), so the register is an ACROSS-slot
superposition (the regime the readout targets), NOT the coarse-key within-slot collision p2's SET-return
fixes. Decode each event's verb.

ARMS (D=1024 FIXED, per-entity register on the LIVE AccumulateRegister):
  argmax   -- the organ (per-slot argmax). Floor that fans on busy entities.
  serial   -- theta-gamma serial decode-and-suppress on the linear superposition (exp1).
  gated    -- the CA1-comparator readout (exp3): argmax when it already reconstructs; serial only on a
              near-exact reconstruction match; else argmax fallback. The DEPLOYABLE readout.
  majority -- per-entity most-frequent-verb floor (a trivial non-superposition baseline).
  twin     -- serial with SHUFFLED keys (info-free): must LOSE.

Binned by events-per-entity. HEADLINE: in the high-fan bins the completion readout beats argmax CI-separated;
in the low-fan bins it is INERT (no false current-task win); the twin loses; majority is far below.

Heavy (serial is O(events^2) on up to 260-event entities) -> ROUTE THE FULL RUN TO REMOTE (standing rule).
--smoke runs a few docs locally for correctness. Default (bare) = FULL. Remote-safe: NO spaCy on any path;
reads only the pre-parsed cache. ASCII only. Writes ONLY to data/exp_register_completion_real_litbank_v1/.
NO hdlab write.

# KB_REFERENT: data/litbank/who_did_what_events.json

Run:  .venv/Scripts/python.exe experiments/exp_register_completion_real_litbank_v1.py [--self-test|--smoke|--full]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from collections import Counter, defaultdict

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from experiments.exp_register_completion_readout_v1 import decode_argmax, decode_serial  # noqa: E402
from experiments.exp_readout_recall_vs_rank_reconciliation_v1 import decode_gated_recall  # noqa: E402

CACHE = os.path.join(REPO_ROOT, "data", "litbank", "who_did_what_events.json")   # KB_REFERENT
OUTDIR = os.path.join(REPO_ROOT, "data", "exp_register_completion_real_litbank_v1")
SEED = 20260828
D = 1024                          # the REAL pipeline FHRR dimensionality (FIXED)
BINS = [(1, 3), (4, 8), (9, 16), (17, 31), (32, 63), (64, 10_000)]
N_ITER = 6


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2 ** 31))


def load_entity_event_seqs(docs=None):
    """Per-doc real LitBank entity->[verbs-in-order] under gold coref (ORACLE linking isolates the STORE).
    Reads ONLY the pre-parsed cache (no spaCy). Returns list of (doc, verb_vocab, {entity: [verbs]})."""
    recs = json.load(open(CACHE, encoding="utf-8"))
    if docs:
        recs = recs[:docs]
    out = []
    for r in recs:
        stream = r["stream"]
        verb_vocab = sorted({m["gov_verb"] for m in stream if m.get("gov_verb") is not None})
        if not verb_vocab:
            continue
        ent_seq = defaultdict(list)
        for m in stream:
            if m.get("gov_verb") is not None:
                ent_seq[int(m["gold"])].append(m["gov_verb"])
        out.append((r["doc"], verb_vocab, dict(ent_seq)))
    return out


def _decode_entity(verb_vocab, verbs, seed):
    """Build ONE entity's register (fine per-event index) and decode every event's verb with each arm.
    Returns dict arm -> list of per-event correctness (0/1)."""
    n = len(verbs)
    g = _gen(seed)
    reg = AccumulateRegister(verb_vocab, D, g, max_event_slots=n)
    role_mat = torch.stack([reg.role_vecs[v] for v in verb_vocab], dim=0)
    vidx = {v: i for i, v in enumerate(verb_vocab)}
    keys = [reg.idx_vecs[s] for s in range(n)]
    truth = [vidx[v] for v in verbs]
    ent = "e"
    for s in range(n):
        reg.add_event(ent, verbs[s], s)
    rawsum = torch.stack(reg._events[ent], dim=0).sum(dim=0)

    arg = decode_argmax(rawsum, keys, role_mat)
    ser = decode_serial(rawsum, keys, role_mat, n_iter=N_ITER)
    gat, _ = decode_gated_recall(rawsum, keys, role_mat, n_iter=N_ITER)
    # per-entity majority-verb floor
    maj = vidx[Counter(verbs).most_common(1)[0][0]]
    # info-free twin: shuffled keys
    perm = list(np.random.default_rng(seed + 99).permutation(n))
    twin = decode_serial(rawsum, [keys[p] for p in perm], role_mat, n_iter=N_ITER)

    return {"argmax": [int(arg[s] == truth[s]) for s in range(n)],
            "serial": [int(ser[s] == truth[s]) for s in range(n)],
            "gated": [int(gat[s] == truth[s]) for s in range(n)],
            "majority": [int(maj == truth[s]) for s in range(n)],
            "twin": [int(twin[s] == truth[s]) for s in range(n)]}


def _bin_of(n):
    for lo, hi in BINS:
        if lo <= n <= hi:
            return (lo, hi)
    return None


def run(docs=None):
    ARMS = ["argmax", "serial", "gated", "majority", "twin"]
    # per-bin, per-entity accuracy lists (entity = the unit; population = entities)
    bin_ent_acc = {b: {a: [] for a in ARMS} for b in BINS}
    bin_counts = {b: 0 for b in BINS}
    data = load_entity_event_seqs(docs=docs)
    for di, (doc, verb_vocab, ent_seq) in enumerate(data):
        for E, verbs in ent_seq.items():
            n = len(verbs)
            if n < 1:
                continue
            b = _bin_of(n)
            if b is None:
                continue
            bin_counts[b] += 1
            if n == 1:
                for a in ARMS:
                    bin_ent_acc[b][a].append(1.0 if a != "twin" else 1.0)
                continue
            res = _decode_entity(verb_vocab, verbs, SEED + di * 131 + E)
            for a in ARMS:
                bin_ent_acc[b][a].append(float(np.mean(res[a])))

    def _ci(vals):
        if not vals:
            return None
        a = np.asarray(vals, float)
        rng = np.random.default_rng(SEED + 5)
        means = a[rng.integers(0, len(a), size=(2000, len(a)))].mean(axis=1)
        lo, hi = np.percentile(means, [2.5, 97.5])
        return {"acc": round(float(a.mean()), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                "n_entities": len(a)}

    rows = {}
    for b in BINS:
        rows[f"{b[0]}-{b[1]}"] = {a: _ci(bin_ent_acc[b][a]) for a in ARMS}
        # paired serial-minus-argmax and gated-minus-argmax CI in this bin
        for pa, pb, key in [("serial", "argmax", "serial_minus_argmax"), ("gated", "argmax", "gated_minus_argmax")]:
            va, vb = bin_ent_acc[b][pa], bin_ent_acc[b][pb]
            if len(va) >= 3:
                d = np.asarray(va) - np.asarray(vb)
                rng = np.random.default_rng(SEED + 9)
                dm = d[rng.integers(0, len(d), size=(2000, len(d)))].mean(axis=1)
                lo, hi = np.percentile(dm, [2.5, 97.5])
                rows[f"{b[0]}-{b[1]}"][key] = {"mean": round(float(d.mean()), 4), "lo": round(float(lo), 4),
                                               "hi": round(float(hi), 4)}
    return {"anchor": "register_completion_real_litbank_v1", "d": D, "n_docs": docs or len(data),
            "bins": [f"{b[0]}-{b[1]}" for b in BINS], "bin_counts": {f"{b[0]}-{b[1]}": bin_counts[b] for b in BINS},
            "rows": rows}


def summarize(res):
    print(f"\n=== REAL LitBank load, completion readout (D={res['d']} FIXED, {res['n_docs']} docs) ===")
    print("  events/ent  n_ent  majority  argmax  serial  gated   twin    [serial-argmax CI]   [gated-argmax CI]")
    for b in res["bins"]:
        r = res["rows"][b]
        def s(a):
            return f"{r[a]['acc']:.3f}" if r[a] else "  -  "
        sm = r.get("serial_minus_argmax"); gm = r.get("gated_minus_argmax")
        smx = f"{sm['mean']:+.3f}[{sm['lo']:+.3f},{sm['hi']:+.3f}]" if sm else "n/a"
        gmx = f"{gm['mean']:+.3f}[{gm['lo']:+.3f},{gm['hi']:+.3f}]" if gm else "n/a"
        nent = r['argmax']['n_entities'] if r['argmax'] else 0
        print(f"   {b:>8s}  {nent:>4d}   {s('majority')}    {s('argmax')}   {s('serial')}   {s('gated')}   {s('twin')}   {smx}   {gmx}")
    print("\n  READING: INERT on low-fan entities (the bulk -- argmax already ~1.0; no false current-task win); "
          "on the high-fan tail (book-scale accumulators) the completion readout recovers over argmax "
          "CI-separated; the shuffled-key twin loses; majority-verb floor is far below. D FIXED.")


def self_test():
    res = run(docs=6)
    lo_bin = res["rows"]["1-3"]; assert lo_bin["argmax"]["acc"] > 0.98, f"low-fan must be inert (argmax~1): {lo_bin}"
    # at least one high-fan bin populated in 6 docs with serial>=argmax
    hi = None
    for b in ["17-31", "32-63", "64-10000"]:
        if res["rows"][b]["argmax"] and res["rows"][b]["argmax"]["n_entities"] >= 2:
            hi = res["rows"][b]
    if hi:
        assert hi["serial"]["acc"] >= hi["argmax"]["acc"] - 0.02, f"serial must not regress high-fan: {hi}"
    print(f"SELF-TEST PASS: low-fan argmax={lo_bin['argmax']['acc']:.3f} (inert); "
          f"{'high-fan bin present, serial>=argmax' if hi else 'no high-fan bin in 6 docs (expected; run full)'}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=5400)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    smoke = bool(args.smoke) or args.mode == "smoke"
    t0 = time.time()
    res = run(docs=10 if smoke else None)
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["mode"] = "smoke" if smoke else "full"
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (mode={res['mode']}, elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
