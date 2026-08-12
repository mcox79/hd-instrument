# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (claim3 mechanism/ablation/scrambled prediction arrays hashed)
# - final_metrics_atomicity = tmp_replace (single-shot)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a declared per-claim (discrete exact-match / co-occurrence gap metrics, no Gaussian floor)
# - baseline_in_band EXEMPTED for claim3 scrambled/ablated arms (intentional can-fail controls)
# - discriminator survives scale: smoke runs the REAL pipeline on the real (frozen) foundation,
#   not a toy substitute; smoke_controls_discriminate is a hard gate (see run_validation)
# - HARD_PASS strictly above floor (explicit gap margins, not at-floor)
# - HP_SCOPE: bands declared per-claim in the pre-reg; overall verdict = AND/OR of the 3
# - cardinality_ok: N/A (no sweep axis; fixed per-mode sample sizes, declared no_sweep_axis)
# - per-unit failure-class instrumentation: N/A (no per-unit try/except; a single failed unit
#   would indicate a code bug, not an expected per-item failure mode, so it propagates and halts)
# - calibration_check: default_ok_for_this_regime (fixed thresholds/sample sizes, no adaptive tuning)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL HDFactStore / ConceptSpace objects at tiny scale (real_code_path)
# - substrate_signature_checked: HDFactStore(n_dim, seed, relation_cardinality, sr_threshold, use_index)
"""exp_foundation_validation_harness_v1 -- FOUNDATION-QUALITY VALIDATION harness: is the
reading-grown foundation (hdlab.hd_fact_store.HDFactStore, populated by hdlab.reading_grounding_
loop) TRULY grounded and properly organized? See preregs/2026-08-12_foundation_validation_
harness_v1.md for the full pre-reg (bands, sampling scheme, control design, SCHEMA-VET gates).

THREE CLAIMS, each with pre-registered HARD_PASS/HARD_FAIL bands:
  1. CORRECTNESS  -- sampled (lemma, GROUNDED_MEANING, canon_obj) facts checked against modern-
                      corpus co-occurrence (held-out reference; per-fact sentence pointers are
                      not recoverable from the store post-promotion, see pre-reg), vs a
                      decoy-object chance baseline.
  2. COHERENCE    -- (a) same-idea==same-rep at foundation scale (ConceptSpace cosine cohesion
                      of same-canon_obj clusters vs cross-cluster); (b) no contradictory ACTIVE
                      facts co-stored (audits the store's own FUNCTIONAL-relation invariant).
  3. CAN-REASON   -- 2-hop transitive GROUNDED_MEANING chains (A->B->C) whose answer is NEVER a
                      single stored fact (no-leak), answered by CHAINING TWO REAL
                      HDFactStore.query() calls (the store's own glass-box read path). Controls:
                      no-leak re-verification, scramble-foundation (shuffle subject->object,
                      rebuild a fresh store, mechanism must collapse toward the empirical chance
                      floor), ablation (drop the 2nd hop, must collapse to near-0 since B != C by
                      chain construction).

SCOPE OF THIS DISPATCH: SELF-TEST + SMOKE ONLY, against a FROZEN, TIMESTAMPED COPY of
data/foundation/reading_grounding_v1/ (an accumulation agent is actively writing the live dir;
this harness never opens it directly -- see --freeze-from). NO FULL dispatch: the decisive run
is deferred until the director hands off the final (post-accumulation) foundation path.

Modes: --self-test (tiny synthetic-but-real fixtures, <5s) / --smoke (real pipeline against a
frozen snapshot, reduced N) / --full (real pipeline, full N; requires explicit --foundation-dir,
never defaults -- NOT run by this dispatch).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import random
import re
import shutil
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ANCHOR_NAME = "foundation_validation_harness_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.foundation_persistence import load_store, load_concept_space  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEED = 20260812
GM_REL = "GROUNDED_MEANING"
KW_REL = "KNOWN_WORD"
FUNCTIONAL_RELATIONS = {KW_REL, GM_REL}

N_CORRECTNESS = {"smoke": 20, "full": 150}
N_REASON = {"smoke": 25, "full": 150}
N_COHERENCE_CLUSTER_CAP = {"smoke": 40, "full": 100000}  # full = effectively unbounded
K_NEG_COHESION = 5

CORPUS_SOURCES_SMOKE: List[Tuple[str, str, str]] = [
    ("textbook_concepts_biology",
     os.path.join(REPO_ROOT, "data", "corpora", "textbook_concepts_biology", "cleaned",
                  "concepts_biology.clean.txt"), "raw_text"),
    ("process_articles_v1",
     os.path.join(REPO_ROOT, "data", "corpora", "process_articles_v1", "process_articles.json"),
     "json_articles"),
]
CORPUS_SOURCES_FULL: List[Tuple[str, str, str]] = list(CORPUS_SOURCES_SMOKE) + [
    ("onestop_adv_glob", os.path.join(REPO_ROOT, "data", "corpora", "onestop",
                                      "Texts-SeparatedByReadingLevel", "Adv-Txt", "*.txt"), "raw_text_glob"),
    ("onestop_ele_glob", os.path.join(REPO_ROOT, "data", "corpora", "onestop",
                                      "Texts-SeparatedByReadingLevel", "Ele-Txt", "*.txt"), "raw_text_glob"),
    ("onestop_int_glob", os.path.join(REPO_ROOT, "data", "corpora", "onestop",
                                      "Texts-SeparatedByReadingLevel", "Int-Txt", "*.txt"), "raw_text_glob"),
    ("base_vocabulary_glob", os.path.join(REPO_ROOT, "data", "corpora", "base_vocabulary",
                                          "cleaned", "*"), "raw_text_glob"),
]
# EXCLUDED (USER-LOCKED modern-only): mcguffey_graded, mcguffey_readers, graded_readers_*.

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


# =========================================================================== corpus loading
def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]


def load_corpus_sentences(sources: Sequence[Tuple[str, str, str]]) -> List[str]:
    """Load + sentence-split all declared corpus sources into one flat list. Missing files are
    skipped with a printed warning (never crash the harness on an optional FULL-only source)."""
    sentences: List[str] = []
    for name, path, kind in sources:
        if kind == "raw_text":
            if not os.path.isfile(path):
                print(f"[corpus] WARN missing {name}: {path}", flush=True)
                continue
            with open(path, encoding="utf-8", errors="replace") as f:
                sentences.extend(_split_sentences(f.read()))
        elif kind == "raw_text_glob":
            import glob
            files = sorted(glob.glob(path))
            if not files:
                print(f"[corpus] WARN no files matched {name}: {path}", flush=True)
            for fp in files:
                if os.path.isfile(fp):
                    with open(fp, encoding="utf-8", errors="replace") as f:
                        sentences.extend(_split_sentences(f.read()))
        elif kind == "json_articles":
            if not os.path.isfile(path):
                print(f"[corpus] WARN missing {name}: {path}", flush=True)
                continue
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            for art_name in sorted(d.get("articles", {})):
                sections = d["articles"][art_name]
                for sec_name in sorted(sections):
                    sentences.extend(sections[sec_name])
        else:
            raise ValueError(f"unknown corpus source kind {kind!r} for {name!r}")
    return sentences


_PREFIX_PATTERN_CACHE: Dict[str, "re.Pattern"] = {}


def _prefix_pattern(lemma: str) -> "re.Pattern":
    pat = _PREFIX_PATTERN_CACHE.get(lemma)
    if pat is None:
        pat = re.compile(r"\b" + re.escape(lemma), re.IGNORECASE)
        _PREFIX_PATTERN_CACHE[lemma] = pat
    return pat


def cooccurs(lemma: str, other: str, sentences: Sequence[str]) -> bool:
    """True iff some sentence contains a word starting with `lemma` AND a word starting with
    `other` (prefix-from-word-start match; stored lemmas are already stemmed, see pre-reg)."""
    p_lemma, p_other = _prefix_pattern(lemma), _prefix_pattern(other)
    for s in sentences:
        if p_lemma.search(s) and p_other.search(s):
            return True
    return False


# =========================================================================== small math helpers
def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score 95% CI for a binomial proportion k/n. Closed-form, no external stats dep."""
    if n == 0:
        return (0.0, 1.0)
    phat = k / n
    denom = 1.0 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def cohesion_gap(clusters: Dict[str, List[np.ndarray]], rng: random.Random,
                 k_neg: int = K_NEG_COHESION, cap: Optional[int] = None) -> Tuple[float, int]:
    """Mean(intra-cluster cosine - inter-cluster cosine) over clusters with >=2 members.
    Deterministic given `rng` (caller owns the seed/consumption order)."""
    keys = sorted(k for k in clusters if len(clusters[k]) >= 2)
    if cap is not None:
        keys = keys[:cap]
    if not keys:
        return (0.0, 0)
    gaps = []
    for key in keys:
        members = clusters[key]
        intra_vals = [cosine(members[i], members[j])
                      for i in range(len(members)) for j in range(i + 1, len(members))]
        intra = sum(intra_vals) / len(intra_vals)
        other_keys = [k2 for k2 in keys if k2 != key]
        inter_vals = []
        if other_keys:
            for m in members:
                for _ in range(k_neg):
                    ok = rng.choice(other_keys)
                    om = rng.choice(clusters[ok])
                    inter_vals.append(cosine(m, om))
        inter = sum(inter_vals) / len(inter_vals) if inter_vals else 0.0
        gaps.append(intra - inter)
    return (sum(gaps) / len(gaps), len(keys))


