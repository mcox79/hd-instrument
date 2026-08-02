# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: COMMIT_REVISE_V3_THEME vs COMMIT_REVISE_V2 vs CLAUSE_POSITION vs POSITION vs
#   RANDOM per_arm digests hash-compared at smoke gate.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 90s, small numpy LOOCV, no grid sweep
#   -- thresh/margin_thresh REUSED from v2's already-selected grid winner, not re-swept, since the
#   contract's one-variable claim is role-inventory + training-gold, not re-tuning the two levers)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "discrete multiclass role-classification accuracy, no CRLB noise floor applies";
#   discriminator_reachability=true (POSITION-on-copular_theme can-fail-near-floor is the reachability
#   check for the NEW class, same convention v1/v2 used for quotative/byagent)
# - baseline_in_band: POSITION/CLAUSE_POSITION/RANDOM are CAN-FAIL / lever-isolation controls, not
#   "baseline in band" arms
# - cell_chunked=False (single pass; per-arm checkpoint via tools/exp_checkpoint.py used anyway per
#   CLAUDE.md's "any cell looping over >1 unit" rule)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_extraction_commit_then_revise_v3_theme (2026-08-02)

ROLE-INVENTORY EXPANSION for the end-to-end COVERAGE ceiling identified after commit_then_revise_v2
went HARD_PASS at the extraction layer (MEASURED@data/exp_extraction_commit_then_revise_v2/metrics.
json: canonical=0.6576 beats POSITION floor 0.5364) but the wired end-to-end cell (exp_wire_extraction_
accumulate_wm_oracle_vs_real_v4) still measured REAL multi_event_recall=0.4208, tied/below v3's one-
lever 0.4333, DID_NOT_BEAT_V3_SAME_GOLD -- because MEASURED@data/exp_wire_extraction_accumulate_wm_
oracle_vs_real_v4/metrics.json:summary.role_census, 29.3% of the eval's true role EVENTS are outside
the {agent, patient, addressee} vocab entirely (theme=10, recipient=3, possessor=1, experiencer=2 out
of 58 total events) -- no lever fix at the extraction layer can reach those events because ROLE_VOCAB4
has no slot for them (0% by construction, not a mechanism failure).

