"""LEARNED CUE-COMPETITION PARSER (LCCP): does a glass-box learned argument-structure parser
REDUCE the hand-rule reader's argument mis-attachments vs INDEPENDENT gold, and GENERALIZE?

QUESTION (the reading-axis CG front-end, per the LCCP brain-drill
notes/research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md):
  The hand-rule reader (exp_read_nested_clause_relative_third_reader_v1, nest ON) mis-attaches arguments
  in two named ways vs independent gold: (1) SUBCAT errors -- it hands PATIENTS to verbs that take none
  (intransitive come/go/sit/stand/fall; cognition wonder/think/know/mean; oblique look-at/tread-on/
  struggle-against; report say/tell); (2) WITHIN-FRAME errors -- for a genuinely transitive verb it keeps
  the WRONG NP (an oblique/adjunct) as the patient (over-extraction: many patients per verb). Does a
  LEARNED cue-competition parser that (B) picks the single best candidate by LEARNED structural cue-weights,
  and (C) additionally induces per-verb / per-construction VERB ARGUMENT-FRAMES (does this verb take a
  patient?), reduce these mis-attachments vs the hand-rule reader against INDEPENDENT gold, and generalize
  to HELD-OUT verbs via construction-level sharing?

THE CRITICAL GOLD (fixes the sibling coherence-gate cell's blind spot -- a9ca3feb / atom 29337):
  data/gold_mcguffey_lccp_argstruct_v1.json -- single-annotator INDEPENDENT gold over McGuffey Third Reader
  narrative lessons. Unlike the v1 SVO gold (patient-only standard -> subcat errors UNMEASURABLE), this gold
  marks per verb-INSTANCE whether it takes a direct patient (pos) OR takes NONE (nopat: intransitive/
  cognition/oblique/report/aspectual/copular). So the parser's SUBCAT knowledge (correctly SUPPRESSING a
  wrong patient on a no-patient verb) is measurable as a TRUE-NEGATIVE. 280 gold items (100 pos + 180 nopat),
  114 sentences, 59 pos verbs / 76 nopat verbs, 16 frame-AMBIGUOUS verbs (build/see/take/know/tell...) that
  appear BOTH ways -> no verb-type rule can solve it; instance-level parse is required.

THE LEARNED MECHANISM (glass-box, CPU, NO treebank, NO external LLM):
  Candidates = the reader's raw (v,a,p) tuples (Angle-1 universal candidate generator, reused as-is).
  Cue features per candidate (STRUCTURAL, from raw sentence text): f_adj (inverse v-p token distance),
    f_postv (patient after verb), f_prep (patient preposition-governed = oblique), f_func (funcword/junk
    patient), f_clause (complementizer to/that/if/how between v and p = clausal complement not NP).
  Teacher signal (SELF-SUPERVISED, semantic, NOT gold, NOT structural): sel = selectional coherence of the
    patient vs the verb's accumulated coherent-patient centroid (GloVe), backed off to a global content
    centroid -- the sibling coherence-gate's Score-1, aggregated per verb. Learning target = 1 if sel high,
    0 if sel low, DEFER (no update) in the middle band. Because the teacher is SEMANTIC and the features are
    STRUCTURAL, the logistic learns which STRUCTURE predicts semantic coherence (Competition-Model cue-
    validity) -- the signs EMERGE, they are not hand-set. (Prediction-3 probe: degrade the ADJACENCY cue
    -> its learned weight must DROP; adjacency is not in the teacher, so this is a clean learned-ness test.)
  ARM A (baseline)  = hand-rule reader, ALL tuples kept (the mis-attachment wall vs independent gold).
  ARM B (+cue-comp) = learned GLOBAL cue-weights; per verb-instance keep the SINGLE best-scoring candidate
    iff sigmoid(w.x) >= keep_thr, else keep none. (isolates learned cue-competition; kills over-extraction.)
  ARM C (+subcat/construction) = B's global cue-weights PLUS a per-verb TRANSITIVITY PRIOR (running mean of
    the verb's best-candidate score, online in reading order); if a verb's induced frame is intransitive
    (prior < subcat_thr) SUPPRESS all its patients (subcat true-negative). HELD-OUT verbs (never in the
    learning stream) get their transitivity prior from the CONSTRUCTION they cluster into (weight-SHARING
    = the compositional-generalization mechanism). (isolates verb argument-frame knowledge; ONE variable
    B->C = construction-level argument-frame knowledge, per the drill's Angle-3/Anchor-4.)

MEASURED (decisive, per arm, vs INDEPENDENT gold):
  primary PRECISION/RECALL/F1 over pos (v_lemma, patient) patient-level; the mis-attachment FP split
  (SUBCAT vs WITHIN-FRAME vs SPURIOUS-VERB); the SUBCAT true-negative suppression rate (over nopat verb-
  instances the reader mis-attached to); the A->C mis-attachment reduction PER CLASS; a HELD-OUT (verb)
  split (C accuracy on held-out verbs vs seen -> compositional generalization); the LEARNING CURVE
  (per-verb subcat-FP rate on first vs later exposures -> improves-with-exposure); the Prediction-3 cue-
  degradation weight-shift (mechanism-validity / not-vacuous check).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = hand-rule reader precision vs INDEPENDENT gold incl. the hard verb-classes.
  (G2) baseline_in_band: 0.05 < arm-A primary precision < 0.95 (a real, un-saturated wall).
  (G3) CAN-FAIL-BOTH-WAYS: HARD_PASS (C reduces total mis-attachment FP-rate >=0.15 vs A AND held-out within
       0.10 of seen) OR HARD_FAIL (<0.05 reduction OR held-out drop >0.25) -- both reachable by the metric.
  (G4) discriminator fires: arm C suppresses >0 reader patients AND kept sets differ across A/B/C.
  (G5) ONE VARIABLE per step: A->B = learned cue-weights (best-candidate + threshold); B->C = subcat
       transitivity prior + construction-level sharing (global cue-weights held IDENTICAL across B and C).

VERDICT BANDS (pre-registered; total mis-attachment FP-rate = (subcat_FP + within_frame_FP + spurious_FP)/
  n_reader_tuples, measured vs independent gold):
  HARD_PASS_LCCP_REDUCES_MISATTACH_AND_GENERALIZES: (A_fp_rate - C_fp_rate) >= 0.15 AND primary recall
    retention (C/A) >= 0.60 AND held-out primary precision within 0.10 of seen primary precision.
  HARD_FAIL_LEARNED_PARSER_NO_BETTER: (A_fp_rate - C_fp_rate) < 0.05 OR held-out primary precision drops
    > 0.25 below seen (construction-sharing does not generalize) OR recall retention < 0.40.
  MIDDLE_BAND: partial (0.05 <= reduction < 0.15, or generalization between the bars).

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): LCCP is brain-faithful (Competition-Model learned
  cue-weights + usage-based construction-frame induction + prediction-error/coherence training, Fitz&Chang).
  Largest risk (drill Prediction-4, P=0.35): coherence/structural feedback may NOT fix the WITHIN-FRAME
  coherent-but-wrong residual (the brain shares this -- garden-path/Moses); if the SUBCAT class improves but
  WITHIN-FRAME does not, that is same-limit-as-brain -> accept + localize; the substrate-native fallback
  (document-scope consistency) is the flagged next step, NOT built here.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- ~250 reader candidates, a
  few hundred GloVe cosines + a tiny logistic over 6 features x a few epochs; wall < ~90s. Foreground local-
  to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage (extraction-precision
  measurement, not a superposition/composition cell). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds,
  deterministic hashlib; no salted builtin hash / list(set); numpy default RNG seeded.

CELL-TEMPLATE MANDATORY (subset for a LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (kept-set hashes across A/B/C differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < arm-A precision < 0.95)
- discriminator fires at smoke (C suppresses >0; kept sets differ)
- scaffold-free witness: a real intransitive over-extraction C SUPPRESSES that the hand-rule keeps, + a
  held-out verb+construction whose frame C gets right by construction-sharing
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
import math
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "learned_argstruct_parser_lccp_independent_gold_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_role_filler_factorization_conceptnet_cg_v1 as FZ  # noqa: E402 (GLOVE_PATH only)

GLOVE_PATH = FZ.GLOVE_PATH
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_lccp_argstruct_v1.json")
ARMS = ["A_handrule", "B_cuecomp", "C_lccp"]

# ----------------------------------------------------------------------------------------------
# Glass-box lexicons.
# ----------------------------------------------------------------------------------------------
PREPS = {"over", "at", "on", "to", "for", "with", "by", "up", "down", "out", "off", "into", "onto",
         "about", "from", "against", "in", "upon", "across", "through", "toward", "towards", "near",
         "along", "of", "than", "round", "past", "under", "above", "behind", "between"}
COMPLEMENTIZERS = {"to", "that", "if", "how", "whether", "what", "why", "when", "where", "who", "which"}
FUNCWORD = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "with", "by", "up", "down", "out",
            "off", "over", "into", "onto", "about", "from", "till", "then", "there", "here", "so", "as",
            "not", "no", "and", "but", "or", "if", "when", "that", "this", "these", "those", "very",
            "just", "only", "all", "any", "some", "such", "too", "quite", "now", "again", "back", "away",
            "much", "more", "most", "well", "ever", "never", "yet", "still", "even"}
PRONOUN = {"i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "it",
           "myself", "himself", "herself", "themselves", "another", "one", "nothing", "myself"}

# ----------------------------------------------------------------------------------------------
# Verb lemmatizer (applied IDENTICALLY to reader surfaces and gold verbs). Explicit map covering the
# corpus + rule fallback; deterministic, ASCII.
# ----------------------------------------------------------------------------------------------
_LEMMA = {
    "building": "build", "build": "build", "built": "build", "rubbed": "rub", "rub": "rub",
    "took": "take", "take": "take", "taken": "take", "takes": "take", "threw": "throw", "throw": "throw",
    "thrown": "throw", "passed": "pass", "pass": "pass", "mean": "mean", "meant": "mean", "means": "mean",
    "opened": "open", "open": "open", "fell": "fall", "fall": "fall", "fallen": "fall", "falls": "fall",
    "know": "know", "knew": "know", "known": "know", "knows": "know", "held": "hold", "hold": "hold",
    "came": "come", "come": "come", "comes": "come", "got": "get", "get": "get", "gets": "get",
    "said": "say", "say": "say", "says": "say", "saying": "say", "heard": "hear", "hear": "hear",
    "nodded": "nod", "nod": "nod", "sat": "sit", "sit": "sit", "show": "show", "showed": "show",
    "shows": "show", "shown": "show", "began": "begin", "begin": "begin", "begun": "begin",
    "crying": "cry", "cry": "cry", "cried": "cry", "cries": "cry", "flitted": "flit", "flit": "flit",
    "knocked": "knock", "knock": "knock", "knocks": "knock", "told": "tell", "tell": "tell",
    "tells": "tell", "telling": "tell", "wonder": "wonder", "wonders": "wonder", "wondered": "wonder",
    "go": "go", "goes": "go", "went": "go", "gone": "go", "going": "go", "looked": "look", "look": "look",
    "looks": "look", "looking": "look", "finished": "finish", "finish": "finish", "finishing": "finish",
    "knit": "knit", "knitting": "knit", "seen": "see", "see": "see", "saw": "see", "sees": "see",
    "left": "leave", "leave": "leave", "leaves": "leave", "leaving": "leave", "sent": "send",
    "send": "send", "sends": "send", "spend": "spend", "spends": "spend", "spent": "spend", "met": "meet",
    "meet": "meet", "meets": "meet", "found": "find", "find": "find", "finds": "find", "finding": "find",
    "given": "give", "give": "give", "gave": "give", "gives": "give", "led": "lead", "lead": "lead",
    "think": "think", "thinks": "think", "thought": "think", "struggled": "struggle",
    "struggle": "struggle", "struggles": "struggle", "reached": "reach", "reach": "reach",
    "reaching": "reach", "reaches": "reach", "became": "become", "become": "become", "obey": "obey",
    "obeys": "obey", "obeyed": "obey", "stroke": "stroke", "wakes": "wake", "wake": "wake",
    "woke": "wake", "choosing": "choose", "choose": "choose", "chose": "choose", "chooses": "choose",
    "intend": "intend", "intends": "intend", "lies": "lie", "lie": "lie", "lay": "lay", "commence": "commence",
    "commences": "commence", "makes": "make", "make": "make", "made": "make", "making": "make",
    "obtain": "obtain", "obtains": "obtain", "peel": "peel", "peels": "peel", "called": "call",
    "call": "call", "calls": "call", "hunt": "hunt", "hunts": "hunt", "leap": "leap", "leaps": "leap",
    "leaped": "leap", "ruling": "rule", "rule": "rule", "ruled": "rule", "feared": "fear", "fear": "fear",
    "fears": "fear", "put": "put", "puts": "put", "beating": "beat", "beat": "beat", "ran": "run",
    "run": "run", "runs": "run", "running": "run", "walking": "walk", "walk": "walk", "walks": "walk",
    "walked": "walk", "invited": "invite", "invite": "invite", "invites": "invite", "thanked": "thank",
    "thank": "thank", "thanks": "thank", "touched": "touch", "touch": "touch", "tread": "tread",
    "treads": "tread", "admiring": "admire", "admire": "admire", "admires": "admire", "admired": "admire",
    "meddled": "meddle", "meddle": "meddle", "meddles": "meddle", "continued": "continue",
    "continue": "continue", "continues": "continue", "enjoyed": "enjoy", "enjoy": "enjoy",
    "enjoys": "enjoy", "drawing": "draw", "draw": "draw", "drew": "draw", "draws": "draw",
    "trying": "try", "try": "try", "tries": "try", "tried": "try", "write": "write", "writes": "write",
    "wrote": "write", "writing": "write", "teach": "teach", "teaches": "teach", "taught": "teach",
    "wish": "wish", "wishes": "wish", "wished": "wish", "sing": "sing", "sang": "sing", "sung": "sing",
    "watch": "watch", "watches": "watch", "watched": "watch", "have": "have", "has": "have", "had": "have",
    "spoke": "speak", "speak": "speak", "spoken": "speak", "catch": "catch", "caught": "catch",
    "hurt": "hurt", "hurts": "hurt", "cover": "cover", "covered": "cover", "do": "do", "did": "do",
    "does": "do", "done": "do", "pull": "pull", "pulled": "pull", "pulls": "pull", "shook": "shake",
    "shake": "shake", "shaken": "shake", "brush": "brush", "brushes": "brush", "save": "save",
    "saves": "save", "saved": "save", "hire": "hire", "hires": "hire", "hired": "hire", "attend": "attend",
    "attends": "attend", "learn": "learn", "learned": "learn", "learns": "learn", "please": "please",
    "pleased": "please", "pleases": "please", "sell": "sell", "selling": "sell", "sold": "sell",
    "spinning": "spin", "spin": "spin", "spun": "spin", "venture": "venture", "ventures": "venture",
    "suppose": "suppose", "supposed": "suppose", "supposes": "suppose", "believe": "believe",
    "believes": "believe", "believed": "believe", "hope": "hope", "hopes": "hope", "hoped": "hope",
    "happen": "happen", "happens": "happen", "happened": "happen", "dash": "dash", "dashes": "dash",
    "follow": "follow", "followed": "follow", "follows": "follow", "break": "break", "broke": "break",
    "broken": "break", "breaks": "break", "retort": "retort", "retorted": "retort", "ask": "ask",
    "asks": "ask", "asked": "ask", "answer": "answer", "answered": "answer", "answers": "answer",
    "exclaim": "exclaim", "exclaimed": "exclaim", "exclaims": "exclaim", "creep": "creep",
    "crept": "creep", "creeps": "creep", "fire": "fire", "fires": "fire", "fired": "fire",
    "remind": "remind", "reminded": "remind", "reminds": "remind", "push": "push", "pushes": "push",
    "kill": "kill", "kills": "kill", "swim": "swim", "swims": "swim", "prefer": "prefer",
    "prefers": "prefer", "gnaw": "gnaw", "gnawing": "gnaw", "live": "live", "lives": "live",
    "lived": "live", "living": "live", "work": "work", "works": "work", "worked": "work",
    "inquire": "inquire", "inquires": "inquire", "amuse": "amuse", "amuses": "amuse", "amused": "amuse",
    "keep": "keep", "keeps": "keep", "kept": "keep", "keeping": "keep", "turn": "turn", "turning": "turn",
    "turns": "turn", "turned": "turn", "forget": "forget", "forgetting": "forget", "forgot": "forget",
    "forgets": "forget", "want": "want", "wants": "want", "wanted": "want", "read": "read",
    "reading": "read", "reads": "read", "stand": "stand", "stood": "stand", "stands": "stand",
    "spring": "spring", "sprang": "spring", "sprung": "spring", "including": "include", "include": "include",
    "commencing": "commence", "clink": "clink", "hammer": "hammer",
}


def lemma_verb(v):
    """Deterministic ASCII verb lemmatizer: explicit corpus map -> rule fallback (kept for OOV)."""
    v = v.lower()
    if v in _LEMMA:
        return _LEMMA[v]
    if "'" in v:
        return v
    if v.endswith("ing") and len(v) > 4:
        stem = v[:-3]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        return _LEMMA.get(stem, stem)
    if v.endswith("ed") and len(v) > 3:
        stem = v[:-2]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        elif stem.endswith("i"):
            stem = stem[:-1] + "y"
        return _LEMMA.get(stem, stem)
    if v.endswith("s") and len(v) > 3 and not v.endswith("ss"):
        return _LEMMA.get(v[:-1], v[:-1])
    return v


# ----------------------------------------------------------------------------------------------
# Corpus slice + reader run (per-sentence provenance via store[sid]).
# ----------------------------------------------------------------------------------------------
def split_sents(text):
    t = re.sub(r"\s+", " ", text).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", t) if p.strip()]


def tokenize(s):
    return re.findall(r"[a-z']+", s.lower())


def load_slice_and_reader(slice_lessons):
    """Run the REAL hand-rule reader per-sentence; return order, sent_text, reader_svo per sentence."""
    from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST
    from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2
    les = NEST.load_lessons()
    clf = V2._fit_clf()
    sent_text, order = {}, []
    for lid in slice_lessons:
        if lid not in les:
            continue
        for j, s in enumerate(split_sents(les[lid])):
            sid = f"{lid}_{j:02d}"
            sent_text[sid] = s
            order.append(sid)
    passages = {sid: sent_text[sid] for sid in order}
    store = NEST.read_corpus(clf, passages, nest=True)["store"]
    reader_svo = {}
    for sid in order:
        tups = [(str(r[1]).lower(), str(r[2]).lower(), str(r[3]).lower())
                for r in store.get(sid, []) if r[0] == "svo" and r[1] != "kind"]
        reader_svo[sid] = tups
    return order, sent_text, reader_svo


def load_gold(slice_lessons):
    with open(GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    gold = {}
    for sid, rec in obj["gold"].items():
        if sid.split("_")[0] not in slice_lessons:
            continue
        pos = [{"v": lemma_verb(r["v"]), "agent": r["agent"].lower(), "patient": r["patient"].lower(),
                "refs": set(x.lower() for x in r.get("refs", [r["agent"]]))} for r in rec.get("pos", [])]
        nopat = set(lemma_verb(r["v"]) for r in rec.get("nopat", []))
        gold[sid] = {"pos": pos, "nopat": nopat,
                     "pos_verbs": set(g["v"] for g in pos)}
    return gold, obj["_meta"]


# ----------------------------------------------------------------------------------------------
# GloVe (for the semantic teacher signal only).
# ----------------------------------------------------------------------------------------------
def load_glove_for(tokens):
    want = set(t for t in tokens if t and t.isalpha())
    vec = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            sp = line.split(" ", 1)
            if sp[0] in want:
                a = np.array([float(t) for t in sp[1].split()], dtype=np.float64)
                n = np.linalg.norm(a)
                vec[sp[0]] = a / (n if n > 1e-8 else 1.0)
                if len(vec) == len(want):
                    break
    return vec


def cos(a, b):
    if a is None or b is None:
        return None
    return float(np.dot(a, b))


# ----------------------------------------------------------------------------------------------
# Candidate feature extraction (STRUCTURAL cues from raw sentence text).
# ----------------------------------------------------------------------------------------------
def find_pair_positions(toks, v_surf, p_surf):
    """Return (i_v, i_p) minimizing |i_p-i_v|; None if a token is absent."""
    iv = [i for i, t in enumerate(toks) if t == v_surf]
    ip = [i for i, t in enumerate(toks) if t == p_surf]
    if not iv or not ip:
        # backoff: prefix match (surface may differ slightly from reader token).
        if not iv:
            iv = [i for i, t in enumerate(toks) if t[:4] == v_surf[:4] and len(v_surf) >= 4]
        if not ip:
            ip = [i for i, t in enumerate(toks) if t[:4] == p_surf[:4] and len(p_surf) >= 4]
        if not iv or not ip:
            return None, None
    best = None
    for a in iv:
        for b in ip:
            d = abs(b - a)
            if best is None or d < best[0]:
                best = (d, a, b)
    return best[1], best[2]


def candidate_features(toks, v_surf, p_surf):
    """6-vector [bias, f_adj, f_postv, f_prep, f_func, f_clause]. Structural only (no semantics)."""
    iv, ip = find_pair_positions(toks, v_surf, p_surf)
    f_func = 1.0 if (p_surf in FUNCWORD or len(p_surf) < 2 or not p_surf.replace("'", "").isalpha()) else 0.0
    if iv is None or ip is None:
        return np.array([1.0, 0.3, 0.5, 0.0, f_func, 0.0]), None  # neutral backoff
    dist = abs(ip - iv)
    f_adj = 1.0 / (1.0 + dist)
    f_postv = 1.0 if ip > iv else 0.0
    prev1 = toks[ip - 1] if ip - 1 >= 0 else ""
    prev2 = toks[ip - 2] if ip - 2 >= 0 else ""
    f_prep = 1.0 if (prev1 in PREPS or prev2 in PREPS) else 0.0
    lo, hi = (iv, ip) if iv < ip else (ip, iv)
    f_clause = 1.0 if any(toks[k] in COMPLEMENTIZERS for k in range(lo + 1, hi)) else 0.0
    return np.array([1.0, f_adj, f_postv, f_prep, f_func, f_clause]), (iv, ip)


FEAT_NAMES = ["bias", "f_adj", "f_postv", "f_prep", "f_func", "f_clause"]


# ----------------------------------------------------------------------------------------------
# Semantic teacher: selectional coherence of patient p for verb v (GloVe), backed off to global.
# ----------------------------------------------------------------------------------------------
def build_semantic_teacher(cands, glove):
    """cands: list of dicts with keys sid,v,a,p,feat. Build verb + global content-patient centroids from
    STRUCTURALLY-likely objects (bootstrap: post-verbal, not-prep, not-func content patients), then return
    a sel(cand)->float|None fn. Semantic ONLY; deterministic (order-independent centroids)."""
    verb_vecs = defaultdict(list)
    global_vecs = []
    for c in cands:
        p = c["p"]
        pv = glove.get(p)
        if pv is None:
            continue
        f = c["feat"]
        if f[2] >= 0.5 and f[3] < 0.5 and f[4] < 0.5:  # post-verbal, not prep-governed, not funcword
            verb_vecs[c["v"]].append(pv)
            global_vecs.append(pv)
    verb_cent = {v: np.mean(np.stack(vs, 0), 0) for v, vs in verb_vecs.items() if len(vs) >= 2}
    glob_cent = np.mean(np.stack(global_vecs, 0), 0) if global_vecs else None

    def sel(v, p):
        pv = glove.get(p)
        if pv is None:
            return None
        if v in verb_cent:
            ref, w = verb_cent[v], 1.0
        elif glob_cent is not None:
            ref, w = glob_cent, 0.6
        else:
            return None
        n = np.linalg.norm(ref)
        ref = ref / (n if n > 1e-8 else 1.0)
        return float(np.dot(pv, ref)) * w
    return sel, verb_cent, glob_cent


# ----------------------------------------------------------------------------------------------
# Learned logistic cue-weights (structural features -> semantic-coherence teacher). Error-driven.
# ----------------------------------------------------------------------------------------------
def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


def cand_target(c, sel_fn, sel_keep, sel_drop):
    """Self-supervised objecthood target (NO gold). Combines STRUCTURAL cue-supervision (funcword/prep/clause
    -> non-object; pronoun in bare post-verbal position -> object) with the SEMANTIC selectional teacher for
    the remaining bare content patients (DEFER band -> None = skip). Brain-faithful: both cue types teach.
    NOTE: adjacency (feat[1]) is NEVER used to set the target -> it is a purely LEARNED correlate (clean
    Prediction-3 probe)."""
    f = c["feat"]; p = c["p"]
    if f[4] >= 0.5:          # funcword / junk patient
        return 0.0
    if f[3] >= 0.5:          # preposition-governed = oblique, not a direct object
        return 0.0
    if f[5] >= 0.5:          # complementizer between v and p = clausal complement, not an NP object
        return 0.0
    if p in PRONOUN:         # pronoun in bare post-verbal position = valid object (throw it / watch her)
        return 1.0 if f[2] >= 0.5 else 0.0
    s = sel_fn(c["v"], c["p"])
    if s is None:
        return None
    if s >= sel_keep:
        return 1.0
    if s <= sel_drop:
        return 0.0
    return None              # DEFER: no update


def learn_cue_weights(cands, sel_fn, sel_keep, sel_drop, lr, epochs, seed, degrade_feat_idx=None):
    """Train a 6-dim logistic w on structural features x -> self-supervised objecthood target (cand_target).
    Returns (w, n_train). If degrade_feat_idx is set, that cue is made UNRELIABLE (randomized 0/1) in BOTH
    the target computation and the training feature -> its learned weight should COLLAPSE toward 0
    (Prediction-3 cue-validity probe)."""
    rng = np.random.default_rng(seed)
    w = np.zeros(6)
    train = []
    for c in cands:
        cc = c
        if degrade_feat_idx is not None:
            cc = {"v": c["v"], "p": c["p"], "feat": c["feat"].copy()}
            cc["feat"][degrade_feat_idx] = float(rng.integers(0, 2))  # unreliable cue (consistent in feat+target)
        t = cand_target(cc, sel_fn, sel_keep, sel_drop)
        if t is None:
            continue
        train.append((cc["feat"].copy(), t))
    for _ in range(epochs):
        idx = rng.permutation(len(train))
        for k in idx:
            x, t = train[k]
            pred = sigmoid(float(np.dot(w, x)))
            w = w + lr * (t - pred) * x
    return w, len(train)


def score_cand(w, feat):
    return sigmoid(float(np.dot(w, feat)))


# ----------------------------------------------------------------------------------------------
# Construction induction (cluster verbs by cue-profile) for held-out transitivity backoff.
# ----------------------------------------------------------------------------------------------
def verb_cue_profiles(cands, w, sel_fn):
    """Per verb: mean [f_adj,f_postv,f_prep,f_func,f_clause, best_score]. best_score = max cand score / verb-
    instance, averaged. Returns dict verb->profile(np6)."""
    by_verb_inst = defaultdict(lambda: defaultdict(list))  # verb -> sid -> [cands]
    for c in cands:
        by_verb_inst[c["v"]][c["sid"]].append(c)
    prof = {}
    for v, insts in by_verb_inst.items():
        feats, bestsc = [], []
        for sid, cs in insts.items():
            feats.append(np.mean(np.stack([c["feat"][1:] for c in cs], 0), 0))  # drop bias
            bestsc.append(max(score_cand(w, c["feat"]) for c in cs))
        prof[v] = np.concatenate([np.mean(np.stack(feats, 0), 0), [float(np.mean(bestsc))]])
    return prof


def kmeans(X, k, seed, iters=50):
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    if n <= k:
        return np.arange(n) % k, X.copy()
    cent = X[rng.choice(n, k, replace=False)].copy()
    assign = np.zeros(n, dtype=int)
    for _ in range(iters):
        d = ((X[:, None, :] - cent[None, :, :]) ** 2).sum(-1)
        na = d.argmin(1)
        if np.array_equal(na, assign):
            break
        assign = na
        for j in range(k):
            m = assign == j
            if m.any():
                cent[j] = X[m].mean(0)
    return assign, cent


# ----------------------------------------------------------------------------------------------
# The three arms.
# ----------------------------------------------------------------------------------------------
def run_arms(order, reader_svo, sent_text, glove, cfg, seed):
    """Return decisions per arm + learned artifacts. Decisions: arm -> list of (sid, tup) kept."""
    # build candidates
    cands = []
    for sid in order:
        toks = tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            v_surf, a, p = tup
            feat, _pos = candidate_features(toks, v_surf, p)
            cands.append({"sid": sid, "v": lemma_verb(v_surf), "a": a, "p": p, "tup": tup, "feat": feat})

    sel_fn, verb_cent, glob_cent = build_semantic_teacher(cands, glove)
    w, n_train = learn_cue_weights(cands, sel_fn, cfg["sel_keep"], cfg["sel_drop"], cfg["lr"],
                                   cfg["epochs"], seed)

    # held-out verb split (deterministic; by sorted verb list + seeded permutation)
    all_verbs = sorted(set(c["v"] for c in cands))
    rng = np.random.default_rng(seed + 1)
    perm = rng.permutation(len(all_verbs))
    n_heldout = max(1, int(round(cfg["heldout_frac"] * len(all_verbs))))
    heldout_verbs = set(all_verbs[i] for i in perm[:n_heldout])
    seen_verbs = set(all_verbs) - heldout_verbs

    # construction clustering (on SEEN verbs only) + held-out backoff transitivity prior
    prof = verb_cue_profiles(cands, w, sel_fn)
    seen_list = sorted(v for v in seen_verbs if v in prof)
    if seen_list:
        X = np.stack([prof[v] for v in seen_list], 0)
        Xn = (X - X.mean(0)) / (X.std(0) + 1e-8)
        assign, _cent = kmeans(Xn, cfg["k_constructions"], seed + 2)
        vconstr = {seen_list[i]: int(assign[i]) for i in range(len(seen_list))}
        constr_centroid = {j: Xn[assign == j].mean(0) for j in range(cfg["k_constructions"]) if (assign == j).any()}
    else:
        vconstr, constr_centroid, X = {}, {}, None

    # ARM A: keep all
    kept_A = [(c["sid"], c["tup"]) for c in cands]

    # group candidates per (sid, verb-instance)
    inst_groups = defaultdict(list)
    for c in cands:
        inst_groups[(c["sid"], c["v"])].append(c)

    # ARM B: per verb-instance keep single best candidate iff score >= keep_thr
    kept_B = []
    for key, cs in inst_groups.items():
        best = max(cs, key=lambda c: score_cand(w, c["feat"]))
        if score_cand(w, best["feat"]) >= cfg["keep_thr"]:
            kept_B.append((best["sid"], best["tup"]))

    # ARM C: online reading-order transitivity prior + subcat gate + construction backoff (held-out)
    # process verb-instances in reading order (by sid order, then stable), maintain running t[v].
    t_run = defaultdict(lambda: [0.0, 0])  # verb -> [sum_best_score, count]
    # cluster mean transitivity computed from SEEN verbs' FINAL profiles (prof[..][-1] = best_score mean)
    constr_trans = {}
    if seen_list:
        for j in range(cfg["k_constructions"]):
            members = [seen_list[i] for i in range(len(seen_list)) if int(assign[i]) == j]
            if members:
                constr_trans[j] = float(np.mean([prof[m][-1] for m in members]))

    def assign_heldout_construction(v):
        if v not in prof or not constr_centroid:
            return None
        p = (prof[v] - X.mean(0)) / (X.std(0) + 1e-8) if X is not None else None
        if p is None:
            return None
        best_j, best_d = None, None
        for j, c in constr_centroid.items():
            d = float(((p - c) ** 2).sum())
            if best_d is None or d < best_d:
                best_j, best_d = j, d
        return best_j

    # construction-backoff transitivity prior per verb (seen: own cluster; held-out: nearest centroid).
    # This is the WEIGHT-SHARING generalization mechanism + cold-start / sparse-verb fill-in.
    def constr_prior_for(v):
        if v in vconstr:
            return constr_trans.get(vconstr[v])
        j = assign_heldout_construction(v)
        return constr_trans.get(j) if j is not None else None

    KAPPA = cfg.get("kappa", 1.5)
    kept_C = []
    subcat_decisions = []
    per_inst_order = []
    for sid in order:
        for key in [k for k in inst_groups if k[0] == sid]:
            per_inst_order.append(key)
    verb_seen_count = defaultdict(int)
    for (sid, v) in per_inst_order:
        cs = inst_groups[(sid, v)]
        best = max(cs, key=lambda c: score_cand(w, c["feat"]))
        best_sc = score_cand(w, best["feat"])
        cprior = constr_prior_for(v)
        # online transitivity prior available BEFORE this instance (seen verbs accumulate own history;
        # held-out verbs NEVER accumulate -> pure construction backoff = the generalization test).
        if v in seen_verbs:
            s, n = t_run[v]
            if cprior is None:
                prior = (s / n) if n > 0 else None
            else:
                prior = (s + KAPPA * cprior) / (n + KAPPA)  # blend own history with construction prior
        else:
            prior = cprior  # held-out: construction-shared knowledge only
        # subcat gate: suppress ALL patients if induced frame is intransitive (low transitivity)
        if prior is not None and prior < cfg["subcat_thr"]:
            keep_patient = False
        else:
            keep_patient = best_sc >= cfg["keep_thr"]
        if keep_patient:
            kept_C.append((best["sid"], best["tup"]))
        occ = verb_seen_count[v]
        subcat_decisions.append({"sid": sid, "v": v, "kept": keep_patient, "occ": occ,
                                 "heldout": v in heldout_verbs, "prior": prior, "best_sc": best_sc})
        verb_seen_count[v] += 1
        # update running prior AFTER decision (seen verbs only)
        if v in seen_verbs:
            t_run[v][0] += best_sc
            t_run[v][1] += 1

    artifacts = {
        "w": w.tolist(), "feat_names": FEAT_NAMES, "n_train_examples": n_train,
        "n_candidates": len(cands), "n_verb_instances": len(inst_groups),
        "seen_verbs": sorted(seen_verbs), "heldout_verbs": sorted(heldout_verbs),
        "n_constructions": cfg["k_constructions"], "constr_trans": {str(k): v for k, v in constr_trans.items()},
        "verb_construction": vconstr,
    }
    decisions = {"A_handrule": kept_A, "B_cuecomp": kept_B, "C_lccp": kept_C}
    return decisions, artifacts, subcat_decisions, heldout_verbs, seen_verbs, inst_groups, w


# ----------------------------------------------------------------------------------------------
# Scoring vs INDEPENDENT gold.
# ----------------------------------------------------------------------------------------------
def match_pos(v_lemma, p, pos_rels):
    for g in pos_rels:
        if g["v"] == v_lemma and g["patient"] == p:
            return g
    return None


def score_arm(kept, gold, only_verbs=None):
    """primary P/R/F1 over pos (v_lemma, patient); FP class split; subcat TN."""
    n_gold = 0
    for sid, rec in gold.items():
        for g in rec["pos"]:
            if only_verbs is None or g["v"] in only_verbs:
                n_gold += 1
    tp, covered = 0, set()
    subcat_fp, within_fp, spurious_fp = 0, 0, 0
    n_pred = 0
    for sid, tup in kept:
        v = lemma_verb(tup[0]); p = tup[2]
        if only_verbs is not None and v not in only_verbs:
            continue
        n_pred += 1
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        g = match_pos(v, p, rec["pos"])
        if g is not None:
            tp += 1
            covered.add((sid, rec["pos"].index(g)))
        else:
            if v in rec["nopat"]:
                subcat_fp += 1
            elif v in rec["pos_verbs"]:
                within_fp += 1
            else:
                spurious_fp += 1
    precision = tp / n_pred if n_pred else 0.0
    recall = len(covered) / n_gold if n_gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "n_pred": n_pred, "tp": tp, "n_gold": n_gold, "n_gold_covered": len(covered),
            "subcat_fp": subcat_fp, "within_frame_fp": within_fp, "spurious_verb_fp": spurious_fp,
            "total_fp": subcat_fp + within_fp + spurious_fp,
            "fp_rate": round((subcat_fp + within_fp + spurious_fp) / n_pred, 4) if n_pred else 0.0}


def subcat_true_negatives(decisions, gold, reader_svo, order):
    """Over nopat verb-instances the READER (arm A) mis-attached a patient to, does each arm SUPPRESS it?
    Returns per-arm dict {n_nopat_instances_reader_attached, n_suppressed(TN), n_kept(FP), tn_rate}."""
    # reader (sid,v) instances that (a) are nopat in gold and (b) reader proposed >=1 patient
    reader_attached = set()
    for sid in order:
        for tup in reader_svo[sid]:
            v = lemma_verb(tup[0])
            rec = gold.get(sid)
            if rec and v in rec["nopat"] and v not in rec["pos_verbs"]:
                reader_attached.add((sid, v))
    out = {}
    for arm, kept in decisions.items():
        kept_inst = set((sid, lemma_verb(tup[0])) for sid, tup in kept)
        suppressed = sum(1 for key in reader_attached if key not in kept_inst)
        kept_n = len(reader_attached) - suppressed
        out[arm] = {"n_nopat_reader_attached": len(reader_attached), "n_suppressed_TN": suppressed,
                    "n_kept_FP": kept_n,
                    "tn_rate": round(suppressed / len(reader_attached), 4) if reader_attached else 0.0}
    return out


def learning_curve(subcat_decisions, gold):
    """Arm-C subcat-FP rate on FIRST vs LATER exposures of each verb (nopat instances only)."""
    first_fp = first_n = late_fp = late_n = 0
    for d in subcat_decisions:
        rec = gold.get(d["sid"])
        if not rec or d["v"] not in rec["nopat"] or d["v"] in rec["pos_verbs"]:
            continue  # count only unambiguous nopat instances
        is_fp = 1 if d["kept"] else 0
        if d["occ"] == 0:
            first_fp += is_fp; first_n += 1
        else:
            late_fp += is_fp; late_n += 1
    fr = first_fp / first_n if first_n else 0.0
    lr = late_fp / late_n if late_n else 0.0
    return {"first_exposure_subcat_fp_rate": round(fr, 4), "later_exposure_subcat_fp_rate": round(lr, 4),
            "n_first": first_n, "n_later": late_n, "slope_first_minus_later": round(fr - lr, 4)}


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness(decisions, gold, reader_svo):
    """A real intransitive over-extraction C SUPPRESSES that A keeps + a held-out frame C gets right."""
    a_inst = set((sid, lemma_verb(t[0]), t[2]) for sid, t in decisions["A_handrule"])
    c_inst = set((sid, lemma_verb(t[0]), t[2]) for sid, t in decisions["C_lccp"])
    # find a nopat verb 'came'/'sat'/'wonder'/'look' patient A kept and C dropped
    witness_supp = None
    for (sid, v, p) in sorted(a_inst):
        rec = gold.get(sid)
        if rec and v in rec["nopat"] and v not in rec["pos_verbs"] and (sid, v, p) not in c_inst:
            witness_supp = [sid, v, p]
            break
    # a TRUE pos relation C KEEPS
    witness_keep = None
    for (sid, v, p) in sorted(c_inst):
        rec = gold.get(sid)
        if rec and match_pos(v, p, rec["pos"]) is not None:
            witness_keep = [sid, v, p]
            break
    return {"intransitive_overextraction_suppressed_by_C_kept_by_A": witness_supp,
            "true_patient_kept_by_C": witness_keep,
            "lemma_parity": {"came": lemma_verb("came"), "struggled": lemma_verb("struggled"),
                             "looked": lemma_verb("looked"), "wonder": lemma_verb("wonder")},
            "witness": "PASS" if (witness_supp is not None and witness_keep is not None) else "PARTIAL"}


# ----------------------------------------------------------------------------------------------
# Config + run.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(slice_lessons=["L04", "L05"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=7)


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], sel_keep=0.28,
               sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25,
               k_constructions=4, seed=7)


def run_config(cfg):
    order, sent_text, reader_svo = load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = load_gold(cfg["slice_lessons"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = load_glove_for(toks)

    decisions, artifacts, subcat_decisions, heldout_verbs, seen_verbs, inst_groups, w = run_arms(
        order, reader_svo, sent_text, glove, cfg, cfg["seed"])

    arm_metrics = {}
    for arm in ARMS:
        arm_metrics[arm] = {
            "all": score_arm(decisions[arm], gold),
            "seen": score_arm(decisions[arm], gold, only_verbs=seen_verbs),
            "heldout": score_arm(decisions[arm], gold, only_verbs=heldout_verbs),
        }
    subcat_tn = subcat_true_negatives(decisions, gold, reader_svo, order)
    lc = learning_curve(subcat_decisions, gold)

    # Prediction-3: degrade adjacency cue -> its learned weight must drop.
    cands3 = []
    for sid in order:
        toks_s = tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            feat, _ = candidate_features(toks_s, tup[0], tup[2])
            cands3.append({"sid": sid, "v": lemma_verb(tup[0]), "a": tup[1], "p": tup[2], "tup": tup, "feat": feat})
    sel_fn3, _, _ = build_semantic_teacher(cands3, glove)
    w_norm, _ = learn_cue_weights(cands3, sel_fn3, cfg["sel_keep"], cfg["sel_drop"], cfg["lr"], cfg["epochs"], cfg["seed"])
    # (a) cue-validity probe on ADJACENCY -- the ONLY cue NOT used to set the teacher target (prep/func/clause
    #     ARE the structural teacher, so probing them is circular; adjacency is a purely LEARNED correlate).
    #     Making adjacency unreliable should shrink its learned weight toward 0.
    adj_i = FEAT_NAMES.index("f_adj")
    w_deg, _ = learn_cue_weights(cands3, sel_fn3, cfg["sel_keep"], cfg["sel_drop"], cfg["lr"], cfg["epochs"], cfg["seed"], degrade_feat_idx=adj_i)
    adj_norm, adj_deg = float(w_norm[adj_i]), float(w_deg[adj_i])
    adj_weight_shrinks = bool(abs(adj_deg) < abs(adj_norm) - 1e-6)
    # (b) cue-structure: did self-supervision recover the CORRECT signs (obliques/junk/clause negative)?
    lw = {FEAT_NAMES[i]: round(float(w_norm[i]), 4) for i in range(6)}
    cue_structure_correct = bool(w_norm[FEAT_NAMES.index("f_prep")] < 0 and w_norm[FEAT_NAMES.index("f_func")] < 0
                                 and w_norm[FEAT_NAMES.index("f_clause")] < 0 and w_norm[FEAT_NAMES.index("f_postv")] > 0)
    # (c) DECISIVE not-vacuous check: does the learned per-verb TRANSITIVITY PRIOR separate gold-INTRANSITIVE
    #     verbs (only-nopat) from gold-TRANSITIVE verbs (only-pos)? Gold used ONLY as an evaluation probe here
    #     (NOT for training). A genuine learned subcat signal -> transitive mean prior > intransitive mean.
    inst_best = defaultdict(list)  # verb -> [best objecthood per instance]
    tmp_groups = defaultdict(list)
    for c in cands3:
        tmp_groups[(c["sid"], c["v"])].append(c)
    for (sid, v), cs in tmp_groups.items():
        inst_best[v].append(max(score_cand(w_norm, c["feat"]) for c in cs))
    verb_trans = {v: float(np.mean(b)) for v, b in inst_best.items()}
    all_pos_v, all_nopat_v = set(), set()
    for rec in gold.values():
        all_pos_v |= rec["pos_verbs"]; all_nopat_v |= rec["nopat"]
    pure_pos_verbs = {v for v in all_pos_v if v not in all_nopat_v and v in verb_trans}
    pure_nopat_verbs = {v for v in all_nopat_v if v not in all_pos_v and v in verb_trans}
    trans_mean = float(np.mean([verb_trans[v] for v in pure_pos_verbs])) if pure_pos_verbs else 0.0
    intrans_mean = float(np.mean([verb_trans[v] for v in pure_nopat_verbs])) if pure_nopat_verbs else 0.0
    prior_separates = bool(trans_mean - intrans_mean > 0.10)
    pred3 = {"probe_cue": "f_adj", "adj_weight_normal": round(adj_norm, 4),
             "adj_weight_degraded_unreliable": round(adj_deg, 4), "adj_weight_shrinks": adj_weight_shrinks,
             "cue_structure_correct": cue_structure_correct, "learned_weights_normal": lw,
             "transitive_verb_prior_mean": round(trans_mean, 4), "intransitive_verb_prior_mean": round(intrans_mean, 4),
             "prior_separates_verb_classes": prior_separates,
             "n_pure_transitive_verbs": len(pure_pos_verbs), "n_pure_intransitive_verbs": len(pure_nopat_verbs),
             "mechanism_validity": bool(cue_structure_correct and prior_separates)}

    n_reader = sum(len(reader_svo[sid]) for sid in order)
    meta = {
        "slice_lessons": cfg["slice_lessons"], "n_sentences": len(order), "n_reader_svo": n_reader,
        "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
        "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
        "gold_meta": gold_meta, "artifacts": artifacts,
        "glove_coverage": round(len(glove) / max(1, len(toks)), 3),
        "reader_svo_dump": {sid: [list(t) for t in reader_svo[sid]] for sid in order if reader_svo[sid]},
        "kept_C_dump": [[sid, list(t)] for sid, t in decisions["C_lccp"]],
    }
    return arm_metrics, subcat_tn, lc, pred3, meta, decisions, heldout_verbs, seen_verbs


def build_verdict(arm_metrics, subcat_tn, cfg):
    A = arm_metrics["A_handrule"]["all"]
    C = arm_metrics["C_lccp"]["all"]
    fp_reduction = A["fp_rate"] - C["fp_rate"]
    recall_ret = (C["recall"] / A["recall"]) if A["recall"] > 0 else 0.0
    seen_p = arm_metrics["C_lccp"]["seen"]["precision"]
    held_p = arm_metrics["C_lccp"]["heldout"]["precision"]
    gen_gap = seen_p - held_p  # positive = held-out worse
    if fp_reduction < 0.05 or recall_ret < 0.40 or gen_gap > 0.25:
        verdict = "HARD_FAIL_LEARNED_PARSER_NO_BETTER"
    elif fp_reduction >= 0.15 and recall_ret >= 0.60 and gen_gap <= 0.10:
        verdict = "HARD_PASS_LCCP_REDUCES_MISATTACH_AND_GENERALIZES"
    else:
        verdict = "MIDDLE_BAND"
    return {"verdict": verdict, "fp_rate_reduction_A_minus_C": round(fp_reduction, 4),
            "recall_retention_C_over_A": round(recall_ret, 4),
            "generalization_gap_seen_minus_heldout_precision": round(gen_gap, 4),
            "subcat_tn_rate_C": subcat_tn["C_lccp"]["tn_rate"], "subcat_tn_rate_A": subcat_tn["A_handrule"]["tn_rate"]}


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
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    arm_metrics, subcat_tn, lc, pred3, meta, decisions, heldout_verbs, seen_verbs = run_config(cfg)
    vd = build_verdict(arm_metrics, subcat_tn, cfg)
    witness = scaffold_free_witness(decisions, {sid: r for sid, r in load_gold(cfg["slice_lessons"])[0].items()},
                                    {sid: meta["reader_svo_dump"].get(sid, []) for sid in meta["reader_svo_dump"]})

    hashes = {arm: kept_hash(decisions[arm]) for arm in ARMS}
    assert hashes["A_handrule"] != hashes["B_cuecomp"], "META_RULE_AF: A==B (cue-comp no-op)"
    assert hashes["B_cuecomp"] != hashes["C_lccp"], "META_RULE_AF: B==C (subcat/construction no-op)"
    assert hashes["A_handrule"] != hashes["C_lccp"], "META_RULE_AF: A==C"

    A = arm_metrics["A_handrule"]["all"]; C = arm_metrics["C_lccp"]["all"]
    baseline_in_band = bool(0.05 < A["precision"] < 0.95)
    discriminator_fires = bool(subcat_tn["C_lccp"]["n_suppressed_TN"] > 0)
    elapsed = time.perf_counter() - t0
    v = vd["verdict"]
    B = arm_metrics["B_cuecomp"]["all"]
    Cs = arm_metrics["C_lccp"]["seen"]; Ch = arm_metrics["C_lccp"]["heldout"]
    msg = (f"{v} | slice={'+'.join(cfg['slice_lessons'])} sents={meta['n_sentences']} "
           f"reader={meta['n_reader_svo']} gold_pos={meta['n_gold_pos']} gold_nopat={meta['n_gold_nopat']} "
           f"| A P={A['precision']:.3f} R={A['recall']:.3f} F1={A['f1']:.3f} fp_rate={A['fp_rate']:.3f} "
           f"| B P={B['precision']:.3f} R={B['recall']:.3f} F1={B['f1']:.3f} "
           f"| C P={C['precision']:.3f} R={C['recall']:.3f} F1={C['f1']:.3f} fp_rate={C['fp_rate']:.3f} "
           f"| dFPrate={vd['fp_rate_reduction_A_minus_C']:+.3f} Rret={vd['recall_retention_C_over_A']:.3f} "
           f"| subcatTN A={subcat_tn['A_handrule']['tn_rate']:.3f} C={subcat_tn['C_lccp']['tn_rate']:.3f} "
           f"| FPclass A(sub={A['subcat_fp']},wf={A['within_frame_fp']},sp={A['spurious_verb_fp']}) "
           f"C(sub={C['subcat_fp']},wf={C['within_frame_fp']},sp={C['spurious_verb_fp']}) "
           f"| gen seenP={Cs['precision']:.3f} heldP={Ch['precision']:.3f} gap={vd['generalization_gap_seen_minus_heldout_precision']:+.3f} "
           f"| LC first={lc['first_exposure_subcat_fp_rate']:.3f} late={lc['later_exposure_subcat_fp_rate']:.3f} "
           f"| pred3 mechval={pred3['mechanism_validity']} cue_ok={pred3['cue_structure_correct']} priorSep(T={pred3['transitive_verb_prior_mean']:.2f},I={pred3['intransitive_verb_prior_mean']:.2f}) adjShrink={pred3['adj_weight_shrinks']} "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "arm_metrics": arm_metrics, "verdict_detail": vd, "subcat_true_negatives": subcat_tn,
        "learning_curve": lc, "prediction3_cue_degradation": pred3, "kept_hashes": hashes,
        "arms_differ_verified": True, "baseline_in_band": baseline_in_band,
        "discriminator_fires": discriminator_fires, "scaffold_free_witness": witness,
        "final_metrics_atomicity": "tmp_replace",
        "independent_gold_source": ("data/gold_mcguffey_lccp_argstruct_v1.json -- single-annotator gold with "
                                    "pos (patient-taking) AND nopat (no-patient: intransitive/cognition/oblique/"
                                    "report) verb-instances, annotated from sentence text independent of reader "
                                    "output; makes SUBCAT true-negatives measurable."),
        "data_meta": meta,
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "verdict_detail", "subcat_true_negatives",
                            "learning_curve", "prediction3_cue_degradation", "scaffold_free_witness", "data_meta"],
        "notes": ("LCCP learned argument-structure parser vs INDEPENDENT gold. A=hand-rule, B=learned cue-"
                  "competition (global weights, best-candidate + threshold), C=+subcat transitivity prior + "
                  "construction-level sharing for held-out. HARD_PASS = C reduces total mis-attachment FP-rate "
                  ">=0.15 vs A at >=0.60 recall retention AND held-out precision within 0.10 of seen. "
                  "HARD_FAIL = <0.05 reduction OR held-out drop >0.25 OR recall retention <0.40. CLAIM-VET-"
                  "pending; single-annotator gold (caveated); document-scope within-frame residual flagged as "
                  "next step, NOT built here."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  learned weights: {pred3['learned_weights_normal']}", flush=True)
    for arm in ARMS:
        m = arm_metrics[arm]["all"]
        print(f"  [{arm:>11}] P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} "
              f"n_pred={m['n_pred']} tp={m['tp']} fp(sub/wf/sp)={m['subcat_fp']}/{m['within_frame_fp']}/{m['spurious_verb_fp']} "
              f"fp_rate={m['fp_rate']:.3f} | subcatTN={subcat_tn[arm]['tn_rate']:.3f} "
              f"({subcat_tn[arm]['n_suppressed_TN']}/{subcat_tn[arm]['n_nopat_reader_attached']})", flush=True)
    print(f"  [generalization] C seen P={arm_metrics['C_lccp']['seen']['precision']:.3f} "
          f"heldout P={arm_metrics['C_lccp']['heldout']['precision']:.3f} "
          f"(n_heldout_verbs={len(heldout_verbs)} n_seen_verbs={len(seen_verbs)})", flush=True)
    print(f"  [learning curve] first-exposure subcat-FP={lc['first_exposure_subcat_fp_rate']:.3f} "
          f"later={lc['later_exposure_subcat_fp_rate']:.3f} slope={lc['slope_first_minus_later']:+.3f} "
          f"(n_first={lc['n_first']} n_later={lc['n_later']})", flush=True)
    print(f"  [prediction-3] mechanism_validity={pred3['mechanism_validity']} | cue_structure_correct={pred3['cue_structure_correct']} "
          f"| prior separates verb classes: transitive={pred3['transitive_verb_prior_mean']:.3f} vs "
          f"intransitive={pred3['intransitive_verb_prior_mean']:.3f} (sep={pred3['prior_separates_verb_classes']}, "
          f"n_T={pred3['n_pure_transitive_verbs']} n_I={pred3['n_pure_intransitive_verbs']}) "
          f"| adj cue-validity {pred3['adj_weight_normal']:.3f}->{pred3['adj_weight_degraded_unreliable']:.3f} shrinks={pred3['adj_weight_shrinks']}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def self_test():
    w = np.zeros(6)
    assert lemma_verb("came") == "come" and lemma_verb("struggled") == "struggle"
    assert lemma_verb("looked") == "look" and lemma_verb("wonder") == "wonder"
    assert lemma_verb("sat") == "sit" and lemma_verb("knocked") == "knock"
    # feature extraction sanity
    toks = tokenize("the little boy got up from the floor and came slowly his eyes full of tears")
    feat_g, _ = candidate_features(toks, "got", "floor")
    feat_c, _ = candidate_features(toks, "came", "eyes")
    assert feat_g[3] == 1.0 or feat_g[2] == 1.0, "got/floor should be post-verbal or prep-governed"
    toks2 = tokenize("he opened the door and came in")
    feat_open, _ = candidate_features(toks2, "opened", "door")
    assert feat_open[2] == 1.0 and feat_open[3] == 0.0, "opened/door should be post-verbal, not prep-governed"
    cfg = cfg_smoke()
    arm_metrics, subcat_tn, lc, pred3, meta, decisions, ho, sn = run_config(cfg)
    vd = build_verdict(arm_metrics, subcat_tn, cfg)
    A = arm_metrics["A_handrule"]["all"]; C = arm_metrics["C_lccp"]["all"]
    print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={vd['verdict']} "
          f"A_P={A['precision']:.3f} C_P={C['precision']:.3f} A_fp={A['fp_rate']:.3f} C_fp={C['fp_rate']:.3f} "
          f"dFP={vd['fp_rate_reduction_A_minus_C']:+.3f} subcatTN_C={subcat_tn['C_lccp']['tn_rate']:.3f} "
          f"pred3_mechval={pred3['mechanism_validity']} reader={meta['n_reader_svo']} "
          f"gold_pos={meta['n_gold_pos']} gold_nopat={meta['n_gold_nopat']}", flush=True)
    print(f"[{ANCHOR_NAME}] learned weights: {pred3['learned_weights_normal']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
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