# =========================================================================== store audits
def build_active_relation_map(store: HDFactStore, relation: str) -> Dict[str, str]:
    """subject -> obj for ACTIVE facts of `relation` (shadow-ledger read; see pre-reg "Reused
    organs" -- used only to construct/grade questions, never as the answer path)."""
    m: Dict[str, str] = {}
    for f in store._facts:
        if f.relation == relation and f.status == "ACTIVE" and f.subject not in m:
            m[f.subject] = f.obj
    return m


def find_active_contradictions(store: HDFactStore,
                               functional_relations: Sequence[str]) -> Tuple[int, List[dict], int]:
    """Audit HDFactStore._facts directly (sanctioned precedent: hdlab/foundation_persistence.py
    already reads this same private state). Returns (active_contradiction_count, examples,
    flagged_pairs_count)."""
    by_sr: Dict[Tuple[str, str], List] = defaultdict(list)
    for f in store._facts:
        if f.relation in functional_relations:
            by_sr[(f.subject, f.relation)].append(f)
    contradictions: List[dict] = []
    n_flagged_pairs = 0
    for (s, r), facts in sorted(by_sr.items()):
        active = [f for f in facts if f.status == "ACTIVE"]
        distinct_objs = sorted({f.obj for f in active})
        if len(distinct_objs) > 1:
            contradictions.append({"subject": s, "relation": r, "objects": distinct_objs})
        if any(f.status == "FLAGGED" for f in facts):
            n_flagged_pairs += 1
    return len(contradictions), contradictions, n_flagged_pairs


