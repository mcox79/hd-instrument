#!/usr/bin/env python
"""GEOMETRY-ABLATION for native role-filler binding compgen (v1). HARNESS-REUSE, NO NEW MECHANISM.

Resolves the LEARNED-vs-FIXED axis the HP2 conflation left open (drill 2026-07-22): does native's held-out
compositional generalization come from the LEARNED binding, or is it RIDING ON the free distributional
filler-GEOMETRY (PPMI-SVD)?

Reuses experiments/exp_compgen_native_bind_attested_real_text_v2.py wholesale (NativeBind, FlatSharedReadout,
build_corpus, make_attested_split, train_arm, eval_*, codebook_geometry). The ONLY change is a GEOMETRY
ABLATION on the corpus embedding table: the "meaningful geometry" is entirely corp["emb"] (consumed
identically by every arm as the real-feature front-end Rfeat). The ablation replaces emb with
IDENTITY-PRESERVING, SEMANTIC-GEOMETRY-DESTROYING random unit vectors:
  - PRESERVED: concept identity (each concept -> one fixed distinct code every use), dimensionality, unit norm.
  - DESTROYED: inter-concept distributional structure (random Gaussian -> near-orthogonal; no neighbors).
Everything else identical between geom and random: SAME triples / vocab / attested held-out split / subsample.
ONE VARIABLE = filler-geometry meaningful-vs-randomized.

ARMS (2x3 factorial): {native_bind_shared, flat_shared_readout, native_bind_tied} x {geom, random}
  + native_bind_scramble (decode-time random-role-key lesion) x {geom, random}.

PRE-REG: preregs/2026-07-22_compgen_geometry_ablation_v1.md (HARD-PASS-A / HARD-FAIL / MIDDLE + must-fail sanity).
CONFLICT-OF-INTEREST: HARD-PASS-A is a CG-CANDIDATE ONLY -> fresh adversarial VET + USER. No self-declared CG.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (native_geom vs native_random MUST differ = ablation changed something)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: classification-accuracy discriminator; bands feasibility-checked vs chance=1/V + REAL-geom reference
# - baseline_in_band: native_random in-dist swept into [0.75,0.90] hard band; must-fail sanity native_random ind>=0.60
# - discriminator survives scale: FULL geometry (V~492, N=256) at smoke; fewer fractions/seeds only
# - deterministic_seeding: fixed int seeds + np rng(fixed) + sorted() splits; NO hash()-seeded RNG
# - progress_logging: line_buffered stdout; wall << 30min (foreground-to-completion, LOCAL)
# - all numbers MEASURED@ this cell's metrics.json
# LOCAL-ONLY: no push, no store mutation, no atom bank. Skunkworks VETs after land.

Anchor: compgen_geometry_ablation_v1
"""
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
import exp_compgen_native_bind_attested_real_text_v2 as base  # noqa: E402  harness reuse

ANCHOR_NAME = "compgen_geometry_ablation_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

N_DIM = base.N_DIM
EMB_D = base.EMB_D
GEOM_SEED = 12345  # fixed; random geometry is ONE fixed instance (seed-independent, like the real emb)

TRAINED_ARMS = ["native_bind_shared", "flat_shared_readout", "native_bind_tied"]
VARIANTS = ["geom", "random"]

DATA_FRACTIONS_FULL = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.75, 0.90, 1.0]
DATA_FRACTIONS_SMOKE = [0.30, 0.60, 1.0]
FULL = dict(fractions=DATA_FRACTIONS_FULL, epochs=50, lr=1e-2, batch=256, seeds=[7, 13, 19])
SMOKE = dict(fractions=DATA_FRACTIONS_SMOKE, epochs=50, lr=1e-2, batch=256, seeds=[7])

