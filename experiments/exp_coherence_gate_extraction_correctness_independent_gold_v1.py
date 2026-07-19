"""COHERENCE-GATE EXTRACTION CORRECTNESS vs INDEPENDENT GROUND TRUTH.

QUESTION (the ONE step toward a TRUE reading-axis chain-grade, per the reader-coupled VET a92fab1d
and the coherence-gate brain-drill a2bd24b6):
Does a brain-faithful COHERENCE-GATE, scored against INDEPENDENT hand-annotated ground truth (NOT the
reader's own self-consistent memberships), RAISE the reader's extraction PRECISION -- i.e. drop the
incoherent WRONG extractions -- versus the un-gated reader, and at what RECALL cost?

WHY THIS IS THE NEEDED STEP (not a rehash of the reader-coupled cell):
  The reader-coupled cell (exp_role_filler_factorization_reader_coupled_cg_v1) had gold = the reader's OWN
  memberships (self-consistent), so extraction-CORRECTNESS was INVISIBLE to the metric and its gate arm was
  NULL (+0.004). The FATAL FLAW was the gold. THIS cell fixes exactly that: INDEPENDENT gold relations,
  hand-annotated by reading the raw McGuffey sentence text WITHOUT consulting the reader output, then the
  gate is scored FOR CORRECTNESS against that independent gold.

INDEPENDENT GROUND TRUTH (the whole point; NON-NEGOTIABLE):
  data/gold_mcguffey_castle_building_svo_v1.json -- single-annotator gold (action, agent, patient) relations
  for lessons L04+L05 ("Castle-Building", one self-contained McGuffey Third Reader narrative, 46 sentences).
  Genuinely independent: annotated from the sentence text, reader output NOT consulted. Semantic
  action-agent-patient standard (documented in the JSON _meta). SINGLE-ANNOTATOR (caveated); full gold +
  full reader output + all matches are dumped to metrics so a VET can re-annotate the same 46 sentences.

THE READER: exp_read_nested_clause_relative_third_reader_v1 (nest ON), run PER-SENTENCE on the slice
  (each sentence is its own passage -> store[sid] gives that sentence's svo tuples with clean provenance).
  Its svo extractions are the noisy ~real-precision output (the wall). We score SVO (action-on-patient)
  relations only -- the dominant, best-defined class (goal/recipient/loc/poss excluded from gold+scoring).

THE UPGRADED COHERENCE-GATE (per brain-drill (5) two-signal design, glass-box, CPU):
  Score 2 -- discrete STRUCTURAL / TAXONOMIC flag (P600-family): reject an extraction whose role/argument
    structure is malformed: verb is a contraction/aux/non-lexical or a mis-tagged adjective; agent is a
    function word OR taxonomically non-animate (an action's agent should be animate); patient is a
    closed-class function word; degenerate self-loop (v==p, a==p). This is the piece the old gate lacked.
  Score 1 -- graded SITUATION-MODEL-CONDITIONED content score (N400/Sentence-Gestalt-family): score each
    surviving candidate's patient against the CURRENT, growing situation-model (reading-order centroid of
    already-ACCEPTED patients for that verb-slot, backed off to a global accepted-patient centroid and a
    selectional verb<->patient association), PRECISION-WEIGHTED by how much context has accumulated
    (early = wide precision, do not punish). NOT the old static per-slot centroid.
  DEFERRED state (the drill's single most important addition over keep/drop): a middle-band candidate is
    neither accepted nor dropped -- it is DEFERRED (held out of the kept set, not counted against precision),
    re-scorable as the foundation grows. Reported explicitly.

ARMS (one variable at a time; SAME reader extractions + SAME independent gold):
  ungated            : the reader's raw svo (REAL baseline; the honest wall against independent gold).
  gated_structural   : Score 2 only (structural/taxonomic flag).
  gated_static_cent  : Score 2 + OLD static per-slot centroid content drop, NO defer (the prior gate design).
  gated_full         : Score 2 + Score 1 situation-model content score + DEFER (the UPGRADED gate).
  good_enough        : gated_full logic but EFFORT-GATED -- the check is skipped (auto-accept) on ~50% of
                       extractions (models the brain's good-enough/Moses-illusion default). FRONTIER-2 probe:
                       always-verify (gated_full) should BEAT good-enough on correctness.

MEASURED (decisive): per arm, PRECISION / RECALL / F1 against INDEPENDENT gold (PRIMARY = (action-lemma,
  patient) sentence-local; SECONDARY = full (action, agent-with-coref, patient) triple). n_kept, n_deferred,
  the precision-recall tradeoff, and a residual-FP error-class breakdown (STRUCTURAL vs COHERENT_BUT_WRONG)
  that localizes what a coherence gate CANNOT fix (coherent-but-wrong parses -> the fix is the parse /
  learned construction-induction, not the gate).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = un-gated reader precision against INDEPENDENT gold, measured (NOT self-consistent).
  (G2) baseline_in_band: 0.05 < ungated primary precision < 0.95 (a real, un-saturated wall).
  (G3) CAN-FAIL-BOTH-WAYS: the gate can RAISE precision (HARD_PASS) OR fail to / over-drop true relations
       (HARD_FAIL) -- both reachable by the metric.
  (G4) discriminator fires: gated_structural or gated_full drops >0 extractions AND the kept set differs
       from ungated (arms must differ).
  (G5) ONE VARIABLE: gate on/off / gate variant; identical reader extractions + identical gold.

VERDICT BANDS (pre-registered; PRIMARY precision):
  HARD_PASS_COHERENCE_GATE_RAISES_CORRECT_COMPREHENSION: gated_full precision >= ungated precision + 0.15
    AND recall retention (gated_full recall / ungated recall) >= 0.70 AND gated_full precision >=
    good_enough precision. => coherence-gating improves correct comprehension = a real step toward a reading-
    axis CG; the OPTIONAL compgen-against-independent-gold is then the milestone.
  HARD_FAIL_ERRORS_NOT_COHERENCE_DETECTABLE: gated_full precision - ungated precision < 0.05 OR recall
    retention < 0.50. => the reader's wrong extractions are coherent-but-wrong (not coherence-detectable) OR
    the gate drops too many TRUE relations => the fix is the learned construction-induction / parse, NOT a
    gate (crucial localization).
  MIDDLE_BAND: partial raise (0.05 <= delta < 0.15) with acceptable recall. => the gate earns a partial
    place (structural garbage is coherence-detectable) but the coherent-but-wrong residual localizes to the
    parser; report the error-class split.

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): the brain gates coherence (N400 graded PE + P600
  structural flag + CI settling) but FAILS ~40-50% (good-enough / Moses illusion) -- so an ALWAYS-VERIFY
  gate may STRUCTURALLY BEAT the brain baseline (Frontier-2; tested via the good_enough arm). WHERE a real
  bound may hit: some reader errors are COHERENT-but-wrong (grammatical-looking action+animate agent+content
  patient that is merely mis-attached, e.g. "began [to sing over his] work" -> began(he, work)); NO
  coherence gate can catch these -- they need the PARSE itself to be correct. Same-limit-as-brain (the
  garden-path lingering-misparse) => accept + localize to the parser; where always-verify beats good-enough
  => Frontier-2 win.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- 46 short sentences, a few
  hundred GloVe cosines; wall < ~60s. Foreground local-to-completion (NO queue; NO push; NO remote-persist).
  Storage: no_storage (this is an extraction-precision measurement, not a superposition/composition cell).
  Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic hashlib; no salted builtin hash / list(set).

CELL-TEMPLATE MANDATORY (subset for a LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (kept-set hashes across arms differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < ungated precision < 0.95)
- discriminator fires at smoke (gate drops >0; kept sets differ)
- scaffold-free witness: a hand-checked WRONG extraction the gate DROPS + a TRUE one it KEEPS
- deterministic seeding; all numbers tagged MEASURED@/CITED@ (MEASURED printed at run)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import gzip
import hashlib
import json
import random
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "coherence_gate_extraction_correctness_independent_gold_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_role_filler_factorization_conceptnet_cg_v1 as FZ  # noqa: E402  (GLOVE_PATH only)

GLOVE_PATH = FZ.GLOVE_PATH
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_castle_building_svo_v1.json")

ARMS = ["ungated", "gated_structural", "gated_static_cent", "gated_full", "good_enough"]

# ----------------------------------------------------------------------------------------------
# Glass-box lexicons (Score 2 structural / taxonomic flag).
# ----------------------------------------------------------------------------------------------
# Closed-class function words that are NOT valid content patients/agents of an action.
FUNCWORD = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "with", "by", "up", "down", "out", "off",
    "over", "into", "onto", "about", "from", "till", "then", "there", "here", "so", "as", "not", "no",
    "and", "but", "or", "if", "when", "that", "this", "these", "those", "very", "just", "only", "all",
    "any", "some", "such", "too", "quite", "now", "again", "back", "away", "much", "more", "most",
}
# Pronouns -- valid patients/agents (throw IT, hurt HER); never structural-dropped as content.
PRONOUN = {"i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "it"}
# Animate nouns (agents of actions are typically animate; P600-style taxonomic flag).
ANIMATE_NOUN = {
    "herbert", "joe", "papa", "hetty", "pussy", "cat", "mamma", "mother", "father", "grandmother",
    "boy", "boys", "girl", "girls", "child", "children", "man", "men", "woman", "women", "people",
    "person", "sister", "brother", "son", "daughter", "baby", "servant", "angel", "angels", "bird",
    "birds", "dog", "dogs", "cows", "sheep", "shepherd", "roy", "johnny", "frank", "rose", "king",
    "queen", "friend", "friends", "family", "teacher", "nurse", "lady", "gentleman",
}
# Mis-tagged non-verbs the reader sometimes heads a relation with (adjectives / quantifiers).
NONVERB = {"sweet", "sorry", "great", "little", "pretty", "dear", "glad", "full", "sure", "ready", "next"}


def is_animate_agent(a):
    return a in PRONOUN or a in ANIMATE_NOUN


def is_content_patient(p):
    return isinstance(p, str) and len(p) >= 2 and p.isalpha() and (p not in FUNCWORD)


# ----------------------------------------------------------------------------------------------
# Verb lemmatizer (shared: applied IDENTICALLY to gold and reader verbs so matching is fair).
# ----------------------------------------------------------------------------------------------
_IRREG = {
    "seen": "see", "saw": "see", "took": "take", "taken": "take", "threw": "throw", "thrown": "throw",
    "held": "hold", "heard": "hear", "left": "leave", "made": "make", "built": "build", "came": "come",
    "went": "go", "fell": "fall", "got": "get", "gotten": "get", "sat": "sit", "stood": "stand",
    "began": "begin", "begun": "begin", "told": "tell", "thought": "think", "caught": "catch",
    "spoke": "speak", "spoken": "speak", "sprang": "spring", "sung": "sing", "sang": "sing",
    "lost": "lose", "did": "do", "done": "do", "had": "have", "was": "be", "were": "be", "is": "be",
    "knew": "know", "known": "know", "bought": "buy", "brought": "bring", "ran": "run", "run": "run",
    "gave": "give", "given": "give", "found": "find", "kept": "keep", "meant": "mean", "read": "read",
}
_DOUBLE = {"rub", "nod", "flit", "knit", "drop", "run", "sit", "begin", "rub"}


def lemma_verb(v):
    """Rule + irregular-map verb lemmatizer; deterministic, ASCII."""
    v = v.lower()
    if "'" in v:  # contraction (won't, can't, sha'n't, didn't) -- kept as-is so Score 2 can flag it.
        return v
    if v in _IRREG:
        return _IRREG[v]
    if v.endswith("ing") and len(v) > 4:
        stem = v[:-3]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]  # rubbing->rub, nodding->nod
        elif stem in ("mak", "tak", "com", "giv", "hav", "writ", "los", "hav"):
            stem = stem + "e"
        return _IRREG.get(stem, stem)
    if v.endswith("ed") and len(v) > 3:
        stem = v[:-2]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]  # rubbed->rub, nodded->nod, flitted->flit
        elif stem.endswith("i"):
            stem = stem[:-1] + "y"  # carried->carry
        return _IRREG.get(stem, stem)
    if v.endswith("s") and len(v) > 3 and not v.endswith("ss"):
        stem = v[:-1]
        if stem.endswith("e") and v[-2] in "sxzo":
            stem = stem[:-1]
        return _IRREG.get(stem, stem)
    return _IRREG.get(v, v)


# ----------------------------------------------------------------------------------------------
# Corpus slice + reader run (per-sentence provenance via store[sid]).
# ----------------------------------------------------------------------------------------------
def split_sents(text):
    t = re.sub(r"\s+", " ", text).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", t) if p.strip()]


def load_slice_and_reader(slice_lessons):
    """Run the REAL reader per-sentence on the slice; return (sent_ids, sent_text, reader_svo per sent)."""
    from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST
    from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2
    les = NEST.load_lessons()
    clf = V2._fit_clf()
    sent_text = {}
    order = []
    for lid in slice_lessons:
        for j, s in enumerate(split_sents(les[lid])):
            sid = f"{lid}_{j:02d}"
            sent_text[sid] = s
            order.append(sid)
    passages = {sid: sent_text[sid] for sid in order}
    store = NEST.read_corpus(clf, passages, nest=True)["store"]
    reader_svo = {}
    for sid in order:
        tups = [(r[1], r[2], r[3]) for r in store.get(sid, []) if r[0] == "svo" and r[1] != "kind"]
        # normalize: lowercase tokens; keep raw verb (contractions preserved for Score 2).
        reader_svo[sid] = [(str(v).lower(), str(a).lower(), str(p).lower()) for (v, a, p) in tups]
    return order, sent_text, reader_svo


def load_gold(slice_lessons):
    with open(GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    gold = {}
    for sid, rels in obj["gold"].items():
        if sid.split("_")[0] in slice_lessons:
            gold[sid] = [{"v": lemma_verb(r["v"]), "agent": r["agent"].lower(),
                          "patient": r["patient"].lower(),
                          "refs": set(x.lower() for x in r.get("refs", [r["agent"]]))} for r in rels]
    return gold, obj["_meta"]


# ----------------------------------------------------------------------------------------------
# GloVe content vectors for the tokens present (Score 1).
# ----------------------------------------------------------------------------------------------
def load_glove_for(tokens):
    want = set(t for t in tokens if t and t.isalpha())
    vec = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            sp = line.split(" ", 1)
            if sp[0] in want:
                vec[sp[0]] = torch.tensor([float(t) for t in sp[1].split()], dtype=torch.float32)
                if len(vec) == len(want):
                    break
    for k in list(vec.keys()):
        vec[k] = vec[k] / torch.clamp(vec[k].norm(), min=1e-8)
    return vec


def cos(a, b):
    if a is None or b is None:
        return None
    return float(torch.dot(a, b))


# ----------------------------------------------------------------------------------------------
# Score 2 -- structural / taxonomic flag. Returns (survives_structural, reason).
# ----------------------------------------------------------------------------------------------
def structural_ok(v, a, p):
    if "'" in v:
        return False, "contraction_nonverb"
    if v in NONVERB:
        return False, "adjective_as_verb"
    if v == p or a == p or v == a:
        return False, "degenerate_selfloop"
    if a in FUNCWORD:
        return False, "agent_funcword"
    if not is_animate_agent(a):
        return False, "agent_inanimate_taxonomic"
    if not is_content_patient(p) and p not in PRONOUN:
        return False, "patient_funcword"
    return True, "ok"


# ----------------------------------------------------------------------------------------------
# The gate. reading-order list of (sid, (v,a,p)). Returns per-arm kept/deferred/dropped decisions.
# ----------------------------------------------------------------------------------------------
def run_gate(order, reader_svo, glove, thr_keep, thr_defer, ctx_k, w_min, static_drop_frac, ge_skip_frac,
             seed):
    """Return dict arm -> dict(kept=[(sid,tup)], deferred=[...], dropped=[(sid,tup,reason)])."""
    rng = random.Random(seed)
    flat = [(sid, tup) for sid in order for tup in reader_svo[sid]]

    # --- structural pass (shared by all gated arms) ---
    struct = {}  # (sid,tup) -> (ok, reason)
    for sid, tup in flat:
        struct[(sid, id(tup))] = structural_ok(*tup)

    def gv(p):
        return glove.get(p)

    # ---- ARM: ungated ----
    kept_ung = list(flat)

    # ---- ARM: gated_structural (Score 2 only) ----
    kept_str, drop_str = [], []
    for sid, tup in flat:
        ok, reason = structural_ok(*tup)
        (kept_str if ok else drop_str).append((sid, tup) if ok else (sid, tup, reason))

    # ---- Score 1 helpers ----
    def content_score(v, p, slot_vecs, global_vecs):
        """Situation-model-conditioned coherence of patient p for verb v. Returns (score, weight)."""
        pv = gv(p)
        if pv is None:
            return None, 0.0  # pronoun / OOV patient -- content score N/A
        if slot_vecs:
            ref = torch.stack(slot_vecs, 0).mean(0)
            n_ctx = len(slot_vecs)
        elif global_vecs:
            ref = torch.stack(global_vecs, 0).mean(0)
            n_ctx = max(1, len(global_vecs) // 4)  # global backoff = weaker context
        else:
            return None, 0.0
        ref = ref / torch.clamp(ref.norm(), min=1e-8)
        sel = gv(v)  # selectional verb<->patient association (backoff signal)
        base = cos(pv, ref)
        if sel is not None:
            base = 0.7 * base + 0.3 * cos(pv, sel)
        w = n_ctx / (n_ctx + ctx_k)
        return base, w

    # ---- ARM: gated_full (Score 2 + Score 1 situation-model + DEFER), reading order ----
    def full_gate(effort_skip):
        slot_vecs = defaultdict(list)
        global_vecs = []
        kept, deferred, dropped = [], [], []
        for sid, tup in flat:
            v, a, p = tup
            if effort_skip and rng.random() < ge_skip_frac:
                kept.append((sid, tup))  # good-enough: skip the check, auto-accept
                continue
            ok, reason = structural_ok(v, a, p)
            if not ok:
                dropped.append((sid, tup, reason)); continue
            sc, w = content_score(v, p, slot_vecs[v], global_vecs)
            if sc is None or w < w_min:
                kept.append((sid, tup))  # not enough context to punish -> accept
                pv = gv(p)
                if pv is not None:
                    slot_vecs[v].append(pv); global_vecs.append(pv)
                continue
            if sc >= thr_keep:
                kept.append((sid, tup)); slot_vecs[v].append(gv(p)); global_vecs.append(gv(p))
            elif sc >= thr_defer:
                deferred.append((sid, tup, round(sc, 3)))  # DEFERRED (held out, re-scorable later)
            else:
                dropped.append((sid, tup, f"content_incoherent_{sc:.2f}"))
        return kept, deferred, dropped

    kept_full, def_full, drop_full = full_gate(effort_skip=False)
    kept_ge, def_ge, drop_ge = full_gate(effort_skip=True)

    # ---- ARM: gated_static_cent (Score 2 + OLD static per-slot centroid, NO defer) ----
    surv = [(sid, tup) for sid, tup in flat if structural_ok(*tup)[0]]
    slot_all = defaultdict(list)
    for sid, tup in surv:
        pv = gv(tup[2])
        if pv is not None:
            slot_all[tup[0]].append(pv)
    scored = []  # (score, sid, tup)
    for sid, tup in surv:
        v, a, p = tup
        pv = gv(p)
        vecs = slot_all[v]
        if pv is None or len(vecs) < 2:
            scored.append((9.0, sid, tup)); continue  # unscorable -> kept
        ref = (torch.stack(vecs, 0).sum(0) - pv) / (len(vecs) - 1)
        ref = ref / torch.clamp(ref.norm(), min=1e-8)
        scored.append((cos(pv, ref), sid, tup))
    real = sorted(s for s, _, _ in scored if s < 8.0)
    thr = real[int(static_drop_frac * len(real))] if real else -9.0
    kept_static, drop_static = [], []
    for s, sid, tup in scored:
        if s >= thr or s >= 8.0:
            kept_static.append((sid, tup))
        else:
            drop_static.append((sid, tup, f"static_cent_{s:.2f}"))

    return {
        "ungated": {"kept": kept_ung, "deferred": [], "dropped": []},
        "gated_structural": {"kept": kept_str, "deferred": [], "dropped": drop_str},
        "gated_static_cent": {"kept": kept_static, "deferred": [], "dropped": drop_static},
        "gated_full": {"kept": kept_full, "deferred": def_full, "dropped": drop_full},
        "good_enough": {"kept": kept_ge, "deferred": def_ge, "dropped": drop_ge},
    }


# ----------------------------------------------------------------------------------------------
# Matching + precision/recall/F1 vs INDEPENDENT gold.
# ----------------------------------------------------------------------------------------------
def match_primary(tup, gold_rels):
    v, a, p = tup
    lv = lemma_verb(v)
    for g in gold_rels:
        if g["v"] == lv and g["patient"] == p:
            return g
    return None


def match_triple(tup, gold_rels):
    v, a, p = tup
    lv = lemma_verb(v)
    for g in gold_rels:
        if g["v"] == lv and g["patient"] == p and (a == g["agent"] or a in g["refs"]):
            return g
    return None


def score_arm(kept, gold, matcher):
    n_gold = sum(len(v) for v in gold.values())
    tp_pred = 0
    covered = set()  # (sid, idx-of-gold)
    kept_by_sid = defaultdict(list)
    for sid, tup in kept:
        kept_by_sid[sid].append(tup)
    for sid, tup in kept:
        grels = gold.get(sid, [])
        g = matcher(tup, grels)
        if g is not None:
            tp_pred += 1
            covered.add((sid, grels.index(g)))
    n_pred = len(kept)
    precision = tp_pred / n_pred if n_pred else 0.0
    recall = len(covered) / n_gold if n_gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "n_pred": n_pred,
            "tp": tp_pred, "n_gold_covered": len(covered), "n_gold": n_gold}


def error_classes(kept, dropped, deferred, gold):
    """Of the KEPT reader tuples that are still WRONG (residual FP under PRIMARY), classify:
    COHERENT_BUT_WRONG (passed the structural/taxonomic flag -- animate agent + content/pronoun patient +
    real verb -- but is mis-attached; NO coherence gate can catch it -> the fix is the PARSE / learned
    construction-induction) vs STRUCTURAL_RESIDUAL (a structurally-flaggable tuple that nonetheless
    survived; should be ~0 for gated_full and >0 for ungated -- a diagnostic that the flag worked)."""
    coherent, structural = [], []
    for sid, tup in kept:
        if match_primary(tup, gold.get(sid, [])) is not None:
            continue  # correct, not an FP
        ok, _ = structural_ok(*tup)
        (coherent if ok else structural).append([sid, list(tup)])
    return {"n_coherent_but_wrong": len(coherent),
            "n_structural_residual": len(structural),
            "coherent_but_wrong_examples": coherent[:20],
            "structural_residual_examples": structural[:8]}


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness: a hand-checked WRONG extraction the gate DROPS + a TRUE one it KEEPS.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness():
    # TRUE (should KEEP): open(he/papa, door) -- L04_11, a correct extraction.
    ok_true, _ = structural_ok("opened", "papa", "door")
    # WRONG structural (should DROP): sat(papa, blocks) -> content oblique; and finished(time, castle)
    #   -> inanimate agent; and can't(i, out) -> contraction+funcword.
    ok_inanim, r_inanim = structural_ok("finished", "time", "castle")
    ok_contr, r_contr = structural_ok("can't", "i", "out")
    ok_selfloop, r_self = structural_ok("build", "down", "build")
    assert ok_true, "witness: gate wrongly REJECTS the true extraction open(papa, door)"
    assert (not ok_inanim) and r_inanim == "agent_inanimate_taxonomic", f"witness: inanimate-agent not flagged ({r_inanim})"
    assert (not ok_contr), "witness: contraction not flagged"
    assert (not ok_selfloop), "witness: self-loop not flagged"
    # verb lemmatizer parity witness (shared normalizer maps reader surface -> gold lemma):
    assert lemma_verb("seen") == "see" and lemma_verb("rubbed") == "rub" and lemma_verb("nodded") == "nod"
    assert lemma_verb("took") == "take" and lemma_verb("knocked") == "knock" and lemma_verb("left") == "leave"
    return {"true_kept": ["opened", "papa", "door"], "wrong_dropped_inanimate": ["finished", "time", "castle"],
            "wrong_dropped_contraction": ["can't", "i", "out"], "wrong_dropped_selfloop": ["build", "down", "build"],
            "lemma_parity": {"seen": "see", "rubbed": "rub", "took": "take", "knocked": "knock"},
            "witness": "PASS"}


# ----------------------------------------------------------------------------------------------
# Config + run.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(slice_lessons=["L04"], thr_keep=0.15, thr_defer=0.03, ctx_k=2.0, w_min=0.34,
               static_drop_frac=0.30, ge_skip_frac=0.5, seed=7)


def cfg_full():
    return dict(slice_lessons=["L04", "L05"], thr_keep=0.15, thr_defer=0.03, ctx_k=2.0, w_min=0.34,
               static_drop_frac=0.30, ge_skip_frac=0.5, seed=7)


def run_config(cfg):
    order, sent_text, reader_svo = load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = load_gold(cfg["slice_lessons"])
    # GloVe for all patient/agent/verb tokens present in reader + gold.
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([v, a, p, lemma_verb(v)])
    for sid, rels in gold.items():
        for g in rels:
            toks.update([g["v"], g["agent"], g["patient"]])
    glove = load_glove_for(toks)

    decisions = run_gate(order, reader_svo, glove, cfg["thr_keep"], cfg["thr_defer"], cfg["ctx_k"],
                         cfg["w_min"], cfg["static_drop_frac"], cfg["ge_skip_frac"], cfg["seed"])

    arm_metrics = {}
    for arm in ARMS:
        kept = decisions[arm]["kept"]
        arm_metrics[arm] = {
            "primary": score_arm(kept, gold, match_primary),
            "triple": score_arm(kept, gold, match_triple),
            "n_kept": len(kept), "n_deferred": len(decisions[arm]["deferred"]),
            "n_dropped": len(decisions[arm]["dropped"]),
        }
    ec = error_classes(decisions["gated_full"]["kept"], decisions["gated_full"]["dropped"],
                       decisions["gated_full"]["deferred"], gold)

    n_reader = sum(len(reader_svo[sid]) for sid in order)
    n_gold = sum(len(v) for v in gold.values())
    meta = {
        "slice_lessons": cfg["slice_lessons"], "n_sentences": len(order),
        "n_reader_svo": n_reader, "n_gold_relations": n_gold,
        "gold_meta": gold_meta,
        "reader_svo_dump": {sid: [list(t) for t in reader_svo[sid]] for sid in order if reader_svo[sid]},
        "gold_dump": {sid: [[g["v"], g["agent"], g["patient"]] for g in gold[sid]]
                      for sid in order if gold.get(sid)},
        "gate_decisions_full": {
            "dropped": [[sid, list(t), r] for (sid, t, r) in decisions["gated_full"]["dropped"]],
            "deferred": [[sid, list(t), s] for (sid, t, s) in decisions["gated_full"]["deferred"]],
        },
        "glove_coverage": round(len(glove) / max(1, len(toks)), 3),
    }
    return arm_metrics, ec, meta, decisions


def kept_hash(decisions, arm):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in decisions[arm]["kept"])
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def build_verdict(arm_metrics):
    ung = arm_metrics["ungated"]["primary"]
    full = arm_metrics["gated_full"]["primary"]
    ge = arm_metrics["good_enough"]["primary"]
    delta = full["precision"] - ung["precision"]
    recall_ret = (full["recall"] / ung["recall"]) if ung["recall"] > 0 else 0.0
    beats_good_enough = full["precision"] >= ge["precision"]
    if delta < 0.05 or recall_ret < 0.50:
        verdict = "HARD_FAIL_ERRORS_NOT_COHERENCE_DETECTABLE"
    elif delta >= 0.15 and recall_ret >= 0.70 and beats_good_enough:
        verdict = "HARD_PASS_COHERENCE_GATE_RAISES_CORRECT_COMPREHENSION"
    else:
        verdict = "MIDDLE_BAND"
    return {"verdict": verdict, "precision_delta_full_vs_ungated": round(delta, 4),
            "recall_retention_full_vs_ungated": round(recall_ret, 4),
            "always_verify_beats_good_enough": bool(beats_good_enough),
            "frontier2_precision_gap_full_minus_goodenough": round(full["precision"] - ge["precision"], 4)}


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data",
                              f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    witness = scaffold_free_witness()
    arm_metrics, ec, meta, decisions = run_config(cfg)
    vd = build_verdict(arm_metrics)

    # arms-differ (kept sets across gated arms must differ from ungated).
    hashes = {arm: kept_hash(decisions, arm) for arm in ARMS}
    assert hashes["gated_full"] != hashes["ungated"], "META_RULE_AF: gated_full kept set == ungated (gate no-op)"
    assert hashes["gated_structural"] != hashes["ungated"], "META_RULE_AF: structural gate no-op"

    # design-gate checks (verified at smoke).
    ung_p = arm_metrics["ungated"]["primary"]["precision"]
    baseline_in_band = bool(0.05 < ung_p < 0.95)
    discriminator_fires = bool(arm_metrics["gated_full"]["n_dropped"] > 0
                               or arm_metrics["gated_full"]["n_deferred"] > 0)

    elapsed = time.perf_counter() - t0
    v = vd["verdict"]
    full = arm_metrics["gated_full"]["primary"]
    strp = arm_metrics["gated_structural"]["primary"]
    stat = arm_metrics["gated_static_cent"]["primary"]
    ge = arm_metrics["good_enough"]["primary"]
    msg = (f"{v} | slice={'+'.join(cfg['slice_lessons'])} sents={meta['n_sentences']} "
           f"reader_svo={meta['n_reader_svo']} gold={meta['n_gold_relations']} "
           f"| UNGATED P={ung_p:.3f} R={arm_metrics['ungated']['primary']['recall']:.3f} "
           f"F1={arm_metrics['ungated']['primary']['f1']:.3f} "
           f"| STRUCT P={strp['precision']:.3f} R={strp['recall']:.3f} "
           f"| STATIC_CENT P={stat['precision']:.3f} R={stat['recall']:.3f} "
           f"| FULL P={full['precision']:.3f} R={full['recall']:.3f} F1={full['f1']:.3f} "
           f"def={arm_metrics['gated_full']['n_deferred']} "
           f"| GOOD_ENOUGH P={ge['precision']:.3f} "
           f"| dP={vd['precision_delta_full_vs_ungated']:+.3f} Rret={vd['recall_retention_full_vs_ungated']:.3f} "
           f"F2gap={vd['frontier2_precision_gap_full_minus_goodenough']:+.3f} "
           f"| coherent_but_wrong={ec['n_coherent_but_wrong']} struct_resid={ec['n_structural_residual']} "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "arm_metrics": arm_metrics, "verdict_detail": vd, "error_classes": ec,
        "kept_hashes": hashes, "arms_differ_verified": True,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "independent_gold_source": ("data/gold_mcguffey_castle_building_svo_v1.json -- single-annotator "
                                    "hand-annotated SVO relations for McGuffey L04+L05 'Castle-Building', "
                                    "annotated from sentence text WITHOUT consulting reader output "
                                    "(genuinely independent of the reader)."),
        "data_meta": meta,
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "verdict_detail", "error_classes",
                            "scaffold_free_witness", "data_meta"],
        "notes": ("Coherence-gate extraction CORRECTNESS vs INDEPENDENT gold. HARD_PASS = gate raises "
                  "primary precision >=+0.15 at >=0.70 recall retention AND beats good-enough (Frontier-2). "
                  "HARD_FAIL = errors not coherence-detectable (coherent-but-wrong -> fix is the parse) OR "
                  "gate over-drops true relations. MIDDLE_BAND = partial. CLAIM-VET-pending; single-annotator "
                  "gold (caveated); compgen-against-independent-gold flagged as next step (slice too small)."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  slice={cfg['slice_lessons']} sents={meta['n_sentences']} reader_svo={meta['n_reader_svo']} "
          f"gold={meta['n_gold_relations']} glove_cov={meta['glove_coverage']}", flush=True)
    for arm in ARMS:
        pm = arm_metrics[arm]["primary"]; tm = arm_metrics[arm]["triple"]
        print(f"  [{arm:>17}] PRIMARY P={pm['precision']:.3f} R={pm['recall']:.3f} F1={pm['f1']:.3f} "
              f"(tp={pm['tp']}/{pm['n_pred']}, gold {pm['n_gold_covered']}/{pm['n_gold']}) "
              f"| TRIPLE P={tm['precision']:.3f} R={tm['recall']:.3f} "
              f"| kept={arm_metrics[arm]['n_kept']} def={arm_metrics[arm]['n_deferred']} "
              f"drop={arm_metrics[arm]['n_dropped']}", flush=True)
    print(f"  [error-classes gated_full residual FP] coherent_but_wrong={ec['n_coherent_but_wrong']} "
          f"structural={ec['n_structural_residual']}", flush=True)
    print(f"    coherent_but_wrong examples (need PARSE fix, not gate): {ec['coherent_but_wrong_examples'][:10]}",
          flush=True)
    print(f"  [gate dropped (gated_full)]: "
          f"{[ [s,t,r] for (s,t,r) in decisions['gated_full']['dropped'][:14] ]}", flush=True)
    print(f"  [gate deferred (gated_full)]: {meta['gate_decisions_full']['deferred'][:8]}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        w = scaffold_free_witness()
        print(f"[{ANCHOR_NAME}] self-test scaffold-free witness: {w}", flush=True)
        cfg = cfg_smoke()
        arm_metrics, ec, meta, decisions = run_config(cfg)
        vd = build_verdict(arm_metrics)
        print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={vd['verdict']} "
              f"UNGATED_P={arm_metrics['ungated']['primary']['precision']:.3f} "
              f"FULL_P={arm_metrics['gated_full']['primary']['precision']:.3f} "
              f"dP={vd['precision_delta_full_vs_ungated']:+.3f} "
              f"reader_svo={meta['n_reader_svo']} gold={meta['n_gold_relations']}", flush=True)
        return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
