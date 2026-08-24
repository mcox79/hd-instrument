"""Calibrate the orthographic floor for the per_row_gain_c3_vet_v1 harness, on ITS OWN items /
pool / gold / scorer, then re-grade its past results against the honest floor.

WHY THIS EXISTS. tools/per_row_gain_c3_vet_v1.py owns no A6_TRIGRAM_ONLY arm. Once the gold was
morphology-stripped (owner ruling Q117), it had no honest floor to gate against and now REFUSES to
issue a verdict (prints [BAR NOT CALIBRATED ...], returns 3). The standing rule forbids pasting the
sibling tool's 0.019500 across: that number belongs to score_space_gain_and_topk_ci_v1.py's own
bootstrap seed, and no number crosses scorers or populations. So the floor must be MEASURED HERE.

WHAT THIS SCRIPT MEASURES, all in per_row_gain's exact harness (it imports the tool's own _gold,
build_excitability_E, and the same C3 corpus/space/items + MS.trigram_matrix the sibling uses):
  - A1_BASE on stripped gold           -- the real read-out; also the harness-identity check.
  - the full per-row-gain arm set       -- to re-grade "does gain clear the floor" honestly.
  - A6_TRIGRAM_ONLY on stripped gold     -- THE FLOOR. This is the number the tool must gate on.
  - two INFORMATION-FREE twins of it:
        A6_TRIGRAM_DONORQ  (query = a DIFFERENT word's spelling; mirrors the existing SCRAMBLE arm)
        A6_TRIGRAM_ROWPERM (candidate spellings permuted across identities)
    If the honest floor cannot be separated from its own twin, the gate cannot separate anything at
    this level -- which the brief names as an explicit PASS, and it is what the stripped floor
    already did once (c3_surprise: [0.0153,0.0238] overlapped its twin [0.0135,0.0213]).
  - a void_plumbing GUARD (recompute the floor, require it to equal the constant) + everything the
    proposed constant would be set to.

THIS SCRIPT WIRES NOTHING AND EDITS NO TOOL. It writes only to its own data dir. The proposed edit
to tools/per_row_gain_c3_vet_v1.py is stated in
notes/problems/the_gate_cannot_measure_its_own_floor/SOLVED.md; the strategy session lands it.

Run:  .venv/Scripts/python.exe experiments/exp_per_row_gain_trigram_floor_calibration_v1.py [--smoke]
Output: data/exp_per_row_gain_trigram_floor_calibration_v1[_smoke]/metrics.json (atomic os.replace).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import hdlab.excitability as EXC  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
import tools.per_row_gain_c3_vet_v1 as PRG  # noqa: E402  -- reuse the TOOL'S OWN _gold + excitability

SMOKE = "--smoke" in sys.argv
ANCHOR_NAME = "exp_per_row_gain_trigram_floor_calibration_v1" + ("_smoke" if SMOKE else "")
# Owner ruling Q115 (2026-08-23), enforced by the pre-commit hook: obtain the output directory
# from the shared helper, never by hand. A hand-built path does not match the runner's convention
# and a re-run REPLAYS the saved answer instead of recomputing it -- so "I re-ran it and got the
# same number" would prove nothing. That matters more here than almost anywhere else: this cell
# exists to let the gate RE-MEASURE its own floor, and a floor that cannot be honestly recomputed
# is exactly the thing the whole Q117 fix was about.
from experiments._seed_checkpoint import get_output_dir  # noqa: E402

OUT = str(get_output_dir(ANCHOR_NAME))
os.makedirs(OUT, exist_ok=True)

SELF_RETRIEVAL_FLOOR = 0.70
# A1_BASE on stripped gold, as the sibling harness reads it. Used ONLY as the guard's expected
# value; the guard requires the value MEASURED HERE to match it, and reports a mismatch rather than
# trusting either. 0.048 is the LEAKY (unstripped) headline and must NOT be the expectation here.
A1_BASE_EXPECTED_STRIPPED = 0.04575
# The legacy leaky bar, kept ONLY for the side-by-side re-grade. Never a gate.
LEGACY_LEAKY_BAR = (0.0870, (0.0783, 0.0960))
BOOT_SEED = C3.MASTER_SEED + 51        # == 20260865, reproduces per_row_gain's own arm CIs exactly


def _boot_pcts(hitarr: np.ndarray, seed: int, pcts, n_boot: int = 5000) -> Dict[str, float]:
    """Percentiles of an arm's accuracy under the item bootstrap (for the twin's null p95)."""
    n = len(hitarr)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = hitarr[idx].mean(axis=1)
    return {("p%s" % p): float(np.percentile(boots, p)) for p in pcts}


def void_plumbing_check(measured_a6: float, ortho_bar, a1_base: float, self_retrieval: float) -> dict:
    """Recompute-and-refuse guard, mirroring score_space_gain_and_topk_ci_v1.py::void_plumbing.

    A constant nobody re-derives drifts silently. This recomputes the floor in-harness and requires
    it to equal the constant to 1e-9; it also requires A1_BASE to reproduce the stripped-gold
    headline and self-retrieval to clear its floor. `void=True` means DO NOT GATE.
    """
    a6_matches_bar = (ortho_bar is not None) and abs(measured_a6 - ortho_bar) < 1e-9
    a1_matches_headline = abs(a1_base - A1_BASE_EXPECTED_STRIPPED) < 1e-9
    sr_ok = self_retrieval >= SELF_RETRIEVAL_FLOOR
    void = bool((ortho_bar is None) or (not a6_matches_bar) or (not a1_matches_headline) or (not sr_ok))
    return {
        "a6_trigram_reproduces_constant_to_1e-9": a6_matches_bar,
        "a1_base_reproduces_stripped_headline_to_1e-9": a1_matches_headline,
        "self_retrieval_ok": sr_ok,
        "ortho_bar_constant": ortho_bar,
        "measured_a6": measured_a6,
        "void": void,
    }


def main() -> int:
    t0 = time.time()
    sents = C3.build_corpus("smoke" if SMOKE else "full")
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, OUT)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    max_items = 200 if SMOKE else C3.MAX_ITEMS
    items, diag = C3.build_items(space, buckets, counts, max_items)
    n = len(items)
    print("[recompute] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0),
          flush=True)

    mat_nrm_base = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm_base >= 1e-9

    # ---- per_row_gain's exact arm matrices (verbatim construction; gain is per-anchor-row) -------
    E = PRG.build_excitability_E(anchors, counts, pos)
    med_E = float(np.median(E))
    rng = np.random.default_rng(C3.MASTER_SEED + 31)

    mats: Dict[str, np.ndarray] = {"A1_BASE": mat}
    m = mat.copy()
    n_hit_e_thresh = EXC.downscale_gate_by_E(m, E, scale=0.4, threshold=med_E)
    mats["PER_ROW_GAIN_E_THRESH"] = m
    m = mat.copy(); m *= (0.5 + 1.5 * E)[:, None]; mats["PER_ROW_GAIN_E_CONTINUOUS"] = m
    m = mat.copy()
    frac_matched = min(max(max(1, n_hit_e_thresh) / max(1, n_anchors), 0.01), 0.99)
    EXC.downscale_gate_random(m, frac=frac_matched, scale=0.4, rng=np.random.RandomState(7))
    mats["PER_ROW_GAIN_RANDOM"] = m
    m = mat.copy(); EXC.downscale_gate_by_magnitude(m, threshold_frac=frac_matched, scale=0.4)
    mats["PER_ROW_GAIN_MAGNITUDE"] = m
    m = mat.copy(); m *= 1.7; mats["GLOBAL_SCALAR"] = m
    col_std = np.std(mat, axis=0)
    gain_dim = 1.0 / np.maximum(col_std, 1e-9)
    gain_dim = gain_dim / float(np.mean(gain_dim))
    m = mat.copy(); m *= gain_dim[None, :]; mats["PER_RAW_DIM_INV_STD"] = m
    gain_dim_shuf = gain_dim.copy(); rng.shuffle(gain_dim_shuf)
    m = mat.copy(); m *= gain_dim_shuf[None, :]; mats["PER_RAW_DIM_RANDOM"] = m
    norms = {k: np.linalg.norm(v, axis=1) for k, v in mats.items()}
    gain_arms = tuple(k for k in mats if k != "A1_BASE")

    # ---- the FLOOR arm and its two information-free twins ----------------------------------------
    t_mat, t_cov = MS.trigram_matrix(anchors)
    perm = np.random.default_rng(C3.MASTER_SEED + 777).permutation(n_anchors)
    t_mat_perm = t_mat[perm]           # each identity now wears a DIFFERENT word's spelling
    trigram_arms = ("A6_TRIGRAM_ONLY", "A6_TRIGRAM_DONORQ", "A6_TRIGRAM_ROWPERM")

    meaning_arms = ("A1_BASE",) + gain_arms + ("SCRAMBLE",)
    all_arms = meaning_arms + trigram_arms
    hits = {a: np.zeros(n, dtype=bool) for a in all_arms}
    scored = np.zeros(n, dtype=bool)
    identical_to_base = {a: np.zeros(n, dtype=bool) for a in gain_arms}

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    donors = C3._derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                                 & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)
    anchor_arr = np.array(anchors)

    def _hit(sc, sel, gold):
        return str(anchor_arr[sel[int(np.argmax(sc))]]) in gold

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        elig &= mat_ok
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        gold = PRG._gold(L)                                  # the TOOL'S OWN stripped gold

        qL = space.bundle(L); qLn = float(np.linalg.norm(qL))
        Ld = items[donors[i]]["L"]
        qD = space.bundle(Ld); qDn = float(np.linalg.norm(qD))
        if qLn < 1e-9:
            continue
        scored[i] = True

        base_scores = None; base_pick = None
        for a in meaning_arms:
            if a == "SCRAMBLE":
                if qDn < 1e-9:
                    continue
                sc = (mats["A1_BASE"][sel] @ qD) / (norms["A1_BASE"][sel] * qDn)
            else:
                sc = (mats[a][sel] @ qL) / (norms[a][sel] * qLn)
            hits[a][i] = _hit(sc, sel, gold)
            if a == "A1_BASE":
                base_scores = sc; base_pick = str(anchor_arr[sel[int(np.argmax(sc))]])
            elif a != "SCRAMBLE":
                p = str(anchor_arr[sel[int(np.argmax(sc))]])
                identical_to_base[a][i] = (p == base_pick) and bool(
                    np.allclose(sc, base_scores, atol=1e-6, rtol=1e-6))

        # A6_TRIGRAM_ONLY: L's own spelling as query
        tqL = t_mat[pos[L]] if t_cov[pos[L]] else None
        sc = t_mat[sel] @ tqL if tqL is not None else np.zeros(sel.size)
        hits["A6_TRIGRAM_ONLY"][i] = _hit(sc, sel, gold)
        # DONORQ twin: a DIFFERENT word's spelling as query (query decoupled from L)
        tqD = t_mat[pos[Ld]] if t_cov[pos[Ld]] else None
        sc = t_mat[sel] @ tqD if tqD is not None else np.zeros(sel.size)
        hits["A6_TRIGRAM_DONORQ"][i] = _hit(sc, sel, gold)
        # ROWPERM twin: candidate spellings permuted across identities (spelling decoupled from id)
        sc = t_mat_perm[sel] @ tqL if tqL is not None else np.zeros(sel.size)
        hits["A6_TRIGRAM_ROWPERM"][i] = _hit(sc, sel, gold)

        if (i + 1) % 500 == 0:
            print("[score] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    # ---- KNOWN_ANSWER positive control (verbatim reuse of C3 construction) -----------------------
    from hdlab.reading_grounding_loop import context_vector_masked
    rng_sr = np.random.default_rng(C3.MASTER_SEED + 41)
    sr_hits, sr_n = 0, 0
    for it in items[:min(300, n)]:
        L = it["L"]
        if it["sent_idx"] is None:
            continue
        other = anchors[int(rng_sr.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or C3._is_variant(other, L)):
            other = anchors[int(rng_sr.integers(len(anchors)))]; tries += 1
        if other == L:
            continue
        q = context_vector_masked(sents[it["sent_idx"]], L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        cand = [pos[L], pos[other]]
        sc = (mat[cand] @ q) / (mat_nrm_base[cand] * qn)
        sr_hits += int(sc[0] >= sc[1]); sr_n += 1
    self_retrieval = round(sr_hits / max(1, sr_n), 6)

    # ---- CIs (per_row_gain's own bootstrap seed) + deltas vs base --------------------------------
    armv = {a: hits[a].astype(float) for a in all_arms}
    deltas = [("d_%s_minus_BASE" % a, a, "A1_BASE") for a in gain_arms] + \
             [("d_SCRAMBLE_minus_BASE", "SCRAMBLE", "A1_BASE"),
              ("d_A6_TRIGRAM_ONLY_minus_DONORQ", "A6_TRIGRAM_ONLY", "A6_TRIGRAM_DONORQ"),
              ("d_A6_TRIGRAM_ONLY_minus_ROWPERM", "A6_TRIGRAM_ONLY", "A6_TRIGRAM_ROWPERM")]
    bs = MS.paired_bootstrap(armv, deltas, 5000, BOOT_SEED)
    acc = bs["arm_acc_ci"]

    def hw(a):     # CI half-width
        c = acc[a]; return round((c["ci_hi"] - c["ci_lo"]) / 2.0, 6)

    measured_a6 = acc["A6_TRIGRAM_ONLY"]["acc"]
    a1_base = acc["A1_BASE"]["acc"]

    # ---- the floor vs its info-free twins: margin + null p95 -------------------------------------
    twin_p = {t: _boot_pcts(hits[t].astype(float), BOOT_SEED + 13 + j, (50, 95, 97.5))
              for j, t in enumerate(("A6_TRIGRAM_DONORQ", "A6_TRIGRAM_ROWPERM"))}
    floor_separates_donorq = bool(acc["A6_TRIGRAM_ONLY"]["ci_lo"] > twin_p["A6_TRIGRAM_DONORQ"]["p95"])
    floor_separates_rowperm = bool(acc["A6_TRIGRAM_ONLY"]["ci_lo"] > twin_p["A6_TRIGRAM_ROWPERM"]["p95"])

    # ---- the void_plumbing guard, run at the value we would set the constant to ------------------
    proposed_ortho_bar = round(measured_a6, 6)
    proposed_ortho_bar_ci = (round(acc["A6_TRIGRAM_ONLY"]["ci_lo"], 6),
                             round(acc["A6_TRIGRAM_ONLY"]["ci_hi"], 6))
    guard_at_correct = void_plumbing_check(measured_a6, proposed_ortho_bar, a1_base, self_retrieval)
    guard_at_wrong = void_plumbing_check(measured_a6, LEGACY_LEAKY_BAR[0], a1_base, self_retrieval)

    # ---- the honest re-grade: does each arm clear the floor, LEAKY vs HONEST ---------------------
    bar_lo_honest = proposed_ortho_bar_ci[1]           # gate on the floor's UPPER CI bound
    bar_lo_leaky = LEGACY_LEAKY_BAR[1][1]              # 0.0960
    regrade = {}
    for a in ("A1_BASE",) + gain_arms:
        regrade[a] = {
            "acc_stripped_gold": acc[a]["acc"], "ci_lo": acc[a]["ci_lo"], "ci_hi": acc[a]["ci_hi"],
            "ci_halfwidth": hw(a),
            "clears_HONEST_floor_%.4f" % bar_lo_honest: bool(acc[a]["ci_lo"] > bar_lo_honest),
            "would_clear_LEAKY_floor_%.4f" % bar_lo_leaky: bool(acc[a]["ci_lo"] > bar_lo_leaky),
            "delta_vs_base": bs["deltas"].get("d_%s_minus_BASE" % a, {}).get("delta")
            if a != "A1_BASE" else 0.0,
            "delta_ci_excludes_zero": bs["deltas"].get("d_%s_minus_BASE" % a, {}).get("ci_excludes_zero")
            if a != "A1_BASE" else None,
        }

    rep = {
        "anchor_name": ANCHOR_NAME,
        "what": "Calibrate the A6_TRIGRAM_ONLY orthographic floor IN the per_row_gain_c3_vet_v1 "
                "harness (its own _gold/pool/scorer + MS.trigram_matrix), measure two info-free "
                "twins, run the recompute-and-refuse guard, and re-grade the past results honestly.",
        "reuses": "tools.per_row_gain_c3_vet_v1._gold + build_excitability_E; C3 corpus/space/items; "
                  "MS.trigram_matrix + paired_bootstrap; bootstrap seed MASTER_SEED+51 (== per_row_gain)",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "smoke": SMOKE, "n_items_scored": int(scored.sum()), "n_items": n, "n_anchors": n_anchors,
        "item_construction": diag,
        "USE_MORPH_STRIPPED_GOLD": PRG.USE_MORPH_STRIPPED_GOLD,
        "self_retrieval": {"acc": self_retrieval, "n": sr_n, "floor": SELF_RETRIEVAL_FLOOR,
                           "ok": self_retrieval >= SELF_RETRIEVAL_FLOOR},
        "harness_identity_check": {
            "a1_base_stripped": a1_base, "expected_stripped_headline": A1_BASE_EXPECTED_STRIPPED,
            "matches_sibling_harness_to_1e-9": abs(a1_base - A1_BASE_EXPECTED_STRIPPED) < 1e-9},
        "THE_CALIBRATED_FLOOR": {
            "arm": "A6_TRIGRAM_ONLY", "acc": measured_a6,
            "ci": [acc["A6_TRIGRAM_ONLY"]["ci_lo"], acc["A6_TRIGRAM_ONLY"]["ci_hi"]],
            "ci_halfwidth": hw("A6_TRIGRAM_ONLY"),
            "PROPOSED_ORTHO_BAR": proposed_ortho_bar,
            "PROPOSED_ORTHO_BAR_CI": list(proposed_ortho_bar_ci)},
        "floor_vs_info_free_twins": {
            "A6_TRIGRAM_DONORQ": {"acc": acc["A6_TRIGRAM_DONORQ"]["acc"],
                                  "ci": [acc["A6_TRIGRAM_DONORQ"]["ci_lo"], acc["A6_TRIGRAM_DONORQ"]["ci_hi"]],
                                  "null_p95": twin_p["A6_TRIGRAM_DONORQ"]["p95"]},
            "A6_TRIGRAM_ROWPERM": {"acc": acc["A6_TRIGRAM_ROWPERM"]["acc"],
                                   "ci": [acc["A6_TRIGRAM_ROWPERM"]["ci_lo"], acc["A6_TRIGRAM_ROWPERM"]["ci_hi"]],
                                   "null_p95": twin_p["A6_TRIGRAM_ROWPERM"]["p95"]},
            "floor_ci_lo": acc["A6_TRIGRAM_ONLY"]["ci_lo"],
            "floor_separates_from_donorq_twin": floor_separates_donorq,
            "floor_separates_from_rowperm_twin": floor_separates_rowperm,
            "delta_floor_minus_donorq": bs["deltas"]["d_A6_TRIGRAM_ONLY_minus_DONORQ"],
            "delta_floor_minus_rowperm": bs["deltas"]["d_A6_TRIGRAM_ONLY_minus_ROWPERM"]},
        "void_plumbing_guard": {
            "at_correct_constant_should_be_void_false": guard_at_correct,
            "at_wrong_constant_0.0870_should_be_void_true": guard_at_wrong,
            "guard_fires_on_wrong_constant": guard_at_wrong["void"] is True,
            "guard_passes_on_correct_constant": guard_at_correct["void"] is False},
        "RE_GRADE_leaky_vs_honest": {
            "leaky_floor": {"acc": LEGACY_LEAKY_BAR[0], "ci": list(LEGACY_LEAKY_BAR[1]),
                            "gold": "unstripped (~78% morphological leakage)"},
            "honest_floor": {"acc": proposed_ortho_bar, "ci": list(proposed_ortho_bar_ci),
                             "gold": "morphology-stripped"},
            "per_arm": regrade},
        "bitwise_identical_pick_fraction_vs_A1_BASE": {a: float(identical_to_base[a].mean())
                                                       for a in gain_arms},
        "bootstrap": bs,
        "scored_population_L": [items[i]["L"] for i in range(n) if scored[i]],
        "hit_arrays": {a: hits[a].astype(int).tolist()
                       for a in ("A1_BASE", "A6_TRIGRAM_ONLY", "A6_TRIGRAM_DONORQ", "A6_TRIGRAM_ROWPERM")},
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(OUT, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)

    print("A1_BASE (stripped):", a1_base, "expected", A1_BASE_EXPECTED_STRIPPED)
    print("A6_TRIGRAM_ONLY floor:", measured_a6, "CI", proposed_ortho_bar_ci, "hw", hw("A6_TRIGRAM_ONLY"))
    print("  DONORQ twin:", acc["A6_TRIGRAM_DONORQ"]["acc"], "p95", twin_p["A6_TRIGRAM_DONORQ"]["p95"],
          "-> floor separates:", floor_separates_donorq)
    print("  ROWPERM twin:", acc["A6_TRIGRAM_ROWPERM"]["acc"], "p95", twin_p["A6_TRIGRAM_ROWPERM"]["p95"],
          "-> floor separates:", floor_separates_rowperm)
    print("SELF_RETRIEVAL:", self_retrieval, "(floor 0.70)")
    print("GUARD fires on wrong constant 0.0870:", guard_at_wrong["void"],
          "| passes on correct:", not guard_at_correct["void"])
    print("RE-GRADE A1_BASE: clears HONEST floor",
          regrade["A1_BASE"]["clears_HONEST_floor_%.4f" % bar_lo_honest],
          "| would clear LEAKY floor",
          regrade["A1_BASE"]["would_clear_LEAKY_floor_%.4f" % bar_lo_leaky])
    print("WROTE", p)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        _crash = os.path.join(OUT, "_crash_diagnostic.json")
        with open(_crash + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME, "error": "%s: %s" % (type(exc).__name__, exc),
                       "traceback": traceback.format_exc(),
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        os.replace(_crash + ".tmp", _crash)
        raise
