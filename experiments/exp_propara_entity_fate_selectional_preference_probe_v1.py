# CELL-TEMPLATE (measurement-probe; NOT a dispatch/pipeline cell -- runs once, locally, to
# completion, then STOP+report per the Director's spawn contract. Same lighter-weight convention
# as the sibling exp_propara_entity_fate_external_knowledge_probe_v1.py (no smoke/full escalation,
# no remote ship), still applies the load-bearing subset:
# - no bare except / no except BaseException (except SystemExit/KeyboardInterrupt: raise, then
#   except Exception -> crash-diagnostic -> re-raise); the per-line parse try/except inside the
#   corpus scan is scoped + COUNTED (not silently swallowed) and gated by an error-rate assertion
#   (META_RULE_J: record + threshold, never silent-continue-forever)
# - final_metrics_atomicity: tmp_replace (os.replace at the end)
# - deterministic_seeding: true (PosTagger.train / train_arc use FIXED integer seeds, not
#   hash()-derived; the TRAIN-gold scramble control reuses _deterministic_perm / _det_seed
#   (hashlib-seeded) verbatim from experiments.exp_propara_decisive_inference_arm1_oracle_v1,
#   F.5-compliant, no python hash() / list(set()) ordering anywhere in this file)
# - self-test constructs REAL substrate objects at N~tiny scale: trains a REAL (tiny) PosTagger +
#   ArcParser on a small slice of REAL UD_English_EWT train data, composes a REAL CandidateGenerator,
#   runs a REAL (capped) SimpleWiki scan, and does a REAL tiny gam fit/predict -- no synthetic-only
#   branch (META_RULE F.1)
# - arms_differ: majority vs selectional-real vs selectional-scramble hash-compared; hard-fails if
#   all three collapse (pipeline bug), matching the sibling probe's convention
# - crlb_n/a: pair-level P/R/F1 vs a majority baseline over a fixed real corpus (ProPara EMNLP18
#   TRAIN/DEV, SAME split as the sibling probe); no noise-floor threshold applies
# See preregs/2026-08-11_propara_entity_fate_selectional_preference_probe_v1.md for the full
# pre-reg (PASS/FAIL bands, verdict logic).
"""exp_propara_entity_fate_selectional_preference_probe_v1 -- DECISIVE BOUNDED MEASUREMENT (not a
full build): can the entity-level process-role knowledge that is the comprehension wall be learned
PURE-GLASS-BOX (NO LLM anywhere) from VERB-ARGUMENT SELECTIONAL-PREFERENCE signal in a corpus,
generalizing to UNSEEN entities?

WHY THIS IS DISTINCT from the sibling probe (exp_propara_entity_fate_external_knowledge_probe_v1,
HARD_FAIL: WordNet/ConceptNet/GloVe -- all STATIC-FACT / SIMILARITY sources -- do not generalize
to unseen-surface ProPara participants, coverage 98-99%, 0b5ca76a1) and from the two prior
selectional-preference cells found at KB-check (see completion report; both cosine>0.30, both
HARD_FAIL but for DIFFERENT target variables -- entity_typing_selectional_wsd_v1 tested verb-SENSE
disambiguation lift, read_grow_selectional_preference_precision_v2 tested SRL triple-extraction
PRECISION): this probe's target is ENTITY FATE (CREATE/MOVE/DESTROY, the SAME ProPara oracle gold
every prior fate-probe arm uses) and its held-out criterion is UNSEEN-SURFACE GENERALIZATION (the
SAME criterion + SAME TRAIN/DEV split + SAME gold multiset + SAME seen/unseen partition as the
sibling external-knowledge probe) -- neither prior selectional-preference cell tested this question.

THE SIGNAL: an entity's fate is hypothesized to be encoded by its SYNTACTIC ROLE relative to
process verbs -- "wood" appears as the object/patient of CONSUME-type verbs (burn/consume/oxidize)
-> DESTROY-class fate; "smoke/ash/CO2" appear as the object/result of PRODUCE-type verbs
(produce/release/emit/form/create) -> CREATE-class fate; things appearing as objects of MOVE-type
verbs (carry/flow/transport) -> MOVE-class fate. This is a fundamentally different signal TYPE from
the sibling probe's 3 sources (all static-fact/similarity): selectional preference is a corpus
CO-OCCURRENCE-FREQUENCY signal, the brain-faithful acquisition path (you learn "wood is fuel" from
hearing it in verb-argument contexts many times).

METHOD (bounded, design-gate; ZERO pipeline engineering beyond the feature+fit):
  1. CORPUS: Simple English Wikipedia, already obtained + cleaned on disk
     (data/corpora/simplewiki/simplewiki_clean_v1.txt, MANIFEST.md: dump 2026-07-02, CC BY-SA,
     2,779,032 sentences / 39,563,102 tokens, one-sentence-per-line). MODERN source (continuously
     updated Wikimedia dump), satisfies the modern-sources-only rule; good coverage of process/
     science topics (combustion, photosynthesis, water cycle, volcanism, digestion, ...) that
     overlaps the ProPara process-entity domain.
  2. FRONTEND (OWNED organs ONLY, NO external parser, NO nltk, NO LLM): hdlab.pos_tagger.PosTagger
     + hdlab.arc_parser.ArcParser/train_arc, TRAINED here on UD_English_EWT
     (data/corpora/ud_english_ewt/en_ewt-ud-train.conllu, already on disk, CC BY-SA 4.0) via
     hdlab.candidate_generator.CandidateGenerator (verb->nominal-argument candidate pairs from the
     unlabeled parse) + hdlab.thematic_role_labeler.frame_slot_role (hand-authored, UNTRAINED
     glass-box verb-frame table: word-order slot [pre-verbal=subj, post-verbal=obj] -> AGENT/
     PATIENT; DEFAULT_FRAME covers verbs not in the table, i.e. every fate-lexicon verb here)
     + .lemma_verb (glass-box lemmatizer). CONFIRMED (repo-wide grep, this cycle): these 3 hdlab
     organs have ZERO prior import/usage anywhere in the repo -- this is the FIRST time they are
     wired end-to-end; a REAL frontend-health check (POS tag accuracy + UAS on UD_English_EWT TEST,
     never touched by ProPara data) gates the probe before any fate-prediction claim.
  3. SEED FATE-VERB LEXICON (hand-authored, missing-FACT supply -- not an LLM; verbatim from the
     Director's spawn prompt + a small, conservative, declared synonym extension -- see
     FATE_VERB_LEXICON below): maps a verb LEMMA to one of the ProPara oracle's own 3 fate classes
     (CREATE/MOVE/DESTROY, SAME vocabulary _gold_effects_from_multiset uses -- CONSUMED-type verbs
     -> DESTROY, PRODUCED-type -> CREATE, MOVED-type -> MOVE, so this probe's numbers are directly
     comparable to the sibling probe's, not a parallel labeling scheme).
  4. SELECTIONAL-PREFERENCE INDEX (the new "feature" half of feature+fit): a TRAIN+DEV
     participant-head-VOCAB-SCOPED scan of SimpleWiki (mirrors the sibling probe's
     TRAIN+DEV-vocab-scoped ConceptNet-index precedent, same rationale -- bound compute, stay
     honest about coverage): a cheap two-condition token prefilter (line contains >=1 vocab token
     AND >=1 token whose hdlab.thematic_role_labeler.lemma_verb is in FATE_VERB_LEXICON;
     MEASURED@this-session-probe: 45,647 / 2,779,032 lines pass both conditions, ~21s full-corpus
     scan) narrows the corpus to a tractable pool; ONLY prefilter-surviving lines get a REAL
     dependency parse via the trained CandidateGenerator. For each (verb, nominal-arg) candidate
     pair where the verb lemma is in FATE_VERB_LEXICON and the argument token is in the TRAIN+DEV
     vocab: role = frame_slot_role(verb_lemma, "subj" if arg before verb else "obj") in
     {AGENT, PATIENT}; increment a per-entity-head count of (fate_class, role).
  5. FIT: reuses hdlab.learner.plugins.gam_plugin verbatim (via the sibling probe's own
     _fit_source/_predict_facts/_build_instances helpers, imported not reimplemented -- SAME
     learner the sibling probe + the original schema binder used, so a positive result here
     directly implicates SELECTIONAL-PREFERENCE SOURCING as the missing piece, not the learner).
     ONE glass-box gam instance per (para, participant, candidate effect in {CREATE, MOVE,
     DESTROY}), features = ["effect:{E}"] + ["sel:{fate}:{role}" for every (fate,role) pair any of
     the participant's head tokens was observed in] -- NO raw surface-identity feature, so any
     held-out signal is 100% corpus-co-occurrence-derived, never memorized entity strings.
  6. SPLIT: reuses the EXACT SAME TRAIN (391 paragraphs) / DEV (43 paragraphs, 175 keys, 29
     surface-unseen) split, oracle gold multiset, and seen/unseen partition as the sibling probe
     (imported verbatim: _load_split, _oracle_event_multiset, _gold_effects_from_multiset,
     _seen_surface_tokens, _is_unseen_surface) -- majority_unseen_pair_f1 is therefore the IDENTICAL
     0.3939 reference number as the sibling probe, not recomputed.

CONTROLS: (a) MAJORITY baseline -- reused verbatim (_majority_facts), same number as the sibling
probe. (b) SCRAMBLE -- deterministically (F.5-compliant) permute the TRAIN entity->fate mapping
before fitting (_scramble_gold, reused verbatim); the source's fit must NOT beat majority on
held-out-unseen after scrambling, or its "signal" is spurious/leaky, not real selectional content.
(c) FRONTEND-HEALTH gate -- POS tag accuracy + UAS on UD_English_EWT TEST (never touched by ProPara
data) must clear a conservative floor (tag_acc>=0.70, uas>=0.50; CITED@hdlab/candidate_generator.py
docstring "UAS ~0.79" as the expected ballpark) before any fate-prediction claim is trusted --
distinguishes "the hypothesis failed" from "the untested frontend was broken."

VERDICT: HARD_PASS_GENERALIZES iff (real_unseen_pair_f1 - majority_unseen_pair_f1) >=
LIFT_HARD_PASS AND scramble_unseen_pair_f1 <= majority_unseen_pair_f1 + SCRAMBLE_CLEAN_MARGIN AND
frontend_health_ok. HARD_FAIL_NO_GENERALIZATION iff lift < LIFT_HARD_FAIL (frontend healthy).
HARD_FAIL_SCRAMBLE_LEAK iff scramble not clean regardless of lift. HARD_FAIL_FRONTEND_BROKEN iff
frontend_health_ok is False (inconclusive-for-the-hypothesis, not a fate-prediction verdict). Else
MIDDLE_BAND. Same LIFT_HARD_PASS/LIFT_HARD_FAIL/SCRAMBLE_CLEAN_MARGIN THRESHOLDS as the sibling
probe (0.05 / 0.02 / 0.05) for direct comparability.

Modes: --self-test only (fast: tiny 60-sentence frontend train, capped 50,000-line SimpleWiki scan
with a tiny vocab, tiny gam fit -- all REAL code paths at reduced scale, per META_RULE F.1). No mode
flag = the REAL probe, foreground-to-completion.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

ANCHOR_NAME = "propara_entity_fate_selectional_preference_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
TRAIN_CONLLU_PATH = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
TEST_CONLLU_PATH = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser, train_arc  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb, frame_slot_role  # noqa: E402

from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import parse_conllu  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset, _det_seed, _deterministic_perm,
)
from experiments.exp_propara_schema_learned_grounded_binder_v1 import (  # noqa: E402
    _gold_effects_from_multiset, _participant_head_tokens, _seen_surface_tokens, _is_unseen_surface,
)
from experiments.exp_propara_entity_fate_external_knowledge_probe_v1 import (  # noqa: E402
    _pair_prf, _majority_facts, _scramble_gold, _hash_facts, _build_instances, _fit_source, _predict_facts,
)
from propara_trap_check import build_step_rows  # noqa: E402

EFFECTS = ("CREATE", "MOVE", "DESTROY")
_WORD = re.compile(r"[a-zA-Z]+")

# ============================================================================ pre-registered bands
# SAME thresholds as the sibling external-knowledge probe (direct comparability, not re-tuned).
LIFT_HARD_PASS = 0.05
LIFT_HARD_FAIL = 0.02
SCRAMBLE_CLEAN_MARGIN = 0.05
FRONTEND_TAG_ACC_FLOOR = 0.70   # HYPOTHESIZED@conservative-floor; typical averaged-perceptron UPOS taggers clear 0.90+
FRONTEND_UAS_FLOOR = 0.50       # CITED@hdlab/candidate_generator.py docstring: "UAS ~0.79" expected ballpark

# ============================================================================ seed fate-verb lexicon
# Verbatim from the Director's spawn prompt (consume/burn/oxidize/absorb -> CONSUMED;
# produce/release/emit/form/create -> PRODUCED; move/carry/flow/transport -> MOVED), mapped onto
# the ProPara oracle's own 3-way fate vocabulary (CREATE/MOVE/DESTROY) for direct comparability
# with every other fate-probe arm in this arc. Minimal, conservative synonym extension declared
# (not tuned post-hoc -- fixed before viewing any FULL outcome): dissolve/decay/evaporate/digest
# for the DESTROY(consumed) class (same physical/chemical-consumption semantic field as
# burn/oxidize/absorb); generate/emerge for the CREATE(produced) class (same semantic field as
# produce/form). No extension for MOVE (kept literal to the spawn prompt's own 4-verb list).
_FATE_VERB_LEXICON_BASE: Dict[str, str] = {
    "consume": "DESTROY", "burn": "DESTROY", "oxidize": "DESTROY", "oxidise": "DESTROY",
    "absorb": "DESTROY", "dissolve": "DESTROY", "decay": "DESTROY", "evaporate": "DESTROY",
    "digest": "DESTROY",
    "produce": "CREATE", "release": "CREATE", "emit": "CREATE", "form": "CREATE", "create": "CREATE",
    "generate": "CREATE", "emerge": "CREATE",
    "move": "MOVE", "carry": "MOVE", "flow": "MOVE", "transport": "MOVE",
}


def _inflect(v: str) -> List[str]:
    """Standard-English surface inflections of a bare verb lemma (regular -ed/-ing/-s morphology,
    incl. y->ied/ies and CVC-doubling), used ONLY to discover what hdlab.thematic_role_labeler.
    lemma_verb() actually maps REAL corpus inflected tokens to -- lemma_verb's own suffix-stripper
    drops the trailing 'e' on -ed/-ing inflections of silent-e verbs (e.g. lemma_verb('consumed')
    == 'consum', not 'consume' -- CAUGHT at self-test, see _expand_fate_lexicon below) rather than
    reconstructing the true infinitive. Feeding the SAME realistic inflected spelling a real corpus
    token would carry through the SAME lemma_verb() function guarantees the reduction matches,
    regardless of whether that reduction is linguistically "correct" -- self-consistency is all
    that's required here, not a perfect lemmatizer (which is out of scope; lemma_verb is a shared
    owned organ, reused verbatim/unpatched)."""
    if v.endswith("e"):
        return [v, v + "d", v[:-1] + "ing", v + "s"]
    if v.endswith("y") and len(v) > 1 and v[-2] not in "aeiou":
        return [v, v[:-1] + "ied", v + "ing", v[:-1] + "ies"]
    if len(v) >= 3 and v[-1] not in "aeiouwxy" and v[-2] in "aeiou" and v[-3] not in "aeiou":
        return [v, v + v[-1] + "ed", v + v[-1] + "ing", v + "s"]
    return [v, v + "ed", v + "ing", v + "s"]


def _expand_fate_lexicon(base: Dict[str, str]) -> Dict[str, str]:
    """Expand each bare-infinitive seed verb to every lemma_verb()-reduction its realistic surface
    inflections produce, so real corpus tokens ('consumed', 'consuming', 'oxidized', ...) match the
    lexicon even where lemma_verb's regular-suffix-stripper doesn't reconstruct the true infinitive."""
    out: Dict[str, str] = {}
    for v, cls in base.items():
        out[v] = cls
        for form in _inflect(v):
            key = lemma_verb(form)
            out.setdefault(key, cls)
    return out


FATE_VERB_LEXICON: Dict[str, str] = _expand_fate_lexicon(_FATE_VERB_LEXICON_BASE)


# ============================================================================ frontend: train hdlab organs
def _to_pos_seqs(sents: List[Dict]) -> List[List[Tuple[str, str]]]:
    return [[(t["form"], t["upos"]) for t in s["tokens"]] for s in sents]


def _to_arc_seqs(sents: List[Dict]) -> List[List[tuple]]:
    return [[(t["id"], t["form"], t["upos"], (t["head"] if t["head"] is not None else 0), t["deprel"])
             for t in s["tokens"]] for s in sents]


def _train_frontend(max_sents: Optional[int], pos_epochs: int, arc_epochs: int) -> Tuple[CandidateGenerator, PosTagger, ArcParser, int]:
    """Train hdlab.pos_tagger.PosTagger + hdlab.arc_parser.ArcParser on UD_English_EWT TRAIN
    (owned organs; CONFIRMED never previously wired end-to-end anywhere in this repo -- repo-wide
    grep, this session)."""
    sents = parse_conllu(TRAIN_CONLLU_PATH)
    if max_sents is not None:
        sents = sents[:max_sents]
    pos_seqs = _to_pos_seqs(sents)
    arc_seqs = _to_arc_seqs(sents)
    t0 = time.time()
    tagger = PosTagger.train(pos_seqs, epochs=pos_epochs)
    print(f"[frontend] pos tagger trained: n_sents={len(sents)} epochs={pos_epochs} "
          f"elapsed={time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    avg = train_arc(arc_seqs, epochs=arc_epochs, seed=1027)
    parser = ArcParser(avg)
    print(f"[frontend] arc parser trained: n_sents={len(sents)} epochs={arc_epochs} "
          f"elapsed={time.time()-t0:.1f}s", flush=True)
    gen = CandidateGenerator(tagger, parser)
    return gen, tagger, parser, len(sents)


def _frontend_health(tagger: PosTagger, parser: ArcParser, max_sents: Optional[int] = None) -> Dict:
    """Real health check on UD_English_EWT TEST (never touched by ProPara data, never touched by
    training) -- distinguishes 'the hypothesis failed' from 'the never-before-wired frontend was
    broken.'"""
    sents = parse_conllu(TEST_CONLLU_PATH)
    if max_sents is not None:
        sents = sents[:max_sents]
    pos_seqs = _to_pos_seqs(sents)
    tag_acc, n_correct, n_tok = tagger.evaluate(pos_seqs)
    arc_seqs = _to_arc_seqs(sents)
    uas, n_arc_correct, n_arcs = parser.eval_uas(arc_seqs, maxlen=50)
    ok = bool(tag_acc >= FRONTEND_TAG_ACC_FLOOR and uas >= FRONTEND_UAS_FLOOR)
    return {"tag_acc": round(float(tag_acc), 4), "uas": round(float(uas), 4),
            "n_test_sents": len(sents), "n_test_tokens": n_tok, "n_test_arcs": n_arcs,
            "frontend_health_ok": ok}


