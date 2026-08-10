# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; prior_lesion/reasoning/scramble grids differ)
# - final_metrics_atomicity: tmp_replace (single-shot; scramble seeds = fast inner loop)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold
# - HP_SCOPE: {content_delta: [content_delta_loc_positive_over_prior_lesion, content_delta_loc_scramble_clean_median]}
# - cardinality_ok: EXPECTED_N_SCRAMBLE_SEEDS=len(SCRAMBLE_SEEDS)=2(smoke)/8(full)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (bands = v3's, applied unchanged -- ARM2 is the
#   extraction-cost test AGAINST v3's oracle bands; not re-tuned)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (spaCy parse + v3 firing + official_eval) at tiny scale
#   (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_propara_arm2_extracted_structure_v1.md for the full pre-reg.
"""exp_propara_arm2_extracted_structure_v1 -- ARM 2: does the scramble-clean MOVES localization
signal from v3 (oracle structure) SURVIVE when the structure is EXTRACTED from raw text?

v3 (exp_propara_decisive_inference_arm1_v3_stateful_verb_v1, HARD_PASS) proved the MECHANISM: a
sequential, state-conditioned, verb-class-gated firing loop produces an order-dependent,
scramble-clean localization signal (content_delta_loc +0.027, moves +0.082, median retained
0.185, 6/8 collapse) -- GIVEN the oracle event-COUNT multiset. ARM 2 is the decisive end-to-end
test of the extraction-as-foundation plan: swap the ONE variable (oracle structure -> EXTRACTED
structure), keep the v3 firing mechanism EXACTLY.

WHAT IS EXTRACTED (from raw text, not oracle):
  - ENTITIES / cross-sentence linking: fastcoref (biu-nlp/f-coref) clusters, precomputed in system
    python (tools/benchmark_trap_check/run_fastcoref_propara_v1.py -> propara_fastcoref_
    predictions_v1.json) and aligned to participants + sentences by char-span overlap here. Links
    pronoun/alias mentions (e.g. Plants<->They) so verb attribution works on sentences that do not
    name the participant.
  - VERBS / verb-class attribution: spaCy (en_core_web_sm) dependency parse per sentence -> the
    verb lemma whose subject / object / prep-object is a participant mention (coref-linked) ->
    classified by the SAME curated verb-class lexicon reused verbatim from v3. This replaces v3's
    participant-AGNOSTIC sentence-level verb-class with participant-SPECIFIC dep-parse attribution.
  - EVENT-COUNT BUDGET: the oracle multiset is WITHHELD. Each participant's canonical event budget
    (#CREATE capped 1, #MOVE, #DESTROY capped 1) is EXTRACTED = the count of verb-class events
    attributed to that participant across the paragraph (coref + dep-parse). This is the key swap.
WHAT IS GRANTED (flagged, standard-ProPara or uniform-across-arms so unbiased):
  - PARTICIPANT LIST: the gold participant set is the TASK INPUT in ProPara (systems are given the
    participants and predict their state grids; the official evaluator requires exact-match
    participants) -- NOT oracle leakage, standard for every ProPara system.
  - LOCATIONS: not extracted; represented by the uniform LOCATION_UNKNOWN placeholder in every
    predicted grid (identical across ALL arms incl. the prior-lesion), so it cannot bias the
    content_delta. Flagged as still-granted (the from->to span extraction is deferred). The MOVES
    content signal is a step-LOCALIZATION signal (step_id + participant match), which the
    placeholder does not confound because it is arm-uniform.

MECHANISM: byte-identical v3 firing (reused import: _assign_verb_stateful / _canonical_sequence /
_grids_from_assign / verb_classes) -- ONLY the (budget, per-sentence verb evidence) inputs change
from oracle/sentence-level to EXTRACTED/participant-attributed.

CONTROLS (same dual as v3, mandatory): PRIOR-LESION (EXTRACTED budget + random-monotonic
placement -- content-free localization, isolates the firing/localization content contribution
WITHIN the extracted-budget regime) + 8 scramble seeds. Claim on MOVES/localization.

EXTRACTION-COST attribution (reported): extracted-vs-oracle budget fidelity (per-class
precision/recall + exact-match rate), coref participant-link rate, verb-attribution rate. If the
signal survives -> FIRST end-to-end glass-box comprehension signal on real prose. If it vanishes
-> the component with worst fidelity is the extraction-improvement target (coref LingMess lever /
better verb-SRL / location extraction).

Modes: --self-test (tiny synth, real spaCy + v3 firing + official eval) / --smoke (DEV, 2 seeds) /
--full (TEST, 8 seeds).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

import numpy as np

ANCHOR_NAME = "propara_arm2_extracted_structure_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
COREF_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_fastcoref_predictions_v1.json")

import propara_official_eval as offeval  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset,
    majority_label_grids, bow_label_grids, bag_of_states_label_grids,
    fit_bag_of_states_classifiers,
    _official_corpus_scores, _proxy_scores, _arms_must_differ, _det_seed,
)
# REUSE v3 firing mechanism VERBATIM (import, do NOT re-transcribe): the localization engine.
from experiments.exp_propara_decisive_inference_arm1_v3_stateful_verb_v1 import (  # noqa: E402
    verb_classes, VERB_CLASS_SETS, _canonical_sequence, _assign_prior_lesion,
    _rng, _grids_from_assign,
    _loc_official_f1, _existence_official_f1, _focus_f1,
    SCRAMBLE_CLEAN_MEDIAN_HARD_PASS, SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL,
    CONTENT_DELTA_LOC_MIN_POSITIVE,
)
from propara_trap_check import build_step_rows, build_paragraph_set_rows, fit_step_bow  # noqa: E402

import spacy  # noqa: E402

SCRAMBLE_SEEDS_SMOKE = [7, 17]
SCRAMBLE_SEEDS_FULL = [7, 17, 29, 41, 53, 71, 83, 97]

_NLP = None


def _get_nlp():
    global _NLP
    if _NLP is None:
        # tagger+parser+attribute_ruler+lemmatizer needed for lemma + dep; drop ner for speed
        _NLP = spacy.load("en_core_web_sm", disable=["ner"])
    return _NLP


# ============================================================================ coref alignment
def _load_coref(split: str) -> Dict[str, Dict]:
    with open(COREF_PATH, encoding="utf-8") as f:
        d = json.load(f)
    return d[split]


def _participant_tokens(participant: str) -> Set[str]:
    return {t for t in participant.lower().replace(",", " ").replace(";", " ").split() if len(t) > 1}


def _span_to_sentence(span: List[int], sentence_offsets: List[int], n_sent: int) -> int:
    """Map a char span (start,end) to a 0-based sentence index by offset containment."""
    start = span[0]
    idx = 0
    for i in range(n_sent):
        lo = sentence_offsets[i]
        hi = sentence_offsets[i + 1] - 1 if i + 1 < n_sent else 10 ** 9
        if lo <= start < hi:
            idx = i
            break
        idx = i
    return idx


def _participant_mention_sentences(participant: str, para_coref: Dict, sentences: List[str]) -> Set[int]:
    """Sentence indices where the participant is mentioned, via (a) exact token match and (b)
    fastcoref cluster membership (any cluster containing a span whose text overlaps the
    participant's name tokens -> ALL spans in that cluster are participant mentions, incl.
    pronouns/aliases in other sentences)."""
    p_toks = _participant_tokens(participant)
    n_sent = len(sentences)
    sents_l = [s.lower() for s in sentences]
    mention_sents: Set[int] = set()
    # (a) exact token match per sentence
    for i, s in enumerate(sents_l):
        if p_toks & set(s.replace(".", " ").replace(",", " ").split()):
            mention_sents.add(i)
    # (b) coref clusters: a cluster is the participant's iff some span's surface text shares a name token
    text = para_coref["text"]
    offs = para_coref["sentence_offsets"]
    for cl in para_coref["clusters"]:
        cl_is_participant = False
        for span in cl:
            surface = text[span[0]:span[1]].lower()
            if p_toks & set(surface.replace(".", " ").replace(",", " ").split()):
                cl_is_participant = True
                break
        if cl_is_participant:
            for span in cl:
                mention_sents.add(_span_to_sentence(span, offs, n_sent))
    return mention_sents


# ============================================================================ EXTRACTION: per-participant verb evidence + budget
def _extract_participant_evidence(participant: str, sentences: List[str], parsed, para_coref: Dict
                                  ) -> Tuple[Dict[int, Set[str]], Dict[str, int], Dict]:
    """For a participant, EXTRACT per-sentence verb-class evidence + an event-count budget from
    raw text (coref + spaCy dep-parse + verb-class lexicon). Returns (evidence_by_sentence,
    extracted_budget, diag).

    evidence_by_sentence[i] = set of verb classes attributed to the participant in sentence i:
      a verb whose subject / object / prep-object head token overlaps a participant mention
      (exact name OR coref-linked), classified by the verb-class lexicon on the verb LEMMA.
    extracted_budget = {CREATE: min(count,1), MOVE: count, DESTROY: min(count,1)} from the
      chronological (sentence-order) evidence stream (deduped so two adjacent same-class hits in
      one sentence count once)."""
    p_toks = _participant_tokens(participant)
    mention_sents = _participant_mention_sentences(participant, para_coref, sentences)
    evidence: Dict[int, Set[str]] = {}
    diag = {"n_mention_sents": len(mention_sents), "n_attributed_verbs": 0}
    for i, doc in enumerate(parsed):
        classes_here: Set[str] = set()
        p_here = (i in mention_sents)
        for tok in doc:
            if tok.pos_ != "VERB":
                continue
            lemma = tok.lemma_.lower()
            vclass = next((c for c, vset in VERB_CLASS_SETS.items() if lemma in vset), None)
            if vclass is None:
                continue
            # attribution: is a participant mention the subj/obj/pobj of this verb?
            args = []
            for c in tok.children:
                if c.dep_ in ("nsubj", "nsubjpass", "dobj", "attr", "oprd"):
                    args.append(c.text.lower())
                if c.dep_ == "prep":
                    for gc in c.children:
                        if gc.dep_ == "pobj":
                            args.append(gc.text.lower())
            arg_toks = set(" ".join(args).replace(".", " ").replace(",", " ").split())
            attributed = bool(p_toks & arg_toks)
            # coref fallback: if the participant is mentioned in this sentence (via coref, e.g.
            # pronoun "They") and the verb has a pronoun/other subject, still attribute -- the
            # coref link is the participant-specificity, dep-parse alone misses pronoun aliases
            if not attributed and p_here:
                attributed = True
            if attributed:
                classes_here.add(vclass)
                diag["n_attributed_verbs"] += 1
        if classes_here:
            evidence[i] = classes_here
    # extracted budget from the chronological evidence stream
    seq_classes = []
    for i in sorted(evidence):
        for c in ("CREATE", "MOVE", "DESTROY"):
            if c in evidence[i]:
                seq_classes.append(c)
    budget = {"CREATE": min(seq_classes.count("CREATE"), 1),
              "MOVE": seq_classes.count("MOVE"),
              "DESTROY": min(seq_classes.count("DESTROY"), 1)}
    return evidence, budget, diag


def _assign_extracted_verb_stateful(budget: Dict[str, int], evidence: Dict[int, Set[str]],
                                    presented_true_steps: List[int], n: int, rng) -> Dict[int, str]:
    """v3's sequential state-conditioned firing, using the EXTRACTED per-sentence participant-
    attributed evidence (evidence[true_step_0based] = set of classes) instead of v3's sentence-
    level verb_classes. Walk presented positions in order; fire the next canonical event (from the
    EXTRACTED budget) when the presented sentence's attributed evidence contains the matching class
    AND state allows. Unfired -> random unused true steps (content-free fallback, same as v3)."""
    seq = _canonical_sequence(budget, n)
    if not seq:
        return {}
    c0 = min(int(budget.get("CREATE", 0)), 1)
    exists = (c0 == 0)
    ptr = 0
    assigned: Dict[int, str] = {}
    used: Set[int] = set()
    for true_step in presented_true_steps:
        if ptr >= len(seq):
            break
        if true_step in used:
            continue
        classes = evidence.get(true_step - 1, set())  # evidence keyed by 0-based sentence index
        nxt = seq[ptr]
        state_ok = (nxt == "CREATE" and not exists) or (nxt in ("MOVE", "DESTROY") and exists)
        if state_ok and nxt in classes:
            assigned[true_step] = nxt
            used.add(true_step)
            if nxt == "CREATE":
                exists = True
            elif nxt == "DESTROY":
                exists = False
            ptr += 1
    remaining = seq[ptr:]
    if remaining:
        free = [s for s in range(1, n + 1) if s not in used]
        if free:
            picks = sorted(rng.sample(free, min(len(remaining), len(free))))
            for j, step in enumerate(picks):
                assigned[step] = remaining[j]
    return assigned


# ============================================================================ per-paragraph extraction (parse once, cache)
def _extract_paragraph(para: Dict, para_coref: Dict) -> Dict[str, Dict]:
    """Returns per-participant {evidence, budget, diag}, parsing each sentence ONCE."""
    sentences = para["sentence_texts"]
    nlp = _get_nlp()
    parsed = list(nlp.pipe(sentences))
    out = {}
    for participant in para["participants"]:
        evidence, budget, diag = _extract_participant_evidence(participant, sentences, parsed, para_coref)
        out[participant] = {"evidence": evidence, "budget": budget, "diag": diag}
    return out


# ============================================================================ grid builders (extracted)
def extracted_reasoning_label_grids(paragraphs, extraction, scramble=False, scramble_seed=0):
    def _fn(para, participant, n):
        para_id = str(para["para_id"])
        ex = extraction[para_id][participant]
        budget, evidence = ex["budget"], ex["evidence"]
        if scramble:
            perm = _rng(f"arm2_scramble_{scramble_seed}_{para_id}").sample(range(n), n)
        else:
            perm = list(range(n))
        presented_true_steps = [p + 1 for p in perm]
        rng = _rng(f"arm2_verbfallback_{scramble}_{scramble_seed}_{para_id}_{participant}")
        return _assign_extracted_verb_stateful(budget, evidence, presented_true_steps, n, rng)
    return _grids_from_assign(paragraphs, _fn)


def extracted_prior_lesion_label_grids(paragraphs, extraction):
    """Content-lesion WITHIN the extracted-budget regime: EXTRACTED budget + random-monotonic
    placement (ZERO verb-firing). Isolates the localization content contribution given the same
    (noisy) extracted budget the reasoning arm gets."""
    def _fn(para, participant, n):
        para_id = str(para["para_id"])
        budget = extraction[para_id][participant]["budget"]
        rng = _rng(f"arm2_prior_lesion_{para_id}_{participant}")
        return _assign_prior_lesion(budget, n, rng)
    return _grids_from_assign(paragraphs, _fn)


# ============================================================================ extraction-cost diagnostics
def _budget_fidelity(extraction: Dict, oracle_multiset: Dict, paragraphs: List[Dict]) -> Dict:
    """Compare EXTRACTED budget vs ORACLE budget per (para, participant): exact-match rate + per-
    class precision/recall of the extracted event counts (treating each class's count as the
    quantity). Localizes the event-count-extraction cost."""
    exact = 0
    total = 0
    tp = {c: 0 for c in ("CREATE", "MOVE", "DESTROY")}
    fp = {c: 0 for c in ("CREATE", "MOVE", "DESTROY")}
    fn = {c: 0 for c in ("CREATE", "MOVE", "DESTROY")}
    n_mention = 0
    n_attr = 0
    for para in paragraphs:
        pid = str(para["para_id"])
        for participant in para["participants"]:
            ex = extraction[pid][participant]
            eb = ex["budget"]
            n_mention += ex["diag"]["n_mention_sents"]
            n_attr += ex["diag"]["n_attributed_verbs"]
            ob = oracle_multiset.get((para["para_id"], participant), {"CREATE": 0, "MOVE": 0, "DESTROY": 0})
            ob_cap = {"CREATE": min(ob.get("CREATE", 0), 1), "MOVE": ob.get("MOVE", 0),
                      "DESTROY": min(ob.get("DESTROY", 0), 1)}
            total += 1
            if eb == ob_cap:
                exact += 1
            for c in ("CREATE", "MOVE", "DESTROY"):
                tp[c] += min(eb[c], ob_cap[c])
                fp[c] += max(eb[c] - ob_cap[c], 0)
                fn[c] += max(ob_cap[c] - eb[c], 0)
    def _pr(c):
        p = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) else 0.0
        r = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) else 0.0
        f = 2 * p * r / (p + r) if (p + r) else 0.0
        return {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4),
                "tp": tp[c], "fp": fp[c], "fn": fn[c]}
    return {"budget_exact_match_rate": round(exact / max(total, 1), 4), "n_pairs": total,
            "per_class": {c: _pr(c) for c in ("CREATE", "MOVE", "DESTROY")},
            "n_mention_sentences_total": n_mention, "n_attributed_verbs_total": n_attr}


# ============================================================================ decomposition over a split
def run_decomposition(split: str, train_paragraphs: List[Dict], scramble_seeds: List[int]) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    train_set_df = build_paragraph_set_rows(train_paragraphs)
    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)  # used ONLY for the cost diagnostic, NOT the arms
    coref = _load_coref(split)

    # EXTRACT structure per paragraph (parse once)
    print(f"[extract] parsing + coref-aligning {len(paragraphs)} paragraphs...", flush=True)
    extraction = {}
    for para in paragraphs:
        pid = str(para["para_id"])
        extraction[pid] = _extract_paragraph(para, coref[pid])
    budget_fidelity = _budget_fidelity(extraction, oracle_multiset, paragraphs)
    print(f"[extract] budget_exact_match={budget_fidelity['budget_exact_match_rate']} "
          f"move_recall={budget_fidelity['per_class']['MOVE']['recall']}", flush=True)

    grids: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
    grids["majority"] = majority_label_grids(paragraphs)
    grids["bow_singlestep"] = bow_label_grids(paragraphs, vec, clf)
    grids["bagstates"] = bag_of_states_label_grids(paragraphs, bag_clfs)
    grids["prior_lesion"], lesion_diag = extracted_prior_lesion_label_grids(paragraphs, extraction)
    grids["reasoning"], reasoning_diag = extracted_reasoning_label_grids(paragraphs, extraction, scramble=False)

    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    loc = {arm: _loc_official_f1(official[arm]) for arm in official}
    exist = {arm: _existence_official_f1(official[arm]) for arm in official}
    focus = {arm: _focus_f1(proxy[arm]) for arm in proxy}

    content_delta_focus = focus["reasoning"] - focus["prior_lesion"]
    content_delta_loc = loc["reasoning"] - loc["prior_lesion"]
    moves_reasoning = official["reasoning"]["moves"]["f1"]
    moves_lesion = official["prior_lesion"]["moves"]["f1"]
    content_delta_moves = moves_reasoning - moves_lesion

    per_seed = {}
    retained_loc = []
    for seed in scramble_seeds:
        g_scr, scr_diag = extracted_reasoning_label_grids(paragraphs, extraction, scramble=True, scramble_seed=seed)
        off_scr = _official_corpus_scores(paragraphs, g_scr)
        l_scr = _loc_official_f1(off_scr)
        cd_loc_scr = l_scr - loc["prior_lesion"]
        rf_loc = (cd_loc_scr / content_delta_loc) if abs(content_delta_loc) > 1e-9 else None
        if rf_loc is not None:
            retained_loc.append(rf_loc)
        per_seed[str(seed)] = {"scramble_loc_f1": l_scr, "scramble_moves_f1": off_scr["moves"]["f1"],
                               "content_delta_loc_scramble": cd_loc_scr, "retained_frac_loc": rf_loc,
                               "decode_fidelity": scr_diag["decode_fidelity"]}

    diff = _arms_must_differ({"majority": grids["majority"], "bow_singlestep": grids["bow_singlestep"],
                              "bagstates": grids["bagstates"], "prior_lesion": grids["prior_lesion"],
                              "reasoning": grids["reasoning"]})

    def _stats(a):
        arr = np.array(a, dtype=float) if a else np.array([])
        return {"list": a, "median": float(np.median(arr)) if arr.size else None,
                "mean": float(np.mean(arr)) if arr.size else None,
                "min": float(np.min(arr)) if arr.size else None,
                "max": float(np.max(arr)) if arr.size else None,
                "frac_below_0.30": float((arr < 0.30).mean()) if arr.size else None}

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "n_scramble_seeds": len(scramble_seeds), "scramble_seeds": scramble_seeds,
        "extraction_cost": {"budget_fidelity": budget_fidelity,
                            "n_coref_clusters_total": sum(len(coref[str(p['para_id'])]['clusters']) for p in paragraphs)},
        "lesion_decode_diag": lesion_diag, "reasoning_decode_diag": reasoning_diag, "arms_differ": diff,
        "official": official, "proxy": proxy,
        "loc_official_f1": loc, "existence_official_f1": exist, "focus_macro_f1": focus,
        "moves_f1": {arm: official[arm]["moves"]["f1"] for arm in official},
        "conversions_f1": {arm: official[arm]["conversions"]["f1"] for arm in official},
        "content_delta_loc": content_delta_loc, "content_delta_moves": content_delta_moves,
        "content_delta_focus": content_delta_focus,
        "per_seed_scramble": per_seed,
        "retained_frac_loc_stats": _stats(retained_loc),
    }


# ============================================================================ verdict logic (same bands as v3, localization-primary)
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    cd_loc = result["content_delta_loc"]
    cd_moves = result["content_delta_moves"]
    median_rf = result["retained_frac_loc_stats"]["median"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = (result["lesion_decode_diag"]["decode_fidelity"] >= 0.99
                 and result["reasoning_decode_diag"]["decode_fidelity"] >= 0.99)
    infra_fail = (not arms_ok) or (not decode_ok)

    content_real = (cd_loc >= CONTENT_DELTA_LOC_MIN_POSITIVE)
    scramble_clean = (median_rf is not None and median_rf < SCRAMBLE_CLEAN_MEDIAN_HARD_PASS)
    scramble_fragile = (median_rf is None) or (median_rf > SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL)

    genuine = content_real and scramble_clean
    hard_fail_sci = (cd_loc < CONTENT_DELTA_LOC_MIN_POSITIVE) or scramble_fragile

    bf = result["extraction_cost"]["budget_fidelity"]
    msg = (f"split={result['split']} EXTRACTED content_delta_loc={cd_loc:.4f}(>= {CONTENT_DELTA_LOC_MIN_POSITIVE}) "
           f"content_delta_moves={cd_moves:.4f} median_retained_frac_loc={median_rf}"
           f"(< {SCRAMBLE_CLEAN_MEDIAN_HARD_PASS} clean, > {SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL} fragile) "
           f"budget_exact={bf['budget_exact_match_rate']} move_recall={bf['per_class']['MOVE']['recall']} "
           f"arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if genuine:
        return "HARD_PASS", f"HARD_PASS_SIGNAL_SURVIVES_EXTRACTION: {msg}"
    if hard_fail_sci:
        return "HARD_FAIL", f"HARD_FAIL_SIGNAL_VANISHED_UNDER_EXTRACTION: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND_PARTIAL_SURVIVAL: {msg}"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
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
    off_result = offeval.self_test()

    # tiny synthetic corpus with clear verbs + a coref pronoun link (They -> seed)
    # 6 sentences with GAPS so verb-timed firing (CREATE@1, MOVE@3, DESTROY@6) is very unlikely to
    # coincide with the deterministic random-monotonic prior-lesion draw (a tiny 3-events-on-4-steps
    # synth forces them equal by construction -- an artifact, not the mechanism; the real arms-differ
    # gate fires on the full corpus in run_decomposition).
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["A seed appears in the soil.", "Water is added.", "It moves downhill.",
                            "The sun shines.", "Time passes.", "The seed dissolves away."],
         "participants": ["seed"],
         "states": [["-", "soil", "soil", "hill", "hill", "hill", "-"]]},  # CREATE@1, MOVE@3, DESTROY@6
    ]
    text = " ".join(synth[0]["sentence_texts"])
    offs = []
    cur = 0
    for s in synth[0]["sentence_texts"]:
        offs.append(cur); cur += len(s) + 1
    # hand coref: cluster links "A seed"(s0) and "It"(s2) and "The seed"(s5)
    def _find(sub, start):
        i = text.index(sub, start); return [i, i + len(sub)]
    clusters = [[_find("seed", 0), _find("It", offs[2]), _find("seed", offs[5])]]
    coref_para = {"text": text, "sentence_offsets": offs, "n_sentences": 6, "clusters": clusters}
    coref = {"s1": coref_para}

    extraction = {"s1": _extract_paragraph(synth[0], coref["s1"])}
    ex = extraction["s1"]["seed"]
    # extracted budget: appears(CREATE)+moves(MOVE)+dissolves(DESTROY) attributed to seed via coref
    assert ex["budget"]["CREATE"] == 1, ex["budget"]
    assert ex["budget"]["MOVE"] >= 1, ex["budget"]
    assert ex["budget"]["DESTROY"] == 1, ex["budget"]
    # "It moves" (sentence index 2) is coref-linked to seed -> MOVE evidence at sentence 2
    assert "MOVE" in ex["evidence"].get(2, set()), ex["evidence"]

    steps_df = build_step_rows(synth)
    oracle = _oracle_event_multiset(steps_df)
    reasoning, r_diag = extracted_reasoning_label_grids(synth, extraction, scramble=False)
    lesion, l_diag = extracted_prior_lesion_label_grids(synth, extraction)
    scr, s_diag = extracted_reasoning_label_grids(synth, extraction, scramble=True, scramble_seed=7)
    assert r_diag["decode_fidelity"] == 1.0 and l_diag["decode_fidelity"] == 1.0, (r_diag, l_diag)
    # reasoning respects monotonicity: CREATE before DESTROY
    seed_lab = reasoning["s1"]["seed"]
    assert seed_lab.index("CREATE") < seed_lab.index("DESTROY"), seed_lab
    assert seed_lab[0] == "CREATE", seed_lab  # "forms" at sentence 0

    diff = _arms_must_differ({"prior_lesion": lesion, "reasoning": reasoning})
    assert diff["pairs_differ"]["prior_lesion_vs_reasoning"], diff

    bf = _budget_fidelity(extraction, oracle, synth)
    assert 0.0 <= bf["budget_exact_match_rate"] <= 1.0, bf

    official = {k: _official_corpus_scores(synth, g) for k, g in {"prior_lesion": lesion, "reasoning": reasoning}.items()}
    assert 0.0 <= official["reasoning"]["overall"]["f1"] <= 1.0

    # verdict-logic unit checks (localization-primary, same bands as v3)
    genuine = {"split": "x", "content_delta_loc": 0.05, "content_delta_moves": 0.06,
               "retained_frac_loc_stats": {"median": 0.10}, "arms_differ": {"all_differ": True},
               "lesion_decode_diag": {"decode_fidelity": 1.0}, "reasoning_decode_diag": {"decode_fidelity": 1.0},
               "extraction_cost": {"budget_fidelity": {"budget_exact_match_rate": 0.5,
                                                       "per_class": {"MOVE": {"recall": 0.5}}}}}
    gv, _ = decomposition_verdict(genuine)
    assert gv == "HARD_PASS", gv
    vanished = dict(genuine); vanished["content_delta_loc"] = 0.005
    vv, _ = decomposition_verdict(vanished)
    assert vv == "HARD_FAIL", vv
    fragile = dict(genuine); fragile["retained_frac_loc_stats"] = {"median": 0.7}
    fv, _ = decomposition_verdict(fragile)
    assert fv == "HARD_FAIL", fv
    partial = dict(genuine); partial["retained_frac_loc_stats"] = {"median": 0.42}
    pv, _ = decomposition_verdict(partial)
    assert pv == "MIDDLE_BAND", pv

    return {"official_eval_fixtures": len(off_result["official_fixtures"]),
            "extracted_budget_seed": ex["budget"], "seed_reasoning_labels": seed_lab,
            "budget_fidelity_synth": bf["budget_exact_match_rate"],
            "arms_differ": diff["all_differ"], "decode": [r_diag["decode_fidelity"], l_diag["decode_fidelity"]],
            "verdict_logic_unit_checks": {"genuine": gv, "vanished": vv, "fragile": fv, "partial": pv}}


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
    scramble_seeds = SCRAMBLE_SEEDS_SMOKE if args.smoke else SCRAMBLE_SEEDS_FULL
    _write_start_marker(output_dir, run_mode, len(scramble_seeds))
    t0 = time.time()

    train_paragraphs = _load_split("train")
    print(f"[{run_mode}] split={split} ARM2 extracted-structure decomposition, {len(scramble_seeds)} scramble seeds...", flush=True)
    result = run_decomposition(split, train_paragraphs, scramble_seeds)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    bf = result["extraction_cost"]["budget_fidelity"]
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "content_delta_loc_EXTRACTED": result["content_delta_loc"],
            "content_delta_moves_EXTRACTED": result["content_delta_moves"],
            "retained_frac_loc_median": result["retained_frac_loc_stats"]["median"],
            "retained_frac_loc_list": result["retained_frac_loc_stats"]["list"],
            "retained_frac_loc_frac_below_0.30": result["retained_frac_loc_stats"]["frac_below_0.30"],
            "moves_f1": result["moves_f1"], "loc_official_f1": result["loc_official_f1"],
            "existence_official_f1_SEPARATE_not_in_claim": result["existence_official_f1"],
            "focus_macro_f1_SECONDARY": result["focus_macro_f1"],
            "EXTRACTION_COST_budget_exact_match": bf["budget_exact_match_rate"],
            "EXTRACTION_COST_per_class": bf["per_class"],
            "v3_oracle_reference": {"content_delta_loc": 0.027, "content_delta_moves": 0.082,
                                    "median_retained": 0.185, "note": "MEASURED@data/exp_propara_"
                                    "decisive_inference_arm1_v3_stateful_verb_v1/metrics.json"},
        },
        "cardinality_ok": len(result["per_seed_scramble"]) == len(scramble_seeds),
        "expected_n_units": len(scramble_seeds),
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: bands = v3 oracle bands, applied unchanged "
                             "(ARM2 is the extraction-cost test against v3's oracle result, not re-tuned)",
        "thresholds": {"CONTENT_DELTA_LOC_MIN_POSITIVE": CONTENT_DELTA_LOC_MIN_POSITIVE,
                       "SCRAMBLE_CLEAN_MEDIAN_HARD_PASS": SCRAMBLE_CLEAN_MEDIAN_HARD_PASS,
                       "SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL": SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL},
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