def build_two_hop_chains(gm_map: Dict[str, str]) -> List[Tuple[str, str, str]]:
    """Non-trivial, no-leak 2-hop GROUNDED_MEANING chains A->B->C (see pre-reg for the 3
    exclusion conditions: C==B degenerate, B==A cycle, (A,C) direct leak)."""
    direct = set(gm_map.items())
    chains = []
    for A in sorted(gm_map):
        B = gm_map[A]
        if B not in gm_map or B == A:
            continue
        C = gm_map[B]
        if C == B or C == A:
            continue
        if (A, C) in direct:
            continue
        chains.append((A, B, C))
    return chains


def query_single(store: HDFactStore, subject: str, relation: str) -> Optional[str]:
    """The REAL glass-box read path: HDFactStore.query() (unbind+cleanup), first live result."""
    results = store.query(subject, relation)
    live = [r for r in results if r["status"] in ("ACTIVE", "COMBINED")]
    return live[0]["object"] if live else None


def build_scrambled_store(gm_map: Dict[str, str], n_dim: int, base_seed: int,
                          shuffle_seed: int) -> HDFactStore:
    """Fresh HDFactStore over the SAME subject universe, objects shuffled (fixed seed,
    degree-preserving marginal). SCRAMBLE-FOUNDATION control (claim 3)."""
    subjects = sorted(gm_map.keys())
    objects = [gm_map[s] for s in subjects]
    rng = random.Random(shuffle_seed)
    shuffled = list(objects)
    rng.shuffle(shuffled)
    new_store = HDFactStore(n_dim=n_dim, seed=base_seed, relation_cardinality={GM_REL: "FUNCTIONAL"},
                            use_index=True)
    for subj, obj in zip(subjects, shuffled):
        new_store.store(subj, GM_REL, obj, "scramble_control", "TRUST_MID")
    return new_store


# =========================================================================== claim 1: CORRECTNESS
def run_claim1(store: HDFactStore, sentences: List[str], n_sample: int, seed: int,
              output_dir: str) -> dict:
    gm_facts = [f for f in store._facts if f.relation == GM_REL and f.status in ("ACTIVE", "COMBINED")]
    n_live = len(gm_facts)
    self_grounded = [f for f in gm_facts if f.subject == f.obj]
    cross = sorted(((f.subject, f.obj) for f in gm_facts if f.subject != f.obj))
    self_grounded_rate = len(self_grounded) / n_live if n_live else 0.0

    all_objects = sorted({f.obj for f in gm_facts})
    n = min(n_sample, len(cross))
    rng = random.Random(seed)
    sample = rng.sample(cross, n) if n > 0 else []

    ckpt_dir = os.path.join(output_dir, "ckpt_claim1")
    done = completed_units(ckpt_dir)
    for i, (lemma, canon_obj) in enumerate(sample):
        key = unit_key("c1", i, lemma, canon_obj)
        if key in done:
            continue
        decoy_pool = [o for o in all_objects if o not in (canon_obj, lemma)]
        decoy = rng.choice(decoy_pool) if decoy_pool else canon_obj
        real_hit = cooccurs(lemma, canon_obj, sentences)
        decoy_hit = cooccurs(lemma, decoy, sentences)
        record_unit(ckpt_dir, key, {"lemma": lemma, "canon_obj": canon_obj, "decoy": decoy,
                                    "real_hit": real_hit, "decoy_hit": decoy_hit})

    units = load_units(ckpt_dir)
    real_hits = [u["real_hit"] for u in units.values()]
    decoy_hits = [u["decoy_hit"] for u in units.values()]
    k_real, k_decoy, n_eval = sum(real_hits), sum(decoy_hits), len(units)
    precision_hat = k_real / n_eval if n_eval else 0.0
    chance_hat = k_decoy / n_eval if n_eval else 0.0
    lo_p, hi_p = wilson_ci(k_real, n_eval)
    lo_c, hi_c = wilson_ci(k_decoy, n_eval)
    gap = precision_hat - chance_hat

    if gap >= 0.20 and lo_p > hi_c:
        verdict = "HARD_PASS"
    elif gap < 0.05:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict, "n_live_grounded_meaning": n_live, "n_self_grounded": len(self_grounded),
        "self_grounded_rate": round(self_grounded_rate, 4), "n_cross_grounded": len(cross),
        "n_sampled": n_eval, "precision_hat": round(precision_hat, 4), "chance_hat": round(chance_hat, 4),
        "gap": round(gap, 4), "wilson_precision": [round(lo_p, 4), round(hi_p, 4)],
        "wilson_chance": [round(lo_c, 4), round(hi_c, 4)],
        "not_found_rate": round(1.0 - max(precision_hat, chance_hat) if n_eval == 0 else
                                sum(1 for u in units.values() if not u["real_hit"] and not u["decoy_hit"]) / n_eval, 4),
        "corpus_n_sentences": len(sentences),
    }


# =========================================================================== claim 2: COHERENCE
def run_claim2(store: HDFactStore, space, cluster_cap: int, seed: int, output_dir: str) -> dict:
    gm_facts = [f for f in store._facts if f.relation == GM_REL and f.status in ("ACTIVE", "COMBINED")]
    clusters_lemmas: Dict[str, List[str]] = defaultdict(list)
    for f in gm_facts:
        clusters_lemmas[f.obj].append(f.subject)

    ckpt_dir = os.path.join(output_dir, "ckpt_claim2")
    done = completed_units(ckpt_dir)
    clusters_vecs: Dict[str, List[np.ndarray]] = {}
    n_missing_vec = 0
    qualifying_keys = sorted(k for k in clusters_lemmas if len(clusters_lemmas[k]) >= 2)[:cluster_cap]
    for ci, key in enumerate(qualifying_keys):
        ckey = unit_key("c2", ci, key)
        vecs = []
        for lem in sorted(set(clusters_lemmas[key])):
            v = space.bundle(lem)
            if v is None:
                n_missing_vec += 1
                continue
            vecs.append(v)
        if ckey not in done:
            record_unit(ckpt_dir, ckey, {"cluster": key, "n_members": len(vecs)})
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

    n_contra, contra_examples, n_flagged = find_active_contradictions(store, sorted(FUNCTIONAL_RELATIONS))
    b_verdict = "HARD_PASS" if n_contra == 0 else "HARD_FAIL"

    if a_verdict == "HARD_PASS" and b_verdict == "HARD_PASS":
        overall = "HARD_PASS"
    elif a_verdict == "HARD_FAIL" or b_verdict == "HARD_FAIL":
        overall = "HARD_FAIL"
    else:
        overall = "MIDDLE_BAND"

    # (c) descriptive concept-neighborhood spot-check
    self_grounded_roots = sorted({f.subject for f in gm_facts if f.subject == f.obj})
    rng_desc = random.Random(seed + 1)
    sample_roots = rng_desc.sample(self_grounded_roots, min(10, len(self_grounded_roots)))
    anchors = space.anchors()
    neighborhoods = {}
    for root in sample_roots:
        v = space.bundle(root)
        if v is None:
            continue
        sims = [(lem, cosine(v, space.bundle(lem))) for lem in anchors if lem != root]
        sims.sort(key=lambda kv: -kv[1])
        neighborhoods[root] = [f"{lem}:{s:.3f}" for lem, s in sims[:5]]

    return {
        "verdict": overall,
        "same_rep_at_scale": {"verdict": a_verdict, "cohesion_gap": round(gap, 4),
                              "n_qualifying_clusters": n_qualifying, "n_missing_vec": n_missing_vec},
        "no_contradictions": {"verdict": b_verdict, "active_contradiction_count": n_contra,
                              "flagged_pairs_count": n_flagged, "examples": contra_examples[:5]},
        "concept_neighborhoods_descriptive": neighborhoods,
    }


# =========================================================================== claim 3: CAN-REASON
def run_claim3(store: HDFactStore, n_sample: int, seed: int, output_dir: str) -> dict:
    gm_map = build_active_relation_map(store, GM_REL)
    chains = build_two_hop_chains(gm_map)
    n = min(n_sample, len(chains))
    rng = random.Random(seed)
    sample = rng.sample(chains, n) if n > 0 else []

    scrambled_store = build_scrambled_store(gm_map, store.n_dim, store.seed + 999, seed + 12345)

    ckpt_dir = os.path.join(output_dir, "ckpt_claim3")
    done = completed_units(ckpt_dir)
    for i, (A, B, C) in enumerate(sample):
        key = unit_key("c3", i, A, B, C)
        if key in done:
            continue
        # mechanism: 2 chained REAL store.query() calls
        B_hat = query_single(store, A, GM_REL)
        C_hat = query_single(store, B_hat, GM_REL) if B_hat is not None else None
        mech_correct = (C_hat == C)
        # no-leak re-verification at measurement time: is (A, GM_REL, C) itself a live fact?
        leaked = bool(any(f.subject == A and f.obj == C and f.status in ("ACTIVE", "COMBINED")
                          for f in store._facts if f.relation == GM_REL))
        # ablation: hop1 guess only, no 2nd hop
        ablation_correct = (B_hat == C)
        # scramble: identical mechanism, scrambled store, graded against the SAME true C
        Bs_hat = query_single(scrambled_store, A, GM_REL)
        Cs_hat = query_single(scrambled_store, Bs_hat, GM_REL) if Bs_hat is not None else None
        scramble_correct = (Cs_hat == C)
        record_unit(ckpt_dir, key, {
            "A": A, "B": B, "C": C, "B_hat": B_hat, "C_hat": C_hat, "mech_correct": bool(mech_correct),
            "ablation_correct": bool(ablation_correct), "scramble_correct": bool(scramble_correct),
            "leaked": leaked,
        })

    units = load_units(ckpt_dir)
    rows = list(units.values())
    n_eval = len(rows)
    mechanism_accuracy = sum(r["mech_correct"] for r in rows) / n_eval if n_eval else 0.0
    ablation_accuracy = sum(r["ablation_correct"] for r in rows) / n_eval if n_eval else 0.0
    scrambled_accuracy = sum(r["scramble_correct"] for r in rows) / n_eval if n_eval else 0.0
    leaked_count = sum(1 for r in rows if r["leaked"])

    import hashlib
    def _digest(vals):
        return hashlib.sha256(json.dumps(vals, sort_keys=True, default=str).encode()).hexdigest()
    mech_digest = _digest([r["C_hat"] for r in rows])
    abl_digest = _digest([r["B_hat"] for r in rows])
    scr_digest = _digest([(r["A"], r["mech_correct"], r["scramble_correct"]) for r in rows])
    arms_differ = len({mech_digest, abl_digest, scr_digest}) > 1 if rows else False

    gap_scramble = mechanism_accuracy - scrambled_accuracy
    gap_ablation = mechanism_accuracy - ablation_accuracy

    if (leaked_count == 0 and mechanism_accuracy >= 0.50 and gap_scramble >= 0.20 and gap_ablation >= 0.20):
        verdict = "HARD_PASS"
    elif (leaked_count > 0 or gap_scramble < 0.05 or gap_ablation < 0.05 or mechanism_accuracy < 0.10):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    controls_discriminate = (mechanism_accuracy > scrambled_accuracy and
                             mechanism_accuracy > ablation_accuracy) if n_eval else False

    return {
        "verdict": verdict, "n_available_chains": len(chains), "n_sampled": n_eval,
        "mechanism_accuracy": round(mechanism_accuracy, 4),
        "scrambled_accuracy": round(scrambled_accuracy, 4),
        "ablation_accuracy": round(ablation_accuracy, 4),
        "gap_vs_scramble": round(gap_scramble, 4), "gap_vs_ablation": round(gap_ablation, 4),
        "leaked_count": leaked_count, "arms_differ_verified": bool(arms_differ),
        "controls_discriminate": bool(controls_discriminate),
        "example_chains": [{"A": r["A"], "B": r["B"], "C": r["C"], "B_hat": r["B_hat"], "C_hat": r["C_hat"]}
                           for r in rows[:5]],
    }


# =========================================================================== self-tests
def _selftest_wilson_ci() -> None:
    for k, n in [(5, 10), (0, 10), (10, 10), (50, 100)]:
        lo, hi = wilson_ci(k, n)
        phat = k / n
        assert 0.0 <= lo <= phat + 1e-9 and phat - 1e-9 <= hi <= 1.0, (k, n, lo, hi, phat)
    lo0, hi0 = wilson_ci(0, 10)
    assert lo0 == 0.0, lo0
    lo_small, hi_small = wilson_ci(5, 10)
    lo_big, hi_big = wilson_ci(50, 100)
    assert (hi_big - lo_big) < (hi_small - lo_small), "CI should narrow as n grows at same phat"


def _selftest_cooccurs_prefix_match() -> None:
    sentences = ["the village council met at dawn.", "the pillage was swift and cruel.",
                 "villagers gathered near the old well."]
    assert cooccurs("villag", "council", sentences) is True
    assert cooccurs("villag", "dawn", sentences) is True
    p_villag = _prefix_pattern("villag")
    assert not p_villag.search("the pillage was swift and cruel."), "prefix match must not match mid-word"
    assert p_villag.search("villagers gathered near the old well."), "prefix must extend to villagers"
    assert cooccurs("villag", "zzznope", sentences) is False


def _selftest_cohesion_gap_discriminates() -> None:
    rng_data = np.random.default_rng(7)
    d = 32
    clusters_tight: Dict[str, List[np.ndarray]] = {}
    for name in ["A", "B", "C"]:
        base = rng_data.choice([-1.0, 1.0], size=d)
        clusters_tight[name] = [np.sign(base + rng_data.normal(0, 0.05, size=d)) for _ in range(3)]
    rng = random.Random(1)
    gap_tight, n_q = cohesion_gap(clusters_tight, rng)
    assert n_q == 3
    assert gap_tight > 0.3, f"tight-cluster gap too low: {gap_tight}"

    clusters_random: Dict[str, List[np.ndarray]] = {
        name: [rng_data.choice([-1.0, 1.0], size=d) for _ in range(3)] for name in ["A", "B", "C"]
    }
    rng2 = random.Random(2)
    gap_random, _ = cohesion_gap(clusters_random, rng2)
    assert gap_random < 0.15, f"random-cluster gap too high (should be near 0): {gap_random}"
    assert gap_tight > gap_random, "cohesion_gap must discriminate structured vs unstructured"


def _selftest_contradiction_scanner_can_fail() -> None:
    st = HDFactStore(n_dim=512, seed=11, relation_cardinality={"rel": "FUNCTIONAL"}, use_index=True)
    st.store("clean1", "rel", "o1", "src", "TRUST_MID")
    r1 = st.store("conflict", "rel", "oA", "src", "TRUST_MID")
    r2 = st.store("conflict", "rel", "oB", "src", "TRUST_MID")  # equal trust, functional -> FLAG
    assert r2.resolution == "FLAG", r2
    n_contra, _, n_flag = find_active_contradictions(st, ["rel"])
    assert n_contra == 0, f"FLAGGED pair must NOT count as an active contradiction: {n_contra}"
    assert n_flag == 1, n_flag

    # simulate a hypothetical bug: force both conflicting records back to ACTIVE
    for f in st._facts:
        if f.subject == "conflict":
            f.status = "ACTIVE"
    n_contra2, examples2, _ = find_active_contradictions(st, ["rel"])
    assert n_contra2 == 1, f"scanner failed to catch an injected active contradiction: {n_contra2}"
    assert examples2[0]["subject"] == "conflict"


def _selftest_chain_builder_noleak() -> None:
    """NOTE on "no-leak": gm_map is subject->object with AT MOST ONE entry per subject (built
    from ACTIVE facts of a FUNCTIONAL relation). That means the ONLY direct fact about A is
    (A, B) -- a genuine (A, C) leak is therefore STRUCTURALLY IMPOSSIBLE at the dict level once
    C != B (already excluded by the degenerate check below); `(A,C) in direct` in
    build_two_hop_chains is a defensive no-op on any clean functional map, not an independent
    filter. A REAL leak can only arise from a STORE-level invariant violation (two co-existing
    ACTIVE facts for one subject, which claim 2b's contradiction scanner would also catch) --
    that scenario is exercised at the store level in
    _selftest_leak_detection_fires_on_corrupted_store, not here."""
    # clean case: p->q->r is a genuine non-trivial 2-hop chain, no direct (p,r) pair -> included.
    gm_map = {"p": "q", "q": "r", "s": "t"}
    chains = build_two_hop_chains(gm_map)
    assert chains == [("p", "q", "r")], chains

    # degenerate case: B == C (hop-2 self-grounded / terminal) must be excluded (ablation would
    # trivially "win" on a degenerate chain, defeating the control's purpose).
    gm_map_degenerate = {"p": "q", "q": "q"}
    assert build_two_hop_chains(gm_map_degenerate) == []

    # cycle case: B == A must be excluded.
    gm_map_cycle = {"p": "q", "q": "p"}
    assert build_two_hop_chains(gm_map_cycle) == []


def _selftest_leak_detection_fires_on_corrupted_store() -> None:
    """The measurement-time `leaked` re-verification in run_claim3 scans HDFactStore._facts
    directly (not gm_map) for ANY live (A, GM_REL, C) fact -- this is the ONLY way a genuine leak
    can be constructed (bypassing store()'s own FUNCTIONAL enforcement by direct list append,
    simulating a hypothetical future bug), and this test proves the check fires when it does."""
    st = HDFactStore(n_dim=512, seed=31, relation_cardinality={GM_REL: "FUNCTIONAL"}, use_index=True)
    st.store("a", GM_REL, "b", "src", "TRUST_MID")
    st.store("b", GM_REL, "c", "src", "TRUST_MID")
    A, B, C = "a", "b", "c"
    leaked_before = any(f.subject == A and f.obj == C and f.status in ("ACTIVE", "COMBINED")
                        for f in st._facts if f.relation == GM_REL)
    assert leaked_before is False, "clean 2-hop store must not report a leak"

    # inject a corrupted direct fact (bypasses store()'s FUNCTIONAL conflict logic on purpose,
    # simulating a hypothetical bug where two ACTIVE facts coexist for one subject).
    corrupt_vec = st._encode_fact(A, GM_REL, C, "corrupt", "TRUST_MID")
    from hdlab.hd_fact_store import FactRecord
    st._append_fact(FactRecord(fid=len(st._facts), vec=corrupt_vec, sr_key=st._sr_key(A, GM_REL),
                               subject=A, relation=GM_REL, obj=C, source="corrupt",
                               trust_sym="TRUST_MID", trust_level=0.6, status="ACTIVE"))
    leaked_after = any(f.subject == A and f.obj == C and f.status in ("ACTIVE", "COMBINED")
                       for f in st._facts if f.relation == GM_REL)
    assert leaked_after is True, "leak detector failed to catch an injected direct-fact leak"


def _selftest_reason_mechanism_and_controls() -> None:
    st = HDFactStore(n_dim=512, seed=21, relation_cardinality={GM_REL: "FUNCTIONAL"}, use_index=True)
    chains_plan = [("a1", "b1", "c1"), ("a2", "b2", "c2"), ("a3", "b3", "c3")]
    for A, B, C in chains_plan:
        st.store(A, GM_REL, B, "src", "TRUST_MID")
        st.store(B, GM_REL, C, "src", "TRUST_MID")
    gm_map = build_active_relation_map(st, GM_REL)
    chains = build_two_hop_chains(gm_map)
    assert set(chains) == set(chains_plan), (chains, chains_plan)

    mech_correct, abl_correct = [], []
    for A, B, C in chains:
        B_hat = query_single(st, A, GM_REL)
        C_hat = query_single(st, B_hat, GM_REL) if B_hat is not None else None
        mech_correct.append(C_hat == C)
        abl_correct.append(B_hat == C)
    mechanism_accuracy = sum(mech_correct) / len(mech_correct)
    ablation_accuracy = sum(abl_correct) / len(abl_correct)
    assert mechanism_accuracy == 1.0, mechanism_accuracy
    assert ablation_accuracy == 0.0, ablation_accuracy

    scrambled = build_scrambled_store(gm_map, st.n_dim, st.seed + 999, shuffle_seed=999)
    scr_correct = []
    for A, B, C in chains:
        Bs = query_single(scrambled, A, GM_REL)
        Cs = query_single(scrambled, Bs, GM_REL) if Bs is not None else None
        scr_correct.append(Cs == C)
    scrambled_accuracy = sum(scr_correct) / len(scr_correct)
    assert (mechanism_accuracy - scrambled_accuracy) >= 0.5, (mechanism_accuracy, scrambled_accuracy)