# ============================================================================ selectional-preference index build
def _build_selectional_index(gen: CandidateGenerator, vocab: Set[str], corpus_path: str,
                             max_lines: Optional[int], max_parsed_lines: Optional[int]) -> Tuple[Dict[str, Dict[str, int]], Dict]:
    """TRAIN+DEV participant-head-VOCAB-SCOPED scan of the corpus (mirrors the sibling probe's
    TRAIN+DEV-scoped ConceptNet-index precedent). Two-condition cheap token prefilter (vocab hit AND
    fate-verb-lemma hit) narrows to a tractable pool; ONLY prefilter survivors get a REAL dependency
    parse via the trained CandidateGenerator."""
    sel_counts: Dict[str, Dict[str, int]] = {}
    n_lines = 0
    n_prefilter_hit = 0
    n_parsed = 0
    n_cand_hits = 0
    n_parse_errors = 0
    last_error = None
    t0 = time.time()
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if max_lines is not None and n_lines > max_lines:
                break
            toks_lower = set(_WORD.findall(line.lower()))
            if not (toks_lower & vocab):
                continue
            if not any(lemma_verb(t) in FATE_VERB_LEXICON for t in toks_lower):
                continue
            n_prefilter_hit += 1
            if max_parsed_lines is not None and n_prefilter_hit > max_parsed_lines:
                break
            text = line.strip()
            try:
                cr = gen.generate(text, extended=True)
            except Exception as e:  # noqa: BLE001 -- per-line resilience (one pathological line must
                # not kill a multi-minute scan); COUNTED + rate-gated below, never silently
                # swallowed-forever (META_RULE_J).
                n_parse_errors += 1
                last_error = f"{type(e).__name__}: {str(e)[:200]}"
                continue
            n_parsed += 1
            for (v, a) in cr.candidates:
                if v - 1 >= len(cr.pos) or cr.pos[v - 1] != "VERB":
                    continue
                lemma = lemma_verb(cr.tokens[v - 1])
                fate = FATE_VERB_LEXICON.get(lemma)
                if fate is None:
                    continue
                arg_tok = cr.tokens[a - 1].lower()
                if arg_tok not in vocab:
                    continue
                order = "pre" if a < v else "post"
                slot = "subj" if order == "pre" else "obj"
                role = frame_slot_role(lemma, slot)
                if role not in ("AGENT", "PATIENT"):
                    continue
                key = f"{fate}:{role}"
                sel_counts.setdefault(arg_tok, {})
                sel_counts[arg_tok][key] = sel_counts[arg_tok].get(key, 0) + 1
                n_cand_hits += 1
            if n_lines % 1_000_000 == 0:
                print(f"[sel-scan] lines={n_lines} prefilter_hits={n_prefilter_hit} parsed={n_parsed} "
                      f"cand_hits={n_cand_hits} errors={n_parse_errors} elapsed={time.time()-t0:.1f}s",
                      flush=True)
    error_rate = n_parse_errors / max(n_parsed + n_parse_errors, 1)
    if error_rate > 0.10:
        raise AssertionError(f"SELECTIONAL_SCAN_ERROR_RATE_TOO_HIGH: {n_parse_errors}/{n_parsed + n_parse_errors} "
                              f"({error_rate:.1%}) parse calls raised -- frontend likely broken, not a "
                              f"legitimate per-line edge case. last_error={last_error}")
    meta = {"n_lines_scanned": n_lines, "n_prefilter_hits": n_prefilter_hit, "n_parsed": n_parsed,
            "n_parse_errors": n_parse_errors, "parse_error_rate": round(error_rate, 4),
            "n_cand_hits": n_cand_hits, "n_vocab_terms_hit": len(sel_counts),
            "elapsed_s": round(time.time() - t0, 2)}
    return sel_counts, meta


