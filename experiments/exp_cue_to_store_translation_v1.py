"""exp_cue_to_store_translation_v1 -- IS THE MISSING ORGAN A CUE->STORE TRANSLATOR?

WHAT THIS CELL IS FOR, IN ONE SENTENCE.
Our read-out compares a retrieval CUE against a STORE by raw cosine in one space; the brain never
does that -- the cue arrives on a DIFFERENT WIRE (direct perforant path, EC-II -> CA3) from the one
that wrote the memory (mossy fibre, EC-II -> DG -> CA3), through a synaptic matrix that was itself
modified during storage, and the hippocampus returns a LINKED cortical value rather than
reconstructing content out of its own sparse index. This cell measures whether supplying the missing
translation / link stage moves the PARTIAL-CUE read-out above every no-understanding floor.

CREDIT, NAMED, BECAUSE THIS IS AN ISLANDING FAILURE AND NOT A NEW IDEA.
notes/research_regime_switch_dense_retrieval_sparse_storage_brain_grounding_2026-07-04.md line 23
already said "The query that drives recall is denser than the sparse hippocampal trace it
addresses", and lines 55-60 already named the fix: LINK-NOT-RECONSTRUCT -- a sparse KEY for
addressing, a LINKED DENSE VALUE for read-out, address in key space, RETURN the value, never decode
content from the index. It was never built. Six weeks later two cells engineered the cue LOWER-rank,
the opposite direction. Arm A8 here IS that July design; the credit belongs to that note.
The experiment design is notes/drill_brain_partial_cue_retrieval_what_the_cue_actually_is_2026-08-16.md
section 7.

THE FRAMING THAT DIED, so it is not rebuilt.
"Make the cue a fragment of the target" is DEAD: the brain's cue is not a subset of the stored
pattern. "Partial cue" is FOUR problems (degraded copy / cross-modal pointer / description /
context); our task poses DESCRIPTION and CONTEXT while every completer result to date implemented
DEGRADED-COPY. That mislabel is reported, not averaged away.

=================================================================================================
THE POOL LADDER -- MANDATORY, AND IT MAY BE THE WHOLE STORY
=================================================================================================
On the landed OPEN pool the CONSTANT/prototype floor reads far above the partial cue, so every arm
is crushed into a FLOOR EFFECT and the experiment cannot measure what it exists to measure. Three
pools are therefore run and NO NUMBER MAY CROSS BETWEEN THEM:

  P1_OPEN            the incumbent open pool (continuity + regression gate). Chance ~0.0101.
  P1b_OPEN_MORPHBLOCK the open pool with every anchor sharing a 4+ character prefix with the query
                     word deleted from the pool AND from the gold sets. The output-side spelling
                     leak control (see LEAKAGE below for what it does and does not replace).
  P2_BALANCED_K15    tools/floor_battery.balanced_candidate_sets. Constant rankings are at chance BY
                     CONSTRUCTION (verified by the ORACLE arm, not assumed). Chance 0.0625.
  P3_MATCHED_K15     tools/floor_battery.matched_candidate_sets on trigram similarity. Kills the
                     spelling channel as well. Chance 0.0625.

If arms that are flat on P1 SEPARATE on P2/P3, then "the partial cue never moves" was a measurement
artefact and THAT is this cell's headline.

=================================================================================================
ARMS
=================================================================================================
A0_RAW_INCUMBENT              the landed partial-cue read-out. Regression-gated against 0.0223.
A1_LEARNED_LINEAR_MAP         ridge W fitted OFFLINE on a TRAIN item split, cue -> the item's OWN
                              stored row (never the gold). One matmul at inference. H1.
A2_FIXED_RANDOM_MAP           same shape, random W, Frobenius-matched. H1 control.
A2b_SHUFFLED_PAIRING_MAP      ridge fitted with the cue->target pairing PERMUTED. A learned-SHAPED
                              map with no true correspondence: it can only learn the generic mean
                              mapping. This is the informative control -- A2 with a one-sided dense
                              random W degenerates to a null, which answers a weaker question.
A3_WHITEN_ONLY                hdlab.whitening.WhiteningTransform (ZCA) fitted on the store, applied
                              to both sides. Equalises rank without learning a correspondence.
A5_NARROW_THEN_READ           hdlab.context_retention coarse shortlist over A0, first use of the
                              owned narrowing organ on this task.
A5r_RANDOM_GATE_size_matched  the SAME shortlist size, members chosen at random. Closes the leak
                              that cost the two-channel cell: pool SIZE, not the criterion.
A6_MAP_INSIDE_NARROW          A1 restricted to A5's shortlist. The interaction.
A7_SPLIT_LEXICON              FORM store (trigram) and MEANING store (context) queried SEPARATELY
                              and combined AT THE DECISION by per-channel confidence, never summed
                              into one cue vector. Two-stage lexical access vs the additive union
                              that measured BELOW incumbent.
A8_LINK_HARD_alpha0.5         THE JULY MECHANISM. dg_separate -> sparse KEY per item; the cue is
A8_LINK_SOFT_alpha0.5         DG-separated too and settled against the KEY codebook with
A8_LINK_SOFT_alpha0.0         iterative_cleanup(alpha=...) -- alpha IS the perforant cue-clamp and
                              is passed EXPLICITLY (the organ default is 0.0). The addressed item's
                              LINKED DENSE VALUE is returned and cosine is taken in the DENSE space.
                              Content is never decoded from the key. alpha 0.5 vs 0.0 measures
                              whether the perforant clamp matters.
A8b_KEY_COLLISION_AUDIT       a DIAGNOSTIC, read BEFORE any A8 score. Prior work names key COLLISION,
                              not value density, as the bottleneck. If exact-key addressing accuracy
                              is below the gate, A8 is declared VOID_ADDRESS and its score is unread.

A4_CONTEXT_BOUND_STORE IS NOT RUN AND HERE IS WHY, PLAINLY.
It is not buildable from the cached artefact. scratch/sparse_code_real_task/real_cache.npz keeps
only the ACCUMULATED per-anchor profile plus one held-out cue per item; the per-OCCURRENCE context
stream was consumed inside exp_grounding_readout_known_answer_v1.build_space and never persisted.
Rebuilding it would rebuild the store, which breaks the identical-instrument invariant every other
arm depends on. The admissible substitute is run instead: the ENCODING-SPECIFICITY CONTRAST --
EXACT_KEY (a cue that IS the encoded aggregate) against PARTIAL_CUE (a sentence DELIBERATELY
EXCLUDED from the trace), same instrument, same pool, same scorer. That contrast measures the
encoding-specificity claim; it does not test a context-BOUND store, and no claim about one is made.

=================================================================================================
VALIDITY -- both arms must pass and they fail INDEPENDENTLY
=================================================================================================
KA_EXACT_KEY        the query IS the designated gold's stored row. Must be >= 0.95 in every
                    condition. Sensitive to scorer / pool / eligibility, INSENSITIVE to the
                    cue->item pairing.
NULL_PERMUTED_CUE   identical pipeline, cue-to-item assignment permuted. Must sit at that
                    condition's own chance. Sensitive to the pairing, INSENSITIVE to the scorer.
A bug in W cannot make both pass: a W that leaked item identity lifts NULL while KA stays 1.0; a
broken scorer drops KA while NULL stays at chance.
NO TREATMENT NUMBER IS READ IN A CONDITION WHOSE KA ARM FAILS.

FLOORS, on every pool, recomputed on that pool, never inherited:
  F1_ORTHO_TRIGRAM, F1b_ORTHO_PREFIX, F2_FREQUENCY, F3_SCRAMBLE_NULL, F4_CONSTANT_PROTOTYPE.
The bar is a CI-separated margin (paired bootstrap) over max(those five) on the IDENTICAL
scorer / n / pool / gold -- never a bare number. ORACLE_CONSTANT is reported and is NOT a floor.
Both tie conventions are published beside every arm, plus the tie-corrected primary.

LEAKAGE CONTROLS, each naming the leak it closes:
 1 FIT/SCORE SPLIT ON ITEMS. W is fitted on items disjoint from the scored items, and EVERY arm is
   scored on the SAME test half, so no arm is compared across populations. Closes: A1 memorising.
 2 SPELLING. Closed twice: P3 matches distractors to the gold on trigram similarity, and P1b
   deletes prefix-sharing anchors from the pool. NOT CLOSED: the drill asked for a cue-FEATURE
   morphology block. The cue is a 256-dim dense context vector with no word-identified features, so
   deleting "cue features sharing a stem with the target" is not constructible here. Said plainly
   rather than substituted silently.
 3 GOLD-BLIND FITTING. W's objective never sees the WordNet golds; its only target is the item's own
   stored row. Closes the circularity a prior cell labelled INADMISSIBLE_CIRCULAR.
 4 POPULARITY / GENERICITY. F4 plus the explicit ORACLE constant arm.
 5 SIZE-MATCHED RANDOM GATE beside A5 at the identical shortlist size.
 6 NO LLM ANYWHERE. W is a matrix fitted offline from the substrate's own vectors; inference is one
   matmul. Nothing in this file calls a language model. THE invariant.
 7 hdlab.grounded_similarity.grounded_similarity() is NEVER used as a scorer, per the standing bar.
 8 POPULATIONS NEVER MERGED. Each pool and each cue regime is reported separately.

CONSOLIDATION NOTE: this cell does not consolidate or rebuild any store, so the "consolidation
destroys a store's own constant floor" hazard does not arise. Every floor here is measured on the
same landed store the treatment arms use.

ASCII-only. Writes only under data/exp_cue_to_store_translation_v1/. No protected path is opened
for writing: data/foundation/**, CLAUDE.md, notes/PLAN.md, notes/LONG_TERM_PLAN.md, notes/BOARD.md,
data/capability_registry.jsonl, tools/status_*.py, tools/c3_gate.py, tools/verdict_bar_check.py and
tools/floor_battery.py are READ ONLY.
"""
from __future__ import annotations