# PRE-REGISTERED gate constants (fixed BEFORE running; see prereg .md)
HARD_BAND = (0.75, 0.90); HARD_TARGET = 0.825
HARDER_BAND = (0.55, 0.68); HARDER_TARGET = 0.62
A1_CHANCE_MULT = 20.0     # native_random_ho >= 20x chance
A2_FLAT_MARGIN = 0.15     # native_random_ho >= flat_geom_ho + 0.15
A3_GEOM_RETAIN = 0.50     # native_random_ho >= 0.50 * native_geom_ho
A4_INIT_MAX = 0.10; A4_RISE_MIN = 0.20
A5_SCRAMBLE_MAX = 0.05
HF_FLAT_MARGIN = 0.05     # native_random_ho <= flat_geom_ho + 0.05  -> collapse
HF_CHANCE_MULT = 5.0      # native_random_ho <= 5x chance            -> collapse
HF_GEOM_RETAIN = 0.20     # native_random_ho <= 0.20 * native_geom_ho -> collapse
SANITY_INDIST_MIN = 0.60  # native_random in-dist @ full must exceed (identity preserved)
SANITY_INDIST_INVALID = 0.40  # below this -> ABLATION_INVALID (identity broken)


# ============================ geometry ablation ============================
def randomize_geometry(corp):
    """Identity-preserving, semantic-geometry-destroying emb ablation.
    Each concept -> a FIXED distinct random Gaussian unit vector (same V x EMB_D shape + unit-L2 norm as the
    real PPMI-SVD emb). Preserves per-concept identity; destroys inter-concept distributional structure
    (random Gaussian is near-orthogonal). ONE fixed instance (GEOM_SEED), seed-independent like the real emb."""
    V, d = corp["emb"].shape
    rng = np.random.default_rng(GEOM_SEED)          # fixed int seed; NOT hash()
    R = rng.standard_normal((V, d)).astype(np.float32)
    R = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-9)  # unit norm, matches real emb rows
    corp2 = dict(corp)                               # shallow copy; only emb differs
    corp2["emb"] = R
    return corp2


def geometry_stats(corp):
    """Off-diagonal |cos| of the FHRR codebook derived from this corp's emb (structure witness)."""
    return base.codebook_geometry(corp, GEOM_SEED)  # (mean_off_cos, rand_floor, max_off_cos)


