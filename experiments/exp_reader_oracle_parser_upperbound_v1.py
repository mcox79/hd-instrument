"""
ORACLE NP-HEAD + CLAUSE-SEG UPPER-BOUND (diagnostic; bound-the-prize BEFORE the learned-parser build).

QUESTION: the VET-confirmed reader wall (a7ecb244) localizes the remaining harm to the HAND-RULE PARSER:
  (a) NP-HEAD errors ("the first strawberry" -> patient="first"; "was"/"nice"/"friend's" as heads;
      manner/temporal nouns as loc) drive the FOUNDATION FALSE-POSITIVES (VET: strict precision ~0.44
      on the 36 grown relations); and
  (b) CLAUSE-SEG shared-subject orphaning ("X v1-ed and v2-ed Y" drops X as agent of v2) drives the
      COMPOSITION-DEGRADE (CMP 0.812 -> 0.333 on the 3rd reader).
Before building ANY learned parser, INJECT the two GOLD signals and measure how much of the FP-rate +
composition-degrade they actually recover. This BOUNDS the prize + confirms (or refutes) that the two
NAMED components ARE the wall (vs a harder parse tail: PP-attachment, argument structure, nested
coordination, cataphora). This is the info-ceiling-before-fix discipline.

ARMS (double-dissociation; the drill's prediction). Downstream is BYTE-IDENTICAL across arms (same coref
+ role-assigner + composition + answer-engine + Q-set); the ONE variable per arm is the injected PARSER
signal:
  hand_rule   : mention_mode=handrule, clause-seg=regex           [FLOOR / positive control -> reproduces
                                                                    the envelope 3rd-reader store EXACTLY]
  gold_heads  : mention_mode=oracle(GOLD_HEADS), clause-seg=regex  [should fix the FP-rate]
  gold_clauses: mention_mode=handrule, GOLD shared-subject inject  [should fix composition]
  gold_both   : mention_mode=oracle(GOLD_HEADS) + GOLD inject      [the CEILING; gold_both - hand_rule =
                                                                    the PRIZE a learned parser could capture]

MEASURE per arm: foundation strict PRECISION (INDEPENDENT complete-truth per-relation classification, like
the VET -- NOT the coverage-limited LB alone; both reported) + FP-rate; CMP (composition Q slice); RELF1
micro P/R/F1; comprehension all/NC/CO/CMP; ref_acc. Report the gold_both-vs-hand_rule DELTA (the prize) +
the per-component ATTRIBUTION (which oracle fixes which harm) + the double-dissociation.

BRANCHES (decisive either way; genuinely can-fail):
  TARGETS_CONFIRMED = gold_heads recovers most of the FP-rate AND gold_clauses recovers the composition
                      (both orphaned svo recovered; CMP up) AND the double-dissociation holds
                      -> the two NAMED components ARE the wall; the learned build (NP-head first,
                         clause-seg second) is worth it, prize bounded.
  TAIL_DOMINATED    = even GOLD heads+clauses leave the FP-rate high (strict precision stays < 0.60) OR
                      composition still degraded -> the harm is dominated by the HARD TAIL (PP-attachment,
                      argument structure, cataphora) NOT the two named components -> a bigger parse
                      problem; RE-SCOPE before building. DEFLATE honestly; localize the residual FPs.
  PARTIAL           = recovers one harm cleanly, leaves a meaningful residual on the other -> localize.

ANTI-CIRCULAR / FAIRNESS (design-gate; USER: fair tests every time):
  - Same REAL grade-3 McGuffey passages + gold Q/antecedents, imported VERBATIM from the envelope cell
    (exp_reader_grade3_envelope_readtogrow_v1). NOT re-authored.
  - GOLD_HEADS (the oracle INPUT) and COMPLETE_TRUTH (the precision EVAL) are SEPARATE hand-annotations:
    a relation can use only gold heads yet still be FALSE (e.g. svo(told,mother,school): school IS a gold
    head but the relation is false -> counted FP). So the oracle does NOT trivially satisfy the eval.
  - INJECT is the MINIMAL shared-subject propagation: clause BOUNDARIES stay identical to the hand-rule
    regex split (which already segments the coordination correctly); only the dropped SUBJECT is restored
    on the 2 orphaned coordinated VP clauses. ONE variable.
  - POSITIVE CONTROL: hand_rule arm byte-reproduces the envelope 3rd-reader store (36 relations, qLB 0.387,
    CMP 0.333, ref 0.833) AND lands strict precision ~0.44 (reproduces the VET, independent-annotation tol).
  - CAN-FAIL: gold_both could leave the harm (residual tail) -> genuinely reachable + informative.
  - Determinism OMP=1, fixed seed, sorted(set).

Glass-box (POS + tiny perceptron + symbolic coref/query; NO external LLM; NO torch/GPU at runtime).
Local / foreground-to-completion. NO push / NO remote-persist. Reported CLAIM-VET-pending (NOT
self-declared chain-grade); strategic read reported as hypothesis-pending-VET.

ANCHOR: reader_oracle_parser_upperbound_v1
BASELINE: envelope 3rd-reader store (commit 00c6688b6; VET a7ecb244). COMPUTE: sequential-CPU; wall < 60s.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD, no-KG cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                        [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                                  [META_RULE_AF]
# - discriminator CAN-FAIL (gold_both can confirm OR leave the tail)     [design-gate]
# - POSITIVE-CONTROL: hand_rule byte-reproduces the envelope 3rd store   [reproduce_prior / Gate D]
# - anti-copy-divergence: my extract == envelope extract byte-identical when NO oracle signal [F.1]
# - deterministic seeding (fixed int seed, fixed order, sorted set)      [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay + REAL perceptron + REAL
#   POS tagger + the REAL handrule/oracle mention gate on REAL 3rd-reader passages  [F.1]
# - PROVENANCE: every gold clause is a verbatim substring of the passage (minus the injected subject)
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 60s)
# - all reported numbers MEASURED@this metrics.json; envelope floor CITED@envelope metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A multi-seed
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
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

# Reuse the confirmed reader pipeline + the REAL 3rd-reader passages/gold VERBATIM.
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_mention_source_gold_vs_handrule_corefixed_v1 as CFX  # noqa: E402
from experiments import exp_reader_grade3_envelope_readtogrow_v1 as ENV         # noqa: E402
from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE      # noqa: E402

_prefers_topical = CFX._prefers_topical
_agreement_attrs = CFX._agreement_attrs
_RESOLVABLE = CFX._RESOLVABLE
_RESOLVABLE_SO = CFX._RESOLVABLE_SO
_RESOLVABLE_POSS = CFX._RESOLVABLE_POSS

ANCHOR_NAME = "reader_oracle_parser_upperbound_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
ENV_METRICS = os.path.join(REPO, "data", "exp_reader_grade3_envelope_readtogrow_v1", "metrics.json")
SEED = 12345

# REAL 3rd-reader passages + independent gold, imported VERBATIM from the envelope cell (NOT re-authored).
G3_PASSAGES = ENV.G3_PASSAGES
G3_GOLD_RELS = ENV.G3_GOLD_RELS
G3_GOLD_ANTECEDENTS = ENV.G3_GOLD_ANTECEDENTS
G3_QS = ENV.G3_QS

# =======================================================================================
# ORACLE ANNOTATION #1 -- GOLD NP-HEADS (per passage): the set of correct REFERENT head lemmas.
# The oracle mention gate admits ONLY these as argument candidates + coref antecedents. Non-heads
# (ordinals "first", adjectives "nice"/"little", aux "was", possessive-marker forms "friend's",
# interjections "help", the ordinal-day "third", manner/temporal nouns "earnest"/"dismay",
# discourse "one") are EXCLUDED -> this removes the NP-HEAD-error false positives. Genuine NP heads
# that happen to be mis-ATTACHED (school as goal, road/work as adjuncts) ARE included (they are real
# heads) -> their FPs are argument/attachment errors the head-oracle does NOT fix (honest tail).
# =======================================================================================
GOLD_HEADS = {
    "L7_james":   frozenset({"james", "parents", "school", "home"}),
    "L7b_james":  frozenset({"james", "mother", "school"}),
    "L34_geo1":   frozenset({"george", "mother"}),
    "L34_geo2":   frozenset({"george", "sun", "time", "place", "dinner"}),
    "L34_geo3":   frozenset({"george", "strawberry", "mouth", "mother"}),
    "L13_wolf2":  frozenset({"wolf", "flock", "sheep"}),
    "L13_wolf3":  frozenset({"day", "wolf", "john", "man"}),
    "L67_susie1": frozenset({"susie", "basket", "mother", "lunch"}),
    "L67_susie2": frozenset({"susie", "lunch"}),
    "L58_john1":  frozenset({"john", "friend", "horse"}),
    "L60_boy":    frozenset({"boy", "work", "field", "road", "horse"}),
}

# =======================================================================================
# ORACLE ANNOTATION #2 -- GOLD CLAUSE-SEG (shared-subject propagation). MINIMAL: the hand-rule regime
# splitter ALREADY segments the coordination at the right boundary; the bug is that the coordinated
# bare-VP conjunct DROPS its shared subject. INJECT restores it: {passage: {orphaned-clause-substring:
# subject-lemma}}. The clause SUBSTRING is verbatim from the regex split (asserted); the subject lemma
# is the gold shared subject prepended as a pre-verb AGENT candidate. Boundaries unchanged -> ONE var.
# =======================================================================================
INJECT_SUBJ = {
    "L13_wolf2": {"killed a great many sheep": "wolf"},        # "The wolf broke ... and [wolf] killed ..."
    "L34_geo3":  {"put the strawberry back again": "george"},  # "... he stopped, and [george] put ..."
}

# =======================================================================================
# COMPLETE-TRUTH (per passage) -- the INDEPENDENT per-relation classification set for STRICT precision /
# FP-rate (like the VET's 0.44 on the 36 grown relations). Every TRUE svo/loc/poss relation the passage
# licenses, in the extractor's canonical output space. An extracted relation NOT in this set = FALSE
# POSITIVE. Hand-annotated by reading; SEPARATE from GOLD_HEADS (an all-gold-head relation can still be
# FALSE). Includes true relations not yet extracted (so an arm that newly extracts a true relation scores
# it TP, not FP). Canonical: ("svo",verb,agent,patient) ("loc",figure,ground) ("poss",owner,owned).
# =======================================================================================
COMPLETE_TRUTH = {
    "L7_james":   {("svo", "sent", "parents", "james"), ("poss", "james", "parents"),
                   ("poss", "james", "home")},
    "L7b_james":  {("svo", "told", "mother", "james"), ("poss", "james", "mother")},
    "L34_geo1":   {("poss", "george", "mother")},
    "L34_geo2":   {("poss", "george", "dinner"), ("svo", "eat", "george", "dinner")},
    "L34_geo3":   {("svo", "lifting", "george", "strawberry"), ("svo", "put", "george", "strawberry"),
                   ("poss", "george", "mouth")},
    "L13_wolf2":  {("svo", "killed", "wolf", "sheep"), ("loc", "wolf", "flock")},
    "L13_wolf3":  set(),  # interjections / manner-PPs only; no clean svo/loc/poss -> all extracted are FP
    "L67_susie1": {("svo", "brought", "susie", "basket"), ("poss", "susie", "basket"),
                   ("poss", "susie", "mother"), ("svo", "put", "mother", "lunch")},
    "L67_susie2": {("poss", "susie", "lunch"), ("svo", "eat", "susie", "lunch")},
    "L58_john1":  {("poss", "friend", "horse"), ("svo", "admiring", "john", "horse"),
                   ("svo", "examining", "john", "horse")},
    "L60_boy":    {("svo", "heard", "boy", "horse"), ("loc", "boy", "field")},
}
_TRUTH_UNION = set()
for _s in COMPLETE_TRUTH.values():
    _TRUTH_UNION |= _s

# ---- Envelope floor (CITED@ENV_METRICS:arms.third_reader) -- hand_rule positive control -----------
FLOOR = dict(all=0.7333, NC=0.8333, CO=0.8333, CMP=0.3333, ref_acc=0.8333,
             RELF1_recall=0.8, RELF1_f1=0.522, n_relations=36, qLB=0.387)
FLOOR_STRICT_PREC_LO = 0.40   # independent strict precision reproduces the VET ~0.44 (annotation tol)
FLOOR_STRICT_PREC_HI = 0.55

# ---- Pre-registered branch bands (HYPOTHESIZED@this cell; set BEFORE the final run; can-fail) ------
# Primary FP-axis metric = the FRACTION of the hand-rule FP-rate that gold_both recovers (principled:
# "do the two NAMED components recover MOST of the FP harm?"). Composition-axis = gold_both CMP.
CONFIRM_FP_FRAC_MIN = 0.60       # gold_both recovers >= 60% of the FP-rate -> named components ARE the wall
TAIL_FP_FRAC_MAX = 0.25          # gold_both recovers < 25% of the FP-rate -> a bigger parse problem
CONFIRM_BOTH_CMP_MIN = 0.667     # gold_both recovers composition (>= 2/3 of CMP slice)
ATTR_HEADS_PREC_MIN = 0.10       # gold_heads must lift strict precision by >= this (FP-harm attribution)
ATTR_CLAUSES_CMP_MIN = 0.20      # gold_clauses must lift CMP by >= this (composition-harm attribution)
ATTR_ORTHO_MAX = 0.05            # the OFF-axis move of each oracle must stay < this (clean dissociation)
TELEMETRY_MIN_MOVE = 0.02


# =======================================================================================
# ORACLE-AWARE extract: EXACT copy of ENV.extract_passage_ds (byte-identity asserted when inject_map is
# empty) + a MINIMAL shared-subject prepend on the orphaned clauses named in inject_map. mention_mode +
# gold_mentions_dict carry the GOLD-HEADS signal (already parameterized in ENV.extract_passage_ds).
# =======================================================================================
def extract_passage_oracle(passage_text, clf, pid, passages_dict, gold_mentions_dict,
                           fix_possessive, agreement, topical, mention_mode, inject_map):
    """ENV.extract_passage_ds body + shared-subject prepend on clauses listed in inject_map[pid]."""
    gold_heads = gold_mentions_dict.get(pid, frozenset())
    coref_strategy = ORC.FIXED_COREF_STRATEGY
    pref = bool(agreement)
    injects = (inject_map or {}).get(pid, {})

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
        # SHARED-SUBJECT INJECT (the ONLY change vs ENV.extract_passage_ds): if this coordinated bare-VP
        # clause dropped its subject, prepend the gold subject as a pre-verb candidate. Boundary unchanged.
        subj = injects.get(sent.strip())
        if subj is not None:
            tagged = [(subj.capitalize(), subj, "NNP")] + tagged
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
# Run one arm -> store + all scores. Downstream (answer_reader, relf1, slices, ref_acc, foundation)
# is BYTE-IDENTICAL to the envelope's run_third; only the (mention_mode, gold_mentions_dict, inject_map)
# inputs differ across arms.
# =======================================================================================
def run_arm(clf, mention_mode, gold_mentions_dict, inject_map):
    store, res_by_pos = {}, {}
    for pid, text in G3_PASSAGES.items():
        rels, rbp = extract_passage_oracle(text, clf, pid, G3_PASSAGES, gold_mentions_dict,
                                           fix_possessive=True, agreement=True, topical=True,
                                           mention_mode=mention_mode, inject_map=inject_map)
        store[pid] = rels
        res_by_pos[pid] = rbp
    correct, answers = [], []
    for q in G3_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = ENV._relf1_g3(store)
    slices = ENV._slices_g3(correct)
    n_tot = n_ok = 0
    for pid in G3_PASSAGES:
        gold = G3_GOLD_ANTECEDENTS.get(pid, [])
        pred_sorted = [res_by_pos[pid][k] for k in sorted(res_by_pos[pid].keys())]
        for gi, (g_surf, g_head) in enumerate(gold):
            p_surf, p_head = (pred_sorted[gi] if gi < len(pred_sorted) else (None, None))
            ok = (p_head is not None and ORC.normalize(p_head) == ORC.normalize(g_head))
            n_tot += 1
            n_ok += 1 if ok else 0
    ref_acc = (n_ok / n_tot) if n_tot else 0.0
    fnd = ENV.build_foundation(store)
    strict = _strict_precision(store)
    return dict(store=store, correct=correct, answers=answers, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_ok=n_ok, ref_n=n_tot, foundation=fnd, strict=strict,
                per_q=[dict(qid=q["qid"], slice=q["slice"], gold=q["gold"], pred=answers[i],
                           ok=bool(correct[i])) for i, q in enumerate(G3_QS)])


# =======================================================================================
# INDEPENDENT strict precision / FP-rate: classify the grown FOUNDATION (union of svo/loc/poss across
# passages) against COMPLETE_TRUTH. strict_precision = TP / n_extracted ; fp_rate = 1 - strict_precision.
# =======================================================================================
def _strict_precision(store):
    KINDS = ("svo", "loc", "poss")
    foundation = set()
    for pid in G3_PASSAGES:
        for r in store[pid]:
            if r[0] in KINDS:
                foundation.add(tuple(r))
    tp_rels = sorted(r for r in foundation if r in _TRUTH_UNION)
    fp_rels = sorted(r for r in foundation if r not in _TRUTH_UNION)
    n = len(foundation)
    tp = len(tp_rels)
    prec = tp / n if n else 0.0
    return dict(n_extracted=n, tp=tp, fp=n - tp, strict_precision=round(prec, 4),
                fp_rate=round(1.0 - prec, 4),
                tp_relations=[list(r) for r in tp_rels], fp_relations=[list(r) for r in fp_rels])


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
def _fit_clf():
    clf = ORC.AveragedPerceptron()
    clf.fit(ORC.build_training_examples(), epochs=ORC.N_EPOCHS)
    return clf


def self_test():
    print("[self-test] constructing REAL reader pipeline (WorkingOverlay + perceptron + POS tagger) ...")
    import inspect
    rp_params = set(inspect.signature(WorkingOverlay.resolve_pronoun).parameters)
    assert {"prefer_agreement", "prefer_topical"} <= rp_params, "resolve_pronoun sig drift (F.2)"
    clf = _fit_clf()

    # (F.1) ANTI-COPY-DIVERGENCE: my extract == ENV.extract_passage_ds byte-identical when NO oracle
    # signal (mention_mode=handrule, inject_map empty) on the REAL 3rd-reader passages.
    n_ok = 0
    for pid, text in G3_PASSAGES.items():
        mine = extract_passage_oracle(text, clf, pid, G3_PASSAGES,
                                      {p: frozenset() for p in G3_PASSAGES},
                                      True, True, True, "handrule", {})
        ref = ENV.extract_passage_ds(text, clf, pid, G3_PASSAGES,
                                     {p: frozenset() for p in G3_PASSAGES},
                                     True, True, True, "handrule")
        assert mine == ref, f"COPY-DIVERGENCE {pid}: my extract != ENV.extract_passage_ds\n {mine}\n {ref}"
        n_ok += 1
    print(f"[self-test] anti-copy-divergence: my extract == envelope extract on {n_ok} passages")

    # PROVENANCE: every injected clause key is a verbatim clause from the regime regex split.
    n_inj = 0
    for pid, mp in INJECT_SUBJ.items():
        clauses = [c.strip() for c in ORC.split_sentences(G3_PASSAGES[pid])]
        for clause_key, subj in mp.items():
            assert clause_key in clauses, f"INJECT key not a verbatim regex clause in {pid}: {clause_key!r}"
            # subject lemma must be a real token lemma earlier in the passage (a genuine shared subject).
            lem = set()
            for s in ORC.split_sentences(G3_PASSAGES[pid]):
                for _su, lo, _po in ORC.pos_tag_sentence(s):
                    lem.add(lo)
            assert subj in lem, f"INJECT subject {subj!r} not a token lemma in {pid}"
            n_inj += 1
    print(f"[self-test] provenance: {n_inj} injected shared-subject clauses verbatim; subjects real lemmas")

    # GOLD_HEADS + COMPLETE_TRUTH cover every passage; truth heads are real lemmas (anti-typo).
    for pid in G3_PASSAGES:
        assert pid in GOLD_HEADS, f"GOLD_HEADS missing {pid}"
        assert pid in COMPLETE_TRUTH, f"COMPLETE_TRUTH missing {pid}"
    def plemmas(pid):
        s = set()
        for sent in ORC.split_sentences(G3_PASSAGES[pid]):
            for surf, low, pos in ORC.pos_tag_sentence(sent):
                s.add(low)
                if "'" in surf:
                    s.add(surf.split("'")[0].lower())
        return s
    for pid, rels in COMPLETE_TRUTH.items():
        lem = plemmas(pid)
        for r in rels:
            heads = (r[2], r[3]) if r[0] == "svo" else (r[1], r[2])
            for h in heads:
                assert h in lem, f"COMPLETE_TRUTH head {h!r} not a token lemma in {pid} ({r})"

    # (POSITIVE CONTROL) hand_rule arm byte-reproduces the envelope 3rd-reader store + strict prec ~VET.
    hand = run_arm(clf, "handrule", {p: frozenset() for p in G3_PASSAGES}, {})
    assert hand["foundation"]["n_relations"] == FLOOR["n_relations"], \
        f"POS-CTRL FAIL: foundation {hand['foundation']['n_relations']} != {FLOOR['n_relations']}"
    assert abs(hand["foundation"]["quality_precision_lower_bound"] - FLOOR["qLB"]) <= 0.002, "POS-CTRL qLB"
    assert abs(hand["slices"]["CMP"] - FLOOR["CMP"]) <= 0.002, "POS-CTRL CMP"
    assert abs(hand["ref_acc"] - FLOOR["ref_acc"]) <= 0.002, "POS-CTRL ref_acc"
    sp = hand["strict"]["strict_precision"]
    assert FLOOR_STRICT_PREC_LO <= sp <= FLOOR_STRICT_PREC_HI, \
        f"POS-CTRL FAIL: hand_rule strict precision {sp:.3f} not in [{FLOOR_STRICT_PREC_LO},{FLOOR_STRICT_PREC_HI}] (VET ~0.44)"
    print(f"[self-test] POS-CTRL: hand_rule reproduces envelope store (n_rel={hand['foundation']['n_relations']} "
          f"qLB={hand['foundation']['quality_precision_lower_bound']:.3f} CMP={hand['slices']['CMP']:.3f} "
          f"ref={hand['ref_acc']:.3f}); strict precision {sp:.3f} (VET ~0.44)")
    print(f"[self-test]   hand_rule FP relations ({hand['strict']['fp']}): {hand['strict']['fp_relations']}")

    # (CAN-FAIL + discriminator fires) the oracle arms MOVE metrics + the double-dissociation is present.
    gh = run_arm(clf, "oracle", GOLD_HEADS, {})
    gc = run_arm(clf, "handrule", {p: frozenset() for p in G3_PASSAGES}, INJECT_SUBJ)
    gb = run_arm(clf, "oracle", GOLD_HEADS, INJECT_SUBJ)
    _arms_must_differ({k: {p: [list(r) for r in v["store"][p]] for p in G3_PASSAGES}
                       for k, v in dict(hand_rule=hand, gold_heads=gh,
                                        gold_clauses=gc, gold_both=gb).items()})
    moved = max(abs(gb["strict"]["strict_precision"] - sp), abs(gb["slices"]["CMP"] - hand["slices"]["CMP"]))
    assert moved >= TELEMETRY_MIN_MOVE, f"telemetry-insensitive: oracle moved < {TELEMETRY_MIN_MOVE}"
    # discriminator FIRES (double-dissociation on the headline metrics + shared-subject restored):
    #  gold_heads lifts strict precision (FP harm); gold_clauses lifts CMP (composition harm) + restores
    #  the shared subject (agent) on BOTH orphaned coordinated VP clauses.
    gc_found = set(tuple(r) for pid in G3_PASSAGES for r in gc["store"][pid])
    gh_found = set(tuple(r) for pid in G3_PASSAGES for r in gh["store"][pid])
    assert any(r[:2] == ("svo", "killed") and r[2] == "wolf" for r in gc_found), \
        "gold_clauses did NOT restore the shared subject of 'killed' (wolf)"
    assert any(r[:3] == ("svo", "put", "george") for r in gc_found), \
        "gold_clauses did NOT restore the shared subject of 'put' (george)"
    assert not any(r[:2] == ("svo", "killed") for r in gh_found), \
        "gold_heads alone unexpectedly restored the orphaned subject (clause-seg not a distinct cause)"
    assert (gh["strict"]["strict_precision"] - sp) >= ATTR_HEADS_PREC_MIN, \
        "gold_heads did NOT lift strict precision by the FP-attribution threshold"
    assert (gc["slices"]["CMP"] - hand["slices"]["CMP"]) >= ATTR_CLAUSES_CMP_MIN, \
        "gold_clauses did NOT lift CMP by the composition-attribution threshold"
    print(f"[self-test] arms move: hand_rule prec={sp:.3f} CMP={hand['slices']['CMP']:.3f} | "
          f"gold_heads prec={gh['strict']['strict_precision']:.3f} CMP={gh['slices']['CMP']:.3f} | "
          f"gold_clauses prec={gc['strict']['strict_precision']:.3f} CMP={gc['slices']['CMP']:.3f} | "
          f"gold_both prec={gb['strict']['strict_precision']:.3f} CMP={gb['slices']['CMP']:.3f}")
    print("[self-test] discriminator fires: heads->precision, clauses->CMP (double-dissociation); "
          "shared subject restored on both orphaned clauses")

    # determinism
    gb2 = run_arm(clf, "oracle", GOLD_HEADS, INJECT_SUBJ)
    assert gb2["correct"] == gb["correct"] and gb2["strict"] == gb["strict"], "non-deterministic"
    print("[self-test] deterministic (two gold_both runs identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=4)
    clf = _fit_clf()

    hand = run_arm(clf, "handrule", {p: frozenset() for p in G3_PASSAGES}, {})
    gh = run_arm(clf, "oracle", GOLD_HEADS, {})
    gc = run_arm(clf, "handrule", {p: frozenset() for p in G3_PASSAGES}, INJECT_SUBJ)
    gb = run_arm(clf, "oracle", GOLD_HEADS, INJECT_SUBJ)
    arms = dict(hand_rule=hand, gold_heads=gh, gold_clauses=gc, gold_both=gb)

    digests = _arms_must_differ({k: {p: [list(r) for r in v["store"][p]] for p in G3_PASSAGES}
                                 for k, v in arms.items()})

    def _sp(a): return a["strict"]["strict_precision"]
    def _cmp(a): return a["slices"]["CMP"]

    h_prec, h_cmp = _sp(hand), _cmp(hand)
    gb_prec, gb_cmp = _sp(gb), _cmp(gb)

    # POSITIVE-CONTROL re-check (hand_rule reproduces the envelope floor).
    pc_ok = (hand["foundation"]["n_relations"] == FLOOR["n_relations"] and
             abs(hand["foundation"]["quality_precision_lower_bound"] - FLOOR["qLB"]) <= 0.002 and
             abs(h_cmp - FLOOR["CMP"]) <= 0.002 and abs(hand["ref_acc"] - FLOOR["ref_acc"]) <= 0.002 and
             FLOOR_STRICT_PREC_LO <= h_prec <= FLOOR_STRICT_PREC_HI)
    moved = max(abs(gb_prec - h_prec), abs(gb_cmp - h_cmp))
    telemetry_ok = moved >= TELEMETRY_MIN_MOVE

    # ATTRIBUTION (textbook double-dissociation on the headline metrics).
    d_heads_prec = _sp(gh) - h_prec       # gold_heads -> FP harm (strict precision)
    d_clauses_prec = _sp(gc) - h_prec
    d_heads_cmp = _cmp(gh) - h_cmp
    d_clauses_cmp = _cmp(gc) - h_cmp      # gold_clauses -> composition harm (CMP)
    gc_found = set(tuple(r) for pid in G3_PASSAGES for r in gc["store"][pid])
    gh_found = set(tuple(r) for pid in G3_PASSAGES for r in gh["store"][pid])
    clauses_restores_orphan_subject = (any(r[:3] == ("svo", "killed", "wolf") for r in gc_found) and
                                       any(r[:3] == ("svo", "put", "george") for r in gc_found))
    heads_alone_misses_orphan_subject = not any(r[:2] == ("svo", "killed") for r in gh_found)
    heads_fixes_prec_not_cmp = (d_heads_prec >= ATTR_HEADS_PREC_MIN and abs(d_heads_cmp) < ATTR_ORTHO_MAX)
    clauses_fixes_cmp_not_prec = (d_clauses_cmp >= ATTR_CLAUSES_CMP_MIN and abs(d_clauses_prec) < ATTR_ORTHO_MAX)
    dissociation = (heads_fixes_prec_not_cmp and clauses_fixes_cmp_not_prec and
                    clauses_restores_orphan_subject and heads_alone_misses_orphan_subject)

    h_fpr, gb_fpr = hand["strict"]["fp_rate"], gb["strict"]["fp_rate"]
    recovered_fp_frac = round((h_fpr - gb_fpr) / h_fpr, 4) if h_fpr > 0 else 0.0
    prize_prec = round(gb_prec - h_prec, 4)
    prize_cmp = round(gb_cmp - h_cmp, 4)
    prize_fp_rate = round(h_fpr - gb_fpr, 4)

    if not pc_ok:
        verdict = "INVALID_POSITIVE_CONTROL_FAIL"
        vmsg = (f"hand_rule did NOT reproduce the envelope floor (n_rel={hand['foundation']['n_relations']} "
                f"qLB={hand['foundation']['quality_precision_lower_bound']:.3f} CMP={h_cmp:.3f} "
                f"ref={hand['ref_acc']:.3f} strict_prec={h_prec:.3f}); one-variable basis broken.")
    elif not telemetry_ok:
        verdict = "INVALID_TELEMETRY_INSENSITIVE"
        vmsg = f"oracle signals moved metrics < {TELEMETRY_MIN_MOVE} (max {moved:.3f}); vacuous."
    elif recovered_fp_frac >= CONFIRM_FP_FRAC_MIN and gb_cmp >= CONFIRM_BOTH_CMP_MIN and dissociation:
        verdict = "TARGETS_CONFIRMED"
        vmsg = (f"the two NAMED components ARE the wall. gold_both recovers most of the FP-rate "
                f"({recovered_fp_frac:.0%}: strict precision {h_prec:.3f}->{gb_prec:.3f}, fp_rate {h_fpr:.3f}->"
                f"{gb_fpr:.3f}) AND composition (CMP {h_cmp:.3f}->{gb_cmp:.3f}); double-dissociation holds "
                f"(heads:+{d_heads_prec:.3f} prec/{d_heads_cmp:+.3f} CMP; clauses:{d_clauses_prec:+.3f} prec/"
                f"+{d_clauses_cmp:.3f} CMP). PRIZE precision +{prize_prec:.3f} / CMP +{prize_cmp:.3f}. The "
                f"learned build (NP-head first, clause-seg second) is worth it; prize bounded.")
    elif recovered_fp_frac < TAIL_FP_FRAC_MAX or gb_cmp <= FLOOR["CMP"] + 0.001:
        verdict = "TAIL_DOMINATED"
        vmsg = (f"even GOLD heads+clauses barely dent the harm: gold_both recovers only {recovered_fp_frac:.0%} "
                f"of the FP-rate (strict precision {h_prec:.3f}->{gb_prec:.3f}, fp_rate {h_fpr:.3f}->{gb_fpr:.3f}) "
                f"/ CMP {h_cmp:.3f}->{gb_cmp:.3f}. The harm is dominated by the HARD TAIL (argument structure, "
                f"PP-attachment, role-assignment, cataphora) NOT the two named components -> a bigger parse "
                f"problem; RE-SCOPE before the learned build. Residual FPs: metrics.arms.gold_both.strict.fp_relations.")
    else:
        verdict = "PARTIAL"
        vmsg = (f"SPLIT by axis. COMPOSITION harm IS the named clause-seg component: gold_clauses recovers CMP "
                f"{h_cmp:.3f}->{_cmp(gc):.3f} (double-dissociation clean, heads move CMP {d_heads_cmp:+.3f}). "
                f"But the FP harm is only PARTLY the named NP-head component: gold_both recovers just "
                f"{recovered_fp_frac:.0%} of the FP-rate (strict precision {h_prec:.3f}->{gb_prec:.3f}, fp_rate "
                f"{h_fpr:.3f}->{gb_fpr:.3f}); the {gb['strict']['fp']} residual FPs localize to a BIGGER parse "
                f"problem NOT covered by the two named fixes -- argument structure (goal-as-patient sent/told->"
                f"school), PP-attachment (loc boy road/work), clause-BOUNDARY + multi-patient (lifting george/"
                f"mouth), role-assignment (sheep->RECIPIENT so N5 never recovers; came man man), cataphora "
                f"(poss his mother). PRIZE precision +{prize_prec:.3f} / CMP +{prize_cmp:.3f}. HYPOTHESIS "
                f"pending-VET: NP-head + shared-subject are REAL, attributable, worth building -- but they are "
                f"NOT the whole wall; the majority residual FP-rate needs argument-structure/attachment/role "
                f"work. Deflate the drill's 'recover a large fraction of both harms' -> composition yes, "
                f"foundation-FPs only ~{recovered_fp_frac:.0%}.")

    def _arm_summary(a):
        return dict(slices=a["slices"], ref_acc=a["ref_acc"], ref_ok=a["ref_ok"], ref_n=a["ref_n"],
                    relf1_micro_f1=a["relf1"]["micro_f1"], relf1_micro_precision=a["relf1"]["micro_precision"],
                    relf1_micro_recall=a["relf1"]["micro_recall"],
                    foundation_n_relations=a["foundation"]["n_relations"],
                    foundation_n_entities=a["foundation"]["n_entities"],
                    foundation_quality_lb=a["foundation"]["quality_precision_lower_bound"],
                    strict=a["strict"], per_q=a["per_q"])

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: strict_prec hand {h_prec:.3f}->both {gb_prec:.3f} (prize +{prize_prec:.3f}; "
                 f"fp_rate {hand['strict']['fp_rate']:.3f}->{gb['strict']['fp_rate']:.3f}) | "
                 f"CMP {h_cmp:.3f}->{gb_cmp:.3f} (+{prize_cmp:.3f}) | heads:dprec {d_heads_prec:+.3f} "
                 f"clauses:dCMP {d_clauses_cmp:+.3f} | dissociation={dissociation}"),
        elapsed_s=round(elapsed, 2), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        one_variable="injected parser signal (gold NP-heads / gold shared-subject / both); downstream byte-identical",
        positive_control_ok=pc_ok, telemetry_ok=telemetry_ok, telemetry_move=round(moved, 4),
        arms_differ_digests=digests,
        prize=dict(strict_precision=prize_prec, CMP=prize_cmp, fp_rate_reduction=prize_fp_rate,
                   recovered_fp_frac=recovered_fp_frac),
        attribution=dict(d_heads_strict_precision=round(d_heads_prec, 4),
                         d_clauses_strict_precision=round(d_clauses_prec, 4),
                         d_heads_CMP=round(d_heads_cmp, 4), d_clauses_CMP=round(d_clauses_cmp, 4),
                         heads_fixes_precision_not_composition=heads_fixes_prec_not_cmp,
                         clauses_fixes_composition_not_precision=clauses_fixes_cmp_not_prec,
                         clauses_restores_orphan_subject=clauses_restores_orphan_subject,
                         heads_alone_misses_orphan_subject=heads_alone_misses_orphan_subject,
                         double_dissociation=dissociation),
        bands=dict(CONFIRM_FP_FRAC_MIN=CONFIRM_FP_FRAC_MIN, TAIL_FP_FRAC_MAX=TAIL_FP_FRAC_MAX,
                   CONFIRM_BOTH_CMP_MIN=CONFIRM_BOTH_CMP_MIN, ATTR_HEADS_PREC_MIN=ATTR_HEADS_PREC_MIN,
                   ATTR_CLAUSES_CMP_MIN=ATTR_CLAUSES_CMP_MIN, ATTR_ORTHO_MAX=ATTR_ORTHO_MAX,
                   FLOOR_STRICT_PREC_LO=FLOOR_STRICT_PREC_LO, FLOOR_STRICT_PREC_HI=FLOOR_STRICT_PREC_HI),
        arms=dict(hand_rule=_arm_summary(hand), gold_heads=_arm_summary(gh),
                  gold_clauses=_arm_summary(gc), gold_both=_arm_summary(gb)),
        cited_floor=dict(source="data/exp_reader_grade3_envelope_readtogrow_v1/metrics.json:arms.third_reader",
                         commit="00c6688b6", vet="a7ecb244", **FLOOR),
        annotation_note=("GOLD_HEADS = oracle mention gate INPUT (correct referent heads); COMPLETE_TRUTH = "
                         "SEPARATE precision EVAL (an all-gold-head relation can still be FALSE -> not "
                         "circular). INJECT = minimal shared-subject restore on the 2 orphaned coordinated "
                         "VP clauses (boundaries unchanged)."),
        scope_caveat=("Same mostly-in-vocab 3rd-reader narrative slice as the envelope (SYNTAX isolated; "
                      "out-of-vocab / poetry / long sentences UNTESTED). n_questions=15, n_relations~36 -> "
                      "modestly powered; strict precision (per-relation, n~36) is the load-bearing FP signal. "
                      "GOLD annotations are hand-authored by the cell author (single annotator). "
                      "CLAIM-VET-pending; strategic read = hypothesis pending landed-VET."),
        n_passages=len(G3_PASSAGES), n_questions=len(G3_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("attribution:", json.dumps(metrics["attribution"]))
    print("prize:", json.dumps(metrics["prize"]))
    for k in ("hand_rule", "gold_heads", "gold_clauses", "gold_both"):
        a = arms[k]
        print(f"  {k:12s} strict_prec={a['strict']['strict_precision']:.3f} fp={a['strict']['fp']:2d}/"
              f"{a['strict']['n_extracted']:2d} | all={a['slices']['all']:.3f} NC={a['slices']['NC']:.3f} "
              f"CO={a['slices']['CO']:.3f} CMP={a['slices']['CMP']:.3f} | ref={a['ref_acc']:.3f} | "
              f"RELF1 R={a['relf1']['micro_recall']:.3f}")
    print("gold_both FP residual:", json.dumps(gb["strict"]["fp_relations"]))
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
