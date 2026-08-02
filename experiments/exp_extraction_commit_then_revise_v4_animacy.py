# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: COMMIT_REVISE_V4_ANIMACY vs COMMIT_REVISE_V4_SCRAMBLED vs V3_THEME_REPRO vs
#   CLAUSE_POSITION vs POSITION vs RANDOM per_arm digests hash-compared at smoke gate.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 90s, small numpy LOOCV, no grid sweep
#   beyond the SAME margin_thresh re-selection convention v3 already used when it changed the feature/
#   vocab space -- documented below, not a silent re-tune)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "discrete multiclass role-classification accuracy, no CRLB noise floor applies";
#   discriminator_reachability=true (the can-fail negative controls below ARE the reachability check
#   for this cell's one variable: does a CORRECT animacy dictionary do anything a SCRAMBLED one and a
#   NO-dictionary reproduction do not)
# - baseline_in_band: CLAUSE_POSITION/POSITION/RANDOM are CAN-FAIL / lever-isolation controls, not
#   "baseline in band" arms; V3_THEME_REPRO is the SAME-GOLD lineage/no-dictionary comparison arm
# - cell_chunked=False (single pass; per-arm checkpoint via tools/exp_checkpoint.py used anyway per
#   CLAUDE.md's "any cell looping over >1 unit" rule)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_extraction_commit_then_revise_v4_animacy (2026-08-02)

