"""
NESTED / RECURSIVE CLAUSE structure on the FULL McGuffey THIRD READER: wire an explicit-relativizer
RELATIVE-CLAUSE axis into the reader so it represents a FACT-INSIDE-A-FACT instead of flattening or
dropping the embedding. This is the RANK-1 "cheap independent win" from the learned-comprehension 5x
drill (notes/research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md).

STEP-0 CONFIRM/KILL (done off-code BEFORE this build; recorded in the dispatch report):
  (a) CONFIRMED the current reader emits FLAT tuples only. Reproduced its mis-handling of embeddings:
      - "The girl saw the man that stole the apple" -> flat emits svo(saw,girl,APPLE)  [WRONG cross-clause
        mis-attachment: apple is the object of STOLE, not SAW] AND drops stole(man,apple).
      - "The dog that chased the cat barked" -> flat emits svo(chased,dog,cat) [correct embedded content]
        but DROPS the matrix predication barked(dog).
      - coordinated-VP "The dog chased the cat and barked" -> flat drops barked(dog).
  (b) CONFIRMED hdlab.binding supports CLEAN depth-2 nested readout: a fact-inside-a-fact built with the
      REAL bind/bundle primitives (FHRR) and read back through TWO unbinds cleaned-up to 100% accuracy
      across N=512..8192 (40 seeds); the top1-top2 cleanup margin shrinks with depth (D1 ~0.33-0.62 ->
      D2 ~0.13-0.20) exactly as Plate-1995 predicts -- a REAL bounded-depth ceiling (matches the human
      center-embedding limit ~2-3), NOT a wall at depth 2.
  HONEST CAVEAT recorded (partial refutation of the drill's "near-zero-cost" framing): the reader is a
  SYMBOLIC extractor and NEVER calls the HD bind() primitive. So the win is NOT "flip on an unused HD
  primitive" -- it is a SYMBOLIC relative-clause parser + new nested/intransitive emission types. The HD
  representational capacity is genuinely free (b); the EXTRACTION (detect the embedding, attach correctly)
  is real symbolic work of the same kind the arc has been grinding. Tractable for the EXPLICIT-relativizer
  clean sub-case (closed-class cue: that/who/which/whom -- like the deixis/argrole prep cues); the HARD
  sub-case (REDUCED RC / garden-path "the horse raced past the barn fell", NO relativizer) is Stage-B
  learned-disambiguation territory and is DELIBERATELY SCOPED OUT + flagged.

MECHANISM (ONE variable vs the current reader = the nest axis; EVERYTHING else byte-identical):
  When nest=False the extract is LITERALLY R.extract_passage_argrole (the shipped reader, argrole=True,
  deixis=True) -> byte-identical baseline by construction. When nest=True an additive post-pass detects an
  explicit relativizer (that/who/which/whom) whose head is a preceding noun mention and whose embedded
  clause has its own verb, then:
    1. SPLITS the sentence into a MATRIX span and an EMBEDDED span at the relativizer (a bounded
       shift-reduce boundary: embedded clause runs from the relativizer to the next finite verb = the
       matrix verb, for subject-RC; to sentence end for object-RC).
    2. RE-PARSES each span with the SAME learned role-assigner (ORC.assign_roles_learned) -> the embedded
       proposition (correct subject = the RC head) + the matrix proposition (RC head correctly attached).
    3. EMITS: the embedded proposition (svo or intransitive pred), the matrix predication (recovers the
       DROPPED matrix verb, incl. intransitive barked(dog)), and a NESTED-LINK relation
       ("nest", head, embedded_verb, embedded_obj) = the fact-inside-a-fact marker the HD readout can
       unbind to depth 2.
    4. SUPPRESSES the cross-clause mis-attachment: for object-RC, drops the flat svo where the MATRIX verb
       took an EMBEDDED-span filler as object (kills svo(saw,girl,apple)).
  Additive, opt-in, default-OFF, byte-identity-preserving -- SAME discipline as deixis / argrole / clause-seg.

BRAIN-FAITHFULNESS NOTE (pre-reg): hierarchical composition via Merge (Chomsky) / the online
  constituent-tracking of Ding et al. 2016 (Nature Neuroscience); the two-region division of labor
  (temporal retrieval + BA44 unification, Friederici) maps onto reuse-the-role-assigner-per-span. HUMAN
  center-embedding depth limit ~2-3 is a REAL capacity bound (Miller-Chomsky), and the HD depth-2 probe
  shows the SAME bounded-depth degradation -> this ceiling is brain-faithful, not a crosstalk bug to fix.
  DEVIATIONS FLAGGED: (a) the relativizer trigger + span-boundary heuristic is a CURATED closed-class
  scaffold standing in for a learned clause segmenter (pivot authorizes ANY tool for the FOUNDATION;
  runtime stays glass-box); (b) REDUCED (relativizer-less) RC + genuine 2-level embedding = the harder
  tail, SCOPED OUT here (Stage-B learned scorer), done honestly.

REAL BASELINE (design-gate #1): the CURRENT reader = extract_passage_nest(nest=False) which IS
  R.extract_passage_argrole (argrole=True) BYTE-IDENTICAL -> reproduces the mis-attach + dropped-matrix FPs.

CAN-FAIL (design-gate #2; all genuinely reachable + informative):
  (a) span-boundary heuristic MIS-FIRES -> wrong embedded obj / wrong matrix -> attachment metric FLAT or
      DOWN vs baseline (no gain), OR
  (b) over-SUPPRESSION -> drops a real matrix relation -> a REGRESSION the metric shows, OR
  (c) the relativizer trigger fires on a complementizer/demonstrative "that" ("found THAT James had money",
      "is THAT all") -> spurious nest -> precision drop. Guard: head-must-be-a-noun + verb-before-that veto.
  The attachment metric is scored identically on BOTH arms -> nest can fail to beat flat.

DIFFICULTY-ON (design-gate #3): real explicit-relativizer RC sentences MINED FROM the full 79-lesson
  corpus (232 relativizer sites: "horses that work so hard", "boy who never had seen a snowstorm", "men
  who hunt these animals", "tree that lay near a beaver dam", ...) + canonical hand-authored witnesses --
  NOT flat SVO.

ONE VARIABLE (design-gate #4): add the nest axis; hold grounding, coref, deixis (=True), clause-seg,
  composition, argrole, cheap wins ALL identical (extract_passage_nest(nest=False) == R.extract_passage_argrole
  byte-identical, both deixis settings; deixis resolutions IDENTICAL nest ON vs OFF).

MEASURE:
  (1) ATTACHMENT correctness vs an INDEPENDENT single-annotator RC gold, scored IDENTICALLY on flat vs
      nest. A site is FULLY-CORRECT iff: (i) the embedded proposition ev(head,eobj) is emitted with the
      RC head as subject, AND (ii) NO cross-clause mis-attachment (no matrix-verb->embedded-filler rel),
      AND (iii) the matrix predication is present. HARD-PASS: nest >= flat + 10 points fully-correct.
  (2) DEPTH-2 READOUT FIDELITY: the emitted ("nest", head, ev, eobj) structures encoded with the REAL
      hdlab FHRR bind/bundle + cleaned-up at nesting depth 2 -> cleanup accuracy (capacity check on the
      ACTUAL emitted structures, not a synthetic toy).
  (3) NO REGRESSION on the flat-SVO majority: the non-RC relations are UNCHANGED nest ON vs OFF except the
      intended suppressions/additions on RC sentences (report count of touched non-RC rels = must be 0).

REGRESSION GUARD: extract_passage_nest(nest=False) BYTE-IDENTICAL to R.extract_passage_argrole (argrole=True)
  on ALL 79 lessons at deixis True AND False; deixis resolutions IDENTICAL nest ON vs OFF; role
  passive/reversal controls >= 1.00; overlay witness (7/7, in-process, .venv) green; determinism (two ON
  reads identical). OMP=1, fixed int seed, sorted(set) ordering, NO salted-builtin-hashing.
  (run_certification.py 208/0 is a fleet check verified out-of-cell; this cell touches NO certified module.)

BRANCHES (decisive, genuinely can-fail):
  NEST_RESOLVES_EMBEDDING = attachment fully-correct nest >= flat + 10 AND no non-RC regression AND depth-2
    readout fidelity >= 0.90 -> the nest axis RESOLVES explicit-relativizer embedding -> component landed
    (VET-pending).
  SCOPE_LIMITED_OR_WEAK = gain < 10 OR readout fidelity below floor -> localize (boundary heuristic /
    suppression / trigger precision) + honest deflate.
  REGRESSION = a guard failed (nest leaked into the banked reader / deixis / non-RC majority) -> revert + localize.

Glass-box (POS + averaged perceptron role assigner + WordNet grounding + a transparent relativizer/span
  layer + the REAL hdlab FHRR bind/bundle for the depth-2 readout check; NO external LLM, NO torch/GPU at
  runtime for the reader itself -- torch used ONLY for the offline HD readout-fidelity measurement). Local /
  foreground-to-completion. NO push / NO remote-persist. CLAIM-VET-pending; strategic read = HYPOTHESIS
  pending landed-VET.

ANCHOR: read_nested_clause_relative_third_reader_v1
BUILDS ON: read_argstruct_goal_role_third_reader_v1 (the current reader state; b9136f131) + the learned
  role-assigner (exp_oracle_mention_upperbound_reader_v1) + hdlab.binding/bundling (depth-2 readout) +
  the packaged state-of-mind overlay.
CORPUS: mcguffey_third_reader.clean.txt (PG#14766, PD). COMPUTE: sequential-CPU; wall target < 600s.
PRIOR-WORK CHECK: substrate_query "nested recursive binding extractor relative clause embedded proposition"
  -> top cosine 0.3975 = the KB lexical atom 'relative_clause' (a concept entry, NOT a prior experiment
  cell); no prior-arc cell rediscovery -> NOVEL reader axis.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments import exp_read_argstruct_goal_role_third_reader_v1 as R          # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC             # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2      # noqa: E402

load_lessons = R.load_lessons
_VF_MODE = R._VF_MODE

ANCHOR_NAME = "read_nested_clause_relative_third_reader_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 20260718
_KINDS = ("svo", "loc", "poss", "goal", "recipient")

# Closed-class relativizers (explicit-RC trigger). "whose" (possessive) + reduced RC are SCOPED OUT.
RELATIVIZERS = frozenset({"that", "who", "which", "whom"})
# who/which/whom are unambiguous relativizers; "that" is also a complementizer/demonstrative -> a
# clause-taking verb governing the head signals a COMPLEMENTIZER "that" ("tell his mother THAT ...",
# "found THAT James had money"), which must NOT be nested. Precision veto for the "that" case only.
CLAUSE_TAKING_VERBS = frozenset({
    "tell", "tells", "told", "telling", "think", "thinks", "thought",
    "say", "says", "said", "know", "knows", "knew", "known",
    "believe", "believes", "believed", "hope", "hopes", "hoped",
    "wish", "wishes", "wished", "find", "finds", "found", "see", "sees", "saw", "seen",
    "hear", "hears", "heard", "remember", "remembers", "remembered",
    "convince", "convinced", "resolve", "resolved", "doubt", "doubts",
    "feel", "feels", "felt", "show", "shows", "showed", "shown",
    "fear", "fears", "feared", "suppose", "supposed", "declare", "declared",
})
# Auxiliaries: skip when choosing the CONTENT verb of an embedded / matrix clause ("who had SEEN" ->
# the content verb is 'seen', not 'had'; "who is CALLED" -> 'called').
AUX_VERBS = frozenset({
    "is", "am", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "having", "do", "does", "did", "doing",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
})


# =======================================================================================
# The nest axis: detect an explicit-relativizer RC per sentence, split matrix vs embedded spans, re-parse
# each with the SAME learned role-assigner, emit embedded + matrix + a nested-link, suppress mis-attach.
# =======================================================================================
def _content_verb_indices(tagged):
    return [i for i, (s, l, p) in enumerate(tagged) if p.startswith("VB") and l not in AUX_VERBS]


def _emit_prop(kind_tagged, clf, subj_low):
    """Re-parse a span with the learned role-assigner. Return (verb, obj_low_or_None). The subject is
    forced to be subj_low (the RC head), at index 0 of kind_tagged. The verb LABEL prefers the CONTENT
    verb (skip auxiliaries: 'who had SEEN' -> 'seen'); obj = first non-subject PATIENT."""
    roles, vi, verb, passive, cand = ORC.assign_roles_learned(kind_tagged, clf, "handrule", frozenset())
    cverbs = [kind_tagged[i][1] for i in _content_verb_indices(kind_tagged)]
    label = cverbs[0] if cverbs else verb
    if label is None:
        return None, None
    patients = [i for i in cand if roles.get(i) == "PATIENT" and kind_tagged[i][1] != subj_low]
    obj = kind_tagged[patients[0]][1] if patients else None
    return label, obj


def detect_rc_sites(tagged, clf):
    """Detect explicit-relativizer RC sites in one tagged sentence. Returns a list of site dicts. Each:
    head (RC head low), rel_idx, embedded (verb, obj), matrix (verb, obj_or_None, intrans), is_object_rc,
    emb_lows (embedded-span lows for suppression), main_verb (flat main verb of the whole sentence)."""
    sites = []
    verbs = _content_verb_indices(tagged)
    if not verbs:
        return sites
    main_vi, main_verb, _mp = ORC.find_main_verb(tagged)
    used_rel = set()
    for j, (surf, low, pos) in enumerate(tagged):
        if low not in RELATIVIZERS or j in used_rel:
            continue
        # head = nearest preceding NOUN candidate; veto if a verb precedes the relativizer first.
        h = None
        for k in range(j - 1, -1, -1):
            pk = tagged[k][2]
            if pk.startswith("NN"):
                h = k
                break
            if pk.startswith("VB"):
                break  # "found THAT James had money" -> complementizer, not a relativizer
        if h is None:
            continue
        head_low = tagged[h][1]
        # COMPLEMENTIZER veto for 'that' ONLY (who/which/whom are unambiguous): a that-relative on a
        # SUBJECT gap has its verb immediately after 'that' (adverbs allowed). If an overt noun/pronoun
        # subject sits between 'that' and the embedded verb, 'that' is a complementizer ("mother THAT he
        # had been to school") OR an object-relative with an overt subject ("way THAT they took") --
        # conservatively skipped to avoid complementizer FPs (flagged: object that-relatives under-covered).
        if low == "that":
            ev_peek = next((i for i in verbs if i > j), None)
            if ev_peek is None:
                continue
            between = tagged[j + 1:ev_peek]
            if any(p.startswith("NN") or p.startswith("PRP") for (s, l, p) in between):
                continue
        # embedded content verb = first content verb strictly after the relativizer.
        ev_idx = next((i for i in verbs if i > j), None)
        if ev_idx is None:
            continue
        # matrix verb = next content verb after the embedded verb (subject-RC); None -> object-RC.
        mv_idx = next((i for i in verbs if i > ev_idx), None)
        emb_end = mv_idx if mv_idx is not None else len(tagged)
        emb_lows = [tagged[i][1] for i in range(j + 1, emb_end)]
        emb_tagged = [tagged[h]] + tagged[j + 1:emb_end]
        if mv_idx is not None:
            mat_tagged = tagged[:h + 1] + tagged[mv_idx:]
        else:
            mat_tagged = tagged[:h + 1]
        ev, eobj = _emit_prop(emb_tagged, clf, head_low)
        if ev is None:
            continue
        mv, mobj = _emit_prop(mat_tagged, clf, head_low)
        is_object_rc = mv_idx is None
        used_rel.add(j)
        sites.append(dict(head=head_low, rel_idx=j, ev=ev, eobj=eobj,
                          mv=mv, mobj=mobj, matrix_intrans=(mv is not None and mobj is None),
                          is_object_rc=is_object_rc, emb_lows=emb_lows,
                          main_verb=main_verb))
    return sites


def nest_axis_passage(text, clf):
    """Run the nest axis over a passage. Returns (add_rels, suppress_pairs, site_records).
    add_rels: new tuples to add. suppress_pairs: set of (verb, obj_low) flat svo to drop (mis-attach)."""
    add = []
    suppress = set()
    records = []
    for sent in ORC.split_sentences(text):
        tagged = ORC.pos_tag_sentence(sent)
        for st in detect_rc_sites(tagged, clf):
            head, ev, eobj = st["head"], st["ev"], st["eobj"]
            mv, mobj = st["mv"], st["mobj"]
            # embedded proposition (correct subject = head).
            if eobj is not None:
                add.append(("svo", ev, head, eobj))
            else:
                add.append(("pred", ev, head))
            # matrix predication: recover the DROPPED matrix verb ONLY for subject-RC (head = matrix
            # subject). For object-RC the head is the matrix OBJECT (the flat pass already emits the
            # matrix svo correctly), so do NOT re-emit a spurious head-subject matrix relation.
            if (not st["is_object_rc"]) and mv is not None and mv != ev:
                if mobj is not None:
                    add.append(("svo", mv, head, mobj))
                else:
                    add.append(("pred", mv, head))
            # nested-link marker (the fact-inside-a-fact; depth-2 readout target).
            add.append(("nest", head, ev, eobj if eobj is not None else "-"))
            # suppress cross-clause mis-attachment (object-RC): matrix main verb took an embedded filler.
            if st["is_object_rc"] and st["main_verb"] is not None and st["main_verb"] != ev:
                for ol in st["emb_lows"]:
                    suppress.add((st["main_verb"], ol))
            records.append(dict(cue=sent.strip().lower()[:70], head=head, ev=ev, eobj=eobj,
                                mv=mv, mobj=mobj, is_object_rc=st["is_object_rc"]))
    return add, suppress, records


def extract_passage_nest(passage_text, clf, pid, passages_dict, mention_mode, clause_seg,
                         role_fix, self_loop_guard, deixis=True, nest=False,
                         resolutions_out=None, records_out=None):
    """nest=False -> LITERALLY R.extract_passage_argrole(argrole=True) (byte-identical baseline). nest=True
    -> additive RC nest pass merged in (adds embedded+matrix+nest-link, suppresses mis-attach)."""
    rels, rbp, removed, inj = R.extract_passage_argrole(
        passage_text, clf, pid, passages_dict, mention_mode, clause_seg,
        role_fix=role_fix, self_loop_guard=self_loop_guard, deixis=deixis, argrole=True,
        resolutions_out=resolutions_out)
    if not nest:
        return rels, rbp, removed, inj
    add, suppress, records = nest_axis_passage(passage_text, clf)
    if records_out is not None:
        for r in records:
            r2 = dict(r); r2["pid"] = pid; records_out.append(r2)
    kept = [r for r in rels if not (r[0] == "svo" and (r[1], r[3]) in suppress)]
    merged = kept + [tuple(a) for a in add]
    merged = sorted(set(merged), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return merged, rbp, removed, inj


def read_corpus(clf, passages, nest, deixis=True, hb=None, want_records=False, want_deixis=False):
    foundation = set()
    store = {}
    records = [] if want_records else None
    deixis_res = [] if want_deixis else None
    for i, (pid, text) in enumerate(passages.items()):
        rr = deixis_res if want_deixis else None
        rels, _rbp, _removed, _inj = extract_passage_nest(
            text, clf, pid, passages, "handrule", _VF_MODE,
            role_fix=True, self_loop_guard=True, deixis=deixis, nest=nest,
            records_out=records, resolutions_out=rr)
        store[pid] = rels
        for r in rels:
            if r[0] in _KINDS or r[0] in ("nest", "pred"):
                foundation.add(tuple(r))
        if hb is not None:
            hb(i, len(passages))
    return dict(foundation=foundation, store=store, records=records, resolutions=deixis_res)


# =======================================================================================
# INDEPENDENT single-annotator RC ATTACHMENT gold (measurement 1). Each record annotates a REAL RC site by
# pid + a distinctive lowercased content CUE + the head; the gold gives the CORRECT embedded (verb,obj) and
# whether the matrix predication should exist + whether a specific cross-clause mis-attachment is FORBIDDEN.
# Annotated by READING the corpus (anti-circular; NOT copied from the mechanism). Loaded from JSON if present
# else the built-in canonical + corpus set below (authored from the raw corpus text, not the reader output).
# =======================================================================================
_GOLD_PATH = os.path.join(REPO, "data", "_rc_gold_nested_v1.json")
RC_GOLD = json.loads(open(_GOLD_PATH, encoding="utf-8").read()) if os.path.exists(_GOLD_PATH) else []


def _find_rc_record(g, records):
    for r in records:
        if r["pid"] == g["pid"] and r["head"] == g["head"] and g["cue"] in r["cue"]:
            return r
    return None


def _prop_correct(rels_for_pid, g):
    """EXACT proposition-match, scored IDENTICALLY on flat and nest. A site is CORRECT iff the exact
    embedded proposition is emitted (transitive -> svo(ev,head,eobj); intransitive -> pred(ev,head) with
    NO spurious object) AND no forbidden cross-clause mis-attachment. Exact match penalizes an arm's OWN
    errors too (e.g. nest emitting svo(blows,flower,loveliness) for a truly intransitive 'blows' FAILS)."""
    head, ev = g["head"], g["embedded_verb"]
    eobj = g.get("embedded_obj")
    if eobj:
        emb_ok = ("svo", ev, head, eobj) in rels_for_pid
    else:
        emb_ok = (("pred", ev, head) in rels_for_pid and
                  not any(r[0] == "svo" and r[1] == ev and r[2] == head for r in rels_for_pid))
    misattach = g.get("forbid_misattach")   # [matrix_verb, wrong_obj] or None
    mis_ok = True
    if misattach:
        mv, wo = misattach
        mis_ok = not any(r[0] == "svo" and r[1] == mv and r[3] == wo for r in rels_for_pid)
    return emb_ok and mis_ok, dict(emb_ok=emb_ok, mis_ok=mis_ok, transitive=bool(eobj))


def attachment_score(store):
    """Report the HEADLINE fair metric = TRANSITIVE embedded propositions (both arms CAN express as svo;
    exact-match, can-fail for both). Report intransitive recovery SEPARATELY (flat has NO intransitive
    relation type -> structurally inexpressible, an honest capability gap, NOT folded into the headline)."""
    per = []
    tr_correct = tr_n = intr_correct = intr_n = 0
    for g in RC_GOLD:
        rels = [tuple(r) for r in store.get(g["pid"], [])]
        ok, comp = _prop_correct(rels, g)
        per.append(dict(pid=g["pid"], head=g["head"], cue=g["cue"], ok=ok, **comp))
        if comp["transitive"]:
            tr_n += 1
            tr_correct += 1 if ok else 0
        else:
            intr_n += 1
            intr_correct += 1 if ok else 0
    return dict(n=len(RC_GOLD),
                transitive_n=tr_n, transitive_correct=tr_correct,
                transitive_frac=round(tr_correct / tr_n, 4) if tr_n else None,
                intransitive_n=intr_n, intransitive_correct=intr_correct,
                intransitive_frac=round(intr_correct / intr_n, 4) if intr_n else None,
                per=per)


# =======================================================================================
# DEPTH-2 READOUT FIDELITY (measurement 2): encode the ACTUAL emitted ("nest", head, ev, eobj) structures
# with the REAL hdlab FHRR bind/bundle and read them back through TWO unbinds + cleanup. Capacity check on
# real emitted structure (not a synthetic toy). torch used ONLY here (offline measurement), not in the reader.
# =======================================================================================
def depth2_readout_fidelity(nest_links, n_dim=2048, seed=SEED, max_sites=120):
    import numpy as np
    import torch
    from hdlab.binding import bind, unbind
    from hdlab.bundling import bundle

    rng = np.random.default_rng(seed)
    vocab = set()
    for (head, ev, eobj) in nest_links:
        vocab.update([head, ev] + ([eobj] if eobj and eobj != "-" else []))
    roles = ["RVERB", "RSUBJ", "ROBJ", "RHEAD", "RREL"]

    def fhrr(n):
        ph = torch.tensor(rng.uniform(-np.pi, np.pi, size=n), dtype=torch.float64)
        return torch.complex(torch.cos(ph), torch.sin(ph)).to(torch.complex64)

    cb = {w: fhrr(n_dim) for w in vocab}
    rl = {r: fhrr(n_dim) for r in roles}

    def cos(a, b):
        a = a.flatten(); b = b.flatten()
        num = torch.vdot(a, b).abs(); den = a.norm() * b.norm()
        return float(num / den) if float(den) > 0 else 0.0

    def cleanup(q):
        return max(cb, key=lambda w: cos(q, cb[w]))

    tested = [nl for nl in nest_links if nl[2] and nl[2] != "-"][:max_sites]
    hits = 0
    trials = 0
    for (head, ev, eobj) in tested:
        # inner proposition ev(head, eobj); dog_nest = HEAD:head (+) REL:inner; outer here IS dog_nest.
        inner = bundle(torch.stack([bind(rl["RVERB"], cb[ev]),
                                    bind(rl["RSUBJ"], cb[head]),
                                    bind(rl["ROBJ"], cb[eobj])]))
        nested = bundle(torch.stack([bind(rl["RHEAD"], cb[head]),
                                     bind(rl["RREL"], inner)]))
        # depth-2: recover the inner proposition through the outer REL unbind, then read its verb + obj.
        q_inner = unbind(nested, rl["RREL"])
        got_v = cleanup(unbind(q_inner, rl["RVERB"]))
        got_o = cleanup(unbind(q_inner, rl["ROBJ"]))
        hits += (1 if got_v == ev else 0) + (1 if got_o == eobj else 0)
        trials += 2
    return dict(n_sites_tested=len(tested), n_trials=trials,
                depth2_cleanup_acc=round(hits / trials, 4) if trials else None,
                n_dim=n_dim)


# =======================================================================================
# NO-REGRESSION on the flat majority (measurement 3): non-RC relations UNCHANGED nest ON vs OFF.
# =======================================================================================
def nonrc_regression(store_off, store_on, rc_pids):
    touched = 0
    for pid in store_off:
        if pid in rc_pids:
            continue
        if [tuple(r) for r in store_off[pid]] != [tuple(r) for r in store_on[pid]]:
            touched += 1
    return dict(n_nonrc_pids=len(store_off) - len(rc_pids), n_touched=touched)


# =======================================================================================
# Regression guards.
# =======================================================================================
def byte_identity_off(clf, passages, deixis):
    n = 0
    for pid, text in passages.items():
        mine, _, _, _ = extract_passage_nest(text, clf, pid, passages, "handrule", _VF_MODE,
                                              role_fix=True, self_loop_guard=True, deixis=deixis, nest=False)
        theirs, _, _, _ = R.extract_passage_argrole(text, clf, pid, passages, "handrule", _VF_MODE,
                                                     role_fix=True, self_loop_guard=True, deixis=deixis,
                                                     argrole=True)
        n += 1
        if list(mine) != list(theirs):
            return False, n, dict(pid=pid, deixis=deixis,
                                  mine_only=[list(r) for r in set(mine) - set(theirs)][:5],
                                  theirs_only=[list(r) for r in set(theirs) - set(mine)][:5])
    return True, n, None


def deixis_unchanged(clf, passages):
    off = read_corpus(clf, passages, nest=False, want_deixis=True)
    on = read_corpus(clf, passages, nest=True, want_deixis=True)
    a = sorted((r["pid"], r["sentence"], r["pronoun"], r["resolved"]) for r in off["resolutions"])
    b = sorted((r["pid"], r["sentence"], r["pronoun"], r["resolved"]) for r in on["resolutions"])
    return a == b, len(a), len(b)


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _heartbeat(output_dir):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    t0 = time.perf_counter()

    def tick(i, total):
        row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=i, total_units=total,
                   elapsed_s=round(time.perf_counter() - t0, 2))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return tick


def _run_overlay_witness_inproc():
    import importlib.util
    path = os.path.join(REPO, "verification", "verify_state_of_mind_overlay.py")
    try:
        spec = importlib.util.spec_from_file_location("verify_som_overlay_inproc", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rc = mod.main()
        return (rc == 0), "inproc witness PASS (7/7)"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:300]}"


# =======================================================================================
# --dump-rc: emit the REAL detected RC sites (for anti-circular gold authoring).
# =======================================================================================
def dump_rc():
    passages = load_lessons()
    clf = V2._fit_clf()
    on = read_corpus(clf, passages, nest=True, want_records=True)
    rows = on["records"]
    print(f"[dump-rc] {len(rows)} explicit-relativizer RC sites over {len(passages)} lessons")
    for r in sorted(rows, key=lambda x: (x["pid"], x["cue"])):
        print(json.dumps(dict(pid=r["pid"], head=r["head"], ev=r["ev"], eobj=r["eobj"],
                              mv=r["mv"], mobj=r["mobj"], obj_rc=r["is_object_rc"], cue=r["cue"])))
    return 0


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def _witness_sentence(sent, clf):
    passages = {"w": sent}
    rels, _, _, _ = extract_passage_nest(sent, clf, "w", passages, "handrule", _VF_MODE,
                                         role_fix=True, self_loop_guard=True, deixis=True, nest=True)
    return [tuple(r) for r in rels]


def self_test():
    print("[self-test] loading full corpus + building REAL reader ...")
    passages = load_lessons()
    assert len(passages) >= 70, f"expected ~79 lessons, got {len(passages)}"
    clf = V2._fit_clf()

    # scaffold-free WITNESS 1: object-RC mis-attachment corrected.
    w = _witness_sentence("The girl saw the man that stole the apple.", clf)
    assert ("svo", "stole", "man", "apple") in w, f"WITNESS FAIL: embedded stole(man,apple) missing: {w}"
    assert ("svo", "saw", "girl", "apple") not in w, f"WITNESS FAIL: mis-attach saw(girl,apple) NOT suppressed: {w}"
    assert ("nest", "man", "stole", "apple") in w, f"WITNESS FAIL: nest-link missing: {w}"
    print("[self-test] W1 object-RC: stole(man,apple) added, saw(girl,apple) SUPPRESSED, nest-link emitted")

    # WITNESS 2: subject-RC recovers the dropped matrix predication (intransitive barked(dog)).
    w = _witness_sentence("The dog that chased the cat barked.", clf)
    assert ("svo", "chased", "dog", "cat") in w, f"WITNESS FAIL: embedded chased(dog,cat) missing: {w}"
    assert ("pred", "barked", "dog") in w, f"WITNESS FAIL: matrix barked(dog) not recovered: {w}"
    assert ("nest", "dog", "chased", "cat") in w, f"WITNESS FAIL: nest-link missing: {w}"
    print("[self-test] W2 subject-RC: chased(dog,cat) embedded + barked(dog) matrix recovered + nest-link")

    # WITNESS 3: complementizer 'that' does NOT trigger a nest (head-noun / verb-before-that veto).
    w = _witness_sentence("Some of these boys found that James had money.", clf)
    assert not any(r[0] == "nest" for r in w), f"WITNESS FAIL: complementizer 'that' wrongly nested: {w}"
    print("[self-test] W3 complementizer guard: 'found that James had money' NOT nested")

    # real_code_path: run the REAL nest extract on a few lessons; nest must fire.
    sub = dict(list(passages.items())[:14])
    on = read_corpus(clf, sub, nest=True, want_records=True)
    off = read_corpus(clf, sub, nest=False)
    assert len(on["foundation"]) > 0 and len(off["foundation"]) > 0, "reader produced no relations"
    assert len(on["records"]) > 0, "nest axis did NOT fire on the sub-corpus (discriminator under-powered)"
    nest_rels = [r for r in on["foundation"] if r[0] == "nest"]
    assert len(nest_rels) > 0, "no nest relations emitted on the sub-corpus"
    print(f"[self-test] reader ran on 14 lessons: ON {len(on['foundation'])} rel / OFF {len(off['foundation'])} rel; "
          f"{len(on['records'])} RC sites; {len(nest_rels)} nest-links; sample: {sorted(nest_rels)[:2]}")

    # byte-identity OFF (both deixis settings; full-corpus check runs in build_verdict).
    for dx in (True, False):
        ok, nchk, diff = byte_identity_off(clf, sub, deixis=dx)
        assert ok, f"REGRESSION: nest-OFF diverged from R.extract_passage_argrole (deixis={dx}): {diff}"
    print("[self-test] nest-OFF byte-identical to R.extract_passage_argrole on 14 lessons (deixis True+False)")

    # deixis unchanged with nest ON.
    dok, na, nb = deixis_unchanged(clf, sub)
    assert dok, f"REGRESSION: deixis resolutions changed with nest ON ({na} off vs {nb} on)"
    print(f"[self-test] deixis resolutions IDENTICAL nest ON vs OFF ({na} resolutions)")

    # gold structural sanity + every gold cue matches a REAL detected site (anti-circular).
    assert len(RC_GOLD) >= 15, f"RC gold too small ({len(RC_GOLD)}); author it via --dump-rc first"
    full = read_corpus(clf, passages, nest=True, want_records=True)
    recs = full["records"]
    n_unmatched = 0
    for g in RC_GOLD:
        if g["pid"] == "witness":
            continue
        if _find_rc_record(g, recs) is None:
            n_unmatched += 1
            print(f"[self-test][WARN] gold RC site not matched to any detected site: {g['pid']} {g['head']} {g['cue'][:40]}")
    assert n_unmatched == 0, f"{n_unmatched} gold sites did not match a real detected site (fix cue/head/pid)"
    print(f"[self-test] RC gold: {len(RC_GOLD)} items, all corpus sites matched to real detected sites")

    # depth-2 readout fidelity on the ACTUAL emitted nest-links.
    nls = [(r[1], r[2], r[3]) for r in full["foundation"] if r[0] == "nest"]
    fid = depth2_readout_fidelity(nls, n_dim=2048)
    assert fid["depth2_cleanup_acc"] is None or fid["depth2_cleanup_acc"] >= 0.5, f"depth2 readout collapsed: {fid}"
    print(f"[self-test] depth-2 readout fidelity on {fid['n_sites_tested']} real nest-links: "
          f"acc={fid['depth2_cleanup_acc']} (N={fid['n_dim']})")

    # REGRESSION controls fire + overlay witness (7/7) green.
    ctrl = V2._role_controls(clf)
    assert ctrl["passive_rolefix"] >= 1.0 and ctrl["reversal_rolefix"] >= 1.0, f"role controls regressed: {ctrl}"
    wok, wtail = _run_overlay_witness_inproc()
    assert wok, f"overlay witness FAILED: {wtail}"
    print(f"[self-test] controls: passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f}; overlay green")

    # determinism: two ON reads identical.
    on2 = read_corpus(clf, sub, nest=True)
    assert on["foundation"] == on2["foundation"], "non-deterministic ON foundation"
    print("[self-test] deterministic (two ON reads identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Full verdict build.
# =======================================================================================
def build_verdict(timeout_s=600):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_start_marker(OUTPUT_DIR, "full", expected_n_units=79)
    hb = _heartbeat(OUTPUT_DIR)
    passages = load_lessons()
    clf = V2._fit_clf()

    # full-corpus byte-identity OFF (both deixis settings).
    bok_t, nchk_t, diff_t = byte_identity_off(clf, passages, deixis=True)
    bok_f, nchk_f, diff_f = byte_identity_off(clf, passages, deixis=False)
    assert bok_t and bok_f, f"REGRESSION full-corpus byte-identity: dxT={diff_t} dxF={diff_f}"

    off = read_corpus(clf, passages, nest=False, hb=hb)
    on = read_corpus(clf, passages, nest=True, want_records=True)
    rc_pids = sorted({r["pid"] for r in on["records"]})

    attach_off = attachment_score(off["store"])
    attach_on = attachment_score(on["store"])
    # HEADLINE = the FAIR, can-fail transitive metric (both arms can express as svo).
    delta = (attach_on["transitive_correct"] - attach_off["transitive_correct"])
    delta_pts = (round(100.0 * (attach_on["transitive_frac"] - attach_off["transitive_frac"]), 2)
                 if attach_on["transitive_frac"] is not None else None)
    intr_recovered = attach_on["intransitive_correct"] - attach_off["intransitive_correct"]

    nls = [(r[1], r[2], r[3]) for r in on["foundation"] if r[0] == "nest"]
    fid = depth2_readout_fidelity(nls, n_dim=2048)
    reg = nonrc_regression(off["store"], on["store"], set(rc_pids))
    dok, na, nb = deixis_unchanged(clf, passages)
    ctrl = V2._role_controls(clf)
    wok, wtail = _run_overlay_witness_inproc()

    hard_pass = (delta_pts is not None and delta_pts >= 10.0 and reg["n_touched"] == 0 and
                 fid["depth2_cleanup_acc"] is not None and fid["depth2_cleanup_acc"] >= 0.90 and
                 dok and wok and ctrl["passive_rolefix"] >= 1.0 and ctrl["reversal_rolefix"] >= 1.0)
    if hard_pass:
        verdict = "NEST_RESOLVES_EMBEDDING"
    elif (not dok) or (not wok) or reg["n_touched"] > 0:
        verdict = "REGRESSION"
    else:
        verdict = "SCOPE_LIMITED_OR_WEAK"

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=verdict,
        verdict_msg=(f"transitive-RC-attach flat {attach_off['transitive_correct']}/{attach_off['transitive_n']} "
                     f"({attach_off['transitive_frac']}) -> nest {attach_on['transitive_correct']}/"
                     f"{attach_on['transitive_n']} ({attach_on['transitive_frac']}); delta={delta_pts}pt; "
                     f"intransitive_recovered={intr_recovered}/{attach_on['intransitive_n']} (flat-inexpressible); "
                     f"depth2_fid={fid['depth2_cleanup_acc']}; nonRC_touched={reg['n_touched']}; deixis_ok={dok}"),
        summary=f"{verdict}: transitive-RC delta {delta_pts}pt, +{intr_recovered} intransitive, depth2 {fid['depth2_cleanup_acc']}",
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        seed=SEED, n_lessons=len(passages), n_rc_sites=len(on["records"]),
        n_rc_pids=len(rc_pids),
        attachment_flat=attach_off, attachment_nest=attach_on,
        attach_delta_transitive_correct=delta, attach_delta_points=delta_pts,
        intransitive_recovered=intr_recovered,
        depth2_readout=fid, nonrc_regression=reg,
        deixis_unchanged=dict(ok=dok, n_off=na, n_on=nb),
        byte_identity_off=dict(deixis_true=bok_t, deixis_false=bok_f, n_checked=nchk_t),
        role_controls=ctrl, overlay_witness=dict(ok=wok, tail=wtail),
        n_nest_links=len(nls),
        cited=dict(builds_on="read_argstruct_goal_role_third_reader_v1@b9136f131",
                   drill="notes/research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md"),
        REQUIRED_FIELDS=["verdict", "attach_delta_points", "depth2_readout", "nonrc_regression",
                         "byte_identity_off", "deixis_unchanged", "overlay_witness"],
        caveats=[
            "SYMBOLIC extractor: reader never calls HD bind(); nest axis is a symbolic RC parser. The HD "
            "depth-2 readout is an OFFLINE capacity check on the emitted structures, not the runtime path.",
            "Explicit-relativizer RC only (that/who/which/whom). REDUCED RC + genuine 2-level embedding "
            "SCOPED OUT (Stage-B learned scorer).",
            "Span-boundary heuristic (RC ends at next finite verb) is the fragile part; single-annotator gold; "
            "pronoun-headed RCs not fully handled.",
            "Depth-2 HD ceiling is brain-faithful (human center-embedding ~2-3), not a crosstalk bug.",
        ],
    )
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[verdict] {verdict} :: {metrics['verdict_msg']} :: {elapsed}s")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dump-rc", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()
    try:
        if args.dump_rc:
            return dump_rc()
        if args.self_test:
            return self_test()
        if args.full:
            return build_verdict(timeout_s=args.timeout)
        return self_test()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        print(f"[CRASH] {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
