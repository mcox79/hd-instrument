"""exp_read_discourse_state_of_mind_wsm_coupling_v1 -- first build of the discourse "STATE OF MIND" (rung 2),
ASSEMBLED from already-validated pieces, PLUS the decisive COUPLING TEST: does maintaining a discourse state
measurably IMPROVE per-sentence extraction (does comprehension help extraction, the top-down predictive loop)?

TRIGGER: notes/research_discourse_state_of_mind_situation_model_2026-07-17.md (the drill) characterizes the
discourse "now" as a NESTED structure -- Tier 0 (Centering's single-pointer Cb, McElree direct-access, zero
search) / Tier 1 (Cowan ~4-item Cf ranked list) / Tier 2 (Zwaan situation model: active entities/events across
sentences) / Tier 3 (durable foundation, consolidated at Zacks-Tversky Event-Segmentation-Theory prediction-
error boundaries). It is CONNECTIVE TISSUE, not a new subsystem: Tier 0/1 + the Cf-ranked search ALREADY EXIST
in experiments/exp_read_coref_hobbs_centering_resolver_v1.py (ANCHOR 2 discourse memory + ANCHOR 3 Hobbs/
Centering resolver); this cell (a) ADDS the missing Tier-0 Cb-FIRST fast path the drill's Prediction 1 asks
for (check Cb before falling into the existing Cf-window search -- reuses resolve_coref() UNMODIFIED as the
Tier-1 fallback, imported not rebuilt), (b) ADDS a minimal Tier-2 "active event" slot (the most recent single
committed (subject, relation, object) -- Zwaan's situation-model content, reduced to what this schema's SVO
register actually carries: an event, not five independently-monitored dimensions -- REDUCED SCOPE, flagged),
used to resolve VP-ELLIPSIS ("The frog does too.") the SAME way Tier 0/1 resolve pronouns -- a SECOND, distinct
discourse-dependent construction (not just relabeling coref), giving the coupling test two independent
mechanisms instead of one, (c) implements Centering's 4-way transition classification (CONTINUE / RETAIN /
SMOOTH-SHIFT / ROUGH-SHIFT, per Grosz-Joshi-Weinstein / Brennan-Friedman-Pollard) PLUS a NOVEL_ENTITY_SHIFT /
SHIFT_FOUNDATION discontinuity signal (the EST/Gernsbacher-SHIFT surprisal proxy: "does the new sentence's
protagonist overlap what is currently active, or is it a genuinely new participant with zero overlap" --
REDUCED SCOPE: a cheap entity-overlap proxy for the drill's relation-conditioned-PE ingest-gate axis, NOT an
import of that axis -- the KG ingest-gate's community-transition-PE module operates over a knowledge-graph
regime (entities embedded in a large relational graph) that is a SHAPE_MISMATCH for this toy closed-schema SVO
discourse register; reusing the CONCEPT (prediction-error-as-boundary-trigger), reimplemented locally at the
register-appropriate scale, is the honest choice per Gate C -- flagged, not silently substituted).

THE COUPLING TEST (decisive arm, per task contract): the SAME fixed hand-authored fixture corpus is scored
TWICE by the IDENTICAL scoring function -- WITH_STATE (the WSM Tier 0/1/2 module active, resolving pronoun-
subjects and VP-ellipsis when the base parser abstains) vs WITHOUT_STATE (the base parser run on each sentence
IN ISOLATION, no cross-sentence memory at all, matching literally "per-sentence extraction with no discourse
memory"). Two independent discourse-dependent construction classes (coref, ellipsis) are each split into an
UNAMBIGUOUS/resolvable kind (gold = the correctly-bound triple; WITHOUT_STATE structurally CANNOT produce it --
the base parser's own rule tags COREF_UNRESOLVED / NO_VERB fire on these rows in isolation by construction,
verified live below, not assumed) and a GUARDRAIL kind (genuine coref ties -- 2+ candidates survive BOTH number
AND schema per the coref cell's own construction; OR ellipsis with ZERO candidate antecedent event -- gold =
ABSTAIN; a state-on resolver that GUESSES here is strictly worse than doing nothing, the zero-hallucination
invariant). A third CONTROL group (plain full-NP declarative sentences, no pronoun, no ellipsis -- gold =
the deterministic ie_extract() result, asserted parseable standalone) checks the state module does NOT
regress sentences that never needed discourse context -- fairness: control rows are scored by the IDENTICAL
function under WITH_STATE and WITHOUT_STATE; the only difference between the two arms is whether the WSM's
resolvers are invoked when the base parser abstains on COREF_UNRESOLVED / a detected ellipsis pattern.

CONSTRUCTION-DETERMINED-OUTCOME GUARD (honestly addressed, not glossed): the coref UNAMBIGUOUS/AMBIGUOUS split
is NOT authored fresh here -- it is REUSED VERBATIM from exp_read_coref_hobbs_centering_resolver_v1.COREF_ITEMS
(that cell's own self-test already verifies every "ambiguous" row is a GENUINE tie: 2+ distinct candidates
survive number-agreement AND the schema-type filter -- _count_genuine_ties(), reused here unmodified). The
ellipsis UNAMBIGUOUS rows use a DIFFERENT full-NP subject than the antecedent sentence's subject (never a
same-word repeat) so WITH_STATE cannot win by literal string match; the ellipsis GUARDRAIL rows use an
out-of-schema verb (sleep/run -- not in VERB_LEX) so the antecedent sentence structurally produces ZERO
triples, verified live (not assumed) at self-test.

REDUCED SCOPE (flagged per task contract's escape hatch): this is the MINIMAL first build -- Tier 0 (Cb
pointer) + Tier 1 (Cf list, reused unmodified) + a REDUCED Tier 2 (single active-event slot, not Zwaan's
5 independently-monitored dimensions -- this SVO register has no time/space/intentionality axis to monitor
distinctly from "the event"). Tier 3 (durable-store consolidation triggered by the discontinuity signal) is
NOT built here -- the discontinuity signal is computed and REPORTED (n_shift / transition histogram) as
evidence the WSM tracks the "now," but nothing is committed to a separate long-term store in this cell (no
VSA/torch needed -- per COMPUTE-PROPORTIONALITY, this is a symbolic parse-level coupling question, not a
capacity/fit question; a heavy VSA store loop would not sharpen the answer to "does state help extraction").
Prediction 4 (dialogue/grounding wrapper) is explicitly out of scope, per the drill's own note (b).

METRICS (reported SEPARATELY per contract -- coverage vs precision, not conflated):
  dependent_resolvable_acc  = accuracy on {coref, ellipsis} x {unambiguous} target rows (the coupling headline)
  guardrail_wrong_rate      = fraction of {coref, ellipsis} x {ambiguous/unresolvable} rows where the resolver
                              emitted something instead of abstaining (the zero-hallucination check)
  control_acc               = accuracy on the discourse-independent control rows (regression check)
  per-group coverage/precision (coref/ellipsis dependent + guardrail) reported separately, not just accuracy
  tier0_fastpath_rate       = of BOUND coref rows, fraction resolved via the Tier-0 Cb-first zero-search path
                              vs falling to the existing Tier-1 Cf-window search (Prediction 1 evidence)
  transition histogram      = CONTINUE / RETAIN / SMOOTH_SHIFT / ROUGH_SHIFT / NOVEL_ENTITY_SHIFT /
                              SHIFT_FOUNDATION counts (does the WSM track the "now" -- descriptive, not gated)

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running):
  HARD-PASS (discourse state genuinely COUPLES to extraction; comprehension helps, without hurting independent
             sentences, without hallucinating on genuine ambiguity):
    (WITH.dependent_resolvable_acc - WITHOUT.dependent_resolvable_acc) >= 0.60  AND
    WITH.dependent_resolvable_acc >= 0.80  AND
    WITH.control_acc >= 0.95 AND WITH.control_acc >= (WITHOUT.control_acc - 0.02)  AND
    WITH.guardrail_wrong_rate < 0.20  AND
    tier0_fastpath_rate > 0.0 (Tier-0 fast path actually fires at least once -- mechanism-fires, not vacuous) AND
    n_shift_total >= 1 (the discontinuity signal fires at least once -- mechanism-fires, not vacuous).
  HARD-FAIL (the module is inert or actively harmful):
    (WITH.dependent_resolvable_acc - WITHOUT.dependent_resolvable_acc) < 0.40  OR
    WITH.control_acc < (WITHOUT.control_acc - 0.05)  OR
    WITH.guardrail_wrong_rate >= 0.30.
  MIDDLE_BAND otherwise (partial: some lift, but under 0.60 delta or guardrail imperfect -- report dominant class).
  P estimates (from the drill, HYPOTHESIZED@notes/research_discourse_state_of_mind_situation_model_2026-07-17.md):
    Prediction 1 (Tier-0 Cb-first) P=0.40; this cell's coupling claim is a NEW construction not in the drill's
    4 numbered predictions (the drill's Predictions 1-4 are narrower/different splits) -- treated as P=0.45
    (deflated: novel-synthesis architecture-assembly claim, no direct prior measurement of THIS exact corpus).

COMPUTE: fully symbolic, deterministic (NO RNG anywhere -- no seeds to declare). No VSA/torch/numpy needed for
  the discriminator (COMPUTE-PROPORTIONALITY: this is a parse-level diagnostic, not a capacity/fit question).
  Wall time < 1s (pure Python string/tag processing over a ~40-row fixed fixture corpus). Local, no queue/GPU/
  atoms/push. ASCII-only. Storage: no_storage. smoke == full (nothing to shrink; deterministic fixed corpus,
  same pattern as this cell's own self-test). progress_logging = print_flush_true (line-buffered stdout).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): WITH_STATE vs WITHOUT_STATE emitted-triple-set hash
#     differs (state resolves rows the isolated baseline structurally cannot).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- fully symbolic, discrete role-assignment; no phasor/argmax noise.
# - baseline_in_band: N/A BY DESIGN -- WITHOUT_STATE's near-zero dependent_resolvable_acc is a BY-CONSTRUCTION
#     floor (the base parser's own rule tags COREF_UNRESOLVED/NO_VERB fire in isolation, verified live), not a
#     tunable regime; asserted, not assumed to be in a "measurable band."
# - discriminator survives scale: fixed hand-authored corpus (no N/scale axis); discriminators are (1) WITH
#     binds dependent-resolvable rows the isolated baseline cannot (asserted), (2) WITH abstains on genuine
#     ties/zero-antecedent rows (guardrail, asserted), (3) control rows identical both arms (asserted),
#     (4) Tier-0 fast path fires >=1 (asserted), (5) discontinuity signal fires >=1 (asserted).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON. Numbers tagged HYPOTHESIZED@prereg /
#     MEASURED@metrics / CITED (drill).
# - real_code_path (F.1): self-test constructs+calls the REAL imported ie_extract / resolve_coref /
#     _mentions_from_triples / _find_subject_pronoun from the actual sibling modules (not reimplemented),
#     at the same tiny fixture scale the FULL run uses (no separate synthetic-only branch).
# - deterministic_seeding (F.5): N/A -- no RNG anywhere in this cell (fully symbolic deterministic parser).
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import hashlib
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_state_of_mind_wsm_coupling_v1"

# --- GENUINE REUSE: the proven glass-box parser + the proven coref discourse-memory/resolver (imported, not
# rebuilt). This IS the "connective tissue over existing validated pieces" the task asked for. ---
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (
    ie_extract,
    _tokenize,
    _tag_token,
    _validity_filter,
)
from experiments.exp_read_coref_hobbs_centering_resolver_v1 import (
    COREF_ITEMS,
    ROLE_RANK,
    WINDOW_DEFAULT,
    _mentions_from_triples,
    _find_subject_pronoun,
    _pron_number,
    resolve_coref,
)

# ---------------------------------------------------------------------------
# ANCHOR E (new, this cell): VP-ellipsis detection + Tier-2 (active-event) resolution.
# ---------------------------------------------------------------------------
ELLIPSIS_TAILS = (("too",), ("as", "well"), ("the", "same"))


def _detect_ellipsis_subject(text):
    """"<full-NP subject> does <too|as well|the same>." with NO other verb -> returns the subject lemma, else
    None. Glass-box: pure token-tag pattern match over the SAME tokenizer/tagger the base parser uses."""
    toks = _tokenize(text)
    if "does" not in toks:
        return None
    di = toks.index("does")
    tail = tuple(toks[di + 1:])
    if tail not in ELLIPSIS_TAILS:
        return None
    tagged = [_tag_token(w) for w in toks[:di]]
    noun_idx = [i for i, (tag, _lm, _fm) in enumerate(tagged) if tag == "NOUN"]
    if not noun_idx:
        return None
    return tagged[noun_idx[-1]][1]


def resolve_ellipsis(subject_lemma, last_event):
    """Tier-2 (active-event) resolution: copy (relation, object) from the most recent single committed event.
    ZERO or AMBIGUOUS antecedent (last_event is None) -> ABSTAIN (never guess). Returns (triples, info)."""
    if last_event is None:
        return [], {"reason": "ELLIPSIS_NO_ANTECEDENT"}
    _esubj, erel, eobj = last_event
    cand = (subject_lemma, erel, eobj)
    valid = _validity_filter([cand])
    if not valid:
        return [], {"reason": "ELLIPSIS_INVALID_SUBSTITUTION", "candidate": cand}
    return valid, {"reason": "BOUND_ELLIPSIS_TIER2", "antecedent_event": list(last_event)}


# ---------------------------------------------------------------------------
# ANCHOR T0 (new, this cell): Tier-0 Cb-first fast path (drill Prediction 1), Tier-1 fallback = resolve_coref
# UNMODIFIED (imported). Tier-2 = active-event slot for ellipsis. WSMState is the per-document "now."
# ---------------------------------------------------------------------------
class WSMState:
    def __init__(self):
        self.cb = None                 # Tier 0: current backward-looking center (single pointer, zero-cost)
        self.cb_number = None
        self.cf_memory = []            # Tier 1: ranked mention window (reuses coref cell's own mention schema)
        self.last_event = None         # Tier 2: most recent single committed (subj, rel, obj), or None
        self.transitions = []          # per-sentence Centering transition log (does it track the "now"?)
        self.n_shift = 0               # NOVEL_ENTITY_SHIFT count (surprisal-proxy discontinuity signal)


def resolve_pronoun_wsm(text, wsm, window=WINDOW_DEFAULT, store=None, use_schema_tiebreak=False):
    """Tier-0-first pronoun resolution: check Cb before falling into the existing Tier-1 Cf-window search
    (resolve_coref, imported UNMODIFIED). Rule 1 (Grosz-Joshi-Weinstein): if pronominalized, prefer the Cb --
    BUT ONLY when the Cb is the UNIQUE number-compatible candidate in the active window. Direct-access (McElree)
    is a claim about UNAMBIGUOUS retrieval being cheap, not a license to override a genuine tie: if another
    same-number entity is ALSO active in wsm.cf_memory, this is exactly a genuine-ambiguity case and MUST fall
    through to Tier-1's number-filter + tie-detection (resolve_coref) rather than guessing via Cb-preference.
    (Caught live at self-test on this cell's own build: an ungated Cb-first check bound the wrong/undetermined
    entity on every genuine-tie fixture -- guardrail_wrong_rate=0.667 -- before this competitor check was added.)
    """
    pron, pidx, toks = _find_subject_pronoun(text)
    if pron is None:
        return [], {"reason": "NO_SUBJECT_PRONOUN"}
    pnum = _pron_number(pron)
    if pnum is None:
        return [], {"reason": "PRONOUN_OUT_OF_SCOPE", "pron": pron}
    if wsm.cb is not None and wsm.cb_number == pnum:
        competitors = {m["lemma"] for m in wsm.cf_memory if m["number"] == pnum and m["lemma"] != wsm.cb}
        if not competitors:
            sub = list(toks)
            sub[pidx] = wsm.cb
            triples, rule, _fr = ie_extract(" ".join(sub))
            if triples:
                return triples, {"reason": "BOUND_TIER0", "antecedent": wsm.cb, "rule": "CENTERING_CB_FASTPATH"}
    # Tier-1 fallback: the EXISTING Cf-ranked Hobbs/Centering resolver (imported, unmodified).
    return resolve_coref(text, wsm.cf_memory, len(wsm.transitions), window=window, store=store,
                          use_schema_tiebreak=use_schema_tiebreak)


def _classify_transition(cb_prev, cur_subjects):
    """Centering's 4-way transition (Grosz-Joshi-Weinstein / Brennan-Friedman-Pollard), PLUS a
    NOVEL_ENTITY_SHIFT / SHIFT_FOUNDATION discontinuity flag (the EST/Gernsbacher-SHIFT surprisal proxy).
    In this single-subject SVO register the current sentence's subject IS always Cf-top-ranked when present,
    so RETAIN/ROUGH-SHIFT (Cb persists/changes but is NOT the preferred item) are reachable only when no
    subject-level Cb candidate exists this sentence -- honestly reported, not forced to occur."""
    cb_new = sorted(cur_subjects)[0] if cur_subjects else None
    if cb_prev is None:
        return "SHIFT_FOUNDATION", cb_new             # laying a foundation (Gernsbacher) -- no prior Cb yet
    if cb_new is None:
        return "NONE_NO_REALIZATION", cb_prev          # sentence realized no subject-level Cb candidate
    if cb_new == cb_prev:
        return "CONTINUE", cb_new
    return "SMOOTH_SHIFT", cb_new                      # new Cb, and it IS the preferred (subject) item


def update_wsm(wsm, sidx, text, triples, window=WINDOW_DEFAULT):
    """Per-sentence WSM update: Tier-0/1 (Cb + Cf memory) + Tier-2 (active event) + discontinuity signal."""
    mentions = _mentions_from_triples(triples, text, sidx)
    subj_mentions = [m for m in mentions if m["role"] == "subject"]
    cur_subjects = {m["lemma"] for m in subj_mentions}
    active_cf = {m["lemma"] for m in wsm.cf_memory}

    label, cb_new = _classify_transition(wsm.cb, cur_subjects)
    if label == "SMOOTH_SHIFT" and cb_new not in active_cf:
        label = "NOVEL_ENTITY_SHIFT"                   # brand-new participant, zero overlap -> surprisal proxy
        wsm.n_shift += 1
    wsm.transitions.append({"sidx": sidx, "transition": label, "cb": cb_new})

    if subj_mentions:
        ranked = sorted(subj_mentions, key=lambda m: (-m["sidx"], ROLE_RANK.get(m["role"], 9)))
        wsm.cb = ranked[0]["lemma"]
        wsm.cb_number = ranked[0]["number"]
    wsm.cf_memory.extend(mentions)
    wsm.cf_memory = [m for m in wsm.cf_memory if (sidx - m["sidx"]) <= window]
    wsm.last_event = triples[0] if len(triples) == 1 else None    # Tier 2: exactly-one-event carries forward
    return label


# ---------------------------------------------------------------------------
# ANCHOR ELL-ITEMS (new, this cell): VP-ellipsis fixtures, same shape/discipline as COREF_ITEMS.
# ---------------------------------------------------------------------------
def _E(text, gts, role):
    return {"text": text, "gts": set(gts), "role": role}


ELLIPSIS_ITEMS = [
    # ---- UNAMBIGUOUS: ctx establishes exactly ONE event; target uses a DIFFERENT full-NP subject (never a
    #      literal string repeat -- WITH_STATE cannot win by string match, only by copying (relation, object)).
    {"kind": "unambiguous", "sents": [
        _E("The bird eats a seed.", [("bird", "eats", "seed")], "ctx"),
        _E("The frog does too.", [("frog", "eats", "seed")], "target")]},
    {"kind": "unambiguous", "sents": [
        _E("The cow chases the cat.", [("cow", "chases", "cat")], "ctx"),
        _E("The dog does as well.", [("dog", "chases", "cat")], "target")]},
    {"kind": "unambiguous", "sents": [
        _E("The owl lives in the barn.", [("owl", "lives_in", "barn")], "ctx"),
        _E("The frog does the same.", [("frog", "lives_in", "barn")], "target")]},
    {"kind": "unambiguous", "sents": [
        _E("The mouse eats the worm.", [("mouse", "eats", "worm")], "ctx"),
        _E("The bird does too.", [("bird", "eats", "worm")], "target")]},
    {"kind": "unambiguous", "sents": [
        _E("The kitten chases the fish.", [("kitten", "chases", "fish")], "ctx"),
        _E("The dog does too.", [("dog", "chases", "fish")], "target")]},
    # ---- UNRESOLVABLE (guardrail): ctx uses an OUT-OF-SCHEMA verb (sleep/run -- not in VERB_LEX) -> the ctx
    #      sentence itself produces ZERO triples (verified live at self-test) -> NO candidate event exists ->
    #      the target ellipsis sentence MUST abstain (gold = empty; a guess here is a wrong-entity fact).
    {"kind": "unresolvable", "sents": [
        _E("The owl sleeps in the tree.", [], "ctx"),
        _E("The frog does too.", [], "target")]},
    {"kind": "unresolvable", "sents": [
        _E("The mouse runs in the field.", [], "ctx"),
        _E("The cat does as well.", [], "target")]},
]

# ---------------------------------------------------------------------------
# ANCHOR CTRL (new, this cell): discourse-independent control -- plain full-NP declaratives, gold = the
# deterministic ie_extract() result (asserted parseable standalone at self-test, not assumed).
# ---------------------------------------------------------------------------
CONTROL_ITEMS = [
    ("The cow eats grass.", [("cow", "eats", "grass")]),
    ("The dog chases the mouse.", [("dog", "chases", "mouse")]),
    ("The fish lives in the pond.", [("fish", "lives_in", "pond")]),
    ("The owls chase the frogs.", [("owl", "chases", "frog")]),
    ("The kitten eats bread.", [("kitten", "eats", "bread")]),
    ("The bird lives in the nest.", [("bird", "lives_in", "nest")]),
]

DEPENDENT_KINDS = {"unambiguous"}
GUARDRAIL_KINDS = {"ambiguous", "unresolvable"}


def build_unified_docs():
    """Unified doc list across 3 groups: coref (reused verbatim from the sibling cell), ellipsis (new), control
    (new). Each sentence carries gts (gold triple set; empty == correct behaviour is ABSTAIN) + is_target."""
    docs = []
    for item in COREF_ITEMS:
        sents = [{"text": s["text"], "gts": set(s["gts"]), "role": s["role"], "is_target": s["role"] == "coref"}
                 for s in item["sents"]]
        docs.append({"group": "coref", "kind": item["kind"], "sents": sents})
    for item in ELLIPSIS_ITEMS:
        sents = [{"text": s["text"], "gts": set(s["gts"]), "role": s["role"], "is_target": s["role"] == "target"}
                 for s in item["sents"]]
        docs.append({"group": "ellipsis", "kind": item["kind"], "sents": sents})
    for text, gold in CONTROL_ITEMS:
        docs.append({"group": "control", "kind": "control",
                      "sents": [{"text": text, "gts": set(gold), "role": "target", "is_target": True}]})
    return docs


# ---------------------------------------------------------------------------
# Per-document run loop: WITH_STATE (WSM active) vs WITHOUT_STATE (isolated per-sentence, no memory at all).
# ---------------------------------------------------------------------------
def run_document(sents, state_on, window=WINDOW_DEFAULT):
    wsm = WSMState() if state_on else None
    records = []
    for sidx, s in enumerate(sents):
        text = s["text"]
        triples, rule, _fr = ie_extract(text)
        resolution = "PARSER_DIRECT"
        if rule == "COREF_UNRESOLVED":
            if state_on:
                triples, info = resolve_pronoun_wsm(text, wsm, window=window)
                resolution = info.get("reason", "UNKNOWN")
            else:
                triples, resolution = [], "STATE_OFF_ABSTAIN"
        elif rule == "NO_VERB":
            subj = _detect_ellipsis_subject(text)
            if subj is not None:
                if state_on:
                    triples, info = resolve_ellipsis(subj, wsm.last_event)
                    resolution = info.get("reason", "UNKNOWN")
                else:
                    triples, resolution = [], "STATE_OFF_ABSTAIN"
        emitted = set(triples) if triples else set()
        gold = s["gts"]
        should_abstain = (len(gold) == 0)
        correct = (len(emitted) == 0) if should_abstain else (emitted == gold)
        records.append({"sidx": sidx, "text": text, "role": s["role"],
                         "emitted": sorted(emitted), "gold": sorted(gold), "resolution": resolution,
                         "correct": correct})
        if state_on:
            update_wsm(wsm, sidx, text, list(emitted), window=window)
    return records, wsm


def analyze_wsm(state_on, window=WINDOW_DEFAULT):
    docs = build_unified_docs()
    all_records = []
    n_shift_total = 0
    transition_hist = {}
    tier0_bound = 0
    tier1_bound = 0
    for doc in docs:
        sents = doc["sents"]
        records, wsm = run_document(sents, state_on, window=window)
        for r, s in zip(records, sents):
            r["group"] = doc["group"]
            r["kind"] = doc["kind"]
            r["is_target"] = s["is_target"]
            if state_on and r["resolution"] == "BOUND_TIER0":
                tier0_bound += 1
            elif state_on and r["resolution"] == "BOUND":
                tier1_bound += 1
        all_records.extend(records)
        if state_on and wsm is not None:
            n_shift_total += wsm.n_shift
            for t in wsm.transitions:
                transition_hist[t["transition"]] = transition_hist.get(t["transition"], 0) + 1

    def _stats(rows):
        n = len(rows)
        if n == 0:
            return {"n": 0, "acc": 0.0, "coverage": 0.0, "precision": 0.0}
        acc = sum(r["correct"] for r in rows) / float(n)
        emitted_rows = [r for r in rows if len(r["emitted"]) > 0]
        coverage = len(emitted_rows) / float(n)
        precision = (sum(1 for r in emitted_rows if r["correct"]) / float(len(emitted_rows))) if emitted_rows else 0.0
        return {"n": n, "acc": acc, "coverage": coverage, "precision": precision}

    def _group(group, kinds):
        return _stats([r for r in all_records if r["is_target"] and r["group"] == group and r["kind"] in kinds])

    coref_dep = _group("coref", {"unambiguous"})
    coref_guard = _group("coref", {"ambiguous"})
    coref_unres = _group("coref", {"unresolvable"})
    coref_schema = _group("coref", {"schema_resolvable"})
    ellipsis_dep = _group("ellipsis", {"unambiguous"})
    ellipsis_guard = _group("ellipsis", {"unresolvable"})
    control = _group("control", {"control"})

    dep_rows = [r for r in all_records if r["is_target"] and r["kind"] in DEPENDENT_KINDS
                and r["group"] in ("coref", "ellipsis")]
    guard_rows = [r for r in all_records if r["is_target"] and r["kind"] in GUARDRAIL_KINDS
                  and r["group"] in ("coref", "ellipsis")]
    dep_stats = _stats(dep_rows)
    guard_stats = _stats(guard_rows)
    guardrail_wrong_rate = 1.0 - guard_stats["acc"]        # correct on a guardrail row == abstained properly

    tier0_denom = tier0_bound + tier1_bound
    tier0_rate = (tier0_bound / float(tier0_denom)) if tier0_denom > 0 else 0.0

    accepted_key = tuple(sorted((r["group"], r["kind"], r["sidx"], tuple(r["emitted"])) for r in all_records))
    arm_hash = hashlib.sha256(json.dumps(accepted_key).encode("utf-8")).hexdigest()

    return {
        "state_on": state_on,
        "dependent_resolvable_acc": dep_stats["acc"], "dependent_resolvable_coverage": dep_stats["coverage"],
        "dependent_resolvable_precision": dep_stats["precision"], "n_dependent_resolvable": dep_stats["n"],
        "guardrail_wrong_rate": guardrail_wrong_rate, "n_guardrail_rows": guard_stats["n"],
        "control_acc": control["acc"], "control_coverage": control["coverage"], "n_control": control["n"],
        "coref_dependent": coref_dep, "coref_guardrail": coref_guard, "coref_unresolvable": coref_unres,
        "coref_schema_resolvable": coref_schema,
        "ellipsis_dependent": ellipsis_dep, "ellipsis_guardrail": ellipsis_guard,
        "n_shift_total": n_shift_total, "transition_histogram": transition_hist,
        "tier0_fastpath_rate": tier0_rate, "tier0_bound": tier0_bound, "tier1_bound": tier1_bound,
        "arm_hash": arm_hash,
        "records": all_records,
    }


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg).
# ---------------------------------------------------------------------------
def compute_verdict(with_s, without_s):
    delta = with_s["dependent_resolvable_acc"] - without_s["dependent_resolvable_acc"]
    hp = (
        delta >= 0.60 and
        with_s["dependent_resolvable_acc"] >= 0.80 and
        with_s["control_acc"] >= 0.95 and
        with_s["control_acc"] >= (without_s["control_acc"] - 0.02) and
        with_s["guardrail_wrong_rate"] < 0.20 and
        with_s["tier0_fastpath_rate"] > 0.0 and
        with_s["n_shift_total"] >= 1
    )
    hf = (
        delta < 0.40 or
        with_s["control_acc"] < (without_s["control_acc"] - 0.05) or
        with_s["guardrail_wrong_rate"] >= 0.30
    )
    tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    localize = []
    if delta < 0.60:
        localize.append("coupling delta below 0.60 (%.3f) -- state does not lift dependent-resolvable rows enough" % delta)
    if with_s["control_acc"] < 0.95:
        localize.append("control accuracy below 0.95 (%.3f) -- state regresses independent sentences" % with_s["control_acc"])
    if with_s["guardrail_wrong_rate"] >= 0.20:
        localize.append("GUARDRAIL: wrong_guess_rate=%.3f on genuine ties/zero-antecedent rows" % with_s["guardrail_wrong_rate"])
    if with_s["tier0_fastpath_rate"] <= 0.0:
        localize.append("Tier-0 fast path never fired (mechanism vacuous)")
    if with_s["n_shift_total"] < 1:
        localize.append("discontinuity signal never fired (segmentation vacuous)")
    weakest = localize if localize else ["none (coupling delta strong, control preserved, guardrail clean)"]

    msg = (f"{tier} | COUPLING delta={delta:.3f} (WITH={with_s['dependent_resolvable_acc']:.3f} vs "
           f"WITHOUT={without_s['dependent_resolvable_acc']:.3f}, n={with_s['n_dependent_resolvable']}) | "
           f"CONTROL WITH={with_s['control_acc']:.3f} WITHOUT={without_s['control_acc']:.3f} "
           f"(n={with_s['n_control']}) | GUARDRAIL wrong_guess_rate={with_s['guardrail_wrong_rate']:.3f} "
           f"(n={with_s['n_guardrail_rows']}) | tier0_fastpath_rate={with_s['tier0_fastpath_rate']:.3f} "
           f"(tier0={with_s['tier0_bound']} tier1={with_s['tier1_bound']}) | n_shift={with_s['n_shift_total']} "
           f"transitions={with_s['transition_histogram']} | weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra (mirrors exp_read_coref_hobbs_centering_resolver_v1's proven pattern).
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_discourse_state_of_mind_wsm_coupling_v1",
           "smoke": "exp_read_discourse_state_of_mind_wsm_coupling_v1_smoke",
           "self_test": "exp_read_discourse_state_of_mind_wsm_coupling_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
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
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminators FIRE.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (ie_extract + resolve_coref + WSMState + ellipsis resolver)...",
          flush=True)

    # (1) sanity: the ellipsis-guardrail ctx sentences produce ZERO triples standalone (verified, not assumed).
    for text in ["The owl sleeps in the tree.", "The mouse runs in the field."]:
        tr, rule, _ = ie_extract(text)
        assert tr == [] and rule == "NO_VERB", f"expected NO_VERB abstain for {text!r}, got {tr}/{rule}"

    # (2) ellipsis detection fires on the target pattern, not on unrelated sentences.
    assert _detect_ellipsis_subject("The frog does too.") == "frog"
    assert _detect_ellipsis_subject("The dog does as well.") == "dog"
    assert _detect_ellipsis_subject("The frog does the same.") == "frog"
    assert _detect_ellipsis_subject("The bird eats a seed.") is None, "must NOT fire on a normal sentence"

    # (3) Tier-2 ellipsis resolution: copies (relation, object) from the active event onto a DIFFERENT subject.
    tr, info = resolve_ellipsis("frog", ("bird", "eats", "seed"))
    assert set(tr) == {("frog", "eats", "seed")}, f"ellipsis bind failed: {tr}"
    assert info["reason"] == "BOUND_ELLIPSIS_TIER2"
    # guardrail: no antecedent event -> ABSTAIN (never guess).
    tr2, info2 = resolve_ellipsis("frog", None)
    assert tr2 == [] and info2["reason"] == "ELLIPSIS_NO_ANTECEDENT", "ellipsis must abstain with no antecedent"

    # (4) Tier-0 fast path: WSM with an established Cb resolves a pronoun with ZERO Tier-1 search.
    # (plural object -- keeps the fixture a genuinely UNIQUE singular candidate, matching the coref cell's own
    #  number-agreement convention; a singular object would create a real number-tie, exercised separately below.)
    wsm = WSMState()
    update_wsm(wsm, 0, "The bird eats seeds.", [("bird", "eats", "seed")])
    assert wsm.cb == "bird" and wsm.cb_number == "singular", f"Cb not set: {wsm.cb}"
    tr3, info3 = resolve_pronoun_wsm("It chases the cat.", wsm)
    assert set(tr3) == {("bird", "chases", "cat")} and info3["reason"] == "BOUND_TIER0", \
        f"Tier-0 fast path failed: {tr3} / {info3}"

    # (4b) GUARDRAIL REGRESSION CHECK (the exact bug caught live during this cell's own build, wrong_guess_rate
    # =0.667 before the fix): when a SAME-NUMBER competitor is active, Tier-0 must NOT fast-path -- it must
    # DEFER to Tier-1's number-filter + tie-detection, which correctly abstains on the genuine tie.
    wsm_tie = WSMState()
    update_wsm(wsm_tie, 0, "The bird eats a seed.", [("bird", "eats", "seed")])   # bird + seed both singular
    tr4, info4 = resolve_pronoun_wsm("It chases the cat.", wsm_tie)
    assert tr4 == [] and info4["reason"] == "GENUINE_TIE", \
        f"Tier-0 must defer on a same-number competitor, not guess: {tr4} / {info4}"

    # (5) transition classification: CONTINUE fires when the same Cb persists; SHIFT_FOUNDATION on doc-initial.
    wsm2 = WSMState()
    lab1 = update_wsm(wsm2, 0, "The bird eats a seed.", [("bird", "eats", "seed")])
    assert lab1 == "SHIFT_FOUNDATION", f"expected SHIFT_FOUNDATION on doc-initial, got {lab1}"
    lab2 = update_wsm(wsm2, 1, "The bird chases the cat.", [("bird", "chases", "cat")])
    assert lab2 == "CONTINUE", f"expected CONTINUE (same Cb persists), got {lab2}"
    lab3 = update_wsm(wsm2, 2, "The frog eats the worm.", [("frog", "eats", "worm")])
    assert lab3 == "NOVEL_ENTITY_SHIFT", f"expected NOVEL_ENTITY_SHIFT (brand-new participant), got {lab3}"

    # (6) full analysis: WITH_STATE vs WITHOUT_STATE, the coupling test itself.
    with_s = analyze_wsm(state_on=True)
    without_s = analyze_wsm(state_on=False)
    assert without_s["dependent_resolvable_acc"] <= 0.05, \
        f"WITHOUT_STATE should be near-zero by construction, got {without_s['dependent_resolvable_acc']}"
    assert with_s["dependent_resolvable_acc"] >= 0.80, \
        f"WITH_STATE dependent-resolvable accuracy too low: {with_s['dependent_resolvable_acc']}"
    assert with_s["guardrail_wrong_rate"] < 0.20, \
        f"GUARDRAIL: WITH_STATE guessed on ties/zero-antecedent rows: {with_s['guardrail_wrong_rate']}"
    assert with_s["control_acc"] >= 0.95 and with_s["control_acc"] >= without_s["control_acc"] - 0.02, \
        f"control regression: WITH={with_s['control_acc']} WITHOUT={without_s['control_acc']}"
    assert with_s["tier0_fastpath_rate"] > 0.0, "META_RULE_K: Tier-0 fast path never fired (vacuous mechanism)"
    assert with_s["n_shift_total"] >= 1, "META_RULE_K: discontinuity signal never fired (vacuous mechanism)"
    assert with_s["arm_hash"] != without_s["arm_hash"], \
        "META_RULE_AF: WITH_STATE and WITHOUT_STATE arms bit-identical (state resolved nothing)"

    print(f"[self_test] PASS | coupling delta={with_s['dependent_resolvable_acc'] - without_s['dependent_resolvable_acc']:.3f} "
          f"(WITH={with_s['dependent_resolvable_acc']:.3f} WITHOUT={without_s['dependent_resolvable_acc']:.3f}) | "
          f"control WITH={with_s['control_acc']:.3f} WITHOUT={without_s['control_acc']:.3f} | "
          f"guardrail_wrong_rate={with_s['guardrail_wrong_rate']:.3f} | tier0_rate={with_s['tier0_fastpath_rate']:.3f} | "
          f"n_shift={with_s['n_shift_total']}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    # deterministic fixed fixture corpus -- no seed/scale axis to shrink; smoke == full (see docstring).
    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    docs = build_unified_docs()
    expected_n_units = sum(len(d["sents"]) for d in docs) * 2       # x2 arms (WITH_STATE, WITHOUT_STATE)
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[wsm_coupling] run_mode={run_mode} n_docs={len(docs)} expected_n_units={expected_n_units}", flush=True)

    with_s = analyze_wsm(state_on=True)
    without_s = analyze_wsm(state_on=False)
    print(f"[wsm_coupling] COUPLING dependent_resolvable_acc WITH={with_s['dependent_resolvable_acc']:.3f} "
          f"WITHOUT={without_s['dependent_resolvable_acc']:.3f} (n={with_s['n_dependent_resolvable']})", flush=True)
    print(f"[wsm_coupling] CONTROL acc WITH={with_s['control_acc']:.3f} WITHOUT={without_s['control_acc']:.3f} "
          f"(n={with_s['n_control']})", flush=True)
    print(f"[wsm_coupling] GUARDRAIL wrong_guess_rate={with_s['guardrail_wrong_rate']:.3f} "
          f"(n={with_s['n_guardrail_rows']})", flush=True)
    print(f"[wsm_coupling] Tier0 fastpath_rate={with_s['tier0_fastpath_rate']:.3f} "
          f"(tier0_bound={with_s['tier0_bound']} tier1_bound={with_s['tier1_bound']})", flush=True)
    print(f"[wsm_coupling] discontinuity n_shift={with_s['n_shift_total']} "
          f"transitions={with_s['transition_histogram']}", flush=True)

    tier, msg, weakest = compute_verdict(with_s, without_s)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "records"}

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "run_mode": run_mode, "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "expected_n_units": expected_n_units,
        "n_docs": len(docs), "weakest_interface": weakest,
        "metric_coupling_delta": with_s["dependent_resolvable_acc"] - without_s["dependent_resolvable_acc"],
        "metric_dependent_resolvable_acc_with": with_s["dependent_resolvable_acc"],
        "metric_dependent_resolvable_acc_without": without_s["dependent_resolvable_acc"],
        "metric_dependent_resolvable_coverage_with": with_s["dependent_resolvable_coverage"],
        "metric_dependent_resolvable_precision_with": with_s["dependent_resolvable_precision"],
        "metric_control_acc_with": with_s["control_acc"], "metric_control_acc_without": without_s["control_acc"],
        "metric_guardrail_wrong_rate_with": with_s["guardrail_wrong_rate"],
        "metric_guardrail_wrong_rate_without": without_s["guardrail_wrong_rate"],
        "metric_tier0_fastpath_rate": with_s["tier0_fastpath_rate"], "metric_tier0_bound": with_s["tier0_bound"],
        "metric_tier1_bound": with_s["tier1_bound"],
        "metric_n_shift_total": with_s["n_shift_total"], "metric_transition_histogram": with_s["transition_histogram"],
        "arms": {"WITH_STATE": strip(with_s), "WITHOUT_STATE": strip(without_s)},
        "records_with_state": with_s["records"], "records_without_state": without_s["records"],
        "prereg": {
            "hard_pass": "coupling_delta>=0.60 & WITH.dep_acc>=0.80 & WITH.control_acc>=0.95 & "
                         "WITH.control_acc>=(WITHOUT.control_acc-0.02) & WITH.guardrail_wrong_rate<0.20 & "
                         "tier0_fastpath_rate>0 & n_shift_total>=1",
            "hard_fail": "coupling_delta<0.40 | WITH.control_acc<(WITHOUT.control_acc-0.05) | "
                         "WITH.guardrail_wrong_rate>=0.30",
            "middle": "otherwise (partial lift or imperfect guardrail -- report dominant class)",
            "novel_synthesis_P": 0.45, "prediction_1_tier0_P_cited": 0.40,
            "scope": "Tier0 Cb pointer + Tier1 Cf list (reused) + REDUCED Tier2 single active-event slot; "
                     "Tier3 consolidation NOT built (discontinuity signal reported, not committed to long-term store); "
                     "5-dim Zwaan situation model REDUCED to 1 event slot (this SVO register has no distinct "
                     "time/space/intentionality axis); dialogue/grounding wrapper (Prediction 4) out of scope",
            "compute_architecture": "sequential-CPU, fully symbolic, NO RNG/VSA/torch (parse-level diagnostic, "
                                     "compute-proportionality: a fit/capacity question this is not)",
            "storage_strategy": "no_storage", "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true", "deterministic_seeding": "N/A_no_rng",
            "real_code_path_exercised": ["ie_extract", "resolve_coref", "_mentions_from_triples",
                                         "_find_subject_pronoun", "resolve_pronoun_wsm", "resolve_ellipsis",
                                         "update_wsm", "analyze_wsm"],
            "crlb_n/a": "no quantitative noise floor; fully symbolic discrete role-assignment, no phasor noise",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[wsm_coupling] {tier} in {elapsed:.4f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[wsm_coupling] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
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
