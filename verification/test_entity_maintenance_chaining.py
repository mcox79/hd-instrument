"""verification/test_entity_maintenance_chaining.py -- scaffold-free witness for
`incremental_entity_maintenance_pronoun_chaining_for_who_has_what`. Recomputes EVERY headline FROM SOURCE (imports
the mechanism, re-runs it on LitBank gold coref), no cached metrics trusted. Run:
    .venv/Scripts/python.exe verification/test_entity_maintenance_chaining.py
Exits non-zero if any check fails.
"""
from __future__ import annotations
import glob
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_entity_maintenance_chaining_v1 import (
    online_resolve, local_graded_pick, load_docs, by_midx, paired, LITBANK_DIR)
from experiments import exp_entity_maintenance_object_chaining_v1 as OBJ

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)


def acc(rows):
    return float(np.mean([r["correct"] for r in rows])) if rows else 0.0


def main():
    from hdlab.graded_coref_pick import graded_antecedent_pick

    # W1 -- the local pick is BIT-EQUAL to the pinned hdlab graded_antecedent_pick at weight=1 (the pick is held fixed)
    rng = np.random.default_rng(1)
    okmatch = True
    for _ in range(300):
        nc = int(rng.integers(2, 6))
        cps = [[(int(rng.integers(0, 12)), ["SUBJECT", "OBJECT", "OTHER"][int(rng.integers(0, 3))]) for _ in range(int(rng.integers(1, 4)))] for _ in range(nc)]
        ref = graded_antecedent_pick(cps, p_sent=13, pron_role="OBJECT")
        loc = local_graded_pick([[(s, r, 1.0) for s, r in pri] for pri in cps], p_sent=13, pron_role="OBJECT")
        if ref["pick"] != loc["pick"] or abs(ref["entropy"] - loc["entropy"]) > 1e-9:
            okmatch = False
            break
    check("W1_local_pick_bit_equal_to_hdlab", okmatch, "(pick held fixed; only histories differ)")

    # W2 -- accrual self-test: chaining breaks a recency tie to the protagonist that nochain misses
    def mk(head, cl, ip, s, mi, g, rk):
        return {"head": head, "cluster": cl, "is_pronoun": ip, "sent_idx": s, "midx": mi, "gender": g,
                "number": "singular", "name_gender": g, "sent_role_rank": rk, "is_subject": rk == 0, "span_toks": [head]}
    ms = [mk("mary", 1, False, 0, 0, "fem", 0), mk("she", 1, True, 1, 1, None, 0),
          mk("anne", 2, False, 1, 2, "fem", 0), mk("she", 1, True, 2, 3, None, 0)]
    a_noc = acc(online_resolve(ms, grouping="gold_nom", chain_mode="none"))
    a_ch = acc(online_resolve(ms, grouping="gold_nom", chain_mode="hard"))
    check("W2_accrual_mechanism", a_ch > a_noc and a_ch >= 0.99, "nochain=%.2f chain=%.2f" % (a_noc, a_ch))

    # ---- full LitBank recompute ----
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    docs = load_docs(files)
    check("W0_corpus_present", len(docs) >= 20, "%d docs" % len(docs))

    def pool(mode):
        rows = []
        for d in docs:
            rr = online_resolve(d["mentions"], grouping="gold_nom", chain_mode=mode,
                                canon_map=d["canon_map"], ekey_gold=d["ekey_gold"]) if mode != "aliaser" else None
            for r in rr:
                r["_doc"] = d["idx"]
            rows.extend(rr)
        return rows
    noc = pool("none"); ch = pool("hard"); sf = pool("soft"); ga = pool("gold"); orc = pool("oracle_hard")
    a = {k: acc(v) for k, v in (("noc", noc), ("ch", ch), ("sf", sf), ("ga", ga), ("orc", orc))}
    print("  ACC: nochain=%.3f chain=%.3f soft=%.3f gold_anchored=%.3f oracle=%.3f" % (a["noc"], a["ch"], a["sf"], a["ga"], a["orc"]), flush=True)

    # W3 -- reproduces the parent's grouping decomposition: gold-chaining is the big lever (~+0.26 over no-chaining)
    check("W3_reproduces_grouping_decomposition", (a["ga"] - a["noc"]) > 0.20,
          "gold_anchored-nochain=+%.3f (parent gold_nom->gold +0.26)" % (a["ga"] - a["noc"]))

    # W4 -- HEADLINE: chaining lifts he/she who-has-what CI-separated over the no-chaining floor
    d4 = paired(by_midx(ch), by_midx(noc), 2000, 7)
    check("W4_chain_beats_nochain_CIsep", d4["CIsep"] and d4["delta"] > 0,
          "chain-nochain=+%.4f %s" % (d4["delta"], d4["ci"]))

    # W5 -- shuffled-chain TWIN loses (maintained IDENTITY does the work, not the machinery)
    K = 80
    tw = []
    for k in range(K):
        r = np.random.default_rng(100 + k)
        hits = tot = 0
        for d in docs:
            rr = online_resolve(d["mentions"], grouping="gold_nom", chain_mode="hard", shuffle_rng=r)
            hits += sum(x["correct"] for x in rr); tot += len(rr)
        tw.append(hits / tot)
    p95 = float(np.percentile(tw, 95))
    check("W5_shuffled_twin_loses", a["ch"] > p95, "chain=%.3f > twin_p95=%.3f" % (a["ch"], p95))

    # W6 -- LONG-DISTANCE re-instatement: the gain is concentrated FAR from the nominal anchor (brief item 4)
    from hdlab.coref import sent_dist_bucket
    ncb = {(r["_doc"], r["midx"]): r for r in noc}
    chb = {(r["_doc"], r["midx"]): r for r in ch}
    near = {"n": 0, "noc": 0, "ch": 0}; far = {"n": 0, "noc": 0, "ch": 0}
    for k, nr in ncb.items():
        cr = chb.get(k)
        if cr is None or nr["nom_dist"] < 0:
            continue
        b = sent_dist_bucket(nr["nom_dist"])
        tgt = near if b in ("same", "plus1") else far
        tgt["n"] += 1; tgt["noc"] += nr["correct"]; tgt["ch"] += cr["correct"]
    fg = (far["ch"] - far["noc"]) / far["n"]
    ng = (near["ch"] - near["noc"]) / near["n"]
    check("W6_long_distance_reinstatement", fg > 0.10 and fg > ng,
          "far gain=+%.3f (n=%d) >> near gain=%+.3f (n=%d)" % (fg, far["n"], ng, near["n"]))

    # W7 -- SOFT (hold-both) maintenance LOSES to HARD commit (attractor settling, not superposition)
    d7 = paired(by_midx(sf), by_midx(ch), 2000, 8)
    check("W7_soft_loses_to_hard", d7["delta"] < 0, "soft-hard=%.4f %s" % (d7["delta"], d7["ci"]))

    # W8 -- residual is PICK reliability: an ORACLE-gated chain (propagate only correct picks) beats the real chain
    check("W8_residual_is_pick_reliability", a["orc"] > a["ch"] and a["ga"] > a["orc"],
          "oracle=%.3f > chain=%.3f ; gold=%.3f > oracle (missed reinforcement)" % (a["orc"], a["ch"], a["ga"]))

    # W9 -- GENERALIZATION: object-'it' chaining reproduces the mechanism (twin loses; long-distance signature)
    odocs = OBJ.load_docs(files)
    o_noc = [r for d in odocs for r in OBJ.online_resolve_obj(d["mentions"], chain_mode="none")]
    o_ch = [r for d in odocs for r in OBJ.online_resolve_obj(d["mentions"], chain_mode="hard")]
    otw = []
    for k in range(60):
        r = np.random.default_rng(500 + k)
        hits = tot = 0
        for d in odocs:
            rr = OBJ.twin_pass(d["mentions"], r)
            hits += sum(rr); tot += len(rr)
        otw.append(hits / tot if tot else 0.0)
    o_ch_acc = acc(o_ch); o_p95 = float(np.percentile(otw, 95))
    check("W9_object_generalization", o_ch_acc >= acc(o_noc) and o_ch_acc > o_p95,
          "object chain=%.3f >= nochain=%.3f, > twin_p95=%.3f" % (o_ch_acc, acc(o_noc), o_p95))

    # W10 -- PICK x MAINTENANCE: the maintenance loop needs the near-optimal GRADED pick; over the incumbent rigid
    # hard-tier pick, chaining does NOT help (in fact hurts) -- the recurrence and the ACT-R pick are coupled.
    def pm(mode, pmode):
        return acc([r for di in docs for r in online_resolve(di["mentions"], grouping="gold_nom", chain_mode=mode, pick_mode=pmode)])
    g_gain = pm("hard", "graded") - pm("none", "graded")
    h_gain = pm("hard", "hardtier") - pm("none", "hardtier")
    check("W10_maintenance_needs_graded_pick", g_gain > 0.03 and h_gain < g_gain and h_gain <= 0.0,
          "graded gain=+%.3f ; hard-tier gain=%+.3f (chaining helps graded, not the rigid tier)" % (g_gain, h_gain))

    # W11 -- DECAY-d ROBUSTNESS: the chain gain holds across the brain-plausible decay range (d=2..4) and REQUIRES
    # decay to exist (at d=1, near-no-decay, it flips) -- the lever exists because memory fades (ACT-R d>0).
    def dgain(dd):
        return acc([r for di in docs for r in online_resolve(di["mentions"], grouping="gold_nom", chain_mode="hard", d=dd)]) \
               - acc([r for di in docs for r in online_resolve(di["mentions"], grouping="gold_nom", chain_mode="none", d=dd)])
    g2, g4, g1 = dgain(2.0), dgain(4.0), dgain(1.0)
    check("W11_decay_robustness", g2 > 0 and g4 > 0 and g1 <= 0,
          "gain@d2=+%.3f @d4=+%.3f @d1=%+.3f (robust across plausible decay; needs decay)" % (g2, g4, g1))

    npass = sum(1 for _n, ok, _d in RESULTS if ok)
    print("\n%d/%d checks PASS" % (npass, len(RESULTS)), flush=True)
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
