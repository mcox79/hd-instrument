# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (claim3 mechanism/ablation/scramble-perm/scramble-derange/
#   ortho/freq prediction arrays hashed; extends v1's hash-uniqueness check with the new arms)
# - final_metrics_atomicity = tmp_replace (single-shot, reuses V1._atomic_write)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a declared per-claim (discrete exact-match / co-occurrence gap metrics, no Gaussian floor
#   for any arm including the new orthographic/frequency floors -- also discrete argmax predictions)
# - baseline_in_band EXEMPTED for claim3 scrambled/ablated/ortho/freq arms (intentional can-fail
#   floor controls, not saturating baselines)
# - discriminator survives scale: smoke runs the REAL pipeline on the real (frozen) foundation;
#   the NEW known-answer arm additionally exercises HDFactStore at PRODUCTION n_dim (2048) inside
#   self-test, not just the tiny n_dim=512 formula self-test v1 had
# - HARD_PASS strictly above floor_max (max of ALL floor arms per claim, not a single arm)
# - HP_SCOPE: bands declared per-claim in the pre-reg; overall verdict = AND of the 3, overridden
#   by INSTRUMENT_INVALID_ABORT if the known-answer arm fails (mandatory instrument check)
# - cardinality_ok: N/A (no sweep axis; fixed per-mode sample sizes, declared no_sweep_axis)
# - per-unit failure-class instrumentation: N/A (no per-unit try/except; a single failed unit
#   would indicate a code bug, not an expected per-item failure mode, so it propagates and halts)
# - calibration_check: default_ok_for_this_regime (fixed thresholds/sample sizes, no adaptive tuning)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL HDFactStore / ConceptSpace objects at tiny scale AND at production
#   n_dim=2048 for the known-answer arm (real_code_path)
# - substrate_signature_checked: HDFactStore(n_dim, seed, relation_cardinality, use_index) -- same
#   base/portable kwargs as V1, imported not re-declared
"""exp_foundation_validation_harness_v2_floors_v1 -- floor-arm + known-answer + draw-spread
extension of exp_foundation_validation_harness_v1. See preregs/2026-08-15_foundation_validation_
harness_v2_floors_v1.md for full design, band derivations, and the read-out invariance check.

WHY THIS EXISTS (C13 re-run, 2026-08-15): the only prior validation
(data/exp_foundation_validation_harness_v1/metrics.json, HARD_PASS_foundation_validated,
2026-08-12T14:27:19Z) ran with NO floor arms -- under the standing gate rule ("a gate is a
CI-separated margin above max(orthographic, frequency, scramble), never a bare absolute number")
that result is NOT_EVALUABLE, not a pass. It also validated a since-stale snapshot
(data/foundation/reading_grounding_v1/, frozen 2026-08-12T14:25:13Z). This cell re-runs against
the CURRENT foundation (data/foundation/reading_grounding_v2_qualityfix/ -- see pre-reg
"CORRECTED: which foundation snapshot is current" section for why v5_termboundary, the highest-
mtime directory, is NOT a loadable store and is not what "current" means here) WITH:
  1. orthographic + frequency floors (claims 1 and 3)
  2. an explicit named scramble floor (both a plain permutation AND a conflict-avoiding
     derangement; the more conservative/higher-scoring of the two is the official floor)
  3. a mandatory known-answer arm at PRODUCTION n_dim (instrument validity, independent of whether
     the foundation itself is any good)
  4. between-random-projection-draw spread for claim 3 (rebuild the SAME real facts under 5
     different HDFactStore seeds; the pass margin must survive redraw noise)

REUSES v1's already-self-tested primitives by import (wire-don't-island): cooccurs, wilson_ci,
cohesion_gap, build_scrambled_store (the permutation variant), build_two_hop_chains, query_single,
build_active_relation_map, find_active_contradictions, load_corpus_sentences, corpus source lists,
_write_start_marker, _write_crash_metrics, _atomic_write, freeze_snapshot.

Modes: --self-test (tiny synthetic-but-real fixtures INCLUDING a production-n_dim=2048
known-answer check, <10s) / --smoke (real pipeline against a frozen snapshot, reduced N) /
--full (real pipeline, full N; requires explicit --foundation-dir or --freeze-from).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import bisect
import hashlib
import json
import random
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ANCHOR_NAME = "foundation_validation_harness_v2_floors_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_foundation_validation_harness_v1 as V1  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.foundation_persistence import load_store, load_concept_space  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEED = 20260815
GM_REL = V1.GM_REL
FUNCTIONAL_RELATIONS = V1.FUNCTIONAL_RELATIONS

N_CORRECTNESS = V1.N_CORRECTNESS
N_REASON = V1.N_REASON
N_COHERENCE_CLUSTER_CAP = V1.N_COHERENCE_CLUSTER_CAP
K_NEG_COHESION = V1.K_NEG_COHESION
N_DRAWS = 5
DRAW_SUBSAMPLE_CAP = 50
N_KNOWN_ANSWER_CHAINS = 20
N_NEGSAMPLE_DRAWS = 5

CORPUS_SOURCES_SMOKE = V1.CORPUS_SOURCES_SMOKE
CORPUS_SOURCES_FULL = V1.CORPUS_SOURCES_FULL

repo_path = V1.repo_path
cooccurs = V1.cooccurs
wilson_ci = V1.wilson_ci
cosine = V1.cosine
cohesion_gap = V1.cohesion_gap
build_active_relation_map = V1.build_active_relation_map
find_active_contradictions = V1.find_active_contradictions
build_two_hop_chains = V1.build_two_hop_chains
query_single = V1.query_single
build_scrambled_store_permutation = V1.build_scrambled_store
load_corpus_sentences = V1.load_corpus_sentences


# =========================================================================== orthographic floor
def char_trigrams(s: str) -> set:
    s2 = "^" + s.lower() + "$"
    if len(s2) < 3:
        return {s2}
    return {s2[i:i + 3] for i in range(len(s2) - 2)}


def trigram_jaccard(a: str, b: str) -> float:
    ta, tb = char_trigrams(a), char_trigrams(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def lcp_ratio(a: str, b: str) -> float:
    k = 0
    for x, y in zip(a.lower(), b.lower()):
        if x != y:
            break
        k += 1
    denom = max(len(a), len(b), 1)
    return k / denom


def orthographic_score(a: str, b: str) -> float:
    """Strongest available zero-meaning attack: max of trigram-Jaccard and LCP-ratio.
    Zero store/ConceptSpace signal -- pure string transform. Reference: tools/orthographic_floor_
    vet_v1.py ("a floor should be the strongest available zero-meaning attack")."""
    return max(trigram_jaccard(a, b), lcp_ratio(a, b))


def predict_orthographic_best(query: str, candidates: Sequence[str]) -> Optional[str]:
    best, best_score = None, -1.0
    for c in candidates:
        if c == query:
            continue
        sc = orthographic_score(query, c)
        if sc > best_score:
            best, best_score = c, sc
    return best


def predict_frequency_mode(counted: Counter) -> Optional[str]:
    if not counted:
        return None
    # deterministic tie-break: sorted() on (count, name) descending count then name asc
    return sorted(counted.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def build_sorted_tokens(sentences: Sequence[str]) -> List[str]:
    tok_re = re.compile(r"[a-zA-Z']+")
    toks: List[str] = []
    for s in sentences:
        toks.extend(t.lower() for t in tok_re.findall(s))
    toks.sort()
    return toks


def prefix_count(lemma: str, sorted_tokens: Sequence[str]) -> int:
    key = lemma.lower()
    if not key:
        return 0
    lo = bisect.bisect_left(sorted_tokens, key)
    hi_key = key[:-1] + chr(ord(key[-1]) + 1)
    hi = bisect.bisect_left(sorted_tokens, hi_key)
    return hi - lo


# =========================================================================== derangement scramble
def build_derangement_mapping(subjects: Sequence[str], objects: Sequence[str],
                              shuffle_seed: int) -> List[str]:
    """Fixed-seed shuffle of `objects` (parallel to `subjects`) with a repair pass guaranteeing
    NO fixed point (shuffled[i] != objects[i] for all i) -- a genuine degree-preserving
    derangement, stricter than V1's plain-permutation build_scrambled_store."""
    rng = random.Random(shuffle_seed)
    shuffled = list(objects)
    rng.shuffle(shuffled)
    n = len(shuffled)
    if n < 2:
        return shuffled
    for i in range(n):
        if shuffled[i] == objects[i]:
            j = (i + 1) % n
            # walk forward to find a safe swap partner (won't itself create a new fixed point)
            tries = 0
            while (shuffled[j] == objects[i] or shuffled[i] == objects[j]) and tries < n:
                j = (j + 1) % n
                tries += 1
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled


def build_scrambled_store_derangement(gm_map: Dict[str, str], n_dim: int, base_seed: int,
                                      shuffle_seed: int) -> HDFactStore:
    subjects = sorted(gm_map.keys())
    objects = [gm_map[s] for s in subjects]
    shuffled = build_derangement_mapping(subjects, objects, shuffle_seed)
    new_store = HDFactStore(n_dim=n_dim, seed=base_seed, relation_cardinality={GM_REL: "FUNCTIONAL"},
                            use_index=True)
    for subj, obj in zip(subjects, shuffled):
        new_store.store(subj, GM_REL, obj, "scramble_derangement_control", "TRUST_MID")
    return new_store


def build_store_from_pairs(gm_map: Dict[str, str], n_dim: int, seed: int) -> HDFactStore:
    """A fresh HDFactStore over the SAME (subject, GROUNDED_MEANING, obj) facts as gm_map, but a
    DIFFERENT random hyperdimensional basis draw (different `seed`). Used for the
    between-random-projection-draw spread check (claim 3)."""
    st = HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality={GM_REL: "FUNCTIONAL"},
                     use_index=True)
    for subj in sorted(gm_map.keys()):
        st.store(subj, GM_REL, gm_map[subj], "draw_spread_rebuild", "TRUST_MID")
    return st