# ============================ run ============================
def run(cfg, run_mode):
    t0 = time.perf_counter()
    corp_geom = base.build_corpus()
    corp_rand = randomize_geometry(corp_geom)
    corps = {"geom": corp_geom, "random": corp_rand}
    V = corp_geom["V"]; chance = 1.0 / V
    seeds = cfg["seeds"]; s0 = seeds[0]

    g_off, g_floor, g_max = geometry_stats(corp_geom)
    r_off, r_floor, r_max = geometry_stats(corp_rand)

    per = []
    curve_rows = {"geom": [], "random": []}   # native_bind_shared held-out [init, final] @ full
    arm_sig = {}

    for seed in seeds:
        # split + eval sets are IDENTICAL across variants (depend only on vocab/agents/patients/seed)
        train_trips, test_trips, _ = base.make_attested_split(corp_geom, seed)
        te = base._tz(corp_geom, test_trips)
        slots = torch.tensor([t[3] for t in test_trips], dtype=torch.long)
        te_tensors = (te[0], te[1], te[2], slots)
        rng = np.random.default_rng(seed + 5)
        n_ind = max(8, int(0.20 * len(train_trips)))
        ind_idx = sorted(rng.choice(len(train_trips), size=min(n_ind, len(train_trips)), replace=False).tolist())
        indist_trips = [train_trips[i] for i in ind_idx]
        ind_tensors = base._tz(corp_geom, indist_trips)

        for frac in cfg["fractions"]:
            sub = base._subsample(train_trips, frac, seed)
            is_full = abs(frac - 1.0) < 1e-6
            for variant in VARIANTS:
                corp = corps[variant]
                for arm in TRAINED_ARMS:
                    track = (arm == "native_bind_shared" and is_full)
                    model, ind, ho, curve = base.train_arm(arm, corp, cfg, seed, sub, te_tensors,
                                                           ind_tensors, track_curve=track)
                    per.append({"variant": variant, "frac": frac, "seed": seed, "arm": arm,
                                "indist": ind, "heldout": ho})
                    if track:
                        curve_rows[variant].append(curve)
                    if arm == "native_bind_shared":
                        # scramble = decode-time random-role-key lesion of the trained native model
                        gk = torch.Generator().manual_seed(seed + 424242)
                        dr = torch.exp(1j * (torch.rand(3, N_DIM, generator=gk) * (2 * np.pi))).to(torch.complex64)
                        sc_ho = base.eval_heldout(model, te[0], te[1], te[2], slots, dr=dr)
                        sc_ind = base.eval_indist(model, ind_tensors[0], ind_tensors[1], ind_tensors[2], dr=dr)
                        per.append({"variant": variant, "frac": frac, "seed": seed,
                                    "arm": "native_bind_scramble", "indist": sc_ind, "heldout": sc_ho})
                        if seed == s0 and is_full:
                            with torch.no_grad():
                                la, lp = model(ind_tensors[0][:32], ind_tensors[1][:32], ind_tensors[2][:32])
                                arm_sig["native_bind_shared__" + variant] = \
                                    torch.cat([la.flatten(), lp.flatten()]).numpy().astype(np.float32)
                    elif seed == s0 and is_full:
                        with torch.no_grad():
                            la, lp = model(ind_tensors[0][:32], ind_tensors[1][:32], ind_tensors[2][:32])
                            arm_sig[arm + "__" + variant] = \
                                torch.cat([la.flatten(), lp.flatten()]).numpy().astype(np.float32)
                print("[seed=%d frac=%.2f %s] done (train=%d)" % (seed, frac, variant, len(sub)), flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF): native_geom vs native_random MUST differ (ablation actually changed emb)
    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in arm_sig.items()}
    dk = sorted(digests)
    for i in range(len(dk)):
        for j in range(i + 1, len(dk)):
            assert digests[dk[i]] != digests[dk[j]], \
                "META_RULE_AF VIOLATION: arms %s / %s bit-identical" % (dk[i], dk[j])
    assert "native_bind_shared__geom" in digests and "native_bind_shared__random" in digests, \
        "missing native arm signatures"

    # attested-novelty audit (seed s0)
    tr0, te0, _ = base.make_attested_split(corp_geom, s0)
    tr0_ag = set(corp_geom["vidx"][a] for (a, v, p) in tr0)
    tr0_pt = set(corp_geom["vidx"][p] for (a, v, p) in tr0)
    breaches = 0
    for (a, v, p, slot) in te0:
        if slot == 0 and corp_geom["vidx"][a] in tr0_ag: breaches += 1
        if slot == 1 and corp_geom["vidx"][p] in tr0_pt: breaches += 1

    sweep = summarize(per)
    curve_agg = {var: ([float(np.mean([c[0] for c in rows])), float(np.mean([c[1] for c in rows]))]
                       if rows else [float("nan"), float("nan")])
                 for var, rows in curve_rows.items()}

    geom_ok = (g_off >= 1.5 * g_floor) and (r_off <= 1.2 * r_floor)
    verdict, msg, gate = compute_ablation_verdict(sweep, per, curve_agg, breaches, chance,
                                                  geom_ok, g_off, r_off, g_floor)
    elapsed = time.perf_counter() - t0

    expected_units = (len(VARIANTS) * len(TRAINED_ARMS) * len(cfg["fractions"]) * len(seeds)
                      + len(VARIANTS) * len(cfg["fractions"]) * len(seeds))  # + scramble rows
    n_units = len(per)

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "compgen GEOMETRY-ABLATION v1: " + verdict,
        "elapsed_s": round(elapsed, 2), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "V": V, "nverb": corp_geom["nverb"], "n_triples": len(corp_geom["triples"]), "chance": round(chance, 5),
        "geom_off_cos": round(g_off, 4), "geom_off_cos_max": round(g_max, 4),
        "random_off_cos": round(r_off, 4), "random_off_cos_max": round(r_max, 4),
        "rand_floor": round(g_floor, 4), "geometry_destroyed_ok": bool(geom_ok),
        "attested_novelty_breaches_seed0": breaches,
        "n_train_seed0": len(tr0), "n_heldout_seed0": len(te0),
        "sweep_by_variant_fraction": sweep,
        "learning_curve_native_ho": curve_agg,
        "ablation_gate": gate,
        "ablation_prereg": {
            "hard_band": list(HARD_BAND), "harder_band": list(HARDER_BAND),
            "a1_chance_mult": A1_CHANCE_MULT, "a2_flat_margin": A2_FLAT_MARGIN, "a3_geom_retain": A3_GEOM_RETAIN,
            "a4_init_max": A4_INIT_MAX, "a4_rise_min": A4_RISE_MIN, "a5_scramble_max": A5_SCRAMBLE_MAX,
            "hf_flat_margin": HF_FLAT_MARGIN, "hf_chance_mult": HF_CHANCE_MULT, "hf_geom_retain": HF_GEOM_RETAIN,
            "sanity_indist_min": SANITY_INDIST_MIN},
        "cardinality_ok": n_units == expected_units, "expected_n_units": expected_units, "n_units": n_units,
        "arms_digests": digests, "config": {k: v for k, v in cfg.items()}, "per_unit": per,
    }
    return metrics


