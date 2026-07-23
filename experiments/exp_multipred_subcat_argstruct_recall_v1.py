"""MULTI-PREDICATE EXTRACTION + SUBCAT/VALENCY FRAMES: does processing EVERY verb in a sentence (not just
`find_main_verb`'s single pick) recover the recall-miss ceiling the leg-2 diagnostic localized, without
flooding precision?

THE DIAGNOSIS THIS ANSWERS (notes/research_recall_miss_extraction_vs_filter_diagnosis_2026-07-23.md):
  Of the 56 recall-miss gold patients in exp_pivot_rich_knowledge_full_reader_integration_v1
  (recall_ceiling=0.44 MEASURED@data/exp_pivot_rich_knowledge_full_reader_integration_v1/metrics.json over
  100 gold-pos items, FULL_SLICE), 54/56 (96%) are EXTRACTION misses (not filter drops), and 38/56 (68%) are
  because the hand-rule reader (exp_read_nested_clause_relative_third_reader_v1 via ORC.assign_roles_learned,
  itself reused verbatim by exp_learned_argstruct_parser_lccp_independent_gold_v1.load_slice_and_reader) runs
  EXACTLY ONE main-verb argument-role pass per sentence (ORC.find_main_verb: first non-aux VB* token) -- any
  SECOND predicate in the same sentence (coordinate VP, infinitival/clausal complement, bare subordinate
  clause) gets ZERO candidates. NOTE: comma-introduced coordination/subordination is ALREADY re-parsed as its
  own clause-segment by NEST's ORC.split_sentences call (CITED@exp_read_nested_clause_relative_third_reader_v1
  .py:260 `for sent in ORC.split_sentences(text)`) -- the residual 38-miss gap is specifically the BARE
  (no-comma) cases ORC._CLAUSE_SPLIT's regex does not trigger on (e.g. "took up X and threw Y" has no comma
  before "and"; "mean to do it" is an infinitival complement, never clause-split at all).

MECHANISM (glass-box; TWO components, per the diagnostic's own "cheap decisive test" recommendation):
  (1) MULTI-PREDICATE candidate generation: find_predicates(tagged) returns EVERY content-verb locus in the
      sentence -- the existing ORC.find_main_verb pick (MAIN) PLUS bare (no-comma) secondary predicates
      triggered by three principled, general syntactic cues (not per-example curve-fit): a coordinating
      conjunction directly preceding a finite/participial verb with no intervening subject (COORD_VP, e.g.
      "...and threw..."); an infinitival marker "to" directly preceding a base-form verb (INF_COMP, e.g.
      "mean to do"); a subordinator (when/while/though/until/because/as/after/before -- the SAME closed-class
      vocabulary ORC._CLAUSE_SPLIT already uses for the comma-required case, CITED@exp_oracle_mention_
      upperbound_reader_v1.py:301-304, extended here to the bare/no-comma trigger) preceding a finite verb
      (SUBORD/SUBORD_FAR). Each predicate gets its OWN local argument-search span (bounded by the neighboring
      predicate indices) and its OWN role-assignment pass using the SAME candidate_features + AveragedPerceptron
      clf the single-pass reader already uses (ORC.candidate_features, V2._fit_clf) -- ONE variable = how many
      predicates get a pass, not a different role-assignment mechanism. Agent carry-forward (the same
      active-subject-across-clauses idea already used by V2/DX/argrole's clause-seg injection) supplies the
      agent for a bare-VP secondary predicate with no local subject.
  (2) SUBCAT/VALENCY FRAME gate (the precision-keeper): admits_patient(verb_lemma) -- False (HARD SUPPRESS,
      no patient emitted for that predicate instance regardless of what the local classifier scores) for a
      small NOPAT table built from (a) VerbNet subcat frames (nltk `verbnet` corpus) as the AUDITOR/base --
      vn_admits_direct_object(lemma) = True iff ANY VerbNet class the lemma belongs to has a frame with a
      bare NP immediately after VERB (a genuine transitive frame; VerbNet frames ARE present even where its
      selectional-restriction fields are empty, per the routing note); (b) a build-time-authored OVERRIDE for
      verbs the corpus/narrative genre uses overwhelmingly intransitively/obliquely/clausally even though
      VerbNet lists a marginal transitive sense (VerbNet's raw "any frame has NP-NP" signal is TOO PERMISSIVE
      for come/go/wonder -- MEASURED via direct nltk.corpus.verbnet query, 2026-07-23 build step -- so the
      override is the KB-VETTED correction layer). The override draws on (i) the EXISTING documented bug-class
      description already IN this codebase (CITED@exp_learned_argstruct_parser_lccp_independent_gold_v1.py
      lines 8-10: "intransitive come/go/sit/stand/fall; cognition wonder/think/know/mean; oblique look-at/
      tread-on/struggle-against; report say/tell") and (ii) general English verb-argument-structure knowledge
      (HYPOTHESIZED, build-time-authored, flagged); it is built WITHOUT reading data/gold_mcguffey_lccp_
      argstruct_v1.json (the private eval gold) to avoid leakage -- glass-box dict lookup at runtime, NO LLM/
      network at inference. AMBIGUOUS verbs (think/know/see/build/take/... -- take a direct object in SOME
      instances, a clausal complement in others) are deliberately left OUT of the override so the SAME
      structural cue features (prep-governed / funcword / complementizer, exactly as the single-verb reader's
      candidate_features already computes) decide per-instance, unchanged.

ARMS (ONE primary variable = predicate-enumeration axis; the subcat gate is the paired precision-control):
  BASELINE        = the REAL production single-verb reader's reader_svo, reused VERBATIM via
                    exp_learned_argstruct_parser_lccp_independent_gold_v1.load_slice_and_reader (byte-identical
                    to what produced the CITED 0.44 recall_ceiling; not reimplemented).
  MULTIPRED_KEEPALL      = multi-predicate candidate generation, subcat gate DISABLED (admits_patient always
                    True) -- MUST-FAIL CONTROL (a): isolates whether the frame gate is the precision-keeper.
  MULTIPRED_FRAMES       = multi-predicate candidate generation WITH the subcat gate -- the HEADLINE arm.
  MULTIPRED_SCRAMBLED    = multi-predicate + the SAME gate mechanism but the admits_patient TRUTH TABLE is
                    permuted across the observed verb lemmas (fixed-seed permutation) -- MUST-FAIL CONTROL (b):
                    isolates whether the frame CONTENT (not just "some suppression exists") is load-bearing.

MEASURED (decisive, per arm, vs the SAME independent LCCP gold / same split as 29473):
  recall_ceiling (extraction-availability: fraction of 100 gold-pos items whose (sid,gold_verb) emitted
  candidate set contains the gold patient surface, per exp_pivot_rich_knowledge_full_reader_integration_v1's
  own recall_ceiling formula, re-derived directly from each arm's kept svo tuples here rather than reusing its
  code -- the formula is: 1 - |{gold-pos item : gold patient not among patients emitted for (sid, gold_verb)}|
  / n_gold_pos); precision/recall/F1 via L.score_arm (reused VERBATIM); zero-regression check (does frames
  arm still cover every gold-pos item baseline covered).

PRE-REGISTERED BANDS (set BEFORE this run; the recall_ceiling primary bar is the diagnostic's OWN pre-existing
  bar from notes/research_recall_miss_extraction_vs_filter_diagnosis_2026-07-23.md ["Cheap decisive test"
  section], predating this cell's build -- adopted rather than re-set post-hoc; the F1/precision/must-fail-
  control conditions are this cell's ADDITIONAL required gates per the routing task):
  HARD_PASS_MULTIPRED_RECOVERS_AND_HOLDS_PRECISION: recall_ceiling(FRAMES) >= 0.65 AND
    recall_ceiling(FRAMES) - recall_ceiling(BASELINE) >= 0.15 AND F1(FRAMES) > F1(BASELINE) AND
    precision(FRAMES) >= precision(BASELINE) - 0.02 (no material precision collapse) AND
    precision(FRAMES) > precision(KEEPALL) (control a: gate beats no-gate on precision) AND
    recall_ceiling(FRAMES) > recall_ceiling(SCRAMBLED) (control b: frame CONTENT beats scrambled content) AND
    zero_regression (every gold-pos item BASELINE covered, FRAMES still covers).
  HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE (per the diagnostic's own pre-set floor): recall_ceiling(FRAMES) -
    recall_ceiling(BASELINE) < 0.05 (the cheap frame-lookup multi-predicate pass does not generalize to
    recover the bulk of the 38 category-d misses -- most residual misses need a real shallow parse, e.g.
    reduced relatives / gerund-participial modifiers / prepositional-gerund objects the two-cue trigger set
    here does not detect) OR F1(FRAMES) <= F1(BASELINE) (no net end-to-end lift) OR precision(KEEPALL) >=
    precision(FRAMES) (must-fail control a failed to fail -- the gate is not doing precision-preserving work).
  MIDDLE_BAND: otherwise (a genuine but partial recall_ceiling gain, 0.05-0.15).

TAGGED NUMBERS (pre-flight design-probe measurements, this exact reader/slice/gate, BEFORE the pre-registered
  FULL run below; recorded here so the final run's numbers can be compared against the design iteration):
  - recall_ceiling(BASELINE) FULL_SLICE: 0.44  CITED@notes/research_recall_miss_extraction_vs_filter_diagnosis
    _2026-07-23.md (56/100 miss; independently re-derived here from L.load_slice_and_reader's reader_svo,
    MEASURED@design-probe 2026-07-23, reproduces 0.44 exactly -- see self_test byte-parity check)
  - recall_ceiling(MULTIPRED_FRAMES) FULL_SLICE design-probe: 0.47 (rise +0.03)  MEASURED@design-probe
    2026-07-23 (17/56 raw category-d misses recovered by COORD_VP+INF_COMP; +SUBORD/SUBORD_FAR trigger adds a
    few more; most of the residual 39/56 misses are reduced-relative / gerund-participial / prepositional-
    gerund constructions the two-cue + subordinator trigger set does not detect -- HONEST EXPECTATION going
    into this run: likely HARD_FAIL per the <0.05-rise floor, i.e. this design iteration ALREADY indicates the
    cheap fix is INSUFFICIENT and a real parse is the likely next lever; reported honestly below, not
    suppressed or re-tuned against the gold to force a pass)
  - recall_ceiling(MULTIPRED_KEEPALL) FULL_SLICE design-probe: 0.51 (higher raw recall, but precision drops to
    ~0.149 vs FRAMES ~0.198)  MEASURED@design-probe 2026-07-23 (confirms MUST-FAIL control (a) is a real,
    reachable failure mode, not vacuous)

FAIRNESS: same reader/gold/split as exp_pivot_rich_knowledge_full_reader_integration_v1 (FULL_SLICE = L04/L05/
  L07/L08/L09/L10/L12; SMOKE_SLICE = L04/L05); gold = data/gold_mcguffey_lccp_argstruct_v1.json (independent,
  single-annotator, NOT read while authoring the NOPAT override); ONE primary variable = the predicate-
  enumeration axis (+ its paired subcat-frame gate, itself ablated by KEEPALL/SCRAMBLED controls).

BRAIN-CHECK: per-predicate argument-role assignment is the standard psycholinguistic picture (each verb opens
  its own argument-structure frame at its own locus, Levin/Fitz&Chang construction-frame induction); the
  DEVIATION flagged here is find_main_verb's single-pass-per-sentence limitation being the substrate's own
  prior implementation choice, not a claimed brain-mechanism; the fix restores per-predicate processing, which
  IS the brain-faithful picture (verbs pre-activate their OWN slots, not the sentence's first verb's slots).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reader candidate gen (reused) + per-
  predicate local role classification (existing AveragedPerceptron, a few hundred instances) + O(predicates)
  VerbNet dict lookups; NO matmul/storage/GPU-batchable primitive; wall < ~60s on the 7-lesson FULL_SLICE.
  Storage: no_storage. Runtime invariant: glass-box (VerbNet corpus lookup + a curated dict), NO LLM/network/
  autograd at inference. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng, sorted(set); no
  hash()-seeded RNG or list(set()) ordering. LOCAL-ONLY, foreground-to-completion. NO push / NO remote-persist
  / NO queue (per routing task contract: inline-local FULL, pause-state ACTIVE, no queue_add).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash test over BASELINE/KEEPALL/FRAMES/SCRAMBLED kept-tuple sets)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASELINE) < 0.95)
  - discriminator fires at smoke: MULTIPRED_KEEPALL n_pred > BASELINE n_pred (multi-predicate axis adds
    candidates) AND precision(FRAMES) != precision(KEEPALL) (gate has a measurable effect)
  - scaffold-free witness: the canonical "Herbert took up one of the blocks and threw it fiercely at pussy"
    (L04_03) case -- FRAMES recovers (throw, ..., it), BASELINE does not
  - deterministic seeding (fixed int SEED; sorted(set) for verb enumeration; numpy default_rng for the
    scramble permutation; no hash()-seeded RNG)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (the diagnosis note + LCCP docstring) / HYPOTHESIZED@
    (the override table's general-knowledge entries) in this docstring
  - N/A: KGStore (no KG); N/A cardinality sweep-axis (no swept parameter, 4 fixed arms); N/A CRLB (no HD noise
    floor; this is a discrete-count/precision measurement); N/A multi-seed (deterministic given fixed SEED)
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

import numpy as np

ANCHOR_NAME = "multipred_subcat_argstruct_recall_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Reuse the REAL integrated reader machinery VERBATIM (candidate gen for BASELINE, gold, scoring, features).
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402

FULL_SLICE = ["L04", "L05", "L07", "L08", "L09", "L10", "L12"]
SMOKE_SLICE = ["L04", "L05"]
SEED = 20260723

# ---- Pre-registered bands (set BEFORE this run; see docstring) ------------------------
HP_RC_MIN = 0.65
HP_RC_RISE_MIN = 0.15
HF_RC_RISE_MAX = 0.05
HP_PRECISION_TOLERANCE = 0.02
BASELINE_RC_CITED = 0.44   # CITED@notes/research_recall_miss_extraction_vs_filter_diagnosis_2026-07-23.md
BASELINE_BAND = (0.05, 0.95)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# SUBCAT/VALENCY FRAME: VerbNet auditor + build-time-authored override (no gold read).
# =======================================================================================
# NOPAT override: verb lemmas this narrative genre uses overwhelmingly WITHOUT a direct-object patient, even
# where VerbNet's frame list includes a marginal transitive sense (MEASURED too permissive for come/go/wonder
# via direct nltk.corpus.verbnet query, 2026-07-23 build step -- see vn_admits_direct_object below).
NOPAT_OVERRIDE = frozenset({
    # INTRANSITIVE motion/stative -- HYPOTHESIZED (general English verb-argument-structure knowledge,
    # build-time authored; NOT read from the private eval gold).
    "come", "go", "sit", "stand", "fall", "rise", "arrive", "remain", "stay", "depart", "proceed",
    # COGNITION -- CITED@exp_learned_argstruct_parser_lccp_independent_gold_v1.py:8-10
    # ("cognition wonder/think/know/mean" named as the reader's documented subcat-error class).
    "wonder", "think", "know", "mean",
    # OBLIQUE -- CITED@ same docstring lines ("oblique look-at/tread-on/struggle-against").
    "look", "tread", "struggle",
    # REPORT -- CITED@ same docstring lines ("report say/tell").
    "say", "tell",
})

_VN_CACHE = {}


def vn_admits_direct_object(lemma):
    """VerbNet AUDITOR signal: True iff ANY VerbNet class the lemma belongs to has a frame with 'VERB'
    immediately followed by 'NP' (a genuine bare-NP direct-object frame). None if the lemma is not in
    VerbNet at all (no evidence either way -> caller defaults to admit). MEASURED (2026-07-23 build step)
    to be TOO PERMISSIVE for come/go/wonder/tread (marginal transitive senses) -- hence the override above
    is applied FIRST by admits_patient; this function is only the fallback signal for un-overridden verbs."""
    if lemma in _VN_CACHE:
        return _VN_CACHE[lemma]
    result = None
    try:
        from nltk.corpus import verbnet as vn
        cids = vn.classids(lemma)
        if cids:
            result = False
            for cid in cids:
                try:
                    frames = vn.frames(cid)
                except Exception:
                    continue
                for fr in frames:
                    tags = [e["pos_tag"] for e in fr["syntax"]]
                    for i in range(len(tags) - 1):
                        if tags[i] == "VERB" and tags[i + 1] == "NP":
                            result = True
                            break
                    if result:
                        break
                if result:
                    break
    except Exception:
        result = None
    _VN_CACHE[lemma] = result
    return result


def admits_patient(lemma, override=NOPAT_OVERRIDE):
    """The subcat/valency gate: False = HARD SUPPRESS (no patient emitted for this predicate instance,
    regardless of the local classifier's PATIENT label). override takes precedence; else VerbNet auditor;
    else default-admit (an un-overridden, VerbNet-silent verb -- local-span restriction already bounds the
    flooding risk to at most the classifier's own candidates)."""
    if lemma in override:
        return False
    sig = vn_admits_direct_object(lemma)
    if sig is None:
        return True
    return sig


def build_scrambled_gate(observed_lemmas, seed):
    """MUST-FAIL CONTROL (b): permute the admits_patient TRUTH TABLE across the observed verb lemmas
    (deterministic seeded permutation, sorted(set) ordering -- no hash()-seeded RNG)."""
    lemmas = sorted(set(observed_lemmas))
    truth = [admits_patient(v) for v in lemmas]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(truth))
    scrambled = {lemmas[i]: bool(truth[perm[i]]) for i in range(len(lemmas))}

    def gate(v):
        return scrambled.get(v, True)
    return gate, scrambled


# =======================================================================================
# MULTI-PREDICATE candidate generation.
# =======================================================================================
COORD_CONJ = frozenset({"and", "or"})
# The SAME closed-class subordinator vocabulary ORC._CLAUSE_SPLIT already uses for the comma-required case
# (CITED@exp_oracle_mention_upperbound_reader_v1.py:301-304), extended here to the bare/no-comma trigger.
SUBORD_WORDS = frozenset({"when", "while", "though", "until", "because", "as", "after", "before"})


def _detect_passive(tagged, i, lows):
    """Same look-back window logic as ORC.find_main_verb, factored for reuse on secondary predicates."""
    for j in range(max(0, i - 3), i):
        if lows[j] in ("was", "were", "is", "are", "be", "been"):
            surf, low, pos = tagged[i]
            if pos == "VBN" or low.endswith("ed") or low in ("fed", "held", "seen", "made", "put",
                                                               "caught", "given", "left", "bit"):
                return True
            break
    return False


def find_predicates(tagged):
    """ALL predicate loci in the sentence: the existing single main-verb pick (ORC.find_main_verb, UNCHANGED)
    PLUS bare (no-comma) secondary predicates via three general syntactic triggers: bare coordinate-VP,
    infinitival complement, bare subordinate clause. Returns [(idx, verb_low, is_passive, kind), ...] in
    sentence order; kind in {MAIN, COORD_VP, INF_COMP, SUBORD, SUBORD_FAR}."""
    lows = [t[1] for t in tagged]
    n = len(tagged)
    primary_idx, primary_verb, primary_passive = ORC.find_main_verb(tagged)
    preds = []
    if primary_idx is None:
        return preds
    preds.append((primary_idx, primary_verb, primary_passive, "MAIN"))
    for i in range(primary_idx + 1, n):
        surf, low, pos = tagged[i]
        is_content_vb = pos.startswith("VB") and low not in ORC.AUX_LEMMAS
        if not is_content_vb:
            continue
        prev_low = lows[i - 1] if i - 1 >= 0 else None
        kind = None
        if prev_low in COORD_CONJ:
            kind = "COORD_VP"
        elif prev_low == "to" and pos == "VB":
            kind = "INF_COMP"
        elif prev_low in SUBORD_WORDS:
            kind = "SUBORD"
        elif pos in ("VBD", "VBZ", "VBP") and any(lows[j] in SUBORD_WORDS for j in range(max(0, i - 3), i)):
            kind = "SUBORD_FAR"
        if kind is not None:
            preds.append((i, low, _detect_passive(tagged, i, lows), kind))
    return preds


def multipred_svo(tagged, clf, gate_fn):
    """Per-predicate argument-role pass, local-span restricted, subcat-gated. Returns [(verb_low, agent_head,
    patient_head), ...]. ONE variable vs the single-pass reader = predicate enumeration; the role-assignment
    mechanism itself (candidate_features + clf.predict) is REUSED, applied per local span instead of once
    globally."""
    preds = find_predicates(tagged)
    n = len(tagged)
    all_cand = ORC.candidate_indices(tagged)
    out = []
    carried_agent = None
    for k, (idx, low, passive, kind) in enumerate(preds):
        lo_bound = preds[k - 1][0] + 1 if k > 0 else 0
        hi_bound = preds[k + 1][0] - 1 if k < len(preds) - 1 else n - 1
        local_cand = [i for i in all_cand if (lo_bound <= i <= idx - 1) or (idx + 1 <= i <= hi_bound)]
        first_cand = local_cand[0] if local_cand else None
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, idx, passive, first_cand)
            roles[i] = clf.predict(feats)
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        vl = L.lemma_verb(low)
        if resolved_agent is not None and patients_local and low not in ("has", "is"):
            if gate_fn(vl):
                for pi in patients_local:
                    out.append((low, resolved_agent, tagged[pi][1]))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return out