def _sel_source_feats(participant: str, sel_counts: Dict[str, Dict[str, int]]) -> List[str]:
    out: Set[str] = set()
    for t in _participant_head_tokens(participant):
        for key in sel_counts.get(t, {}):
            out.add(f"sel:{key}")
    return sorted(out)


def _coverage_stats(all_keys: Set[Tuple], sel_counts: Dict[str, Dict[str, int]]) -> Dict:
    """Per the Director's instruction: report entity-COVERAGE honestly (how many ProPara entities
    appeared with >=k verb-arg fate-contexts) -- low coverage vs no-signal are different failures."""
    n_ge1 = n_ge3 = n_ge5 = 0
    for (_pid, participant) in all_keys:
        total = sum(sel_counts.get(t, {}).get(k, 0)
                    for t in _participant_head_tokens(participant)
                    for k in sel_counts.get(t, {}))
        if total >= 1:
            n_ge1 += 1
        if total >= 3:
            n_ge3 += 1
        if total >= 5:
            n_ge5 += 1
    n = max(len(all_keys), 1)
    return {"n_keys": len(all_keys), "n_ge1_ctx": n_ge1, "n_ge3_ctx": n_ge3, "n_ge5_ctx": n_ge5,
            "frac_ge1_ctx": round(n_ge1 / n, 4), "frac_ge3_ctx": round(n_ge3 / n, 4),
            "frac_ge5_ctx": round(n_ge5 / n, 4)}