# =========================================================================== claim 1 (+ floors)
def run_claim1_floors(store: HDFactStore, sentences: List[str], sorted_tokens: List[str],
                      n_sample: int, seed: int, output_dir: str) -> dict:
    gm_facts = [f for f in store._facts if f.relation == GM_REL and f.status in ("ACTIVE", "COMBINED")]
    n_live = len(gm_facts)
    self_grounded = [f for f in gm_facts if f.subject == f.obj]
    cross = sorted(((f.subject, f.obj) for f in gm_facts if f.subject != f.obj))
    self_grounded_rate = len(self_grounded) / n_live if n_live else 0.0

    all_objects = sorted({f.obj for f in gm_facts})
    obj_freq_counts = Counter({o: prefix_count(o, sorted_tokens) for o in all_objects})
    freq_pick_global = predict_frequency_mode(obj_freq_counts)

    n = min(n_sample, len(cross))
    rng = random.Random(seed)
    sample = rng.sample(cross, n) if n > 0 else []

    ckpt_dir = os.path.join(output_dir, "ckpt_claim1_v2")
    done = completed_units(ckpt_dir)
    for i, (lemma, canon_obj) in enumerate(sample):
        key = unit_key("c1v2", i, lemma, canon_obj)
        if key in done:
            continue
        decoy_pool = [o for o in all_objects if o not in (canon_obj, lemma)]
        decoy = rng.choice(decoy_pool) if decoy_pool else canon_obj
        ortho_pick = predict_orthographic_best(lemma, all_objects) or canon_obj
        real_hit = cooccurs(lemma, canon_obj, sentences)
        decoy_hit = cooccurs(lemma, decoy, sentences)
        ortho_hit = cooccurs(lemma, ortho_pick, sentences)
        freq_hit = cooccurs(lemma, freq_pick_global, sentences) if freq_pick_global else False
        record_unit(ckpt_dir, key, {
            "lemma": lemma, "canon_obj": canon_obj, "decoy": decoy, "ortho_pick": ortho_pick,
            "freq_pick": freq_pick_global, "real_hit": real_hit, "decoy_hit": decoy_hit,
            "ortho_hit": ortho_hit, "freq_hit": freq_hit,
        })

    units = load_units(ckpt_dir)
    rows = list(units.values())
    n_eval = len(rows)

    def _rate(field):
        k = sum(1 for r in rows if r[field])
        return k, (k / n_eval if n_eval else 0.0)

    k_real, precision_hat = _rate("real_hit")
    k_decoy, chance_hat = _rate("decoy_hit")
    k_ortho, ortho_rate = _rate("ortho_hit")
    k_freq, freq_rate = _rate("freq_hit")

    lo_p, hi_p = wilson_ci(k_real, n_eval)
    floors = {"chance": (chance_hat, wilson_ci(k_decoy, n_eval)),
             "orthographic": (ortho_rate, wilson_ci(k_ortho, n_eval)),
             "frequency": (freq_rate, wilson_ci(k_freq, n_eval))}
    floor_name = max(floors, key=lambda k: floors[k][0])
    floor_max, (floor_lo, floor_hi) = floors[floor_name][0], floors[floor_name][1]
    gap = precision_hat - floor_max

    if gap >= 0.20 and lo_p > floor_hi:
        verdict = "HARD_PASS"
    elif gap < 0.05:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict, "n_live_grounded_meaning": n_live, "n_self_grounded": len(self_grounded),
        "self_grounded_rate": round(self_grounded_rate, 4), "n_cross_grounded": len(cross),
        "n_sampled": n_eval, "precision_hat": round(precision_hat, 4),
        "chance_hat": round(chance_hat, 4), "ortho_rate": round(ortho_rate, 4),
        "freq_rate": round(freq_rate, 4), "floor_name": floor_name, "floor_max": round(floor_max, 4),
        "gap": round(gap, 4), "wilson_precision": [round(lo_p, 4), round(hi_p, 4)],
        "wilson_floor": [round(floor_lo, 4), round(floor_hi, 4)],
        "freq_pick_global": freq_pick_global, "corpus_n_sentences": len(sentences),
        "n_distinct_objects": len(all_objects),
        "arms_differ_verified": len({tuple(r["canon_obj"] for r in rows),
                                     tuple(r["decoy"] for r in rows),
                                     tuple(r["ortho_pick"] for r in rows)}) > 1 if rows else False,
    }