import os

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
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.floor_battery import (                                              # noqa: E402
    as_constant_matrix, balanced_candidate_sets, constant_prototype_floor, frequency_floor,
    hit_at_1_both_tie_conventions, l2n, margin, matched_candidate_sets, oracle_constant_scores,
    rank_of_best_gold, scramble_null,
)
from experiments._seed_checkpoint import record_gate                            # noqa: E402

ANCHOR_NAME = "exp_cue_to_store_translation_v1"
OUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)

# PROVENANCE: the harness cache built by the 2026-08-16 cells from
# experiments/exp_grounding_readout_known_answer_v1 UNMODIFIED (same corpus, ConceptSpace, items,
# WordNet golds, eligible pool, MASTER_SEED). Reused so this cell scores the IDENTICAL pool the
# landed numbers were computed on. exp_task_degeneracy_v1 uses the same two paths.
CACHE = os.path.join(REPO_ROOT, "scratch", "sparse_code_real_task", "real_cache.npz")
AUX = os.path.join(REPO_ROOT, "scratch", "sparsify_right_object", "aux_v2.npz")

MASTER_SEED = 20260816
N_BOOT = 10000
K_BAL = 15                     # balanced/matched pool size -> chance 1/16 = 0.0625
KA_CEILING_MIN = 0.95
SAT_MIN_SPREAD = 0.02
TEST_FRAC = 0.5                # item split for the fitted arms; EVERY arm is scored on TEST
RIDGE_GRID = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0)
DG_EXPAND = 2048               # EC-II -> DG expansion (store dim is 256, so this is 8x)
DG_SPARSITY = 0.02             # granule-cell population sparsity ~1-4% (Jung & McNaughton 1993)
DG_TAG = "cue_store_translation_v1:DG"
CA3_TEMP = 4.0                 # iterative_cleanup temp; effective beta = temp*sqrt(D)
CA3_STEPS = 4
CA3_ALPHA_CLAMP = 0.5          # perforant cue clamp, PASSED EXPLICITLY (organ default is 0.0)
CA3_ALPHA_NOCLAMP = 0.0
LINK_BETA = 32.0               # softmax sharpness of the soft link read
ADDRESS_GATE = 0.95            # exact-key addressing accuracy below this -> A8 is VOID_ADDRESS
SHORT_FRAC = 0.25              # A5 shortlist size as a fraction of the condition's eligible pool
MORPH_LCP = 4                  # P1b deletes anchors sharing a >=4 char prefix with the query word
REGRESSION_A0_PARTIAL = 0.0223  # landed A_ORIGINAL_open_pool|PARTIAL_CUE R0_CTX_DENSE, tie-corrected
REGRESSION_TOL = 5e-4


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def ruler_mode_gate() -> Dict:
    """HARD GATE, never inferred -- the real one, lifted from exp_task_degeneracy_v1:121.

    exp_encoding_quality_instrument_v2 resolves RUN_MODE from argv/env AT IMPORT, so the token
    '--smoke' anywhere in argv would silently recompute every number on a 512-word vocabulary with
    no error and no warning. This cell's mode flag is --grid full|reduced for exactly that reason.
    """
    from experiments import exp_encoding_quality_instrument_v2 as INS
    g = {"RUN_MODE": INS.RUN_MODE, "V": int(INS.V), "CORPUS_BYTES": int(INS.CORPUS_BYTES),
         "argv": list(sys.argv)}
    g["PASS"] = bool(INS.RUN_MODE == "full" and int(INS.V) == 4096
                     and int(INS.CORPUS_BYTES) == 64_000_000)
    if not g["PASS"]:
        raise SystemExit("RULER MODE GATE FAILED: %r" % g)
    return g


def _unflatten(flat: np.ndarray, lens: np.ndarray) -> List[np.ndarray]:
    out, o = [], 0
    for n in lens:
        out.append(flat[o:o + int(n)])
        o += int(n)
    return out


def _lcp(a: str, b: str) -> int:
    k = 0
    for x, y in zip(a, b):
        if x != y:
            break
        k += 1
    return k


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def col(v: np.ndarray) -> np.ndarray:
    """A CONSTANT floor as an [n_anchors, 1] column: it cannot silently acquire per-item variation."""
    return np.asarray(v, dtype=np.float32).reshape(-1, 1)


def load_cache() -> Dict:
    if not os.path.exists(CACHE):
        raise SystemExit(
            "CACHE MISSING: %s. This cell deliberately does NOT rebuild the store -- rebuilding it "
            "would break the identical-instrument invariant every arm depends on. Run "
            "experiments/exp_task_degeneracy_v1.py first, which rebuilds it from "
            "exp_grounding_readout_known_answer_v1 unmodified." % CACHE)
    z = np.load(CACHE, allow_pickle=False)
    anchors = [str(a) for a in z["anchors"]]
    return {"anchors": anchors, "mat": z["mat"].astype(np.float32), "mat_ok": z["mat_ok"],
            "Q_exact": z["Q_exact"].astype(np.float32), "Q_part": z["Q_part"].astype(np.float32),
            "keep": z["keep"], "excl": _unflatten(z["excl_flat"], z["excl_len"]),
            "goldi": _unflatten(z["gold_flat"], z["gold_len"]),
            "L_words": [str(w) for w in z["L_words"]],
            "pos": {a: i for i, a in enumerate(anchors)}}


def load_aux() -> Dict:
    if not os.path.exists(AUX):
        raise SystemExit("AUX MISSING: %s -- run experiments/exp_task_degeneracy_v1.py first." % AUX)
    z = np.load(AUX, allow_pickle=False)
    return {"Tq": z["Tq"], "t_mat": z["t_mat"], "Pq": z["Pq"], "fq": z["fq"], "source": AUX}


# =================================================================================================
# THE TRANSLATION ARMS
# =================================================================================================
def fit_ridge(C: np.ndarray, T: np.ndarray, lam: float) -> np.ndarray:
    """W minimising ||C W - T||^2 + lam*||W||^2. Closed form, 256x256, inspectable on disk.

    GLASS-BOX AND OFFLINE. No gradient loop, no model, no LLM. One matmul at inference.
    """
    C = np.asarray(C, dtype=np.float64)
    T = np.asarray(T, dtype=np.float64)
    d = C.shape[1]
    A = C.T @ C + float(lam) * np.eye(d)
    return np.linalg.solve(A, C.T @ T).astype(np.float32)


def select_ridge_lam(C: np.ndarray, T: np.ndarray, seed: int) -> Tuple[float, List[Dict]]:
    """Pick lam by held-out RECONSTRUCTION error inside TRAIN. Gold-blind by construction: the
    selection criterion never sees a WordNet gold, only the item's own stored row."""
    rng = np.random.default_rng(seed)
    n = C.shape[0]
    perm = rng.permutation(n)
    n_in = int(0.8 * n)
    tr, va = perm[:n_in], perm[n_in:]
    trace: List[Dict] = []
    best, best_err = RIDGE_GRID[0], float("inf")
    for lam in RIDGE_GRID:
        W = fit_ridge(C[tr], T[tr], lam)
        pred = l2n(C[va] @ W)
        err = float(np.mean(np.sum((pred - T[va]) ** 2, axis=1)))
        cos = float(np.mean(np.sum(pred * T[va], axis=1)))
        trace.append({"lam": lam, "heldout_mse": round(err, 6), "heldout_cos": round(cos, 6)})
        if err < best_err:
            best, best_err = lam, err
    return best, trace


def dg_keys(X: np.ndarray, W: np.ndarray) -> np.ndarray:
    """Sparse DG keys for a batch. hdlab.dg_pattern_separation.dg_separate is a PER-VECTOR organ
    (W @ x), so it is called per row -- the organ is reused verbatim, not reimplemented."""
    from hdlab.dg_pattern_separation import dg_separate
    out = np.zeros((X.shape[0], DG_EXPAND), dtype=np.float32)
    for i in range(X.shape[0]):
        out[i] = dg_separate(X[i], expand_dim=DG_EXPAND, sparsity=DG_SPARSITY,
                             proj_seed_tag=DG_TAG, W=W)
    return out


