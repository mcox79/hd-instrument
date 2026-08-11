# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified analog: anti_collapse_ok (T0) -- leave-one-out classification of every
#   seed marker must recover its true class, and PRODUCES/CONSUMES must never cross-classify
# - final_metrics_atomicity = tmp_replace (single-shot)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: discrete classification-accuracy gates, not a Gaussian noise-floor metric;
#   discriminator_reachability=TRUE argued via axis-overlap arithmetic (within-class mean sim
#   ~0.75-0.88 vs cross-class ~0.06-0.35, RELATION_CLASS_FLOOR=0.50 / MARGIN=0.15 set BEFORE
#   running) and EMPIRICALLY CONFIRMED in this cell's own self-test
# - baseline_in_band: N/A (representation-identity/classification-accuracy test, not a
#   baseline-vs-mechanism accuracy gap)
# - discriminator survives scale: T1(b) runs the REAL FULL population (121 gaps), not a toy subset
# - HP_SCOPE: T0/T2 (closed-form) and T1 (real-data reproduction) gates apply jointly to the
#   overall verdict; no arm is exempted (see preregs/2026-08-11_relation_canonicalization_
#   learned_v1.md verdict tree)
# - cardinality_ok: EXPECTED = 12 seed leave-one-out probes (T0) + 4 held-out probes x 2
#   (real + scrambled, T2) + parent's full real-data population (121 gaps, T1) -- every count
#   logged, verdict counts checked against population size
# - per-unit failure-class instrumentation: N/A (single deterministic pass per test group)
# - calibration_check: default_ok_for_this_regime (RELATION_CLASS_FLOOR/MARGIN set from
#   axis-overlap arithmetic before running, never tuned post-hoc)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL HDFactStore objects + calls the REAL classify_nway/mean_similarity_
#   to_seeds organs at tiny scale (real_code_path)
# - substrate_signature_checked: HDFactStore(n_dim,seed) base kwargs only; hdlab/
#   verb_lexical_similarity.py is the ONE hdlab/ file this cell's task additively extends (new
#   DATA + classify_nway only, zero existing lines changed, existing self_test() untouched)
"""exp_relation_canonicalization_learned_v1 -- EARNS the relation-canonicalization mapping the
SAME way exp_representation_canonicalization_v1 (commit e65de60f1, HARD_PASS) earned entity-
canonicalization: cluster/classify surface relation-markers into canonical relation classes
(PART_OF/PRODUCES/CONSUMES/MOVES) via verb-similarity (hdlab.verb_lexical_similarity, extended
additively with a new "relation" domain), instead of a hand-authored `marker -> canon` dict.

STEP-0 HONEST RE-READ (task premise correction, see pre-reg for the full disclosure): the task
brief names `RELATION_DIRECTION_TABLE` as "the" hand table. On disk inspection, that dict is
DECLARED in e65de60f1 (lines 131-141) but never referenced again anywhere in that 843-line file --
dead/vestigial documentation, not the live mechanism. The ACTUALLY-EXECUTED hand-authored mapping
is `KB_ROLE_TO_CANON` (a 3-entry dict, used once) PLUS the canonical-class constant hard-coded
directly as a return value inside each `extract_*_triple` function. The task's underlying
diagnosis is still correct (relation-class identity is hand-authored, unlike the learned entity
path); only the specific artifact name is corrected. This cell replaces BOTH.

REUSE (wire-don't-island):
  hdlab.verb_lexical_similarity: RELATION_SEED_POOLS / RELATION_HELDOUT_POOLS / RELATION_CANON_
    CLASSES / RELATION_MARKER_FEATURES (NEW data, additive) + classify_nway (NEW generic function,
    additive) + mean_similarity_to_seeds / in_lexicon / _feature_vectors / _concept_vector_from /
    _cos_complex (existing, reused verbatim for the scramble-control recipe, same convention as
    every scramble control in this codebase) + self_test (existing, called unchanged as a
    regression witness -- its own coverage loop hardcodes ("outcome","goal"), so it is BYTE-
    IDENTICAL before/after this file's additive extension).
  experiments.exp_representation_canonicalization_v1 (READ-ONLY imports): CANON_PART_OF/PRODUCES/
    CONSUMES/MOVES, canon_entity, build_anchor_set, content_repr_vector, render_composes,
    render_partof, _pair_corroboration_check. RELATION_DIRECTION_TABLE is imported ONLY as a
    grading/comparison reference in the self-test (never as an input to any computation).
  experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1 / exp_three_tier_loop_genuine_
    cross_source_corroboration_v1: same real-data pipeline functions the parent cell reuses,
    imported verbatim.
  hdlab.hd_fact_store.HDFactStore / hdlab.lexical_similarity.self_test / hdlab.grounding_
    acquisition_loop.self_test / hdlab.prelim_tier.self_test -- core-preserved regression witnesses
    (identical convention to the parent cell).

THE ONE NEW THING (honestly disclosed): (a) the hdlab/verb_lexical_similarity.py "relation" domain
extension (data + classify_nway, additive, see that file's own new section); (b)
LEARNED_MARKER_TABLE + _apply_canon_order (this cell owns this SUPPLIED-STRUCTURE remainder --
which literal marker-word a template uses + whether its surface argument order needs swapping --
the task explicitly sanctions this staying supplied while the relation-CLASS mapping is learned);
(c) the _learned extraction-function family (regex-identical to the parent cell's extract_*
functions, canon computed via learned_canon_for_marker instead of a hard-coded literal).

SCOPE (honestly declared): same real-data population as the parent cell (CSKG wave0 + KB-role-
schema wave2 axes; CauseNet out of scope, same reason as the parent). Entity-canonicalization
(`canon_entity`/`concept_similarity`) is UNTOUCHED by this cell -- it was already earned in
e65de60f1; this cell's entire contribution is the RELATION side.

Modes: --self-test (closed-form fixtures + a 1-marker held-out smoke, <10s) / (no flag, default) =
FULL (real pipeline, same population as the parent cell's FULL run; MEASURED elapsed_s=13.28 on
that population for the parent cell, so a single-mode run comfortably fits the ~2min local budget
without a separate smoke/full split).

ASCII-only. Deterministic throughout (sorted(set()) discipline; fixed integer seeds; no built-in
hash() anywhere -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import ast
import json
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import torch

ANCHOR_NAME = "relation_canonicalization_learned_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.verb_lexical_similarity import (  # noqa: E402
    RELATION_SEED_POOLS, RELATION_HELDOUT_POOLS, RELATION_CANON_CLASSES, RELATION_MARKER_FEATURES,
    classify_nway, mean_similarity_to_seeds, in_lexicon as verb_in_lexicon,
    self_test as verb_lexical_similarity_self_test,
    _feature_vectors as _verb_feature_vectors,          # scramble-control recipe reuse only
    _concept_vector_from as _verb_concept_vector_from,  # scramble-control recipe reuse only
    _cos_complex as _verb_cos_complex,                  # scramble-control recipe reuse only
)
from hdlab.lexical_similarity import self_test as lexical_similarity_self_test  # noqa: E402
from hdlab.hd_fact_store import HDFactStore, _run_all_selftests as hd_fact_store_self_test  # noqa: E402

from experiments.exp_representation_canonicalization_v1 import (  # noqa: E402
    CANON_PART_OF, CANON_PRODUCES, CANON_CONSUMES, CANON_MOVES, RELATION_DIRECTION_TABLE,
    canon_entity, build_anchor_set, content_repr_vector, render_composes, render_partof,
    _pair_corroboration_check,
)
from experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1 import (  # noqa: E402
    build_reading_facts, reading_vocab, build_cskg_bridges, build_gap_set,
)
from experiments.exp_three_tier_loop_genuine_cross_source_corroboration_v1 import (  # noqa: E402
    build_genuine_waves, compute_cskg_extra, compute_kb_role_hits,
)

RELATION_CLASS_FLOOR = 0.50
RELATION_CLASS_MARGIN = 0.15

_LABEL_TO_CANON = {"PART_OF": CANON_PART_OF, "PRODUCES": CANON_PRODUCES,
                   "CONSUMES": CANON_CONSUMES, "MOVES": CANON_MOVES}
_CANON_TO_LABEL = {v: k for k, v in _LABEL_TO_CANON.items()}

# ---- SUPPLIED STRUCTURE (task-sanctioned remainder): which literal marker a template uses + its
# swap direction. NO canon field here -- class identity is COMPUTED, never looked up. ------------
LEARNED_MARKER_TABLE = {
    "cskg_madeof":            {"marker": "made_of",   "swap": True},
    "paraphrase_composes":    {"marker": "compose",   "swap": False},   # HELD-OUT marker
    "paraphrase_partof":      {"marker": "part_of",   "swap": False},
    "kb_produces":            {"marker": "produce",   "swap": False},
    "kb_consumes":            {"marker": "consume",   "swap": False},
    "kb_moves":               {"marker": "move",      "swap": False},
    "kb_paraphrase_produces": {"marker": "generate",  "swap": True},    # HELD-OUT marker
    "kb_paraphrase_consumes": {"marker": "require",   "swap": True},    # HELD-OUT marker
    "kb_paraphrase_moves":    {"marker": "transport", "swap": True},    # HELD-OUT marker
}
_KB_ROLE_TEMPLATE_KEY = {"produces": "kb_produces", "consumes": "kb_consumes", "moves": "kb_moves"}
_CANON_TO_PARAPHRASE_TEMPLATE_KEY = {CANON_PRODUCES: "kb_paraphrase_produces",
                                     CANON_CONSUMES: "kb_paraphrase_consumes",
                                     CANON_MOVES: "kb_paraphrase_moves"}
_PARAPHRASE_RENDER_LEARNED = {
    "kb_paraphrase_produces": lambda m, p: f"process {p} generates {m} as an output.",
    "kb_paraphrase_consumes": lambda m, p: f"process {p} requires {m} as an input.",
    "kb_paraphrase_moves":    lambda m, p: f"process {p} transports {m} along its pathway.",
}
_KB_PARAPHRASE_PATTERN_LEARNED = {
    "kb_paraphrase_produces": re.compile(r"^process (\S+) generates (\S+) as an output\.$"),
    "kb_paraphrase_consumes": re.compile(r"^process (\S+) requires (\S+) as an input\.$"),
    "kb_paraphrase_moves":    re.compile(r"^process (\S+) transports (\S+) along its pathway\.$"),
}


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def _apply_canon_order(arg_a: str, canon: str, arg_b: str, swap: bool) -> Tuple[str, str, str]:
    """Shared helper replacing the per-function hard-coded canon literals: swap=False -> canonical
    (arg_a, canon, arg_b); swap=True -> canonical (arg_b, canon, arg_a)."""
    return (arg_b, canon, arg_a) if swap else (arg_a, canon, arg_b)


# =========================================================================== LEARNED classifier
def learned_canon_for_marker(marker: str, seed_pools: Optional[Dict[str, List[str]]] = None
                             ) -> Optional[str]:
    """LEARNED relation-class lookup: verb-similarity argmax over the 4 canonical seed pools
    (hdlab.verb_lexical_similarity.classify_nway), the SAME organ + SAME convention entity
    canonicalization already uses via concept_similarity. NO hand dict maps marker->canon; the
    canon is COMPUTED. Returns None (abstain) if OOV / below floor / margin too thin -- never
    forces a guess."""
    pools = seed_pools if seed_pools is not None else {
        lbl: list(d.keys()) for lbl, d in RELATION_SEED_POOLS.items()}
    label = classify_nway(marker, pools, domain="relation",
                          floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)
    return None if label is None else _LABEL_TO_CANON[label]


def learned_canon_leave_one_out(marker: str, true_label: str) -> Optional[str]:
    """Classify `marker` using every OTHER seed in its own pool + all seeds of the other 3 pools
    (marker itself excluded) -- the leave-one-out anti-collapse probe (T0)."""
    pools = {}
    for lbl, d in RELATION_SEED_POOLS.items():
        pools[lbl] = [k for k in d.keys() if not (lbl == true_label and k == marker)]
    return classify_nway(marker, pools, domain="relation",
                         floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)


# =========================================================================== T0: anti-collapse
def run_anti_collapse_marker_classes() -> Dict:
    per_marker = {}
    for true_label, pool in RELATION_SEED_POOLS.items():
        for marker in sorted(pool.keys()):
            got = learned_canon_leave_one_out(marker, true_label)
            got_label = _CANON_TO_LABEL.get(got) if got is not None else None
            per_marker[marker] = {"true_label": true_label, "predicted_label": got_label,
                                  "correct": got_label == true_label}
    n_correct = sum(1 for r in per_marker.values() if r["correct"])
    n_total = len(per_marker)
    produces_never_consumes = all(
        r["predicted_label"] != "CONSUMES" for r in per_marker.values() if r["true_label"] == "PRODUCES")
    consumes_never_produces = all(
        r["predicted_label"] != "PRODUCES" for r in per_marker.values() if r["true_label"] == "CONSUMES")
    return {"per_marker": per_marker, "n_correct": n_correct, "n_total": n_total,
           "accuracy": n_correct / n_total if n_total else 0.0,
           "produces_never_consumes_ok": bool(produces_never_consumes),
           "consumes_never_produces_ok": bool(consumes_never_produces),
           "anti_collapse_ok": bool(n_correct == n_total and produces_never_consumes
                                    and consumes_never_produces)}


# =========================================================================== T2: held-out generalization
def _structural_no_leak_ok() -> bool:
    seed_words = {m for d in RELATION_SEED_POOLS.values() for m in d.keys()}
    heldout_words = {m for d in RELATION_HELDOUT_POOLS.values() for m in d.keys()}
    return seed_words.isdisjoint(heldout_words)


def run_held_out_generalization() -> Dict:
    pools = {lbl: list(d.keys()) for lbl, d in RELATION_SEED_POOLS.items()}
    per_marker = {}
    for true_label, hd in RELATION_HELDOUT_POOLS.items():
        for marker in sorted(hd.keys()):
            sims = {lbl: mean_similarity_to_seeds(marker, pools[lbl], "relation")
                    for lbl in RELATION_CANON_CLASSES}
            label = classify_nway(marker, pools, domain="relation",
                                  floor=RELATION_CLASS_FLOOR, margin=RELATION_CLASS_MARGIN)
            ranked = sorted(sims.items(), key=lambda kv: -kv[1])
            margin = ranked[0][1] - ranked[1][1]
            per_marker[marker] = {"true_label": true_label, "predicted_label": label,
                                  "correct": label == true_label,
                                  "sims": {k: round(v, 4) for k, v in sims.items()},
                                  "margin": round(margin, 4)}
    n_correct = sum(1 for r in per_marker.values() if r["correct"])
    n_total = len(per_marker)
    return {"per_marker": per_marker, "n_correct": n_correct, "n_total": n_total,
           "held_out_generalization_rate": n_correct / n_total if n_total else 0.0}


def _scrambled_relation_sim_fn():
    """Byte-identical scramble recipe to every other self_test/scramble control in this codebase:
    fixed-seed (999) permutation of the word->feature-set assignment. Corrupts the verb-similarity
    signal without touching the shared hdlab module."""
    words = sorted(RELATION_MARKER_FEATURES.keys())
    gen = torch.Generator().manual_seed(999)
    perm = torch.randperm(len(words), generator=gen).tolist()
    scrambled_map = {words[i]: RELATION_MARKER_FEATURES[words[perm[i]]] for i in range(len(words))}
    fv = _verb_feature_vectors("relation")

    def scrambled_mean_sim(word: str, seed_words: List[str]) -> Optional[float]:
        if word not in scrambled_map:
            return None
        wv = _verb_concept_vector_from(scrambled_map[word], fv)
        sims = [_verb_cos_complex(wv, _verb_concept_vector_from(scrambled_map[s], fv))
                for s in seed_words if s in scrambled_map]
        return sum(sims) / len(sims) if sims else None

    return scrambled_mean_sim


def run_held_out_generalization_scrambled() -> Dict:
    pools = {lbl: list(d.keys()) for lbl, d in RELATION_SEED_POOLS.items()}
    scrambled_sim = _scrambled_relation_sim_fn()
    per_marker = {}
    for true_label, hd in RELATION_HELDOUT_POOLS.items():
        for marker in sorted(hd.keys()):
            sims = {lbl: scrambled_sim(marker, pools[lbl]) for lbl in RELATION_CANON_CLASSES}
            ranked = sorted(sims.items(), key=lambda kv: -kv[1])
            best_label, best = ranked[0]
            second = ranked[1][1]
            predicted = (best_label if (best >= RELATION_CLASS_FLOOR
                                        and (best - second) >= RELATION_CLASS_MARGIN) else None)
            per_marker[marker] = {"true_label": true_label, "predicted_label": predicted,
                                  "correct": predicted == true_label}
    n_correct = sum(1 for r in per_marker.values() if r["correct"])
    n_total = len(per_marker)
    return {"per_marker": per_marker, "n_correct": n_correct, "n_total": n_total,
           "scrambled_generalization_rate": n_correct / n_total if n_total else 0.0}


# =========================================================================== T1: learned extraction (regex-identical to parent cell)
def extract_cskg_triple_learned(text: str) -> Optional[Tuple[str, str, str]]:
    m = re.match(r"^CSKG external knowledge base records that (\S+) bridges to (\S+) "
                r"via relation\(s\) (\[.*\])\.$", text)
    if not m:
        return None
    whole, material, rels_repr = m.group(1), m.group(2), m.group(3)
    rels = ast.literal_eval(rels_repr)
    if "/r/MadeOf" not in rels:
        return None
    entry = LEARNED_MARKER_TABLE["cskg_madeof"]
    canon = learned_canon_for_marker(entry["marker"])
    if canon is None:
        return None
    return _apply_canon_order(whole, canon, material, entry["swap"])


def extract_composes_triple_learned(text: str) -> Optional[Tuple[str, str, str]]:
    m = re.match(r"^(\S+) composes (\S+)\.$", text)
    if not m:
        return None
    material, whole = m.group(1), m.group(2)
    entry = LEARNED_MARKER_TABLE["paraphrase_composes"]
    canon = learned_canon_for_marker(entry["marker"])
    if canon is None:
        return None
    return _apply_canon_order(material, canon, whole, entry["swap"])


def extract_partof_triple_learned(text: str) -> Optional[Tuple[str, str, str]]:
    m = re.match(r"^(\S+) is part of (\S+)\.$", text)
    if not m:
        return None
    material, whole = m.group(1), m.group(2)
    entry = LEARNED_MARKER_TABLE["paraphrase_partof"]
    canon = learned_canon_for_marker(entry["marker"])
    if canon is None:
        return None
    return _apply_canon_order(material, canon, whole, entry["swap"])


def extract_kb_role_triples_learned(text: str) -> List[Tuple[str, str, str]]:
    m = re.match(r"^ProPara process physics KB lists (\S+) among the (\[.*\]) "
                r"terms for process (\S+)\.$", text)
    if not m:
        return []
    material, roles_repr, process = m.group(1), m.group(2), m.group(3)
    roles = ast.literal_eval(roles_repr)
    out = []
    for r in roles:
        key = _KB_ROLE_TEMPLATE_KEY.get(r)
        if key is None:
            continue
        entry = LEARNED_MARKER_TABLE[key]
        canon = learned_canon_for_marker(entry["marker"])
        if canon is None:
            continue
        out.append(_apply_canon_order(material, canon, process, entry["swap"]))
    return out


def extract_kb_paraphrase_triple_learned(text: str, template_key: str) -> Optional[Tuple[str, str, str]]:
    pat = _KB_PARAPHRASE_PATTERN_LEARNED[template_key]
    m = pat.match(text)
    if not m:
        return None
    process, material = m.group(1), m.group(2)
    entry = LEARNED_MARKER_TABLE[template_key]
    canon = learned_canon_for_marker(entry["marker"])
    if canon is None:
        return None
    return _apply_canon_order(process, canon, material, entry["swap"])


# =========================================================================== T1: real-data reproduction
def run_real_data_tests_learned(targets: List[Dict], waves_by_pk: Dict[str, List[Tuple[int, str, str]]]) -> Dict:
    anchors = build_anchor_set(targets)

    seen_mw = set()
    part_of_pairs = []
    idx = 0
    for pk, gw in sorted(waves_by_pk.items()):
        cskg_text = next((g[2] for g in gw if g[1] == "cskg"), None)
        if cskg_text is None:
            continue
        real_triple = extract_cskg_triple_learned(cskg_text)
        if real_triple is None:
            continue
        material, _, whole = real_triple
        if (material, whole) in seen_mw:
            continue
        seen_mw.add((material, whole))
        para_text = render_composes(material, whole) if idx % 2 == 0 else render_partof(material, whole)
        para_triple = (extract_composes_triple_learned(para_text) if idx % 2 == 0
                      else extract_partof_triple_learned(para_text))
        if para_triple is None:
            idx += 1
            part_of_pairs.append({"pk": pk, "material": material, "whole": whole,
                                  "same_rep": False, "no_leak_ok": True, "consistent_dup": False,
                                  "extraction_failed": True})
            continue
        same_rep, no_leak, consistent_dup = _pair_corroboration_check(
            real_triple, para_triple, anchors, seed=95200 + idx)
        idx += 1
        part_of_pairs.append({"pk": pk, "material": material, "whole": whole,
                              "same_rep": same_rep, "no_leak_ok": no_leak,
                              "consistent_dup": consistent_dup, "extraction_failed": False})

    kb_pairs = []
    kb_idx = 0
    for pk, gw in sorted(waves_by_pk.items()):
        kb_text = next((g[2] for g in gw if g[1] == "kb_role_schema"), None)
        if kb_text is None:
            continue
        real_triples = extract_kb_role_triples_learned(kb_text)
        for (rm, rr, rp) in real_triples:
            template_key = _CANON_TO_PARAPHRASE_TEMPLATE_KEY.get(rr)
            kb_idx += 1
            if template_key is None:
                kb_pairs.append({"pk": pk, "material": rm, "process": rp, "relation": rr,
                                 "same_rep": False, "no_leak_ok": True, "consistent_dup": False,
                                 "extraction_failed": True})
                continue
            para_text = _PARAPHRASE_RENDER_LEARNED[template_key](rm, rp)
            para_triple = extract_kb_paraphrase_triple_learned(para_text, template_key)
            if para_triple is None:
                kb_pairs.append({"pk": pk, "material": rm, "process": rp, "relation": rr,
                                 "same_rep": False, "no_leak_ok": True, "consistent_dup": False,
                                 "extraction_failed": True})
                continue
            same_rep, no_leak, consistent_dup = _pair_corroboration_check(
                (rm, rr, rp), para_triple, anchors, seed=96200 + kb_idx)
            kb_pairs.append({"pk": pk, "material": rm, "process": rp, "relation": rr,
                             "same_rep": same_rep, "no_leak_ok": no_leak,
                             "consistent_dup": consistent_dup, "extraction_failed": False})

    canon_triples = [(canon_entity(m, anchors), CANON_PART_OF, canon_entity(w, anchors)) for (m, w) in seen_mw]
    n_distinct_pairs = len(seen_mw)
    n_distinct_canon_triples = len(set(canon_triples))
    cross_gap_no_collision = (n_distinct_canon_triples == n_distinct_pairs)

    n_partof_pairs = len(part_of_pairs)
    n_partof_same_rep = sum(1 for r in part_of_pairs if r["same_rep"])
    n_partof_dup = sum(1 for r in part_of_pairs if r["consistent_dup"])
    n_partof_failed = sum(1 for r in part_of_pairs if r["extraction_failed"])
    n_kb_pairs = len(kb_pairs)
    n_kb_same_rep = sum(1 for r in kb_pairs if r["same_rep"])
    n_kb_dup = sum(1 for r in kb_pairs if r["consistent_dup"])
    n_kb_failed = sum(1 for r in kb_pairs if r["extraction_failed"])
    real_data_no_leak_ok = all(r["no_leak_ok"] for r in part_of_pairs) and all(r["no_leak_ok"] for r in kb_pairs)

    n_total_pairs = n_partof_pairs + n_kb_pairs
    n_total_same_rep = n_partof_same_rep + n_kb_same_rep
    n_total_dup = n_partof_dup + n_kb_dup
    n_total_failed = n_partof_failed + n_kb_failed

    return {
        "n_distinct_material_whole_pairs": n_distinct_pairs,
        "n_distinct_canon_triples": n_distinct_canon_triples,
        "cross_gap_no_collision": bool(cross_gap_no_collision),
        "real_data_no_leak_ok": bool(real_data_no_leak_ok),
        "n_partof_pairs": n_partof_pairs, "n_partof_same_rep": n_partof_same_rep,
        "n_partof_consistent_dup": n_partof_dup, "n_partof_extraction_failed": n_partof_failed,
        "n_kb_pairs": n_kb_pairs, "n_kb_same_rep": n_kb_same_rep,
        "n_kb_consistent_dup": n_kb_dup, "n_kb_extraction_failed": n_kb_failed,
        "n_total_pairs": n_total_pairs, "n_total_same_rep": n_total_same_rep,
        "n_total_dup": n_total_dup, "n_total_extraction_failed": n_total_failed,
        "real_data_same_idea_rate": (n_total_same_rep / n_total_pairs) if n_total_pairs else 0.0,
        "real_data_corroboration_rate": (n_total_dup / n_total_pairs) if n_total_pairs else 0.0,
    }


# =========================================================================== self-test
def run_self_test() -> Dict:
    lex_result = lexical_similarity_self_test()
    hdfs_result = hd_fact_store_self_test()
    verb_result = verb_lexical_similarity_self_test()

    assert _structural_no_leak_ok(), "LEAK: a held-out marker is present in a seed pool"

    # T0 anti-collapse (mandatory, checked first)
    anti = run_anti_collapse_marker_classes()
    assert anti["anti_collapse_ok"], anti

    # T2 held-out generalization (1-marker smoke: "compose" -> PART_OF, matches the parent cell's
    # own worked example marker) -- full 4/4 battery runs in main(), this is the fast self-test gate
    pools = {lbl: list(d.keys()) for lbl, d in RELATION_SEED_POOLS.items()}
    got = learned_canon_for_marker("compose", pools)
    assert got == CANON_PART_OF, f"SELF_TEST FAIL: held-out 'compose' must classify PART_OF, got {got}"

    # direction-handling boundary: opposite surface orders (whole,material) vs (material,whole)
    # must resolve to the IDENTICAL canonical triple -- reproduces the parent cell's own worked
    # example WITHOUT any hand canon table.
    real_text = "CSKG external knowledge base records that wood bridges to cellulose via relation(s) ['/r/MadeOf']."
    real_triple = extract_cskg_triple_learned(real_text)
    assert real_triple == ("cellulose", CANON_PART_OF, "wood"), real_triple
    para_text = render_composes("cellulose", "wood")
    assert para_text == "cellulose composes wood.", para_text
    para_triple = extract_composes_triple_learned(para_text)
    assert para_triple == real_triple, (real_triple, para_triple)

    store = HDFactStore(n_dim=2048, seed=1, use_index=True)
    assert store.query("cellulose", CANON_PART_OF) == []
    v1 = content_repr_vector(store.codec, *real_triple)
    v2 = content_repr_vector(store.codec, *para_triple)
    assert torch.equal(v1, v2), "SELF_TEST FAIL: direction-flipped paraphrase must produce IDENTICAL content representation"
    r1 = store.store(*real_triple, source="cskg_real", trust="TRUST_MID")
    r2 = store.store(*para_triple, source="cskg_paraphrase", trust="TRUST_MID")
    assert r1.resolution == "CLEAN_STORE", r1
    assert r2.resolution == "CONSISTENT_DUP", r2

    # anti-collapse: a genuinely different material must NOT collapse onto the same rep.
    diff_triple = ("coal", CANON_PART_OF, "wood")
    v3 = content_repr_vector(store.codec, *diff_triple)
    assert not torch.equal(v1, v3), "SELF_TEST FAIL: distinct material must NOT produce identical representation"

    # PRODUCES vs CONSUMES must stay distinct via the LEARNED path (seed markers, no held-out risk).
    produce_canon = learned_canon_for_marker("produce")
    consume_canon = learned_canon_for_marker("consume")
    assert produce_canon == CANON_PRODUCES and consume_canon == CANON_CONSUMES, (produce_canon, consume_canon)
    vec_produces = content_repr_vector(store.codec, "energy", produce_canon, "combustion")
    vec_consumes = content_repr_vector(store.codec, "energy", consume_canon, "combustion")
    assert not torch.equal(vec_produces, vec_consumes), "SELF_TEST FAIL: PRODUCES/CONSUMES must NOT collapse"

    return {
        "lexical_similarity_self_test": lex_result, "hd_fact_store_self_test": hdfs_result,
        "verb_lexical_similarity_self_test": verb_result,
        "structural_no_leak_ok": True, "anti_collapse_closed_form": anti,
        "held_out_compose_smoke_ok": True, "direction_handling_ok": True,
        "produces_consumes_boundary_ok": True,
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
def run_pipeline(run_mode: str) -> Dict:
    t0 = time.perf_counter()

    print("[stage] T0 anti-collapse (leave-one-out seed classification)", flush=True)
    anti = run_anti_collapse_marker_classes()
    print(f"[T0] accuracy={anti['accuracy']:.4f} ({anti['n_correct']}/{anti['n_total']}) "
          f"anti_collapse_ok={anti['anti_collapse_ok']}", flush=True)

    print("[stage] T2 held-out generalization (real + scrambled control)", flush=True)
    structural_no_leak_ok = _structural_no_leak_ok()
    held_out = run_held_out_generalization()
    held_out_scr = run_held_out_generalization_scrambled()
    print(f"[T2] held_out_generalization_rate={held_out['held_out_generalization_rate']:.4f} "
          f"({held_out['n_correct']}/{held_out['n_total']}) scrambled_rate="
          f"{held_out_scr['scrambled_generalization_rate']:.4f} "
          f"structural_no_leak_ok={structural_no_leak_ok}", flush=True)
    for m, r in sorted(held_out["per_marker"].items()):
        print(f"  {m}: true={r['true_label']} pred={r['predicted_label']} "
              f"correct={r['correct']} margin={r['margin']:.4f} sims={r['sims']}", flush=True)

    print("[stage] building real reading facts + CSKG bridges + gap-set (T1, real-data reproduction)", flush=True)
    reading = build_reading_facts(process_filter=None)
    vocab = reading_vocab(reading)
    narrow, _wide = build_cskg_bridges(vocab)
    gap = build_gap_set(reading, narrow)
    targets = gap if isinstance(gap, list) else gap["targets"]
    assert targets, "gap-set is empty -- cannot proceed with a decisive test (honest HARD_FAIL condition)"
    processes = sorted(reading.keys())
    materials = vocab
    wholes = sorted({t["whole"] for t in targets})
    print(f"[gap-set] n_targets={len(targets)} n_processes={len(processes)} n_materials={len(materials)} "
          f"n_wholes={len(wholes)}", flush=True)

    print("[stage] CSKG cross-source scan + KB-role-schema scan", flush=True)
    mat_whole_rel, _proc_whole_rel, _proc_mat_rel, n_cskg_rows = compute_cskg_extra(materials, wholes, processes)
    kb_hits, kb_path = compute_kb_role_hits(processes, materials)
    print(f"[cskg] n_rows={n_cskg_rows} n_mat_whole_pairs={len(mat_whole_rel)} "
          f"[kb-role-schema] {len(kb_hits)} (process,material) role hits from {kb_path}", flush=True)

    waves_by_pk = build_genuine_waves(targets, mat_whole_rel, _proc_whole_rel, _proc_mat_rel,
                                      set(), set(), set(), kb_hits, do_causenet=False)
    n_2plus = sum(1 for gw in waves_by_pk.values() if len(gw) >= 2)
    print(f"[genuine-waves] n_gaps={len(waves_by_pk)} n_2plus_sources={n_2plus}", flush=True)

    print("[stage] real-data T1 (LEARNED extraction, no hand canon table)", flush=True)
    real_data = run_real_data_tests_learned(targets, waves_by_pk)
    print(f"[real-data] n_total_pairs={real_data['n_total_pairs']} "
          f"same_rep={real_data['n_total_same_rep']} dup={real_data['n_total_dup']} "
          f"extraction_failed={real_data['n_total_extraction_failed']} "
          f"rate={real_data['real_data_same_idea_rate']:.4f} "
          f"cross_gap_no_collision={real_data['cross_gap_no_collision']} "
          f"({real_data['n_distinct_canon_triples']}/{real_data['n_distinct_material_whole_pairs']})", flush=True)

    print("[stage] core-preserved regression", flush=True)
    lex_result = lexical_similarity_self_test()
    hdfs_result = hd_fact_store_self_test()
    verb_result = verb_lexical_similarity_self_test()
    import hdlab.grounding_acquisition_loop as gal
    import hdlab.prelim_tier as pt
    gal_result = gal.self_test()
    pt_result = pt.self_test()

    same_idea_match_rate = real_data["real_data_same_idea_rate"]
    automatic_corroboration_rate = real_data["real_data_corroboration_rate"]

    distinct_idea_distinct_rep_ok = real_data["cross_gap_no_collision"]
    no_leak_ok = structural_no_leak_ok and real_data["real_data_no_leak_ok"]
    scramble_control_ok = (held_out["held_out_generalization_rate"] >= 0.75
                           and held_out_scr["scrambled_generalization_rate"] <= 0.25)
    core_preserved_ok = (lex_result is not None and hdfs_result is not None and verb_result is not None
                         and gal_result is not None and pt_result is not None)
    controls_ok = no_leak_ok and scramble_control_ok and core_preserved_ok
    held_out_rate = held_out["held_out_generalization_rate"]
    same_idea_ok = same_idea_match_rate >= 0.90
    corroboration_ok = automatic_corroboration_rate >= 0.90

    elapsed = time.perf_counter() - t0

    if not anti["anti_collapse_ok"]:
        verdict = "HARD_FAIL_relation_class_anti_collapse"
        verdict_msg = (f"T0 mandatory can-fail control FAILED: leave-one-out seed classification "
                        f"accuracy={anti['accuracy']:.4f} ({anti['n_correct']}/{anti['n_total']}) "
                        f"produces_never_consumes_ok={anti['produces_never_consumes_ok']} "
                        f"consumes_never_produces_ok={anti['consumes_never_produces_ok']} -- a "
                        f"relation-canonicalizer that merges opposite relations is broken.")
    elif not controls_ok:
        verdict = "HARD_FAIL_controls_broken"
        verdict_msg = (f"one or more mandatory controls FAILED: no_leak_ok={no_leak_ok} "
                        f"scramble_control_ok={scramble_control_ok} core_preserved_ok={core_preserved_ok} "
                        f"(held_out_rate={held_out_rate:.4f}, scrambled_rate="
                        f"{held_out_scr['scrambled_generalization_rate']:.4f})")
    elif held_out_rate == 1.0 and same_idea_ok and corroboration_ok:
        verdict = "HARD_PASS_relation_canonicalization_learned_earned"
        verdict_msg = (f"RELATION-CANONICALIZATION IS EARNED, not supplied: held_out_generalization_"
                        f"rate={held_out_rate:.4f} (4/4) -- every held-out marker (compose/generate/"
                        f"require/transport, never in a seed pool) correctly classifies into its true "
                        f"canonical class via verb-similarity (hdlab.verb_lexical_similarity."
                        f"classify_nway), with NO marker->canon hand dict anywhere. Real-data "
                        f"reproduction WITHOUT the hand table: same_idea_match_rate="
                        f"{same_idea_match_rate:.4f} ({real_data['n_total_same_rep']}/"
                        f"{real_data['n_total_pairs']}), automatic_corroboration_rate="
                        f"{automatic_corroboration_rate:.4f} ({real_data['n_total_dup']}/"
                        f"{real_data['n_total_pairs']}), matching the parent cell's (e65de60f1) own "
                        f"FULL bands (same_idea_match_rate=1.0, automatic_corroboration_rate=1.0 on "
                        f"the identical population). Anti-collapse holds (T0 leave-one-out "
                        f"{anti['n_correct']}/{anti['n_total']}, PRODUCES/CONSUMES never cross). "
                        f"Scramble control confirms genuine structure-dependence (real="
                        f"{held_out_rate:.2f} vs scrambled={held_out_scr['scrambled_generalization_rate']:.2f}). "
                        f"Entity-canonicalization (canon_entity/concept_similarity) is untouched -- "
                        f"both halves of the parent cell's canonicalization policy are now LEARNED.")
    elif held_out_rate >= 0.50:
        verdict = "MIDDLE_BAND_relation_canon_partial_generalization"
        verdict_msg = (f"anti-collapse + controls hold, but held-out generalization is PARTIAL: "
                        f"held_out_generalization_rate={held_out_rate:.4f} "
                        f"({held_out['n_correct']}/{held_out['n_total']}). Some learnable signal, "
                        f"not fully decisive across all 4 classes. same_idea_match_rate="
                        f"{same_idea_match_rate:.4f} automatic_corroboration_rate="
                        f"{automatic_corroboration_rate:.4f}. The hand-table-equivalent lookup "
                        f"(KB_ROLE_TO_CANON + per-function canon literals in e65de60f1) remains the "
                        f"working fallback for the markers that don't generalize.")
    else:
        verdict = "HONEST_NEGATIVE_relation_canon_not_earned_from_thin_signal"
        verdict_msg = (f"anti-collapse + controls hold, but held-out generalization mostly FAILED: "
                        f"held_out_generalization_rate={held_out_rate:.4f} "
                        f"({held_out['n_correct']}/{held_out['n_total']}). As pre-registered "
                        f"(honest note, task-sanctioned outcome): the relation set is small (4 "
                        f"classes, a handful of markers) and the learnable signal proved too thin "
                        f"to reliably generalize. This is an informative negative, NOT forced into "
                        f"a pass -- the hand-table-equivalent lookup (KB_ROLE_TO_CANON + per-"
                        f"function canon literals in e65de60f1) remains legitimate SUPPLIED "
                        f"STRUCTURE (charter-acceptable) as the working mechanism.")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "n_targets": len(targets), "n_gaps": len(waves_by_pk), "n_2plus_sources": n_2plus,
        "n_cskg_rows": n_cskg_rows, "kb_path": kb_path,
        "anti_collapse": anti, "held_out_generalization": held_out,
        "held_out_generalization_scrambled": held_out_scr,
        "real_data": real_data,
        "same_idea_match_rate": same_idea_match_rate,
        "automatic_corroboration_rate": automatic_corroboration_rate,
        "held_out_generalization_rate": held_out_rate,
        "distinct_idea_distinct_rep_ok": distinct_idea_distinct_rep_ok,
        "no_leak_ok": no_leak_ok, "scramble_control_ok": scramble_control_ok,
        "core_preserved_ok": core_preserved_ok, "controls_ok": controls_ok,
        "same_idea_ok": same_idea_ok, "corroboration_ok": corroboration_ok,
        "relation_direction_table_reference_only": {
            k: v["canon"] for k, v in RELATION_DIRECTION_TABLE.items()},  # grading reference, not an input
        "learned_marker_table": LEARNED_MARKER_TABLE,
        "relation_class_thresholds": {"floor": RELATION_CLASS_FLOOR, "margin": RELATION_CLASS_MARGIN},
        "bands": {"same_idea_match_rate_floor": 0.90, "automatic_corroboration_rate_floor": 0.90,
                 "held_out_generalization_hard_pass": 1.0, "held_out_generalization_middle_band_floor": 0.50,
                 "scramble_real_floor": 0.75, "scramble_corrupted_ceiling": 0.25},
        "reference_parent_full": {
            "n_targets": 121, "n_gaps": 121, "n_2plus_sources": 50,
            "same_idea_match_rate": 1.0, "automatic_corroboration_rate": 1.0, "elapsed_s": 13.28,
            "source": "MEASURED@d:/AI/hd-instrument/data/exp_representation_canonicalization_v1/metrics.json"},
    }
    return metrics


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="closed-form fixtures only, <10s")
    parser.add_argument("--timeout", type=float, default=180.0,
                        help="declared wall-time budget: self-test<10s, FULL~15-30s (reuses parent cell's real-data pipeline, MEASURED elapsed_s=13.28 for that population)")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                  "verdict_msg": ("T0 anti-collapse (12/12 leave-one-out) + held-out 'compose'->"
                                  "PART_OF smoke + direction-handling worked example (identical to "
                                  "e65de60f1's own) + PRODUCES/CONSUMES boundary + core-preserved "
                                  "(lexical_similarity/hd_fact_store/verb_lexical_similarity self-"
                                  "tests) all pass"),
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    run_mode = "full"
    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
    _write_start_marker(output_dir, run_mode, expected_n_units=4)
    metrics = run_pipeline(run_mode)
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