def summarize(per):
    """per -> per-(variant,frac) aggregate dict over seeds (sorted)."""
    ARMS_ALL = TRAINED_ARMS + ["native_bind_scramble"]
    out = []
    for var in VARIANTS:
        for f in sorted(set(r["frac"] for r in per if r["variant"] == var)):
            row = {"variant": var, "frac": f}
            for arm in ARMS_ALL:
                rr = [r for r in per if r["variant"] == var and r["frac"] == f and r["arm"] == arm]
                row[arm + "_indist"] = round(float(np.mean([r["indist"] for r in rr])), 4) if rr else None
                row[arm + "_heldout"] = round(float(np.mean([r["heldout"] for r in rr])), 4) if rr else None
            out.append(row)
    return out


# ============================ verdict ============================
def _closest(sweep, variant, arm, target):
    rows = [r for r in sweep if r["variant"] == variant]
    return min(rows, key=lambda r: abs(r[arm + "_indist"] - target))


def _matched_point(sweep, per, chance, target, band):
    """Match native_geom + flat_geom to native_random's in-dist at a target hard level."""
    NB, FL = "native_bind_shared", "flat_shared_readout"
    nr = _closest(sweep, "random", NB, target)         # native_random anchor row
    nr_ind = nr[NB + "_indist"]; nr_ho = nr[NB + "_heldout"]; nr_frac = nr["frac"]
    ng = _closest(sweep, "geom", NB, nr_ind)           # native_geom matched to nr in-dist
    fg = _closest(sweep, "geom", FL, nr_ind)           # flat_geom matched to nr in-dist
    sc_rows = [r for r in per if r["variant"] == "random" and abs(r["frac"] - nr_frac) < 1e-9
               and r["arm"] == "native_bind_scramble"]
    sc_ho = float(np.mean([r["heldout"] for r in sc_rows])) if sc_rows else float("nan")
    return {
        "target_in_dist": target, "band": list(band),
        "native_random_frac": nr_frac, "native_random_ind": round(nr_ind, 4), "native_random_ho": round(nr_ho, 4),
        "native_random_in_band": bool(band[0] <= nr_ind <= band[1]),
        "native_geom_frac": ng["frac"], "native_geom_ind": round(ng[NB + "_indist"], 4),
        "native_geom_ho": round(ng[NB + "_heldout"], 4),
        "flat_geom_frac": fg["frac"], "flat_geom_ind": round(fg[FL + "_indist"], 4),
        "flat_geom_ho": round(fg[FL + "_heldout"], 4),
        "scramble_random_ho_at_frac": round(sc_ho, 4),
        "chance_mult_native_random_ho": round(nr_ho / chance, 1),
        "native_random_minus_flat_geom_ho": round(nr_ho - fg[FL + "_heldout"], 4),
        "native_random_over_native_geom_ho": round(nr_ho / (ng[NB + "_heldout"] + 1e-9), 3),
    }


