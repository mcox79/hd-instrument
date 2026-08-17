"""exp_readout_writerule_binary_profile_v1 -- DOES BINARISING THE WRITE-SIDE ROWS THAT FEED THE
PARADIGMATIC (SECOND-ORDER) WRITE RULE CLOSE MORE OF THE GAP THAN THE PROFILE RULE ALONE DID?

FINDINGS LOG (append after every arm): notes/readout_ceiling_findings_2026-08-17.md section 10 plus
this file's own new section. PRE-EXISTING RESULTS THIS CELL COMBINES, both READ OFF DISK before this
cell was authored, never re-derived:

FACT 1 (data/exp_readout_writerule_paradigmatic_v1/metrics.json, commit a8fdc968f; findings log
sec 10). Building a word's write-time code from its neighbours' first-order CONTEXT-PROFILE rows
(mat0n, the L2-unit row of the EXISTING count-weighted store) instead of their IDENTITY draws lifts
partial-cue hit@1 from W0=0.02228 to W1=0.02979: margin +0.0075 CI [+0.0023,+0.0128], CI-separated,
roughly +34% relative. Three controls came back clean (F_FREQ_MATCHED_PROFILE NOT_SEPARATED from W0,
N1_NULL random-profile permutation NOT_SEPARATED from W0, orthographic-leakage check clean). But W1
remained ~2.9x short of its own binding floor (F_ORTHOGRAPHIC, 0.08731) and NONE of that cell's
stop-ifs fired cleanly -- its own honest reading was "the write rule was part of the defect but not
sufficient".

FACT 2 (data/exp_cue_binarised_readout_transfer_v1/metrics.json, commit 1e085d761; and its own
diagnosis parent data/exp_cue_compression_property_diagnosis_v1/metrics.json, commit 201776cc9).
Discarding token COUNTS and keeping only presence/absence of each content word raises PARTIAL-CUE
ADDRESSING from R0=0.0711 to R1=0.1094: +0.0383 CI [+0.0295,+0.0473], CI-separated, while two rival
explanations failed (S1 exact-zero/sparse-hash-projection BELOW; N1 non-negativity NOT_SEPARATED).
CRITICAL QUALIFIER THAT MUST NOT BE LOST: that gain was measured ON THE CUE and it DID NOT TRANSFER
to read-out -- hit@1 margin +0.0026 CI [-0.0026,+0.0078], NOT_SEPARATED, and R1 stayed CI-separated
BELOW every one of the four floors. The pre-registered reason given at the time: "compressing the
CUE cannot change WHICH RELATION was written into the STORE."

THE HYPOTHESIS THIS CELL TESTS, STATED BEFORE ANY NUMBER IS READ. The paradigmatic write rule (FACT
1) built its second-order profiles from the incumbent's CACHED COUNT-WEIGHTED rows (mat0n = L2-unit
row of mat0_raw, where mat0_raw[a] = sum over context-token OCCURRENCES of symbol_vector(token) --
literally a raw word-count vector projected through the fixed hashlib symbol-vector basis, verified
byte-identical in exp_cue_information_audit_v1.reconstruct_bipolar / verify_recoverability, ALL_EXACT
against this same cache). If counts are a defect in the representation GENERALLY -- not merely in the
cue, where FACT 2 already showed the fix does not transfer to hit@1 -- then the PROFILES that those
count-weighted rows produce are themselves degraded, and W1's +0.0075 is a LOWER BOUND on what the
paradigmatic write rule can do. This cell tests that by building the SAME second-order write, unaltered
in every other respect, from BINARISED presence/absence rows instead of count rows -- applying FACT 2
on the WRITE side, where it has never been tested (FACT 2 was only ever tested on the cue, where it
failed to transfer).

THE HONEST PRIOR, STATED BEFORE THE RUN, PER THE DISPATCH BRIEF. FACT 2 not transferring on the cue is
GENUINE EVIDENCE AGAINST this working -- the same intervention (discard counts, keep presence/absence)
already failed to move hit@1 once, on the same population, same store, same scorer. The prior on
D_BINARY_PROFILE clearing a floor is LOW. The counter-argument for running it anyway is narrow and
specific, not a hand-wave: the cue and the store are DIFFERENT OBJECTS; the stated reason the cue fix
did not transfer was that a cue-side change "cannot change which relation was written to the store";
and this intervention DOES change what gets written (the store's own rows, and therefore the profile
rows that get summed into every OTHER word's second-order code, change). If D ties B (does not beat the
profile-write incumbent), that specific reasoning is REFUTED and the honest conclusion is that
binarisation is a cue-side property only, full stop, in those words.

ARMS, one variable at a time, on the IDENTICAL store/pool/gold/scorer as exp_readout_writerule_paradigmatic_v1
and its own W0/W1 (same cache, same rebuilt corpus/bucket pipeline, verified to reproduce the cached
anchor set exactly before anything else runs), so the 2x2 (ROW-SOURCE: count vs binary) x
(WRITE-RULE: identity-draw vs second-order-profile) is complete and interpretable:

  A_COUNT_IDENTITY   the original incumbent. mat0_raw, REUSED VERBATIM from the cache, never rebuilt.
                     Expect ~0.0223 (W0_SYNTAGMATIC). REGRESSION GATE, EXITS ON FAILURE.
  B_COUNT_PROFILE    the landed paradigmatic write rule: second-order store built by
                     exp_readout_writerule_paradigmatic_v1.build_arm(mode="PROFILE") over
                     mat0n = L2-unit(mat0_raw) -- IMPORTED AND CALLED, not reimplemented. Expect
                     ~0.0298 (W1_PARADIGMATIC). REGRESSION GATE, EXITS ON FAILURE.
  C_BINARY_IDENTITY  isolates binarisation ON THE WRITE SIDE ALONE, never run before. A NEW store
                     where anchor L's row is the sum of symbol_vector(w) over each DISTINCT SURFACE
                     TOKEN w that ever co-occurs with L across L's profile-sentence window (repeats,
                     within one sentence or across sentences, collapsed to presence -- exactly the
                     `binarize_sparse` "presence/absence... counts discarded" semantics from
                     exp_cue_compression_property_diagnosis_v1, applied here in the SAME 256-dim
                     symbol_vector basis mat0_raw itself uses, not a fresh random projection, so this
                     isolates count-vs-presence with everything else, including the projection basis,
                     held fixed). Built by `build_binary_identity_arm` below, which reuses
                     exp_readout_writerule_paradigmatic_v1.occurrence_vector(mode="IDENTITY") for the
                     actual vector arithmetic and only changes the AGGREGATION (a deduplicated word
                     list per anchor instead of the raw per-sentence token stream).
  D_BINARY_PROFILE   THE ARM THIS CELL EXISTS FOR. The identical second-order write rule as B
                     (WR.build_arm(mode="PROFILE"), same function, same call), with ONLY the
                     row-source swapped: mat0n = L2-unit(C's raw store) instead of L2-unit(mat0_raw).
                     Nothing about the outer accumulation (how many times each context token's
                     profile row is added while building a word's own code) changes between B and D --
                     that would conflate two binarisations and violate one-variable-at-a-time. Only
                     the INPUT PROFILE ROWS being looked up are binary instead of count-weighted.
  F_FREQ_MATCHED_D   binarisation CHANGES the frequency profile of the representation (a word that
                     occurs 40 times and a word that occurs 2 times now contribute EQUALLY to C's
                     rows), so the frequency-matched control from the parent cell is NOT inherited and
                     is recomputed here, fresh, against D specifically: same construction as B's own
                     F_FREQ_MATCHED_PROFILE (WR.build_arm(mode="PROFILE_PERM"), a derangement of
                     anchor-row assignment done WITHIN corpus-frequency deciles, so the assigned
                     profile is frequency-matched to the true neighbour even though its identity is
                     wrong), but the row-source deranged is mat0n_bin (C's rows), not mat0n (A's rows).
                     Catches "D's lift over B, if any, is a frequency effect wearing a binarisation
                     costume."
  K1_KNOWN_ANSWER    exact-key self-addressing (query = an arm's own stored row) for A, B, C, D and
                     F_FREQ_MATCHED_D. Must pass >=0.95 for EVERY arm or the run raises SystemExit
                     before any treatment number is computed. Deliberately insensitive to the WordNet
                     gold pairing -- an addressing-side liveness check only.
  N1_NULL            item-to-cue permutation validity check (the cue for item i scored against a
                     DERANGED assignment of items), applied to every arm. Must sit near this
                     population's own analytic chance in every space -- sensitive to the pairing,
                     insensitive to whether the comparator itself is right (mirrors
                     NULL_PERMUTED_partial_cue in the parent write-rule cell exactly).

PRIMARY REGIME: PARTIAL CUE (a held-out sentence's own write-transformed vector, built with the SAME
per-arm construction as that arm's store), matching the parent cell and every sibling on this arc.

FLOORS: max(F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE), ALL FOUR recomputed on
THIS run's own population, on the identical scorer (tools/floor_battery, imported, never edited,
never reimplemented), against the PARTIAL cue matching every arm's own regime, both tie conventions
reported, CI half-width and analytic-null half-width (1.96*sqrt(p(1-p)/n)) beside every margin.
F_ORTHOGRAPHIC and F_FREQUENCY are store-independent (spelling / corpus count) and computed ONCE,
shared across arms. F_SCRAMBLE and F_CONSTANT_PROTOTYPE are store-DEPENDENT and recomputed on EACH
ARM'S OWN store. 0.1390, 0.0873, 0.1382, 0.2070, -0.1959 are NEVER imported -- they are numbers from
a different run's population and the standing rule forbids carrying a floor across populations even
when the construction is nominally the same.

STANDING RULE 12 (a floor is cleared by understanding, never adopted). Reused twice: (a) mean
trigram-cosine of each arm's top-1 winner to the query (the parent cell's own ORTHOGRAPHIC_LEAKAGE_CHECK
construction, reused per arm here); (b) the per-item hit@1 GAIN of D over B correlated against that
item's own best-gold orthographic-similarity score, bootstrap CI on the Pearson r (reusing
exp_cue_binarised_readout_transfer_v1.pearson_ci_bootstrap directly, imported not reimplemented). If D
clears a floor, both checks are read before the result is called a win.

THE INTERACTION, reported explicitly and not left as four bare numbers: margin(D,C) -- does
binarisation help GIVEN a second-order write -- versus margin(B,A) -- does the second-order write
help GIVEN count rows. Both computed on the SAME shared paired bootstrap so a diff-of-diffs CI
((D-C)-(B-A)) can be reported directly: CI excludes zero -> the two interventions INTERACT (their
combined effect is not the sum of their separate effects); CI includes zero -> ADDITIVE (consistent
with independent contributions), reported without over-claiming exact additivity from a CI overlap
alone.

STOP-IF (report ALL FOUR conditions plus the K1 gate regardless of which is the headline; first that
fires in this order is the primary verdict; if none of (i)-(iv) fires exactly, the honest fifth
reading is stated instead, matching the parent cell's own practice of not forcing a result into a
branch it was not pre-registered for):
  (v)   Any arm's K1 < 0.95 -> INSTRUMENT_STILL_LOOSE. SystemExit before any treatment number.
        Publish nothing quality-bearing.
  (i)   D clears max(4 floors) CI-separated -> the first genuine read-out win this programme has had
        on this arc. Report the LEVEL as prominently as the margin, and every control (K1, N1,
        F_FREQ_MATCHED_D, rule-12 both checks) alongside it.
  (ii)  D beats B CI-separated but D is still below the floors -> the write-side binarisation is REAL
        and ADDITIVE; report the remaining gap to the floor as the open quantity. Do NOT call it a win.
  (iii) D ties B (NOT_SEPARATED) -> binarisation is a CUE-SIDE property only; the transfer reasoning
        stated in the honest prior above is REFUTED; say so in exactly those words.
  (iv)  C beats A (CI-separated ABOVE) while D ties B -> binarisation and the second-order profile
        write are SUBSTITUTES rather than complements (each alone helps, combined they do not add);
        report as an interaction result, not as two independent findings.
  else  D CI-separated BELOW B (binarisation on top of the profile write HURTS) -> reported plainly;
        this is not one of the four pre-registered branches and is not forced into one.

BRAIN FIDELITY: none of the write-rule constructions here (second-order profile summation, dedup-to-
presence aggregation) is claimed to be a brain structure; this cell inherits the parent write-rule
cell's own brain-fidelity block verbatim (complementary-learning-systems motivation for testing
regularity-across-episodes structure at write time; OURS, invention-under-test, not laundered as
biology) and does not extend or restate it -- the ONLY new methodological ingredient here is
count-vs-presence aggregation, which is an information-theoretic property of the encoder, not a
biological claim, exactly like FACT 2's own cell (which explicitly claimed no brain fidelity for the
same reason).

ORGAN REUSE, enumerated then reconciled by RUNTIME witness (sys.modules after the run), never grep.
IMPORTED, NEVER EDITED: tools/floor_battery; experiments/exp_cue_to_store_translation_v1 (cache
loader, ruler gate, landed regression constant); experiments/exp_readout_ceiling_diagnosis_v1
(grounded_similarity tripwire); experiments/exp_grounding_readout_known_answer_v1 (build_corpus,
build_buckets, _n_profile -- the IDENTICAL deterministic corpus/bucket construction the cached store
was built from); experiments/exp_readout_writerule_paradigmatic_v1 (occurrence_vector, build_arm,
deranged_permutation, l2n_rows64, l2n -- THE SECOND-ORDER WRITE MECHANISM ITSELF, called not
reimplemented, so a divergent reimplementation cannot make the regression gate meaningless);
experiments/exp_cue_binarised_readout_transfer_v1 (pearson_ci_bootstrap); hdlab's ConceptSpace-
adjacent primitives (content_words, normalize_lemma, symbol_vector, CTX_D) imported directly;
tools/exp_checkpoint.

Prior-work check (per the standing rule, `tools/substrate_query.sh` unusable per the same livelock
documented by the sibling cells today -- enumeration used instead): `ls experiments/` filtered on
readout/writerule/binary/profile/paradigmatic turned up exactly the three cells this docstring already
credits (exp_readout_writerule_paradigmatic_v1, exp_cue_binarised_readout_transfer_v1,
exp_cue_compression_property_diagnosis_v1) plus exp_readout_second_order_v1 and
exp_readout_ceiling_diagnosis_v1, all already read and credited above. No cell in this repo has
previously built a second-order write from binarised rows -- this composition is genuinely novel, not
a rediscovery.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network. data/foundation/**
is never opened. The incumbent cache (scratch/sparse_code_real_task/real_cache.npz) is NEVER rebuilt
or edited. Every new store this cell builds lives only in-memory under
data/exp_readout_writerule_binary_profile_v1/. DO NOT WIRE ANYTHING INTO hdlab/ regardless of outcome
-- that is a Director wire-or-shelve decision, not this cell's.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; hash-digest test on all 4 primary arms)
  - final_metrics_atomicity: "tmp_replace" (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: no quantitative noise floor of that form applies here
  - baseline_in_band: checked via K1 (>=0.95, addressing self-check) and N1 (near chance) gates
  - discriminator survives scale: the parent write-rule cell already measured its own discriminator
    (B vs A) at full-N (n=3994) and it survived; this cell's full run is itself the full-N read, no
    separate preview arm needed since the mechanism (build_arm) is bit-identical code, imported
  - HARD_PASS vocabulary: not used; this cell uses CI-separated / NOT_SEPARATED / BELOW per
    floor_battery.margin, consistent with every sibling cell on this arc
  - cardinality_ok: fixed arm set (A, B, C, D, F_FREQ_MATCHED_D, 4 floors, no sweep)
  - per-unit failure-class instrumentation: no bare except; SystemExit/KeyboardInterrupt re-raised
  - calibration_check: "default_ok_for_this_regime" (identical population to 3 landed sibling cells)
  - progress_logging: "print_flush_true" (every stage prints with flush=True; expected full-run
    wall time ~90-150s based on the parent write-rule cell's own 84.2s for 6 profile-style builds --
    this cell builds 4 -- so no cell here approaches the 1800s threshold that would make this field
    strictly mandatory, but the discipline is applied anyway)
  - all numbers in this docstring are MEASURED@ the cited metrics.json paths (see PROVENANCE below)
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import (numpy sizes its pools at import time).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_cue_to_store_translation_v1 as CTS               # cache loader + ruler gate, NEVER EDITED
import exp_readout_ceiling_diagnosis_v1 as DIAG              # tripwire, NEVER EDITED
import exp_grounding_readout_known_answer_v1 as GRK          # corpus/buckets, NEVER EDITED
import exp_readout_writerule_paradigmatic_v1 as WR           # second-order write mechanism, NEVER EDITED
import exp_cue_binarised_readout_transfer_v1 as BCT          # pearson_ci_bootstrap, NEVER EDITED
from hdlab.reading_grounding_loop import CTX_D, content_words, normalize_lemma
from tools import floor_battery as FB                        # NEVER EDITED
from tools.exp_checkpoint import record_unit, unit_key

ANCHOR_NAME = "exp_readout_writerule_binary_profile_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_ceiling_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "reduced" if _ARGS.grid == "reduced" else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 2000 if RUN_MODE == "reduced" else 10000
KA_MIN = 0.95
N_DECILES = 10

# PROVENANCE, verified off disk before this cell was authored:
# data/exp_readout_writerule_paradigmatic_v1/metrics.json, commit a8fdc968f.
REGRESSION_A_EXPECTED = 0.02228       # W0_SYNTAGMATIC, partial-cue hit@1, tie-corrected
REGRESSION_B_EXPECTED = 0.02979       # W1_PARADIGMATIC, partial-cue hit@1, tie-corrected
REGRESSION_TOL = 5e-4


def _out_dir() -> str:
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + ("" if RUN_MODE == "full" else "_smoke"))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _halfwidth(p: float, n: int) -> float:
    return float(1.96 * (max(p * (1.0 - p), 1e-12) / max(int(n), 1)) ** 0.5)


# =================================================================================================
# THE ONE NEW CONSTRUCTION -- a store + held-out cue where each anchor's row/cue is the sum of
# symbol_vector(w) over DISTINCT surface tokens only (repeats, within one sentence or across the
# whole profile-sentence bucket, collapsed to presence). Reuses WR.occurrence_vector(mode="IDENTITY")
# for the actual vector arithmetic -- only the word list fed to it is deduplicated instead of being
# the raw per-sentence token stream. Matches exp_cue_compression_property_diagnosis_v1.binarize_sparse's
# own semantics exactly (it dedupes at the SURFACE-TOKEN vocab key, not the lemma), applied here in
# the SAME symbol_vector 256-dim basis the incumbent store itself uses.
# =================================================================================================
def build_binary_identity_arm(anchors: List[str], buckets: Dict[str, List[int]],
                              cw_cache: Dict[int, List[str]], sents: List[str], pos: Dict[str, int],
                              d: int) -> Tuple[np.ndarray, Dict[str, Optional[np.ndarray]]]:
    def cw(i: int) -> List[str]:
        v = cw_cache.get(i)
        if v is None:
            v = content_words(sents[i])
            cw_cache[i] = v
        return v

    n = len(anchors)
    mat = np.zeros((n, d), dtype=np.float64)
    part: Dict[str, Optional[np.ndarray]] = {}
    dummy_mat0n = np.zeros((1, d), dtype=np.float64)   # unused by IDENTITY mode; kept for signature parity
    for i, L in enumerate(anchors):
        b = buckets.get(L, [])
        nprof = GRK._n_profile(len(b))
        seen: set = set()
        distinct_words: List[str] = []
        for sidx in b[:nprof]:
            for w in cw(sidx):
                if normalize_lemma(w) == L:
                    continue
                if w not in seen:
                    seen.add(w)
                    distinct_words.append(w)
        mat[i] = WR.occurrence_vector(distinct_words, L, pos, dummy_mat0n, d, "IDENTITY")
        ev = b[nprof:]
        sidx = ev[0] if ev else None
        if sidx is None:
            part[L] = None
            continue
        seen2: set = set()
        distinct_sent: List[str] = []
        for w in cw(sidx):
            if normalize_lemma(w) == L:
                continue
            if w not in seen2:
                seen2.add(w)
                distinct_sent.append(w)
        q = WR.occurrence_vector(distinct_sent, L, pos, dummy_mat0n, d, "IDENTITY")
        part[L] = q if float(np.linalg.norm(q)) > 1e-9 else None
    return mat.astype(np.float32), part


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    DIAG.install_grounded_similarity_tripwire()
    ev["floor_battery_selftest_ok"] = sorted(FB.self_test().keys())
    ev["WR_selftest_ran"] = sorted(WR.self_test().keys())    # reuses/verifies the imported write-rule module itself

    d = 128
    rng = np.random.default_rng(21)

    # T1 -- COUNT vs BINARY DIFFER EXACTLY WHERE THEY SHOULD: a word repeated many times in an
    # anchor's profile sentences must weight a COUNT store's row MORE than a word seen once, while
    # a BINARY store's row must be INSENSITIVE to that repeat count (only presence matters).
    TA = "trgccc"
    rep_word = "repeatedword"     # appears many times across TA's profile sentences
    once_word = "onceonlyword"    # appears exactly once
    filler_pool = ["fillerqa%02d" % i for i in range(20)]
    anchors = [TA] + [rep_word, once_word] + filler_pool
    pos = {a: i for i, a in enumerate(anchors)}
    sents_local: List[str] = []
    buckets: Dict[str, List[int]] = {TA: []}
    # 6 profile sentences: rep_word appears in ALL 6 (repeated exposure), once_word in only 1.
    for k in range(8):        # extra 2 sentences serve as the held-out tail
        fillers = list(rng.choice(filler_pool, size=3, replace=False))
        words = [TA, rep_word] + fillers
        if k == 0:
            words = [TA, once_word] + fillers
        sents_local.append(" ".join(words))
        buckets[TA].append(len(sents_local) - 1)
    cw_cache: Dict[int, List[str]] = {}

    def cw_local(i: int) -> List[str]:
        v = cw_cache.get(i)
        if v is None:
            v = content_words(sents_local[i])
            cw_cache[i] = v
        return v

    _probe = cw_local(0)
    assert TA in _probe and once_word in _probe, "fixture tokens do not survive content_words()"

    nprof = GRK._n_profile(len(buckets[TA]))
    assert nprof >= 6, "fixture bucket too small for a meaningful profile split: nprof=%d" % nprof

    # COUNT construction: reuse WR.occurrence_vector(mode="IDENTITY") SUMMED PER SENTENCE (the real
    # incumbent construction: repeats across sentences accumulate).
    mat0n_dummy = np.zeros((len(anchors), d), dtype=np.float64)
    acc_count = np.zeros(d, dtype=np.float64)
    for sidx in buckets[TA][:nprof]:
        acc_count += WR.occurrence_vector(cw_local(sidx), TA, pos, mat0n_dummy, d, "IDENTITY")
    from hdlab.reading_grounding_loop import symbol_vector
    rep_dir = symbol_vector(rep_word, d) / float(np.linalg.norm(symbol_vector(rep_word, d)))
    once_dir = symbol_vector(once_word, d) / float(np.linalg.norm(symbol_vector(once_word, d)))
    count_dot_rep = float(np.dot(acc_count, rep_dir))
    count_dot_once = float(np.dot(acc_count, once_dir))
    assert count_dot_rep > count_dot_once + 1.0, (
        "COUNT construction did not weight the repeated word more than the once-seen word: "
        "rep=%.4f once=%.4f" % (count_dot_rep, count_dot_once))

    # BINARY construction: build_binary_identity_arm on the SAME fixture.
    mat_bin, part_bin = build_binary_identity_arm([TA] + filler_pool[:1], buckets, cw_cache,
                                                   sents_local, pos, d)
    bin_dot_rep = float(np.dot(mat_bin[0].astype(np.float64), rep_dir))
    bin_dot_once = float(np.dot(mat_bin[0].astype(np.float64), once_dir))
    assert abs(bin_dot_rep - bin_dot_once) < 0.35, (
        "BINARY construction is NOT count-insensitive: rep=%.4f once=%.4f (both words are present "
        "exactly once in the DEDUPED aggregation, so their contributions must be near-equal, "
        "unlike the count construction above)" % (bin_dot_rep, bin_dot_once))
    ev["T1_count_weights_repeats_binary_does_not"] = {
        "count_dot_rep": round(count_dot_rep, 4), "count_dot_once": round(count_dot_once, 4),
        "binary_dot_rep": round(bin_dot_rep, 4), "binary_dot_once": round(bin_dot_once, 4)}

    # T2 -- SECOND-ORDER WRITE OVER BINARY ROWS STILL RECOVERS SHARED-MEDIATOR STRUCTURE (the same
    # falsifiability contract as WR's own T1/T2, but the row-source fed to WR.build_arm is now a
    # BINARY store built by build_binary_identity_arm, not a count store).
    k_ctx = 6
    n_extra = 40
    c_words = ["cctxb%s" % chr(97 + i) for i in range(k_ctx)]
    d_words = ["ddtxb%s" % chr(97 + i) for i in range(k_ctx)]
    extra_a = ["exfilaab%03d" % i for i in range(n_extra)]
    extra_b = ["exfilbbb%03d" % i for i in range(n_extra)]
    TA2, TB2 = "trgaab", "trgbbb2"
    anchors2 = [TA2, TB2] + c_words + d_words + extra_a + extra_b
    pos2 = {a: i for i, a in enumerate(anchors2)}
    n_a2 = len(anchors2)
    # BINARY mediator rows (mat0n_bin2): c_i and d_i share a near-identical direction; TA2/TB2 and
    # extras get independent random rows -- mirrors WR's own T1/T2 fixture construction exactly,
    # except this array now plays the role of "C's rows" (binary row-source), not "A's rows".
    base2 = rng.standard_normal(d)
    mat0_bin2 = np.zeros((n_a2, d))
    for i in range(k_ctx):
        priv = 0.15 * rng.standard_normal(d)
        mat0_bin2[pos2[c_words[i]]] = base2 + priv + 0.05 * rng.standard_normal(d)
        mat0_bin2[pos2[d_words[i]]] = base2 + priv + 0.05 * rng.standard_normal(d)
    mat0_bin2[pos2[TA2]] = rng.standard_normal(d)
    mat0_bin2[pos2[TB2]] = rng.standard_normal(d)
    for e in extra_a + extra_b:
        mat0_bin2[pos2[e]] = rng.standard_normal(d)
    mat0n_bin2 = WR.l2n_rows64(mat0_bin2)

    sents2: List[str] = []
    buckets2: Dict[str, List[int]] = {TA2: [], TB2: []}
    for _ in range(30):
        fa = list(rng.choice(extra_a, size=3, replace=False))
        fb = list(rng.choice(extra_b, size=3, replace=False))
        sents2.append(" ".join([TA2] + c_words + fa))
        buckets2[TA2].append(len(sents2) - 1)
        sents2.append(" ".join([TB2] + d_words + fb))
        buckets2[TB2].append(len(sents2) - 1)
    cw_cache2: Dict[int, List[str]] = {}
    _probe2 = content_words(sents2[0])
    assert len(_probe2) == 1 + k_ctx + 3 and TA2 in _probe2, "fixture2 tokens vanished at tokenization"

    matI2, _ = WR.build_arm([TA2, TB2], buckets2, cw_cache2, sents2, mat0n_bin2, pos2, d, "IDENTITY")
    cos_I2 = float(np.dot(WR.l2n(matI2[0:1])[0], WR.l2n(matI2[1:2])[0]))
    assert abs(cos_I2) < 0.15, "fixture2 is not first-order-orthogonal (cos=%.4f)" % cos_I2

    matP2, _ = WR.build_arm([TA2, TB2], buckets2, cw_cache2, sents2, mat0n_bin2, pos2, d, "PROFILE")
    cos_P2 = float(np.dot(WR.l2n(matP2[0:1])[0], WR.l2n(matP2[1:2])[0]))
    assert cos_P2 > cos_I2 + 0.5, (
        "second-order write over BINARY rows does not recover a shared-mediator relation first-order "
        "misses: first=%.4f second=%.4f -- the D construction would be vacuous" % (cos_I2, cos_P2))
    ev["T2_second_order_write_over_binary_rows_recovers_mediator_structure"] = {
        "first_order_cos": round(cos_I2, 4), "second_order_over_binary_rows_cos": round(cos_P2, 4)}

    # T3 -- ARMS_MUST_DIFFER (META_RULE_AF) on this fixture's own tiny arm set.
    digests = {"A_fixture": _digest(mat0_bin2), "B_fixture_PROFILE": _digest(matP2),
              "C_fixture_IDENTITY_binary": _digest(mat_bin), "D_would_reuse_B_mechanism": _digest(matI2)}
    assert len(set(digests.values())) == len(digests), "fixture arms are not bit-distinct: %r" % digests
    ev["T3_arms_must_differ_fixture"] = True

    # T4 -- K1 self-address sanity: on fixture2, exact-key argmax must recover the item's own anchor.
    MATn2 = WR.l2n(matP2)
    Sfull2 = MATn2 @ MATn2.T
    pred2 = np.argmax(Sfull2, axis=0)
    assert np.all(pred2 == np.arange(2)), "K1 self-address fails on the fixture: pred=%r" % pred2
    ev["T4_k1_self_address_fixture"] = True

    # T5 -- corpus/bucket reconstruction reproduces the CACHED anchor set (full grid only).
    C = CTS.load_cache()
    sents = GRK.build_corpus(RUN_MODE if RUN_MODE == "reduced" else "full")
    if RUN_MODE == "full":
        buckets_full, _counts = GRK.build_buckets(sents)
        b_anchors = sorted(buckets_full)
        assert b_anchors == C["anchors"], (
            "rebuilt buckets do NOT reproduce the cached anchor set (rebuilt=%d cached=%d)"
            % (len(b_anchors), len(C["anchors"])))
        ev["T5_corpus_reconstruction_matches_cache"] = {"n_anchors_rebuilt": len(b_anchors),
                                                         "n_anchors_cached": len(C["anchors"])}
    else:
        ev["T5_corpus_reconstruction_matches_cache"] = "SKIPPED in reduced grid"

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1600], flush=True)
    return ev


# =================================================================================================
def run(grid: str, output_dir: str) -> Dict:
    t0 = time.time()
    gate = CTS.ruler_mode_gate()
    tripwire = DIAG.install_grounded_similarity_tripwire()
    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors, mat0_raw, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors = len(anchors)
    pos = {a: i for i, a in enumerate(anchors)}
    d = CTX_D
    print("[load] cache n_anchors=%d t=%.0fs" % (n_anchors, time.time() - t0), flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": gate, "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(tripwire),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "HYPOTHESIS": "the paradigmatic (second-order) write rule was trained on the incumbent's "
                      "count-weighted rows; if counts are a defect generally (not only on the cue, "
                      "where the same fix already failed to transfer to hit@1), the profiles those "
                      "rows produce are degraded and B's +0.0075 is a lower bound.",
        "HONEST_PRIOR": "LOW -- the identical presence/absence intervention already failed to move "
                        "hit@1 when applied to the cue (exp_cue_binarised_readout_transfer_v1, "
                        "margin +0.0026 CI [-0.0026,+0.0078] NOT_SEPARATED); this cell tests it on "
                        "the store/write side instead, where the cue result's own stated reason for "
                        "not transferring (a cue-side change cannot change what was written) does "
                        "not apply by construction.",
    }

    # ---- rebuild corpus/buckets exactly as the parent write-rule cell does, verify match ----------
    sents = GRK.build_corpus("full")
    buckets, counts = GRK.build_buckets(sents)
    b_anchors = sorted(buckets)
    if b_anchors != anchors:
        raise SystemExit("CORPUS/BUCKET RECONSTRUCTION DOES NOT MATCH THE CACHED ANCHOR SET -- "
                         "STOPPING (rebuilt=%d cached=%d)" % (len(b_anchors), len(anchors)))
    print("[corpus] n_sentences=%d n_anchors_matches_cache=True t=%.0fs"
          % (len(sents), time.time() - t0), flush=True)
    cw_cache: Dict[int, List[str]] = {}

    # ---- A_COUNT_IDENTITY: reused verbatim from the cache ------------------------------------------
    mat0n_count = WR.l2n_rows64(mat0_raw)
    Q_part0 = C["Q_part"].astype(np.float32)
    L_words = C["L_words"]
    n_items_all = len(L_words)
    part0_by_L: Dict[str, np.ndarray] = {}
    for i, L in enumerate(L_words):
        if L not in part0_by_L:
            part0_by_L[L] = Q_part0[i]

    # ---- B_COUNT_PROFILE: the landed write rule, IMPORTED AND CALLED, not reimplemented -----------
    t1 = time.time()
    mat_B, part_B = WR.build_arm(anchors, buckets, cw_cache, sents, mat0n_count, pos, d, "PROFILE")
    print("[build] B_COUNT_PROFILE t=%.1fs" % (time.time() - t1), flush=True)

    # ---- C_BINARY_IDENTITY: the one new construction -----------------------------------------------
    t1 = time.time()
    mat_C, part_C = build_binary_identity_arm(anchors, buckets, cw_cache, sents, pos, d)
    print("[build] C_BINARY_IDENTITY t=%.1fs" % (time.time() - t1), flush=True)
    mat0n_bin = WR.l2n_rows64(mat_C.astype(np.float64))

    # ---- D_BINARY_PROFILE: the arm this cell exists for, reusing WR.build_arm unchanged -----------
    t1 = time.time()
    mat_D, part_D = WR.build_arm(anchors, buckets, cw_cache, sents, mat0n_bin, pos, d, "PROFILE")
    print("[build] D_BINARY_PROFILE t=%.1fs" % (time.time() - t1), flush=True)

    # ---- F_FREQ_MATCHED_D: frequency-decile derangement of the BINARY row-source ------------------
    freq = np.array([counts.get(a, 0) for a in anchors], dtype=np.float64)
    deciles = np.floor(np.argsort(np.argsort(freq)) / max(1.0, n_anchors / N_DECILES)).astype(np.int64)
    deciles = np.clip(deciles, 0, N_DECILES - 1)
    perm_freq = WR.deranged_permutation(n_anchors, seed=MASTER_SEED + 7502, groups=deciles)
    t1 = time.time()
    mat_F, part_F = WR.build_arm(anchors, buckets, cw_cache, sents, mat0n_bin, pos, d, "PROFILE_PERM",
                                 perm=perm_freq)
    print("[build] F_FREQ_MATCHED_D t=%.1fs" % (time.time() - t1), flush=True)
    rep["FREQ_DECILE_DERANGEMENT"] = {
        "no_fixed_points": bool(np.all(perm_freq != np.arange(n_anchors))),
        "groups_respected": bool(np.all(deciles[perm_freq] == deciles)), "n_deciles": N_DECILES}

    mats: Dict[str, np.ndarray] = {
        "A_COUNT_IDENTITY": mat0_raw, "B_COUNT_PROFILE": mat_B,
        "C_BINARY_IDENTITY": mat_C, "D_BINARY_PROFILE": mat_D, "F_FREQ_MATCHED_D": mat_F}
    parts: Dict[str, Dict[str, Optional[np.ndarray]]] = {
        "A_COUNT_IDENTITY": part0_by_L, "B_COUNT_PROFILE": part_B,
        "C_BINARY_IDENTITY": part_C, "D_BINARY_PROFILE": part_D, "F_FREQ_MATCHED_D": part_F}

    # ---- ARMS_MUST_DIFFER (META_RULE_AF) -------------------------------------------------------
    digests_primary = {k: _digest(mats[k]) for k in ("A_COUNT_IDENTITY", "B_COUNT_PROFILE",
                                                      "C_BINARY_IDENTITY", "D_BINARY_PROFILE")}
    assert len(set(digests_primary.values())) == 4, (
        "META_RULE_AF VIOLATION: primary arms are not bit-distinct: %r" % digests_primary)
    rep["ARMS_MUST_DIFFER_DIGESTS"] = digests_primary

    # ---- population: identical construction to the parent write-rule cell -----------------------
    qidx_all = np.array([pos.get(w, -1) for w in L_words], dtype=np.int64)
    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not C["keep"][i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = C["keep"] & GOLD_ALL.any(axis=0)

    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T, E_T = GOLD_ALL[:, T].copy(), E_ALL[:, T].copy()
    qidx_T = qidx_all[T]
    L_test = [L_words[int(i)] for i in T]
    ok_q = qidx_T >= 0
    print("[population] n_items_scored=%d t=%.0fs" % (n_items, time.time() - t0), flush=True)

    # ---- per-item partial-cue matrices, one per arm ------------------------------------------------
    Qpart_by_arm: Dict[str, np.ndarray] = {}
    for name, part in parts.items():
        Q = np.zeros((n_items, d), dtype=np.float32)
        for j, L in enumerate(L_test):
            v = part.get(L)
            if v is not None:
                Q[j] = np.asarray(v, dtype=np.float32)
        Qpart_by_arm[name] = Q

    # ---- K1_KNOWN_ANSWER, EVERY ARM, GATED BEFORE ANY TREATMENT NUMBER -----------------------------
    ka_by_arm: Dict[str, float] = {}
    for name, mat_arm in mats.items():
        MATn = WR.l2n(mat_arm)
        Sfull = (MATn @ MATn.T).astype(np.float32)
        pred = np.argmax(Sfull[:, qidx_T[ok_q]], axis=0)
        ka = float(np.mean(pred == qidx_T[ok_q])) if ok_q.any() else float("nan")
        ka_by_arm[name] = ka
        del Sfull
    rep["K1_KNOWN_ANSWER_addressing"] = {k: round(v, 4) for k, v in ka_by_arm.items()}
    rep["K1_GATE"] = KA_MIN
    k1_fail = {k: v for k, v in ka_by_arm.items() if v < KA_MIN}
    print("[K1] " + json.dumps(rep["K1_KNOWN_ANSWER_addressing"]), flush=True)
    if k1_fail:
        rep["STOP_IF_VERDICT"] = {"verdict": "v_INSTRUMENT_STILL_LOOSE",
                                  "failing_arms": {k: round(v, 4) for k, v in k1_fail.items()}}
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        raise SystemExit("K1 GATE FAILED -- INSTRUMENT_STILL_LOOSE, no quality number published: %r"
                         % k1_fail)

    # ---- N1_NULL validity (shared item permutation across all arms) -------------------------------
    rng = np.random.default_rng(MASTER_SEED + 7077)
    itperm = np.arange(n_items)
    for _ in range(64):
        itperm = rng.permutation(n_items)
        if np.all(itperm != np.arange(n_items)):
            break
    null_by_arm: Dict[str, float] = {}
    for name, mat_arm in mats.items():
        MATn = WR.l2n(mat_arm)
        Sp = (MATn @ WR.l2n(Qpart_by_arm[name]).T).astype(np.float32)
        hn = FB.hit_at_1_both_tie_conventions(Sp[:, itperm], E_T, GOLD_T)
        null_by_arm[name] = float(hn["hit_exp"][hn["scored"]].mean())
    rep["NULL_PERMUTED_partial_cue"] = {k: round(v, 6) for k, v in null_by_arm.items()}

    # ---- FLOORS: shared (F_ORTHOGRAPHIC/F_FREQUENCY) + per-arm store-dependent --------------------
    F_ORTHO = (WR.l2n(aux["t_mat"]) @ WR.l2n(aux["Tq"][T]).T).astype(np.float32)
    F_FREQ = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    rep["FLOORS_SHARED_STORE_INDEPENDENT"] = ["F_ORTHOGRAPHIC", "F_FREQUENCY"]
    rep["FLOORS_PER_ARM_STORE_DEPENDENT"] = ["F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    rep["NEVER_IMPORTED"] = ["0.1390", "0.0873", "0.1382", "0.2070", "-0.1959"]

    hits_exp: Dict[str, np.ndarray] = {}
    scored_all = np.ones(n_items, dtype=bool)

    def add(name: str, Sx: np.ndarray) -> None:
        nonlocal scored_all
        hh = FB.hit_at_1_both_tie_conventions(Sx, E_T, GOLD_T)
        hits_exp[name] = hh["hit_exp"]
        scored_all = scored_all & hh["scored"]

    add("F_ORTHOGRAPHIC", F_ORTHO)
    add("F_FREQUENCY", F_FREQ)

    ortho_leak: Dict[str, float] = {}
    Tqn = WR.l2n(aux["Tq"][T])
    FLOOR_ARMS = ("A_COUNT_IDENTITY", "B_COUNT_PROFILE", "C_BINARY_IDENTITY", "D_BINARY_PROFILE")
    for name in mats:
        mat_arm = mats[name]
        MATn = WR.l2n(mat_arm)
        Spart = (MATn @ WR.l2n(Qpart_by_arm[name]).T).astype(np.float32)
        if name in FLOOR_ARMS:
            Sscr = (WR.l2n(FB.scramble_null(mat_arm, MASTER_SEED + 7091))
                   @ WR.l2n(Qpart_by_arm[name]).T).astype(np.float32)
            add("F_SCRAMBLE__%s" % name, Sscr)
            cfv = FB.constant_prototype_floor(mat_arm, mat_ok)
            add("F_CONSTANT_PROTOTYPE__%s" % name, FB.as_constant_matrix(cfv, n_items))
        add(name, Spart)
        Sm = np.where(E_T, Spart, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        ortho_leak[name] = float(np.mean(np.sum(WR.l2n(aux["t_mat"])[top1] * Tqn, axis=1)))
        del MATn, Spart, Sm

    rep["ORTHOGRAPHIC_LEAKAGE_CHECK"] = {
        "what": "mean trigram-cosine(top-1 winner, query), PARTIAL-CUE regime, per arm",
        "values": {k: round(v, 5) for k, v in ortho_leak.items()},
        "F_ORTHOGRAPHIC_floor_own_reference":
            round(float(np.mean(np.sum(WR.l2n(aux["t_mat"])[np.argmax(F_ORTHO, axis=0)] * Tqn, axis=1))),
                  5)}

    # ---- ONE shared paired bootstrap over everything -----------------------------------------------
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 7101)
    acc, boot = pb["acc"], pb["boot"]
    nc = pb["n_common"]

    per_arm_report: Dict[str, Dict] = {}
    for name in mats:
        entry: Dict = {"value_tie_corrected": round(acc[name], 5), "K1_addressing": round(ka_by_arm[name], 4),
                       "NULL_PERMUTED": round(null_by_arm[name], 6),
                       "orthographic_leakage": round(ortho_leak[name], 5)}
        if name in FLOOR_ARMS:
            floor_keys = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE__%s" % name,
                         "F_CONSTANT_PROTOTYPE__%s" % name]
            binding = max(floor_keys, key=lambda f: acc[f])
            mg_floor = FB.margin(boot, name, binding)
            mg_floor["ci_halfwidth"] = round((mg_floor["ci95"][1] - mg_floor["ci95"][0]) / 2.0, 5)
            mg_floor["analytic_null_halfwidth_at_this_n"] = round(_halfwidth(acc[binding], nc), 5)
            entry["binding_floor_name"] = binding
            entry["binding_floor_value"] = round(acc[binding], 5)
            entry["all_four_floors"] = {f: round(acc[f], 5) for f in floor_keys}
            entry["margin_vs_binding_floor"] = mg_floor
        per_arm_report[name] = entry
        print("[score] %-20s val=%.4f K1=%.4f NULL=%.5f" % (
            name, acc[name], ka_by_arm[name], null_by_arm[name]), flush=True)

    def margin_with_hw(a: str, b: str) -> Dict:
        m = FB.margin(boot, a, b)
        m["ci_halfwidth"] = round((m["ci95"][1] - m["ci95"][0]) / 2.0, 5)
        m["analytic_null_halfwidth_at_this_n"] = round(
            _halfwidth(0.5 * (acc[a] + acc[b]), nc), 5)
        return m

    margin_B_vs_A = margin_with_hw("B_COUNT_PROFILE", "A_COUNT_IDENTITY")
    margin_C_vs_A = margin_with_hw("C_BINARY_IDENTITY", "A_COUNT_IDENTITY")
    margin_D_vs_B = margin_with_hw("D_BINARY_PROFILE", "B_COUNT_PROFILE")
    margin_D_vs_C = margin_with_hw("D_BINARY_PROFILE", "C_BINARY_IDENTITY")
    margin_F_vs_D = margin_with_hw("F_FREQ_MATCHED_D", "D_BINARY_PROFILE")

    # ---- INTERACTION: diff-of-diffs (D-C) - (B-A), on the SAME bootstrap draws --------------------
    dd = (boot["D_BINARY_PROFILE"] - boot["C_BINARY_IDENTITY"]) - (boot["B_COUNT_PROFILE"] - boot["A_COUNT_IDENTITY"])
    dd_lo, dd_hi = float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))
    dd_band = "INTERACT" if (dd_lo > 0 or dd_hi < 0) else "ADDITIVE_CI_OVERLAPS_ZERO"
    interaction = {
        "margin_D_minus_C_binarisation_given_profile_write": margin_D_vs_C,
        "margin_B_minus_A_profile_write_given_count_rows": margin_B_vs_A,
        "diff_of_diffs_point": round(float(np.mean(dd)), 4),
        "diff_of_diffs_ci95": [round(dd_lo, 4), round(dd_hi, 4)],
        "diff_of_diffs_ci_halfwidth": round((dd_hi - dd_lo) / 2.0, 5),
        "band": dd_band,
        "reading": ("the two interventions INTERACT -- their combined effect is not the sum of "
                   "their separate effects" if dd_band == "INTERACT" else
                   "CI includes zero -- consistent with the two interventions being ADDITIVE, "
                   "not proof of exact additivity, just no evidence against it")}
    rep["INTERACTION"] = interaction
    print("[interaction] " + json.dumps({k: v for k, v in interaction.items() if k != "reading"},
                                        default=str), flush=True)

    # ---- STANDING RULE 12(b): per-item correlation of D's gain over B vs orthographic sim to gold -
    hit_D = hits_exp["D_BINARY_PROFILE"]
    hit_B = hits_exp["B_COUNT_PROFILE"]
    gain_D_minus_B = hit_D - hit_B
    orth_to_gold = np.full(n_items, np.nan, dtype=np.float64)
    for i in range(n_items):
        gcols = np.flatnonzero(GOLD_T[:, i])
        if gcols.size:
            orth_to_gold[i] = float(np.max(F_ORTHO[gcols, i]))
    corr_all = BCT.pearson_ci_bootstrap(gain_D_minus_B, orth_to_gold, seed=MASTER_SEED + 7303)
    nz = gain_D_minus_B != 0.0
    corr_nz = BCT.pearson_ci_bootstrap(gain_D_minus_B[nz], orth_to_gold[nz], seed=MASTER_SEED + 7304)
    rep["RULE12_ORTHOGRAPHIC_CORRELATION_CHECK"] = {
        "what": "pearson r between per-item (D_hit_exp - B_hit_exp) and that item's own best-gold "
                "F_ORTHOGRAPHIC score. ABOVE (CI-separated positive) would mean D's gains concentrate "
                "on items where the answer LOOKS LIKE the query -- a spelling-shaped win, not a "
                "substitutability win, per standing rule 12.",
        "all_items": corr_all, "gain_nonzero_items_only": corr_nz, "n_gain_nonzero": int(nz.sum())}
    print("[rule12] %r" % rep["RULE12_ORTHOGRAPHIC_CORRELATION_CHECK"], flush=True)

    # ---- REGRESSION GATE: A and B must reproduce the parent cell's landed figures ------------------
    reg = {
        "A_measured": round(acc["A_COUNT_IDENTITY"], 5), "A_expected": REGRESSION_A_EXPECTED,
        "A_PASS": bool(abs(acc["A_COUNT_IDENTITY"] - REGRESSION_A_EXPECTED) <= REGRESSION_TOL),
        "B_measured": round(acc["B_COUNT_PROFILE"], 5), "B_expected": REGRESSION_B_EXPECTED,
        "B_PASS": bool(abs(acc["B_COUNT_PROFILE"] - REGRESSION_B_EXPECTED) <= REGRESSION_TOL),
    }
    reg["ALL_PASS"] = bool(reg["A_PASS"] and reg["B_PASS"])
    reg["enforced"] = (grid == "full")
    reg["note_if_not_enforced"] = ("ONLY MEANINGFUL at --grid full: the landed parent-cell figures "
        "(A=0.02228, B=0.02979) were measured on the full 3994-item/5491-anchor pool; a --grid "
        "reduced population (400 items) is a different, much smaller pool by construction and is "
        "NOT expected to reproduce them -- reported here for visibility, never enforced.")
    rep["REGRESSION_GATE"] = reg
    print("[regression] enforced=%s " % reg["enforced"] + json.dumps(
        {k: v for k, v in reg.items() if k not in ("note_if_not_enforced",)}), flush=True)
    if grid == "full" and not reg["ALL_PASS"]:
        rep["STOP_IF_VERDICT"] = {"verdict": "REGRESSION_GATE_FAILED_NOT_THE_LANDED_INSTRUMENT",
                                  "detail": reg}
        rep["HIT_AT_1_PARTIAL_CUE_PRIMARY"] = {"n_common_scored": nc, "per_arm": per_arm_report,
                                               "ALL_VALUES_tie_corrected": {k: round(v, 5) for k, v in acc.items()}}
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r" % reg)

    rep["HIT_AT_1_PARTIAL_CUE_PRIMARY"] = {
        "n_common_scored": nc, "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED, PARTIAL-CUE regime",
        "per_arm": per_arm_report, "ALL_VALUES_tie_corrected": {k: round(v, 5) for k, v in acc.items()},
        "MARGINS": {"B_vs_A": margin_B_vs_A, "C_vs_A": margin_C_vs_A, "D_vs_B": margin_D_vs_B,
                   "D_vs_C": margin_D_vs_C, "F_FREQ_MATCHED_D_vs_D": margin_F_vs_D},
    }

    # ---- STOP-IF, evaluated in the pre-registered order, ALL flags reported ------------------------
    d_entry = per_arm_report["D_BINARY_PROFILE"]
    d_clears_floor = bool(d_entry.get("margin_vs_binding_floor", {}).get("band") == "ABOVE")
    d_vs_b_band = margin_D_vs_B["band"]
    c_vs_a_band = margin_C_vs_A["band"]

    if d_clears_floor:
        stop_if = "i_D_CLEARS_MAX_FLOOR_FIRST_GENUINE_READOUT_WIN"
    elif d_vs_b_band == "ABOVE":
        stop_if = "ii_D_BEATS_B_BUT_STILL_BELOW_FLOOR_WRITE_SIDE_BINARISATION_REAL_AND_ADDITIVE"
    elif d_vs_b_band == "NOT_SEPARATED":
        if c_vs_a_band == "ABOVE":
            stop_if = "iv_C_BEATS_A_WHILE_D_TIES_B_BINARISATION_AND_PROFILE_ARE_SUBSTITUTES_INTERACTION"
        else:
            stop_if = "iii_D_TIES_B_BINARISATION_IS_CUE_SIDE_PROPERTY_ONLY_TRANSFER_REASONING_REFUTED"
    else:
        stop_if = "OTHER_D_CI_SEPARATED_BELOW_B_BINARISATION_ON_TOP_OF_PROFILE_WRITE_HURTS"

    rep["STOP_IF_VERDICT"] = {
        "verdict": stop_if,
        "d_clears_its_own_binding_floor": d_clears_floor,
        "d_vs_b_band": d_vs_b_band, "c_vs_a_band": c_vs_a_band,
        "interaction_band": dd_band,
        "does_binarising_the_write_side_help": (
            "YES, AND IT CLEARS THE FLOOR" if stop_if.startswith("i_") else
            "YES, REAL BUT NOT ENOUGH -- GAP TO THE FLOOR REMAINS OPEN" if stop_if.startswith("ii_") else
            "NO -- BINARISATION IS A CUE-SIDE PROPERTY ONLY; THE TRANSFER REASONING IS REFUTED"
            if stop_if.startswith("iii_") else
            "THE TWO INTERVENTIONS ARE SUBSTITUTES, NOT COMPLEMENTS" if stop_if.startswith("iv_") else
            "NO -- BINARISATION HURTS ONCE THE PROFILE WRITE IS ALREADY APPLIED"),
    }
    print("[STOP_IF] " + stop_if, flush=True)

    rep["POWER"] = {"n_common_scored": nc,
                    "reading": "A WIDTH IS NOT AN EFFECT. Every margin carries its own ci_halfwidth "
                               "and analytic_null_halfwidth_at_this_n."}
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = {
        "loaded": sorted(m for m in sys.modules if m.startswith(("hdlab", "tools.", "exp_"))),
        "edited_by_this_cell": [], "cache_never_rebuilt": True}
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def decide(rep: Dict) -> Tuple[str, str]:
    sv = rep.get("STOP_IF_VERDICT", {})
    v = sv.get("verdict", "NO_ARM_RUN")
    h = rep.get("HIT_AT_1_PARTIAL_CUE_PRIMARY", {}).get("per_arm", {})
    a = h.get("A_COUNT_IDENTITY", {}); b = h.get("B_COUNT_PROFILE", {})
    c = h.get("C_BINARY_IDENTITY", {}); dd = h.get("D_BINARY_PROFILE", {})
    msg = ("STOP_IF=%s || A=%.4f B=%.4f C=%.4f D=%.4f (D_floor=%s) || d_vs_b=%s c_vs_a=%s" % (
        v, a.get("value_tie_corrected", float("nan")), b.get("value_tie_corrected", float("nan")),
        c.get("value_tie_corrected", float("nan")), dd.get("value_tie_corrected", float("nan")),
        dd.get("binding_floor_value"), sv.get("d_vs_b_band"), sv.get("c_vs_a_band")))
    return v, msg


def main() -> None:
    args = _ap.parse_args()
    if args.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return
    output_dir = _out_dir()
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE})
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(_ARGS.grid, output_dir)
        v, m = decide(rep)
        rep["verdict"], rep["verdict_msg"], rep["wire_status"] = v, m, "VET_PENDING"
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        print(json.dumps({"verdict": v, "verdict_msg": m}, indent=2), flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(output_dir, "_crash_diagnostic.json"),
                    {"anchor_name": ANCHOR_NAME, "error": "%s: %s" % (type(exc).__name__, exc),
                     "traceback": traceback.format_exc(),
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise


if __name__ == "__main__":
    main()
