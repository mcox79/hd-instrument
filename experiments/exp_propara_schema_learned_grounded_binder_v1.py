# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (6 arms: prior_lesion/without/oracle/promiscuous/learned/
#   learned_scramble_kb hash-differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1 over a fixed real corpus (ProPara EMNLP18) + a counting/log-odds glass-box learner;
#   no noise-floor threshold. The gam's own MDL compression_ratio is reported instead.
# - HP_SCOPE: {with_learned_binder: [lift_beats_promiscuous, scramble_collapses, generalizes_heldout,
#              no_leak, arms_differ, decode_ok]}
# - cardinality_ok: single split (DEV at smoke; STOPS at smoke per director), fixed 6 arms
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (gam min_coverage/max_interactions pre-set;
#   discriminator-fires = learned binder must beat promiscuous on the HELD-OUT surface subset)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL gam over real binder features at tiny scale AND a synthetic
#   separable task proving the learner fires (real_code_path)
# - progress_logging: print_flush_true
# - deterministic_seeding: true (hashlib-seeded vectors; gam is a deterministic counting fit;
#   scramble reuses the F.5-compliant _scramble_kb_processes)
# See preregs/2026-08-11_propara_schema_learned_grounded_binder_v1.md for the full pre-reg.
"""exp_propara_schema_learned_grounded_binder_v1 -- LEARNED glass-box grounded binder for unstated
participant fates, composed with the validated schema pattern-completion + convergence-gated
selection from exp_propara_schema_pattern_completion_v1 (commit e97a1437b, HARD_FAIL: completion
works in isolation but the residual is per-participant GROUNDED BINDING, promiscuous pair-precision
0.079).

DIRECTOR'S REFRAME (rule b, missing-LEARNING): every prior binder -- literal set-intersection,
graded concept_similarity, the convergence gate, the owned native thematic_role_labeler, and v1's
name-vector->slot scoring -- was UNSUPERVISED SURFACE MATCHING, and all hit the promiscuity wall.
The one untried lever is to LEARN the surface->slot grounding from data. The MAVEN-ERE cell this
session PROVED the glass-box learner (hdlab.learner.plugins.gam_plugin: additive log-odds + MDL-gated
pairwise interactions) works for exactly this shape. Reuse that learner; do NOT hand-roll.

THE ONE VARIABLE: keep validated completion + selection UNCHANGED; swap the per-(participant, schema-
slot) FILL decision from promiscuous threshold scoring (v1's arm = the baseline/ablation) to a
LEARNED gam binary classifier (FILL/SKIP) over GROUNDED + interpretable features.

FEATURES (string tokens for gam): slot identity; active-schema identity (schema:/schemaslot:);
gm: graded-match of participant vs the slot's word-list (v1's promiscuous signal, now a reweightable
FEATURE; content-derived -> scramble-sensitive); cs: bucketed COMPLETION score of the participant
name-vec vs unbind(completed_schema, role_vec[slot]) (keeps completion load-bearing; scramble-
sensitive); lex: WordNet lexicographer supersense of the participant head (owned nltk.wordnet, same
source as hdlab.animacy_lexicon; GROUNDED, generalizes across surface forms -- the held-out lever);
cat: hdlab.animacy_lexicon category (GROUNDED); surf: participant head token (MEMORIZATION channel --
absent below gam min_coverage for unseen surfaces). Native thematic-role feature = available lever,
toggled OFF for this decisive smoke (native-roles-alone already HARD_FAILed + carries a McGuffey
caveat; the decisive question is whether WORDNET GROUNDING generalizes).

SUPERVISION (no DEV/TEST leak): one instance per (paragraph, matched schema P, slot r). TRAIN label
FILL iff effect(r) in the participant's gold effect-set from _oracle_event_multiset over TRAIN
steps_df (the participant-level oracle grant every arm uses); else SKIP. DEV/TEST gold is NEVER read
for features or prediction -- only TRAIN gold sets labels.

THE decisive control = HELD-OUT SURFACE FORMS: SEEN = participant head tokens in TRAIN; a DEV
participant is UNSEEN if none of its head tokens is SEEN. If the binder beats the promiscuous baseline
on the UNSEEN subset, scramble-clean, it LEARNED the grounding; if unseen collapses to ~0 / ~
promiscuous, it MEMORIZED (reported plainly). Plus scramble-schema (must collapse) + no-leak.

See preregs/2026-08-11_propara_schema_learned_grounded_binder_v1.md. Modes: --self-test / --smoke
(DEV) / --full (TEST). Per director this build STOPS at smoke; --full implemented but NOT invoked.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import functools
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "propara_schema_learned_grounded_binder_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab import binding  # noqa: E402
from hdlab.learner.plugins import gam_plugin  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402

from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _official_corpus_scores, _proxy_scores, _arms_must_differ,
)
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import (  # noqa: E402
    _paragraph_precompute, _grids, _prior_lesion_grids, _unm,
    LEAK_CEILING, WITHOUT_COLLAPSE_CEILING,
)
from experiments.exp_propara_bridging_real_kb_sourcing_v1 import _fact_coverage  # noqa: E402
from experiments.exp_propara_arm2_extracted_structure_v1 import _load_coref  # noqa: E402
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import (  # noqa: E402
    _toks, _norm_toks, _load_kb,
)
# IMPORT ONLY -- these cells are owned by other agents (frame-activation) / are prior committed work
# (v1). Not edited here.
from experiments.exp_propara_bridging_frame_activation_v1 import (  # noqa: E402
    _graded_frame_score, _process_convergent, _graded_role_hit, _scramble_kb_processes,
    MIN_FRAME_SIG_HITS, CAND_K, MAX_DONORS,
)
from experiments.exp_propara_schema_pattern_completion_v1 import (  # noqa: E402
    ROLE_VOCAB, _EFFECT_BY_ROLE, ROLE_VECS, SCHEMA_D, COMPLETION_TEMP, COMPLETION_MAX_STEPS,
    _build_schema_codebook, _build_partial_query, _word_vec, _cos,
    _build_schema_completion_bridge_facts,  # v1's PROMISCUOUS arm = baseline/ablation (reused verbatim)
    cf_iterative_attractor,
)
from propara_trap_check import build_step_rows  # noqa: E402

# ============================================================================ WordNet lexname grounder
# Owned nltk.wordnet access (SAME source hdlab.animacy_lexicon uses for its glass-box category
# lexicon). First-noun-sense lexicographer supersense (noun.substance / noun.artifact / noun.food /
# noun.phenomenon / ...). GROUNDED + generalizes across surface forms -- the held-out lever.
@functools.lru_cache(maxsize=4096)
def _wn_lexname(word: str) -> Optional[str]:
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(word, pos="n")
        if not syns:
            return None
        return syns[0].lexname()
    except Exception:  # noqa: BLE001 -- optional grounded feature; absent-on-failure, never phantom
        return None


def _participant_head_tokens(participant: str) -> List[str]:
    """Content head tokens of a participant surface (len>2), longest-first (head heuristic)."""
    return sorted((t for t in _norm_toks(participant) if len(t) > 2), key=lambda t: (-len(t), t))


# ============================================================================ binder instance construction
CS_BUCKETS = (0.0, 0.05, 0.12)   # completion-score bucket edges (bucket index by np.digitize)


def _cs_bucket(score: float) -> str:
    idx = int(np.digitize([score], CS_BUCKETS)[0])  # 0..3
    return ["neg", "lo", "mid", "hi"][idx]


def _instance_feats(participant: str, schema: str, slot: str, proc_dict: Dict,
                    role_bundle: Optional[torch.Tensor]) -> List[str]:
    """Grounded + interpretable feature-value strings for gam. See module docstring / pre-reg."""
    p_toks = _norm_toks(participant)
    heads = _participant_head_tokens(participant)
    feats = [f"slot:{slot}", f"schema:{schema}", f"schemaslot:{schema}_{slot}"]
    # promiscuous graded-match signal as a FEATURE (content-derived -> scramble-sensitive)
    gm = _graded_role_hit(p_toks, proc_dict.get(slot, []))
    feats.append(f"gm:{slot}:{1 if gm else 0}")
    # completion-derived score bucket (keeps completion load-bearing; scramble/completion-sensitive)
    if role_bundle is not None:
        best = -1.0
        for t in heads:
            s = _cos(role_bundle, _word_vec(t, SCHEMA_D))
            if s > best:
                best = s
        feats.append(f"cs:{slot}:{_cs_bucket(best)}")
    else:
        feats.append(f"cs:{slot}:none")
    # GROUNDED features (WordNet supersense + owned animacy category) on the participant head
    head = heads[0] if heads else None
    if head is not None:
        lex = _wn_lexname(head)
        if lex is not None:
            feats.append(f"lex:{lex}")
        anim = lookup_animacy(head, "NOUN")
        if anim is not None:
            feats.append(f"cat:{anim['category']}")
        feats.append(f"surf:{head}")   # MEMORIZATION channel (absent below gam min_coverage on unseen)
    return feats


def _build_binder_instances(paragraphs, kb, scramble_kb: bool = False,
                            gold_effects: Optional[Dict[Tuple, Set[str]]] = None) -> Tuple[List[Dict], Dict]:
    """One instance per (paragraph, convergence-gated-matched schema P, non-empty slot r). Features
    are IDENTICAL construction for TRAIN (gold_effects set -> labels attached) and DEV/TEST (no gold).
    Selection + completion are the SAME validated machinery as v1 (imported)."""
    procs = kb["processes"]
    if scramble_kb:
        procs = _scramble_kb_processes(procs)
    names, codebook = _build_schema_codebook(procs, SCHEMA_D)
    cb_np = codebook.numpy().astype(np.float32)

    instances: List[Dict] = []
    n_matched_paras = 0
    n_completions = 0
    n_completions_no_query = 0
    for para in paragraphs:
        pid = str(para["para_id"])
        full_text = " ".join(para["sentence_texts"]).lower()
        text_toks = _toks(" ".join(para["sentence_texts"]))
        participants_toks = [_norm_toks(p) for p in para["participants"]]

        # selection: convergence-gated candidate pool (identical to v1)
        scored = []
        for name, d in procs.items():
            score, hits = _graded_frame_score(text_toks, d["signature"])
            if score is not None and hits >= MIN_FRAME_SIG_HITS:
                scored.append((name, score))
        scored.sort(key=lambda kv: -kv[1])
        cand = [name for name, sc in scored[:CAND_K]]
        matched = [nm for nm in cand if _process_convergent(procs[nm], participants_toks)[0]][:MAX_DONORS]
        if matched:
            n_matched_paras += 1

        # completion per matched schema -> per-slot recovered role-bundles (feature source)
        schema_role_bundles: Dict[str, Optional[Dict[str, torch.Tensor]]] = {}
        for P in matched:
            pq, _hw = _build_partial_query(procs[P], text_toks, SCHEMA_D)
            n_completions += 1
            if pq is None:
                n_completions_no_query += 1
                schema_role_bundles[P] = None
                continue
            recovered_np, _cd = cf_iterative_attractor(
                pq.numpy().astype(np.float32), cb_np, temp=COMPLETION_TEMP, max_steps=COMPLETION_MAX_STEPS)
            completed = torch.from_numpy(recovered_np)
            schema_role_bundles[P] = {r: binding.unbind(completed, ROLE_VECS[r]) for r in ROLE_VOCAB}

        for participant in para["participants"]:
            p_toks = _norm_toks(participant)
            mentioned = any(t in full_text for t in p_toks if len(t) > 2)
            for P in matched:
                rbs = schema_role_bundles.get(P)
                for r in ROLE_VOCAB:
                    if not procs[P].get(r):
                        continue   # slot must exist in this (possibly-scrambled) schema (license)
                    effect, trigs = _EFFECT_BY_ROLE[r]
                    rb = rbs[r] if rbs is not None else None
                    feats = _instance_feats(participant, P, r, procs[P], rb)
                    inst = {"pid": pid, "participant": participant, "schema": P, "slot": r,
                            "effect": effect, "trigs": sorted(trigs), "feats": feats,
                            "mentioned": mentioned}
                    if gold_effects is not None:
                        ge = gold_effects.get((pid, participant), set())
                        inst["gold_class"] = "FILL" if effect in ge else "SKIP"
                    instances.append(inst)
    stats = {"n_instances": len(instances), "n_matched_paras": n_matched_paras,
             "n_completions": n_completions, "n_completions_no_query": n_completions_no_query,
             "scramble_kb": scramble_kb}
    return instances, stats


def _facts_from_instances(instances, hypothesis) -> Tuple[Dict[Tuple, Dict[str, Set[str]]], Dict]:
    """Apply the fitted gam per instance; FILL -> add (effect, trigger-classes) to the participant's
    bridge dict. Bit-identical downstream contract to v1 / the promiscuous arm."""
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    n_fill = 0
    n_fill_unmentioned = 0
    for inst in instances:
        key = (inst["pid"], inst["participant"])
        facts.setdefault(key, {})
        pred = gam_plugin.apply(hypothesis, inst["feats"])
        if pred == "FILL":
            facts[key].setdefault(inst["effect"], set()).update(inst["trigs"])
            n_fill += 1
            if not inst["mentioned"]:
                n_fill_unmentioned += 1
    return facts, {"n_fill": n_fill, "n_fill_for_unmentioned_IMPLICIT": n_fill_unmentioned}


def _gold_effects_from_multiset(oracle_multiset) -> Dict[Tuple, Set[str]]:
    out: Dict[Tuple, Set[str]] = {}
    for key, counts in oracle_multiset.items():
        out[key] = {e for e in ("CREATE", "MOVE", "DESTROY") if counts.get(e, 0) > 0}
    return out


def _fit_binder(train_instances) -> Tuple[Dict, Dict]:
    """Fit the glass-box gam binder (FILL/SKIP) over TRAIN instances (reused learner, not hand-rolled)."""
    spec = {"classes": ["FILL", "SKIP"], "label_fn": lambda ep: ep["gold_class"],
            "min_coverage": 3, "max_singles_for_pairing": 60, "max_interactions": 40, "alpha": 1.0}
    res = gam_plugin.learn(train_instances, lambda ep: ep["feats"], spec, prior=None)
    meta = {"n_train_instances": len(train_instances),
            "n_fill_train": sum(1 for e in train_instances if e["gold_class"] == "FILL"),
            "compression_ratio": round(res.compression_ratio, 4),
            "n_main_keys": res.metrics.get("n_main_keys"),
            "n_interaction_keys": res.metrics.get("n_interaction_keys"),
            "is_episodic": res.is_episodic}
    return res.hypothesis, meta


# ============================================================================ held-out-surface split
def _seen_surface_tokens(train_paragraphs) -> Set[str]:
    seen: Set[str] = set()
    for para in train_paragraphs:
        for participant in para["participants"]:
            seen.update(_participant_head_tokens(participant))
    return seen


def _is_unseen_surface(participant: str, seen: Set[str]) -> bool:
    heads = _participant_head_tokens(participant)
    return bool(heads) and all(h not in seen for h in heads)


def _filter_facts(facts, keyset):
    return {k: v for k, v in facts.items() if k in keyset}


# ============================================================================ pre-registered bands
SCRAMBLE_MAX_RETAINED_FRACTION = 0.50
MEMORIZATION_MIN_RATIO = 0.34     # unseen_pair_f1 / seen_pair_f1 >= this -> not memorized
LEAK_ORACLE_MARGIN = 0.02


# ============================================================================ decomposition
def run_decomposition(split: str, train_paragraphs: List[Dict]) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    oracle_multiset = _oracle_event_multiset(steps_df)
    train_oracle_multiset = _oracle_event_multiset(train_steps_df)
    coref = _load_coref(split)
    kb = _load_kb()

    print(f"[precompute] {len(paragraphs)} eval paragraphs (extraction + oracle facts)...", flush=True)
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp] for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}

    # ---- LEARNED binder: fit on TRAIN, apply on eval split ----
    print(f"[binder] building TRAIN instances over {len(train_paragraphs)} paragraphs...", flush=True)
    train_gold = _gold_effects_from_multiset(train_oracle_multiset)
    train_instances, train_stats = _build_binder_instances(train_paragraphs, kb, gold_effects=train_gold)
    print(f"[binder] fitting glass-box gam over {len(train_instances)} instances...", flush=True)
    hypothesis, binder_meta = _fit_binder(train_instances)
    print(f"[binder] gam: {binder_meta}", flush=True)

    print("[binder] applying to eval split (real KB)...", flush=True)
    eval_instances, eval_stats = _build_binder_instances(paragraphs, kb)
    learned_facts, learned_apply_stats = _facts_from_instances(eval_instances, hypothesis)
    cov_learned = _fact_coverage(learned_facts, oracle_facts)

    print("[binder] applying to eval split (SCRAMBLE-schema)...", flush=True)
    eval_instances_scr, _ = _build_binder_instances(paragraphs, kb, scramble_kb=True)
    learned_scr_facts, _ = _facts_from_instances(eval_instances_scr, hypothesis)
    cov_learned_scr = _fact_coverage(learned_scr_facts, oracle_facts)

    # ---- PROMISCUOUS baseline (= v1's real schema-completion arm; the ablation of the learned swap)
    print("[promiscuous] v1 schema-completion baseline (threshold scoring)...", flush=True)
    promisc_facts, promisc_stats = _build_schema_completion_bridge_facts(paragraphs, kb, scramble_kb=False, ablation=False)
    cov_promisc = _fact_coverage(promisc_facts, oracle_facts)

    # ---- HELD-OUT surface split ----
    seen = _seen_surface_tokens(train_paragraphs)
    unseen_keys = {(pid, pp) for para in paragraphs for pid in [str(para["para_id"])]
                   for pp in para["participants"] if _is_unseen_surface(pp, seen)}
    seen_keys = {(pid, pp) for para in paragraphs for pid in [str(para["para_id"])]
                 for pp in para["participants"]} - unseen_keys
    oracle_unseen = _filter_facts(oracle_facts, unseen_keys)
    oracle_seen = _filter_facts(oracle_facts, seen_keys)
    cov_learned_unseen = _fact_coverage(_filter_facts(learned_facts, unseen_keys), oracle_unseen)
    cov_learned_seen = _fact_coverage(_filter_facts(learned_facts, seen_keys), oracle_seen)
    cov_promisc_unseen = _fact_coverage(_filter_facts(promisc_facts, unseen_keys), oracle_unseen)

    # ---- scored arms (unmentioned-subset macro-F1) ----
    def _pre_with_bridge(facts):
        pre = {}
        for para in paragraphs:
            pid = str(para["para_id"])
            pr = dict(pre_oracle[pid])
            pr["bridge"] = {pp: facts.get((pid, pp), {}) for pp in para["participants"]}
            pre[pid] = pr
        return pre

    grids: Dict[str, Dict] = {}
    grids["prior_lesion"], lesion_diag = _prior_lesion_grids(paragraphs, pre_oracle)
    grids["without_knowledge"], without_diag = _grids(paragraphs, pre_oracle, use_bridge=False)
    grids["with_oracle"], oracle_diag = _grids(paragraphs, pre_oracle, use_bridge=True)
    grids["with_promiscuous_completion"], promisc_diag = _grids(paragraphs, _pre_with_bridge(promisc_facts), use_bridge=True)
    grids["with_learned_binder"], learned_diag = _grids(paragraphs, _pre_with_bridge(learned_facts), use_bridge=True)
    grids["with_learned_binder_scramble_kb"], learned_scr_diag = _grids(paragraphs, _pre_with_bridge(learned_scr_facts), use_bridge=True)

    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    unm = {arm: _unm(proxy[arm]) for arm in proxy}

    without_f1 = unm["without_knowledge"]["macro_f1"]
    oracle_f1 = unm["with_oracle"]["macro_f1"]
    promisc_f1 = unm["with_promiscuous_completion"]["macro_f1"]
    learned_f1 = unm["with_learned_binder"]["macro_f1"]
    learned_scr_f1 = unm["with_learned_binder_scramble_kb"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]

    oracle_lift = oracle_f1 - without_f1
    promisc_lift = promisc_f1 - without_f1
    learned_lift = learned_f1 - without_f1
    learned_scr_lift = learned_scr_f1 - without_f1
    survival = (learned_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    promisc_survival = (promisc_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    scramble_retained_fraction = (learned_scr_lift / learned_lift) if abs(learned_lift) > 1e-9 else (
        0.0 if abs(learned_scr_lift) < 1e-9 else float("inf"))

    diff = _arms_must_differ(grids)

    # memorization ratio (held-out generalization; the decisive control)
    seen_f1 = cov_learned_seen["pair_f1"]
    unseen_f1 = cov_learned_unseen["pair_f1"]
    memorization_ratio = (unseen_f1 / seen_f1) if seen_f1 > 1e-9 else (0.0 if unseen_f1 < 1e-9 else float("inf"))

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff,
        "decode": {"lesion": lesion_diag["decode_fidelity"], "without": without_diag["decode_fidelity"],
                   "oracle": oracle_diag["decode_fidelity"], "promiscuous": promisc_diag["decode_fidelity"],
                   "learned": learned_diag["decode_fidelity"], "learned_scramble_kb": learned_scr_diag["decode_fidelity"]},
        "unmentioned_subset": unm,
        "without_f1": without_f1, "with_oracle_f1": oracle_f1,
        "with_promiscuous_completion_f1": promisc_f1, "with_learned_binder_f1": learned_f1,
        "with_learned_binder_scramble_kb_f1": learned_scr_f1, "prior_lesion_f1": lesion_f1,
        "oracle_lift": oracle_lift, "promiscuous_lift": promisc_lift, "learned_lift": learned_lift,
        "learned_scramble_lift": learned_scr_lift,
        "survival_fraction": survival, "promiscuous_survival_fraction": promisc_survival,
        "scramble_retained_fraction": scramble_retained_fraction,
        "learned_minus_prior_lesion": learned_f1 - lesion_f1,
        "fact_coverage_learned_vs_oracle": cov_learned,
        "fact_coverage_promiscuous_vs_oracle": cov_promisc,
        "fact_coverage_learned_scramble_vs_oracle": cov_learned_scr,
        "heldout_surface": {
            "n_unseen_participants": len(unseen_keys), "n_seen_participants": len(seen_keys),
            "learned_unseen": cov_learned_unseen, "learned_seen": cov_learned_seen,
            "promiscuous_unseen": cov_promisc_unseen,
            "memorization_ratio_unseenf1_over_seenf1": round(memorization_ratio, 4),
            "n_oracle_unseen_with_fact": cov_learned_unseen["n_oracle_participants_with_fact"],
        },
        "binder_meta": binder_meta, "train_instance_stats": train_stats, "eval_instance_stats": eval_stats,
        "learned_apply_stats": learned_apply_stats, "promiscuous_stats": promisc_stats,
        "kb_n_processes": kb["_meta"]["n_processes"],
        "official": {arm: official[arm]["overall"] for arm in official},
    }


# ============================================================================ verdict
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    survival = result["survival_fraction"]
    learned_lift = result["learned_lift"]
    promisc_lift = result["promiscuous_lift"]
    without_f1 = result["without_f1"]
    learned_f1 = result["with_learned_binder_f1"]
    oracle_f1 = result["with_oracle_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = all(v >= 0.99 for v in result["decode"].values())
    infra_fail = (not arms_ok) or (not decode_ok)

    floor_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING
    leak = (learned_f1 > LEAK_CEILING) or (learned_f1 >= oracle_f1 - LEAK_ORACLE_MARGIN)

    cov_l = result["fact_coverage_learned_vs_oracle"]
    cov_p = result["fact_coverage_promiscuous_vs_oracle"]
    beats_promiscuous = (cov_l["pair_precision"] > cov_p["pair_precision"]) and (learned_lift >= promisc_lift)

    scramble_retained = result["scramble_retained_fraction"]
    scramble_collapsed = (scramble_retained is not None) and (scramble_retained <= SCRAMBLE_MAX_RETAINED_FRACTION)

    ho = result["heldout_surface"]
    unseen_beats_promisc = ho["learned_unseen"]["pair_precision"] > ho["promiscuous_unseen"]["pair_precision"]
    not_memorized = (ho["memorization_ratio_unseenf1_over_seenf1"] >= MEMORIZATION_MIN_RATIO) and \
                    (ho["learned_unseen"]["pair_f1"] > 1e-9)
    generalizes = unseen_beats_promisc and not_memorized

    msg = (f"split={result['split']} learned_f1={learned_f1:.4f} promisc_f1={result['with_promiscuous_completion_f1']:.4f} "
           f"oracle_f1={oracle_f1:.4f} without_f1={without_f1:.4f} "
           f"survival={survival} learned_lift={learned_lift:.4f} promisc_lift={promisc_lift:.4f} "
           f"learned_prec={cov_l['pair_precision']}(promisc={cov_p['pair_precision']}) learned_recall={cov_l['pair_recall']} "
           f"beats_promiscuous={beats_promiscuous} scramble_retained={scramble_retained} scramble_collapsed={scramble_collapsed} "
           f"UNSEEN[n={ho['n_unseen_participants']} learned_prec={ho['learned_unseen']['pair_precision']} "
           f"promisc_prec={ho['promiscuous_unseen']['pair_precision']} learned_f1={ho['learned_unseen']['pair_f1']} "
           f"seen_f1={ho['learned_seen']['pair_f1']} memo_ratio={ho['memorization_ratio_unseenf1_over_seenf1']}] "
           f"unseen_beats_promisc={unseen_beats_promisc} not_memorized={not_memorized} generalizes={generalizes} "
           f"floor_collapsed={floor_collapsed} leak={leak} arms_ok={arms_ok} decode_ok={decode_ok} "
           f"gam[{result['binder_meta']}]")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not floor_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_FLOOR_DID_NOT_COLLAPSE_void: {msg}"
    if leak:
        return "HARD_FAIL", f"HARD_FAIL_LEAKED_ANSWERS_reject: {msg}"
    if not beats_promiscuous:
        return "HARD_FAIL", f"HARD_FAIL_LEARNED_BINDER_DOES_NOT_BEAT_PROMISCUOUS: {msg}"
    if not scramble_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_SCRAMBLE_SCHEMA_DID_NOT_COLLAPSE_generic_not_grounded: {msg}"
    if not generalizes:
        reason = "MEMORIZED_seen_only" if not not_memorized else "unseen_not_above_promiscuous"
        return "HARD_FAIL", f"HARD_FAIL_DOES_NOT_GENERALIZE_TO_HELDOUT_SURFACE[{reason}]: {msg}"
    return "HARD_PASS", f"HARD_PASS_LEARNED_GROUNDED_BINDER_GENERALIZES_scramble_clean: {msg}"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": n, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def self_test() -> Dict:
    kb = _load_kb()
    assert kb["_meta"]["n_processes"] >= 12, kb["_meta"]

    # (1) WordNet lexname grounder fires + generalizes across surface (log/timber/wood -> same super).
    assert _wn_lexname("wood") == "noun.substance", _wn_lexname("wood")
    assert _wn_lexname("oxygen") == "noun.substance", _wn_lexname("oxygen")
    assert _wn_lexname("qwertyxz") is None

    # (2) gam learner FIRES on a synthetic separable task (proves the learner discriminates, not a
    # phantom): feature 'good' -> FILL, 'bad' -> SKIP, plus noise; apply must recover the mapping.
    synth_train = []
    for i in range(60):
        synth_train.append({"feats": ["good", f"n{i%7}"], "gold_class": "FILL"})
        synth_train.append({"feats": ["bad", f"n{i%7}"], "gold_class": "SKIP"})
    hyp_synth, meta_synth = _fit_binder(synth_train)
    assert gam_plugin.apply(hyp_synth, ["good", "n0"]) == "FILL", "learner failed to fire on separable task"
    assert gam_plugin.apply(hyp_synth, ["bad", "n1"]) == "SKIP", "learner failed to fire on separable task"
    assert not meta_synth["is_episodic"], meta_synth

    # (3) REAL binder pipeline on a tiny synth ProPara-like paragraph (real_code_path): build
    # instances over the REAL KB, fit gam with gold, apply, produce bridge facts.
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["The wood burns in the fire.", "Ash and smoke form as it burns."],
         "participants": ["wood", "oxygen", "ash"],
         "states": [["here", "here", "-"], ["here", "-", "-"], ["-", "-", "here"]]},
    ]
    gold = {("s1", "wood"): {"DESTROY"}, ("s1", "oxygen"): {"DESTROY"}, ("s1", "ash"): {"CREATE"}}
    insts, istats = _build_binder_instances(synth, kb, gold_effects=gold)
    assert istats["n_instances"] > 0, istats
    assert all("gold_class" in e for e in insts), "gold labels not attached"
    # features present: grounded + schema + slot + gm + cs + surf
    fset = set(f for e in insts for f in e["feats"])
    assert any(f.startswith("lex:") for f in fset), "no WordNet lexname feature emitted"
    assert any(f.startswith("schema:") for f in fset), "no schema feature emitted"
    assert any(f.startswith("gm:") for f in fset), "no graded-match feature emitted"
    assert any(f.startswith("cs:") for f in fset), "no completion-score feature emitted"
    # fit + apply round-trip
    hyp, meta = _fit_binder(insts)
    facts, apply_stats = _facts_from_instances(insts, hyp)
    assert isinstance(facts, dict), facts

    # (4) held-out-surface helper: 'boulder' unseen if not in seen set; 'wood' seen if in train.
    seen = _seen_surface_tokens(synth)   # {wood, oxygen, ash}
    assert _is_unseen_surface("boulder", seen) is True
    assert _is_unseen_surface("wood", seen) is False

    # (5) scramble path runs + deterministic.
    insts_scr, _ = _build_binder_instances(synth, kb, scramble_kb=True)
    insts_scr2, _ = _build_binder_instances(synth, kb, scramble_kb=True)
    feats_scr = [e["feats"] for e in insts_scr]
    feats_scr2 = [e["feats"] for e in insts_scr2]
    assert feats_scr == feats_scr2, "scramble must be deterministic across calls"

    # (6) verdict-logic unit checks.
    base = {"split": "x", "survival_fraction": 0.30, "learned_lift": 0.03, "promiscuous_lift": 0.012,
            "without_f1": 0.35, "with_learned_binder_f1": 0.38, "with_oracle_f1": 0.45,
            "with_promiscuous_completion_f1": 0.362,
            "arms_differ": {"all_differ": True}, "decode": {"a": 1.0},
            "fact_coverage_learned_vs_oracle": {"pair_precision": 0.20, "pair_recall": 0.25, "pair_f1": 0.222},
            "fact_coverage_promiscuous_vs_oracle": {"pair_precision": 0.079, "pair_recall": 0.17, "pair_f1": 0.108},
            "scramble_retained_fraction": 0.10,
            "heldout_surface": {"n_unseen_participants": 30, "n_seen_participants": 100,
                                 "learned_unseen": {"pair_precision": 0.18, "pair_recall": 0.20, "pair_f1": 0.19},
                                 "promiscuous_unseen": {"pair_precision": 0.06, "pair_recall": 0.10, "pair_f1": 0.075},
                                 "learned_seen": {"pair_precision": 0.22, "pair_recall": 0.27, "pair_f1": 0.24},
                                 "memorization_ratio_unseenf1_over_seenf1": 0.79},
            "binder_meta": {"compression_ratio": 1.4}}
    hp, hp_msg = decomposition_verdict(base)
    assert hp == "HARD_PASS", (hp, hp_msg)
    nb = json.loads(json.dumps(base)); nb["fact_coverage_learned_vs_oracle"]["pair_precision"] = 0.05
    v, _ = decomposition_verdict(nb); assert v == "HARD_FAIL", ("beats_promiscuous", v)
    sc = json.loads(json.dumps(base)); sc["scramble_retained_fraction"] = 0.9
    v, _ = decomposition_verdict(sc); assert v == "HARD_FAIL", ("scramble", v)
    mem = json.loads(json.dumps(base)); mem["heldout_surface"]["memorization_ratio_unseenf1_over_seenf1"] = 0.10
    v, m = decomposition_verdict(mem); assert v == "HARD_FAIL" and "MEMORIZED" in m, ("memorized", v, m)
    un = json.loads(json.dumps(base)); un["heldout_surface"]["learned_unseen"]["pair_precision"] = 0.01
    v, _ = decomposition_verdict(un); assert v == "HARD_FAIL", ("unseen_not_above_promisc", v)
    lk = json.loads(json.dumps(base)); lk["with_learned_binder_f1"] = 0.45
    v, _ = decomposition_verdict(lk); assert v == "HARD_FAIL", ("leak", v)
    vd = json.loads(json.dumps(base)); vd["without_f1"] = 0.7
    v, _ = decomposition_verdict(vd); assert v == "HARD_FAIL", ("void", v)

    return {"kb_n_processes": kb["_meta"]["n_processes"],
            "wn_lexname_probe": {"wood": _wn_lexname("wood"), "oxygen": _wn_lexname("oxygen"),
                                  "ash": _wn_lexname("ash"), "electricity": _wn_lexname("electricity")},
            "synth_learner_meta": meta_synth,
            "real_binder_meta": meta, "n_real_instances": istats["n_instances"],
            "feature_kinds_present": sorted({f.split(":")[0] for f in fset}),
            "verdict_logic_unit_checks": {"hard_pass": hp}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str)[:8000])
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    split = "dev" if args.smoke else "test"
    _write_start_marker(output_dir, run_mode, 1)
    t0 = time.time()
    train_paragraphs = _load_split("train")
    print(f"[{run_mode}] split={split} LEARNED GROUNDED BINDER over schema completion...", flush=True)
    result = run_decomposition(split, train_paragraphs)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    ho = result["heldout_surface"]
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "SURVIVAL_FRACTION": result["survival_fraction"],
            "PROMISCUOUS_SURVIVAL_FRACTION": result["promiscuous_survival_fraction"],
            "SCRAMBLE_RETAINED_FRACTION": result["scramble_retained_fraction"],
            "with_learned_binder_f1": result["with_learned_binder_f1"],
            "with_promiscuous_completion_f1": result["with_promiscuous_completion_f1"],
            "with_learned_binder_scramble_kb_f1": result["with_learned_binder_scramble_kb_f1"],
            "with_oracle_f1": result["with_oracle_f1"], "without_f1": result["without_f1"],
            "learned_lift": result["learned_lift"], "promiscuous_lift": result["promiscuous_lift"],
            "oracle_lift": result["oracle_lift"],
            "learned_pair_precision": result["fact_coverage_learned_vs_oracle"]["pair_precision"],
            "learned_pair_recall": result["fact_coverage_learned_vs_oracle"]["pair_recall"],
            "promiscuous_pair_precision": result["fact_coverage_promiscuous_vs_oracle"]["pair_precision"],
            "HELDOUT_SURFACE": ho,
            "binder_meta": result["binder_meta"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1 over a fixed real corpus (ProPara EMNLP18) + counting/log-odds glass-box learner; "
                    "no noise-floor threshold. gam MDL compression_ratio reported.",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: gam min_coverage=3/max_interactions=40 pre-set; "
                              "discriminator-fires = learned binder must beat promiscuous on the held-out surface subset",
        "thresholds": {"SCRAMBLE_MAX_RETAINED_FRACTION": SCRAMBLE_MAX_RETAINED_FRACTION,
                       "MEMORIZATION_MIN_RATIO": MEMORIZATION_MIN_RATIO,
                       "LEAK_CEILING": LEAK_CEILING, "LEAK_ORACLE_MARGIN": LEAK_ORACLE_MARGIN,
                       "WITHOUT_COLLAPSE_CEILING": WITHOUT_COLLAPSE_CEILING, "SCHEMA_D": SCHEMA_D},
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "result"}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
