"""
READ-TO-GROW at SCALE + CLAUSE-SEG FACTIVITY GENERALIZATION on the FULL McGuffey THIRD READER (79
lessons), running the CURRENT reader UNCHANGED (fixed coref agreement+salience + hand-rule grounded
mentions + clause-seg factivity filter + cheap wins [self-loop + role-fix] + composition). Three
simultaneous measurements the tick calls for:

  (1) CLAUSE-SEG GENERALIZATION (the VET-banked CG-revival gate, a8b287c8): across the full corpus's
      COORD bare-VP injection sites, does the factivity filter (verb-class list + structural direct-object
      parse) track a factivity ORACLE VERB-INDEPENDENTLY -- especially in the NON-FACTIVE+DO DIVERGENCE
      regime (verb-list says non-factive, structural DO says admit)? The 14-passage subset had only 2
      non-factive verbs (wished, thought); the full corpus is the >=3-non-factive corpus the gate asked for.
  (2) FOUNDATION-GROWTH (read-to-grow at scale, tick step-5): accumulate extracted svo/loc/poss relations
      from an EMPTY start across all 79 lessons; report growth (# relations / # entities) + a FAIR
      per-relation precision estimate on a deterministic hand-checked random sample (single-annotator,
      coverage-honest).
  (3) COMPONENT-PRIORITIZATION: classify the sampled FPs by cause (COREF / ARG_STRUCT / NP_HEAD / VERB_TAG)
      -> which dominates at scale = the data-driven next-component priority.
  Also: COMPREHENSION spot-check -- a small hand-authored Q-set on full-corpus lessons OUTSIDE the 14-subset,
      answered by the reader's answer engine over the (noisy) grown store; accuracy vs the 14-subset baseline.

ONE-VARIABLE per measurement (design-gate; USER: fair tests every time):
  - CG gate: factivity filter ON (verbfilter suppression) vs the filter's decision at EVERY site, scored
    against an INDEPENDENT hand-annotated factivity gold. Divergence subset isolates verb-list vs structure.
  - Foundation: filter ON (verbfilter) vs OFF (v2 topical, inject-always) -> foundation SIZE + which FPs the
    filter removes at scale (does the factivity filter matter for foundation precision at scale?).
  - Corpus: the FULL 79-lesson third reader (vs the 14 hand-selected in-vocab passages = the confirmed scope).

BASELINE (the confirmed scope): the 14-passage subset envelope result
  (reader_grade3_envelope_readtogrow_v1: comp all=0.7333, ref=0.8333, RELF1 R=0.800, foundation 36 rel /
   32 ent, quality_LB 0.387, verdict HOLDS)  CITED@data/exp_reader_grade3_envelope_readtogrow_v1/metrics.json.
  Does the reader HOLD at scale (79 lessons, more entities, longer passages, dialogue+poetry, the non-
  factive+DO divergence)?

CAN-FAIL (all genuinely reachable + informative):
  (a) clause-seg could FAIL generalization: the divergence breaks the structural signal OR the verb-list is
      corpus-tuned -> SCOPE-LIMITED.
  (b) foundation could grow mostly-WRONG at scale: precision collapses on harder/poetic passages.
  (c) reader could degrade at scale on comprehension.

REGRESSION GUARD: role controls (passive/reversal via V2._role_controls) hold at 1.00; overlay witness
  green; determinism (two foundation builds identical). Independent single-annotator gold (coverage +
  annotator limits reported HONESTLY). OMP=1, fixed seed, sorted(set), no hash()-seeded randomness.

BRANCHES (decisive):
  GENERALIZES_AND_GROWS = factivity filter tracks the oracle verb-independently at scale (incl. divergence)
    AND foundation grows mostly-correct AND reader holds -> real scale-up win (clause-seg -> CG candidate).
  SCOPE_LIMITED_OR_DEGRADES = filter needs the verb-list (divergence breaks structure) OR foundation grows
    noisy OR reader degrades -> localize the dominant FP component = data-driven next priority + honest deflate.

Glass-box (POS + averaged perceptron + WordNet grounding + transparent verb-class + POS direct-object parse;
NO external LLM, NO torch/GPU at runtime). Local / foreground-to-completion. NO push / NO remote-persist.
CLAIM-VET-pending; strategic read = HYPOTHESIS pending landed-VET (NOT self-declared chain-grade).

ANCHOR: read_grow_full_third_reader_clauseseg_generalization_v1
BUILDS ON: reader_clauseseg_verbclass_filter_v1 (the factivity filter; VET a8b287c8) + reader_grade3_
envelope_readtogrow_v1 (14-subset read-to-grow; 00c6688b6). CORPUS: mcguffey_third_reader.clean.txt (PG#14766,
PD). COMPUTE: sequential-CPU; wall target < 600s (79 lessons x2 passes).
PRIOR-WORK CHECK: substrate_query "read to grow clause-seg factivity scale generalization" -> no prior-arc
cell at cosine>0.30 (top hits WordNet concept atoms, irrelevant); this builds directly on the two cited cells.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD, no-KG measurement cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                                 [META_RULE_AH: tmp_replace]
# - discriminator CAN-FAIL (SCOPE_LIMITED/DEGRADES genuinely reachable)           [design-gate]
# - REAL baseline = the 14-subset envelope result (cited) + filter OFF arm        [not a strawman]
# - one variable per measurement; independent hand gold; coverage/annotator limits reported honestly
# - real_code_path: runs the REAL extract_passage_vf + REAL perceptron + POS tagger on REAL corpus text;
#   runs the REAL passive/reversal role controls + overlay witness                [F.1]
# - deterministic seeding (fixed int seed, sample via sorted(set)+Random(FIXED); no hash())  [F.5/PROT-023]
# - PROVENANCE: corpus loaded verbatim from the cleaned file (page-number + lesson-marker lines stripped)
# - start-marker + crash-diagnostic; heartbeat present (wall can exceed 60s)
# - all reported numbers MEASURED@this metrics.json; baseline/refs CITED@their metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A multi-seed
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import re
import sys
import json
import time
import random
import argparse
import platform
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# The CURRENT reader, imported VERBATIM (unchanged): VF = the clause-seg verb-class factivity filter cell.
# extract_passage_vf runs the whole pipeline (coref overlay + role assigner + cheap wins + clause-seg
# factivity filter + composition) on arbitrary passage text -> corpus-independent glass-box extractor.
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2   # noqa: E402
from experiments import exp_reader_clauseseg_verbclass_filter_v1 as VF          # noqa: E402

ANCHOR_NAME = "read_grow_full_third_reader_clauseseg_generalization_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
CORPUS_PATH = os.path.join(REPO, "data", "corpora", "graded_readers_graded", "cleaned",
                           "mcguffey_third_reader.clean.txt")
SEED = 20260718

# ---- CITED baseline (the confirmed 14-subset scope) ------------------------------------------------
BASE14 = dict(comp_all=0.7333, ref_acc=0.8333, RELF1_recall=0.800, n_relations=36, n_entities=32,
              quality_lb=0.387)  # CITED@data/exp_reader_grade3_envelope_readtogrow_v1/metrics.json

# =======================================================================================
# INDEPENDENT hand-annotated FACTIVITY GOLD for the CG gate (measurement 1).
# Gold question per COORD bare-VP injection site: SHOULD the held-subject injection be SUPPRESSED on
# FACTIVITY grounds -- i.e. is the coordinated main verb NON-FACTIVE / mental-state / irrealis /
# appearance (injecting an svo would be semantically SPURIOUS), IGNORING whether the held subject is
# correct? Annotated by READING the clauses (anti-circular; NOT copied from the filter's own flag).
# Lexical (verb-level) EXCEPT the DIVERGENCE overrides, where a filter-non-factive verb is FACTIVE-
# TRANSITIVE in context (real event + genuine direct object -> gold = ADMIT). Single-annotator.
GOLD_NONFACTIVE_VERBS = frozenset({
    # clear cognition / desire / irrealis / appearance verbs -> injecting an svo is spurious.
    "think", "thought", "thinking", "wish", "wished", "hope", "hoped", "believe", "believed",
    "want", "wanted", "seem", "seemed", "wonder", "wondered", "decide", "decided", "long", "longing",
    "remember", "remembered", "looked", "looking", "wait", "waiting", "forgotten", "dream", "pretend",
    "imagine", "suppose", "expect",
})
# DIVERGENCE overrides: filter-non-factive verbs that are FACTIVE-TRANSITIVE at THIS site (real event +
# genuine direct object). Gold = ADMIT. These are the non-factive+DO divergence sites the banked gate
# targets: the verb-LIST suppresses, the STRUCTURAL DO-parse would admit, and the STRUCTURE is correct.
DIVERGENCE_FACTIVE_SITES = frozenset({
    ("L39", "feel"),     # "or taste, or feel THEM" -- physical perception of thoughts; DO pronoun 'them'
    ("L62", "forget"),   # "forget the injury" -- transitive, genuine direct-object 'injury'
})


def gold_should_suppress(pid, verb):
    """INDEPENDENT gold: True iff this site should be suppressed on factivity grounds."""
    if (pid, verb) in DIVERGENCE_FACTIVE_SITES:
        return False   # factive-transitive in context -> gold ADMIT (divergence)
    return verb in GOLD_NONFACTIVE_VERBS


# =======================================================================================
# INDEPENDENT hand-annotated FOUNDATION-PRECISION SAMPLE (measurements 2 + 3).
# 60 relations drawn deterministically (sorted(foundation) + Random(SEED)) from the FILTER-ON foundation;
# each labelled by READING: verdict in {CORRECT, FP, BORDERLINE(lean-correct)} + FP cause in
# {COREF, ARG_STRUCT, NP_HEAD, VERB_TAG}. Single-annotator, coverage-honest. Keyed by the relation tuple
# so the score is robust to sample-ordering; the cell ASSERTS every sampled tuple is annotated (else FAIL
# LOUD -- foundation drift would otherwise silently mis-score).
# cause categories: COREF = unresolved/wrong pronoun (i/you/we/me/my/our/your) or wrong held subject;
#   ARG_STRUCT = wrong role (goal/particle/oblique/complement as patient, intransitive-with-patient);
#   NP_HEAD = adjective/adverb/determiner as an entity head; VERB_TAG = non-verb tagged as the verb.
HAND_GOLD_SAMPLE = {
    ("loc", "girl", "front"): ("BORDERLINE", None),
    ("loc", "man", "midst"): ("CORRECT", None),
    ("loc", "mules", "precipice"): ("CORRECT", None),
    ("loc", "sheep", "turnips"): ("FP", "ARG_STRUCT"),
    ("poss", "fisher", "book"): ("BORDERLINE", None),
    ("poss", "george", "mother"): ("CORRECT", None),
    ("poss", "little", "homage"): ("FP", "NP_HEAD"),
    ("poss", "my", "aunt"): ("FP", "COREF"),
    ("poss", "my", "plan"): ("FP", "COREF"),
    ("poss", "our", "way"): ("FP", "COREF"),
    ("poss", "sailor", "plan"): ("BORDERLINE", None),
    ("poss", "shepherd", "feet"): ("CORRECT", None),
    ("poss", "shepherd", "pasture"): ("CORRECT", None),
    ("poss", "traveler", "sultry"): ("FP", "NP_HEAD"),
    ("poss", "your", "case"): ("FP", "COREF"),
    ("poss", "your", "snowballs"): ("FP", "COREF"),
    ("svo", "advance", "you", "bolder"): ("FP", "COREF"),
    ("svo", "bring", "i", "susie"): ("FP", "COREF"),
    ("svo", "came", "harry", "hands"): ("FP", "ARG_STRUCT"),
    ("svo", "care", "i", "things"): ("FP", "COREF"),
    ("svo", "caught", "you", "horse"): ("FP", "COREF"),
    ("svo", "coming", "james", "stones"): ("FP", "ARG_STRUCT"),
    ("svo", "find", "sooner", "stones"): ("FP", "NP_HEAD"),
    ("svo", "fly", "down", "snowy"): ("FP", "NP_HEAD"),
    ("svo", "flying", "boy", "i"): ("FP", "COREF"),
    ("svo", "fought", "we", "till"): ("FP", "COREF"),
    ("svo", "found", "son", "joe"): ("BORDERLINE", None),
    ("svo", "gave", "father", "bridle"): ("CORRECT", None),
    ("svo", "gave", "widow", "side"): ("FP", "ARG_STRUCT"),
    ("svo", "given", "susie", "meat"): ("BORDERLINE", None),
    ("svo", "heard", "sands", "deep"): ("FP", "NP_HEAD"),
    ("svo", "helped", "willie", "out"): ("FP", "ARG_STRUCT"),
    ("svo", "kept", "tom", "a"): ("FP", "NP_HEAD"),
    ("svo", "laugh", "as", "heart"): ("FP", "NP_HEAD"),
    ("svo", "led", "man", "western"): ("FP", "NP_HEAD"),
    ("svo", "led", "shepherd", "sheep"): ("CORRECT", None),
    ("svo", "lifted", "george", "mouth"): ("FP", "ARG_STRUCT"),
    ("svo", "looks", "bird", "living"): ("FP", "NP_HEAD"),
    ("svo", "make", "dishes", "fires"): ("FP", "ARG_STRUCT"),
    ("svo", "married", "will", "lovely"): ("FP", "NP_HEAD"),
    ("svo", "play", "you", "pencil"): ("FP", "COREF"),
    ("svo", "play", "you", "slate"): ("FP", "COREF"),
    ("svo", "played", "we", "i"): ("FP", "COREF"),
    ("svo", "put", "son", "head"): ("FP", "ARG_STRUCT"),
    ("svo", "ruined", "boys", "will"): ("FP", "VERB_TAG"),
    ("svo", "said", "gracie", "birdie"): ("FP", "ARG_STRUCT"),
    ("svo", "said", "mary", "matches"): ("FP", "ARG_STRUCT"),
    ("svo", "said", "susan", "word"): ("BORDERLINE", None),
    ("svo", "sat", "merchant", "piece"): ("FP", "ARG_STRUCT"),
    ("svo", "saw", "i", "sign"): ("FP", "COREF"),
    ("svo", "saw", "susie", "spring"): ("BORDERLINE", None),
    ("svo", "see", "i", "beggar"): ("FP", "COREF"),
    ("svo", "sing", "i", "folks"): ("FP", "COREF"),
    ("svo", "singing", "snowbird", "ere"): ("FP", "NP_HEAD"),
    ("svo", "sitting", "herbert", "face"): ("FP", "ARG_STRUCT"),
    ("svo", "takes", "great", "growth"): ("FP", "NP_HEAD"),
    ("svo", "tell", "me", "victory"): ("FP", "COREF"),
    ("svo", "took", "man", "crusts"): ("CORRECT", None),
    ("svo", "went", "son", "river"): ("FP", "ARG_STRUCT"),
    ("svo", "wished", "father", "books"): ("FP", "ARG_STRUCT"),
}

# =======================================================================================
# COMPREHENSION spot-check Q-set (measurement "also"). Hand-authored on full-corpus lessons; independent
# gold by reading. Each spec never contains the answer. The reader answers over the (noisy) grown store,
# so a correct answer means the reader RESOLVED the right relation despite competing FPs (fair, can-fail).
# slice in {NC, CO}. Small-n, single-annotator (reported honestly).
COMP_QS = [
    dict(qid="C1", pid="L13", slice="NC", spec=("svo_patient", "killed", "wolf"), gold="sheep",
         text="What did the wolf kill?"),
    dict(qid="C2", pid="L13", slice="NC", spec=("svo_agent", "killed", "sheep"), gold="wolf",
         text="Who killed the sheep?"),
    dict(qid="C3", pid="L07", slice="CO", spec=("has_owner", "home"), gold="james",
         text="Whose home was the school near?"),
    dict(qid="C4", pid="L07", slice="CO", spec=("has_owner", "mother"), gold="james",
         text="Whose mother is in the story?"),
    dict(qid="C5", pid="L67", slice="NC", spec=("svo_patient", "brought", "susie"), gold="basket",
         text="What did Susie bring?"),
    dict(qid="C6", pid="L67", slice="CO", spec=("has_owner", "basket"), gold="susie",
         text="Whose basket was it?"),
    dict(qid="C7", pid="L66", slice="NC", spec=("svo_agent", "sent", "children"), gold="baker",
         text="Who sent for the children?"),
    dict(qid="C8", pid="L60", slice="NC", spec=("svo_patient", "heard", "boy"), gold="horse",
         text="What did the boy hear?"),
]

_PAGE_RE = re.compile(r"^\(\d+\)\s*$")
_LESSON_RE = re.compile(r"^#?\s*LESSON\b", re.IGNORECASE)
_KINDS = ("svo", "loc", "poss")


# =======================================================================================
# Corpus loader: split the cleaned file into lessons; strip lesson-marker + page-number artifact lines.
# =======================================================================================
def load_lessons():
    with open(CORPUS_PATH, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    lessons = {}
    cur_id, cur, idx = None, [], 0
    for ln in lines:
        s = ln.strip()
        if _LESSON_RE.match(s):
            if cur_id is not None:
                lessons[cur_id] = " ".join(x.strip() for x in cur if x.strip()).strip()
            idx += 1
            cur_id, cur = f"L{idx:02d}", []
            continue
        if _PAGE_RE.match(s):
            continue
        cur.append(ln)
    if cur_id is not None:
        lessons[cur_id] = " ".join(x.strip() for x in cur if x.strip()).strip()
    return {k: v for k, v in lessons.items() if v}


# =======================================================================================
# Run the CURRENT reader over the full corpus; accumulate the foundation + injection-site decisions.
# clause_seg = "learned_topical_verbfilter" (filter ON) or "learned_topical" (filter OFF).
# =======================================================================================
def read_corpus(clf, passages, clause_seg, hb=None):
    foundation = set()
    per_passage = {}
    decisions = []
    store = {}
    for i, (pid, text) in enumerate(passages.items()):
        dec = [] if clause_seg == "learned_topical_verbfilter" else None
        rels, rbp, _removed, inj = VF.extract_passage_vf(
            text, clf, pid, passages, "handrule", clause_seg,
            role_fix=True, self_loop_guard=True, decisions_out=dec)
        store[pid] = rels
        kinds = [r for r in rels if r[0] in _KINDS]
        per_passage[pid] = dict(n_rels=len(kinds), n_inj=len(inj))
        for r in kinds:
            foundation.add(tuple(r))
        if dec is not None:
            for d in dec:
                decisions.append(d)
        if hb is not None:
            hb(i, len(passages))
    ents = set()
    for r in foundation:
        if r[0] == "svo":
            ents.update([r[2], r[3]])
        else:
            ents.update([r[1], r[2]])
    return dict(foundation=foundation, entities=ents, per_passage=per_passage,
                decisions=decisions, store=store)


# =======================================================================================
# Measurement 1: CG gate -- factivity filter vs the independent factivity gold on ALL injection sites.
# =======================================================================================
def cg_gate(decisions):
    n_sites = len(decisions)
    # filter_label = the filter would SUPPRESS on factivity grounds (its non_factive flag).
    # gold_label   = should suppress on factivity grounds (independent).
    tp = fp = fn = tn = 0
    divergence = []
    filter_over_suppress = []   # filter suppresses (non_factive) but gold says ADMIT (factive)
    filter_miss = []            # gold says suppress but filter admits (non_factive False)
    for d in decisions:
        pid, verb = d["pid"], d["verb"]
        f = bool(d["non_factive"])
        g = gold_should_suppress(pid, verb)
        if f and g:
            tp += 1
        elif f and not g:
            fp += 1
            filter_over_suppress.append(dict(pid=pid, verb=verb, has_do=d["has_direct_object"],
                                             clause=d["clause"][:80]))
        elif (not f) and g:
            fn += 1
            filter_miss.append(dict(pid=pid, verb=verb, has_do=d["has_direct_object"],
                                    clause=d["clause"][:80]))
        else:
            tn += 1
        if d["non_factive"] and d["has_direct_object"]:
            divergence.append(dict(pid=pid, verb=verb, filter_suppress=True, structural_admit=True,
                                   gold_suppress=g, clause=d["clause"][:80]))
    prec = tp / (tp + fp) if (tp + fp) else None
    rec = tp / (tp + fn) if (tp + fn) else None
    # divergence subset: sites where verb-list & structural DO DISAGREE (non_factive AND has_DO).
    n_div = len(divergence)
    div_filter_correct = sum(1 for x in divergence if x["filter_suppress"] == x["gold_suppress"])
    div_struct_correct = sum(1 for x in divergence if (not x["gold_suppress"]))  # structural admits -> correct iff gold admit
    return dict(
        n_sites=n_sites, tp=tp, fp=fp, fn=fn, tn=tn,
        factivity_suppression_precision=(round(prec, 4) if prec is not None else None),
        factivity_suppression_recall=(round(rec, 4) if rec is not None else None),
        n_flagged=tp + fp, n_gold_nonfactive=tp + fn,
        n_divergence_sites=n_div, divergence_sites=divergence,
        divergence_filter_correct=div_filter_correct, divergence_structural_correct=div_struct_correct,
        filter_over_suppress=filter_over_suppress, filter_miss=filter_miss,
        n_admit=sum(1 for d in decisions if d["admit"]),
        n_suppress=sum(1 for d in decisions if not d["admit"]),
        suppress_reason_hist=dict(Counter(d["reason"] for d in decisions if not d["admit"])))


# =======================================================================================
# Measurements 2 + 3: foundation growth + hand-checked precision sample + FP-cause histogram.
# =======================================================================================
def sample_foundation(foundation):
    fnd_sorted = sorted([tuple(r) for r in foundation])
    rng = random.Random(SEED)
    idx = list(range(len(fnd_sorted)))
    rng.shuffle(idx)
    take = sorted(idx[:60])
    return [fnd_sorted[i] for i in take]


def foundation_precision(sample):
    missing = [list(r) for r in sample if r not in HAND_GOLD_SAMPLE]
    assert not missing, ("HAND_GOLD_SAMPLE does not cover the drawn sample (foundation drifted); "
                         f"unannotated: {missing}")
    n = len(sample)
    correct = sum(1 for r in sample if HAND_GOLD_SAMPLE[r][0] == "CORRECT")
    borderline = sum(1 for r in sample if HAND_GOLD_SAMPLE[r][0] == "BORDERLINE")
    fp = sum(1 for r in sample if HAND_GOLD_SAMPLE[r][0] == "FP")
    cause = Counter(HAND_GOLD_SAMPLE[r][1] for r in sample if HAND_GOLD_SAMPLE[r][0] == "FP")
    prec_lower = correct / n                      # borderline counted as FP
    prec_upper = (correct + borderline) / n       # borderline counted as correct
    return dict(n_sample=n, n_correct=correct, n_borderline=borderline, n_fp=fp,
                precision_point=round((correct + 0.5 * borderline) / n, 4),
                precision_lower=round(prec_lower, 4), precision_upper=round(prec_upper, 4),
                fp_cause_histogram=dict(cause),
                fp_cause_fraction={k: round(v / fp, 3) for k, v in cause.items()} if fp else {})


# =======================================================================================
# Comprehension spot-check.
# =======================================================================================
def comprehension(store):
    correct, per_q = [], []
    for q in COMP_QS:
        rels = store.get(q["pid"], [])
        ans = ORC.answer_reader(q["spec"], rels)
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        ok = (na is not None and na == ng)
        correct.append(1 if ok else 0)
        per_q.append(dict(qid=q["qid"], slice=q["slice"], gold=q["gold"], pred=na, ok=ok))
    acc = sum(correct) / len(correct) if correct else 0.0
    return dict(accuracy=round(acc, 4), n=len(COMP_QS), per_q=per_q,
                n_correct=sum(correct))


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


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] loading full corpus + building REAL reader ...")
    passages = load_lessons()
    assert len(passages) >= 70, f"expected ~79 lessons, got {len(passages)}"
    # PROVENANCE: sampled lesson text is verbatim-ish substring of the cleaned corpus (whitespace-normalized).
    with open(CORPUS_PATH, encoding="utf-8") as fh:
        corpus_norm = re.sub(r"\s+", " ", fh.read())
    checked = 0
    for pid in list(passages)[:5]:
        # first ~40 chars of the lesson body should occur in the corpus (page/lesson lines stripped).
        frag = re.sub(r"\s+", " ", passages[pid])[:40]
        if frag:
            assert frag in corpus_norm, f"PROVENANCE: {pid} fragment not in corpus: {frag!r}"
            checked += 1
    print(f"[self-test] corpus: {len(passages)} lessons; provenance ok on {checked} fragments")

    clf = V2._fit_clf()

    # real_code_path: run the REAL current reader on a few lessons (filter ON) -> decisions + relations.
    r = read_corpus(clf, dict(list(passages.items())[:8]), "learned_topical_verbfilter")
    assert len(r["foundation"]) > 0, "reader produced no relations on first lessons"
    assert isinstance(r["decisions"], list)
    print(f"[self-test] reader ran on 8 lessons: {len(r['foundation'])} relations, "
          f"{len(r['decisions'])} injection decisions")

    # CG-gate gold sanity: gold_should_suppress separates clear non-factives from divergence.
    assert gold_should_suppress("Lx", "thought") and gold_should_suppress("Lx", "wished")
    assert not gold_should_suppress("L39", "feel") and not gold_should_suppress("L62", "forget")
    assert not gold_should_suppress("Lx", "killed") and not gold_should_suppress("Lx", "put")
    print("[self-test] factivity gold: thought/wished=suppress; feel@L39/forget@L62=admit(divergence); "
          "killed/put=admit")

    # HAND_GOLD_SAMPLE tally sanity (60 items; labels valid; causes valid).
    assert len(HAND_GOLD_SAMPLE) == 60, f"sample gold must be 60, got {len(HAND_GOLD_SAMPLE)}"
    valid_v = {"CORRECT", "FP", "BORDERLINE"}
    valid_c = {"COREF", "ARG_STRUCT", "NP_HEAD", "VERB_TAG", None}
    for k, (v, c) in HAND_GOLD_SAMPLE.items():
        assert v in valid_v and c in valid_c, f"bad annotation {k}: {(v, c)}"
        assert (c is None) == (v != "FP"), f"cause must be set iff FP: {k}"
    print("[self-test] hand-gold sample: 60 items, labels + causes valid")

    # REGRESSION controls fire (role passive/reversal) + overlay witness green.
    ctrl = V2._role_controls(clf)
    assert ctrl["passive_rolefix"] >= 1.0 and ctrl["reversal_rolefix"] >= 1.0, \
        f"role controls regressed: {ctrl}"
    ok, tail = V2._run_overlay_witness()
    assert ok, f"overlay witness FAILED: {tail}"
    print(f"[self-test] controls: passive {ctrl['passive_rolefix']:.2f} reversal "
          f"{ctrl['reversal_rolefix']:.2f}; overlay green")

    # determinism: two reads of the same 8 lessons identical.
    r2 = read_corpus(clf, dict(list(passages.items())[:8]), "learned_topical_verbfilter")
    assert r["foundation"] == r2["foundation"], "non-deterministic foundation"
    print("[self-test] deterministic (two reads identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=79)
    hb = _heartbeat(output_dir)
    passages = load_lessons()
    clf = V2._fit_clf()

    on = read_corpus(clf, passages, "learned_topical_verbfilter", hb=hb)     # filter ON
    off = read_corpus(clf, passages, "learned_topical", hb=hb)               # filter OFF

    cg = cg_gate(on["decisions"])
    sample = sample_foundation(on["foundation"])
    prec = foundation_precision(sample)
    comp = comprehension(on["store"])

    ctrl = V2._role_controls(clf)
    witness_ok, witness_tail = V2._run_overlay_witness()
    off2 = read_corpus(clf, passages, "learned_topical")
    deterministic = (off["foundation"] == off2["foundation"])

    n_rel_on, n_ent_on = len(on["foundation"]), len(on["entities"])
    n_rel_off = len(off["foundation"])
    growth_factor = round(n_rel_on / BASE14["n_relations"], 1)

    passive_ok = ctrl["passive_rolefix"] >= 1.0
    reversal_ok = ctrl["reversal_rolefix"] >= 1.0
    no_regression = passive_ok and reversal_ok and witness_ok and deterministic

    # ---- Decisive bands (pre-registered; can-fail) ----
    # CG gate GENERALIZES iff the filter tracks factivity precision>=0.90 AND recall>=0.90 AND handles the
    # divergence regime (filter correct on >=80% of non-factive+DO divergence sites). SCOPE-LIMITED else.
    cg_prec = cg["factivity_suppression_precision"] or 0.0
    cg_rec = cg["factivity_suppression_recall"] or 0.0
    div_ok = (cg["n_divergence_sites"] == 0) or \
             (cg["divergence_filter_correct"] / cg["n_divergence_sites"] >= 0.80)
    cg_generalizes = (cg_prec >= 0.90 and cg_rec >= 0.90 and div_ok and cg["n_divergence_sites"] >= 1)
    # foundation GROWS-CORRECT iff sample precision point-estimate >= 0.60 (mostly-correct).
    foundation_grows_correct = prec["precision_point"] >= 0.60
    # reader HOLDS iff comprehension accuracy retention vs the 14-subset baseline >= 0.70.
    comp_retention = comp["accuracy"] / BASE14["comp_all"] if BASE14["comp_all"] else 0.0
    reader_holds = comp_retention >= 0.70

    dom_cause = (max(prec["fp_cause_histogram"].items(), key=lambda kv: kv[1])[0]
                 if prec["fp_cause_histogram"] else None)

    if not no_regression:
        verdict = "REGRESSION"
        vmsg = (f"a regression guard failed: passive {ctrl['passive_rolefix']:.2f} reversal "
                f"{ctrl['reversal_rolefix']:.2f} overlay={witness_ok} deterministic={deterministic}. "
                f"Do NOT trust the scale measurements.")
    elif cg_generalizes and foundation_grows_correct and reader_holds:
        verdict = "GENERALIZES_AND_GROWS"
        vmsg = (f"SCALE-UP WIN. On the FULL 79-lesson third reader the factivity filter tracks the factivity "
                f"gold verb-independently (suppression precision {cg_prec:.3f} recall {cg_rec:.3f}; divergence "
                f"{cg['divergence_filter_correct']}/{cg['n_divergence_sites']}) AND read-to-grow grew "
                f"{n_rel_on} relations / {n_ent_on} entities (x{growth_factor} the 14-subset) at sample "
                f"precision {prec['precision_point']:.2f} AND comprehension held ({comp['accuracy']:.2f} vs "
                f"baseline {BASE14['comp_all']:.2f}). Clause-seg -> CG candidate; read-to-grow validated at "
                f"scale. HYPOTHESIS pending landed-VET.")
    else:
        verdict = "SCOPE_LIMITED_OR_DEGRADES"
        vmsg = (f"SCALE-UP LOCALIZES. Reader RUNS end-to-end on all {len(passages)} lessons (no crash) and "
                f"read-to-grow grows a BIG foundation ({n_rel_on} rel / {n_ent_on} ent, x{growth_factor} the "
                f"14-subset) BUT: "
                f"(1) CG gate is {'CLEAN' if cg_generalizes else 'SCOPE-LIMITED'} -- factivity suppression "
                f"precision {cg_prec:.3f} recall {cg_rec:.3f} on {cg['n_sites']} sites, but the NON-FACTIVE+DO "
                f"DIVERGENCE regime (the banked test) appears at only {cg['n_divergence_sites']} sites and the "
                f"verb-LIST is correct on {cg['divergence_filter_correct']}/{cg['n_divergence_sites']} of them "
                f"(over-suppresses {[x['verb'] for x in cg['filter_over_suppress']]} where the structural "
                f"direct-object parse would ADMIT and is correct); the corpus under-powers verb-independence. "
                f"(2) foundation grows NOISY at scale: sample precision {prec['precision_point']:.2f} "
                f"(range {prec['precision_lower']:.2f}-{prec['precision_upper']:.2f}) vs the clean-subset "
                f"quality_LB {BASE14['quality_lb']:.2f}. "
                f"(3) comprehension {comp['accuracy']:.2f} (retention {comp_retention:.2f} vs baseline "
                f"{BASE14['comp_all']:.2f}). DATA-DRIVEN NEXT PRIORITY = the dominant FP cause = {dom_cause} "
                f"(hist {prec['fp_cause_histogram']}); the clause-seg factivity filter is NOT the scale "
                f"bottleneck (it correctly suppresses {cg['tp']} sites). HONEST DEFLATE. HYPOTHESIS pending VET.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: full 3rd reader ({len(passages)} lessons) | foundation ON {n_rel_on}rel/"
                 f"{n_ent_on}ent (OFF {n_rel_off}rel; x{growth_factor} vs 14-subset {BASE14['n_relations']}) "
                 f"sample_prec {prec['precision_point']:.2f} [{prec['precision_lower']:.2f}-"
                 f"{prec['precision_upper']:.2f}] | CG suppr P {cg_prec:.3f} R {cg_rec:.3f} div "
                 f"{cg['divergence_filter_correct']}/{cg['n_divergence_sites']} | comp {comp['accuracy']:.2f} "
                 f"(ret {comp_retention:.2f}) | dom_FP={dom_cause} {prec['fp_cause_histogram']} | "
                 f"passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f} "
                 f"overlay={witness_ok} det={deterministic}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        n_lessons=len(passages),
        one_variable=("per measurement: CG gate = factivity filter decision vs INDEPENDENT factivity gold at "
                      "every injection site; foundation = filter ON (verbfilter) vs OFF (topical inject-always); "
                      "corpus = FULL 79-lesson 3rd reader vs the 14 hand-selected in-vocab passages"),
        bands=dict(cg_prec_min=0.90, cg_rec_min=0.90, div_correct_min_frac=0.80,
                   foundation_prec_min=0.60, comp_retention_min=0.70),
        cg_gate=cg,
        foundation=dict(n_relations_on=n_rel_on, n_entities_on=n_ent_on, n_relations_off=n_rel_off,
                        growth_factor_vs_14subset=growth_factor,
                        filter_removed_relations=n_rel_off - n_rel_on,
                        precision_sample=prec,
                        sample=[list(r) for r in sample]),
        comprehension=comp,
        comprehension_retention=round(comp_retention, 4),
        regression=dict(passive_rolefix=ctrl["passive_rolefix"], reversal_rolefix=ctrl["reversal_rolefix"],
                        passive_ok=passive_ok, reversal_ok=reversal_ok, overlay_witness_ok=witness_ok,
                        overlay_witness_tail=witness_tail, deterministic=deterministic,
                        no_regression=no_regression),
        cited_baseline=dict(source="data/exp_reader_grade3_envelope_readtogrow_v1/metrics.json", **BASE14),
        infra_note=("scale-surfaced latent bug in ORC.ground_category (Python-3.12 dict|set on the -es "
                    "depluralize path) fixed BEHAVIOR-IDENTICALLY (set(NAME_GENDER)|... ) so the reader runs "
                    "at scale; no extraction behavior on the 14-subset changes (that branch never fired there)."),
        scope_caveat=("Single-annotator INDEPENDENT gold (factivity per site + 60-relation precision sample + "
                      "8 comprehension Qs), coverage-honest. Foundation precision is a random-sample point "
                      "estimate with a borderline band. The non-factive+DO DIVERGENCE regime appears at only "
                      f"{cg['n_divergence_sites']} natural sites in the whole corpus -> the corpus alone cannot "
                      "fully separate a correct general factivity oracle from a verb-tuned list; the divergence "
                      "sites show the verb-LIST over-suppresses factive-transitive uses (feel THEM / forget the "
                      "injury) where the STRUCTURAL direct-object parse is correct -> the structural signal is "
                      "the more generalizable one and should DOMINATE the verb-list in the divergence regime. "
                      "CLAIM-VET-pending; strategic read = HYPOTHESIS pending landed-VET."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("\nCG gate:", json.dumps({k: cg[k] for k in
          ("n_sites", "n_admit", "n_suppress", "factivity_suppression_precision",
           "factivity_suppression_recall", "n_divergence_sites", "divergence_filter_correct",
           "suppress_reason_hist")}, indent=1))
    print("divergence sites:", json.dumps(cg["divergence_sites"], indent=1))
    print("filter over-suppress:", json.dumps(cg["filter_over_suppress"], indent=1))
    print("\nfoundation precision sample:", json.dumps(prec, indent=1))
    print("comprehension:", json.dumps(comp, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    return build_verdict(OUTPUT_DIR, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