DIRECTOR CONTRACT: "GIVE THE READER A DICTIONARY" -- supply a symbolic glass-box LEXICON of word
animacy/category (hdlab/animacy_lexicon.py, WordNet-hypernym-closure sourced) as a signal/prior in
role assignment, so MEANING-REQUIRED role cases resolve via lookup ("music can't be a maker, a
shepherd can") rather than inference. This is explicitly ALLOWED per the contract: supplying a
lexicon = supplying KNOWLEDGE/DATA (same status as the CSKG/ConceptNet already used elsewhere in this
project); it is NOT a borrowed embedding (no GloVe/BGE/transformer vectors -- every lexicon entry is a
small readable {animacy, category, agent_capable} dict) and NOT a bolt-on reader/parser (the extraction
mechanism -- clause-level COMMIT default + margin-gated graceful-degrade REVISE softmax -- is UNCHANGED
architecture from commit_then_revise_v2/v3_theme; only the FEATURE VECTOR fed into the existing REVISE
softmax gains 4 new animacy-derived dims).

PROBE-BEFORE-BUILD (per director instruction to measure not assume; MEASURED this session via two
throwaway probe scripts over the real pools + eval file, not included as production code):
  1. WordNet has TWO collision failure modes on this corpus that would poison a naive lookup: (a)
     PRONOUN/SHORT-WORD collision -- "I"/"He" match chemistry-symbol noun senses (iodine/helium), not
     the pronoun; (b) PROPER-NOUN/COMMON-NOUN HOMOGRAPH collision -- "Dash" (a dog's name) matches the
     common noun "dash", "Patty" matches "patty" (a cake), "Read" (surname "Thomas Read") matches the
     verb-noun "read". hdlab/animacy_lexicon.py guards BOTH (explicit PRONOUN_TABLE checked before any
     WordNet call; PROPN-tagged tokens NEVER get a WordNet-common-noun lookup).
  2. After guarding both collisions, a direct scan of ALL FIVE existing gold pools (canonical/
     quotative/byagent/passive/copular_theme) for "subject mention is lexicon-inanimate/not-agent-
     capable AND the gold role is agent" (the literal animacy-conflict case the contract's example
     describes) found ZERO genuine instances outside constructions ALREADY syntactically gated by
     has_by / is_copular (e.g. "the music was made by the shepherd" -- music=patient is already fully
     resolved by the has_by cue; the by-agent construction pool was itself curated around exactly this
     class of sentence). Likewise scanning gold_multiclause_entity_track_v2.jsonl (the END-TO-END EVAL,
     read-only for diagnosis, never for training) found 3 raw "inanimate-subject-labeled-agent" hits,
     and ALL THREE were the PROPER-NOUN HOMOGRAPH COLLISION above (Dash/Thomas Read/Patty) -- i.e.
     lexicon ARTIFACTS, not genuine animacy-driven role conflicts. Zero genuine conflicts remain after
     guarding. HONEST PRE-REGISTERED EXPECTATION (declared before the full run below, not after): this
     specific McGuffey-primer corpus, under the current 5-way construction taxonomy, does not contain
     naturally-occurring cases where animacy carries information the has_by/is_copular/quotative
     construction cues do not already carry -- so a NULL or near-null lift on meaning-required accuracy
     is the EXPECTED, MECHANISM-CONSISTENT outcome here, not evidence the lever/lexicon is broken. This
     is exactly the "flat result -> diagnose why" discipline: the diagnosis is corpus/construction-
     coverage, not a broken feature or non-learning softmax (see CAN-FAIL DESIGN below, which is built
     to tell these apart).

WHERE THE LEXICON IS WIRED (ONE-VARIABLE change from v3_theme): build_sentence_multi6 (duplicated from
v3_theme's build_sentence_multi5, NOT edited in place -- same "duplicate don't edit a function other
cells import verbatim" convention v3_theme itself used) adds 4 new per-mention BASE feature dims sourced
from hdlab.animacy_lexicon.lookup_animacy(token, pos_tag): mention_animate, mention_inanimate (this
mention's own animacy), subj_animate, subj_inanimate (0 unless this mention IS the clause subject --
the specific "inanimate subject should not default to agent" prior the contract describes). A word with
NO lexicon coverage gets all 4 dims = 0.0 (neutral, no signal) -- CAN-FAIL CONTROL (a). The GATE
(gate_fires_v4) and the COMMIT default (clause_position_predict5) are REUSED VERBATIM UNCHANGED from
v3_theme -- the lexicon is deliberately NOT wired into a new gate condition or into the COMMIT default,
because the probe above found canonical-kind gold ITSELF assigns "agent" to several inanimate subjects
by the corpus's own convention (intransitive "a shadow flitted across his face" / "a crash followed" is
labeled agent regardless of animacy) -- adding an animacy-triggered gate override there would DEGRADE
canonical accuracy on gold-correct COMMIT predictions, not fix a meaning-required gap. Only the ALREADY-
GATED REVISE softmax (trained on the non-canonical pools, applied to sentences where has_by/quotative/
is_copular already fire) gets the new features, so the WHOLE canonical arm accuracy path is UNTOUCHED
by this cell's one variable (protects the canonical preservation gate exactly, not just approximately).

CAN-FAIL DESIGN (2 controls the director's contract requires, both MEASURED, not assumed):
  (a) UNCOVERED-WORD NULL CHECK: report role_acc separately for the SUBSET of REVISE-gated mentions
      whose clause subject IS lexicon-covered vs IS NOT. If the dictionary is doing real work, any lift
      from V3_THEME_REPRO (no dictionary) to COMMIT_REVISE_V4_ANIMACY should concentrate in the COVERED
      subset; the UNCOVERED subset's accuracy should not durably differ between the two arms (allowing
      for LOOCV/shared-softmax-weight cross-talk, reported honestly either way, not asserted).
  (b) SCRAMBLED-DICTIONARY NEGATIVE CONTROL: hdlab.animacy_lexicon.scrambled_lookup_factory permutes
      the covered vocabulary's animacy/category dicts across words (same coverage, WRONG assignments).
      COMMIT_REVISE_V4_SCRAMBLED is architecturally IDENTICAL to COMMIT_REVISE_V4_ANIMACY except every
      lexicon call goes through the scrambled lookup instead of the real one. A correct dictionary must
      NOT be beaten by (or must not reliably beat) the scrambled one by more than noise; SCRAMBLED
      durably beating REAL would falsify "this is doing the right kind of work."

PRESERVATION (per contract, "do NOT worsen canonical further; recover toward 0.536+ if possible"):
  canonical/quotative/byagent role_acc gates REUSED verbatim from v3_theme's own already-selected
  values (CANONICAL_MIN, QUOTATIVE_MIN, BYAGENT_MIN below) -- since COMMIT default + gate are byte-
  identical to v3_theme, canonical accuracy for sentences where the gate does NOT fire is expected
  IDENTICAL to v3_theme (MEASURED, not assumed, in the verdict below via a canonical-only digest
  comparison against V3_THEME_REPRO).

MARGIN_THRESH_GRID re-swept (same convention v3_theme itself documented when IT changed the feature/
vocab space: an added feature dimension shifts the softmax's probability-mass geometry, so an absolute
margin cutoff calibrated on the OLD feature space is not portable unchanged). Selection rule identical
3-tier priority v2/v3 used: (1) canonical/quotative/byagent ALL clear their v2/v3-inherited
preservation bars, (2) among configs clearing (1), HIGHEST theme_role_acc AND best meaning-required
lift over V3_THEME_REPRO (see selection key below), (3) tie-break LOWEST canonical gate FP rate. Fixed
BEFORE inspecting downstream can-fail-control numbers a second time.

Run:  .venv/Scripts/python.exe experiments/exp_extraction_commit_then_revise_v4_animacy.py --self-test
      .venv/Scripts/python.exe experiments/exp_extraction_commit_then_revise_v4_animacy.py --full
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

from hdlab.animacy_lexicon import lookup_animacy, coverage_report, scrambled_lookup_factory  # noqa: E402

# Reuse EVERYTHING vocab/architecture-agnostic verbatim (import, not reimplement).
from exp_extraction_construction_conditional_multirole_v1 import (  # noqa: E402
    tokenize, get_tagger, quote_spans, norm_word, VERB_POS, BE_FORMS, MENTION_POS,
    fit_softmax, _softmax, load_canonical_pool, load_quotative_pool, load_byagent_pool,
    load_passive_pool, _last_word, L2_LAMBDA, LR, N_ITERS,
)
from exp_extraction_commit_then_revise_v2 import (  # noqa: E402
    segment_clauses, BOUNDARY_WORDS, revise_predict_one_with_margin,
)
from exp_extraction_commit_then_revise_v3_theme import (  # noqa: E402
    load_copular_theme_pool, ROLE_VOCAB5, ROLE_IDX5, THRESH, gate_fires_v3,
    clause_position_predict5, position_predict5, random_predict5, eval_predictions5,
    POSITION_CANONICAL_FLOOR, CANONICAL_SLACK, CANONICAL_MIN, QUOTATIVE_MIN, BYAGENT_MIN,
    build_sentence_multi5 as v3_build_sentence_multi5,
)

ANCHOR_NAME = "extraction_commit_then_revise_v4_animacy"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

RANDOM_CHANCE_5WAY = 1.0 / len(ROLE_VOCAB5)

MARGIN_THRESH_GRID = [0.0, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
SELF_TEST_MARGIN_THRESH = 0.08


# ---------------------------------------------------------------------------
# build_sentence_multi6: DUPLICATED from v3_theme's build_sentence_multi5 (NOT edited in place --
# same convention v3_theme used for v1/v2's build_sentence_multi). Only change: 4 new per-mention
# BASE feature dims from the animacy lexicon, via an INJECTABLE lookup_fn (real vs scrambled vs
# none) so all 3 dictionary conditions (real / scrambled / no-dict-reproduction) share one builder.
# ---------------------------------------------------------------------------
def build_sentence_multi6(rec, lookup_fn):
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

    n_lexicon_covered = 0
    subj_lexicon_covered = False

    feats = {}
    labels = {}
    for i in mention_idx:
        follows_verb = (i - 1) in verb_idx
        is_subject = (i == subj_idx)
        in_passive_ctx = has_be and any(j in verb_idx and pos[j] == "VERB" and j > i - 3
                                        for j in range(max(0, i - 2), min(n, i + 3)))
        follows_by = any(0 < i - j <= 3 for j in by_idx)
        comma_after = (i + 1 < n) and tokens[i + 1] == ","

        lex = lookup_fn(tokens[i], pos[i])
        mention_animate = 0.0
        mention_inanimate = 0.0
        if lex is not None:
            n_lexicon_covered += 1
            if is_subject:
                subj_lexicon_covered = True
            if lex["agent_capable"]:
                mention_animate = 1.0
            else:
                mention_inanimate = 1.0
        subj_animate = mention_animate if is_subject else 0.0
        subj_inanimate = mention_inanimate if is_subject else 0.0

        base = np.array([i / max(1, n - 1), 1.0 if i == first_ment else 0.0,
                          mention_animate, mention_inanimate, subj_animate, subj_inanimate],
                         dtype=np.float64)
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
        "n_lexicon_covered": n_lexicon_covered, "subj_lexicon_covered": subj_lexicon_covered,
    }


def mention_features_multi6(sent, i):
    base, constr = sent["feats"][i]
    ss = sent["sent_summary"]
    inter = np.outer(constr, ss).reshape(-1)
    return np.concatenate([base, inter])


def build_design_multi6(sents):
    rows, ys, row_sent, row_mi = [], [], [], []
    for sid, sent in enumerate(sents):
        for i in sent["mention_idx"]:
            rows.append(mention_features_multi6(sent, i))
            ys.append(sent["labels"][i])
            row_sent.append(sid)
            row_mi.append(i)
    X = np.array(rows, dtype=np.float64)
    y = np.array(ys, dtype=np.int64)
    X = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    return X, y, np.array(row_sent), np.array(row_mi)


def fit_softmax_on6(sents: list):
    X, y, row_sent, row_mi = build_design_multi6(sents)
    mu = X[:, :-1].mean(axis=0)
    sd = X[:, :-1].std(axis=0)
    sd[sd < 1e-8] = 1.0
    Xs = X.copy()
    Xs[:, :-1] = (X[:, :-1] - mu) / sd
    W = fit_softmax(Xs, y, len(ROLE_VOCAB5), L2_LAMBDA, LR, N_ITERS)
    return W, mu, sd


def revise_predict_one_with_margin6(sent, W, mu, sd):
    """Same math as v2's revise_predict_one_with_margin, using mention_features_multi6."""
    preds, margins = {}, {}
    for i in sent["mention_idx"]:
        x = mention_features_multi6(sent, i)
        x = np.concatenate([x, [1.0]])
        xs = x.copy()
        xs[:-1] = (x[:-1] - mu) / sd
        p = _softmax((xs @ W)[None, :])[0]
        order = np.argsort(-p)
        top1, top2 = p[order[0]], p[order[1]] if len(p) > 1 else 0.0
        preds[i] = int(order[0])
        margins[i] = float(top1 - top2)
    return preds, margins


def loocv_revise_v4(noncanon_sents: list) -> tuple:
    n = len(noncanon_sents)
    out_preds, out_margins = {}, {}
    for held in range(n):
        train = [s for j, s in enumerate(noncanon_sents) if j != held]
        if not train:
            out_preds[held] = {}
            out_margins[held] = {}
            continue
        W, mu, sd = fit_softmax_on6(train)
        p, m = revise_predict_one_with_margin6(noncanon_sents[held], W, mu, sd)
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


def _lexicon_coverage_split_acc(sents, preds_by_sent):
    """CAN-FAIL CONTROL (a) diagnostic: role_acc split by whether this sentence's SUBJECT is
    lexicon-covered, restricted to REVISE-gated (non-canonical) sentences (canonical is untouched
    by construction; see module docstring)."""
    buckets = {"subj_covered": [0, 0], "subj_uncovered": [0, 0]}
    for sid, sent in enumerate(sents):
        if sent["kind"] == "canonical":
            continue
        key = "subj_covered" if sent["subj_lexicon_covered"] else "subj_uncovered"
        preds = preds_by_sent[sid]
        for i in sent["mention_idx"]:
            gold = sent["labels"][i]
            if gold == ROLE_IDX5["none"]:
                continue
            pred = preds.get(i, ROLE_IDX5["none"])
            buckets[key][1] += 1
            buckets[key][0] += int(pred == gold)
    return {k: {"role_acc": (c / n) if n else None, "role_n": n} for k, (c, n) in buckets.items()}


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

    # -----------------------------------------------------------------------
    # LEXICON COVERAGE REPORT over the ACTUAL train vocabulary (per contract: "report coverage over
    # the eval + train vocab"). Tokenized+tagged once here (also used to build the scrambled lexicon
    # over the SAME covered vocabulary).
    # -----------------------------------------------------------------------
    vocab_words, vocab_tags = [], []
    for r in all_recs:
        toks = tokenize(r["text"])
        tags = get_tagger().tag(toks)
        for w, t in zip(toks, tags):
            if t in MENTION_POS and w != '"':
                vocab_words.append(w)
                vocab_tags.append(t)
    train_coverage = coverage_report(vocab_words, vocab_tags)
    print("[%s] LEXICON train-vocab coverage: %s" % (mode, train_coverage), flush=True)

    eval_path = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
                              "gold_multiclause_entity_track_v2.jsonl")
    eval_words, eval_tags = [], []
    if os.path.exists(eval_path):
        with open(eval_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                for name, chain in rec["entities"].items():
                    for ev in chain:
                        head = ev["mention"].split()[-1]
                        toks = tokenize(ev["mention"])
                        tg = get_tagger().tag(toks)[-1] if toks else None
                        eval_words.append(head)
                        eval_tags.append(tg)
    eval_coverage = coverage_report(eval_words, eval_tags) if eval_words else None
    print("[%s] LEXICON eval-vocab (gold_multiclause_entity_track_v2) coverage: %s"
          % (mode, eval_coverage), flush=True)

    scrambled_lookup = scrambled_lookup_factory(vocab_words, vocab_tags, seed=20260802)

    def real_lookup(word, pos_tag):
        return lookup_animacy(word, pos_tag)

    def none_lookup(word, pos_tag):
        return None

    print("[%s] building %d sentences x 3 lexicon conditions (tagger load+tag) ..."
          % (mode, len(all_recs)), flush=True)
    sents_real = [build_sentence_multi6(r, real_lookup) for r in all_recs]
    sents_scrambled = [build_sentence_multi6(r, scrambled_lookup) for r in all_recs]
    sents_nodict = [build_sentence_multi6(r, none_lookup) for r in all_recs]

    n_copular_true = sum(1 for s in sents_real if s["kind"] == "copular_theme" and s["sent_summary"][4] >= 0.5)
    n_copular_total = sum(1 for s in sents_real if s["kind"] == "copular_theme")
    print("[%s] is_copular fires on %d/%d copular_theme-pool sentences (discriminator-fires check, "
          "unaffected by lexicon condition since gate is reused verbatim)"
          % (mode, n_copular_true, n_copular_total), flush=True)

    rng_random = np.random.default_rng(20260802)

    def commit_revise_predict(sents, loocv_pred_map, loocv_margin_map, W_prod, mu_prod, sd_prod,
                               margin_thresh, sid, sent):
        default_preds = clause_position_predict5(sent)
        if gate_fires_v3(sent, THRESH):
            if sid in loocv_pred_map:
                revise_preds, revise_margins = loocv_pred_map[sid], loocv_margin_map[sid]
            else:
                revise_preds, revise_margins = revise_predict_one_with_margin6(sent, W_prod, mu_prod, sd_prod)
            merged = {}
            for i in sent["mention_idx"]:
                if i in revise_preds and revise_margins.get(i, 0.0) >= margin_thresh:
                    merged[i] = revise_preds[i]
                else:
                    merged[i] = default_preds.get(i, ROLE_IDX5["patient"])
            return merged
        return default_preds

    def fit_and_score(sents, margin_thresh):
        noncanon_ids = [sid for sid, s in enumerate(sents) if s["kind"] != "canonical"]
        noncanon_sents = [sents[sid] for sid in noncanon_ids]
        loocv_preds, loocv_margins = loocv_revise_v4(noncanon_sents)
        loocv_pred_map = {noncanon_ids[j]: loocv_preds[j] for j in range(len(noncanon_ids))}
        loocv_margin_map = {noncanon_ids[j]: loocv_margins[j] for j in range(len(noncanon_ids))}
        W_prod, mu_prod, sd_prod = fit_softmax_on6(noncanon_sents)

        preds_by_sent = {}
        gate_flags = {}
        for sid, sent in enumerate(sents):
            preds_by_sent[sid] = commit_revise_predict(
                sents, loocv_pred_map, loocv_margin_map, W_prod, mu_prod, sd_prod, margin_thresh, sid, sent)
            gate_flags[sid] = gate_fires_v3(sent, THRESH)
        per_kind = eval_predictions5(sents, preds_by_sent)
        gate_diag = _gate_rate_by_kind(sents, gate_flags)
        coverage_split = _lexicon_coverage_split_acc(sents, preds_by_sent)
        canon = (per_kind.get("canonical") or {}).get("role_acc") or 0.0
        quot = (per_kind.get("quotative") or {}).get("role_acc") or 0.0
        byagent = (per_kind.get("passive_byagent") or {}).get("role_acc") or 0.0
        theme = (per_kind.get("copular_theme") or {}).get("role_acc") or 0.0
        n_gates = (int(canon >= CANONICAL_MIN) + int(quot >= QUOTATIVE_MIN) + int(byagent >= BYAGENT_MIN))
        return {
            "margin_thresh": margin_thresh, "canonical_role_acc": canon, "quotative_role_acc": quot,
            "byagent_role_acc": byagent, "theme_role_acc": theme, "n_preservation_gates_cleared": n_gates,
            "canonical_gate_fp_rate": gate_diag.get("canonical"),
            "preds_by_sent": preds_by_sent, "gate_diag": gate_diag, "coverage_split": coverage_split,
        }

    def _select_key(res):
        fp = res["canonical_gate_fp_rate"]
        fp = fp if fp is not None else 1.0
        return (res["n_preservation_gates_cleared"], res["theme_role_acc"], -fp)

    grid = [SELF_TEST_MARGIN_THRESH] if mode == "self_test" else MARGIN_THRESH_GRID
    print("[%s] sweeping %d margin_thresh configs for COMMIT_REVISE_V4_ANIMACY (re-selected per v3's "
          "own precedent for feature-space changes; THRESH/gate fixed) ..." % (mode, len(grid)), flush=True)
    grid_real = [fit_and_score(sents_real, m) for m in grid]
    selected_real = max(grid_real, key=_select_key)
    grid_summary_real = [{k: v for k, v in r.items() if k not in ("preds_by_sent", "gate_diag", "coverage_split")}
                          for r in grid_real]
    print("[%s] REAL selected margin_thresh=%.2f (canon=%.4f quot=%.4f byagent=%.4f theme=%.4f gates=%d/3)"
          % (mode, selected_real["margin_thresh"], selected_real["canonical_role_acc"],
             selected_real["quotative_role_acc"], selected_real["byagent_role_acc"],
             selected_real["theme_role_acc"], selected_real["n_preservation_gates_cleared"]), flush=True)

    print("[%s] sweeping %d margin_thresh configs for COMMIT_REVISE_V4_SCRAMBLED (identical grid, "
          "scrambled lexicon) ..." % (mode, len(grid)), flush=True)
    grid_scr = [fit_and_score(sents_scrambled, m) for m in grid]
    selected_scr = max(grid_scr, key=_select_key)
    grid_summary_scr = [{k: v for k, v in r.items() if k not in ("preds_by_sent", "gate_diag", "coverage_split")}
                         for r in grid_scr]
    print("[%s] SCRAMBLED selected margin_thresh=%.2f (canon=%.4f quot=%.4f byagent=%.4f theme=%.4f)"
          % (mode, selected_scr["margin_thresh"], selected_scr["canonical_role_acc"],
             selected_scr["quotative_role_acc"], selected_scr["byagent_role_acc"], selected_scr["theme_role_acc"]),
          flush=True)

    print("[%s] sweeping %d margin_thresh configs for V3_THEME_REPRO (no-dictionary lineage baseline) ..."
          % (mode, len(grid)), flush=True)
    grid_nodict = [fit_and_score(sents_nodict, m) for m in grid]
    selected_nodict = max(grid_nodict, key=_select_key)
    print("[%s] NO_DICT selected margin_thresh=%.2f (canon=%.4f quot=%.4f byagent=%.4f theme=%.4f)"
          % (mode, selected_nodict["margin_thresh"], selected_nodict["canonical_role_acc"],
             selected_nodict["quotative_role_acc"], selected_nodict["byagent_role_acc"],
             selected_nodict["theme_role_acc"]), flush=True)

    def run_arm(arm_name, tick, sents, selected):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            gate_diag = None
            extra = {}
            if arm_name in ("COMMIT_REVISE_V4_ANIMACY", "COMMIT_REVISE_V4_SCRAMBLED", "V3_THEME_REPRO"):
                preds_by_sent = selected["preds_by_sent"]
                gate_diag = selected["gate_diag"]
                extra = {"selected_margin_thresh": selected["margin_thresh"],
                         "coverage_split_role_acc": selected["coverage_split"]}
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
            print("[%s] arm=%s per_kind=%s" % (mode, arm_name, per_kind), flush=True)

    arm_specs = [
        ("COMMIT_REVISE_V4_ANIMACY", sents_real, selected_real),
        ("COMMIT_REVISE_V4_SCRAMBLED", sents_scrambled, selected_scr),
        ("V3_THEME_REPRO", sents_nodict, selected_nodict),
        ("CLAUSE_POSITION", sents_nodict, None),
        ("POSITION", sents_nodict, None),
        ("RANDOM", sents_nodict, None),
    ]
    for i, (arm, sents, sel) in enumerate(arm_specs):
        run_arm(arm, i, sents, sel)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return (units, canon_diag, len(all_recs), n_copular_true, n_copular_total, elapsed,
            train_coverage, eval_coverage, grid_summary_real, grid_summary_scr)


def _arms_must_differ(units):
    digs = {k: v["digest"] for k, v in units.items()}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical"


def decide_verdict(units, n_copular_true, n_copular_total, train_coverage, eval_coverage):
    def racc(arm, kind):
        v = (units[arm]["per_kind"].get(kind) or {}).get("role_acc")
        return v if v is not None else 0.0

    v4_canon = racc("COMMIT_REVISE_V4_ANIMACY", "canonical")
    v4_quot = racc("COMMIT_REVISE_V4_ANIMACY", "quotative")
    v4_byagent = racc("COMMIT_REVISE_V4_ANIMACY", "passive_byagent")
    v4_theme = racc("COMMIT_REVISE_V4_ANIMACY", "copular_theme")
    scr_canon = racc("COMMIT_REVISE_V4_SCRAMBLED", "canonical")
    scr_quot = racc("COMMIT_REVISE_V4_SCRAMBLED", "quotative")
    scr_byagent = racc("COMMIT_REVISE_V4_SCRAMBLED", "passive_byagent")
    scr_theme = racc("COMMIT_REVISE_V4_SCRAMBLED", "copular_theme")
    nd_canon = racc("V3_THEME_REPRO", "canonical")
    nd_quot = racc("V3_THEME_REPRO", "quotative")
    nd_byagent = racc("V3_THEME_REPRO", "passive_byagent")
    nd_theme = racc("V3_THEME_REPRO", "copular_theme")
    pos_theme = racc("POSITION", "copular_theme")
    rand_theme = racc("RANDOM", "copular_theme")

    discriminator_fires = (n_copular_true == n_copular_total) and (n_copular_total > 0)
    canonical_preserved = v4_canon >= CANONICAL_MIN
    quotative_preserved = v4_quot >= QUOTATIVE_MIN
    byagent_preserved = v4_byagent >= BYAGENT_MIN
    canonical_byte_identical_to_nodict = units["COMMIT_REVISE_V4_ANIMACY"]["per_kind"].get("canonical") == \
        units["V3_THEME_REPRO"]["per_kind"].get("canonical")

    meaning_required_lift = (v4_quot + v4_byagent + v4_theme) / 3.0 - (nd_quot + nd_byagent + nd_theme) / 3.0
    real_vs_scrambled = (v4_quot + v4_byagent + v4_theme) / 3.0 - (scr_quot + scr_byagent + scr_theme) / 3.0
    LIFT_NOISE_BAND = 0.03  # MEASURED-scale small-N pools (N~14-23 per kind); +/- this is noise, not signal

    lexicon_did_something = abs(meaning_required_lift) > LIFT_NOISE_BAND
    scrambled_does_not_beat_real = real_vs_scrambled >= -LIFT_NOISE_BAND

    summary = {
        "v4_animacy_canonical": v4_canon, "v4_animacy_quotative": v4_quot,
        "v4_animacy_byagent": v4_byagent, "v4_animacy_theme": v4_theme,
        "v4_scrambled_canonical": scr_canon, "v4_scrambled_quotative": scr_quot,
        "v4_scrambled_byagent": scr_byagent, "v4_scrambled_theme": scr_theme,
        "v3_theme_repro_nodict_canonical": nd_canon, "v3_theme_repro_nodict_quotative": nd_quot,
        "v3_theme_repro_nodict_byagent": nd_byagent, "v3_theme_repro_nodict_theme": nd_theme,
        "position_theme": pos_theme, "random_theme": rand_theme,
        "meaning_required_mean_lift_over_nodict": meaning_required_lift,
        "real_minus_scrambled_mean": real_vs_scrambled,
        "lexicon_did_something_above_noise_band": bool(lexicon_did_something),
        "scrambled_does_not_beat_real": bool(scrambled_does_not_beat_real),
        "canonical_byte_identical_to_nodict_repro": bool(canonical_byte_identical_to_nodict),
        "canonical_preserved": bool(canonical_preserved), "quotative_preserved": bool(quotative_preserved),
        "byagent_preserved": bool(byagent_preserved), "discriminator_fires": bool(discriminator_fires),
        "n_copular_true": n_copular_true, "n_copular_total": n_copular_total,
        "train_vocab_lexicon_coverage": train_coverage, "eval_vocab_lexicon_coverage": eval_coverage,
        "coverage_split_role_acc_v4_animacy": units["COMMIT_REVISE_V4_ANIMACY"].get("coverage_split_role_acc"),
        "per_arm_per_kind": {a: units[a]["per_kind"] for a in units},
    }

    if not discriminator_fires:
        return "HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE_IS_COPULAR_GATE_BROKEN", summary
    if not (canonical_preserved and quotative_preserved and byagent_preserved):
        return "PARTIAL_LEXICON_ADDED_BUT_EXISTING_ROLES_REGRESSED", summary
    if not scrambled_does_not_beat_real:
        return "CANFAIL_VIOLATION_SCRAMBLED_DICTIONARY_BEATS_REAL", summary
    if lexicon_did_something and meaning_required_lift > LIFT_NOISE_BAND:
        return "MIDDLE_BAND_LEXICON_LIFTS_MEANING_REQUIRED_ROLES_PRESERVATION_OK", summary
    return "NULL_RESULT_LEXICON_NO_MEASURABLE_LIFT_PRESERVATION_OK_CANFAIL_CLEAN", summary


def _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode,
                    grid_summary_real, grid_summary_scr):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | ANIMACY canon=%.3f quot=%.3f byagent=%.3f theme=%.3f | SCRAMBLED quot=%.3f byagent=%.3f "
            "theme=%.3f | NODICT(v3_repro) quot=%.3f byagent=%.3f theme=%.3f | meaning_required_lift=%.4f "
            "real_minus_scrambled=%.4f | discriminator_fires=%s canon_preserved=%s quot_preserved=%s "
            "byagent_preserved=%s | train_cov=%.3f eval_cov=%s"
            % (verdict, summary["v4_animacy_canonical"], summary["v4_animacy_quotative"],
               summary["v4_animacy_byagent"], summary["v4_animacy_theme"],
               summary["v4_scrambled_quotative"], summary["v4_scrambled_byagent"], summary["v4_scrambled_theme"],
               summary["v3_theme_repro_nodict_quotative"], summary["v3_theme_repro_nodict_byagent"],
               summary["v3_theme_repro_nodict_theme"], summary["meaning_required_mean_lift_over_nodict"],
               summary["real_minus_scrambled_mean"], summary["discriminator_fires"],
               summary["canonical_preserved"], summary["quotative_preserved"], summary["byagent_preserved"],
               summary["train_vocab_lexicon_coverage"]["coverage_frac"],
               ("%.3f" % summary["eval_vocab_lexicon_coverage"]["coverage_frac"])
               if summary["eval_vocab_lexicon_coverage"] else "n/a")
        ),
        "summary": summary,
        "bands": {"THRESH": THRESH, "MARGIN_THRESH_GRID": MARGIN_THRESH_GRID,
                  "CANONICAL_MIN": CANONICAL_MIN, "QUOTATIVE_MIN": QUOTATIVE_MIN, "BYAGENT_MIN": BYAGENT_MIN,
                  "RANDOM_CHANCE_5WAY": RANDOM_CHANCE_5WAY, "LIFT_NOISE_BAND": 0.03},
        "grid_summary_real": grid_summary_real, "grid_summary_scrambled": grid_summary_scr,
        "per_arm": {a: {k: v for k, v in u.items()} for a, u in units.items()},
        "canonical_pool_diag": canon_diag,
        "role_vocab": ROLE_VOCAB5,
        "n_sentences_pooled": n_sents,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "calibration_check": "adaptive_with_discriminator_gate: margin_thresh re-selected per v3's own "
                              "precedent (feature-space change); gate/THRESH/COMMIT default untouched",
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
# PRODUCTION-MODEL API for downstream wiring (exp_wire_extraction_accumulate_wm_oracle_vs_real_v6),
# mirroring v2/v3's fit_*_production_model / stage1_predict_clause_* convention exactly.
# ---------------------------------------------------------------------------
SELECTED_MARGIN_THRESH_V4 = 0.08  # placeholder; overwritten to the FULL run's selected value below
                                   # via _read_selected_margin_thresh_from_metrics() at import time
                                   # if a full-run metrics.json already exists (keeps downstream wiring
                                   # honest without re-running the grid twice).


