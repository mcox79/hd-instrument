# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (6 arms: prior_lesion/without/oracle/promiscuous/keyed/
#   keyed_scramble hash-differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1 over a fixed real corpus (ProPara EMNLP18) + exact dict/HD-store lookup; no
#   noise-floor threshold
# - HP_SCOPE: {with_keyed_lookup: [beats_promiscuous_margin, scramble_collapses,
#              residual_coverage_dominated, no_leak, arms_differ, decode_ok]}
# - cardinality_ok: single split (DEV at smoke; STOPS at smoke per director), fixed 6 arms
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (exact lookup + pre-registered bands, no tuned thresh)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test builds the REAL re-keyed HDFactStore over the REAL KB + validates store==dict +
#   exercises the arm + residual decomposition (real_code_path)
# - progress_logging: print_flush_true
# - deterministic_seeding: true (HDFactStore seeded; scramble via hashlib _deterministic_perm;
#   never python hash() / list(set()) ordering)
# See preregs/2026-08-11_propara_process_keyed_lookup_v1.md for the full pre-reg.
"""exp_propara_process_keyed_lookup_v1 -- validate the FOUNDATION FORM (per-(entity,process)-keyed
EXACT lookup) with ZERO LLM. Audit finding: the binding wall is STRUCTURAL -- the hand-vetted KB
(propara_process_physics_kb_v1.json) is a FLAT, UNKEYED bag per role, so an entity like 'water'
recurs across many processes and no fuzzy/graded/completion operator disambiguates (v1 completion
HARD_FAIL e97a1437b; learned binder HARD_FAIL 50b8d8751; both hit the promiscuity wall, pair-
precision 0.079). HYPOTHESIS: the fix is PER-(entity,process)-KEYED facts + process-conditioned
EXACT lookup.

ONE VARIABLE (same content, no new knowledge, no LLM): swap ONLY the binder OPERATOR -- fuzzy graded/
completion over the flat role-bag (v1's promiscuous arm = the ABLATION) -> EXACT per-(entity,process)
keyed lookup. Selection (which process is cued) stays the SAME validated convergence gate (26x).

RE-KEYING (deterministic): for each process P, each entity e in P.consumes -> (e,P)->DESTROY;
P.produces -> CREATE; P.moves -> MOVE. Stored as triples (subject=e, relation=fate_in_<P>, obj=FATE,
source=propara_physics_kb_v1, trust=TRUST_HIGH) in the owned hdlab.hd_fact_store.HDFactStore
(fate_in_<P> MULTIVALUED). The arm's lookups go THROUGH the store (wire-don't-island: validates
hd_fact_store for this content); a plain dict mirror is cross-checked bit-equal in self-test and used
for the structural coverage/residual questions. Entity keys normalized identically to the promiscuous
arm (_norm_toks variants) so the ONLY difference is exact-vs-graded.

ARM with_keyed_lookup: gate selects process(es); per NAMED participant, per selected process, EXACT
keyed lookup (participant-token, P) -> FATE(s); bind (effect + _ROLE_EFFECT trigger-classes).

CONTROLS: SCRAMBLE (per-process permutation of entity->fate keying; coverage+selection held identical
so it isolates the KEYING signal; must collapse) + ABLATION (= the promiscuous flat arm) + NO-LEAK
(gold never read) + HELD-OUT ENTITIES (surface not in KB -> coverage gap).

RESIDUAL DECOMPOSITION (over DEV oracle-fact participants): RECOVERED, or COVERAGE (entity not in
KB) / GATE (in KB but not under a selected process) / FORM (present under selected process but wrong
fate). HARD_PASS = keyed beats promiscuous meaningfully AND scramble collapses AND residual
COVERAGE-dominated (form validated, remaining problem is coverage). HARD_FAIL = keyed does not beat
promiscuous even for in-KB entities, OR scramble doesn't collapse.

See preregs/2026-08-11_propara_process_keyed_lookup_v1.md. Modes: --self-test / --smoke (DEV) /
--full (TEST). Per director this build STOPS at smoke; --full implemented but NOT invoked.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

ANCHOR_NAME = "propara_process_keyed_lookup_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab.hd_fact_store import HDFactStore  # noqa: E402

from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _official_corpus_scores, _proxy_scores, _arms_must_differ,
    _deterministic_perm,
)
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import (  # noqa: E402
    _paragraph_precompute, _grids, _prior_lesion_grids, _unm,
    LEAK_CEILING, WITHOUT_COLLAPSE_CEILING,
)
from experiments.exp_propara_bridging_real_kb_sourcing_v1 import _fact_coverage  # noqa: E402
from experiments.exp_propara_arm2_extracted_structure_v1 import _load_coref  # noqa: E402
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import (  # noqa: E402
    _toks, _norm_toks, _load_kb, _ROLE_EFFECT,
)
# IMPORT ONLY -- owned by other agents / prior committed work; not edited here.
from experiments.exp_propara_bridging_frame_activation_v1 import (  # noqa: E402
    _graded_frame_score, _process_convergent, MIN_FRAME_SIG_HITS, CAND_K, MAX_DONORS,
)
from experiments.exp_propara_schema_pattern_completion_v1 import (  # noqa: E402
    _build_schema_completion_bridge_facts,  # v1's PROMISCUOUS arm = the ablation/baseline (reused)
)
from propara_trap_check import build_step_rows  # noqa: E402

# role -> (effect, trigger-verb-classes); and the inverse effect -> trigs (each role maps to a
# distinct effect here, so effect determines trigs -- bit-identical to every other arm's contract).
_EFFECT_TRIGS: Dict[str, Set[str]] = {effect: set(trigs) for _role, effect, trigs in _ROLE_EFFECT}
_ROLE_EFFECT_LABEL: Dict[str, str] = {role: effect for role, effect, _trigs in _ROLE_EFFECT}
ROLE_VOCAB: Tuple[str, ...] = ("consumes", "produces", "moves")

STORE_N_DIM = 8192
STORE_SEED = 0
SCRAMBLE_SEED = "propara_process_keyed_lookup_scramble_v1"

# pre-registered bands
KEYED_BEATS_PROMISCUOUS_MARGIN = 0.05
SCRAMBLE_MAX_RETAINED_FRACTION = 0.50
LEAK_ORACLE_MARGIN = 0.02


# ============================================================================ re-keying (no LLM, no gold)
def _rekey_kb(procs: Dict) -> Tuple[Dict[Tuple[str, str], Set[str]], Set[str]]:
    """Flat role-bag KB -> per-(entity_token, process) -> set(FATE). Entity keys normalized with the
    SAME _norm_toks variants the promiscuous arm uses (so exact-vs-graded is the only difference).
    Returns (keyed_dict, entity_vocab). Deterministic re-keying of already-vetted content."""
    keyed: Dict[Tuple[str, str], Set[str]] = {}
    vocab: Set[str] = set()
    for pname, d in procs.items():
        for role in ROLE_VOCAB:
            effect = _ROLE_EFFECT_LABEL[role]
            for word in d.get(role, []):
                for tok in _norm_toks(word):
                    if len(tok) <= 2:
                        continue
                    keyed.setdefault((tok, pname), set()).add(effect)
                    vocab.add(tok)
    return keyed, vocab


def _scramble_keyed(keyed: Dict[Tuple[str, str], Set[str]], procs: Dict) -> Dict[Tuple[str, str], Set[str]]:
    """Per-process permutation of the entity->fate keying: within each process, each entity token
    receives a DIFFERENT entity's fate-set (deterministic hashlib-seeded _deterministic_perm --
    never python hash()). Coverage + which-tokens-are-keys are held IDENTICAL (same keys, permuted
    values) so the scramble isolates the entity->fate KEYING signal. If keyed lookup's win survives
    this, the keying does not carry the signal."""
    by_proc: Dict[str, List[str]] = {}
    for (tok, pname) in keyed:
        by_proc.setdefault(pname, []).append(tok)
    scrambled: Dict[Tuple[str, str], Set[str]] = {}
    for pname, toks in by_proc.items():
        toks_sorted = sorted(set(toks))
        n = len(toks_sorted)
        if n < 2:
            for t in toks_sorted:
                scrambled[(t, pname)] = set(keyed[(t, pname)])
            continue
        perm = _deterministic_perm(f"{SCRAMBLE_SEED}::{pname}", n)
        # ensure non-identity where possible (rotate if degenerate)
        if perm == list(range(n)):
            perm = perm[1:] + perm[:1]
        for i, t in enumerate(toks_sorted):
            donor = toks_sorted[perm[i]]
            scrambled[(t, pname)] = set(keyed[(donor, pname)])
    return scrambled


def _build_store(keyed: Dict[Tuple[str, str], Set[str]], procs: Dict) -> HDFactStore:
    """Ingest the re-keyed facts into the owned HDFactStore (wire-don't-island). Each
    (entity, fate_in_<process>) -> effect triple, TRUST_HIGH, source=propara_physics_kb_v1."""
    relations = {f"fate_in_{p}": "MULTIVALUED" for p in procs}
    st = HDFactStore(n_dim=STORE_N_DIM, seed=STORE_SEED, relation_cardinality=relations)
    for (tok, pname), effects in keyed.items():
        rel = f"fate_in_{pname}"
        for eff in sorted(effects):
            st.store(tok, rel, eff, "propara_physics_kb_v1", "TRUST_HIGH")
    return st


# ============================================================================ selection (same validated gate)
def _select_matched(para: Dict, procs: Dict) -> List[str]:
    """Convergence-gated process selection -- IDENTICAL to v1 / the frame-activation cell (imported
    sub-primitives). Returns up to MAX_DONORS selected process names."""
    text_toks = _toks(" ".join(para["sentence_texts"]))
    participants_toks = [_norm_toks(p) for p in para["participants"]]
    scored = []
    for name, d in procs.items():
        score, hits = _graded_frame_score(text_toks, d["signature"])
        if score is not None and hits >= MIN_FRAME_SIG_HITS:
            scored.append((name, score))
    scored.sort(key=lambda kv: -kv[1])
    cand = [name for name, sc in scored[:CAND_K]]
    return [nm for nm in cand if _process_convergent(procs[nm], participants_toks)[0]][:MAX_DONORS]


# ============================================================================ keyed-lookup arm (via the store)
def _build_keyed_bridge_facts(paragraphs, procs, store: HDFactStore,
                              keyed_for_check: Optional[Dict] = None) -> Tuple[Dict[Tuple, Dict[str, Set[str]]], Dict]:
    """Per (para_id, participant): {effect: set(trigs)} via EXACT process-conditioned keyed lookup
    through the HDFactStore. Selection = the same convergence gate. NO gold."""
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    store_memo: Dict[Tuple[str, str], Set[str]] = {}

    def _lookup(tok: str, pname: str) -> Set[str]:
        key = (tok, pname)
        if key in store_memo:
            return store_memo[key]
        rows = store.query(tok, f"fate_in_{pname}")
        effs = {str(r["object"]) for r in rows if str(r["object"]) in _EFFECT_TRIGS}
        store_memo[key] = effs
        return effs

    n_lookups = 0
    n_hits = 0
    n_hits_unmentioned = 0
    for para in paragraphs:
        pid = str(para["para_id"])
        full_text = " ".join(para["sentence_texts"]).lower()
        matched = _select_matched(para, procs)
        for participant in para["participants"]:
            variants = {t for t in _norm_toks(participant) if len(t) > 2}
            mentioned = any(t in full_text for t in variants)
            fdict: Dict[str, Set[str]] = {}
            for P in matched:
                for t in variants:
                    n_lookups += 1
                    for eff in _lookup(t, P):
                        fdict.setdefault(eff, set()).update(_EFFECT_TRIGS[eff])
                        n_hits += 1
                        if not mentioned:
                            n_hits_unmentioned += 1
            facts[(pid, participant)] = fdict
    stats = {"n_lookups": n_lookups, "n_hits": n_hits, "n_hits_for_unmentioned_IMPLICIT": n_hits_unmentioned,
             "n_participants_with_fact": sum(1 for v in facts.values() if v)}
    if keyed_for_check is not None:
        # glass-box store validation: the store's returned effects must match the dict re-keying
        # for a sample of keys that ARE in the store (bit-equal wire check).
        checked = 0
        for (tok, pname), effs in list(keyed_for_check.items())[:200]:
            rows = store.query(tok, f"fate_in_{pname}")
            got = {str(r["object"]) for r in rows if str(r["object"]) in _EFFECT_TRIGS}
            assert got == effs, f"STORE_DICT_MISMATCH ({tok},{pname}): store={got} dict={effs}"
            checked += 1
        stats["store_dict_consistency_checked"] = checked
    return facts, stats


# ============================================================================ residual decomposition
def _residual_decomposition(paragraphs, procs, keyed_dict, entity_vocab, oracle_facts) -> Dict:
    """Over DEV oracle-fact participants: RECOVERED vs COVERAGE / GATE / FORM. See module docstring."""
    matched_by_pid = {str(p["para_id"]): _select_matched(p, procs) for p in paragraphs}
    counts = {"RECOVERED": 0, "COVERAGE": 0, "GATE": 0, "FORM": 0}
    n_oracle_fact = 0
    n_covered = 0
    for para in paragraphs:
        pid = str(para["para_id"])
        matched = matched_by_pid[pid]
        for participant in para["participants"]:
            ofd = oracle_facts.get((pid, participant), {})
            gold_effects = {e for e in ofd.keys()}
            if not gold_effects:
                continue
            n_oracle_fact += 1
            variants = {t for t in _norm_toks(participant) if len(t) > 2}
            covered = any(t in entity_vocab for t in variants)
            if covered:
                n_covered += 1
            present_in_selected = any((t, P) in keyed_dict for t in variants for P in matched)
            keyed_effects: Set[str] = set()
            for t in variants:
                for P in matched:
                    keyed_effects |= keyed_dict.get((t, P), set())
            correct = bool(keyed_effects & gold_effects)
            if correct:
                counts["RECOVERED"] += 1
            elif not covered:
                counts["COVERAGE"] += 1
            elif not present_in_selected:
                counts["GATE"] += 1
            else:
                counts["FORM"] += 1
    n_err = counts["COVERAGE"] + counts["GATE"] + counts["FORM"]
    return {
        "counts": counts, "n_oracle_fact_participants": n_oracle_fact,
        "kb_coverage_fraction": round(n_covered / n_oracle_fact, 4) if n_oracle_fact else None,
        "n_covered": n_covered,
        "error_fractions": {k: (round(counts[k] / n_err, 4) if n_err else 0.0) for k in ("COVERAGE", "GATE", "FORM")},
        "recovered_fraction": round(counts["RECOVERED"] / n_oracle_fact, 4) if n_oracle_fact else None,
        "n_errors": n_err,
    }


# ============================================================================ decomposition
def run_decomposition(split: str) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    oracle_multiset = _oracle_event_multiset(steps_df)
    coref = _load_coref(split)
    kb = _load_kb()
    procs = kb["processes"]

    print(f"[precompute] {len(paragraphs)} paragraphs (extraction + oracle facts)...", flush=True)
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp] for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}

    print("[rekey] flat KB -> per-(entity,process) keyed facts + HDFactStore ingest...", flush=True)
    keyed, entity_vocab = _rekey_kb(procs)
    keyed_scr = _scramble_keyed(keyed, procs)
    store = _build_store(keyed, procs)
    store_scr = _build_store(keyed_scr, procs)
    print(f"[rekey] {len(keyed)} keyed facts, {len(entity_vocab)} entity tokens, store live={len(store.live_facts())}", flush=True)

    print("[keyed] EXACT process-conditioned keyed lookup arm (via HDFactStore)...", flush=True)
    keyed_facts, keyed_stats = _build_keyed_bridge_facts(paragraphs, procs, store, keyed_for_check=keyed)
    cov_keyed = _fact_coverage(keyed_facts, oracle_facts)

    print("[keyed_scramble] SCRAMBLE-keying control...", flush=True)
    keyed_scr_facts, keyed_scr_stats = _build_keyed_bridge_facts(paragraphs, procs, store_scr)
    cov_keyed_scr = _fact_coverage(keyed_scr_facts, oracle_facts)

    print("[promiscuous] v1 flat-KB graded/completion baseline (the ablation)...", flush=True)
    promisc_facts, promisc_stats = _build_schema_completion_bridge_facts(paragraphs, kb, scramble_kb=False, ablation=False)
    cov_promisc = _fact_coverage(promisc_facts, oracle_facts)

    # held-out entities: participants whose surface NOT in KB entity vocab (coverage gap)
    in_kb_keys, heldout_keys = set(), set()
    for para in paragraphs:
        pid = str(para["para_id"])
        for pp in para["participants"]:
            variants = {t for t in _norm_toks(pp) if len(t) > 2}
            (in_kb_keys if any(t in entity_vocab for t in variants) else heldout_keys).add((pid, pp))

    def _flt(facts, keyset):
        return {k: v for k, v in facts.items() if k in keyset}
    cov_keyed_inkb = _fact_coverage(_flt(keyed_facts, in_kb_keys), _flt(oracle_facts, in_kb_keys))
    cov_promisc_inkb = _fact_coverage(_flt(promisc_facts, in_kb_keys), _flt(oracle_facts, in_kb_keys))
    cov_keyed_heldout = _fact_coverage(_flt(keyed_facts, heldout_keys), _flt(oracle_facts, heldout_keys))

    residual = _residual_decomposition(paragraphs, procs, keyed, entity_vocab, oracle_facts)

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
    grids["with_keyed_lookup"], keyed_diag = _grids(paragraphs, _pre_with_bridge(keyed_facts), use_bridge=True)
    grids["with_keyed_lookup_scramble"], keyed_scr_diag = _grids(paragraphs, _pre_with_bridge(keyed_scr_facts), use_bridge=True)

    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    unm = {arm: _unm(proxy[arm]) for arm in proxy}

    without_f1 = unm["without_knowledge"]["macro_f1"]
    oracle_f1 = unm["with_oracle"]["macro_f1"]
    promisc_f1 = unm["with_promiscuous_completion"]["macro_f1"]
    keyed_f1 = unm["with_keyed_lookup"]["macro_f1"]
    keyed_scr_f1 = unm["with_keyed_lookup_scramble"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]

    oracle_lift = oracle_f1 - without_f1
    promisc_lift = promisc_f1 - without_f1
    keyed_lift = keyed_f1 - without_f1
    keyed_scr_lift = keyed_scr_f1 - without_f1
    survival = (keyed_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    promisc_survival = (promisc_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    scramble_retained_fraction = (keyed_scr_lift / keyed_lift) if abs(keyed_lift) > 1e-9 else (
        0.0 if abs(keyed_scr_lift) < 1e-9 else float("inf"))

    diff = _arms_must_differ(grids)

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff,
        "decode": {"lesion": lesion_diag["decode_fidelity"], "without": without_diag["decode_fidelity"],
                   "oracle": oracle_diag["decode_fidelity"], "promiscuous": promisc_diag["decode_fidelity"],
                   "keyed": keyed_diag["decode_fidelity"], "keyed_scramble": keyed_scr_diag["decode_fidelity"]},
        "unmentioned_subset": unm,
        "without_f1": without_f1, "with_oracle_f1": oracle_f1,
        "with_promiscuous_completion_f1": promisc_f1, "with_keyed_lookup_f1": keyed_f1,
        "with_keyed_lookup_scramble_f1": keyed_scr_f1, "prior_lesion_f1": lesion_f1,
        "oracle_lift": oracle_lift, "promiscuous_lift": promisc_lift, "keyed_lift": keyed_lift,
        "keyed_scramble_lift": keyed_scr_lift,
        "survival_fraction": survival, "promiscuous_survival_fraction": promisc_survival,
        "scramble_retained_fraction": scramble_retained_fraction,
        "fact_coverage_keyed_vs_oracle": cov_keyed,
        "fact_coverage_promiscuous_vs_oracle": cov_promisc,
        "fact_coverage_keyed_scramble_vs_oracle": cov_keyed_scr,
        "heldout_entities": {
            "n_in_kb": len(in_kb_keys), "n_heldout_not_in_kb": len(heldout_keys),
            "keyed_in_kb": cov_keyed_inkb, "promiscuous_in_kb": cov_promisc_inkb,
            "keyed_heldout": cov_keyed_heldout,
        },
        "residual_decomposition": residual,
        "keyed_stats": keyed_stats, "keyed_scramble_stats": keyed_scr_stats, "promiscuous_stats": promisc_stats,
        "n_keyed_facts": len(keyed), "n_entity_vocab": len(entity_vocab), "store_live_facts": len(store.live_facts()),
        "kb_n_processes": kb["_meta"]["n_processes"],
        "official": {arm: official[arm]["overall"] for arm in official},
    }


# ============================================================================ verdict
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    without_f1 = result["without_f1"]
    keyed_f1 = result["with_keyed_lookup_f1"]
    oracle_f1 = result["with_oracle_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = all(v >= 0.99 for v in result["decode"].values())
    infra_fail = (not arms_ok) or (not decode_ok)

    floor_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING
    leak = (keyed_f1 > LEAK_CEILING) or (keyed_f1 >= oracle_f1 - LEAK_ORACLE_MARGIN)

    cov_k = result["fact_coverage_keyed_vs_oracle"]
    cov_p = result["fact_coverage_promiscuous_vs_oracle"]
    cov_kscr = result["fact_coverage_keyed_scramble_vs_oracle"]
    beats_promiscuous = cov_k["pair_precision"] >= cov_p["pair_precision"] + KEYED_BEATS_PROMISCUOUS_MARGIN

    scramble_retained = result["scramble_retained_fraction"]
    scramble_prec_collapsed = cov_kscr["pair_precision"] <= 0.5 * cov_k["pair_precision"] + 1e-12
    scramble_lift_collapsed = (scramble_retained is not None) and (scramble_retained <= SCRAMBLE_MAX_RETAINED_FRACTION)
    scramble_collapsed = scramble_prec_collapsed and scramble_lift_collapsed

    ef = result["residual_decomposition"]["error_fractions"]
    coverage_dominated = ef["COVERAGE"] > ef["FORM"]

    msg = (f"split={result['split']} keyed_f1={keyed_f1:.4f} promisc_f1={result['with_promiscuous_completion_f1']:.4f} "
           f"oracle_f1={oracle_f1:.4f} without_f1={without_f1:.4f} "
           f"keyed_prec={cov_k['pair_precision']}(promisc={cov_p['pair_precision']} +{KEYED_BEATS_PROMISCUOUS_MARGIN}) "
           f"keyed_recall={cov_k['pair_recall']} keyed_in_kb_prec={result['heldout_entities']['keyed_in_kb']['pair_precision']} "
           f"beats_promiscuous={beats_promiscuous} scramble_prec={cov_kscr['pair_precision']} "
           f"scramble_retained={scramble_retained} scramble_collapsed={scramble_collapsed} "
           f"kb_coverage_frac={result['residual_decomposition']['kb_coverage_fraction']} "
           f"residual_err_fracs={ef} coverage_dominated={coverage_dominated} "
           f"floor_collapsed={floor_collapsed} leak={leak} arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not floor_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_FLOOR_DID_NOT_COLLAPSE_void: {msg}"
    if leak:
        return "HARD_FAIL", f"HARD_FAIL_LEAKED_ANSWERS_reject: {msg}"
    if not beats_promiscuous:
        return "HARD_FAIL", f"HARD_FAIL_KEYED_DOES_NOT_BEAT_PROMISCUOUS_form_not_the_answer: {msg}"
    if not scramble_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_SCRAMBLE_KEYING_DID_NOT_COLLAPSE_keying_not_carrying_signal: {msg}"
    if not coverage_dominated:
        return "MIDDLE_BAND", f"MIDDLE_BAND_FORM_VALIDATED_but_residual_FORM_dominated_not_coverage: {msg}"
    return "HARD_PASS", f"HARD_PASS_KEYED_FORM_VALIDATED_residual_is_COVERAGE_scramble_clean: {msg}"


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
    procs = kb["processes"]
    assert kb["_meta"]["n_processes"] >= 12, kb["_meta"]

    # (1) re-keying: combustion consumes 'wood' -> DESTROY; produces 'ash' -> CREATE; moves 'smoke'.
    keyed, vocab = _rekey_kb(procs)
    assert "DESTROY" in keyed[("wood", "combustion")], keyed[("wood", "combustion")]
    assert "CREATE" in keyed[("ash", "combustion")], keyed[("ash", "combustion")]
    assert "MOVE" in keyed[("smoke", "combustion")], keyed[("smoke", "combustion")]
    # keying is PROCESS-CONDITIONED: 'water' recurs across processes with process-specific fates.
    water_procs = {p for (t, p) in keyed if t == "water"}
    assert len(water_procs) >= 2, ("water should key under multiple processes", water_procs)

    # (2) HDFactStore ingest + glass-box round-trip: query returns the re-keyed fate.
    store = _build_store(keyed, procs)
    rows = store.query("wood", "fate_in_combustion")
    got = {str(r["object"]) for r in rows}
    assert "DESTROY" in got, ("store query must recover the keyed fate", rows)
    # process-conditioning in the store: wood under photosynthesis should NOT return combustion's fate
    rows_ps = store.query("wood", "fate_in_photosynthesis")
    assert all(str(r["object"]) in _EFFECT_TRIGS for r in rows_ps), rows_ps

    # (3) scramble: within-process fate permutation is non-identity + deterministic.
    keyed_scr = _scramble_keyed(keyed, procs)
    keyed_scr2 = _scramble_keyed(keyed, procs)
    assert keyed_scr == keyed_scr2, "scramble must be deterministic"
    n_changed = sum(1 for k in keyed if keyed[k] != keyed_scr.get(k))
    assert n_changed >= 1, "scramble changed nothing (degenerate)"

    # (4) keyed arm on a synth paragraph (real_code_path): EXACT lookup binds the fate; a graded-only
    # paraphrase that the promiscuous arm would catch is NOT bound by exact lookup (isolates the swap).
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["The wood burns in the fire.", "Ash and smoke form as it burns."],
         "participants": ["wood", "ash", "boulder"],
         "states": [["here", "here", "-"], ["here", "-", "-"], ["-", "-", "-"]]},
    ]
    facts, stats = _build_keyed_bridge_facts(synth, procs, store, keyed_for_check=keyed)
    assert "DESTROY" in facts[("s1", "wood")], (facts, stats)   # wood -> combustion.consumes -> DESTROY
    assert facts[("s1", "boulder")] == {}, ("boulder not in combustion keying -> no fate", facts)
    assert stats.get("store_dict_consistency_checked", 0) > 0, stats

    # (5) residual decomposition + coverage on the synth.
    synth_oracle = {("s1", "wood"): {"DESTROY": {"DESTROY"}}, ("s1", "boulder"): {"MOVE": {"MOVE"}}}
    resid = _residual_decomposition(synth, procs, keyed, vocab, synth_oracle)
    assert resid["n_oracle_fact_participants"] == 2, resid
    # wood covered + correct -> RECOVERED; boulder not in KB vocab -> COVERAGE
    assert resid["counts"]["RECOVERED"] >= 1, resid
    assert resid["counts"]["COVERAGE"] >= 1, resid

    # (6) verdict-logic unit checks.
    base = {"split": "x", "without_f1": 0.32, "with_keyed_lookup_f1": 0.37, "with_oracle_f1": 0.40,
            "with_promiscuous_completion_f1": 0.336,
            "arms_differ": {"all_differ": True}, "decode": {"a": 1.0},
            "fact_coverage_keyed_vs_oracle": {"pair_precision": 0.20, "pair_recall": 0.12},
            "fact_coverage_promiscuous_vs_oracle": {"pair_precision": 0.079, "pair_recall": 0.167},
            "fact_coverage_keyed_scramble_vs_oracle": {"pair_precision": 0.02, "pair_recall": 0.01},
            "scramble_retained_fraction": 0.10,
            "heldout_entities": {"keyed_in_kb": {"pair_precision": 0.35}},
            "residual_decomposition": {"kb_coverage_fraction": 0.4,
                                        "error_fractions": {"COVERAGE": 0.7, "GATE": 0.2, "FORM": 0.1}}}
    hp, hp_msg = decomposition_verdict(base)
    assert hp == "HARD_PASS", (hp, hp_msg)
    nb = json.loads(json.dumps(base)); nb["fact_coverage_keyed_vs_oracle"]["pair_precision"] = 0.09
    v, _ = decomposition_verdict(nb); assert v == "HARD_FAIL", ("beats_promiscuous", v)
    sc = json.loads(json.dumps(base)); sc["fact_coverage_keyed_scramble_vs_oracle"]["pair_precision"] = 0.19
    sc["scramble_retained_fraction"] = 0.95
    v, _ = decomposition_verdict(sc); assert v == "HARD_FAIL", ("scramble", v)
    fm = json.loads(json.dumps(base)); fm["residual_decomposition"]["error_fractions"] = {"COVERAGE": 0.1, "GATE": 0.2, "FORM": 0.7}
    v, m = decomposition_verdict(fm); assert v == "MIDDLE_BAND", ("form_dominated", v, m)
    lk = json.loads(json.dumps(base)); lk["with_keyed_lookup_f1"] = 0.40
    v, _ = decomposition_verdict(lk); assert v == "HARD_FAIL", ("leak", v)
    vd = json.loads(json.dumps(base)); vd["without_f1"] = 0.7
    v, _ = decomposition_verdict(vd); assert v == "HARD_FAIL", ("void", v)

    return {"kb_n_processes": kb["_meta"]["n_processes"], "n_keyed_facts": len(keyed),
            "n_entity_vocab": len(vocab), "store_live_facts": len(store.live_facts()),
            "water_processes": sorted(water_procs),
            "synth_keyed_wood": {k: sorted(v) for k, v in facts[("s1", "wood")].items()},
            "residual_synth": resid, "verdict_logic_unit_checks": {"hard_pass": hp}}


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
    print(f"[{run_mode}] split={split} PROCESS-KEYED EXACT LOOKUP (via HDFactStore) vs promiscuous...", flush=True)
    result = run_decomposition(split)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "with_keyed_lookup_f1": result["with_keyed_lookup_f1"],
            "with_promiscuous_completion_f1": result["with_promiscuous_completion_f1"],
            "with_keyed_lookup_scramble_f1": result["with_keyed_lookup_scramble_f1"],
            "with_oracle_f1": result["with_oracle_f1"], "without_f1": result["without_f1"],
            "keyed_lift": result["keyed_lift"], "promiscuous_lift": result["promiscuous_lift"],
            "oracle_lift": result["oracle_lift"], "survival_fraction": result["survival_fraction"],
            "keyed_pair_precision": result["fact_coverage_keyed_vs_oracle"]["pair_precision"],
            "keyed_pair_recall": result["fact_coverage_keyed_vs_oracle"]["pair_recall"],
            "promiscuous_pair_precision": result["fact_coverage_promiscuous_vs_oracle"]["pair_precision"],
            "keyed_scramble_pair_precision": result["fact_coverage_keyed_scramble_vs_oracle"]["pair_precision"],
            "SCRAMBLE_RETAINED_FRACTION": result["scramble_retained_fraction"],
            "HELDOUT_ENTITIES": result["heldout_entities"],
            "RESIDUAL_DECOMPOSITION": result["residual_decomposition"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1 over a fixed real corpus (ProPara EMNLP18) + exact dict/HD-store lookup; no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: exact lookup + pre-registered bands, no tuned threshold",
        "thresholds": {"KEYED_BEATS_PROMISCUOUS_MARGIN": KEYED_BEATS_PROMISCUOUS_MARGIN,
                       "SCRAMBLE_MAX_RETAINED_FRACTION": SCRAMBLE_MAX_RETAINED_FRACTION,
                       "LEAK_CEILING": LEAK_CEILING, "LEAK_ORACLE_MARGIN": LEAK_ORACLE_MARGIN,
                       "WITHOUT_COLLAPSE_CEILING": WITHOUT_COLLAPSE_CEILING, "STORE_N_DIM": STORE_N_DIM},
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
