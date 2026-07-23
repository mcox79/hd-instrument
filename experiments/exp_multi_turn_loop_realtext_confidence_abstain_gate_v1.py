"""exp_multi_turn_loop_realtext_confidence_abstain_gate_v1 -- can the glass-box substrate KNOW
when it does NOT know, and ABSTAIN instead of confabulating?

CONTEXT: exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1 (HARD_FAIL) showed the assembled
real-text conversational loop hallucinates at scale: the REAL arm answers 21 of 31 cross-turn Qs, of
which only 8 are correct and 13 are CONFIDENT WRONG answers (global hallucination_rate=0.4194
MEASURED@data/exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1/metrics.json:REAL.hallucination_rate).
The query engine (O.answer_reader) returns the FIRST relation matching the query pattern with NO
confidence gate -- so a mis-parsed / mis-resolved relation surfaces as a fluent wrong answer.

THIS CELL adds a CONFIDENCE/ABSTAIN gate over the SAME real pipeline + SAME passages + SAME Q-set.
ONE variable = the abstain gate (vs the no-gate baseline). The gate uses GLASS-BOX confidence signals
the substrate ALREADY computes -- NO autograd, NO LLM, nothing learned-from-labels:
  (1) PARSE margin      = the averaged-perceptron role-assignment margin (score(argmax role) -
                          score(runner-up role)) for the head(s) that produced the matched relation.
                          A low-margin (agent-vs-patient near-tie) role decision is the reversal-error
                          signature.
  (2) COREF margin      = the maintained-overlay salience gap (best - second) / best among the
                          agreement-compatible antecedents at the pronoun's resolution point. The
                          resolver ALREADY abstains on no-compatible-candidate (returns None); this
                          EXTENDS that same abstain discipline DOWNSTREAM -- a pronoun resolved on a
                          near-tie salience is low-confidence.
  (3) MATCH support     = does more than one store relation match the query pattern with DIFFERENT
                          answers? A conflict caps the confidence (the store disagrees with itself).
Per-relation rel_conf = min(parse_conf, coref_conf); per-answer conf = matched rel_conf, capped by
conflict. Brain-faithful = metacognition / feeling-of-knowing: answer when evidence is strong, abstain
when weak (Nelson-Narens metamemory; Hart 1965 feeling-of-knowing). CITED, reference-not-oracle.

CORE QUESTION (a PRECISION/COVERAGE tradeoff): does the gate drive hallucination toward ~0 (restore
zero-hallucination at scale) WHILE RETAINING non-trivial coverage of the answerable cases (keeps the
originally-CORRECT answers, high precision-on-answered)?  The absolute ceiling on coverage-at-zero-
hallucination is fixed by construction: only the 8 originally-correct answers CAN be kept (the gate
cannot turn a wrong answer right), so max zero-halluc coverage = 8/31 = 0.258 global. We therefore band
COVERAGE as RETAINED-CORRECT-FRACTION of that ceiling (how many of the 8 correct the gate keeps),
NOT an unreachable absolute rate.  Primary threshold-FREE discriminator = AUC(confidence vs
correctness) over the 21 answered Qs (8 correct-positive / 13 wrong-negative): can the confidence
signal RANK its own right answers above its own wrong ones?

ARMS:
  NO_GATE       = the REAL pipeline answers everything it matches (reproduces the 0.4194 baseline;
                  positive control).
  ABSTAIN_GATE  = REAL + confidence gate at the pre-registered operating threshold (lowest conf
                  threshold achieving global halluc <= 0.05).  THE MECHANISM.
  SCRAMBLE_GATE = anti-cheat must-fail: the SAME per-answer confidences RANDOMLY PERMUTED across the
                  answered Qs, gated at the SAME coverage (same number answered).  If random abstention
                  at matched coverage kills hallucination just as well, the real signal is NOT doing
                  the work (it is just "answer fewer").  The real gate must BEAT scramble.

BANDS (envelope-fail; I own them; set BEFORE the run; global halluc = wrong-answered / 31, same
definition as the baseline):
  HARD_PASS (glass-box confidence GENUINELY discriminates correct-vs-wrong; zero-halluc restored at
    non-trivial coverage):
      auc_combined >= 0.70 AND
      retained_correct_frac >= 0.60 (keeps >= 60% of the 8 originally-correct at the operating point) AND
      precision_on_answered >= 0.80 (answered ones mostly right) AND
      op_halluc <= 0.05 AND
      (scramble_halluc - op_halluc) >= 0.10 at matched coverage (real BEATS random abstention).
  HARD_FAIL (to kill hallucination the gate must abstain on ~everything -> confidence is NOT
    informative; an important earned finding about glass-box metacognition):
      auc_combined <= 0.55 OR
      retained_correct_frac <= 0.25 (at halluc<=0.05 it also killed the correct answers) OR
      (scramble_halluc - op_halluc) <= 0.02 (real no better than random abstention).
  MIDDLE otherwise (partial: reduces halluc at a real coverage cost; localize which signal carries it).

DESIGN-GATE (verified at self-test): (1) REAL baseline reproduced (NO_GATE halluc within tol of 0.4194,
  n_correct==8); (2) discriminator CAN-FAIL (AUC ~0.5 -> abstain-all is the honest HARD_FAIL; both bands
  reachable); (3) difficulty ON (real grade-2 syntax, true-MM components, unchanged); (4) ONE variable =
  the abstain gate; (5) NO answer leakage (Q specs unchanged, inherited assertion); (6) ONE-VARIABLE
  ISOLATION AIRTIGHT: the confidence-annotating extractor's relation SET is byte-identical to the base
  O.extract_passage per passage (self-test asserts set-equality) -- same relations, we only ALSO compute
  confidence, so ABSTAIN_GATE answers are a SUBSET of NO_GATE answers; (7) POSITIVE-CONTROL: NO_GATE
  per-question answers reproduce O.answer_reader exactly; (8) determinism (OMP=1, fixed seed, sorted set,
  no hash()-seeding; scramble uses random.Random(seed)).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                 [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                            [META_RULE_AF]
# - discriminator CAN-FAIL AND FIRES (AUC; retained-correct; beat-scramble)      [design-gate]
# - REAL code path exercised in self-test (perceptron fit + POS tag + WorkingOverlay + conf-extract) [F.1]
# - baseline_in_band: NO_GATE reproduces 0.4194; AUC free to be ~0.5 (can-fail)  [META_RULE_AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))               [F.5/PROT-023]
# - multi-seed variance probe on the confidence discriminator: AUC bootstrap CI + K-seed scramble null
#   (the confidence scalar itself is DETERMINISTIC; only scramble/bootstrap are stochastic)  [META CG]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: no quantitative HD noise floor (symbolic glass-box). coverage-at-zero-halluc ceiling
#   (8/31=0.258) IS the capacity-feasibility bound; bands stated relative to it (retained-correct-frac).
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule (not learned;
#   avoids overfit on 21 answered points); the full precision/coverage CURVE is the deliverable.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import experiments.exp_oracle_mention_upperbound_reader_v1 as O
from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE

ANCHOR_NAME = "multi_turn_loop_realtext_confidence_abstain_gate_v1"
SEED = 12345
N_SCRAMBLE_SEEDS = 400      # scramble null distribution (matched-coverage random abstention)
N_BOOT = 5000               # AUC bootstrap CI

# --- pre-registered bands (HYPOTHESIZED@this prereg) ---
HP_AUC_MIN = 0.70
HP_RETAINED_CORRECT_MIN = 0.60
HP_PRECISION_MIN = 0.80
HP_HALLUC_MAX = 0.05
HP_BEAT_SCRAMBLE_MIN = 0.10
HF_AUC_MAX = 0.55
HF_RETAINED_CORRECT_MAX = 0.25
HF_BEAT_SCRAMBLE_MAX = 0.02

# baseline positive-control targets (MEASURED@ the no-gate compounding cell) ---
BASE_HALLUC = 0.4194
BASE_HALLUC_TOL = 0.03
BASE_N_CORRECT = 8

CONFLICT_CAP = 0.15         # a self-disagreeing store (>1 distinct matching answer) caps confidence
CO_EPS = 1e-9

CROSS_TURN_SLICES = ("CC", "CMP")


# ===========================================================================================
# Confidence-annotating extractor. FAITHFUL COPY of O.extract_passage (assigner='learned',
# mention_mode='handrule', gold_heads=frozenset()) that ALSO records, per emitted relation, its
# provenance confidence:
#   raw_parse_margin : min over the relation's learned-role heads of (score(argmax) - score(runner-up))
#                      from the averaged perceptron; math.inf sentinel for POS-driven STRUCTURAL rules
#                      (possessive 's / poss-pronoun / color -- deterministic, not learned).
#   coref_conf       : min over the relation's heads of the pronoun-resolution salience margin
#                      (best-second)/best among agreement-compatible antecedents (1.0 if no head came
#                      from a pronoun; 0.0 if the resolver abstained -> head is the raw pronoun).
# Self-test asserts the emitted relation SET equals O.extract_passage's set per passage (ONE-VARIABLE
# isolation: identical relations, we only ALSO compute confidence).
# ===========================================================================================
def _role_margin(clf, feats):
    """Averaged-perceptron argmax margin over ROLES (glass-box; clf._score is the inspectable cue sum)."""
    scores = sorted((clf._score(r, feats) for r in O.ROLES), reverse=True)
    return scores[0] - scores[1]


def _coref_margin(ov, pronoun_low, now):
    """Maintained-overlay salience margin among agreement-compatible antecedents at resolution time.
    Returns margin in [0,1] (1=unambiguous, 0=tie) and the chosen head (None if the resolver abstains)."""
    sc = PRONOUN_SCOPE[pronoun_low]
    cands = ov._compatible_entities(sc["gender"], sc["number"])
    if not cands:
        return 0.0, None
    sals = sorted((e.salience(now, ov.beta, ov.lam) for e in cands), reverse=True)
    best = sals[0]
    second = sals[1] if len(sals) > 1 else 0.0
    if best <= 0:
        return 0.0, None
    margin = (best - second) / best
    return margin, best


def extract_passage_conf(passage_text, clf, coref_strategy):
    """Mirror of O.extract_passage (learned / handrule / no-gold-heads) with per-relation provenance
    confidence. Returns (rels_sorted, reslog, prov) where prov maps rel_tuple -> {raw_parse_margin,
    coref_conf} (the MOST-confident provenance kept when a relation is emitted more than once)."""
    do_coref = coref_strategy is not None
    known = set()
    for txt in list(O.TEST_PASSAGES.values()):
        for s in O.split_sentences(txt):
            for _su, lo, _po in O.pos_tag_sentence(s):
                if O.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))
    rels = []
    reslog = []
    prov_list = {}   # rel_tuple -> list of (raw_parse_margin, coref_conf)

    def add(rel, raw_parse_margin, coref_conf):
        prov_list.setdefault(rel, []).append((raw_parse_margin, coref_conf))
        rels.append(rel)

    for sent in O.split_sentences(passage_text):
        tagged = O.pos_tag_sentence(sent)
        pron_res = {}
        pron_conf = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:
                if do_coref and low not in ("i", "you", "we"):
                    now = ov._next_midx
                    m, _best = _coref_margin(ov, low, now)
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy)
                    pron_res[i] = ent.head if ent is not None else None
                    pron_conf[i] = m if ent is not None else 0.0
                    reslog.append((low, pron_res[i]))
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in O.PRONOUNS_POSS:
                pass
            else:
                if not O.observe_as_mention(low, pos, "handrule", frozenset()):
                    continue
                is_name = (low in O.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                g, num = O.grounded_gender_number(low, is_name)
                ov.observe(low, gender=g, number=num, is_proper_name=is_name)

        roles, verb_idx, verb, passive, cand = O.assign_roles_learned(
            tagged, clf, "handrule", frozenset())
        first = cand[0] if cand else None

        # cache learned-role argmax margin per candidate index
        role_margin_cache = {}

        def rmargin(i):
            if i not in role_margin_cache:
                feats = O.candidate_features(tagged, i, verb_idx, passive, first)
                role_margin_cache[i] = _role_margin(clf, feats)
            return role_margin_cache[i]

        def head_of(i):
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            return tagged[i][1]

        def coref_conf_of(i):
            if i in pron_res:
                return pron_conf[i] if pron_res[i] is not None else 0.0
            return 1.0

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)

        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                pm = min(rmargin(agents[0]), rmargin(pi))
                cc = min(coref_conf_of(agents[0]), coref_conf_of(pi))
                add(("svo", verb, head_of(agents[0]), head_of(pi)), pm, cc)

        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or O.prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        pm = rmargin(i)
                        cc = min(coref_conf_of(agents[0]) if agents else 1.0, coref_conf_of(i))
                        add(("svo", "kind", subj_head, head_of(i)), pm, cc)

        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        pm = min(rmargin(owner_idx), rmargin(pi))
                        cc = min(coref_conf_of(owner_idx), coref_conf_of(pi))
                        add(("poss", head_of(owner_idx), head_of(pi)), pm, cc)

        for ri in recips:
            if verb is not None and agents:
                pm = min(rmargin(agents[0]), rmargin(ri))
                cc = min(coref_conf_of(agents[0]), coref_conf_of(ri))
                add(("recipient", verb, head_of(agents[0]), head_of(ri)), pm, cc)

        for li in locs:
            figure = subj_head
            fig_i = agents[0] if agents else (cand[0] if cand else None)
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
                    fig_i = j
            if figure is not None and figure != head_of(li):
                pm = min(rmargin(li), rmargin(fig_i) if fig_i is not None else rmargin(li))
                cc = min(coref_conf_of(li), coref_conf_of(fig_i) if fig_i is not None else 1.0)
                add(("loc", figure, head_of(li)), pm, cc)

        # ---- STRUCTURAL (POS-driven, NOT learned): possessive 's, poss-pronoun, color ----
        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        add(("poss", owner, head_of(j)), math.inf, coref_conf_of(j))
                        break
            if low in O.PRONOUNS_POSS and do_coref:
                if low in PRONOUN_SCOPE:
                    now = ov._next_midx
                    m, _best = _coref_margin(ov, low, now)
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy)
                    owner = ent.head if ent is not None else low
                    occ = m if ent is not None else 0.0
                else:
                    owner = low
                    occ = 1.0
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        add(("poss", owner, head_of(j)), math.inf, min(occ, coref_conf_of(j)))
                        break

        for i in range(len(tagged) - 1):
            if O.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        add(("attr", head_of(j), tagged[i][1], "COLOR"), math.inf, coref_conf_of(j))
                        break

    rels_sorted = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return rels_sorted, reslog, prov_list


# ===========================================================================================
# Confidence-aware query engine. Mirrors O.answer_reader's FIRST-MATCH logic exactly so NO_GATE
# reproduces the baseline answer, and returns (answer, rel_conf, n_distinct_matches). rel_conf uses
# the pre-normalized per-relation confidence in `conf_by_rel` (rel_tuple -> scalar in [0,1]).
# ===========================================================================================
def _match_conf(rels, conf_by_rel, pred, key_fn):
    """First relation r with pred(r) True: return (key_fn(r), conf_by_rel[r], n_distinct_keys)."""
    first = None
    keys = set()
    for r in rels:
        if pred(r):
            k = key_fn(r)
            keys.add(k)
            if first is None:
                first = (k, conf_by_rel.get(r, 0.0))
    if first is None:
        return None, 0.0, 0
    return first[0], first[1], len(keys)


def answer_reader_conf(spec, rels, conf_by_rel):
    op = spec[0]
    if op == "svo_agent":
        return _match_conf(rels, conf_by_rel,
                           lambda r: r[0] == "svo" and r[1] == spec[1] and r[3] == spec[2],
                           lambda r: r[2])
    if op == "svo_patient":
        return _match_conf(rels, conf_by_rel,
                           lambda r: r[0] == "svo" and r[1] == spec[1] and r[2] == spec[2],
                           lambda r: r[3])
    if op == "loc_ground":
        return _match_conf(rels, conf_by_rel,
                           lambda r: r[0] == "loc" and r[1] == spec[1], lambda r: r[2])
    if op == "has_owner":
        return _match_conf(rels, conf_by_rel,
                           lambda r: r[0] == "poss" and r[2] == spec[1], lambda r: r[1])
    if op == "loc_of_owned":
        owner, owned = spec[1], spec[2]
        poss = [r for r in rels if r[0] == "poss" and r[1] == owner and r[2] == owned]
        if not poss:
            return None, 0.0, 0
        a, lc, nd = _match_conf(rels, conf_by_rel,
                                lambda r: r[0] == "loc" and r[1] == owned, lambda r: r[2])
        if a is None:
            return None, 0.0, 0
        return a, min(lc, conf_by_rel.get(poss[0], 0.0)), nd
    if op == "owner_of_owned_chain":
        contained = spec[1]
        mids = [r for r in rels if r[0] == "poss" and r[2] == contained]
        for rm in mids:
            mid = rm[1]
            for r in rels:
                if r[0] == "poss" and r[2] == mid:
                    return r[1], min(conf_by_rel.get(rm, 0.0), conf_by_rel.get(r, 0.0)), 1
        return None, 0.0, 0
    return None, 0.0, 0


# ===========================================================================================
# Build the REAL store + per-question confidence over the FULL Q-set.
# ===========================================================================================
def build_clf():
    clf = O.AveragedPerceptron()
    clf.fit(O.build_training_examples(), O.N_EPOCHS)
    return clf


def _normalize_prov(prov_all):
    """Turn raw provenance (rel -> [(raw_parse_margin, coref_conf), ...]) into a per-passage
    rel -> scalar rel_conf in [0,1]. parse_conf = m/(m+SCALE) (SCALE = median positive finite raw
    parse margin across the whole corpus; inf sentinel -> 1.0). rel_conf = max over provenances of
    min(parse_conf, coref_conf)."""
    finite = [m for prov in prov_all.values() for provlist in prov.values()
              for (m, _c) in provlist if math.isfinite(m) and m > 0]
    scale = statistics.median(finite) if finite else 1.0
    if scale <= 0:
        scale = 1.0
    conf_by_pid = {}
    for pid, prov in prov_all.items():
        cbr = {}
        for rel, provlist in prov.items():
            best = 0.0
            for (m, cc) in provlist:
                pc = 1.0 if (math.isinf(m)) else (m / (m + scale) if m > 0 else 0.0)
                best = max(best, min(pc, cc))
            cbr[rel] = round(best, 6)
        conf_by_pid[pid] = cbr
    return conf_by_pid, scale


def build_real_conf(clf, qs):
    """Returns per-question records: {q, ans, conf, correct, n_distinct, is_answered}. Answers reproduce
    O.answer_reader (first-match). conf uses the normalized glass-box confidence; conflict caps it."""
    stores = {}
    provs = {}
    for pid, text in O.TEST_PASSAGES.items():
        rels, _rlog, prov = extract_passage_conf(text, clf, "maintained")
        stores[pid] = rels
        provs[pid] = prov
    conf_by_pid, scale = _normalize_prov(provs)

    recs = []
    for q in qs:
        rels = stores.get(q["p"], [])
        cbr = conf_by_pid.get(q["p"], {})
        ans, conf, n_distinct = answer_reader_conf(q["spec"], rels, cbr)
        if n_distinct > 1:
            conf = min(conf, CONFLICT_CAP)
        na, ng = O.normalize(ans), O.normalize(q["gold"])
        correct = 1 if (na is not None and na == ng) else 0
        recs.append({"q": q, "ans": na, "gold": ng, "conf": conf,
                     "n_distinct": n_distinct, "correct": correct,
                     "is_answered": na is not None,
                     "slice": q["slice"]})
    return recs, stores, scale


# ===========================================================================================
# Metrics over a gated arm (a set of answered records) -- global halluc def matches the baseline.
# ===========================================================================================
def _gate_metrics(recs, keep_fn):
    """keep_fn(rec) -> bool (True = answer, False = abstain). Global halluc = wrong-answered / n_total."""
    n_total = len(recs)
    n_correct_kept = sum(1 for r in recs if keep_fn(r) and r["correct"] == 1)
    n_wrong_kept = sum(1 for r in recs if keep_fn(r) and r["is_answered"] and r["correct"] == 0)
    n_answered = sum(1 for r in recs if keep_fn(r) and r["is_answered"])
    halluc = n_wrong_kept / n_total if n_total else 0.0
    coverage = n_answered / n_total if n_total else 0.0
    precision = n_correct_kept / n_answered if n_answered else 0.0
    return {"halluc": round(halluc, 4), "coverage": round(coverage, 4),
            "precision_on_answered": round(precision, 4),
            "n_answered": n_answered, "n_correct_kept": n_correct_kept, "n_wrong_kept": n_wrong_kept,
            "n_total": n_total}


def _auc(scores, labels):
    """AUROC via all-pairs (Mann-Whitney); labels 1=positive(correct). 0.5 on degenerate class."""
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1.0
            elif abs(p - n) <= CO_EPS:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def _auc_ci(scores, labels, rng, n_boot):
    base = _auc(scores, labels)
    n = len(scores)
    boots = []
    for _b in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        bs = [scores[i] for i in idx]
        bl = [labels[i] for i in idx]
        if len(set(bl)) < 2:
            continue
        boots.append(_auc(bs, bl))
    if not boots:
        return base, base, base
    boots.sort()
    lo = boots[int(0.025 * len(boots))]
    hi = boots[int(0.975 * len(boots)) - 1]
    return base, lo, hi


def precision_coverage_curve(recs):
    """Sweep the confidence threshold over observed answered-conf values; report the Pareto frontier."""
    answered = [r for r in recs if r["is_answered"]]
    confs = sorted(set(r["conf"] for r in answered))
    thresholds = [-1.0] + confs   # -1 = keep all answered (NO_GATE)
    curve = []
    for th in thresholds:
        m = _gate_metrics(recs, keep_fn=lambda r, th=th: r["is_answered"] and r["conf"] > th)
        m["threshold"] = round(th, 6)
        curve.append(m)
    return curve


def choose_operating_threshold(curve):
    """Lowest threshold (max coverage) achieving global halluc <= HP_HALLUC_MAX."""
    feasible = [c for c in curve if c["halluc"] <= HP_HALLUC_MAX]
    if not feasible:
        return curve[-1]   # cannot happen (highest threshold -> 0 answered -> halluc 0), defensive
    return max(feasible, key=lambda c: (c["coverage"], -c["threshold"]))


def scramble_null(recs, n_answered_target, rng, n_seeds):
    """Matched-coverage random abstention: keep n_answered_target of the answered Qs uniformly at
    random; report the halluc / precision null distribution (the 'answer fewer' baseline)."""
    answered = [r for r in recs if r["is_answered"]]
    n_total = len(recs)
    hall = []
    prec = []
    k = min(n_answered_target, len(answered))
    for _s in range(n_seeds):
        keep = rng.sample(range(len(answered)), k) if k > 0 else []
        keepset = set(keep)
        n_wrong = sum(1 for j in keepset if answered[j]["correct"] == 0)
        n_corr = sum(1 for j in keepset if answered[j]["correct"] == 1)
        hall.append(n_wrong / n_total)
        prec.append(n_corr / k if k else 0.0)
    return {"halluc_mean": round(statistics.mean(hall), 4),
            "halluc_p95": round(sorted(hall)[int(0.95 * len(hall)) - 1], 4) if hall else 0.0,
            "precision_mean": round(statistics.mean(prec), 4),
            "n_kept": k, "n_seeds": n_seeds}


# ===========================================================================================
# Verdict.
# ===========================================================================================
def compute_verdict(res):
    auc = res["auc"]["combined"]
    op = res["operating_point"]
    retained = res["retained_correct_frac"]
    precision = op["precision_on_answered"]
    op_halluc = op["halluc"]
    beat = res["beat_scramble"]

    hp = (auc >= HP_AUC_MIN and retained >= HP_RETAINED_CORRECT_MIN and
          precision >= HP_PRECISION_MIN and op_halluc <= HP_HALLUC_MAX and
          beat >= HP_BEAT_SCRAMBLE_MIN)
    hf = (auc <= HF_AUC_MAX or retained <= HF_RETAINED_CORRECT_MAX or beat <= HF_BEAT_SCRAMBLE_MAX)

    if hp:
        tier, outcome = "HARD_PASS", "restores-zero-halluc-at-coverage"
    elif hf:
        tier, outcome = "HARD_FAIL", "must-abstain-all-or-signal-uninformative"
    else:
        tier, outcome = "MIDDLE_BAND", "partial-precision-coverage-tradeoff"

    localize = []
    if auc <= HF_AUC_MAX:
        localize.append("confidence NOT informative: AUC(conf,correct)=%.3f <= %.2f (parse-only=%.3f "
                        "coref-only=%.3f) -- cannot rank its own right answers above its own wrong ones"
                        % (auc, HF_AUC_MAX, res["auc"]["parse_only"], res["auc"]["coref_only"]))
    if retained <= HF_RETAINED_CORRECT_MAX:
        localize.append("to reach halluc<=%.2f the gate abstains on ~everything: retained_correct_frac="
                        "%.3f <= %.2f (kept %d of %d originally-correct)"
                        % (HP_HALLUC_MAX, retained, HF_RETAINED_CORRECT_MAX,
                           op["n_correct_kept"], res["baseline"]["n_correct"]))
    if beat <= HF_BEAT_SCRAMBLE_MAX:
        localize.append("gate no better than RANDOM abstention at matched coverage: scramble_halluc-"
                        "op_halluc=%.3f <= %.2f (real=%.3f scramble=%.3f)"
                        % (beat, HF_BEAT_SCRAMBLE_MAX, op_halluc, res["scramble"]["halluc_mean"]))
    if not localize:
        if hp:
            localize.append("glass-box confidence discriminates: AUC=%.3f, kept %d/%d correct, "
                            "precision_on_answered=%.3f, beats random abstention by %.3f"
                            % (auc, op["n_correct_kept"], res["baseline"]["n_correct"], precision, beat))
        else:
            localize.append("partial: halluc %.3f->%.3f at coverage %.3f (retained_correct=%.3f, AUC=%.3f)"
                            % (res["baseline"]["halluc"], op_halluc, op["coverage"], retained, auc))

    msg = ("%s (%s) | NO_GATE halluc=%.3f cov=1.000 prec=%.3f | AUC comb=%.3f [%.3f,%.3f] "
           "(parse=%.3f coref=%.3f) | OP@th=%.3f: halluc=%.3f cov=%.3f prec=%.3f retained_correct=%.3f "
           "(%d/%d) | scramble halluc=%.3f -> beat=%.3f" % (
               tier, outcome, res["baseline"]["halluc"], res["baseline"]["precision_on_answered"],
               auc, res["auc"]["ci_lo"], res["auc"]["ci_hi"], res["auc"]["parse_only"],
               res["auc"]["coref_only"], op["threshold"], op_halluc, op["coverage"], precision,
               retained, op["n_correct_kept"], res["baseline"]["n_correct"],
               res["scramble"]["halluc_mean"], beat))
    return tier, outcome, msg, localize


# ===========================================================================================
# Full assembly.
# ===========================================================================================
def run_all(qs, clf):
    recs, stores, scale = build_real_conf(clf, qs)

    no_gate = _gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]

    answered = [r for r in recs if r["is_answered"]]
    scores = [r["conf"] for r in answered]
    labels = [r["correct"] for r in answered]
    rng = random.Random(SEED)
    auc_comb, ci_lo, ci_hi = _auc_ci(scores, labels, rng, N_BOOT)
    # parse-only / coref-only AUC: recompute per-answer conf from each signal alone is not stored
    # separately, so approximate via the combined-signal decomposition is not available; instead we
    # rank by the two component ceilings we DID store on records (added below). Fall back to combined
    # if components absent.
    parse_scores = [r.get("parse_conf", r["conf"]) for r in answered]
    coref_scores = [r.get("coref_conf", r["conf"]) for r in answered]
    auc_parse = _auc(parse_scores, labels)
    auc_coref = _auc(coref_scores, labels)

    curve = precision_coverage_curve(recs)
    op = choose_operating_threshold(curve)
    retained = (op["n_correct_kept"] / n_correct) if n_correct else 0.0

    srng = random.Random(SEED + 1)
    scramble = scramble_null(recs, op["n_answered"], srng, N_SCRAMBLE_SEEDS)
    beat = round(scramble["halluc_mean"] - op["halluc"], 4)

    # representative single scramble arm for arms-differ
    arng = random.Random(SEED + 2)
    k = op["n_answered"]
    keep_idx = set(arng.sample(range(len(answered)), min(k, len(answered)))) if k > 0 else set()
    answered_id = {id(r): j for j, r in enumerate(answered)}
    scramble_answers = []
    for r in recs:
        if not r["is_answered"]:
            scramble_answers.append(None)
        else:
            j = answered_id[id(r)]
            scramble_answers.append(r["ans"] if j in keep_idx else None)

    no_gate_answers = [r["ans"] if r["is_answered"] else None for r in recs]
    gate_answers = [r["ans"] if (r["is_answered"] and r["conf"] > op["threshold"]) else None for r in recs]

    res = {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"],
                     "n_correct": n_correct, "n_answered": no_gate["n_answered"],
                     "n_wrong": no_gate["n_wrong_kept"], "n_total": no_gate["n_total"]},
        "auc": {"combined": round(auc_comb, 4), "ci_lo": round(ci_lo, 4), "ci_hi": round(ci_hi, 4),
                "parse_only": round(auc_parse, 4), "coref_only": round(auc_coref, 4), "n_boot": N_BOOT,
                "n_pos": sum(labels), "n_neg": len(labels) - sum(labels)},
        "operating_point": op,
        "retained_correct_frac": round(retained, 4),
        "scramble": scramble,
        "beat_scramble": beat,
        "curve": curve,
        "margin_scale": round(scale, 6),
        "cross_turn": _cross_turn_report(recs, op),
        "_answers": {"NO_GATE": no_gate_answers, "ABSTAIN_GATE": gate_answers, "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "slice": r["slice"], "ans": r["ans"], "gold": r["gold"],
                         "conf": r["conf"], "correct": r["correct"], "n_distinct": r["n_distinct"]}
                        for r in recs],
    }
    return res


def _cross_turn_report(recs, op):
    ct = [r for r in recs if r["slice"] in CROSS_TURN_SLICES]
    ng = _gate_metrics(ct, keep_fn=lambda r: r["is_answered"])
    gated = _gate_metrics(ct, keep_fn=lambda r: r["is_answered"] and r["conf"] > op["threshold"])
    return {"no_gate": ng, "gated": gated}


def _arms_differ(res):
    digests = {}
    for name in ("NO_GATE", "ABSTAIN_GATE", "SCRAMBLE_GATE"):
        digests[name] = hashlib.sha256(
            json.dumps(res["_answers"][name], sort_keys=True).encode()).hexdigest()
    assert digests["NO_GATE"] != digests["ABSTAIN_GATE"], \
        "META_RULE_AF: NO_GATE == ABSTAIN_GATE (the gate abstained on nothing)"
    assert digests["ABSTAIN_GATE"] != digests["SCRAMBLE_GATE"], \
        "META_RULE_AF: ABSTAIN_GATE == SCRAMBLE_GATE (gate identical to random abstention)"
    return digests


# ===========================================================================================
# infra: markers / metrics / crash (atomic).
# ===========================================================================================
def _out_dir(run_mode):
    sub = ANCHOR_NAME + ("_smoke" if run_mode == "smoke" else "")
    d = REPO / "data" / ("exp_" + sub)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(out_dir, diag)


# ===========================================================================================
# self-test: exercise the REAL code path + assert the discriminators FIRE + one-variable isolation.
# ===========================================================================================
def self_test():
    print("[self-test] building REAL pipeline (perceptron fit + conf-extractor) ...", flush=True)
    clf = build_clf()

    # (1) ONE-VARIABLE ISOLATION: conf-extractor relation SET == base O.extract_passage per passage.
    for pid, text in O.TEST_PASSAGES.items():
        base_rels, _ = O.extract_passage(text, "learned", clf, "maintained", "handrule", frozenset())
        conf_rels, _rl, _prov = extract_passage_conf(text, clf, "maintained")
        assert set(base_rels) == set(conf_rels), \
            "ONE-VARIABLE BREACH: conf-extractor relations != base for %s\n base-only=%s\n conf-only=%s" % (
                pid, sorted(set(base_rels) - set(conf_rels)), sorted(set(conf_rels) - set(base_rels)))

    # (2) POSITIVE CONTROL: NO_GATE per-question answers reproduce O.answer_reader exactly.
    recs, stores, scale = build_real_conf(clf, O.TEST_QS)
    for r in recs:
        base_ans = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base_ans, "answer drift on %s: conf=%r base=%r" % (r["q"]["qid"], r["ans"], base_ans)

    # (3) baseline reproduces the 0.4194 hallucination + n_correct==8 (positive control vs prior cell).
    ng = _gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    assert abs(ng["halluc"] - BASE_HALLUC) <= BASE_HALLUC_TOL, \
        "baseline halluc=%.4f not within %.3f of prior %.4f" % (ng["halluc"], BASE_HALLUC_TOL, BASE_HALLUC)
    assert ng["n_correct_kept"] == BASE_N_CORRECT, \
        "baseline n_correct=%d != expected %d" % (ng["n_correct_kept"], BASE_N_CORRECT)

    # (4) confidence scalar is in [0,1] and NOT constant (a constant conf cannot gate).
    confs = [r["conf"] for r in recs if r["is_answered"]]
    assert all(0.0 <= c <= 1.0 for c in confs), "conf out of [0,1]"
    assert len(set(round(c, 4) for c in confs)) >= 3, \
        "confidence near-constant (%d distinct) -- cannot gate" % len(set(round(c, 4) for c in confs))

    # (5) the gate CAN change the answer set (abstains on at least one wrong answer at SOME threshold);
    # discriminator is allowed to be weak (can-fail) but must be EXERCISED.
    _attach_component_confs(clf, O.TEST_QS)
    full = run_all_with_components(O.TEST_QS, clf)
    _arms_differ(full)
    assert full["operating_point"]["threshold"] > -1.0 or full["operating_point"]["coverage"] < 1.0, \
        "gate never abstains -- operating point keeps everything"

    print("[self-test] PASS | isolation OK | NO_GATE halluc=%.4f n_correct=%d | AUC comb=%.3f "
          "parse=%.3f coref=%.3f | OP th=%.3f halluc=%.3f retained=%.3f | beat_scramble=%.3f | scale=%.4f"
          % (ng["halluc"], ng["n_correct_kept"], full["auc"]["combined"], full["auc"]["parse_only"],
             full["auc"]["coref_only"], full["operating_point"]["threshold"],
             full["operating_point"]["halluc"], full["retained_correct_frac"],
             full["beat_scramble"], full["margin_scale"]), flush=True)
    return True


def _augment_component_conf(recs, clf):
    """No-op hook kept for interface parity (component confs are attached in run() via re-derivation)."""
    return recs


# ===========================================================================================
# main.
# ===========================================================================================
def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        smoke_pids = {"L5_dogs", "L18_king", "L14_henry", "L60_geo", "L32_tiger", "L28_sam"}
        qs = [q for q in qs if q["p"] in smoke_pids]
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units=len(qs))
    t0 = time.perf_counter()

    clf = build_clf()
    # attach per-signal component confidences to records for parse-only / coref-only AUC
    _attach_component_confs(clf, qs)
    res = run_all_with_components(qs, clf)
    digests = _arms_differ(res)
    tier, outcome, msg, localize = compute_verdict(res)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_questions": len(qs),
        "arms": ["NO_GATE", "ABSTAIN_GATE", "SCRAMBLE_GATE"],
        "baseline_no_gate": res["baseline"],
        "auc": res["auc"],
        "operating_point": res["operating_point"],
        "retained_correct_frac": res["retained_correct_frac"],
        "scramble_matched_coverage": res["scramble"],
        "beat_scramble": res["beat_scramble"],
        "precision_coverage_curve": res["curve"],
        "cross_turn": res["cross_turn"],
        "margin_scale": res["margin_scale"],
        "confidence_signals": ["parse_margin(perceptron argmax-runnerup)",
                               "coref_margin(maintained-overlay salience gap)",
                               "match_support(conflict cap)"],
        "gate_threshold_kind": "fixed_interpretable_rule_not_learned",
        "flexible_improving": "n/a_fixed_rule (curve is the deliverable; learned threshold overfits 21 pts)",
        "bands": {"HP_auc_min": HP_AUC_MIN, "HP_retained_correct_min": HP_RETAINED_CORRECT_MIN,
                  "HP_precision_min": HP_PRECISION_MIN, "HP_halluc_max": HP_HALLUC_MAX,
                  "HP_beat_scramble_min": HP_BEAT_SCRAMBLE_MIN, "HF_auc_max": HF_AUC_MAX,
                  "HF_retained_correct_max": HF_RETAINED_CORRECT_MAX,
                  "HF_beat_scramble_max": HF_BEAT_SCRAMBLE_MAX},
        "coverage_at_zero_halluc_ceiling": round(res["baseline"]["n_correct"] / res["baseline"]["n_total"], 4),
        "weakest_interface": localize,
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; coverage-at-zero-halluc ceiling 8/31=0.258 is the feasibility bound",
        "per_question": res["_recs_debug"],
        "reuse_credited": {
            "realtext_loop_and_baseline": "exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1.py",
            "realtext_components_and_gold": "exp_oracle_mention_upperbound_reader_v1.py",
            "coref_abstain_discipline": "hdlab/state_of_mind.py resolve_pronoun (abstains on no-compatible; "
                                        "extended downstream to low-salience-margin abstention)"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "auc", "operating_point",
                            "retained_correct_frac", "scramble_matched_coverage", "beat_scramble",
                            "arms_differ_digests"],
        "notes": ("Confidence/abstain gate over the real-text conversational loop. Glass-box signals "
                  "(perceptron role margin + maintained-overlay coref salience margin + match-conflict), "
                  "no autograd, no LLM. Primary discriminator = AUC(conf,correct) over the 21 answered "
                  "Qs; SCRAMBLE_GATE = matched-coverage random abstention anti-cheat. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] halluc=%.3f cov=1.000 prec=%.3f (correct=%d wrong=%d abstain=%d of %d)"
          % (res["baseline"]["halluc"], res["baseline"]["precision_on_answered"],
             res["baseline"]["n_correct"], res["baseline"]["n_wrong"],
             res["baseline"]["n_total"] - res["baseline"]["n_answered"], res["baseline"]["n_total"]), flush=True)
    print("  [AUC     ] combined=%.3f [%.3f,%.3f] parse_only=%.3f coref_only=%.3f (pos=%d neg=%d)"
          % (res["auc"]["combined"], res["auc"]["ci_lo"], res["auc"]["ci_hi"], res["auc"]["parse_only"],
             res["auc"]["coref_only"], res["auc"]["n_pos"], res["auc"]["n_neg"]), flush=True)
    op = res["operating_point"]
    print("  [OP GATE ] th=%.3f halluc=%.3f cov=%.3f prec=%.3f retained_correct=%.3f (kept %d/%d correct)"
          % (op["threshold"], op["halluc"], op["coverage"], op["precision_on_answered"],
             res["retained_correct_frac"], op["n_correct_kept"], res["baseline"]["n_correct"]), flush=True)
    print("  [SCRAMBLE] matched-cov halluc_mean=%.3f p95=%.3f -> real BEATS random by %.3f"
          % (res["scramble"]["halluc_mean"], res["scramble"]["halluc_p95"], res["beat_scramble"]), flush=True)
    print("  [weakest ] %s" % localize, flush=True)
    print("  [metrics ] -> %s" % (out_dir / "metrics.json"), flush=True)
    return tier


# component-confidence attachment (parse-only / coref-only AUC): re-derive per-question the parse and
# coref confidences of the MATCHED relation, so we can report which signal carries the discrimination.
_COMPONENT_CACHE = {}


def _attach_component_confs(clf, qs):
    """Populate a cache: (pid) -> {rel: (parse_conf, coref_conf)} using the same normalization as the
    combined signal, so parse-only / coref-only AUC use the actual component values."""
    provs = {}
    for pid, text in O.TEST_PASSAGES.items():
        _rels, _rl, prov = extract_passage_conf(text, clf, "maintained")
        provs[pid] = prov
    finite = [m for prov in provs.values() for pl in prov.values() for (m, _c) in pl
              if math.isfinite(m) and m > 0]
    scale = statistics.median(finite) if finite else 1.0
    if scale <= 0:
        scale = 1.0
    comp = {}
    for pid, prov in provs.items():
        cbr = {}
        for rel, pl in prov.items():
            best_pc = best_cc = -1.0
            best_rel = -1.0
            for (m, cc) in pl:
                pc = 1.0 if math.isinf(m) else (m / (m + scale) if m > 0 else 0.0)
                if min(pc, cc) > best_rel:
                    best_rel = min(pc, cc)
                    best_pc, best_cc = pc, cc
            cbr[rel] = (round(best_pc, 6), round(best_cc, 6))
        comp[pid] = cbr
    _COMPONENT_CACHE.clear()
    _COMPONENT_CACHE.update(comp)


def run_all_with_components(qs, clf):
    """run_all + attach parse_conf/coref_conf to each answered record for component AUC."""
    recs, stores, scale = build_real_conf(clf, qs)
    # attach component confs to the matched relation per question (mirror answer match to fetch the rel)
    for r in recs:
        pid = r["q"]["p"]
        comp = _COMPONENT_CACHE.get(pid, {})
        pc, cc = _matched_component_conf(r["q"]["spec"], stores.get(pid, []), comp)
        r["parse_conf"] = pc
        r["coref_conf"] = cc
    # now recompute res via the record-driven path
    return _run_from_recs(recs, scale)


def _matched_component_conf(spec, rels, comp):
    """Find the matched relation (first-match) and return its (parse_conf, coref_conf); (conf,conf) fallback."""
    def look(pred):
        for r in rels:
            if pred(r):
                return comp.get(r, None)
        return None
    op = spec[0]
    got = None
    if op == "svo_agent":
        got = look(lambda r: r[0] == "svo" and r[1] == spec[1] and r[3] == spec[2])
    elif op == "svo_patient":
        got = look(lambda r: r[0] == "svo" and r[1] == spec[1] and r[2] == spec[2])
    elif op == "loc_ground":
        got = look(lambda r: r[0] == "loc" and r[1] == spec[1])
    elif op == "has_owner":
        got = look(lambda r: r[0] == "poss" and r[2] == spec[1])
    elif op == "loc_of_owned":
        got = look(lambda r: r[0] == "loc" and r[1] == spec[2])
    elif op == "owner_of_owned_chain":
        got = look(lambda r: r[0] == "poss" and r[2] == spec[1])
    if got is None:
        return 1.0, 1.0
    return got


def _run_from_recs(recs, scale):
    """Assemble res dict from finished records (with conf + parse_conf/coref_conf)."""
    no_gate = _gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]
    answered = [r for r in recs if r["is_answered"]]
    scores = [r["conf"] for r in answered]
    labels = [r["correct"] for r in answered]
    rng = random.Random(SEED)
    auc_comb, ci_lo, ci_hi = _auc_ci(scores, labels, rng, N_BOOT)
    auc_parse = _auc([r["parse_conf"] for r in answered], labels)
    auc_coref = _auc([r["coref_conf"] for r in answered], labels)

    curve = precision_coverage_curve(recs)
    op = choose_operating_threshold(curve)
    retained = (op["n_correct_kept"] / n_correct) if n_correct else 0.0

    srng = random.Random(SEED + 1)
    scramble = scramble_null(recs, op["n_answered"], srng, N_SCRAMBLE_SEEDS)
    beat = round(scramble["halluc_mean"] - op["halluc"], 4)

    arng = random.Random(SEED + 2)
    k = op["n_answered"]
    keep_idx = set(arng.sample(range(len(answered)), min(k, len(answered)))) if k > 0 else set()
    answered_id = {id(r): j for j, r in enumerate(answered)}
    scramble_answers = []
    for r in recs:
        if not r["is_answered"]:
            scramble_answers.append(None)
        else:
            j = answered_id[id(r)]
            scramble_answers.append(r["ans"] if j in keep_idx else None)
    no_gate_answers = [r["ans"] if r["is_answered"] else None for r in recs]
    gate_answers = [r["ans"] if (r["is_answered"] and r["conf"] > op["threshold"]) else None for r in recs]

    return {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"],
                     "n_correct": n_correct, "n_answered": no_gate["n_answered"],
                     "n_wrong": no_gate["n_wrong_kept"], "n_total": no_gate["n_total"]},
        "auc": {"combined": round(auc_comb, 4), "ci_lo": round(ci_lo, 4), "ci_hi": round(ci_hi, 4),
                "parse_only": round(auc_parse, 4), "coref_only": round(auc_coref, 4), "n_boot": N_BOOT,
                "n_pos": sum(labels), "n_neg": len(labels) - sum(labels)},
        "operating_point": op, "retained_correct_frac": round(retained, 4),
        "scramble": scramble, "beat_scramble": beat, "curve": curve, "margin_scale": round(scale, 6),
        "cross_turn": _cross_turn_report(recs, op),
        "_answers": {"NO_GATE": no_gate_answers, "ABSTAIN_GATE": gate_answers, "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "slice": r["slice"], "ans": r["ans"], "gold": r["gold"],
                         "conf": r["conf"], "parse_conf": r.get("parse_conf"), "coref_conf": r.get("coref_conf"),
                         "correct": r["correct"], "n_distinct": r["n_distinct"]} for r in recs],
    }


def main():
    ap = argparse.ArgumentParser(description=ANCHOR_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)
    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    run(run_mode)
    sys.exit(0)


if __name__ == "__main__":
    _md = "smoke" if ("--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv)) else \
        ("self_test" if ("--self-test" in sys.argv or ("--run-mode" in sys.argv and "self_test" in sys.argv)) else "full")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