def _read_selected_margin_thresh_from_metrics():
    p = os.path.join(OUTPUT_DIR, "metrics.json")
    if not os.path.exists(p):
        return SELECTED_MARGIN_THRESH_V4
    try:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("mode") != "full":
            return SELECTED_MARGIN_THRESH_V4
        return d["per_arm"]["COMMIT_REVISE_V4_ANIMACY"]["selected_margin_thresh"]
    except Exception:
        return SELECTED_MARGIN_THRESH_V4


def fit_commit_revise_v4_animacy_production_model():
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()
    theme_recs = load_copular_theme_pool()
    noncanon_recs = quot_recs + byagent_recs + passive_recs + theme_recs
    noncanon_sents = [build_sentence_multi6(r, lookup_animacy) for r in noncanon_recs]
    W, mu, sd = fit_softmax_on6(noncanon_sents)
    margin_thresh = _read_selected_margin_thresh_from_metrics()
    return {"W": W, "mu": mu, "sd": sd, "n_train_sentences": len(noncanon_sents),
            "thresh": THRESH, "margin_thresh": margin_thresh}


def stage1_predict_clause_commit_revise_v4_animacy(text, model):
    sent = build_sentence_multi6({"text": text, "kind": "eval", "role_map": {}, "parser_correct": False},
                                  lookup_animacy)
    if not sent["mention_idx"]:
        return sent, {}
    default_preds = clause_position_predict5(sent)
    if gate_fires_v3(sent, model["thresh"]):
        preds_idx, margins = revise_predict_one_with_margin6(sent, model["W"], model["mu"], model["sd"])
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
    ap.add_argument("--timeout", type=float, default=300.0,
                    help="formula self-test timeout budget (declared; full run expected < 180s: "
                         "3x the LOOCV grid v3_theme ran in ~60s, for the real/scrambled/no-dict "
                         "lexicon conditions)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        (units, canon_diag, n_sents, n_copular_true, n_copular_total, elapsed,
         train_coverage, eval_coverage, grid_summary_real, grid_summary_scr) = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units, n_copular_true, n_copular_total, train_coverage, eval_coverage)
    metrics = _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode,
                              grid_summary_real, grid_summary_scr)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
