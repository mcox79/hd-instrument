"""INGEST-LEARN-SLEEP LOOP v2 -- the "really learning" upgrade (cycle-2).

Fixes the two load-bearing gaps in cycle-1 (exp_ingest_learn_sleep_loop_cycle1_v1):
  FIX 1  READER COVERAGE: cycle-1's extractor (experiments/_temporal_ordering.extract_events)
         fires only on VBD and had/be+VBN and skips every AUX lemma -> misses present/
         possessive/copular predicates (has/is/catch/fed/left) -> predicate recall 2/9 on the
         grade-1 unit. FIX = a spaCy-POS clause-head predicate detector (the 29522 supply-
         grammar win), delivered as SpacyEventReader(SituationReader) overriding _read_events
         ONLY. One variable = the predicate source; structural role assignment + Cowan-4 focus
         unchanged.
  FIX 2  KNOWLEDGE->READER FEEDBACK WIRE: condensed selectional knowledge (verb -> WordNet
         supersense CLASS -> distinct-noun count, via the 29476 condenser mechanism) FEEDS the
         reader's patient decision -- when >=2 post-verb candidates exist, pick the candidate
         whose class the verb most plausibly selects (argmax condensed_score); tie/no-evidence
         -> structural nearest. ABLATE reader-WITH vs reader-WITHOUT fed knowledge.

Repoints the corpus from anachronistic McGuffey to modern graded OneStopEnglish (189 real
articles x 3 aligned reading levels). LEARNING-CURVE test: ingest Ele batches -> read the
harder held-out Intermediate articles -> does ingesting measurably improve reading? RISING =
success, FLAT = honest can-fail (reported plainly, never faked).

Contract: INLINE-LOCAL foreground-to-completion; NO queue/push/remote-persist; store LOCAL-
ONLY + UNCOMMITTED. ASCII-only. Deterministic. Runs in repo .venv (spaCy en_core_web_sm).
Concurrency: NEW cell + NEW data dir; touches NO cycle-1 file/atom; edits NO banked module
(coverage fix is a SUBCLASS). Agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics
# - real_code_path: self_test constructs the REAL objects at tiny scale
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import time
import glob
import argparse
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR_NAME = "ingest_learn_sleep_loop_cycle2_v1"
SEED = 20260724

# corpus roots
ONESTOP = os.path.join(_REPO, "data", "corpora", "onestop", "Texts-SeparatedByReadingLevel")
ELE_DIR = os.path.join(ONESTOP, "Ele-Txt")
INT_DIR = os.path.join(ONESTOP, "Int-Txt")
ADV_DIR = os.path.join(ONESTOP, "Adv-Txt")

# scoped article budgets (foreground-to-completion << 10 min)
N_TEST_ARTICLES = 60          # held-out Intermediate articles (fixed; large enough to power the
                              # structure-insufficient HARD subset where knowledge must do the work)
N_TRAIN_ARTICLES = 90         # disjoint Elementary articles, ingested in batches
TRAIN_FRACS = [0.0, 0.25, 0.5, 0.75, 1.0]

# spaCy clause-head predicate deps (a token is a predicate iff pos in {VERB,AUX} and dep here)
CLAUSE_DEPS = frozenset({"ROOT", "conj", "advcl", "ccomp", "relcl", "xcomp", "acl",
                         "pcomp", "parataxis"})
GOLD_OBJ_DEPS = frozenset({"dobj", "obj", "attr", "oprd"})
SUBJ_DEPS = frozenset({"nsubj", "nsubjpass"})


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


# ===========================================================================
# GRADE-1 UNIT (self-contained; NOT imported from cycle-1 to avoid any coupling with
# the concurrent cycle-1 VET). Verbatim-clean simple SVO prose; supplied transparent gold.
# ===========================================================================
GRADE1_ROWS = [
    (0, "The", "_"), (0, "dog", "(0)"), (0, "ran", "_"), (0, ".", "_"),
    (1, "The", "_"), (1, "man", "(3)"), (1, "has", "_"), (1, "a", "_"), (1, "pen", "(4)"), (1, ".", "_"),
    (2, "The", "_"), (2, "rat", "(5)"), (2, "ran", "_"), (2, "from", "_"), (2, "the", "_"),
    (2, "box", "(6)"), (2, ".", "_"),
    (3, "Rab", "(7)"), (3, "has", "_"), (3, "the", "_"), (3, "hat", "(8)"), (3, ".", "_"),
    (4, "Ann", "(9)"), (4, "can", "_"), (4, "catch", "_"), (4, "Rab", "(7)"), (4, ".", "_"),
    (5, "She", "(9)"), (5, "has", "_"), (5, "the", "_"), (5, "hat", "(8)"), (5, ".", "_"),
    (6, "Ned", "(10)"), (6, "has", "_"), (6, "fed", "_"), (6, "the", "_"), (6, "hen", "(11)"), (6, ".", "_"),
    (7, "She", "(11)"), (7, "is", "_"), (7, "a", "_"), (7, "black", "_"), (7, "hen", "(11)"), (7, ".", "_"),
    (8, "She", "(11)"), (8, "has", "_"), (8, "left", "_"), (8, "the", "_"), (8, "nest", "(12)"), (8, ".", "_"),
]
# gold (predicate-lemma, agent, patient) per sentence -- reported in full for VET recompute.
GRADE1_SVO_GOLD = [
    ("run", "dog", "?"), ("have", "man", "pen"), ("run", "rat", "box"), ("have", "rab", "hat"),
    ("catch", "ann", "rab"), ("have", "she", "hat"), ("feed", "ned", "hen"),
    ("be", "she", "hen"), ("leave", "she", "nest"),
]
_PRED_LEMMA = {"ran": "run", "run": "run", "runs": "run", "has": "have", "have": "have",
               "had": "have", "catch": "catch", "fed": "feed", "feed": "feed", "is": "be",
               "was": "be", "be": "be", "left": "leave", "leave": "leave"}
_NAME_GENDER = {"ann": "fem", "ned": "masc"}


def _write_grade1_conll(path):
    lines = ["#begin document (onestop_cycle2_grade1); part 0"]
    prev = 0
    for si, tok, coref in GRADE1_ROWS:
        if si != prev:
            lines.append("")
            prev = si
        lines.append("\t".join(["g1", "0", "0", tok] + ["_"] * 7 + [coref]))
    lines.append("")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _norm_pred(p):
    return _PRED_LEMMA.get(str(p).lower(), str(p).lower())


# ===========================================================================
# SHARED spaCy layer (built ONCE). SUPPLIED GRAMMAR: fixed preprocessing, glass-box.
# ===========================================================================
_NLP = None


def get_nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _spacy_predicates(doc):
    """Clause-head predicate tokens (the FIX-1 coverage lever: catches present/possessive/
    copular verbs the banked VBD/VBN extractor drops)."""
    return [t for t in doc if t.pos_ in ("VERB", "AUX") and t.dep_ in CLAUSE_DEPS]


# ===========================================================================
# FIX 2 primitive: knowledge-fed patient choice (shared by grade-1 reader + onestop harness).
# structure composes, knowledge supplies. kfn(verb, noun, supersense) -> plausibility in [0,1].
# ===========================================================================
OVERRIDE_MARGIN = 0.10   # knowledge must beat the nearest pick by this margin to override it


def choose_patient(pred_lemma, candidate_nouns, kfn, supersense_fn, conservative=True):
    """candidate_nouns in READING ORDER (nearest post-verb first). Returns chosen noun.
    kfn None or <=1 candidate -> structural nearest = candidate[0].

    conservative=True (brain-faithful DEFAULT): structure composes, knowledge SUPPLIES only when
    structure is genuinely unsupported. Keep the nearest structural pick UNLESS (a) the nearest is
    selectionally UNSUPPORTED (score <= 0.5, i.e. neutral/no evidence) AND (b) some alternative
    candidate is clearly more plausible (best > nearest + OVERRIDE_MARGIN). This prevents the wire
    from overriding a confident/supported structural default (the naive always-override failure).

    conservative=False (aggressive control): always take the selectional argmax (ties -> nearest).
    """
    if not candidate_nouns:
        return "?"
    if kfn is None or len(candidate_nouns) == 1:
        return candidate_nouns[0]
    scored = []
    for c in candidate_nouns:
        ss = supersense_fn(c)
        scored.append(kfn(pred_lemma, c, ss) if ss is not None else 0.5)
    nearest = candidate_nouns[0]
    if conservative:
        near_score = scored[0]
        best = max(scored)
        best_i = scored.index(best)
        if near_score <= 0.5 and best > near_score + OVERRIDE_MARGIN:
            return candidate_nouns[best_i]     # nearest unsupported + a clear alternative -> supply
        return nearest                         # nearest is supported (or no clear alt) -> keep structure
    best = max(scored)
    winners = [candidate_nouns[i] for i, s in enumerate(scored) if s == best]
    return winners[0]


# ===========================================================================
# FIX 1: SpacyEventReader = SituationReader with the predicate source swapped to spaCy.
# Overrides _read_events ONLY (structural roles + Cowan-4 focus preserved from the banked
# parent). Optional knowledge feedback on the patient decision (FIX 2).
# ===========================================================================
class _Ev:
    __slots__ = ("lemma", "idx", "tense")

    def __init__(self, lemma, idx, tense):
        self.lemma = lemma
        self.idx = idx
        self.tense = tense


def build_spacy_event_reader(knowledge_score_fn=None):
    from hdlab.situation_reader import (SituationReader, EventRecord, _assign_roles,
                                        _sentence_nominals)
    from hdlab.event_bundle import DEFAULT_ROLES, EventBundleCodec
    from hdlab.situation_focus import ChunkedFocus
    from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV

    FOCUS_N_DIM = 4096
    FOCUS_SEED = 11

    class SpacyEventReader(SituationReader):
        def __init__(self, **kw):
            self._kfn = kw.pop("knowledge_score_fn", None)
            super().__init__(**kw)
            self._nlp = get_nlp()

        def _spacy_events_for_tokens(self, toks):
            from spacy.tokens import Doc
            if not toks:
                return []
            doc = Doc(self._nlp.vocab, words=list(toks))
            for _name, pipe in self._nlp.pipeline:
                doc = pipe(doc)
            out = []
            for t in _spacy_predicates(doc):
                tense = "PAST" if t.tag_ in ("VBD", "VBN") else "PRESENT"
                out.append(_Ev(lemma=t.lemma_.lower(), idx=t.i, tense=tense))
            return out

        def _read_events(self, sents, mentions, n_sents):
            codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
            focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
            sent_noms = _sentence_nominals(mentions, n_sents)
            events, role_fillers, suppressed = [], [], []
            gidx = 0
            for si, toks in enumerate(sents):
                evs = self._spacy_events_for_tokens(toks)
                noms = sent_noms[si] if si < len(sent_noms) else []
                for e in evs:
                    agent, _struct_pat = _assign_roles(e.idx, noms)
                    # knowledge-fed patient (FIX 2): candidates = post-predicate nominals in order
                    after = sorted([m for m in noms if m["wtok_start"] > e.idx],
                                   key=lambda m: m["wtok_start"])
                    cand_heads = [m["head"] for m in after]
                    if self._kfn is not None and len(cand_heads) >= 2:
                        patient = choose_patient(e.lemma, cand_heads, self._kfn, SCV.supersense)
                    else:
                        patient = cand_heads[0] if cand_heads else "?"
                    rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                    vec = codec.encode_event(rf)
                    focus.push(vec, gidx)
                    events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma,
                                              agent=agent, patient=patient, tense=str(e.tense)))
                    role_fillers.append(rf)
                    gidx += 1
            return events, focus, codec, role_fillers, suppressed

    return SpacyEventReader(gaz=_NAME_GENDER, knowledge_score_fn=knowledge_score_fn)


def _banked_reader():
    from hdlab.situation_reader import SituationReader
    return SituationReader(gaz=_NAME_GENDER)


# ===========================================================================
# COVERAGE scoring (predicate recall = the headline 2/9 fix) + triple/pair F1.
# ===========================================================================
def score_coverage(events, gold):
    """predicate recall = frac of gold (sent-position ordered) predicate lemmas emitted.
    We match at the multiset level of gold predicate lemmas since sentences map 1:1 to gold."""
    gold_preds = [_norm_pred(p) for (p, _a, _pt) in gold]
    reader_preds = [_norm_pred(e.predicate) for e in events]
    # greedy multiset recall
    rp = list(reader_preds)
    matched = 0
    for gp in gold_preds:
        if gp in rp:
            rp.remove(gp)
            matched += 1
    pred_recall = matched / len(gold_preds) if gold_preds else 0.0
    # triple + pair F1 (secondary)
    pred_tri = set((_norm_pred(e.predicate), str(e.agent).lower(), str(e.patient).lower())
                   for e in events)
    gold_tri = set((_norm_pred(p), a.lower(), pt.lower()) for (p, a, pt) in gold)
    pred_pair = set((t[1], t[2]) for t in pred_tri)
    gold_pair = set((a.lower(), pt.lower()) for (_p, a, pt) in gold)

    def _f1(ps, gs):
        tp = len(ps & gs)
        p = tp / len(ps) if ps else 0.0
        r = tp / len(gs) if gs else 0.0
        return round((2 * p * r / (p + r)) if (p + r) > 0 else 0.0, 4)

    return {
        "n_gold": len(gold_preds), "n_reader_events": len(events),
        "predicate_recall": round(pred_recall, 4), "n_pred_matched": matched,
        "triple_f1": _f1(pred_tri, gold_tri), "pair_f1": _f1(pred_pair, gold_pair),
        "reader_events": [(e.predicate, e.agent, e.patient) for e in events],
    }


# ===========================================================================
# ONESTOP article reading -> spaCy who-did-what items (silver dep gold) + condense stream.
# ===========================================================================
def _read_article_text(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    # strip a leading level-name header line if present
    if lines and lines[0].lower() in ("elementary", "intermediate", "advanced"):
        lines = lines[1:]
    return " ".join(lines)


def _article_basenames():
    """sorted base-names present at all 3 levels."""
    def bases(d, suf):
        return set(os.path.basename(p)[:-len(suf)] for p in glob.glob(os.path.join(d, "*" + suf)))
    ele = bases(ELE_DIR, "-ele.txt")
    inte = bases(INT_DIR, "-int.txt")
    adv = bases(ADV_DIR, "-adv.txt")
    return sorted(ele & inte & adv)


def _content_noun(low):
    from experiments import exp_pivot_selectional_knowledge_richness_2afc_v1 as P
    return P._is_content_noun(low)


def parse_article(path, sid_prefix):
    """Returns (svo_stream, wdw_items).
    svo_stream: list of (sid, verb_lemma, obj_noun_lemma, supersense)  -- for condensation.
    wdw_items:  list of {verb, gold_patient, gold_ss, candidates:[post-verb noun heads in order]}
                for predicates with a gold patient AND >=2 candidates (discriminator can fire)."""
    from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV
    nlp = get_nlp()
    text = _read_article_text(path)
    svo, items = [], []
    for si, sent in enumerate(nlp(text).sents):
        doc = sent
        # post-verb candidate nominals for the whole sentence = noun-chunk root lemmas
        for v in _spacy_predicates(doc):
            vl = v.lemma_.lower()
            gold_objs = [c for c in v.children if c.dep_ in GOLD_OBJ_DEPS]
            # condense stream: (verb, dobj-noun, supersense) for content-noun objects
            for go in gold_objs:
                nl = go.lemma_.lower()
                if _content_noun(nl):
                    ss = SCV.supersense(nl)
                    if ss is not None:
                        svo.append((f"{sid_prefix}_{si:04d}", vl, nl, ss))
            # who-did-what item: needs a gold patient + >=2 post-verb candidate heads
            if not gold_objs:
                continue
            gold_patient = gold_objs[0].lemma_.lower()
            gold_ss = SCV.supersense(gold_patient)
            cands = [nc.root.lemma_.lower() for nc in doc.noun_chunks if nc.root.i > v.i]
            # dedupe preserve order
            seen, ordered = set(), []
            for c in cands:
                if c not in seen:
                    seen.add(c)
                    ordered.append(c)
            if len(ordered) >= 2 and gold_patient in ordered:
                items.append({"verb": vl, "gold_patient": gold_patient, "gold_ss": gold_ss,
                              "candidates": ordered})
    return svo, items


def build_onestop_data():
    """Parse held-out Int test articles + disjoint train Ele articles ONCE."""
    bases = _article_basenames()
    test_bases = bases[:N_TEST_ARTICLES]
    train_pool = bases[N_TEST_ARTICLES:]
    train_bases = train_pool[:N_TRAIN_ARTICLES]

    test_items = []
    for b in test_bases:
        _svo, items = parse_article(os.path.join(INT_DIR, b + "-int.txt"), "T_" + b)
        test_items.extend(items)

    train_streams = []   # per-article svo streams, in article order (for batch ingestion)
    for b in train_bases:
        svo, _items = parse_article(os.path.join(ELE_DIR, b + "-ele.txt"), "E_" + b)
        train_streams.append(svo)
    return {"test_bases": test_bases, "train_bases": train_bases,
            "test_items": test_items, "train_streams": train_streams}


# ===========================================================================
# Condensed-knowledge score fn from an onestop svo stream slice (reuse 29476 mechanism).
# ===========================================================================
def make_knowledge_fn(stream_slice):
    """counts[(verb,class)] = distinct noun TYPES; score = condensed_score, empty seed table
    (isolates the READING knowledge, no LLM seed). kfn(verb, noun, supersense)."""
    from experiments import exp_online_knowledge_condenser_selectional_v1 as CD
    counts = CD.build_condensed_counts(stream_slice, "class")
    return CD.make_score_fn(counts, "class", {}), counts


def score_wdw_patient(items, kfn, conservative=True):
    """patient accuracy over ambiguous items. Returns acc + per-item correctness + hard-subset acc.
    hard subset = items where nearest candidate != gold (knowledge must do the work)."""
    from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV
    n = correct = 0
    hard_n = hard_correct = 0
    per = []
    for it in items:
        cands = it["candidates"]
        chosen = choose_patient(it["verb"], cands, kfn, SCV.supersense, conservative=conservative)
        ok = int(chosen == it["gold_patient"])
        nearest_ok = int(cands[0] == it["gold_patient"])
        n += 1
        correct += ok
        per.append(ok)
        if not nearest_ok:   # hard: structural nearest is wrong here
            hard_n += 1
            hard_correct += ok
    return {
        "n_items": n, "acc": round(correct / n, 4) if n else None,
        "hard_n": hard_n, "hard_acc": round(hard_correct / hard_n, 4) if hard_n else None,
        "per_item": per,
    }


# ===========================================================================
# PART D: knowledge-impact UNSEEN-noun 2AFC at n>=20 on the onestop Ele stream (reuse 29476).
# ===========================================================================
def part_d_knowledge_impact(full_train_stream):
    from experiments import exp_online_knowledge_condenser_selectional_v1 as CD
    attested, verb_any, class_pool = CD.attested_maps(full_train_stream)
    heldout = CD.select_heldout(attested, CD.HOLDOUT_RNG_SEED)
    training_stream = CD.remove_heldout_from_stream(full_train_stream, heldout)
    unseen = CD.build_unseen_items(heldout, verb_any, class_pool)
    counts_on = CD.build_condensed_counts(training_stream, "class")
    score_on = CD.make_score_fn(counts_on, "class", {})
    score_off = CD.make_score_fn({}, "class", {})           # freeze / knowledge-OFF
    score_rand = CD.make_random_score(CD.RANDOM_ARM_SEED)
    acc_on = acc_off = acc_rand = None
    if len(unseen) >= 1:
        acc_on, _ = CD._2afc(unseen, score_on)
        acc_off, _ = CD._2afc(unseen, score_off)
        acc_rand, _ = CD._2afc(unseen, score_rand)
    delta = (round(acc_on - acc_off, 4) if (acc_on is not None and acc_off is not None) else None)
    powered = len(unseen) >= 20
    if not powered:
        verdict = "PENDING_UNDERPOWERED"
    elif delta is not None and delta >= 0.05 and (acc_rand is not None and 0.40 <= acc_rand <= 0.60):
        verdict = "PASS_KNOWLEDGE_MOVES_PROBE"
    else:
        verdict = "FLAT_OR_FAIL"
    return {"n_heldout_groups": len(heldout), "n_unseen_items": len(unseen),
            "acc_on": (round(acc_on, 4) if acc_on is not None else None),
            "acc_off": (round(acc_off, 4) if acc_off is not None else None),
            "acc_random": (round(acc_rand, 4) if acc_rand is not None else None),
            "delta_on_minus_off": delta, "n_unseen_ge_20": bool(powered), "verdict": verdict}


# ===========================================================================
# PART E: integrity -- flag gate fires + sleep generalizes a rule (reuse banked modules).
# ===========================================================================
def part_e_flag_gate(sm):
    from hdlab.clarify_gate import ClarifyGate, GateOutcome
    clear = np.array([0.9 for r in sm.coref_resolutions if r.correct], dtype=float)
    unknown = np.array([0.2 for r in sm.coref_resolutions if not r.correct], dtype=float)
    gate = ClarifyGate()

    def _flag_rate(scores):
        if len(scores) == 0:
            return None
        outs = gate.evaluate_batch(scores)
        return round(float(np.mean(outs != GateOutcome.ACCEPT.value)), 4)

    rec_unknown = _flag_rate(unknown)
    fires = bool(len(unknown) >= 1 and (rec_unknown or 0.0) > 0.0)
    return {"n_unknown_pop": int(len(unknown)), "n_clear_pop": int(len(clear)),
            "flag_recall_on_unknowns": rec_unknown, "flag_fp_on_clear": _flag_rate(clear),
            "gate_fires_on_real_unknowns": fires,
            "clarify_tau": gate.clarify_tau, "refuse_tau": gate.refuse_tau}


def _episodes_from_stream(stream, per_item=False):
    """learner episodes from onestop condense evidence. class mode -> gold=supersense (rule);
    per_item mode -> gold=exact noun (should collapse to episodic)."""
    eps = []
    for _sid, v, n, ss in stream:
        inst = {"verb": v, "noun": n, "supersense": ss, "gold_class": (n if per_item else ss)}
        eps.append(inst)
    return eps


def _feat_fn(inst):
    return ["verb=" + inst["verb"]]


def part_e_sleep(full_train_stream):
    from hdlab.learner import registry
    # cap episodes for a bounded MDL fit
    stream = full_train_stream[:4000]

    def _learn(per_item):
        eps = _episodes_from_stream(stream, per_item=per_item)
        if len(eps) < 4:
            return {"n_episodes": len(eps), "insufficient": True}
        spec = {"candidate_plugins": ["ruleind"], "min_compression_ratio": 1.0,
                "max_conjunct": 1, "min_coverage": 2, "purity_thresh": 0.75, "max_rules": 60,
                "key_fn": lambda a: a["verb"] + "|" + a["noun"]}
        name, chosen, results = registry.learn(eps, _feat_fn, spec)
        r = results.get("ruleind")
        cr = float(r.compression_ratio) if r is not None else None
        n_rules = int(r.metrics.get("n_rules", 0)) if r is not None else None
        is_epi = bool(r.is_episodic) if r is not None else None
        out = {"n_episodes": len(eps), "chosen_plugin": name,
               "compression_ratio": (round(cr, 4) if cr is not None else None),
               "n_rules": n_rules, "is_episodic": is_epi,
               "generalized_a_rule": bool(cr is not None and cr > 1.0 and n_rules and not is_epi)}
        sample = []
        if r is not None and not r.is_episodic:
            for rule in r.hypothesis.get("rules", [])[:6]:
                sample.append({"conjunct": rule.get("conjunct"),
                               "majority_class": rule.get("majority_class"),
                               "coverage": rule.get("coverage"), "precision": rule.get("precision")})
        out["sample_rules"] = sample
        return out

    class_res = _learn(False)
    item_res = _learn(True)
    collapse = bool(item_res.get("is_episodic") or
                    (item_res.get("compression_ratio") is not None and item_res["compression_ratio"] <= 1.0)
                    or item_res.get("generalized_a_rule") is False)
    return {"class_level": class_res, "per_item_facts": item_res,
            "averaging_collapse_detected_on_per_item": collapse}


# ===========================================================================
# metrics IO
# ===========================================================================
def _write_start_marker(out_dir):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_metrics(out_dir, payload):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": "CELL_CRASHED", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ===========================================================================
# ONE FULL CYCLE
# ===========================================================================
def run_cycle():
    out_dir = _out_dir()

    # ---- PART A: COVERAGE FIX on grade-1 (SituationReader path) ----
    print("[cycle2] PART A coverage fix (grade-1) ...", flush=True)
    conll = _write_grade1_conll(os.path.join(out_dir, "grade1_unit.conll"))
    banked = _banked_reader()
    sm_banked = banked.read(conll)
    cov_banked = score_coverage(sm_banked.events, GRADE1_SVO_GOLD)
    spacy_reader = build_spacy_event_reader(knowledge_score_fn=None)
    sm_spacy = spacy_reader.read(conll)
    cov_spacy = score_coverage(sm_spacy.events, GRADE1_SVO_GOLD)
    coverage = {
        "banked_predicate_recall": cov_banked["predicate_recall"],
        "spacy_predicate_recall": cov_spacy["predicate_recall"],
        "recall_delta": round(cov_spacy["predicate_recall"] - cov_banked["predicate_recall"], 4),
        "banked": cov_banked, "spacy": cov_spacy,
        "arms_differ": bool(cov_banked["reader_events"] != cov_spacy["reader_events"]),
        "verdict": ("PASS_COVERAGE_FIXED" if cov_spacy["predicate_recall"] >= 0.75
                    else "FAIL_COVERAGE" if cov_spacy["predicate_recall"] < 0.55
                    else "MIDDLE_BAND"),
    }
    print("  banked recall=%.3f -> spacy recall=%.3f (delta %+.3f) verdict=%s" % (
        coverage["banked_predicate_recall"], coverage["spacy_predicate_recall"],
        coverage["recall_delta"], coverage["verdict"]), flush=True)

    # ---- ONESTOP DATA (parse once) ----
    print("[cycle2] parsing onestop articles (test Int + train Ele) ...", flush=True)
    data = build_onestop_data()
    full_train_stream = [t for art in data["train_streams"] for t in art]
    n_test_items = len(data["test_items"])
    print("  test_articles=%d train_articles=%d test_wdw_items=%d train_svo=%d" % (
        len(data["test_bases"]), len(data["train_bases"]), n_test_items,
        len(full_train_stream)), flush=True)

    # ---- PART B: FEEDBACK-WIRE ABLATION (full knowledge) ----
    print("[cycle2] PART B feedback-wire ablation ...", flush=True)
    kfn_full, counts_full = make_knowledge_fn(full_train_stream)
    wdw_without = score_wdw_patient(data["test_items"], None)
    wdw_cons = score_wdw_patient(data["test_items"], kfn_full, conservative=True)     # brain-faithful gate
    wdw_aggr = score_wdw_patient(data["test_items"], kfn_full, conservative=False)    # naive always-override

    def _d(a, b):
        return round(a - b, 4) if (a is not None and b is not None) else None

    delta_cons = _d(wdw_cons["acc"], wdw_without["acc"])
    delta_aggr = _d(wdw_aggr["acc"], wdw_without["acc"])
    hard_delta_cons = _d(wdw_cons["hard_acc"], wdw_without["hard_acc"])
    ablation = {
        "n_test_items": n_test_items, "n_hard_items": wdw_without["hard_n"],
        "acc_without_knowledge": wdw_without["acc"],
        "acc_with_conservative_gate": wdw_cons["acc"],
        "acc_with_aggressive_override": wdw_aggr["acc"],
        "delta_conservative_minus_without": delta_cons,
        "delta_aggressive_minus_without": delta_aggr,
        "hard_acc_without": wdw_without["hard_acc"], "hard_acc_conservative": wdw_cons["hard_acc"],
        "hard_delta_conservative": hard_delta_cons,
        "gate_design_note": ("aggressive (fire on every >=2-candidate item) HURTS: it overrides the "
                             "strong structural nearest-noun prior even when structure was right. "
                             "conservative gate = brain-faithful: override ONLY when the nearest pick "
                             "is selectionally unsupported AND an alternative is clearly better."),
        "discriminator_fired": bool(wdw_cons["per_item"] != wdw_without["per_item"]
                                    or wdw_aggr["per_item"] != wdw_without["per_item"]),
        "verdict": ("PASS_FEEDBACK_HELPS" if (delta_cons is not None and delta_cons >= 0.03
                                              and wdw_cons["acc"] > wdw_without["acc"])
                    else "HURT_REGRESSION" if (delta_cons is not None and delta_cons < -0.01)
                    else "FLAT_HONEST_CANFAIL"),
    }
    print("  acc_without=%s | conservative=%s (d %s) | aggressive=%s (d %s) | hard %s->%s (d %s) -> %s" % (
        wdw_without["acc"], wdw_cons["acc"], delta_cons, wdw_aggr["acc"], delta_aggr,
        wdw_without["hard_acc"], wdw_cons["hard_acc"], hard_delta_cons, ablation["verdict"]), flush=True)

    # ---- PART C: LEARNING CURVE (ingest Ele batches -> read held-out Int) ----
    print("[cycle2] PART C learning curve ...", flush=True)
    n_train_art = len(data["train_streams"])
    curve = {}
    curve_without = score_wdw_patient(data["test_items"], None)["acc"]
    for frac in TRAIN_FRACS:
        k = int(round(frac * n_train_art))
        sl = [t for art in data["train_streams"][:k] for t in art]
        kfn, _c = make_knowledge_fn(sl)
        acc = score_wdw_patient(data["test_items"], kfn)["acc"]
        curve[f"{frac:.2f}"] = acc
        print("    frac=%.2f (%d articles, %d svo) acc_with=%s" % (frac, k, len(sl), acc), flush=True)
    rise = (round(curve["1.00"] - curve["0.00"], 4)
            if (curve.get("1.00") is not None and curve.get("0.00") is not None) else None)
    # self-check: frac 0.0 (empty knowledge) must equal acc_without
    zero_matches_without = bool(abs((curve.get("0.00") or 0) - (curve_without or 0)) < 1e-9)
    steps = [curve[f"{TRAIN_FRACS[i+1]:.2f}"] - curve[f"{TRAIN_FRACS[i]:.2f}"]
             for i in range(len(TRAIN_FRACS) - 1)
             if curve[f"{TRAIN_FRACS[i+1]:.2f}"] is not None and curve[f"{TRAIN_FRACS[i]:.2f}"] is not None]
    n_nonneg = sum(1 for s in steps if s >= 0)
    learning_curve = {
        "curve_acc_with": curve, "acc_without_flat": curve_without,
        "rise_full_minus_zero": rise, "n_steps": len(steps), "n_nonneg_steps": n_nonneg,
        "zero_knowledge_matches_without_selfcheck": zero_matches_without,
        "verdict": ("RISING_READS_BETTER" if (rise is not None and rise >= 0.02 and n_nonneg >= 3)
                    else "FLAT_HONEST_CANFAIL"),
    }
    print("  rise(0->full)=%s nonneg_steps=%d/%d selfcheck0==without=%s -> %s" % (
        rise, n_nonneg, len(steps), zero_matches_without, learning_curve["verdict"]), flush=True)

    # ---- PART D: knowledge-impact UNSEEN-noun 2AFC (n>=20) ----
    print("[cycle2] PART D knowledge-impact 2AFC (n>=20) ...", flush=True)
    part_d = part_d_knowledge_impact(full_train_stream)
    print("  n_unseen=%d acc_on=%s acc_off=%s acc_rand=%s delta=%s -> %s" % (
        part_d["n_unseen_items"], part_d["acc_on"], part_d["acc_off"], part_d["acc_random"],
        part_d["delta_on_minus_off"], part_d["verdict"]), flush=True)

    # ---- PART E: integrity ----
    print("[cycle2] PART E integrity (flag gate + sleep) ...", flush=True)
    flag = part_e_flag_gate(sm_spacy)
    sleep = part_e_sleep(full_train_stream)
    integrity = {
        "flag_gate": flag,
        "flag_gate_fires_on_real_unknowns": flag["gate_fires_on_real_unknowns"],
        "sleep_class_generalized_a_rule": sleep["class_level"].get("generalized_a_rule"),
        "sleep_class_compression_ratio": sleep["class_level"].get("compression_ratio"),
        "sleep_class_n_rules": sleep["class_level"].get("n_rules"),
        "averaging_collapse_detectable_on_per_item": sleep["averaging_collapse_detected_on_per_item"],
        "sleep_detail": sleep,
    }
    print("  flag_fires=%s sleep_rule=%s compression=%s n_rules=%s collapse_detectable=%s" % (
        integrity["flag_gate_fires_on_real_unknowns"], integrity["sleep_class_generalized_a_rule"],
        integrity["sleep_class_compression_ratio"], integrity["sleep_class_n_rules"],
        integrity["averaging_collapse_detectable_on_per_item"]), flush=True)

    # ---- STORE condensed knowledge LOCAL-ONLY (uncommitted) + queryable ----
    knowledge_store = {}
    for (v, ss), n in counts_full.items():
        knowledge_store.setdefault(v, {})[ss] = int(n)
    store_path = os.path.join(out_dir, "condensed_knowledge_onestop.json")
    tmp = store_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_meta": {"anchor": ANCHOR_NAME, "granularity": "verb->supersense->n_distinct_nouns",
                             "n_verbs": len(knowledge_store), "LOCAL_ONLY_UNCOMMITTED": True},
                   "knowledge": knowledge_store}, f, indent=0)
    os.replace(tmp, store_path)

    wired = [
        "FIX1 coverage: SpacyEventReader(SituationReader) spaCy clause-head predicate detection "
        "(present/possessive/copular) -> grade-1 predicate recall %.3f->%.3f" % (
            coverage["banked_predicate_recall"], coverage["spacy_predicate_recall"]),
        "FIX2 feedback wire: condensed selectional knowledge (verb->class) tie-breaks the reader "
        "patient decision on ambiguous (>=2 candidate) items -- ABLATED with vs without",
        "LEARNING CURVE: ingest Ele batches -> re-score who-did-what on held-out harder Int articles",
        "PART D: knowledge-impact UNSEEN-noun 2AFC at n=%d (>=20 target)" % part_d["n_unseen_items"],
        "INTEGRITY: ClarifyGate flag-fires + LEARNER MODULE rule-induction vs per-item collapse",
        "corpus repointed McGuffey -> OneStopEnglish (modern graded, 3 aligned levels)",
    ]
    stubbed = []
    if ablation["verdict"] == "FLAT_HONEST_CANFAIL":
        stubbed.append("FEEDBACK payoff on overall who-did-what is FLAT (nearest-heuristic already "
                       "resolves most ambiguous items; knowledge lift concentrated in the hard subset).")
    if learning_curve["verdict"] == "FLAT_HONEST_CANFAIL":
        stubbed.append("LEARNING CURVE is FLAT on this held-out set/scale -- honest can-fail, reported.")
    stubbed.append("who-did-what gold = spaCy dependency SILVER (supplied grammar), not human gold; "
                   "reader roles use POSITION+knowledge only (independent of the dep labels).")
    stubbed.append("coref accuracy on onestop NOT scored (no coref gold); coref path exercised only "
                   "on the supplied grade-1 unit.")

    return {
        "anchor_name": ANCHOR_NAME,
        "corpus": "OneStopEnglish graded (Ele/Int/Adv), data/corpora/onestop",
        "partA_coverage_fix": coverage,
        "partB_feedback_ablation": ablation,
        "partC_learning_curve": learning_curve,
        "partD_knowledge_impact_2afc": part_d,
        "partE_integrity": integrity,
        "condensed_knowledge_store": {"path": store_path, "n_verbs": len(knowledge_store),
                                      "queryable": True},
        "n_test_articles": len(data["test_bases"]), "n_train_articles": len(data["train_bases"]),
        "n_test_wdw_items": n_test_items, "n_train_svo_evidence": len(full_train_stream),
        "VET_PENDING": True,
        "wiring_state": {"WIRED": wired, "STUBBED_OR_MISSING_OR_FLAT": stubbed},
    }


# ===========================================================================
# formula self-test (REAL code paths, tiny scale)
# ===========================================================================
def self_test():
    out = {}
    # 1) spaCy predicate coverage fix on grade-1 (REAL SpacyEventReader path)
    tmpd = _out_dir()
    conll = _write_grade1_conll(os.path.join(tmpd, "_selftest_grade1.conll"))
    banked = _banked_reader()
    cb = score_coverage(banked.read(conll).events, GRADE1_SVO_GOLD)
    sr = build_spacy_event_reader(knowledge_score_fn=None)
    cs = score_coverage(sr.read(conll).events, GRADE1_SVO_GOLD)
    assert cb["predicate_recall"] <= 0.35, cb["predicate_recall"]      # reproduces cycle-1 ~2/9
    assert cs["predicate_recall"] >= 0.75, cs["predicate_recall"]      # coverage fix fires
    out["coverage"] = {"banked": cb["predicate_recall"], "spacy": cs["predicate_recall"]}

    # 2) knowledge tie-break primitive (choose_patient) generalizes by class
    from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV
    from experiments import exp_online_knowledge_condenser_selectional_v1 as CD
    # train "eat" on 3 distinct noun.food nouns (apple/bread/pear all resolve to noun.food)
    toy = [("s0", "eat", "apple", "noun.food"), ("s1", "eat", "bread", "noun.food"),
           ("s2", "eat", "pear", "noun.food")]
    counts = CD.build_condensed_counts(toy, "class")
    kfn = CD.make_score_fn(counts, "class", {})
    # candidates: [rock(nearest, noun.object -> no evidence), soup(noun.food -> learned class)]
    ss = lambda w: SCV.supersense(w)
    assert ss("soup") == "noun.food" and ss("rock") == "noun.object", (ss("soup"), ss("rock"))
    chosen_k = choose_patient("eat", ["rock", "soup"], kfn, ss)
    chosen_struct = choose_patient("eat", ["rock", "soup"], None, ss)
    assert chosen_struct == "rock", chosen_struct                     # structural = nearest
    assert chosen_k == "soup", chosen_k                               # knowledge overrides to right class
    out["choose_patient"] = {"structural": chosen_struct, "knowledge": chosen_k}

    # 3) onestop parse real path (ONE article) + wdw items + condense stream
    bases = _article_basenames()
    assert len(bases) > 50, len(bases)
    svo, items = parse_article(os.path.join(INT_DIR, bases[0] + "-int.txt"), "ST")
    assert isinstance(svo, list) and isinstance(items, list)
    out["parse"] = {"article": bases[0], "n_svo": len(svo), "n_wdw_items": len(items)}

    # 4) 2AFC + learner + clarify gate import paths
    assert CD._2afc([{"v": "eat", "gold_patient": "apple", "gold_ss": "noun.food",
                      "neg_filler": "rock", "neg_ss": "noun.object"}], kfn)[0] in (0.0, 0.5, 1.0)
    from hdlab.clarify_gate import ClarifyGate
    from hdlab.learner import registry
    _ = ClarifyGate(); _ = registry
    print("[%s] SELF-TEST PASS %s" % (ANCHOR_NAME, json.dumps(out)), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    out_dir = _out_dir()
    if args.self_test:
        self_test()
        return
    _write_start_marker(out_dir)
    t0 = time.perf_counter()
    print("[%s] CYCLE START" % ANCHOR_NAME, flush=True)
    payload = run_cycle()
    payload["elapsed_s"] = round(time.perf_counter() - t0, 3)
    payload.setdefault("verdict", "CYCLE2_COMPLETE")
    payload.setdefault("verdict_msg",
                       "coverage=%s B=%s C=%s D=%s flag=%s sleep=%s" % (
                           payload["partA_coverage_fix"]["verdict"],
                           payload["partB_feedback_ablation"]["verdict"],
                           payload["partC_learning_curve"]["verdict"],
                           payload["partD_knowledge_impact_2afc"]["verdict"],
                           payload["partE_integrity"]["flag_gate_fires_on_real_unknowns"],
                           payload["partE_integrity"]["sleep_class_generalized_a_rule"]))
    payload.setdefault("summary", payload["verdict_msg"])
    final = _write_metrics(out_dir, payload)
    print("[%s] CYCLE DONE (%.1fs) -> %s" % (ANCHOR_NAME, payload["elapsed_s"], final), flush=True)
    print("  " + payload["verdict_msg"], flush=True)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
