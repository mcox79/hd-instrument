"""exp_target_space_vs_bridge_mechanism_v1 -- IS THE TARGET SPACE THE LIMIT, OR THE MECHANISM?

PRE-REG: preregs/2026-08-16_target_space_vs_bridge_mechanism_v1.md
         (every threshold fixed BEFORE any run; this file never edits them)

THE ONE VARIABLE IS THE TARGET SPACE. The bridging mechanism, the graph, the core, the held-out
set, the stratum, the scorer, the bootstrap seed and the permutation count are held FIXED by
CONSTRUCTION -- they are supplied by two SIBLING CELLS THAT ARE IMPORTED AND NEVER EDITED:
  experiments/exp_thematic_relation_supply_bridged_grounding_v2.py  (run_config, the arm battery)
  experiments/exp_bridged_grounding_from_core_v1.py                 (Bridger, eligibility, floors)

TWO DISCLOSED RUNTIME PARAMETERISATIONS, BOTH SELF-TESTED, NEITHER AN EDIT TO EITHER FILE:
  P1  CELL.code_matrix hard-codes np.zeros((n, 12)) and cannot hold a 15- or 23-dim code. It is
      replaced at runtime by a dimension-agnostic function with identical semantics. SELF-TEST S1
      asserts BIT-IDENTICAL output on 12-dim input, so the incumbent arm runs the original path.
  P2  THEM.score_arm is WRAPPED (original called, return value passed through unchanged) only to
      RECORD the per-arm cosine vector run_config discards. Required for the PAIRED cross-space
      retention CI. SELF-TEST S2 asserts pass-through equality.

WHY AFFECT IS A CHANNEL AND NOT MORE DIMENSIONS OF THE SAME ONE -- BRAIN STRUCTURE, not a
cognitive-theory label: valence/arousal/dominance is carried by amygdala (population coding of
valence), orbitofrontal and ventromedial prefrontal cortex, and insula (interoceptive), which are
DIFFERENT NEURAL SYSTEMS from the modality-specific perceptual and motor SPOKES that converge on
the anterior temporal lobe hub. Separable by lesion. [PINNED] The CHOICE of Warriner V/A/D as the
3-dim operationalisation of that block is OURS-INVENTION-UNDER-TEST.

TRAPS GUARDED BY RUNTIME EVERY RUN, NEVER INHERITED:
  hdlab.grounded_similarity.grounded_similarity() SATURATES >70% of SimLex pairs onto two values.
  IT IS NEVER THE SCORER. The scorer is the raw rating vector, L2-normalised, plain cosine.
  ZERO-FILL IS BARRED: every arm runs on the intersection vocabulary where EVERY space is defined.
  NO NUMBER IS CARRIED BETWEEN SCORERS OR POPULATIONS. The 8.2% retention figure is NOT imported;
  TS1 re-earns its own baseline on this stratum.

The Warriner norms are HUMAN RATINGS, not a co-occurrence table. NO EXTERNAL LANGUAGE MODEL
ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network. data/foundation/** read-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import csv
import io
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
import exp_bridged_grounding_from_core_v1 as CELL          # IMPORTED, NEVER EDITED
import exp_thematic_relation_supply_bridged_grounding_v2 as THEM   # IMPORTED, NEVER EDITED
import thematic_relation_extractor_v1 as TX
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "target_space_vs_bridge_mechanism_v1"
CODE_VERSION = "v1.1"   # v1.0 -> v1.1 adds ONLY the --space parallel-worker orchestration; the
                        # per-config computation is byte-identical (same run_config, same stratum,
                        # same seeds). The v1.0 SMOKE gate is reported separately and not merged.
PREREG = "preregs/2026-08-16_target_space_vs_bridge_mechanism_v1.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
# PARALLEL WORKER MODE. Each target space is INDEPENDENT by construction (that is the whole point
# of the design), so one space per process is a scheduling change and NOT a computational one:
# each worker runs the IDENTICAL run_config on the IDENTICAL stratum with the IDENTICAL seed and
# writes its own part file. The assembler reads the parts and does the PAIRED cross-space maths.
# Parts are per-space FILES, never a shared append log -- a ~100 KB JSONL line is not an atomic
# append on this filesystem and concurrent writers would interleave.
_ap.add_argument("--space", default=None, help="compute ONE target space and exit (worker mode)")
_ARGS, _ = _ap.parse_known_args()
SMOKE = bool(_ARGS.smoke) or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
RUN_MODE = "smoke" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS (prereg sections 5-6). NOT EDITED AFTER A RUN.
N_BOOT = 2000 if SMOKE else 10000
N_PERM = 400 if SMOKE else 2000
BOOT_SEED = 20260816
T_MARGIN_MIN = FT.T_MARGIN_MIN                       # 0.05
AOA_CORE_MAX = CELL.AOA_CORE_MAX                     # 6.0
RATIO_GUARD = 0.05          # discard retention draws where |rho(K1)| < this; discard rate REPORTED
PRIMARY_ARM = "B1_BRIDGE_MEAN"
KNOWN_ANSWER = "K1_OWN_NORMS"
DESIGN_GATE_MIN_N = 250

GT = REPO / "data" / "grounding_testbed"
LANC = GT / "Lancaster_sensorimotor_norms_for_39707_words.csv"
CONC = GT / "Concreteness_ratings_Brysbaert_et_al_BRM.txt"
WARR = GT / "Ratings_Warriner_et_al.csv"

L11 = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean",
       "Olfactory.mean", "Visual.mean", "Foot_leg.mean", "Hand_arm.mean",
       "Head.mean", "Mouth.mean", "Torso.mean"]
LSD = [c.replace(".mean", ".SD") for c in L11]
VAD = ["V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"]

# the ONLY thing that varies -- (source_tag, column) specs
SPACE_SPECS: Dict[str, List[Tuple[str, str]]] = {
    "TS1_CURRENT_12": [("L", c) for c in L11] + [("C", "Conc.M")],
    "TS2_PLUS_AFFECT_15": [("L", c) for c in L11] + [("C", "Conc.M")] + [("W", c) for c in VAD],
    "TS3_AFFECT_ONLY_3": [("W", c) for c in VAD],
    "TS4_WIDER_UNINFORMATIVE_23": [("L", c) for c in L11] + [("C", "Conc.M")]
                                  + [("L", c) for c in LSD],
}
SPACE_ORDER = ["TS0_INCUMBENT_TABLE_VERBATIM", "TS1_CURRENT_12", "TS2_PLUS_AFFECT_15",
               "TS3_AFFECT_ONLY_3", "TS4_WIDER_UNINFORMATIVE_23"]
TARGET_SPACE_ARMS = ["TS1_CURRENT_12", "TS2_PLUS_AFFECT_15", "TS3_AFFECT_ONLY_3",
                     "TS4_WIDER_UNINFORMATIVE_23"]

SPACE_ROLE = {
    "TS0_INCUMBENT_TABLE_VERBATIM":
        "CONSTRUCTION CONTROL, NOT a target-space arm. hdlab.grounded_similarity._table() rows "
        "verbatim, restricted to the intersection. Measures how far re-z-scoring on the "
        "intersection population moved the incumbent.",
    "TS1_CURRENT_12": "INCUMBENT. Re-earns its own retention baseline ON THIS STRATUM. The 8.2% "
                      "figure from the sibling is NOT imported.",
    "TS2_PLUS_AFFECT_15": "PRIMARY TREATMENT. Adds the AFFECTIVE block (amygdala / OFC / vmPFC / "
                          "insula), a separable subsystem with its own substrate. The CHANNEL is "
                          "PINNED as a semantic block; the CHOICE of Warriner V/A/D as its 3-dim "
                          "operationalisation is OURS-INVENTION-UNDER-TEST.",
    "TS3_AFFECT_ONLY_3": "DISSOCIATION. If bridged TS3 matches bridged TS2, sensorimotor "
                         "contributes nothing under bridging.",
    "TS4_WIDER_UNINFORMATIVE_23":
        "THE DECISIVE NEGATIVE CONTROL. Same magnitude of widening, same source file, NO new "
        "channel. IF TS4 RAISES BRIDGED RETENTION AS MUCH AS TS2, 'more dimensions' is the "
        "mechanism, the affect story is REFUTED, and the direction dies.",
}


# ------------------------------------------------------------------------------------------
# P1 -- dimension-agnostic code_matrix. SEMANTICS IDENTICAL; only the width is not hard-coded.
# ------------------------------------------------------------------------------------------
_ORIG_CODE_MATRIX = CELL.code_matrix
_ORIG_SCORE_ARM = THEM.score_arm


def code_matrix_anydim(vocab: List[str], raw: Dict[str, np.ndarray],
                       bridged: Dict[str, np.ndarray]) -> np.ndarray:
    d = len(next(iter(raw.values())))
    X = np.zeros((len(vocab), d), dtype=np.float32)
    for i, w in enumerate(vocab):
        X[i] = bridged[w] if w in bridged else raw[w]
    return INS._l2n(X)


# P2 -- recorder. The ORIGINAL is called and its return value is passed through UNCHANGED.
_COS: Dict[Tuple[str, str], np.ndarray] = {}
_STRAT: Dict[str, Dict[str, np.ndarray]] = {}
_CUR = {"cfg": None}


def score_arm_recording(name, X, ia, ib, gold, floors, seed, light=False):
    r = _ORIG_SCORE_ARM(name, X, ia, ib, gold, floors, seed, light=light)
    cfg = _CUR["cfg"]
    if cfg is not None and "_cos" in r:
        _COS[(cfg, name)] = np.array(r["_cos"], dtype=np.float64, copy=True)
        if cfg not in _STRAT:
            _STRAT[cfg] = {"ia": np.array(ia, copy=True), "ib": np.array(ib, copy=True),
                           "gold": np.array(gold, dtype=np.float64, copy=True)}
    return r


def install_patches() -> None:
    CELL.code_matrix = code_matrix_anydim
    THEM.score_arm = score_arm_recording
    THEM.N_BOOT = N_BOOT
    THEM.N_PERM = N_PERM


# ------------------------------------------------------------------------------------------
# norm tables
# ------------------------------------------------------------------------------------------
def read_tbl(path: Path, key: str = "Word") -> Dict[str, Dict[str, str]]:
    with io.open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        first = f.readline()
    delim = "\t" if first.count("\t") > first.count(",") else ","
    out: Dict[str, Dict[str, str]] = {}
    with io.open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        for r in csv.DictReader(f, delimiter=delim):
            w = (r.get(key) or "").strip().lower()
            if w and " " not in w and "\t" not in w:
                out[w] = r
    return out


def _f(v) -> Optional[float]:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


def build_space_tables(inter: List[str], src: Dict[str, Dict[str, Dict[str, str]]],
                       incumbent: Dict[str, Sequence[float]]) -> Tuple[Dict[str, Dict[str, np.ndarray]], Dict]:
    """Z-SCORE EACH COLUMN OVER THE IDENTICAL INTERSECTION POPULATION for every space.

    Z-scoring is NOT a choice made for this cell: hdlab/grounded_similarity.py already stores its
    12-dim table z-scored per dimension, so this IS the incumbent's own construction. Using the
    SAME population for every space is what makes 'add a channel' ONE variable rather than two.
    """
    tables: Dict[str, Dict[str, np.ndarray]] = {}
    info: Dict[str, Dict] = {}
    for name, spec in SPACE_SPECS.items():
        M = np.empty((len(inter), len(spec)), dtype=np.float64)
        for j, (s, c) in enumerate(spec):
            col = np.array([_f(src[s][w].get(c)) for w in inter], dtype=np.float64)
            if not np.all(np.isfinite(col)):
                raise SystemExit(f"[fatal] space {name} column {c} has a hole on the intersection")
            M[:, j] = col
        mu, sd = M.mean(0), M.std(0)
        sd[sd == 0] = 1.0
        Z = (M - mu) / sd
        tables[name] = {w: Z[i] for i, w in enumerate(inter)}
        info[name] = {"dims": len(spec), "columns": [f"{s}:{c}" for s, c in spec],
                      "construction": "z-scored per column over the intersection population",
                      "col_mean_raw": [round(float(x), 4) for x in mu],
                      "col_sd_raw": [round(float(x), 4) for x in sd],
                      "role": SPACE_ROLE[name]}
    tables["TS0_INCUMBENT_TABLE_VERBATIM"] = {
        w: np.asarray(incumbent[w], dtype=np.float64) for w in inter}
    info["TS0_INCUMBENT_TABLE_VERBATIM"] = {
        "dims": 12, "columns": ["hdlab.grounded_similarity._table() -- verbatim, already z-scored "
                                "over its own 36,810-word population"],
        "construction": "NOT rebuilt. The live incumbent rows, restricted to the intersection.",
        "role": SPACE_ROLE["TS0_INCUMBENT_TABLE_VERBATIM"]}
    return tables, info


# ------------------------------------------------------------------------------------------
# PAIRED CROSS-SPACE RETENTION -- shared resample index, identical stratum
# ------------------------------------------------------------------------------------------
def _rho(c: np.ndarray, g: np.ndarray) -> float:
    return INS._spearman(c, g)


def retention_block(gold: np.ndarray, n_boot: int, seed: int) -> Dict:
    n = len(gold)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    spaces = [s for s in SPACE_ORDER if (s, PRIMARY_ARM) in _COS and (s, KNOWN_ANSWER) in _COS]
    boots_ret: Dict[str, np.ndarray] = {}
    boots_b1: Dict[str, np.ndarray] = {}
    boots_k1: Dict[str, np.ndarray] = {}
    point: Dict[str, Dict] = {}
    valid = np.ones(n_boot, dtype=bool)
    for s in spaces:
        b1, k1 = _COS[(s, PRIMARY_ARM)], _COS[(s, KNOWN_ANSWER)]
        rb = np.empty(n_boot)
        rk = np.empty(n_boot)
        for b in range(n_boot):
            j = idx[b]
            gg = gold[j]
            rb[b] = _rho(b1[j], gg)
            rk[b] = _rho(k1[j], gg)
        boots_b1[s], boots_k1[s] = rb, rk
        with np.errstate(divide="ignore", invalid="ignore"):
            boots_ret[s] = rb / rk
        valid &= np.isfinite(rb) & np.isfinite(rk) & (np.abs(rk) >= RATIO_GUARD)
        pb, pk = _rho(b1, gold), _rho(k1, gold)
        point[s] = {"rho_B1": round(float(pb), 4), "rho_K1": round(float(pk), 4),
                    "retention_fraction": (round(float(pb / pk), 4) if abs(pk) > 1e-9 else None)}
    kept = int(valid.sum())
    out = {
        "WHAT_THIS_IS": ("RETENTION = rho(B1 in space S) / rho(K1 in space S). The stratum, the "
                         "gold and the resample index are IDENTICAL across spaces, so every "
                         "difference below is PAIRED."),
        "n_stratum": int(n), "n_boot": int(n_boot),
        "ratio_guard": {"rule": f"discard a draw if |rho(K1)| < {RATIO_GUARD} in ANY space",
                        "draws_kept": kept, "draws_discarded": int(n_boot - kept),
                        "discard_rate": round(1.0 - kept / max(n_boot, 1), 4)},
        "per_space_point": point, "per_space_ci": {}, "PAIRED_DIFFERENCES_vs_TS1": {},
        "PAIRED_RAW_RHO_DIFFERENCES_vs_TS1": {},
    }
    for s in spaces:
        r = boots_ret[s][valid]
        out["per_space_ci"][s] = {
            "retention_ci95": ([round(float(np.percentile(r, 2.5)), 4),
                                round(float(np.percentile(r, 97.5)), 4)] if kept > 20 else None),
            "rho_B1_ci95": [round(float(np.percentile(boots_b1[s], 2.5)), 4),
                            round(float(np.percentile(boots_b1[s], 97.5)), 4)],
            "rho_K1_ci95": [round(float(np.percentile(boots_k1[s], 2.5)), 4),
                            round(float(np.percentile(boots_k1[s], 97.5)), 4)]}
    base = "TS1_CURRENT_12"
    if base in spaces:
        for s in spaces:
            if s == base:
                continue
            d = (boots_ret[s] - boots_ret[base])[valid]
            pt = (None if point[s]["retention_fraction"] is None
                  or point[base]["retention_fraction"] is None
                  else round(point[s]["retention_fraction"] - point[base]["retention_fraction"], 4))
            ci = ([round(float(np.percentile(d, 2.5)), 4),
                   round(float(np.percentile(d, 97.5)), 4)] if kept > 20 else None)
            out["PAIRED_DIFFERENCES_vs_TS1"][s] = {
                "point": pt, "ci95": ci,
                "band": (FT.band(ci) if ci else "NOT_CONSTRUCTIBLE"),
                "CI_SEPARATED": bool(ci and (ci[0] > 0 or ci[1] < 0))}
            dr = boots_b1[s] - boots_b1[base]
            cir = [round(float(np.percentile(dr, 2.5)), 4),
                   round(float(np.percentile(dr, 97.5)), 4)]
            out["PAIRED_RAW_RHO_DIFFERENCES_vs_TS1"][s] = {
                "point": round(point[s]["rho_B1"] - point[base]["rho_B1"], 4),
                "ci95": cir, "band": FT.band(cir),
                "CI_SEPARATED": bool(cir[0] > 0 or cir[1] < 0)}
        # the ceiling moved too -- report it, so a retention change is never read as a bridge change
        out["PAIRED_K1_CEILING_DIFFERENCES_vs_TS1"] = {}
        for s in spaces:
            if s == base:
                continue
            dk = boots_k1[s] - boots_k1[base]
            cik = [round(float(np.percentile(dk, 2.5)), 4),
                   round(float(np.percentile(dk, 97.5)), 4)]
            out["PAIRED_K1_CEILING_DIFFERENCES_vs_TS1"][s] = {
                "point": round(point[s]["rho_K1"] - point[base]["rho_K1"], 4),
                "ci95": cik, "band": FT.band(cik),
                "CI_SEPARATED": bool(cik[0] > 0 or cik[1] < 0)}
    return out


# ------------------------------------------------------------------------------------------
def selftest(inter: Optional[List[str]] = None) -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # S1 -- the dimension-agnostic code_matrix is BIT-IDENTICAL to the original at 12 dims
    g = np.random.default_rng(20260816)
    vocab = [f"w{i}" for i in range(200)]
    raw12 = {w: g.standard_normal(12) for w in vocab}
    brd = {w: g.standard_normal(12) for w in vocab[:37]}
    A = _ORIG_CODE_MATRIX(vocab, raw12, brd)
    B = code_matrix_anydim(vocab, raw12, brd)
    assert A.shape == B.shape and np.array_equal(A, B), "P1 patch is NOT bit-identical at d=12"
    for d in (3, 15, 23):
        rd = {w: g.standard_normal(d) for w in vocab}
        assert code_matrix_anydim(vocab, rd, {}).shape == (200, d)
    ev["S1_code_matrix_patch"] = {
        "bit_identical_at_d12": True, "widths_supported": [3, 12, 15, 23],
        "what_it_proves": "the TS1 incumbent arm runs the ORIGINAL code path exactly; only the "
                          "array WIDTH is not hard-coded"}

    # S2 -- the score_arm wrapper passes the original's value through UNCHANGED
    ia = np.arange(60) % 40
    ib = (np.arange(60) * 7 + 3) % 40
    gold = g.random(60)
    voc40 = [f"v{i}" for i in range(40)]
    r40 = {w: g.standard_normal(12) for w in voc40}
    X = code_matrix_anydim(voc40, r40, {})
    counts = {w: 10 + i for i, w in enumerate(voc40)}
    THEM.N_PERM, THEM.N_BOOT = 40, 200
    fl = THEM.build_floors(voc40, ia, ib, gold, counts)
    a = _ORIG_SCORE_ARM("PROBE", X, ia, ib, gold, fl, 7)
    _CUR["cfg"] = None
    b = score_arm_recording("PROBE", X, ia, ib, gold, fl, 7)
    assert np.allclose(a.pop("_cos"), b.pop("_cos")), "P2 wrapper altered the cosine"
    assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True,
                                                                    default=str), \
        "P2 wrapper altered the scored result"
    THEM.N_PERM, THEM.N_BOOT = N_PERM, N_BOOT
    ev["S2_score_arm_wrapper"] = {"pass_through_identical": True}

    # S3 -- the grounded_similarity SATURATION trap, re-asserted BY RUNTIME, never inherited
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    assert len(tab) == 36810, f"norms table {len(tab)} != 36810"
    assert len(next(iter(tab.values()))) == 12, "incumbent norms are not 12-dim"
    pairs = CELL.load_simlex_pos()
    vals = [GS.grounded_similarity(x, y) for x, y, _, _ in pairs]
    c = collections.Counter(round(v, 6) for v in vals if v is not None)
    frac2 = sum(n for _, n in c.most_common(2)) / len(vals)
    assert frac2 > 0.70, f"expected saturation; top-2 mass {frac2:.4f}"
    ev["S3_TRAP_grounded_similarity_saturation"] = {
        "fraction_on_two_values": round(frac2, 4), "n_distinct": len(c),
        "consequence": "NEVER the scorer here; the scorer is the raw rating vector + plain cosine"}

    # S4 -- the bootstrap can BOTH fire and fail
    gg = g.random(200)
    good = gg + 0.05 * g.standard_normal(200)
    noise = g.standard_normal(200)
    assert FT.band(FT.boot_rho_diff(good, good.copy(), gg, n_boot=400)["ci95"]) == "NOT_SEPARATED"
    assert FT.band(FT.boot_rho_diff(good, noise, gg, n_boot=400)["ci95"]) == "ABOVE"

    # S5 -- the ARMS-MUST-DIFFER gate on the SPACES themselves
    if inter is not None:
        ev["S5_spaces_must_differ"] = _spaces_differ_evidence(inter)

    # S6 -- floor-name legibility to the standing-bar reader
    from tools.c3_gate import classify_arm_role
    for k, want in ((THEM.FLOOR_ORTHO, "orthographic"), (THEM.FLOOR_FREQ, "frequency"),
                    (THEM.FLOOR_SCRAM, "scramble"), ("K2_ORACLE_BRIDGE", "known_answer"),
                    ("N1_NULL_ARM_MATCHED_REWIRE", "null_control")):
        assert classify_arm_role(k) == want, f"c3_gate reads {k} as {classify_arm_role(k)}"
    for k in (PRIMARY_ARM, KNOWN_ANSWER):
        assert classify_arm_role(k) is None, f"treatment arm {k} misreads"

    # S7 -- MANDATORY CLEANUP. THEM._ORTHO_CACHE is keyed on the DIMENSION ONLY, not on the
    # vocabulary, so the 40-word probe table built in S2 would be served to the 1,008-word run and
    # silently corrupt every orthographic floor. Cleared here, and the clear is asserted.
    THEM._ORTHO_CACHE.clear()
    assert not THEM._ORTHO_CACHE, "orthographic-floor cache not cleared after the selftest probe"
    ev["S7_ortho_cache_cleared"] = {
        "why": "THEM._ORTHO_CACHE is keyed on dimension only; a selftest-sized table left in it "
               "would be served to the real stratum and corrupt F_ORTHOGRAPHIC"}

    print("[selftest] ALL PASS", flush=True)
    return ev


_SPACE_TABLES: Dict[str, Dict[str, np.ndarray]] = {}


def _spaces_differ_evidence(inter: List[str]) -> Dict:
    sub = inter[:400]
    sigs = {}
    for s in SPACE_ORDER:
        if s not in _SPACE_TABLES:
            continue
        M = INS._l2n(np.stack([_SPACE_TABLES[s][w] for w in sub]).astype(np.float32))
        sigs[s] = M
    out = {"n_probe_words": len(sub), "dims": {s: int(M.shape[1]) for s, M in sigs.items()},
           "pairwise_identical": []}
    ks = sorted(sigs)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = sigs[ks[i]], sigs[ks[j]]
            same = (a.shape == b.shape and np.allclose(a, b))
            if same:
                out["pairwise_identical"].append([ks[i], ks[j]])
    assert not out["pairwise_identical"], f"target spaces collapse: {out['pairwise_identical']}"
    # a strong check: TS0 and TS1 are the SAME columns, differing only in z-scoring population
    if "TS0_INCUMBENT_TABLE_VERBATIM" in sigs and "TS1_CURRENT_12" in sigs:
        A, B = sigs["TS0_INCUMBENT_TABLE_VERBATIM"], sigs["TS1_CURRENT_12"]
        cs = float(np.mean(np.einsum("ij,ij->i", A, B)))
        out["TS0_vs_TS1_mean_rowwise_cosine"] = round(cs, 6)
        out["TS0_vs_TS1_note"] = ("same columns, different z-scoring population (36,810 vs the "
                                  "intersection). Reported, not assumed away.")
    return out


# ------------------------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    install_patches()

    src = {"L": read_tbl(LANC), "C": read_tbl(CONC), "W": read_tbl(WARR)}
    print(f"[tbl] lanc={len(src['L'])} conc={len(src['C'])} warr={len(src['W'])}", flush=True)

    from hdlab import grounded_similarity as GS
    incumbent = {w: list(v) for w, v in GS._table().items()}

    def has(w: str, s: str, cols: Sequence[str]) -> bool:
        r = src[s].get(w)
        return r is not None and all(_f(r.get(c)) is not None for c in cols)

    inter = sorted(w for w in incumbent
                   if has(w, "L", L11) and has(w, "L", LSD) and has(w, "C", ["Conc.M"])
                   and has(w, "W", VAD))
    print(f"[inter] intersection vocabulary = {len(inter)}", flush=True)

    global _SPACE_TABLES
    _SPACE_TABLES, space_info = build_space_tables(inter, src, incumbent)
    ev = selftest(inter)

    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK")
        return 0

    INTER = set(inter)
    pairs_all = CELL.load_simlex_pos()
    pairs = [p for p in pairs_all if p[0] in INTER and p[1] in INTER]
    vocab = sorted({w for p in pairs for w in p[:2]})
    idx = {w: i for i, w in enumerate(vocab)}
    partners: Dict[str, Set[str]] = collections.defaultdict(set)
    for a, b, _, _ in pairs:
        partners[a].add(b)
        partners[b].add(a)

    aoa = CELL.load_aoa()
    core = {w for w, v in aoa.items() if v <= AOA_CORE_MAX and w in INTER}
    held_out = {w for w in vocab if w not in core}
    counts = CELL.corpus_counts()

    def_graph, pat_census, def_rows = CELL.load_def_graph()
    edges = TX.build_or_load()
    them_graph, them_info = THEM.build_thematic_graph(edges)
    enriched = THEM.merge(def_graph, them_graph)
    cooc = edges["cooccurrence"]
    print(f"[assets] pairs={len(pairs)} vocab={len(vocab)} core={len(core)} "
          f"held_out={len(held_out)} enriched_nodes={len(enriched)}", flush=True)

    # ---- DESIGN GATE, measured before any arm is scored
    br0 = CELL.Bridger({w: np.zeros(3) for w in INTER}, held_out, partners)
    nb0 = {w: br0.neighbours(w, enriched, core, False) for w in sorted(held_out)}
    nb0 = {w: v for w, v in nb0.items() if v}
    S0 = set(nb0)
    strat0 = [p for p in pairs if (p[0] in S0) != (p[1] in S0)]
    design_gate = {
        "n_bridged_words": len(nb0), "n_stratum": len(strat0),
        "pos_counts": dict(collections.Counter(p[2] for p in strat0)),
        "spearman_ci_halfwidth_approx": round(1.96 / max(len(strat0) - 3, 1) ** 0.5, 4),
        "rule": f"n < {DESIGN_GATE_MIN_N} -> UNDERPOWERED BY CONSTRUCTION; report as such, never "
                f"bank a null",
        "GATE": "PASS" if len(strat0) >= DESIGN_GATE_MIN_N else "UNDERPOWERED_BY_CONSTRUCTION",
        "core_shrink": {"AoA_le_6_on_incumbent_vocab":
                        len({w for w, v in aoa.items() if v <= AOA_CORE_MAX and w in incumbent}),
                        "AoA_le_6_on_intersection": len(core)},
    }
    print(f"[design-gate] n={len(strat0)} {design_gate['GATE']} POS={design_gate['pos_counts']}",
          flush=True)

    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_PERM={N_PERM} out={out_dir}", flush=True)

    parts = out_dir / "parts"
    parts.mkdir(parents=True, exist_ok=True)

    def part_path(space: str) -> Path:
        return parts / f"{unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, space)}.json"

    def compute(space: str) -> Dict:
        raw = _SPACE_TABLES[space]
        ctx = {"vocab": vocab, "raw": raw, "pairs": pairs, "idx": idx, "held_out": held_out,
               "core": core, "partners": partners, "counts": counts, "aoa": aoa, "cooc": cooc}
        _CUR["cfg"] = space
        print(f"[cfg] {space} START dims={space_info[space]['dims']} "
              f"t+{round(time.time()-t_start,1)}s", flush=True)
        r = THEM.run_config(space, enriched, set(core), False, False, ctx, do_pos=True)
        rec = {"space": space, "code_version": CODE_VERSION, "run_mode": RUN_MODE, "result": r,
               "cos": {a: [float(x) for x in v] for (s2, a), v in _COS.items() if s2 == space}}
        if space in _STRAT:
            rec["gold"] = [float(x) for x in _STRAT[space]["gold"]]
            rec["ia"] = [int(x) for x in _STRAT[space]["ia"]]
            rec["ib"] = [int(x) for x in _STRAT[space]["ib"]]
        tmp = part_path(space).with_suffix(".tmp")
        with io.open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rec, fh)
        os.replace(tmp, part_path(space))         # atomic; never a shared append log
        _CUR["cfg"] = None
        return rec

    def absorb(space: str, rec: Dict) -> None:
        for arm, v in rec.get("cos", {}).items():
            _COS[(space, arm)] = np.asarray(v, dtype=np.float64)
        if space not in _STRAT and "gold" in rec:
            _STRAT[space] = {"ia": np.asarray(rec["ia"]), "ib": np.asarray(rec["ib"]),
                             "gold": np.asarray(rec["gold"], dtype=np.float64)}

    if _ARGS.space:
        if _ARGS.space not in SPACE_ORDER:
            raise SystemExit(f"[fatal] unknown --space {_ARGS.space}; expected one of {SPACE_ORDER}")
        rec = compute(_ARGS.space)
        print(f"[worker] wrote {part_path(_ARGS.space)} "
              f"({round(time.time()-t_start,1)}s)", flush=True)
        return 0

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    results: Dict[str, Dict] = {}
    for space in SPACE_ORDER:
        pp = part_path(space)
        if pp.exists():
            rec = json.load(io.open(pp, encoding="utf-8"))
            results[space] = rec["result"]
            absorb(space, rec)
            print(f"[cfg] {space} LOADED from part ({len(rec.get('cos', {}))} cosines)", flush=True)
            continue
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, space)
        if key in done and key in units:
            rec = units[key]
            results[space] = rec["result"]
            absorb(space, rec)
            print(f"[cfg] {space} RESUMED from checkpoint", flush=True)
            continue
        rec = compute(space)
        record_unit(str(out_dir), key, {"space": space, "part": str(part_path(space))})
        results[space] = rec["result"]
    _CUR["cfg"] = None

    # ---- VALIDITY V3: the SPACE-INDEPENDENT floors must be IDENTICAL across spaces
    v3 = {"F_ORTHOGRAPHIC": {}, "F_FREQUENCY_HARDENED": {}, "F_SCRAMBLE_PERM_P95_per_space": {}}
    for s in SPACE_ORDER:
        fl = results[s].get("floors", {})
        v3["F_ORTHOGRAPHIC"][s] = fl.get(THEM.FLOOR_ORTHO, {}).get("rho")
        v3["F_FREQUENCY_HARDENED"][s] = fl.get(THEM.FLOOR_FREQ, {}).get("rho")
        k1 = results[s].get("arms", {}).get(KNOWN_ANSWER, {})
        v3["F_SCRAMBLE_PERM_P95_per_space"][s] = k1.get("scramble_null", {}).get("p95")
    v3["ortho_identical_across_spaces"] = len(set(
        round(x, 9) for x in v3["F_ORTHOGRAPHIC"].values() if x is not None)) == 1
    v3["freq_identical_across_spaces"] = len(set(
        round(x, 9) for x in v3["F_FREQUENCY_HARDENED"].values() if x is not None)) == 1
    v3["WHY"] = ("F_ORTHOGRAPHIC and F_FREQUENCY_HARDENED never touch the codes, so on a FIXED "
                 "stratum they are ONE number shared by every arm. Four different values would be "
                 "four bootstrap-noise variants of one floor reported as four floors. "
                 "F_SCRAMBLE_PERM_P95 IS space-dependent and MUST differ.")

    # ---- VALIDITY V4: the stratum really is identical across spaces
    ns = {s: results[s].get("n_stratum") for s in SPACE_ORDER}
    v4 = {"n_stratum_per_space": ns, "identical": len(set(ns.values())) == 1,
          "pos_counts_per_space": {s: results[s].get("pos_counts") for s in SPACE_ORDER}}
    if _STRAT:
        ref = _STRAT[SPACE_ORDER[0]]
        v4["gold_vector_identical_across_spaces"] = all(
            np.array_equal(_STRAT[s]["gold"], ref["gold"]) and np.array_equal(_STRAT[s]["ia"],
                                                                              ref["ia"])
            and np.array_equal(_STRAT[s]["ib"], ref["ib"]) for s in _STRAT)

    # ---- G0 FIRST, before any treatment number is read
    g0 = {}
    for s in SPACE_ORDER:
        gg = results[s].get("G0_power_gate", {})
        g0[s] = {"K1_clears_floor": gg.get("K1_clears_floor"), "K1_rho": gg.get("K1_rho"),
                 "K1_margin": gg.get("K1_margin"), "K1_band": gg.get("K1_band"),
                 "READABLE": bool(gg.get("K1_clears_floor"))}
    g0["RULE"] = ("if K1 does not clear THAT SPACE'S floors CI-separated, every arm on that space "
                  "is POWER_INSUFFICIENT, NEVER FAIL. Checked and reported BEFORE any treatment "
                  "number is read.")

    # ---- the deciding quantity
    gold = _STRAT[SPACE_ORDER[0]]["gold"] if _STRAT else np.array([])
    ret = retention_block(gold, N_BOOT, BOOT_SEED) if len(gold) else {
        "status": "NOT_CONSTRUCTIBLE"}

    # ---- POS falsifier, read out per space
    def pos_block(space: str, arm: str) -> Dict:
        a = results.get(space, {}).get("arms", {}).get(arm, {})
        return a.get("POS_STRATA_WITH_OWN_FLOORS", a.get("POS_RHO_ONLY", {}))

    fals = {
        "PRE_REGISTERED_PREDICTION": (
            "the affect gain must be CONCENTRATED in V and A and near-zero in N. If the bridged "
            "retention gain is UNIFORM across POS the affect channel is not doing what the biology "
            "says and the result is a topical artefact -- report it as a MECHANISM FAILURE even if "
            "the headline rises."),
        "STATED_IN_ADVANCE_IN_THE_PREREG": (
            "SimVerb-3500 is NOT on disk and was NOT acquired. The VERB (n~79) and ADJECTIVE "
            "(n~43) sub-strata are EXPECTED to be POWER_INSUFFICIENT and their numbers may NOT be "
            "reported as a FAIL in either direction."),
        "per_space": {s: {"K1_OWN_NORMS": pos_block(s, KNOWN_ANSWER),
                          "K2_ORACLE_BRIDGE": pos_block(s, "K2_ORACLE_BRIDGE"),
                          PRIMARY_ARM: pos_block(s, PRIMARY_ARM)} for s in SPACE_ORDER},
    }
    pos_g0 = {}
    for s in SPACE_ORDER:
        blk = pos_block(s, KNOWN_ANSWER)
        pos_g0[s] = {}
        for tag in ("N", "V", "A"):
            e = blk.get(tag, {}) if isinstance(blk, dict) else {}
            pos_g0[s][tag] = {
                "n": e.get("n"), "K1_rho": (e.get("rho") or {}).get("point"),
                "K1_band": e.get("band"), "strongest_floor": e.get("strongest_floor"),
                "G0": ("PASS" if e.get("clears_floor") else
                       ("POWER_INSUFFICIENT" if e.get("n") else "NOT_CONSTRUCTIBLE"))}
    fals["G0_PER_POS_SUB_STRATUM"] = pos_g0

    # ---- verdict
    d2 = ret.get("PAIRED_DIFFERENCES_vs_TS1", {}).get("TS2_PLUS_AFFECT_15", {})
    d4 = ret.get("PAIRED_DIFFERENCES_vs_TS1", {}).get("TS4_WIDER_UNINFORMATIVE_23", {})
    b1_clears = {s: bool(results[s].get("arms", {}).get(PRIMARY_ARM, {}).get("clears_floor"))
                 for s in SPACE_ORDER}
    readable = [s for s in TARGET_SPACE_ARMS if g0.get(s, {}).get("READABLE")]

    if design_gate["GATE"] != "PASS":
        verdict = "UNDERPOWERED_BY_CONSTRUCTION_NOT_A_NULL"
    elif not results[SPACE_ORDER[0]].get("G3_passed") or not v4.get("identical"):
        verdict = "INVALID_VALIDITY_GATE_FAILED"
    elif "TS1_CURRENT_12" not in readable or "TS2_PLUS_AFFECT_15" not in readable:
        verdict = "POWER_INSUFFICIENT_KNOWN_ANSWER_ARM_DOES_NOT_LICENSE_THE_INSTRUMENT"
    elif d4.get("CI_SEPARATED") and (d4.get("point") or 0) > 0 and \
            (d2.get("point") or 0) <= (d4.get("point") or 0):
        verdict = "REFUTED_DIMENSIONALITY_PER_SE_NOT_THE_AFFECT_CHANNEL"
    elif d2.get("CI_SEPARATED") and (d2.get("point") or 0) > 0 and not d4.get("CI_SEPARATED"):
        verdict = ("TARGET_SPACE_WAS_THE_LIMIT_AFFECT_CHANNEL_RAISES_BRIDGED_RETENTION"
                   if any(b1_clears[s] for s in readable)
                   else "MIDDLE_BAND_SPACE_HELPS_AND_IS_NOT_YET_SUFFICIENT")
    else:
        verdict = "MECHANISM_IS_THE_LIMIT_TARGET_SPACE_EXONERATED"

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "prereg": PREREG, "verdict": verdict, "summary": verdict,
        "verdict_msg": (
            "Holding the bridging mechanism, the graph, the core, the held-out set and the stratum "
            "FIXED and varying ONLY the target space: does bridged semantic RETENTION rise when the "
            "space gains the AFFECT channel (a separable block with its own neural substrate), and "
            "does the same-magnitude NO-NEW-CHANNEL widening fail to reproduce it? -> " + verdict),
        "HOW_TO_READ_A_NULL": (
            "The brain does this, so the capability is DEMONSTRATED. A null here is a fact about "
            "OUR IMPLEMENTATION, never about the capability. Deflate claims, never ambition."),
        "NO_NUMBER_CARRIED": (
            "The 8.2% retention figure from exp_thematic_relation_supply_bridged_grounding_v2 is "
            "NOT imported. It was computed on a DIFFERENT stratum with a DIFFERENT core. "
            "TS1_CURRENT_12 re-earns its own baseline inside this cell. Every floor is recomputed "
            "on THIS stratum with THIS scorer."),
        "config": {"N_BOOT": N_BOOT, "N_PERM": N_PERM, "BOOT_SEED": BOOT_SEED,
                   "T_MARGIN_MIN": T_MARGIN_MIN, "AOA_CORE_MAX": AOA_CORE_MAX,
                   "RATIO_GUARD": RATIO_GUARD,
                   "THEMATIC_MIN_COUNT": THEM.THEMATIC_MIN_COUNT,
                   "THEMATIC_MIN_PMI": THEM.THEMATIC_MIN_PMI,
                   "THEMATIC_TOPK": THEM.THEMATIC_TOPK,
                   "NULL_SEEDS": list(THEM.NULL_SEEDS), "POS_MIN_N": THEM.POS_MIN_N,
                   "ORTHO_DIMS": list(THEM.ORTHO_DIMS)},
        "THE_ONE_VARIABLE": (
            "the TARGET SPACE. Edge set, core membership, held-out membership, stratum, scorer "
            "form, bootstrap seed and permutation count are IDENTICAL across arms -- asserted by "
            "validity gates V3 and V4 below, not merely intended."),
        "DISCLOSED_RUNTIME_PARAMETERISATION": {
            "P1_code_matrix": "exp_bridged_grounding_from_core_v1.code_matrix hard-codes 12 dims; "
                              "replaced at runtime by a dimension-agnostic function proved "
                              "BIT-IDENTICAL at d=12 (selftest S1). NEITHER SIBLING FILE EDITED.",
            "P2_score_arm": "exp_thematic_relation_supply_bridged_grounding_v2.score_arm WRAPPED "
                            "to record the per-arm cosine run_config discards; the original is "
                            "called and its value passed through unchanged (selftest S2)."},
        "spaces": space_info,
        "DESIGN_GATE_measured_before_any_arm_was_scored": design_gate,
        "population": {"intersection_vocabulary": len(inter), "simlex_pairs_all": len(pairs_all),
                       "simlex_pairs_on_intersection": len(pairs), "simlex_words": len(vocab),
                       "core_AoA_le_6_intersected": len(core), "held_out": len(held_out),
                       "def_graph_nodes": len(def_graph), "def_graph_rows": def_rows,
                       "thematic_graph_nodes": len(them_graph),
                       "enriched_graph_nodes": len(enriched),
                       "relation_pattern_census": pat_census},
        "thematic_extraction": {**edges["report"], **them_info},
        "G0_POWER_GATE_CHECKED_FIRST": g0,
        "V3_space_independent_floors_must_be_identical": v3,
        "V4_stratum_identical_across_spaces": v4,
        "THE_DECIDING_QUANTITY_paired_retention": ret,
        "POS_FALSIFIER": fals,
        "B1_clears_floor_per_space": b1_clears,
        "results_per_space": results,
        "selftest_evidence": ev,
        "brain_fidelity_block": {
            "a_BRAIN_STRUCTURE_per_component": {
                "sensorimotor spokes (11 of the incumbent 12 dims)":
                    "modality-specific perceptual and motor cortices, converging on the ANTERIOR "
                    "TEMPORAL LOBE hub. Spoke lesion loses one facet; hub lesion loses meaning "
                    "across the board. [PINNED]",
                "AFFECT (the channel added by TS2)":
                    "AMYGDALA (population coding of valence), ORBITOFRONTAL and VENTROMEDIAL "
                    "PREFRONTAL CORTEX, and INSULA (interoceptive). These are DIFFERENT NEURAL "
                    "SYSTEMS from the sensorimotor spokes, which is WHY affect is a separate "
                    "CHANNEL and not more dimensions of the same one. Separable. [PINNED] "
                    "Affective experience is a grounding channel for ABSTRACT concepts and "
                    "abstract words receive higher valence and arousal ratings than concrete ones "
                    "(Vigliocco et al., PMID 23408565). [PINNED]",
                "the thematic relation graph (held FIXED here)":
                    "TEMPORO-PARIETAL: posterior middle temporal gyrus + angular gyrus. Double "
                    "dissociated from the taxonomic anterior-temporal channel by lesion (Schwartz "
                    "et al. 2011 PNAS VLSM; Mirman, Landrigan & Britt 2017). [PINNED]",
                "the additive bridge operator (held FIXED here)":
                    "LATL conceptual combination; ADDITIVITY PINNED (Baron & Osherson 2011), the "
                    "specific transformation UNPINNED and OURS.",
                "the AoA<=6.0 core cut (held FIXED here)":
                    "the early sensorimotor-grounded lexicon. OURS as an operationalisation."},
            "b_ORGAN_REUSE_enumerated_from_disk_then_reconciled_to_the_registry":
                "See organ_reuse_runtime below -- enumerated by RUNTIME (imported and called, "
                "module __file__ and byte size recorded), then reconciled READ-ONLY to "
                "data/capability_registry.jsonl. NEVER registry-first. This cell writes NOTHING "
                "to the registry; WIRE-or-SHELVE is a separate act at land time.",
            "c_PINNED_vs_OUR_INVENTION": {
                "PINNED": ["affect is a separable semantic block with its own neural substrate",
                           "hub-and-spoke architecture with separable spokes",
                           "abstract words carry higher affective ratings than concrete words",
                           "taxonomic and thematic are separate systems",
                           "additivity of conceptual combination"],
                "OURS_BEING_TESTED": [
                    "the CHOICE of Warriner V/A/D as the 3-dim operationalisation of the affect "
                    "block", "z-scored concatenation as the way a second channel joins the first",
                    "the intersection-stratum construction", "the AoA<=6.0 core cut",
                    "the event-co-participation edge rule inherited from the sibling",
                    "the 11 rater-SD columns as the no-new-channel widening control"]},
            "d_SHELVE_REVIVAL_CRITERION_BRAIN_FRAMED_never_performance_framed": (
                "Whatever this cell returns, the direction is NOT shelved on a number. Revival is "
                "triggered by closing a NAMED BIOLOGICAL DIVERGENCE, in order: (1) our thematic "
                "edge is UNTYPED co-participation where the brain's thematic relations are "
                "ROLE-STRUCTURED (agent/patient/location/instrument) -- we own "
                "hdlab/thematic_role_labeler.py and extract_predicates_v62 and have never fed "
                "either into a bridging graph at scale; (2) the space still lacks the SOCIAL block "
                "(bilateral ATL / TPJ / dmPFC / precuneus) and the SPATIAL-TEMPORAL-CAUSAL block; "
                "(3) a per-word rating is a SENSE-AVERAGE and the brain settles on a sense in "
                "context (Trott & Bergen, arXiv 2203.05648); (4) no informative-encounter selector "
                "(Medina et al. 2011); (5) no consolidation (Dumay & Gaskell 2007)."),
        },
        "named_divergences_from_the_biology": [
            "MISSING SPOKES: even TS2 covers THREE of Binder's seven blocks. SOCIAL relevance "
            "(bilateral ATL / TPJ / dmPFC / posterior cingulate) and SPATIAL-TEMPORAL-CAUSAL are "
            "absent. Neither is on disk as a rating set.",
            "EDGE TYPING: our thematic edge is UNTYPED event co-participation; the brain's is "
            "ROLE-STRUCTURED.",
            "SENSE AVERAGING: a per-word rating averages over senses; the brain settles on a sense "
            "in context.",
            "HAND-RATED PROXY: these are human INTROSPECTIVE ratings, not neural recordings, and "
            "hand-rating does not scale. This cell re-scopes the landing space; it does NOT solve "
            "the scaling problem that motivates Phase 2.",
            "NO INFORMATIVE-ENCOUNTER SELECTOR and NO CONSOLIDATION.",
        ],
        "elapsed_s": round(time.time() - t_start, 1),
    }
    metrics["organ_reuse_runtime"] = {
        m.__name__: {"file": str(Path(m.__file__).resolve()).replace("\\", "/"),
                     "bytes": Path(m.__file__).stat().st_size}
        for m in (CELL, THEM, INS, FT, TX, GS)}
    write_metrics(out_dir, metrics)

    print("\n===== RESULTS (one variable: the TARGET SPACE)")
    for s in SPACE_ORDER:
        r = results[s]
        print(f"\n--- {s}  dims={space_info[s]['dims']}  n={r.get('n_stratum')}  "
              f"POS={r.get('pos_counts')}  "
              f"G0={'PASS' if g0[s]['K1_clears_floor'] else 'FAIL->POWER_INSUFFICIENT'}")
        for a in (KNOWN_ANSWER, "K2_ORACLE_BRIDGE", PRIMARY_ARM):
            v = r.get("arms", {}).get(a, {})
            if "rho" not in v or "margin_over_strongest_floor" not in v:
                continue
            m = v["margin_over_strongest_floor"]
            print(f"  {a:<22} rho={v['rho']['point']:+.4f} "
                  f"[{v['rho']['ci95'][0]:+.4f},{v['rho']['ci95'][1]:+.4f}]  "
                  f"floor={v['strongest_floor']:<22}"
                  f"({v['floor_rho_by_arm'][v['strongest_floor']]:+.4f})  "
                  f"margin={m['point']:+.4f} [{m['ci95'][0]:+.4f},{m['ci95'][1]:+.4f}] "
                  f"{v['band']:<14} {v.get('verdict_for_this_arm','')}")
    print("\nRETENTION:", json.dumps(ret.get("per_space_point", {}), indent=1))
    print("PAIRED RETENTION DIFF vs TS1:",
          json.dumps(ret.get("PAIRED_DIFFERENCES_vs_TS1", {}), indent=1))
    print("VERDICT:", verdict)
    print(f"[done] {out_dir}/metrics.json ({metrics['elapsed_s']}s)", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:                                     # noqa: BLE001 -- printed, never hidden
        import traceback
        traceback.print_exc()
        sys.exit(2)