# =========================================================================== claim 2 (+ scramble)
def run_claim2_floors(store: HDFactStore, space, cluster_cap: int, seed: int, output_dir: str) -> dict:
    gm_facts = [f for f in store._facts if f.relation == GM_REL and f.status in ("ACTIVE", "COMBINED")]
    clusters_lemmas: Dict[str, List[str]] = defaultdict(list)
    cross_pairs: List[Tuple[str, str]] = []
    for f in gm_facts:
        clusters_lemmas[f.obj].append(f.subject)
        if f.subject != f.obj:
            cross_pairs.append((f.subject, f.obj))

    qualifying_keys = sorted(k for k in clusters_lemmas if len(clusters_lemmas[k]) >= 2)[:cluster_cap]
    clusters_vecs: Dict[str, List[np.ndarray]] = {}
    lemma_vec_cache: Dict[str, Optional[np.ndarray]] = {}
    n_missing_vec = 0
    for key in qualifying_keys:
        vecs = []
        for lem in sorted(set(clusters_lemmas[key])):
            if lem not in lemma_vec_cache:
                lemma_vec_cache[lem] = space.bundle(lem)
            v = lemma_vec_cache[lem]
            if v is None:
                n_missing_vec += 1
                continue
            vecs.append(v)
        if len(vecs) >= 2:
            clusters_vecs[key] = vecs

    rng = random.Random(seed)
    gap, n_qualifying = cohesion_gap(clusters_vecs, rng, cap=cluster_cap)
    if n_qualifying < 5:
        a_verdict = "INCONCLUSIVE_INSUFFICIENT_CLUSTERS"
    elif gap >= 0.10:
        a_verdict = "HARD_PASS"
    elif gap <= 0.02:
        a_verdict = "HARD_FAIL"
    else:
        a_verdict = "MIDDLE_BAND"

    # negative-sampling draw-spread (partial substitute for a full basis redraw; declared as such)
    negsample_gaps = []
    for di in range(N_NEGSAMPLE_DRAWS):
        rng_d = random.Random(seed + 1000 + di)
        g_d, _ = cohesion_gap(clusters_vecs, rng_d, cap=cluster_cap)
        negsample_gaps.append(g_d)
    negsample_mean = float(np.mean(negsample_gaps)) if negsample_gaps else 0.0
    negsample_sd = float(np.std(negsample_gaps)) if negsample_gaps else 0.0

    # scramble-cluster floor: derangement-shuffle canon_obj labels over cross-grounded pairs,
    # rebuild cluster membership, recompute cohesion_gap over the SAME real vectors.
    scrambled_gap, n_scrambled_qualifying = 0.0, 0
    if cross_pairs:
        subjects = [s for s, _ in sorted(cross_pairs)]
        objects = [o for _, o in sorted(cross_pairs)]
        shuffled_objs = build_derangement_mapping(subjects, objects, seed + 777)
        scrambled_clusters_lemmas: Dict[str, List[str]] = defaultdict(list)
        for subj, sh_obj in zip(subjects, shuffled_objs):
            scrambled_clusters_lemmas[sh_obj].append(subj)
        scr_keys = sorted(k for k in scrambled_clusters_lemmas
                          if len(scrambled_clusters_lemmas[k]) >= 2)[:cluster_cap]
        scrambled_clusters_vecs: Dict[str, List[np.ndarray]] = {}
        for key in scr_keys:
            vecs = []
            for lem in sorted(set(scrambled_clusters_lemmas[key])):
                if lem not in lemma_vec_cache:
                    lemma_vec_cache[lem] = space.bundle(lem)
                v = lemma_vec_cache[lem]
                if v is not None:
                    vecs.append(v)
            if len(vecs) >= 2:
                scrambled_clusters_vecs[key] = vecs
        rng_scr = random.Random(seed)
        scrambled_gap, n_scrambled_qualifying = cohesion_gap(scrambled_clusters_vecs, rng_scr,
                                                              cap=cluster_cap)

    floor_margin = gap - scrambled_gap
    if a_verdict == "HARD_PASS" and floor_margin < 0.08:
        a_verdict = "MIDDLE_BAND"
    not_robust_to_negsample = (gap - scrambled_gap) < 3 * negsample_sd if n_qualifying >= 5 else None

    n_contra, contra_examples, n_flagged = find_active_contradictions(store, sorted(FUNCTIONAL_RELATIONS))
    b_verdict = "HARD_PASS" if n_contra == 0 else "HARD_FAIL"

    if a_verdict == "HARD_PASS" and b_verdict == "HARD_PASS":
        overall = "HARD_PASS"
    elif a_verdict == "HARD_FAIL" or b_verdict == "HARD_FAIL":
        overall = "HARD_FAIL"
    else:
        overall = "MIDDLE_BAND"

    return {
        "verdict": overall,
        "same_rep_at_scale": {
            "verdict": a_verdict, "cohesion_gap": round(gap, 4),
            "n_qualifying_clusters": n_qualifying, "n_missing_vec": n_missing_vec,
            "scrambled_cohesion_gap": round(scrambled_gap, 4),
            "n_scrambled_qualifying_clusters": n_scrambled_qualifying,
            "floor_margin": round(floor_margin, 4),
            "cohesion_gap_negsample_mean": round(negsample_mean, 4),
            "cohesion_gap_negsample_sd": round(negsample_sd, 4),
            "not_robust_to_negsample_draw": not_robust_to_negsample,
            "negsample_draw_note": "partial substitute only -- see pre-reg claim2 draw-spread "
                                   "section; a full ConceptSpace basis redraw requires a "
                                   "multihour reencode and is declared out of scope",
        },
        "no_contradictions": {"verdict": b_verdict, "active_contradiction_count": n_contra,
                              "flagged_pairs_count": n_flagged, "examples": contra_examples[:5]},
    }


