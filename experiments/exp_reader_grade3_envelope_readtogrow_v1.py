"""
READER ENVELOPE (grade-2 -> grade-3) + FIRST READ-TO-GROW STEP. Does the VET-confirmed grade-2 reader
(fixed coref [agreement+salience] + hand-rule grounded mention detector + learned role-assigner +
composition + Q-engine) HOLD on the HARDER 3rd McGuffey Reader (longer, multi-clause syntax, more
entities), and does READING it GROW a correct relation foundation? ONE variable = GRADE / SYNTAX
(2nd-reader baseline vs 3rd-reader). The reader pipeline is BYTE-IDENTICAL across arms -- only the
input corpus changes.

WHY (a working-enough reader now EXISTS; tick the read-textbook-after-textbook step):
  The end-to-end reader is VET-CONFIRMED on REAL grade-2 McGuffey NARRATIVE
  (handrule + fixed coref: comprehension all=0.7419, CMP=0.8125, RELF1 F1=0.488 R=0.833, ref=0.8529;
   MEASURED@data/exp_reader_mention_source_gold_vs_handrule_corefixed_v1/metrics.json:arms.handrule_mentions).
  SCOPE = in-grounding-vocab, grade-2, small corpus. The tick: WHEN a working-enough reader exists,
  begin reading the NEXT rung (3rd reader = harder syntax, still narrative, mostly in-vocab).

ONE VARIABLE = grade (corpus). Both arms run the SAME reader (handrule mentions + agreement+topical
coref + learned role-assigner + relation emission + comprehension Q-engine), imported VERBATIM from the
confirmed cell. An anti-copy-divergence self-test asserts my dataset-parameterized extract ==
CFX.extract_passage_cfg_mm BYTE-IDENTICALLY on the 2nd-reader data (the ONLY change vs CFX: the passage
set + gold-mention dict that build `known` and gate oracle-mode are PARAMETERS instead of the hardcoded
ORC 2nd-reader globals). The reader is NOT re-tuned for the 3rd reader (no new names added to the
grounding dict, no coref/mention/extractor changes).

  second_reader (BASELINE / POSITIVE CONTROL) : CFX.run_arm("handrule_mentions") on ORC 2nd-reader data.
                                                MUST reproduce all=0.7419, ref=0.8529, RELF1 F1=0.488.
  third_reader  (THE ENVELOPE TEST)           : the same reader on REAL 3rd-reader passages (verbatim;
                                                provenance-verified) + INDEPENDENT hand-authored gold.

MEASURE {2nd vs 3rd}: comprehension `all` + slices (NC/CO/CMP), ref-acc (coref), RELF1 (P / R / F1 --
does extraction HOLD on richer syntax or DROP toward the 0.44 hand-rule wall?). RELF1 gold is a SPARSE
salient-relation annotation, so PRECISION is gold-coverage-limited (a true-but-unannotated relation is
penalized); the LOAD-BEARING signals are RELF1 RECALL + comprehension + ref-acc (COMPLETE gold).

READ-TO-GROW (secondary; the first read-to-build-the-foundation measurement): accumulate the reader's
EXTRACTED svo/loc/poss relations across the 3rd-reader passages into a foundation; report GROWTH
(# relations / # entities, from an empty start) + a QUALITY spot-estimate (micro-precision on the
gold-annotated passages = a COVERAGE-LIMITED LOWER BOUND on correctness; many non-gold relations are
true-but-unannotated). HONEST -- fair-oracle lower bound, not inflated.

BRANCHES (decisive either way; genuinely can-fail):
  HOLDS    = 3rd comprehension + RELF1-recall + ref-acc stay CLOSE to 2nd (degrade gracefully) -> the
             reader GENERALIZES across grades = scope expands toward CG; read-to-grow accumulates
             (mostly) correct relations = the foundation grows.
  DEGRADES = 3rd comprehension / extraction COLLAPSES vs 2nd -> harder syntax breaks it -> LOCALIZE
             (parsing multi-clause? coref more entities? extraction precision?) + brain-check (a learned
             construction inventory handles richer syntax; a hand-rule extractor may wall = the
             learned-parser lever, re-evaluated). DEFLATE honestly.
  PARTIAL  = holds on some axes, degrades on others -> localize.

HONEST SCOPE CAVEAT (reported, load-bearing): 3rd-reader PASSAGES are SELECTED to be mostly-in-vocab
(protagonist names already grounded OR common person-nouns) so the ONE variable is SYNTAX not
vocab-coverage. This BIASES toward HOLDS: out-of-scope 3rd-reader material (new ungrounded names,
poetry, 100+word sentences) is EXCLUDED BY SELECTION and remains UNTESTED. A HOLDS verdict = "holds on
the in-vocab narrative slice", NOT "generalizes to the whole 3rd reader". Vocab coverage is reported.

DESIGN-GATE (verified at self-test/smoke BEFORE any full interpretation; USER: fair tests every time):
  (1) POSITIVE-CONTROL: second_reader arm reproduces the confirmed handrule baseline (all/ref/RELF1).
  (2) REAL 3rd-reader passages (verbatim; every clause a substring of the cleaned corpus file).
  (3) INDEPENDENT gold: comprehension + antecedents + relations hand-authored by reading (anti-circular;
      NOT copied from the extractor output).
  (4) ONE variable = grade (corpus); reader BYTE-IDENTICAL (anti-copy-divergence self-test vs CFX).
  (5) CAN-FAIL: 3rd could collapse (harder syntax) -- genuinely reachable + informative.
  (6) DIFFICULTY-ON: real 3rd-reader syntax (coordinated multi-clause), more entities, natural coref.
  (7) determinism OMP=1, fixed seed, sorted(set); read-to-grow quality = honest coverage-limited bound.

Glass-box (POS + tiny perceptron + symbolic coref/query; NO external LLM; NO torch/GPU at runtime).
Local / foreground-to-completion. NO push / NO remote-persist. Reported CLAIM-VET-pending (NOT
self-declared chain-grade); strategic read reported as hypothesis-pending-VET.

ANCHOR: reader_grade3_envelope_readtogrow_v1
BASELINE: confirmed handrule reader (4ec1a4c20; VET a237d1f3). CORPUS: 3rd = mcguffey_third_reader.clean.txt
  (PG#14766, PD); 2nd = mcguffey_second_reader.clean.txt (via ORC). COMPUTE: sequential-CPU; wall < 120s.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                        [META_RULE_AF]
# - discriminator CAN-FAIL (3rd can hold OR collapse)          [design-gate]
# - POSITIVE-CONTROL: 2nd-reader arm reproduces the confirmed baseline [reproduce_prior / Gate D]
# - anti-copy-divergence: dataset-parameterized extract == CFX byte-identical on 2nd-reader data [F.1]
# - deterministic seeding (fixed int seed, fixed order, sorted set)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay + REAL perceptron fit +
#   REAL POS tagger + the REAL handrule gate on REAL 3rd-reader passages [F.1]
# - substrate_signature: binds WorkingOverlay.resolve_pronoun sig (prefer_agreement/prefer_topical) [F.2]
# - PROVENANCE: every 3rd-reader clause is a verbatim substring of the cleaned corpus file
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - all reported numbers MEASURED@this metrics.json; baseline CITED@CFX metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import re
import json
import time
import argparse
import hashlib
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the confirmed reader pipeline VERBATIM. CFX = the VET-confirmed handrule+fixed-coref reader
# (imports ORC = the passages/gold/scorers + SAL = the coref-fixed helpers). The ONLY thing this cell
# changes vs CFX is the INPUT CORPUS (2nd -> 3rd reader) + its independent gold; the reader CODE is
# byte-identical (asserted in self_test).
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_mention_source_gold_vs_handrule_corefixed_v1 as CFX  # noqa: E402
from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE      # noqa: E402

# coref-fixed helpers (VERBATIM from the salience cell, via CFX) -- NOT re-tuned.
_prefers_topical = CFX._prefers_topical
_agreement_attrs = CFX._agreement_attrs
_RESOLVABLE = CFX._RESOLVABLE
_RESOLVABLE_SO = CFX._RESOLVABLE_SO
_RESOLVABLE_POSS = CFX._RESOLVABLE_POSS

ANCHOR_NAME = "reader_grade3_envelope_readtogrow_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
CORPUS3_PATH = os.path.join(REPO, "data", "corpora", "graded_readers_graded", "cleaned",
                            "mcguffey_third_reader.clean.txt")
CFX_METRICS = os.path.join(REPO, "data", "exp_reader_mention_source_gold_vs_handrule_corefixed_v1",
                           "metrics.json")
SEED = 12345

# ---- Confirmed 2nd-reader handrule baseline (CITED@CFX_METRICS:arms.handrule_mentions) -----------
# POSITIVE CONTROL: the second_reader arm must reproduce these exactly (same code + data as CFX).
BASE = dict(all=0.7419, NC=0.7143, CO=0.6667, CC=0.6000, CMP=0.8125,
            ref_acc=0.8529, RELF1_f1=0.488, RELF1_recall=0.833, RELF1_prec=0.345)
BASE_TOL = 0.005

# ---- Pre-registered envelope bands (set BEFORE the final run; HYPOTHESIZED@this prereg) ----------
# Primary = 3rd-reader comprehension `all` retention vs the 2nd-reader baseline, corroborated by
# RELF1 recall (extraction) + ref_acc (coref). Bands can-fail both ways; BOUND-first classification.
HOLDS_RETENTION_MIN = 0.80    # 3rd `all` >= 0.80 * 2nd `all`  (>= ~0.594)
HOLDS_RELF1_RECALL_MIN = 0.65 # AND 3rd RELF1 micro-recall >= 0.65
HOLDS_REF_MIN = 0.70          # AND 3rd ref_acc >= 0.70
DEGRADE_RETENTION_MAX = 0.55  # 3rd `all` <= 0.55 * 2nd `all`  (<= ~0.408) OR ...
DEGRADE_RELF1_RECALL_MAX = 0.40  # ... RELF1 recall collapses toward the 0.44 wall OR ...
DEGRADE_REF_MAX = 0.45        # ... coref collapses
TELEMETRY_MIN_MOVE = 0.02     # swapping corpus must MOVE at least one metric (arms are not identical)

# =======================================================================================
# REAL McGuffey THIRD READER passages (VERBATIM; provenance-verified per clause). SELECTED to be
# mostly-in-vocab (protagonist names already in the grounding dict OR common person-nouns) so the ONE
# variable is SYNTAX not vocab-coverage (see HONEST SCOPE CAVEAT in the docstring). Real grade-3
# narrative prose (coordinated multi-clause sentences, more entities); poems + new-name + very-long
# sentences are OUT OF SCOPE by selection. Each cites its LESSON. NOT authored (real text).
G3_PASSAGES = {
    # LESSON VII THE TRUANT -- non-competitive coref his/him->james; possession
    "L7_james": "James Brown was ten years old when his parents sent him to school. It was not far "
                "from his home, and therefore they sent him by himself.",
    # LESSON VII -- cataphoric 'his mother told James' (hard: antecedent follows the pronoun)
    "L7b_james": "One fine morning, his mother told James to make haste home from school.",
    # LESSON XXXIV GEORGE'S FEAST -- possessive 's (structural, no coref)
    "L34_geo1": "George's mother was very poor.",
    # LESSON XXXIV -- cross-clause coref his->george over several clauses + possession
    "L34_geo2": "George worked very hard; so that by the time the sun was high, he was hot, and wished "
                "for a cool place where he might rest and eat his dinner.",
    # LESSON XXXIV -- cross-clause coref he->george (mother is a recent competitor) + action verbs
    "L34_geo3": "George thought of all this, and just as he was lifting the first strawberry to his "
                "mouth, he said to himself, \"How much mother would like these;\" and he stopped, and "
                "put the strawberry back again.",
    # LESSON XIII THE WOLF -- coordinated svo (the second verb is orphaned from its subject by the split)
    "L13_wolf2": "The wolf broke into the flock, and killed a great many sheep.",
    # LESSON XIII -- competitive coref him->john (wolf is the recent competitor); coref-only passage
    "L13_wolf3": "On the third day, the wolf came in earnest. John cried in dismay, \"Help! help! the "
                 "wolf! the wolf!\" But not a single man came to help him.",
    # LESSON LXVII SUSIE AND ROVER -- within-sentence coref her->susie + possession + svo
    "L67_susie1": "Susie brought her little basket, and her mother put up a nice lunch for her.",
    # LESSON LXVII -- within-sentence coref she/her->susie + possession
    "L67_susie2": "Susie began to feel hungry, and thought she would eat her lunch.",
    # LESSON LVIII JOHN CARPENTER -- possessive 's (friend's horse) + coref his/he->john
    "L58_john1": "John was soon admiring his friend's horse; and he was examining it carefully, to see "
                 "how it was made.",
    # LESSON LX THE CONTENTED BOY -- single-hop svo (common person-noun 'boy', no coref)
    "L60_boy": "A little boy at work in a field near the road, heard the horse.",
}

# INDEPENDENT gold RELATION triples (hand-annotated TRUTH by reading; anti-circular; NOT emitted by the
# extractor). Canonical forms: ("svo", verb, agent, patient) ; ("loc", figure, ground) ;
# ("poss", owner, owned). SPARSE salient annotation (precision is gold-coverage-limited). Passages used
# ONLY for coref/telemetry (L13_wolf3) are omitted from RELF1.
G3_GOLD_RELS = {
    "L7_james":  [("poss", "james", "parents"), ("poss", "james", "home")],
    "L7b_james": [("poss", "james", "mother")],
    "L34_geo1":  [("poss", "george", "mother")],
    "L34_geo2":  [("poss", "george", "dinner")],
    "L34_geo3":  [("svo", "lifting", "george", "strawberry"), ("svo", "put", "george", "strawberry")],
    "L13_wolf2": [("svo", "killed", "wolf", "sheep")],
    "L67_susie1": [("svo", "brought", "susie", "basket"), ("poss", "susie", "basket"),
                   ("poss", "susie", "mother"), ("svo", "put", "mother", "lunch")],
    "L67_susie2": [("poss", "susie", "lunch")],
    "L58_john1": [("poss", "friend", "horse")],
    "L60_boy":   [("svo", "heard", "boy", "horse")],
}

# INDEPENDENT gold ANTECEDENTS (truth), one entry per RESOLVABLE pronoun in text order (matches the
# res_by_pos scorer's positional alignment). Truth by reading -- NOT the extractor's output.
G3_GOLD_ANTECEDENTS = {
    "L7_james":  [("his", "james"), ("him", "james"), ("it", "school"), ("his", "james"),
                  ("they", "parents"), ("him", "james")],
    "L7b_james": [("his", "james")],
    "L34_geo1":  [],
    "L34_geo2":  [("he", "george"), ("he", "george"), ("his", "george")],
    "L34_geo3":  [("he", "george"), ("his", "george"), ("he", "george"), ("he", "george")],
    "L13_wolf2": [],
    "L13_wolf3": [("him", "john")],
    "L67_susie1": [("her", "susie"), ("her", "susie"), ("her", "susie")],
    "L67_susie2": [("she", "susie"), ("her", "susie")],
    "L58_john1": [("his", "john"), ("he", "john"), ("it", "horse"), ("it", "horse")],
    "L60_boy":   [],
}

# Comprehension questions on REAL 3rd-reader passages. slice in {NC, CO, CMP}. Each carries an
# arm-independent query spec (never contains the answer) + independent gold. NC=no coref on the answer
# path (structural 's / nominal args); CO=one non-competitive same-sentence coref; CMP=cross-clause/
# sentence coref join OR 2 relations. Competitive-coref evidence is reported via ref_acc (see caveat).
G3_QS = [
    # ---- NC: no coref on the answer path ----
    dict(qid="N1", p="L34_geo1", slice="NC", atype="AGENT", spec=("has_owner", "mother"),
         gold="george", text="Whose mother was poor?"),
    dict(qid="N2", p="L58_john1", slice="NC", atype="AGENT", spec=("has_owner", "horse"),
         gold="friend", text="Whose horse was John admiring?"),
    dict(qid="N3", p="L67_susie1", slice="NC", atype="PATIENT", spec=("svo_patient", "brought", "susie"),
         gold="basket", text="What did Susie bring?"),
    dict(qid="N4", p="L60_boy", slice="NC", atype="PATIENT", spec=("svo_patient", "heard", "boy"),
         gold="horse", text="What did the boy hear?"),
    dict(qid="N5", p="L13_wolf2", slice="NC", atype="PATIENT", spec=("svo_patient", "killed", "wolf"),
         gold="sheep", text="What did the wolf kill?"),
    dict(qid="N6", p="L67_susie1", slice="NC", atype="PATIENT", spec=("svo_patient", "put", "mother"),
         gold="lunch", text="What did the mother put up?"),
    # ---- CO: one non-competitive same-sentence coref ----
    dict(qid="O1", p="L7_james", slice="CO", atype="AGENT", spec=("svo_agent", "sent", "james"),
         gold="parents", text="Who sent James to school?"),
    dict(qid="O2", p="L7_james", slice="CO", atype="AGENT", spec=("has_owner", "parents"),
         gold="james", text="Whose parents sent him to school?"),
    dict(qid="O3", p="L7_james", slice="CO", atype="AGENT", spec=("has_owner", "home"),
         gold="james", text="Whose home was the school near?"),
    dict(qid="O4", p="L67_susie1", slice="CO", atype="AGENT", spec=("has_owner", "mother"),
         gold="susie", text="Whose mother put up the lunch?"),
    dict(qid="O5", p="L67_susie2", slice="CO", atype="AGENT", spec=("has_owner", "lunch"),
         gold="susie", text="Whose lunch was it?"),
    dict(qid="O6", p="L7b_james", slice="CO", atype="AGENT", spec=("has_owner", "mother"),
         gold="james", text="Whose mother told James to hurry?"),
    # ---- CMP: cross-clause coref join OR 2 relations ----
    dict(qid="M1", p="L34_geo2", slice="CMP", atype="AGENT", spec=("has_owner", "dinner"),
         gold="george", text="Whose dinner was to be eaten?"),
    dict(qid="M2", p="L34_geo3", slice="CMP", atype="PATIENT", spec=("svo_patient", "lifting", "george"),
         gold="strawberry", text="What was George lifting?"),
    dict(qid="M3", p="L34_geo3", slice="CMP", atype="AGENT", spec=("svo_agent", "put", "strawberry"),
         gold="george", text="Who put the strawberry back?"),
]

# Grounding-dict names present vs absent (reported vocab-coverage telemetry; NOT a gate).
IN_DICT_NAMES = set(ORC.NAME_GENDER)


# =======================================================================================
# DATASET-PARAMETERIZED extract: EXACT copy of CFX.extract_passage_cfg_mm with the passage set +
# gold-mention dict as PARAMETERS (CFX hardcodes ORC.TEST_PASSAGES / ORC.GOLD_MENTIONS). Those two
# are DATA (they build `known` + gate oracle-mode), NOT reader logic. self_test asserts byte-identity
# vs CFX on the 2nd-reader data -> the reader CODE is unchanged; only the corpus differs.
# =======================================================================================
def extract_passage_ds(passage_text, clf, pid, passages_dict, gold_mentions_dict,
                       fix_possessive, agreement, topical, mention_mode):
    """Coref pass + role assignment + relation emission on ONE passage. Body byte-identical to
    CFX.extract_passage_cfg_mm EXCEPT ORC.TEST_PASSAGES->passages_dict and
    ORC.GOLD_MENTIONS->gold_mentions_dict (the ONE-VARIABLE corpus swap)."""
    gold_heads = gold_mentions_dict.get(pid, frozenset())
    coref_strategy = ORC.FIXED_COREF_STRATEGY
    pref = bool(agreement)

    known = set()
    for txt in list(passages_dict.values()):
        for s in ORC.split_sentences(txt):
            for _su, lo, _po in ORC.pos_tag_sentence(s):
                if ORC.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))

    rels = []
    res_by_pos = {}
    offset = 0
    for sent in ORC.split_sentences(passage_text):
        tagged = ORC.pos_tag_sentence(sent)
        pron_res = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:
                if low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    pron_res[i] = ent.head if ent is not None else None
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in ORC.PRONOUNS_POSS:
                pass
            else:
                if not ORC.observe_as_mention(low, pos, mention_mode, gold_heads):
                    continue
                is_name = (low in ORC.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                if agreement:
                    g, num, anim = _agreement_attrs(low, pos, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name, animacy=anim)
                else:
                    g, num = ORC.grounded_gender_number(low, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name)

        roles, verb_idx, verb, passive, cand = ORC.assign_roles_learned(
            tagged, clf, mention_mode, gold_heads)

        def head_of(i):
            surf, low, pos = tagged[i]
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            return low

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)
        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                rels.append(("svo", verb, head_of(agents[0]), head_of(pi)))
        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or ORC.prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        rels.append(("svo", "kind", subj_head, head_of(i)))
        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        rels.append(("poss", head_of(owner_idx), head_of(pi)))
        for ri in recips:
            if verb is not None and agents:
                rels.append(("recipient", verb, head_of(agents[0]), head_of(ri)))
        for li in locs:
            figure = subj_head
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
            if figure is not None and figure != head_of(li):
                rels.append(("loc", figure, head_of(li)))

        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in ORC.PRONOUNS_POSS:
                if fix_possessive and low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    owner = pron_res.get(i)
                    owner = owner if owner is not None else low
                elif low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
                if low in _RESOLVABLE:
                    res_by_pos[offset + i] = (low, owner if owner != low else None)
        for i in range(len(tagged) - 1):
            if ORC.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break

        for i, (surf, low, pos) in enumerate(tagged):
            if low in _RESOLVABLE_SO and low not in _RESOLVABLE_POSS:
                res_by_pos[offset + i] = (low, pron_res.get(i))

        offset += len(tagged)

    sorted_rels = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return sorted_rels, res_by_pos


# =======================================================================================
# 3rd-reader dataset scorers (mirror ORC/CFX; over G3_* gold instead of ORC globals).
# =======================================================================================
def _relf1_g3(store):
    tot_tp = tot_ex = tot_go = 0
    per_p = {}
    for pid in G3_GOLD_RELS:
        p, r, f1, tp, ngo = ORC.rel_prf(store[pid], G3_GOLD_RELS[pid])
        per_p[pid] = dict(precision=round(p, 3), recall=round(r, 3), f1=round(f1, 3),
                          tp=tp, n_gold=ngo, extracted=[list(x) for x in store[pid]])
        ex_k = set(x for x in store[pid] if x[0] in ("svo", "loc", "poss"))
        go_k = set(x for x in G3_GOLD_RELS[pid] if x[0] in ("svo", "loc", "poss"))
        tot_tp += len(ex_k & go_k)
        tot_ex += len(ex_k)
        tot_go += len(go_k)
    P = tot_tp / tot_ex if tot_ex else 0.0
    R = tot_tp / tot_go if tot_go else 0.0
    F = 2 * P * R / (P + R) if (P + R) > 0 else 0.0
    return dict(micro_precision=round(P, 3), micro_recall=round(R, 3), micro_f1=round(F, 3),
                tp=tot_tp, n_extracted=tot_ex, n_gold=tot_go, per_passage=per_p)


def _slices_g3(correct):
    d = {}
    for sl in ("NC", "CO", "CMP"):
        idx = [i for i, q in enumerate(G3_QS) if q["slice"] == sl]
        d[sl] = round(sum(correct[i] for i in idx) / len(idx), 4) if idx else 0.0
        d["n_" + sl] = len(idx)
    d["all"] = round(sum(correct) / len(correct), 4) if correct else 0.0
    return d


def run_third(clf):
    """The confirmed reader (handrule + agreement + topical) on the REAL 3rd-reader passages."""
    store = {}
    res_by_pos = {}
    for pid, text in G3_PASSAGES.items():
        rels, rbp = extract_passage_ds(text, clf, pid, G3_PASSAGES, {p: frozenset() for p in G3_PASSAGES},
                                       fix_possessive=True, agreement=True, topical=True,
                                       mention_mode="handrule")
        store[pid] = rels
        res_by_pos[pid] = rbp
    correct = []
    answers = []
    for q in G3_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = _relf1_g3(store)
    slices = _slices_g3(correct)
    # ref-acc (coref) over G3_GOLD_ANTECEDENTS.
    n_tot = n_ok = 0
    ref_detail = {}
    for pid in G3_PASSAGES:
        gold = G3_GOLD_ANTECEDENTS.get(pid, [])
        pred_sorted = [res_by_pos[pid][k] for k in sorted(res_by_pos[pid].keys())]
        det = []
        for gi, (g_surf, g_head) in enumerate(gold):
            p_surf, p_head = (pred_sorted[gi] if gi < len(pred_sorted) else (None, None))
            ok = (p_head is not None and ORC.normalize(p_head) == ORC.normalize(g_head))
            n_tot += 1
            n_ok += 1 if ok else 0
            det.append(dict(surf=g_surf, gold=g_head, pred=p_head, ok=ok))
        ref_detail[pid] = det
    ref_acc = (n_ok / n_tot) if n_tot else 0.0
    return dict(store=store, correct=correct, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_n=n_tot, ref_ok=n_ok,
                ref_detail=ref_detail, answers=answers, per_q=[
                    dict(qid=q["qid"], slice=q["slice"], gold=q["gold"], pred=answers[i],
                         ok=bool(correct[i])) for i, q in enumerate(G3_QS)])


# =======================================================================================
# READ-TO-GROW: accumulate the extracted relations across the 3rd-reader passages into a foundation.
# =======================================================================================
def build_foundation(store):
    """Union of svo/loc/poss relations across passages -> a grown foundation (from an empty start)."""
    KINDS = ("svo", "loc", "poss")
    foundation = set()
    for pid in G3_PASSAGES:
        for r in store[pid]:
            if r[0] in KINDS:
                foundation.add(r)
    ents = set()
    for r in foundation:
        if r[0] == "svo":
            ents.update([r[2], r[3]])
        elif r[0] in ("loc", "poss"):
            ents.update([r[1], r[2]])
    # QUALITY spot-estimate: micro-precision on the gold-annotated passages = a COVERAGE-LIMITED LOWER
    # BOUND on correctness (a true-but-unannotated relation is scored as a false-positive here).
    tp = ex = 0
    for pid in G3_GOLD_RELS:
        ex_k = set(x for x in store[pid] if x[0] in KINDS)
        go_k = set(x for x in G3_GOLD_RELS[pid] if x[0] in KINDS)
        tp += len(ex_k & go_k)
        ex += len(ex_k)
    quality_lb = round(tp / ex, 3) if ex else 0.0
    return dict(n_relations=len(foundation), n_entities=len(ents),
                relations=sorted([list(r) for r in foundation]),
                entities=sorted(ents),
                quality_precision_lower_bound=quality_lb,
                quality_note=("micro-precision on gold-annotated passages; COVERAGE-LIMITED LOWER "
                              "BOUND (true-but-unannotated relations counted as FP -> true quality "
                              "is higher). RECALL of gold = relf1 micro_recall."),
                n_gold_scored_extracted=ex, n_gold_scored_tp=tp)


# =======================================================================================
# Vocab-coverage telemetry (reports the mostly-in-vocab selection honestly).
# =======================================================================================
def vocab_coverage():
    tot = grounded = 0
    ungrounded = set()
    names_present = set()
    for pid, text in G3_PASSAGES.items():
        for sent in ORC.split_sentences(text):
            for surf, low, pos in ORC.pos_tag_sentence(sent):
                if pos in ("NN", "NNS", "NNP", "NNPS"):
                    tot += 1
                    if ORC.ground_category(low) is not None:
                        grounded += 1
                    else:
                        ungrounded.add(low)
                    if low in IN_DICT_NAMES:
                        names_present.add(low)
    return dict(noun_tokens=tot, grounded=grounded,
                grounded_frac=round(grounded / tot, 3) if tot else 0.0,
                ungrounded_noun_lemmas=sorted(ungrounded),
                in_dict_names_used=sorted(names_present))


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


def _arms_must_differ(named_outputs):
    digests = {}
    for name, out in named_outputs.items():
        b = json.dumps(out, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], \
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical"
    return digests


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] constructing REAL WorkingOverlay + confirmed reader pipeline ...")
    import inspect
    rp_params = set(inspect.signature(WorkingOverlay.resolve_pronoun).parameters)
    assert {"prefer_agreement", "prefer_topical"} <= rp_params, \
        "resolve_pronoun() must accept prefer_agreement + prefer_topical kwargs (F.2)"

    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    # (4) ANTI-COPY-DIVERGENCE: my dataset-parameterized extract == CFX.extract_passage_cfg_mm
    # byte-identically on the 2nd-reader data (passages_dict=ORC.TEST_PASSAGES, gold=ORC.GOLD_MENTIONS).
    # Proves the reader CODE is unchanged; only the corpus differs.
    n_ok = 0
    for pid, text in ORC.TEST_PASSAGES.items():
        for fp, ag, tp, mm in [(True, True, True, "handrule"), (True, True, True, "oracle")]:
            mine = extract_passage_ds(text, clf, pid, ORC.TEST_PASSAGES, ORC.GOLD_MENTIONS, fp, ag, tp, mm)
            ref = CFX.extract_passage_cfg_mm(text, clf, pid, fp, ag, tp, mm)
            assert mine == ref, (f"COPY-DIVERGENCE {pid} (mm={mm}): dataset extract != CFX\n"
                                 f"  mine={mine}\n  ref={ref}")
            n_ok += 1
    print(f"[self-test] anti-copy-divergence: dataset-extract == CFX byte-identical on {n_ok} "
          f"(passage x mode)")

    # (2)+(3) PROVENANCE: every 3rd-reader clause is a verbatim substring of the cleaned corpus.
    with open(CORPUS3_PATH, encoding="utf-8") as fh:
        corpus_norm = re.sub(r"\s+", " ", fh.read())
    n_clauses = 0
    for pid, text in G3_PASSAGES.items():
        for clause in ORC.split_sentences(text):
            cn = re.sub(r"\s+", " ", clause).strip()
            assert cn in corpus_norm, f"PROVENANCE: {pid} clause not verbatim: {cn!r}"
            n_clauses += 1
    print(f"[self-test] provenance: {n_clauses} 3rd-reader clauses verbatim in {os.path.basename(CORPUS3_PATH)}")

    # gold sanity: every gold-relation / antecedent head + every Q gold occurs as a token lemma in its
    # passage (anti-typo; heads must be real passage tokens the pipeline can produce).
    def passage_lemmas(pid):
        # token lemmas PLUS the pre-apostrophe owner form the possessive-'s handler emits
        # (e.g. "George's" -> owner "george"), so gold heads produced by that handler validate.
        s = set()
        for sent in ORC.split_sentences(G3_PASSAGES[pid]):
            for surf, low, pos in ORC.pos_tag_sentence(sent):
                s.add(low)
                if "'" in surf:
                    s.add(surf.split("'")[0].lower())
        return s
    for pid, rels in G3_GOLD_RELS.items():
        lem = passage_lemmas(pid)
        for r in rels:
            heads = (r[2], r[3]) if r[0] == "svo" else (r[1], r[2])
            for h in heads:
                assert h in lem, f"gold-rel head {h!r} not a token lemma in {pid} ({r})"
    for q in G3_QS:
        lem = passage_lemmas(q["p"])
        assert q["gold"] in lem, f"Q {q['qid']} gold {q['gold']!r} not a token lemma in {q['p']}"
        assert q["p"] in G3_PASSAGES, f"Q {q['qid']} references missing passage {q['p']}"
    for pid, ants in G3_GOLD_ANTECEDENTS.items():
        lem = passage_lemmas(pid)
        for surf, head in ants:
            assert head in lem, f"antecedent head {head!r} not a token lemma in {pid}"
    print("[self-test] gold sanity: all gold heads / Q golds are real passage token lemmas")

    # (1) POSITIVE-CONTROL: second_reader arm reproduces the confirmed handrule baseline.
    base = CFX.run_arm("handrule_mentions", clf)
    b_all, b_ref = base["slices"]["all"], base["ref_acc"]
    b_f1, b_rec = base["relf1"]["micro_f1"], base["relf1"]["micro_recall"]
    for k, got in dict(all=b_all, ref_acc=b_ref, RELF1_f1=b_f1, RELF1_recall=b_rec).items():
        assert abs(got - BASE[k]) <= BASE_TOL, \
            f"POSITIVE-CONTROL FAIL: 2nd-reader {k}={got:.4f} != baseline {BASE[k]:.4f}"
    print(f"[self-test] POSITIVE-CONTROL: 2nd-reader reproduces baseline all={b_all:.4f} "
          f"ref={b_ref:.4f} RELF1_f1={b_f1:.3f} R={b_rec:.3f}")

    # (5) CAN-FAIL + (telemetry): 3rd-reader arm runs; corpus swap MOVES metrics (arms not identical).
    third = run_third(clf)
    _arms_must_differ({"second_reader": base["answers"], "third_reader": third["answers"]})
    moved = max(abs(third["slices"]["all"] - b_all), abs(third["relf1"]["micro_f1"] - b_f1),
                abs(third["ref_acc"] - b_ref))
    assert moved >= TELEMETRY_MIN_MOVE, f"telemetry-insensitive: corpus swap moved metrics < {TELEMETRY_MIN_MOVE}"
    print(f"[self-test] 3rd-reader arm: all={third['slices']['all']:.4f} "
          f"(NC={third['slices']['NC']:.3f} CO={third['slices']['CO']:.3f} CMP={third['slices']['CMP']:.3f}) "
          f"ref={third['ref_acc']:.4f} RELF1 F1={third['relf1']['micro_f1']:.3f} "
          f"R={third['relf1']['micro_recall']:.3f}")
    print(f"[self-test] corpus-swap moved a metric by {moved:.3f} (arms differ)")

    fnd = build_foundation(third["store"])
    print(f"[self-test] read-to-grow: foundation {fnd['n_relations']} relations / {fnd['n_entities']} "
          f"entities; quality LB={fnd['quality_precision_lower_bound']:.3f}")
    vc = vocab_coverage()
    print(f"[self-test] vocab coverage: {vc['grounded_frac']:.3f} noun tokens grounded; "
          f"in-dict names {vc['in_dict_names_used']}")

    # determinism
    r2 = run_third(clf)
    assert r2["correct"] == third["correct"] and r2["ref_acc"] == third["ref_acc"], "non-deterministic"
    print("[self-test] deterministic (two 3rd-reader runs identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=2)

    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)

    base = CFX.run_arm("handrule_mentions", clf)   # 2nd-reader (positive control)
    third = run_third(clf)                          # 3rd-reader (envelope test)
    digests = _arms_must_differ({"second_reader": base["answers"], "third_reader": third["answers"]})

    b_all, t_all = base["slices"]["all"], third["slices"]["all"]
    b_ref, t_ref = base["ref_acc"], third["ref_acc"]
    b_f1, t_f1 = base["relf1"]["micro_f1"], third["relf1"]["micro_f1"]
    b_rec, t_rec = base["relf1"]["micro_recall"], third["relf1"]["micro_recall"]
    b_prec, t_prec = base["relf1"]["micro_precision"], third["relf1"]["micro_precision"]
    b_cmp, t_cmp = base["slices"]["CMP"], third["slices"]["CMP"]

    retention = (t_all / b_all) if b_all else 0.0

    # POSITIVE-CONTROL re-check.
    pc_ok = all(abs(v - BASE[k]) <= BASE_TOL for k, v in
                dict(all=b_all, ref_acc=b_ref, RELF1_f1=b_f1, RELF1_recall=b_rec).items())
    moved = max(abs(t_all - b_all), abs(t_f1 - b_f1), abs(t_ref - b_ref))
    telemetry_ok = moved >= TELEMETRY_MIN_MOVE

    holds = (retention >= HOLDS_RETENTION_MIN) and (t_rec >= HOLDS_RELF1_RECALL_MIN) and \
            (t_ref >= HOLDS_REF_MIN)
    degrades = (retention <= DEGRADE_RETENTION_MAX) or (t_rec <= DEGRADE_RELF1_RECALL_MAX) or \
               (t_ref <= DEGRADE_REF_MAX)

    fnd = build_foundation(third["store"])
    vc = vocab_coverage()

    if not pc_ok:
        verdict = "INVALID_POSITIVE_CONTROL_FAIL"
        vmsg = (f"2nd-reader arm did NOT reproduce the confirmed baseline (all={b_all:.4f} ref={b_ref:.4f} "
                f"RELF1_f1={b_f1:.3f} R={b_rec:.3f}); one-variable basis broken -> do NOT trust the envelope.")
    elif not telemetry_ok:
        verdict = "INVALID_TELEMETRY_INSENSITIVE"
        vmsg = f"corpus swap moved metrics < {TELEMETRY_MIN_MOVE} (max {moved:.3f}); vacuous."
    elif degrades and not holds:
        verdict = "DEGRADES"
        vmsg = (f"3rd-reader COLLAPSES vs 2nd: comprehension all {b_all:.3f}->{t_all:.3f} "
                f"(retention {retention:.2f}), RELF1 recall {b_rec:.3f}->{t_rec:.3f}, ref {b_ref:.3f}->"
                f"{t_ref:.3f}, CMP {b_cmp:.3f}->{t_cmp:.3f}. Harder syntax breaks the reader -> localize "
                f"(coordinated multi-clause parsing / coref / extraction). The learned-parser lever is "
                f"re-evaluated. Vocab grounded_frac={vc['grounded_frac']:.2f}.")
    elif holds:
        verdict = "HOLDS"
        vmsg = (f"3rd-reader HOLDS vs 2nd (on the in-vocab narrative slice): comprehension all "
                f"{b_all:.3f}->{t_all:.3f} (retention {retention:.2f}), RELF1 recall {b_rec:.3f}->"
                f"{t_rec:.3f}, ref {b_ref:.3f}->{t_ref:.3f}, CMP {b_cmp:.3f}->{t_cmp:.3f}. The confirmed "
                f"reader GENERALIZES across grades on this scoped slice; read-to-grow accumulated "
                f"{fnd['n_relations']} relations / {fnd['n_entities']} entities (quality LB "
                f"{fnd['quality_precision_lower_bound']:.2f}). SCOPE CAVEAT: passages selected "
                f"mostly-in-vocab (grounded_frac={vc['grounded_frac']:.2f}); out-of-scope 3rd-reader "
                f"(new names, poetry, long sentences) UNTESTED.")
    else:
        verdict = "PARTIAL"
        vmsg = (f"3rd-reader holds on some axes, degrades on others: comprehension all {b_all:.3f}->"
                f"{t_all:.3f} (retention {retention:.2f}), RELF1 recall {b_rec:.3f}->{t_rec:.3f}, ref "
                f"{b_ref:.3f}->{t_ref:.3f}, CMP {b_cmp:.3f}->{t_cmp:.3f}. Localize the degrading axis. "
                f"Vocab grounded_frac={vc['grounded_frac']:.2f}.")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: comp all {b_all:.3f}->{t_all:.3f} (ret {retention:.2f}) | "
                 f"RELF1 F1 {b_f1:.3f}->{t_f1:.3f} R {b_rec:.3f}->{t_rec:.3f} | ref {b_ref:.3f}->"
                 f"{t_ref:.3f} | CMP {b_cmp:.3f}->{t_cmp:.3f} | foundation {fnd['n_relations']}rel/"
                 f"{fnd['n_entities']}ent qLB {fnd['quality_precision_lower_bound']:.2f}"),
        elapsed_s=round(elapsed, 2),
        ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME, run_mode=run_mode,
        seed=SEED,
        one_variable="grade/corpus (2nd-reader vs 3rd-reader); reader pipeline byte-identical (handrule + agreement + topical coref)",
        bands=dict(HOLDS_RETENTION_MIN=HOLDS_RETENTION_MIN, HOLDS_RELF1_RECALL_MIN=HOLDS_RELF1_RECALL_MIN,
                   HOLDS_REF_MIN=HOLDS_REF_MIN, DEGRADE_RETENTION_MAX=DEGRADE_RETENTION_MAX,
                   DEGRADE_RELF1_RECALL_MAX=DEGRADE_RELF1_RECALL_MAX, DEGRADE_REF_MAX=DEGRADE_REF_MAX,
                   TELEMETRY_MIN_MOVE=TELEMETRY_MIN_MOVE),
        positive_control_ok=pc_ok, telemetry_ok=telemetry_ok, telemetry_move=round(moved, 4),
        arms_differ_digests=digests, retention_all=round(retention, 4),
        arms=dict(
            second_reader=dict(slices=base["slices"], ref_acc=base["ref_acc"], ref_ok=base["ref_ok"],
                               ref_n=base["ref_n"], relf1_micro_f1=b_f1, relf1_micro_precision=b_prec,
                               relf1_micro_recall=b_rec),
            third_reader=dict(slices=third["slices"], ref_acc=third["ref_acc"], ref_ok=third["ref_ok"],
                              ref_n=third["ref_n"], relf1_micro_f1=t_f1, relf1_micro_precision=t_prec,
                              relf1_micro_recall=t_rec),
        ),
        delta=dict(all=round(b_all - t_all, 4), CMP=round(b_cmp - t_cmp, 4),
                   RELF1_f1=round(b_f1 - t_f1, 4), RELF1_recall=round(b_rec - t_rec, 4),
                   ref_acc=round(b_ref - t_ref, 4)),
        read_to_grow=fnd,
        vocab_coverage=vc,
        third_reader_per_q=third["per_q"],
        third_reader_ref_detail=third["ref_detail"],
        third_reader_relf1_per_passage=third["relf1"]["per_passage"],
        cited_baseline=dict(source="data/exp_reader_mention_source_gold_vs_handrule_corefixed_v1/metrics.json:arms.handrule_mentions",
                            confirmed_commit="4ec1a4c20", vet="a237d1f3", **BASE),
        n_third_passages=len(G3_PASSAGES), n_third_questions=len(G3_QS),
        n_third_ref_pronouns=third["ref_n"], n_third_gold_relations=third["relf1"]["n_gold"],
        scope_caveat=("3rd-reader passages SELECTED mostly-in-vocab (names grounded OR common person-"
                      "nouns) to isolate SYNTAX as the one variable; BIASES toward HOLDS. Out-of-scope "
                      "3rd-reader (new ungrounded names, poetry, 100+word sentences) EXCLUDED BY "
                      "SELECTION + UNTESTED. HOLDS = holds on the in-vocab narrative slice only."),
        power_caveat=(f"3rd-reader Q set (n={len(G3_QS)}) is smaller than the 2nd-reader baseline "
                      f"(n=31); comprehension slices are modestly powered. Load-bearing corroboration "
                      f"= ref_acc (n={third['ref_n']} pronouns) + RELF1 recall (n={third['relf1']['n_gold']} "
                      f"gold relations). CLAIM-VET-pending."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=2))
    print("delta:", json.dumps(metrics["delta"]))
    print("read_to_grow:", json.dumps({k: fnd[k] for k in
          ("n_relations", "n_entities", "quality_precision_lower_bound", "n_gold_scored_tp",
           "n_gold_scored_extracted")}))
    print("vocab_coverage:", json.dumps(vc))
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
