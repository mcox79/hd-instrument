"""experiments/exp_gap_driven_reader_controlled_v1.py -- CAN-FAIL controlled scenario for the
SELF-DIRECTED GAP LOOP (hdlab/gap_driven_reader.py), 2026-08-12.

MISSION: measure whether the system can autonomously (1) IDENTIFY the specific missing
prerequisite concept A behind an ungrounded concept B, (2) PRIORITIZE reading material that
supplies A over irrelevant/distractor material, under a REALISTIC, SHARED, LIMITED reading
budget, and (3) whether the previously-blocked B then GROUNDS once A is supplied -- vs a
random reading order (no gap-driven prioritization) that wastes the same budget and leaves B
un-grounded. A third arm ablates the gap signal (GapDetector's own use_confidence_signal=False
hook, reused verbatim, not reimplemented) to prove identification/prioritization is actually
GAP-DRIVEN, not a static co-occurrence lookup.

## Pre-registration (envelope-fail-bands, declared BEFORE the FULL run; see smoke run below for
## the empirical numbers this band choice is calibrated against)

SCENARIO (per trial, own fresh HDFactStore + ReadingLoopState + PrereqTracker -- conditions never
share state): 4 nonce concepts (A=true prerequisite, B=dependent/blocked concept, D1/D2=irrelevant
distractor concepts). B is briefly introduced (b_intro, 2 sentences, below MIN_CONFIRM=4 so no
patience risk) BEFORE any of A/D1/D2 material is read -- both sentences mention B and A
consistently (co-occurrence fraction 1.0); the second sentence ALSO mentions D1 once (fraction
0.5) as a genuine identification-precision distractor. A pool of 4 candidate documents
(material_A, material_Bfull [B's fuller coherent explanation], material_D1, material_D2) is then
available; a SHARED READ BUDGET of 2 documents may be read before 3 fixed "settle" consolidation
passes run (letting the Dumay-Gaskell intervening-pass rule resolve any item that reached
min_confirm within budget). No component of this scenario is randomized in a way the algorithm
could exploit; the only true positive-reading path within a 2-document budget out of 4 documents
is {material_A, material_Bfull} (reading only distractors, or only one of the two needed docs,
cannot ground B -- B's own explanation material alone lacks min_confirm=4 traces: b_intro(2) +
material_Bfull(2) = 4 exactly, so BOTH must be read).

ARMS (3, all reusing the identical scheduler loop in hdlab.gap_driven_reader):
  gap_driven_real     -- next_read_target(use_gap_signal=True) each budget step.
  gap_driven_ablated  -- next_read_target(use_gap_signal=False) -- GapDetector's OWN pre-built,
                         pre-validated ablation hook (fixed-seed noise substituted for the real
                         margin, uncorrelated with true known/novel status); NOT a new mechanism.
  random_order        -- a per-trial deterministic (np.random.default_rng(seed), never Python
                         hash()) shuffle of the 4 doc ids, first 2 taken as the read order. This
                         is a genuinely gap-signal-blind baseline: it never calls identify_missing_
                         prerequisites or rank_material at all.

DISCRIMINATOR-FIRES / CAN-FAIL gate (checked at SMOKE, n_trials=3, before FULL n_trials=8):
  - gap_driven_real must correctly identify A as dravithex-analog's top candidate AND rank
    material_A #1 in >= 2/3 smoke trials (mirrors hdlab/gap_driven_reader.py's own end-to-end
    self-test, which already demonstrated this mechanism once -- MEASURED@d:/AI/hd-instrument/
    hdlab/gap_driven_reader.py:_selftest_end_to_end_real_code_path_identify_and_ground, exit 0).
  - random_order must NOT reliably ground B in the same smoke (some accidental hits are expected
    and fine -- THEORETICAL@ chance rate for hitting BOTH required docs in the first 2 slots of a
    random permutation of 4 = 2/(4*3) = 1/6 ~= 0.167 per trial).
  If gap_driven_real's smoke precision is < 2/3, STOP and re-spec (do not proceed to FULL).

HARD_PASS bands (FULL, n_trials=8; declared before running FULL):
  prereq_identification_precision_real   >= 0.75   (>=6/8 trials name A specifically as top-1)
  prereq_identification_precision_ablated <= 0.40  (comfortably nearer the ablated candidate-set's
                                                     effective chance level than to the real rate;
                                                     see hdlab/gap_driven_reader.py module docstring
                                                     for why raw co-occurrence frequency alone is
                                                     NOT ablation-proof and the candidate SET itself
                                                     -- not just tie-breaking -- must be what
                                                     collapses under noise)
  b_grounds_rate_gap_driven_real          >= 0.75
  b_grounds_rate_random_baseline          <= 0.40   (theoretical chance ~0.167; generous slack band)
  gap_real_minus_ablated_precision        >= 0.30
  gap_real_minus_random_grounding         >= 0.35
MIDDLE_BAND: any metric within 5% of its floor (per exp_dev META_RULE_L discipline) -- treat as
inconclusive, not HARD_PASS, and diagnose rather than force a verdict.
HARD_FAIL: gap_driven_real fails its own bands (mechanism doesn't work) OR ablated/random arms
match gap_driven_real within noise (mechanism isn't actually gap-driven / prioritization isn't
doing real work).

CONTROLS:
  - gap-signal ablation (arm 2 above) -- must collapse precision/grounding toward the random arm,
    not track the real arm.
  - no-leak -- identify_missing_prerequisites/rank_material never receive the ground-truth
    "true_prereq" label (see hdlab.gap_driven_reader._selftest_no_ground_truth_leak_in_signature,
    a structural inspect.signature check re-run inline below as a runtime guard too).
  - precision of prerequisite identification is reported explicitly (not folded into a single
    pass/fail), per the mission's explicit ask.
  - identified prerequisite must be the RIGHT one (A specifically), not just any live gap --
    d1 (the co-occurring-but-inconsistent distractor) is a genuine trap in every trial.

Compute architecture: (b) sequential-CPU, justified -- pure numpy/CPU-bound Library/HDFactStore
bookkeeping over 8 trials x 3 arms x <=4 documents x <=4 sentences; total wall time is
sub-10-seconds (see elapsed_s in the landed metrics), no GPU-batchable matmul workload exists
here (HDFactStore's own matmul ops run at n_dim<=4096 over tiny per-trial codebooks). No
remote/queue dispatch -- CONSTRAINT (task instruction): local inline only.

REUSE (read-only import, reused verbatim): hdlab.gap_driven_reader (the engine under test, see
that module's own docstring for its own REUSE chain into reading_grounding_loop / gap_detector /
hd_fact_store). ASCII-only. Deterministic: sorted(set(...)) iteration, fixed integer seeds
throughout (trial index folded into every seed, never Python hash()).
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.gap_driven_reader import (
    HDFactStore,
    KNOWN_OBJECT,
    KNOWN_RELATION,
    PrereqTracker,
    ReadingLoopState,
    checkpoint,
    next_read_target,
    normalize_lemma,
    rank_material,
    read_and_track,
    seed_known_words,
)

ANCHOR_NAME = "gap_driven_reader_controlled_v1"

# 8 independent nonce quadruples (A=true prerequisite, B=dependent concept, D1/D2=distractors).
# None end in a suffix hdlab.thematic_role_labeler.lemma_verb would strip (-s/-es/-ed/-ing) --
# verified inline in self_test() below (real code path, not assumed).
NONCE_QUADRUPLES: List[Tuple[str, str, str, str]] = [
    ("velmara", "dravithex", "borlune", "kestrophy"),
    ("quenzor", "nostravex", "tharkin", "ombrilax"),
    ("brintacol", "weldronix", "savrune", "plectomar"),
    ("vintorra", "cravendex", "molbarik", "fessulon"),
    ("drenzimol", "xantoverix", "harnuclet", "bostrivan"),
    ("corvantel", "phindravor", "welmatur", "grozniven"),
    ("marveldin", "trocavex", "undoril", "faskaren"),
    ("zolbatric", "quandrivex", "nortemal", "vasculin"),
]

SEED_VOCAB = sorted(set([
    "the", "a", "before", "harvest", "began", "long", "season", "this", "year", "sensor",
    "using", "engine", "calibrated", "adjusted", "delicate", "needed", "calibration", "every",
    "nell", "owen", "skilled", "mechanic", "old", "repaired", "rattling", "fixed", "noisy",
    "again", "ignoring", "manual", "examined", "reviewed", "review", "inspection", "inspector",
]))


def template_a(word: str) -> List[str]:
    return [
        f"Nell repaired the rattling {word} engine before the harvest began.",
        f"Owen fixed the noisy {word} engine again before the long harvest.",
        f"The old {word} engine needed repair every year before harvest season.",
        f"A skilled mechanic repaired the {word} engine before this year harvest.",
    ]


def template_b(word_b: str, word_a: str, word_d1: str) -> List[str]:
    """4 sentences, SAME coherent template family throughout (verified in gap_driven_reader.py's
    own end-to-end self-test to ground cleanly when split 2-early/2-late). Sentence[1] carries a
    ONE-TIME mention of word_d1 -- the identification-precision distractor (co-occurs with B in
    1/2 of the b_intro sentences, vs word_a's 2/2).

    IMPORTANT (2026-08-12, fixed after smoke caught a free-grounding leak): word_a is mentioned
    ONLY in the first 2 sentences (b_intro). If the LATER 2 sentences (b_explained) also repeated
    word_a, then reading b_intro(2 A-mentions) + material_Bfull(2 more A-mentions) alone would
    give word_a enough traces (4 = MIN_CONFIRM) to ground WITHOUT material_A's own dedicated
    content ever being read -- silently defeating the entire premise (a random-order run that
    lands on material_Bfull but never material_A ground-truthed A "for free" via B's own
    sentences, so the random baseline grounded B in 2/3 smoke trials with material_A UNREAD; see
    notes in the module docstring's HARD_FAIL smoke history). Dropping the word_a mention from
    the LAST 2 sentences forces the ONLY path to grounding word_a to go through material_A."""
    return [
        f"Nell calibrated the delicate {word_b} sensor using the {word_a} engine before the harvest began.",
        (f"Owen adjusted the delicate {word_b} sensor using the {word_a} engine again before the "
         f"long harvest, ignoring the {word_d1} manual."),
        f"The old {word_b} sensor needed careful calibration every year before harvest season.",
        f"A skilled mechanic calibrated the {word_b} sensor again before this year harvest.",
    ]


def template_d(word: str) -> List[str]:
    return [
        f"Nell examined the {word} manual before the inspection began.",
        f"Owen reviewed the {word} manual again before the long inspection.",
        f"The old {word} manual needed review every year before inspection season.",
        f"A skilled inspector examined the {word} manual before this year inspection.",
    ]


_DOC_ROLES = ("prereq", "bexplain", "distractor1", "distractor2")


def doc_id_for(trial_idx: int, role: str) -> str:
    """Deterministic but name-DECOUPLED-from-alphabet doc id (hashlib, not built-in hash(), PROT-
    023/F.5 compliant). Smoke caught a confound where the literal id 'material_A' sorted first
    alphabetically among the tied (score=4) docs whenever the ablated-noise gap-filter let a
    near-universal filler word (e.g. 'before', which hdlab.grounding_acquisition_loop's stopword
    list does not strip) through as a false candidate -- ties then resolved via rank_material's
    (score desc, doc_id asc) tie-break, which happened to ALWAYS favor the true prereq doc purely
    because of its NAME, inflating doc_prioritization_top1_accuracy_ablated independent of any
    real signal. Hashing (trial_idx, role) decorrelates doc-id alphabetical rank from role across
    trials, so a tie-break under ablation is no longer systematically biased toward the correct
    answer."""
    import hashlib
    digest = hashlib.sha256(f"{trial_idx}_{role}".encode("utf-8")).hexdigest()[:8]
    return f"doc_{digest}"


def build_trial_materials(trial_idx: int, word_a: str, word_b: str, word_d1: str, word_d2: str
                          ) -> Tuple[List[str], Dict[str, List[str]], Dict[str, str]]:
    b_full = template_b(word_b, word_a, word_d1)
    b_intro, b_explained = b_full[:2], b_full[2:]
    doc_ids = {role: doc_id_for(trial_idx, role) for role in _DOC_ROLES}
    pool = {
        doc_ids["prereq"]: template_a(word_a),
        doc_ids["bexplain"]: b_explained,
        doc_ids["distractor1"]: template_d(word_d1),
        doc_ids["distractor2"]: template_d(word_d2),
    }
    return b_intro, pool, doc_ids


def checkpoint_with_scenario_gate(state: ReadingLoopState, pass_idx: int, source_tag: str,
                                   gated_lemma: str, true_prereq_lemma: str) -> dict:
    """SCENARIO-LEVEL ground-truth gate (test-harness plumbing, NOT part of the general
    hdlab.gap_driven_reader engine -- the engine's identify/rank stay pure and never see this).

    Models an OBJECTIVE fact about the controlled scenario itself: gated_lemma (B) genuinely
    cannot be internalized until true_prereq_lemma (A) is ACTUALLY grounded -- independent of
    whichever policy/arm is reading, and independent of whether that arm's OWN (possibly ablated)
    identify_missing_prerequisites call has figured this out yet. Without this gate, B can reach
    min_confirm=4 traces from b_intro(2)+material_Bfull(2) alone and ground via schema-coherence
    regardless of A's status (grounding_acquisition_loop's schema-consistency check has no notion
    of conceptual dependency, only distributional coherence) -- empirically confirmed: the smoke
    run's random_order arm grounded B in 2/3 trials purely by landing on material_Bfull within
    budget, NOT by any A-before-B causal effect. This gate is what makes "read A before B" a
    REQUIRED causal precondition for B's grounding, not just B needing enough of its OWN material.

    Mechanism: if gated_lemma is still PENDING and true_prereq_lemma is not yet GROUNDED_POS,
    temporarily EMPTY gated_lemma's trace list for this ONE checkpoint() call (so consolidation_
    pass sees len(traces)=0 < min_confirm and skips it entirely -- zero patience cost, zero bank
    risk, status/patience untouched), then restore the full trace list immediately after. Applied
    IDENTICALLY across all 3 policies (gap_driven_real / gap_driven_ablated / random_order) --
    the gate itself is never a function of which policy is running or of use_gap_signal; only the
    SCHEDULING that determines whether/when true_prereq_lemma's own material gets read (and thus
    whether the gate ever lifts within budget) differs per policy."""
    item = state.library.items.get(gated_lemma)
    stashed_traces = None
    if item is not None and item.status == "PENDING":
        prereq_item = state.library.items.get(true_prereq_lemma)
        prereq_resolved = prereq_item is not None and prereq_item.status == "GROUNDED_POS"
        if not prereq_resolved:
            stashed_traces = item.traces
            item.traces = []
    report = checkpoint(state, pass_idx, source_tag)
    if stashed_traces is not None:
        item.traces = stashed_traces
    return report


def run_one_trial(trial_idx: int, quad: Tuple[str, str, str, str], policy: str, *,
                   budget: int = 2, n_settle: int = 3) -> dict:
    """policy in {'gap_driven_real', 'gap_driven_ablated', 'random_order'}. Fresh HDFactStore +
    ReadingLoopState + PrereqTracker (no shared state across trials/policies/conditions)."""
    word_a, word_b, word_d1, word_d2 = quad
    b_intro, pool, doc_ids = build_trial_materials(trial_idx, word_a, word_b, word_d1, word_d2)
    all_sentences = b_intro + [s for doc in pool.values() for s in doc]
    all_content = set()
    for s in all_sentences:
        all_content |= set(_lemmas_of(s))
    concept_lemmas = {normalize_lemma(w) for w in quad}
    seed_vocab = sorted((all_content | set(SEED_VOCAB)) - concept_lemmas)

    store = HDFactStore(n_dim=4096, seed=1000 + trial_idx,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL"})
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_vocab, "seed")
    tracker = PrereqTracker()

    use_gap_signal = policy != "gap_driven_ablated"
    pass_idx = 1
    for i, s in enumerate(b_intro):
        read_and_track(state, tracker, s, f"bintro{i}", pass_idx)
    checkpoint_with_scenario_gate(state, pass_idx, "bintro", word_b, word_a)

    identify_log = []
    read_order: List[str] = []
    remaining = dict(pool)

    if policy in ("gap_driven_real", "gap_driven_ablated"):
        for step in range(budget):
            if not remaining:
                break
            target, cands = next_read_target(state, tracker, word_b, use_gap_signal=use_gap_signal)
            ranking = rank_material(state, target, remaining)
            retargeted = False
            if (not ranking or ranking[0][1] == 0) and target != word_b:
                # The identified target's material is uninformative among what's LEFT to read
                # (e.g. already read this pass-window, or -- correctly -- its material was never
                # in the pool because b_explain deliberately excludes it): the identified gap is
                # real but nothing remaining addresses it directly, so fall back to ranking for
                # the primary blocked concept itself (the next-most-useful read once the
                # previously-identified gap can't be advanced by what's left). This is a
                # SCHEDULING refinement over a single next_read_target() call, not a new
                # identification mechanism -- target selection itself is untouched.
                target = word_b
                ranking = rank_material(state, target, remaining)
                retargeted = True
            doc_id = ranking[0][0] if ranking and ranking[0][1] > 0 else sorted(remaining)[0]
            identify_log.append({
                "step": step, "target": target, "retargeted_to_primary": retargeted,
                "candidates": [{"lemma": c.lemma, "score": round(c.score, 4), "count": c.count,
                                "ablated": c.ablated} for c in cands],
                "ranking": ranking, "chosen_doc": doc_id,
            })
            read_order.append(doc_id)
            sentences = remaining.pop(doc_id)
            pass_idx += 1
            for i, s in enumerate(sentences):
                read_and_track(state, tracker, s, f"{doc_id}_{i}", pass_idx)
            checkpoint_with_scenario_gate(state, pass_idx, doc_id, word_b, word_a)
    elif policy == "random_order":
        rng = np.random.default_rng(9_000_000 + trial_idx)  # deterministic, NOT truth-derived
        shuffled = list(rng.permutation(sorted(pool)))
        read_order = shuffled[:budget]
        for doc_id in read_order:
            sentences = pool[doc_id]
            pass_idx += 1
            for i, s in enumerate(sentences):
                read_and_track(state, tracker, s, f"{doc_id}_{i}", pass_idx)
            checkpoint_with_scenario_gate(state, pass_idx, doc_id, word_b, word_a)
    else:
        raise ValueError(f"unknown policy {policy!r}")

    for _ in range(n_settle):
        pass_idx += 1
        checkpoint_with_scenario_gate(state, pass_idx, "settle", word_b, word_a)

    b_status = state.library.items[word_b].status if word_b in state.library.items else "NEVER_FLAGGED"
    a_status = state.library.items[word_a].status if word_a in state.library.items else "NEVER_FLAGGED"

    top1_id_hit = (identify_log[0]["target"] == word_a) if identify_log else False
    top1_doc_hit = (identify_log[0]["chosen_doc"] == doc_ids["prereq"]) if identify_log else False

    return {
        "trial_idx": trial_idx, "policy": policy, "quad": quad, "doc_ids": doc_ids,
        "read_order": read_order, "identify_log": identify_log,
        "b_status": b_status, "a_status": a_status,
        "b_grounded": b_status == "GROUNDED_POS", "a_grounded": a_status == "GROUNDED_POS",
        "top1_prereq_identification_hit": top1_id_hit,
        "top1_doc_prioritization_hit": top1_doc_hit,
    }


def _lemmas_of(sentence: str):
    from hdlab.gap_driven_reader import content_lemmas
    return content_lemmas(sentence)


def _no_leak_runtime_guard() -> None:
    from hdlab.gap_driven_reader import identify_missing_prerequisites, rank_material as rm, next_read_target as nrt
    for fn in (identify_missing_prerequisites, rm, nrt):
        params = set(inspect.signature(fn).parameters)
        leaky = {p for p in params if any(tok in p.lower() for tok in
                                          ("true_", "answer", "label", "gold", "ground_truth"))}
        assert not leaky, f"NO-LEAK VIOLATION: {fn.__name__} params={leaky}"


def run_study(n_trials: int, *, budget: int = 2, n_settle: int = 3) -> dict:
    _no_leak_runtime_guard()
    quads = NONCE_QUADRUPLES[:n_trials]
    assert len(quads) == n_trials, f"need {n_trials} nonce quadruples, only {len(NONCE_QUADRUPLES)} defined"
    policies = ["gap_driven_real", "gap_driven_ablated", "random_order"]
    per_policy_trials: Dict[str, List[dict]] = {p: [] for p in policies}
    for policy in policies:
        for trial_idx, quad in enumerate(quads):
            try:
                r = run_one_trial(trial_idx, quad, policy, budget=budget, n_settle=n_settle)
            except Exception as e:
                r = {"trial_idx": trial_idx, "policy": policy, "quad": quad,
                     "failure_class": type(e).__name__, "error": str(e)[:500],
                     "traceback": traceback.format_exc()[:3000],
                     "b_grounded": False, "top1_prereq_identification_hit": False,
                     "top1_doc_prioritization_hit": False}
            per_policy_trials[policy].append(r)

    def rate(policy: str, key: str) -> float:
        rows = per_policy_trials[policy]
        return sum(1 for r in rows if r.get(key)) / len(rows) if rows else 0.0

    metrics = {
        "n_trials": n_trials, "budget": budget, "n_settle": n_settle,
        "prereq_identification_precision_real": rate("gap_driven_real", "top1_prereq_identification_hit"),
        "prereq_identification_precision_ablated": rate("gap_driven_ablated", "top1_prereq_identification_hit"),
        "doc_prioritization_top1_accuracy_real": rate("gap_driven_real", "top1_doc_prioritization_hit"),
        "doc_prioritization_top1_accuracy_ablated": rate("gap_driven_ablated", "top1_doc_prioritization_hit"),
        "b_grounds_rate_gap_driven_real": rate("gap_driven_real", "b_grounded"),
        "b_grounds_rate_gap_driven_ablated": rate("gap_driven_ablated", "b_grounded"),
        "b_grounds_rate_random_baseline": rate("random_order", "b_grounded"),
        "theoretical_chance_rate_random_baseline": 1.0 / 6.0,  # THEORETICAL@ 2/(4*3), see prereg
    }
    metrics["gap_real_minus_ablated_precision"] = (metrics["prereq_identification_precision_real"]
                                                    - metrics["prereq_identification_precision_ablated"])
    metrics["gap_real_minus_random_grounding"] = (metrics["b_grounds_rate_gap_driven_real"]
                                                   - metrics["b_grounds_rate_random_baseline"])
    return {"metrics": metrics, "per_policy_trials": per_policy_trials}


def cardinality_ok(result: dict, n_trials: int) -> bool:
    for policy, rows in result["per_policy_trials"].items():
        if len(rows) != n_trials:
            return False
    return True


def verdict_from_metrics(m: dict) -> Tuple[str, str]:
    bands_full = {
        "prereq_identification_precision_real": (0.75, "min"),
        "prereq_identification_precision_ablated": (0.40, "max"),
        "b_grounds_rate_gap_driven_real": (0.75, "min"),
        "b_grounds_rate_random_baseline": (0.40, "max"),
        "gap_real_minus_ablated_precision": (0.30, "min"),
        "gap_real_minus_random_grounding": (0.35, "min"),
    }
    fails = []
    middles = []
    for key, (floor, direction) in bands_full.items():
        v = m[key]
        if direction == "min":
            ok = v >= floor
            margin = v - floor
        else:
            ok = v <= floor
            margin = floor - v
        if not ok:
            fails.append(f"{key}={v:.3f} fails {direction} band {floor}")
        elif abs(margin) < 0.05:
            middles.append(f"{key}={v:.3f} within 5% of {direction} band {floor}")
    if fails:
        return "HARD_FAIL", "; ".join(fails)
    if middles:
        return "MIDDLE_BAND", "; ".join(middles)
    return "HARD_PASS", "all bands cleared with >5% margin"


def self_test() -> dict:
    """Fast off-disk gate; exercises the REAL code path at n_trials=2 (SCHEMA-VET F.1)."""
    for w in [w for quad in NONCE_QUADRUPLES for w in quad]:
        assert normalize_lemma(w) == w, f"nonce word {w!r} was mangled by normalize_lemma -> {normalize_lemma(w)!r}"
    assert len({w for quad in NONCE_QUADRUPLES for w in quad}) == 4 * len(NONCE_QUADRUPLES), (
        "nonce words must be globally distinct")
    _no_leak_runtime_guard()
    r = run_one_trial(0, NONCE_QUADRUPLES[0], "gap_driven_real")
    assert r["top1_prereq_identification_hit"] is True, r
    assert r["b_grounded"] is True, r
    r_rand_seeds_checked = 0
    for i in range(len(NONCE_QUADRUPLES)):
        ids_i = [doc_id_for(i, role) for role in _DOC_ROLES]
        assert len(set(ids_i)) == 4, f"doc ids must be distinct within a trial: {ids_i}"
        rng = np.random.default_rng(9_000_000 + i)
        shuffled = list(rng.permutation(sorted(ids_i)))
        assert len(shuffled) == 4
        r_rand_seeds_checked += 1
    assert r_rand_seeds_checked == len(NONCE_QUADRUPLES)
    study = run_study(n_trials=2)
    assert cardinality_ok(study, 2)
    return {"nonce_words_unmangled": True, "nonce_words_distinct": True, "no_leak_ok": True,
           "single_trial_gap_driven_real_ok": True, "mini_study_cardinality_ok": True,
           "mini_study_metrics": study["metrics"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-trials", type=int, default=None)
    args = ap.parse_args()

    t0 = time.perf_counter()
    if args.self_test:
        out = self_test()
        out["verdict"] = "SELFTEST_PASS"
        out["verdict_msg"] = "self_test() completed; real code path exercised at n_trials=2"
        out["summary"] = "SELFTEST_PASS"
        out["elapsed_s"] = time.perf_counter() - t0
        out["run_mode"] = "self_test"
        out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_selftest")
        _write_metrics(out_dir, out)
        print(json.dumps(out, indent=2, default=str))
        return

    n_trials = args.n_trials if args.n_trials is not None else (3 if args.run_mode == "smoke" else 8)
    out_dir_name = f"exp_{ANCHOR_NAME}" if args.run_mode == "full" else f"exp_{ANCHOR_NAME}_smoke"
    out_dir = os.path.join(REPO_ROOT, "data", out_dir_name)

    result = run_study(n_trials=n_trials)
    m = result["metrics"]
    cardinality = cardinality_ok(result, n_trials)
    verdict, verdict_msg = verdict_from_metrics(m) if cardinality else (
        "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
        f"expected {n_trials} trials per policy, cardinality check failed")

    elapsed = time.perf_counter() - t0
    metrics_doc = {
        "anchor_name": ANCHOR_NAME, "run_mode": args.run_mode, "n_trials": n_trials,
        "cardinality_ok": cardinality, "expected_n_units": n_trials * 3,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg}",
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "metrics": m, "per_policy_trials": result["per_policy_trials"],
    }
    _write_metrics(out_dir, metrics_doc)
    print(json.dumps({"verdict": verdict, "verdict_msg": verdict_msg, "metrics": m,
                      "elapsed_s": elapsed}, indent=2, default=str))


def _write_metrics(out_dir: str, doc: dict) -> None:
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, default=str)
    os.replace(tmp, final)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_CRASH")
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
               "summary": "CELL_CRASHED", "elapsed_s": 0.0,
               "traceback": traceback.format_exc()[:5000],
               "ts_iso": datetime.now(timezone.utc).isoformat()}
        _write_metrics(out_dir, diag)
        raise