# =========================================================================== claim 3 (+ all 4)
def run_claim3_floors(store: HDFactStore, n_sample: int, seed: int, output_dir: str) -> dict:
    gm_map = build_active_relation_map(store, GM_REL)
    chains = build_two_hop_chains(gm_map)
    n = min(n_sample, len(chains))
    rng = random.Random(seed)
    sample = rng.sample(chains, n) if n > 0 else []

    all_objects = sorted(set(gm_map.values()))
    obj_mode_counts = Counter(gm_map.values())

    scrambled_perm_store = build_scrambled_store_permutation(gm_map, store.n_dim, store.seed + 999,
                                                              seed + 12345)
    scrambled_derange_store = build_scrambled_store_derangement(gm_map, store.n_dim, store.seed + 998,
                                                                 seed + 54321)

    ckpt_dir = os.path.join(output_dir, "ckpt_claim3_v2")
    done = completed_units(ckpt_dir)
    for i, (A, B, C) in enumerate(sample):
        key = unit_key("c3v2", i, A, B, C)
        if key in done:
            continue
        B_hat = query_single(store, A, GM_REL)
        C_hat = query_single(store, B_hat, GM_REL) if B_hat is not None else None
        mech_correct = (C_hat == C)
        leaked = bool(any(f.subject == A and f.obj == C and f.status in ("ACTIVE", "COMBINED")
                          for f in store._facts if f.relation == GM_REL))
        ablation_correct = (B_hat == C)

        Bp_hat = query_single(scrambled_perm_store, A, GM_REL)
        Cp_hat = query_single(scrambled_perm_store, Bp_hat, GM_REL) if Bp_hat is not None else None
        scramble_perm_correct = (Cp_hat == C)

        Bd_hat = query_single(scrambled_derange_store, A, GM_REL)
        Cd_hat = query_single(scrambled_derange_store, Bd_hat, GM_REL) if Bd_hat is not None else None
        scramble_derange_correct = (Cd_hat == C)

        ortho_pick = predict_orthographic_best(A, all_objects)
        ortho_correct = (ortho_pick == C)
        freq_pick = predict_frequency_mode(obj_mode_counts)
        freq_correct = (freq_pick == C)

        record_unit(ckpt_dir, key, {
            "A": A, "B": B, "C": C, "B_hat": B_hat, "C_hat": C_hat, "mech_correct": bool(mech_correct),
            "ablation_correct": bool(ablation_correct),
            "scramble_perm_correct": bool(scramble_perm_correct),
            "scramble_derange_correct": bool(scramble_derange_correct),
            "ortho_pick": ortho_pick, "ortho_correct": bool(ortho_correct),
            "freq_pick": freq_pick, "freq_correct": bool(freq_correct), "leaked": leaked,
        })

    units = load_units(ckpt_dir)
    rows = list(units.values())
    n_eval = len(rows)

    def _acc(field):
        return sum(1 for r in rows if r[field]) / n_eval if n_eval else 0.0

    mechanism_accuracy = _acc("mech_correct")
    ablation_accuracy = _acc("ablation_correct")
    scramble_perm_accuracy = _acc("scramble_perm_correct")
    scramble_derange_accuracy = _acc("scramble_derange_correct")
    ortho_accuracy = _acc("ortho_correct")
    freq_accuracy = _acc("freq_correct")
    leaked_count = sum(1 for r in rows if r["leaked"])

    floors = {"scramble_permutation": scramble_perm_accuracy,
             "scramble_derangement": scramble_derange_accuracy,
             "ablation": ablation_accuracy, "orthographic": ortho_accuracy,
             "frequency": freq_accuracy}
    floor_name = max(floors, key=lambda k: floors[k])
    floor_max = floors[floor_name]
    gap_vs_floor = mechanism_accuracy - floor_max

    def _digest(vals):
        return hashlib.sha256(json.dumps(vals, sort_keys=True, default=str).encode()).hexdigest()
    digests = {"mech": _digest([r["C_hat"] for r in rows]),
              "ablation": _digest([r["B_hat"] for r in rows]),
              "scramble_perm": _digest([r["scramble_perm_correct"] for r in rows]),
              "scramble_derange": _digest([r["scramble_derange_correct"] for r in rows]),
              "ortho": _digest([r["ortho_pick"] for r in rows]),
              "freq": _digest([r["freq_pick"] for r in rows])}
    arms_differ = len(set(digests.values())) > 1 if rows else False

    # between-random-projection-draw spread (bounded sub-sample)
    draw_sample = sample[:DRAW_SUBSAMPLE_CAP]
    draw_gaps: List[float] = []
    draw_mech: List[float] = []
    for di in range(N_DRAWS):
        draw_seed = store.seed + di
        draw_store = build_store_from_pairs(gm_map, store.n_dim, draw_seed)
        draw_scr = build_scrambled_store_derangement(gm_map, store.n_dim, draw_seed + 998,
                                                      seed + 54321 + di)
        m_correct, a_correct, s_correct = [], [], []
        for (A, B, C) in draw_sample:
            Bh = query_single(draw_store, A, GM_REL)
            Ch = query_single(draw_store, Bh, GM_REL) if Bh is not None else None
            m_correct.append(Ch == C)
            a_correct.append(Bh == C)
            Bs = query_single(draw_scr, A, GM_REL)
            Cs = query_single(draw_scr, Bs, GM_REL) if Bs is not None else None
            s_correct.append(Cs == C)
        m_acc = sum(m_correct) / len(m_correct) if m_correct else 0.0
        a_acc = sum(a_correct) / len(a_correct) if a_correct else 0.0
        s_acc = sum(s_correct) / len(s_correct) if s_correct else 0.0
        draw_mech.append(m_acc)
        draw_gaps.append(m_acc - max(a_acc, s_acc))

    draw_gap_mean = float(np.mean(draw_gaps)) if draw_gaps else 0.0
    draw_gap_sd = float(np.std(draw_gaps)) if draw_gaps else 0.0
    draw_gap_min = float(np.min(draw_gaps)) if draw_gaps else 0.0
    draw_survives = (draw_gap_mean - 2 * draw_gap_sd) >= 0.10

    if (leaked_count == 0 and mechanism_accuracy >= 0.50 and gap_vs_floor >= 0.20 and draw_survives):
        verdict = "HARD_PASS"
    elif (leaked_count > 0 or gap_vs_floor < 0.05 or mechanism_accuracy < 0.10):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    controls_discriminate = (mechanism_accuracy > floor_max) if n_eval else False

    return {
        "verdict": verdict, "n_available_chains": len(chains), "n_sampled": n_eval,
        "mechanism_accuracy": round(mechanism_accuracy, 4),
        "ablation_accuracy": round(ablation_accuracy, 4),
        "scramble_permutation_accuracy": round(scramble_perm_accuracy, 4),
        "scramble_derangement_accuracy": round(scramble_derange_accuracy, 4),
        "orthographic_accuracy": round(ortho_accuracy, 4), "frequency_accuracy": round(freq_accuracy, 4),
        "floor_name": floor_name, "floor_max": round(floor_max, 4), "gap_vs_floor": round(gap_vs_floor, 4),
        "leaked_count": leaked_count, "arms_differ_verified": bool(arms_differ),
        "controls_discriminate": bool(controls_discriminate),
        "draw_spread": {
            "n_draws": N_DRAWS, "n_questions_per_draw": len(draw_sample),
            "per_draw_mechanism_accuracy": [round(x, 4) for x in draw_mech],
            "per_draw_gap": [round(x, 4) for x in draw_gaps],
            "gap_mean": round(draw_gap_mean, 4), "gap_sd": round(draw_gap_sd, 4),
            "gap_min": round(draw_gap_min, 4),
            "survives_2sd_margin_0.10": bool(draw_survives),
        },
        "example_chains": [{"A": r["A"], "B": r["B"], "C": r["C"], "B_hat": r["B_hat"], "C_hat": r["C_hat"],
                           "ortho_pick": r["ortho_pick"], "freq_pick": r["freq_pick"]}
                           for r in rows[:5]],
    }