def key_collision_audit(K_store: np.ndarray, mat: np.ndarray, W_dg: np.ndarray,
                        mat_ok: np.ndarray) -> Dict:
    """A8b -- READ THIS BEFORE ANY A8 SCORE.

    Prior work (research_to_exp_dev_DIMSPARSE2, 2026-06-06) names KEY COLLISION, not value density,
    as the retrieval bottleneck, and a 1,476-codes-for-4,096-words collision has been self-flagged
    in this repo once already. Two questions, both answered here:
      1. how many of the stored items share an identical active-set signature;
      2. can the key space address the store AT ALL -- i.e. present each item's OWN dense row as the
         cue, run the full DG -> settle -> address path, and ask how often the addressed item is
         itself. Below ADDRESS_GATE the A8 family is VOID and its scores are not read.
    """
    from hdlab.iterative_attractor import iterative_cleanup
    ok = np.flatnonzero(np.asarray(mat_ok, dtype=bool))
    sigs = set()
    for i in ok:
        sigs.add(np.flatnonzero(K_store[i]).tobytes())
    Kn = l2n(K_store)
    rng = np.random.default_rng(MASTER_SEED + 77)
    samp = rng.choice(ok, size=int(min(600, ok.size)), replace=False)
    cue_keys = dg_keys(mat[samp], W_dg)
    st = iterative_cleanup(cue_keys, K_store, temp=CA3_TEMP, max_steps=CA3_STEPS,
                           alpha=CA3_ALPHA_CLAMP)
    addr = l2n(st["state"]) @ Kn.T
    hit_self = float(np.mean(np.argmax(addr, axis=1) == samp))
    st0 = iterative_cleanup(cue_keys, K_store, temp=CA3_TEMP, max_steps=CA3_STEPS,
                            alpha=CA3_ALPHA_NOCLAMP)
    addr0 = l2n(st0["state"]) @ Kn.T
    hit_self0 = float(np.mean(np.argmax(addr0, axis=1) == samp))
    off = addr.copy()
    off[np.arange(samp.size), samp] = -np.inf
    return {
        "expand_dim": DG_EXPAND, "sparsity": DG_SPARSITY, "active_units_per_key": int(
            round(DG_SPARSITY * DG_EXPAND)),
        "n_items_with_a_key": int(ok.size),
        "n_distinct_active_set_signatures": int(len(sigs)),
        "collision_rate": round(1.0 - len(sigs) / max(int(ok.size), 1), 6),
        "EXACT_KEY_ADDRESSING_ACCURACY_alpha0.5": round(hit_self, 4),
        "EXACT_KEY_ADDRESSING_ACCURACY_alpha0.0": round(hit_self0, 4),
        "address_gate": ADDRESS_GATE,
        "ADDRESS_USABLE": bool(hit_self >= ADDRESS_GATE),
        "mean_margin_self_minus_best_other": round(
            float(np.mean(addr[np.arange(samp.size), samp] - off.max(axis=1))), 4),
        "n_sampled": int(samp.size),
        "reading": "if ADDRESS_USABLE is False the A8 family is VOID_ADDRESS and its scores must "
                   "not be read as evidence about link-not-reconstruct; the key space cannot "
                   "address the store even from the store's own rows.",
    }


def address_diagnostic(cue_keys: np.ndarray, K_store: np.ndarray, qidx: np.ndarray,
                       alpha: float) -> Dict:
    """THE MECHANISTIC NUMBER FOR THIS CELL: does the cue address the RIGHT ITEM?

    link-not-reconstruct has two stages and they fail for different reasons. If the cue addresses
    the query word's own trace and the read-out is still wrong, the LINK is the problem. If the cue
    addresses the wrong item, the ADDRESS is the problem and no amount of value-side machinery
    helps. Averaging the two together is how a component gets mislabelled.
    """
    from hdlab.iterative_attractor import iterative_cleanup
    st = iterative_cleanup(cue_keys, K_store, temp=CA3_TEMP, max_steps=CA3_STEPS, alpha=alpha)
    addr = np.argmax(l2n(st["state"]) @ l2n(K_store).T, axis=1)
    ok = qidx >= 0
    return {"alpha": alpha, "n": int(ok.sum()),
            "addressed_item_IS_the_query_word": round(float(np.mean(addr[ok] == qidx[ok])), 4),
            "n_distinct_items_addressed": int(np.unique(addr[ok]).size),
            "settle_converged": bool(st["converged"]), "settle_steps": int(st["n_iterations"])}


def link_not_reconstruct(cue_keys: np.ndarray, K_store: np.ndarray, mat: np.ndarray,
                         alpha: float, hard: bool) -> np.ndarray:
    """THE 2026-07-04 MECHANISM. Address in the SPARSE KEY space with the cue clamped through the
    settle (alpha = the perforant drive, passed explicitly), then RETURN THE LINKED DENSE VALUE and
    score cosine in the DENSE space. Content is never decoded out of the key.

    hard=True returns the single addressed item's stored row (the literal reinstatement);
    hard=False returns a softmax-weighted blend of linked values (a graded reinstatement).
    """
    from hdlab.iterative_attractor import iterative_cleanup
    st = iterative_cleanup(cue_keys, K_store, temp=CA3_TEMP, max_steps=CA3_STEPS, alpha=alpha)
    Kn = l2n(K_store)
    addr = (l2n(st["state"]) @ Kn.T).astype(np.float32)          # [n_items, n_anchors] KEY SPACE
    Vn = l2n(mat)                                                # the LINKED DENSE VALUES
    if hard:
        retrieved = Vn[np.argmax(addr, axis=1)]
    else:
        z = addr - addr.max(axis=1, keepdims=True)
        w = np.exp((LINK_BETA * z).astype(np.float64))
        w /= (w.sum(axis=1, keepdims=True) + 1e-30)
        retrieved = (w.astype(np.float32) @ Vn)
    return (Vn @ l2n(retrieved).T).astype(np.float32)            # DENSE SPACE cosine


