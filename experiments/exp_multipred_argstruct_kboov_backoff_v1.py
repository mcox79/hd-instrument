"""OOV BACK-OFF / CLASS-SMOOTHING REVIVAL FIX -- does the scaled selectional-knowledge table's isolated
2AFC win (29479, +0.199) transfer to the integrated multi-predicate reader once the COVERAGE artifact
29484 diagnosed is fixed?

THE PRECISELY-DIAGNOSED BOUND THIS CELL TESTS THE FIX FOR (29483/29484, CITED, this cell's own reuse):
  29483 (`exp_multipred_argstruct_agentfix_kbgate_v3.py`) wired the 29479 scaled 579-pair
  verb|noun selectional table into the parser-integrated reader's patient-disambiguation gate:
  when a predicate has >=2 locally-assigned PATIENT candidates, argmax-`sel(verb_lemma, noun)` keeps
  only one, with OOV pairs scored -1.0 (strictly below ANY rated pair). LANDED HARD_FAIL
  (`data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json`): F1(V3_KNOWLEDGE_SCRAMBLE)=0.5738
  == F1(V3_INTEGRATED)=0.5738, kept_hash IDENTICAL between the real-table arm and the table-scrambled
  must-fail control -- scrambling the table's VALUES changed ZERO kept-tuple decisions. DIAGNOSIS: at
  real multi-patient competitions, the 579-pair table rarely covers BOTH competing candidates
  (154 verbs x ~3.75 nouns/verb average density); when one candidate is OOV, `-1.0 < any rated value`
  means the COVERED candidate wins by construction regardless of ITS OWN rating (a candidate rated 0.05
  still beats an OOV rival scored -1.0) -- the plausibility CONTENT of the table never gets to decide,
  only its COVERAGE does. The +0.199 isolated-2AFC win (29479, both-candidates-in-table BY THE 2AFC
  TASK'S OWN CONSTRUCTION) cannot manifest through this coverage bottleneck.

THE FIX (brain-faithful; CITED, Clark & Weir 2002 class-based smoothing -- humans facing an unfamiliar
  verb-noun combination back off to CATEGORY-level plausibility, e.g. WordNet-supersense-conditioned
  generality, rather than having no opinion at all): replace OOV=-1.0 with a THREE-TIER graded back-off
  estimate, computed FROM THE SAME 579-pair table (so a scramble of the table propagates through every
  tier, keeping the must-fail control meaningful at every tier, not just the item-specific one):
    TIER 0 (item-specific): exact verb|noun rating, if present -- unchanged from 29483.
    TIER 1 (verb + WordNet noun-supersense class average): mean of all OTHER rated nouns for this SAME
      verb sharing the OOV noun's first-synset `lexname()` (e.g. `noun.plant`, `noun.food`,
      `noun.artifact`) -- the Clark & Weir class-conditional estimate.
    TIER 2 (verb average): mean of ALL rated nouns for this verb, regardless of noun class (used when
      the verb has no rated noun sharing the OOV noun's supersense, or the noun has no WordNet noun
      synset at all).
    TIER 3 (global mean): mean of ALL 579 ratings (used only when the verb itself has zero table
      coverage -- rare given 154/154 verbs have >=1 rated noun in the table).
  Every competition is now a GRADED comparison (never a hard -1.0 vs covered-value comparison); an OOV
  candidate can win a competition against an item-specific-covered rival IF the class/verb-level
  evidence genuinely favors it -- something -1.0 could never do BY CONSTRUCTION. Concrete case this
  cell's self-test proves live (not hypothesized): under 'eat', branches is item-specific-rated 0.15
  (low) while nut is OOV; nut's WordNet supersense (noun.plant) matches acorn/acorns (0.90, 0.90) and
  firs (0.02) under 'eat' -> TIER 1 estimate = mean(0.90,0.90,0.02) = 0.6067, which BEATS branches'
  0.15 -- the old OOV=-1.0 scheme could never let 'nut' win this competition; the back-off scheme does,
  driven by genuine class-level content.

ARMS (9; the 6 arms are BYTE-IDENTICAL reproductions of 29483's own code+numbers via direct import,
  reused as the fixed reference; the 3 new arms are this cell's ONLY novel measurement):
  BASELINE, V2_FRAMES_29478, V3_PARSEFIX_ONLY, V3_INTEGRATED, V3_ARCSCRAMBLE, V3_KNOWLEDGE_SCRAMBLE
    = 29483's OWN `run_all_arms_v3` output, called directly (same W/clf/code/table) -- guarantees
    byte-identical numbers to the cited landed metrics (F1(V3_INTEGRATED)=0.5738,
    F1(V3_KNOWLEDGE_SCRAMBLE)=0.5738, kept_hash-identical, the coverage bound this cell fixes).
  V4_INTEGRATED_BACKOFF   = SAME assignment fix + SAME learned gate (29483's, reused byte-identical via
    its returned `evidence`) + the NEW three-tier back-off sel_fn, in place of 29483's OOV=-1.0 sel_fn.
    THE HEADLINE ARM. ONE VARIABLE = the OOV back-off (assignment mechanism, gate, clf, parser: ALL
    byte-identical reuse of 29483).
  V4_ARCSCRAMBLE_BACKOFF  = back-off sel_fn on deterministically SCRAMBLED decoded head arcs (reuses
    29483's own `M.scramble_heads`). MUST-FAIL CONTROL (a): real parse structure vs scrambled structure.
  V4_KNOWLEDGE_SCRAMBLE_BACKOFF = back-off sel_fn computed FROM a table whose VALUES are permuted across
    (verb,noun) keys (fixed seed, sorted-keys ordering, same scramble mechanics as 29483's own
    `build_scrambled_sel_fn`) -- because ALL THREE back-off tiers are recomputed from this SAME
    scrambled table, a scramble now perturbs the item tier AND the class/verb-average tiers together.
    THE LOAD-BEARING MUST-FAIL CONTROL (b): does knowledge CONTENT now drive picks, or does the
    argmax-among-graded-candidates mechanism itself still never let content decide?

FRESH INSTRUMENTATION THIS CELL ADDS (29483 did not track per-competition picks, only the aggregate
  kept-tuple hash; this cell adds `clause_predicate_pass_v4` / `build_parse_arm_v4`, byte-identical to
  29483's `clause_predicate_pass_v3` / `build_parse_arm_v3` PLUS an optional competition_log so the
  0-flip finding can be measured directly, not inferred from an identical aggregate hash):
    n_competitions_total = count of predicates with >=2 locally-assigned PATIENT candidates (the ONLY
      place any sel_fn, old or new, can act).
    n_flipped_OLD_SCHEME = pick differs between 29483's OWN raw sel_fn (item-specific-or-OOV=-1.0) and
      29483's OWN scrambled-table sel_fn, measured FRESH on this run via the SAME competition-tracking
      wrapper (an apples-to-apples re-derivation of the "0/N" finding, not an assumed prior number).
    n_flipped_NEW_SCHEME = pick differs between the back-off sel_fn (real table) and the back-off sel_fn
      (scrambled table) -- THE decisive measurement: does back-off make the must-fail control fire?
    tier_usage_counts = how many OOV resolutions in V4_INTEGRATED_BACKOFF landed at TIER1/TIER2/TIER3.
    n_tied_competitions = competitions where ALL competing candidates get the identical backed-off score
      (content cannot discriminate them -- the BRAIN-CHECK diagnostic for "is class-level back-off too
      COARSE," per atom 29471's supersense-ties-same-class-rivals caveat).

PRE-REGISTERED BANDS (set BEFORE this run; grounded on 29483's own landed MEASURED numbers
  F1(V3_INTEGRATED)=0.5738, F1(V3_PARSEFIX_ONLY)=0.4651, F1(V3_KNOWLEDGE_SCRAMBLE)=0.5738 -- a tight
  decisive band, NOT the calibration-probe +/-50% widening reserved for anchor-free theoretical probes):
  HARD_PASS_BACKOFF_TRANSFERS_KNOWLEDGE: ALL of --
    (a) n_flipped_NEW_SCHEME >= 1 (control NOW flips at least one pick)
    (b) n_flipped_NEW_SCHEME / n_competitions_total >= 0.05 (not a lone coincidental flip)
    (c) F1(V4_KNOWLEDGE_SCRAMBLE_BACKOFF) <= F1(V4_INTEGRATED_BACKOFF) - 0.02 (scramble hurts F1)
    (d) F1(V4_INTEGRATED_BACKOFF) > 0.5738 + 0.01 (lifts past the pre-backoff structural number)
    (e) F1(V4_INTEGRATED_BACKOFF) > 0.4651 (still beats the no-knowledge parsefix-only number)
    (f) F1(V4_ARCSCRAMBLE_BACKOFF) <= F1(V4_INTEGRATED_BACKOFF) - 0.05 (structural control still fires)
  HARD_FAIL_COVERAGE_ARTIFACT_CONFIRMED_EVEN_WITH_BACKOFF: ANY of --
    (a) n_flipped_NEW_SCHEME == 0 (scramble STILL cannot flip a single pick -- a deeper mechanics issue
        than mere coverage: the argmax structure itself, not just OOV=-1.0, blocks content from deciding)
    (b) F1(V4_KNOWLEDGE_SCRAMBLE_BACKOFF) >= F1(V4_INTEGRATED_BACKOFF) - 0.01 (control fails to fail at
        the aggregate F1 level even if some picks flip)
    (c) F1(V4_INTEGRATED_BACKOFF) <= 0.5738 (back-off adds NOTHING beyond the pre-backoff number; the
        isolated-2AFC win does not transfer AT ALL even with the revival fix)
  MIDDLE_BAND: otherwise (e.g. partial pick-flipping but too small/noisy, or F1 improves without
    clearing the strict margin) -- report which condition(s) failed + the tier_usage / n_tied diagnostic
    (coarse-class-caveat check per atom 29471) + whether item-level table DENSITY (not class back-off)
    is the deeper remaining lever.

FAIRNESS: same reader/gold/split/parser-training-budget/clf/gate as 29483 and 29478 (FULL_SLICE =
  L04/L05/L07/L08/L09/L10/L12; SMOKE_SLICE = L04/L05); gold = data/gold_mcguffey_lccp_argstruct_v1.json
  (independent, single-annotator, never read while authoring this fix). ONE primary variable = the
  OOV back-off (replaces 29483's OOV=-1.0); assignment mechanism / learned gate / role-assignment clf /
  parser training / subcat-gate ALL byte-identical reuse of 29483's own code (imported, not
  re-transcribed). Learning-curve axis NOT reproduced this cell (out of scope per compute-
  proportionality -- the decisive question is single-slice knowledge-transfer via back-off, not sample-
  efficiency; 29483's own landed learning curve stands for that axis).

BRAIN-CHECK: Clark & Weir (2002), "Class-Based Probability Estimation Using a Semantic Hierarchy" --
  humans and corpus-based selectional-preference models alike back off to a WordNet-hypernym/class-level
  estimate when item-specific evidence is sparse, rather than treating unseen combinations as having NO
  plausibility signal at all (which is what -1.0 does). Atom 29471 (banked, CITED) already flagged that
  supersense-level classes can be too COARSE to discriminate same-class rivals (e.g. acorn 0.90 and firs
  0.02 are BOTH noun.plant under 'eat' -- a wide within-class spread); this cell's tier_usage/n_tied
  instrumentation measures that coarseness directly rather than assuming it away.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reuses 29483's own arc-eager parser
  training pass + per-clause greedy decode + AveragedPerceptron role classification + O(candidates) dict
  lookups (assignment walk + 3-tier back-off table lookup, itself O(1) after one-time O(|table|)
  precomputation of the class/verb aggregates); NO matmul/storage/GPU-batchable primitive. Storage:
  no_storage. Runtime invariant: glass-box (a from-scratch-trained transition parser + a curated dict +
  a corpus-observed admissibility table + a build-time-authored knowledge dict + nltk WordNet lexname
  lookups, all LOCAL), NO LLM/network/autograd at inference. Determinism: OMP/MKL/OPENBLAS=1, fixed int
  seeds, numpy default_rng, sorted(keys); no hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion.
  NO push / NO remote-persist / NO queue_add (routing task contract: inline-local FULL, pause-state
  ACTIVE, not banked -- skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell; N/A items stated
  explicitly per META_RULE_AC):
  - arms_differ_verified at smoke gate (hash test over all 9 arms' kept-tuple sets; V4_INTEGRATED_BACKOFF
    vs V4_KNOWLEDGE_SCRAMBLE_BACKOFF exempted at SMOKE scale ONLY per the same small-sample rationale
    29483 itself used for its own V3_INTEGRATED vs V3_KNOWLEDGE_SCRAMBLE pair -- the FULL run's aggregate
    F1 gap + n_flipped_NEW_SCHEME are the load-bearing must-fail checks, not a hash-identity assertion)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASELINE) < 0.95)
  - discriminator fires at smoke: back-off sel_fn changes >=1 kept-tuple decision vs the no-backoff
    V3_INTEGRATED arm at SMOKE_SLICE scale (WARN not FAIL if small-sample -- same discipline 29483 used)
  - scaffold-free witness (class-tier back-off flips a real pick): 'eat' + branches (item-specific=0.15)
    vs nut (OOV, TIER1 class-average via noun.plant supersense = 0.6067 from acorn/acorns/firs) --
    OLD scheme picks 'branches' (0.15 > -1.0 by construction); NEW back-off scheme picks 'nut' (0.6067 >
    0.15), driven by genuine class-level content, not mere coverage.
  - deterministic seeding (fixed int SEED; sorted(dict.keys()) for scramble permutations; numpy
    default_rng; no hash()-seeded RNG)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (29483/29479/29471) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A
    multi-seed for the arms (deterministic given fixed SEED; parser training is single-seed by design, a
    scope/wall-time tradeoff already stated+accepted in 29483, not hidden here); N/A cardinality-sweep
    (no swept axis besides the fixed 9-arm comparison -- EXPECTED_N_ARMS=9 gate used instead)
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

ANCHOR_NAME = "multipred_argstruct_kboov_backoff_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from nltk.corpus import wordnet as wn                                                  # noqa: E402

# Reuse 29483's OWN code VERBATIM (parser training, decode, assignment fix, learned gate, scoring,
# 6-arm reproduction). 29483 is importable (module scope guarded by `if __name__ == "__main__"`).
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3                # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M                 # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L      # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC                  # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2           # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260725

KNOWLEDGE_TABLE_PATH = V3.KNOWLEDGE_TABLE_PATH

# ---- Pre-registered bands (set BEFORE this run; see docstring) ------------------------
HP_MIN_FLIPS = 1
HP_MIN_FLIP_FRACTION = 0.05
HP_SCRAMBLE_F1_MARGIN = 0.02
HP_F1_OVER_STRUCTURAL_MIN = 0.01
HP_ARCSCRAMBLE_MARGIN = 0.05
HF_SCRAMBLE_F1_MARGIN = 0.01
CITED_29483_F1_INTEGRATED = 0.5738          # V3_INTEGRATED, MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
CITED_29483_F1_PARSEFIX_ONLY = 0.4651       # MEASURED@ same file: arms.V3_PARSEFIX_ONLY.f1
CITED_29483_F1_KNOWLEDGE_SCRAMBLE = 0.5738  # MEASURED@ same file: arms.V3_KNOWLEDGE_SCRAMBLE.f1 (== INTEGRATED; the bound)
EXPECTED_N_ARMS = 9
BASELINE_BAND = (0.05, 0.95)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# Three-tier back-off selectional score (Clark & Weir 2002 class-smoothing). Item-specific ->
# verb+WordNet-noun-supersense class average -> verb average -> global mean. Never returns None.
# =======================================================================================
_NOUN_SUPERSENSE_CACHE = {}


def noun_supersense(noun_low):
    if noun_low not in _NOUN_SUPERSENSE_CACHE:
        syns = wn.synsets(noun_low, pos="n")
        _NOUN_SUPERSENSE_CACHE[noun_low] = syns[0].lexname() if syns else None
    return _NOUN_SUPERSENSE_CACHE[noun_low]


def build_backoff_sel_fn(ratings_table, tier_counter=None):
    """sel(v_lemma, noun_low) -> float, ALWAYS graded (never None). tier_counter, if given, is a dict
    this function increments in place: {'tier0_item':N, 'tier1_class':N, 'tier2_verbavg':N,
    'tier3_global':N}."""
    verb_noun_rating = defaultdict(dict)
    for k, v in ratings_table.items():
        vb, nn = k.split("|", 1)
        verb_noun_rating[vb][nn] = float(v)

    verb_class_ratings = defaultdict(lambda: defaultdict(list))
    for vb, nd in verb_noun_rating.items():
        for nn, val in nd.items():
            ss = noun_supersense(nn)
            if ss is not None:
                verb_class_ratings[vb][ss].append(val)

    verb_avg = {vb: sum(nd.values()) / len(nd) for vb, nd in verb_noun_rating.items()}
    global_mean = sum(float(v) for v in ratings_table.values()) / len(ratings_table)

    def sel(v_lemma, noun_low):
        if v_lemma in verb_noun_rating and noun_low in verb_noun_rating[v_lemma]:
            if tier_counter is not None:
                tier_counter["tier0_item"] += 1
            return verb_noun_rating[v_lemma][noun_low]
        ss = noun_supersense(noun_low)
        if ss is not None and v_lemma in verb_class_ratings and ss in verb_class_ratings[v_lemma]:
            vals = verb_class_ratings[v_lemma][ss]
            if tier_counter is not None:
                tier_counter["tier1_class"] += 1
            return sum(vals) / len(vals)
        if v_lemma in verb_avg:
            if tier_counter is not None:
                tier_counter["tier2_verbavg"] += 1
            return verb_avg[v_lemma]
        if tier_counter is not None:
            tier_counter["tier3_global"] += 1
        return global_mean
    return sel


def build_scrambled_backoff_sel_fn(ratings_table, seed):
    """MUST-FAIL CONTROL (b), back-off variant: permute the table's VALUES across (verb,noun) keys
    (deterministic seeded permutation, sorted-keys ordering -- same scramble mechanics as 29483's own
    build_scrambled_sel_fn), THEN recompute ALL THREE back-off tiers from the SCRAMBLED table -- a
    scramble now perturbs the item AND class/verb-average tiers together."""
    keys = sorted(ratings_table.keys())
    vals = [ratings_table[k] for k in keys]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(vals))
    scrambled = {keys[i]: float(vals[perm[i]]) for i in range(len(keys))}
    return build_backoff_sel_fn(scrambled)


# =======================================================================================
# clause_predicate_pass_v4 / build_parse_arm_v4 -- byte-identical to 29483's own
# clause_predicate_pass_v3 / build_parse_arm_v3 PLUS an optional competition_log (29483 never tracked
# per-competition picks, only the aggregate kept-tuple hash).
# =======================================================================================
def clause_predicate_pass_v4(tagged, heads, clf, gate_fn, carried_agent_in, assign_fn, sel_fn=None,
                              competition_log=None):
    lows = [t[1] for t in tagged]
    verb_positions = M.content_verb_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    by_pred = assign_fn(tagged, heads, verb_positions)
    out = []
    carried_agent = carried_agent_in
    evidence = {}
    for v0 in verb_positions:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        vl = L.lemma_verb(low)
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True
        kept_patients = patients_local
        if sel_fn is not None and len(patients_local) >= 2:
            def _score(i):
                s = sel_fn(vl, tagged[i][1])
                return -1.0 if s is None else s
            scores = [_score(i) for i in patients_local]
            best_i = max(patients_local, key=lambda i: (_score(i), -i))
            kept_patients = [best_i]
            if competition_log is not None:
                competition_log.append(dict(
                    vlemma=vl,
                    candidates=tuple(tagged[i][1] for i in patients_local),
                    scores=tuple(round(s, 6) for s in scores),
                    picked=tagged[best_i][1],
                    all_tied=(len(set(round(s, 6) for s in scores)) == 1),
                ))
        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                for pi in kept_patients:
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return out, carried_agent, evidence


def build_parse_arm_v4(slice_lessons, W, clf, gate_fn, assign_fn, sel_fn=None, scramble_arcs=False,
                        scramble_seed=None, track_competitions=False):
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    out = {}
    competition_log = [] if track_competitions else None
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        for clause_i, clause_text in enumerate(ORC.split_sentences(raw)):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            if scramble_arcs:
                heads = M.scramble_heads(heads, (scramble_seed or SEED) + M.hash_stable(sid) + clause_i)
            clause_tups, carried_agent, _ev = clause_predicate_pass_v4(
                tagged, heads, clf, gate_fn, carried_agent, assign_fn, sel_fn, competition_log)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
        out[sid] = tups
    if track_competitions:
        return order, sent_text, out, competition_log
    return order, sent_text, out


# =======================================================================================
# Run all 9 arms: 6 byte-identical reproductions of 29483's own run_all_arms_v3 (also gives us
# `evidence` to rebuild the SAME learned gate without re-running the keepall pass), + 3 new back-off
# arms + 2 competition-tracked OLD-scheme reproductions (for the fresh apples-to-apples flip count).
# =======================================================================================
def run_all_arms_v4(slice_lessons, W, clf, ratings_table):
    res_v3 = V3.run_all_arms_v3(slice_lessons, W, clf, ratings_table)
    gold = res_v3["gold"]
    learned_gate_fixed = M.build_learned_admissibility(res_v3["evidence"])

    old_sel_fn = V3.build_sel_fn(ratings_table)
    old_scrambled_sel_fn = V3.build_scrambled_sel_fn(ratings_table, SEED + 13)  # SAME seed as 29483

    tier_counter = defaultdict(int)
    backoff_sel_fn = build_backoff_sel_fn(ratings_table, tier_counter=tier_counter)
    scrambled_backoff_sel_fn = build_scrambled_backoff_sel_fn(ratings_table, SEED + 13)

    assign_fn = V3.assign_candidates_to_predicates_fixed

    # Fresh apples-to-apples OLD-scheme flip count (29483 never instrumented per-competition picks).
    _, _, old_real_kept, comps_old_real = build_parse_arm_v4(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, sel_fn=old_sel_fn, track_competitions=True)
    _, _, old_scr_kept, comps_old_scr = build_parse_arm_v4(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, sel_fn=old_scrambled_sel_fn,
        track_competitions=True)

    # NEW back-off arms.
    _, _, backoff_kept, comps_new_real = build_parse_arm_v4(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, sel_fn=backoff_sel_fn,
        track_competitions=True)
    _, _, arcscramble_backoff_kept = build_parse_arm_v4(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, sel_fn=backoff_sel_fn,
        scramble_arcs=True, scramble_seed=SEED + 7)
    _, _, knowscramble_backoff_kept, comps_new_scr = build_parse_arm_v4(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, sel_fn=scrambled_backoff_sel_fn,
        track_competitions=True)

    n_comp = len(comps_old_real)
    assert len(comps_old_scr) == n_comp and len(comps_new_real) == n_comp and len(comps_new_scr) == n_comp, \
        (f"HARD_FAIL_CARDINALITY_BREACH: competition-log lengths diverge across sel_fn variants "
         f"(old_real={n_comp} old_scr={len(comps_old_scr)} new_real={len(comps_new_real)} "
         f"new_scr={len(comps_new_scr)}) -- the competition SET must be sel_fn-independent (it depends "
         f"only on clf-assigned PATIENT roles), a divergent length is an instrumentation bug")

    n_flipped_old = sum(1 for a, b in zip(comps_old_real, comps_old_scr) if a["picked"] != b["picked"])
    n_flipped_new = sum(1 for a, b in zip(comps_new_real, comps_new_scr) if a["picked"] != b["picked"])
    n_tied_new_real = sum(1 for c in comps_new_real if c["all_tied"])

    all_arms_kept = dict(res_v3["arms"])
    all_arms_kept["V4_INTEGRATED_BACKOFF"] = backoff_kept
    all_arms_kept["V4_ARCSCRAMBLE_BACKOFF"] = arcscramble_backoff_kept
    all_arms_kept["V4_KNOWLEDGE_SCRAMBLE_BACKOFF"] = knowscramble_backoff_kept

    scored = dict(res_v3["scored"])
    for name in ("V4_INTEGRATED_BACKOFF", "V4_ARCSCRAMBLE_BACKOFF", "V4_KNOWLEDGE_SCRAMBLE_BACKOFF"):
        kept = all_arms_kept[name]
        rc, miss, npos, _misses = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                             kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    return dict(order=res_v3["order"], sent_text=res_v3["sent_text"], gold=gold, arms=all_arms_kept,
                scored=scored, n_competitions_total=n_comp, n_flipped_old_scheme=n_flipped_old,
                n_flipped_new_scheme=n_flipped_new,
                flip_fraction_old=round(n_flipped_old / n_comp, 4) if n_comp else None,
                flip_fraction_new=round(n_flipped_new / n_comp, 4) if n_comp else None,
                n_tied_competitions_backoff=n_tied_new_real, tier_usage=dict(tier_counter),
                comps_new_real_sample=comps_new_real[:30], comps_new_scr_sample=comps_new_scr[:30])


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
    print("[self-test] loading SMOKE_SLICE reader + gold + knowledge table ...")
    order, sent_text, reader_svo = L.load_slice_and_reader(SMOKE_SLICE)
    gold, meta = L.load_gold(SMOKE_SLICE)
    assert len(order) >= 20, f"expected >=20 sentences in SMOKE_SLICE, got {len(order)}"
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    assert len(ratings_table) > 100, f"knowledge table suspiciously small: {len(ratings_table)}"

    # WordNet availability preflight (F.1-style real-code-path check: exercise the ACTUAL nltk corpus
    # call the FULL run uses, not a mocked/synthetic branch).
    ss = noun_supersense("acorn")
    assert ss == "noun.plant", f"WordNet preflight FAIL: noun_supersense('acorn') = {ss!r}, expected 'noun.plant'"
    print(f"[self-test] WordNet real-code-path preflight OK: noun_supersense('acorn')={ss}")

    print("[self-test] training arc-eager parser (smoke budget, reused 29483 code) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    res = run_all_arms_v4(SMOKE_SLICE, W, clf, ratings_table)
    assert len(res["scored"]) == EXPECTED_N_ARMS, \
        f"HARD_FAIL_CARDINALITY_BREACH: expected {EXPECTED_N_ARMS} arms, got {len(res['scored'])}: {list(res['scored'])}"
    print(f"[self-test] {EXPECTED_N_ARMS}-arm pipeline ran on SMOKE_SLICE: "
          f"{ {k: v['score']['f1'] for k, v in res['scored'].items()} }")
    print(f"[self-test] SMOKE_SLICE flip counts: old_scheme={res['n_flipped_old_scheme']}/"
          f"{res['n_competitions_total']} new_scheme(backoff)={res['n_flipped_new_scheme']}/"
          f"{res['n_competitions_total']} tier_usage={res['tier_usage']} n_tied={res['n_tied_competitions_backoff']}")

    prec_base = res["scored"]["BASELINE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"BASELINE precision {prec_base} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(BASELINE)={prec_base} in {BASELINE_BAND}")

    # arms_differ_verified (META_RULE_AF). All STRUCTURAL arms (differing mechanism/table axis) must
    # differ. V4_INTEGRATED_BACKOFF vs V4_KNOWLEDGE_SCRAMBLE_BACKOFF exempted at SMOKE scale ONLY, same
    # small-sample rationale 29483 itself used for its own analogous pair.
    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    # Both real-vs-scrambled-table pairs (the 29483-reused pair AND this cell's new backoff pair) are
    # EXEMPTED from the strict must-differ assertion at SMOKE scale ONLY -- 29483 itself already
    # exempted its own V3_INTEGRATED/V3_KNOWLEDGE_SCRAMBLE pair at self-test scale for the identical
    # small-sample reason (too few multi-patient competitions for a table scramble to bite by chance).
    exempt_pairs = [("V3_INTEGRATED", "V3_KNOWLEDGE_SCRAMBLE"),
                    ("V4_INTEGRATED_BACKOFF", "V4_KNOWLEDGE_SCRAMBLE_BACKOFF")]
    exempt_names = {n for pair in exempt_pairs for n in pair}
    structural = {k: v for k, v in hashes.items() if k not in exempt_names}
    assert len(set(structural.values())) == len(structural), \
        f"META_RULE_AF VIOLATION: structural arm hashes collide: {structural}"
    arms_differ_exempted = []
    for pair in exempt_pairs:
        if hashes.get(pair[0]) == hashes.get(pair[1]):
            arms_differ_exempted.append(pair)
            print(f"[self-test] WARN: {pair} kept_hash collide at SMOKE_SLICE scale (small-sample; "
                  f"the FULL run's n_flipped_*_SCHEME + aggregate F1 gap are the load-bearing must-fail "
                  f"checks, not this hash)")
    print(f"[self-test] arms_differ_verified (structural, n={len(structural)}): OK; exempted: {arms_differ_exempted}")

    # discriminator fires at smoke: back-off changes >=1 kept-tuple decision vs no-backoff V3_INTEGRATED.
    if hashes["V4_INTEGRATED_BACKOFF"] == hashes["V3_INTEGRATED"]:
        print("[self-test] WARN: back-off had ZERO measurable effect vs no-backoff at SMOKE_SLICE scale "
              "(small-sample; re-verified via the scaffold-free witness below + the FULL run has far "
              "more OOV competition instances)")
    else:
        print("[self-test] back-off changes >=1 kept-tuple decision vs no-backoff at smoke scale (kept_hash differs)")

    # scaffold-free witness: 'eat' + branches (item-specific=0.15, LOW) vs nut (OOV; TIER1 class-average
    # via noun.plant supersense, from acorn/acorns/firs under 'eat') -- OLD scheme picks 'branches'
    # (0.15 > -1.0 BY CONSTRUCTION); NEW back-off scheme picks 'nut' (class-avg > 0.15), driven by
    # genuine content, not coverage.
    assert ratings_table.get("eat|branches") is not None, "witness precondition: eat|branches must be in table"
    assert ratings_table.get("eat|nut") is None, "witness precondition: eat|nut must be OOV (not in table)"
    old_sel_fn_w = V3.build_sel_fn(ratings_table)
    backoff_sel_fn_w = build_backoff_sel_fn(ratings_table)
    old_branches = old_sel_fn_w("eat", "branches")
    old_nut = old_sel_fn_w("eat", "nut")
    assert old_nut is None, f"witness precondition: raw sel_fn('eat','nut') should be OOV/None, got {old_nut}"
    old_score_nut = -1.0  # the OLD clause_predicate_pass_v3 scoring convention (None -> -1.0)
    old_picked = "branches" if old_branches >= old_score_nut else "nut"
    assert old_picked == "branches", \
        f"WITNESS PRECONDITION FAIL: OLD scheme should pick 'branches' by coverage-construction " \
        f"(branches={old_branches} vs nut(OOV)={old_score_nut}), got {old_picked}"
    back_branches = backoff_sel_fn_w("eat", "branches")
    back_nut = backoff_sel_fn_w("eat", "nut")
    assert abs(back_branches - old_branches) < 1e-9, \
        f"back-off item-specific tier should reproduce the raw table value for 'branches': {back_branches} vs {old_branches}"
    assert back_nut > back_branches, \
        f"WITNESS FAIL: back-off TIER1 class-average for 'nut' ({back_nut}) should exceed item-specific " \
        f"'branches' ({back_branches}) via the noun.plant class (acorn=0.9, acorns=0.9, firs=0.02)"
    new_picked = "nut" if back_nut > back_branches else "branches"
    print(f"[self-test] scaffold-free witness: 'eat' competition branches(item-specific={back_branches}) "
          f"vs nut(OOV, TIER1 class-avg={round(back_nut, 4)}) -- OLD scheme picks '{old_picked}' "
          f"(coverage-forced); NEW back-off scheme picks '{new_picked}' (content-driven)")
    assert new_picked == "nut" and old_picked == "branches", \
        "WITNESS FAIL: back-off did not flip the pick relative to the coverage-forced OLD scheme"
    print("[self-test] scaffold-free witness PASS: back-off flips a real competition via genuine "
          "class-level content, something OOV=-1.0 could never do by construction")

    # determinism: two runs over the same slice + same W produce identical hashes.
    res2 = run_all_arms_v4(SMOKE_SLICE, W, clf, ratings_table)
    assert res["scored"]["V4_INTEGRATED_BACKOFF"]["kept_hash"] == res2["scored"]["V4_INTEGRATED_BACKOFF"]["kept_hash"], \
        "non-deterministic V4_INTEGRATED_BACKOFF output across identical runs"
    assert res["n_flipped_new_scheme"] == res2["n_flipped_new_scheme"], \
        "non-deterministic flip count across identical runs"
    print("[self-test] deterministic (two runs produce identical kept-hash + flip count)")

    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=EXPECTED_N_ARMS)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    W, parser_info = M.train_dep_parser(run_mode)
    res = run_all_arms_v4(slice_lessons, W, clf, ratings_table)
    scored = res["scored"]

    f1_integrated_noback = scored["V3_INTEGRATED"]["score"]["f1"]
    f1_parsefix = scored["V3_PARSEFIX_ONLY"]["score"]["f1"]
    f1_backoff = scored["V4_INTEGRATED_BACKOFF"]["score"]["f1"]
    f1_arcscramble_backoff = scored["V4_ARCSCRAMBLE_BACKOFF"]["score"]["f1"]
    f1_knowscramble_backoff = scored["V4_KNOWLEDGE_SCRAMBLE_BACKOFF"]["score"]["f1"]

    n_flip_new = res["n_flipped_new_scheme"]
    n_flip_old = res["n_flipped_old_scheme"]
    n_comp = res["n_competitions_total"]
    flip_frac_new = res["flip_fraction_new"]

    hard_fail_reasons = []
    if n_flip_new == 0:
        hard_fail_reasons.append(f"n_flipped_new_scheme=0/{n_comp}: the knowledge-scramble control STILL "
                                  f"cannot flip a single pick even with graded back-off -- a deeper "
                                  f"mechanics issue than mere coverage")
    if f1_knowscramble_backoff >= f1_backoff - HF_SCRAMBLE_F1_MARGIN:
        hard_fail_reasons.append(f"F1(V4_KNOWLEDGE_SCRAMBLE_BACKOFF) {f1_knowscramble_backoff} >= "
                                  f"F1(V4_INTEGRATED_BACKOFF) {f1_backoff} - {HF_SCRAMBLE_F1_MARGIN} "
                                  f"(control fails to fail at the aggregate F1 level)")
    if f1_backoff <= CITED_29483_F1_INTEGRATED:
        hard_fail_reasons.append(f"F1(V4_INTEGRATED_BACKOFF) {f1_backoff} <= cited 29483 F1(V3_INTEGRATED) "
                                  f"{CITED_29483_F1_INTEGRATED} (back-off adds nothing beyond the pre-fix "
                                  f"number; the isolated-2AFC win does not transfer at all even with the "
                                  f"revival fix)")

    hard_pass_conditions = dict(
        control_now_flips=(n_flip_new >= HP_MIN_FLIPS),
        flip_fraction_meaningful=(flip_frac_new is not None and flip_frac_new >= HP_MIN_FLIP_FRACTION),
        control_scramble_hurts_f1=(f1_knowscramble_backoff <= f1_backoff - HP_SCRAMBLE_F1_MARGIN),
        f1_beats_structural_baseline=(f1_backoff > CITED_29483_F1_INTEGRATED + HP_F1_OVER_STRUCTURAL_MIN),
        f1_beats_no_knowledge=(f1_backoff > CITED_29483_F1_PARSEFIX_ONLY),
        control_arcscramble_fires=(f1_arcscramble_backoff <= f1_backoff - HP_ARCSCRAMBLE_MARGIN),
    )

    if hard_fail_reasons:
        verdict = "HARD_FAIL_COVERAGE_ARTIFACT_CONFIRMED_EVEN_WITH_BACKOFF"
        vmsg = ("HARD_FAIL: " + "; ".join(hard_fail_reasons) +
                f". F1 V3_PARSEFIX_ONLY(cited)={CITED_29483_F1_PARSEFIX_ONLY} "
                f"V3_INTEGRATED(cited,no-backoff)={CITED_29483_F1_INTEGRATED} "
                f"V4_INTEGRATED_BACKOFF={f1_backoff} V4_KNOWLEDGE_SCRAMBLE_BACKOFF={f1_knowscramble_backoff} "
                f"V4_ARCSCRAMBLE_BACKOFF={f1_arcscramble_backoff}. pick-flip count: OLD_SCHEME="
                f"{n_flip_old}/{n_comp} NEW_SCHEME(backoff)={n_flip_new}/{n_comp} (fraction={flip_frac_new}). "
                f"tier_usage={res['tier_usage']} n_tied_competitions={res['n_tied_competitions_backoff']}. "
                f"HONEST BOUND: even the OOV back-off/class-smoothing revival fix does not let the "
                f"isolated-2AFC knowledge win (29479, +0.199) transfer to this reader's decision points.")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_BACKOFF_TRANSFERS_KNOWLEDGE"
        vmsg = (f"HARD_PASS: back-off revives the knowledge-scramble control: NEW_SCHEME flips "
                f"{n_flip_new}/{n_comp} picks (fraction={flip_frac_new}) vs OLD_SCHEME's {n_flip_old}/{n_comp}. "
                f"F1 V3_INTEGRATED(cited,no-backoff)={CITED_29483_F1_INTEGRATED} -> "
                f"V4_INTEGRATED_BACKOFF={f1_backoff} (lifts past structural baseline); "
                f"V4_KNOWLEDGE_SCRAMBLE_BACKOFF={f1_knowscramble_backoff} (control now hurts F1, as required); "
                f"V4_ARCSCRAMBLE_BACKOFF={f1_arcscramble_backoff} (structural control still fires). "
                f"tier_usage={res['tier_usage']}. The +0.199 isolated-2AFC win PARTIALLY TRANSFERS once "
                f"the coverage artifact is fixed via class-level back-off.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL_BACKOFF_TRANSFER"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND: no HARD_FAIL trigger fired but not all HARD_PASS conditions held "
                f"(failing: {failing}). pick-flip count: OLD_SCHEME={n_flip_old}/{n_comp} "
                f"NEW_SCHEME(backoff)={n_flip_new}/{n_comp} (fraction={flip_frac_new}). F1 "
                f"V3_INTEGRATED(cited,no-backoff)={CITED_29483_F1_INTEGRATED} -> "
                f"V4_INTEGRATED_BACKOFF={f1_backoff}; V4_KNOWLEDGE_SCRAMBLE_BACKOFF={f1_knowscramble_backoff}; "
                f"V4_ARCSCRAMBLE_BACKOFF={f1_arcscramble_backoff}. tier_usage={res['tier_usage']} "
                f"n_tied_competitions={res['n_tied_competitions_backoff']} (BRAIN-CHECK: high n_tied "
                f"relative to n_comp suggests class-level back-off may be too COARSE per atom 29471 -- "
                f"item-level table density, not class smoothing, would be the deeper remaining lever). "
                f"Genuine but partial signal; localize which condition failed before escalating scope.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: F1 parsefix_only(cited)={CITED_29483_F1_PARSEFIX_ONLY} "
                 f"integrated_no_backoff(cited)={CITED_29483_F1_INTEGRATED} integrated_backoff={f1_backoff} "
                 f"knowledge_scramble_backoff={f1_knowscramble_backoff} arcscramble_backoff={f1_arcscramble_backoff} "
                 f"| pick-flips: old_scheme={n_flip_old}/{n_comp} new_scheme={n_flip_new}/{n_comp} "
                 f"(fraction={flip_frac_new}) | tier_usage={res['tier_usage']} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["order"]),
        one_variable="OOV back-off (build_backoff_sel_fn: item -> verb+WordNet-noun-supersense class "
                     "average -> verb average -> global mean) REPLACES 29483's OOV=-1.0 raw sel_fn; "
                     "assignment mechanism / learned gate / role-assignment clf / parser training ALL "
                     "byte-identical reuse of 29483's own code (imported, not re-transcribed)",
        bands=dict(HP_MIN_FLIPS=HP_MIN_FLIPS, HP_MIN_FLIP_FRACTION=HP_MIN_FLIP_FRACTION,
                   HP_SCRAMBLE_F1_MARGIN=HP_SCRAMBLE_F1_MARGIN,
                   HP_F1_OVER_STRUCTURAL_MIN=HP_F1_OVER_STRUCTURAL_MIN,
                   HP_ARCSCRAMBLE_MARGIN=HP_ARCSCRAMBLE_MARGIN, HF_SCRAMBLE_F1_MARGIN=HF_SCRAMBLE_F1_MARGIN,
                   CITED_29483_F1_INTEGRATED=CITED_29483_F1_INTEGRATED,
                   CITED_29483_F1_PARSEFIX_ONLY=CITED_29483_F1_PARSEFIX_ONLY,
                   CITED_29483_F1_KNOWLEDGE_SCRAMBLE=CITED_29483_F1_KNOWLEDGE_SCRAMBLE),
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"], n_gold_pos=v["n_gold_pos"],
                         precision=v["score"]["precision"], recall=v["score"]["recall"], f1=v["score"]["f1"],
                         n_pred=v["n_pred"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        hard_pass_conditions=hard_pass_conditions,
        hard_fail_reasons=hard_fail_reasons,
        n_competitions_total=n_comp, n_flipped_old_scheme=n_flip_old, n_flipped_new_scheme=n_flip_new,
        flip_fraction_old=res["flip_fraction_old"], flip_fraction_new=flip_frac_new,
        n_tied_competitions_backoff=res["n_tied_competitions_backoff"], tier_usage=res["tier_usage"],
        comps_new_real_sample=res["comps_new_real_sample"], comps_new_scr_sample=res["comps_new_scr_sample"],
        parser_info=parser_info,
        cited_29483=dict(source="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json",
                         verdict="HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND",
                         f1_integrated=CITED_29483_F1_INTEGRATED, f1_parsefix_only=CITED_29483_F1_PARSEFIX_ONLY,
                         f1_knowledge_scramble=CITED_29483_F1_KNOWLEDGE_SCRAMBLE,
                         note="kept_hash(V3_INTEGRATED) == kept_hash(V3_KNOWLEDGE_SCRAMBLE) -- the coverage "
                              "bound this cell's back-off fix targets"),
        cited_29479=dict(source="data/exp_pivot_scaled_seed_knowledge_table_v1/metrics.json",
                         verdict="HARD_PASS_SCALED_KNOWLEDGE_HELPS_AT_COVERAGE",
                         isolated_2afc_lift=0.199),
        cited_29471=dict(note="WordNet-supersense classes can be too COARSE to discriminate same-class "
                              "rivals (ties); this cell's n_tied_competitions_backoff + tier_usage fields "
                              "measure that coarseness directly on this run rather than assuming it"),
        scope_caveat=("Parser trained on UD-EWT via a from-scratch dynamic-oracle arc-eager model at a "
                      "FOREGROUND-bounded training budget, byte-identical reuse of 29483's own training "
                      "code; out-of-domain transfer to 19th-c. McGuffey narrative prose is the SAME "
                      "untested transfer 29478/29483 already flagged. The knowledge table (29479) is "
                      "LLM-self-built (residual leakage-adjacent risk per that cell's own scope caveat); "
                      "an independent-KB replication is the flagged rigor follow-up. WordNet lexname is "
                      "the FIRST synset only (no WSD) -- a deterministic, glass-box simplification, not "
                      "sense-disambiguated. CLAIM-VET-pending; strategic read = HYPOTHESIS pending "
                      "landed-VET."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("flip counts: old=", n_flip_old, "new=", n_flip_new, "of", n_comp, "competitions")
    print("tier_usage:", res["tier_usage"])
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
