# CELL-TEMPLATE (measurement/build-probe; NOT a queue-dispatch cell). Builds + validates a
# STATED-entity-fate EXTRACTOR (glass-box, NO LLM) -- the grow-by-reading channel the foundation
# bootstrap needs (store=hd_fact_store + fade-dynamic already exist; the prose->(entity,fate)
# STATED-fact extractor did not). This EXTRACTS what a sentence literally STATES (patient/theme of a
# fate-verb), fundamentally more tractable than the exp_propara_entity_fate_selectional_preference
# probes which tried to INFER unstated fate from distributional co-occurrence (both HARD_FAIL).
#
# WIRE-DON'T-ISLAND: reuses the exact owned frontend (hdlab.candidate_generator = pos_tagger +
# arc_parser, health-checked UAS 0.776) + hdlab.thematic_role_labeler (lemma_verb / frame_slot_role
# / is_passive_clause) + hdlab.hd_fact_store + the SimpleWiki corpus + ProPara TRAIN. NO rebuild.
#
# Load-bearing subset: no bare except / no except BaseException (SystemExit/KeyboardInterrupt
# re-raise, then Exception->crash-diagnostic->re-raise); final_metrics_atomicity=tmp_replace;
# deterministic_seeding=true (frontend fixed seeds; corpus sample uses a FIXED-seed random.Random,
# no python hash()/list(set()) ordering); self-test constructs REAL objects (real frontend + real
# HDFactStore store/recover at tiny scale) -- no synthetic-only branch; crlb_n/a (precision/recall
# over a hand-authored gold + hand-adjudicated real-corpus sample; no noise-floor threshold).
# See preregs/2026-08-11_stated_entity_fate_reading_extractor_v1.md for the full pre-reg.
"""exp_stated_entity_fate_reading_extractor_v1 -- glass-box STATED-(entity,fate) reading extractor.

PIPELINE (all owned organs, NO LLM):
  1. hdlab.candidate_generator.CandidateGenerator.generate(text) -> UD tokens + UPOS + arc parse.
  2. FATE-VERB LEXICON (hand-authored glass-box seed, missing-FACT SUPPLY): verb-lemma -> fate class
     (CONSUMED/DESTROY, PRODUCED/CREATE, MOVED). Expanded through hdlab.thematic_role_labeler.
     lemma_verb's own reductions (reused _expand_fate_lexicon) so real inflected corpus tokens match.
  3. For each token whose lemma_verb() is a fate-verb AND is functioning as a CLAUSAL verb (guarded
     against pure-noun usage 'the release of energy' by a determiner/possessive check): find its
     PATIENT/THEME by a POSITIONAL role rule that MIRRORS hdlab.situation_reader._pick_role_mentions
     (nearest-preceding nominal = subject; nearest-following = object) made voice-aware via
     is_passive_clause (passive -> surface subject is the deep PATIENT). frame_slot_role(lemma,'obj')
     confirms the slot maps to PATIENT. Emit (entity, fate, via_verb). Compound NPs expanded
     ('carbon dioxide' -> carbon_dioxide). NOTE (honest, measured this session): the owned POS tagger
     MISTAGS many present-tense process verbs as NOUN ('produces'/'release'/'carries' -> NOUN), which
     kills a pure-parse extractor on active present-tense science prose; the positional rule recovers
     these (fate-lemma in an SVO slot) without a parser rebuild -- both pure-parse and positional
     paths reported.
  4. NEGATION GUARD: if the fate is negated/absent (not/never/no/without/cannot/n't between the
     patient and the verb, or a determiner 'no'/'No' on the subject) emit NOTHING (do not hallucinate
     stated facts). This is the control the coordinator requires.
  5. STORE each tuple in hdlab.hd_fact_store.HDFactStore as
     (subject=entity, relation='fate_via_<verb>', obj=<FATE>, source='reading', trust=TRUST_LOW)
     -- lower trust than a curated seed, per the crutch-that-fades bootstrap.

VALIDATION (the whole point -- can reading yield CORRECT (entity,fate) that GENERALIZE?):
  A) CURATED gold (hand-authored, reproducible): a DESIGN set (the coordinator's own examples) + a
     HELD-OUT set (different entities/verbs, same 3 fate classes, NOT used to design the lexicon) +
     a NEGATION-CONTROL set (fate negated/absent -> must emit nothing). Reports precision + recall +
     negation-false-positive-rate on each, so held-out generalization is a direct number.
  B) REAL-CORPUS run: extract over a deterministic sample of SimpleWiki science sentences
     (combustion/photosynthesis/water-cycle/erosion/digestion topics) + ProPara TRAIN sentences;
     dump every extracted (tuple, source-sentence) to _extractions_for_handcheck.json for hand
     adjudication; store into a real HDFactStore + emit a recovery witness (n stored + a recovered
     sample). Reports n_extracted / n_stored + the sample for the hand-checked precision the verdict
     needs.

Modes: --self-test (tiny real frontend + real store/recover) ; no flag = the full validation.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import random
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

ANCHOR_NAME = "stated_entity_fate_reading_extractor_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
FRONTEND_DIR = os.path.join(OUTPUT_DIR, "frontend_cache")
POS_CACHE = os.path.join(FRONTEND_DIR, "pos_tagger.json")
ARC_CACHE = os.path.join(FRONTEND_DIR, "arc_parser.npz")
# reuse the sibling probe's already-trained frontend if present (wire-don't-island; avoids retrain)
V2_POS_CACHE = os.path.join(REPO_ROOT, "data", "exp_propara_entity_fate_selectional_preference_probe_v2",
                            "frontend_cache", "pos_tagger.json")
V2_ARC_CACHE = os.path.join(REPO_ROOT, "data", "exp_propara_entity_fate_selectional_preference_probe_v2",
                            "frontend_cache", "arc_parser.npz")
TRAIN_CONLLU_PATH = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb, frame_slot_role, is_passive_clause  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from experiments.exp_propara_entity_fate_selectional_preference_probe_v1 import (  # noqa: E402
    _inflect, _expand_fate_lexicon,
)
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import _load_split  # noqa: E402

# ============================================================================ fate-verb lexicon
# Hand-authored glass-box seed (missing-FACT SUPPLY, NO LLM). Coordinator's list + a conservative
# synonym extension (each verb ONE fate class by clear process semantics). CONSUMED=DESTROY,
# PRODUCED=CREATE, MOVED=MOVE. Expanded through lemma_verb's own reductions so inflected corpus
# tokens ('consumes'->'consum', 'produces'->'produc', 'released'->'releas') match.
_FATE_VERB_BASE: Dict[str, str] = {}
for _v in ["consume", "burn", "oxidize", "oxidise", "absorb", "digest", "dissolve", "decompose",
           "combust", "metabolize", "metabolise", "corrode", "rot"]:
    _FATE_VERB_BASE[_v] = "DESTROY"
for _v in ["produce", "release", "emit", "form", "create", "generate", "make", "secrete", "yield",
           "deposit", "synthesize", "synthesise", "excrete", "exhale"]:
    _FATE_VERB_BASE.setdefault(_v, "CREATE")
for _v in ["move", "carry", "flow", "transport", "travel", "rise", "fall", "circulate", "drain",
           "spread", "migrate", "diffuse", "pump", "convey"]:
    _FATE_VERB_BASE.setdefault(_v, "MOVE")

FATE_VERB_LEXICON: Dict[str, str] = _expand_fate_lexicon(_FATE_VERB_BASE)
FATE_LABEL = {"DESTROY": "CONSUMED", "CREATE": "PRODUCED", "MOVE": "MOVED"}

NOMINAL = {"NOUN", "PROPN", "PRON"}
_NP_POS = {"NOUN", "PROPN", "ADJ"}
_DET_POSS = {"DET", "PRON"}  # a determiner/possessive immediately before -> noun usage guard
_BE_AUX = {"is", "are", "was", "were", "be", "been", "being", "am", "'s", "'re"}
_NEG = {"not", "never", "no", "without", "cannot", "n't", "nor", "neither", "none", "nothing"}
_STOP_ENT = {"it", "he", "she", "they", "we", "you", "i", "this", "that", "these", "those", "there",
             "them", "him", "her", "us", "who", "which", "what", "one", "some", "any", "thing"}


# ============================================================================ frontend load/train
def _load_or_build_frontend() -> CandidateGenerator:
    if os.path.exists(POS_CACHE) and os.path.exists(ARC_CACHE):
        return CandidateGenerator.load(POS_CACHE, ARC_CACHE)
    if os.path.exists(V2_POS_CACHE) and os.path.exists(V2_ARC_CACHE):
        print(f"[frontend] reusing sibling v2 frontend cache (wire-don't-island)", flush=True)
        return CandidateGenerator.load(V2_POS_CACHE, V2_ARC_CACHE)
    print(f"[frontend] no cache found; training on UD_English_EWT (~3min)", flush=True)
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser, train_arc
    from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import parse_conllu
    sents = parse_conllu(TRAIN_CONLLU_PATH)
    pos_seqs = [[(t["form"], t["upos"]) for t in s["tokens"]] for s in sents]
    arc_seqs = [[(t["id"], t["form"], t["upos"], (t["head"] if t["head"] is not None else 0), t["deprel"])
                 for t in s["tokens"]] for s in sents]
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    tagger = PosTagger.train(pos_seqs, epochs=5)
    tagger.save(POS_CACHE)
    parser = ArcParser(train_arc(arc_seqs, epochs=8, seed=1027))
    parser.save(ARC_CACHE)
    return CandidateGenerator(tagger, parser)


# ============================================================================ the extractor
def _singularize(t: str) -> str:
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("ses") and len(t) > 4:
        return t[:-2]
    if t.endswith("s") and len(t) > 3 and not t.endswith("ss"):
        return t[:-1]
    return t


def _expand_np(tokens: List[str], pos: List[str], head_i: int, direction: str) -> Tuple[str, str]:
    """Expand a compound NP around the nominal at 1-based head_i. direction='back' gathers preceding
    NOUN/ADJ modifiers (English compounds are head-final: 'carbon dioxide' head=dioxide). Returns
    (phrase_joined_with_underscore, head_token_lower_singular)."""
    n = len(tokens)
    idxs = [head_i]
    j = head_i - 1
    while j >= 1 and pos[j - 1] in _NP_POS:
        idxs.insert(0, j)
        j -= 1
    # also gather a trailing compound noun if the nominal continues to the right and head_i is a
    # left modifier (e.g. nearest-following nominal 'carbon' in 'carbon dioxide')
    k = head_i + 1
    while k <= n and pos[k - 1] in {"NOUN", "PROPN"}:
        idxs.append(k)
        k += 1
    idxs = sorted(set(idxs))
    phrase = "_".join(tokens[i - 1].lower() for i in idxs)
    head_tok = tokens[idxs[-1] - 1].lower()  # head-final
    return phrase, _singularize(head_tok)


def _is_clausal_verb_use(tokens: List[str], pos: List[str], v: int) -> bool:
    """Guard against pure-noun usage of a fate-lemma ('the release of energy', 'a burn'): if the
    token is immediately preceded by a determiner/possessive AND is NOT in a 'be + X' passive frame,
    treat it as a noun, not a clausal verb."""
    if pos[v - 1] == "VERB":
        return True
    prev = tokens[v - 2].lower() if v - 2 >= 0 else ""
    prev_pos = pos[v - 2] if v - 2 >= 0 else ""
    # passive frame 'is/was <lemma>' (allowing an intervening 'not') -> clausal
    for j in (v - 1, v - 2):
        if j >= 1 and tokens[j - 1].lower() in _BE_AUX:
            return True
    if prev_pos in _DET_POSS or prev in {"the", "a", "an", "this", "that", "its", "their", "his", "her", "of"}:
        return False
    return True


def _neg_in_window(tokens: List[str], lo: int, hi: int) -> bool:
    for j in range(max(1, lo), min(len(tokens), hi) + 1):
        if tokens[j - 1].lower() in _NEG:
            return True
    return False


def extract_facts(gen: CandidateGenerator, text: str) -> List[Dict]:
    """Return list of {entity, entity_head, fate, fate_label, via_verb, voice, path, subject,
    sentence}. path='parse' when the fate-verb was tagged VERB (candidate_generator gave the
    object), 'positional' when it was mistagged NOUN and recovered positionally."""
    cr = gen.generate(text, extended=True)
    tokens, pos, heads = cr.tokens, cr.pos, cr.heads
    n = len(tokens)
    if n == 0:
        return []
    passive_sent = is_passive_clause(tokens, pos)
    out: List[Dict] = []
    seen = set()
    for v in range(1, n + 1):
        lemma = lemma_verb(tokens[v - 1])
        fate = FATE_VERB_LEXICON.get(lemma)
        if fate is None:
            continue
        if not _is_clausal_verb_use(tokens, pos, v):
            continue
        # frame confirms object-slot maps to PATIENT (true for every fate verb via DEFAULT_FRAME)
        if frame_slot_role(lemma, "obj") != "PATIENT":
            continue
        # local passive: BE-aux within [v-3, v-1]
        local_passive = any(tokens[j - 1].lower() in _BE_AUX for j in range(max(1, v - 3), v))
        voice_passive = local_passive or (passive_sent and pos[v - 1] == "VERB")

        patient_i = None
        path = None
        # (A) parse-based: verb correctly tagged VERB -> use candidate_generator candidates
        if pos[v - 1] == "VERB":
            cand_args = [(a, cr.cand_rules.get((v, a), "core_dep")) for (vv, a) in cr.candidates if vv == v]
            if voice_passive:
                pre = [a for a, r in cand_args if a < v and pos[a - 1] in NOMINAL]
                if pre:
                    patient_i = max(pre)
                    path = "parse"
            else:
                post = [a for a, r in cand_args if a > v and pos[a - 1] in NOMINAL and r != "relcl_gap"]
                gap = [a for a, r in cand_args if r == "relcl_gap"]
                if post:
                    patient_i = min(post)
                    path = "parse"
                elif gap:
                    patient_i = gap[0]
                    path = "parse"
        # (B) positional recovery: mistagged-NOUN fate-verb (or parse found no patient) -> positional
        if patient_i is None:
            noms_before = [i for i in range(1, v) if pos[i - 1] in NOMINAL]
            noms_after = [i for i in range(v + 1, n + 1) if pos[i - 1] in NOMINAL]
            if voice_passive:
                patient_i = noms_before[-1] if noms_before else None
            else:
                patient_i = noms_after[0] if noms_after else None
            if patient_i is not None:
                path = "positional"
        if patient_i is None:
            continue
        # negation guard: NEG anywhere between the patient and the verb (inclusive) or just before
        lo, hi = min(patient_i, v) - 1, max(patient_i, v)
        if _neg_in_window(tokens, lo, hi):
            continue
        # build entity phrase
        direction = "back" if patient_i < v else "back"  # head-final compound both ways
        phrase, head_tok = _expand_np(tokens, pos, patient_i, direction)
        if head_tok in _STOP_ENT or len(head_tok) < 2 or not head_tok.isalpha():
            continue
        key = (head_tok, fate, lemma)
        if key in seen:
            continue
        seen.add(key)
        subj_i = None
        noms_before = [i for i in range(1, v) if pos[i - 1] in NOMINAL and i != patient_i]
        if not voice_passive and noms_before:
            subj_i = noms_before[-1]
        out.append({
            "entity": phrase, "entity_head": head_tok, "fate": fate, "fate_label": FATE_LABEL[fate],
            "via_verb": lemma, "voice": "passive" if voice_passive else "active", "path": path,
            "subject": tokens[subj_i - 1].lower() if subj_i else None, "sentence": text.strip(),
        })
    return out


# ============================================================================ curated gold
# (sentence, [ (gold_entity_head_singular, gold_fate), ... ]). Empty list = negation/absent control.
CURATED_DESIGN = [
    ("Fire consumes the wood.", [("wood", "DESTROY")]),
    ("Combustion produces carbon dioxide.", [("dioxide", "CREATE")]),
    ("The fuel is consumed.", [("fuel", "DESTROY")]),
    ("Plants release oxygen.", [("oxygen", "CREATE")]),
    ("The river carries sediment.", [("sediment", "MOVE")]),
    ("The engine burns gasoline.", [("gasoline", "DESTROY")]),
    ("Photosynthesis produces glucose.", [("glucose", "CREATE")]),
    ("Blood transports oxygen.", [("oxygen", "MOVE")]),
]
CURATED_HELDOUT = [
    ("The stomach digests food.", [("food", "DESTROY")]),
    ("Volcanoes emit ash.", [("ash", "CREATE")]),
    ("Glaciers transport rocks.", [("rock", "MOVE")]),
    ("The leaf absorbs sunlight.", [("sunlight", "DESTROY")]),
    ("Bacteria decompose leaves.", [("leave", "DESTROY")]),  # 'leaves' -> singular 'leave' by rule
    ("Yeast produces alcohol.", [("alcohol", "CREATE")]),
    ("The wind carries seeds.", [("seed", "MOVE")]),
    ("Carbon dioxide is released by the reaction.", [("dioxide", "CREATE")]),
    ("The acid dissolves the metal.", [("metal", "DESTROY")]),
    ("Rivers deposit silt.", [("silt", "CREATE")]),
]
CURATED_NEGATION = [
    ("The wood is not consumed.", []),
    ("No oxygen is produced.", []),
    ("The fuel does not burn.", []),
    ("The plant does not release oxygen.", []),
    ("Nothing is emitted by the process.", []),
    ("The rock is dry and hard.", []),          # no fate verb at all -> must emit nothing
    ("The scientist studies combustion.", []),  # 'combustion' noun, no fate-verb clause
]


def _score_curated(gen, cases) -> Dict:
    tp = fp = fn = 0
    rows = []
    for sent, gold in cases:
        gold_set = {(_singularize(e), f) for e, f in gold}
        preds = extract_facts(gen, sent)
        pred_set = {(p["entity_head"], p["fate"]) for p in preds}
        tp += len(gold_set & pred_set)
        fp += len(pred_set - gold_set)
        fn += len(gold_set - pred_set)
        rows.append({"sentence": sent, "gold": sorted(gold_set), "pred": sorted(pred_set),
                     "correct": sorted(gold_set & pred_set), "wrong": sorted(pred_set - gold_set),
                     "missed": sorted(gold_set - pred_set)})
    prec = tp / (tp + fp) if (tp + fp) else (1.0 if fn == 0 else 0.0)
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"n_cases": len(cases), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4), "rows": rows}


def _score_negation(gen, cases) -> Dict:
    """Negation control: every case has gold=[] -> any emission is a false-positive hallucination."""
    n_fp = 0
    rows = []
    for sent, _gold in cases:
        preds = extract_facts(gen, sent)
        n_fp += len(preds)
        rows.append({"sentence": sent, "emitted": [(p["entity_head"], p["fate_label"]) for p in preds]})
    return {"n_cases": len(cases), "n_false_positive_emissions": n_fp,
            "negation_clean": n_fp == 0, "rows": rows}


# ============================================================================ real-corpus run
_SCI_TOPIC = re.compile(r"\b(combust|burn|photosynthesi|respirat|oxygen|carbon|dioxide|glucose|"
                        r"water\s+cycle|evaporat|condens|precipitat|erosion|erode|sediment|weather|"
                        r"digest|stomach|nutrient|volcano|magma|lava|nitrogen|energy|fuel|"
                        r"chlorophyll|glacier|mineral|molecule|atom|acid|solar|steam|vapor|"
                        r"decompos|bacteria|enzyme|metabol)", re.IGNORECASE)
_WORD = re.compile(r"[a-zA-Z]+")


def _sample_simplewiki(gen_lex: Dict[str, str], n_target: int, seed: int) -> List[str]:
    """Deterministic reservoir sample of SimpleWiki sentences that are science-topic AND contain a
    fate-verb-lemma token (so extraction has something to work on). FIXED-seed RNG (F.5)."""
    rng = random.Random(seed)
    reservoir: List[str] = []
    n_seen = 0
    with open(SIMPLEWIKI_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not (12 <= len(s) <= 240):
                continue
            if not _SCI_TOPIC.search(s):
                continue
            toks = set(_WORD.findall(s.lower()))
            if not any(lemma_verb(t) in gen_lex for t in toks):
                continue
            n_seen += 1
            if len(reservoir) < n_target:
                reservoir.append(s)
            else:
                j = rng.randint(0, n_seen - 1)
                if j < n_target:
                    reservoir[j] = s
    return reservoir


def _propara_train_sentences() -> List[str]:
    out: List[str] = []
    for para in _load_split("train"):
        for s in para.get("sentence_texts", []):
            s = s.strip()
            if s:
                out.append(s)
    return out


def run_validation(n_simplewiki: int = 4000, sample_dump: int = 100, seed: int = 20260811) -> Dict:
    t0 = time.time()
    gen = _load_or_build_frontend()

    # (A) curated gold
    design = _score_curated(gen, CURATED_DESIGN)
    heldout = _score_curated(gen, CURATED_HELDOUT)
    negation = _score_negation(gen, CURATED_NEGATION)
    print(f"[curated] design precision={design['precision']} recall={design['recall']} "
          f"(tp={design['tp']} fp={design['fp']} fn={design['fn']})", flush=True)
    print(f"[curated] heldout precision={heldout['precision']} recall={heldout['recall']} "
          f"(tp={heldout['tp']} fp={heldout['fp']} fn={heldout['fn']})", flush=True)
    print(f"[curated] negation clean={negation['negation_clean']} "
          f"(false_positive_emissions={negation['n_false_positive_emissions']})", flush=True)

    # (B) real corpus
    sw = _sample_simplewiki(FATE_VERB_LEXICON, n_simplewiki, seed)
    pp = _propara_train_sentences()
    print(f"[corpus] simplewiki sampled={len(sw)} propara_train_sents={len(pp)}", flush=True)

    store = HDFactStore(n_dim=8192, seed=0)
    all_extractions: List[Dict] = []
    path_counts = Counter()
    fate_counts = Counter()
    voice_counts = Counter()
    n_stored = 0
    store_res_counts = Counter()
    for src_name, sents in (("simplewiki", sw), ("propara_train", pp)):
        for s in sents:
            for fact in extract_facts(gen, s):
                fact["source_corpus"] = src_name
                all_extractions.append(fact)
                path_counts[fact["path"]] += 1
                fate_counts[fact["fate_label"]] += 1
                voice_counts[fact["voice"]] += 1
                res = store.store(subject=fact["entity"], relation=f"fate_via_{fact['via_verb']}",
                                  obj=fact["fate_label"], source="reading", trust="TRUST_LOW")
                store_res_counts[res.resolution] += 1
                n_stored += 1
    print(f"[corpus] extracted={len(all_extractions)} stored={n_stored} paths={dict(path_counts)} "
          f"fates={dict(fate_counts)} voices={dict(voice_counts)}", flush=True)

    # store-recovery witness: recover a few facts from the substrate (glass-box round-trip)
    recovery_witness = []
    for rec in store._facts[:8]:
        rc = store.recover_fact(rec.vec)
        recovery_witness.append({"stored_subject": rec.subject, "stored_relation": rec.relation,
                                 "stored_obj": rec.obj, "recovered_subject": rc["subject"],
                                 "recovered_relation": rc["relation"], "recovered_object": rc["object"],
                                 "recovered_source": rc["source"], "recovered_trust": rc["trust"]})

    # dump a deterministic sample of real-corpus extractions for HAND ADJUDICATION
    rng = random.Random(seed + 1)
    idxs = list(range(len(all_extractions)))
    rng.shuffle(idxs)
    sample = [all_extractions[i] for i in idxs[:sample_dump]]
    dump_path = os.path.join(OUTPUT_DIR, "_extractions_for_handcheck.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(dump_path, "w", encoding="utf-8") as f:
        json.dump({"n_total_extractions": len(all_extractions), "sample": sample}, f, indent=2)
    # also dump ALL extractions (compact) for full audit
    full_path = os.path.join(OUTPUT_DIR, "_extractions_all.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump([{k: fx[k] for k in ("entity", "fate_label", "via_verb", "voice", "path",
                                        "source_corpus", "sentence")} for fx in all_extractions], f, indent=2)
    print(f"[corpus] dumped {len(sample)} for hand-check -> {dump_path}; all -> {full_path}", flush=True)

    # curated precision on emitting cases only (for the reproducible headline)
    design_heldout_prec = None
    dh_tp = design["tp"] + heldout["tp"]
    dh_fp = design["fp"] + heldout["fp"]
    if (dh_tp + dh_fp) > 0:
        design_heldout_prec = round(dh_tp / (dh_tp + dh_fp), 4)

    verdict_inputs = {
        "curated_design_precision": design["precision"], "curated_design_recall": design["recall"],
        "curated_heldout_precision": heldout["precision"], "curated_heldout_recall": heldout["recall"],
        "curated_combined_precision": design_heldout_prec,
        "negation_clean": negation["negation_clean"],
        "negation_false_positive_emissions": negation["n_false_positive_emissions"],
        "n_corpus_extracted": len(all_extractions), "n_stored": n_stored,
    }
    # PRELIMINARY verdict on the REPRODUCIBLE curated numbers (hand-checked real-corpus precision is
    # adjudicated by the operator from the dumped sample and folded into the final report).
    if not negation["negation_clean"]:
        verdict = "HARD_FAIL_NEGATION_HALLUCINATION"
    elif heldout["precision"] >= 0.6 and design["precision"] >= 0.6:
        verdict = "CURATED_PASS_PENDING_HANDCHECK"
    else:
        verdict = "CURATED_FAIL_LOW_PRECISION"
    verdict_msg = (f"{verdict}: curated design P={design['precision']}/R={design['recall']}, "
                   f"HELD-OUT P={heldout['precision']}/R={heldout['recall']}, "
                   f"negation_clean={negation['negation_clean']} "
                   f"(fp_emissions={negation['n_false_positive_emissions']}); "
                   f"corpus extracted={len(all_extractions)} stored={n_stored} "
                   f"paths={dict(path_counts)}; hand-check sample dumped ({len(sample)}) -- "
                   f"final precision folded in by operator")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "run_mode": "validation",
        "anchor_name": ANCHOR_NAME,
        "fate_verb_lexicon_base_size": len(_FATE_VERB_BASE),
        "fate_verb_lexicon_expanded_size": len(FATE_VERB_LEXICON),
        "curated_design": design,
        "curated_heldout": heldout,
        "curated_negation": negation,
        "verdict_inputs": verdict_inputs,
        "corpus": {"n_simplewiki_sampled": len(sw), "n_propara_train_sents": len(pp),
                   "n_extracted": len(all_extractions), "n_stored": n_stored,
                   "path_counts": dict(path_counts), "fate_counts": dict(fate_counts),
                   "voice_counts": dict(voice_counts), "store_resolution_counts": dict(store_res_counts)},
        "store_recovery_witness": recovery_witness,
        "handcheck_dump_path": dump_path,
        "all_extractions_path": full_path,
        "bands": {"HARD_PASS_PRECISION": 0.6},
    }


# ============================================================================ metrics I/O
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
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
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}

    # (1) lexicon: coordinator's core verbs present after expansion
    for w, exp in [("consumes", "DESTROY"), ("produces", "CREATE"), ("carries", "MOVE"),
                   ("released", "CREATE"), ("burned", "DESTROY"), ("transports", "MOVE")]:
        lm = lemma_verb(w)
        assert lm in FATE_VERB_LEXICON and FATE_VERB_LEXICON[lm] == exp, f"{w}->{lm} lexicon miss ({exp})"
    out["checks"]["lexicon"] = {"base": len(_FATE_VERB_BASE), "expanded": len(FATE_VERB_LEXICON)}
    print(f"[self-test] lexicon OK ({len(_FATE_VERB_BASE)} base -> {len(FATE_VERB_LEXICON)} expanded)", flush=True)

    # (2) REAL frontend + extractor on the coordinator's canonical examples (real_code_path)
    gen = _load_or_build_frontend()
    e1 = extract_facts(gen, "Fire consumes the wood.")
    e2 = extract_facts(gen, "The fuel is consumed.")
    e3 = extract_facts(gen, "Combustion produces carbon dioxide.")
    got = {(p["entity_head"], p["fate"]) for p in e1 + e2 + e3}
    assert ("wood", "DESTROY") in got, f"missed (wood,DESTROY): {e1}"
    assert ("fuel", "DESTROY") in got, f"missed passive (fuel,DESTROY): {e2}"
    assert ("dioxide", "CREATE") in got, f"missed (carbon_dioxide,CREATE): {e3}"
    out["checks"]["extract"] = {"e1": e1, "e2": e2, "e3": e3}
    print(f"[self-test] extractor OK on canonical active/passive/compound examples", flush=True)

    # (3) negation guard: must emit NOTHING
    for s in ["The wood is not consumed.", "No oxygen is produced."]:
        assert extract_facts(gen, s) == [], f"negation hallucination on {s!r}: {extract_facts(gen, s)}"
    out["checks"]["negation"] = "clean"
    print(f"[self-test] negation guard OK (no emission on negated sentences)", flush=True)

    # (4) REAL HDFactStore store + glass-box recover round-trip
    store = HDFactStore(n_dim=8192, seed=0)
    res = store.store(subject="wood", relation="fate_via_consume", obj="CONSUMED",
                      source="reading", trust="TRUST_LOW")
    assert res.resolution in ("CLEAN_STORE", "CONSISTENT_DUP")
    rc = store.recover_fact(store._facts[0].vec)
    assert rc["subject"] == "wood" and rc["object"] == "CONSUMED" and rc["source"] == "reading", rc
    assert rc["trust"] == "TRUST_LOW", rc
    out["checks"]["store_roundtrip"] = {"stored": "wood/fate_via_consume/CONSUMED",
                                        "recovered_subject": rc["subject"], "recovered_object": rc["object"],
                                        "recovered_trust": rc["trust"]}
    print(f"[self-test] hd_fact_store store+recover OK (wood->CONSUMED, trust=TRUST_LOW)", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = ("SELFTEST_PASS: lexicon + real frontend extractor (active/passive/compound) "
                          "+ negation guard + hd_fact_store store/recover round-trip all OK")
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


# ============================================================================ main
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--n-simplewiki", type=int, default=4000)
    p.add_argument("--sample-dump", type=int, default=100)
    args = p.parse_args()

    run_mode = "self_test" if args.self_test else "validation"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)

    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run_validation(n_simplewiki=args.n_simplewiki, sample_dump=args.sample_dump)
        _write_metrics(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
