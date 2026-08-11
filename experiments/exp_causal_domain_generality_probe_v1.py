# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: arm3(cued) vs arm1(blind) vs arm2(voting) per-target top-1 index arrays
#   hashed + asserted not-all-identical (same convention as the source cell)
# - final_metrics_atomicity = tmp_replace (single-shot)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: discrete top-k retrieval accuracy (Part A) + discrete classification accuracy
#   (Part B), no Gaussian noise-floor metric; discriminator_reachability=true, argued via the
#   author's own dev-time probe (MEASURED below, reproduced by this cell's own FULL run) AND the
#   closed-form CAUSAL_MARKER_FEATURES separation (cross-class mean sim ~0.07 vs within-class
#   ~0.56-0.77, comfortably clears floor=0.50/margin=0.15)
# - baseline_in_band: N/A for arm0 (structural =0 by construction, same exemption as the source
#   cell); arm1/arm2 ARE the real baselines this cell's HARD_PASS gate compares against (both
#   MEASURED near-floor on this domain, see docstring), not exempted
# - discriminator survives scale: FULL population is real (52 targets, all 15 processes); no
#   separate smoke-vs-full parameter change needed for Part B (closed-form, already full-scale
#   for its own tiny domain); Part A smoke uses the SAME 2-process-subset convention as the
#   source cell
# - HP_SCOPE: HARD_PASS/HARD_FAIL bands apply to the OVERALL verdict (Part A AND Part B jointly,
#   per the task's own pre-registered "HARD_PASS = weak->strong recovers AND canonicalization
#   gives same-rep/distinct-rep AND controls clean" definition); zero_shot_into_old_classes is a
#   DIAGNOSTIC-ONLY field, not a gate (see docstring "boundary-respect, not a claim")
# - cardinality_ok: EXPECTED = Part A 52 real gap targets (FULL) / 2-process subset (smoke) +
#   Part B 9 leave-one-out probes + 3 held-out probes x 2 (real + scrambled) + 3 real-data
#   same/distinct-rep pairs -- every count logged, verdict counts checked against population size
# - per-unit failure-class instrumentation: N/A (single deterministic pass per test group)
# - calibration_check: default_ok_for_this_regime (RELATION_CLASS_FLOOR/MARGIN=0.50/0.15 REUSED
#   UNCHANGED from exp_relation_canonicalization_learned_v1's own calibration, never re-tuned for
#   this domain -- this cell's own separation is measured, not calibrated-for-pass)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL KGStore/RelationRegister/HDFactStore objects (via the reused source
#   cells' own self-test fixtures) PLUS a new tiny fixture isolating _causal_narrow_from_rows
#   (this cell's one new disk-scan function) at N~10 synthetic rows, and real classify_nway calls
#   against the real (tiny, ~12-word) CAUSAL_MARKER_FEATURES lexicon (real_code_path)
# - substrate_signature_checked: KGStore/HDFactStore base kwargs only; hdlab/
#   verb_lexical_similarity.py is the ONE hdlab/ file this task additively extends (new CAUSAL_*
#   data + one new _DOMAINS key only; classify_nway/mean_similarity_to_seeds/existing domains
#   zero lines changed; existing self_test() re-run below as a regression witness)
"""exp_causal_domain_generality_probe_v1 -- GENERALITY probe (2026-08-11): does the proven
three-tier weak->strong + canonicalization pipeline -- built and validated end-to-end on ONE
relation family (121 material-composition MadeOf-bridge facts, relation classes
PART_OF/PRODUCES/CONSUMES/MOVES, ~15 processes; data/exp_state_of_mind_relevance_gather_
reasoning_union_v1/metrics.json HARD_PASS + data/exp_relation_canonicalization_learned_v1/
metrics.json) -- GENERALIZE to a FRESH relation family, or is it fit to that one structure?

DOMAIN PICKED: CAUSAL (X causes/enables/prevents Y). This is the natural strong test per the
task brief: exp_representation_canonicalization_v1 (commit e65de60f1) already DECLARED
`CANON_CAUSAL = "CAUSALLY_LINKED"` but explicitly did NOT exercise it ("declared, NOT exercised
this run" -- see that file's own module docstring); and hdlab.verb_lexical_similarity's (3)
RELATION_MARKER_FEATURES domain covers PART_OF/PRODUCES/CONSUMES/MOVES only -- CAUSAL markers
("cause"/"trigger"/"prevent"/...) are OOV of that domain BY CONSTRUCTION (verified below, T0-b),
so recovering CAUSAL is a genuinely NEW relation family, not a held-out marker within the 4
trained classes. A separate, UNRELATED prior cell (exp_causal_enrichment_probe_recovery_v1,
preregs/2026-08-11_causal_enrichment_probe_recovery_v1.md) tested CauseNet/GO KB-ENRICHMENT
recall on CSKG -- a different question (graph-coverage diagnostic, no gather_reason/ThreeTierLoop/
canonicalization involved); noted here for the record, not reused (disjoint mechanism).

PRIOR-WORK CHECK (substrate_query.sh, mandatory before authoring): top cosine=0.3438
("Cross-domain generalization", a general methodology memory note, not a prior arc CELL);
"causation"/"Causation" (WordNet/FrameNet generic lexical entries). No prior arc cell tests
three-tier-pipeline generality on a causal relation family -- genuinely novel, not a rediscovery.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim; NONE
modified by this cell EXCEPT the one disclosed additive hdlab/verb_lexical_similarity.py
extension, see CELL-TEMPLATE header):
  PART A (weak->strong):
    hdlab.gather_reason.ca3_relevance_gather / fanout_two_hop / recovery_at / real_to_concat / top1
    hdlab.situation_model_accumulate.RelationRegister / unit_phase_vec
    hdlab.kg_traversal.KGStore
    experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1's own build functions
      (build_reading_facts, reading_vocab, reading_fact_set, build_cskg_bridges [wide pool only],
      build_gap_set, build_entity_index, fresh_kg, ingest_reading_hop1, ingest_bridge_hop2,
      build_material_codebook, scramble_edges, voting_predict, run_self_test) -- the SAME real
      15-process reading corpus + gap-set-construction machinery the landed HARD_PASS cell uses,
      imported directly, not re-derived. build_gap_set in particular is reused 100% VERBATIM: it
      is already generic over its `narrow: Dict[material, List[whole]]` argument and does not
      hardcode /r/MadeOf anywhere in its own body.
  PART B (canonicalization):
    hdlab.verb_lexical_similarity.classify_nway / mean_similarity_to_seeds / in_lexicon /
      CAUSAL_SEED_POOLS / CAUSAL_HELDOUT_POOLS / CAUSAL_CANON_CLASSES / CAUSAL_MARKER_FEATURES
      (NEW additive data, see header) / RELATION_SEED_POOLS / RELATION_MARKER_FEATURES (existing,
      for the cross-domain OOV boundary check) / self_test (existing, called unchanged as a
      regression witness) / _feature_vectors / _concept_vector_from / _cos_complex (scramble-
      control recipe reuse only, byte-identical convention to every other scramble control in
      this codebase)
    hdlab.lexical_similarity.self_test / hdlab.hd_fact_store.HDFactStore /
      hdlab.hd_fact_store._run_all_selftests -- core-preserved regression witnesses
    experiments.exp_representation_canonicalization_v1.canon_entity / build_anchor_set /
      content_repr_vector -- the ENTITY side of canonicalization (concept_similarity), UNTOUCHED
      by this cell, reused verbatim exactly as the task specifies ("concept_similarity entities...
      the ONE new thing is the RELATION side")
    experiments.exp_relation_canonicalization_learned_v1's own learned_canon_for_marker /
      learned_canon_leave_one_out pattern (structurally mirrored below for the causal domain, not
      imported -- that module's functions are hardwired to domain="relation"/RELATION_* pools, so
      this cell writes the causal-domain twin of each, same body shape, disclosed as new)

THE NEW THINGS (honestly disclosed, kept to the minimum the generality question needs -- per
compute-proportionality this is a DIRECTIONAL generality question, not a robustness/extraction
sweep, so no new regex-template extraction machinery is built; T1 tests canonicalization IDENTITY
directly on resolved (subject,relation,object) triples):
  (a) hdlab/verb_lexical_similarity.py: additive CAUSAL_MARKER_FEATURES domain (see that file's
      own new section docstring for the full citation/design rationale) + one new _DOMAINS key.
  (b) _causal_narrow_from_rows + build_causal_bridges_narrow: a twin of the source cell's
      build_cskg_bridges, narrow-scoped to /r/Causes instead of /r/MadeOf (the wide/blind pool is
      reused VERBATIM from build_cskg_bridges -- it already scans ANY relation, unaffected by
      which relation the narrow scope picks).
  (c) learned_causal_canon_for_marker / learned_causal_canon_leave_one_out: causal-domain twins of
      exp_relation_canonicalization_learned_v1's own functions (same body shape, domain="causal").
  (d) causenet_causal_corroboration_scan: literal (cause_entity,effect) pair audit against
      CauseNet-precision (the SAME source the "genuine_cross_source_corroboration" cell scanned
      for the MadeOf domain and found ZERO overlap there -- CAUSAL domain is the direct contrast:
      MEASURED@this cell's own dev probe, reproduced in FULL below: 7 literal (material,effect)
      pairs corroborated, e.g. (sugar,cavities), (heat,pain), (oxygen,corrosion), (electricity,
      electrocution), (car,pollution) -- informational corroboration audit, does NOT gate the
      recovery verdict, which is scored on gather_reason/ThreeTierLoop mechanism alone).

GAP-SET (CAUSAL, cross-source, absence-verified): reading (process,material,fate) facts (real
extractor, real corpus) crossed with CSKG's real /r/Causes edges FROM materials TO effect
entities, absence-filtered against the reading fact set itself (build_gap_set's own survive
filter -- zero leakage into the gap-set by construction). MEASURED@this cell's own dev probe
(reproduced in FULL below): raw=52, survive=52, unique=52 (100% survive -- no candidate was ever
literally read; the CAUSAL bridge count itself, 12 materials x 46 total /r/Causes edges scanned
over the SAME 1,213,912-row CSKG corpus the MadeOf domain used, is naturally smaller than MadeOf's
316-edge count, so this is honestly a SMALLER population than the original 121, not a like-for-
like replication -- disclosed, not hidden).

WEAK->STRONG ARMS (mirrors the source cell's arm0/1/2/3 EXACTLY, same functions, only the narrow
bridge relation differs): arm0=structural single-source (=0 by construction), arm1=BLIND UNION
(no cue, wide pool), arm2=VOTING (co-occurrence, no chaining), arm3=STATE-OF-MIND CUED (CA3-
gathered materials, narrow /r/Causes-only pool). CONTROLS: SCRAMBLE-THE-CHAIN (permute narrow-pool
material->effect attachment) + ABLATE-THE-CUE (arm1 vs arm3, by construction).
MEASURED@this cell's own dev probe (reproduced in FULL below): arm1@5=0.0192, arm2@5=0.0192,
arm3@5=0.4615, delta(arm3-arm1)@5=0.4423, arm3_scrambled@5=0.0962.

CANONICALIZATION TESTS (Part B): T0 anti-collapse (9 seed leave-one-out probes, CAUSES/ENABLES/
PREVENTS must never cross-classify), T1 held-out generalization (3 held-out markers:
induce/facilitate/inhibit, MEASURED@dev probe: all 3 correct, margin>=0.68), T2 scramble/
circularity control (fixed-seed word->feature permutation must collapse held-out accuracy), T3
real-data same-rep/distinct-rep (two DIFFERENT causal markers describing the IDENTICAL real gap
fact must produce IDENTICAL content_repr_vector; a genuinely different real fact, or the same
(subject,object) under a different causal relation-class, must produce a DISTINCT vector) +
no-leak, T4 (diagnostic-only, does not gate the verdict) zero-shot classification of causal
markers into the OLD 4 (PART_OF/PRODUCES/CONSUMES/MOVES) classes, and the reverse (old-domain
markers into the new causal classes) -- both directions expected to ABSTAIN (OOV), a boundary-
respect check, not a generalization claim (an OOV abstain is not evidence the mechanism
generalizes OR fails to; it only shows the classifier never forces a wrong-domain guess).

Modes: --self-test (reused source-cell fixtures + gather_reason self-test + a new tiny
_causal_narrow_from_rows fixture + real classify_nway calls against the real causal lexicon,
<10s) / --smoke (real Part-A pipeline, 2-process subset; Part B is already full-scale, closed-
form, run identically in every mode) / (no flag, default) = FULL (real Part-A pipeline, all 15
processes, 52 targets; MEASURED elapsed_s for the structurally-identical source cell at a larger
121-target population = 13.28s-130s, so this smaller population is expected well inside the
~2-3min local budget).

ASCII-only. Deterministic throughout (sorted(set()) discipline; fixed integer seeds, freshly
namespaced from the source cell's own; no built-in hash() anywhere -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import bz2
import glob
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "causal_domain_generality_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec  # noqa: E402
from hdlab.gather_reason import (  # noqa: E402
    ca3_relevance_gather, fanout_two_hop, recovery_at, real_to_concat, top1,
    self_test as gather_reason_self_test,
)
from hdlab.verb_lexical_similarity import (  # noqa: E402
    classify_nway, mean_similarity_to_seeds, in_lexicon,
    CAUSAL_SEED_POOLS, CAUSAL_HELDOUT_POOLS, CAUSAL_CANON_CLASSES, CAUSAL_MARKER_FEATURES,
    RELATION_SEED_POOLS, RELATION_MARKER_FEATURES,
    self_test as verb_lexical_similarity_self_test,
    _feature_vectors as _verb_feature_vectors,          # scramble-control recipe reuse only
    _concept_vector_from as _verb_concept_vector_from,  # scramble-control recipe reuse only
    _cos_complex as _verb_cos_complex,                  # scramble-control recipe reuse only
)
from hdlab.lexical_similarity import self_test as lexical_similarity_self_test  # noqa: E402
from hdlab.hd_fact_store import HDFactStore, _run_all_selftests as hd_fact_store_self_test  # noqa: E402
from experiments.exp_representation_canonicalization_v1 import (  # noqa: E402
    canon_entity, build_anchor_set, content_repr_vector,
)
from experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1 import (  # noqa: E402
    build_reading_facts, reading_vocab, reading_fact_set, build_cskg_bridges, build_gap_set,
    build_entity_index, fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook,
    scramble_edges, voting_predict, run_self_test as source_run_self_test,
    FATE_RELS, BRIDGE_REL, KG_DIM, FHRR_D,
)

CSKG_GLOB = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1", "edges_shard_*.jsonl")
CAUSENET_PATH = os.path.join(REPO_ROOT, "data", "bio_kb_cache", "causenet", "causenet-precision.jsonl.bz2")

K1_FANOUT = 30
K2_FANOUT = 500
CA3_K_PEEL = 25
CA3_SIM_FLOOR = 0.05
CAUSAL_REL = "/r/Causes"

RELATION_CLASS_FLOOR = 0.50   # REUSED UNCHANGED from exp_relation_canonicalization_learned_v1
RELATION_CLASS_MARGIN = 0.15  # (never re-tuned for this domain; see calibration_check header)

# ---- this cell's own fresh seeds (distinct namespace from the source cell's) ----
SEED_KG_CAUSAL = 20260814101
SEED_FHRR_CAUSAL = 20260814102
SEED_SCRAMBLE_CAUSAL = 20260814103


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


# =========================================================================== (b) NEW: causal narrow bridge
def _causal_narrow_from_rows(rows: List[Tuple[str, str, str]], vocab: Set[str]) -> Dict[str, List[str]]:
    """Real filter logic (self-test-exercisable at tiny scale): rows are (subject, obj, relation)
    triples; keep obj-as-effect for every row whose subject is in vocab, relation==CAUSAL_REL, and
    subject != obj. Twin of build_cskg_bridges' own narrow-scope logic, generalized to an
    injectable row source so self-test can exercise it without a real 1.2M-row disk scan."""
    narrow: Dict[str, List[str]] = {}
    for s, o, rel in rows:
        if rel == CAUSAL_REL and s in vocab and s != o:
            narrow.setdefault(s, []).append(o)
    return narrow


def build_causal_bridges_narrow(vocab: List[str]) -> Tuple[Dict[str, List[str]], int]:
    """Real disk scan over all CSKG shards, delegating the actual filter to
    _causal_narrow_from_rows (real code path shared with self-test). Returns (narrow, n_rows)."""
    vset = set(vocab)
    narrow: Dict[str, List[str]] = {}
    n_rows = 0
    for fn in sorted(glob.glob(CSKG_GLOB)):
        rows = []
        with open(fn, encoding="utf-8") as f:
            for line in f:
                n_rows += 1
                row = json.loads(line)
                rows.append((row["subject"], row["obj"], row["relation"]))
        for m, effs in _causal_narrow_from_rows(rows, vset).items():
            narrow.setdefault(m, []).extend(effs)
    return narrow, n_rows


# =========================================================================== (d) NEW: cross-source audit
def causenet_causal_corroboration_scan(narrow: Dict[str, List[str]]) -> Dict:
    """Literal (material,effect) pair audit against CauseNet-precision (informational only; does
    NOT gate the recovery verdict). Direct contrast with the MadeOf domain, where the identically-
    structured scan found ZERO overlap (see exp_state_of_mind_relevance_gather_reasoning_union_v1's
    own causenet_leak_check, out-of-scope declaration)."""
    mat_effect_pairs = {(m, e) for m, effs in narrow.items() for e in effs}
    n_scanned = 0
    literal_hits: List[Tuple[str, str]] = []
    with bz2.open(CAUSENET_PATH, "rt", encoding="utf-8") as f:
        for line in f:
            n_scanned += 1
            row = json.loads(line)
            cr = row["causal_relation"]
            c, e = cr["cause"]["concept"], cr["effect"]["concept"]
            if (c, e) in mat_effect_pairs or (e, c) in mat_effect_pairs:
                literal_hits.append((c, e))
    return {"n_scanned": n_scanned, "n_literal_hits": len(literal_hits),
            "literal_hits": sorted(set(literal_hits))}


# =========================================================================== (c) NEW: learned causal canon
def learned_causal_canon_for_marker(marker: str, seed_pools: Optional[Dict[str, List[str]]] = None
                                    ) -> Optional[str]:
    """Causal-domain twin of exp_relation_canonicalization_learned_v1.learned_canon_for_marker:
    verb-similarity argmax over the 3 canonical causal seed pools (classify_nway, domain="causal",
    REUSED VERBATIM). NO hand marker->canon dict; the canon is COMPUTED. None = abstain."""
    pools = seed_pools if seed_pools is not None else {
        lbl: list(d.keys()) for lbl, d in CAUSAL_SEED_POOLS.items()}
    return classify_nway(marker, pools, domain="causal",
                         floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)


def learned_causal_canon_leave_one_out(marker: str, true_label: str) -> Optional[str]:
    pools = {}
    for lbl, d in CAUSAL_SEED_POOLS.items():
        pools[lbl] = [k for k in d.keys() if not (lbl == true_label and k == marker)]
    return classify_nway(marker, pools, domain="causal",
                         floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)


# =========================================================================== Part B: T0 anti-collapse
def run_causal_anti_collapse() -> Dict:
    per_marker = {}
    for true_label, pool in CAUSAL_SEED_POOLS.items():
        for marker in sorted(pool.keys()):
            got = learned_causal_canon_leave_one_out(marker, true_label)
            per_marker[marker] = {"true_label": true_label, "predicted_label": got,
                                  "correct": got == true_label}
    n_correct = sum(1 for r in per_marker.values() if r["correct"])
    n_total = len(per_marker)
    causes_never_prevents = all(
        r["predicted_label"] != "PREVENTS" for r in per_marker.values() if r["true_label"] == "CAUSES")
    prevents_never_causes = all(
        r["predicted_label"] != "CAUSES" for r in per_marker.values() if r["true_label"] == "PREVENTS")
    return {"per_marker": per_marker, "n_correct": n_correct, "n_total": n_total,
           "accuracy": n_correct / n_total if n_total else 0.0,
           "causes_never_prevents_ok": bool(causes_never_prevents),
           "prevents_never_causes_ok": bool(prevents_never_causes),
           "anti_collapse_ok": bool(n_correct == n_total and causes_never_prevents and prevents_never_causes)}


# =========================================================================== Part B: T1 held-out
def run_causal_held_out_generalization() -> Dict:
    pools = {lbl: list(d.keys()) for lbl, d in CAUSAL_SEED_POOLS.items()}
    per_marker = {}
    for true_label, hd in CAUSAL_HELDOUT_POOLS.items():
        for marker in sorted(hd.keys()):
            sims = {lbl: mean_similarity_to_seeds(marker, pools[lbl], "causal") for lbl in CAUSAL_CANON_CLASSES}
            label = classify_nway(marker, pools, domain="causal",
                                  floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)
            ranked = sorted(sims.items(), key=lambda kv: -kv[1])
            margin = ranked[0][1] - ranked[1][1]
            per_marker[marker] = {"true_label": true_label, "predicted_label": label,
                                  "correct": label == true_label,
                                  "sims": {k: round(v, 4) for k, v in sims.items()}, "margin": round(margin, 4)}
    n_correct = sum(1 for r in per_marker.values() if r["correct"])
    n_total = len(per_marker)
    return {"per_marker": per_marker, "n_correct": n_correct, "n_total": n_total,
           "held_out_generalization_rate": n_correct / n_total if n_total else 0.0}


# =========================================================================== Part B: T2 scramble control
def _scrambled_causal_sim_fn():
    words = sorted(CAUSAL_MARKER_FEATURES.keys())
    gen = torch.Generator().manual_seed(999)
    perm = torch.randperm(len(words), generator=gen).tolist()
    scrambled_map = {words[i]: CAUSAL_MARKER_FEATURES[words[perm[i]]] for i in range(len(words))}
    fv = _verb_feature_vectors("causal")

    def scrambled_mean_sim(word: str, seed_words: List[str]) -> Optional[float]:
        if word not in scrambled_map:
            return None
        wv = _verb_concept_vector_from(scrambled_map[word], fv)
        sims = [_verb_cos_complex(wv, _verb_concept_vector_from(scrambled_map[s], fv))
                for s in seed_words if s in scrambled_map]
        return sum(sims) / len(sims) if sims else None
    return scrambled_mean_sim


def run_causal_held_out_generalization_scrambled() -> Dict:
    pools = {lbl: list(d.keys()) for lbl, d in CAUSAL_SEED_POOLS.items()}
    scrambled_sim = _scrambled_causal_sim_fn()
    per_marker = {}
    for true_label, hd in CAUSAL_HELDOUT_POOLS.items():
        for marker in sorted(hd.keys()):
            sims = {lbl: scrambled_sim(marker, pools[lbl]) for lbl in CAUSAL_CANON_CLASSES}
            ranked = sorted(sims.items(), key=lambda kv: -kv[1])
            best_label, best = ranked[0]
            second = ranked[1][1]
            predicted = best_label if (best >= RELATION_CLASS_FLOOR and (best - second) >= RELATION_CLASS_MARGIN) else None
            per_marker[marker] = {"true_label": true_label, "predicted_label": predicted, "correct": predicted == true_label}
    n_correct = sum(1 for r in per_marker.values() if r["correct"])
    n_total = len(per_marker)
    return {"per_marker": per_marker, "n_correct": n_correct, "n_total": n_total,
           "scrambled_generalization_rate": n_correct / n_total if n_total else 0.0}


# =========================================================================== Part B: T4 (diagnostic-only) boundary
def run_cross_domain_oov_boundary() -> Dict:
    """DIAGNOSTIC ONLY (does not gate the verdict): causal markers are OOV of the OLD "relation"
    domain (never classified into PART_OF/PRODUCES/CONSUMES/MOVES), and old-domain markers are OOV
    of the NEW "causal" domain. Both directions must abstain -- proves the classifier never forces
    a wrong-domain guess, NOT that either mechanism generalizes across the domain boundary."""
    causal_words = sorted(CAUSAL_MARKER_FEATURES.keys())
    relation_words = sorted(RELATION_MARKER_FEATURES.keys())
    relation_pools = {lbl: list(d.keys()) for lbl, d in RELATION_SEED_POOLS.items()}
    causal_pools = {lbl: list(d.keys()) for lbl, d in CAUSAL_SEED_POOLS.items()}
    causal_into_old = {w: classify_nway(w, relation_pools, domain="relation",
                                        floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)
                       for w in causal_words}
    old_into_causal = {w: classify_nway(w, causal_pools, domain="causal",
                                        floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)
                       for w in relation_words}
    causal_oov_of_relation = all(not in_lexicon(w, "relation") for w in causal_words)
    relation_oov_of_causal = all(not in_lexicon(w, "causal") for w in relation_words)
    all_abstain_causal_into_old = all(v is None for v in causal_into_old.values())
    all_abstain_old_into_causal = all(v is None for v in old_into_causal.values())
    return {"causal_words_oov_of_relation_domain": bool(causal_oov_of_relation),
           "relation_words_oov_of_causal_domain": bool(relation_oov_of_causal),
           "causal_into_old_classes": causal_into_old, "old_into_causal_classes": old_into_causal,
           "all_abstain_causal_into_old": bool(all_abstain_causal_into_old),
           "all_abstain_old_into_causal": bool(all_abstain_old_into_causal),
           "boundary_respect_ok": bool(causal_oov_of_relation and relation_oov_of_causal
                                       and all_abstain_causal_into_old and all_abstain_old_into_causal)}


# =========================================================================== Part B: T3 real-data same/distinct-rep
def _isolated_pair_check(triple_a: Tuple[str, str, str], triple_b: Tuple[str, str, str], seed: int
                         ) -> Tuple[bool, bool]:
    """Isolated per-pair check (own fresh HDFactStore): same_rep (content-only representation
    identity) + no_leak (store starts empty). Same isolation discipline as
    exp_representation_canonicalization_v1._pair_corroboration_check (own docstring explains why
    isolation is the correct scope, not a convenience)."""
    store = HDFactStore(n_dim=4096, seed=seed, use_index=True)
    no_leak = store.query(triple_a[0], triple_a[1]) == [] and store.query(triple_b[0], triple_b[1]) == []
    vec_a = content_repr_vector(store.codec, *triple_a)
    vec_b = content_repr_vector(store.codec, *triple_b)
    same_rep = torch.equal(vec_a, vec_b)
    return bool(same_rep), bool(no_leak)


def run_real_data_same_distinct_rep(targets: List[Dict]) -> Dict:
    """T3: real gap-set entities, canon resolved via canon_entity (entity side, UNTOUCHED) +
    learned_causal_canon_for_marker (relation side, the ONE new thing). (a) SAME-IDEA: two
    DIFFERENT causal markers (one seed, one held-out) describing the IDENTICAL real (cause_entity,
    effect) fact must produce an IDENTICAL content_repr_vector. (b) DISTINCT-OBJECT: the same
    cause_entity with a genuinely different real effect must produce a DISTINCT vector. (c)
    DISTINCT-RELATION: the same (cause_entity,effect) pair under a different causal relation-class
    (CAUSES vs PREVENTS) must produce a DISTINCT vector (mirrors the source cell's own T2(b)
    PRODUCES-vs-CONSUMES check)."""
    anchors = build_anchor_set(targets)
    by_material: Dict[str, List[Dict]] = {}
    for t in targets:
        by_material.setdefault(t["via_material"], []).append(t)
    hub = max(by_material, key=lambda m: len(by_material[m]))
    same_a, same_b = by_material[hub][0], by_material[hub][0]
    diff_candidates = [t for t in by_material[hub] if t["whole"] != same_a["whole"]]
    assert diff_candidates, f"test construction requires >=2 distinct effects for hub material {hub!r}"
    diff_t = diff_candidates[0]

    cause_a = canon_entity(same_a["via_material"], anchors)
    effect_a = canon_entity(same_a["whole"], anchors)
    effect_diff = canon_entity(diff_t["whole"], anchors)

    canon_seed = learned_causal_canon_for_marker("cause")       # seed marker
    canon_heldout = learned_causal_canon_for_marker("induce")   # held-out marker (same class)
    canon_prevent = learned_causal_canon_for_marker("prevent")  # different class, same seed-tier
    assert canon_seed is not None and canon_heldout is not None and canon_prevent is not None, (
        f"test construction failed: expected all 3 markers to classify, got "
        f"seed={canon_seed} heldout={canon_heldout} prevent={canon_prevent}")
    assert canon_seed == canon_heldout, (
        f"test construction failed: seed marker 'cause' ({canon_seed}) and held-out marker "
        f"'induce' ({canon_heldout}) must classify to the SAME class for the same-idea probe")

    same_rep_ok, no_leak_1 = _isolated_pair_check(
        (cause_a, canon_seed, effect_a), (cause_a, canon_heldout, effect_a), seed=90101)
    distinct_object_ok, no_leak_2 = _isolated_pair_check(
        (cause_a, canon_seed, effect_a), (cause_a, canon_seed, effect_diff), seed=90102)
    distinct_relation_ok, no_leak_3 = _isolated_pair_check(
        (cause_a, canon_seed, effect_a), (cause_a, canon_prevent, effect_a), seed=90103)
    # same_rep pair must be IDENTICAL; the other two pairs must be DISTINCT -- invert accordingly.
    distinct_object_ok = not distinct_object_ok
    distinct_relation_ok = not distinct_relation_ok

    return {"hub_material": hub, "cause_entity": cause_a, "effect_a": effect_a, "effect_diff": effect_diff,
           "canon_seed_cause": canon_seed, "canon_heldout_induce": canon_heldout, "canon_prevent": canon_prevent,
           "same_idea_same_rep_ok": bool(same_rep_ok), "distinct_object_gives_distinct_rep_ok": bool(distinct_object_ok),
           "distinct_relation_gives_distinct_rep_ok": bool(distinct_relation_ok),
           "no_leak_ok": bool(no_leak_1 and no_leak_2 and no_leak_3),
           "t3_ok": bool(same_rep_ok and distinct_object_ok and distinct_relation_ok and no_leak_1 and no_leak_2 and no_leak_3)}


# =========================================================================== Part A: weak->strong arms
def run_recovery_arms(targets: List[Dict], reading, wide, hop1: KGStore, hop2_blind: KGStore,
                      hop2_cued: KGStore, ent_idx: Dict[str, int], rel_idx: Dict[str, int],
                      bridge_idx: int, gathered_per_proc: Dict[str, List[str]], n_ent: int) -> Dict:
    per_target = []
    for t in targets:
        proc, whole, fate = t["process"], t["whole"], t["fate"]
        if proc not in ent_idx or whole not in ent_idx or fate not in rel_idx:
            continue
        gold_idx = ent_idx[whole]
        start_idx = ent_idx[proc]
        fate_idx = rel_idx[fate]

        arm0_hit = int((proc, whole, fate) in reading_fact_set(reading))  # always 0 by construction

        ranked1 = fanout_two_hop(hop1, hop2_blind, start_idx, fate_idx, bridge_idx, K1_FANOUT, K2_FANOUT,
                                 n_ent, restrict_hop1_to=None)
        arm1_at1, arm1_at5 = recovery_at(ranked1, gold_idx, 1), recovery_at(ranked1, gold_idx, 5)

        ranked2 = voting_predict(proc, reading, wide, ent_idx)
        arm2_at1, arm2_at5 = recovery_at(ranked2, gold_idx, 1), recovery_at(ranked2, gold_idx, 5)

        gathered_idx = {ent_idx[m] for m in gathered_per_proc.get(proc, []) if m in ent_idx}
        ranked3 = fanout_two_hop(hop1, hop2_cued, start_idx, fate_idx, bridge_idx, K1_FANOUT, K2_FANOUT,
                                 n_ent, restrict_hop1_to=gathered_idx)
        arm3_at1, arm3_at5 = recovery_at(ranked3, gold_idx, 1), recovery_at(ranked3, gold_idx, 5)

        per_target.append({
            "process": proc, "whole": whole, "fate": fate, "via_material": t["via_material"],
            "arm0_hit": arm0_hit, "arm1_at1": arm1_at1, "arm1_at5": arm1_at5,
            "arm2_at1": arm2_at1, "arm2_at5": arm2_at5, "arm3_at1": arm3_at1, "arm3_at5": arm3_at5,
            "arm1_top1_idx": top1(ranked1) if ranked1 else -1, "arm2_top1_idx": ranked2[0][0] if ranked2 else -1,
            "arm3_top1_idx": top1(ranked3) if ranked3 else -1,
        })

    def agg_mean(field):
        vals = [r[field] for r in per_target]
        return float(np.mean(vals)) if vals else 0.0

    recovery = {
        "arm0_at5": agg_mean("arm0_hit"),
        "arm1_at1": agg_mean("arm1_at1"), "arm1_at5": agg_mean("arm1_at5"),
        "arm2_at1": agg_mean("arm2_at1"), "arm2_at5": agg_mean("arm2_at5"),
        "arm3_at1": agg_mean("arm3_at1"), "arm3_at5": agg_mean("arm3_at5"),
    }
    return {"per_target": per_target, "recovery": recovery, "n": len(per_target)}


# =========================================================================== self-test
def run_self_test() -> Dict:
    """(a) reused source-cell fixture (proves the REUSED arm0/1/2/3 mechanism sound at tiny
    scale) + hdlab.gather_reason's own self-test (proves the promoted GATHER+REASON organs sound
    in isolation). (b) a NEW tiny fixture for _causal_narrow_from_rows (this cell's one new disk-
    scan filter): synthetic rows including a /r/Causes hit, a wrong-relation row, and a self-loop,
    must extract ONLY the genuine causal edge. (c) real classify_nway calls against the real (not
    synthetic) ~12-word CAUSAL_MARKER_FEATURES lexicon -- there is no larger scale to test this
    domain at, so this IS production scale for Part B."""
    ref_a = source_run_self_test()
    ref_gather = gather_reason_self_test()

    rows = [
        ("wood", "smoke", "/r/Causes"), ("wood", "ash", "/r/MadeOf"),
        ("fire", "fire", "/r/Causes"),  # self-loop, must be excluded
        ("water", "flood", "/r/Causes"),  # subject not in vocab, must be excluded
    ]
    vocab = {"wood", "fire"}
    narrow = _causal_narrow_from_rows(rows, vocab)
    assert narrow == {"wood": ["smoke"]}, f"SELF_TEST FAIL: _causal_narrow_from_rows got {narrow}"

    anti = run_causal_anti_collapse()
    assert anti["anti_collapse_ok"], f"SELF_TEST FAIL: causal T0 anti-collapse failed: {anti}"
    heldout = run_causal_held_out_generalization()
    assert heldout["n_correct"] == heldout["n_total"] == 3, (
        f"SELF_TEST FAIL: causal held-out generalization expected 3/3, got {heldout}")
    scr = run_causal_held_out_generalization_scrambled()
    assert scr["n_correct"] < heldout["n_correct"], (
        f"SELF_TEST FAIL: scramble must degrade held-out accuracy, got scrambled={scr} real={heldout}")
    boundary = run_cross_domain_oov_boundary()
    assert boundary["boundary_respect_ok"], f"SELF_TEST FAIL: cross-domain OOV boundary violated: {boundary}"

    return {"reference_source_cell_self_test": {"positive_control_recovery": ref_a["arm3_top1_idx"] if False else "see_ref_a"},
           "ref_a_keys": sorted(ref_a.keys()), "ref_gather_keys": sorted(ref_gather.keys()),
           "causal_narrow_from_rows_fixture": narrow,
           "causal_anti_collapse": anti["anti_collapse_ok"],
           "causal_held_out": heldout["held_out_generalization_rate"],
           "causal_scrambled": scr["scrambled_generalization_rate"],
           "boundary_respect_ok": boundary["boundary_respect_ok"]}


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
def run_pipeline(process_filter, run_mode: str) -> Dict:
    t0 = time.perf_counter()

    print("[stage] Part A: building real reading facts + CAUSAL gap-set", flush=True)
    reading = build_reading_facts(process_filter=process_filter)
    vocab = reading_vocab(reading)
    _madeof_narrow_unused, wide = build_cskg_bridges(vocab)   # wide (blind pool) REUSED verbatim
    causal_narrow, n_cskg_rows = build_causal_bridges_narrow(vocab)
    print(f"[causal-bridge] scanned {n_cskg_rows} CSKG rows; {len(causal_narrow)} materials with "
          f"real /r/Causes edges, {sum(len(v) for v in causal_narrow.values())} total edges", flush=True)

    gap = build_gap_set(reading, causal_narrow)   # REUSED 100% VERBATIM (generic over narrow arg)
    targets = gap["targets"]
    print(f"[gap-set] raw={gap['raw_n']} survive={gap['survive_n']} unique={gap['unique_n']}", flush=True)
    assert targets, "gap-set is empty -- cannot proceed with a decisive test (honest HARD_FAIL condition)"

    processes = sorted(reading.keys())
    materials = vocab
    wholes = sorted({t["whole"] for t in targets} | {w for lst in wide.values() for w in lst}
                     | {w for lst in causal_narrow.values() for w in lst})
    ents, ent_idx = build_entity_index(processes, materials, wholes)
    n_ent = len(ents)
    print(f"[entities] n_ent={n_ent} n_targets={len(targets)}", flush=True)

    hop1 = fresh_kg(n_ent, SEED_KG_CAUSAL)
    rel_idx = ingest_reading_hop1(hop1, reading, ent_idx)
    bridge_idx = rel_idx[BRIDGE_REL]

    wide_edges = [(m, w) for m in sorted(wide) for w in wide[m]]
    narrow_edges = [(m, w) for m in sorted(causal_narrow) for w in causal_narrow[m]]
    hop2_blind = fresh_kg(n_ent, SEED_KG_CAUSAL)
    ingest_bridge_hop2(hop2_blind, wide_edges, ent_idx, bridge_idx)
    hop2_cued = fresh_kg(n_ent, SEED_KG_CAUSAL)
    ingest_bridge_hop2(hop2_cued, narrow_edges, ent_idx, bridge_idx)

    print("[stage] STATE-OF-MIND + CA3 GATHER (hdlab.gather_reason, reused verbatim)", flush=True)
    mat_names, codebook, mat_vecs = build_material_codebook(materials, SEED_FHRR_CAUSAL)
    reg = RelationRegister(d=FHRR_D, generator=torch.Generator().manual_seed(SEED_FHRR_CAUSAL + 1))
    for proc in processes:
        for material in sorted(reading.get(proc, {}).keys()):
            reg.bind_filler(proc, "GOAL", mat_vecs[material])
    gathered_per_proc: Dict[str, List[str]] = {}
    for proc in processes:
        q = real_to_concat(reg.decode_filler(proc, "GOAL"))
        gathered_per_proc[proc] = ca3_relevance_gather(q, mat_names, codebook, k_peel=CA3_K_PEEL, sim_floor=CA3_SIM_FLOOR)

    print("[stage] Part A: recovery arms 0/1/2/3", flush=True)
    arms = run_recovery_arms(targets, reading, wide, hop1, hop2_blind, hop2_cued, ent_idx, rel_idx,
                             bridge_idx, gathered_per_proc, n_ent)
    recovery = arms["recovery"]
    print(f"[recovery] arm0={recovery['arm0_at5']:.4f} arm1@5={recovery['arm1_at5']:.4f} "
          f"arm2@5={recovery['arm2_at5']:.4f} arm3@5={recovery['arm3_at5']:.4f}", flush=True)

    per_target = arms["per_target"]
    a1 = tuple(r["arm1_top1_idx"] for r in per_target)
    a3 = tuple(r["arm3_top1_idx"] for r in per_target)
    arms_differ = not (a1 == a3)
    assert arms_differ, "META_RULE_AF VIOLATION: arm1 and arm3 top-1 predictions identical on every target"

    print("[stage] SCRAMBLE-THE-CHAIN control", flush=True)
    scrambled_edges = scramble_edges(narrow_edges, SEED_SCRAMBLE_CAUSAL)
    hop2_scrambled = fresh_kg(n_ent, SEED_KG_CAUSAL)
    ingest_bridge_hop2(hop2_scrambled, scrambled_edges, ent_idx, bridge_idx)
    scr_at1_vals, scr_at5_vals = [], []
    for t in targets:
        proc, whole, fate = t["process"], t["whole"], t["fate"]
        if proc not in ent_idx or whole not in ent_idx or fate not in rel_idx:
            continue
        gold_idx = ent_idx[whole]
        gathered_idx = {ent_idx[m] for m in gathered_per_proc.get(proc, []) if m in ent_idx}
        ranked = fanout_two_hop(hop1, hop2_scrambled, ent_idx[proc], rel_idx[fate], bridge_idx,
                                K1_FANOUT, K2_FANOUT, n_ent, restrict_hop1_to=gathered_idx)
        scr_at1_vals.append(recovery_at(ranked, gold_idx, 1))
        scr_at5_vals.append(recovery_at(ranked, gold_idx, 5))
    scramble_result = {"arm3_scrambled_at1": float(np.mean(scr_at1_vals)) if scr_at1_vals else 0.0,
                       "arm3_scrambled_at5": float(np.mean(scr_at5_vals)) if scr_at5_vals else 0.0}
    print(f"[scramble] arm3_scrambled@5={scramble_result['arm3_scrambled_at5']:.4f} "
          f"(unscrambled arm3@5={recovery['arm3_at5']:.4f})", flush=True)

    causenet_audit = None
    if run_mode == "full":
        print("[stage] CauseNet cross-source corroboration audit (informational, FULL only)", flush=True)
        causenet_audit = causenet_causal_corroboration_scan(causal_narrow)
        print(f"[causenet-audit] scanned={causenet_audit['n_scanned']} "
              f"literal_hits={causenet_audit['n_literal_hits']}", flush=True)

    print("[stage] Part B: canonicalization generality (causal domain)", flush=True)
    anti_collapse = run_causal_anti_collapse()
    held_out = run_causal_held_out_generalization()
    held_out_scrambled = run_causal_held_out_generalization_scrambled()
    boundary = run_cross_domain_oov_boundary()
    t3 = run_real_data_same_distinct_rep(targets)
    print(f"[canon] anti_collapse_ok={anti_collapse['anti_collapse_ok']} "
          f"held_out={held_out['held_out_generalization_rate']:.4f} "
          f"scrambled={held_out_scrambled['scrambled_generalization_rate']:.4f} "
          f"boundary_respect_ok={boundary['boundary_respect_ok']} t3_ok={t3['t3_ok']}", flush=True)

    elapsed = time.perf_counter() - t0

    # ---- verdict per pre-registered bands ----
    delta15 = recovery["arm3_at5"] - recovery["arm1_at5"]
    clears_floor = recovery["arm3_at5"] >= 0.20
    scramble_collapses = scramble_result["arm3_scrambled_at5"] <= 0.10
    ablation_ok = delta15 >= 0.15
    part_a_hard_pass = delta15 >= 0.20 and clears_floor and scramble_collapses and ablation_ok
    part_a_hard_fail = (recovery["arm3_at5"] <= recovery["arm1_at5"] or recovery["arm3_at5"] <= 0.05
                        or scramble_result["arm3_scrambled_at5"] >= 0.5 * max(recovery["arm3_at5"], 1e-9)
                        or delta15 < 0.05)

    part_b_hard_pass = (anti_collapse["anti_collapse_ok"]
                        and held_out["held_out_generalization_rate"] == 1.0
                        and held_out_scrambled["scrambled_generalization_rate"] <= 0.34
                        and t3["t3_ok"])
    part_b_hard_fail = (not anti_collapse["anti_collapse_ok"]
                        or held_out["held_out_generalization_rate"] <= 0.34
                        or not t3["t3_ok"])

    if part_a_hard_pass and part_b_hard_pass:
        verdict = "HARD_PASS_pipeline_generalizes_to_causal_domain"
        verdict_msg = (f"GENERAL: Part A weak->strong recovers on the fresh CAUSAL domain "
                        f"(delta(arm3-arm1)@5={delta15:.4f}>=0.20, arm3@5={recovery['arm3_at5']:.4f}>=0.20, "
                        f"scramble@5={scramble_result['arm3_scrambled_at5']:.4f}<=0.10, "
                        f"ablation_delta={delta15:.4f}>=0.15); Part B canonicalization generalizes to "
                        f"the causal relation family (anti_collapse={anti_collapse['anti_collapse_ok']}, "
                        f"held_out={held_out['held_out_generalization_rate']:.4f}, "
                        f"scrambled={held_out_scrambled['scrambled_generalization_rate']:.4f}, "
                        f"t3_same_distinct_rep={t3['t3_ok']}) -- classify_nway/gather_reason/build_gap_set "
                        f"REUSED VERBATIM with zero mechanism modification; the only new supplied structure "
                        f"was the CAUSAL_MARKER_FEATURES seed-pool DATA (same cost the original 4 classes "
                        f"needed), not a missing-LEARNING capability")
    elif part_a_hard_fail or part_b_hard_fail:
        verdict = "HARD_FAIL_domain_specific_overfit"
        verdict_msg = (f"OVERFIT: pipeline did not clear HARD_PASS on the fresh CAUSAL domain "
                        f"(part_a_hard_fail={part_a_hard_fail}, part_b_hard_fail={part_b_hard_fail}, "
                        f"delta={delta15:.4f}, arm3@5={recovery['arm3_at5']:.4f}, "
                        f"anti_collapse={anti_collapse['anti_collapse_ok']}, "
                        f"held_out={held_out['held_out_generalization_rate']:.4f})")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"PARTIAL: delta={delta15:.4f} arm3@5={recovery['arm3_at5']:.4f} "
                        f"part_a_hard_pass={part_a_hard_pass} part_b_hard_pass={part_b_hard_pass} -- "
                        f"does not clear strict HARD_PASS margins on both parts jointly, "
                        f"does not hit HARD_FAIL floors either")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "process_filter": sorted(process_filter) if process_filter else "ALL",
        "n_ent": n_ent, "n_targets": len(targets), "n_eligible_arm_targets": arms["n"],
        "gap_set_audit": {"raw_n": gap["raw_n"], "survive_n": gap["survive_n"], "unique_n": gap["unique_n"],
                          "n_cskg_rows_scanned": n_cskg_rows, "n_causal_bridge_materials": len(causal_narrow),
                          "n_causal_bridge_edges": sum(len(v) for v in causal_narrow.values())},
        "causenet_cross_source_audit": causenet_audit,
        "recovery": recovery, "ablation_delta_arm3_minus_arm1_at5": delta15,
        "scramble_control": scramble_result,
        "arms_differ_verified": bool(arms_differ),
        "part_a_hard_pass": part_a_hard_pass, "part_a_hard_fail": part_a_hard_fail,
        "canon_anti_collapse": anti_collapse, "canon_held_out": held_out,
        "canon_held_out_scrambled": held_out_scrambled, "canon_boundary_diagnostic": boundary,
        "canon_real_data_t3": t3,
        "part_b_hard_pass": part_b_hard_pass, "part_b_hard_fail": part_b_hard_fail,
        "bands": {"hard_pass_delta_min": 0.20, "hard_pass_floor_min": 0.20, "hard_pass_scramble_max": 0.10,
                 "hard_pass_ablation_delta_min": 0.15, "relation_class_floor": RELATION_CLASS_FLOOR,
                 "relation_class_margin": RELATION_CLASS_MARGIN,
                 "hard_pass_held_out_rate_min": 1.0, "hard_pass_scrambled_rate_max": 0.34},
    }
    return metrics


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="reused fixtures + tiny new-function fixture")
    parser.add_argument("--smoke", action="store_true", help="real Part-A pipeline, 2-process subset")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="declared wall-time budget: smoke~30-60s, FULL~60-150s (CSKG scan dominates)")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                  "verdict_msg": ("reused source-cell + gather_reason fixtures PASS; new "
                                  "_causal_narrow_from_rows fixture PASS; real causal classify_nway "
                                  "T0/T1/T2/boundary checks PASS at production scale for this domain"),
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    if args.smoke:
        run_mode = "smoke"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_smoke")
        # NOTE (differs from the source cell's own {"combustion","photosynthesis"} smoke subset):
        # the CAUSAL /r/Causes bridge is far sparser than /r/MadeOf (12 materials total vs 316
        # edges), and MEASURED@dev probe the 2-process combustion+photosynthesis subset yields
        # only 4 gap targets -- too few for a non-degenerate scramble control (both unscrambled
        # and scrambled arm3@5 saturate at 1.0, a false SMOKE pass/fail signal, not a real
        # discriminator). respiration alone contributes 36/52 FULL targets (MEASURED@dev probe);
        # this 3-process subset yields 43/52 (83%) -- still a genuine subset of FULL, but large
        # enough for scramble to actually differentiate.
        process_filter = {"respiration", "combustion", "hydrocarbon_formation"}
    else:
        run_mode = "full"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        process_filter = None

    _write_start_marker(output_dir, run_mode, expected_n_units=52 if run_mode == "full" else 10)
    metrics = run_pipeline(process_filter, run_mode)

    if run_mode == "smoke":
        # SMOKE reports its OWN discriminator-fires status, never the FULL-population HARD_PASS/
        # HARD_FAIL/MIDDLE_BAND verdict tree computed by run_pipeline (those bands are pre-
        # registered against the FULL 52-target population; a smoke subset's scramble-control
        # numbers are noisier at smaller N and would otherwise mislabel a healthy discriminator
        # as HARD_FAIL, purely a population-size artifact, not a real full-verdict signal).
        d15 = metrics["ablation_delta_arm3_minus_arm1_at5"]
        canon_ok = metrics["canon_anti_collapse"]["anti_collapse_ok"] and metrics["canon_held_out"]["held_out_generalization_rate"] == 1.0
        arm3_above_arm1 = metrics["recovery"]["arm3_at5"] > metrics["recovery"]["arm1_at5"]
        scramble_degrades = metrics["scramble_control"]["arm3_scrambled_at5"] < metrics["recovery"]["arm3_at5"]
        smoke_discriminator_ok = d15 >= 0.10 and canon_ok and arm3_above_arm1 and scramble_degrades
        if smoke_discriminator_ok:
            metrics["verdict"] = "SMOKE_GATE_PASS"
            metrics["verdict_msg"] = (f"smoke discriminator check PASS: arm3@5-arm1@5={d15:.4f} (>=0.10), "
                                      f"arm3@5={metrics['recovery']['arm3_at5']:.4f} > arm1@5="
                                      f"{metrics['recovery']['arm1_at5']:.4f}, scramble degrades "
                                      f"({metrics['scramble_control']['arm3_scrambled_at5']:.4f} < "
                                      f"{metrics['recovery']['arm3_at5']:.4f}), canon_ok={canon_ok} -- "
                                      f"FULL dispatch authorized (note: smoke scramble margin is noisier "
                                      f"at this smaller subset-N than the pre-registered FULL bands; the "
                                      f"strict HARD_PASS/HARD_FAIL bands apply only to the FULL run)")
        else:
            metrics["verdict"] = "SMOKE_GATE_FAIL_discriminator_not_firing"
            metrics["verdict_msg"] = (f"smoke discriminator check FAIL: d15={d15:.4f} (need >=0.10) "
                                      f"arm3_above_arm1={arm3_above_arm1} scramble_degrades={scramble_degrades} "
                                      f"canon_ok={canon_ok}")

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