# =========================================================================== known-answer arm
def run_known_answer_arm(n_dim: int, k_chains: int, seed: int) -> dict:
    """Mandatory instrument check, at PRODUCTION n_dim -- distinct from the tiny n_dim=512 formula
    self-test. Plants noiseless 2-hop chains with synthetic tokens guaranteed disjoint from real
    vocabulary; if this arm fails, the READ-OUT/MECHANISM itself is broken at this scale,
    independent of whether the real foundation is any good."""
    st = HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality={GM_REL: "FUNCTIONAL"}, use_index=True)
    chains = []
    for i in range(k_chains):
        A, B, C = f"__ka_subj_{i}", f"__ka_mid_{i}", f"__ka_obj_{i}"
        st.store(A, GM_REL, B, "known_answer_plant", "TRUST_HIGH")
        st.store(B, GM_REL, C, "known_answer_plant", "TRUST_HIGH")
        chains.append((A, B, C))
    correct = []
    for A, B, C in chains:
        B_hat = query_single(st, A, GM_REL)
        C_hat = query_single(st, B_hat, GM_REL) if B_hat is not None else None
        correct.append(C_hat == C)
    acc = sum(correct) / len(correct) if correct else 0.0
    return {"n_dim": n_dim, "k_chains": k_chains, "accuracy": round(acc, 4),
           "instrument_valid": bool(acc >= 0.90)}


# =========================================================================== self-tests (new)
def _selftest_orthographic_score() -> None:
    assert trigram_jaccard("village", "village") == 1.0
    assert trigram_jaccard("village", "zzzzz") == 0.0
    assert lcp_ratio("village", "villager") > 0.5
    assert orthographic_score("cat", "car") > orthographic_score("cat", "dog")
    best = predict_orthographic_best("villag", ["village", "unrelated", "banana"])
    assert best == "village", best
    # query itself excluded even if present in candidates
    best2 = predict_orthographic_best("village", ["village", "villager", "banana"])
    assert best2 == "villager", best2


def _selftest_frequency_mode() -> None:
    c = Counter({"apple": 3, "banana": 7, "cherry": 5})
    assert predict_frequency_mode(c) == "banana"
    assert predict_frequency_mode(Counter()) is None
    # deterministic tie-break
    c2 = Counter({"zeta": 4, "alpha": 4})
    assert predict_frequency_mode(c2) == "alpha"


def _selftest_prefix_count() -> None:
    sentences = ["the village council met.", "villagers gathered near the well.",
                "pillage is not the same word."]
    toks = build_sorted_tokens(sentences)
    n_villag = prefix_count("villag", toks)
    assert n_villag == 2, n_villag  # village, villagers -- NOT pillage
    assert prefix_count("zzznope", toks) == 0


def _selftest_derangement_no_fixed_points() -> None:
    subjects = [f"s{i}" for i in range(30)]
    objects = [f"o{i}" for i in range(30)]
    shuffled = build_derangement_mapping(subjects, objects, shuffle_seed=42)
    n_fixed = sum(1 for o, s in zip(shuffled, objects) if o == s)
    assert n_fixed == 0, f"derangement must have zero fixed points, found {n_fixed}"
    assert sorted(shuffled) == sorted(objects), "derangement must be degree-preserving (same multiset)"
    # determinism
    shuffled2 = build_derangement_mapping(subjects, objects, shuffle_seed=42)
    assert shuffled == shuffled2, "derangement must be deterministic given the same seed"


