"""exp_near_vs_far_diagnostic_v1 -- does the ONE arm that carried signal survive on the
distinction the substrate actually needs?

PRE-REG: preregs/2026-08-13_near_vs_far_diagnostic.md, committed BEFORE this file ran and BEFORE
any split was scored. Every split definition, the power gate and the three reads are frozen there.

PARENT: experiments/exp_differentia_feature_supply_v1.py
MEASURED@data/exp_differentia_feature_supply_v1/metrics.json:rho_primary (n=350, UNIFORM):
    A_DIFFERENTIA 0.0247 | B_GENUS_ONLY 0.0179 | B_STRICT_GENUS -0.0464
    C_GROUNDED_RAW 0.2759 | D_CSKG_NOLEXREL 0.0751 | E_SCRAMBLE -0.0235

Every symbolic arm is at chance; the graded sensorimotor channel scored 0.2759. But
CITED@hdlab/grounded_similarity.py:23-38 ("HONEST, MEASURED LIMIT") that channel CANNOT separate
sofa/couch (0.968) from apple/orange (0.952). If the 0.2759 comes from far-apart pairs and
collapses on near-neighbours, nothing we own works on the real wall.

NOTHING UNDER hdlab/ AND NOTHING IN THE PARENT CELL IS MODIFIED. The pair set, the arms, the
comparator and the bootstrap are all the PARENT'S OWN CODE, imported. The only new machinery is
the WordNet-based partition and the per-half reporting.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-arm score-vector sha256)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes SEPARATE output dirs
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a declared (pre-reg 7); power statement is the paired bootstrap, reported as per-half
#   mde_95 = 1.96 * bootstrap sd, plus a HARD n>=50 gate per half
# - discriminator survives scale: multi-scale smoke (120 / 480 pairs) + FULL at all 350
# - cardinality_ok: EXPECTED_N_UNITS = 6 arms x 8 half-cells = 48, gated in the verdict
# - per-unit failure-class instrumentation (META_RULE_J); no bare except
# - deterministic seeding: fixed ints + hashlib only; no builtin hash(), no list(set())
# - positive control: the re-derived pair set MUST reproduce the parent's n and every rho
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy/torch import (they size their pools at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import csv
import hashlib
import json
import platform
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nltk.corpus import wordnet as wn                                    # noqa: E402

from hdlab.grounded_similarity import (                                  # noqa: E402
    _raw_cos as grounded_raw_cos, grounded_vector, in_grounded_lexicon,
)
# REUSE, not re-implementation: the pair set, the arms, the comparator and the bootstrap are the
# PARENT's own code. Importing it also runs the parent's module-scope self-test before we start.
from experiments.exp_differentia_feature_supply_v1 import (              # noqa: E402
    BOOTSTRAP_SEED, N_BOOTSTRAP, _rho, delta_ci, leak_controls, load_treatment_store,
    load_v6_genus, make_supply, paired_bootstrap, supply_scores,
)
from experiments.exp_distinctiveness_weighted_composition_v1 import (    # noqa: E402
    _scrambled_assignment, build_supply, get_cskg_cache, load_simlex,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

# ---------------------------------------------------------------------------------------------
# CONFIG -- pre-registered. Nothing here is adjusted after seeing a result.
# ---------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_near_vs_far_diagnostic_v1"
PREREG_PATH = "preregs/2026-08-13_near_vs_far_diagnostic.md"
PARENT_METRICS = os.path.join(REPO_ROOT, "data", "exp_differentia_feature_supply_v1",
                              "metrics.json")
SIMLEX_PATH = os.path.join(REPO_ROOT, "data", "encoder_eval_benchmarks", "simlex999.txt")

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

ARMS = ("A", "B", "B_STRICT", "C", "D", "E")          # 6 arms; A/B/C/D/E are the brief's five
ARM_LABEL = {"A": "A_DIFFERENTIA", "B": "B_GENUS_ONLY", "B_STRICT": "B_STRICT_GENUS",
             "C": "C_GROUNDED_RAW", "D": "D_CSKG_NOLEXREL", "E": "E_SCRAMBLE"}
SYMBOLIC_ARMS = ("A", "B", "D")                        # the "do symbols work coarsely?" question

SPLIT_HALVES = (("SPLIT1_TAXONOMIC", ("NEAR", "FAR")),
                ("SPLIT1B_WN_PATH_MEDIAN", ("NEAR_G", "FAR_G")),
                ("SPLIT2_HUMAN_RATING", ("HIGH", "LOW")),
                ("SPLIT3_CONCRETENESS", ("CONCRETE", "ABSTRACT")))
EXPECTED_N_UNITS = len(ARMS) * sum(len(h) for _, h in SPLIT_HALVES)      # 6 * 8 = 48

MIN_HALF_N = 50                  # pre-reg 5: HARD power gate; below this NO READ is drawn
SMOKE_PAIR_SCALES = (120, 480)   # multi-scale smoke; pair count is the statistic's load axis

# Positive control (pre-reg 2 / SCHEMA-VET gate D): the re-derived set must BE the parent's set.
PARENT_RHO = {"A": 0.0247, "B": 0.0179, "B_STRICT": -0.0464, "C": 0.2759, "D": 0.0751,
              "E": -0.0235}    # MEASURED@data/exp_differentia_feature_supply_v1/metrics.json
PARENT_N = 350                 # MEASURED@same:n_surviving_pairs
PARENT_TOL = 1e-4              # rho_primary is stored rounded to 4dp, so this is exact-match

_WN_POS = {"N": "n", "V": "v", "A": "as"}      # SimLex POS -> WordNet pos; 'as' = ADJ + ADJ_SAT


# ---------------------------------------------------------------------------------------------
# Durability plumbing (same shape as the parent)
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _heartbeat(output_dir: str, unit_idx: int, total_units: int, elapsed_s: float,
               extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 3)}
    if extra:
        row["extra"] = extra
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)          # META_RULE_AH
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "run_mode": "crash", "failure_class": type(exc).__name__,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME})


# ---------------------------------------------------------------------------------------------
# SimLex side fields (POS / concQ) -- the gold itself still comes from the parent's load_simlex
# ---------------------------------------------------------------------------------------------
def load_simlex_fields() -> Dict[Tuple[str, str], dict]:
    out: Dict[Tuple[str, str], dict] = {}
    with open(SIMLEX_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            out[(row["word1"], row["word2"])] = {
                "pos": row["POS"], "gold": float(row["SimLex999"]),
                "concQ": int(row["concQ"]),
                "conc_mean": round((float(row["conc(w1)"]) + float(row["conc(w2)"])) / 2.0, 4),
                "assoc_usf": float(row["Assoc(USF)"])}
    return out


# ---------------------------------------------------------------------------------------------
# SPLIT 1 / 1B -- WordNet 3.0. EXTERNAL to every arm (pre-reg 3).
# ---------------------------------------------------------------------------------------------
_SYNSET_CACHE: Dict[Tuple[str, str], list] = {}


def _synsets(word: str, pos: str) -> list:
    key = (word, pos)
    if key not in _SYNSET_CACHE:
        ss = wn.synsets(word, pos)              # 'as' iterates ADJ then ADJ_SAT (nltk semantics)
        if not ss:
            ss = wn.synsets(word)               # declared fallback: all POS
        _SYNSET_CACHE[key] = ss
    return _SYNSET_CACHE[key]


def taxonomic_nearness(a: str, b: str, pos: str) -> dict:
    """PRE-REGISTERED SPLIT 1. NEAR iff N1 (shared synset = synonyms) OR N2 (shared DIRECT
    hypernym = co-hyponyms/siblings) OR N3 (adjectives only: same similar_to cluster).

    Also returns wnsim = max path_similarity over synset pairs (SPLIT 1B's statistic).
    Parent/child hypernym pairs are NOT counted NEAR -- the pre-reg says siblings-or-synonyms."""
    wp = _WN_POS.get(pos, None)
    sa = _synsets(a, wp) if wp else wn.synsets(a)
    sb = _synsets(b, wp) if wp else wn.synsets(b)
    fallback = bool(wp) and (not wn.synsets(a, wp) or not wn.synsets(b, wp))
    na, nb = {s.name() for s in sa}, {s.name() for s in sb}
    n1 = bool(na & nb)
    ha = {h.name() for s in sa for h in s.hypernyms()}
    hb = {h.name() for s in sb for h in s.hypernyms()}
    n2 = bool(ha & hb)
    n3 = False
    if pos == "A":
        sim_a = {t.name() for s in sa for t in s.similar_tos()}
        sim_b = {t.name() for s in sb for t in s.similar_tos()}
        n3 = bool(sim_a & nb) or bool(sim_b & na)
    best = None
    for x in sa:
        for y in sb:
            v = x.path_similarity(y)            # None across POS; max over defined values
            if v is not None and (best is None or v > best):
                best = float(v)
    return {"near": bool(n1 or n2 or n3), "N1_synonym": n1, "N2_cohyponym": n2,
            "N3_adj_cluster": n3, "n3_alone": bool(n3 and not (n1 or n2)),
            "wnsim": best, "pos_fallback": fallback,
            "n_synsets_a": len(sa), "n_synsets_b": len(sb)}


# ---------------------------------------------------------------------------------------------
# Per-half scoring
# ---------------------------------------------------------------------------------------------
def score_half(arm_scores: Dict[str, List[float]], golds: List[float], idx: List[int],
               n_boot: int) -> Dict[str, dict]:
    """rho + 95% percentile paired-bootstrap CI + sd + mde_95 for every arm, on the SAME
    resampled index sets (the arms are dependent correlations)."""
    g = [golds[i] for i in idx]
    sub = {k: [v[i] for i in idx] for k, v in arm_scores.items()}
    rho = {k: _rho(v, g) for k, v in sub.items()}
    if len(idx) < 3 or float(np.asarray(g).std()) == 0.0:
        return {k: {"rho": round(rho[k], 4), "n": len(idx), "ci_lo": None, "ci_hi": None,
                    "sd": None, "mde_95": None, "ci_excludes_zero": None,
                    "failure_class": "HALF_TOO_SMALL_TO_SCORE"} for k in sub}
    bs, boot = paired_bootstrap(sub, g, n_boot, BOOTSTRAP_SEED)
    out = {}
    for k in sub:
        ci = bs["arm_ci"][k]
        out[k] = {"rho": round(rho[k], 4), "n": len(idx),
                  "ci_lo": round(ci["lo"], 4), "ci_hi": round(ci["hi"], 4),
                  "sd": round(ci["sd"], 4), "mde_95": round(1.96 * ci["sd"], 4),
                  "ci_excludes_zero": bool(ci["lo"] > 0.0 or ci["hi"] < 0.0),
                  "n_boot_used": bs["n_boot_used"], "failure_class": None}
    return out


# ---------------------------------------------------------------------------------------------
# The frozen reads (pre-reg 6)
# ---------------------------------------------------------------------------------------------
def decide_read(table: dict, near_key: str, far_key: str, split: str) -> Tuple[str, List[str]]:
    c_near = table[split][near_key]["C"]
    c_far = table[split][far_key]["C"]
    notes = ["read source = %s (NEAR n=%d, FAR n=%d)"
             % (split, c_near["n"], c_far["n"])]
    near_null = (c_near["ci_excludes_zero"] is False)
    far_pos = bool(c_far["ci_excludes_zero"]) and c_far["rho"] > 0
    near_pos = bool(c_near["ci_excludes_zero"]) and c_near["rho"] > 0
    if near_null and far_pos:
        return "NEAR_COLLAPSE", notes + [
            "C NEAR rho=%.4f CI=[%.4f,%.4f] includes 0; C FAR rho=%.4f CI=[%.4f,%.4f] excludes 0 "
            "and is positive." % (c_near["rho"], c_near["ci_lo"], c_near["ci_hi"],
                                  c_far["rho"], c_far["ci_lo"], c_far["ci_hi"])]
    if near_pos:
        return "NEAR_SURVIVES", notes + [
            "C NEAR rho=%.4f CI=[%.4f,%.4f] excludes 0."
            % (c_near["rho"], c_near["ci_lo"], c_near["ci_hi"])]
    return "MIXED", notes + [
        "neither read fires: C NEAR rho=%.4f CI=[%.4f,%.4f], C FAR rho=%.4f CI=[%.4f,%.4f]."
        % (c_near["rho"], c_near["ci_lo"], c_near["ci_hi"],
           c_far["rho"], c_far["ci_lo"], c_far["ci_hi"])]


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY -- module scope, before any measurement)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}

    # (1) the parent's landed metrics exist and carry the numbers this cell is anchored to.
    assert os.path.exists(PARENT_METRICS), "parent metrics missing: %s" % PARENT_METRICS
    with open(PARENT_METRICS, encoding="utf-8") as f:
        pm = json.load(f)
    assert pm["n_surviving_pairs"] == PARENT_N, "parent n drifted: %r" % pm["n_surviving_pairs"]
    for k, v in PARENT_RHO.items():
        assert abs(pm["rho_primary"][k] - v) < 1e-9, (
            "parent rho drifted for %s: disk=%r constant=%r" % (k, pm["rho_primary"][k], v))
    res["parent_metrics_ok"] = True

    # (2) WordNet is live and the split criteria FIRE and DISCRIMINATE (a criterion that can never
    #     fire, or that fires on everything, is not a split).
    res["wordnet_version"] = wn.get_version()
    syn = taxonomic_nearness("sofa", "couch", "N")
    sib = taxonomic_nearness("couch", "chair", "N")
    far = taxonomic_nearness("couch", "democracy", "N")
    assert syn["near"] and syn["N1_synonym"], "N1 (synonym) does not fire on sofa/couch: %r" % syn
    assert sib["near"] and sib["N2_cohyponym"], "N2 (co-hyponym) does not fire on couch/chair"
    assert not far["near"], "split does not separate: couch/democracy came back NEAR: %r" % far
    assert (syn["wnsim"] or 0) > (far["wnsim"] or 0), (
        "wnsim not ordered: sofa/couch=%r vs couch/democracy=%r" % (syn["wnsim"], far["wnsim"]))
    adj = taxonomic_nearness("happy", "cheerful", "A")
    res["selftest_split"] = {"sofa_couch": syn["near"], "couch_chair": sib["near"],
                             "couch_democracy": far["near"], "happy_cheerful": adj["near"],
                             "wnsim_sofa_couch": syn["wnsim"], "wnsim_couch_chair": sib["wnsim"],
                             "wnsim_couch_democracy": far["wnsim"]}

    # (3) SimLex side fields load, cover all 999, and the split-3/-2 keys actually vary.
    fields = load_simlex_fields()
    assert len(fields) == 999, "SimLex side fields loaded %d rows" % len(fields)
    qs = sorted({v["concQ"] for v in fields.values()})
    assert qs == [1, 2, 3, 4], "concQ does not carry quartiles: %r" % qs
    poss = sorted({v["pos"] for v in fields.values()})
    assert poss == ["A", "N", "V"], "unexpected POS set: %r" % poss
    pairs = load_simlex()
    assert len(pairs) == 999, "parent load_simlex returned %d" % len(pairs)
    missing = [(a, b) for a, b, _ in pairs if (a, b) not in fields]
    assert not missing, "side-field keying does not match the parent's pair order: %r" % missing[:5]
    golds_match = all(abs(fields[(a, b)]["gold"] - g) < 1e-9 for a, b, g in pairs)
    assert golds_match, "side-field gold does not match the parent's gold"
    res["simlex_fields_ok"] = {"n": len(fields), "concQ_values": qs, "pos_values": poss}

    # (4) the grounded control (arm C) is live and non-sentinel, and covers the lexicon.
    graw = grounded_raw_cos(grounded_vector("sofa"), grounded_vector("couch"))
    assert graw is not None and np.isfinite(graw), "grounded raw control returned %r" % graw
    n_gnd = sum(1 for a, b, _ in pairs if in_grounded_lexicon(a) and in_grounded_lexicon(b))
    assert n_gnd >= 1, "grounded-lexicon filter eliminated ALL SimLex pairs"
    res["grounded_raw_sofa_couch"] = round(float(graw), 4)
    res["pairs_both_grounded"] = n_gnd

    # (5) the half-scorer is wired, MOVES, and separates a real correlation from a null one.
    g = list(np.linspace(0.0, 10.0, 80))
    good = [x + 0.05 * ((i * 37) % 7) for i, x in enumerate(g)]
    noise = list(np.random.default_rng(11).normal(size=80))
    idx = list(range(80))
    hs = score_half({"good": good, "noise": noise}, g, idx, 200)
    assert hs["good"]["ci_lo"] > 0.0 and hs["good"]["ci_excludes_zero"], (
        "half-scorer failed to detect a perfect correlation: %r" % hs["good"])
    assert not hs["noise"]["ci_excludes_zero"], (
        "half-scorer claims pure noise is non-null: %r" % hs["noise"])
    assert hs["good"]["mde_95"] is not None and hs["good"]["mde_95"] >= 0.0, "mde not computed"
    # a SMALL half must widen the CI -- this is the power statement being real, not decorative
    hs_small = score_half({"noise": noise}, g, idx[:12], 200)
    assert hs_small["noise"]["sd"] > hs["noise"]["sd"], (
        "CI does not widen at small n: sd(12)=%r sd(80)=%r"
        % (hs_small["noise"]["sd"], hs["noise"]["sd"]))
    res["half_scorer"] = {"good_ci_lo": hs["good"]["ci_lo"],
                          "noise_excludes_zero": hs["noise"]["ci_excludes_zero"],
                          "sd_n80": hs["noise"]["sd"], "sd_n12": hs_small["noise"]["sd"]}

    # (6) every read branch is reachable (no unreachable verdict).
    def _cell(rho, lo, hi):
        return {"C": {"rho": rho, "ci_lo": lo, "ci_hi": hi, "n": 100,
                      "ci_excludes_zero": bool(lo > 0 or hi < 0)}}
    tbl_collapse = {"S": {"NEAR": _cell(0.02, -0.15, 0.19), "FAR": _cell(0.40, 0.25, 0.55)}}
    tbl_survive = {"S": {"NEAR": _cell(0.30, 0.12, 0.48), "FAR": _cell(0.40, 0.25, 0.55)}}
    tbl_mixed = {"S": {"NEAR": _cell(0.02, -0.15, 0.19), "FAR": _cell(0.03, -0.14, 0.20)}}
    seen = sorted({decide_read(tbl_collapse, "NEAR", "FAR", "S")[0],
                   decide_read(tbl_survive, "NEAR", "FAR", "S")[0],
                   decide_read(tbl_mixed, "NEAR", "FAR", "S")[0]})
    assert seen == ["MIXED", "NEAR_COLLAPSE", "NEAR_SURVIVES"], "reads not all reachable: %r" % seen
    res["reads_reachable"] = seen

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, n_pairs: Optional[int]) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode)
    n_boot = N_BOOTSTRAP if run_mode == "full" else 500

    # ---- REPLAY OF THE PARENT'S ELIGIBILITY CHAIN, in the parent's own order, with the parent's
    # ---- own code. This is how "the same 350 pairs" is guaranteed rather than assumed.
    pairs_all = load_simlex(limit=n_pairs)
    full_vocab = {w for p in load_simlex() for w in p[:2]}
    recs, df_pop, supply_prov = load_treatment_store(full_vocab)
    v6_all, v6_strict, v6_prov = load_v6_genus(full_vocab)
    cskg = get_cskg_cache(full_vocab)
    sup_d = build_supply("C_CSKG_NOLEXREL", sorted(full_vocab), cskg)

    diff_words = sorted({w for w, r in recs.items() if r.diff})
    diff_set = set(diff_words)
    cov_diff = [p for p in pairs_all if p[0] in diff_set and p[1] in diff_set]
    cov_gnd = [p for p in cov_diff if in_grounded_lexicon(p[0]) and in_grounded_lexicon(p[1])]
    covered = [p for p in cov_gnd if p[0] in sup_d.word_feats and p[1] in sup_d.word_feats]
    survivors, leak = leak_controls(covered, recs)
    n_surv = len(survivors)
    golds = [g for _, _, g in survivors]
    print("[replay] survivors=%d (parent expects %d at full)" % (n_surv, PARENT_N), flush=True)

    # ---- Supplies (parent's construction, verbatim) -------------------------------------------
    n_docs_pop = supply_prov["n_population_terms"]
    wf_diff = {w: sorted(recs[w].diff) for w in diff_words}
    wf_genus = {w: sorted(recs[w].genus | v6_all.get(w, set())) for w in diff_words}
    wf_genus_strict = {w: sorted(recs[w].genus | v6_strict.get(w, set())) for w in diff_words}
    df_b = dict(df_pop)
    for w, fs in list(wf_genus.items()) + list(wf_genus_strict.items()):
        for f in fs:
            df_b.setdefault(f, 1)
    sup_a = make_supply("A_DIFFERENTIA", wf_diff, df_pop, n_docs_pop)
    sup_b = make_supply("B_GENUS_ONLY", wf_genus, df_b, n_docs_pop)
    sup_bs = make_supply("B_STRICT_GENUS", wf_genus_strict, df_b, n_docs_pop)
    sup_e = make_supply("E_SCRAMBLE", _scrambled_assignment(sup_a), df_pop, n_docs_pop)

    # ---- Arm scores at the PRIMARY UNIFORM comparator (weighted=False) ------------------------
    arm_scores: Dict[str, List[float]] = {
        "A": supply_scores(sup_a, survivors, False),
        "B": supply_scores(sup_b, survivors, False),
        "B_STRICT": supply_scores(sup_bs, survivors, False),
        "D": supply_scores(sup_d, survivors, False),
        "E": supply_scores(sup_e, survivors, False),
        "C": [float(grounded_raw_cos(grounded_vector(a), grounded_vector(b)))
              for a, b, _ in survivors],
    }
    digests = {k: hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()
               for k, v in arm_scores.items()}
    seen: Dict[str, str] = {}
    for k in sorted(digests):
        if digests[k] in seen:
            raise AssertionError("META_RULE_AF VIOLATION: arms %r and %r bit-identical"
                                 % (seen[digests[k]], k))
        seen[digests[k]] = k

    # ---- POSITIVE CONTROL: is this the parent's experiment? -----------------------------------
    pooled = {k: round(_rho(v, golds), 4) for k, v in arm_scores.items()}
    dev = {k: round(abs(pooled[k] - PARENT_RHO[k]), 6) for k in PARENT_RHO}
    reproduced = bool(n_surv == PARENT_N and all(d <= PARENT_TOL for d in dev.values()))
    pos_ctrl = {"n_surviving": n_surv, "parent_n": PARENT_N, "rho_pooled": pooled,
                "parent_rho": PARENT_RHO, "abs_deviation": dev, "tolerance": PARENT_TOL,
                "reproduced": reproduced}
    print("[positive-control] reproduced=%s pooled=%s" % (reproduced, json.dumps(pooled)),
          flush=True)
    if run_mode == "full" and not reproduced:
        metrics = {"verdict": "HARD_FAIL_PARENT_NOT_REPRODUCED",
                   "verdict_msg": "re-derived pair set is not the parent's: %s" % json.dumps(dev),
                   "summary": "NEAR vs FAR diagnostic -- parent positive control failed",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "positive_control_parent_reproduce": pos_ctrl,
                   "n_units": 0, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": False}
        _atomic_write_metrics(output_dir, metrics)
        print("[verdict] HARD_FAIL_PARENT_NOT_REPRODUCED", flush=True)
        return metrics

    # ---- THE SPLITS (pre-reg 3), computed from WordNet + SimLex only --------------------------
    fields = load_simlex_fields()
    tax: List[dict] = []
    for a, b, _g in survivors:
        fl = fields[(a, b)]
        t = taxonomic_nearness(a, b, fl["pos"])
        t.update({"a": a, "b": b, "pos": fl["pos"], "concQ": fl["concQ"], "gold": fl["gold"]})
        tax.append(t)

    idx_near = [i for i, t in enumerate(tax) if t["near"]]
    idx_far = [i for i, t in enumerate(tax) if not t["near"]]

    wnsims = sorted(t["wnsim"] for t in tax if t["wnsim"] is not None)
    wn_median = float(np.median(wnsims)) if wnsims else None
    idx_near_g = [i for i, t in enumerate(tax)
                  if t["wnsim"] is not None and wn_median is not None and t["wnsim"] >= wn_median]
    idx_far_g = [i for i, t in enumerate(tax)
                 if t["wnsim"] is not None and wn_median is not None and t["wnsim"] < wn_median]
    n_no_wnsim = sum(1 for t in tax if t["wnsim"] is None)

    gold_median = float(np.median(golds))
    idx_high = [i for i, g in enumerate(golds) if g >= gold_median]
    idx_low = [i for i, g in enumerate(golds) if g < gold_median]

    idx_conc = [i for i, t in enumerate(tax) if t["concQ"] >= 3]
    idx_abst = [i for i, t in enumerate(tax) if t["concQ"] <= 2]

    half_idx = {"SPLIT1_TAXONOMIC": {"NEAR": idx_near, "FAR": idx_far},
                "SPLIT1B_WN_PATH_MEDIAN": {"NEAR_G": idx_near_g, "FAR_G": idx_far_g},
                "SPLIT2_HUMAN_RATING": {"HIGH": idx_high, "LOW": idx_low},
                "SPLIT3_CONCRETENESS": {"CONCRETE": idx_conc, "ABSTRACT": idx_abst}}

    # ---- Score every half (per-unit checkpoint/resume) ----------------------------------------
    done = completed_units(output_dir)
    prior = load_units(output_dir)
    table: Dict[str, Dict[str, dict]] = {}
    unit_idx = 0
    for split, halves in SPLIT_HALVES:
        table[split] = {}
        for half in halves:
            idx = half_idx[split][half]
            cells = score_half(arm_scores, golds, idx, n_boot)
            for arm in ARMS:
                unit_idx += 1
                key = unit_key(ANCHOR_NAME, split, half, arm, run_mode, n_surv)
                if key in done:
                    cells[arm] = prior[key]["cell"]
                else:
                    record_unit(output_dir, key, {"cell": cells[arm], "split": split,
                                                  "half": half, "arm": arm})
            table[split][half] = cells
            _heartbeat(output_dir, unit_idx, EXPECTED_N_UNITS, time.time() - t0,
                       {"split": split, "half": half, "n": len(idx),
                        "C_rho": cells["C"]["rho"]})
            print("[%s|%s] n=%d %s" % (split, half, len(idx),
                                       " ".join("%s=%.4f%s" % (
                                           a, cells[a]["rho"],
                                           "*" if cells[a]["ci_excludes_zero"] else "")
                                           for a in ARMS)), flush=True)
    pooled_cells = score_half(arm_scores, golds, list(range(n_surv)), n_boot)

    # ---- POWER GATE (pre-reg 5) + read selection (pre-reg 6) ----------------------------------
    underpowered = {"%s|%s" % (s, h): len(half_idx[s][h])
                    for s, hs in SPLIT_HALVES for h in hs if len(half_idx[s][h]) < MIN_HALF_N}
    s1_ok = len(idx_near) >= MIN_HALF_N and len(idx_far) >= MIN_HALF_N
    s1b_ok = len(idx_near_g) >= MIN_HALF_N and len(idx_far_g) >= MIN_HALF_N
    if s1_ok:
        read, read_notes = decide_read(table, "NEAR", "FAR", "SPLIT1_TAXONOMIC")
        read_source = "SPLIT1_TAXONOMIC"
    elif s1b_ok:
        read, read_notes = decide_read(table, "NEAR_G", "FAR_G", "SPLIT1B_WN_PATH_MEDIAN")
        read_source = "SPLIT1B_WN_PATH_MEDIAN"
        read_notes.append("FALLBACK: SPLIT1 had a half below n=%d (%r); the pre-registered "
                          "fallback to the balanced SPLIT1B was used." % (MIN_HALF_N, underpowered))
    else:
        read, read_notes = "UNDERPOWERED_NO_READ", [
            "both primary splits had a half below n=%d: %r" % (MIN_HALF_N, underpowered)]
        read_source = None

    # ---- Reported for its own sake: do symbols work COARSELY? --------------------------------
    far_key = "FAR" if s1_ok else ("FAR_G" if s1b_ok else None)
    far_split = read_source
    sym = {}
    if far_key:
        for arm in SYMBOLIC_ARMS:
            c = table[far_split][far_key][arm]
            sym[arm] = {"rho": c["rho"], "ci_lo": c["ci_lo"], "ci_hi": c["ci_hi"],
                        "n": c["n"], "beats_chance": bool(c["ci_excludes_zero"])}
    symbols_flag = ("SYMBOLS_WORK_COARSE" if any(v["beats_chance"] for v in sym.values())
                    else "SYMBOLS_CARRY_NOTHING") if sym else "NOT_EVALUABLE"

    units = load_units(output_dir)
    cardinality_ok = len(units) >= EXPECTED_N_UNITS
    verdict = "DIAGNOSTIC_" + read
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"

    msg = ("READ=%s (source=%s) | C: NEAR/HIGH-difficulty rho=%s CI=%s vs FAR rho=%s CI=%s | "
           "symbols_on_FAR=%s | n=%d | underpowered_halves=%s"
           % (read, read_source,
              table[read_source][("NEAR" if s1_ok else "NEAR_G")]["C"]["rho"] if read_source
              else "n/a",
              (table[read_source][("NEAR" if s1_ok else "NEAR_G")]["C"]["ci_lo"],
               table[read_source][("NEAR" if s1_ok else "NEAR_G")]["C"]["ci_hi"])
              if read_source else "n/a",
              table[read_source][("FAR" if s1_ok else "FAR_G")]["C"]["rho"] if read_source
              else "n/a",
              (table[read_source][("FAR" if s1_ok else "FAR_G")]["C"]["ci_lo"],
               table[read_source][("FAR" if s1_ok else "FAR_G")]["C"]["ci_hi"])
              if read_source else "n/a",
              symbols_flag, n_surv, sorted(underpowered)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "read": read, "read_source": read_source,
        "read_notes": read_notes,
        "summary": "NEAR vs FAR difficulty split of the parent's 350 SimLex pairs, same arms",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
        "parent_cell": "experiments/exp_differentia_feature_supply_v1.py",
        "parent_metrics": "data/exp_differentia_feature_supply_v1/metrics.json",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "hdlab_modified": False, "parent_cell_modified": False,
        "n_units": len(units), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok, "arms_differ_verified": True, "arm_digests": digests,
        "arm_labels": ARM_LABEL,
        "positive_control_parent_reproduce": pos_ctrl,
        "n_surviving_pairs": n_surv,
        "pooled_all_pairs": pooled_cells,
        "table": table,
        "half_sizes": {s: {h: len(half_idx[s][h]) for h in hs} for s, hs in SPLIT_HALVES},
        "power": {"MIN_HALF_N": MIN_HALF_N, "underpowered_halves": underpowered,
                  "split1_powered": s1_ok, "split1b_powered": s1b_ok,
                  "mde_note": "mde_95 = 1.96 * paired-bootstrap sd of rho within that half; it is "
                              "the smallest |rho| that half could distinguish from 0"},
        "symbolic_arms_on_far_half": sym, "symbols_flag": symbols_flag,
        "split_definitions": {
            "SPLIT1_TAXONOMIC": "NEAR iff shared synset (N1) OR shared DIRECT hypernym (N2) OR, "
                                "for adjectives only, same similar_to cluster (N3, author "
                                "extension); FAR otherwise. WordNet %s." % wn.get_version(),
            "SPLIT1B_WN_PATH_MEDIAN": "NEAR_G iff max synset-pair path_similarity >= median over "
                                      "the evaluated pairs (ties to NEAR_G); balanced by "
                                      "construction so it is powered whenever the parent set is.",
            "SPLIT2_HUMAN_RATING": "HIGH iff gold >= median gold (ties to HIGH). RANGE-RESTRICTION "
                                   "WARNING: conditioning on the rating restricts the range of the "
                                   "very variable being correlated and mechanically depresses rho "
                                   "in BOTH halves. Reported, not headlined; no read taken from it.",
            "SPLIT3_CONCRETENESS": "CONCRETE iff SimLex concQ in {3,4}; ABSTRACT iff concQ in "
                                   "{1,2}. Tests the dual-coding prediction directly.",
            "independence": "arms A/B/E come from the simplewiki extractor + v6 ISA store; arm C "
                            "from Lancaster sensorimotor + Brysbaert concreteness norms; arm D "
                            "from CSKG-minus-lexical-relations. None reads WordNet at score time. "
                            "DISCLOSED: CSKG is a merged graph that includes WordNet among its "
                            "sources, so arm D has partial provenance overlap with the split "
                            "criterion; arm D is excluded from setting the read.",
        },
        "split_diagnostics": {
            "wordnet_version": wn.get_version(),
            "wordnet_asset": "nltk corpora/wordnet.zip (data/wordnet_cache/ is EMPTY on disk)",
            "n_near_by_N1_synonym": sum(1 for t in tax if t["N1_synonym"]),
            "n_near_by_N2_cohyponym": sum(1 for t in tax if t["N2_cohyponym"]),
            "n_near_by_N3_adj_cluster_alone": sum(1 for t in tax if t["n3_alone"]),
            "n_pos_fallback": sum(1 for t in tax if t["pos_fallback"]),
            "n_no_wn_path_similarity": n_no_wnsim,
            "wn_path_similarity_median": None if wn_median is None else round(wn_median, 4),
            "gold_median": round(gold_median, 4),
            "pos_counts_near": {p: sum(1 for t in tax if t["near"] and t["pos"] == p)
                                for p in ("N", "V", "A")},
            "pos_counts_far": {p: sum(1 for t in tax if not t["near"] and t["pos"] == p)
                               for p in ("N", "V", "A")},
            "near_sample": [[t["a"], t["b"], t["pos"]] for t in tax if t["near"]][:20],
            "far_sample": [[t["a"], t["b"], t["pos"]] for t in tax if not t["near"]][:20],
        },
        "bootstrap_config": {"n_boot": n_boot, "seed": BOOTSTRAP_SEED,
                             "procedure": "paired percentile bootstrap over pairs WITHIN the "
                                          "half; all arms recomputed on the SAME resampled index "
                                          "set (parent's paired_bootstrap, unmodified)"},
        "leak_controls": leak, "supply_provenance": supply_prov, "v6_provenance": v6_prov,
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (verdict, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--pairs", type=int, default=None)
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        for n in SMOKE_PAIR_SCALES:              # multi-scale smoke; pair count is the load axis
            out = OUT_SMOKE + "_p%d" % n
            print("=== SMOKE at %d pairs -> %s ===" % (n, out), flush=True)
            m = run("smoke", out, n)
            if m["n_surviving_pairs"] < 10:
                raise AssertionError("VACUOUS SMOKE at %d pairs: %d survivors"
                                     % (n, m["n_surviving_pairs"]))
            hs = m["half_sizes"]["SPLIT1_TAXONOMIC"]
            if hs["NEAR"] == 0 or hs["FAR"] == 0:
                raise AssertionError("VACUOUS SMOKE at %d pairs: SPLIT1 degenerate %r" % (n, hs))
            # the split must PARTITION, not relabel: the halves must differ on arm C
            cn = m["table"]["SPLIT1_TAXONOMIC"]["NEAR"]["C"]
            cf = m["table"]["SPLIT1_TAXONOMIC"]["FAR"]["C"]
            if cn["rho"] == cf["rho"] and cn["n"] == cf["n"]:
                raise AssertionError("VACUOUS SMOKE: NEAR and FAR halves are indistinguishable")
            if m["n_units"] < EXPECTED_N_UNITS:
                raise AssertionError("SMOKE cardinality breach: %d < %d"
                                     % (m["n_units"], EXPECTED_N_UNITS))
            print("[smoke] p%d ok: halves=%r C_near=%.4f C_far=%.4f units=%d"
                  % (n, m["half_sizes"], cn["rho"], cf["rho"], m["n_units"]), flush=True)
        print("SMOKE=PASS (all scales)", flush=True)
        return
    run("full", OUT_FULL, args.pairs)


_SELFTEST_RESULT = _instrumentation_selftest()      # module scope, before any measurement

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                          # NOT BaseException
        _write_crash_metrics(OUT_SMOKE if "smoke" in sys.argv else OUT_FULL, _e)
        raise
