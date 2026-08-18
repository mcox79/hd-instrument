#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout

FULL verb-affectedness gate = VerbNet lexicon (breadth + per-sense + graded proto-patient score)
COMBINED with the v1 hand-lexicon (copula/stative/light verbs VerbNet OMITS) -> applied to the reader's
who-is-affected on a HELD-OUT McGuffey slice (lessons XIV-XXII, N=38, Director-labeled, DISTINCT from
the v1 N=34 gold). This is the HONEST magnitude test: the v1 0.912 was co-defined (single-annotator,
gold shares the gate's own definition) per VET ad793d3a; this held-out gold was labeled independently
and DELIBERATELY packs the WORD-SENSE test cases the lemma-level gate is predicted to miss.

PRIOR ART CREDITED (adopted + built-on, NOT invented):
  - VerbNet (Kipper-Schuler 2005) via nltk.corpus.verbnet -> data/verbnet_affectedness_lexicon_v1
    (3621 verbs, 429 classes; per-verb affectedness_type + graded_score + per_sense[...]).
  - Levin (1993) verb classes; Dowty (1991) proto-patient; Beavers (2011) affectedness hierarchy.
  - The v1 hand-lexicon (exp_mcguffey_whoaffected_verb_affectedness_gate_v1) = copula/stative/light +
    phrasal overrides that VerbNet OMITS (have/is/are/be/own/do/let; get-up/look-at).
  Prior-work KB check (substrate_query): NONE at cosine>0.30 (only WordNet lexical hits for the word
  'affectedness'); this cell is a genuine EXTENSION (held-out eval + VerbNet integration), not a
  rediscovery.

THREE BACKENDS (arm-2 lexicon comparison, one-variable per arm = the gate source):
  - HAND    : v1 affectedness_class (surface-keyed) + phrasal overrides + negation.
  - VERBNET : lemmatize -> VerbNet graded_score < 0.35 => force NONE (0.35 = the builder's own
              spot-check threshold, 94.4% decision accuracy); OOV => KEEP (no decision).
  - COMBINED: negation -> hand phrasal override -> hand copula/stative/light (VerbNet omits) => NONE
              authoritative -> VerbNet graded threshold (primary) -> hand fallback on VerbNet-OOV.
  DEFAULT is KEEP everywhere (gate only FIRES on verbs KNOWN non-affecting -> cannot destroy accuracy
  where the reader is already right).

NEGATION (crudeness fix, task-requested): clause-aware, multi-clause-safe. A verb is negated iff a
  negation marker sits in the SAME clause segment (segments split at commas + coordinating conjunctions
  but/and/or/nor/;) -- glass-box, parse-independent. Reported ALONGSIDE the v1 crude any-marker-in-
  sentence rule so the improvement is measurable (e.g. h05 'must not touch..., but may look at it':
  clause-aware negates touch, NOT look).

MEASURE (design-gate, can-fail, real baseline = raw reader on held-out):
  1. HELD-OUT accuracy: RAW reader (gate off) vs COMBINED gate, overall + per-type. HONEST magnitude.
  2. LEXICON comparison: HAND-only vs VERBNET-only vs COMBINED accuracy + coverage (which covers the
     held-out verbs; does VerbNet per-sense/graded help the WORD-SENSE cases a lemma gate gets wrong?).
  3. WORD-SENSE residual: per sense-test case (h08 leave=deposit, h14 hunt=pursuit, h15 lose=change-of-
     possession, h17/h20 meet=encounter) report the gate decision vs gold + whether VerbNet PER-SENSE
     data COULD have rescued (a correct per_sense decision exists though the modal lemma decision is
     wrong) -> confirms whether WORD-SENSE-DISAMBIGUATION is the next gap.
  + SECONDARY over-fire COST guard: UD-EWT who-affected no-regression for the COMBINED gate (UD gold is
    STRUCTURAL -> every obj=patient -> the semantic gate can only COST here, never help).

CAN-FAIL: (a) gate does NOT generalize (combined <= raw + 0.05 on held-out -> v1 magnitude was
  co-defined/overfit); OR (b) word-sense cases fail (< half pass -> sense-blind = confirmed next lever);
  OR (c) VerbNet+hand disagree/conflict on decisions (reported).

HONEST BANDS: N=38 SMALL (illustrative; single-annotator held-out). Raw reader expected LOW on gold-NONE
  types (transitive copula/have/perception all extract a spurious object). Combined expected to LIFT
  clearly over raw but BELOW the v1 co-defined 0.912 (the held-out packs hard sense cases on purpose ->
  a lower honest number is the EXPECTED, correct outcome, not a failure). GENERALIZES = combined > raw
  + 0.05. LEAK-CLEAN: gate = verb surface/lemma type-fact, gold-independent; REAL mutation-probe in
  self_test permutes the gold type/affected labels + re-derives -> gate decisions byte-identical.

Compute architecture: sequential-CPU, justified (pure-python glass-box pass over 38 McGuffey gold + a
  UD-EWT subset; persisted averaged-perceptron POS + hashed arc-parser/labeler; numpy only; wall
  seconds; no matmul-heavy inner loop -> not a GPU-batching candidate). Storage: no_storage/
  no_composition (measurement cell; atomic tmp+replace metrics.json). Determinism: OMP/MKL/OPENBLAS=1;
  sorted(set); fixed 0.35 threshold; no hash()-seeded RNG. LOCAL-only foreground; NO queue, NO push, NO
  remote-persist, NO git add, NO production hdlab mutation (gate composed in-cell). ASCII-only, no em-dashes.

# CELL-TEMPLATE MANDATORY (measurement cell; single-shot, no seed/sweep axis):
# - arms_differ_verified at smoke gate (raw/hand/verbnet/combined decision vectors not all identical)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor (accuracy on labeled gold, not a capacity/argmax-noise cell)
# - baseline_in_band: raw reader on held-out expected 0.05 < acc < 0.95 (verified at smoke)
# - discriminator survives scale: full IS the scale (N=38 held-out fixed; not a smoke-vs-full-N issue)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - cardinality_ok: n/a (no sweep axis; single held-out pass)
# - calibration_check: default_ok_for_this_regime (0.35 threshold = builder spot-check 94.4% dec acc)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

ANCHOR_NAME = "mcguffey_whoaffected_verb_affectedness_gate_v2_heldout"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the validated reader/overlay wiring + UD who-affected eval (read-only import; NO mutation)
from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, UD_TEST,
    reader_pass, base_pick, load_ud_docs, gold_instances,
)
# reuse the v1 hand-lexicon (surface-keyed affectedness classes + phrasal overrides)
from experiments.exp_mcguffey_whoaffected_verb_affectedness_gate_v1 import (  # noqa: E402
    affectedness_class, NONE_CLASSES, PHRASAL_CLASS, span_head_tokens, find_verb_index,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402

GOLD_PATH = os.path.join(REPO_ROOT, "data", "mcguffey_whoaffected_oracle_gold_v2_heldout", "gold.json")
VERBNET_PATH = os.path.join(REPO_ROOT, "data", "verbnet_affectedness_lexicon_v1", "lexicon.json")

AFFECTED_TYPES = {"patient", "effected", "transfer"}
NONE_TYPES = {"target_not_affected", "none", "negated"}
NEG_MARKERS = {"not", "n't", "never", "no", "none", "cannot", "nor"}
CLAUSE_BREAKS = {",", ";", ":", "but", "and", "or", "nor", "yet", "so", "for"}

VN_GRADED_THRESHOLD = 0.35  # CITED@data/verbnet_affectedness_lexicon_v1 builder spot-check (94.4% dec acc)

# word-sense test cases (the strategic probe: does the full gate handle these or persist sense-blind?)
SENSE_CASE_IDS = {"h08", "h14", "h15", "h17", "h20"}

# --- load VerbNet lexicon (lemma-keyed) ---
with open(VERBNET_PATH, encoding="utf-8") as _f:
    _VN_DOC = json.load(_f)
VN_LEX = _VN_DOC["lexicon"]

# =====================================================================================================
# Glass-box lemmatizer (VerbNet is lemma-keyed; McGuffey text has surface forms). Irregular map + a
# lookup-guided regular stripper (generate candidates, return the first present in VerbNet). Transparent
# and self-contained (no external lemmatizer dependency).
# =====================================================================================================
IRREGULAR = {
    "fed": "feed", "left": "leave", "lost": "lose", "met": "meet", "has": "have", "had": "have",
    "is": "be", "am": "be", "are": "be", "was": "be", "were": "be", "been": "be", "being": "be",
    "gave": "give", "given": "give", "went": "go", "gone": "go", "came": "come", "ran": "run",
    "saw": "see", "seen": "see", "felt": "feel", "heard": "hear", "held": "hold", "sang": "sing",
    "sung": "sing", "caught": "catch", "thought": "think", "got": "get", "gotten": "get",
    "made": "make", "took": "take", "brought": "bring", "bought": "buy", "sold": "sell",
    "sent": "send", "told": "tell", "threw": "throw", "drew": "draw", "wrote": "write",
    "written": "write", "knew": "know", "known": "know", "grew": "grow", "flew": "fly",
    "fell": "fall", "fallen": "fall", "rose": "rise", "risen": "rise", "sat": "sit", "stood": "stand",
    "slept": "sleep", "swam": "swim", "swum": "swim", "ate": "eat", "eaten": "eat", "drank": "drink",
    "does": "do", "did": "do", "done": "do", "lets": "let",
}


def lemmatize(surface):
    """Surface -> base lemma. Irregular map first, then a VerbNet-lookup-guided regular stripper.
    Returns the best guess (present in VerbNet if found; else the plain morphological guess)."""
    s = (surface or "").lower().strip()
    if s in IRREGULAR:
        return IRREGULAR[s]
    if s in VN_LEX:
        return s
    cands = []
    if s.endswith("ies"):
        cands.append(s[:-3] + "y")
    if s.endswith("es"):
        cands.append(s[:-2])
    if s.endswith("s") and not s.endswith("ss"):
        cands.append(s[:-1])
    if s.endswith("ing"):
        cands += [s[:-3], s[:-3] + "e"]
    if s.endswith("ed"):
        cands += [s[:-2], s[:-1]]
    if len(s) > 3 and s[-1] == s[-2] and s.endswith(("ed", "ing")):
        stem = s.rstrip("ed").rstrip("ing")
        cands.append(stem[:-1] if len(stem) > 1 else stem)
    for c in cands:
        if c in VN_LEX:
            return c
    return cands[0] if cands else s


# =====================================================================================================
# Clause-aware negation (multi-clause fix). Split token stream into clause segments at commas + coord
# conjunctions; a verb is negated iff a negation marker is in the SAME segment. Glass-box, parse-free.
# =====================================================================================================
def clause_segments(tokens):
    """Return list of (start1based, end1based_inclusive) segment ranges split on clause-break tokens."""
    segs = []
    start = 1
    for i in range(1, len(tokens) + 1):
        low = tokens[i - 1].lower().strip(".,'\"!?;:")
        raw = tokens[i - 1]
        if raw in {",", ";", ":"} or low in {"but", "and", "or", "nor", "yet", "so"}:
            if i - 1 >= start:
                segs.append((start, i - 1))
            start = i + 1
    if start <= len(tokens):
        segs.append((start, len(tokens)))
    return segs if segs else [(1, len(tokens))]


def verb_is_negated_clauseaware(tokens, vidx):
    """True iff a negation marker sits in the same clause segment as the verb at 1-based vidx."""
    if vidx is None:
        return sentence_is_negated_crude(tokens)
    for (a, b) in clause_segments(tokens):
        if a <= vidx <= b:
            for j in range(a, b + 1):
                tok = tokens[j - 1].lower().strip(".,'\"!?;:")
                if tok in NEG_MARKERS:
                    return True
            return False
    return sentence_is_negated_crude(tokens)


def sentence_is_negated_crude(tokens):
    """v1 crude rule: ANY negation marker anywhere in the sentence (reported for comparison)."""
    lows = {t.lower().strip(".,'\"!?;:") for t in tokens}
    return bool(lows & NEG_MARKERS)


# =====================================================================================================
# The three gate backends. Each returns True => force NONE (nobody affected). DEFAULT is KEEP (False).
# =====================================================================================================
def hand_forces_none(verb_surface):
    """v1 hand-lexicon: surface/phrasal affectedness class in a NONE class."""
    key = (verb_surface or "").lower().strip()
    if key in PHRASAL_CLASS:
        return PHRASAL_CLASS[key] in NONE_CLASSES
    return affectedness_class(key) in NONE_CLASSES


def verbnet_forces_none(verb_surface):
    """VerbNet graded_score < threshold => force NONE. Returns (decision_bool, covered_bool, info).
    covered=False when the lemma is OOV (verbnet-only then defaults to KEEP)."""
    head = (verb_surface or "").lower().strip().split()[0] if verb_surface else ""
    lem = lemmatize(head)
    entry = VN_LEX.get(lem)
    if entry is None:
        return False, False, {"lemma": lem, "vn_type": "OOV", "graded": None}
    g = float(entry.get("graded_score", 0.5))
    return (g < VN_GRADED_THRESHOLD), True, {"lemma": lem, "vn_type": entry.get("affectedness_type"),
                                             "graded": g, "sense_ambiguous": entry.get("sense_ambiguous")}


HAND_STATIVE_LIGHT = {  # copula/stative/light verbs VerbNet OMITS (have/is/are/be/own/do/let/...)
    "be", "have", "own", "possess", "belong", "contain", "cost", "weigh", "seem", "appear",
    "remain", "exist", "lack", "comprise", "equal", "resemble", "consist", "do", "let",
}


def combined_forces_none(verb_surface):
    """COMBINED gate: hand phrasal override -> hand copula/stative/light (VerbNet omits) => NONE
    authoritative -> VerbNet graded threshold (primary) -> hand fallback on VerbNet-OOV.
    (Negation is composed by the caller.) Returns (decision_bool, source_str, info)."""
    key = (verb_surface or "").lower().strip()
    head = key.split()[0] if key else ""
    if key in PHRASAL_CLASS:
        return (PHRASAL_CLASS[key] in NONE_CLASSES), "hand_phrasal", {"phrasal": key}
    lem = lemmatize(head)
    if lem in HAND_STATIVE_LIGHT or affectedness_class(head) == "possession_stative":
        return True, "hand_stative_light", {"lemma": lem}
    dec, covered, info = verbnet_forces_none(head)
    if covered:
        info["source"] = "verbnet"
        return dec, "verbnet", info
    # VerbNet OOV -> full hand fallback
    return (affectedness_class(head) in NONE_CLASSES), "hand_fallback", {"lemma": lem}


def verbnet_per_sense_decisions(verb_surface):
    """For the WORD-SENSE probe: list of per-sense (vn_class, type, graded, forces_none) for this lemma.
    A case is 'rescuable by sense' if a CORRECT per-sense decision exists though the modal is wrong."""
    head = (verb_surface or "").lower().strip().split()[0] if verb_surface else ""
    lem = lemmatize(head)
    entry = VN_LEX.get(lem)
    if entry is None:
        return []
    out = []
    for ps in entry.get("per_sense", []):
        g = float(ps.get("graded_score", 0.5))
        out.append({"vn_class": ps.get("vn_class"), "vn_type": ps.get("affectedness_type"),
                    "graded": g, "forces_none": (g < VN_GRADED_THRESHOLD)})
    return out


# =====================================================================================================
def eval_mcguffey(gold, tagger, parser, labeler):
    """Reader on held-out McGuffey; RAW + hand/verbnet/combined gate correctness (+ neg variants)."""
    inst = []
    for g in gold:
        text, gverb, gaff, gtype = g["text"], g["verb"], g["affected"], g["type"]
        gold_none = gtype in NONE_TYPES
        heads_gold = span_head_tokens(gaff)

        tokens = ud_tokenize(text)
        rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
        pos = rp["pos"]
        vidx, pos_missed = find_verb_index(tokens, pos, gverb)
        pool = rp["pools"].get(vidx, []) if vidx is not None else []
        bp = base_pick(pool)
        pred_surf = bp["surf"] if bp is not None else None
        pred_none = bp is None

        neg_clause = verb_is_negated_clauseaware(tokens, vidx)
        neg_crude = sentence_is_negated_crude(tokens)

        hand_none = hand_forces_none(gverb)
        vn_dec, vn_cov, vn_info = verbnet_forces_none(gverb)
        comb_dec, comb_src, comb_info = combined_forces_none(gverb)

        # negation composes into each gate (clause-aware for the mechanism arms)
        hand_full = hand_none or neg_clause
        vn_full = vn_dec or neg_clause
        comb_full = comb_dec or neg_clause
        comb_crudeneg = comb_dec or neg_crude

        def correct(force_none):
            pred_is_none = pred_none or force_none
            if gold_none:
                return pred_is_none
            return bool((not force_none) and pred_surf is not None and pred_surf in heads_gold)

        raw_correct = correct(False)
        hand_correct = correct(hand_full)
        vn_correct = correct(vn_full)
        comb_correct = correct(comb_full)
        comb_crudeneg_correct = correct(comb_crudeneg)

        row = {
            "id": g["id"], "text": text, "verb": gverb, "type": gtype, "gold_affected": gaff,
            "gold_none": gold_none, "pred_surf": pred_surf, "pred_none": pred_none,
            "vn_lemma": vn_info.get("lemma"), "vn_type": vn_info.get("vn_type"),
            "vn_graded": vn_info.get("graded"), "vn_covered": vn_cov, "comb_source": comb_src,
            "neg_clause": neg_clause, "neg_crude": neg_crude, "pos_missed": pos_missed,
            "hand_none": hand_none, "vn_none": vn_dec, "comb_none": comb_dec,
            "raw_correct": raw_correct, "hand_correct": hand_correct,
            "vn_correct": vn_correct, "comb_correct": comb_correct,
            "comb_crudeneg_correct": comb_crudeneg_correct,
        }
        if g["id"] in SENSE_CASE_IDS:
            row["per_sense"] = verbnet_per_sense_decisions(gverb)
        inst.append(row)
    return inst


def eval_ud_noregression(docs, tagger, parser, labeler):
    """UD-EWT who-affected no-regression for the COMBINED gate (structural gold -> pure over-fire cost)."""
    rows = []
    for doc in docs:
        for sent in doc:
            rp = reader_pass(sent, tagger, parser, labeler)
            tokens, lemmas = sent["tokens"], sent["lemmas"]
            for gi in gold_instances(sent):
                v, gp = gi["vidx"], gi["gold_pidx"]
                pool = rp["pools"].get(v, [])
                bp = base_pick(pool)
                base_aidx = bp["aidx"] if bp is not None else None
                lemma = lemmas[v - 1] if 1 <= v <= len(lemmas) else tokens[v - 1].lower()
                comb_dec, _, _ = combined_forces_none(lemma)
                neg = verb_is_negated_clauseaware(tokens, v)
                comb_full = comb_dec or neg
                base_correct = bool(base_aidx is not None and base_aidx == gp)
                comb_correct = bool((not comb_full) and base_correct)
                rows.append({"base_correct": base_correct, "comb_correct": comb_correct,
                             "fired": comb_full})
    return rows


# ---------------------------------------------------------------------------------------------------
def run(mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    _tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(_tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(_tmp, os.path.join(out_dir, "_start_marker.json"))
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_doc = json.load(f)
    gold = gold_doc["gold"]
    if mode == "smoke":
        gold = gold[:14]

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded; held-out McGuffey N={len(gold)}", flush=True)

    minst = eval_mcguffey(gold, tagger, parser, labeler)
    n_m = len(minst)

    def acc(items, key):
        c = sum(1 for i in items if i[key])
        return (round(c / len(items), 4) if items else None), len(items), c

    m_raw = acc(minst, "raw_correct")
    m_hand = acc(minst, "hand_correct")
    m_vn = acc(minst, "vn_correct")
    m_comb = acc(minst, "comb_correct")
    m_comb_crudeneg = acc(minst, "comb_crudeneg_correct")

    # per-type (raw vs combined)
    m_per_type = {}
    for ty in sorted({i["type"] for i in minst}):
        items = [i for i in minst if i["type"] == ty]
        m_per_type[ty] = {
            "n": len(items),
            "raw_acc": acc(items, "raw_correct")[0], "raw_correct": acc(items, "raw_correct")[2],
            "comb_acc": acc(items, "comb_correct")[0], "comb_correct": acc(items, "comb_correct")[2],
        }

    # coverage per backend (does the backend supply a NON-default decision for this verb?)
    hand_cov = sum(1 for i in minst
                   if (i["verb"].lower() in PHRASAL_CLASS) or affectedness_class(i["verb"].split()[0].lower()) != "keep_default")
    vn_cov = sum(1 for i in minst if i["vn_covered"])
    comb_cov = sum(1 for i in minst if i["comb_source"] != "hand_fallback" or affectedness_class(i["verb"].split()[0].lower()) != "keep_default")
    hand_oov = sorted({i["verb"] for i in minst
                       if (i["verb"].lower() not in PHRASAL_CLASS) and affectedness_class(i["verb"].split()[0].lower()) == "keep_default"})
    vn_oov = sorted({i["verb"] for i in minst if not i["vn_covered"]})

    # WORD-SENSE residual: per sense case, gate decision vs gold + per-sense rescue availability
    sense_cases = []
    for i in minst:
        if i["id"] not in SENSE_CASE_IDS:
            continue
        # a per-sense decision is 'correct' if it matches what gold needs:
        #   gold_none -> need forces_none True ; gold affected -> need forces_none False
        need_none = i["gold_none"]
        ps = i.get("per_sense", [])
        rescuable = (not i["comb_correct"]) and any(p["forces_none"] == need_none for p in ps)
        sense_cases.append({
            "id": i["id"], "verb": i["verb"], "gold_type": i["type"], "gold_none": need_none,
            "vn_lemma": i["vn_lemma"], "vn_modal_type": i["vn_type"], "vn_modal_graded": i["vn_graded"],
            "comb_forces_none": i["comb_none"] or i["neg_clause"], "comb_correct": i["comb_correct"],
            "n_senses": len(ps), "per_sense": ps, "rescuable_by_sense": rescuable,
        })
    n_sense_pass = sum(1 for s in sense_cases if s["comb_correct"])
    n_sense = len(sense_cases)
    n_sense_rescuable = sum(1 for s in sense_cases if s["rescuable_by_sense"])

    # combined-gate misses (transparency)
    comb_misses = [{"id": i["id"], "verb": i["verb"], "type": i["type"], "vn_type": i["vn_type"],
                    "comb_source": i["comb_source"], "comb_none": i["comb_none"],
                    "pred_surf": i["pred_surf"], "pred_none": i["pred_none"]}
                   for i in minst if not i["comb_correct"]]

    # hand vs verbnet DECISION conflicts (arm-2 conflict report; negation excluded to isolate lexicon)
    conflicts = [{"id": i["id"], "verb": i["verb"], "hand_none": i["hand_none"], "vn_none": i["vn_none"],
                  "vn_covered": i["vn_covered"], "gold_type": i["type"]}
                 for i in minst if i["hand_none"] != i["vn_none"]]

    # ARMS-MUST-DIFFER: raw/hand/verbnet/combined decision vectors must not all be identical
    def _digest(key):
        b = bytes([1 if i[key] else 0 for i in minst])
        return hashlib.sha256(b).hexdigest()
    arm_digests = {"raw": _digest("raw_correct"), "hand": _digest("hand_correct"),
                   "verbnet": _digest("vn_correct"), "combined": _digest("comb_correct")}
    arms_differ = len(set(arm_digests.values())) > 1

    # UD-EWT no-regression (secondary over-fire cost guard for the combined gate)
    ud_docs = load_ud_docs(UD_TEST)
    ud_docs = [d for d in ud_docs if len(d) >= 1]
    ud_docs = ud_docs[:(20 if mode == "smoke" else 250)]
    urows = eval_ud_noregression(ud_docs, tagger, parser, labeler)
    n_u = len(urows)
    u_base = acc(urows, "base_correct")
    u_comb = acc(urows, "comb_correct")
    u_delta = round((u_comb[0] or 0.0) - (u_base[0] or 0.0), 4)
    u_fired = sum(1 for r in urows if r["fired"])
    u_cost = sum(1 for r in urows if r["fired"] and r["base_correct"])

    # baseline-in-band (META_RULE_AG) on the held-out raw reader
    raw_in_band = bool(0.05 < (m_raw[0] or 0.0) < 0.95)

    # ---- verdict ----
    generalizes = bool((m_comb[0] or 0.0) > (m_raw[0] or 0.0) + 0.05)
    beats_raw_any = bool((m_comb[0] or 0.0) > (m_raw[0] or 0.0) + 1e-9)
    sense_blind_confirmed = bool(n_sense_pass < (n_sense / 2.0 + 1e-9)) if n_sense else False
    no_regression = bool(u_delta >= -0.05)

    if not arms_differ:
        verdict = "GATE_ARMS_IDENTICAL_BUG"
    elif generalizes and no_regression:
        verdict = "GATE_GENERALIZES_HELDOUT"
    elif generalizes and not no_regression:
        verdict = "GATE_GENERALIZES_BUT_OVERFIRES_UD"
    elif beats_raw_any:
        verdict = "GATE_WEAK_LIFT_HELDOUT"
    else:
        verdict = "GATE_NO_GENERALIZATION"

    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] held-out McGuffey N={n_m} (SMALL, single-annotator) | who-affected acc: "
        f"RAW={m_raw[0]}({m_raw[2]}/{m_raw[1]}) HAND={m_hand[0]} VERBNET={m_vn[0]} "
        f"COMBINED={m_comb[0]}({m_comb[2]}/{m_comb[1]}) (generalizes_over_raw={generalizes}) "
        f"| per_type_comb=" + ",".join(f"{ty}:{m_per_type[ty]['comb_acc']}({m_per_type[ty]['comb_correct']}/{m_per_type[ty]['n']})"
                                       for ty in sorted(m_per_type))
        + f" | coverage(held-out verbs): hand={hand_cov}/{n_m} verbnet={vn_cov}/{n_m} "
        f"(verbnet_OOV={vn_oov}) | hand-vs-verbnet decision conflicts={len(conflicts)} "
        f"| WORD-SENSE cases pass={n_sense_pass}/{n_sense} (sense_blind_confirmed={sense_blind_confirmed} "
        f"rescuable_by_per_sense={n_sense_rescuable}/{n_sense}) "
        f"| UD-EWT no-reg N={n_u}: base={u_base[0]} comb={u_comb[0]}(d={u_delta}) fired={u_fired} "
        f"cost={u_cost} (no_regression={no_regression}) | crude-neg COMBINED={m_comb_crudeneg[0]} "
        f"| arms_differ={arms_differ} raw_in_band={raw_in_band}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "N_heldout": n_m, "N_ud_instances": n_u, "is_probe_flag": True,
        "note": ("FULL verb-affectedness gate = VerbNet lexicon (breadth + per-sense + graded proto-"
                 "patient) COMBINED with v1 hand-lexicon (copula/stative/light VerbNet omits) on a "
                 "HELD-OUT McGuffey slice (N=38, Director-labeled, distinct from v1 N=34). HONEST "
                 "magnitude (v1 0.912 was co-defined per VET ad793d3a). Held-out packs word-sense test "
                 "cases on purpose. Gate = verb surface/lemma type-fact, gold-independent -> leak-clean "
                 "(mutation-probe permutes gold labels + re-derives). Credit VerbNet/Levin/Dowty/Beavers "
                 "+ v1 hand-lexicon. LOCAL-only; no push/remote-persist; no hdlab mutation."),
        "heldout_mcguffey": {
            "raw_acc": m_raw[0], "hand_acc": m_hand[0], "verbnet_acc": m_vn[0],
            "combined_acc": m_comb[0], "combined_crudeneg_acc": m_comb_crudeneg[0],
            "raw_correct": m_raw[2], "combined_correct": m_comb[2], "n": n_m,
            "generalizes_over_raw": generalizes, "beats_raw_any": beats_raw_any,
            "raw_in_band": raw_in_band, "per_type": m_per_type,
            "combined_misses": comb_misses,
        },
        "lexicon_comparison": {
            "hand_coverage": hand_cov, "verbnet_coverage": vn_cov, "combined_coverage": comb_cov,
            "hand_oov": hand_oov, "verbnet_oov": vn_oov,
            "hand_vs_verbnet_conflicts": conflicts, "n_conflicts": len(conflicts),
        },
        "word_sense_residual": {
            "n_cases": n_sense, "n_pass": n_sense_pass, "n_rescuable_by_per_sense": n_sense_rescuable,
            "sense_blind_confirmed": sense_blind_confirmed, "cases": sense_cases,
        },
        "ud_ewt_no_regression": {
            "base_acc": u_base[0], "combined_acc": u_comb[0], "delta": u_delta,
            "n_instances": n_u, "n_docs": len(ud_docs), "fired": u_fired, "cost": u_cost,
            "no_regression": no_regression,
            "gold_is_structural_caveat": ("UD-EWT who-affected gold = parse-derived (every obj = "
                                          "patient); the semantic gate can only cost here, never help. "
                                          "Delta is the over-fire cost, not a capability gap."),
        },
        "arms_differ_verified": arms_differ, "arm_digests": arm_digests,
        "negation_comparison": {"rule_primary": "clause_aware_segment",
                                "rule_reported": "crude_any_marker",
                                "combined_clauseaware_acc": m_comb[0],
                                "combined_crudeneg_acc": m_comb_crudeneg[0]},
        "mcguffey_per_instance": minst,
        "design_gate": {
            "real_baseline": "reader RAW who-affected (base_pick), recomputed in-cell on held-out",
            "one_variable": "the gate (off=RAW; on=hand/verbnet/combined)",
            "can_fail": ("combined<=raw+0.05 (no generalization) OR word-sense cases fail (<half) OR "
                         "hand-vs-verbnet decision conflict"),
            "difficulty_on": "real archaic McGuffey held-out + deliberately-packed word-sense cases",
            "leak_clean": "gate = verb surface/lemma type-fact, gold-independent; mutation-probe in self_test",
            "final_metrics_atomicity": "tmp_replace", "crlb_n/a": "accuracy on labeled gold, no noise floor",
            "calibration_check": "default_ok_for_this_regime (0.35 = builder spot-check 94.4% dec acc)",
        },
        "credit": ("VerbNet (Kipper-Schuler 2005); Levin 1993; Dowty 1991 proto-patient; Beavers 2011; "
                   "v1 hand-lexicon (exp_mcguffey_whoaffected_verb_affectedness_gate_v1)."),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    print("[self_test] start", flush=True)
    # --- lemmatizer (VerbNet is lemma-keyed) ---
    assert lemmatize("fed") == "feed"
    assert lemmatize("left") == "leave"
    assert lemmatize("lost") == "lose"
    assert lemmatize("met") == "meet"
    assert lemmatize("gives") == "give"
    assert lemmatize("stands") == "stand"
    assert lemmatize("has") == "have"
    assert lemmatize("are") == "be"

    # --- VerbNet decisions (graded threshold) ---
    dec, cov, info = verbnet_forces_none("see")
    assert cov and dec and info["vn_type"] == "cognition"          # see -> cognition 0.033 -> NONE
    dec, cov, info = verbnet_forces_none("fed")
    assert cov and not dec and info["lemma"] == "feed"             # feed -> change_of_state 0.8 -> KEEP
    dec, cov, info = verbnet_forces_none("met")
    assert cov and not dec and info["vn_type"] == "contact"        # meet -> contact 0.45 -> KEEP (sense-blind)
    dec, cov, info = verbnet_forces_none("has")
    assert (not cov)                                               # have -> OOV in VerbNet (hand supplies)

    # --- combined gate: hand supplies copula/stative/light that VerbNet omits ---
    d, src, _ = combined_forces_none("has"); assert d and src == "hand_stative_light"
    d, src, _ = combined_forces_none("are"); assert d and src == "hand_stative_light"
    d, src, _ = combined_forces_none("get up"); assert d and src == "hand_phrasal"      # phrasal override
    d, src, _ = combined_forces_none("fed"); assert (not d) and src == "verbnet"        # KEEP via VerbNet
    d, src, _ = combined_forces_none("zorptify"); assert (not d)                        # unknown -> KEEP

    # --- clause-aware negation (multi-clause fix) ---
    toks = ud_tokenize("We must not touch the nest, but we may look at it.")
    vt, _ = find_verb_index(toks, ["PRON","AUX","PART","VERB","DET","NOUN","PUNCT","CCONJ","PRON","AUX","VERB","ADP","PRON","PUNCT"], "touch")
    ti = [k + 1 for k, t in enumerate(toks) if t.lower() == "touch"][0]
    li = [k + 1 for k, t in enumerate(toks) if t.lower() == "look"][0]
    assert verb_is_negated_clauseaware(toks, ti) is True           # touch in the negated clause
    assert verb_is_negated_clauseaware(toks, li) is False          # look in the un-negated clause
    assert sentence_is_negated_crude(toks) is True                 # crude fires on either (the bug we fix)

    # --- real code path: construct the REAL front-end + run reader_pass on real held-out text ---
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    toks = ud_tokenize("The man has fed the black hen and the fat duck.")
    rp = reader_pass({"tokens": toks}, tagger, parser, labeler)
    assert "pos" in rp and "pools" in rp
    vidx, _ = find_verb_index(toks, rp["pos"], "fed")
    assert vidx is not None
    ud_docs = load_ud_docs(UD_TEST)
    assert ud_docs, "UD test conllu must load"
    ur = eval_ud_noregression(ud_docs[:2], tagger, parser, labeler)
    assert isinstance(ur, list)

    # --- LEAK-CLEAN mutation-probe (REAL): permute gold type/affected labels + re-derive gate ---
    with open(GOLD_PATH, encoding="utf-8") as f:
        gd = json.load(f)
    gold = gd["gold"]
    assert len(gold) == 38
    for g in gold:
        assert g["type"] in (AFFECTED_TYPES | NONE_TYPES), "unexpected gold type: %r" % g["type"]

    def gate_decisions(gold_list):
        out = []
        for g in gold_list:
            toks = ud_tokenize(g["text"])
            vi = [k + 1 for k, t in enumerate(toks) if t.lower() == g["verb"].split()[0].lower()]
            neg = verb_is_negated_clauseaware(toks, vi[0] if vi else None)
            d, _, _ = combined_forces_none(g["verb"])
            out.append(bool(d or neg))
        return out

    base_dec = gate_decisions(gold)
    # permute the gold type + affected labels across instances (verbs/text UNCHANGED)
    import random
    rng = random.Random(12345)  # FIXED seed (no hash()-derived seeding; PROT-023)
    perm = list(range(len(gold)))
    rng.shuffle(perm)
    mutated_gold = []
    for k, g in enumerate(gold):
        gg = dict(g)
        gg["type"] = gold[perm[k]]["type"]
        gg["affected"] = gold[perm[k]]["affected"]
        mutated_gold.append(gg)
    mut_dec = gate_decisions(mutated_gold)
    assert base_dec == mut_dec, "LEAK: gate decision changed when gold labels were permuted"

    print("[self_test] lemmatizer OK; VerbNet decisions OK; combined OK; clause-aware-neg OK; "
          "real-code-path OK; UD-load OK; leak-clean permutation-probe OK; gold OK", flush=True)
    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run("smoke"); return
    if args.full:
        run("full"); return
    self_test()


if __name__ == "__main__":
    out_dir_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(out_dir_crash, exist_ok=True)
        with open(os.path.join(out_dir_crash, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