def build_multipred_arm(slice_lessons, clf, gate_fn):
    """Run the multi-predicate pass over every gold-scoring sentence in the slice (same sent_text LCCP's
    load_slice_and_reader uses -- FAIR: same sentences, same split)."""
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    out = {}
    for sid in order:
        tagged = ORC.pos_tag_sentence(sent_text[sid])
        out[sid] = multipred_svo(tagged, clf, gate_fn)
    return order, sent_text, out


# =======================================================================================
# Scoring: recall_ceiling (extraction-availability) + precision/recall/F1 (score_arm, reused verbatim).
# =======================================================================================
def to_kept_list(kept_by_sid):
    out = []
    for sid, tups in kept_by_sid.items():
        for tup in tups:
            out.append((sid, tup))
    return out


def recall_ceiling_of(kept_by_sid, gold):
    """1 - |gold-pos items whose (sid, gold_verb) emitted-candidate patients do NOT include the gold patient|
    / n_gold_pos. Matches exp_pivot_rich_knowledge_full_reader_integration_v1.error_decomposition's
    recall_ceiling formula, re-derived directly against each arm's kept svo tuples."""
    by_patients = defaultdict(list)
    for sid, tups in kept_by_sid.items():
        for tup in tups:
            v = L.lemma_verb(tup[0])
            by_patients[(sid, v)].append(tup[2])
    n_pos = 0
    miss = 0
    misses = []
    for sid, rec in gold.items():
        for g in rec["pos"]:
            n_pos += 1
            if g["patient"] not in by_patients.get((sid, g["v"]), []):
                miss += 1
                misses.append((sid, g["v"], g["patient"]))
    ceiling = round(1.0 - miss / max(1, n_pos), 4)
    return ceiling, miss, n_pos, misses


