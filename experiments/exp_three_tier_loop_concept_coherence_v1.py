# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - 2026-08-11 CONTROL FIX: W_scramble now ALSO corrupts CONCEPT CONTENT (scramble_wave_content),
#   not just cross-source KG links (root cause of the disclosed scramble_collapses=False leak);
#   NEW arm W_mechanism_isolation isolates concept-content-only corruption on exactly the pks that
#   recovered under W_concept -- the decisive "is the win real" control. See module docstring ARMS.
# - arms_differ_verified: W_baseline vs W_concept asserted; W_concept vs R_reference asserted;
#   W_concept vs W_scramble asserted or exempted-by-construction if scrambled population collapses
#   to the same size class; W_concept vs W_mechanism_isolation asserted or exempted-by-construction
#   if the mechanism-isolation population collapses to the same size class
# - final_metrics_atomicity = tmp_replace (single-shot)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: discrete matched/unmatched in-lexicon-word-fraction gate, not a Gaussian noise-floor
#   metric; discriminator_reachability=TRUE proven closed-form (real paraphrase / cross-domain /
#   wrong-material pairs) AND via real-pipeline control checks in self-test, not just hand-computed
# - baseline_in_band: N/A (this cell swaps a coherence METRIC inside an existing gate; the
#   underlying independence-weighted count gate's own baseline behavior is unchanged, verified via
#   W_baseline reproducing the parent cell's own W_full)
# - discriminator survives scale: smoke gate checks the closed-form + real-pipeline control checks
#   fire correctly on synthetic fixtures (scale-independent) BEFORE FULL dispatch
# - HP_SCOPE: HARD_PASS/HARD_FAIL gates apply to the concept-coherence metric's own discrimination
#   property (paraphrase-vs-distinct-fact) + the end-to-end W_concept retain rate on the real
#   blocked-gap population; R_reference carries its own single reproduces_prior gate
# - cardinality_ok: EXPECTED checkpoints = n_waves for W_baseline/W_concept/W_scramble/
#   W_mechanism_isolation, VISITS_PER_GAP(6, or VISITS_PER_GAP_SMOKE at smoke) for R_reference
# - per-unit failure-class instrumentation: N/A (single deterministic pass per arm, 4 arms + 2
#   closed-form audits + 1 control-check block)
# - calibration_check: default_ok_for_this_regime (CONCEPT_MATCH_THRESHOLD reused verbatim from
#   hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD, an independently pre-registered constant,
#   never tuned by this cell; schema_thresh left at the codebase default 0.10, unchanged)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL KGStore/HDFactStore/Library/TierState/ScriptLibrary/RelationRegister/
#   ThreeTierLoop objects (via the reused source cells' own self-tests) PLUS new fixtures isolating
#   the concept-coherence metric's own boundary (real_code_path)
# - substrate_signature_checked: KGStore/HDFactStore/ThreeTierLoop/TierState base kwargs only; the
#   organ extension (coherence_fn on consolidation_pass / update_prelim_and_generalize /
#   schema_consistency_split_half) is an ADDITIVE kwonly param with a default that preserves prior
#   behavior byte-for-byte -- verified via the reused organs' own self-tests
#   (hdlab/grounding_acquisition_loop.py, hdlab/prelim_tier.py) passing unchanged after the edit
"""exp_three_tier_loop_concept_coherence_v1 -- tests the BRAIN-FOUNDATIONAL fix for the SECOND
floor honestly disclosed by exp_three_tier_loop_independence_weighted_confirm_v1 (commit
62dafbc08, HARD_PASS): that cell solved the count gate (independence-weighted confirmation score
correctly separates genuine 2-3-source corroboration from N repeats of one source), but
MEASURED@data/exp_three_tier_loop_independence_weighted_confirm_v1/metrics.json: only 15 of 36
real 2+-source-eligible gaps (closed_form_audit.by_source_count 2+3 buckets, all 36 crossing the
count gate) actually retain end-to-end -- 21 gaps cross the count gate and then get blocked by a
SEPARATE schema-coherence check (hdlab.grounding_acquisition_loop.schema_consistency_split_half)
that compares two halves' accumulated context vectors by raw cosine of a bag-of-random-hash-words
bundle. Root cause (measured during that cell's authoring, reproduced and extended here): CSKG-
style and KB-role-schema-style source text for the SAME gap share few surface words (cos=0.039 <
schema_thresh=0.10) because each source's template mentions a DIFFERENT subset of the gap's
entities, diluted by source-specific boilerplate -- the SAME fact, worded differently, fails a
literal-surface-overlap check.

THE FIX: replace the surface-TEXT-overlap coherence check with the OWNED graded
hdlab.lexical_similarity.concept_similarity organ (the ATL amodal-concept-hub analog, McRae-style
shared-feature lexicon, HARD_PASS at commit 7d0a574b4, EXTENDED 2026-08-10 with exactly this
ProPara process-physics vocabulary) so two traces are judged coherent by MEANING, not by which
random-hash boilerplate words happen to literally match. See preregs/2026-08-11_three_tier_loop_
concept_coherence_v1.md for the full design (metric definition, authoring-time empirical
validation, arms, pre-registered bands, schema-vet declarations).

DESIGN (see pre-reg for the full derivation): concept_coherence_score(traces_a, traces_b,
episode_text) pools each half's raw source text, keeps ONLY words IN hdlab.lexical_similarity.
CONCEPT_FEATURES (drops source-provenance boilerplate), then scores the fraction of pooled
in-lexicon words that find a match (literal equality OR concept_similarity >= CONCEPT_MATCH_
THRESHOLD) on the other side. CONCEPT_MATCH_THRESHOLD = hdlab.lexical_similarity.
SIMILARITY_LINK_THRESHOLD = 0.50, REUSED VERBATIM (not re-tuned by this cell) -- binarizing at
this ALREADY-validated near-synonym bar is what keeps a same-role-different-specific-material pair
(e.g. "wood" vs "coal", concept_similarity=0.450 MEASURED, both COMBUSTION_CONSUME_ROLE) from
being treated as "the same fact": an earlier un-binarized average-cosine design scored that pair
0.45 (ABOVE schema_thresh=0.10), which would have been exactly the "merges everything" failure
mode this cell's mandatory NEG controls exist to catch. schema_thresh is LEFT AT THE CODEBASE
DEFAULT (0.10, unchanged) -- not tuned down to force a pass.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim; NONE modified
by this cell EXCEPT the additive, backward-compatible coherence_fn kwonly-parameter extension
named above):
  hdlab.three_tier_loop.ThreeTierLoop / gap_item_key / parse_gap_item_key
  hdlab.grounding_acquisition_loop.Library / Trace / consolidation_pass / context_vector /
    content_words / MIN_CONFIRM / PROMOTE_MIN_EXPOSURE / PROMOTE_MIN_CONSISTENCY /
    schema_consistency_split_half
  hdlab.prelim_tier.TierState / update_prelim_and_generalize / CLUSTER_MIN_MEMBERS /
    CLUSTER_EXPOSURE_MULTIPLIER
  hdlab.hd_fact_store.HDFactStore / ACTIVE_STATUSES
  hdlab.script_grain_acquisition_loop.calibrate_novelty_threshold / build_instance_register
  hdlab.gather_reason.ca3_relevance_gather / fanout_two_hop / recovery_at / real_to_concat
  hdlab.situation_model_accumulate.RelationRegister / unit_phase_vec
  hdlab.kg_traversal.KGStore
  hdlab.lexical_similarity.concept_similarity / in_lexicon / SIMILARITY_LINK_THRESHOLD
  experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1's own build functions
  experiments.exp_three_tier_loop_real_corpus_gap_stream_v1's own functions (pk_of,
    cluster_key_fn, my_gap_register_fn, _eligible_targets, _positive_control_reproduction,
    run_arm, VISITS_PER_GAP, VISITS_PER_GAP_SMOKE, K1_FANOUT, K2_FANOUT, CA3_K_PEEL, CA3_SIM_FLOOR,
    FHRR_D, FOUND_DIM, RELATION, SEED_KG_HOP1, SEED_KG_HOP2, SEED_SCRAMBLE, SEED_FHRR)
  experiments.exp_three_tier_loop_genuine_cross_source_corroboration_v1's own functions
    (pk_of_genuine, build_genuine_waves, compute_cskg_extra, compute_causenet_pairs,
    compute_kb_role_hits, compute_go_literal_hits, compute_novelty_thresh)
  experiments.exp_three_tier_loop_independence_weighted_confirm_v1's own definitions
    (SOURCE_INDEPENDENCE_CLASS, W_INDEPENDENT, REPEAT_DECAY, CORRELATED_WEIGHT,
    INDEPENDENCE_MIN_CONFIRM, independence_weighted_trace_score) -- the count-gate fix, UNCHANGED
    by this cell; this cell's ONLY new axis is the schema-COHERENCE metric.

THE ONE NEW THING (honestly disclosed): (a) the additive coherence_fn organ extension named above;
(b) concept_coherence_score + CONCEPT_MATCH_THRESHOLD (this cell owns the definition of what
counts as a "concept match" -- the organs stay generic, they know nothing about words); (c)
run_concept_arm, a thin generalization of the independence-weighted-confirm cell's own
run_weighted_arm (threading coherence_fn + per-arm episode_text + per-checkpoint resolved-pk-set
tracking, for the exact blocked-gap diff); (d) closed_form_schema_audit (per-real-gap OLD-vs-NEW
coherence-verdict table, no pipeline needed); (e) run_concept_control_checks (closed-form
paraphrase/cross-domain/wrong-material probes PLUS real-pipeline POS/NEG probes via the actual
WIRED gate).

ARMS: W_baseline (independence-weighted gate, OLD raw-cosine coherence -- reproduces the parent
cell's own W_full inside this cell for an exact per-gap diff) / W_concept (same gate, NEW
concept-similarity coherence -- the headline arm) / W_scramble (2026-08-11 FIXED: W_concept wiring,
scrambled hop2 eligibility AND scrambled CONCEPT CONTENT via scramble_wave_content -- ISOLATION 1,
must collapse to ~0 retention) / W_mechanism_isolation (2026-08-11 NEW, the decisive control: REAL
unscrambled eligibility, restricted to exactly the pks that recovered under W_concept, concept
content ONLY scrambled -- ISOLATION 2, the 21/21 recovery must COLLAPSE if the win is genuine
concept-meaning alignment and not pipeline artifact) / R_reference (POSITIVE CONTROL: byte-identical
reproduction of the landed A_full arm via VISITS_PER_GAP=6 templated repeats and the UNWEIGHTED
default gate, imported verbatim -- proves this cell's own plumbing is correct and the count-gate fix
is untouched).

Modes: --self-test (source cells' own fixtures + new concept-coherence-boundary fixtures, <10s) /
--smoke (real pipeline, 2-process subset, CauseNet scan skipped -> 2-wave ceiling) / (no flag,
default) = FULL (real pipeline, all real processes/targets, 3-wave ceiling, CauseNet scan
included).

ASCII-only. Deterministic throughout (sorted(set()) discipline; fixed integer seeds; no built-in
hash() anywhere -- PROT-023/F.5 compliant; concept_coherence_score sorts/pools words
deterministically, never depends on dict-iteration order for its own float result beyond Python's
stable insertion-ordered dict, itself fed by a deterministic wave-construction loop).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import functools
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch

ANCHOR_NAME = "three_tier_loop_concept_coherence_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec  # noqa: E402
from hdlab.gather_reason import ca3_relevance_gather, fanout_two_hop, recovery_at, real_to_concat  # noqa: E402
from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, Trace, consolidation_pass, context_vector, content_words, MIN_CONFIRM,
    PROMOTE_MIN_EXPOSURE, PROMOTE_MIN_CONSISTENCY, schema_consistency_split_half,
)
from hdlab.prelim_tier import (  # noqa: E402
    TierState, update_prelim_and_generalize, CLUSTER_MIN_MEMBERS, CLUSTER_EXPOSURE_MULTIPLIER,
)
from hdlab.hd_fact_store import HDFactStore, ACTIVE_STATUSES  # noqa: E402
from hdlab.script_grain_acquisition_loop import calibrate_novelty_threshold, build_instance_register  # noqa: E402
from hdlab.lexical_similarity import concept_similarity, in_lexicon, SIMILARITY_LINK_THRESHOLD  # noqa: E402
import hdlab.three_tier_loop as ttl  # noqa: E402
from experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1 import (  # noqa: E402
    build_reading_facts, reading_vocab, build_cskg_bridges, build_gap_set, build_entity_index,
    fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook, scramble_edges,
)
from experiments.exp_three_tier_loop_real_corpus_gap_stream_v1 import (  # noqa: E402
    pk_of, cluster_key_fn, my_gap_register_fn, _eligible_targets, _positive_control_reproduction,
    run_arm, VISITS_PER_GAP, VISITS_PER_GAP_SMOKE, K1_FANOUT, K2_FANOUT, CA3_K_PEEL, CA3_SIM_FLOOR,
    FHRR_D, FOUND_DIM, RELATION, SEED_KG_HOP1, SEED_KG_HOP2, SEED_SCRAMBLE, SEED_FHRR,
)
from experiments.exp_three_tier_loop_genuine_cross_source_corroboration_v1 import (  # noqa: E402
    pk_of_genuine, build_genuine_waves, compute_cskg_extra, compute_causenet_pairs,
    compute_kb_role_hits, compute_go_literal_hits, compute_novelty_thresh,
)
from experiments.exp_three_tier_loop_independence_weighted_confirm_v1 import (  # noqa: E402
    SOURCE_INDEPENDENCE_CLASS, W_INDEPENDENT, REPEAT_DECAY, CORRELATED_WEIGHT,
    INDEPENDENCE_MIN_CONFIRM, independence_weighted_trace_score,
)

# ---- concept-similarity-based coherence metric (THIS CELL's own definition; the organs stay
# generic; they know nothing about words or concepts) ----
CONCEPT_MATCH_THRESHOLD = SIMILARITY_LINK_THRESHOLD  # = 0.50, REUSED VERBATIM (not re-tuned here)
SCHEMA_THRESH = 0.10  # codebase default (grounding_acquisition_loop / prelim_tier), unchanged

# ---- 2026-08-11 CONTROL FIX: the disclosed HARD_FAIL_controls_broken (scramble_collapses=False,
# 2 entries leaked, igneous_rock_cycle||lava||lava_lake being one GENUINE fact) traced to the fact
# that the ORIGINAL W_scramble only permutes cross-source KG BRIDGE LINKS (used to recompute
# eligibility -- fanout_two_hop over hop2_scrambled), leaving every gap's real wave TEXT (the thing
# concept_coherence_score actually reads) fully intact. A gap that remains eligible by chance under
# scrambled links still carries its own genuine, unscrambled evidence -- so it can legitimately
# cohere and retain, which is not a leak of the MECHANISM under test, just an incomplete control.
# MECH_ISO_COLLAPSE_BAND: pre-registered BEFORE running the fixed cells below. The domain's
# concept vocabulary is small and recycled across gaps (energy/light/water/rain/rock/moon appear
# in MANY unrelated (process,material,whole) triples), so pure-chance cross-wiring under
# scramble_wave_content could occasionally reproduce an accidental shared-word match even between
# two truly-unrelated gaps. HYPOTHESIZED (not measured): allow up to ~3/21 (14%) survivors as
# chance-collision noise before calling the recovery genuinely "not collapsed" -- chosen to require
# a decisive supermajority collapse while not being falsely triggered by ordinary base-rate noise;
# NOT tuned post-hoc against the actual measured result.
MECH_ISO_COLLAPSE_BAND = 0.15


def _in_lexicon_words(text: str) -> List[str]:
    """Content words of `text` that are IN hdlab.lexical_similarity.CONCEPT_FEATURES, sorted +
    de-duplicated (deterministic). Drops source-provenance boilerplate (never a scientific-domain
    concept) and any OOV entity name (e.g. synthetic 'whole' items like 'cotton_candy'/'pepsi') --
    conservative: only words this cell CAN judge by meaning ever contribute to the score."""
    return sorted({w for w in content_words(text) if in_lexicon(w)})


def _has_concept_match(word: str, others: List[str]) -> bool:
    """True iff `word` literally equals some word in `others`, OR concept_similarity(word, other)
    >= CONCEPT_MATCH_THRESHOLD for some other in `others`. Binarized (not averaged) at the
    ALREADY-validated near-synonym bar -- see module docstring "wood vs coal" measured example for
    why binarizing (not averaging raw cosine) is load-bearing for the wrong-material can-fail
    control."""
    for o in others:
        if o == word:
            return True
    for o in others:
        s = concept_similarity(word, o)
        if s is not None and s >= CONCEPT_MATCH_THRESHOLD:
            return True
    return False


def concept_coherence_score(traces_a: List["Trace"], traces_b: List["Trace"],
                            episode_text: Dict[str, str]) -> float:
    """The graded, meaning-based coherence metric this cell substitutes for schema_consistency_
    split_half's default raw-context-vec cosine, via that function's additive coherence_fn hook.
    Pools each half's raw source text (looked up by episode_id in the caller-supplied
    episode_text side-table -- Trace itself is untouched, no organ-level schema change), keeps
    only in-lexicon words, scores the fraction with a concept match on the other side. Returns 0.0
    (conservative deny, not None -- the None/defer semantics belong to the n<2*min_half_size gate
    one level up in schema_consistency_split_half) if either half has zero in-lexicon words."""
    text_a = " ".join(episode_text.get(t.episode_id, "") for t in traces_a)
    text_b = " ".join(episode_text.get(t.episode_id, "") for t in traces_b)
    words_a = _in_lexicon_words(text_a)
    words_b = _in_lexicon_words(text_b)
    if not words_a or not words_b:
        return 0.0
    matches = [1.0 if _has_concept_match(w, words_b) else 0.0 for w in words_a]
    matches += [1.0 if _has_concept_match(w, words_a) else 0.0 for w in words_b]
    return sum(matches) / len(matches)


def scramble_wave_content(waves_by_pk: Dict[str, List[Tuple[int, str, str]]], seed: int
                          ) -> Tuple[Dict[str, List[Tuple[int, str, str]]], Dict]:
    """THE FIX (2026-08-11): corrupts the CONCEPT CONTENT (raw text) that concept_coherence_score
    actually reads, while leaving the structural WIRING -- which (wave_idx, source_tag) slots each
    gap has, hence eligibility/cardinality/independence-class tagging via source_tag (see
    exp_three_tier_loop_independence_weighted_confirm_v1._source_tag_of, which parses source_tag
    from episode_id, itself built from source_tag not text) -- completely UNTOUCHED.

    Groups every (pk, text) pair by its (wave_idx, source_tag) category [0=cskg, 1=causenet,
    2=kb_role_schema -- these are grammatically-identical sibling texts across gaps, differing only
    in which entities they name]. WITHIN each category, further groups pks by their DISTINCT TEXT
    CONTENT (not raw pk identity) -- MANDATORY, not cosmetic: several real source templates name
    fewer than all of (process, material, whole), so multiple DIFFERENT pks legitimately produce
    BYTE-IDENTICAL text (e.g. kb_role_schema's "ProPara ... lists {m} ... for process {p}." never
    mentions `whole`, so every gap sharing (process, material) -- e.g.
    photosynthesis||sugar||cotton_candy and photosynthesis||sugar||jelly_beans -- has identical
    kb_role_schema text; causenet's process_material hits have the same property). A derangement
    over raw PK POSITIONS can accidentally reassign a pk to a content-identical sibling: nominally
    a "different pk" but ZERO actual concept-content corruption for that entry. MEASURED (2026-08-11,
    first cut of this function): this exact residual let 8/21 real mechanism-isolation-population
    gaps survive scrambling by riding on a sibling's byte-identical text -- not a leak in the
    concept-coherence mechanism, a leak in this control. FIX: derange the SORTED LIST OF DISTINCT
    TEXTS (not pks) via a cyclic rotation by a nonzero offset drawn from a seeded
    np.random.default_rng, then broadcast each rotated text to every pk that shared the
    corresponding original group -- guarantees EVERY pk (whichever content-group it started in)
    ends up with text from a DIFFERENT content-group, with zero possibility of an accidental
    same-content self-match, however many pks share a template. A cyclic rotation by k in [1, n-1]
    over n >= 2 DISTINCT texts is a derangement (zero fixed points) by construction. Categories with
    < 2 distinct texts (nothing content-different to derange against) are left uncorrupted and
    counted in the returned diagnostic so the caller can audit true coverage -- never silently
    assumed corrupted."""
    by_category: Dict[Tuple[int, str], List[str]] = {}
    orig_text: Dict[Tuple[str, int, str], str] = {}
    for pk, gw in waves_by_pk.items():
        for (w, tag, text) in gw:
            by_category.setdefault((w, tag), []).append(pk)
            orig_text[(pk, w, tag)] = text
    for key in by_category:
        by_category[key] = sorted(set(by_category[key]))

    rng = np.random.default_rng(seed)
    rotation_offsets: Dict[str, int] = {}
    scrambled_text: Dict[Tuple[str, int, str], str] = {}
    n_categories_deranged = 0
    n_categories_too_small = 0
    n_content_groups_total = 0
    for key in sorted(by_category.keys()):
        pks_sorted = by_category[key]
        w, tag = key
        content_groups: Dict[str, List[str]] = {}
        for pk in pks_sorted:
            content_groups.setdefault(orig_text[(pk, w, tag)], []).append(pk)
        distinct_texts = sorted(content_groups.keys())
        n_content_groups_total += len(distinct_texts)
        n = len(distinct_texts)
        if n < 2:
            n_categories_too_small += 1
            for pk in pks_sorted:
                scrambled_text[(pk, w, tag)] = orig_text[(pk, w, tag)]  # nothing content-different to derange against
            continue
        offset = int(rng.integers(1, n))  # in [1, n-1] -- rotation by nonzero offset = derangement
        rotation_offsets[f"{w}:{tag}"] = offset
        n_categories_deranged += 1
        rotated_texts = distinct_texts[offset:] + distinct_texts[:offset]
        for group_text, new_text in zip(distinct_texts, rotated_texts):
            for pk in content_groups[group_text]:
                scrambled_text[(pk, w, tag)] = new_text

    deranged_categories = set(rotation_offsets.keys())
    out: Dict[str, List[Tuple[int, str, str]]] = {}
    n_entries_changed = 0
    n_entries_total = 0
    for pk, gw in waves_by_pk.items():
        new_gw = []
        for (w, tag, text) in gw:
            new_text = scrambled_text[(pk, w, tag)]
            n_entries_total += 1
            if new_text != text:
                n_entries_changed += 1
            elif f"{w}:{tag}" in deranged_categories:
                # a category we DID derange must never leave any entry byte-identical -- the
                # content-group derangement guarantees this; a violation here is a real bug in
                # the grouping/rotation logic above, not tolerable chance-collision (raise loud,
                # never silently continue, per the no-silent-except / fail-loud discipline).
                raise AssertionError(
                    f"scramble_wave_content BUG: category {w}:{tag} was deranged but pk={pk!r} "
                    f"kept byte-identical text after content-group rotation -- grouping invariant "
                    f"violated")
            new_gw.append((w, tag, new_text))
        out[pk] = new_gw
    diag = {"n_categories_deranged": n_categories_deranged, "n_categories_too_small": n_categories_too_small,
           "n_content_groups_total": n_content_groups_total,
           "rotation_offsets": rotation_offsets, "n_entries_total": n_entries_total,
           "n_entries_changed": n_entries_changed,
           "n_entries_unchanged": n_entries_total - n_entries_changed}
    return out, diag


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


# =========================================================================== arm runner
def run_concept_arm(arm_name: str, eligible_targets: List[Dict],
                    waves_by_pk: Dict[str, List[Tuple[int, str, str]]], n_waves: int,
                    novelty_thresh: float, found_seed: int, tier_seed: int,
                    use_concept_coherence: bool,
                    register_fn: Callable[[str, str, str], torch.Tensor] = my_gap_register_fn) -> Dict:
    """Thin generalization of the independence-weighted-confirm cell's own run_weighted_arm:
    IDENTICAL independence-weighted count gate (min_confirm=INDEPENDENCE_MIN_CONFIRM,
    trace_weight_fn=independence_weighted_trace_score, schema_min_half_size=1, all imported
    verbatim, UNCHANGED by this cell) -- the ONLY new axis is use_concept_coherence, which selects
    coherence_fn=concept_coherence_fn (bound to THIS arm's own fresh episode_text side-table) vs
    coherence_fn=None (the OLD raw-cosine metric, for W_baseline's exact reproduction of the
    parent cell's own W_full). Each checkpoint also records the FULL resolved-pk set (not just a
    count) so the caller can diff W_baseline vs W_concept at the individual-gap level -- the
    authoritative source for 'how many of the blocked gaps now retain'."""
    eligible_sorted = sorted(eligible_targets, key=lambda t: (t["process"], t["via_material"], t["fate"], t["whole"]))
    pks = [pk_of_genuine(t) for t in eligible_sorted]

    foundation_store = HDFactStore(n_dim=FOUND_DIM, seed=found_seed, use_index=True)
    no_leak_ok = all(foundation_store.query(pk, RELATION) == [] for pk in pks)

    loop = ttl.ThreeTierLoop(foundation_store, seed_base=tier_seed, n_dim=FOUND_DIM, relation=RELATION)
    episode_text: Dict[str, str] = {}
    coherence_fn = functools.partial(concept_coherence_score, episode_text=episode_text) if use_concept_coherence else None
    gate_kwargs = {"register": False, "min_confirm": INDEPENDENCE_MIN_CONFIRM,
                   "trace_weight_fn": independence_weighted_trace_score, "schema_min_half_size": 1,
                   "coherence_fn": coherence_fn}
    middle_kwargs = {"min_confirm": INDEPENDENCE_MIN_CONFIRM,
                     "trace_weight_fn": independence_weighted_trace_score, "schema_min_half_size": 1,
                     "coherence_fn": coherence_fn}

    checkpoints: List[Dict] = []
    for wave in range(n_waves):
        for t in eligible_sorted:
            pk = pk_of_genuine(t)
            gw = waves_by_pk.get(pk, [])
            match = next((g for g in gw if g[0] == wave), None)
            if match is None:
                continue
            _, source_tag, text = match
            cvec = context_vector(text)
            episode_id = f"{pk}|{source_tag}|w{wave}"
            episode_text[episode_id] = text
            loop.encounter(pk, "POS", cvec, episode_id, pass_idx=wave, also_strict=True)
        cp = wave + 1
        step = loop.consolidate(cp, cluster_key_fn, novelty_thresh, register_fn=register_fn,
                                gate_kwargs=gate_kwargs, middle_kwargs=middle_kwargs)
        gate_report, middle_report = step["gate"], step["middle"]
        n_found = 0
        n_mid = 0
        resolved_pks_now: List[str] = []
        for pk in pks:
            fh = foundation_store.query(pk, RELATION)
            if fh and fh[0]["status"] in ACTIVE_STATUSES:
                n_found += 1
                resolved_pks_now.append(pk)
                continue
            mh = loop.tier_state.prelim_store.query(pk, RELATION)
            if mh and mh[0]["status"] in ACTIVE_STATUSES:
                n_mid += 1
                resolved_pks_now.append(pk)
        checkpoints.append({
            "checkpoint": cp, "n_foundation": n_found, "n_middle": n_mid,
            "n_total_resolved": n_found + n_mid,
            "n_combined_promoted_this_pass": middle_report.get("n_combined_promoted_this_pass", 0),
            "n_clusters_eligible_size": middle_report.get("n_clusters_eligible_size", 0),
            "n_newly_retained_this_pass": middle_report.get("newly_retained", 0),
            "n_banked_pos_this_pass": len(gate_report.get("newly_grounded_pos", [])),
            "resolved_pks": sorted(resolved_pks_now),
        })

    final = checkpoints[-1] if checkpoints else {"n_foundation": 0, "n_middle": 0, "n_total_resolved": 0, "resolved_pks": []}
    return {
        "arm_name": arm_name, "n_targets": len(eligible_targets), "n_eligible": len(eligible_sorted),
        "no_leak_ok": bool(no_leak_ok), "checkpoints": checkpoints, "final": final,
        "use_concept_coherence": use_concept_coherence,
    }


# =========================================================================== closed-form schema audit
def closed_form_schema_audit(eligible_targets: List[Dict],
                             waves_by_pk: Dict[str, List[Tuple[int, str, str]]]) -> Dict:
    """For every real eligible gap with >=2 real sources, scores its ACTUAL wave texts under BOTH
    the OLD (raw-cosine) and NEW (concept-similarity) coherence metric directly via
    schema_consistency_split_half -- no ThreeTierLoop/TierState pipeline needed. The fastest, most
    direct per-gap answer to 'does the fix change the coherence VERDICT for this real gap,' and
    the source of n_regressed (any gap that crossed under the OLD metric and does not under the
    NEW one -- must be 0 or explained)."""
    rows: List[Dict] = []
    for t in eligible_targets:
        pk = pk_of_genuine(t)
        gw = waves_by_pk.get(pk, [])
        if len(gw) < 2:
            continue
        episode_text: Dict[str, str] = {}
        traces: List[Trace] = []
        for (w, tag, text) in gw:
            eid = f"{pk}|{tag}|w{w}"
            episode_text[eid] = text
            traces.append(Trace(eid, "POS", context_vector(text), w))
        old_score = schema_consistency_split_half(traces, min_half_size=1, coherence_fn=None)
        new_score = schema_consistency_split_half(
            traces, min_half_size=1,
            coherence_fn=functools.partial(concept_coherence_score, episode_text=episode_text))
        old_crosses = old_score is not None and old_score >= SCHEMA_THRESH
        new_crosses = new_score is not None and new_score >= SCHEMA_THRESH
        rows.append({"pk": pk, "n_sources": len(gw),
                     "old_score": round(old_score, 4) if old_score is not None else None,
                     "new_score": round(new_score, 4) if new_score is not None else None,
                     "old_crosses": old_crosses, "new_crosses": new_crosses})
    n_old_cross = sum(1 for r in rows if r["old_crosses"])
    n_new_cross = sum(1 for r in rows if r["new_crosses"])
    n_newly_crossing = sum(1 for r in rows if r["new_crosses"] and not r["old_crosses"])
    n_regressed = sum(1 for r in rows if r["old_crosses"] and not r["new_crosses"])
    return {"rows": rows, "n_gaps_2plus": len(rows), "n_old_cross": n_old_cross,
           "n_new_cross": n_new_cross, "n_newly_crossing": n_newly_crossing,
           "n_regressed": n_regressed}


# =========================================================================== control checks
# Fixed synthetic probe texts (constructed, not real-pipeline gap text; matches the module template
# CONVENTION exactly -- see build_genuine_waves -- so the mechanism is exercised honestly).
_PARA_CSKG = ("CSKG external knowledge base records that cotton_candy bridges to sugar via "
             "relation(s) ['/r/MadeOf'].")
_PARA_KB = "ProPara process physics KB lists sugar among ['produces'] terms for process photosynthesis."
_NEG_CSKG = "CSKG external knowledge base records that ash bridges to wood via relation(s) ['/r/MadeOf']."
_NEG_KB = "ProPara process physics KB lists water among ['produces'] terms for process photosynthesis."
_WRONGMAT_CSKG = ("CSKG external knowledge base records that campfire bridges to wood via "
                  "relation(s) ['/r/MadeOf'].")
_WRONGMAT_KB = "ProPara process physics KB lists coal among ['consumes'] terms for process combustion."


def run_concept_control_checks() -> Dict:
    """(1) Closed-form (word-list-only, no pipeline): the real paraphrase pair scores >=
    SCHEMA_THRESH under the NEW metric and < SCHEMA_THRESH under the OLD metric on the identical
    pair (proves the fix); a cross-domain distinct-fact pair AND a same-domain wrong-material pair
    both score < SCHEMA_THRESH under the NEW metric (mandatory can-fail: 'a similarity gate that
    merges everything is broken'). (2) Real-pipeline (actual update_prelim_and_generalize on a
    fresh TierState, independence-weighted count gate satisfied by construction with exactly 2
    independent-tagged sources so the ONLY variable is the coherence metric): the same paraphrase
    pair retains WITH concept coherence and does NOT retain WITHOUT it; the cross-domain distinct-
    fact pair does NOT retain even though its count gate alone would clear 2.5."""
    tr_para_a = Trace("ctrl_para|cskg|w0", "POS", context_vector(_PARA_CSKG), 0)
    tr_para_b = Trace("ctrl_para|kb_role_schema|w1", "POS", context_vector(_PARA_KB), 1)
    ep_para = {tr_para_a.episode_id: _PARA_CSKG, tr_para_b.episode_id: _PARA_KB}
    para_old = schema_consistency_split_half([tr_para_a, tr_para_b], min_half_size=1, coherence_fn=None)
    para_new = schema_consistency_split_half(
        [tr_para_a, tr_para_b], min_half_size=1,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_para))

    tr_neg_a = Trace("ctrl_neg|cskg|w0", "POS", context_vector(_NEG_CSKG), 0)
    tr_neg_b = Trace("ctrl_neg|kb_role_schema|w1", "POS", context_vector(_NEG_KB), 1)
    ep_neg = {tr_neg_a.episode_id: _NEG_CSKG, tr_neg_b.episode_id: _NEG_KB}
    neg_new = schema_consistency_split_half(
        [tr_neg_a, tr_neg_b], min_half_size=1,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_neg))

    tr_wm_a = Trace("ctrl_wm|cskg|w0", "POS", context_vector(_WRONGMAT_CSKG), 0)
    tr_wm_b = Trace("ctrl_wm|kb_role_schema|w1", "POS", context_vector(_WRONGMAT_KB), 1)
    ep_wm = {tr_wm_a.episode_id: _WRONGMAT_CSKG, tr_wm_b.episode_id: _WRONGMAT_KB}
    wm_new = schema_consistency_split_half(
        [tr_wm_a, tr_wm_b], min_half_size=1,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_wm))

    closed_form_ok = (para_new is not None and para_new >= SCHEMA_THRESH
                      and para_old is not None and para_old < SCHEMA_THRESH
                      and neg_new is not None and neg_new < SCHEMA_THRESH
                      and wm_new is not None and wm_new < SCHEMA_THRESH)

    def cluster_key_fn_local(pk: str) -> str:
        return "CONTROL_CLUSTER"

    def register_fn_local(pk: str, cluster_key: str, label: str) -> torch.Tensor:
        return build_instance_register(pk, pk, cluster_key, f"CTRL_{label}")

    weighted_common = dict(min_confirm=INDEPENDENCE_MIN_CONFIRM,
                           trace_weight_fn=independence_weighted_trace_score, schema_min_half_size=1)

    ep_d = {"ctrl_paraphrase_pair|cskg|w0": _PARA_CSKG, "ctrl_paraphrase_pair|kb_role_schema|w1": _PARA_KB}
    cvec_d1, cvec_d2 = context_vector(_PARA_CSKG), context_vector(_PARA_KB)

    state_d_new = TierState(seed_base=80001, n_dim=512, relation="CTRL_REL")
    state_d_new.prelim_lib.flag("ctrl_paraphrase_pair", "ctrl_paraphrase_pair|cskg|w0", "POS", cvec_d1, 0)
    state_d_new.prelim_lib.flag("ctrl_paraphrase_pair", "ctrl_paraphrase_pair|kb_role_schema|w1", "POS", cvec_d2, 1)
    diag_d_new = update_prelim_and_generalize(
        state_d_new, cluster_key_fn_local, novelty_thresh=0.15, register_fn=register_fn_local,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_d), **weighted_common)

    state_d_old = TierState(seed_base=80002, n_dim=512, relation="CTRL_REL")
    state_d_old.prelim_lib.flag("ctrl_paraphrase_pair", "ctrl_paraphrase_pair|cskg|w0", "POS", cvec_d1, 0)
    state_d_old.prelim_lib.flag("ctrl_paraphrase_pair", "ctrl_paraphrase_pair|kb_role_schema|w1", "POS", cvec_d2, 1)
    diag_d_old = update_prelim_and_generalize(
        state_d_old, cluster_key_fn_local, novelty_thresh=0.15, register_fn=register_fn_local,
        **weighted_common)  # coherence_fn=None default -> OLD metric

    ep_e = {"ctrl_corrupted_pair|cskg|w0": _NEG_CSKG, "ctrl_corrupted_pair|kb_role_schema|w1": _NEG_KB}
    cvec_e1, cvec_e2 = context_vector(_NEG_CSKG), context_vector(_NEG_KB)
    state_e = TierState(seed_base=80003, n_dim=512, relation="CTRL_REL")
    state_e.prelim_lib.flag("ctrl_corrupted_pair", "ctrl_corrupted_pair|cskg|w0", "POS", cvec_e1, 0)
    state_e.prelim_lib.flag("ctrl_corrupted_pair", "ctrl_corrupted_pair|kb_role_schema|w1", "POS", cvec_e2, 1)
    diag_e = update_prelim_and_generalize(
        state_e, cluster_key_fn_local, novelty_thresh=0.15, register_fn=register_fn_local,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_e), **weighted_common)

    real_pipeline_pos_new = diag_d_new["newly_retained"] > 0
    real_pipeline_pos_old = diag_d_old["newly_retained"] > 0
    real_pipeline_neg = diag_e["newly_retained"] > 0
    real_pipeline_ok = real_pipeline_pos_new and not real_pipeline_pos_old and not real_pipeline_neg

    return {
        "closed_form_ok": bool(closed_form_ok), "real_pipeline_ok": bool(real_pipeline_ok),
        "paraphrase_new_score": round(para_new, 4) if para_new is not None else None,
        "paraphrase_old_score": round(para_old, 4) if para_old is not None else None,
        "cross_domain_neg_score": round(neg_new, 4) if neg_new is not None else None,
        "wrong_material_neg_score": round(wm_new, 4) if wm_new is not None else None,
        "real_pipeline_pos_retained_with_concept": real_pipeline_pos_new,
        "real_pipeline_pos_retained_with_old": real_pipeline_pos_old,
        "real_pipeline_neg_retained": real_pipeline_neg,
        "control_check_ok": bool(closed_form_ok and real_pipeline_ok),
    }


# =========================================================================== self-test
def run_self_test() -> Dict:
    """(a) regression: hdlab.grounding_acquisition_loop.self_test() and hdlab.prelim_tier.
    self_test() both still PASS unchanged (proves the additive coherence_fn edits are backward-
    compatible); (b) closed-form + real-pipeline concept-coherence control checks (this cell's own
    mechanism, isolated from the full 62-gap pipeline)."""
    import hdlab.grounding_acquisition_loop as gal
    import hdlab.prelim_tier as pt
    gal_result = gal.self_test()
    pt_result = pt.self_test()

    # closed-form boundary: a real 3-word case (leaf/oxygen CSKG vs photosynthesis/oxygen CauseNet)
    cskg_ox = "CSKG external knowledge base records that leaf bridges to oxygen via relation(s) ['/r/MadeOf']."
    cn_ox = "CauseNet precision cache records a causal pair between photosynthesis and oxygen, match type process_material."
    ep_ox = {"ox_a": cskg_ox, "ox_b": cn_ox}
    tr_ox_a = Trace("ox_a", "POS", context_vector(cskg_ox), 0)
    tr_ox_b = Trace("ox_b", "POS", context_vector(cn_ox), 1)
    ox_new = schema_consistency_split_half(
        [tr_ox_a, tr_ox_b], min_half_size=1,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_ox))
    assert ox_new is not None and ox_new >= SCHEMA_THRESH, (
        f"SELF_TEST FAIL: real 3-source-style paraphrase pair (leaf/oxygen CSKG vs "
        f"photosynthesis/oxygen CauseNet) must cohere under the concept metric, got {ox_new}")

    # OOV-both-sides -> 0.0, not a crash, not an accidental pass.
    oov_a = "CSKG external knowledge base records that zzqxfoo bridges to wibbleblorp via relation(s) []."
    oov_b = "ProPara process physics KB lists wibbleblorp among [] terms for process zzqxfoo."
    ep_oov = {"oov_a": oov_a, "oov_b": oov_b}
    tr_oov_a = Trace("oov_a", "POS", context_vector(oov_a), 0)
    tr_oov_b = Trace("oov_b", "POS", context_vector(oov_b), 1)
    oov_score = schema_consistency_split_half(
        [tr_oov_a, tr_oov_b], min_half_size=1,
        coherence_fn=functools.partial(concept_coherence_score, episode_text=ep_oov))
    assert oov_score == 0.0, f"SELF_TEST FAIL: zero in-lexicon words on both sides must score 0.0, got {oov_score}"

    ctrl = run_concept_control_checks()
    assert ctrl["control_check_ok"], f"SELF_TEST FAIL: concept-coherence control checks failed: {ctrl}"

    # scramble_wave_content boundary (2026-08-11 fix): tiny synthetic 4-pk x 2-category fixture,
    # every category has n=4 >= 2 (fully derangeable). Assert (a) EVERY entry's text actually
    # changed (zero fixed points -- the derangement guarantee), (b) structure (wave_idx, source_tag,
    # cardinality per pk) is byte-identical to the input, (c) re-running with the SAME seed
    # reproduces the identical output (determinism), (d) a DIFFERENT seed produces a different
    # rotation (the seed is actually consulted, not ignored).
    synth_waves = {
        "gap_a": [(0, "cskg", "text_a_cskg"), (2, "kb_role_schema", "text_a_kb")],
        "gap_b": [(0, "cskg", "text_b_cskg"), (2, "kb_role_schema", "text_b_kb")],
        "gap_c": [(0, "cskg", "text_c_cskg"), (2, "kb_role_schema", "text_c_kb")],
        "gap_d": [(0, "cskg", "text_d_cskg"), (2, "kb_role_schema", "text_d_kb")],
    }
    scr1, diag1 = scramble_wave_content(synth_waves, seed=777)
    assert diag1["n_categories_too_small"] == 0, f"SELF_TEST FAIL: expected all synth categories derangeable, got {diag1}"
    for pk, gw in synth_waves.items():
        assert len(scr1[pk]) == len(gw), "SELF_TEST FAIL: scramble changed cardinality"
        for (w, tag, text), (w2, tag2, text2) in zip(gw, scr1[pk]):
            assert (w, tag) == (w2, tag2), "SELF_TEST FAIL: scramble changed wiring (wave_idx/source_tag)"
            assert text2 != text, f"SELF_TEST FAIL: scramble left a fixed point for {pk} {tag}: {text2!r}"
    scr1_repeat, _ = scramble_wave_content(synth_waves, seed=777)
    assert scr1_repeat == scr1, "SELF_TEST FAIL: scramble_wave_content not deterministic under fixed seed"
    scr2, _ = scramble_wave_content(synth_waves, seed=778)
    assert scr2 != scr1, "SELF_TEST FAIL: scramble_wave_content ignores its seed (different seed -> identical output)"
    # n=1 category must be left uncorrupted and flagged, never silently dropped or crashed on.
    synth_small = {"gap_e": [(0, "cskg", "only_text")]}
    scr_small, diag_small = scramble_wave_content(synth_small, seed=999)
    assert diag_small["n_categories_too_small"] == 1 and scr_small["gap_e"][0][2] == "only_text", (
        f"SELF_TEST FAIL: n=1 category must be left as-is and counted, got {diag_small} / {scr_small}")

    # DUPLICATE-CONTENT-SIBLINGS regression (2026-08-11): reproduces the exact real-data pattern
    # that let 8/21 mechanism-isolation gaps survive the FIRST cut of this function -- multiple
    # pks sharing a template that omits `whole` (e.g. kb_role_schema only names process+material)
    # produce BYTE-IDENTICAL text. gap_p/gap_q/gap_r all share "shared_text" (3-way tie); gap_s is
    # the lone odd-one-out. A pk-position-only derangement could swap gap_p<->gap_q (both
    # "shared_text") and leave BOTH looking "changed" by donor-identity but byte-IDENTICAL in
    # content -- exactly the leak. The content-group fix must guarantee every one of gap_p/q/r ends
    # up holding gap_s's "distinct_text", and gap_s ends up holding "shared_text" -- i.e. NONE of
    # the 4 pks may retain a text content-equal to what they started with.
    synth_dup = {
        "gap_p": [(2, "kb_role_schema", "shared_text")],
        "gap_q": [(2, "kb_role_schema", "shared_text")],
        "gap_r": [(2, "kb_role_schema", "shared_text")],
        "gap_s": [(2, "kb_role_schema", "distinct_text")],
    }
    scr_dup, diag_dup = scramble_wave_content(synth_dup, seed=42)
    assert diag_dup["n_content_groups_total"] == 2, f"SELF_TEST FAIL: expected 2 content groups, got {diag_dup}"
    for pk, gw in synth_dup.items():
        orig = gw[0][2]
        new = scr_dup[pk][0][2]
        assert new != orig, (
            f"SELF_TEST FAIL: DUPLICATE-CONTENT-SIBLINGS regression -- {pk} kept content-equal "
            f"text ({new!r} vs original {orig!r}) after scramble; this is the exact leak class "
            f"that let 8/21 real mechanism-isolation gaps survive on the first cut of this fn")
    assert scr_dup["gap_p"][0][2] == scr_dup["gap_q"][0][2] == scr_dup["gap_r"][0][2] == "distinct_text", (
        f"SELF_TEST FAIL: all 3 members of the 'shared_text' content-group must be reassigned the "
        f"SAME foreign text (group-level derangement), got {scr_dup}")
    assert scr_dup["gap_s"][0][2] == "shared_text", f"SELF_TEST FAIL: gap_s must swap to the other group's text, got {scr_dup}"

    return {
        "grounding_acquisition_loop_regression_ok": True,
        "prelim_tier_regression_ok": True,
        "leaf_oxygen_paraphrase_ok": True, "leaf_oxygen_score": round(ox_new, 4),
        "oov_both_sides_zero_ok": True,
        "control_checks": ctrl,
        "scramble_wave_content_derangement_ok": True,
        "scramble_wave_content_deterministic_ok": True,
        "scramble_wave_content_seed_sensitive_ok": True,
        "scramble_wave_content_n1_category_handled_ok": True,
        "scramble_wave_content_duplicate_content_siblings_ok": True,
        "gal_self_test": gal_result, "pt_self_test": pt_result,
    }


# =========================================================================== I/O helpers
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


# =========================================================================== main pipeline
SEED_FOUND_WBASE = 20260815201
SEED_TIER_WBASE = 20260815202
SEED_FOUND_WCON = 20260815203
SEED_TIER_WCON = 20260815204
SEED_FOUND_WSCR = 20260815205
SEED_TIER_WSCR = 20260815206
SEED_FOUND_R = 20260815207
SEED_TIER_R = 20260815208
SEED_CONTENT_SCRAMBLE = 20260811301   # scramble_wave_content derangement rotation offsets
SEED_FOUND_WMECH = 20260815209        # W_mechanism_isolation (2026-08-11 control fix)
SEED_TIER_WMECH = 20260815210


def run_pipeline(process_filter, run_mode: str) -> Dict:
    t0 = time.perf_counter()

    print("[stage] building real reading facts + CSKG bridges + gap-set", flush=True)
    reading = build_reading_facts(process_filter=process_filter)
    vocab = reading_vocab(reading)
    narrow, wide = build_cskg_bridges(vocab)
    gap = build_gap_set(reading, narrow)
    targets = gap["targets"]
    print(f"[gap-set] raw={gap['raw_n']} survive={gap['survive_n']} unique={gap['unique_n']}", flush=True)
    assert targets, "gap-set is empty -- cannot proceed with a decisive test (honest HARD_FAIL condition)"

    processes = sorted(reading.keys())
    materials = vocab
    wholes = sorted({t["whole"] for t in targets} | {w for lst in wide.values() for w in lst}
                     | {w for lst in narrow.values() for w in lst})
    ents, ent_idx = build_entity_index(processes, materials, wholes)
    n_ent = len(ents)
    print(f"[entities] n_ent={n_ent} n_targets={len(targets)}", flush=True)

    hop1 = fresh_kg(n_ent, SEED_KG_HOP1)
    rel_idx = ingest_reading_hop1(hop1, reading, ent_idx)
    bridge_idx = rel_idx["BRIDGE"]

    narrow_edges = [(m, w) for m in sorted(narrow) for w in narrow[m]]
    hop2_real = fresh_kg(n_ent, SEED_KG_HOP2)
    ingest_bridge_hop2(hop2_real, narrow_edges, ent_idx, bridge_idx)

    scrambled_edges = scramble_edges(narrow_edges, SEED_SCRAMBLE)
    hop2_scrambled = fresh_kg(n_ent, SEED_KG_HOP2)
    ingest_bridge_hop2(hop2_scrambled, scrambled_edges, ent_idx, bridge_idx)

    print("[stage] STATE-OF-MIND + CA3 GATHER", flush=True)
    mat_names, codebook, mat_vecs = build_material_codebook(materials, SEED_FHRR)
    reg = RelationRegister(d=FHRR_D, generator=torch.Generator().manual_seed(SEED_FHRR + 1))
    for proc in processes:
        for material in sorted(reading.get(proc, {}).keys()):
            reg.bind_filler(proc, "GOAL", mat_vecs[material])
    gathered_per_proc: Dict[str, List[str]] = {}
    for proc in processes:
        q = real_to_concat(reg.decode_filler(proc, "GOAL"))
        gathered_per_proc[proc] = ca3_relevance_gather(q, mat_names, codebook, k_peel=CA3_K_PEEL,
                                                        sim_floor=CA3_SIM_FLOOR)

    print("[stage] positive-control reproduction (Gate D)", flush=True)
    pc_recovery5 = _positive_control_reproduction(targets, hop1, hop2_real, ent_idx, rel_idx,
                                                  bridge_idx, gathered_per_proc, n_ent)
    positive_control_ok = (abs(pc_recovery5 - 0.3802) <= 0.10) if run_mode == "full" else True
    print(f"[positive-control] arm3-reproduction recovery@5={pc_recovery5:.4f} "
          f"(cited=0.3802, gated={run_mode == 'full'}, ok={positive_control_ok})", flush=True)

    print("[stage] eligibility (per-cue REASON, unscrambled)", flush=True)
    eligible_real, _cache, excl_real = _eligible_targets(targets, hop1, hop2_real, ent_idx,
                                                          rel_idx, bridge_idx, gathered_per_proc, n_ent)
    print(f"[eligibility] n_eligible={len(eligible_real)} / {len(targets)} excl={excl_real}", flush=True)

    print("[stage] eligibility under SCRAMBLED hop2 (for W_scramble)", flush=True)
    eligible_scr, _cache_scr, excl_scr = _eligible_targets(targets, hop1, hop2_scrambled, ent_idx,
                                                            rel_idx, bridge_idx, gathered_per_proc, n_ent)
    print(f"[eligibility-scramble] n_eligible={len(eligible_scr)} / {len(targets)} excl={excl_scr}", flush=True)

    print("[stage] novelty-threshold calibration", flush=True)
    novelty_thresh, calib_fallback = compute_novelty_thresh(eligible_real)
    print(f"[calibration] novelty_thresh={novelty_thresh:.4f} fallback={calib_fallback}", flush=True)

    do_causenet = (run_mode == "full")
    print("[stage] CSKG cross-source scan", flush=True)
    mat_whole_rel, proc_whole_rel, proc_mat_rel, n_cskg_rows = compute_cskg_extra(materials, wholes, processes)
    if do_causenet:
        print("[stage] CauseNet cross-source scan (FULL only, ~50-80s)", flush=True)
        cn_mat_whole, cn_proc_mat, cn_proc_whole, n_cn_rows = compute_causenet_pairs(materials, wholes, processes)
    else:
        cn_mat_whole, cn_proc_mat, cn_proc_whole, n_cn_rows = set(), set(), set(), 0
        print("[causenet] skipped (smoke mode -- 2-wave ceiling)", flush=True)
    kb_hits, kb_path = compute_kb_role_hits(processes, materials)
    print(f"[kb-role-schema] {len(kb_hits)} (process,material) role hits from {kb_path}", flush=True)

    eligible_pks = {pk_of_genuine(t) for t in eligible_real}
    coverage_hist_eligible: Dict[int, int] = {}
    for t in targets:
        if pk_of_genuine(t) not in eligible_pks:
            continue
        p, m, w = t["process"], t["via_material"], t["whole"]
        n_src = 1
        if (m, w) in cn_mat_whole or (p, m) in cn_proc_mat or (p, w) in cn_proc_whole:
            n_src += 1
        if (p, m) in kb_hits:
            n_src += 1
        coverage_hist_eligible[n_src] = coverage_hist_eligible.get(n_src, 0) + 1
    print(f"[HEADLINE] per-gap coverage histogram, {len(eligible_real)} ELIGIBLE targets: "
          f"{dict(sorted(coverage_hist_eligible.items()))}", flush=True)

    waves_by_pk = build_genuine_waves(targets, mat_whole_rel, proc_whole_rel, proc_mat_rel,
                                      cn_mat_whole, cn_proc_mat, cn_proc_whole, kb_hits, do_causenet)
    n_waves = 3 if do_causenet else 2
    print(f"[genuine-waves] n_waves={n_waves}", flush=True)

    print("[stage] closed-form schema audit (OLD vs NEW coherence metric, every real 2+-source gap)", flush=True)
    schema_audit = closed_form_schema_audit(eligible_real, waves_by_pk)
    print(f"[closed-form-schema-audit] n_gaps_2plus={schema_audit['n_gaps_2plus']} "
          f"n_old_cross={schema_audit['n_old_cross']} n_new_cross={schema_audit['n_new_cross']} "
          f"n_newly_crossing={schema_audit['n_newly_crossing']} n_regressed={schema_audit['n_regressed']}", flush=True)

    print("[stage] concept-coherence control checks (real WIRED gate)", flush=True)
    ctrl = run_concept_control_checks()
    print(f"[control-checks] closed_form_ok={ctrl['closed_form_ok']} real_pipeline_ok={ctrl['real_pipeline_ok']} "
          f"control_check_ok={ctrl['control_check_ok']}", flush=True)

    print(f"[stage] running W_baseline (n_waves={n_waves})", flush=True)
    w_baseline = run_concept_arm("W_baseline", eligible_real, waves_by_pk, n_waves, novelty_thresh,
                                 SEED_FOUND_WBASE, SEED_TIER_WBASE, use_concept_coherence=False)
    print(f"[arm W_baseline] {w_baseline['final']['n_foundation']}/{w_baseline['final']['n_middle']} "
          f"(foundation/middle)", flush=True)

    print(f"[stage] running W_concept (n_waves={n_waves})", flush=True)
    w_concept = run_concept_arm("W_concept", eligible_real, waves_by_pk, n_waves, novelty_thresh,
                                SEED_FOUND_WCON, SEED_TIER_WCON, use_concept_coherence=True)
    print(f"[arm W_concept] {w_concept['final']['n_foundation']}/{w_concept['final']['n_middle']} "
          f"(foundation/middle)", flush=True)

    # ---- the headline diff: blocked-under-baseline gaps that now retain under concept coherence
    # (moved BEFORE W_scramble/W_mechanism_isolation -- newly_retained_pks is the population the
    # 2026-08-11 mechanism-isolation control needs) ----
    eligible_2plus_pks = {r["pk"] for r in schema_audit["rows"]}
    baseline_resolved = set(w_baseline["final"]["resolved_pks"])
    concept_resolved = set(w_concept["final"]["resolved_pks"])
    blocked_pks = eligible_2plus_pks - baseline_resolved
    newly_retained_pks = blocked_pks & concept_resolved
    regressed_pks = (baseline_resolved & eligible_2plus_pks) - concept_resolved
    newly_retained_fraction = (len(newly_retained_pks) / len(blocked_pks)) if blocked_pks else 0.0
    print(f"[HEADLINE-DIFF] eligible_2plus={len(eligible_2plus_pks)} baseline_resolved="
          f"{len(baseline_resolved & eligible_2plus_pks)} blocked={len(blocked_pks)} "
          f"newly_retained={len(newly_retained_pks)} regressed={len(regressed_pks)} "
          f"fraction={newly_retained_fraction:.4f}", flush=True)

    # ---- 2026-08-11 CONTROL FIX: corrupt the CONCEPT CONTENT the coherence metric reads (see
    # scramble_wave_content docstring for the full derivation) ----
    print("[stage] scrambling wave CONCEPT CONTENT (control fix)", flush=True)
    waves_by_pk_content_scrambled, content_scramble_diag = scramble_wave_content(waves_by_pk, SEED_CONTENT_SCRAMBLE)
    print(f"[content-scramble] categories_deranged={content_scramble_diag['n_categories_deranged']} "
          f"categories_too_small={content_scramble_diag['n_categories_too_small']} "
          f"entries_changed={content_scramble_diag['n_entries_changed']}/{content_scramble_diag['n_entries_total']}", flush=True)

    # ---- ISOLATION 1 (SCRAMBLE-RETENTION): W_scramble FIXED -- scrambled cross-source KG LINKS
    # (recomputed eligibility, as before) AND NOW ALSO scrambled CONCEPT CONTENT, so a gap that
    # survives the link-scramble by chance can no longer ride on its own real, unscrambled
    # evidence. Must collapse to ~0 retention. ----
    print(f"[stage] running W_scramble (FIXED: link-scrambled + content-scrambled, n_waves={n_waves})", flush=True)
    w_scramble = run_concept_arm("W_scramble", eligible_scr, waves_by_pk_content_scrambled, n_waves, novelty_thresh,
                                 SEED_FOUND_WSCR, SEED_TIER_WSCR, use_concept_coherence=True)
    print(f"[arm W_scramble] {w_scramble['final']['n_foundation']}/{w_scramble['final']['n_middle']}", flush=True)

    # ---- ISOLATION 2 (MECHANISM-ISOLATION, the decisive one): REAL (unscrambled) eligibility,
    # restricted to EXACTLY the pks that recovered under W_concept (newly_retained_pks), run again
    # with ONLY the concept content scrambled. If the win is genuine concept-alignment, none of
    # these should retain a second time once their content no longer matches; if the recovery
    # SURVIVES, it was never about concept meaning. ----
    mech_iso_targets = [t for t in eligible_real if pk_of_genuine(t) in newly_retained_pks]
    print(f"[stage] running W_mechanism_isolation (population={len(mech_iso_targets)} of the "
          f"{len(newly_retained_pks)} newly-retained gaps, content-scrambled ONLY, n_waves={n_waves})", flush=True)
    w_mechanism_isolation = run_concept_arm("W_mechanism_isolation", mech_iso_targets,
                                            waves_by_pk_content_scrambled, n_waves, novelty_thresh,
                                            SEED_FOUND_WMECH, SEED_TIER_WMECH, use_concept_coherence=True)
    mech_iso_recovered_pks = set(w_mechanism_isolation["final"]["resolved_pks"]) & newly_retained_pks
    mech_iso_population_n = len(mech_iso_targets)
    mech_iso_recovered_count = len(mech_iso_recovered_pks)
    mech_iso_fraction = (mech_iso_recovered_count / mech_iso_population_n) if mech_iso_population_n > 0 else 0.0
    mechanism_isolation_collapse_ok = (mech_iso_population_n == 0) or (mech_iso_fraction <= MECH_ISO_COLLAPSE_BAND)
    print(f"[arm W_mechanism_isolation] recovered={mech_iso_recovered_count}/{mech_iso_population_n} "
          f"fraction={mech_iso_fraction:.4f} collapse_ok={mechanism_isolation_collapse_ok} "
          f"(band<={MECH_ISO_COLLAPSE_BAND})", flush=True)

    r_visits = VISITS_PER_GAP if run_mode == "full" else VISITS_PER_GAP_SMOKE
    r_reference = run_arm("R_reference", "full", targets, hop1, hop2_real, ent_idx, rel_idx,
                          bridge_idx, gathered_per_proc, n_ent, r_visits, novelty_thresh,
                          found_seed=SEED_FOUND_R, tier_seed=SEED_TIER_R)
    print(f"[arm R_reference] {r_reference['final']} n_eligible={r_reference['n_eligible']}", flush=True)

    # ---- cardinality ----
    cardinality_ok = (len(w_baseline["checkpoints"]) == n_waves and len(w_concept["checkpoints"]) == n_waves
                      and len(w_scramble["checkpoints"]) == n_waves
                      and len(w_mechanism_isolation["checkpoints"]) == n_waves
                      and len(r_reference["checkpoints"]) == r_visits)

    # ---- arms-must-differ (META_RULE_AF) ----
    def _curve_digest(checkpoints):
        c = [(cp["n_foundation"], cp["n_middle"]) for cp in checkpoints]
        return hashlib.sha256(json.dumps(c).encode("utf-8")).hexdigest()

    digests = {"W_baseline": _curve_digest(w_baseline["checkpoints"]), "W_concept": _curve_digest(w_concept["checkpoints"]),
              "W_scramble": _curve_digest(w_scramble["checkpoints"]),
              "W_mechanism_isolation": _curve_digest(w_mechanism_isolation["checkpoints"]),
              "R_reference": _curve_digest(r_reference["checkpoints"])}
    arms_differ_baseline_vs_concept_ok = digests["W_baseline"] != digests["W_concept"]
    arms_differ_concept_vs_reference_ok = digests["W_concept"] != digests["R_reference"]
    arms_differ_concept_vs_scramble_ok = digests["W_concept"] != digests["W_scramble"] or w_concept["n_eligible"] == w_scramble["n_eligible"]
    arms_differ_concept_vs_mechanism_isolation_ok = (digests["W_concept"] != digests["W_mechanism_isolation"]
                                                      or w_concept["n_eligible"] == w_mechanism_isolation["n_eligible"])

    # ---- verdict quantities ----
    no_leak_ok = all(arm["no_leak_ok"] for arm in (w_baseline, w_concept, w_scramble, w_mechanism_isolation, r_reference))
    if run_mode == "full":
        reference_reproduces_prior = (abs(r_reference["final"]["n_foundation"] - 40) <= 15 and
                                      r_reference["final"]["n_total_resolved"] == r_reference["n_eligible"])
        baseline_reproduces_parent = (w_baseline["final"]["n_middle"] == 15 or
                                      abs(w_baseline["final"]["n_middle"] - 15) <= 3)
    else:
        reference_reproduces_prior = (r_reference["final"]["n_total_resolved"] == r_reference["n_eligible"])
        baseline_reproduces_parent = True

    # scramble_collapses (FIXED, strict): with concept content now ALSO corrupted, no residual
    # channel remains for a genuinely-coherent gap to survive by carrying its own real evidence --
    # require an exact 0, not just "n_eligible<=1" (the old, weaker OR-clause this replaces).
    scramble_collapses = (w_scramble["final"]["n_foundation"] + w_scramble["final"]["n_middle"]) == 0

    concept_gate_discriminates = ctrl["closed_form_ok"]
    control_check_ok = ctrl["control_check_ok"]

    controls_ok = (control_check_ok and no_leak_ok and reference_reproduces_prior and scramble_collapses
                  and positive_control_ok and len(regressed_pks) == 0 and baseline_reproduces_parent
                  and mechanism_isolation_collapse_ok)

    end_to_end_retain_ok = (len(blocked_pks) > 0 and newly_retained_fraction >= 0.30)

    elapsed = time.perf_counter() - t0

    if not concept_gate_discriminates and not control_check_ok:
        verdict = "HARD_FAIL_concept_gate_merges_everything"
        verdict_msg = (f"the concept-coherence metric FAILED to correctly discriminate paraphrase "
                        f"from distinct-fact: closed_form_ok={ctrl['closed_form_ok']} -- "
                        f"paraphrase_new={ctrl['paraphrase_new_score']} (need >=0.10), "
                        f"cross_domain_neg={ctrl['cross_domain_neg_score']} (need <0.10), "
                        f"wrong_material_neg={ctrl['wrong_material_neg_score']} (need <0.10). "
                        f"A similarity gate that cannot separate same-fact-paraphrase from "
                        f"genuinely-different-fact is exactly the 'merges everything' failure mode "
                        f"this drill was designed to catch -- needs metric redesign, not a threshold nudge.")
    elif not mechanism_isolation_collapse_ok:
        verdict = "HARD_FAIL_mechanism_isolation_recovery_survives_scrambled_concepts"
        verdict_msg = (f"THE DECISIVE ISOLATION: {mech_iso_recovered_count}/{mech_iso_population_n} "
                        f"({mech_iso_fraction:.1%}) of the previously-recovered gaps STILL retained "
                        f"after ONLY their concept content was scrambled (links/eligibility left "
                        f"real) -- above the pre-registered {MECH_ISO_COLLAPSE_BAND:.0%} chance-"
                        f"collision band. The 21/21 recovery does NOT survive isolation of its "
                        f"claimed mechanism -- this means the win is (at least partly) an artifact "
                        f"of the pipeline/gate plumbing, not genuine concept-meaning alignment, and "
                        f"cannot be trusted as-is regardless of how clean the other controls look.")
    elif not controls_ok:
        verdict = "HARD_FAIL_controls_broken"
        verdict_msg = (f"one or more mandatory can-fail controls FAILED: control_check_ok="
                        f"{control_check_ok} no_leak_ok={no_leak_ok} reference_reproduces_prior="
                        f"{reference_reproduces_prior} scramble_collapses={scramble_collapses} "
                        f"positive_control_ok={positive_control_ok} n_regressed={len(regressed_pks)} "
                        f"baseline_reproduces_parent={baseline_reproduces_parent} "
                        f"mechanism_isolation_collapse_ok={mechanism_isolation_collapse_ok} -- the "
                        f"concept-coherence fix cannot be trusted until every control passes")
    elif end_to_end_retain_ok:
        verdict = "HARD_PASS_concept_coherence_unblocks_cross_source_paraphrase"
        verdict_msg = (f"OWNED graded concept_similarity aligns genuinely-same facts worded "
                        f"differently across sources: {len(newly_retained_pks)}/{len(blocked_pks)} "
                        f"({newly_retained_fraction:.1%}) of the previously-blocked real 2+-source "
                        f"gaps NOW retain end-to-end (W_concept final n_middle="
                        f"{w_concept['final']['n_middle']} vs W_baseline "
                        f"{w_baseline['final']['n_middle']}), zero regressions "
                        f"({len(regressed_pks)}), all controls pass (real paraphrase pair coheres "
                        f"and retains WITH the concept metric / does NOT with the old metric; "
                        f"cross-domain and wrong-material distinct-fact pairs correctly REJECTED "
                        f"both closed-form and real-pipeline; FIXED scramble collapses to "
                        f"{w_scramble['final']['n_foundation'] + w_scramble['final']['n_middle']} "
                        f"under corrupted content; R_reference reproduces cited n_foundation="
                        f"{r_reference['final']['n_foundation']} vs cited 40; no_leak_ok=True) AND "
                        f"the DECISIVE mechanism-isolation control confirms it is real: with ONLY "
                        f"concept content scrambled (eligibility left real), the recovery collapses "
                        f"to {mech_iso_recovered_count}/{mech_iso_population_n} "
                        f"({mech_iso_fraction:.1%}, band<={MECH_ISO_COLLAPSE_BAND:.0%}) -- the win "
                        f"depends on genuine concept-meaning alignment, not pipeline artifact.")
    else:
        verdict = "MIDDLE_BAND_concept_coherence_correct_but_insufficient_lexicon_coverage"
        verdict_msg = (f"the concept-coherence metric itself correctly discriminates paraphrase "
                        f"from distinct-fact (every control passes, INCLUDING the decisive "
                        f"mechanism-isolation: recovery collapses to {mech_iso_recovered_count}/"
                        f"{mech_iso_population_n} under scrambled concept content) -- BUT "
                        f"end-to-end only {len(newly_retained_pks)}/{len(blocked_pks)} "
                        f"({newly_retained_fraction:.1%}) of the real blocked gaps cross the 30% "
                        f"floor. This means too small a fraction of the blocked gaps' specific "
                        f"materials/entities happen to be covered by the current lexical_similarity "
                        f"CONCEPT_FEATURES lexicon (89 base concepts + the 2026-08-10 ProPara "
                        f"extension) to move the needle -- a genuine lexicon-coverage / grounding-"
                        f"wall finding, not a mechanism failure: the mechanism WORKS on the words it "
                        f"knows, it just doesn't know enough words yet.")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "process_filter": sorted(process_filter) if process_filter else "ALL",
        "n_ent": n_ent, "n_targets": len(targets), "n_eligible": len(eligible_real),
        "n_eligible_scramble": len(eligible_scr),
        "positive_control_arm3_reproduction": pc_recovery5, "positive_control_ok": positive_control_ok,
        "novelty_thresh": novelty_thresh, "calibration_fallback": calib_fallback,
        "concept_metric": {"CONCEPT_MATCH_THRESHOLD": CONCEPT_MATCH_THRESHOLD,
                          "SCHEMA_THRESH": SCHEMA_THRESH,
                          "reused_from": "hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD"},
        "coverage_histogram_eligible": {str(k): v for k, v in sorted(coverage_hist_eligible.items())},
        "closed_form_schema_audit": {k: v for k, v in schema_audit.items() if k != "rows"},
        "closed_form_schema_audit_rows_sample": schema_audit["rows"][:10],
        "control_checks": ctrl,
        "content_scramble_diag": content_scramble_diag,
        "n_waves": n_waves, "r_visits": r_visits,
        "arm_results": {"W_baseline": w_baseline, "W_concept": w_concept, "W_scramble": w_scramble,
                       "W_mechanism_isolation": w_mechanism_isolation, "R_reference": r_reference},
        "concept_gate_discriminates": concept_gate_discriminates,
        "eligible_2plus_count": len(eligible_2plus_pks),
        "blocked_count": len(blocked_pks), "newly_retained_count": len(newly_retained_pks),
        "regressed_count": len(regressed_pks), "newly_retained_fraction": newly_retained_fraction,
        "end_to_end_retain_ok": end_to_end_retain_ok, "scramble_collapses": scramble_collapses,
        "mechanism_isolation_population_n": mech_iso_population_n,
        "mechanism_isolation_recovered_count": mech_iso_recovered_count,
        "mechanism_isolation_fraction": mech_iso_fraction,
        "mechanism_isolation_collapse_ok": mechanism_isolation_collapse_ok,
        "no_leak_ok": no_leak_ok, "reference_reproduces_prior": reference_reproduces_prior,
        "baseline_reproduces_parent": baseline_reproduces_parent,
        "controls_ok": controls_ok, "cardinality_ok": cardinality_ok,
        "arm_curve_digests": digests,
        "arms_differ_baseline_vs_concept_ok": arms_differ_baseline_vs_concept_ok,
        "arms_differ_concept_vs_reference_ok": arms_differ_concept_vs_reference_ok,
        "arms_differ_concept_vs_scramble_ok": arms_differ_concept_vs_scramble_ok,
        "arms_differ_concept_vs_mechanism_isolation_ok": arms_differ_concept_vs_mechanism_isolation_ok,
        "bands": {"schema_thresh": SCHEMA_THRESH, "concept_match_threshold": CONCEPT_MATCH_THRESHOLD,
                  "end_to_end_retain_fraction_floor": 0.30, "reference_tolerance_abs": 15,
                  "reference_cited_n_foundation": 40, "positive_control_tolerance": 0.10,
                  "baseline_cited_n_middle": 15, "mechanism_isolation_collapse_band": MECH_ISO_COLLAPSE_BAND},
    }
    return metrics


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="closed-form + real-pipeline control checks, <10s")
    parser.add_argument("--smoke", action="store_true", help="real pipeline, 2-process subset, CauseNet skipped")
    parser.add_argument("--timeout", type=float, default=400.0,
                        help="declared wall-time budget: smoke~20-50s, FULL~100-180s (CauseNet scan dominates)")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                  "verdict_msg": ("regression: grounding_acquisition_loop.self_test() and "
                                  "prelim_tier.self_test() both pass unchanged after the additive "
                                  "coherence_fn edits; closed-form concept-coherence boundary "
                                  "proofs pass (real paraphrase pair coheres, cross-domain/wrong-"
                                  "material distinct-fact pairs rejected, OOV-both-sides -> 0.0); "
                                  "real-pipeline control checks pass (paraphrase pair retains WITH "
                                  "concept coherence and does NOT retain WITHOUT it; distinct-fact "
                                  "pair never retains) -- the mechanism works correctly before "
                                  "touching real data"),
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    if args.smoke:
        run_mode = "smoke"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_smoke")
        process_filter = {"combustion", "photosynthesis"}
    else:
        run_mode = "full"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        process_filter = None

    _write_start_marker(output_dir, run_mode, expected_n_units=5)
    metrics = run_pipeline(process_filter, run_mode)

    if run_mode == "smoke":
        discriminator_ok = (metrics["concept_gate_discriminates"] and metrics["control_checks"]["control_check_ok"]
                            and metrics["scramble_collapses"] and metrics["mechanism_isolation_collapse_ok"])
        if not discriminator_ok:
            metrics["verdict"] = "SMOKE_GATE_FAIL_discriminator_not_firing"
            metrics["verdict_msg"] = (f"smoke discriminator check: concept_gate_discriminates="
                                      f"{metrics['concept_gate_discriminates']} control_check_ok="
                                      f"{metrics['control_checks']['control_check_ok']} "
                                      f"scramble_collapses={metrics['scramble_collapses']} "
                                      f"mechanism_isolation_collapse_ok="
                                      f"{metrics['mechanism_isolation_collapse_ok']} -- the "
                                      f"concept-coherence gate's own can-fail signals must fire "
                                      f"cleanly at smoke scale before FULL dispatch")

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