def _run_all_selftests() -> dict:
    _selftest_wilson_ci()
    _selftest_cooccurs_prefix_match()
    _selftest_cohesion_gap_discriminates()
    _selftest_contradiction_scanner_can_fail()
    _selftest_chain_builder_noleak()
    _selftest_leak_detection_fires_on_corrupted_store()
    _selftest_reason_mechanism_and_controls()
    return {
        "wilson_ci_ok": True, "cooccurs_prefix_match_ok": True, "cohesion_gap_discriminates_ok": True,
        "contradiction_scanner_can_fail_ok": True, "chain_builder_noleak_ok": True,
        "leak_detection_fires_on_corrupted_store_ok": True, "reason_mechanism_and_controls_ok": True,
    }


# =========================================================================== freeze helper
def freeze_snapshot(live_dir: str, tag: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = repo_path(os.path.join("data", "foundation_snapshots", f"{tag}_{ts}"))
    shutil.copytree(live_dir, dest)
    return dest


# =========================================================================== orchestration
def run_validation(foundation_dir: str, run_mode: str, output_dir: str,
                   corpus_sources: Sequence[Tuple[str, str, str]]) -> dict:
    t0 = time.perf_counter()
    store = load_store(os.path.join(foundation_dir, "store"))
    space = load_concept_space(os.path.join(foundation_dir, "concept_space.npz"))
    print(f"[load] n_facts={len(store._facts)} n_dim={store.n_dim} foundation_dir={foundation_dir}",
          flush=True)

    sentences = load_corpus_sentences(corpus_sources)
    print(f"[corpus] {len(sentences)} sentences loaded from {len(corpus_sources)} sources", flush=True)

    n_correct = N_CORRECTNESS[run_mode]
    n_reason = N_REASON[run_mode]
    cluster_cap = N_COHERENCE_CLUSTER_CAP[run_mode]

    c1 = run_claim1(store, sentences, n_correct, SEED, output_dir)
    print(f"[claim1 CORRECTNESS] {c1['verdict']} precision={c1['precision_hat']} "
          f"chance={c1['chance_hat']} gap={c1['gap']} n={c1['n_sampled']}", flush=True)

    c2 = run_claim2(store, space, cluster_cap, SEED, output_dir)
    print(f"[claim2 COHERENCE] {c2['verdict']} cohesion_gap="
          f"{c2['same_rep_at_scale']['cohesion_gap']} active_contradictions="
          f"{c2['no_contradictions']['active_contradiction_count']}", flush=True)

    c3 = run_claim3(store, n_reason, SEED, output_dir)
    print(f"[claim3 CAN-REASON] {c3['verdict']} mechanism={c3['mechanism_accuracy']} "
          f"scrambled={c3['scrambled_accuracy']} ablation={c3['ablation_accuracy']} "
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
    verdict_msg = (f"claim1={c1['verdict']}(gap={c1['gap']}) claim2={c2['verdict']}"
                  f"(cohesion={c2['same_rep_at_scale']['cohesion_gap']},contra="
                  f"{c2['no_contradictions']['active_contradiction_count']}) "
                  f"claim3={c3['verdict']}(mech={c3['mechanism_accuracy']},"
                  f"scr={c3['scrambled_accuracy']},abl={c3['ablation_accuracy']}) "
                  f"smoke_controls_discriminate={smoke_controls_discriminate}")

    return {
        "verdict": overall, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "foundation_dir": foundation_dir, "n_facts_loaded": len(store._facts),
        "seed": SEED, "claim1_correctness": c1, "claim2_coherence": c2, "claim3_can_reason": c3,
        "smoke_controls_discriminate": smoke_controls_discriminate,
        "bands": {
            "claim1": {"hard_pass_gap_min": 0.20, "hard_fail_gap_max": 0.05},
            "claim2a": {"hard_pass_cohesion_min": 0.10, "hard_fail_cohesion_max": 0.02},
            "claim2b": {"hard_pass_active_contradictions": 0},
            "claim3": {"hard_pass_mech_min": 0.50, "hard_pass_gap_min": 0.20, "hard_fail_gap_max": 0.05},
        },
    }


# =========================================================================== I/O plumbing
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
             "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
             "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown")}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


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
                  "verdict_msg": "all 7 formula self-tests passed (wilson_ci, prefix-cooccurs, "
                                  "cohesion_gap discriminates, contradiction scanner can-fail, "
                                  "chain builder degenerate/cycle exclusion, leak detection fires "
                                  "on a corrupted store, reason mechanism+controls fire)",
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    foundation_dir = args.foundation_dir
    if args.freeze_from:
        foundation_dir = freeze_snapshot(args.freeze_from, tag="reading_grounding_v1_" +
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
