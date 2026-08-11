# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; lesion/without/oracle/frame/scramble_kb differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold
# - HP_SCOPE: {frame_activation: [survival_beats_literal_floor, pair_recall_up, pair_precision_up,
#              scramble_kb_collapses, ablation_collapses, no_leak, arms_differ]}
# - cardinality_ok: single split, one pass (+ scramble-KB-content control arm); EXPECTED arms fixed
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (FRAME_SIM_THRESH/ROLE_SIM_THRESH DEV-pinned
#   below on prior lexicon self-test evidence; discriminator-fires re-verified in this cell's smoke)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (KB + lexicon + graded matcher + firing + official_eval)
# - progress_logging: print_flush_true
# - deterministic_seeding: true (scramble uses TWO independent hashlib-seeded _deterministic_perm
#   calls -- sig-donor + role-donor -- never python hash() / list(set()) ordering -- PROT-023/F.5)
# - 2026-08-11 MECHANISM-BUG FIX (post-smoke HARD_FAIL): (1) _scramble_kb_processes rewritten from
#   a single whole-block name permutation (confirmed on disk to be a content-preserving no-op --
#   the SAME content objects just moved to new keys, invisible to name-agnostic content-driven
#   scoring) to a DOUBLE permutation decoupling signature-donor from role-word-donor; (2)
#   _graded_frame_score rewritten from MEAN best-match similarity to COUNT of signature words
#   clearing threshold (parallels literal's count-based ranking; guarantees graded hit-count >=
#   literal hit-count per process, fixing a top-2-selection hijack that was regressing BOTH
#   precision and recall below the literal floor). See inline FIX #1/#2 comments at point of use.
# - 2026-08-11 OPTION-b CONVERGENCE GATE (director-directed, after v2 re-smoke showed scramble>frame
#   i.e. WRONG facts beat RIGHT facts): CO-PARTICIPATION-GATED frame selection -- a process may
#   donate fates only if the paragraph convergently CONFIRMS it (>=2 distinct roles filled by >=2
#   distinct participants; coincidence detection). Hard GATE, not an additive score (SIQa iter-2
#   prior-art caution honored). RESULT = HARD pre-committed EXIT: the gate WORKS structurally
#   (scramble donors collapse 16->1 on disk; gate-pass asymmetry real 0.30 vs scramble 0.012) but
#   does NOT move the F1 wall (frame_f1 0.3273 < scramble_f1 0.3388 < oracle_f1 0.3993; frame_lift
#   0.0032 < scramble_lift 0.0147; precision 0.0625 < literal 0.0905). The residual is per-participant
#   ROLE->EFFECT assignment = reading the specific participant's specific fate out of the prose = the
#   situation-model / extraction wall, NOT frame SELECTION (which the gate fixed). oracle_f1 >> all
#   matcher arms = the knowledge IS usable; the matcher cannot source it from text. See prereg
#   AMENDMENT-2 (Option-b exit) + inline CONVERGENCE GATE comment at point of use.
# See preregs/2026-08-10_propara_bridging_frame_activation_v1.md for the full pre-reg.
"""exp_propara_bridging_frame_activation_v1 -- ASSOCIATIVE FRAME/SCRIPT-ACTIVATION reading, direct
successor to exp_propara_bridging_distilled_kb_endtoend_v1 (357143e98, HARD_FAIL, SURVIVAL=0.1823).

USER's reframe (see notes/research_frame_script_reading_build_spec_2026-08-10.md, filed by research
this cycle, VET-CONFIRMED on disk): ProPara bridging did NOT cap at 0.18 for lack of knowledge -- the
oracle cell (exp_propara_bridging_knowledge_vs_mechanism_v1) already proves the mechanism and
knowledge content ARE load-bearing once correctly sourced (+0.1062 real lift). It capped because the
distilled cell's `_build_distilled_bridge_facts` sources bridging facts via LITERAL SET-INTERSECTION
at BOTH required steps -- `len(set(signature) & text_toks)` for paragraph-to-process matching,
`p_toks & role_toks` for participant-to-role mapping -- a phone-book lookup, structurally blind to
ANY paraphrase ("the log burns" never matches signature "wood"/"fire" unless those EXACT strings
appear). The brain's actual mechanism (Schank-Abelson scripts / Fillmore frame semantics) is
ASSOCIATIVE: a trigger word activates a whole process frame via graded similarity, not exact lookup.

ONE-VARIABLE TEST: hold the KB CONTENT fixed (the SAME 18-process propara_process_physics_kb_v1.json,
zero edits) and swap ONLY the matching OPERATOR: literal set-intersection -> graded
hdlab.lexical_similarity.concept_similarity. If survival climbs off the 0.1823 floor toward the
+0.1062 oracle with all controls clean, it proves the wall was the MECHANISM (matcher), not the
knowledge -- the USER's point, now measured, not just brain-analogical.

VET-CAUGHT PREREQUISITE (this build, before writing this cell): hdlab.lexical_similarity's
pre-existing 89-concept lexicon had ZERO usable overlap with this KB's vocabulary (MEASURED@this
build: 3/197 words -- water, mountain, fix). Extending the lexicon was NOT optional; without it,
concept_similarity returns None (honest-abstain) for nearly every pair and graded matching cannot
fire at all. Fixed via a SUPPLY EXTENSION to hdlab/lexical_similarity.py (2026-08-10 ProPara block):
(1) a MECHANICAL part auto-generated from the KB's own JSON (every literal signature/consumes/
produces/moves word gets a DOM + DOM_ROLE compound tag -- guarantees literal-match parity as a
floor, zero new knowledge, pure re-encoding of already-hand-vetted content); (2) a hand-authored
PARAPHRASE part (~35 words: log/timber/kindling->wood, blaze->fire, mist->vapor, sun->sunlight,
carcass->body, boulder->rock, ...) from general science + common-synonym knowledge, NOT from reading
ProPara TEST paragraphs -- THIS is what actually tests "many surface forms -> one frame" (the
mechanical part alone only reproduces literal-match parity, self-similarity=1.0, it cannot beat the
floor by itself). See hdlab/lexical_similarity.py's module-level "SUPPLY EXTENSION (2026-08-10,
ProPara frame-activation build)" comment block for the full construction + self_test additions.

ORGANS REUSED (per the build-spec audit, Section 2 of the note above):
  - hdlab.lexical_similarity.concept_similarity -- THE graded matcher (Step 2a/2b below).
  - hdlab.situation_model_accumulate / exp_propara_bridging_knowledge_vs_mechanism_v1._grids --
    UNCHANGED downstream retrieve-validate-advance consumption (bit-identical to the distilled
    cell's `pre[pid]["bridge"]` contract; this cell only changes HOW that dict gets populated).
  - propara_process_physics_kb_v1.json -- UNCHANGED KB content (Step 1, reuse verbatim).
NOT reused (deviations from the build spec's optional mentions, both DISK-CHECKED this build, not
assumed): hdlab.frame_induction.py is OOV-VERB thematic-role induction (AGENT/EXPERIENCER), a
naming-collision false-friend for PROCESS-frame identification -- confirmed by direct code read,
not used. hdlab.script_grain_acquisition_loop.ScriptLibrary's FHRR bind-then-bundle pattern is the
right SHAPE but only 4 fixed roles and consumes already-typed category tags, not raw text; NOT
invoked here because this cell's downstream consumer (`_grids`) only needs a plain
{effect_label: set(trigger_verb_classes)} dict (identical to the literal-match cell's contract) --
introducing FHRR script-instance objects would not change the scored F1 output at all (pure
decoration for this contract), so it is scoped out per compute-proportionality (match method weight
to the question). Genuinely reusing ScriptLibrary for GENERALIZING beyond this hand-vetted KB (a
subsequent "learn new process types from exposure" step) is future work, not this build.

STEP 3 (implicit-entity SCOPE NOTE, honest): the KB build spec asked for implicit-entity allocation
for frame-slot fillers with no textual mention (e.g. oxygen never named in text). DISK-CHECKED this
build: `_grids` only ever consumes `pre[pid]["bridge"][participant]` for `participant in
para["participants"]` -- ProPara's OWN gold participant list, which ALREADY includes every tracked
entity regardless of whether it is textually mentioned at a given step (that is exactly what
"unmentioned subset" means in this arc -- a known, tracked participant with an untextualized state
change, not a wholly-new entity). So no NEW entity ever needs allocating for the scored metric to
move; what IS new and audited here is an IMPLICIT-vs-MENTIONED trace tag per (paragraph, participant)
pair (never-literally-named-in-text vs named), surfaced in stats for inspectability, without
changing the `_grids` contract -- satisfying the audit-trail intent without adding unscored objects.

CONTROLS (all reused from the distilled cell's harness, unchanged, PLUS one new one):
  - prior_lesion, without_knowledge (ablation), with_oracle (ceiling) -- unchanged.
  - NO-LEAK: with_frame_activation must stay < 0.95 AND not approach oracle (same LEAK_ORACLE_MARGIN).
  - NEW: with_frame_activation_scramble_kb -- deterministic DOUBLE hashlib-seeded permutation
    (never python hash(); _deterministic_perm, PROT-023/F.5) that decouples each process's
    SIGNATURE (frame-identification content, one donor permutation) from its consumes/produces/
    moves ROLE-WORD lists (frame-effect content, an INDEPENDENTLY-chosen donor permutation) -- a
    2026-08-11 fix, see below; the original single whole-block permutation was disk-confirmed to
    be a content-preserving no-op (relocates the same content objects, invisible to name-agnostic
    scoring). If graded matching's lift SURVIVES this decoupled scramble, the win is a structural
    artifact of looser thresholds, not genuine frame-content matching -- this is the single most
    important new control (per the build spec) and GATES
    HARD-PASS, not just reported.

MEASURED@data/exp_propara_bridging_distilled_kb_endtoend_v1/metrics.json (TEST split, run_mode=full):
  LITERAL_SURVIVAL_FLOOR_TEST=0.18226561332964253, LITERAL_PAIR_RECALL_TEST=0.2469,
  LITERAL_PAIR_PRECISION_TEST=0.0905, ORACLE_LIFT_TEST=0.10622865330406278 (also
  MEASURED@data/exp_propara_bridging_knowledge_vs_mechanism_v1/metrics.json).
MEASURED@data/exp_propara_bridging_distilled_kb_endtoend_v1_smoke/metrics.json (DEV split,
  run_mode=smoke): LITERAL_SURVIVAL_FLOOR_DEV=0.033371288035546114, ORACLE_LIFT_DEV=0.07514267964957705,
  LITERAL_PAIR_RECALL_DEV=0.2381, LITERAL_PAIR_PRECISION_DEV=0.0676.

Modes: --self-test / --smoke (DEV) / --full (TEST).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

ANCHOR_NAME = "propara_bridging_frame_activation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
KB_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_process_physics_kb_v1.json")

import propara_official_eval as offeval  # noqa: E402
from hdlab.lexical_similarity import concept_similarity as _concept_similarity_raw  # noqa: E402

_SIM_CACHE: Dict[Tuple[str, str], "float | None"] = {}


def concept_similarity(word_a: str, word_b: str):
    """Memoized wrapper around hdlab.lexical_similarity.concept_similarity -- pure/deterministic
    function (same FHRR encoding every call), so caching is a performance-only change (this cell's
    nested paragraph x process x signature-word x text-token loops re-query the same word pairs
    thousands of times; unmemoized this made even a single DEV-split smoke run take >1min and made
    threshold-calibration sweeps intractable). Not a mechanism change."""
    key = (word_a, word_b) if word_a <= word_b else (word_b, word_a)
    if key not in _SIM_CACHE:
        _SIM_CACHE[key] = _concept_similarity_raw(word_a, word_b)
    return _SIM_CACHE[key]
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset,
    majority_label_grids, bow_label_grids, bag_of_states_label_grids,
    fit_bag_of_states_classifiers, _official_corpus_scores, _proxy_scores, _arms_must_differ,
    _deterministic_perm,  # hashlib-seeded permutation helper (F.5-compliant; reused for scramble-KB)
)
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import (  # noqa: E402
    _paragraph_precompute, _grids, _prior_lesion_grids, _unm,
    LEAK_CEILING, WITHOUT_COLLAPSE_CEILING,
)
from experiments.exp_propara_bridging_real_kb_sourcing_v1 import _fact_coverage  # noqa: E402
from experiments.exp_propara_arm2_extracted_structure_v1 import _load_coref  # noqa: E402
from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import (  # noqa: E402
    _toks, _norm_toks, _load_kb, _ROLE_EFFECT,
)
from propara_trap_check import build_step_rows, build_paragraph_set_rows, fit_step_bow  # noqa: E402

# ============================================================================ pre-registered thresholds
# DEV-pinned on the lexicon's OWN self-test evidence (hdlab/lexical_similarity.py self_test(), this
# build): true within-role paraphrases score 1.0 (identical tag sets, e.g. log~wood, blaze~fire,
# mist~vapor=0.5906, sun~sunlight=0.6748, timber~fuel=0.5245); same-domain-DIFFERENT-role pairs
# (must NOT cross-bind) score materially lower (wood~ash=0.4077, wood~fire=0.4130,
# boulder~rock=0.3503). MEASURED@this build's own interactive probe (see completion report).
FRAME_SIM_THRESH = 0.45   # paragraph-token vs SIGNATURE-word (frame identification; broader net)
# 2026-08-11 RE-PIN (post mechanism-bug fix, before this the value was 0.55 -- see prereg amendment):
# MEASURED@this build's own DEV-split grid sweep (12+ operating points, both thresholds AND
# MIN_FRAME_SIG_HITS independently varied, run in-process with the memoized similarity cache --
# see completion report): a single ROLE_SIM_THRESH value could not simultaneously satisfy all three
# re-smoke gates on the tiny (43-paragraph) DEV split -- ROLE_SIM_THRESH in [0.55,0.65] gives a
# cleanly-collapsing scramble control (scramble_retained well under 0, i.e. the scrambled/decoupled
# KB does WORSE than the real one) but frame_lift stays negative; ROLE_SIM_THRESH>=0.70 turns
# frame_lift positive and improves precision monotonically (plateaus at n_role_hits=139 for any
# value >=0.80 -- all remaining hits are near-1.0 self-similarity, i.e. purely literal-adjacent) but
# makes scramble_retained_fraction numerically unstable (a near-zero frame_lift denominator inflates
# the ratio even though the scramble control DOES structurally perturb the output -- see
# _scramble_kb_processes fix comment). 0.70 is the LOWEST value at which frame_lift turns positive
# (the honest minimum re-pin, not cherry-picked for the best-looking number): frame_lift=+0.0061,
# survival=0.0808, pair_recall=0.2619 (beats BOTH the DEV-split AND the TEST-pinned literal
# reference), pair_precision=0.0655 (beats the true DEV-split literal reference 0.0676... narrowly
# short actually, see completion report honest caveat) but still short of the TEST-pinned
# LITERAL_PAIR_PRECISION_TEST=0.0905 bar used by the pre-registered verdict bands below (unchanged,
# no test-set peeking -- this re-pin only touches the two DEV-facing similarity thresholds, never
# the TEST-pinned pass/fail bands).
ROLE_SIM_THRESH = 0.70    # participant-token vs role-word (consumes/produces/moves; precision-favoring)
MIN_FRAME_SIG_HITS = 1     # >=1 signature word must clear FRAME_SIM_THRESH for a process to be "matched"
SCRAMBLE_SEED_SIG = "propara_frame_activation_kb_scramble_v2_sig"      # hashlib-seeded, not python hash()
SCRAMBLE_SEED_ROLES = "propara_frame_activation_kb_scramble_v2_roles"  # DIFFERENT seed -- see _scramble_kb_processes

# ------------------------------------------------------------------ CONVERGENCE GATE (2026-08-11 Option-b)
# Director decision (rejecting FULL-despite-DEV-shortfall): the v2 re-smoke's tiny frame_lift is NOT
# correct-frame-binding -- the scramble control (0.0 oracle overlap) gave scramble_lift=+0.0148 >
# frame_lift=+0.0061, i.e. WRONG facts beat RIGHT facts (an anti-correlated signal no DEV/TEST
# scaling can fix). ROOT CAUSE (localized in v2 completion report): KB role-vocabulary PROMISCUITY --
# a wrong/scrambled process is reached by ONE promiscuous role-word (heat/water/material) by chance;
# top-2-signature selection then lets it donate net-harmful fates.
# FIX (brain: coincidence detection -- a frame is the node where MULTIPLE independent context cues
# CONVERGE): a process may donate fates ONLY IF the paragraph convergently CONFIRMS it -- >=2 DISTINCT
# roles of that SAME process are each filled by a participant AND >=2 DISTINCT participants do the
# filling. This is a HARD GATE (precision lever), NOT an additive score. PRIOR-ART CAUTION honored
# (SIQa iter-1 79c354a6d / iter-2 e7cee79ae): raw convergence-COUNT as an additive scoring feature
# was a NET DRAG and was dropped; iter-2 kept convergence ONLY as a >=2-distinct STRUCTURAL GATE
# (retrieve-VALIDATE MIN_COH_CONVERGENCE). This gate reuses that exact validated pattern. ONE VARIABLE
# vs v2 = the frame-SELECTION criterion only (KB content, thresholds, role-mapping, downstream _grids,
# and the oracle/without/prior_lesion arms are all UNCHANGED).
CONVERGENCE_GATE = True         # master toggle; if False, falls back to v2 signature-top-2 selection
CAND_K = 4                       # signature-ranked candidate pool considered for the convergence gate
                                 # (widen past top-2 so a convergent-but-lower-signature process is not
                                 # pre-excluded; final donors still capped at MAX_DONORS)
MAX_DONORS = 2                   # cap on donor processes AFTER gating (matches literal cell's k=2)
MIN_CONVERGENT_ROLES = 2         # >=2 DISTINCT roles of the process must be filled (coincidence det.)
MIN_CONVERGENT_FILLERS = 2       # ...by >=2 DISTINCT participants (independent cues, not one hub word)

# Bands (pre-registered BEFORE --full; see prereg). TEST-split floor/ceiling per module docstring.
LITERAL_SURVIVAL_FLOOR_TEST = 0.18226561332964253
LITERAL_PAIR_RECALL_TEST = 0.2469
LITERAL_PAIR_PRECISION_TEST = 0.0905
FRAME_SURVIVAL_HARD_PASS = 2.0 * LITERAL_SURVIVAL_FLOOR_TEST   # a doubling (build-spec's own suggested margin)
FRAME_SURVIVAL_HARD_FAIL = LITERAL_SURVIVAL_FLOOR_TEST * 1.10  # within ~10% of floor = mechanism swap didn't matter
SCRAMBLE_MAX_RETAINED_FRACTION = 0.50  # scramble-KB arm must retain <= 50% of the real arm's lift
LEAK_ORACLE_MARGIN = 0.02


# ============================================================================ graded matching (THE FIX)
# MECHANISM-BUG FIX #1 (2026-08-11, smoke HARD_FAIL diagnosis, disk-confirmed before this edit):
# the ORIGINAL version scored a process by MEAN best-match similarity (sum(scored)/len(scored)).
# That is not commensurate with the literal cell's ranking rule (COUNT of exact signature-word
# hits, `len(set(signature) & text_toks)`): a process with a single spuriously-high-similarity
# signature word could out-rank a genuinely-matching process with many weaker-but-real hits,
# hijacking top-2 process SELECTION away from what literal matching would (correctly) have
# chosen. MEASURED@this build's disk diagnosis: with mean-aggregation, graded pair_precision
# (0.0538) AND pair_recall (0.2381) were BOTH *below* the literal floor (0.0905 / 0.2469) -- the
# graded matcher, which should be a strict superset of literal (every exact match also
# self-similarity=1.0 in the lexicon, so graded hits >= literal hits per signature word), was
# instead doing worse, which is only possible if TOP-2 PROCESS SELECTION itself was regressing.
# FIX: rank by COUNT of signature words clearing FRAME_SIM_THRESH (paralleling literal's count-
# based ranking exactly, generalizing the per-word test from EXACT to GRADED) instead of MEAN
# similarity. This guarantees graded_hit_count(process, text) >= literal_hit_count(process, text)
# for every process/paragraph pair (never worse), so top-2 selection can only gain candidates
# paraphrase-matching added, never lose ones literal would have found.
def _graded_frame_score(text_toks: Set[str], signature_words: List[str]) -> Tuple[float, int]:
    """COUNT of signature words that clear FRAME_SIM_THRESH against some paragraph token (graded
    generalization of literal's exact set-intersection COUNT, not a mean -- see FIX #1 above).
    Honest-abstain: OOV pairs (concept_similarity returns None) are SKIPPED, never treated as 0 --
    never silently degrades to a false non-match. Returns (None, 0) if no signature word had ANY
    in-lexicon paragraph token (this process is unscoreable here, distinct from scoreable-but-0-hits)."""
    scored_words = 0
    hits = 0
    for sig_w in signature_words:
        best = None
        for tok in text_toks:
            s = concept_similarity(tok, sig_w)
            if s is None:
                continue
            if best is None or s > best:
                best = s
        if best is not None:
            scored_words += 1
            if best >= FRAME_SIM_THRESH:
                hits += 1
    if scored_words == 0:
        return None, 0
    return float(hits), hits


def _graded_role_hit(p_toks: Set[str], role_words: List[str]) -> bool:
    """True iff some participant token clears ROLE_SIM_THRESH against some role-list word.
    Honest-abstain on OOV pairs (skipped, not treated as 0/no-match by construction)."""
    for tok in p_toks:
        for rw in role_words:
            s = concept_similarity(tok, rw)
            if s is not None and s >= ROLE_SIM_THRESH:
                return True
    return False


def _literal_role_hit(p_toks: Set[str], role_words: List[str]) -> bool:
    """The OLD literal-match rule (exact string membership), used ONLY as a diagnostic reference
    inside this cell to measure graded-only coverage -- NOT part of the sourced facts."""
    role_toks = set(role_words) | {w[:-1] if w.endswith("s") else w + "s" for w in role_words}
    return bool(p_toks & role_toks)


def _process_convergent(proc_dict: Dict, participants_toks: List[Set[str]]) -> Tuple[bool, int, int]:
    """COINCIDENCE-DETECTION GATE (boolean, NOT a score): a process may donate fates only if the
    paragraph convergently evidences it -- >= MIN_CONVERGENT_ROLES DISTINCT roles of the process are
    each filled by SOME participant AND >= MIN_CONVERGENT_FILLERS DISTINCT participants do the filling.
    A wrong/scrambled process is typically reached by ONE promiscuous role-word by chance; a genuine
    frame is where multiple independent entity->role cues converge. Reuses the validated SIQa iter-2
    pattern (e7cee79ae): convergence kept ONLY as a >=2-distinct STRUCTURAL gate, never as an additive
    score (raw convergence-count was a net drag there). Returns (passes, n_distinct_roles_filled,
    n_distinct_fillers)."""
    roles_filled = 0
    fillers: Set[int] = set()
    for role in ("consumes", "produces", "moves"):
        role_words = proc_dict.get(role, [])
        if not role_words:
            continue
        hit_idxs = [i for i, pt in enumerate(participants_toks) if _graded_role_hit(pt, role_words)]
        if hit_idxs:
            roles_filled += 1
            fillers.update(hit_idxs)
    passes = (roles_filled >= MIN_CONVERGENT_ROLES) and (len(fillers) >= MIN_CONVERGENT_FILLERS)
    return passes, roles_filled, len(fillers)


# MECHANISM-BUG FIX #2 (2026-08-11, THE root cause of scramble_retained_fraction=1.0):
# disk-confirmed via a throwaway diagnostic (removed after use) that the ORIGINAL implementation
# below -- `{names[i]: procs[names[perm[i]]] for i in range(n)}` -- moves each process's ENTIRE
# dict (signature AND consumes/produces/moves TOGETHER, as the same Python object) to a new name
# key. `sorted(id(v) for v in procs.values()) == sorted(id(v) for v in scrambled.values())` was
# True: the scramble is a pure NAME relabeling; the SET of content-blob objects is bit-identical.
# Because `_graded_frame_score` scores every entry in `procs.items()` by CONTENT alone (never by
# name) and top-2 selection then re-fetches `procs[pname]` (the SAME relocated object), the
# permutation is a structural no-op for this content-driven, name-agnostic consumption pattern --
# scramble_retained_fraction was 1.0 not because the mechanism is a "threshold artifact" but
# because the control never actually perturbed anything the downstream code reads.
# FIX: decouple the SIGNATURE (used to identify/activate a frame) from the ROLE-WORD lists (used
# to source effects for that frame) via TWO INDEPENDENT permutations. Whichever content wins the
# signature-match (frame IDENTIFICATION is unperturbed -- same 18 real signatures, just filed
# under different names, so matching quality is preserved) is now paired with a DIFFERENT,
# independently-chosen process's consumes/produces/moves lists (role-word CONTENT is genuinely
# decoupled from the matched frame). If the graded win survives THIS -- correct frame recognition
# wired to a WRONG frame's effects -- the win does not depend on genuine frame-content coherence.
def _scramble_kb_processes(procs: Dict) -> Dict:
    """Deterministic hashlib-seeded DOUBLE permutation (via _deterministic_perm, PROT-023/F.5 --
    never python hash() / list(set()) ordering): each output process name gets its SIGNATURE from
    one donor (perm_sig) and its consumes/produces/moves ROLE-WORD lists from a DIFFERENTLY-CHOSEN
    donor (perm_roles) -- decoupling frame-identification content from frame-effect content.
    Content-scramble control -- if the graded-matching win SURVIVES this, the win is a structural/
    threshold artifact, not genuine frame-content matching."""
    names = sorted(procs.keys())
    n = len(names)
    perm_sig = _deterministic_perm(SCRAMBLE_SEED_SIG, n)
    perm_roles = _deterministic_perm(SCRAMBLE_SEED_ROLES, n)
    assert perm_sig != list(range(n)), "SCRAMBLE_DEGENERATE: sig permutation is identity (re-seed)"
    assert perm_roles != list(range(n)), "SCRAMBLE_DEGENERATE: roles permutation is identity (re-seed)"
    assert perm_sig != perm_roles, "SCRAMBLE_DEGENERATE: sig and roles permutations coincide (not decoupled, re-seed)"
    n_decoupled = sum(1 for i in range(n) if perm_sig[i] != perm_roles[i])
    assert n_decoupled >= n // 2, (
        f"SCRAMBLE_INSUFFICIENT_DECOUPLING: only {n_decoupled}/{n} entries have a different "
        f"sig-donor vs role-donor; scramble control would be too weak to be diagnostic")
    scrambled = {}
    for i, name in enumerate(names):
        sig_donor = procs[names[perm_sig[i]]]
        role_donor = procs[names[perm_roles[i]]]
        d = {"signature": sig_donor.get("signature", [])}
        for role in ("consumes", "produces", "moves"):
            d[role] = role_donor.get(role, [])
        scrambled[name] = d
    return scrambled


# ============================================================================ frame-activation sourcing (no gold)
def _build_frame_activation_bridge_facts(paragraphs, kb, scramble_kb: bool = False) -> Tuple[Dict[Tuple, Dict[str, Set[str]]], Dict]:
    """Per (para_id, participant): {effect_label: set(trigger_verb_classes)}, sourced via GRADED
    associative frame-activation (concept_similarity) instead of literal set-intersection. Bit-
    identical output SHAPE to _build_distilled_bridge_facts -- pure sourcing-mechanism ablation."""
    procs = kb["processes"]
    if scramble_kb:
        procs = _scramble_kb_processes(procs)
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    proc_log = {}
    n_role_hits = 0
    n_graded_only_role_hits = 0   # graded fired where literal (against the SAME possibly-scrambled
                                   # content) would not have -- the genuine paraphrase-generalization count
    n_never_mentioned_participants = 0
    n_facts_for_never_mentioned = 0
    n_cand_before_gate = 0        # signature-ranked candidates entering the convergence gate
    n_donors_after_gate = 0       # donors surviving the convergence gate (CONVERGENCE_GATE precision lever)
    for para in paragraphs:
        pid = str(para["para_id"])
        full_text = " ".join(para["sentence_texts"]).lower()
        text_toks = _toks(" ".join(para["sentence_texts"]))
        participants_toks = [_norm_toks(p) for p in para["participants"]]
        scored = []
        for name, d in procs.items():
            score, hits = _graded_frame_score(text_toks, d["signature"])
            if score is not None and hits >= MIN_FRAME_SIG_HITS:
                scored.append((name, score))
        scored.sort(key=lambda kv: -kv[1])
        if CONVERGENCE_GATE:
            # gate the signature-ranked candidate pool by convergence (coincidence detection), then
            # keep at most MAX_DONORS in signature order among those that PASS -- convergence is a hard
            # boolean GATE here, never added into a donor score (SIQa prior-art caution).
            cand = [name for name, sc in scored[:CAND_K]]
            n_cand_before_gate += len(cand)
            donors = [nm for nm in cand if _process_convergent(procs[nm], participants_toks)[0]]
            matched = donors[:MAX_DONORS]
            n_donors_after_gate += len(matched)
        else:
            matched = [name for name, sc in scored[:2]]  # v2 fallback: top-2 by signature (no gate)
        proc_log[pid] = matched
        for participant in para["participants"]:
            p_toks = _norm_toks(participant)
            mentioned_in_text = any(t in full_text for t in p_toks if len(t) > 2)
            if not mentioned_in_text:
                n_never_mentioned_participants += 1
            fdict: Dict[str, Set[str]] = {}
            got_any = False
            for pname in matched:
                d = procs[pname]
                for role, effect, trigs in _ROLE_EFFECT:
                    role_words = d.get(role, [])
                    if not role_words:
                        continue
                    graded = _graded_role_hit(p_toks, role_words)
                    if graded:
                        fdict.setdefault(effect, set()).update(trigs)
                        n_role_hits += 1
                        got_any = True
                        if not _literal_role_hit(p_toks, role_words):
                            n_graded_only_role_hits += 1
            if got_any and not mentioned_in_text:
                n_facts_for_never_mentioned += 1
            facts[(pid, participant)] = fdict
    stats = {
        "n_paragraphs_matched": sum(1 for v in proc_log.values() if v),
        "n_role_hits": n_role_hits,
        "n_graded_only_role_hits": n_graded_only_role_hits,   # the paraphrase-generalization evidence
        "n_never_mentioned_participants": n_never_mentioned_participants,
        "n_facts_sourced_for_never_mentioned_IMPLICIT": n_facts_for_never_mentioned,
        "process_match_sample": {k: proc_log[k] for k in list(proc_log)[:8]},
        "scramble_kb": scramble_kb,
        "convergence_gate": CONVERGENCE_GATE,
        "n_cand_before_gate": n_cand_before_gate,             # convergence-gate diagnostics: how many
        "n_donors_after_gate": n_donors_after_gate,           # signature candidates survived the gate
        "gate_pass_fraction": (round(n_donors_after_gate / n_cand_before_gate, 4)
                               if n_cand_before_gate else None),
    }
    return facts, stats


# ============================================================================ decomposition
def run_decomposition(split: str, train_paragraphs: List[Dict]) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    train_set_df = build_paragraph_set_rows(train_paragraphs)
    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)
    coref = _load_coref(split)
    kb = _load_kb()

    print(f"[precompute] {len(paragraphs)} paragraphs (extraction + oracle facts)...", flush=True)
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp] for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}

    print("[frame_activation] graded concept-similarity process-frame sourcing (match process + map roles, no gold)...", flush=True)
    frame_facts, frame_stats = _build_frame_activation_bridge_facts(paragraphs, kb, scramble_kb=False)
    cov = _fact_coverage(frame_facts, oracle_facts)

    print("[frame_activation_scramble_kb] SCRAMBLE-KB-CONTENT control (deterministic permutation)...", flush=True)
    scramble_facts, scramble_stats = _build_frame_activation_bridge_facts(paragraphs, kb, scramble_kb=True)
    cov_scr = _fact_coverage(scramble_facts, oracle_facts)

    def _pre_with_bridge(facts):
        pre = {}
        for para in paragraphs:
            pid = str(para["para_id"])
            pr = dict(pre_oracle[pid])
            pr["bridge"] = {pp: facts.get((pid, pp), {}) for pp in para["participants"]}
            pre[pid] = pr
        return pre

    pre_frame = _pre_with_bridge(frame_facts)
    pre_scramble = _pre_with_bridge(scramble_facts)

    grids: Dict[str, Dict] = {}
    grids["prior_lesion"], lesion_diag = _prior_lesion_grids(paragraphs, pre_oracle)
    grids["without_knowledge"], without_diag = _grids(paragraphs, pre_oracle, use_bridge=False)
    grids["with_oracle"], oracle_diag = _grids(paragraphs, pre_oracle, use_bridge=True)
    grids["with_frame_activation"], frame_diag = _grids(paragraphs, pre_frame, use_bridge=True)
    grids["with_frame_activation_scramble_kb"], scramble_diag = _grids(paragraphs, pre_scramble, use_bridge=True)

    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    unm = {arm: _unm(proxy[arm]) for arm in proxy}

    without_f1 = unm["without_knowledge"]["macro_f1"]
    oracle_f1 = unm["with_oracle"]["macro_f1"]
    frame_f1 = unm["with_frame_activation"]["macro_f1"]
    scramble_f1 = unm["with_frame_activation_scramble_kb"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]

    oracle_lift = oracle_f1 - without_f1
    frame_lift = frame_f1 - without_f1
    scramble_lift = scramble_f1 - without_f1
    survival = (frame_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    scramble_survival = (scramble_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    scramble_retained_fraction = (scramble_lift / frame_lift) if abs(frame_lift) > 1e-9 else (
        0.0 if abs(scramble_lift) < 1e-9 else float("inf"))

    diff = _arms_must_differ({
        "prior_lesion": grids["prior_lesion"], "without_knowledge": grids["without_knowledge"],
        "with_oracle": grids["with_oracle"], "with_frame_activation": grids["with_frame_activation"],
        "with_frame_activation_scramble_kb": grids["with_frame_activation_scramble_kb"],
    })

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff,
        "decode": {"lesion": lesion_diag["decode_fidelity"], "without": without_diag["decode_fidelity"],
                   "oracle": oracle_diag["decode_fidelity"], "frame_activation": frame_diag["decode_fidelity"],
                   "frame_activation_scramble_kb": scramble_diag["decode_fidelity"]},
        "unmentioned_subset": unm,
        "without_f1": without_f1, "with_oracle_f1": oracle_f1, "with_frame_activation_f1": frame_f1,
        "with_frame_activation_scramble_kb_f1": scramble_f1, "prior_lesion_f1": lesion_f1,
        "oracle_lift": oracle_lift, "frame_lift": frame_lift, "scramble_lift": scramble_lift,
        "survival_fraction": survival, "scramble_survival_fraction": scramble_survival,
        "scramble_retained_fraction": scramble_retained_fraction,
        "frame_minus_prior_lesion": frame_f1 - lesion_f1,
        "fact_coverage_frame_vs_oracle": cov, "fact_coverage_scramble_vs_oracle": cov_scr,
        "frame_sourcing_stats": frame_stats, "scramble_sourcing_stats": scramble_stats,
        "kb_hand_vet": kb["_meta"]["hand_vet_general_science"], "kb_n_processes": kb["_meta"]["n_processes"],
        "official": {arm: official[arm]["overall"] for arm in official},
        "literal_reference_TEST": {"survival": LITERAL_SURVIVAL_FLOOR_TEST, "pair_recall": LITERAL_PAIR_RECALL_TEST,
                                    "pair_precision": LITERAL_PAIR_PRECISION_TEST},
    }


# ============================================================================ verdict
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    survival = result["survival_fraction"]
    frame_lift = result["frame_lift"]
    without_f1 = result["without_f1"]
    frame_f1 = result["with_frame_activation_f1"]
    oracle_f1 = result["with_oracle_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = all(v >= 0.99 for v in result["decode"].values())
    infra_fail = (not arms_ok) or (not decode_ok)

    ablation_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING
    leak = (frame_f1 > LEAK_CEILING) or (frame_f1 >= oracle_f1 - LEAK_ORACLE_MARGIN)

    cov = result["fact_coverage_frame_vs_oracle"]
    recall_up = cov["pair_recall"] > LITERAL_PAIR_RECALL_TEST
    precision_up = cov["pair_precision"] > LITERAL_PAIR_PRECISION_TEST
    both_up = recall_up and precision_up

    scramble_retained = result["scramble_retained_fraction"]
    scramble_collapsed = (scramble_retained is not None) and (scramble_retained <= SCRAMBLE_MAX_RETAINED_FRACTION)

    survives = (survival is not None and survival >= FRAME_SURVIVAL_HARD_PASS)
    # "precision does not improve" is a HARD-FAIL guard specifically AGAINST a would-be pass that is
    # actually just a looser threshold finding more spurious matches (softer phone-book problem) --
    # it only fires when survival OTHERWISE clears the pass bar. When survival is genuinely in the
    # middle region, a precision-flat/recall-only (or vice versa) result is MIDDLE_BAND, not HARD_FAIL
    # (build-spec Section 3: "recall improves but precision doesn't (or vice versa) -- informative
    # split, localizes whether the residual is frame-IDENTIFICATION or ROLE-MAPPING specifically").
    residual_no_go = (survival is None) or (survival <= FRAME_SURVIVAL_HARD_FAIL)

    msg = (f"split={result['split']} FRAME_SURVIVAL={survival} (frame_lift={frame_lift:.4f} / "
           f"oracle_lift={result['oracle_lift']:.4f}) frame_f1={frame_f1:.4f} oracle_f1={oracle_f1:.4f} "
           f"without_f1={without_f1:.4f} pair_recall={cov['pair_recall']}(lit={LITERAL_PAIR_RECALL_TEST}) "
           f"pair_precision={cov['pair_precision']}(lit={LITERAL_PAIR_PRECISION_TEST}) "
           f"recall_up={recall_up} precision_up={precision_up} "
           f"scramble_retained_fraction={scramble_retained} scramble_collapsed={scramble_collapsed} "
           f"ablation_collapsed={ablation_collapsed} leak={leak} arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not ablation_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_ABLATION_DID_NOT_COLLAPSE_void: {msg}"
    if leak:
        return "HARD_FAIL", f"HARD_FAIL_LEAKED_ANSWERS_reject: {msg}"
    if survives and both_up and scramble_collapsed:
        return "HARD_PASS", f"HARD_PASS_GRADED_FRAME_ACTIVATION_BEATS_LITERAL_FLOOR_scramble_clean: {msg}"
    if survives and not scramble_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_SCRAMBLE_KB_DID_NOT_COLLAPSE_threshold_artifact_not_frame_content: {msg}"
    if survives and not precision_up:
        return "HARD_FAIL", f"HARD_FAIL_PRECISION_FLAT_SOFTER_PHONEBOOK_not_genuine_frame_match: {msg}"
    if residual_no_go:
        return "HARD_FAIL", f"HARD_FAIL_FRAME_ACTIVATION_DOES_NOT_BEAT_LITERAL_FLOOR_residual: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND_PARTIAL_{'recall_only' if recall_up and not precision_up else 'precision_only' if precision_up and not recall_up else 'mixed'}: {msg}"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": n, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def self_test() -> Dict:
    off_result = offeval.self_test()
    kb = _load_kb()
    assert kb["_meta"]["n_processes"] >= 12, kb["_meta"]

    # (1) mechanism-fires: graded matcher fires on a PARAPHRASE literal matching structurally
    # cannot -- 'blaze' (not in combustion signature) / 'timber' (not in combustion consumes).
    assert concept_similarity("blaze", "fire") is not None and concept_similarity("blaze", "fire") >= FRAME_SIM_THRESH
    assert concept_similarity("timber", "wood") is not None and concept_similarity("timber", "wood") >= ROLE_SIM_THRESH
    # over-link guard: same-domain-different-role must NOT clear ROLE_SIM_THRESH (wood must not bind
    # to the PRODUCE role via 'ash').
    assert concept_similarity("wood", "ash") < ROLE_SIM_THRESH

    frame_score, hits = _graded_frame_score({"blaze", "timber"}, kb["processes"]["combustion"]["signature"])
    assert frame_score is not None and hits >= 1, (frame_score, hits)
    literal_score = len(set(kb["processes"]["combustion"]["signature"]) & {"blaze", "timber"})
    assert literal_score == 0, "synth must be UNCATCHABLE by literal matching (both words absent from signature)"

    # synth paragraph: text uses ONLY paraphrases ('blaze' / 'timber') for the graded-only check,
    # AND supplies TWO DISTINCT participants filling TWO DISTINCT combustion roles (timber->consumes
    # via graded 'wood'; ash->produces, literal) so the CONVERGENCE GATE fires (coincidence detection
    # requires >= MIN_CONVERGENT_ROLES roles x >= MIN_CONVERGENT_FILLERS fillers). Literal matching
    # still gets ZERO signature hits from the paraphrases.
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["The blaze consumes the timber.", "Ash and soot form as the fuel burns.",
                             "The fire spreads through the pile.", "Only embers remain."],
         "participants": ["timber", "ash"],
         "states": [["-", "here", "here", "here", "-"], ["-", "-", "here", "here", "here"]]},
    ]
    graded_facts, graded_stats = _build_frame_activation_bridge_facts(synth, kb, scramble_kb=False)
    f = graded_facts[("s1", "timber")]
    assert "DESTROY" in f, (f, graded_stats)
    assert graded_stats["n_role_hits"] >= 1, graded_stats
    assert graded_stats["n_graded_only_role_hits"] >= 1, "mechanism-fires check FAILED: graded matcher found nothing literal wouldn't"
    assert graded_stats["n_donors_after_gate"] >= 1, ("CONVERGENCE GATE rejected the convergent combustion frame", graded_stats)

    # convergence-gate DISCRIMINATOR: the SAME text with only ONE participant ('timber', a lone
    # consumes-filler) supplies 1 role x 1 filler -- BELOW the gate -- so combustion MUST be gated
    # out and NO fate sourced. Proves the gate is a real coincidence detector (a lone promiscuous
    # role-word match is rejected), not a pass-through. (Any <2-participant paragraph can never reach
    # >=2 distinct fillers, so this is a guaranteed structural property of the gate.)
    if CONVERGENCE_GATE:
        synth_1p = [dict(synth[0], participants=["timber"], states=[synth[0]["states"][0]])]
        facts_1p, stats_1p = _build_frame_activation_bridge_facts(synth_1p, kb, scramble_kb=False)
        assert facts_1p[("s1", "timber")] == {}, ("gate should reject single-filler match", facts_1p, stats_1p)
        assert stats_1p["n_donors_after_gate"] == 0, stats_1p

    # scramble-KB-content control: on the SAME synth, a scrambled KB must NOT reproduce the hit
    # (combustion's role words get reassigned to a different process -> 'timber' no longer maps to
    # the DESTROY-mapped role of whatever process now occupies the combustion slot, by construction
    # extremely unlikely to coincidentally still hit).
    scr_facts, scr_stats = _build_frame_activation_bridge_facts(synth, kb, scramble_kb=True)
    # (not asserting scramble MUST miss on this single tiny synth -- that's a corpus-level statistical
    # claim, checked at full-corpus scale via scramble_retained_fraction; here we only assert the
    # scramble path runs, differs in content from the real KB, and is deterministic.)
    scr_facts_2, _ = _build_frame_activation_bridge_facts(synth, kb, scramble_kb=True)
    assert scr_facts == scr_facts_2, "GLASS-BOX FAILURE: scramble must be bit-identical across calls (deterministic seeding)"

    text = " ".join(synth[0]["sentence_texts"]); offs = []; cur = 0
    for s in synth[0]["sentence_texts"]:
        offs.append(cur); cur += len(s) + 1
    coref = {"s1": {"text": text, "sentence_offsets": offs, "n_sentences": 4, "clusters": []}}
    steps_df = build_step_rows(synth)
    oracle = _oracle_event_multiset(steps_df)
    pre = _paragraph_precompute(synth, oracle, coref, steps_df)
    pre_g = {"s1": {**pre["s1"], "bridge": {pp: graded_facts[("s1", pp)] for pp in synth[0]["participants"]}}}
    gd, dd = _grids(synth, pre_g, use_bridge=True)
    assert dd["decode_fidelity"] == 1.0
    assert "DESTROY" in gd["s1"]["timber"], gd["s1"]["timber"]

    # verdict-logic unit checks
    base = {"split": "x", "survival_fraction": 0.5, "frame_lift": 0.09, "oracle_lift": 0.11,
            "without_f1": 0.35, "with_frame_activation_f1": 0.42, "with_oracle_f1": 0.46,
            "arms_differ": {"all_differ": True}, "decode": {"a": 1.0},
            "fact_coverage_frame_vs_oracle": {"pair_recall": 0.30, "pair_precision": 0.15},
            "scramble_retained_fraction": 0.10}
    hv, hv_msg = decomposition_verdict(base)
    assert hv == "HARD_PASS", (hv, hv_msg)
    leak = dict(base); leak["with_frame_activation_f1"] = 0.46
    lv, _ = decomposition_verdict(leak)
    assert lv == "HARD_FAIL", lv
    scr_bad = dict(base); scr_bad["scramble_retained_fraction"] = 0.90
    sv, _ = decomposition_verdict(scr_bad)
    assert sv == "HARD_FAIL", sv  # scramble did NOT collapse -> reject even though survival cleared
    nogo = dict(base); nogo["survival_fraction"] = 0.15; nogo["frame_lift"] = 0.01
    nv, _ = decomposition_verdict(nogo)
    assert nv == "HARD_FAIL", nv
    void = dict(base); void["without_f1"] = 0.7
    vv, _ = decomposition_verdict(void)
    assert vv == "HARD_FAIL", vv
    mid = dict(base); mid["survival_fraction"] = 0.25
    mid["fact_coverage_frame_vs_oracle"] = {"pair_recall": 0.30, "pair_precision": 0.05}  # recall up, precision NOT up
    mv, _ = decomposition_verdict(mid)
    assert mv == "MIDDLE_BAND", mv

    return {"official_eval_fixtures": len(off_result["official_fixtures"]),
            "kb_n_processes": kb["_meta"]["n_processes"],
            "frame_score_synth": frame_score, "hits_synth": hits, "literal_score_synth": literal_score,
            "graded_facts_timber": {k: sorted(v) for k, v in f.items()}, "sourcing_stats": graded_stats,
            "with_frame_timber_labels": gd["s1"]["timber"],
            "lexicon_probe": {"blaze_fire": concept_similarity("blaze", "fire"),
                               "timber_wood": concept_similarity("timber", "wood"),
                               "wood_ash_overlink_guard": concept_similarity("wood", "ash")},
            "verdict_logic_unit_checks": {"hard_pass": hv, "leak": lv, "scramble_not_collapsed": sv,
                                           "no_go": nv, "void": vv, "middle_band": mv}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str)[:8000])
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    split = "dev" if args.smoke else "test"
    _write_start_marker(output_dir, run_mode, 1)
    t0 = time.time()
    train_paragraphs = _load_split("train")
    print(f"[{run_mode}] split={split} FRAME-ACTIVATION (graded concept-similarity) bridging test...", flush=True)
    result = run_decomposition(split, train_paragraphs)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "FRAME_SURVIVAL_FRACTION": result["survival_fraction"],
            "SCRAMBLE_SURVIVAL_FRACTION": result["scramble_survival_fraction"],
            "SCRAMBLE_RETAINED_FRACTION": result["scramble_retained_fraction"],
            "with_frame_activation_f1": result["with_frame_activation_f1"],
            "with_frame_activation_scramble_kb_f1": result["with_frame_activation_scramble_kb_f1"],
            "with_oracle_f1": result["with_oracle_f1"], "without_f1": result["without_f1"],
            "prior_lesion_f1": result["prior_lesion_f1"],
            "frame_lift": result["frame_lift"], "oracle_lift": result["oracle_lift"],
            "frame_minus_prior_lesion": result["frame_minus_prior_lesion"],
            "frame_pair_recall": result["fact_coverage_frame_vs_oracle"]["pair_recall"],
            "frame_pair_precision": result["fact_coverage_frame_vs_oracle"]["pair_precision"],
            "literal_reference_TEST": result["literal_reference_TEST"],
            "frame_sourcing_stats": result["frame_sourcing_stats"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: FRAME_SIM_THRESH/ROLE_SIM_THRESH DEV-pinned "
                              "on lexicon self-test evidence; discriminator-fires re-verified in self_test()",
        "thresholds": {"FRAME_SURVIVAL_HARD_PASS": FRAME_SURVIVAL_HARD_PASS,
                       "FRAME_SURVIVAL_HARD_FAIL": FRAME_SURVIVAL_HARD_FAIL,
                       "SCRAMBLE_MAX_RETAINED_FRACTION": SCRAMBLE_MAX_RETAINED_FRACTION,
                       "FRAME_SIM_THRESH": FRAME_SIM_THRESH, "ROLE_SIM_THRESH": ROLE_SIM_THRESH,
                       "LEAK_CEILING": LEAK_CEILING, "LEAK_ORACLE_MARGIN": LEAK_ORACLE_MARGIN,
                       "WITHOUT_COLLAPSE_CEILING": WITHOUT_COLLAPSE_CEILING},
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "result"}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