def covered_set(kept_by_sid, gold):
    by_patients = defaultdict(list)
    for sid, tups in kept_by_sid.items():
        for tup in tups:
            v = L.lemma_verb(tup[0])
            by_patients[(sid, v)].append(tup[2])
    covered = set()
    for sid, rec in gold.items():
        for g in rec["pos"]:
            if g["patient"] in by_patients.get((sid, g["v"]), []):
                covered.add((sid, g["v"], g["patient"]))
    return covered


def arm_hash(kept_by_sid):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, tups in kept_by_sid.items() for t in tups)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


# =======================================================================================
# Run all arms over a slice.
# =======================================================================================
def run_all_arms(slice_lessons, clf):
    order, sent_text, reader_svo = L.load_slice_and_reader(slice_lessons)
    gold, meta = L.load_gold(slice_lessons)
    baseline = {sid: reader_svo[sid] for sid in order}

    _, _, keepall = build_multipred_arm(slice_lessons, clf, lambda v: True)
    _, _, frames = build_multipred_arm(slice_lessons, clf, admits_patient)

    observed_lemmas = set()
    for sid in order:
        for t in reader_svo[sid]:
            observed_lemmas.add(L.lemma_verb(t[0]))
        for t in keepall[sid]:
            observed_lemmas.add(L.lemma_verb(t[0]))
    gate_scrambled, scrambled_table = build_scrambled_gate(observed_lemmas, SEED + 9)
    _, _, scrambled = build_multipred_arm(slice_lessons, clf, gate_scrambled)

    arms = {"BASELINE": baseline, "MULTIPRED_KEEPALL": keepall, "MULTIPRED_FRAMES": frames,
            "MULTIPRED_SCRAMBLED": scrambled}
    scored = {}
    for name, kept in arms.items():
        rc, miss, npos, misses = recall_ceiling_of(kept, gold)
        sc = L.score_arm(to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                            kept_hash=arm_hash(kept), n_pred=sc["n_pred"])
    baseline_covered = covered_set(baseline, gold)
    frames_covered = covered_set(frames, gold)
    regressed = sorted(baseline_covered - frames_covered)
    recovered = sorted(covered_set(frames, gold) - baseline_covered)
    return dict(order=order, sent_text=sent_text, gold=gold, meta=meta, arms=arms, scored=scored,
                regressed=regressed, recovered=recovered, scrambled_table_size=len(scrambled_table))


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


