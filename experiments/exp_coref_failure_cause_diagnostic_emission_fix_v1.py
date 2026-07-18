"""
COREF FAILURE-CAUSE DIAGNOSTIC (+ cheap self-ref emission-fix) on REAL grade-2 text.

WHY (VET-confirmed redirect ac0a45eb off oracle-mention cell a68f9fe72):
  The oracle-mention upper-bound (exp_oracle_mention_upperbound_reader_v1) PROVED mention detection
  is NOT the reader's primary bottleneck: with PERFECT gold mentions the reader still floored coref
  (CO=CC=0.000; RELF1 R=0.375 unmoved; verdict STARVATION_REFUTED). The TRUE bottleneck = COREF
  ANTECEDENT SELECTION on real multi-competitor text (he->sport not james; he->mother [fem!]; her->dash
  not mary) PLUS a self-referential RELATION-EMISSION bug (poss(father,father), svo(scolded,dash,dash),
  poss(sport,sport)). VET caveat: SOME apparent "coref misses" ARE the emission bug, not pure
  antecedent-selection -> this cell SEPARATES them and CATEGORIZES the residual by CAUSE, so the
  eventual multi-cue resolver build targets the RIGHT cue in priority order (info-ceiling /
  categorize-before-build discipline -- the same that just refuted the mention-detector).

WHAT (this is a DIAGNOSTIC + a cheap scoped bug-fix; NOT the resolver build):
  Starts from the oracle setup VERBATIM (imported): GOLD mentions injected, REAL 2nd-reader passages,
  byte-identical downstream (learned AveragedPerceptron role-assigner + WorkingOverlay maintained-
  salience coref + relation emission + RELF1 + Q-engine). Two measurements + one categorization:

  FIX #1 (cheap, scoped): SELF-REF EMISSION-FIX = drop any emitted relation whose two ENTITY args are
    identical (svo(v,X,X) / poss(X,X) / loc(X,X) / recipient(v,X,X)). Applied as a downstream POST-
    FILTER on the oracle store (== "do not emit" for the set-based query engine) -> a clean ONE-
    VARIABLE contrast (emission_bug vs emission_fix; mentions + coref held FIXED). Re-measure RELF1
    (P/R/F1) + CC/CO/CMP. QUESTION: does removing the self-ref noise move anything? + how many Q's
    flip wrong->right purely from the fix (= the "was-emission-bug" fraction of apparent coref misses).

  DIAGNOSTIC #2 (the deliverable): PRONOUN-REFERENCE FAILURE-CAUSE HISTOGRAM. Replay the REAL overlay
    observe/resolve loop (faithful to extract_passage's reference-resolution path) over every GOLD-
    annotated 3rd-person pronoun; for each MIS-resolution categorize the cause by an INDEPENDENT,
    DOCUMENTED rule (anti-circular; NOT gerrymandered to a desired outcome):
      (a) AGREEMENT      : the resolver's pick VIOLATES gender/number/ANIMACY agreement with the
                           pronoun, OR the gold antecedent is a strictly-better agreement match (known
                           gender/animacy) that the resolver under-weighted. (Root: the overlay genders
                           only PROPER NAMES, not common person nouns [mother/father], and treats
                           gender-unknown animals as compatible with he/she.)
      (b) SALIENCE_RANK  : pred + gold are BOTH agreement-valid with EQUAL agreement strength, but the
                           gold is the more TOPICAL entity (higher mention count, or equal count but
                           introduced earlier = the established discourse subject) -- a subject/
                           centering-weighted salience picks gold; the count+recency salience did not.
      (c) SELECTIONAL_PREF: pred + gold both agreement-valid, equal agreement strength, and salience
                           genuinely favors pred (or ties) -- only world-knowledge / predicate meaning
                           separates them (the hard case).
      (d) WAS_EMISSION_BUG: reported at the Q-LEVEL (not pronoun-level) -- a coref-dependent Q that was
                           WRONG under emission_bug but RIGHT under emission_fix (the self-ref junk was
                           shadowing the correct triple in the query engine).
    The DOMINANT pronoun-reference cause = the primary cue the resolver build must add, in priority
    order. AMBIGUOUS (gold not tracked at pronoun time / undecidable) reported honestly as its own bin.

BRANCHES (DIAGNOSTIC -- the histogram IS the result; genuinely can-fail every way):
  - emission-fix moves RELF1/CC or NOT (self-ref may not intersect gold -> precision-only lift, or may
    un-shadow correct triples -> CC flips). Either is informative.
  - primary cue = AGREEMENT (cheap: gender/animacy enforcement) OR SALIENCE_RANK (salience/centering
    fix) OR SELECTIONAL_PREF (world-knowledge cue, coverage-probe-first). Whichever DOMINATES steers
    the next build. HONEST: this cell only BOUNDS which fix matters; it does NOT build the resolver.

DESIGN-GATE (verified at self-test BEFORE any full run; USER: fair tests every time):
  (1) discriminator FIRES: emission_bug store contains >=1 self-ref triple on a real passage, and the
      fix removes exactly those (not vacuous); (2) ONE variable for FIX #1 (self-ref filter; mentions +
      coref FIXED); (3) categorization rule is INDEPENDENT (grounded gender/animacy + overlay count/
      order), documented, not tuned to a target histogram; (4) CAN-FAIL (emission-fix may move nothing;
      cause may be SALIENCE/SELECTIONAL not AGREEMENT); (5) GOLD_COREF alignment gate (annotated golds
      align 1:1 with the tokenizer's target-pronoun occurrences); (6) provenance: passages VERBATIM from
      the oracle cell (already provenance-verified vs corpus; re-asserted); (7) determinism OMP=1, fixed
      seed, sorted(set), no builtin-hash-seeded RNG.

COMPUTE: sequential-CPU (POS-tag + tiny perceptron fit + symbolic replay); wall < 60s; no HD/torch/GPU
  (COMPUTE-PROPORTIONALITY: a directional categorize-before-build diagnostic). Local/foreground; NO
  push / NO remote-persist. Reported CLAIM-VET-pending (NOT self-declared chain-grade).

ANCHOR: coref_failure_cause_diagnostic_emission_fix_v1
IMPORTS (byte-identical downstream): experiments.exp_oracle_mention_upperbound_reader_v1 (git-tracked).

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD diagnostic):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER: emission_bug vs emission_fix stores differ [META_RULE_AF]
# - discriminator CAN-FAIL (fix may move nothing; cause may be non-AGREEMENT) [design-gate]
# - deterministic seeding (fixed int seed, fixed order, sorted set; NO builtin-hash)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay + REAL perceptron fit +
#   REAL POS tagger via the imported oracle machinery + the REAL extract_passage  [F.1]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 60s)
# - all reported numbers MEASURED@this metrics.json (oracle/v4 floors CITED@ their metrics.json)
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A GPU-batching
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import time
import platform
import traceback
from collections import Counter
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Imported downstream machinery (byte-identical to the oracle upper-bound cell).
import experiments.exp_oracle_mention_upperbound_reader_v1 as OR
from hdlab.state_of_mind import (WorkingOverlay, SetKnownBase, PRONOUN_SCOPE,
                                 MASC_CUES, FEM_CUES)

ANCHOR_NAME = "coref_failure_cause_diagnostic_emission_fix_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
ORACLE_METRICS_PATH = os.path.join(REPO, "data", "exp_oracle_mention_upperbound_reader_v1",
                                   "metrics.json")

SEED = 12345  # fixed int seed (NOT hash-derived); this diagnostic is deterministic (no RNG sampling).

# ---- CITED prior floors (for context; not gates) --------------------------------------
# oracle upper-bound (with gold mentions): CO=CC=0.000, RELF1 R=0.375 (STARVATION_REFUTED).
ORACLE_CC_CITED = 0.000   # CITED@ORACLE_METRICS_PATH:arms.oracle.acc_CC
ORACLE_CO_CITED = 0.000   # CITED@ORACLE_METRICS_PATH:arms.oracle.acc_CO
ORACLE_RELF1_R_CITED = 0.375  # CITED@ORACLE_METRICS_PATH:relation_f1.oracle.micro_recall

MENTION_MODE = "oracle"          # gold mentions (the mention bottleneck is already excluded)
FIXED_COREF_STRATEGY = "maintained"  # the v4/oracle claim strategy (FIXED; not the variable here)

# =======================================================================================
# GOLD COREF ANTECEDENTS (independent hand annotation; anti-circular -- NOT emitted by the reader).
# One entry per TARGET 3rd-person pronoun occurrence, in the tokenizer's reading order (verified by
# self-test to align 1:1 with the target-pronoun stream). Value = the gold antecedent HEAD (lowercased,
# matching candidate `low`), or None for an occurrence deliberately UNSCORED (number-mismatched or
# genuinely ambiguous antecedent -- annotating it would be a guess). Target pronouns =
# {he,him,his,she,her,hers,it,its,they,them,their}. All scored golds are BACKWARD references present in
# the oracle mention set (tracked entities), so they are resolvable in principle.
# =======================================================================================
GOLD_COREF = {
    # "James White has two dogs. His name is Sport. Sport is a good watchdog. In the daytime, James
    #  often uses Sport for his horse. He has a little wagon. He hitches Sport to this wagon ..."
    # his1(name of a dog: singular ref to plural 'dogs' -> UNSCORED); his2(horse)->james; He(wagon)->james; He(hitches)->james
    "L5_dogs": [None, "james", "james", "james"],
    # "The name of James's Scotch terrier is Dodger. Dodger has very bright eyes, and he does many funny things."
    "L5b_dodger": ["dodger"],
    # "The kingbird ... a robin. He eats flies ... He builds his nest in a tree ..."
    "L18_king": ["kingbird", "kingbird", "kingbird"],
    # "Henry was a kind, good boy. His father was dead, and his mother was very poor. He had a little sister ..."
    "L14_henry": ["henry", "henry", "henry"],
    # "Mary ... played with Dash, her pet dog ... She knew ... that Dash had done this, and she scolded him harshly."
    "L23_doll": ["mary", "mary", "mary", "dash"],
    # "George Ellet had a ... dollar ... He sent a ball at James Mason, but it missed him ..."
    "L60_geo": ["george", "ball", "james"],
    # "The blind man stood, and held out his hat. His mother gave him some cents. Harry took them, but did
    #  not put them into the man's hat." his1(hat)->man; His2(mother, contextually Harry-not-yet-named -> UNSCORED);
    #  him(gave, ambiguous man/harry -> UNSCORED); them(took)->cents; them(put)->cents
    "L28_sam": ["man", None, None, "cents", "cents"],
    # "Puss, with her three kittens ... carried them to the attic."
    "L8_puss": ["puss", "kittens"],
    # "Little Patty lives ... She brought her bread and milk ..."
    "L26_patty": ["patty", "patty"],
    # "Laura English is a greedy little girl. Her kitten never eats more than it needs."
    "L57_laura": ["laura", "kitten"],
    # "... a large tigress bounded ... She caught her kitten by the neck, and broke the chain which bound it."
    "L32_tiger": ["tigress", "tigress", "chain"],
    # "Two fast friends were Willie Brown and his little dog Bounce. Willie taught his dog many cunning tricks."
    "L35_willie": ["willie", "willie"],
}
TARGET_PRONOUNS = {"he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their"}

# =======================================================================================
# INDEPENDENT agreement / animacy / topicality primitives (documented; NOT the resolver's own logic).
# indep_gender KNOWS common-noun gender (mother=fem, father=masc) -- unlike the overlay, which genders
# only proper NAMES -- so it can DETECT the resolver's agreement gap. This is the anti-circular core.
# =======================================================================================
# Common-noun gender from the validated state_of_mind cue sets (drop the pronoun entries themselves).
_PRON = set(PRONOUN_SCOPE) | {"himself", "herself"}
MASC_NOUNS = {w for w in MASC_CUES if w not in _PRON}
FEM_NOUNS = {w for w in FEM_CUES if w not in _PRON}
GENDERED_PRONOUNS = {"he", "him", "his", "she", "her", "hers"}


def indep_gender(head):
    """Independent gender of a candidate head: 'masc' / 'fem' / None (unknown). Names via the grounding
    dictionary; common person nouns via the validated cue sets. This KNOWS mother=fem/father=masc."""
    h = head.lower()
    if h in OR.NAME_GENDER:
        return OR.NAME_GENDER[h]        # curated name gender (may be None for animals: sport/dash/...)
    if h in MASC_NOUNS:
        return "masc"
    if h in FEM_NOUNS:
        return "fem"
    return None


def indep_is_person(head):
    return OR.ground_category(head) == "PERSON"


def indep_is_animate(head):
    return OR.ground_category(head) in OR.ANIMATE_CATS


def indep_number(head):
    """Independent number ('singular'/'plural') via the grounding number rule."""
    _g, num = OR.grounded_gender_number(head, is_name=(head.lower() in OR.NAME_GENDER))
    return num


def agreement_valid(head, pron):
    """Does `head` satisfy HARD agreement with pronoun `pron`? number + animacy + known-gender no-conflict."""
    sc = PRONOUN_SCOPE[pron]
    pg, pn = sc["gender"], sc["number"]
    hg, hn = indep_gender(head), indep_number(head)
    # number
    if pn not in ("any", None) and hn not in ("any", None) and pn != hn:
        return False
    # animacy: he/she/him/her cannot refer to an inanimate thing; it/its does not refer to a person
    if pron in GENDERED_PRONOUNS and not indep_is_animate(head):
        return False
    if pron in ("it", "its") and indep_is_person(head):
        return False
    # gender: a KNOWN candidate gender must not conflict with a gendered pronoun
    if pg in ("masc", "fem") and hg in ("masc", "fem") and hg != pg:
        return False
    return True


def agreement_strength(head, pron):
    """Agreement-match strength (higher = better): +1 if the pronoun is gendered and the candidate has a
    KNOWN matching gender; else 0. Captures 'gold has a gender match the resolver ignored'."""
    sc = PRONOUN_SCOPE[pron]
    pg = sc["gender"]
    hg = indep_gender(head)
    if pg in ("masc", "fem") and hg == pg:
        return 1
    return 0


def categorize_misresolution(pron, pred, gold, snap):
    """INDEPENDENT cause label for a single pronoun mis-resolution (pred != gold).
    snap: {head: (count, first_midx)} for entities tracked at the pronoun's resolution moment.
    Returns one of AGREEMENT / SALIENCE_RANK / SELECTIONAL_PREF / AMBIGUOUS (+ a sub-reason)."""
    g_info = snap.get(gold)
    if g_info is None:
        return "AMBIGUOUS", "gold_not_tracked_at_pronoun_time"
    gv = agreement_valid(gold, pron)
    if not gv:
        return "AMBIGUOUS", "gold_itself_agreement_invalid(annotation_edge)"
    if pred is None:
        # resolver returned nothing though a valid gold was present -> its agreement filter dropped gold
        return "AGREEMENT", "pred_none_valid_gold_dropped"
    pv = agreement_valid(pred, pron)
    gs = agreement_strength(gold, pron)
    ps = agreement_strength(pred, pron)
    if not pv:
        return "AGREEMENT", "pred_violates_agreement"        # hard: he/she->wrong-gender or inanimate
    if gs > ps:
        return "AGREEMENT", "gold_stronger_gender_animacy"   # soft: gold known-gender, pred unknown
    if gs < ps:
        return "SELECTIONAL_PREF", "pred_stronger_agreement"  # gold wins only on world-knowledge
    # equal agreement strength, both valid -> the discriminator is salience/topicality vs selection
    gc, gm = g_info[0], g_info[1]
    p_info = snap.get(pred, (0, 10 ** 9))
    pc, pm = p_info[0], p_info[1]
    if gc > pc:
        return "SALIENCE_RANK", "gold_more_frequent"
    if gc == pc and gm < pm:
        return "SALIENCE_RANK", "gold_established_earlier_subject"
    return "SELECTIONAL_PREF", "salience_favors_pred_or_ties"


# =======================================================================================
# Self-ref emission-fix (FIX #1): drop any emitted relation whose two ENTITY args are identical.
# Applied as a downstream POST-FILTER -> equivalent to "do not emit" for the set-based query engine,
# and a clean ONE-VARIABLE contrast (mentions + coref held fixed). ENTITY-arg index pairs per kind:
#   svo=(agent,patient)=(2,3) ; poss=(owner,owned)=(1,2) ; loc=(figure,ground)=(1,2) ;
#   recipient=(agent,recipient)=(2,3). attr/color left untouched (no two-entity args).
# =======================================================================================
SELF_REF_ARG_IDX = {"svo": (2, 3), "poss": (1, 2), "loc": (1, 2), "recipient": (2, 3)}


def drop_self_ref(rels):
    """Return (kept_rels, dropped_self_ref_rels). Drops triples with two identical entity args."""
    kept, dropped = [], []
    for r in rels:
        idx = SELF_REF_ARG_IDX.get(r[0])
        if idx is not None and r[idx[0]] == r[idx[1]]:
            dropped.append(r)
        else:
            kept.append(r)
    return kept, dropped


# =======================================================================================
# Faithful replay of the REFERENCE-resolution path (mirrors extract_passage's first observe loop with
# oracle mentions). Records, per target pronoun, the resolver's pick + an entity snapshot at that moment.
# =======================================================================================
def _known_vocab():
    """Same durable-base vocab extract_passage builds: every grounded head across ALL passages."""
    known = set()
    for txt in OR.TEST_PASSAGES.values():
        for s in OR.split_sentences(txt):
            for _su, lo, _po in OR.pos_tag_sentence(s):
                if OR.ground_category(lo) is not None:
                    known.add(lo)
    return known


def replay_reference_resolutions(pid, known):
    """Replay one passage's observe/resolve loop (faithful to extract_passage reference path, oracle
    mentions). Returns an ordered list of dicts: {pron, pred, snap} for every target pronoun."""
    text = OR.TEST_PASSAGES[pid]
    gold_heads = OR.GOLD_MENTIONS.get(pid, frozenset())
    ov = WorkingOverlay(base=SetKnownBase(known))
    out = []
    for sent in OR.split_sentences(text):
        tagged = OR.pos_tag_sentence(sent)
        for _i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:                       # subj/obj AND poss pronouns (his/her/its/their)
                if low not in ("i", "you", "we") and low in TARGET_PRONOUNS:
                    snap = {h: (e.count, e.mention_midxs[0])
                            for h, e in ov._entities.items()}
                    ent = ov.resolve_pronoun(low, strategy=FIXED_COREF_STRATEGY)
                    out.append({"pron": low, "pred": (ent.head if ent is not None else None),
                                "snap": snap})
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in OR.PRONOUNS_POSS:
                pass                                       # my/your/our: structural, no reference here
            else:
                if not OR.observe_as_mention(low, pos, MENTION_MODE, gold_heads):
                    continue
                is_name = (low in OR.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                g, num = OR.grounded_gender_number(low, is_name)
                ov.observe(low, gender=g, number=num, is_proper_name=is_name)
    return out


# =======================================================================================
# Coref-dependent question set: the Q's whose answer hinges on resolving a pronoun (CO/CC/CMP that
# require crossing a pronoun). Used for the WAS_EMISSION_BUG (Q flip) attribution.
# =======================================================================================
def _coref_dependent_q_indices():
    """Indices into OR.TEST_QS for coref-dependent slices (CO/CC/CMP). NC is no-coref by design."""
    return [i for i, q in enumerate(OR.TEST_QS) if q["slice"] in ("CO", "CC", "CMP")]


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
# Build the diagnostic.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()

    # ---- FIT the learned role-assigner on the training grammar (held-out passages never seen) ----
    clf = OR.AveragedPerceptron()
    clf.fit(OR.build_training_examples(), epochs=OR.N_EPOCHS)

    # ---- Build oracle stores: emission_bug (raw) + emission_fix (self-ref dropped). ONE variable. ----
    stores_bug, stores_fix, dropped_all = {}, {}, {}
    for pid, text in OR.TEST_PASSAGES.items():
        gold_heads = OR.GOLD_MENTIONS.get(pid, frozenset())
        rels, _ = OR.extract_passage(text, "learned", clf, FIXED_COREF_STRATEGY, MENTION_MODE, gold_heads)
        kept, dropped = drop_self_ref(rels)
        stores_bug[pid] = rels
        stores_fix[pid] = kept
        if dropped:
            dropped_all[pid] = [list(x) for x in dropped]

    # ---- FIX #1 measurement: RELF1 + Q-slices, emission_bug vs emission_fix ----
    relf1_bug = OR._relf1_for_store(stores_bug)
    relf1_fix = OR._relf1_for_store(stores_fix)
    correct_bug, correct_fix = [], []
    for q in OR.TEST_QS:
        ab = OR.normalize(OR.answer_reader(q["spec"], stores_bug[q["p"]]))
        af = OR.normalize(OR.answer_reader(q["spec"], stores_fix[q["p"]]))
        g = OR.normalize(q["gold"])
        correct_bug.append(1 if (ab is not None and ab == g) else 0)
        correct_fix.append(1 if (af is not None and af == g) else 0)
    sl_bug = OR._slices(correct_bug)
    sl_fix = OR._slices(correct_fix)

    # WAS_EMISSION_BUG: coref-dependent Q's that flip wrong(bug)->right(fix). And any regressions.
    cdep = _coref_dependent_q_indices()
    was_emission_bug_qids, emission_fix_regressions = [], []
    for i in cdep:
        if correct_bug[i] == 0 and correct_fix[i] == 1:
            was_emission_bug_qids.append(OR.TEST_QS[i]["qid"])
        elif correct_bug[i] == 1 and correct_fix[i] == 0:
            emission_fix_regressions.append(OR.TEST_QS[i]["qid"])

    n_self_ref = sum(len(v) for v in dropped_all.values())
    stores_differ = (stores_bug != stores_fix)

    # ---- DIAGNOSTIC #2: pronoun-reference resolution + failure-cause histogram ----
    known = _known_vocab()
    per_pron = []            # every scored pronoun with pred/gold/cause
    cause_counts = Counter()
    n_scored = n_correct = 0
    for pid in OR.TEST_PASSAGES:
        recs = replay_reference_resolutions(pid, known)
        golds = GOLD_COREF.get(pid, [])
        # alignment (also asserted in self-test): recs (target prons) align 1:1 with golds
        for k, rec in enumerate(recs):
            gold = golds[k] if k < len(golds) else None
            if gold is None:
                continue                                  # unscored occurrence
            n_scored += 1
            pred = rec["pred"]
            correct = (pred == gold)
            entry = dict(pid=pid, pron=rec["pron"], pred=pred, gold=gold, correct=correct)
            if correct:
                n_correct += 1
            else:
                cause, reason = categorize_misresolution(rec["pron"], pred, gold, rec["snap"])
                cause_counts[cause] += 1
                entry["cause"] = cause
                entry["reason"] = reason
                # attach the competitor snapshot for auditability
                entry["snap"] = {h: list(v) for h, v in rec["snap"].items()}
            per_pron.append(entry)

    n_mis = n_scored - n_correct
    ref_acc = round(n_correct / n_scored, 4) if n_scored else 0.0
    cause_hist = {c: cause_counts.get(c, 0) for c in
                  ("AGREEMENT", "SALIENCE_RANK", "SELECTIONAL_PREF", "AMBIGUOUS")}
    # primary cue = dominant cause among the DECIDABLE bins (AMBIGUOUS excluded from the pick)
    decidable = {c: cause_hist[c] for c in ("AGREEMENT", "SALIENCE_RANK", "SELECTIONAL_PREF")}
    primary_cause = max(decidable, key=lambda c: decidable[c]) if n_mis > 0 and max(decidable.values()) > 0 else None
    ambiguous_frac = round(cause_hist["AMBIGUOUS"] / n_mis, 4) if n_mis else 0.0

    CUE_BUILD = {
        "AGREEMENT": "gender/number/ANIMACY enforcement + weighting (cheap): gender common person nouns "
                     "(mother/father/sister), require animate for he/she, prefer known-gender match over "
                     "gender-unknown competitor -- the overlay currently genders only proper names.",
        "SALIENCE_RANK": "subject/centering-weighted salience (medium): prioritize the established topical "
                         "subject over the recent same-gender competitor (the count+recency salience "
                         "under-weights topic continuity).",
        "SELECTIONAL_PREF": "selectional-preference / predicate-semantics cue (expensive; coverage-probe "
                            "first per abc96fce): needs world-knowledge to separate equally-salient "
                            "equally-agreeing competitors.",
    }
    primary_cue_build = CUE_BUILD.get(primary_cause, "n/a (no decidable mis-resolutions)")

    # ---- design-gate flags ----
    discriminator_fires = (n_self_ref >= 1 and stores_differ)
    alignment_ok = all(
        len(replay_reference_resolutions(pid, known)) == len(GOLD_COREF.get(pid, []))
        for pid in OR.TEST_PASSAGES)

    d_relf1_f1 = round(relf1_fix["micro_f1"] - relf1_bug["micro_f1"], 4)
    d_relf1_p = round(relf1_fix["micro_precision"] - relf1_bug["micro_precision"], 4)
    d_relf1_r = round(relf1_fix["micro_recall"] - relf1_bug["micro_recall"], 4)
    d_cc = round(sl_fix["CC"] - sl_bug["CC"], 4)
    d_co = round(sl_fix["CO"] - sl_bug["CO"], 4)
    d_cmp = round(sl_fix["CMP"] - sl_bug["CMP"], 4)
    emission_fix_moved = (abs(d_relf1_f1) > 0 or abs(d_cc) > 0 or abs(d_co) > 0 or abs(d_cmp) > 0
                          or len(was_emission_bug_qids) > 0)

    # ---- verdict (DIAGNOSTIC: the histogram IS the result) ----
    verdict = "COREF_CAUSE_DIAGNOSTIC"
    vmsg = (
        f"EMISSION-FIX (self-ref drop; {n_self_ref} triples over {len(dropped_all)} passages): "
        f"RELF1 F1 {relf1_bug['micro_f1']:.3f}->{relf1_fix['micro_f1']:.3f} (d={d_relf1_f1:+.3f}; "
        f"P {relf1_bug['micro_precision']:.3f}->{relf1_fix['micro_precision']:.3f}, R {relf1_bug['micro_recall']:.3f}->"
        f"{relf1_fix['micro_recall']:.3f}); CC {sl_bug['CC']:.3f}->{sl_fix['CC']:.3f}; CO {sl_bug['CO']:.3f}->"
        f"{sl_fix['CO']:.3f}; CMP {sl_bug['CMP']:.3f}->{sl_fix['CMP']:.3f}; was-emission-bug Q flips="
        f"{was_emission_bug_qids}. PRONOUN-REFERENCE resolution acc={ref_acc:.3f} ({n_correct}/{n_scored}); "
        f"mis-resolution CAUSE histogram (independent rule): AGREEMENT={cause_hist['AGREEMENT']} "
        f"SALIENCE_RANK={cause_hist['SALIENCE_RANK']} SELECTIONAL_PREF={cause_hist['SELECTIONAL_PREF']} "
        f"AMBIGUOUS={cause_hist['AMBIGUOUS']}. PRIMARY CUE TO BUILD = {primary_cause}. CLAIM-VET-pending."
    )

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"COREF_CAUSE_DIAGNOSTIC: primary_cue={primary_cause}; ref_acc={ref_acc:.3f}; "
                 f"AGR/SAL/SEL/AMB={cause_hist['AGREEMENT']}/{cause_hist['SALIENCE_RANK']}/"
                 f"{cause_hist['SELECTIONAL_PREF']}/{cause_hist['AMBIGUOUS']}; emission_fix_moved={emission_fix_moved}; "
                 f"self_ref_dropped={n_self_ref}; RELF1_F1 {relf1_bug['micro_f1']:.3f}->{relf1_fix['micro_f1']:.3f}"),
        diagnostic=True,
        elapsed_s=round(elapsed, 4), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        heldout_source="mcguffey_second_reader.clean.txt via imported oracle cell (passages VERBATIM, "
                       "provenance-verified); pronoun gold coref hand-annotated (independent, anti-circular)",

        # ---- FIX #1: emission-fix effect (ONE variable = self-ref drop) ----
        emission_fix=dict(
            one_variable="self-ref emission filter (emission_bug vs emission_fix); gold mentions + "
                         "maintained coref held FIXED",
            n_self_ref_dropped=n_self_ref,
            self_ref_triples_by_passage=dropped_all,
            relf1_bug=relf1_bug, relf1_fix=relf1_fix,
            deltas=dict(relf1_f1=d_relf1_f1, relf1_precision=d_relf1_p, relf1_recall=d_relf1_r,
                        CC=d_cc, CO=d_co, CMP=d_cmp),
            slices_bug=sl_bug, slices_fix=sl_fix,
            was_emission_bug_qids=was_emission_bug_qids,
            emission_fix_regressions=emission_fix_regressions,
            emission_fix_moved=emission_fix_moved,
        ),

        # ---- DIAGNOSTIC #2: pronoun-reference failure-cause histogram (the deliverable) ----
        pronoun_reference=dict(
            n_scored=n_scored, n_correct=n_correct, n_mis=n_mis, ref_acc=ref_acc,
            cause_histogram=cause_hist,
            primary_cause=primary_cause,
            primary_cue_build=primary_cue_build,
            ambiguous_fraction=ambiguous_frac,
            categorization_rule="INDEPENDENT: AGREEMENT = pred violates number/animacy/known-gender OR "
                                "gold is a strictly-better gender/animacy match (agreement_strength); "
                                "SALIENCE_RANK = equal agreement strength + gold more frequent or "
                                "established-earlier topical subject; SELECTIONAL_PREF = equal agreement, "
                                "salience favors/ties pred (world-knowledge only); AMBIGUOUS = gold not "
                                "tracked at pronoun time / annotation edge.",
            per_pronoun=per_pron,
        ),

        # ---- design-gate flags ----
        gates=dict(
            discriminator_fires_self_ref_present=discriminator_fires,
            stores_differ=stores_differ,
            gold_coref_alignment_ok=alignment_ok,
            can_fail_note="emission-fix may move nothing; primary cause may be SALIENCE/SELECTIONAL not "
                          "AGREEMENT; both branches pre-registered informative",
            n_self_ref=n_self_ref,
        ),

        cited_context=dict(
            oracle_cc=ORACLE_CC_CITED, oracle_co=ORACLE_CO_CITED, oracle_relf1_recall=ORACLE_RELF1_R_CITED,
            source="CITED@" + ORACLE_METRICS_PATH),
        provenance="passages+downstream imported VERBATIM from exp_oracle_mention_upperbound_reader_v1 "
                   "(gold mentions injected; learned role-assigner + maintained overlay coref byte-"
                   "identical); FIX #1 = self-ref post-filter (one variable); pronoun-reference "
                   "categorization uses an INDEPENDENT grounded gender/animacy + overlay count/order "
                   "rule (anti-circular; gold coref annotated separately from the reader's output).",
    )
    return metrics


# =======================================================================================
# Self-test (EXERCISES the REAL imported machinery + the categorization rule + alignment gate).
# =======================================================================================
def self_test():
    # F.1 real_code_path: the imported oracle machinery constructs the REAL overlay + fits the REAL
    # perceptron + tags with the REAL POS tagger + runs the REAL extract_passage.
    assert hasattr(OR, "extract_passage") and hasattr(OR, "WorkingOverlay" if False else "AveragedPerceptron")
    clf = OR.AveragedPerceptron()
    clf.fit(OR.build_training_examples(), epochs=OR.N_EPOCHS)

    known = _known_vocab()
    assert len(known) > 20, f"known vocab too small: {len(known)}"

    # GOLD_COREF ALIGNMENT GATE: annotated golds align 1:1 with the tokenizer's target-pronoun stream.
    total_scored = 0
    for pid in OR.TEST_PASSAGES:
        recs = replay_reference_resolutions(pid, known)
        golds = GOLD_COREF.get(pid, [])
        assert len(recs) == len(golds), (
            f"self-test ALIGNMENT: {pid} has {len(recs)} target pronouns but {len(golds)} gold entries")
        # every recorded pronoun surface must be a real target pronoun
        for r in recs:
            assert r["pron"] in TARGET_PRONOUNS, f"non-target pronoun recorded: {r['pron']}"
        total_scored += sum(1 for g in golds if g is not None)
    assert total_scored >= 25, f"self-test: too few scored pronouns ({total_scored}); need a real sample"

    # Every SCORED gold antecedent must be a real token head in its passage (no ghosts/typos).
    for pid, golds in GOLD_COREF.items():
        toks = set()
        for sent in OR.split_sentences(OR.TEST_PASSAGES[pid]):
            for _s, lo, _p in OR.pos_tag_sentence(sent):
                toks.add(lo)
        for g in golds:
            if g is not None:
                assert g in toks, f"self-test GOLD: '{g}' not a token in {pid}"

    # DISCRIMINATOR FIRES: emission_bug store has >=1 self-ref triple on a real passage; fix removes it.
    rels_h, _ = OR.extract_passage(OR.TEST_PASSAGES["L14_henry"], "learned", clf, FIXED_COREF_STRATEGY,
                                   MENTION_MODE, OR.GOLD_MENTIONS["L14_henry"])
    kept_h, dropped_h = drop_self_ref(rels_h)
    assert len(dropped_h) >= 1, f"self-test: expected >=1 self-ref triple on L14_henry, got {dropped_h}"
    for r in dropped_h:
        idx = SELF_REF_ARG_IDX[r[0]]
        assert r[idx[0]] == r[idx[1]], f"self-test: dropped non-self-ref triple {r}"
    for r in kept_h:
        idx = SELF_REF_ARG_IDX.get(r[0])
        assert idx is None or r[idx[0]] != r[idx[1]], f"self-test: kept a self-ref triple {r}"
    assert kept_h != rels_h, "self-test: emission-fix must change the L14 store (stores must differ)"

    # INDEPENDENT-RULE sanity (documented expected labels; NOT tuned to a target histogram):
    # (a) hard AGREEMENT: 'he'->'mother' while 'henry' available -> AGREEMENT (mother is fem/known conflict).
    snap = {"henry": (1, 0), "father": (1, 3), "mother": (1, 6)}
    cause, _ = categorize_misresolution("he", "mother", "henry", snap)
    assert cause == "AGREEMENT", f"self-test cause: he->mother should be AGREEMENT, got {cause}"
    # (b) soft AGREEMENT: 'she'->'dash'(name,gender-unknown) while 'mary'(fem) available.
    snap2 = {"mary": (1, 0), "dash": (2, 4)}
    cause, _ = categorize_misresolution("she", "dash", "mary", snap2)
    assert cause == "AGREEMENT", f"self-test cause: she->dash(vs mary) should be AGREEMENT, got {cause}"
    # (c) SALIENCE_RANK: equal-gender masc competitors, gold established earlier + equal count.
    snap3 = {"henry": (1, 0), "father": (1, 5)}
    cause, _ = categorize_misresolution("his", "father", "henry", snap3)
    assert cause == "SALIENCE_RANK", f"self-test cause: his->father(vs earlier henry) should be SALIENCE_RANK, got {cause}"
    # (d) SELECTIONAL_PREF: equal-gender masc, pred strictly MORE frequent (salience favors pred).
    snap4 = {"james": (1, 8), "george": (2, 0)}
    cause, _ = categorize_misresolution("him", "george", "james", snap4)
    assert cause == "SELECTIONAL_PREF", f"self-test cause: him->george(more freq) vs james should be SELECTIONAL_PREF, got {cause}"

    # agreement_valid / strength primitives independent of the resolver:
    assert not agreement_valid("mother", "he"), "mother should be gender-invalid for 'he'"
    assert agreement_valid("henry", "he"), "henry should be valid for 'he'"
    assert not agreement_valid("dollar", "he"), "inanimate dollar invalid for 'he'"
    assert agreement_strength("henry", "he") == 1 and agreement_strength("sport", "he") == 0, \
        "gender strength: named-masc henry=1, gender-unknown sport=0"

    # PROVENANCE (re-assert via the imported cell's corpus check on a couple of clauses).
    import re
    with open(OR.CORPUS_PATH, encoding="utf-8") as fh:
        corpus_norm = re.sub(r"\s+", " ", fh.read())
    for pid in ("L14_henry", "L23_doll"):
        for clause in OR.split_sentences(OR.TEST_PASSAGES[pid]):
            cn = re.sub(r"\s+", " ", clause).strip()
            assert cn in corpus_norm, f"self-test PROVENANCE: {pid} clause not verbatim: {cn!r}"

    print(f"SELF-TEST PASS: imported oracle machinery real; {total_scored} scored gold pronouns aligned "
          f"1:1 with tokenizer stream across {len(GOLD_COREF)} passages; self-ref discriminator fires on "
          f"L14 ({len(dropped_h)} dropped); 4 categorization sanity labels correct; agreement primitives "
          f"independent of resolver; provenance verbatim.")
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else "full"
    _write_start_marker(OUTPUT_DIR, run_mode, expected_n_units=len(OR.TEST_QS))
    metrics = build_verdict(OUTPUT_DIR, run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    ef = metrics["emission_fix"]
    pr = metrics["pronoun_reference"]
    print(f"[{run_mode}] {metrics['verdict']}: {metrics['verdict_msg']}")
    print(f"  EMISSION-FIX: dropped {ef['n_self_ref_dropped']} self-ref; RELF1 F1 "
          f"{ef['relf1_bug']['micro_f1']:.3f}->{ef['relf1_fix']['micro_f1']:.3f} "
          f"(dP={ef['deltas']['relf1_precision']:+.3f} dR={ef['deltas']['relf1_recall']:+.3f}); "
          f"CC {ef['slices_bug']['CC']:.3f}->{ef['slices_fix']['CC']:.3f} "
          f"CO {ef['slices_bug']['CO']:.3f}->{ef['slices_fix']['CO']:.3f} "
          f"CMP {ef['slices_bug']['CMP']:.3f}->{ef['slices_fix']['CMP']:.3f}; "
          f"was-emission-bug flips={ef['was_emission_bug_qids']} regressions={ef['emission_fix_regressions']}")
    print(f"  PRONOUN-REF: acc={pr['ref_acc']:.3f} ({pr['n_correct']}/{pr['n_scored']}); "
          f"CAUSE AGR={pr['cause_histogram']['AGREEMENT']} SAL={pr['cause_histogram']['SALIENCE_RANK']} "
          f"SEL={pr['cause_histogram']['SELECTIONAL_PREF']} AMB={pr['cause_histogram']['AMBIGUOUS']} "
          f"(amb_frac={pr['ambiguous_fraction']:.3f})")
    print(f"  PRIMARY CUE TO BUILD = {pr['primary_cause']}: {pr['primary_cue_build']}")
    print(f"  gates: self_ref_fires={metrics['gates']['discriminator_fires_self_ref_present']} "
          f"alignment_ok={metrics['gates']['gold_coref_alignment_ok']} stores_differ={metrics['gates']['stores_differ']}")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
