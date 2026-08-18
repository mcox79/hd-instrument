"""ROLES chain-grade DRIVE-4: EMISSION-PRESERVING RE-LABEL who-did-what reader lever, built on the drive-3
harness (exp_reader_role_valency_supplied_lexicon_v3, imported + reused, NOT edited).

WHY DRIVE-3 FAILED (MEASURED@data/exp_reader_role_valency_supplied_lexicon_v3/metrics.json): the blunt
  post_core[0]->PATIENT override FORCE-EMITS a patient on every admissible post-verbal core. n_pred inflated
  144 (BASE) -> 156 (VALENCY_GATED / CANONICAL_BLUNT) = +12 mostly-FP, driving subcat_fp 35->41 and
  spurious_verb_fp 33->36 and F1 0.5738 -> 0.5391 (HARD_FAIL, below BASE). That is the WRONG FP category.
  THE KEY OBSERVATION (MEASURED@ same, arm ROLE_ORACLE): the +0.0391 ceiling is reached at n_pred=148 (~=BASE
  144) with subcat_fp/spurious_verb_fp = BASE. ROLE_ORACLE RE-LABELS an existing routed candidate's role; it
  does NOT force-EMIT new tuples. So the brain-faithful mechanism is an EMISSION-PRESERVING RE-LABEL, not a
  force-emit. (The supplied-valency lexicon is a REAL secondary lever -- drive-3 P2 scramble degraded -- but it
  sat on the wrong force-emit substrate.)

THE MECHANISM THIS CELL BUILDS (role_relabel_reassign; glass-box; the only word-identity input is the SUPPLIED
  ditransitive-valency lexicon; NO selectional/animacy/patient-fit knowledge). Three named drive-3 autopsy gaps:

  (1) NP-HEAD SELECTION. The out-of-domain parser splits a single NP into fragments, so drive-3's post_core[0]
      grabbed "herbert's castle"->"herbert's" (possessive JJ/NNP) and "plenty of boys"->"plenty" (quantifier).
      FIX: target the HEAD NOUN of the FIRST post-verbal noun-CHUNK = the rightmost NN* in the chunk, skipping
      possessive-'s / determiners. Chunk boundary = a DETERMINER (DT/PDT), a verb (VB*/MD), a wh-word
      (WP/WP$/WDT/WRB), or punctuation between two candidates (a fresh determiner starts a new NP:
      "the child [a] servant" breaks; "plenty [of] boys" and "castles down" and "herbert's castle" do not).
      Recovers rub/castle + meet/boys. For a DITRANSITIVE verb the THEME is the head of the LAST post-verbal
      chunk (recipient = the earlier chunk).

  (2) EMISSION-PRESERVING RE-LABEL (the crux). Operate ONLY on the EXISTING routed candidate set; do NOT add
      tuples. FLIP the post-verbal NP-head to PATIENT ONLY WHEN the perceptron already assigned it a real
      argument role (AGENT/RECIPIENT -- the mislabel signature: 3/5 gold patients were labeled RECIPIENT while a
      pre-verbal subject was present) AND a pre-verbal subject exists; OR keep it if the perceptron already
      labeled it PATIENT (dedupe siblings onto the head); OR move a perceptron-PATIENT from a non-head modifier
      (possessive/quantifier) onto the head. If the head is NONE and no sibling carries a patient, DO NOTHING
      (respect the perceptron's "no argument here" -- this is what prevents the drive-3 force-emit inflation).
      n_pred MUST stay ~=144 (inflation = reverted to force-emit).

  (3) LEXICON PRECISION. Keep a TIGHT supplied ditransitive set (core change-of-possession + transfer-of-message
      datives) and DROP the VerbNet benefactive/edge datives -- notably `find`, which drive-3 mis-marked
      ditransitive and so picked the appositive "joe" (in "a boy whose name was joe") instead of the gold patient
      "boy". Dropping `find` makes it transitive -> head of first chunk = "boy". Recovers find/boy.

TARGET: recover the 5 non-OSV ROLE_ORACLE-headroom items by emission-preserving RE-LABEL, approaching the
  +0.0391 ceiling, WITHOUT subcat/spurious inflation (n_pred ~=BASE):
    L04_12 rub/castle (NP-head skip possessive), L07_09 meet/boys (NP-head skip quantifier),
    L05_22 see/child (RECIPIENT->PATIENT flip, subject present), L05_16 knock/castles (dedupe onto head),
    L10_11 find/boy (drop find from ditransitive -> transitive first-chunk head).
  L04_01 build/blockhouse is fronted-OSV (blockhouse is PRE-verbal) = drive-1's FRONTED arm, OUT of scope here.

ARMS (seven; one parameterized clause pass isolates every lever):
  BASE            = AUDIT REAL arm (== V3_INTEGRATED). P1 FAIRNESS ANCHOR (reproduces F1=0.5738 byte-identical).
  RELABEL_GATED   = NP-head + emission-preserving gate + TIGHT ditransitive lexicon (HEADLINE).
  RELABEL_FORCEEMIT = same NP-head + same lexicon, but emission-preserving gate OFF (force NP-head->PATIENT
                    unconditionally). ABLATION (relabel-gate vs force-emit): isolates the emission-preserving
                    gate holding NP-head + lexicon constant. Expected: recovers the 5 too BUT inflates n_pred/FP.
  RELABEL_LEFTMOST = same emission-preserving gate + same lexicon, but NP-head OFF (transitive head=post_core[0],
                    ditransitive theme=post_core[-1], drive-3 style). ABLATION (NP-head vs leftmost-core).
  RELABEL_NOLEX   = NP-head + emission-preserving gate, ditransitive lexicon OFF (every verb transitive).
                    ABLATION (with vs without lexicon): isolates the supplied ditransitive fact.
  RELABEL_SCRAMBLE = NP-head + emission-preserving gate, ditransitive lexicon SCRAMBLED (same #ditransitive
                    corpus verbs, RANDOM membership, fixed seed). P2 FAIRNESS CONTROL.
  ROLE_ORACLE     = AUDIT oracle_role arm on the SAME parser weights = the +0.0391 CEILING (F1=0.6129).

MEASURED (per arm, SAME independent LCCP gold / split as audit/V3/drive-1/2/3): F1, precision, recall,
  recall_ceiling, n_pred (EMISSION-PRESERVING CHECK), subcat/within_frame/spurious FP; n_recovered/n_regressed
  vs BASE; gap_closed_frac = (F1(RELABEL_GATED)-F1(BASE))/(F1(ROLE_ORACLE)-F1(BASE)); the three ablation deltas;
  the scramble-degrade delta; per-item outcome on the 5 in-scope headroom items; deep per-item autopsy.

PRE-REGISTERED BANDS (set BEFORE the RELABEL_GATED full run; grounded on MEASURED anchors f1_BASE=0.5738,
  f1_ROLE_ORACLE=0.6129, gap=0.0391, base_n_pred=144):
  HARD_PASS_EMISSION_PRESERVING_RELABEL requires ALL of:
    (P1)  abs(F1(BASE)-0.5738) <= 0.02                                   # base reproduces V3 byte-identical-ish
    (a)   F1(RELABEL_GATED) >= F1(BASE) + 0.0196                         # closes >= 50% of the 0.0391 gap
    (b)   recall(RELABEL_GATED) >= recall(BASE) - 0.005                  # no recall regression
    (c)   precision(RELABEL_GATED) >= precision(BASE)                    # no precision regression
    (EP)  n_pred(RELABEL_GATED) <= base_n_pred + 6                       # EMISSION-PRESERVING (ROLE_ORACLE=+4)
    (ABL1) F1(RELABEL_GATED) >= F1(RELABEL_FORCEEMIT) + 0.01             # emission-preserving beats force-emit
    (ABL2) F1(RELABEL_GATED) >= F1(RELABEL_LEFTMOST) + 0.01              # NP-head beats leftmost-core
    (P2)  F1(RELABEL_GATED) >= F1(RELABEL_SCRAMBLE) + 0.01 AND F1(RELABEL_SCRAMBLE) <= F1(BASE) + 0.005
                                                                        # correct ditransitive membership earns keep
  HARD_FAIL_RELABEL_NULL if ANY of:
    F1(RELABEL_GATED) <= F1(BASE)                                        # no lift (mechanism null)
    recall(RELABEL_GATED) < recall(BASE) - 0.02                         # regressed recall
    n_pred(RELABEL_GATED) > base_n_pred + 12                            # force-emit inflation (reverted to drive-3)
    abs(F1(BASE)-0.5738) > 0.02                                         # P1 broke
  MIDDLE_BAND_PARTIAL_RELABEL otherwise (genuine but partial gap-closure / a control did not separate; no
  HARD_FAIL) -- the honest 'drove toward the ceiling, name the residual wall from the autopsy' outcome.

FAIRNESS: SAME reader / gold (data/gold_mcguffey_lccp_argstruct_v1.json) / split (FULL_SLICE, SMOKE_SLICE) as
  audit/V3/drive-1/2/3. BASE and ROLE_ORACLE are byte-identical reuse of AUDIT.build_arm_audit; the shared
  admissibility gate is built ONCE (pass-through-gate evidence pass, exactly as drive-1/2/3) and held identical;
  the pre-existing >=2-patient selectional argmax is held CONSTANT (NOT my variable). ONE variable = the
  emission-preserving NP-head re-label + the SUPPLIED ditransitive-valency lexicon. No selectional/animacy/
  patient-fit knowledge. No cross-base compare. PLUGGABLE for the consolidated reader (role_relabel_reassign
  is a pure function of roles + tagged + gate + supplied-lexicon).

COMPUTE ARCHITECTURE: class (b) sequential-CPU -- ONE arc-eager parser train (~68s FULL) + ms/clause decode +
  per-predicate perceptron + O(cand) position/chunk lookups + O(1) lexicon lookups. NO matmul/GPU/storage. 7
  scored arms + 1 evidence pass + 1 corpus-verb pass + 1 autopsy trace pass. Est wall < 6min FULL. Determinism:
  OMP/MKL/OPENBLAS=1, fixed int SEED, random.Random(SEED) for the scramble, sorted() iteration. Storage:
  no_storage. Runtime invariant: glass-box, NO LLM/network/autograd. LOCAL-ONLY foreground-to-completion, NOT
  banked (skunkworks VETs separately), NO queue_add.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash over the 7 arms; small-sample WARN permitted)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASE) < 0.95)
  - P1 reproduction self-test: BASE via AUDIT REAL == WO override-disabled (hash-identical)
  - discriminator fires at smoke: RELABEL_GATED recovers >=1 gold item BASE misses; 3 of the 5 headroom items
    (rub/castle L04_12, knock/castles L05_16, see/child L05_22) are IN SMOKE_SLICE L04/L05
  - EMISSION-PRESERVING self-test: n_pred(RELABEL_GATED) <= n_pred(RELABEL_FORCEEMIT) at smoke
  - scaffold-free witnesses: NP-head skip-possessive; NP-head skip-quantifier ('of'); DT chunk boundary
    (child vs servant); transitive RECIPIENT->PATIENT flip with subject; emission-preserving NO-OP on NONE head;
    ditransitive theme=last-chunk head + recipient protection; force-emit differs
  - deterministic seeding (fixed int SEED; random.Random(SEED) scramble; sorted() where order matters)
  - progress_logging: line_buffered_stdout (sys.stdout.reconfigure) -- FULL est < 6min < 30min so not gated
  - all numbers tagged MEASURED@ / CITED@ in this docstring
  - N/A: KGStore (no KG); CRLB (discrete count/precision, no HD noise floor); multi-seed (single-seed parser
    budget, accepted per M/V3/audit/drive-1/2/3); GPU-batching (sequential parse, no matmul)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import random
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "reader_role_relabel_emission_preserving_v4"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3             # noqa: E402
from experiments import exp_reader_component_oracle_ablation_audit_v1 as AUDIT       # noqa: E402
from experiments import exp_reader_role_wordorder_valency_v1 as WO                   # noqa: E402  (drive-1; reuse only)
from experiments import exp_reader_role_valency_supplied_lexicon_v3 as SRC3          # noqa: E402  (drive-3; reuse only)

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260727

# ---- Pre-registered anchors + bands (set BEFORE the RELABEL_GATED full run) --------------------
CITED_AUDIT_F1_REAL = 0.5738         # MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/metrics.json:f1.REAL
CITED_AUDIT_F1_ROLE_ORACLE = 0.6129  # MEASURED@ same:f1.ROLE_ORACLE
CITED_ROLE_GAP = 0.0391              # MEASURED@ same:uplift.ROLE_ORACLE
CITED_BASE_N_PRED = 144              # MEASURED@data/exp_reader_role_valency_supplied_lexicon_v3/metrics.json:arms.BASE.n_pred
CITED_ROLEORA_N_PRED = 148          # MEASURED@ same:arms.ROLE_ORACLE.n_pred
P1_REPRO_TOL = 0.02
HP_GAP_CLOSE_FRAC = 0.50
HP_F1_MIN_LIFT = round(CITED_ROLE_GAP * HP_GAP_CLOSE_FRAC, 4)   # 0.0196
HP_RECALL_TOL = 0.005
HP_ABLATION_MARGIN = 0.01
HP_SCRAMBLE_MARGIN = 0.01
HP_EMISSION_PRESERVE_MARGIN = 6      # n_pred(GATED) <= base + 6 (ROLE_ORACLE is +4)
HF_RECALL_REGRESS = 0.02
HF_EMISSION_INFLATE = 12             # n_pred(GATED) > base + 12 = reverted to drive-3 force-emit
BASELINE_BAND = (0.05, 0.95)
EXPECTED_N_ARMS = 7
HEADLINE = "RELABEL_GATED"
# The 5 in-scope ROLE_ORACLE-headroom items this cell targets (L04_01 build/blockhouse is fronted-OSV, out).
IN_SCOPE_HEADROOM = [("L04_12", "rub", "castle"), ("L05_16", "knock", "castles"),
                     ("L05_22", "see", "child"), ("L07_09", "meet", "boys"), ("L10_11", "find", "boy")]

# ================================================================================================
# TIGHT SUPPLIED DITRANSITIVE-VALENCY LEXICON (drive-3 lexicon-precision fix).
# Core change-of-possession + transfer-of-message datives ONLY. Every member is in the drive-3
# VerbNet role-filtered set (SRC3.DITRANSITIVE_SET) -> provenance CITED@VerbNet 3.x (Recipient|Beneficiary +
# Theme|Topic double-object role-filter). The drive-3 benefactive/edge datives (notably `find`, plus book/call/
# catch/choose/dance/draw/...) are DROPPED: they mis-fire on out-of-domain McGuffey clauses.
# ================================================================================================
DITRANSITIVE_TIGHT = frozenset({
    # core change-of-possession (giving / transfer of goods)
    "give", "hand", "pass", "sell", "lend", "loan", "offer", "owe", "bring", "send",
    "award", "grant", "bequeath", "rent", "promise",
    # transfer-of-message (communication datives)
    "tell", "show", "teach", "ask", "read", "write", "quote", "wire", "cable", "fax", "assign",
})
# The 5 transitive-headroom verbs + the drive-3 edge-dative that broke find/boy, all OUT by design.
DROPPED_EDGE_DATIVES_CHECK = ("find", "book", "call", "catch", "choose", "dance", "draw", "pull", "reach")

# Chunk-boundary POS classes. A DETERMINER / possessive-pronoun-determiner / verb / wh-word / punctuation /
# PP-preposition (any IN except the genitive/quantifier 'of') between two candidates starts a new NP -> break.
_BREAKER_POS = frozenset({"DT", "PDT", "PRP$", "WP", "WP$", "WDT", "WRB", "MD",
                          ".", ",", ":", "``", "''", "HYPH", "-LRB-", "-RRB-", "(", ")"})
_BREAKER_WORDS = frozenset({"-", "--", ";", "dash"})


def _is_breaker_token(surface, low, pos):
    if pos in _BREAKER_POS:
        return True
    if pos.startswith("VB"):
        return True
    if pos == "IN" and low != "of":     # 'with his hands', 'for his boy' = PP adjunct -> new phrase; keep 'of'
        return True
    if low in _BREAKER_WORDS or surface in _BREAKER_WORDS:
        return True
    return False


def _is_possessive(surface, pos):
    return pos == "POS" or surface.lower().endswith("'s")


def split_post_chunks(post_core, tagged):
    """Group post-verbal candidate indices into NP chunks. A DETERMINER / verb / wh-word / punctuation lying
    strictly between two consecutive candidates starts a new NP chunk (a fresh determiner = a new NP)."""
    if not post_core:
        return []
    chunks = [[post_core[0]]]
    for a, b in zip(post_core, post_core[1:]):
        broke = any(_is_breaker_token(tagged[k][0], tagged[k][1], tagged[k][2]) for k in range(a + 1, b))
        # a candidate immediately followed by a finite verb is a clause SUBJECT ('copybook [Joe was reading]',
        # 'boy [whose name was joe]') -> it starts a new chunk, not part of the preceding object NP.
        if not broke and b + 1 < len(tagged) and tagged[b + 1][2].startswith("VB"):
            broke = True
        if broke:
            chunks.append([b])
        else:
            chunks[-1].append(b)
    return chunks


def _is_nominal(surface, pos):
    """A nominal head candidate: common/proper noun or a personal pronoun. Particles (RP), adverbs, possessive
    modifiers are NOT nominal heads."""
    if _is_possessive(surface, pos):
        return False
    return pos.startswith("NN") or pos == "PRP"


def np_head(chunk, tagged):
    """Head of an NP chunk = rightmost NN* (non-possessive); else rightmost personal pronoun; else rightmost
    non-possessive candidate; then rightmost candidate."""
    if not chunk:
        return None
    nouns = [i for i in chunk if tagged[i][2].startswith("NN") and not _is_possessive(tagged[i][0], tagged[i][2])]
    if nouns:
        return nouns[-1]
    prns = [i for i in chunk if tagged[i][2] == "PRP"]
    if prns:
        return prns[-1]
    nonposs = [i for i in chunk if not _is_possessive(tagged[i][0], tagged[i][2])]
    if nonposs:
        return nonposs[-1]
    return chunk[-1]


# ================================================================================================
# EMISSION-PRESERVING re-label. Mutates `roles` in place. Returns a trace dict for the autopsy.
#   use_np_head=False  -> leftmost-core ablation (transitive post_core[0]; ditransitive post_core[-1])
#   emission_preserving=False -> force-emit ablation (set the NP-head PATIENT unconditionally)
#   ditrans_fn -> supplied lexicon membership (None-of / scramble / disabled handled by the caller's fn)
# ================================================================================================
def role_relabel_reassign(roles, local_cand, tagged, v0, passive, gate_fn, ditrans_fn,
                          use_np_head=True, emission_preserving=True):
    tr = {"frame": None, "post_core": [], "pre_core": [], "chunks": [], "head": None,
          "recip": [], "applied": False, "acted": False, "reason": None}
    if passive:
        tr["frame"] = "passive_skip"
        return tr
    post_core = sorted(i for i in local_cand if i > v0 and ORC.prev_prep(tagged, i) is None)
    pre_core = sorted(i for i in local_cand if i < v0 and ORC.prev_prep(tagged, i) is None)
    tr["post_core"] = post_core
    tr["pre_core"] = pre_core
    if not post_core:
        tr["frame"] = "no_postverbal_core"
        return tr
    vl = L.lemma_verb(tagged[v0][1])
    if not gate_fn(vl):
        tr["frame"] = "gate_blocked"
        return tr

    # OBLIQUE-PP GUARD: a canonical direct object occupies the slot immediately after the verb with no
    # intervening preposition. If a non-'of' preposition sits between the verb and the FIRST post-verbal core,
    # that core is a PP-object (oblique) -- the verb is used without a direct object (intransitive/oblique:
    # 'lived with his father', 'walked in the paths', 'spoke to herbert'). Do NOT force a patient -> defer to
    # BASE (respect the perceptron). prev_prep only checks the immediate predecessor, so it misses 'with his X'.
    first_pc = post_core[0]
    if any(tagged[k][2] == "IN" and tagged[k][1] != "of" for k in range(v0 + 1, first_pc)):
        tr["frame"] = "oblique_pp_skip"
        return tr

    subject_present = len(pre_core) > 0
    is_ditrans = bool(ditrans_fn(vl))
    chunks = split_post_chunks(post_core, tagged)
    tr["chunks"] = chunks

    def _has_nominal(chunk):
        return any(_is_nominal(tagged[i][0], tagged[i][2]) for i in chunk)

    if is_ditrans:
        tr["frame"] = "ditransitive"
        # theme = head of the LAST nominal-bearing chunk (skip trailing particle/adverbial chunks)
        theme_chunk = next((c for c in reversed(chunks) if _has_nominal(c)), chunks[-1])
        recip_indices = [i for i in post_core if i not in theme_chunk]
        h = np_head(theme_chunk, tagged) if use_np_head else post_core[-1]
        head_chunk = theme_chunk
    else:
        tr["frame"] = "transitive"
        # object = head of the FIRST nominal-bearing chunk (skip leading particle chunks 'held [out] his hands')
        first_chunk = next((c for c in chunks if _has_nominal(c)), chunks[0])
        recip_indices = []
        h = np_head(first_chunk, tagged) if use_np_head else post_core[0]
        head_chunk = first_chunk
    tr["head"] = h
    tr["recip"] = recip_indices
    if h is None:
        tr["reason"] = "no_head"
        return tr

    h_role = roles.get(h)
    # Perceptron patients (BEFORE mutation) = what BASE would score/argmax over. The emission-preserving
    # discipline: DEFER to BASE's own selectional argmax whenever it has patients spanning >1 chunk (that is the
    # regime BASE handles well, e.g. ditransitive 'gives me an hour'); intervene ONLY on clear STRUCTURAL errors.
    perc_patients = [i for i in local_cand if roles.get(i) == "PATIENT"]
    chunk_perc_patients = [i for i in head_chunk if roles.get(i) == "PATIENT"]

    if emission_preserving:
        if len(perc_patients) == 0:
            # BASE emitted NO patient for this predicate: flip the direct-object-position head if the perceptron
            # mis-labelled it a routed argument (RECIPIENT/AGENT) and a pre-verbal subject licenses SVO.
            if h_role in ("AGENT", "RECIPIENT") and subject_present:
                roles[h] = "PATIENT"
                act = True
                tr["reason"] = "flip_missed_clause"
            else:
                act = False
                tr["reason"] = "no_op_no_argument"
        elif len(chunk_perc_patients) == len(perc_patients):
            # EVERY base patient is inside the head's single NP chunk (an over-split NP: 'herbert's|castle',
            # 'castles|down'). The head is THE object of that NP -> keep/collapse onto the head, dedupe siblings.
            if h_role != "PATIENT":
                roles[h] = "PATIENT"
                tr["reason"] = "collapse_split_np_to_head"
            else:
                tr["reason"] = "keep_head_dedupe"
            act = True
        elif len(perc_patients) == 1 and perc_patients[0] in head_chunk and perc_patients[0] != h:
            # BASE picked a non-head modifier (possessive/quantifier) of the head's NP -> move to the head noun.
            roles[h] = "PATIENT"
            act = True
            tr["reason"] = "move_modifier_to_head"
        elif is_ditrans and len(perc_patients) == 1 and perc_patients[0] in recip_indices:
            # DITRANSITIVE recipient protection: BASE mis-stole the recipient as the patient; move to the theme
            # head (supplied ditransitive-valency fact: recipient is not the patient). 'give the boy the books'.
            roles[h] = "PATIENT"
            act = True
            tr["reason"] = "ditrans_protect_recipient_move_to_theme"
        elif (h_role in ("AGENT", "RECIPIENT") and subject_present and h not in perc_patients
              and all(p > h for p in perc_patients)):
            # the head is a mis-labelled argument in direct-object position and every BASE patient is a LATER
            # appositive/adjunct (after the head) -> the head is the true object ('found a boy whose name was joe'
            # -> boy, not the appositive 'joe'). Flip the head; the demote loop drops the trailing appositives.
            roles[h] = "PATIENT"
            act = True
            tr["reason"] = "flip_head_over_trailing_appositive"
        else:
            # BASE has patients spanning multiple chunks -> its selectional argmax owns this; DO NOT override.
            act = False
            tr["reason"] = "defer_to_base_argmax"
    else:
        roles[h] = "PATIENT"
        act = True
        tr["reason"] = "force_emit_head_unconditional"

    if act:
        # enforce single object = the head: demote every OTHER post-verbal patient in this clause
        # (transitive: appositive/adjunct; ditransitive: recipient protection).
        for i in post_core:
            if i != h and roles.get(i) == "PATIENT":
                roles[i] = "NONE"
        # recipient protection is subsumed by the demote above (recip_indices are post_core, != h).
        ag = pre_core[-1] if pre_core else None
        if ag is not None and ag != h and roles.get(ag) != "PATIENT":
            roles[ag] = "AGENT"
        tr["applied"] = True
    tr["acted"] = act
    return tr


# ================================================================================================
# One clause pass. Mirrors AUDIT.clause_predicate_pass_audit's REAL (all-oracle-False) path plus the single
# emission-preserving re-label. trace_sink: optional dict populated when sid in trace_sids (autopsy).
# ================================================================================================
def clause_predicate_pass_relabel(sid, tagged, heads, clf, gate_fn, carried_agent_in, sel_fn,
                                  ditrans_fn, use_np_head, emission_preserving,
                                  trace_sink=None, trace_sids=None):
    predicates = M.content_verb_indices(tagged)
    candidates = ORC.candidate_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    route = AUDIT.real_route(tagged, heads, predicates, candidates, False)

    pred_1based = set(p + 1 for p in predicates)
    by_pred = defaultdict(list)
    for c0 in candidates:
        c1 = c0 + 1
        if c1 in pred_1based:
            continue
        target = route.get(c0)
        if target is not None:
            by_pred[target].append(c0)

    tracing = (trace_sink is not None and trace_sids is not None and sid in trace_sids)
    lows = [t[1] for t in tagged]
    out = []
    carried_agent = carried_agent_in
    evidence = {}
    for v0 in predicates:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        vl = L.lemma_verb(low)
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)
        perceptron_roles = dict(roles) if tracing else None

        tr = role_relabel_reassign(roles, local_cand, tagged, v0, passive, gate_fn, ditrans_fn,
                                   use_np_head=use_np_head, emission_preserving=emission_preserving)

        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True
        kept_patients = patients_local
        if sel_fn is not None and len(patients_local) >= 2:
            def _score(i):
                s = sel_fn(vl, tagged[i][1])
                return -1.0 if s is None else s
            best_i = max(patients_local, key=lambda i: (_score(i), -i))
            kept_patients = [best_i]
        emitted = None
        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                emitted = []
                for pi in kept_patients:
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
                    emitted.append(tagged[pi][1])
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]

        if tracing:
            def _w(idxs):
                return [tagged[i][1] for i in idxs]
            trace_sink.setdefault(sid, []).append(dict(
                sid=sid, verb=vl, verb_low=low, verb_idx=v0, passive=passive,
                frame=tr["frame"], reason=tr["reason"], acted=tr["acted"], gate_admits=bool(gate_fn(vl)),
                is_ditransitive=bool(ditrans_fn(vl)),
                local_cand=_w(local_cand), post_core=_w(tr["post_core"]), pre_core=_w(tr["pre_core"]),
                chunks=[_w(c) for c in tr["chunks"]],
                head=(tagged[tr["head"]][1] if tr["head"] is not None else None),
                perceptron_roles={tagged[i][1]: perceptron_roles[i] for i in local_cand},
                final_roles={tagged[i][1]: roles[i] for i in local_cand},
                resolved_agent=resolved_agent,
                kept_patients=[tagged[i][1] for i in kept_patients],
                emitted_patients=emitted))
    return out, carried_agent, evidence


def build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, ditrans_fn,
                      use_np_head=True, emission_preserving=True, trace_sink=None, trace_sids=None):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    out = {}
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            clause_tups, carried_agent, _ = clause_predicate_pass_relabel(
                sid, tagged, heads, clf, gate_fn, carried_agent, sel_fn, ditrans_fn,
                use_np_head, emission_preserving, trace_sink=trace_sink, trace_sids=trace_sids)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
        out[sid] = tups
    return order, out


# ================================================================================================
# Corpus verb vocabulary (fair scramble) + lexicon fns.
# ================================================================================================
def collect_corpus_verbs(slice_lessons):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    vocab = set()
    for sid in order:
        for clause_text in ORC.split_sentences(sent_text[sid]):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            for v0 in M.content_verb_indices(tagged):
                vocab.add(L.lemma_verb(tagged[v0][1]))
    return vocab


def build_scramble_fn(vocab, seed):
    """Fair P2 scramble: mark the SAME NUMBER of corpus verbs ditransitive as the real TIGHT lexicon does, but
    choose RANDOM (wrong) members. Deterministic (random.Random(seed); sorted vocab)."""
    v = sorted(vocab)
    real_ditrans = [w for w in v if w in DITRANSITIVE_TIGHT]
    n_d = len(real_ditrans)
    rng = random.Random(seed)
    shuffled = list(v)
    rng.shuffle(shuffled)
    fake_ditrans = set(shuffled[:n_d])
    info = dict(n_ditrans_marked=n_d, real_ditrans_in_corpus=sorted(real_ditrans),
                fake_ditrans=sorted(fake_ditrans))
    return (lambda w: w in fake_ditrans), info


def real_ditrans_fn(vl):
    return vl in DITRANSITIVE_TIGHT


def no_ditrans_fn(vl):
    return False


# ================================================================================================
# Deep per-item autopsy of the in-scope headroom set (KEEP-DIGGING deliverable).
# ================================================================================================
def autopsy_headroom(slice_lessons, W, clf, gate_fn, sel_fn, roleora_recovered, head_recovered):
    trace_sids = set(sid for (sid, v, p) in roleora_recovered)
    trace_sink = {}
    build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, real_ditrans_fn,
                      use_np_head=True, emission_preserving=True,
                      trace_sink=trace_sink, trace_sids=trace_sids)
    head_set = set((sid, v, p) for (sid, v, p) in head_recovered)
    report = []
    for (sid, gverb, gpat) in roleora_recovered:
        recovered = (sid, gverb, gpat) in head_set
        preds = trace_sink.get(sid, [])
        matches = [pr for pr in preds if pr["verb"] == gverb]
        item = dict(sid=sid, gold_verb=gverb, gold_patient=gpat, recovered_by_relabel_gated=recovered)
        if not matches:
            item["diagnosis"] = ("NO_PREDICATE_TRACE: RELABEL_GATED produced no predicate with lemma "
                                 f"{gverb!r} in {sid} -> upstream (parser routing / predicate detection / clause "
                                 "segmentation) never presented this verb. Not a role-assignment gap.")
            item["predicate_traces"] = []
            report.append(item)
            continue
        pdiag = []
        for pr in matches:
            gpat_in_local = gpat in pr["local_cand"]
            gpat_in_post = gpat in pr["post_core"]
            perc_role = pr["perceptron_roles"].get(gpat)
            fin_role = pr["final_roles"].get(gpat)
            emitted_ok = pr["emitted_patients"] is not None and gpat in (pr["emitted_patients"] or [])
            if not gpat_in_local:
                why = ("ROUTING_GAP: gold patient not among this predicate's routed local candidates "
                       f"(local={pr['local_cand']}) -> parser routing / mention gate dropped it.")
            elif not gpat_in_post:
                why = ("NON_POSTVERBAL: gold patient routed but NOT a post-verbal core "
                       f"(post_core={pr['post_core']}, pre_core={pr['pre_core']}) -> fronted/OSV/prep-governed.")
            elif pr["frame"] == "gate_blocked":
                why = "GATE_BLOCKED: learned admissibility gate says the verb admits no patient -> suppressed."
            elif pr["head"] != gpat:
                why = (f"NP_HEAD_MISPICK: chunk head ={pr['head']!r} but gold patient ={gpat!r} "
                       f"(chunks={pr['chunks']}, frame={pr['frame']}) -> chunk boundary / head-noun rule missed it "
                       "OR (ditransitive) gold patient is the recipient chunk.")
            elif not pr["acted"]:
                why = (f"EMISSION_PRESERVE_NOOP: head is gold patient but re-label did not act "
                       f"(reason={pr['reason']!r}, perceptron={perc_role!r}) -> perceptron said NONE with no "
                       "sibling patient (respected) OR no pre-verbal subject to license the flip.")
            elif fin_role != "PATIENT":
                why = (f"NOT_PATIENT_AFTER: head=gold patient, acted, but final role={fin_role!r} "
                       f"(perceptron={perc_role!r}, reason={pr['reason']!r}).")
            elif not emitted_ok:
                why = (f"POST_OVERRIDE_FILTER: gold patient set PATIENT (reason={pr['reason']!r}) but not emitted "
                       f"(kept_patients={pr['kept_patients']}, emitted={pr['emitted_patients']}) -> the >=2-patient "
                       "selectional argmax OR the emit gate dropped it.")
            else:
                why = (f"EMITTED_OK: frame={pr['frame']}, reason={pr['reason']!r}, perceptron={perc_role!r} -> "
                       f"PATIENT; emitted {pr['emitted_patients']} (recovered={recovered}).")
            pdiag.append(dict(frame=pr["frame"], reason=pr["reason"], is_ditransitive=pr["is_ditransitive"],
                              gate_admits=pr["gate_admits"], chunks=pr["chunks"], head=pr["head"],
                              post_core=pr["post_core"], pre_core=pr["pre_core"],
                              perceptron_role_of_gold_patient=perc_role, final_role_of_gold_patient=fin_role,
                              emitted_patients=pr["emitted_patients"], diagnosis=why))
        item["predicate_traces"] = pdiag
        report.append(item)
    return report


# ================================================================================================
# Full 7-arm experiment.
# ================================================================================================
def run_experiment(slice_lessons, W, clf, ratings_table, gold, with_autopsy=True):
    sel_fn = V3.build_sel_fn(ratings_table)
    # Gate built EXACTLY as drive-1/2/3: pass-through-gate evidence pass via WO.build_arm_wo -> byte-identical gate.
    _, _, evidence_real = WO.build_arm_wo(slice_lessons, W, clf, lambda v: True, None, override=None,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)

    vocab = collect_corpus_verbs(slice_lessons)
    scr_ditrans_fn, scramble_info = build_scramble_fn(vocab, SEED)

    arms = {}
    _, base_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                         oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, roleora_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                            oracle_enum=False, oracle_parse=False, oracle_role=True)
    _, gated_kept = build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, real_ditrans_fn,
                                      use_np_head=True, emission_preserving=True)
    _, force_kept = build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, real_ditrans_fn,
                                      use_np_head=True, emission_preserving=False)
    _, leftmost_kept = build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, real_ditrans_fn,
                                         use_np_head=False, emission_preserving=True)
    _, nolex_kept = build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, no_ditrans_fn,
                                      use_np_head=True, emission_preserving=True)
    _, scramble_kept = build_arm_relabel(slice_lessons, W, clf, gate_fn, sel_fn, scr_ditrans_fn,
                                         use_np_head=True, emission_preserving=True)

    arms["BASE"] = base_kept
    arms["RELABEL_GATED"] = gated_kept
    arms["RELABEL_FORCEEMIT"] = force_kept
    arms["RELABEL_LEFTMOST"] = leftmost_kept
    arms["RELABEL_NOLEX"] = nolex_kept
    arms["RELABEL_SCRAMBLE"] = scramble_kept
    arms["ROLE_ORACLE"] = roleora_kept

    scored = {}
    for name, kept in arms.items():
        rc, miss, npos, misses = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                            kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    base_covered = M.covered_set(arms["BASE"], gold)
    roleora_recovered = sorted(M.covered_set(arms["ROLE_ORACLE"], gold) - base_covered)
    head_recovered = sorted(M.covered_set(arms[HEADLINE], gold) - base_covered)
    head_regressed = sorted(base_covered - M.covered_set(arms[HEADLINE], gold))
    head_of_roleora = sorted(set(head_recovered) & set(roleora_recovered))
    force_recovered = sorted(M.covered_set(arms["RELABEL_FORCEEMIT"], gold) - base_covered)
    leftmost_recovered = sorted(M.covered_set(arms["RELABEL_LEFTMOST"], gold) - base_covered)
    nolex_recovered = sorted(M.covered_set(arms["RELABEL_NOLEX"], gold) - base_covered)
    scramble_recovered = sorted(M.covered_set(arms["RELABEL_SCRAMBLE"], gold) - base_covered)

    # per-item outcome on the 5 in-scope headroom items
    head_cov = M.covered_set(arms[HEADLINE], gold)
    in_scope_outcome = {f"{sid}:{v}/{p}": ((sid, v, p) in head_cov) for (sid, v, p) in IN_SCOPE_HEADROOM}

    autopsy = None
    if with_autopsy:
        autopsy = autopsy_headroom(slice_lessons, W, clf, gate_fn, sel_fn, roleora_recovered, head_recovered)

    return dict(arms=arms, scored=scored, scramble_info=scramble_info, vocab=sorted(vocab),
                roleora_recovered=roleora_recovered, head_recovered=head_recovered,
                head_regressed=head_regressed, head_of_roleora=head_of_roleora,
                force_recovered=force_recovered, leftmost_recovered=leftmost_recovered,
                nolex_recovered=nolex_recovered, scramble_recovered=scramble_recovered,
                in_scope_outcome=in_scope_outcome, autopsy=autopsy)


# ================================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# ================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


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


# ================================================================================================
# Self-test (design-gate; smoke scale = SMOKE_SLICE).
# ================================================================================================
def self_test():
    print("[self-test] auditing TIGHT ditransitive lexicon vs drive-3 VerbNet role-filter ...")
    for w in ("give", "show", "tell", "bring", "send", "hand", "offer", "teach"):
        assert w in DITRANSITIVE_TIGHT, f"lexicon: seed ditransitive {w!r} missing from DITRANSITIVE_TIGHT"
    for w in ("see", "rub", "meet", "knock", "build", "find"):
        assert w not in DITRANSITIVE_TIGHT, f"lexicon: transitive/edge {w!r} wrongly in DITRANSITIVE_TIGHT"
    # provenance: every TIGHT member is in the drive-3 VerbNet-role-filtered set (subset relation).
    drift = sorted(DITRANSITIVE_TIGHT - SRC3.DITRANSITIVE_SET)
    assert not drift, f"lexicon: TIGHT set not a subset of drive-3 VerbNet role-filter; extra {drift}"
    print(f"[self-test] lexicon: TIGHT ({len(DITRANSITIVE_TIGHT)}) subset of VerbNet role-filter "
          f"({len(SRC3.DITRANSITIVE_SET)}); find + 5 headroom verbs excluded")

    # ---- scaffold-free NP-head / chunk witnesses (pure, no parser) ----
    def _tag(rows):
        return [(s, s.lower(), p) for (s, p) in rows]
    # (W1) skip-possessive: "herbert's castle" post_core -> head=castle
    tg = _tag([("Pussy", "NNP"), ("rubbed", "VBD"), ("herbert's", "NNP"), ("castle", "NN")])
    ch = split_post_chunks([2, 3], tg)
    assert ch == [[2, 3]] and np_head(ch[0], tg) == 3, f"W1 skip-possessive failed: chunks={ch}"
    # (W2) skip-quantifier via 'of': "plenty of boys" -> head=boys
    tg = _tag([("He", "PRP"), ("met", "VBD"), ("plenty", "NN"), ("of", "IN"), ("boys", "NNS")])
    ch = split_post_chunks([2, 4], tg)
    assert ch == [[2, 4]] and np_head(ch[0], tg) == 4, f"W2 skip-quantifier failed: chunks={ch}"
    # (W3) DT chunk boundary: "the child a servant" -> first chunk head=child (NOT servant)
    tg = _tag([("I", "PRP"), ("saw", "VBD"), ("the", "DT"), ("child", "NN"), ("a", "DT"), ("servant", "NN")])
    ch = split_post_chunks([3, 5], tg)
    assert ch == [[3], [5]] and np_head(ch[0], tg) == 3, f"W3 DT-boundary failed: chunks={ch}"
    # (W4) wh/verb boundary: "boy whose name was joe" -> first chunk head=boy
    tg = _tag([("He", "PRP"), ("found", "VBD"), ("boy", "NN"), ("whose", "WP$"), ("name", "NN"),
               ("was", "VBD"), ("joe", "NN")])
    ch = split_post_chunks([2, 4, 6], tg)
    assert ch[0] == [2] and np_head(ch[0], tg) == 2, f"W4 wh-boundary failed: chunks={ch}"
    # (W5) particle: "castles down" -> head=castles (down=RP, not a noun)
    tg = _tag([("Pussy", "NNP"), ("knocked", "VBD"), ("castles", "NNS"), ("down", "RP")])
    ch = split_post_chunks([2, 3], tg)
    assert ch == [[2, 3]] and np_head(ch[0], tg) == 2, f"W5 particle failed: chunks={ch}"
    print("[self-test] NP-head/chunk witnesses W1-W5 pass")

    # ---- scaffold-free re-label witnesses ----
    # (WA) transitive RECIPIENT->PATIENT flip with subject present
    tg = _tag([("I", "PRP"), ("saw", "VBD"), ("child", "NN")])
    roles = {0: "AGENT", 2: "RECIPIENT"}
    tr = role_relabel_reassign(roles, [0, 2], tg, 1, False, lambda v: True, no_ditrans_fn,
                               use_np_head=True, emission_preserving=True)
    assert tr["frame"] == "transitive" and roles[2] == "PATIENT" and tr["acted"], f"WA flip failed: {roles} {tr}"
    print(f"[self-test] WA transitive flip: {roles} reason={tr['reason']}")
    # (WB) emission-preserving NO-OP: head perceptron NONE, no sibling patient, no force-emit
    tg = _tag([("It", "PRP"), ("fell", "VBD"), ("down", "RB")])
    roles = {0: "AGENT", 2: "NONE"}
    tr = role_relabel_reassign(roles, [0, 2], tg, 1, False, lambda v: True, no_ditrans_fn,
                               use_np_head=True, emission_preserving=True)
    assert roles.get(2) == "NONE" and not tr["acted"], f"WB no-op failed (force-emitted): {roles} {tr}"
    print(f"[self-test] WB emission-preserving no-op: {roles} reason={tr['reason']}")
    # (WC) same clause, force-emit ablation DOES set the head PATIENT (arms differ)
    roles = {0: "AGENT", 2: "NONE"}
    tr = role_relabel_reassign(roles, [0, 2], tg, 1, False, lambda v: True, no_ditrans_fn,
                               use_np_head=True, emission_preserving=False)
    assert roles.get(2) == "PATIENT" and tr["acted"], f"WC force-emit failed: {roles} {tr}"
    print(f"[self-test] WC force-emit ablation differs: {roles} reason={tr['reason']}")
    # (WD) ditransitive: theme=last-chunk head, recipient protected (demoted)
    tg = _tag([("He", "PRP"), ("gave", "VBD"), ("the", "DT"), ("boy", "NN"), ("the", "DT"), ("books", "NNS")])
    roles = {0: "AGENT", 3: "PATIENT", 5: "NONE"}   # perceptron mis-stole recipient 'boy' as PATIENT
    tr = role_relabel_reassign(roles, [0, 3, 5], tg, 1, False, lambda v: True, real_ditrans_fn,
                               use_np_head=True, emission_preserving=True)
    assert tr["frame"] == "ditransitive" and roles[5] == "PATIENT" and roles[3] != "PATIENT", \
        f"WD ditransitive theme/recipient failed: {roles} {tr}"
    print(f"[self-test] WD ditransitive theme=books, recipient boy protected: {roles} head={tg[tr['head']][1]}")

    print("[self-test] loading SMOKE_SLICE reader + gold + knowledge table ...")
    gold, meta = L.load_gold(SMOKE_SLICE)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)

    print("[self-test] training arc-eager parser (smoke budget) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    # (P1 REPRODUCTION) BASE via AUDIT REAL must equal WO.build_arm_wo(override=None).
    _, _, evidence_real = WO.build_arm_wo(SMOKE_SLICE, W, clf, lambda v: True, None, override=None,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)
    _, audit_base = AUDIT.build_arm_audit(SMOKE_SLICE, W, clf, gate_fn, sel_fn, gold,
                                          oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, wo_base = WO.build_arm_wo(SMOKE_SLICE, W, clf, gate_fn, sel_fn, override=None)
    assert M.arm_hash(audit_base) == M.arm_hash(wo_base), \
        f"P1 REPRODUCTION FAIL: AUDIT REAL != WO override-disabled (audit={M.arm_hash(audit_base)} wo={M.arm_hash(wo_base)})"
    print(f"[self-test] P1 reproduction: AUDIT REAL == WO override-disabled (hash {M.arm_hash(audit_base)})")

    res = run_experiment(SMOKE_SLICE, W, clf, ratings_table, gold, with_autopsy=True)
    for name in ("BASE", "RELABEL_GATED", "RELABEL_FORCEEMIT", "RELABEL_LEFTMOST",
                 "RELABEL_NOLEX", "RELABEL_SCRAMBLE", "ROLE_ORACLE"):
        assert name in res["scored"], f"arm {name} missing from smoke run"
    f1s = {k: v["score"]["f1"] for k, v in res["scored"].items()}
    npreds = {k: v["n_pred"] for k, v in res["scored"].items()}
    print(f"[self-test] 7-arm SMOKE f1={f1s}")
    print(f"[self-test] 7-arm SMOKE n_pred={npreds}")
    print(f"[self-test] scramble_info: {res['scramble_info']}")
    print(f"[self-test] in_scope_outcome (SMOKE covers L04/L05): {res['in_scope_outcome']}")

    prec_base = res["scored"]["BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], f"BASE precision {prec_base} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(BASE)={prec_base}")

    # EMISSION-PRESERVING sanity at smoke: gated must not emit MORE than force-emit.
    assert npreds["RELABEL_GATED"] <= npreds["RELABEL_FORCEEMIT"], \
        f"emission-preserving broken: n_pred(GATED)={npreds['RELABEL_GATED']} > FORCEEMIT={npreds['RELABEL_FORCEEMIT']}"
    print(f"[self-test] emission-preserving sanity: n_pred(GATED)={npreds['RELABEL_GATED']} <= "
          f"FORCEEMIT={npreds['RELABEL_FORCEEMIT']}")

    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    if len(set(hashes.values())) != len(hashes):
        print("[self-test] WARN: >=2 arms share a kept_hash at SMOKE_SLICE scale (small-sample) -- FULL slice "
              "is the load-bearing arms-differ check")
    else:
        print("[self-test] arms_differ: all 7 arms distinct kept_hash at SMOKE_SLICE")

    if not res["head_recovered"]:
        print(f"[self-test] WARN: {HEADLINE} recovered 0 gold items BASE misses at SMOKE_SLICE scale")
    else:
        print(f"[self-test] discriminator fires: {HEADLINE} recovers {len(res['head_recovered'])} gold items "
              f"BASE misses: {res['head_recovered']}")

    assert res["autopsy"] is not None, "autopsy did not run in smoke"
    print(f"[self-test] autopsy produced {len(res['autopsy'])} headroom item reports")

    _, k2 = build_arm_relabel(SMOKE_SLICE, W, clf, gate_fn, sel_fn, real_ditrans_fn, True, True)
    _, k3 = build_arm_relabel(SMOKE_SLICE, W, clf, gate_fn, sel_fn, real_ditrans_fn, True, True)
    assert M.arm_hash(k2) == M.arm_hash(k3), "non-deterministic RELABEL_GATED output across identical runs"
    print("[self-test] deterministic (two RELABEL_GATED runs identical kept-tuple hash)")

    print("[self-test] PASS")
    return 0


# ================================================================================================
# Verdict.
# ================================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=EXPECTED_N_ARMS)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    gold, meta = L.load_gold(slice_lessons)
    W, parser_info = M.train_dep_parser(run_mode)
    res = run_experiment(slice_lessons, W, clf, ratings_table, gold, with_autopsy=True)
    scored = res["scored"]

    f1 = {n: v["score"]["f1"] for n, v in scored.items()}
    prec = {n: v["score"]["precision"] for n, v in scored.items()}
    rec = {n: v["score"]["recall"] for n, v in scored.items()}
    rc = {n: v["recall_ceiling"] for n, v in scored.items()}
    npred = {n: v["n_pred"] for n, v in scored.items()}

    f1_base = f1["BASE"]
    f1_head = f1[HEADLINE]
    f1_force = f1["RELABEL_FORCEEMIT"]
    f1_left = f1["RELABEL_LEFTMOST"]
    f1_nolex = f1["RELABEL_NOLEX"]
    f1_scram = f1["RELABEL_SCRAMBLE"]
    f1_oracle = f1["ROLE_ORACLE"]
    n_base = npred["BASE"]
    n_head = npred[HEADLINE]

    role_gap = round(f1_oracle - f1_base, 4)
    head_lift = round(f1_head - f1_base, 4)
    gap_closed_frac = round(head_lift / role_gap, 4) if role_gap > 1e-9 else None
    ablation_forceemit = round(f1_head - f1_force, 4)   # emission-preserving vs force-emit
    ablation_nphead = round(f1_head - f1_left, 4)       # NP-head vs leftmost-core
    ablation_lexicon = round(f1_head - f1_nolex, 4)     # with vs without ditransitive lexicon
    scramble_degrade = round(f1_head - f1_scram, 4)     # correct membership earns
    n_pred_delta = n_head - n_base                      # EMISSION-PRESERVING CHECK

    p1_ok = abs(f1_base - CITED_AUDIT_F1_REAL) <= P1_REPRO_TOL

    hard_fail_reasons = []
    if not p1_ok:
        hard_fail_reasons.append(f"P1 reproduction broke: |F1(BASE)={f1_base} - {CITED_AUDIT_F1_REAL}| > {P1_REPRO_TOL}")
    if f1_head <= f1_base:
        hard_fail_reasons.append(f"F1({HEADLINE})={f1_head} <= F1(BASE)={f1_base} (relabel lever null)")
    if rec[HEADLINE] < rec["BASE"] - HF_RECALL_REGRESS:
        hard_fail_reasons.append(f"recall({HEADLINE})={rec[HEADLINE]} < recall(BASE)={rec['BASE']} - "
                                 f"{HF_RECALL_REGRESS} (recall regressed)")
    if n_pred_delta > HF_EMISSION_INFLATE:
        hard_fail_reasons.append(f"n_pred({HEADLINE})={n_head} > BASE={n_base}+{HF_EMISSION_INFLATE} "
                                 "(FORCE-EMIT INFLATION -- reverted to drive-3 substrate)")

    hard_pass_conditions = dict(
        p1_reproduces=p1_ok,
        closes_half_gap=(head_lift >= HP_F1_MIN_LIFT),
        no_recall_regress=(rec[HEADLINE] >= rec["BASE"] - HP_RECALL_TOL),
        precision_holds=(prec[HEADLINE] >= prec["BASE"]),
        emission_preserving=(n_pred_delta <= HP_EMISSION_PRESERVE_MARGIN),
        beats_force_emit=(f1_head >= f1_force + HP_ABLATION_MARGIN),
        beats_leftmost=(f1_head >= f1_left + HP_ABLATION_MARGIN),
        scramble_degrades=(f1_head >= f1_scram + HP_SCRAMBLE_MARGIN and f1_scram <= f1_base + 0.005),
    )

    if hard_fail_reasons:
        verdict = "HARD_FAIL_RELABEL_NULL"
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_EMISSION_PRESERVING_RELABEL"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RELABEL"
    failing = [k for k, v in hard_pass_conditions.items() if not v]

    vmsg = (f"{verdict}: F1 BASE={f1_base} -> {HEADLINE}={f1_head} (+{head_lift}, closes {gap_closed_frac} of the "
            f"+{role_gap} ROLE_ORACLE gap). n_pred BASE={n_base} {HEADLINE}={n_head} (delta {n_pred_delta:+d}; "
            f"EMISSION-PRESERVING check, ROLE_ORACLE=+{CITED_ROLEORA_N_PRED - CITED_BASE_N_PRED}). "
            f"precision {prec['BASE']}->{prec[HEADLINE]}; recall {rec['BASE']}->{rec[HEADLINE]}. "
            f"ABLATIONS: vs FORCEEMIT(f1={f1_force}) +{ablation_forceemit}; vs LEFTMOST(f1={f1_left}) "
            f"+{ablation_nphead}; vs NOLEX(f1={f1_nolex}) +{ablation_lexicon}. P2 SCRAMBLE(f1={f1_scram}) "
            f"degrade {scramble_degrade}. ROLE_ORACLE={f1_oracle}. n_head_recovered={len(res['head_recovered'])} "
            f"n_head_regressed={len(res['head_regressed'])}. in_scope_5={res['in_scope_outcome']}. "
            f"failing_HP={failing}. hard_fail={hard_fail_reasons}. SEE autopsy[] (KEEP-DIGGING).")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: f1 BASE={f1_base} {HEADLINE}={f1_head} (+{head_lift}) | n_pred BASE={n_base} "
                 f"{HEADLINE}={n_head} ({n_pred_delta:+d}) | gap_closed_frac={gap_closed_frac} | abl_forceemit="
                 f"{ablation_forceemit} abl_nphead={ablation_nphead} abl_lexicon={ablation_lexicon} | "
                 f"scramble_degrade={scramble_degrade} | ROLE_ORACLE={f1_oracle} | uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["BASE"]), headline_arm=HEADLINE,
        one_variable="role_relabel_reassign: emission-preserving NP-head re-label + SUPPLIED tight ditransitive "
                     "lexicon. NO force-emit (respect perceptron NONE), NO selectional/animacy/patient-fit "
                     "knowledge. parser/perceptron/routing/admissibility-gate/>=2-patient argmax held constant.",
        bands=dict(CITED_AUDIT_F1_REAL=CITED_AUDIT_F1_REAL, CITED_AUDIT_F1_ROLE_ORACLE=CITED_AUDIT_F1_ROLE_ORACLE,
                   CITED_ROLE_GAP=CITED_ROLE_GAP, CITED_BASE_N_PRED=CITED_BASE_N_PRED,
                   CITED_ROLEORA_N_PRED=CITED_ROLEORA_N_PRED, P1_REPRO_TOL=P1_REPRO_TOL,
                   HP_F1_MIN_LIFT=HP_F1_MIN_LIFT, HP_RECALL_TOL=HP_RECALL_TOL,
                   HP_ABLATION_MARGIN=HP_ABLATION_MARGIN, HP_SCRAMBLE_MARGIN=HP_SCRAMBLE_MARGIN,
                   HP_EMISSION_PRESERVE_MARGIN=HP_EMISSION_PRESERVE_MARGIN,
                   HF_RECALL_REGRESS=HF_RECALL_REGRESS, HF_EMISSION_INFLATE=HF_EMISSION_INFLATE),
        f1=f1, precision=prec, recall=rec, recall_ceiling=rc, n_pred=npred,
        role_gap=role_gap, head_lift=head_lift, gap_closed_frac=gap_closed_frac,
        n_pred_delta=n_pred_delta, emission_preserving_ok=(n_pred_delta <= HP_EMISSION_PRESERVE_MARGIN),
        ablation_forceemit=ablation_forceemit, ablation_nphead=ablation_nphead, ablation_lexicon=ablation_lexicon,
        scramble_degrade=scramble_degrade, p1_reproduces=p1_ok,
        hard_pass_conditions=hard_pass_conditions, hard_fail_reasons=hard_fail_reasons,
        in_scope_outcome=res["in_scope_outcome"],
        n_roleora_recovered=len(res["roleora_recovered"]),
        roleora_recovered=[list(x) for x in res["roleora_recovered"][:40]],
        n_head_recovered=len(res["head_recovered"]),
        head_recovered=[list(x) for x in res["head_recovered"][:40]],
        n_head_regressed=len(res["head_regressed"]),
        head_regressed=[list(x) for x in res["head_regressed"][:40]],
        n_head_of_roleora=len(res["head_of_roleora"]),
        head_of_roleora=[list(x) for x in res["head_of_roleora"][:40]],
        force_recovered=[list(x) for x in res["force_recovered"][:40]],
        leftmost_recovered=[list(x) for x in res["leftmost_recovered"][:40]],
        nolex_recovered=[list(x) for x in res["nolex_recovered"][:40]],
        scramble_recovered=[list(x) for x in res["scramble_recovered"][:40]],
        roleora_headroom_coverage=(round(len(res["head_of_roleora"]) / len(res["roleora_recovered"]), 4)
                                   if res["roleora_recovered"] else None),
        lexicon_audit=dict(n_ditransitive=len(DITRANSITIVE_TIGHT),
                           tight_set=sorted(DITRANSITIVE_TIGHT),
                           dropped_edge_check={w: (w not in DITRANSITIVE_TIGHT) for w in DROPPED_EDGE_DATIVES_CHECK},
                           headroom_out={w: (w not in DITRANSITIVE_TIGHT)
                                         for w in ("see", "rub", "meet", "knock", "build", "find")},
                           scramble=res["scramble_info"]),
        autopsy=res["autopsy"],
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"], n_gold_pos=v["n_gold_pos"],
                         precision=v["score"]["precision"], recall=v["score"]["recall"], f1=v["score"]["f1"],
                         n_pred=v["n_pred"], subcat_fp=v["score"]["subcat_fp"],
                         within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        parser_info=parser_info,
        cited_audit=dict(source="data/exp_reader_component_oracle_ablation_audit_v1/metrics.json",
                         f1_real=CITED_AUDIT_F1_REAL, f1_role_oracle=CITED_AUDIT_F1_ROLE_ORACLE,
                         role_uplift=CITED_ROLE_GAP),
        cited_drive3=dict(source="data/exp_reader_role_valency_supplied_lexicon_v3/metrics.json",
                          base_n_pred=CITED_BASE_N_PRED, forceemit_n_pred=156, roleora_n_pred=CITED_ROLEORA_N_PRED,
                          note="drive-3 blunt force-emit inflated n_pred 144->156 (+12 FP) -> F1 0.5391 < BASE."),
        brain_check="the brain does not force a patient onto a clause it parses as argument-less; it RE-LABELS a "
                    "routed argument (recipient/agent confusion) to patient when a subject licenses SVO reading, "
                    "and retrieves a verb's ditransitivity as a supplied lexical fact. Emission-preserving = the "
                    "reader does not invent arguments; it corrects role assignment on arguments it already found.",
        scope_caveat=("Parser trained on UD-EWT out-of-domain to McGuffey. Tight ditransitive lexicon is a "
                      "VerbNet-role-filter SUBSET (drops benefactive/edge datives incl. find). build/blockhouse "
                      "OSV is drive-1's FRONTED arm, out of scope. MEASUREMENT cell, NOT banked; CLAIM-VET-pending; "
                      "strategic read = HYPOTHESIS pending landed-VET (skunkworks VETs separately)."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("in_scope_outcome:", res["in_scope_outcome"])
    print("head_recovered:", res["head_recovered"])
    print("head_regressed:", res["head_regressed"])
    print("roleora_recovered:", res["roleora_recovered"])
    print("scramble_info:", json.dumps(res["scramble_info"], indent=1))
    print("AUTOPSY (headroom per-item):")
    print(json.dumps(res["autopsy"], indent=1))
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