# ============================================================================ probe orchestration
def run_probe(pos_epochs: int = 6, arc_epochs: int = 10, train_max_sents: Optional[int] = None,
             health_max_sents: Optional[int] = None, scan_max_lines: Optional[int] = None,
             scan_max_parsed_lines: Optional[int] = 20_000) -> Dict:
    t0 = time.time()
    train = _load_split("train")
    dev = _load_split("dev")
    print(f"[probe] train={len(train)} paragraphs, dev={len(dev)} paragraphs", flush=True)
    train_steps = build_step_rows(train)
    dev_steps = build_step_rows(dev)
    train_gold = _gold_effects_from_multiset(_oracle_event_multiset(train_steps))
    dev_gold = _gold_effects_from_multiset(_oracle_event_multiset(dev_steps))

    seen_tokens = _seen_surface_tokens(train)
    dev_keys = set(dev_gold.keys())
    unseen_keys = {k for k in dev_keys if _is_unseen_surface(k[1], seen_tokens)}
    seen_keys = dev_keys - unseen_keys
    print(f"[probe] dev_keys={len(dev_keys)} seen={len(seen_keys)} unseen={len(unseen_keys)}", flush=True)

    train_key_order = sorted(train_gold.keys())
    scrambled_train_gold = _scramble_gold(train_gold, train_key_order)

    majority_pred = _majority_facts(train_gold, dev_keys)
    majority_scores = {
        "all": _pair_prf(dev_gold, majority_pred, dev_keys),
        "seen": _pair_prf(dev_gold, majority_pred, seen_keys),
        "unseen": _pair_prf(dev_gold, majority_pred, unseen_keys),
    }
    print(f"[probe] majority baseline: {majority_scores}", flush=True)

    gen, tagger, parser, n_frontend_train_sents = _train_frontend(train_max_sents, pos_epochs, arc_epochs)
    health = _frontend_health(tagger, parser, health_max_sents)
    print(f"[probe] frontend health: {health}", flush=True)

    vocab = _seen_surface_tokens(train) | _seen_surface_tokens(dev)
    print(f"[probe] TRAIN+DEV participant-head vocab size={len(vocab)}", flush=True)
    sel_counts, scan_meta = _build_selectional_index(gen, vocab, SIMPLEWIKI_PATH, scan_max_lines, scan_max_parsed_lines)
    print(f"[probe] selectional scan: {scan_meta}", flush=True)

    train_cov = _coverage_stats(set(train_gold.keys()), sel_counts)
    dev_cov_all = _coverage_stats(dev_keys, sel_counts)
    dev_cov_seen = _coverage_stats(seen_keys, sel_counts)
    dev_cov_unseen = _coverage_stats(unseen_keys, sel_counts)
    print(f"[probe] coverage train={train_cov} dev_all={dev_cov_all} dev_unseen={dev_cov_unseen}", flush=True)

    source_fn = lambda p: _sel_source_feats(p, sel_counts)  # noqa: E731

    train_inst_real = _build_instances(train, train_gold, source_fn)
    dev_inst = _build_instances(dev, None, source_fn)
    hyp_real, meta_real = _fit_source(train_inst_real)
    pred_real = _predict_facts(hyp_real, dev_inst)

    train_inst_scr = _build_instances(train, scrambled_train_gold, source_fn)
    hyp_scr, meta_scr = _fit_source(train_inst_scr)
    pred_scr = _predict_facts(hyp_scr, dev_inst)

    arms_hashes = {"majority": _hash_facts(majority_pred), "selectional_real": _hash_facts(pred_real),
                   "selectional_scramble": _hash_facts(pred_scr)}
    all_collapsed = arms_hashes["selectional_real"] == arms_hashes["majority"] and \
        arms_hashes["selectional_scramble"] == arms_hashes["majority"]
    if all_collapsed:
        raise AssertionError("ARMS_DID_NOT_DIFFER: both selectional arms hash-identical to majority "
                              "baseline -- pipeline bug (selectional source is doing nothing)")

    real_scores = {"all": _pair_prf(dev_gold, pred_real, dev_keys),
                   "seen": _pair_prf(dev_gold, pred_real, seen_keys),
                   "unseen": _pair_prf(dev_gold, pred_real, unseen_keys)}
    scr_scores = {"all": _pair_prf(dev_gold, pred_scr, dev_keys),
                  "seen": _pair_prf(dev_gold, pred_scr, seen_keys),
                  "unseen": _pair_prf(dev_gold, pred_scr, unseen_keys)}

    maj_unseen_f1 = majority_scores["unseen"]["pair_f1"]
    real_unseen_f1 = real_scores["unseen"]["pair_f1"]
    scr_unseen_f1 = scr_scores["unseen"]["pair_f1"]
    lift = round(real_unseen_f1 - maj_unseen_f1, 4)
    scramble_clean = scr_unseen_f1 <= maj_unseen_f1 + SCRAMBLE_CLEAN_MARGIN

    if not health["frontend_health_ok"]:
        verdict = "HARD_FAIL_FRONTEND_BROKEN"
        verdict_msg = (f"HARD_FAIL_FRONTEND_BROKEN: tag_acc={health['tag_acc']} uas={health['uas']} "
                       f"below floors (tag_acc>={FRONTEND_TAG_ACC_FLOOR}, uas>={FRONTEND_UAS_FLOOR}) -- "
                       f"inconclusive for the selectional-preference hypothesis, the never-before-wired "
                       f"frontend itself is broken, not the mechanism")
    elif lift >= LIFT_HARD_PASS and scramble_clean:
        verdict = "HARD_PASS_GENERALIZES"
        verdict_msg = (f"HARD_PASS_GENERALIZES: lift_unseen={lift} >= {LIFT_HARD_PASS}, scramble_clean=True -- "
                       f"pure-glass-box selectional-preference acquisition WORKS, generalizes to unseen entities")
    elif not scramble_clean:
        verdict = "HARD_FAIL_SCRAMBLE_LEAK"
        verdict_msg = (f"HARD_FAIL_SCRAMBLE_LEAK: scramble_unseen_f1={scr_unseen_f1} > majority+{SCRAMBLE_CLEAN_MARGIN} "
                       f"-- apparent signal is spurious/leaky, not real selectional content")
    elif lift < LIFT_HARD_FAIL:
        verdict = "HARD_FAIL_NO_GENERALIZATION"
        verdict_msg = (f"HARD_FAIL_NO_GENERALIZATION: lift_unseen={lift} < {LIFT_HARD_FAIL} -- selectional-preference "
                       f"signal does NOT generalize to unseen-surface entities above majority; pure-glass-box "
                       f"distributional acquisition of entity-fate is closed at this corpus/regime")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = f"MIDDLE_BAND: lift_unseen={lift} between {LIFT_HARD_FAIL} and {LIFT_HARD_PASS}"

    elapsed = time.time() - t0
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(elapsed, 2),
        "run_mode": "probe",
        "anchor_name": ANCHOR_NAME,
        "n_train_paragraphs": len(train),
        "n_dev_paragraphs": len(dev),
        "n_dev_keys": len(dev_keys),
        "n_unseen_keys": len(unseen_keys),
        "n_seen_keys": len(seen_keys),
        "n_frontend_train_sents": n_frontend_train_sents,
        "frontend_health": health,
        "vocab_size_train_dev": len(vocab),
        "scan_meta": scan_meta,
        "coverage": {"train": train_cov, "dev_all": dev_cov_all, "dev_seen": dev_cov_seen, "dev_unseen": dev_cov_unseen},
        "majority_baseline": majority_scores,
        "fit_meta_real": meta_real,
        "fit_meta_scramble": meta_scr,
        "results": {"real": real_scores, "scramble": scr_scores},
        "lift_unseen_vs_majority": lift,
        "scramble_clean": scramble_clean,
        "arms_hashes": arms_hashes,
        "arms_differ_verified": not all_collapsed,
        "fate_verb_lexicon": FATE_VERB_LEXICON,
        "bands": {"LIFT_HARD_PASS": LIFT_HARD_PASS, "LIFT_HARD_FAIL": LIFT_HARD_FAIL,
                  "SCRAMBLE_CLEAN_MARGIN": SCRAMBLE_CLEAN_MARGIN,
                  "FRONTEND_TAG_ACC_FLOOR": FRONTEND_TAG_ACC_FLOOR, "FRONTEND_UAS_FLOOR": FRONTEND_UAS_FLOOR},
    }