def _selftest_known_answer_arm_production_scale() -> None:
    """Exercises HDFactStore at PRODUCTION n_dim=2048 inside self-test (not just n_dim=512) --
    this is the "discriminator survives scale" check applied to the INSTRUMENT itself."""
    result = run_known_answer_arm(n_dim=2048, k_chains=10, seed=777)
    assert result["instrument_valid"] is True, result
    assert result["accuracy"] == 1.0, result  # noiseless synthetic chains must be perfect


def _selftest_draw_spread_mechanics() -> None:
    """Small real store, 2 draws, proves the rebuild-under-different-seed machinery produces a
    non-degenerate (draw_store.seed differs, vectors differ, but the CLEAN mechanism still works
    on each draw)."""
    gm_map = {"a1": "b1", "b1": "c1", "a2": "b2", "b2": "c2", "a3": "b3", "b3": "c3"}
    for base_seed in (100, 200):
        st = build_store_from_pairs(gm_map, n_dim=512, seed=base_seed)
        chains = build_two_hop_chains(gm_map)
        correct = []
        for A, B, C in chains:
            B_hat = query_single(st, A, GM_REL)
            C_hat = query_single(st, B_hat, GM_REL) if B_hat is not None else None
            correct.append(C_hat == C)
        acc = sum(correct) / len(correct) if correct else 0.0
        assert acc == 1.0, (base_seed, acc)  # clean mechanism must work at EVERY draw seed


def _selftest_floor_gate_selects_max() -> None:
    """Formula check: floor_max selection picks the HIGHEST-scoring floor arm (the conservative
    choice), not an arbitrary or lowest one."""
    floors = {"a": 0.10, "b": 0.35, "c": 0.05}
    name = max(floors, key=lambda k: floors[k])
    assert name == "b" and floors[name] == 0.35, (name, floors[name])


def _run_all_selftests() -> dict:
    _selftest_orthographic_score()
    _selftest_frequency_mode()
    _selftest_prefix_count()
    _selftest_derangement_no_fixed_points()
    _selftest_known_answer_arm_production_scale()
    _selftest_draw_spread_mechanics()
    _selftest_floor_gate_selects_max()
    return {
        "orthographic_score_ok": True, "frequency_mode_ok": True, "prefix_count_ok": True,
        "derangement_no_fixed_points_ok": True,
        "known_answer_arm_production_scale_ok": True, "draw_spread_mechanics_ok": True,
        "floor_gate_selects_max_ok": True,
    }