def compute_ablation_verdict(sweep, per, curve_agg, breaches, chance, geom_ok, g_off, r_off, floor):
    hard = _matched_point(sweep, per, chance, HARD_TARGET, HARD_BAND)
    harder = _matched_point(sweep, per, chance, HARDER_TARGET, HARDER_BAND)

    # must-fail sanity: native_random in-dist @ full (identity preserved)
    nr_full = [r for r in sweep if r["variant"] == "random" and abs(r["frac"] - 1.0) < 1e-6][0]
    nr_indist_full = nr_full["native_bind_shared_indist"]
    ci, cf = curve_agg["random"]; rise = cf - ci

    sanity_valid = nr_indist_full >= SANITY_INDIST_INVALID
    sanity_ok = nr_indist_full >= SANITY_INDIST_MIN

    p = hard  # gate is evaluated at the HARD matched point
    nr_ho = p["native_random_ho"]; fg_ho = p["flat_geom_ho"]; ng_ho = p["native_geom_ho"]
    sc_ho = p["scramble_random_ho_at_frac"]

    A = {
        "A1_native_random_ge_20x_chance": nr_ho >= A1_CHANCE_MULT * chance,
        "A2_native_random_ge_flat_geom_plus_0.15": nr_ho >= fg_ho + A2_FLAT_MARGIN,
        "A3_native_random_ge_0.50x_native_geom": nr_ho >= A3_GEOM_RETAIN * ng_ho,
        "A4_curve_init_le_0.10": ci <= A4_INIT_MAX,
        "A4_curve_rise_ge_0.20": rise >= A4_RISE_MIN,
        "A5_scramble_random_le_0.05": sc_ho <= A5_SCRAMBLE_MAX,
        "A6_breaches_zero": breaches == 0,
        "native_random_in_hard_band": p["native_random_in_band"],
    }
    hard_fail = (nr_ho <= fg_ho + HF_FLAT_MARGIN) or (nr_ho <= HF_CHANCE_MULT * chance) \
        or (nr_ho <= HF_GEOM_RETAIN * ng_ho)
    hard_pass_a = all(A.values()) and sanity_ok and geom_ok

    if not sanity_valid or not geom_ok:
        verdict = "ABLATION_INVALID"
    elif hard_pass_a:
        verdict = "CG_CANDIDATE_GEOMETRY_FREE"      # LEARNED binding does it; CG-CANDIDATE ONLY -> fresh VET
    elif hard_fail:
        verdict = "MEASURED_MECHANISM"              # geometry-free collapse -> MM confirmed (HP2 conflation resolved)
    else:
        verdict = "MIDDLE_GRADED_GEOMETRY"          # partial geometry contribution

    msg = ("verdict=%s | HARD pt[ind~%.2f nr_frac=%.2f]: native_random_ho=%.3f flat_geom_ho=%.3f "
           "native_geom_ho=%.3f (nr-fg=%.3f nr/ng=%.2f nr/chance=%.1fx) scramble_random=%.3f | "
           "HARDER pt[ind~%.2f]: native_random_ho=%.3f flat_geom_ho=%.3f native_geom_ho=%.3f | "
           "sanity: native_random_indist_full=%.3f (valid=%s ok=%s) | curve %.3f->%.3f rise=%.3f | "
           "breaches=%d geom_off|cos|=%.3f rand_off|cos|=%.3f (floor=%.3f destroyed=%s) chance=%.4f | "
           "A_gates=%s"
           % (verdict, hard["native_random_ind"], hard["native_random_frac"], nr_ho, fg_ho, ng_ho,
              p["native_random_minus_flat_geom_ho"], p["native_random_over_native_geom_ho"],
              p["chance_mult_native_random_ho"], sc_ho,
              harder["native_random_ind"], harder["native_random_ho"], harder["flat_geom_ho"],
              harder["native_geom_ho"],
              nr_indist_full, sanity_valid, sanity_ok, ci, cf, rise, breaches, g_off, r_off, floor,
              geom_ok, chance, {k: bool(v) for k, v in A.items()}))
    gate = {"hard_point": hard, "harder_point": harder, "A_checks": {k: bool(v) for k, v in A.items()},
            "hard_fail_triggered": bool(hard_fail), "hard_pass_a": bool(hard_pass_a),
            "sanity_valid": bool(sanity_valid), "sanity_ok": bool(sanity_ok),
            "native_random_indist_full": round(nr_indist_full, 4),
            "learning_rise_random": round(rise, 4), "learning_init_random": round(ci, 4)}
    return verdict, msg, gate


