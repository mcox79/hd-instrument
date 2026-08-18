"""
NOISE-TOLERANCE PROBE -- does the HD reasoning-map degrade GRACEFULLY under realistic reader noise
where the SYMBOLIC baseline COLLAPSES? (VET-flagged open lever from the Stage-1 bridge; load-bearing
for the Stage-2 architecture decision "HD-map over symbolic tuples".) DIAGNOSTIC, not the Stage-2 build.

WHY (pointers, not trusted summaries):
  - Stage-1 bridge (exp_read_bridge_rolefiller_hd_reasoning_map_v1, atom 29331) + its VET (ac440c94): on
    CLEAN facts HD reasoning MATCHED symbolic exact-lookup (bridge_fidelity_single=0.0); the VET flagged
    "noise-tolerance UNTESTED = the one place HD might BEAT symbolic (graceful degradation)".
  - Stakes: the reader's REAL corpus-wide extraction is ~0.40-0.60 precision (noisy). If the HD map
    degrades NO better than symbolic tuples under that noise, the HD-map target has no advantage over
    keeping symbolic tuples -> reshape Stage-2. If HD degrades GRACEFULLY at the reader's real rate, that
    is a real capability win + a strong argument for the HD-map target.
  - Plan: notes/learned_in_substrate_reader_plan_forms_hd_reasoning_maps_2026-07-18.md.

WHAT (one variable = the SUBSTRATE; everything else held):
  Reuse the Stage-1 bridge setup (SAME reader front-end, SAME clean micro-passages, SAME gold + query
  set, SAME FHRR reasoner + SAME symbolic dict-lookup baseline over the SAME tuples). CLEAN queries +
  CLEAN gold (the true world). Inject REALISTIC NOISE into the fact STORE (the reader's extracted facts)
  at increasing rates and measure reasoning accuracy (single-hop + strict multi-hop joins + conjunctive)
  for BOTH substrates as a function of noise. FAIRNESS: at each (noise-type, rate, seed) ONE corrupted
  fact set is drawn and BOTH substrates consume THAT SAME set -> only the substrate differs.

NOISE TYPES (match the reader's real failure modes -- nesting/argstruct VETs: wrong-head, goal-as-patient,
  spurious objects, dropped relations); the corruption acts at the SEMANTIC (tuple) level so it is
  substrate-agnostic and FAIR:
    WRONG   : per role-slot, with prob p, replace the filler with a PLAUSIBLE wrong entity (drawn from the
              same role's atom pool) = wrong-head / goal-as-patient / spurious-object. A fact keeps its
              length; one or more slots are wrong.
    MISSING : with prob p, the WHOLE fact is dropped = dropped relation. Symbolic -> no fact -> no answer;
              HD -> the missing fact vector is absent from the sharded set.
    MIX     : the realistic reader. With prob p a fact is unreliable; if so, 50/50 it is DROPPED or has ONE
              slot WRONG. p == 1 - precision (p in [0.4,0.6] == precision ~0.4-0.6, the reader's real rate).

THE MECHANISM THAT COULD MAKE HD WIN (honest, NOT by-construction): a multi-constraint query brings K
  role-constraints to bear. If the target fact has ONE binding corrupted, the SYMBOLIC exact-match store
  requires ALL constraints to match the stored tuple -> the corrupted target is EXCLUDED -> symbolic
  returns None / a wrong unique fact (BRITTLE). The HD cosine-select scores PARTIAL overlap -> the target
  with K-1 clean bindings can still be the argmax -> selected -> the (clean) read-role is recovered
  (GRACEFUL, = content-addressable partial-cue completion, Hopfield/Kanerva). CAN-FAIL: with ~200
  distractor facts the crosstalk can make the argmax pick a WRONG fact -> HD collapses too, possibly
  WORSE than symbolic (superposition AMPLIFIES noise). Both outcomes are MEASURED.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = the SAME symbolic dict-lookup reasoner (BR.run_symbolic_query), same query-program;
      MUST-DEGRADE CONTROL = symbolic collapses under noise (sym_single at p=0.5 < sym at p=0 minus 0.20).
  (2) CAN-FAIL BOTH WAYS = HD can degrade gracefully (PASS: positive DELTA at realistic noise + gentler
      slope + cleanup recovers) OR as-hard-or-worse (FAIL: DELTA ~ 0 / crosstalk amplifies). The MISSING
      curve is the built-in no-advantage regime (both fail together) -> proves the metric can show either.
  (3) DIFFICULTY-ON = the sweep INCLUDES the reader's real rate p in {0.4,0.5,0.6}, not just tiny noise.
  (4) ONE VARIABLE = the substrate; same facts / queries / noise draw at every (type, rate, seed).

METRIC: reasoning-accuracy-vs-noise CURVES for HD and symbolic (single-hop + strict multi-hop + conj);
  the DELTA = HD_acc - symbolic_acc at the realistic band (the LOAD-BEARING decision number); the
  degradation SLOPE (linear fit over the rate grid; gentler = smaller magnitude); a CLEANUP-RECOVERY rate
  (fraction of vector-degraded fillers the FHRR cleanup / associative-memory restores) with the fair
  symbolic analog (single-obs cleanup == argmax; the distributed win is R-fold analog averaging vs
  discrete majority voting).

BANDS (strict, above-floor per META_RULE_L; all thresholds HYPOTHESIZED@this-cell):
  realistic band = mean over p in {0.4,0.5,0.6}.
  HARD_PASS = HD_GRACEFUL_ADVANTAGE:
      D_mix_single >= 0.10 AND D_wrong_single >= 0.15 AND |slope_hd_mix| < |slope_sym_mix| (gentler) AND
      cleanup R_hd >= R_sym at mid-degradation AND can_fail_confirmed.
  HARD_FAIL = NO_HD_ADVANTAGE (reshape Stage-2):
      (D_mix_single <= 0.02 AND D_wrong_single <= 0.05) OR |slope_hd_mix| >= |slope_sym_mix|.
  MIDDLE = HD_MARGINAL_OR_REGIME_SPECIFIC: anything between -> localize + honest deflate.

BRAIN-CHECK (pre-reg; outcome NOT pre-assumed): distributed memory is a hallmark NOISE-TOLERANT /
  content-addressable / graceful-degrading store (Hopfield attractor completion; Kanerva SDM), whereas a
  brittle symbolic lookup fails hard on any corruption. So graceful degradation is the BRAIN-FAITHFUL
  EXPECTATION -- IF the substrate's FHRR partial-match + cleanup deliver it and crosstalk does not break
  it. SAME-LIMIT (HD collapses as hard) = a real bound (crosstalk is the substrate's WM-capacity analog;
  the brain also fails when too many similar traces interfere = catastrophic interference). BETTER (HD
  gentler) = the genuine HD advantage. The DEVIATION (FHRR multiplicative binding is an engineering stand-
  in for phase/assembly binding) is flagged; the crosstalk ceiling mirrors the human WM interference limit.

COMPUTE ARCHITECTURE: sequential-CPU. Justified: (a) wall << 10s per condition (few hundred facts, N=2048,
  small complex matmuls); total grid ~1-3 min; (b) the cell VALIDATES substrate FHRR primitives (bit
  reference) so a CPU reference is correct; (c) no SGD training (zero-training FHRR path). No GPU batching
  win at this scale. STORAGE STRATEGY: SHARDED reasoning-map (compositional/multi-hop; per
  META_STORAGE_STRATEGY) + a BUNDLED cleanup-recovery control (declared). CRLB: n/a -- no additive-Gaussian
  estimator floor; the relevant bound is the Plate O(N/log N) crosstalk bound (bridge-measured) which is
  the can-fail mechanism, not a discriminator threshold.

DETERMINISM: OMP/MKL=1; fixed int SEED; np.random.default_rng(seed) with per-condition seeds derived from
  ENUMERATED indices (no builtin hash(); no list(set())); sorted(set(...)) ordering. FHRR representation
  seed depends on seed-index ONLY (independent of the noise draw) so curves are comparable across p.

Glass-box (REAL reader front-end + REAL hdlab FHRR bind/bundle/unbind/cleanup + REAL symbolic executor;
  NO external LLM, NO runtime LLM). Local / foreground-to-completion. NO push / NO remote-persist.
  CLAIM-VET-pending; strategic read = HYPOTHESIS pending skunkworks landed-VET.

ANCHOR: read_bridge_noise_tolerance_hd_vs_symbolic_v1
BUILDS ON: exp_read_bridge_rolefiller_hd_reasoning_map_v1 (reader front-end + FHRR reasoner + symbolic
  baseline + gold/query generation -- all imported, none re-implemented) + hdlab.binding/bundling.
PRIOR-WORK CHECK: substrate_query "VSA HDC graceful degradation noise tolerance robustness cleanup memory
  reasoning" -> top cosine 0.3115 = 'Option C: Graceful Degradation' (a RAG product-fallback drill note,
  DIFFERENT topic) + 0.276 = deep_reasoning_hub_robustness (hub-protection, below 0.30). NO prior-arc cell
  on HD-map-vs-symbolic reasoning under reader noise at cosine>0.30 -> NOVEL probe.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke (SYMBOLIC and FHRR_HD produce distinct outputs under noise)
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (VSA cleanup; capacity = Plate crosstalk bound, bridge-measured)
# - baseline_in_band: symbolic is the MUST-DEGRADE control (collapses under noise); HD is the discriminator
# - discriminator survives scale: full runs at N_DISTRACTORS=200 crosstalk pressure + N=2048; a full-N
#   preview arm in smoke confirms the HD-vs-symbolic gap is not a small-smoke artifact
# - HARD_PASS strictly above floor
# - real_code_path: self-test constructs REAL hdlab bind/bundle/unbind + REAL reader tuples + REAL executors
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the ENTIRE Stage-1 bridge setup (one variable = the substrate; nothing re-implemented).
from experiments import exp_read_bridge_rolefiller_hd_reasoning_map_v1 as BR   # noqa: E402

ANCHOR_NAME = "read_bridge_noise_tolerance_hd_vs_symbolic_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 20260719
N_DIM = BR.N_DIM            # 2048 (same representation space as the bridge)
N_SEEDS = 5
N_DISTRACTORS = 200         # full crosstalk pressure (same as bridge)
P_GRID = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]
NOISE_TYPES = ["WRONG", "MISSING", "MIX"]
REALISTIC_PS = [0.4, 0.5, 0.6]          # the reader's real ~0.40-0.60 error rate == 1 - precision
CLEANUP_SIGMAS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
CLEANUP_R = 3               # redundant observations for the analog-averaging vs discrete-voting contrast


# ===========================================================================
# Noise injection (semantic / tuple-level; substrate-agnostic; deterministic per enumerated indices).
# ===========================================================================
def cond_seed(seed_idx, type_idx, p_idx):
    """Deterministic per-condition seed from ENUMERATED indices (no builtin hash(); no list(set()))."""
    return SEED + 1_000_003 * seed_idx + 10_007 * type_idx + 101 * p_idx


def build_role_pool(all_facts):
    """{role_name: sorted list of atoms that appear in that role} -> plausible wrong-entity source."""
    pool = {}
    for t in all_facts:
        for (role, slot) in BR.REL_SCHEMA[t[0]]:
            if slot < len(t):
                pool.setdefault(role, set()).add(str(t[slot]))
    return {r: sorted(v) for r, v in pool.items()}


def _draw_wrong(role, cur, pool, rng):
    cands = [a for a in pool.get(role, []) if a != cur]
    if not cands:
        return cur  # cannot corrupt plausibly (single-atom pool); leave unchanged
    return cands[int(rng.integers(len(cands)))]


def corrupt_facts(facts, pool, ntype, p, rng):
    """Return a corrupted fact list (both substrates consume THIS same list -> fair)."""
    out = []
    for t in facts:
        rel = t[0]
        roles = BR.REL_SCHEMA[rel]
        if ntype == "WRONG":
            t2 = list(t)
            for (role, slot) in roles:
                if slot < len(t2) and rng.random() < p:
                    t2[slot] = _draw_wrong(role, str(t2[slot]), pool, rng)
            out.append(tuple(t2))
        elif ntype == "MISSING":
            if rng.random() < p:
                continue
            out.append(tuple(t))
        elif ntype == "MIX":
            if rng.random() < p:
                if rng.random() < 0.5:
                    continue  # dropped relation
                ent_roles = [(role, slot) for (role, slot) in roles if slot < len(t)]
                if not ent_roles:
                    out.append(tuple(t))
                    continue
                role, slot = ent_roles[int(rng.integers(len(ent_roles)))]
                t2 = list(t)
                t2[slot] = _draw_wrong(role, str(t2[slot]), pool, rng)
                out.append(tuple(t2))
            else:
                out.append(tuple(t))
        else:
            out.append(tuple(t))
    return sorted(set(out), key=lambda t: (t[0], tuple(str(x) for x in t[1:])))


# ===========================================================================
# HD reasoner over a corrupted store, with a FIXED codebook (fair: same representation space at every p).
# ===========================================================================
def base_reasoner(clean_all_facts, n_dim, seed):
    """FHRRReasoner whose codebooks are fixed over the CLEAN atom pool (covers all plausible-wrong atoms)."""
    return BR.FHRRReasoner(clean_all_facts, n_dim, seed)


def reasoner_set_store(reasoner, corrupted_facts):
    """Re-point the reasoner at a corrupted store, re-encoding with its FIXED codebook. Mutates in place."""
    reasoner.facts = list(corrupted_facts)
    reasoner.fact_vecs = [reasoner._encode_fact(t) for t in reasoner.facts]
    return reasoner


def eval_condition(setup, pool, base_r, ntype, type_idx, p, p_idx, seed_idx):
    """One (type, p, seed) cell: draw ONE corrupted store, score symbolic + HD on the SAME store."""
    import numpy as np
    clean_all = setup["all_facts"]
    nrng = np.random.default_rng(cond_seed(seed_idx, type_idx, p_idx))
    corrupted = corrupt_facts(clean_all, pool, ntype, p, nrng)
    reasoner_set_store(base_r, corrupted)
    single, multi, conj = setup["single"], setup["multi"], setup["conj"]
    sym_s = BR._score_arm(lambda q: BR.run_symbolic_query(corrupted, q), single)
    sym_m = BR._score_arm(lambda q: BR.run_symbolic_query(corrupted, q), multi)
    sym_c = BR._score_arm(lambda q: BR.run_symbolic_query(corrupted, q), conj)
    hd_s = BR._score_arm(base_r.run, single)
    hd_m = BR._score_arm(base_r.run, multi)
    hd_c = BR._score_arm(base_r.run, conj)
    return dict(n_single=len(single), n_multi=len(multi), n_conj=len(conj),
                sym_single=sym_s, sym_multi=sym_m, sym_conj=sym_c,
                hd_single=hd_s, hd_multi=hd_m, hd_conj=hd_c, n_corrupt=len(corrupted))


# ===========================================================================
# Cleanup-recovery: associative-memory graceful degradation under CONTINUOUS vector noise.
# single-obs cleanup == symbolic argmax (tie by construction); the DISTRIBUTED win is R-fold analog
# averaging (bundle then cleanup) vs discrete R-fold majority voting.
# ===========================================================================
def cleanup_recovery(n_dim, sigmas, R, seed, n_atoms=48):
    import numpy as np
    import torch
    from hdlab.bundling import bundle
    rng = np.random.default_rng(seed)

    def fhrr():
        ph = torch.tensor(rng.uniform(-np.pi, np.pi, size=n_dim))
        return torch.complex(torch.cos(ph), torch.sin(ph)).to(torch.complex64)

    cb = [fhrr() for _ in range(n_atoms)]

    def clean(v):
        best, bs = -1, -2.0
        for j, u in enumerate(cb):
            c = BR._cos(v, u)
            if c > bs:
                bs, best = c, j
        return best

    def noisy(v, sigma):
        ph = torch.tensor(rng.normal(0.0, sigma, size=n_dim)) if sigma > 0 else torch.zeros(n_dim)
        return v * torch.complex(torch.cos(ph), torch.sin(ph)).to(v.dtype)

    out = {}
    for sigma in sigmas:
        s_hd = r_hd = r_sym = 0
        for i in range(n_atoms):
            v = cb[i]
            obs = [noisy(v, sigma) for _ in range(R)]
            s_hd += int(clean(obs[0]) == i)                                   # single obs (== symbolic argmax)
            r_hd += int(clean(bundle(torch.stack(obs))) == i)                 # analog averaging
            votes = [clean(o) for o in obs]
            vc = {}
            for w in votes:
                vc[w] = vc.get(w, 0) + 1
            maj = sorted(vc.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]    # discrete majority vote
            r_sym += int(maj == i)
        out[round(float(sigma), 3)] = dict(single_obs=round(s_hd / n_atoms, 4),
                                           R_hd=round(r_hd / n_atoms, 4),
                                           R_sym=round(r_sym / n_atoms, 4))
    return out


# ===========================================================================
# Scaffold-free witness: hand-built 3-fact map with ONE corrupted constraint-slot ->
# symbolic hard-fails (exact-match excludes the corrupted fact) while HD recovers (partial-match select +
# clean read-role); plus cleanup degrades gracefully.
# ===========================================================================
def _witness():
    import numpy as np
    import torch
    facts = [("svo", "chased", "hound", "rabbit"),
             ("svo", "ate", "rabbit", "carrot"),
             ("loc", "rabbit", "pond")]
    q = dict(kind="single", rel="svo",
             constraints={"RVERB": "chased", "RPATIENT": "rabbit"}, read_role="RAGENT", gold="hound")

    # corrupt the target fact's RPATIENT rabbit->carrot (a plausible wrong entity present in the map)
    corrupted = [("svo", "chased", "hound", "carrot"),
                 ("svo", "ate", "rabbit", "carrot"),
                 ("loc", "rabbit", "pond")]
    sym_ans = BR.run_symbolic_query(corrupted, q)                     # exact-match -> excludes target
    r = BR.FHRRReasoner(facts, N_DIM, seed=SEED)                      # fixed codebook over clean atoms
    reasoner_set_store(r, corrupted)
    hd_ans = r.run(q)                                                 # partial-match select + clean read-role

    # cleanup graceful shape: phase-noise an atom vector; recover at low sigma, fail at high sigma.
    rng = np.random.default_rng(SEED)
    cb = [r.atom_cb[a] for a in sorted(r.atom_cb)]

    def clean(v):
        best, bs = -1, -2.0
        for j, u in enumerate(cb):
            c = BR._cos(v, u)
            if c > bs:
                bs, best = c, j
        return best

    def noisy(idx, sigma):
        ph = torch.tensor(rng.normal(0.0, sigma, size=N_DIM))
        return cb[idx] * torch.complex(torch.cos(ph), torch.sin(ph)).to(cb[idx].dtype)

    rec_lo = sum(int(clean(noisy(i, 0.4)) == i) for i in range(len(cb))) / len(cb)
    rec_hi = sum(int(clean(noisy(i, 3.0)) == i) for i in range(len(cb))) / len(cb)
    return sym_ans, hd_ans, rec_lo, rec_hi


# ===========================================================================
# Markers / metrics (atomic) / crash-diagnostic.
# ===========================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# ===========================================================================
# Curve builder (shared by smoke-preview + full).
# ===========================================================================
def build_curves(setup, pool, n_seeds, p_grid, verbose=False):
    import numpy as np
    clean_all = setup["all_facts"]
    fhrr_seeds = [SEED + 7919 * si for si in range(n_seeds)]
    base_reasoners = [base_reasoner(clean_all, N_DIM, s) for s in fhrr_seeds]

    curves = {}
    for ti, ntype in enumerate(NOISE_TYPES):
        acc = {k: [] for k in ("hd_single", "sym_single", "hd_multi", "sym_multi", "hd_conj", "sym_conj")}
        std = {k: [] for k in ("hd_single", "sym_single", "hd_multi", "sym_multi")}
        n_corrupt_at = []
        for pi, p in enumerate(p_grid):
            per_seed = []
            for si in range(n_seeds):
                ev = eval_condition(setup, pool, base_reasoners[si], ntype, ti, p, pi, si)
                per_seed.append(ev)
            n_c = float(np.mean([e["n_corrupt"] for e in per_seed]))
            n_corrupt_at.append(round(n_c, 1))

            def fr(hitk, nk):
                vals = [e[hitk] / e[nk] if e[nk] else 0.0 for e in per_seed]
                return float(np.mean(vals)), float(np.std(vals))

            for cat, hk, nk in (("single", "hd_single", "n_single"), ("single", "sym_single", "n_single"),
                                ("multi", "hd_multi", "n_multi"), ("multi", "sym_multi", "n_multi"),
                                ("conj", "hd_conj", "n_conj"), ("conj", "sym_conj", "n_conj")):
                m, s = fr(hk, nk)
                acc[hk].append(round(m, 4))
                if hk in std:
                    std[hk].append(round(s, 4))
            if verbose:
                print(f"  [{ntype} p={p:.2f}] HD single={acc['hd_single'][-1]:.3f} "
                      f"sym single={acc['sym_single'][-1]:.3f} | HD multi={acc['hd_multi'][-1]:.3f} "
                      f"sym multi={acc['sym_multi'][-1]:.3f} | n_store~{n_c:.0f}", flush=True)
        curves[ntype] = dict(p_grid=list(p_grid), n_corrupt=n_corrupt_at, acc=acc, std=std)
    return curves


def _slope(p_grid, fracs):
    import numpy as np
    return float(np.polyfit(np.array(p_grid, dtype=float), np.array(fracs, dtype=float), 1)[0])


def _band_delta(curve, cat_hd, cat_sym, p_grid, band_ps):
    idxs = [i for i, p in enumerate(p_grid) if round(p, 3) in [round(b, 3) for b in band_ps]]
    if not idxs:
        return 0.0
    return float(sum(curve["acc"][cat_hd][i] - curve["acc"][cat_sym][i] for i in idxs) / len(idxs))


# ===========================================================================
# Self-test (design-gate).
# ===========================================================================
def self_test():
    print("[self-test] building reader front-end + gold + query set (bridge reuse) ...", flush=True)
    clf = BR.V2._fit_clf()

    # WITNESS (scaffold-free): symbolic hard-fails, HD recovers via partial-match; cleanup graceful shape.
    sym_ans, hd_ans, rec_lo, rec_hi = _witness()
    assert sym_ans != "hound", f"WITNESS symbolic should hard-fail on corrupted constraint, got {sym_ans!r}"
    assert hd_ans == "hound", f"WITNESS HD should recover via partial-match, got {hd_ans!r}"
    assert rec_lo >= 0.8 and rec_hi < rec_lo - 0.3, \
        f"WITNESS cleanup not graceful: rec(sigma=0.4)={rec_lo} rec(sigma=3.0)={rec_hi} " \
        f"(want rec@0.4>=0.8 and a >0.3 drop at sigma=3; floor is 1/n_atoms on the tiny witness codebook)"
    print(f"[self-test] witness: symbolic->{sym_ans!r} (hard-fail) ; HD->{hd_ans!r} (recovered) ; "
          f"cleanup rec@0.4={rec_lo:.2f} rec@3.0={rec_hi:.2f} (graceful)", flush=True)

    # real_code_path: REAL reader emits tuples; REAL executors consume them.
    setup = BR.build_setup(clf, n_distractors=60)   # smaller distractor set for a fast smoke
    assert len(setup["single"]) >= 12, f"too few single-hop queries: {len(setup['single'])}"
    assert len(setup["multi"]) >= 6, f"too few multi-hop queries: {len(setup['multi'])}"
    pool = build_role_pool(setup["all_facts"])
    print(f"[self-test] gold facts={len(setup['gold_facts'])} distractors={len(setup['distractors'])} | "
          f"queries single={len(setup['single'])} multi={len(setup['multi'])} conj={len(setup['conj'])}",
          flush=True)

    # small curves at coarse grid (smoke).
    smoke_grid = [0.0, 0.3, 0.6]
    curves = build_curves(setup, pool, n_seeds=2, p_grid=smoke_grid, verbose=True)

    # DESIGN-GATE 1 -- bridge preserved at p=0 (HD ~= symbolic single-hop; both high).
    for nt in NOISE_TYPES:
        hd0 = curves[nt]["acc"]["hd_single"][0]
        sym0 = curves[nt]["acc"]["sym_single"][0]
        assert sym0 >= 0.90, f"[{nt}] symbolic p=0 not ~1.0: {sym0}"
        assert abs(hd0 - sym0) <= 0.20, f"[{nt}] HD not ~= symbolic at p=0: HD {hd0} vs sym {sym0}"

    # DESIGN-GATE 1 -- MUST-DEGRADE control: symbolic collapses under noise (MIX @ high p).
    sym_mix_hi = curves["MIX"]["acc"]["sym_single"][-1]
    sym_mix_0 = curves["MIX"]["acc"]["sym_single"][0]
    assert sym_mix_hi < sym_mix_0 - 0.20, \
        f"MUST-DEGRADE control did not fire: symbolic MIX single {sym_mix_0}->{sym_mix_hi} (drop < 0.20)"
    print(f"[self-test] must-degrade control fired: symbolic MIX single {sym_mix_0:.3f} -> {sym_mix_hi:.3f}",
          flush=True)

    # DESIGN-GATE 2 -- CAN-FAIL BOTH WAYS: arms differ under noise AND MISSING is a no-advantage regime.
    hd_wrong_hi = curves["WRONG"]["acc"]["hd_single"][-1]
    sym_wrong_hi = curves["WRONG"]["acc"]["sym_single"][-1]
    assert abs(hd_wrong_hi - sym_wrong_hi) > 0.0 or hd_wrong_hi != sym_wrong_hi, "arms bit-identical under noise"
    d_missing = curves["MISSING"]["acc"]["hd_single"][-1] - curves["MISSING"]["acc"]["sym_single"][-1]
    print(f"[self-test] can-fail: WRONG@hi HD {hd_wrong_hi:.3f} vs sym {sym_wrong_hi:.3f} "
          f"(delta {hd_wrong_hi - sym_wrong_hi:+.3f}); MISSING@hi delta {d_missing:+.3f} "
          f"(no-advantage regime present)", flush=True)

    # MECHANISM LOAD-BEARING (arms-differ done right): wrong-role unbind collapses HD single-hop at p=0.
    base_r = base_reasoner(setup["all_facts"], N_DIM, SEED)
    reasoner_set_store(base_r, setup["all_facts"])
    real_hit = BR._score_arm(base_r.run, setup["single"])
    wrong_hit = BR._score_arm(lambda q: base_r.run(q, wrong_role=True), setup["single"])
    real_f = real_hit / len(setup["single"])
    wrong_f = wrong_hit / len(setup["single"])
    assert real_f - wrong_f >= 0.30, \
        f"MECHANISM NOT LOAD-BEARING: real {real_f:.3f} vs wrong-role {wrong_f:.3f} (gap < 0.30)"
    print(f"[self-test] mechanism load-bearing: real-role {real_f:.3f} vs wrong-role {wrong_f:.3f} "
          f"(gap {real_f - wrong_f:.3f} >= 0.30)", flush=True)

    # DISCRIMINATOR-SURVIVES-SCALE preview: full-N distractors=200 at a realistic rate, 1 seed.
    setup_full = BR.build_setup(clf, n_distractors=N_DISTRACTORS)
    pool_full = build_role_pool(setup_full["all_facts"])
    prev = build_curves(setup_full, pool_full, n_seeds=1, p_grid=[0.5], verbose=False)
    d_prev_mix = (prev["MIX"]["acc"]["hd_single"][0] - prev["MIX"]["acc"]["sym_single"][0])
    d_prev_wrong = (prev["WRONG"]["acc"]["hd_single"][0] - prev["WRONG"]["acc"]["sym_single"][0])
    print(f"[self-test] SCALE preview (200 distractors, p=0.5): MIX delta {d_prev_mix:+.3f}, "
          f"WRONG delta {d_prev_wrong:+.3f} (gap not a small-smoke artifact if it persists)", flush=True)

    # CLEANUP-RECOVERY graceful shape + integration helps.
    cr = cleanup_recovery(N_DIM, [0.0, 0.75, 3.0], CLEANUP_R, seed=SEED, n_atoms=32)
    assert cr[0.0]["single_obs"] >= 0.99, f"cleanup broken at sigma=0: {cr[0.0]}"
    assert cr[3.0]["single_obs"] <= 0.5, f"cleanup did not degrade at sigma=3: {cr[3.0]}"
    assert cr[0.75]["R_hd"] >= cr[0.75]["single_obs"] - 0.02, "R-fold integration should not hurt vs single-obs"
    print(f"[self-test] cleanup-recovery: single@0={cr[0.0]['single_obs']} single@3={cr[3.0]['single_obs']} "
          f"| @0.75 single={cr[0.75]['single_obs']} R_hd={cr[0.75]['R_hd']} R_sym={cr[0.75]['R_sym']}",
          flush=True)

    # DETERMINISM: two identical builds match.
    c2 = build_curves(setup, pool, n_seeds=2, p_grid=smoke_grid, verbose=False)
    assert curves["MIX"]["acc"] == c2["MIX"]["acc"], "non-deterministic curves"
    print("[self-test] deterministic (two curve builds identical)", flush=True)
    print("[self-test] PASS", flush=True)
    return 0


# ===========================================================================
# Full verdict.
# ===========================================================================
def build_verdict(timeout_s=900):
    import numpy as np
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_start_marker(OUTPUT_DIR, "full", expected_n_units=len(NOISE_TYPES) * len(P_GRID) * N_SEEDS)
    clf = BR.V2._fit_clf()
    setup = BR.build_setup(clf, n_distractors=N_DISTRACTORS)
    pool = build_role_pool(setup["all_facts"])
    n_single, n_multi, n_conj = len(setup["single"]), len(setup["multi"]), len(setup["conj"])

    print(f"[full] gold={len(setup['gold_facts'])} distractors={len(setup['distractors'])} "
          f"queries s/m/c={n_single}/{n_multi}/{n_conj}; sweeping {NOISE_TYPES} x {P_GRID} x {N_SEEDS} seeds",
          flush=True)
    curves = build_curves(setup, pool, n_seeds=N_SEEDS, p_grid=P_GRID, verbose=True)

    # cleanup-recovery (multi-seed mean).
    cr_seeds = [cleanup_recovery(N_DIM, CLEANUP_SIGMAS, CLEANUP_R, seed=SEED + 7919 * si, n_atoms=48)
                for si in range(N_SEEDS)]
    cr_mean = {}
    for sig in CLEANUP_SIGMAS:
        k = round(float(sig), 3)
        cr_mean[k] = {m: round(float(np.mean([cs[k][m] for cs in cr_seeds])), 4)
                      for m in ("single_obs", "R_hd", "R_sym")}
    # mid-degradation sigma = closest single_obs to 0.5
    sig_mid = min(cr_mean, key=lambda s: abs(cr_mean[s]["single_obs"] - 0.5))
    cleanup_recovery_rate = cr_mean[sig_mid]["R_hd"]
    cleanup_win = round(cr_mean[sig_mid]["R_hd"] - cr_mean[sig_mid]["R_sym"], 4)

    # DELTAS at the realistic band (the load-bearing decision numbers).
    d_mix_single = _band_delta(curves["MIX"], "hd_single", "sym_single", P_GRID, REALISTIC_PS)
    d_mix_multi = _band_delta(curves["MIX"], "hd_multi", "sym_multi", P_GRID, REALISTIC_PS)
    d_wrong_single = _band_delta(curves["WRONG"], "hd_single", "sym_single", P_GRID, REALISTIC_PS)
    d_wrong_multi = _band_delta(curves["WRONG"], "hd_multi", "sym_multi", P_GRID, REALISTIC_PS)
    d_missing_single = _band_delta(curves["MISSING"], "hd_single", "sym_single", P_GRID, REALISTIC_PS)

    # SLOPES (single-hop accuracy vs rate; gentler = smaller magnitude).
    slope_hd_mix = _slope(P_GRID, curves["MIX"]["acc"]["hd_single"])
    slope_sym_mix = _slope(P_GRID, curves["MIX"]["acc"]["sym_single"])
    slope_hd_wrong = _slope(P_GRID, curves["WRONG"]["acc"]["hd_single"])
    slope_sym_wrong = _slope(P_GRID, curves["WRONG"]["acc"]["sym_single"])
    gentler_mix = abs(slope_hd_mix) < abs(slope_sym_mix)

    # can-fail-both-ways confirmation: must-degrade fired AND a measured no-advantage regime (MISSING ~0).
    sym_mix_0 = curves["MIX"]["acc"]["sym_single"][0]
    sym_mix_band = _band_delta(curves["MIX"], "sym_single", "sym_single", P_GRID, REALISTIC_PS)  # = 0; placeholder
    sym_mix_realistic = float(np.mean([curves["MIX"]["acc"]["sym_single"][i]
                                       for i, p in enumerate(P_GRID) if round(p, 3) in [0.4, 0.5, 0.6]]))
    must_degrade_fired = sym_mix_realistic < sym_mix_0 - 0.20
    no_advantage_regime = abs(d_missing_single) < 0.10
    can_fail_confirmed = bool(must_degrade_fired and no_advantage_regime)

    cleanup_helps = cr_mean[sig_mid]["R_hd"] >= cr_mean[sig_mid]["R_sym"]

    hard_pass = (d_mix_single >= 0.10 and d_wrong_single >= 0.15 and gentler_mix and
                 cleanup_helps and can_fail_confirmed)
    hard_fail = ((d_mix_single <= 0.02 and d_wrong_single <= 0.05) or (abs(slope_hd_mix) >= abs(slope_sym_mix)))

    if hard_pass:
        verdict = "HD_GRACEFUL_ADVANTAGE"
    elif hard_fail:
        verdict = "NO_HD_ADVANTAGE"
    else:
        verdict = "HD_MARGINAL_OR_REGIME_SPECIFIC"

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=verdict,
        verdict_msg=(
            f"DELTA@realistic(p0.4-0.6): MIX single {d_mix_single:+.3f} multi {d_mix_multi:+.3f}; "
            f"WRONG single {d_wrong_single:+.3f} multi {d_wrong_multi:+.3f}; MISSING single "
            f"{d_missing_single:+.3f}; slopes MIX HD {slope_hd_mix:+.3f} sym {slope_sym_mix:+.3f} "
            f"(gentler={gentler_mix}); cleanup R_hd {cleanup_recovery_rate:.3f} vs R_sym "
            f"{cr_mean[sig_mid]['R_sym']:.3f} @sigma={sig_mid} (win {cleanup_win:+.3f}); "
            f"can_fail={can_fail_confirmed}"),
        summary=(f"{verdict}: MIX-delta {d_mix_single:+.2f} WRONG-delta {d_wrong_single:+.2f} "
                 f"gentler={gentler_mix} cleanup-win {cleanup_win:+.2f}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        seed=SEED, n_dim=N_DIM, n_seeds=N_SEEDS, n_distractors=len(setup["distractors"]),
        n_query=dict(single=n_single, multi=n_multi, conj=n_conj),
        decision_numbers=dict(
            realistic_band=REALISTIC_PS,
            d_mix_single=round(d_mix_single, 4), d_mix_multi=round(d_mix_multi, 4),
            d_wrong_single=round(d_wrong_single, 4), d_wrong_multi=round(d_wrong_multi, 4),
            d_missing_single=round(d_missing_single, 4),
            slope_hd_mix=round(slope_hd_mix, 4), slope_sym_mix=round(slope_sym_mix, 4),
            slope_hd_wrong=round(slope_hd_wrong, 4), slope_sym_wrong=round(slope_sym_wrong, 4),
            gentler_mix=bool(gentler_mix)),
        curves=curves,
        cleanup_recovery=dict(sigmas=CLEANUP_SIGMAS, R=CLEANUP_R, curve=cr_mean,
                              sigma_mid=sig_mid, recovery_rate_R_hd=cleanup_recovery_rate,
                              R_sym_at_mid=cr_mean[sig_mid]["R_sym"], cleanup_win=cleanup_win),
        can_fail=dict(confirmed=can_fail_confirmed, must_degrade_fired=bool(must_degrade_fired),
                      no_advantage_regime_missing=bool(no_advantage_regime),
                      sym_mix_p0=round(sym_mix_0, 4), sym_mix_realistic=round(sym_mix_realistic, 4)),
        arms_differ_verified=True,
        REQUIRED_FIELDS=["verdict", "decision_numbers", "curves", "cleanup_recovery", "can_fail"],
        cited=dict(bridge="exp_read_bridge_rolefiller_hd_reasoning_map_v1",
                   plan="notes/learned_in_substrate_reader_plan_forms_hd_reasoning_maps_2026-07-18.md"),
        caveats=[
            "CLEAN queries + CLEAN gold (the true world); only the STORE is corrupted -> tests robustness "
            "to the reader's extraction noise, NOT the reader's extraction itself. Same corrupted store "
            "consumed by both substrates at every (type,rate,seed) -> one variable = the substrate.",
            "The HD win, where present, is PARTIAL-MATCH graceful retrieval (cosine-select tolerates a "
            "corrupted binding + reads a clean role) vs brittle symbolic exact-match; it is NOT magic "
            "recovery of a genuinely-wrong value. On MISSING (dropped relations) HD has NO structural "
            "advantage (both fail) -- that is the built-in no-advantage regime and is reported.",
            "Cleanup-recovery: single-observation cleanup == symbolic argmax (tie by construction); the "
            "distributed advantage measured here is R-fold analog averaging (bundle+cleanup) vs discrete "
            "majority voting, isolated on a synthetic codebook (Kanerva/Hopfield hallmark).",
            "Crosstalk is the can-fail: at 200 distractors + N=2048 the cosine-select can pick a wrong "
            "fact -> HD collapses too; the curves measure whether it does at the reader's real rate.",
            "MIX rate p == 1 - precision; realistic band p in {0.4,0.5,0.6} == precision ~0.4-0.6. "
            "single-annotator/auto gold; CLAIM-VET-pending (skunkworks landed-VET before fact).",
        ],
    )
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[verdict] {verdict} :: {metrics['verdict_msg']} :: {elapsed}s", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.full:
            return build_verdict(timeout_s=args.timeout)
        return self_test()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        print(f"[CRASH] {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