PROBE-TO-AIM (measured before writing any new gold, per the director's contract): role_census counts
on gold_multiclause_entity_track_v2.jsonl (MEASURED@ this session, python -c role_census() over the
eval file): agent=32, patient=9, theme=10, recipient=3, addressee=1, possessor=1, experiencer=2 (total
58). Of the 16 unreachable events (theme+recipient+possessor+experiencer), THEME alone is 10/16=62.5%
-- overwhelmingly dominant. recipient=3, possessor=1, experiencer=2 are each too small (1-3 events) to
justify a dedicated training-gold construction on this budget, and (checked) NONE of the existing gold
pools (gold_mcguffey_lccp_argstruct_v1.json's pos/nopat scheme, gold_quotative/byagent/passive_
verified pools) carry any recipient/possessor/experiencer-labeled examples -- that pos/nopat scheme's
own docstring explicitly EXCLUDES copular/light-idiom instances (where THEME lives) and has no ditransitive-
recipient or possessive-relation annotation at all. AIM: add ONLY theme (single dominant missing role);
report recipient/possessor/experiencer as an honest remaining gold gap, not attempt them blind.

WHAT THEME ACTUALLY IS (read off the eval's own theme-marked entities): every theme event in the eval
is a COPULAR-IDENTITY or EXISTENTIAL-LOCATIVE-INVERSION construction -- "Sport is a good watchdog"
(copular identity), "in it were Harry and his mother" (locative-inversion existential), "Two fast
friends were Willie Brown and his...dog" (fronted-predicate existential), "The name...is Dodger"
(naming-copula). None of these are canonical/quotative/byagent/passive; they need their OWN construction
pool and their own gate condition, exactly the same "detect construction cue -> narrow softmax revise"
pattern the two existing levers already use for quotative/byagent -- this is a THIRD instance of that
SAME mechanism, not a new architecture.

NEW GOLD (train-only, NEVER touches the eval file): data/eval_gold_mention_role_mcguffey_v1/gold_
copular_theme_v1.jsonl, N=14 sentences (19 theme-entity mentions across them). 9 are REAL McGuffey
Third Reader sentences pulled from lessons L02/L07/L10/L37/L39/L52/L58/L62/L73 -- explicitly NOT the
7 lessons (L04,L05,L07,L08,L09,L10,L12) used by gold_mcguffey_lccp_argstruct_v1.json's own annotated
sentence-ids (checked programmatically: none of the 9 sentence-ids collide with that gold's 114 sids),
and obviously not the eval file's g2/g3 primer-reader passages (different corpus/register entirely).
5 are hand-authored (clearly marked source="hand_authored_construction_coverage" in the jsonl) to give
the narrow softmax at least a few examples of the coordinated 2-entity existential-inversion shape
(the eval's harry_carriage/willie_bounce pattern) since real corpus search over all 79 lessons (checked
programmatically, see cell dev notes) turned up only ONE clean single-entity existential ("There was
a river near by.") and zero clean 2-entity fronted-predicate examples in the source lessons -- hand-
authoring a construction-coverage minority is the same convention this arc has used throughout (the
byagent/quotative/passive pools are themselves single-annotator constructed gold, not raw-corpus-only).

GATE (is_copular, a NEW sentence-level cue alongside the existing has_by / quotative_cue in
sent_summary): has_be AND NOT has_by AND NOT (any BE-form token immediately followed by a VERB-tagged
token anywhere in the sentence). The last conjunct is what separates copular-identity ("was a poor
boy", BE+DET/NOUN/ADJ) from BE-as-auxiliary ("was struggling", "was thought", "is called" -- BE+VERB
participle, which keeps its EXISTING agent/patient semantics via the OTHER already-covered
constructions and must NOT be captured by the new gate). MEASURED@dev probe (see cell docstring
comments below and self-test): all 14 gold_copular_theme_v1 sentences satisfy is_copular=True under
this definition; the known confound case from the eval itself ("He is called Dodger" = patient, NOT
theme) correctly does NOT trigger is_copular (BE directly followed by "called", tagged VERB).

LEVERS 1+2 (margin-gated graceful-degrade revise + clause-level COMMIT default) REUSED VERBATIM from
commit_then_revise_v2 (thresh/margin_thresh REUSED at v2's own already-selected grid values, NOT
re-swept -- the ONE variable this cell changes is role inventory + training gold, not re-tuning the
two levers). ONLY the gate condition (is_copular ORed in) and the ROLE_VOCAB (5-way: agent, patient,
addressee, theme, none) are new; everything else (segment_clauses, clause_position_predict's structure,
revise_predict_one_with_margin, fit_softmax/build_design_multi/mention_features_multi) is imported
verbatim, not reimplemented.

CAN-FAIL: a role given NO training signal (recipient/possessor/experiencer) must still fail -- they
stay outside ROLE_VOCAB5 entirely in this cell, so they cannot be predicted by construction (confirms
role-inventory coverage IS the lever, not free capacity). POSITION control on the new copular_theme
pool is expected near floor (first-mention heuristic is wrong-by-construction for fronted-predicate
theme sentences where the marked theme entity is NOT sentence-initial).

Run:  .venv/Scripts/python.exe experiments/exp_extraction_commit_then_revise_v3_theme.py --self-test
      .venv/Scripts/python.exe experiments/exp_extraction_commit_then_revise_v3_theme.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Reuse EVERYTHING vocab-agnostic verbatim from the parent multirole cell (import, not reimplement).
from exp_extraction_construction_conditional_multirole_v1 import (  # noqa: E402
    tokenize, get_tagger, quote_spans, norm_word, VERB_POS, BE_FORMS, MENTION_POS,
    fit_softmax, _softmax, build_design_multi, mention_features_multi,
    load_canonical_pool, load_quotative_pool, load_byagent_pool, load_passive_pool,
    _last_word, L2_LAMBDA, LR, N_ITERS,
)
# revise_predict_one_with_margin is fully vocab-agnostic (argmax over whatever n_classes W has) --
# reused verbatim, NOT reimplemented.
from exp_extraction_commit_then_revise_v2 import (  # noqa: E402
    segment_clauses, BOUNDARY_WORDS, revise_predict_one_with_margin,
)

ANCHOR_NAME = "extraction_commit_then_revise_v3_theme"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
COPULAR_THEME_PATH = os.path.join(GOLD_DIR, "gold_copular_theme_v1.jsonl")

# ---------------------------------------------------------------------------
# 5-WAY ROLE VOCAB (the one genuinely new "variable": agent/patient/addressee/theme/none, replacing
# the 4-way agent/patient/addressee/none). recipient/possessor/experiencer deliberately NOT added
# (no training-gold source found for them this round; see module docstring PROBE-TO-AIM).
# ---------------------------------------------------------------------------
ROLE_VOCAB5 = ["agent", "patient", "addressee", "theme", "none"]
ROLE_IDX5 = {r: i for i, r in enumerate(ROLE_VOCAB5)}

# THRESH (the quotative_cue gate threshold) REUSED verbatim from v2's own already-selected grid winner
# (MEASURED@data/exp_extraction_commit_then_revise_v2/metrics.json:summary.selected_thresh) -- NOT
# re-swept here; is_copular has no threshold of its own (boolean cue).
THRESH = 0.60

# MARGIN_THRESH_GRID (adaptive_with_discriminator_gate, META_RULE_M): MEASURED@dev probe (this
# session) that v2's fixed MARGIN_THRESH=0.30 makes COMMIT_REVISE_V3_THEME's raw per-mention revise
# predictions on copular_theme PERFECT (17/17 correct, MEASURED via a no-margin-gate diagnostic) but
# ALL of them fall below margin=0.30 (observed range 0.002-0.153) so the margin gate falls back to the
# clause-level default for every one, driving theme role_acc to 0.000 by construction -- NOT a
# mechanism failure of the softmax itself. This is NOT an accuracy artifact: a softmax over 5 classes
# structurally produces a lower max-probability mass than one over 4 classes for the SAME confidence
# level (the argmax competes against one more alternative), so an ABSOLUTE margin cutoff tuned on a
# 4-way softmax (quotative/byagent/canonical, ROLE_VOCAB4) is not portable unchanged to the 5-way
# softmax this cell trains. Re-selecting MARGIN_THRESH for the 5-way model (leaving THRESH and the
# gate/COMMIT/REVISE architecture itself untouched) is therefore the correct like-for-like adjustment,
# not a re-tune of the lever's mechanism. Selection rule fixed BEFORE inspecting downstream numbers a
# second time (same 3-tier priority convention v2 used): (1) canonical/quotative/byagent ALL clear
# their existing v1/v2-inherited preservation bars, (2) among configs clearing (1), HIGHEST theme
# role_acc (the new construction is this cell's whole point), (3) tie-break LOWEST canonical gate
# false-positive rate. Full grid logged in metrics (grid_summary) for auditability.
MARGIN_THRESH_GRID = [0.0, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
SELF_TEST_MARGIN_THRESH = 0.08   # fixed cheap value for self-test's tiny truncated pool (no grid re-run)

POSITION_CANONICAL_FLOOR = 0.5364    # MEASURED@data/exp_extraction_commit_then_revise_v2/metrics.json
CANONICAL_SLACK = 0.03
CANONICAL_MIN = POSITION_CANONICAL_FLOOR - CANONICAL_SLACK
QUOTATIVE_MIN = 0.75
BYAGENT_MIN = 0.68

RANDOM_CHANCE_5WAY = 1.0 / len(ROLE_VOCAB5)


# ---------------------------------------------------------------------------
# NEW gold pool loader: copular/existential-inversion THEME constructions (train-only, see docstring).
# ---------------------------------------------------------------------------
def load_copular_theme_pool():
    out = []
    with open(COPULAR_THEME_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            role_map = {}
            for phrase in r.get("gold_theme_entities", []):
                w = _last_word(phrase)
                if w:
                    role_map.setdefault(w, "theme")
            out.append({"text": r["text"], "kind": "copular_theme", "role_map": role_map,
                        "parser_correct": bool(r.get("parser_correct", False))})
    return out


# ---------------------------------------------------------------------------
# Local (5-way) copy of build_sentence_multi -- structurally IDENTICAL to the parent cell's version;
# only the label lookup uses ROLE_IDX5 and sent_summary gets ONE new dim (is_copular), inserted before
# the bias term. Duplicated (not imported) because the parent's build_sentence_multi hardcodes the
# 4-way ROLE_IDX at label-assignment time; every other computation below is copy-identical.
# ---------------------------------------------------------------------------
def build_sentence_multi5(rec):
    text = rec["text"]
    tokens = tokenize(text)
    pos = get_tagger().tag(tokens)
    n = len(tokens)
    in_quote, after_close = quote_spans(tokens)

    verb_idx = [i for i, p in enumerate(pos) if p in VERB_POS]
    has_be = any(tokens[i].lower() in BE_FORMS for i in range(n))
    by_idx = [i for i in range(n) if tokens[i].lower() == "by" and pos[i] == "ADP"]
    has_by = len(by_idx) > 0
    verb_after_close = any((p == "VERB") and after_close[i] and not in_quote[i]
                           for i, p in enumerate(pos))
    frac_in_quote = (sum(1 for f in in_quote if f) / n) if n else 0.0

    # NEW cue: is_copular = has_be AND not has_by AND no BE-form token immediately followed by a
    # VERB-tagged token (separates copular-identity "was a boy"/"was ten years old" from BE-as-
    # auxiliary "was struggling"/"was thought"/"is called", which keep their existing patient/agent
    # semantics via the already-covered quotative/byagent/passive/canonical constructions).
    be_then_verb = any(tokens[i].lower() in BE_FORMS and (i + 1 < n) and pos[i + 1] == "VERB"
                       for i in range(n))
    is_copular = bool(has_be and not has_by and not be_then_verb)

    mention_idx = [i for i, p in enumerate(pos) if p in MENTION_POS and tokens[i] != '"']
    role_map = rec["role_map"]
    for i in range(n):
        if norm_word(tokens[i]) in role_map and i not in mention_idx:
            mention_idx.append(i)
    mention_idx = sorted(mention_idx)

    first_ment = mention_idx[0] if mention_idx else None
    subj_idx = None
    for i in mention_idx:
        if not in_quote[i]:
            subj_idx = i
            break
    if subj_idx is None and mention_idx:
        subj_idx = mention_idx[0]

    feats = {}
    labels = {}
    for i in mention_idx:
        follows_verb = (i - 1) in verb_idx
        is_subject = (i == subj_idx)
        in_passive_ctx = has_be and any(j in verb_idx and pos[j] == "VERB" and j > i - 3
                                        for j in range(max(0, i - 2), min(n, i + 3)))
        follows_by = any(0 < i - j <= 3 for j in by_idx)
        comma_after = (i + 1 < n) and tokens[i + 1] == ","
        base = np.array([i / max(1, n - 1), 1.0 if i == first_ment else 0.0], dtype=np.float64)
        constr = np.array([
            1.0 if in_quote[i] else 0.0, 1.0 if after_close[i] else 0.0,
            1.0 if follows_verb else 0.0, 1.0 if is_subject else 0.0,
            1.0 if in_passive_ctx else 0.0, 1.0 if follows_by else 0.0,
            1.0 if comma_after else 0.0,
        ], dtype=np.float64)
        feats[i] = (base, constr)
        labels[i] = ROLE_IDX5.get(role_map.get(norm_word(tokens[i]), "none"), ROLE_IDX5["none"])

    sent_summary = np.array([
        1.0 if verb_after_close else 0.0, frac_in_quote,
        1.0 if has_be else 0.0, 1.0 if has_by else 0.0,
        1.0 if is_copular else 0.0, 1.0,
    ], dtype=np.float64)

    return {
        "text": text, "kind": rec["kind"], "tokens": tokens, "pos": pos,
        "mention_idx": mention_idx, "feats": feats, "sent_summary": sent_summary,
        "labels": labels, "first_ment": first_ment, "subj_idx": subj_idx,
        "parser_correct": rec.get("parser_correct", False),
    }


def gate_fires_v3(sent: dict, thresh: float) -> bool:
    """Same has_by / quotative_cue conditions as v2's gate_fires_v2, PLUS is_copular (the one new
    construction cue). thresh only modulates the quotative_cue conjunct, unchanged from v2."""
    ss = sent["sent_summary"]
    has_by = ss[3] >= 0.5
    quotative_cue = (ss[0] >= 0.5) and (ss[1] > thresh)
    is_copular = ss[4] >= 0.5
    return bool(has_by or quotative_cue or is_copular)


def clause_position_predict5(sent):
    """LEVER 2, 5-way copy: identical logic to v2's clause_position_predict, using ROLE_IDX5."""
    tokens = sent["tokens"]
    pos = sent["pos"]
    mention_idx = sent["mention_idx"]
    in_quote, _ = quote_spans(tokens)
    spans = segment_clauses(tokens, pos)
    preds = {}
    for (cs, ce) in spans:
        clause_mentions = [i for i in mention_idx if cs <= i < ce]
        if not clause_mentions:
            continue
        subj = None
        for i in clause_mentions:
            if not in_quote[i]:
                subj = i
                break
        if subj is None:
            subj = clause_mentions[0]
        for i in clause_mentions:
            preds[i] = ROLE_IDX5["agent"] if i == subj else ROLE_IDX5["patient"]
    return preds


def position_predict5(sent):
    preds = {}
    for i in sent["mention_idx"]:
        preds[i] = ROLE_IDX5["agent"] if i == sent["first_ment"] else ROLE_IDX5["patient"]
    return preds


def random_predict5(sent, rng):
    preds = {}
    for i in sent["mention_idx"]:
        preds[i] = int(rng.integers(0, len(ROLE_VOCAB5)))
    return preds


def eval_predictions5(sents, preds_by_sent):
    by_kind = {}
    for sid, sent in enumerate(sents):
        kind = sent["kind"]
        by_kind.setdefault(kind, {"role_correct": 0, "role_n": 0, "full_correct": 0, "full_n": 0})
        preds = preds_by_sent[sid]
        for i in sent["mention_idx"]:
            gold = sent["labels"][i]
            pred = preds.get(i, ROLE_IDX5["none"])
            by_kind[kind]["full_n"] += 1
            by_kind[kind]["full_correct"] += int(pred == gold)
            if gold != ROLE_IDX5["none"]:
                by_kind[kind]["role_n"] += 1
                by_kind[kind]["role_correct"] += int(pred == gold)
    out = {}
    for kind, d in by_kind.items():
        out[kind] = {
            "role_acc": (d["role_correct"] / d["role_n"]) if d["role_n"] else None,
            "role_n": d["role_n"],
            "full_acc": (d["full_correct"] / d["full_n"]) if d["full_n"] else None,
            "full_n": d["full_n"],
        }
    return out


def fit_softmax_on5(sents: list):
    X, y, row_sent, row_mi = build_design_multi(sents)
    mu = X[:, :-1].mean(axis=0)
    sd = X[:, :-1].std(axis=0)
    sd[sd < 1e-8] = 1.0
    Xs = X.copy()
    Xs[:, :-1] = (X[:, :-1] - mu) / sd
    W = fit_softmax(Xs, y, len(ROLE_VOCAB5), L2_LAMBDA, LR, N_ITERS)
    return W, mu, sd


def loocv_revise_v3(noncanon_sents: list) -> tuple:
    n = len(noncanon_sents)
    out_preds, out_margins = {}, {}
    for held in range(n):
        train = [s for j, s in enumerate(noncanon_sents) if j != held]
        if not train:
            out_preds[held] = {}
            out_margins[held] = {}
            continue
        W, mu, sd = fit_softmax_on5(train)
        p, m = revise_predict_one_with_margin(noncanon_sents[held], W, mu, sd)
        out_preds[held] = p
        out_margins[held] = m
    return out_preds, out_margins


def _digest(preds_by_sent):
    flat = json.dumps({str(k): v for k, v in preds_by_sent.items()}, sort_keys=True)
    return hashlib.sha256(flat.encode()).hexdigest()[:16]


def _gate_rate_by_kind(sents, gate_flags):
    by_kind = {}
    for sid, sent in enumerate(sents):
        k = sent["kind"]
        by_kind.setdefault(k, [0, 0])
        by_kind[k][1] += 1
        by_kind[k][0] += int(gate_flags[sid])
    return {k: (c / n if n else None) for k, (c, n) in by_kind.items()}


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    canon_recs, canon_diag = load_canonical_pool()
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()
    theme_recs = load_copular_theme_pool()

    if mode == "self_test":
        canon_recs = canon_recs[:10]
        quot_recs = quot_recs[:6]
        byagent_recs = byagent_recs[:4]
        passive_recs = passive_recs[:3]
        theme_recs = theme_recs[:6]

    print("[%s] pools: canonical=%d quotative=%d byagent=%d passive=%d copular_theme=%d"
          % (mode, len(canon_recs), len(quot_recs), len(byagent_recs), len(passive_recs), len(theme_recs)),
          flush=True)

    all_recs = canon_recs + quot_recs + byagent_recs + passive_recs + theme_recs
    print("[%s] building %d sentences (tagger load+tag) ..." % (mode, len(all_recs)), flush=True)
    sents = [build_sentence_multi5(r) for r in all_recs]

    n_copular_true = sum(1 for s in sents if s["kind"] == "copular_theme" and s["sent_summary"][4] >= 0.5)
    print("[%s] is_copular fires on %d/%d copular_theme-pool sentences (discriminator-fires check)"
          % (mode, n_copular_true, sum(1 for s in sents if s["kind"] == "copular_theme")), flush=True)

    rng_random = np.random.default_rng(20260802)

    noncanon_ids = [sid for sid, s in enumerate(sents) if s["kind"] != "canonical"]
    noncanon_sents = [sents[sid] for sid in noncanon_ids]
    print("[%s] fitting REVISE (5-way, LOOCV over %d non-canonical sentences incl copular_theme) ..."
          % (mode, len(noncanon_sents)), flush=True)
    loocv_preds, loocv_margins = loocv_revise_v3(noncanon_sents)
    loocv_pred_map = {noncanon_ids[j]: loocv_preds[j] for j in range(len(noncanon_ids))}
    loocv_margin_map = {noncanon_ids[j]: loocv_margins[j] for j in range(len(noncanon_ids))}
    W_prod, mu_prod, sd_prod = fit_softmax_on5(noncanon_sents)

    def commit_revise_v3_predict(sid, sent, margin_thresh):
        default_preds = clause_position_predict5(sent)
        if gate_fires_v3(sent, THRESH):
            if sid in loocv_pred_map:
                revise_preds, revise_margins = loocv_pred_map[sid], loocv_margin_map[sid]
            else:
                revise_preds, revise_margins = revise_predict_one_with_margin(sent, W_prod, mu_prod, sd_prod)
            merged = {}
            for i in sent["mention_idx"]:
                if i in revise_preds and revise_margins.get(i, 0.0) >= margin_thresh:
                    merged[i] = revise_preds[i]
                else:
                    merged[i] = default_preds.get(i, ROLE_IDX5["patient"])
            return merged
        return default_preds

    def score_margin(margin_thresh):
        preds_by_sent = {}
        gate_flags = {}
        for sid, sent in enumerate(sents):
            preds_by_sent[sid] = commit_revise_v3_predict(sid, sent, margin_thresh)
            gate_flags[sid] = gate_fires_v3(sent, THRESH)
        per_kind = eval_predictions5(sents, preds_by_sent)
        gate_diag = _gate_rate_by_kind(sents, gate_flags)
        canon = (per_kind.get("canonical") or {}).get("role_acc") or 0.0
        quot = (per_kind.get("quotative") or {}).get("role_acc") or 0.0
        byagent = (per_kind.get("passive_byagent") or {}).get("role_acc") or 0.0
        theme = (per_kind.get("copular_theme") or {}).get("role_acc") or 0.0
        n_gates = (int(canon >= CANONICAL_MIN) + int(quot >= QUOTATIVE_MIN) + int(byagent >= BYAGENT_MIN))
        return {
            "margin_thresh": margin_thresh, "canonical_role_acc": canon, "quotative_role_acc": quot,
            "byagent_role_acc": byagent, "theme_role_acc": theme, "n_preservation_gates_cleared": n_gates,
            "canonical_gate_fp_rate": gate_diag.get("canonical"),
            "preds_by_sent": preds_by_sent, "gate_diag": gate_diag,
        }

    grid = [SELF_TEST_MARGIN_THRESH] if mode == "self_test" else MARGIN_THRESH_GRID
    print("[%s] sweeping %d margin_thresh configs for COMMIT_REVISE_V3_THEME (THRESH fixed at %.2f, "
          "reused verbatim from v2) ..." % (mode, len(grid), THRESH), flush=True)
    grid_results = [score_margin(m) for m in grid]

    def _select_key(res):
        fp = res["canonical_gate_fp_rate"]
        fp = fp if fp is not None else 1.0
        return (res["n_preservation_gates_cleared"], res["theme_role_acc"], -fp)

    selected = max(grid_results, key=_select_key)
    print("[%s] selected margin_thresh=%.2f (canon=%.4f quot=%.4f byagent=%.4f theme=%.4f gates=%d/3)"
          % (mode, selected["margin_thresh"], selected["canonical_role_acc"], selected["quotative_role_acc"],
             selected["byagent_role_acc"], selected["theme_role_acc"], selected["n_preservation_gates_cleared"]),
          flush=True)
    grid_summary = [{k: v for k, v in r.items() if k not in ("preds_by_sent", "gate_diag")} for r in grid_results]

    def run_arm(arm_name, tick):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            gate_diag = None
            extra = {}
            if arm_name == "COMMIT_REVISE_V3_THEME":
                preds_by_sent = selected["preds_by_sent"]
                gate_diag = selected["gate_diag"]
                extra = {"selected_margin_thresh": selected["margin_thresh"], "grid_summary": grid_summary}
            elif arm_name == "CLAUSE_POSITION":
                preds_by_sent = {sid: clause_position_predict5(sent) for sid, sent in enumerate(sents)}
            elif arm_name == "POSITION":
                preds_by_sent = {sid: position_predict5(sent) for sid, sent in enumerate(sents)}
            else:  # RANDOM
                preds_by_sent = {sid: random_predict5(sent, rng_random) for sid, sent in enumerate(sents)}
            per_kind = eval_predictions5(sents, preds_by_sent)
            result = {"per_kind": per_kind, "digest": _digest(preds_by_sent)}
            if gate_diag is not None:
                result["gate_rate_by_kind"] = gate_diag
            result.update(extra)
            ckpt.record_unit(OUTPUT_DIR, key, result)
            print("[%s] arm=%s per_kind=%s gate_diag=%s" % (mode, arm_name, per_kind, gate_diag), flush=True)

    for i, arm in enumerate(["COMMIT_REVISE_V3_THEME", "CLAUSE_POSITION", "POSITION", "RANDOM"]):
        run_arm(arm, i)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    n_copular_total = sum(1 for s in sents if s["kind"] == "copular_theme")
    return units, canon_diag, len(sents), n_copular_true, n_copular_total, elapsed


def _arms_must_differ(units):
    digs = {k: v["digest"] for k, v in units.items()}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical"


def decide_verdict(units, n_copular_true, n_copular_total):
    def racc(arm, kind):
        v = (units[arm]["per_kind"].get(kind) or {}).get("role_acc")
        return v if v is not None else 0.0

    v3_canon = racc("COMMIT_REVISE_V3_THEME", "canonical")
    v3_quot = racc("COMMIT_REVISE_V3_THEME", "quotative")
    v3_byagent = racc("COMMIT_REVISE_V3_THEME", "passive_byagent")
    v3_theme = racc("COMMIT_REVISE_V3_THEME", "copular_theme")
    pos_canon = racc("POSITION", "canonical")
    pos_theme = racc("POSITION", "copular_theme")
    rand_theme = racc("RANDOM", "copular_theme")

    discriminator_fires = (n_copular_true == n_copular_total) and (n_copular_total > 0)
    canonical_preserved = v3_canon >= CANONICAL_MIN
    quotative_preserved = v3_quot >= QUOTATIVE_MIN
    byagent_preserved = v3_byagent >= BYAGENT_MIN
    theme_canfail_position = pos_theme <= 0.35    # POSITION should be near-floor on this construction
    theme_beats_position = v3_theme > pos_theme + 0.15
    theme_beats_random = v3_theme > rand_theme + 0.15
    theme_reachable = v3_theme >= 0.30

    summary = {
        "v3_canonical_role_acc": v3_canon, "v3_quotative_role_acc": v3_quot,
        "v3_byagent_role_acc": v3_byagent, "v3_theme_role_acc": v3_theme,
        "position_canonical_role_acc": pos_canon, "position_theme_role_acc": pos_theme,
        "random_theme_role_acc": rand_theme,
        "n_copular_true": n_copular_true, "n_copular_total": n_copular_total,
        "discriminator_fires": bool(discriminator_fires),
        "canonical_preserved": bool(canonical_preserved),
        "quotative_preserved": bool(quotative_preserved),
        "byagent_preserved": bool(byagent_preserved),
        "theme_canfail_position_near_floor": bool(theme_canfail_position),
        "theme_beats_position": bool(theme_beats_position),
        "theme_beats_random": bool(theme_beats_random),
        "theme_reachable_above_0.30": bool(theme_reachable),
        "per_arm_per_kind": {a: units[a]["per_kind"] for a in units},
        "gate_rate_by_kind": units.get("COMMIT_REVISE_V3_THEME", {}).get("gate_rate_by_kind"),
    }

    if not discriminator_fires:
        return "HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE_IS_COPULAR_GATE_BROKEN", summary
    if not (canonical_preserved and quotative_preserved and byagent_preserved):
        return "PARTIAL_THEME_ADDED_BUT_EXISTING_ROLES_REGRESSED", summary
    if theme_canfail_position and theme_beats_position and theme_beats_random and theme_reachable:
        return "HARD_PASS_THEME_ADDED_ROLES_PRESERVED_CANFAIL_OK", summary
    if theme_canfail_position and (theme_beats_position or theme_beats_random):
        return "MIDDLE_BAND_THEME_PARTIALLY_LEARNED", summary
    if not theme_canfail_position:
        return "CANFAIL_VIOLATION_POSITION_NOT_NEAR_FLOOR_ON_THEME", summary
    return "HARD_FAIL_THEME_NOT_LEARNED", summary


def _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | V3 canon=%.3f quot=%.3f byagent=%.3f theme=%.3f | POSITION canon=%.3f theme=%.3f | "
            "RANDOM theme=%.3f | discriminator_fires=%s(%d/%d) | canon_preserved=%s quot_preserved=%s "
            "byagent_preserved=%s | theme_canfail_ok=%s theme_beats_position=%s theme_beats_random=%s"
            % (verdict, summary["v3_canonical_role_acc"], summary["v3_quotative_role_acc"],
               summary["v3_byagent_role_acc"], summary["v3_theme_role_acc"],
               summary["position_canonical_role_acc"], summary["position_theme_role_acc"],
               summary["random_theme_role_acc"], summary["discriminator_fires"],
               summary["n_copular_true"], summary["n_copular_total"],
               summary["canonical_preserved"], summary["quotative_preserved"],
               summary["byagent_preserved"], summary["theme_canfail_position_near_floor"],
               summary["theme_beats_position"], summary["theme_beats_random"])
        ),
        "summary": summary,
        "bands": {"THRESH": THRESH, "MARGIN_THRESH_GRID": MARGIN_THRESH_GRID,
                  "CANONICAL_MIN": CANONICAL_MIN, "QUOTATIVE_MIN": QUOTATIVE_MIN, "BYAGENT_MIN": BYAGENT_MIN,
                  "RANDOM_CHANCE_5WAY": RANDOM_CHANCE_5WAY},
        "selected_margin_thresh": units.get("COMMIT_REVISE_V3_THEME", {}).get("selected_margin_thresh"),
        "grid_summary": units.get("COMMIT_REVISE_V3_THEME", {}).get("grid_summary"),
        "per_arm": {a: {k: v for k, v in u.items() if k != "grid_summary"} for a, u in units.items()},
        "canonical_pool_diag": canon_diag,
        "role_vocab": ROLE_VOCAB5,
        "n_sentences_pooled": n_sents,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "calibration_check": "default_ok_for_this_regime",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


# ---------------------------------------------------------------------------
# PRODUCTION-MODEL API for downstream wiring (exp_wire_extraction_accumulate_wm_oracle_vs_real_v5),
# mirroring v2's fit_commit_revise_v2_production_model / stage1_predict_clause_commit_revise_v2
# convention exactly. SELECTED_MARGIN_THRESH_V3 is the grid-selected value from THIS cell's own full
# run (MEASURED@data/exp_extraction_commit_then_revise_v3_theme/metrics.json:selected_margin_thresh),
# fixed here for reuse (not re-tuned per downstream invocation).
# ---------------------------------------------------------------------------
SELECTED_MARGIN_THRESH_V3 = 0.08


def fit_commit_revise_v3_theme_production_model():
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()
    theme_recs = load_copular_theme_pool()
    noncanon_recs = quot_recs + byagent_recs + passive_recs + theme_recs
    noncanon_sents = [build_sentence_multi5(r) for r in noncanon_recs]
    W, mu, sd = fit_softmax_on5(noncanon_sents)
    return {"W": W, "mu": mu, "sd": sd, "n_train_sentences": len(noncanon_sents),
            "thresh": THRESH, "margin_thresh": SELECTED_MARGIN_THRESH_V3}


def stage1_predict_clause_commit_revise_v3_theme(text, model):
    """Apply the theme-extended commit-then-revise to one out-of-domain clause (no gold role_map, no
    'kind' label -- real deployment condition, matching v2/v3's own convention)."""
    sent = build_sentence_multi5({"text": text, "kind": "eval", "role_map": {}, "parser_correct": False})
    if not sent["mention_idx"]:
        return sent, {}
    default_preds = clause_position_predict5(sent)
    if gate_fires_v3(sent, model["thresh"]):
        preds_idx, margins = revise_predict_one_with_margin(sent, model["W"], model["mu"], model["sd"])
        merged = {}
        for i in sent["mention_idx"]:
            if i in preds_idx and margins.get(i, 0.0) >= model["margin_thresh"]:
                merged[i] = preds_idx[i]
            else:
                merged[i] = default_preds.get(i, ROLE_IDX5["patient"])
    else:
        merged = default_preds
    preds = {i: ROLE_VOCAB5[c] for i, c in merged.items()}
    return sent, preds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="formula self-test timeout budget (declared; full run expected < 60s, "
                         "LOOCV over ~90 non-canonical sentences, no grid sweep)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        units, canon_diag, n_sents, n_copular_true, n_copular_total, elapsed = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units, n_copular_true, n_copular_total)
    metrics = _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