# ============================ io ============================
def _atomic_write(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp"); final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: " + type(exc).__name__, "elapsed_s": 0.0, "run_mode": "crash",
            "anchor_name": ANCHOR_NAME, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp"); final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ============================ self-test ============================
def self_test():
    print("[self-test] start", flush=True)
    corp = base.build_corpus()
    V = corp["V"]
    corp_r = randomize_geometry(corp)
    assert corp_r["emb"].shape == corp["emb"].shape, "ablation changed emb shape"
    # identity preserved: rows distinct + consistent + unit norm
    norms = np.linalg.norm(corp_r["emb"], axis=1)
    assert np.allclose(norms, 1.0, atol=1e-4), "random emb not unit norm: %.4f..%.4f" % (norms.min(), norms.max())
    corp_r2 = randomize_geometry(corp)
    assert np.array_equal(corp_r["emb"], corp_r2["emb"]), "random emb NOT deterministic (identity unstable)"
    # every concept row distinct (identity preserved)
    uniq = np.unique(corp_r["emb"], axis=0)
    assert uniq.shape[0] == corp_r["emb"].shape[0], "random emb has duplicate rows (identity collision)"
    # geometry destroyed: random near-orthogonal, real non-orthogonal
    g_off, g_floor, g_max = geometry_stats(corp)
    r_off, r_floor, r_max = geometry_stats(corp_r)
    assert g_off >= 1.5 * g_floor, "real geometry not non-orthogonal: %.4f vs floor %.4f" % (g_off, g_floor)
    assert r_off <= 1.2 * r_floor, "random geometry NOT destroyed (off|cos|=%.4f floor=%.4f)" % (r_off, r_floor)
    print("[self-test] ablation OK: geom off|cos|=%.4f (max %.3f) -> random off|cos|=%.4f (max %.3f) floor=%.4f"
          % (g_off, g_max, r_off, r_max, g_floor), flush=True)
    # split identical across variants (only emb differs)
    tr_g, te_g, _ = base.make_attested_split(corp, 7)
    tr_r, te_r, _ = base.make_attested_split(corp_r, 7)
    assert tr_g == tr_r and te_g == te_r, "split differs across variants (should be identical)"
    print("[self-test] split identical across geom/random (train=%d heldout=%d)" % (len(tr_g), len(te_g)), flush=True)
    # TINY end-to-end: both variants train; native_random in-dist not collapsed (identity preserved); arms differ
    tiny = dict(fractions=[1.0], epochs=50, lr=1e-2, batch=256, seeds=[7])
    m = run(tiny, "self_test")
    assert m["attested_novelty_breaches_seed0"] == 0, "novelty breach"
    assert m["geometry_destroyed_ok"], "geometry_destroyed_ok False"
    nr_full = [r for r in m["sweep_by_variant_fraction"] if r["variant"] == "random"
               and abs(r["frac"] - 1.0) < 1e-6][0]
    ng_full = [r for r in m["sweep_by_variant_fraction"] if r["variant"] == "geom"
               and abs(r["frac"] - 1.0) < 1e-6][0]
    nr_ind = nr_full["native_bind_shared_indist"]
    assert nr_ind >= SANITY_INDIST_INVALID, \
        "MUST-FAIL SANITY: native_random in-dist collapsed (%.3f) -> ablation broke IDENTITY not geometry" % nr_ind
    assert len(set(m["arms_digests"].values())) == len(m["arms_digests"]), "arms not all distinct"
    assert m["arms_digests"]["native_bind_shared__geom"] != m["arms_digests"]["native_bind_shared__random"], \
        "native geom/random bit-identical (ablation did nothing)"
    print("[self-test] run OK: native_random_indist_full=%.3f native_geom_indist_full=%.3f "
          "native_random_ho=%.3f native_geom_ho=%.3f | verdict=%s"
          % (nr_ind, ng_full["native_bind_shared_indist"], nr_full["native_bind_shared_heldout"],
             ng_full["native_bind_shared_heldout"], m["verdict"]), flush=True)
    print("[self-test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if args.self_test:
        self_test(); sys.exit(0)
    cfg = SMOKE if args.smoke else FULL
    run_mode = "smoke" if args.smoke else "full"
    print("[run] mode=%s seeds=%s fractions=%s" % (run_mode, cfg["seeds"], cfg["fractions"]), flush=True)
    metrics = run(cfg, run_mode)
    path = _atomic_write(metrics)
    print("[run] %s verdict=%s" % (path, metrics["verdict"]), flush=True)
    print("[run] " + metrics["verdict_msg"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise
