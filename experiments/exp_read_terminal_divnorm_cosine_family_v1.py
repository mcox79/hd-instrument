"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- COSINE-READOUT family.

Measures whether the pooled divisive-norm (Carandini-Heeger) that fixed the register's SERIAL readout
also helps the COSINE-readout bundle consumers (hdlab.lexical_similarity / hdlab.verb_lexical_similarity;
hdlab.quality_relation reads these TRANSITIVELY through concept_similarity, so it is covered here, not a
distinct site). This is the brief's "DISTINCT readout" question: cosine of a per-component-renormed bundle
differs in DIRECTION from a pooled-normed one, so it must be MEASURED, not assumed invariant.

THE CALLER'S OWN VALIDATED TASK (reused, not re-authored): exp_n11c's 29 Tier1(synonym)/Tier2(related)/
Tier3(unrelated) probe TRIPLES + the hand-authored McRae-style CONCEPT_FEATURES lexicon + the FHRR feature
vectors. The landed organ reads similarity with `_cos_complex(a,b) = Re(sum(conj(a)*b))/d` -- an UNNORMALIZED
inner product over the (per-component-renormed) concept bundles. ordered_frac = fraction of triples with
cos_syn > cos_rel > cos_unrel (landed 0.9655 = 28/29, per-component).

KEY IDENTITY (the reason the readout is coupled to per-component): under PER-COMPONENT renorm every concept
vector has |a_i|=1 for all i, so ||a|| = sqrt(d) is CONSTANT across concepts -> the organ's `Re<a,b>/d`
readout IS the exact normalized cosine FOR per-component vectors. Pooled DIVNORM breaks that (it keeps the
graded per-component magnitude = how many features agree in phase at each component), so a divnorm bundle
read by the SAME `Re<a,b>/d` is no longer a normalized cosine (it becomes size-dependent). Mirroring the
register lesson ("a divnorm STORE needs the gain-matched READOUT"), the faithful divnorm reader is a TRUE
normalized cosine. So three distinct arms:

  PERCOMP        bundle(percomp), read Re<a,b>/d   == normalized cosine (norms constant)  -- THE FLOOR / DEFAULT
  DIVNORM_DOT    bundle(divnorm),  read Re<a,b>/d   -- divnorm store, the OLD (now size-dependent) readout
  DIVNORM_NCOS   bundle(divnorm),  read Re<a,b>/(||a||*||b||) -- divnorm store + gain-matched (normalized) read

GOLD (two, both on-disk / self-contained):
  (A) TIER task: ordered_frac over the 29 validated triples (the organ's own metric).
  (B) GRADED gold: feature-set overlap. For every concept pair, Jaccard(features) and shared-count are the
      ground truth of meaning HERE (the features ARE the semantics). Spearman rho(FHRR_sim, gold) measures how
      faithfully each (norm,readout) preserves graded overlap -- the cosine analog of the register's graded
      serial readout.

CONTROLS:
  - INFO-FREE TWIN: SCRAMBLED_FEATURES (concept->feature permuted, fixed disjoint seed). Must LOSE for every arm.
  - POSITIVE CONTROL (metric CAN move): a synthetic K-shared-feature ladder (two concepts share K of N
    i.i.d. features, sweep K). Raw/divnorm inner product tracks K linearly; PER-COMPONENT phase-flattening
    COMPRESSES the K-gradient -> demonstrates the regime where per-component provably degrades a GRADED cosine
    read, so a null on the real 29-triple task (which is only 3-level and already near-ceiling) is interpretable.

Bootstrap CIs over triples (ordered_frac) and over pairs (rho). No torch grad, CPU, sub-second.

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_cosine_family_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_cosine_family_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys
from itertools import combinations

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# KB_REFERENT: experiments/exp_n11c_shared_feature_lexical_similarity_v1.py (the caller's validated task)
# KB_REFERENT: experiments/exp_n11b_symmetric_pattern_lexical_similarity_v1.py (the 29 probe triples)
from experiments.exp_n11c_shared_feature_lexical_similarity_v1 import (  # noqa: E402
    _PROBE_TRIPLES,
    CONCEPT_FEATURES,
    _build_feature_vectors,
    _probe_words,
    _scrambled_concept_features,
)
from hdlab.bundling import bundle  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

N_DIM = 8192
SEED = 7
SCRAMBLE_SEED = 999
N_BOOT = 2000
BOOT_SEED = 20260828


# ---------------------------------------------------------------- norms + readouts -----------
def _concept_vec(features, feature_vecs, norm):
    stacked = torch.stack([feature_vecs[t] for t in sorted(features)])
    return bundle(stacked, norm=(None if norm == "percomp" else norm))


def _dot(a, b):
    """The organ's landed readout: Re(sum(conj(a)*b))/d (unnormalized)."""
    d = a.shape[0]
    return float(torch.real(torch.sum(torch.conj(a) * b))) / d


def _ncos(a, b):
    """True normalized FHRR cosine: Re<a,b>/(||a|| ||b||)."""
    num = float(torch.real(torch.sum(torch.conj(a) * b)))
    na = float(torch.sqrt(torch.sum((a * torch.conj(a)).real)))
    nb = float(torch.sqrt(torch.sum((b * torch.conj(b)).real)))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    return num / (na * nb)


ARMS = {
    "PERCOMP": ("percomp", _dot),        # == normalized cosine (constant norms) -- the FLOOR / current default
    "DIVNORM_DOT": ("divnorm", _dot),    # divnorm store, old unnormalized readout
    "DIVNORM_NCOS": ("divnorm", _ncos),  # divnorm store + gain-matched (normalized) readout
}


# ---------------------------------------------------------------- gold ------------------------
def _jaccard(fa, fb):
    fa, fb = set(fa), set(fb)
    u = len(fa | fb)
    return (len(fa & fb) / u) if u else 0.0


def _spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    rx = rx - rx.mean(); ry = ry - ry.mean()
    den = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


# ---------------------------------------------------------------- the two measurements --------
def _vecs_for(concept_map, feature_vecs, norm):
    return {w: _concept_vec(concept_map[w], feature_vecs, norm) for w in concept_map}


def _tier_scores(vecs, readout):
    """Per-triple (cos_syn, cos_rel, cos_unrel, ordered) over the 29 validated triples."""
    rows = []
    for a, s, r, u in _PROBE_TRIPLES:
        if not all(w in vecs for w in (a, s, r, u)):
            continue
        cs, cr, cu = readout(vecs[a], vecs[s]), readout(vecs[a], vecs[r]), readout(vecs[a], vecs[u])
        rows.append((cs, cr, cu, (cs > cr) and (cr > cu)))
    return rows


def _dprime(x, y):
    """Scale-free separation of two similarity distributions: (mean_x - mean_y)/sqrt(0.5(var_x+var_y))."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    pooled = np.sqrt(0.5 * (x.var() + y.var())) + 1e-12
    return float((x.mean() - y.mean()) / pooled)


def _link_dprimes(rows):
    """LINK-DECISION ROBUSTNESS on the REAL lexicon (scale-free): d' separating the must-LINK synonym tier from
    the must-NOT-link related tier (the over-link guard) and the unrelated tier. Bigger d' = a more robust link
    threshold, even if the RANK (ordered_frac) is identical across norms."""
    syn = [r[0] for r in rows]; rel = [r[1] for r in rows]; unrel = [r[2] for r in rows]
    return {"dprime_syn_vs_rel": round(_dprime(syn, rel), 4), "dprime_syn_vs_unrel": round(_dprime(syn, unrel), 4)}


def _pair_gold_and_sim(vecs, readout, words):
    """Every concept pair: (Jaccard gold, shared-count gold, FHRR sim)."""
    jac, shared, sim = [], [], []
    for a, b in combinations(words, 2):
        fa, fb = CONCEPT_FEATURES[a], CONCEPT_FEATURES[b]
        jac.append(_jaccard(fa, fb))
        shared.append(len(set(fa) & set(fb)))
        sim.append(readout(vecs[a], vecs[b]))
    return np.array(jac), np.array(shared), np.array(sim)


def _boot_mean_ci(vals, n_boot, rng):
    vals = np.asarray(vals, float)
    n = len(vals)
    if n == 0:
        return 0.0, 0.0, 0.0
    idx = rng.integers(0, n, size=(n_boot, n))
    means = vals[idx].mean(axis=1)
    return float(vals.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _boot_spearman_ci(gold, sim, n_boot, rng):
    n = len(gold)
    base = _spearman(gold, sim)
    if n == 0:
        return 0.0, 0.0, 0.0
    reps = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        reps[b] = _spearman(gold[idx], sim[idx])
    return base, float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))


# ---------------------------------------------------------------- positive control ------------
def _graded_discrim_sweep(n_dim, seed, n_trials=300, sizes=(4, 8, 16, 32, 64, 128)):
    """POSITIVE CONTROL that MEASURES the regime where per-component could break a GRADED cosine read.

    A single cosine comparison is RANK-preserving under both norms (per-component only compresses
    magnitude monotonically), so the fair positive control is DISCRIMINABILITY UNDER NOISE as the
    bundle SIZE (number of superposed features) grows -- the cosine analog of the register's overload.
    At each size N: draw many random concept pairs sharing a random K of N i.i.d. features; the gold is
    K (graded overlap). Measure, per arm:
      - rho(K, sim) across trials (graded fidelity), with a bootstrap CI, and
      - d' between adjacent overlap levels (K=N//2 vs K=N//2+1) across independent draws (fine discrimination).
    If per-component degrades FASTER than divnorm as N grows, that is the regime where the norm matters for
    a cosine read; if they track together, the cosine readout is genuinely norm-insensitive (the null is then
    interpretable: there is NO cosine overload regime, because the read does not iterate)."""
    def _mk(idxs, norm):
        return bundle(torch.stack([feats[i] for i in idxs]), norm=(None if norm == "percomp" else norm))

    out = {}
    for N in sizes:
        gen = torch.Generator().manual_seed(seed + N)
        rng = np.random.default_rng(seed + N)
        pool = 4 * N + 8
        feats = [unit_phase_vec(n_dim, gen) for _ in range(pool)]
        # graded-fidelity trials
        per_arm_gold = {a: [] for a in ARMS}
        per_arm_sim = {a: [] for a in ARMS}
        # fine-discrimination draws at K0 vs K0+1
        K0 = N // 2
        lo_sims = {a: [] for a in ARMS}
        hi_sims = {a: [] for a in ARMS}
        for _ in range(n_trials):
            perm = rng.permutation(pool)
            a_idx = list(perm[:N])
            K = int(rng.integers(0, N + 1))
            shared = a_idx[:K]
            fresh = list(perm[N:N + (N - K)])
            b_idx = shared + fresh
            for arm, (norm, readout) in ARMS.items():
                s = readout(_mk(a_idx, norm), _mk(b_idx, norm))
                per_arm_gold[arm].append(K); per_arm_sim[arm].append(s)
            # fine discrimination: same anchor, K0 vs K0+1
            for K, store in ((K0, lo_sims), (K0 + 1, hi_sims)):
                shared = a_idx[:K]
                fresh = list(perm[N:N + (N - K)])
                b_idx = shared + fresh
                for arm, (norm, readout) in ARMS.items():
                    store[arm].append(readout(_mk(a_idx, norm), _mk(b_idx, norm)))
        row = {}
        for arm in ARMS:
            rho = _spearman(per_arm_gold[arm], per_arm_sim[arm])
            lo = np.array(lo_sims[arm]); hi = np.array(hi_sims[arm])
            pooled = np.sqrt(0.5 * (lo.var() + hi.var())) + 1e-12
            dprime = float((hi.mean() - lo.mean()) / pooled)
            row[arm] = {"rho_K": round(rho, 4), "dprime_adj": round(dprime, 4)}
        out["N=%d" % N] = row
    return out


# ---------------------------------------------------------------- driver ----------------------
def cell(n_dim=N_DIM, seed=SEED, n_boot=N_BOOT):
    feature_vecs = _build_feature_vectors(n_dim, seed)
    words = _probe_words()
    scrambled_map = _scrambled_concept_features(SCRAMBLE_SEED)
    rng = np.random.default_rng(BOOT_SEED)

    res = {"arms": {}, "twin": {}}
    for arm, (norm, readout) in ARMS.items():
        vecs = _vecs_for({w: CONCEPT_FEATURES[w] for w in words}, feature_vecs, norm)
        rows = _tier_scores(vecs, readout)
        ordered = [float(r[3]) for r in rows]
        t1 = [r[0] for r in rows]; t2 = [r[1] for r in rows]; t3 = [r[2] for r in rows]
        of_mean, of_lo, of_hi = _boot_mean_ci(ordered, n_boot, rng)
        jac, shared, sim = _pair_gold_and_sim(vecs, readout, words)
        rho_j, rj_lo, rj_hi = _boot_spearman_ci(jac, sim, n_boot, rng)
        rho_s = _spearman(shared, sim)
        res["arms"][arm] = {
            "norm": norm, "readout": readout.__name__,
            "ordered_frac": round(of_mean, 4), "of_ci": [round(of_lo, 4), round(of_hi, 4)],
            "tier1": round(float(np.mean(t1)), 4), "tier2": round(float(np.mean(t2)), 4),
            "tier3": round(float(np.mean(t3)), 4), "t1_minus_t2": round(float(np.mean(t1) - np.mean(t2)), 4),
            "rho_jaccard": round(rho_j, 4), "rho_j_ci": [round(rj_lo, 4), round(rj_hi, 4)],
            "rho_shared_count": round(rho_s, 4), "n_triples": len(rows), "n_pairs": len(jac),
            "link_dprimes": _link_dprimes(rows),   # DRILL 2: link-decision robustness on the REAL lexicon
        }
        # info-free twin for this arm/readout
        tw_vecs = _vecs_for(scrambled_map, feature_vecs, norm)
        tw_rows = _tier_scores(tw_vecs, readout)
        tw_ordered = [float(r[3]) for r in tw_rows]
        twj, tws, twsim = _pair_gold_and_sim(tw_vecs, readout, words)
        res["twin"][arm] = {"ordered_frac": round(float(np.mean(tw_ordered)), 4),
                             "rho_jaccard": round(_spearman(twj, twsim), 4)}

    res["positive_control_graded_discrim"] = _graded_discrim_sweep(n_dim, seed + 555)
    # paired deltas vs the PERCOMP floor
    floor = res["arms"]["PERCOMP"]
    res["deltas_vs_percomp"] = {
        arm: {
            "d_ordered_frac": round(res["arms"][arm]["ordered_frac"] - floor["ordered_frac"], 4),
            "d_rho_jaccard": round(res["arms"][arm]["rho_jaccard"] - floor["rho_jaccard"], 4),
        }
        for arm in ARMS if arm != "PERCOMP"
    }
    return res


def _print(res):
    print("=== COSINE-READOUT family: per-component vs pooled-divnorm (lexical_similarity mechanism) ===")
    print("  task: exp_n11c 29 tier triples (ordered_frac) + feature-Jaccard graded gold; N=%d\n" % N_DIM)
    print("  arm            norm     readout  ordered_frac  [CI]              rho_Jac  [CI]             t1-t2")
    for arm in ARMS:
        a = res["arms"][arm]
        print("  %-13s %-8s %-7s  %.4f  [%.3f,%.3f]    %+.4f [%+.3f,%+.3f]   %+.4f"
              % (arm, a["norm"], a["readout"], a["ordered_frac"], a["of_ci"][0], a["of_ci"][1],
                 a["rho_jaccard"], a["rho_j_ci"][0], a["rho_j_ci"][1], a["t1_minus_t2"]))
    print("\n  info-free twin (scrambled features):")
    for arm in ARMS:
        print("    %-13s ordered_frac=%.4f  rho_Jac=%+.4f" % (arm, res["twin"][arm]["ordered_frac"], res["twin"][arm]["rho_jaccard"]))
    print("\n  deltas vs PERCOMP floor:")
    for arm, d in res["deltas_vs_percomp"].items():
        print("    %-13s d_ordered_frac=%+.4f  d_rho_Jac=%+.4f" % (arm, d["d_ordered_frac"], d["d_rho_jaccard"]))
    print("\n  DRILL 2 -- link-decision robustness on the REAL lexicon (scale-free d' between tiers; bigger=more robust):")
    for arm in ARMS:
        ld = res["arms"][arm]["link_dprimes"]
        print("    %-13s d'(syn vs rel)=%+.3f   d'(syn vs unrel)=%+.3f" % (arm, ld["dprime_syn_vs_rel"], ld["dprime_syn_vs_unrel"]))
    print("\n  POSITIVE CONTROL (graded-overlap discriminability under noise, per bundle size N):")
    print("    (rho_K = fidelity to graded overlap; dprime_adj = fine discrimination of K vs K+1)")
    pc = res["positive_control_graded_discrim"]
    print("    %-8s  %-22s %-22s %-22s" % ("size", "PERCOMP", "DIVNORM_DOT", "DIVNORM_NCOS"))
    for N, row in pc.items():
        print("    %-8s  rho=%+.3f d'=%+.3f      rho=%+.3f d'=%+.3f      rho=%+.3f d'=%+.3f"
              % (N, row["PERCOMP"]["rho_K"], row["PERCOMP"]["dprime_adj"],
                 row["DIVNORM_DOT"]["rho_K"], row["DIVNORM_DOT"]["dprime_adj"],
                 row["DIVNORM_NCOS"]["rho_K"], row["DIVNORM_NCOS"]["dprime_adj"]))


def _self_test():
    # tiny, cheap: the three arms are DISTINCT and the mechanism fires (syn>rel>unrel) under each arm.
    fv = _build_feature_vectors(256, SEED)
    for arm, (norm, readout) in ARMS.items():
        va = _concept_vec(CONCEPT_FEATURES["vessel"], fv, norm)
        vf = _concept_vec(CONCEPT_FEATURES["ship"], fv, norm)   # near-synonym of vessel
        vd = _concept_vec(CONCEPT_FEATURES["dock"], fv, norm)   # related-not-synonym
        vh = _concept_vec(CONCEPT_FEATURES["happy"], fv, norm)  # unrelated
        s_syn, s_rel, s_unrel = readout(va, vf), readout(va, vd), readout(va, vh)
        assert s_syn > s_rel > s_unrel, "%s mechanism-fires broken: %.3f %.3f %.3f" % (arm, s_syn, s_rel, s_unrel)
    # PERCOMP dot == PERCOMP ncos (constant norms) -- the coupling identity
    va = _concept_vec(CONCEPT_FEATURES["vessel"], fv, "percomp")
    vf = _concept_vec(CONCEPT_FEATURES["ship"], fv, "percomp")
    assert abs(_dot(va, vf) - _ncos(va, vf)) < 1e-5, "PERCOMP dot must equal ncos (norms constant)"
    # divnorm changes DIRECTION: divnorm normalized cosine != percomp for a graded pair
    va_d = _concept_vec(CONCEPT_FEATURES["vessel"], fv, "divnorm")
    vf_d = _concept_vec(CONCEPT_FEATURES["ship"], fv, "divnorm")
    assert abs(_ncos(va_d, vf_d) - _ncos(va, vf)) > 1e-6, "divnorm should change the normalized cosine (direction)"
    print("[self-test] PASS: 3 arms distinct, mechanism fires under each, PERCOMP dot==ncos identity holds")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    _print(cell(n_boot=args.n_boot))