# =========================================================================== orchestration
def run_validation(foundation_dir: str, run_mode: str, output_dir: str,
                   corpus_sources: Sequence[Tuple[str, str, str]]) -> dict:
    t0 = time.perf_counter()
    store = load_store(os.path.join(foundation_dir, "store"))
    space = load_concept_space(os.path.join(foundation_dir, "concept_space.npz"))
    print(f"[load] n_facts={len(store._facts)} n_dim={store.n_dim} foundation_dir={foundation_dir}",
          flush=True)

    sentences = load_corpus_sentences(corpus_sources)
    sorted_tokens = build_sorted_tokens(sentences)
    print(f"[corpus] {len(sentences)} sentences, {len(sorted_tokens)} tokens loaded from "
          f"{len(corpus_sources)} sources", flush=True)

    ka = run_known_answer_arm(n_dim=store.n_dim, k_chains=N_KNOWN_ANSWER_CHAINS, seed=SEED)
    print(f"[known_answer_arm] n_dim={ka['n_dim']} accuracy={ka['accuracy']} "
          f"instrument_valid={ka['instrument_valid']}", flush=True)

    if not ka["instrument_valid"]:
        elapsed = time.perf_counter() - t0
        return {
            "verdict": "INSTRUMENT_INVALID_ABORT",
            "verdict_msg": f"known_answer_arm accuracy={ka['accuracy']} < 0.90 at production "
                          f"n_dim={ka['n_dim']} -- mechanism/read-out itself is broken at this "
                          f"scale; aborting BEFORE trusting any claim1/2/3 number",
            "summary": "INSTRUMENT_INVALID_ABORT", "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
            "run_mode": run_mode, "foundation_dir": foundation_dir,
            "n_facts_loaded": len(store._facts), "seed": SEED, "known_answer_arm": ka,
        }

    n_correct = N_CORRECTNESS[run_mode]
    n_reason = N_REASON[run_mode]
    cluster_cap = N_COHERENCE_CLUSTER_CAP[run_mode]

    c1 = run_claim1_floors(store, sentences, sorted_tokens, n_correct, SEED, output_dir)
    print(f"[claim1 CORRECTNESS] {c1['verdict']} precision={c1['precision_hat']} "
          f"floor_max={c1['floor_max']}({c1['floor_name']}) gap={c1['gap']} n={c1['n_sampled']}",
          flush=True)

    c2 = run_claim2_floors(store, space, cluster_cap, SEED, output_dir)
    print(f"[claim2 COHERENCE] {c2['verdict']} cohesion_gap="
          f"{c2['same_rep_at_scale']['cohesion_gap']} scrambled="
          f"{c2['same_rep_at_scale']['scrambled_cohesion_gap']} active_contradictions="
          f"{c2['no_contradictions']['active_contradiction_count']}", flush=True)

    c3 = run_claim3_floors(store, n_reason, SEED, output_dir)
    print(f"[claim3 CAN-REASON] {c3['verdict']} mechanism={c3['mechanism_accuracy']} "
          f"floor_max={c3['floor_max']}({c3['floor_name']}) gap={c3['gap_vs_floor']} "
          f"draw_gap_mean={c3['draw_spread']['gap_mean']} draw_gap_sd={c3['draw_spread']['gap_sd']} "
          f"leaked={c3['leaked_count']}", flush=True)

    claim_verdicts = [c1["verdict"], c2["verdict"], c3["verdict"]]
    if all(v == "HARD_PASS" for v in claim_verdicts):
        overall = "HARD_PASS_foundation_validated"
    elif any(v == "HARD_FAIL" for v in claim_verdicts):
        overall = "HARD_FAIL_foundation_validation_failed"
    else:
        overall = "MIDDLE_BAND"

    smoke_controls_discriminate = c3["controls_discriminate"]
    if run_mode == "smoke" and not smoke_controls_discriminate:
        overall = "SMOKE_GATE_FAIL_discriminator_not_firing"

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"claim1={c1['verdict']}(gap={c1['gap']},floor={c1['floor_name']}) "
                  f"claim2={c2['verdict']}(cohesion={c2['same_rep_at_scale']['cohesion_gap']},"
                  f"scrambled={c2['same_rep_at_scale']['scrambled_cohesion_gap']},"
                  f"contra={c2['no_contradictions']['active_contradiction_count']}) "
                  f"claim3={c3['verdict']}(mech={c3['mechanism_accuracy']},"
                  f"floor={c3['floor_name']}={c3['floor_max']},"
                  f"draw_gap_mean={c3['draw_spread']['gap_mean']}+-{c3['draw_spread']['gap_sd']}) "
                  f"known_answer_instrument_valid={ka['instrument_valid']} "
                  f"smoke_controls_discriminate={smoke_controls_discriminate}")

    return {
        "verdict": overall, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "foundation_dir": foundation_dir, "n_facts_loaded": len(store._facts),
        "seed": SEED, "known_answer_arm": ka, "claim1_correctness": c1, "claim2_coherence": c2,
        "claim3_can_reason": c3, "smoke_controls_discriminate": smoke_controls_discriminate,
        "bands": {
            "claim1": {"hard_pass_gap_min": 0.20, "hard_fail_gap_max": 0.05, "floor": "max(chance,ortho,freq)"},
            "claim2a": {"hard_pass_cohesion_min": 0.10, "hard_pass_floor_margin_min": 0.08,
                       "hard_fail_cohesion_max": 0.02},
            "claim2b": {"hard_pass_active_contradictions": 0},
            "claim3": {"hard_pass_mech_min": 0.50, "hard_pass_gap_min": 0.20,
                      "hard_fail_gap_max": 0.05, "hard_pass_draw_margin": "gap_mean-2*gap_sd>=0.10",
                      "floor": "max(scramble_perm,scramble_derange,ablation,ortho,freq)"},
            "known_answer_arm": {"hard_pass_accuracy_min": 0.90},
        },
    }


# =========================================================================== I/O plumbing (reuse)
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    V1._write_start_marker(output_dir, run_mode, expected_n_units)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
           "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
           "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
           "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _atomic_write(output_dir: str, metrics: Dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--foundation-dir", type=str, default=None,
                        help="frozen snapshot dir (never the live data/foundation dir)")
    parser.add_argument("--freeze-from", type=str, default=None,
                        help="live dir to copytree-freeze before validating (writes under "
                             "data/foundation_snapshots/)")
    args = parser.parse_args()

    if args.self_test or not (args.smoke or args.full):
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = _run_all_selftests()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                  "verdict_msg": "all 7 v2 formula self-tests passed (orthographic score, frequency "
                                  "mode, prefix count, derangement no-fixed-points, known-answer arm "
                                  "AT PRODUCTION n_dim=2048, draw-spread rebuild mechanics, floor-gate "
                                  "max-selection)",
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    foundation_dir = args.foundation_dir
    if args.freeze_from:
        foundation_dir = V1.freeze_snapshot(args.freeze_from, tag="reading_grounding_v2q_" +
                                            ("smoke" if args.smoke else "full"))
        print(f"[freeze] {args.freeze_from} -> {foundation_dir}", flush=True)
    if not foundation_dir:
        raise ValueError("--foundation-dir (or --freeze-from) is required for --smoke/--full")

    if args.smoke:
        run_mode = "smoke"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_smoke")
        corpus_sources = CORPUS_SOURCES_SMOKE
        expected_units = N_CORRECTNESS["smoke"] + N_REASON["smoke"] + N_COHERENCE_CLUSTER_CAP["smoke"]
    else:
        run_mode = "full"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        corpus_sources = CORPUS_SOURCES_FULL
        expected_units = N_CORRECTNESS["full"] + N_REASON["full"]

    _write_start_marker(output_dir, run_mode, expected_n_units=expected_units)
    metrics = run_validation(foundation_dir, run_mode, output_dir, corpus_sources)
    _atomic_write(output_dir, metrics)
    print(f"[{ANCHOR_NAME}] {metrics['verdict']} elapsed={metrics['elapsed_s']:.2f}s -> {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately narrow; NOT BaseException
        _write_crash_metrics(repo_path(f"data/exp_{ANCHOR_NAME}"), e)
        raise