# ============================================================================ metrics I/O
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}

    # (1) hand-constructed synthetic-parse correctness check of the FATE/ROLE extraction LOGIC
    # itself (independent of tagger/parser accuracy -- deterministic, always correct if the logic
    # is right): "The fire consumed the wood ." tokens 1-6, verb idx3="consumed", nominal idx5="wood"
    # is its direct object (heads[5]=3), so candidates_from_parse core_dep should fire (5,3)->core_dep
    # style pair (3,5), and frame_slot_role(lemma_verb('consumed'), 'obj') must be PATIENT, and
    # 'consumed'->DESTROY via FATE_VERB_LEXICON.
    from hdlab.candidate_generator import candidates_from_parse
    toks = ["The", "fire", "consumed", "the", "wood", "."]
    pos = ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"]
    heads = {1: 2, 2: 3, 3: 0, 4: 5, 5: 3, 6: 3}  # 1-based; wood(5) is obj of consumed(3)
    cands, rules = candidates_from_parse(toks, pos, heads, extended=True)
    assert (3, 5) in cands, f"expected (verb=3,arg=5) candidate pair from core_dep, got {cands}"
    lemma = lemma_verb(toks[2])
    assert lemma in FATE_VERB_LEXICON, f"lemma_verb('consumed')={lemma!r} not in expanded FATE_VERB_LEXICON"
    assert FATE_VERB_LEXICON[lemma] == "DESTROY", f"lemma {lemma!r} -> {FATE_VERB_LEXICON[lemma]!r}, expected DESTROY"
    role = frame_slot_role(lemma, "obj")
    assert role == "PATIENT", f"expected PATIENT role for object slot of 'consume', got {role}"
    out["checks"]["fate_role_logic"] = {"pair": [3, 5], "lemma": lemma, "fate": "DESTROY", "role": role}
    print(f"[self-test] fate/role extraction logic OK: {out['checks']['fate_role_logic']}", flush=True)

    # (2) REAL (tiny-scale) frontend training -- constructs the ACTUAL PosTagger/ArcParser/
    # CandidateGenerator objects the FULL run uses, on a small REAL slice of UD_English_EWT
    # (real_code_path, not synthetic-only).
    gen, tagger, parser, n_train_sents = _train_frontend(max_sents=60, pos_epochs=3, arc_epochs=3)
    assert n_train_sents > 0
    cr = gen.generate("The fire consumed the wood.", extended=True)
    assert cr.tokens and cr.pos and isinstance(cr.candidates, set)
    out["checks"]["real_frontend"] = {"n_train_sents": n_train_sents, "n_tokens": len(cr.tokens),
                                      "n_candidates": len(cr.candidates)}
    print(f"[self-test] real (tiny) frontend trained + composed OK: {out['checks']['real_frontend']}", flush=True)

    # (3) REAL frontend health check on a tiny REAL UD TEST slice (structure only at this scale,
    # not a strict accuracy floor -- the floor gate applies to the FULL probe's full-scale frontend).
    health = _frontend_health(tagger, parser, max_sents=20)
    assert 0.0 <= health["tag_acc"] <= 1.0 and 0.0 <= health["uas"] <= 1.0
    out["checks"]["health_tiny"] = health
    print(f"[self-test] tiny-scale health check ran OK: {health}", flush=True)

    # (4) REAL (capped) SimpleWiki scan -- proves the REAL scanning code path runs on REAL corpus
    # data at reduced scale (max_lines cap), not a mocked corpus.
    tiny_vocab = {"wood", "ash", "water", "gas"}
    sel_counts, scan_meta = _build_selectional_index(gen, tiny_vocab, SIMPLEWIKI_PATH,
                                                       max_lines=50_000, max_parsed_lines=50)
    assert scan_meta["n_lines_scanned"] <= 50_001
    out["checks"]["sel_scan_capped"] = scan_meta
    print(f"[self-test] capped real SimpleWiki scan OK: {scan_meta}", flush=True)

    # (5) REAL gam fit/predict at tiny scale (N~12 paragraphs), REAL substrate loaders + REAL
    # selectional source_fn (built from the tiny capped scan above -- may be sparse/empty, that's
    # fine, this checks the CODE PATH runs, not that it has signal at this reduced scale).
    train = _load_split("train")[:8]
    dev = _load_split("dev")[:4]
    train_steps = build_step_rows(train)
    dev_steps = build_step_rows(dev)
    train_gold = _gold_effects_from_multiset(_oracle_event_multiset(train_steps))
    dev_gold = _gold_effects_from_multiset(_oracle_event_multiset(dev_steps))
    source_fn = lambda p: _sel_source_feats(p, sel_counts)  # noqa: E731
    train_inst = _build_instances(train, train_gold, source_fn)
    dev_inst = _build_instances(dev, None, source_fn)
    assert train_inst and dev_inst, "REAL_CODE_PATH_EMPTY: tiny-scale instance construction produced nothing"
    hyp, meta = _fit_source(train_inst)
    pred = _predict_facts(hyp, dev_inst)
    assert isinstance(pred, dict)
    out["checks"]["gam_real_code_path"] = {"n_train_inst": len(train_inst), "n_dev_inst": len(dev_inst),
                                           "fit_meta": meta, "n_pred_keys": len(pred)}
    print(f"[self-test] gam tiny-scale fit/predict OK: {meta}", flush=True)

    # (6) coverage-stats + arms-hash + scramble-determinism sanity
    dev_keys = set(dev_gold.keys())
    majority_pred = _majority_facts(train_gold, dev_keys)
    h_maj = _hash_facts(majority_pred)
    h_sel = _hash_facts(pred)
    cov = _coverage_stats(dev_keys, sel_counts)
    out["checks"]["coverage_tiny"] = cov
    key_order = sorted(train_gold.keys())
    scr1 = _scramble_gold(train_gold, key_order)
    scr2 = _scramble_gold(train_gold, key_order)
    assert scr1 == {k: v for k, v in scr2.items()}, "SCRAMBLE_NONDETERMINISTIC"
    out["checks"]["scramble_deterministic"] = True
    out["checks"]["arms_hashes_present"] = {"majority": h_maj, "selectional": h_sel}
    print(f"[self-test] coverage={cov} scramble-determinism OK", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = ("SELFTEST_PASS: fate/role logic + real tiny frontend train/compose + "
                          "tiny health check + capped real SimpleWiki scan + real tiny gam "
                          "fit/predict + coverage-stats + scramble-determinism all OK")
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


# ============================================================================ main
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--pos-epochs", type=int, default=6)
    p.add_argument("--arc-epochs", type=int, default=10)
    p.add_argument("--train-max-sents", type=int, default=None)
    p.add_argument("--health-max-sents", type=int, default=None)
    p.add_argument("--scan-max-lines", type=int, default=None)
    p.add_argument("--scan-max-parsed-lines", type=int, default=20_000)
    args = p.parse_args()

    run_mode = "self_test" if args.self_test else "probe"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)

    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run_probe(pos_epochs=args.pos_epochs, arc_epochs=args.arc_epochs,
                                train_max_sents=args.train_max_sents, health_max_sents=args.health_max_sents,
                                scan_max_lines=args.scan_max_lines, scan_max_parsed_lines=args.scan_max_parsed_lines)
        _write_metrics(out_dir, metrics)
        print(f"[main] wrote metrics to {os.path.join(out_dir, 'metrics.json')} "
              f"verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