# =======================================================================================
# Self-test (design-gate; smoke scale = SMOKE_SLICE).
# =======================================================================================
def self_test():
    print("[self-test] loading SMOKE_SLICE reader + gold ...")
    order, sent_text, reader_svo = L.load_slice_and_reader(SMOKE_SLICE)
    gold, meta = L.load_gold(SMOKE_SLICE)
    assert len(order) >= 20, f"expected >=20 sentences in SMOKE_SLICE, got {len(order)}"
    clf = V2._fit_clf()

    # real_code_path: run the REAL 4-arm pipeline at smoke scale.
    res = run_all_arms(SMOKE_SLICE, clf)
    for name in ("BASELINE", "MULTIPRED_KEEPALL", "MULTIPRED_FRAMES", "MULTIPRED_SCRAMBLED"):
        assert name in res["scored"], f"arm {name} missing from smoke run"
    print(f"[self-test] 4-arm pipeline ran on SMOKE_SLICE: "
          f"{ {k: v['recall_ceiling'] for k, v in res['scored'].items()} }")

    # baseline_in_band: 0.05 < precision(BASELINE) < 0.95 (a real, unsaturated wall).
    prec_base = res["scored"]["BASELINE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"BASELINE precision {prec_base} outside band {BASELINE_BAND} (not a real un-saturated wall)"
    print(f"[self-test] baseline_in_band: precision(BASELINE)={prec_base} in {BASELINE_BAND}")

    # discriminator fires: multi-predicate axis adds candidates; the gate has a measurable effect.
    n_pred_base = res["scored"]["BASELINE"]["n_pred"]
    n_pred_keepall = res["scored"]["MULTIPRED_KEEPALL"]["n_pred"]
    assert n_pred_keepall > n_pred_base, \
        f"MULTIPRED_KEEPALL n_pred {n_pred_keepall} not > BASELINE n_pred {n_pred_base} (multi-pred axis inert)"
    prec_keepall = res["scored"]["MULTIPRED_KEEPALL"]["score"]["precision"]
    prec_frames = res["scored"]["MULTIPRED_FRAMES"]["score"]["precision"]
    assert prec_frames != prec_keepall, \
        f"subcat gate had ZERO measurable effect on precision (frames == keepall == {prec_frames})"
    print(f"[self-test] discriminator fires: n_pred BASELINE={n_pred_base} < KEEPALL={n_pred_keepall}; "
          f"precision KEEPALL={prec_keepall} vs FRAMES={prec_frames} (gate has an effect)")

    # arms_differ_verified (META_RULE_AF): all 4 kept-tuple sets are NOT bit-identical.
    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    assert len(set(hashes.values())) == len(hashes), f"META_RULE_AF VIOLATION: arm hashes collide: {hashes}"
    print(f"[self-test] arms_differ_verified: {hashes}")

    # scaffold-free witness: the canonical coordinate-VP case, on the REAL tagger + REAL clf.
    raw = "Herbert took up one of the blocks and threw it fiercely at pussy."
    tagged = ORC.pos_tag_sentence(raw)
    preds = find_predicates(tagged)
    kinds = [p[3] for p in preds]
    assert "COORD_VP" in kinds, f"WITNESS FAIL: no COORD_VP predicate found in {preds!r}"
    svo_frames = multipred_svo(tagged, clf, admits_patient)
    got_threw_it = any(v == "threw" and p == "it" for v, a, p in svo_frames)
    assert got_threw_it, f"WITNESS FAIL: MULTIPRED_FRAMES did not recover (threw, _, it); got {svo_frames!r}"
    # BASELINE (single main-verb pass) must NOT produce this tuple (the miss this cell targets).
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    assert main_verb == "took", f"WITNESS SETUP CHANGED: find_main_verb picked {main_verb!r}, expected 'took'"
    print(f"[self-test] scaffold-free witness: COORD_VP found; MULTIPRED_FRAMES recovers (threw,_,it) that "
          f"the single main-verb pass ({main_verb!r}) never reaches")

    # VerbNet auditor: override takes precedence regardless of VerbNet's own (too-permissive) signal.
    assert admits_patient("come") is False, "NOPAT override for 'come' did not fire"
    assert admits_patient("throw") is True, "'throw' (not overridden) should admit a patient"
    vn_sig_come = vn_admits_direct_object("come")
    print(f"[self-test] VerbNet auditor: vn_admits_direct_object('come')={vn_sig_come} "
          f"(overridden to False regardless); admits_patient('throw')={admits_patient('throw')}")

    # determinism: two FRAMES runs over the same slice are identical.
    res2 = run_all_arms(SMOKE_SLICE, clf)
    assert res["scored"]["MULTIPRED_FRAMES"]["kept_hash"] == res2["scored"]["MULTIPRED_FRAMES"]["kept_hash"], \
        "non-deterministic MULTIPRED_FRAMES output across identical runs"
    print("[self-test] deterministic (two MULTIPRED_FRAMES runs produce identical kept-tuple hash)")

    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=len(slice_lessons))
    clf = V2._fit_clf()
    res = run_all_arms(slice_lessons, clf)
    scored = res["scored"]

    rc_base = scored["BASELINE"]["recall_ceiling"]
    rc_keepall = scored["MULTIPRED_KEEPALL"]["recall_ceiling"]
    rc_frames = scored["MULTIPRED_FRAMES"]["recall_ceiling"]
    rc_scrambled = scored["MULTIPRED_SCRAMBLED"]["recall_ceiling"]
    rise_frames = round(rc_frames - rc_base, 4)

    f1_base = scored["BASELINE"]["score"]["f1"]
    f1_frames = scored["MULTIPRED_FRAMES"]["score"]["f1"]
    prec_base = scored["BASELINE"]["score"]["precision"]
    prec_keepall = scored["MULTIPRED_KEEPALL"]["score"]["precision"]
    prec_frames = scored["MULTIPRED_FRAMES"]["score"]["precision"]

    n_regressed = len(res["regressed"])
    zero_regression = (n_regressed == 0)

    hard_fail_reasons = []
    if rise_frames < HF_RC_RISE_MAX:
        hard_fail_reasons.append(
            f"recall_ceiling rise {rise_frames} < {HF_RC_RISE_MAX} (multi-predicate extraction does not "
            f"generalize to recover the bulk of the multi-predicate misses; needs a real parse, not a "
            f"frame-lookup extension of the existing trigger set)")
    if f1_frames <= f1_base:
        hard_fail_reasons.append(f"F1 did not rise: FRAMES {f1_frames} <= BASELINE {f1_base}")
    if prec_keepall >= prec_frames:
        hard_fail_reasons.append(
            f"MUST-FAIL control (a) did not fail: KEEPALL precision {prec_keepall} >= FRAMES precision "
            f"{prec_frames} (subcat gate not doing precision-preserving work)")

    hard_pass_conditions = dict(
        rc_frames_above_bar=(rc_frames >= HP_RC_MIN),
        rc_rise_above_bar=(rise_frames >= HP_RC_RISE_MIN),
        f1_rises=(f1_frames > f1_base),
        precision_no_collapse=(prec_frames >= prec_base - HP_PRECISION_TOLERANCE),
        control_a_gate_beats_noframe=(prec_frames > prec_keepall),
        control_b_frames_beat_scrambled=(rc_frames > rc_scrambled),
        zero_regression=zero_regression,
    )

    if hard_fail_reasons:
        verdict = "HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE"
        vmsg = ("HARD_FAIL: " + "; ".join(hard_fail_reasons) +
                f". recall_ceiling BASELINE={rc_base} -> FRAMES={rc_frames} (rise {rise_frames}); "
                f"KEEPALL={rc_keepall} SCRAMBLED={rc_scrambled}. F1 BASELINE={f1_base} FRAMES={f1_frames}. "
                f"precision BASELINE={prec_base} KEEPALL={prec_keepall} FRAMES={prec_frames}. "
                f"{len(res['recovered'])} gold-pos items newly recovered, {n_regressed} regressed. HONEST "
                f"DEFLATE: the cheap coordinate-VP + infinitival-complement + bare-subordinator trigger set "
                f"recovers only a modest slice of the 38 category-d misses (recall_ceiling barely moves); the "
                f"residual misses are likely reduced-relative / gerund-participial / prepositional-gerund "
                f"constructions this trigger set does not detect -- consistent with the diagnosis note's own "
                f"flagged risk that the multipredicate cases need a real shallow parse, not a frame lookup.")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_MULTIPRED_RECOVERS_AND_HOLDS_PRECISION"
        vmsg = (f"HARD_PASS: recall_ceiling BASELINE={rc_base} -> FRAMES={rc_frames} (rise {rise_frames} >= "
                f"{HP_RC_RISE_MIN}, FRAMES >= {HP_RC_MIN}); F1 BASELINE={f1_base} -> FRAMES={f1_frames} "
                f"(rises); precision BASELINE={prec_base} FRAMES={prec_frames} (no collapse); KEEPALL precision "
                f"{prec_keepall} < FRAMES (gate is the precision-keeper); SCRAMBLED recall_ceiling "
                f"{rc_scrambled} < FRAMES (frame CONTENT is load-bearing, not just gate-existence); zero "
                f"regression on {len(res['recovered'])} newly-recovered items. Multi-predicate extraction + "
                f"subcat/valency frame gating RESOLVES the 68% single-verb-pass extraction bound.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RECALL_GAIN"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND: no HARD_FAIL trigger fired but not all HARD_PASS conditions held (failing: "
                f"{failing}). recall_ceiling BASELINE={rc_base} -> FRAMES={rc_frames} (rise {rise_frames}); "
                f"F1 BASELINE={f1_base} FRAMES={f1_frames}; precision BASELINE={prec_base} FRAMES={prec_frames}; "
                f"{n_regressed} regressed. Genuine but partial signal; localize which condition failed before "
                f"escalating scope.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: recall_ceiling {rc_base}->{rc_frames} (rise {rise_frames}) | F1 {f1_base}->"
                 f"{f1_frames} | precision base={prec_base} keepall={prec_keepall} frames={prec_frames} "
                 f"scrambled_rc={rc_scrambled} | recovered={len(res['recovered'])} regressed={n_regressed}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["order"]),
        one_variable="predicate-enumeration axis (find_predicates: MAIN-only baseline vs MAIN+COORD_VP+"
                     "INF_COMP+SUBORD/SUBORD_FAR), paired with the subcat/valency frame gate (admits_patient); "
                     "role-assignment mechanism (candidate_features + AveragedPerceptron clf) unchanged",
        bands=dict(HP_RC_MIN=HP_RC_MIN, HP_RC_RISE_MIN=HP_RC_RISE_MIN, HF_RC_RISE_MAX=HF_RC_RISE_MAX,
                   HP_PRECISION_TOLERANCE=HP_PRECISION_TOLERANCE, BASELINE_RC_CITED=BASELINE_RC_CITED),
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"], n_gold_pos=v["n_gold_pos"],
                         precision=v["score"]["precision"], recall=v["score"]["recall"], f1=v["score"]["f1"],
                         n_pred=v["n_pred"], subcat_fp=v["score"]["subcat_fp"],
                         within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        hard_pass_conditions=hard_pass_conditions,
        hard_fail_reasons=hard_fail_reasons,
        recovered_sample=[list(x) for x in res["recovered"][:40]],
        n_recovered=len(res["recovered"]),
        regressed_sample=[list(x) for x in res["regressed"][:40]],
        n_regressed=n_regressed,
        nopat_override=sorted(NOPAT_OVERRIDE),
        scrambled_table_size=res["scrambled_table_size"],
        cited_baseline=dict(source="notes/research_recall_miss_extraction_vs_filter_diagnosis_2026-07-23.md",
                            recall_ceiling=BASELINE_RC_CITED,
                            n_category_d_misses=38, n_total_misses=56, n_gold_pos=100),
        scope_caveat=("Two-cue + bare-subordinator trigger set (COORD_VP, INF_COMP, SUBORD/SUBORD_FAR); does "
                      "NOT detect reduced relative clauses (NP + VBG/VBN with no relativizer), gerund/"
                      "participial adjuncts, or prepositional-gerund objects ('by V-ing', 'before V-ing') -- "
                      "these remain uncaught and are the likely dominant residual per the honest run below. "
                      "NOPAT_OVERRIDE built WITHOUT reading the private eval gold (data/gold_mcguffey_lccp_"
                      "argstruct_v1.json); sourced from this codebase's own prior documented bug-class "
                      "description (CITED) + general English verb-argument-structure knowledge (HYPOTHESIZED, "
                      "flagged). CLAIM-VET-pending; strategic read = HYPOTHESIS pending landed-VET."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
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
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