# =================================================================================================
# pool-dependent arms (built per condition, because a shortlist and a decision rule both depend on
# which candidates are eligible)
# =================================================================================================
def coarse_scores(mat: np.ndarray, Q: np.ndarray, d_coarse: int,
                  seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Coarse random-projection similarity using hdlab.context_retention.build_coarse_projection.

    The organ's own coarse_shortlist() is a PER-QUERY torch call; calling it 2,000 times per
    condition is the same arithmetic at 2,000x the overhead, so the projection organ is reused and
    the top-k is taken in bulk. self_test T6 verifies bulk selection agrees with the organ's own
    coarse_shortlist on a sample, so the reuse is witnessed rather than asserted.
    """
    import torch
    from hdlab.context_retention import build_coarse_projection
    g = torch.Generator().manual_seed(int(seed))
    proj = build_coarse_projection(mat.shape[1], d_coarse, g).numpy().astype(np.float32)
    return (l2n(mat @ proj) @ l2n(Q @ proj).T).astype(np.float32), proj


def topk_mask_within(E: np.ndarray, score: np.ndarray, frac: float,
                     rng: Optional[np.random.Generator]) -> np.ndarray:
    """Per item, keep ceil(frac * n_eligible) candidates -- by `score` if rng is None (the criterion
    gate), else uniformly at random (the SIZE-MATCHED control at the identical size)."""
    n_a, n_i = E.shape
    M = np.zeros((n_a, n_i), dtype=bool)
    for i in range(n_i):
        idx = np.flatnonzero(E[:, i])
        if idx.size == 0:
            continue
        k = max(1, int(np.ceil(frac * idx.size)))
        if k >= idx.size:
            M[idx, i] = True
            continue
        if rng is None:
            sel = idx[np.argpartition(-score[idx, i], k - 1)[:k]]
        else:
            sel = rng.choice(idx, size=k, replace=False)
        M[sel, i] = True
    return M


def split_lexicon(S_form: np.ndarray, S_mean: np.ndarray, E: np.ndarray) -> np.ndarray:
    """A7 -- two stores, two cues, combined AT THE DECISION.

    The FORM channel (orthographic store, orthographic cue) and the MEANING channel (context store,
    context cue) are each scored against their OWN store. The decision rule picks, per item, the
    channel with the larger within-pool confidence (top1 minus top2 in z units of that channel's own
    eligible scores) and uses THAT channel's ranking. Nothing is ever summed into one cue vector --
    that is the configuration the two-channel cell measured BELOW incumbent, and in the brain lemma
    and word-form retrieval are separate stages that dissociate in anomia.
    """
    def conf(S: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        Sm = np.where(E, S, -np.inf)
        z = np.sort(Sm, axis=0)
        top1 = z[-1]
        top2 = z[-2] if z.shape[0] > 1 else z[-1]
        sd = np.nanstd(np.where(E, S, np.nan), axis=0) + 1e-9
        gap = np.where(np.isfinite(top1) & np.isfinite(top2), top1 - top2, 0.0)
        return (gap / sd), Sm
    cf, Sf = conf(S_form)
    cm, Sm_ = conf(S_mean)
    use_form = (cf > cm)[None, :]
    zf = (Sf - np.nanmean(np.where(E, S_form, np.nan), axis=0)) / (
        np.nanstd(np.where(E, S_form, np.nan), axis=0) + 1e-9)
    zm = (Sm_ - np.nanmean(np.where(E, S_mean, np.nan), axis=0)) / (
        np.nanstd(np.where(E, S_mean, np.nan), axis=0) + 1e-9)
    return np.where(use_form, zf, zm).astype(np.float32)


# =================================================================================================
# scoring one condition (same shape as exp_task_degeneracy_v1.score_condition -- one ruler)
# =================================================================================================
def score_condition(name: str, E: np.ndarray, GOLD: np.ndarray, keepm: np.ndarray,
                    arms: Dict[str, np.ndarray], chance: float, do_rank: bool,
                    floors: Sequence[str]) -> Dict:
    per: Dict[str, Dict] = {}
    scored_all = None
    for k, S in arms.items():
        h = hit_at_1_both_tie_conventions(S, E, GOLD)
        sc = h["scored"] & keepm
        per[k] = {"hit_exp": h["hit_exp"], "hit_opt": h["hit_opt"], "hit_cons": h["hit_cons"],
                  "tie": h["tie_mass"], "scored": sc}
        if do_rank:
            per[k].update(rank_of_best_gold(S, E, GOLD))
        scored_all = sc.copy() if scored_all is None else (scored_all & sc)
    nc = int(scored_all.sum())
    if nc < 30:
        return {"n_common_scored": nc, "VOID": "fewer than 30 commonly scored items"}
    idx = np.flatnonzero(scored_all)
    rng = np.random.default_rng(MASTER_SEED + 101)
    IDX = rng.integers(0, nc, size=(N_BOOT, nc))
    boot = {c: {k: per[k][c][idx][IDX].mean(axis=1) for k in arms}
            for c in ("hit_exp", "hit_opt", "hit_cons")}
    acc = {c: {k: round(float(per[k][c][idx].mean()), 4) for k in arms}
           for c in ("hit_exp", "hit_opt", "hit_cons")}
    ci = {k: [round(float(np.percentile(boot["hit_exp"][k], 2.5)), 4),
              round(float(np.percentile(boot["hit_exp"][k], 97.5)), 4)] for k in arms}
    tie = {k: round(float(per[k]["tie"][idx].mean()), 4) for k in arms}

    A = acc["hit_exp"]
    treat = [k for k in arms if not k.startswith(("KA_", "NULL_", "ORACLE"))]
    spread = round(float(max(A[k] for k in treat) - min(A[k] for k in treat)), 4)
    ka = A.get("KA_EXACT_KEY_planted", float("nan"))
    nul = A.get("NULL_PERMUTED_CUE", float("nan"))
    present = [f for f in floors if f in A]
    binding = max(present, key=lambda f: A[f]) if present else None
    out = {
        "n_common_scored": nc, "chance_for_THIS_condition": round(float(chance), 6),
        "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED (expected hit under a random tie-break)",
        "VALIDITY": {
            "KNOWN_ANSWER_hit_at_1": ka, "gate": KA_CEILING_MIN,
            "KA_PASSES": bool(ka >= KA_CEILING_MIN),
            "NULL_PERMUTED_CUE_hit_at_1": nul, "chance": round(float(chance), 6),
            "null_near_chance": bool(abs(nul - chance) < max(0.02, 0.5 * chance)),
            "treatment_spread": spread, "saturation_tripped": bool(spread < SAT_MIN_SPREAD),
            "CONDITION_READABLE": bool(ka >= KA_CEILING_MIN and spread >= SAT_MIN_SPREAD),
            "independence": "KA plants the answer (sensitive to scorer/pool, blind to the pairing); "
                            "NULL permutes the cue->item assignment (sensitive to the pairing, "
                            "blind to the scorer). They cannot both be rescued by one bug."},
        "hit_at_1_TIE_CORRECTED_primary": A,
        "hit_at_1_OPTIMISTIC_tie": acc["hit_opt"],
        "hit_at_1_CONSERVATIVE_tie": acc["hit_cons"],
        "ci95_tie_corrected": ci, "mean_tie_mass_of_eligible_pool": tie,
        "arm_digests": {k: _digest(per[k]["hit_exp"][idx]) for k in arms},
        "BINDING_FLOOR": binding,
        "BINDING_FLOOR_VALUE_tie_corrected": (A[binding] if binding else None),
        "MARGIN_vs_binding_floor_TIE_CORRECTED": (
            {k: margin(boot["hit_exp"], k, binding) for k in arms if k != binding}
            if binding else {}),
        "MARGIN_vs_binding_floor_CONSERVATIVE": (
            {k: margin(boot["hit_cons"], k, binding) for k in arms if k != binding}
            if binding else {}),
        "MARGIN_vs_binding_floor_OPTIMISTIC": (
            {k: margin(boot["hit_opt"], k, binding) for k in arms if k != binding}
            if binding else {}),
        "ARM_BY_ARM_vs_EACH_FLOOR_tie_corrected": {
            k: {f: margin(boot["hit_exp"], k, f) for f in present if f != k}
            for k in arms if k not in present},
    }
    # THE HEAD-TO-HEAD COMPARISONS THE DESIGN EXISTS TO MAKE, paired on the same resamples.
    def pair(a: str, b: str) -> Optional[Dict]:
        return margin(boot["hit_exp"], a, b) if (a in arms and b in arms) else None
    out["DECISIVE_PAIRED_MARGINS_tie_corrected"] = {
        "A1_LEARNED_vs_A2_RANDOM": pair("A1_LEARNED_LINEAR_MAP", "A2_FIXED_RANDOM_MAP"),
        "A1_LEARNED_vs_A2b_SHUFFLED_PAIRING": pair("A1_LEARNED_LINEAR_MAP",
                                                   "A2b_SHUFFLED_PAIRING_MAP"),
        "A1_LEARNED_vs_A0_RAW": pair("A1_LEARNED_LINEAR_MAP", "A0_RAW_INCUMBENT"),
        "A3_WHITEN_vs_A0_RAW": pair("A3_WHITEN_ONLY", "A0_RAW_INCUMBENT"),
        "A5_NARROW_vs_A5r_RANDOM_GATE_size_matched": pair("A5_NARROW_THEN_READ",
                                                          "A5r_RANDOM_GATE_size_matched"),
        "A5_NARROW_vs_A0_RAW": pair("A5_NARROW_THEN_READ", "A0_RAW_INCUMBENT"),
        "A6_MAP_INSIDE_NARROW_vs_A5_NARROW": pair("A6_MAP_INSIDE_NARROW", "A5_NARROW_THEN_READ"),
        "A7_SPLIT_LEXICON_vs_A0_RAW": pair("A7_SPLIT_LEXICON_decision_level", "A0_RAW_INCUMBENT"),
        "A8_LINK_HARD_vs_A0_RAW": pair("A8_LINK_HARD_alpha0.5", "A0_RAW_INCUMBENT"),
        "A8_LINK_SOFT_vs_A0_RAW": pair("A8_LINK_SOFT_alpha0.5", "A0_RAW_INCUMBENT"),
        "A8_clamp_alpha0.5_vs_alpha0.0": pair("A8_LINK_SOFT_alpha0.5", "A8_LINK_SOFT_alpha0.0"),
    }
    orc = "ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"
    if orc in arms:
        out["MARGIN_vs_ORACLE_CONSTANT_tie_corrected"] = {
            k: margin(boot["hit_exp"], k, orc) for k in arms if k != orc}
    if binding:
        out["MARGIN_vs_CHANCE_tie_corrected"] = {
            k: {"point": round(A[k] - float(chance), 4), "ci95_of_arm": ci[k],
                "band": ("ABOVE" if ci[k][0] > chance else
                         ("BELOW" if ci[k][1] < chance else "NOT_SEPARATED"))} for k in arms}
    if do_rank:
        out["top50_recall_OPTIMISTIC"] = {
            k: round(float((per[k]["rank_opt"][idx] <= 50).mean()), 4) for k in arms}
        out["top50_recall_CONSERVATIVE"] = {
            k: round(float((per[k]["rank_cons"][idx] <= 50).mean()), 4) for k in arms}
        out["median_rank_OPTIMISTIC"] = {
            k: float(np.median(per[k]["rank_opt"][idx])) for k in arms}
    print("[%s] n=%d KA=%.4f NULL=%.4f chance=%.4f binding=%s(%s)" % (
        name, nc, ka, nul, chance, binding, A.get(binding)), flush=True)
    print("        " + " ".join("%s=%.4f" % (k[:26], v) for k, v in A.items()), flush=True)
    return out


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {}
    from tools import floor_battery
    res["floor_battery_selftest_keys"] = sorted(floor_battery.self_test().keys())
    rng = np.random.default_rng(3)

    # T1 -- the ridge really recovers a KNOWN linear map, and the shuffled-pairing control does not.
    d, n = 24, 900
    Wtrue = rng.standard_normal((d, d)).astype(np.float32)
    Cx = l2n(rng.standard_normal((n, d)).astype(np.float32))
    Tx = l2n(Cx @ Wtrue)
    lam, tr = select_ridge_lam(Cx[:600], Tx[:600], 1)
    Wf = fit_ridge(Cx[:600], Tx[:600], lam)
    cos_fit = float(np.mean(np.sum(l2n(Cx[600:] @ Wf) * Tx[600:], axis=1)))
    perm = np.random.default_rng(2).permutation(600)
    Ws = fit_ridge(Cx[:600], Tx[:600][perm], lam)
    cos_shuf = float(np.mean(np.sum(l2n(Cx[600:] @ Ws) * Tx[600:], axis=1)))
    assert cos_fit > 0.95, "ridge failed to recover a known linear map: %.4f" % cos_fit
    assert cos_shuf < 0.5, "shuffled-pairing control recovered the map: %.4f" % cos_shuf
    res["T1_ridge_recovers_known_map"] = {"lam": lam, "cos_fit": round(cos_fit, 4),
                                          "cos_shuffled_pairing": round(cos_shuf, 4),
                                          "lam_trace": tr}

    # T2 -- DG keys are sparse to spec, deterministic, and address their OWN store row.
    from hdlab.dg_pattern_separation import projection_matrix
    small = 128
    M = l2n(rng.standard_normal((small, 32)).astype(np.float32))
    Wd = projection_matrix(32, 256, DG_TAG)
    Ks = np.zeros((small, 256), dtype=np.float32)
    from hdlab.dg_pattern_separation import dg_separate
    for i in range(small):
        Ks[i] = dg_separate(M[i], expand_dim=256, sparsity=DG_SPARSITY, proj_seed_tag=DG_TAG, W=Wd)
    nnz = int((Ks[0] != 0).sum())
    assert nnz == max(1, round(DG_SPARSITY * 256)), "DG sparsity not honoured: %d" % nnz
    assert np.array_equal(Ks[0], dg_separate(M[0], expand_dim=256, sparsity=DG_SPARSITY,
                                             proj_seed_tag=DG_TAG, W=Wd)), "DG not deterministic"
    res["T2_dg_keys"] = {"active_units": nnz,
                         "distinct_signatures": len({np.flatnonzero(k).tobytes() for k in Ks})}

    # T3 -- LINK-NOT-RECONSTRUCT is wired correctly: with the cue = an item's OWN row, the hard link
    # must return THAT item's dense value, so the arm's argmax is that item. If this fails the arm
    # is not implementing the July design and no A8 number means anything.
    S8 = link_not_reconstruct(Ks, Ks, M, CA3_ALPHA_CLAMP, True)
    self_hit = float(np.mean(np.argmax(S8, axis=0) == np.arange(small)))
    assert self_hit > 0.95, "link-not-reconstruct does not reinstate an item from its own key: %.4f" \
                            % self_hit
    # and it must be a LINK, not a decode: perturbing the VALUES while keeping the KEYS fixed must
    # change the read-out. A pipeline that decoded content from the index would be unaffected.
    M2 = l2n(M + 0.9 * rng.standard_normal(M.shape).astype(np.float32))
    S8b = link_not_reconstruct(Ks, Ks, M2, CA3_ALPHA_CLAMP, True)
    assert not np.allclose(S8, S8b), "read-out ignores the linked VALUE -- it is decoding the key"
    res["T3_link_not_reconstruct"] = {"self_reinstatement": round(self_hit, 4),
                                      "value_is_load_bearing": True}

    # T4 -- score_condition end to end on a synthetic pool with a KNOWN answer.
    n_a, n_i = 120, 900
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    proto = np.linspace(1, 0, n_a).astype(np.float32)
    p = proto ** 6; p = p / p.sum()
    g = rng.choice(n_a, size=n_i, p=p)
    GOLD[g, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    keepm = np.ones(n_i, dtype=bool)
    Splant = np.zeros((n_a, n_i), dtype=np.float32); Splant[g, np.arange(n_i)] = 1.0
    arms = {"A0_RAW_INCUMBENT": rng.standard_normal((n_a, n_i)).astype(np.float32),
            "F4_CONSTANT_PROTOTYPE": as_constant_matrix(proto, n_i),
            "KA_EXACT_KEY_planted": Splant,
            "NULL_PERMUTED_CUE": rng.standard_normal((n_a, n_i)).astype(np.float32)}
    r = score_condition("T4", E, GOLD, keepm, arms, 1.0 / n_a, False, ["F4_CONSTANT_PROTOTYPE"])
    assert r["VALIDITY"]["KA_PASSES"], "planted arm did not reach ceiling: %r" % r["VALIDITY"]
    assert r["hit_at_1_OPTIMISTIC_tie"]["NULL_PERMUTED_CUE"] < 0.05, "null arm is not null"
    assert r["BINDING_FLOOR"] == "F4_CONSTANT_PROTOTYPE"
    res["T4_harness_end_to_end"] = {"KA": r["VALIDITY"]["KNOWN_ANSWER_hit_at_1"],
                                    "NULL": r["VALIDITY"]["NULL_PERMUTED_CUE_hit_at_1"]}

    # T5 -- the two validity arms fail INDEPENDENTLY (demonstrated, not asserted).
    bad = dict(arms); bad["KA_EXACT_KEY_planted"] = arms["NULL_PERMUTED_CUE"]
    r2 = score_condition("T5", E, GOLD, keepm, bad, 1.0 / n_a, False, ["F4_CONSTANT_PROTOTYPE"])
    assert not r2["VALIDITY"]["KA_PASSES"] and r2["VALIDITY"]["NULL_PERMUTED_CUE_hit_at_1"] < 0.05
    leak = dict(arms); leak["NULL_PERMUTED_CUE"] = Splant
    r3 = score_condition("T5b", E, GOLD, keepm, leak, 1.0 / n_a, False, ["F4_CONSTANT_PROTOTYPE"])
    assert r3["VALIDITY"]["KA_PASSES"] and not r3["VALIDITY"]["null_near_chance"], \
        "a leaking NULL was not caught while KA still passed"
    res["T5_validity_arms_fail_independently"] = True

    # T6 -- WITNESS that the bulk top-k agrees with the OWNED organ's own coarse_shortlist, so
    # "reuse" is measured rather than claimed.
    import torch
    from hdlab.context_retention import coarse_shortlist
    Msmall = l2n(rng.standard_normal((300, 64)).astype(np.float32))
    Qsmall = l2n(rng.standard_normal((25, 64)).astype(np.float32))
    cs, proj = coarse_scores(Msmall, Qsmall, 16, MASTER_SEED)
    tp = torch.from_numpy(proj)
    agree = []
    for i in range(Qsmall.shape[0]):
        organ = set(coarse_shortlist(torch.from_numpy(Qsmall[i]), torch.from_numpy(Msmall), tp,
                                     32).numpy().tolist())
        mine = set(np.argpartition(-cs[:, i], 31)[:32].tolist())
        agree.append(len(organ & mine) / 32.0)
    ag = float(np.mean(agree))
    assert ag > 0.99, "bulk shortlist disagrees with hdlab.context_retention.coarse_shortlist: %.4f" \
                      % ag
    res["T6_shortlist_matches_owned_organ"] = round(ag, 4)

    # T7 -- the SATURATION guard trips when every treatment arm is identical.
    same = rng.standard_normal((n_a, n_i)).astype(np.float32)
    sat = {"A0_RAW_INCUMBENT": same, "F4_CONSTANT_PROTOTYPE": same,
           "KA_EXACT_KEY_planted": Splant, "NULL_PERMUTED_CUE": same}
    r4 = score_condition("T7", E, GOLD, keepm, sat, 1.0 / n_a, False, ["F4_CONSTANT_PROTOTYPE"])
    assert r4["VALIDITY"]["saturation_tripped"] and not r4["VALIDITY"]["CONDITION_READABLE"]
    res["T7_saturation_guard_trips"] = True

    print("[selftest] PASS " + json.dumps(res, default=str)[:1500], flush=True)
    return res


# =================================================================================================
# main
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid,
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                 "RULER_MODE_GATE": ruler_mode_gate(),
                 "NO_LLM_IN_OPERATIONAL_FLOW": True,
                 "cache": {"store": CACHE, "aux": AUX, "rebuilt": False}}
    C = load_cache()
    aux = load_aux()
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    qidx = np.array([C["pos"].get(w, -1) for w in C["L_words"]], dtype=np.int64)
    print("[load] n_anchors=%d n_items=%d keep=%d %.0fs" % (
        n_anchors, n_items_all, int(keep.sum()), time.time() - t0), flush=True)

    # ---- FULL-POPULATION gold + eligibility (the incumbent open pool) -------------------------
    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not keep[i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = keep & GOLD_ALL.any(axis=0)

    # ---- REGRESSION GATE: reproduce the landed partial-cue number on the FULL population -------
    S_full = (l2n(mat) @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = hit_at_1_both_tie_conventions(S_full, E_ALL, GOLD_ALL)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    f4_all = constant_prototype_floor(mat, mat_ok)
    h_f4 = hit_at_1_both_tie_conventions(as_constant_matrix(f4_all, n_items_all), E_ALL, GOLD_ALL)
    rep["REGRESSION_GATE"] = {
        "what": "A0 partial-cue on the FULL landed open pool must reproduce the landed value.",
        "A0_partial_tie_corrected_FULL_POP": round(a0_full, 4),
        "expected": REGRESSION_A0_PARTIAL, "tol": REGRESSION_TOL,
        "PASS": bool(abs(a0_full - REGRESSION_A0_PARTIAL) <= REGRESSION_TOL),
        "n_scored": int(m_full.sum()),
        "CONSTANT_FLOOR_on_the_same_full_pool": {
            "tie_corrected": round(float(h_f4["hit_exp"][m_full].mean()), 4),
            "optimistic": round(float(h_f4["hit_opt"][m_full].mean()), 4),
            "conservative": round(float(h_f4["hit_cons"][m_full].mean()), 4),
            "note": "reported under all three conventions because the constant channel carries tie "
                    "mass and a convention chosen silently has already flipped one comparison."},
    }
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- the instrument is not the landed one: %r"
                         % rep["REGRESSION_GATE"])
    print("[regression] A0_partial_FULL=%.4f (expected %.4f) PASS" % (a0_full,
                                                                      REGRESSION_A0_PARTIAL),
          flush=True)
    del S_full, h_full, h_f4

    # ---- ITEM SPLIT: W is fitted on TRAIN, EVERY arm is scored on TEST ------------------------
    elig_items = np.flatnonzero(keep_ALL)
    rs = np.random.default_rng(MASTER_SEED + 3)
    shuf = rs.permutation(elig_items)
    n_test = int(round(TEST_FRAC * shuf.size))
    test_items = np.sort(shuf[:n_test])
    train_items = np.sort(shuf[n_test:])
    if grid == "reduced":
        test_items = test_items[:400]
        train_items = train_items[:800]
    rep["ITEM_SPLIT"] = {
        "n_eligible_items": int(elig_items.size), "n_train_fit_only": int(train_items.size),
        "n_test_scored": int(test_items.size), "test_frac": TEST_FRAC, "seed": MASTER_SEED + 3,
        "why": "the fitted arms (A1, A2b, A6) are fitted ONLY on TRAIN items and EVERY arm is "
               "scored ONLY on TEST items, so no arm is ever compared across populations and A1 "
               "cannot memorise a scored item."}
    print("[split] train=%d test=%d" % (train_items.size, test_items.size), flush=True)

    # ---- restrict every per-item object to the TEST columns -----------------------------------
    T = test_items
    n_items = int(T.size)
    L_test = [C["L_words"][int(i)] for i in T]
    GOLD = GOLD_ALL[:, T].copy()
    E_OPEN = E_ALL[:, T].copy()
    keep_T = np.ones(n_items, dtype=bool)
    excl_T = [C["excl"][int(i)] for i in T]
    gold_lists = [np.flatnonzero(GOLD[:, i]) for i in range(n_items)]
    qidx_T = qidx[T]

    # ---- the fitted maps, per regime ----------------------------------------------------------
    Wmaps: Dict[str, Dict] = {}
    cue_of = {"EXACT_KEY": C["Q_exact"], "PARTIAL_CUE": C["Q_part"]}
    for regime, Q in cue_of.items():
        Ctr = l2n(Q[train_items])
        Ttr = l2n(mat[qidx[train_items]])
        lam, lam_trace = select_ridge_lam(Ctr, Ttr, MASTER_SEED + 21)
        W = fit_ridge(Ctr, Ttr, lam)
        pshuf = np.random.default_rng(MASTER_SEED + 22).permutation(Ctr.shape[0])
        Wsh = fit_ridge(Ctr, Ttr[pshuf], lam)
        rr = np.random.default_rng(MASTER_SEED + 23)
        Wrand = rr.standard_normal(W.shape).astype(np.float32)
        Wrand *= float(np.linalg.norm(W) / (np.linalg.norm(Wrand) + 1e-12))
        cos_cue_to_own_row = float(np.mean(np.sum(l2n(Q[T]) * l2n(mat[qidx_T]), axis=1)))
        Wmaps[regime] = {
            "W": W, "W_shuf": Wsh, "W_rand": Wrand, "lam": lam,
            "diag": {
                "ridge_lam": lam, "lam_selection_trace_heldout_MSE_gold_blind": lam_trace,
                "W_frobenius": round(float(np.linalg.norm(W)), 4),
                "W_shuffled_frobenius": round(float(np.linalg.norm(Wsh)), 4),
                "cos_cue_to_its_OWN_stored_row_on_TEST": round(cos_cue_to_own_row, 4),
                "note": "if cos_cue_to_its_OWN_stored_row is near 1.0 the ridge for this regime is "
                        "a near-identity fit by construction and A1 cannot differ much from A0; "
                        "that is a property of the cue, and it is reported rather than hidden."}}
        np.save(os.path.join(OUT_DIR, "W_%s.npy" % regime), W)
    rep["FITTED_MAPS"] = {r: v["diag"] for r, v in Wmaps.items()}
    rep["FITTED_MAPS"]["glass_box"] = ("W is a 256x256 matrix written to data/%s/W_<regime>.npy. "
                                       "Fitted offline by closed-form ridge from the substrate's "
                                       "own vectors. Inference is ONE matmul. No LLM." % ANCHOR_NAME)

    # ---- whitening (A3): fit on the STORE, apply to both sides ---------------------------------
    from hdlab.whitening import WhiteningTransform
    wt = WhiteningTransform(mode="zca", eps=1e-3).fit(mat[mat_ok])
    mat_w = l2n(wt.transform(mat))
    rep["WHITENING"] = {"organ": "hdlab.whitening.WhiteningTransform(mode=zca, eps=1e-3)",
                        "fitted_on": "the STORE rows (mat[mat_ok]); the same transform is applied "
                                     "to the cue, which is what makes it a rank-equalisation and "
                                     "not a learned correspondence",
                        "n_fit_rows": int(mat_ok.sum())}

    # ---- DG keys + A8b audit, READ BEFORE ANY A8 SCORE ----------------------------------------
    from hdlab.dg_pattern_separation import projection_matrix
    t_dg = time.time()
    W_dg = projection_matrix(mat.shape[1], DG_EXPAND, DG_TAG)
    K_store = dg_keys(mat, W_dg)
    rep["A8b_KEY_COLLISION_AUDIT"] = key_collision_audit(K_store, mat, W_dg, mat_ok)
    rep["A8b_KEY_COLLISION_AUDIT"]["elapsed_s"] = round(time.time() - t_dg, 1)
    print("[A8b] collisions=%.4f address_acc=%.4f usable=%s" % (
        rep["A8b_KEY_COLLISION_AUDIT"]["collision_rate"],
        rep["A8b_KEY_COLLISION_AUDIT"]["EXACT_KEY_ADDRESSING_ACCURACY_alpha0.5"],
        rep["A8b_KEY_COLLISION_AUDIT"]["ADDRESS_USABLE"]), flush=True)

    # ---- static arms (regime-independent) ------------------------------------------------------
    f4 = constant_prototype_floor(mat, mat_ok)
    STATIC: Dict[str, np.ndarray] = {
        "F1_ORTHO_TRIGRAM": (aux["t_mat"] @ aux["Tq"][T].T).astype(np.float32),
        "F1b_ORTHO_PREFIX": aux["Pq"][T].T.astype(np.float32),
        "F2_FREQUENCY": col(frequency_floor(np.expm1(aux["fq"].astype(np.float64)))),
        "F4_CONSTANT_PROTOTYPE": col(f4),
    }
    FLOORS = ("F1_ORTHO_TRIGRAM", "F1b_ORTHO_PREFIX", "F2_FREQUENCY", "F3_SCRAMBLE_NULL",
              "F4_CONSTANT_PROTOTYPE")

    # ---- designated gold per condition ---------------------------------------------------------
    def designate(G: np.ndarray, km: np.ndarray, seed: int) -> np.ndarray:
        r = np.random.default_rng(seed)
        d = np.full(n_items, -1, dtype=np.int64)
        for i in np.flatnonzero(km):
            gi = np.flatnonzero(G[:, i])
            if gi.size:
                d[i] = int(gi[r.integers(0, gi.size)])
        return d

    designated = designate(GOLD, keep_T, MASTER_SEED + 5)

    # ---- P1b morphology-blocked open pool ------------------------------------------------------
    E_MORPH = E_OPEN.copy()
    n_blocked = 0
    for i in range(n_items):
        Lw = L_test[i]
        blk = np.array([j for j in np.flatnonzero(E_MORPH[:, i])
                        if _lcp(Lw, anchors[int(j)]) >= MORPH_LCP], dtype=np.int64)
        if blk.size:
            E_MORPH[blk, i] = False
            n_blocked += int(blk.size)
    GOLD_M = GOLD & E_MORPH
    keep_M = GOLD_M.any(axis=0)

    # ---- balanced + matched pools --------------------------------------------------------------
    cand_b, _gcb = balanced_candidate_sets(designated, gold_lists, excl_T, keep_T, K_BAL,
                                           MASTER_SEED + 17)
    ok_b = cand_b[:, 0] >= 0
    cand_m, _gcm, dmatch = matched_candidate_sets(designated, gold_lists, excl_T, keep_T, K_BAL,
                                                  MASTER_SEED + 31, STATIC["F1_ORTHO_TRIGRAM"])
    ok_m = cand_m[:, 0] >= 0

    def _elig_from_cand(cand: np.ndarray, ok: np.ndarray) -> np.ndarray:
        Ec = np.zeros((n_anchors, n_items), dtype=bool)
        rows = cand[ok]
        cols = np.repeat(np.flatnonzero(ok)[:, None], K_BAL + 1, axis=1)
        Ec[rows.ravel(), cols.ravel()] = True
        return Ec

    E_BAL = _elig_from_cand(cand_b, ok_b)
    E_MAT = _elig_from_cand(cand_m, ok_m)
    assert int((E_BAL & GOLD).sum(axis=0)[ok_b].max()) == 1, "balanced pool has 2 correct answers"
    assert int((E_MAT & GOLD).sum(axis=0)[ok_m].max()) == 1, "matched pool has 2 correct answers"

    n_elig_open = E_OPEN.sum(axis=0)
    chance_open = float(np.mean(GOLD[:, keep_T].sum(axis=0) / np.maximum(n_elig_open[keep_T], 1)))
    n_elig_m = E_MORPH.sum(axis=0)
    chance_morph = float(np.mean(GOLD_M[:, keep_M].sum(axis=0) / np.maximum(n_elig_m[keep_M], 1)))

    conditions: Dict[str, Dict] = {
        "P1_OPEN": {"E": E_OPEN, "GOLD": GOLD, "keep": keep_T, "chance": chance_open, "rank": True,
                    "what": "the incumbent open pool, TEST half. Continuity with the landed number."},
        "P1b_OPEN_MORPHBLOCK": {
            "E": E_MORPH, "GOLD": GOLD_M, "keep": keep_M, "chance": chance_morph, "rank": True,
            "n_pool_entries_blocked": n_blocked, "lcp_threshold": MORPH_LCP,
            "what": "open pool with every anchor sharing a %d+ character prefix with the query word "
                    "deleted from the pool AND from the gold sets. The OUTPUT-side spelling block. "
                    "It is NOT the cue-feature morphology block the design asked for -- that is not "
                    "constructible on a 256-dim dense cue with no word-identified features."
                    % MORPH_LCP},
        "P2_BALANCED_K%d" % K_BAL: {
            "E": E_BAL, "GOLD": GOLD, "keep": ok_b, "chance": 1.0 / (K_BAL + 1), "rank": False,
            "what": "DE-BIASED. Per-item pool = designated gold + %d distractors drawn from the "
                    "population of OTHER items' golds, so no item-independent (constant) ranking "
                    "can beat chance %.4f. Verified by the ORACLE arm, not assumed."
                    % (K_BAL, 1.0 / (K_BAL + 1))},
        "P3_MATCHED_K%d" % K_BAL: {
            "E": E_MAT, "GOLD": GOLD, "keep": ok_m, "chance": 1.0 / (K_BAL + 1), "rank": False,
            "match_diagnostics": dmatch,
            "what": "STRICTER. As P2, plus every distractor matched to the gold on trigram "
                    "similarity to the query word, so the SPELLING channel is neutralised too. "
                    "Sub-selecting donors perturbs role symmetry, so the constant arms are re-read "
                    "on this pool and never inherited from P2."},
    }

    # ---- per-condition constants ---------------------------------------------------------------
    ORACLE: Dict[str, np.ndarray] = {}
    KAS: Dict[str, np.ndarray] = {}
    for cname, cfg in conditions.items():
        G = cfg["GOLD"]
        kk = np.flatnonzero(cfg["keep"])
        restricted = cname.startswith(("P2_", "P3_"))
        ORACLE[cname] = col(oracle_constant_scores(
            n_anchors, [np.flatnonzero(G[:, i]) for i in kk],
            ([np.flatnonzero(cfg["E"][:, i]) for i in kk] if restricted else None)))
        d = designate(G, cfg["keep"], MASTER_SEED + 5)
        Qka = np.zeros((n_items, mat.shape[1]), dtype=np.float32)
        okd = d >= 0
        Qka[okd] = mat[d[okd]]
        KAS[cname] = (l2n(mat) @ l2n(Qka).T).astype(np.float32)

    # ---- run every regime x condition ----------------------------------------------------------
    results: Dict[str, Dict] = {}
    a8diag: Dict[str, Dict] = {}
    matn = l2n(mat)
    for regime, Qfull in cue_of.items():
        Q = Qfull[T]
        Qn = l2n(Q)
        WM = Wmaps[regime]
        arms: Dict[str, np.ndarray] = dict(STATIC)
        arms["A0_RAW_INCUMBENT"] = (matn @ Qn.T).astype(np.float32)
        arms["A1_LEARNED_LINEAR_MAP"] = (matn @ l2n(Qn @ WM["W"]).T).astype(np.float32)
        arms["A2_FIXED_RANDOM_MAP"] = (matn @ l2n(Qn @ WM["W_rand"]).T).astype(np.float32)
        arms["A2b_SHUFFLED_PAIRING_MAP"] = (matn @ l2n(Qn @ WM["W_shuf"]).T).astype(np.float32)
        arms["A3_WHITEN_ONLY"] = (mat_w @ l2n(wt.transform(Q)).T).astype(np.float32)
        cue_keys = dg_keys(Q, W_dg)
        arms["A8_LINK_HARD_alpha0.5"] = link_not_reconstruct(cue_keys, K_store, mat,
                                                             CA3_ALPHA_CLAMP, True)
        arms["A8_LINK_SOFT_alpha0.5"] = link_not_reconstruct(cue_keys, K_store, mat,
                                                             CA3_ALPHA_CLAMP, False)
        arms["A8_LINK_SOFT_alpha0.0"] = link_not_reconstruct(cue_keys, K_store, mat,
                                                             CA3_ALPHA_NOCLAMP, False)
        # DO THE THREE A8 VARIANTS ACTUALLY DIFFER? They read identically to 4dp on the reduced
        # grid, and "identical to 4dp" is either a real finding (the clamp does not move the
        # address) or a coding bug. Measured rather than assumed.
        a8h, a8s, a8z = (arms["A8_LINK_HARD_alpha0.5"], arms["A8_LINK_SOFT_alpha0.5"],
                         arms["A8_LINK_SOFT_alpha0.0"])
        a8diag.setdefault(regime, {})["VARIANT_DIVERGENCE"] = {
            "hard_vs_soft_score_matrices_bit_identical": bool(np.array_equal(a8h, a8s)),
            "soft_alpha0.5_vs_alpha0.0_bit_identical": bool(np.array_equal(a8s, a8z)),
            "hard_vs_soft_argmax_agreement": round(float(np.mean(
                np.argmax(a8h, axis=0) == np.argmax(a8s, axis=0))), 4),
            "alpha0.5_vs_alpha0.0_argmax_agreement": round(float(np.mean(
                np.argmax(a8s, axis=0) == np.argmax(a8z, axis=0))), 4),
            "max_abs_score_diff_hard_vs_soft": round(float(np.abs(a8h - a8s).max()), 6),
            "max_abs_score_diff_alpha": round(float(np.abs(a8s - a8z).max()), 6)}
        a8diag[regime]["ADDRESSING_alpha0.5"] = address_diagnostic(
            cue_keys, K_store, qidx_T, CA3_ALPHA_CLAMP)
        a8diag[regime]["ADDRESSING_alpha0.0"] = address_diagnostic(
            cue_keys, K_store, qidx_T, CA3_ALPHA_NOCLAMP)
        print("[A8 %s] addressed_item_is_query_word a0.5=%.4f a0.0=%.4f" % (
            regime, a8diag[regime]["ADDRESSING_alpha0.5"]["addressed_item_IS_the_query_word"],
            a8diag[regime]["ADDRESSING_alpha0.0"]["addressed_item_IS_the_query_word"]), flush=True)
        del a8h, a8s, a8z, cue_keys
        arms["F3_SCRAMBLE_NULL"] = (l2n(scramble_null(mat, MASTER_SEED)) @ Qn.T).astype(np.float32)
        pcue = np.random.default_rng(MASTER_SEED + 55).permutation(n_items)
        arms["NULL_PERMUTED_CUE"] = arms["A0_RAW_INCUMBENT"][:, pcue].copy()
        cs, _proj = coarse_scores(mat, Q, 64, MASTER_SEED)

        for cname, cfg in conditions.items():
            Ec, G = cfg["E"], cfg["GOLD"]
            a2 = dict(arms)
            a2["KA_EXACT_KEY_planted"] = KAS[cname]
            a2["ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"] = ORACLE[cname]
            Mg = topk_mask_within(Ec, cs, SHORT_FRAC, None)
            Mr = topk_mask_within(Ec, cs, SHORT_FRAC,
                                  np.random.default_rng(MASTER_SEED + 91))
            NEG = np.float32(-1e30)
            a2["A5_NARROW_THEN_READ"] = np.where(Mg, arms["A0_RAW_INCUMBENT"], NEG)
            a2["A5r_RANDOM_GATE_size_matched"] = np.where(Mr, arms["A0_RAW_INCUMBENT"], NEG)
            a2["A6_MAP_INSIDE_NARROW"] = np.where(Mg, arms["A1_LEARNED_LINEAR_MAP"], NEG)
            a2["A7_SPLIT_LEXICON_decision_level"] = split_lexicon(
                arms["F1_ORTHO_TRIGRAM"], arms["A0_RAW_INCUMBENT"], Ec)
            key = "%s|%s" % (cname, regime)
            results[key] = score_condition(key, Ec, G, cfg["keep"], a2, cfg["chance"],
                                           bool(cfg["rank"]), FLOORS)
            results[key]["condition_note"] = cfg["what"]
            results[key]["shortlist_frac"] = SHORT_FRAC
            if not rep["A8b_KEY_COLLISION_AUDIT"]["ADDRESS_USABLE"]:
                results[key]["A8_STATUS"] = (
                    "VOID_ADDRESS -- exact-key addressing accuracy %.4f < gate %.2f, so no A8 "
                    "number in this condition is evidence about link-not-reconstruct."
                    % (rep["A8b_KEY_COLLISION_AUDIT"]["EXACT_KEY_ADDRESSING_ACCURACY_alpha0.5"],
                       ADDRESS_GATE))
            else:
                results[key]["A8_STATUS"] = "ADDRESS_USABLE"
            del a2, Mg, Mr
        del arms, cs

    rep["CONDITIONS"] = {
        k: dict({kk: vv for kk, vv in v.items() if kk not in ("E", "GOLD", "keep")},
                n_items_in_condition=int(np.asarray(v["keep"]).sum())) for k, v in
        conditions.items()}
    rep["RESULTS"] = results
    rep["A8_MECHANISM_DIAGNOSTICS"] = a8diag
    rep["A8_MECHANISM_DIAGNOSTICS"]["how_to_read"] = (
        "link-not-reconstruct has TWO stages. addressed_item_IS_the_query_word is the ADDRESS "
        "stage; the arm's hit@1 is the ADDRESS plus the LINK. If addressing is near 1.0 under the "
        "exact key and near 0 under the partial cue, the July design is not refuted -- the cue "
        "never reaches the right trace, and the gap is upstream of the link.")
    rep["ENCODING_SPECIFICITY_CONTRAST"] = {
        "what": "the admissible substitute for A4_CONTEXT_BOUND_STORE, which is NOT BUILDABLE from "
                "the cached artefact (the per-occurrence context stream was consumed inside "
                "exp_grounding_readout_known_answer_v1.build_space and never persisted; rebuilding "
                "it would break the identical-instrument invariant). EXACT_KEY is a cue that IS the "
                "encoded aggregate; PARTIAL_CUE is a sentence DELIBERATELY EXCLUDED from the trace. "
                "Same store, same pool, same scorer.",
        "per_pool_A0_exact_minus_partial": {
            c: {"EXACT_KEY": results["%s|EXACT_KEY" % c]["hit_at_1_TIE_CORRECTED_primary"].get(
                    "A0_RAW_INCUMBENT"),
                "PARTIAL_CUE": results["%s|PARTIAL_CUE" % c]["hit_at_1_TIE_CORRECTED_primary"].get(
                    "A0_RAW_INCUMBENT"),
                "chance": results["%s|PARTIAL_CUE" % c]["chance_for_THIS_condition"]}
            for c in conditions if "%s|EXACT_KEY" % c in results},
        "caveat": "this measures ENCODING SPECIFICITY. It does NOT test a context-BOUND store, and "
                  "no claim about one is made here.",
    }
    rep["BRAIN_FIDELITY"] = {
        "structures_not_cognitive_labels": {
            "entorhinal cortex (EC layer II/III)": "the gateway that delivers the retrieval cue as "
                                                   "a compressed, typed cortical code. OURS: the "
                                                   "held-out-sentence context vector stands in for "
                                                   "it. INVENTION UNDER TEST.",
            "direct perforant path EC-II -> CA3": "the RETRIEVAL-cue wire, numerically large, "
                                                  "individually weak, associatively modified during "
                                                  "storage. PINNED (Treves & Rolls 1992; Rolls "
                                                  "2018). OURS: the ridge W stands in for the "
                                                  "associatively-modified matrix (arm A1) and the "
                                                  "iterative_cleanup alpha term stands in for the "
                                                  "continuous perforant drive (arms A8).",
            "mossy fibre EC-II -> DG -> CA3": "the STORAGE wire, few and powerful. PINNED. OURS: "
                                              "dg_separate at %.0f%% sparsity builds the key."
                                              % (100 * DG_SPARSITY),
            "dentate gyrus": "expansion recoding + sparsification. PINNED (Leutgeb 2007; Guzman "
                             "2016; McHugh 2007). ORGAN: hdlab.dg_pattern_separation.",
            "CA3": "autoassociative completer. PINNED. ORGAN: hdlab.iterative_attractor. OURS: the "
                   "softmax attractor update rule is not pinned; ORGAN_MAP.md:1732 records the CA3 "
                   "UPDATE RULE as explicitly UNPINNED and this cell does not change that.",
            "CA1 / hippocampal index": "heteroassociative recode and cortical reinstatement -- the "
                                       "hippocampus returns a LINKED cortical value, it does not "
                                       "decode content from its own index. PINNED (Teyler & Rudy "
                                       "2007; Goode 2020). OURS: arm A8's linked dense value.",
            "inhibitory normalisation of the live set": "PINNED that SIZE is controlled; the "
                                                        "MECHANISM (a coarse random projection "
                                                        "shortlist) is OURS. Arms A5 / A5r.",
            "two-stage lexical access (lemma then word form)": "PINNED, dissociated by anomia. "
                                                               "OURS: trigram store as the FORM "
                                                               "lexicon. Arm A7.",
        },
        "organ_reuse_ENUMERATED_FROM_DISK_then_reconciled": {
            "method": "each module below was IMPORTED and its callables read at runtime; the "
                      "registry was consulted AFTER, never as the frame of the audit.",
            "hdlab.dg_pattern_separation": "dg_separate + projection_matrix. NOTE: there is NO "
                                           "dg_expand_sparsify -- that name does not exist.",
            "hdlab.iterative_attractor": "iterative_cleanup; alpha IS the perforant cue-clamp and "
                                         "DEFAULTS TO 0.0, so it is passed EXPLICITLY here "
                                         "(%.2f clamped, %.2f unclamped contrast)."
                                         % (CA3_ALPHA_CLAMP, CA3_ALPHA_NOCLAMP),
            "hdlab.context_retention": "build_coarse_projection + coarse_shortlist (self-test T6 "
                                       "witnesses agreement with the bulk top-k).",
            "hdlab.whitening": "WhiteningTransform(zca).",
            "tools.floor_battery": "the whole floor + pool ladder.",
            "hdlab.grounded_similarity": "NEVER CALLED. grounded_similarity() is barred as a scorer.",
            "registry_caveat": "data/capability_registry.jsonl carries mutually contradictory rows "
                               "for dg_pattern_separation, context_retention and cleanup_family, so "
                               "'the registry says X' is not a usable single fact for them. The "
                               "registry is not written by this cell.",
        },
        "shelve_revival_criteria_BRAIN_framed": {
            "make the cue a fragment of the target": "STAYS SHELVED. The brain's retrieval cue is "
                                                     "not a subset of the stored pattern and "
                                                     "arrives on a different wire. REVIVE only if "
                                                     "evidence appears that a cortical stream "
                                                     "delivers a literal subset of a hippocampal "
                                                     "pattern.",
            "the autoassociative completer": "DO NOT SHELVE. It is the correct organ for cue type "
                                             "(a) degraded-copy and has never been tested on a "
                                             "type-(a) cue in this substrate. REVIVE-TEST: build a "
                                             "genuine degraded copy of a stored row and complete it.",
            "link-not-reconstruct (A8)": "shelve ONLY if the key space cannot address the store "
                                         "from the store's OWN rows (A8b below gate) AND a denser "
                                         "or differently-sparsified key does not fix it. A failure "
                                         "at a single sparsity is a failure of THAT key, not of the "
                                         "indexing architecture.",
        },
    }
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    out = OUT_DIR + ("_selftest" if a.self_test else "")
    os.makedirs(out, exist_ok=True)
    if a.self_test:
        r = self_test()
        _atomic_json(os.path.join(out, "metrics.json"),
                     {"verdict": "SELFTEST_PASS", "verdict_msg": "all self-tests passed",
                      "elapsed_s": 0.0, "summary": "selftest", "detail": r})
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(a.grid)
        rep.setdefault("verdict", "COMPUTED")
        rep.setdefault("verdict_msg", "see RESULTS; gates are per-condition")
        rep.setdefault("summary", "cue->store translation ladder")
        rep["structured_gate_claims"] = [
            record_gate("regression_A0_partial_full_pool",
                        rep["REGRESSION_GATE"]["A0_partial_tie_corrected_FULL_POP"],
                        REGRESSION_A0_PARTIAL, "==",
                        "the instrument must be the landed one"),
            record_gate("A8b_exact_key_addressing_accuracy",
                        rep["A8b_KEY_COLLISION_AUDIT"]["EXACT_KEY_ADDRESSING_ACCURACY_alpha0.5"],
                        ADDRESS_GATE, ">=",
                        "read BEFORE any A8 score; below this A8 is VOID_ADDRESS"),
        ]
        _atomic_json(os.path.join(OUT_DIR, "metrics.json"), rep)
        print("WROTE " + os.path.join(OUT_DIR, "metrics.json"), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(OUT_DIR, "_crash_diagnostic.json"),
                     {"error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
