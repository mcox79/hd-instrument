"""INGEST-LEARN LOOP CYCLE-3 -- the FAIR "reads better over time" test.

WHY (the cycle-2 VET mandate): cycle-2 (ingest_learn_sleep_loop_cycle2) proved the loop learns GENUINELY
GOOD selectional knowledge (2AFC +0.25, p=0.0004) but its who-did-what reading curve was FLAT and NOT a
FAIR test, for two reasons: (a) simple declarative who-did-what is STRUCTURE-SATURATED (nearest-noun ~98%,
no headroom for knowledge), and (b) the gold was spaCy-dobj SILVER while the reader ALSO used spaCy = a
CIRCULAR ceiling. This cell builds the fair test the VET demanded: all three of
  (1) a ROLE-AMBIGUOUS, KNOWLEDGE-SENSITIVE reading decision with real HEADROOM (structure genuinely fails a
      meaningful fraction) -- PP-ATTACHMENT (does "prep n2" attach to the VERB or the preceding NOUN?), the
      parser's biggest error class and the classic selectional/world-knowledge parse decision (Hindle&Rooth
      1993). Structure baseline = 0.664 with headroom to ~0.85 (MEASURED below), NOT ~0.98.
  (2) a REAL, NON-CIRCULAR, HUMAN gold -- the UD-English-EWT treebank (human annotators' dependency heads:
      obl->VERB = V attachment, nmod->NOUN = N attachment). spaCy NEVER touches the test sentences; the gold
      is entirely independent of the reader's parser. This is what fixes the cycle-2 circularity.
  (3) the INGEST LEARNING CURVE (the point) -- ingest OneStopEnglish (read -> extract PP attachments ->
      accumulate a Hindle&Rooth-style lexical-association table) at fractions [0,.25,.5,.75,1.0], then measure
      the hard PP-attach decision accuracy on the HELD-OUT human-gold UD items using ONLY the accumulated
      reading knowledge. Does accuracy RISE as more is ingested?

THE DECISION (isolated binary sub-decision, identical mechanism across all arms):
  Given an ambiguous quadruple (verb v, noun n1, prep, noun n2) in linear order v ... n1 prep n2, decide
  whether "prep n2" attaches to v (label V) or to n1 (label N). accuracy = fraction predicted == UD gold.

THE INGEST (the "reads better over time" lever = REAL reading, NOT an LLM table):
  Read OneStopEnglish articles with spaCy. For every prepositional phrase (ADP dep=prep with a NOUN/PROPN
  pobj n2) attaching to a head H, record the lexical association
       assoc[(H_lemma, prep)][supersense(n2)] += 1   ;   head_pp_total[H_lemma] += 1
  This is the classic Hindle&Rooth lexical-association model of PP-attachment, with the association counts
  ACCUMULATED BY READING (the ingest loop) instead of supplied by an LLM. n2 is generalized to its WordNet
  supersense (the cycle-2 condenser granularity) so a modest corpus yields real coverage. spaCy parses the
  TRAINING corpus (OneStop, a DIFFERENT corpus from the test); the aggregate lexical statistics are the
  training signal, evaluated against INDEPENDENT human UD gold on held-out sentences -- the standard, NON-
  circular Hindle&Rooth paradigm (parser-derived aggregate priors, human-gold test).

ARMS (ONE VARIABLE = the knowledge; SAME items, split, binary mechanism across all):
  ARM_STRUCTURE  (baseline / f=0): Collins&Brooks prep-preference from UD-TRAIN (human gold). Knows syntax,
     NOTHING about the specific content words. Standard strong syntax-only model. == curve point f=0.00.
  ARM_INGEST@f   (the curve): structure + the OneStop-learned association table from the first k=round(f*N)
     ingest units; an item is knowledge-decided iff a head has a learned (head,prep) association AND the two
     head scores differ, else backoff to ARM_STRUCTURE. score(head,prep,ss)=assoc[(head,prep)][ss]/(head_pp_
     total[head]+SMOOTH) (a frequency-normalized selectional-association strength; glass-box DICT LOOKUP, NO
     LLM/network/autograd at inference). Decide V iff score(v,prep,ss) > score(n1,prep,ss).
  ARM_INGEST_SCRAMBLED (must-fail knowledge control): full table with head keys permuted (bijection) ->
     destroys head-specific associations, preserves marginals. If scrambling keeps the lift, the lift was an
     artifact not the reading -> the cell FAILS its own control.
  ARM_MAJORITY (floor sentinel) ; ARM_RANDOM (fixed-seed chance control ~0.5, proves task not saturated).

HONEST DIAGNOSIS (built in): coverage_frac = fraction of test items the reading knowledge is ACTIVE on at
  f=1. On the ACTIVE subset we report active_acc vs structure-on-active_acc = whether the reading knowledge
  DISCRIMINATES where it fires. A small overall rise decomposes as: COVERAGE gap (few test heads/preps seen
  in OneStop -> loop must ingest the RIGHT text) vs MECHANISM gap (covered but associations don't help). A
  FLAT curve is reported plainly and diagnosed; it is NEVER faked and the circular gold is NEVER reused.

VERDICT BANDS (pre-registered BEFORE running; do NOT redefine mid-run):
  HARD_PASS_INGEST_READS_BETTER_FAIRLY:
     rise = acc_ingest[f=1.00] - acc_structure ; rise >= 0.03 AND acc_ingest[1.00] > acc_structure
     AND n_nonneg_steps >= 3 (curve mostly monotone up)
     AND acc_scrambled <= acc_structure + 0.03 (lift is head-lexical READING knowledge, not artifact)
     AND 0.40 <= acc_random <= 0.60 (task can-fail, not saturated)
     AND 0.05 < acc_structure < 0.95 (baseline in measurable band)
     -> ingesting OneStop makes a hard, non-circular, knowledge-sensitive reading decision BETTER as it reads
        more; USER criterion #1 (reads-better) MET FAIRLY.
  FLAT_HONEST_COVERAGE_OR_MECHANISM:
     rise <= 0.01 -> the ingested selectional knowledge does not transfer to this decision at this scale;
     honest can-fail; the coverage-vs-mechanism decomposition is reported (a real finding: the loop must
     ingest the right text). NOT a substrate failure claim.
  MIDDLE_BAND: otherwise (partial rise, or rise present but a control/gate not fully clean).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- spaCy en_core_web_sm parse of OneStop
  ingest articles + O(items) dict-lookup comparisons; NO matmul, NO GPU-batchable primitive; wall bounded by
  the spaCy parse (~2.5 min for all ingest units). Storage: no_storage (association table = plain dict dumped
  LOCAL-ONLY json). progress_logging: print_flush per ingest batch + per curve point (timeout>=1800).
  Runtime invariant: glass-box dict lookup ONLY at inference, NO LLM/network/autograd (spaCy is the READING
  front-end at ingest time only; the test sentences are pre-parsed HUMAN UD gold, never spaCy). Determinism:
  OMP/MKL/OPENBLAS=1, sorted article order, fixed int seeds, numpy default_rng, sorted(set); spaCy deterministic.
  LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO git add -A.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash on per-item prediction vectors)
  - final_metrics_atomicity: tmp_replace ; start-marker at entry ; crash-diagnostic metrics
  - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except)
  - crlb_n/a: binary attachment-accuracy; no quantitative noise floor for the discriminator
  - baseline_in_band at smoke: ARM_STRUCTURE in (0.05,0.95); ARM_RANDOM ~0.5 = can-fail
  - discriminator survives scale: the FULL run ingests ALL units (max coverage) = the reported scale; smoke =
    fewer ingest units, SAME mechanism (fewer active items by design; full is the scale)
  - HARD_PASS strictly above floor (rise>=0.03, well above the +0.01 FLAT edge)
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
  - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()/list(set())
  - cardinality_ok: curve has EXPECTED_COV_POINTS=5; verdict counts them
  - real_code_path: self_test constructs the REAL UD extraction + REAL spaCy ingest at tiny scale

TAGGED NUMBERS:
  - UD test 446 items (gold N=288/V=158), acc_structure=0.6637, acc_majority=0.6457, n_train=3966:
    MEASURED@scratchpad probe 2026-07-24 (experiments.exp_pivot_pp_attachment_rich_knowledge_v1 extract+baseline)
  - OneStop parse 0.271s/article, 740 pp-obs / 12 adv articles: MEASURED@scratchpad probe 2026-07-24
  - PP-attach = parser's biggest single error class (18.5%): CITED@exp_depparse_transition_richfeat_cpu_v1
  - Hindle&Rooth lexical-association PP-attach model: CITED@Hindle&Rooth 1993 "Structural Ambiguity and Lexical Relations"
  - cycle-2 selectional 2AFC +0.25 p=0.0004: CITED@data/exp_ingest_learn_sleep_loop_cycle2_v1/metrics.json (29528)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import glob
import json
import time
import hashlib
import argparse
import platform
import traceback
from collections import defaultdict, Counter
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# Reuse the BANKED 29472 PP-attach machinery (human-gold UD extraction + fair syntactic baseline + accuracy)
import experiments.exp_pivot_pp_attachment_rich_knowledge_v1 as PPA
import experiments.exp_scene_coherence_verifier_contrastive_scv_v1 as SCV

ANCHOR_NAME = "ingest_learn_sleep_loop_cycle3_ppattach_v1"
SEED = 20260724

# OneStopEnglish graded corpus (the ingest text)
ONESTOP = os.path.join(_REPO, "data", "corpora", "onestop", "Texts-SeparatedByReadingLevel")
LEVEL_DIRS = {"ele": os.path.join(ONESTOP, "Ele-Txt"),
              "int": os.path.join(ONESTOP, "Int-Txt"),
              "adv": os.path.join(ONESTOP, "Adv-Txt")}
LEVEL_SUFFIX = {"ele": "-ele.txt", "int": "-int.txt", "adv": "-adv.txt"}
INGEST_LEVELS = ("ele", "int", "adv")           # read each topic at all 3 levels = max reading

CURVE_FRACS = [0.0, 0.25, 0.5, 0.75, 1.0]
EXPECTED_COV_POINTS = len(CURVE_FRACS)
SMOOTH = 0.5                                     # denominator smoothing on the selectional-association score
N_INGEST_SMOKE = 8                               # ingest units (topics) in smoke
NOMINAL = {"NOUN", "PROPN"}

_NLP = None


def get_nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _out_dir(mode):
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(d, exist_ok=True)
    return d


# ----------------------------------------------------------------------------------------------
# OneStop reading -> PP attachment observations (the INGEST).
# ----------------------------------------------------------------------------------------------
def _read_article_text(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if lines and lines[0].lower() in ("elementary", "intermediate", "advanced"):
        lines = lines[1:]
    return " ".join(lines)


def _ingest_bases():
    """Sorted topic base-names present at ALL 3 reading levels (deterministic ingest order)."""
    def bases(level):
        d, suf = LEVEL_DIRS[level], LEVEL_SUFFIX[level]
        return set(os.path.basename(p)[:-len(suf)] for p in glob.glob(os.path.join(d, "*" + suf)))
    common = bases("ele") & bases("int") & bases("adv")
    return sorted(common)


def extract_pp_observations(doc):
    """From a spaCy-parsed doc, yield (head_lemma, prep_lemma, n2_supersense, head_pos) for each PP.
    ADP dep=prep with a NOUN/PROPN pobj; head is a VERB (verb-attach) or NOUN/PROPN (noun-attach)."""
    obs = []
    for tok in doc:
        if tok.pos_ != "ADP" or tok.dep_ != "prep":
            continue
        pobjs = [c for c in tok.children if c.dep_ == "pobj" and c.pos_ in NOMINAL]
        if not pobjs:
            continue
        n2 = pobjs[0]
        head = tok.head
        if head.pos_ == "VERB":
            hp = "verb"
        elif head.pos_ in NOMINAL:
            hp = "noun"
        else:
            continue
        ss = SCV.supersense(n2.lemma_.lower())
        if ss is None:
            continue
        obs.append((head.lemma_.lower(), tok.lemma_.lower(), ss, hp))
    return obs


def ingest_unit_stream(base):
    """Read one topic at all present reading levels; return its full PP-observation stream."""
    nlp = get_nlp()
    stream = []
    for lvl in INGEST_LEVELS:
        path = os.path.join(LEVEL_DIRS[lvl], base + LEVEL_SUFFIX[lvl])
        if not os.path.exists(path):
            continue
        text = _read_article_text(path)
        if not text:
            continue
        stream.extend(extract_pp_observations(nlp(text)))
    return stream


def build_ingest_streams(bases, log_every=20, tag="ingest"):
    """Parse each ingest unit ONCE (order preserved) -> list of per-unit observation streams."""
    streams = []
    t0 = time.perf_counter()
    for i, b in enumerate(bases):
        streams.append(ingest_unit_stream(b))
        if (i + 1) % log_every == 0 or (i + 1) == len(bases):
            print("  [%s] read %d/%d units (%d obs so far, %.1fs)" % (
                tag, i + 1, len(bases), sum(len(s) for s in streams),
                time.perf_counter() - t0), flush=True)
    return streams


# ----------------------------------------------------------------------------------------------
# Association table (Hindle&Rooth lexical association) accumulated from the reading.
# ----------------------------------------------------------------------------------------------
def build_assoc(stream):
    """stream = list of (head_lemma, prep, n2_supersense, head_pos).
    assoc[(head,prep)] = Counter over n2 supersense ; head_pp_total[head] = total PP-modifier obs."""
    assoc = defaultdict(Counter)
    head_pp_total = Counter()
    for head, prep, ss, _hp in stream:
        assoc[(head, prep)][ss] += 1
        head_pp_total[head] += 1
    return assoc, head_pp_total


def _score(head, prep, ss, assoc, head_pp_total):
    """Frequency-normalized selectional-association strength of head for (prep, ss). None = uncovered head."""
    denom = head_pp_total.get(head, 0)
    if denom == 0:
        return None
    num = assoc.get((head, prep), {})
    num = num.get(ss, 0) if num else 0
    return num / (denom + SMOOTH)


def scramble_assoc(assoc, head_pp_total, seed):
    """Permute head keys (bijection) -> destroys head-specific associations, preserves marginals."""
    heads = sorted(head_pp_total.keys())
    if not heads:
        return defaultdict(Counter), Counter()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(heads)).tolist()
    remap = {heads[i]: heads[perm[i]] for i in range(len(heads))}
    new_assoc = defaultdict(Counter)
    new_total = Counter()
    for (head, prep), ctr in assoc.items():
        nh = remap[head]
        for ss, c in ctr.items():
            new_assoc[(nh, prep)][ss] += c
    for head, c in head_pp_total.items():
        new_total[remap[head]] += c
    return new_assoc, new_total


def score_ingest(items, assoc, head_pp_total, syn_pred):
    """PP-attach accuracy using the reading-derived association table with structure backoff.
    Returns overall acc, per-item correctness + prediction vector, and the ACTIVE-subset decomposition
    (n_active = items decided by reading knowledge; active_acc vs structure-on-active_acc)."""
    correct = 0
    per = []
    preds = []
    n_active = 0
    active_correct = 0
    struct_on_active_correct = 0
    for it in items:
        ss = SCV.supersense(it["n2"])
        sv = sn = None
        if ss is not None:
            sv = _score(it["v"], it["prep"], ss, assoc, head_pp_total)
            sn = _score(it["n1"], it["prep"], ss, assoc, head_pp_total)
        active = False
        if ss is None or (sv is None and sn is None):
            p = syn_pred(it)                       # uncovered -> structure backoff
        else:
            svv = 0.0 if sv is None else sv
            snn = 0.0 if sn is None else sn
            if svv > snn:
                p = "V"; active = True
            elif snn > svv:
                p = "N"; active = True
            else:
                p = syn_pred(it)                   # tie -> structure backoff
        ok = int(p == it["gold"])
        correct += ok
        per.append(ok)
        preds.append(p)
        if active:
            n_active += 1
            active_correct += ok
            struct_on_active_correct += int(syn_pred(it) == it["gold"])
    n = max(1, len(items))
    return {
        "acc": round(correct / n, 4),
        "per_item": per, "preds": preds,
        "n_active": n_active,
        "coverage_frac": round(n_active / n, 4),
        "active_acc": (round(active_correct / n_active, 4) if n_active else None),
        "struct_on_active_acc": (round(struct_on_active_correct / n_active, 4) if n_active else None),
    }


def _pred_digest(preds):
    b = "".join("1" if x == "V" else "0" for x in preds).encode()
    return hashlib.sha256(b).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# metrics IO
# ----------------------------------------------------------------------------------------------
def _write_start_marker(out_dir, mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_metrics(out_dir, payload):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ----------------------------------------------------------------------------------------------
# ONE RUN
# ----------------------------------------------------------------------------------------------
def run_mode(mode):
    t0 = time.perf_counter()
    out_dir = _out_dir(mode)
    _write_start_marker(out_dir, mode)
    print("[%s:%s] START" % (ANCHOR_NAME, mode), flush=True)

    # ---- HUMAN-GOLD TEST (UD-EWT); NON-CIRCULAR, spaCy never touches these sentences ----
    test_items = PPA.extract_ppa("test")
    test_items = sorted(test_items, key=lambda d: (d["v"], d["n1"], d["prep"], d["n2"], d["gold"]))
    syn_pred, maj_pred, syn_stats = PPA.build_syntactic_model()
    acc_structure, pi_syn, pr_syn, strat_syn, strat_n = PPA.accuracy(test_items, syn_pred)
    acc_majority, _, pr_maj, _, _ = PPA.accuracy(test_items, maj_pred)
    rand_pred = PPA.make_random_pred()
    acc_random, _, pr_rand, _, _ = PPA.accuracy(test_items, rand_pred)
    print("  UD human-gold test items=%d gold=%s | acc_structure=%.4f acc_majority=%.4f acc_random=%.4f" % (
        len(test_items), dict(Counter(i["gold"] for i in test_items)),
        acc_structure, acc_majority, acc_random), flush=True)

    # ---- INGEST OneStop (read once, per-unit streams in order) ----
    bases = _ingest_bases()
    if mode == "smoke":
        bases = bases[:N_INGEST_SMOKE]
    print("  ingesting %d OneStop topic-units (%s levels) ..." % (len(bases), "+".join(INGEST_LEVELS)),
          flush=True)
    streams = build_ingest_streams(bases, log_every=(4 if mode == "smoke" else 20), tag=mode)
    full_stream = [o for s in streams for o in s]
    n_units = len(streams)

    # ---- LEARNING CURVE: accuracy vs ingest fraction (f=0 == ARM_STRUCTURE exactly) ----
    curve = {}
    curve_detail = {}
    for f in CURVE_FRACS:
        k = int(round(f * n_units))
        sl = [o for s in streams[:k] for o in s]
        assoc, hpt = build_assoc(sl)
        r = score_ingest(test_items, assoc, hpt, syn_pred)
        curve["%.2f" % f] = r["acc"]
        curve_detail["%.2f" % f] = {"k_units": k, "n_obs": len(sl), "acc": r["acc"],
                                    "n_active": r["n_active"], "coverage_frac": r["coverage_frac"],
                                    "active_acc": r["active_acc"],
                                    "struct_on_active_acc": r["struct_on_active_acc"]}
        print("    frac=%.2f (%d units, %d obs) acc=%.4f | n_active=%d cov=%.3f active_acc=%s struct_on_active=%s"
              % (f, k, len(sl), r["acc"], r["n_active"], r["coverage_frac"],
                 r["active_acc"], r["struct_on_active_acc"]), flush=True)

    # full-ingest arms: ingest / scrambled control
    assoc_full, hpt_full = build_assoc(full_stream)
    r_full = score_ingest(test_items, assoc_full, hpt_full, syn_pred)
    assoc_scr, hpt_scr = scramble_assoc(assoc_full, hpt_full, SEED + 9)
    r_scr = score_ingest(test_items, assoc_scr, hpt_scr, syn_pred)
    acc_ingest_full = curve["1.00"]
    acc_scrambled = r_scr["acc"]

    # ---- discriminator / fairness gates ----
    per_pred_digests = {"structure": _pred_digest(pr_syn), "majority": _pred_digest(pr_maj),
                        "random": _pred_digest(pr_rand), "ingest_full": _pred_digest(r_full["preds"]),
                        "ingest_scrambled": _pred_digest(r_scr["preds"])}
    # META_RULE_AF: the arms that MUST genuinely differ are structure / ingest_full / random. The scrambled
    # control is DESIGNED to collapse toward structure (destroying head-associations -> syntactic backoff);
    # its collapse == structure is the control WORKING, not a bug -> exempted from the differ gate and tracked
    # as an informative flag instead.
    core = {k: per_pred_digests[k] for k in ("structure", "ingest_full", "random")}
    arms_differ_verified = len(set(core.values())) == len(core)
    arms_differ_exempted = [["structure", "ingest_scrambled"]]
    scrambled_collapses_to_structure = bool(
        per_pred_digests["ingest_scrambled"] == per_pred_digests["structure"])

    baseline_in_band = bool(0.05 < acc_structure < 0.95)
    random_is_chance = bool(0.40 <= acc_random <= 0.60)
    n_active_full = r_full["n_active"]
    active_min = 1 if mode == "smoke" else 10
    discriminator_fires = bool(baseline_in_band and random_is_chance and n_active_full >= active_min)

    # ---- curve shape ----
    steps = [curve["%.2f" % CURVE_FRACS[i + 1]] - curve["%.2f" % CURVE_FRACS[i]]
             for i in range(len(CURVE_FRACS) - 1)]
    n_nonneg = sum(1 for s in steps if s >= -1e-9)
    rise = round(acc_ingest_full - acc_structure, 4)
    zero_matches_structure = bool(abs(curve["0.00"] - acc_structure) < 1e-9)
    scramble_ok = bool(acc_scrambled <= acc_structure + 0.03)
    cardinality_ok = bool(len(curve) == EXPECTED_COV_POINTS)

    # ---- honest coverage-vs-mechanism diagnosis ----
    active_lift = (round(r_full["active_acc"] - r_full["struct_on_active_acc"], 4)
                   if (r_full["active_acc"] is not None and r_full["struct_on_active_acc"] is not None)
                   else None)
    if rise >= 0.03:
        diagnosis = "RISE_KNOWLEDGE_TRANSFERS"
    elif active_lift is not None and active_lift >= 0.05 and r_full["coverage_frac"] < 0.34:
        diagnosis = "COVERAGE_GAP_knowledge_helps_where_it_fires_but_few_test_heads_seen_in_onestop"
    elif n_active_full >= active_min and (active_lift is None or active_lift <= 0.02):
        diagnosis = "MECHANISM_GAP_covered_but_associations_do_not_discriminate_this_decision"
    else:
        diagnosis = "COVERAGE_GAP_or_underpowered_low_active_count"

    # ---- verdict ----
    if (rise >= 0.03 and acc_ingest_full > acc_structure and n_nonneg >= 3 and scramble_ok
            and random_is_chance and baseline_in_band):
        verdict = "HARD_PASS_INGEST_READS_BETTER_FAIRLY"
    elif rise <= 0.01:
        verdict = "FLAT_HONEST_COVERAGE_OR_MECHANISM"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = round(time.perf_counter() - t0, 2)
    msg = (("VERDICT rise=%+.4f (acc_ingest_full=%.4f vs acc_structure=%.4f) | curve=%s | "
            "acc_scrambled=%.4f acc_majority=%.4f acc_random=%.4f | coverage_frac=%.3f n_active=%d "
            "active_acc=%s struct_on_active=%s active_lift=%s | n_nonneg=%d/4 scramble_ok=%s "
            "diagnosis=%s") % (
        rise, acc_ingest_full, acc_structure, curve, acc_scrambled, acc_majority, acc_random,
        r_full["coverage_frac"], n_active_full, r_full["active_acc"], r_full["struct_on_active_acc"],
        active_lift, n_nonneg, scramble_ok, diagnosis))

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_test_items": len(test_items), "gold_strata_n": strat_n,
        "decision": "PP-attachment (V=verb-attach vs N=noun-attach); Hindle&Rooth lexical association",
        "gold_source": ("HUMAN UD-English-EWT dependency annotation (obl->VERB=V, nmod->NOUN=N); NON-CIRCULAR "
                        "-- spaCy NEVER parses the test sentences; independent of the reading front-end"),
        "acc_structure": acc_structure, "acc_majority": acc_majority, "acc_random": acc_random,
        "acc_ingest_full": acc_ingest_full, "acc_ingest_scrambled": acc_scrambled,
        "rise_full_minus_structure": rise,
        "learning_curve_acc": curve, "learning_curve_detail": curve_detail,
        "expected_cov_points": EXPECTED_COV_POINTS, "cardinality_ok": cardinality_ok,
        "curve_steps": [round(s, 4) for s in steps], "n_nonneg_steps": n_nonneg,
        "zero_knowledge_matches_structure_selfcheck": zero_matches_structure,
        "coverage_frac_full": r_full["coverage_frac"], "n_active_full": n_active_full,
        "active_acc_full": r_full["active_acc"], "struct_on_active_acc_full": r_full["struct_on_active_acc"],
        "active_lift_full": active_lift, "coverage_mechanism_diagnosis": diagnosis,
        "scramble_ok": scramble_ok,
        "per_pred_digests": per_pred_digests, "arms_differ_verified": arms_differ_verified,
        "arms_differ_exempted": arms_differ_exempted,
        "scrambled_collapses_to_structure": scrambled_collapses_to_structure,
        "baseline_in_band": baseline_in_band, "random_is_chance": random_is_chance,
        "discriminator_fires": discriminator_fires,
        "n_ingest_units": n_units, "ingest_levels": list(INGEST_LEVELS),
        "n_ingest_obs_full": len(full_stream), "n_heads_learned": len(hpt_full),
        "syntactic_model_stats": syn_stats,
        "runtime_invariant": ("glass-box dict lookup ONLY at inference; NO LLM/network/autograd. spaCy is the "
                              "READING front-end at INGEST time only; test = pre-parsed HUMAN UD gold."),
        "one_variable_note": ("All arms share the SAME UD human-gold test items, split, and binary attach "
                              "mechanism. ONLY the decision source differs: STRUCTURE=prep-preference "
                              "(Collins&Brooks, UD-train), INGEST=OneStop-READ lexical association "
                              "(Hindle&Rooth), SCRAMBLED/MAJORITY/RANDOM=controls."),
        "non_circular_note": ("Cycle-2 was circular (gold=spaCy-dobj on the SAME sentences the spaCy reader "
                              "scored). Here gold=HUMAN UD annotation; the reading knowledge is aggregate "
                              "OneStop lexical statistics (a DIFFERENT corpus); spaCy never sees the test "
                              "sentences -> non-circular. The ingested associations are spaCy-derived SILVER, "
                              "so the ceiling reflects how well OneStop-read PP knowledge transfers to human-"
                              "gold web text (the standard Hindle&Rooth parser-priors + human-gold-test setup)."),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "binary attachment-accuracy; no quantitative noise floor for the discriminator",
        "deterministic_seeding": "fixed int seeds + numpy default_rng + sorted(set); no hash()-seeded RNG",
        "VET_PENDING": True,
        "REQUIRED_FIELDS": ["verdict", "acc_structure", "acc_ingest_full", "acc_ingest_scrambled",
                            "acc_majority", "acc_random", "learning_curve_acc", "rise_full_minus_structure",
                            "coverage_frac_full", "active_lift_full", "coverage_mechanism_diagnosis",
                            "arms_differ_verified", "runtime_invariant", "non_circular_note"],
    }
    _write_metrics(out_dir, payload)

    # store the reading-derived association table LOCAL-ONLY (uncommitted, queryable)
    if mode != "smoke":
        assoc_store = {}
        for (head, prep), ctr in assoc_full.items():
            assoc_store.setdefault(head, {})["%s" % prep] = dict(ctr)
        store_path = os.path.join(out_dir, "read_pp_association_table.json")
        tmp = store_path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"_meta": {"anchor": ANCHOR_NAME,
                                 "granularity": "(head_lemma,prep)->n2_supersense->count",
                                 "n_heads": len(assoc_store), "n_obs": len(full_stream),
                                 "LOCAL_ONLY_UNCOMMITTED": True}, "association": assoc_store},
                      f, indent=0)
        os.replace(tmp, store_path)
        payload["association_store_path"] = store_path

    print("[%s:%s] %s" % (ANCHOR_NAME, mode, msg), flush=True)
    print("[%s:%s] verdict=%s (%.1fs) -> %s" % (
        ANCHOR_NAME, mode, verdict, elapsed, os.path.join(out_dir, "metrics.json")), flush=True)
    return payload


# ----------------------------------------------------------------------------------------------
# formula self-test (REAL UD extraction + REAL spaCy ingest at tiny scale)
# ----------------------------------------------------------------------------------------------
def self_test():
    # 1) REAL human-gold UD extraction + REAL fair syntactic baseline (in band)
    items = PPA.extract_ppa("test")
    assert len(items) > 100, len(items)
    for it in items[:5]:
        assert it["gold"] in ("V", "N") and it["v"] and it["n1"] and it["prep"] and it["n2"]
    syn_pred, maj_pred, stats = PPA.build_syntactic_model()
    acc_syn, _, _, _, _ = PPA.accuracy(items, syn_pred)
    assert 0.05 < acc_syn < 0.95, acc_syn
    assert stats["n_train_items"] > 100

    # 2) association mechanics: reading that gives the CORRECT head a (prep, n2-supersense) association solves
    #    the 2-way; empty backs off; f=0 (empty assoc) == structure exactly; scramble does not exceed correct.
    #    item1 gold=V -> only the VERB has the learned association; item2 gold=N -> only the NOUN does.
    toy = [{"v": "see", "n1": "star", "prep": "through", "n2": "telescope", "gold": "V"},
           {"v": "live", "n1": "house", "prep": "with", "n2": "garden", "gold": "N"}]
    ss_t = SCV.supersense("telescope"); ss_g = SCV.supersense("garden")
    assert ss_t is not None and ss_g is not None
    learned = [("see", "through", ss_t, "verb"), ("see", "through", ss_t, "verb"),
               ("house", "with", ss_g, "noun"), ("house", "with", ss_g, "noun")]
    a, h = build_assoc(learned)
    r_learned = score_ingest(toy, a, h, syn_pred)
    assert r_learned["acc"] == 1.0, r_learned["acc"]            # correct reading solves the 2-way
    assert r_learned["n_active"] == 2, r_learned["n_active"]
    a0, h0 = build_assoc([])
    r0 = score_ingest(items, a0, h0, syn_pred)
    assert abs(r0["acc"] - acc_syn) < 1e-9, (r0["acc"], acc_syn)  # f=0 == ARM_STRUCTURE exactly
    assert r0["n_active"] == 0
    a_scr, h_scr = scramble_assoc(a, h, SEED + 9)
    r_scr = score_ingest(toy, a_scr, h_scr, syn_pred)
    assert r_scr["acc"] <= r_learned["acc"]

    # 3) REAL spaCy ingest path on ONE OneStop unit produces observations
    bases = _ingest_bases()
    assert len(bases) > 50, len(bases)
    stream = ingest_unit_stream(bases[0])
    assert isinstance(stream, list) and len(stream) > 0, len(stream)
    for (head, prep, ss_, hp) in stream[:3]:
        assert hp in ("verb", "noun") and head and prep and ss_.startswith("noun.")

    print("[%s] SELF-TEST PASS | UD_items=%d acc_structure=%.4f | toy_learned=%.2f toy_active=%d "
          "f0==structure OK | onestop_unit=%r n_obs=%d" % (
              ANCHOR_NAME, len(items), acc_syn, r_learned["acc"], r_learned["n_active"],
              bases[0], len(stream)), flush=True)


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
    _od = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
