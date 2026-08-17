"""exp_cue_information_audit_v1 -- IS THE ANSWER IN THE CUE AT ALL?

THE QUESTION THIS CELL EXISTS TO SETTLE, AND WHY IT DECIDES THE WHOLE PROGRAMME'S DIRECTION.
Before any of our machinery (expansion, completer, translator, addressing scheme) touches the
partial cue, does the partial cue CONTAIN ENOUGH INFORMATION to identify its target at all? If it
does not, no downstream mechanism can help, and the blocker relocates upstream to WHAT WE WRITE
(the encoder / the store), not to how we READ. That outcome is a GOOD one -- it is a real answer,
not a defeat -- and is reported as such.

BRAIN STRUCTURE: NONE IS CLAIMED, AND NONE IS FABRICATED HERE.
This is an INFORMATION AUDIT OF OUR OWN ENCODER, not a model of any neural structure. Saying so
plainly is the honest answer; inventing an anatomy to fill the box is exactly the laundering the
project's brain-fidelity gate exists to ban. (The adjacent brain claim that IS pinned -- Treves &
Rolls' two-input argument that a numerically large DENSE cortical cue should address a SPARSE store
through a learned map -- belongs to the sibling build item, not to this measurement.)

THE ONE-VARIABLE CONTROL THAT MAKES THIS CONSTRUCTIBLE (the encoder's own algebraic identity).
`context_vector(text, graded=True)` (hdlab/grounding_acquisition_loop.py:117) is, verbatim:
    words = content_words(text)                      # a LIST, NOT deduplicated -- repeats count
    acc = sum( symbol_vector(w) for w in words )      # symbol_vector = sha256(w)-seeded bipolar draw
    return acc                                        # (graded=True: no terminal sign())
So for any bag of content words W with per-word counts p, `context_vector(...) == H^T p` where H's
row for word w IS `symbol_vector(w)` (hdlab.reading_grounding_loop.symbol_vector, itself documented
BYTE-IDENTICAL to context_vector's own inline per-word draw). ConceptSpace.observe(lemma, ctx_vec)
just accumulates `self._sums[lemma] += ctx_vec` (hdlab/reading_grounding_loop.py:478-482), so the
STORE row for anchor a is `mat[a] == H^T P_a` where P_a is the TOTAL raw surface-word count vector
over every PROFILE-split occurrence of a in the corpus (experiments/exp_grounding_readout_known_
answer_v1.py build_space / build_buckets), and the CUE for item i is `Q_part[i] == H^T q_i` where
q_i is the raw count vector of its held-out sentence, masked of the target lemma's own tokens.
`cos(mat[a], Q_part[i])` (the incumbent, C0) and `cos(P_a, q_i)` (U0, this cell's new arm) THEREFORE
DIFFER BY EXACTLY ONE THING: the random projection H. An UNCOMPRESSED arm scored on P_a / q_i
directly is a genuine ONE-VARIABLE CONTROL on our own encoder -- not a different encoder, not a
different corpus, not a different pool. `H^T P_a == mat[a]` and `H^T q_i == Q_part[i]` are asserted
BIT-EXACT (float64 accumulation of +/-1 draws is exact up to 2^53; the float32 cache cast is exact
for magnitudes this small) as the cell's own precondition gate, not adopted from any other agent's
number -- see RECOVERABILITY_GATE below, which REPRODUCES rather than imports the prior fragment's
finding (.claude/scan-out/address-information-audit.json, attributed, never adopted).

ARMS, on the IDENTICAL store, cue, pool and gold (the harness cache built by the 2026-08-16 cells,
scratch/sparse_code_real_task/real_cache.npz -- UNMODIFIED, reused so every number here is on the
SAME population exp_task_degeneracy_v1 and exp_cue_to_store_translation_v1 already measured):
  C0_PROJECTED_256   the incumbent: cos(mat[a], Q_part[i]) in the 256-dim projected space.
  U0_UNCOMPRESSED    THE ARM THAT DECIDES THE ITEM: cos(P_a, q_i), raw sparse count vectors, no
                     projection. Computed via scipy.sparse over a shared content-word vocabulary.
  K1_EXACT_KEY       known-answer: query = the item's OWN store row (C0) / OWN count vector (U0).
                     PRIMARY MEASURE (addressing accuracy) must sit at 1.0000 in both regimes, or
                     the instrument is dead and no quality number is published.
  N1_RANDOM_KEY      size-matched random address: the REAL cue reassigned to a different item
                     (same construction, same size, permuted item<->cue pairing). Must sit at the
                     empirical chance rate (~1/n_anchors_eligible).
  CUE-KIND SPLIT (ONLY IF RECOVERABILITY HOLDS; SECONDARY, reported beside the decisive C0/U0 pair,
  never in place of it): the owner's description of a partial cue has TWO parts -- word-onset and
  same-meaning neighbours -- and our machinery implements a THIRD, a degraded copy (the context
  sentence). Reported separately, never averaged with the primary comparison:
    SYNONYM_SET   cue = the item's own WordNet synonym/hypernym/hyponym LEMMAS (excluding the
                  target and its morphological variants), encoded through the SAME hash-seeded
                  symbol map as the context cue. ADDRESSING accuracy is a clean read (identity is
                  never in the cue); the SECONDARY hit@1-vs-WordNet-gold read for this cue kind is
                  built from the SAME relation that builds the gold set and is labelled
                  INADMISSIBLE_CIRCULAR, never read as a capability result.
    WORD_ONSET    cue = the word's own first 4 characters, treated as ONE symbol through the SAME
                  hash-seeded map. A degenerate, maximally orthographic partial cue.

PRIMARY MEASURE: addressing accuracy (`addressed_item_IS_the_query_word` -- argmax over all
eligible anchors of cos(anchor, cue) equals the item's OWN anchor index). SECONDARY: hit@1 against
the WordNet meaning-set gold, scored on the identical harness pool/floors as the sibling cells
(tools/floor_battery, reused unmodified).

FLOOR. Addressing accuracy must clear the size-matched random-key control (N1), CI-separated,
paired bootstrap (tools.floor_battery.paired_bootstrap_ci + margin). hit@1 must clear
max(orthographic, frequency, scramble, constant/prototype), EACH RECOMPUTED ON THIS ITEM'S OWN
POPULATION, both tie conventions -- NEVER importing 0.1382, 0.2070 or -0.1959 from another
population. The exact-key arm is reported ALONGSIDE the partial-cue arm always, never instead of it
-- an exact-key number does not transfer to the partial-cue regime, which is the real operating
point. Every margin is reported with its CI half-width; the null's own p95/chance sits beside it.

STOP-IF (pre-registered here, before any number is read):
  (i)   U0_UNCOMPRESSED lands NEAR C0_PROJECTED_256's level (NOT_SEPARATED, or BELOW) on the
        primary addressing-accuracy comparison -> THE INFORMATION IS NOT IN THE CUE. The
        address-side build (sibling plan item 3's capability half) is VOID AS A CAPABILITY CLAIM
        and the programme redirects to the write side. Reported LOUDLY: this is a good outcome.
  (ii)  K1_EXACT_KEY is not 1.0000 in either regime -> INSTRUMENT_STILL_LOOSE. No quality number
        published; the report states this and stops there.
  (iii) U0 beats C0 CI-separated -> the COMPRESSION is the defect, with a measured target; the
        sibling item becomes an expansion question. (A fourth, non-pre-registered outcome -- U0
        CI-separated BELOW C0 -- is also possible and is reported plainly if it occurs; it was not
        one of the three pre-registered readings and is not forced into one.)

RUNNER: cpu_runner_local. Sparse count vectors over the harness's ~2,000-item eligible pool and
~5,491-anchor store are cheap; the one non-trivial cost is a single full-corpus tokenisation pass
(shared by smoke and full via a private cache) to recover the raw content-word counts, which is the
SAME cost the original store build already paid.

PROGRESS LOGGING: every phase prints a flushed line; expected wall time for --grid full can exceed
1800s (the corpus tokenisation + full anchor-count build), so this is mandatory, not decorative.

ASCII-only. No LLM anywhere in this path. Writes only under data/exp_cue_information_audit_v1[_smoke]/
and a private cache under scratch/cue_information_audit_v1/ (gitignored, may be cleared). No file
under data/foundation/, hdlab/, tools/floor_battery.py or tools/exp_checkpoint.py is written.
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
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.floor_battery import (                                              # noqa: E402
    constant_prototype_floor, frequency_floor, hit_at_1_both_tie_conventions, l2n, margin,
    paired_bootstrap_ci, scramble_null,
)
from tools.exp_checkpoint import load_units, record_unit, unit_key             # noqa: E402

import experiments.exp_task_degeneracy_v1 as DEG                                # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3                  # noqa: E402
from hdlab.reading_grounding_loop import (                                      # noqa: E402
    CTX_D, content_words, context_vector_masked, normalize_lemma, symbol_vector,
)

ANCHOR_NAME = "exp_cue_information_audit_v1"
BUCKET_CACHE = os.path.join(REPO_ROOT, "scratch", "cue_information_audit_v1", "buckets_full.npz")

MASTER_SEED = 20260817
N_BOOT = 10000
KA_CEILING_MIN = 0.999
ONSET_LEN = 4
N_SMOKE_ITEMS = 150
ANCHOR_POOL_SMOKE = 250
RECOVERABILITY_SAMPLE_FULL = None      # None = check every keep_ALL item, not a subsample
# PROVENANCE: exp_cue_to_store_translation_v1.py:193 -- the landed A0 partial-cue tie-corrected
# hit@1 on the FULL open pool, on this SAME harness cache. Reused here as the regression gate that
# proves this cell is scoring the identical store/cue/pool/gold, not a drifted copy.
REGRESSION_A0_PARTIAL = 0.0223
REGRESSION_TOL = 5e-4


def _out_dir(grid: str) -> str:
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + ("_smoke" if grid == "reduced" else ""))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# THE ENCODER IDENTITY -- raw counts <-> the projected store, both directions
# =================================================================================================
def raw_counts_for_window(sentence: str, target_lemma: str) -> Counter:
    """The RAW SURFACE-WORD COUNT VECTOR p such that H^T p == context_vector_masked(sentence,
    target_lemma, graded=True). Mirrors context_vector_masked's own construction exactly:
    content_words(sentence) with every token whose LEMMA == target_lemma removed, kept WITH
    repeats (content_words does not dedupe, so a repeated word counts multiple times -- this is
    what makes it a genuine COUNT vector rather than a set)."""
    return Counter(w for w in content_words(sentence) if normalize_lemma(w) != target_lemma)


def reconstruct_bipolar(counts: Counter, d: int = CTX_D) -> np.ndarray:
    """H^T p via the OWNED, byte-identical symbol map (hdlab.reading_grounding_loop.symbol_vector).
    float64 accumulation of +/-1 draws is exact up to 2**53; nothing here can drift."""
    acc = np.zeros(d, dtype=np.float64)
    for w, c in counts.items():
        acc += float(c) * symbol_vector(w, d)
    return acc


# =================================================================================================
# SHIM SPACE -- re-derives `items` (and each item's held-out sent_idx) from the CACHED anchor
# matrix, without re-running the ConceptSpace accumulation. Read-only stand-in for hdlab's own
# ConceptSpace; C3.build_items only ever calls .anchors() and .bundle() on it.
# =================================================================================================
class _ShimSpace:
    def __init__(self, anchors: Sequence[str], pos: Dict[str, int], mat: np.ndarray) -> None:
        self._anchors = list(anchors)
        self._pos = pos
        self._mat = mat

    def anchors(self) -> List[str]:
        return list(self._anchors)

    def bundle(self, lemma: str) -> Optional[np.ndarray]:
        i = self._pos.get(lemma)
        return None if i is None else self._mat[i]


def load_corpus_and_buckets() -> Tuple[List[str], Dict[str, List[int]], Dict[str, int], Dict]:
    """Full corpus + lemma buckets, cached under this cell's OWN scratch dir so smoke and full
    (and any resume) pay the one-time tokenisation cost once. NEVER writes to data/foundation/ or
    to any other cell's scratch/ subdirectory."""
    if os.path.exists(BUCKET_CACHE):
        z = np.load(BUCKET_CACHE, allow_pickle=False)
        sents = [str(s) for s in z["sents"]]
        buckets = json.loads(str(z["buckets_json"]))
        counts = json.loads(str(z["counts_json"]))
        return sents, buckets, counts, {"source": "reused", "path": BUCKET_CACHE}
    t0 = time.time()
    sents = C3.build_corpus("full")
    buckets, counts = C3.build_buckets(sents)
    os.makedirs(os.path.dirname(BUCKET_CACHE), exist_ok=True)
    tmp = BUCKET_CACHE + ".tmp.npz"
    np.savez_compressed(tmp, sents=np.array(sents),
                        buckets_json=json.dumps(buckets), counts_json=json.dumps(dict(counts)))
    os.replace(tmp, BUCKET_CACHE)
    elapsed = round(time.time() - t0, 1)
    print("[corpus] built %d sentences, %d lemma buckets in %.0fs" % (
        len(sents), len(buckets), elapsed), flush=True)
    return sents, buckets, dict(counts), {"source": "rebuilt", "elapsed_s": elapsed}


def verify_recoverability(items: List[dict], C: Dict, sents: List[str]) -> Dict:
    """THE BLOCKING SUB-QUESTION. Checked here, not imported: an earlier agent's fragment
    (.claude/scan-out/address-information-audit.json) claims the held-out sentence behind every
    partial cue is exactly reconstructible; that figure is attributed, never adopted. This function
    REPRODUCES it independently, on every keep_ALL item (not a 400-item subsample), and ALSO proves
    the encoder identity H^T p_a == mat[a] bit-exact, which the prior fragment did not check."""
    L_words, keep = C["L_words"], C["keep"]
    n = len(L_words)
    assert len(items) == n, "rebuilt items count (%d) != cached L_words count (%d)" % (len(items), n)
    n_L_mismatch = 0
    n_sentidx_none_but_kept = 0
    max_abs_err = 0.0
    n_checked = 0
    for i, it in enumerate(items):
        if it["L"] != L_words[i]:
            n_L_mismatch += 1
            continue
        if not keep[i]:
            continue
        if it["sent_idx"] is None:
            n_sentidx_none_but_kept += 1
            continue
        cnt = raw_counts_for_window(sents[it["sent_idx"]], it["L"])
        recon = reconstruct_bipolar(cnt).astype(np.float32)
        err = float(np.max(np.abs(recon - C["Q_part"][i]))) if cnt else float(
            np.max(np.abs(C["Q_part"][i])))
        max_abs_err = max(max_abs_err, err)
        n_checked += 1
    all_exact = (n_L_mismatch == 0 and n_sentidx_none_but_kept == 0 and max_abs_err == 0.0
                and n_checked > 0)
    return {"n_items_total": n, "n_checked_full_pop": n_checked, "n_L_mismatch": n_L_mismatch,
            "n_sentidx_none_but_cache_kept_true": n_sentidx_none_but_kept,
            "max_abs_error": max_abs_err, "ALL_EXACT": bool(all_exact),
            "method": "C3.build_items() over a read-only shim serving the CACHED anchor matrix, "
                      "checked against EVERY item the cache marks kept -- not a subsample."}


# =================================================================================================
# per-unit (checkpointed) raw-count builds -- the only genuinely expensive loops in this cell
# =================================================================================================
def build_store_counts(anchor_subset: Sequence[str], buckets: Dict[str, List[int]],
                       sents: List[str], out_dir: str) -> Tuple[Dict[str, Counter], Dict]:
    done = load_units(out_dir)
    P: Dict[str, Counter] = {}
    n_built = n_reused = 0
    t0 = time.time()
    for k, a in enumerate(anchor_subset):
        key = unit_key("Pstore", a)
        rec = done.get(key)
        if rec is not None:
            P[a] = Counter(rec["counts"])
            n_reused += 1
        else:
            occ = buckets.get(a, [])
            prof = occ[:C3._n_profile(len(occ))]
            c: Counter = Counter()
            for i in prof:
                c.update(raw_counts_for_window(sents[i], a))
            P[a] = c
            record_unit(out_dir, key, {"counts": dict(c), "n_sentences": len(prof)})
            n_built += 1
        if (k + 1) % 1000 == 0 or k == len(anchor_subset) - 1:
            print("[Pstore] %d/%d anchors built=%d reused=%d elapsed=%.0fs" % (
                k + 1, len(anchor_subset), n_built, n_reused, time.time() - t0), flush=True)
    return P, {"n_built": n_built, "n_reused": n_reused, "elapsed_s": round(time.time() - t0, 1)}


def build_context_cue_counts(item_ids: Sequence[str], L_of: Dict[str, str],
                             sentidx_of: Dict[str, int], sents: List[str],
                             out_dir: str) -> Tuple[Dict[str, Counter], Dict]:
    done = load_units(out_dir)
    Q: Dict[str, Counter] = {}
    n_built = n_reused = 0
    t0 = time.time()
    for k, iid in enumerate(item_ids):
        key = unit_key("Qcue_context", iid)
        rec = done.get(key)
        if rec is not None:
            Q[iid] = Counter(rec["counts"])
            n_reused += 1
        else:
            c = raw_counts_for_window(sents[sentidx_of[iid]], L_of[iid])
            Q[iid] = c
            record_unit(out_dir, key, {"counts": dict(c)})
            n_built += 1
        if (k + 1) % 500 == 0 or k == len(item_ids) - 1:
            print("[Qcue_context] %d/%d items built=%d reused=%d elapsed=%.0fs" % (
                k + 1, len(item_ids), n_built, n_reused, time.time() - t0), flush=True)
    return Q, {"n_built": n_built, "n_reused": n_reused, "elapsed_s": round(time.time() - t0, 1)}


def synonym_cue_words(L: str) -> List[str]:
    """'same-meaning neighbours', the owner's second description of a partial cue. Built from the
    SAME WordNet relation that builds the scoring gold set -- flagged INADMISSIBLE_CIRCULAR for the
    hit@1-vs-gold read of THIS cue kind only; the addressing-accuracy read never sees the gold set
    and is not circular."""
    out = []
    for w in sorted(C3.gold_meaning_set(L)):
        if not w.isalpha() or len(w) <= 2 or w in out:
            continue
        if C3._is_variant(w, L):
            continue
        out.append(w)
    return out


def build_synonym_and_onset_cues(item_ids: Sequence[str], L_of: Dict[str, str]
                                 ) -> Tuple[Dict[str, Counter], Dict[str, Counter]]:
    """Cheap (word list per item, no corpus access) -- NOT checkpointed; see the module docstring's
    checkpointing note for why a sub-millisecond-per-item construction is exempt."""
    Qsyn: Dict[str, Counter] = {}
    Qons: Dict[str, Counter] = {}
    for iid in item_ids:
        L = L_of[iid]
        syns = synonym_cue_words(L)
        if syns:
            Qsyn[iid] = Counter(syns)
        Qons[iid] = Counter({L[:min(ONSET_LEN, len(L))]: 1})
    return Qsyn, Qons


# =================================================================================================
# sparse machinery
# =================================================================================================
def build_vocab(counter_groups: Sequence[Dict[str, Counter]]) -> Dict[str, int]:
    vocab: Dict[str, int] = {}
    for group in counter_groups:
        for cnt in group.values():
            for w in cnt:
                if w not in vocab:
                    vocab[w] = len(vocab)
    return vocab


def to_sparse(counts_by_key: Dict[str, Counter], key_order: Sequence[str],
             vocab: Dict[str, int]) -> sp.csr_matrix:
    rows: List[int] = []
    cols: List[int] = []
    data: List[float] = []
    for r, k in enumerate(key_order):
        for w, c in counts_by_key.get(k, {}).items():
            rows.append(r)
            cols.append(vocab[w])
            data.append(float(c))
    return sp.csr_matrix((data, (rows, cols)), shape=(len(key_order), len(vocab)), dtype=np.float32)


def l2n_sparse(M: sp.csr_matrix) -> sp.csr_matrix:
    norms = np.sqrt(np.asarray(M.multiply(M).sum(axis=1)).ravel())
    norms[norms < 1e-12] = 1.0
    return sp.diags(1.0 / norms) @ M


def constant_prototype_floor_sparse(Mn: sp.csr_matrix) -> np.ndarray:
    """Sparse analogue of tools.floor_battery.constant_prototype_floor -- cosine to the mean of the
    L2-NORMALISED rows (the dense floor uses the mean of the RAW rows; disclosed, both are valid
    zero-query-information constant floors and this is the sparse-tractable one)."""
    mean_dir = np.asarray(Mn.mean(axis=0)).ravel()
    nrm = float(np.linalg.norm(mean_dir))
    if nrm > 1e-12:
        mean_dir = mean_dir / nrm
    return np.asarray((Mn @ mean_dir)).ravel().astype(np.float32)


# =================================================================================================
# scoring
# =================================================================================================
def addressing_hits(S: np.ndarray, valid_mask: np.ndarray, target_idx: np.ndarray) -> np.ndarray:
    Sm = np.where(valid_mask[:, None], S, -np.inf)
    amax = np.argmax(Sm, axis=0)
    return (amax == target_idx).astype(np.float64)


def score_addressing(name: str, hits: Dict[str, np.ndarray], chance: float) -> Dict:
    n = next(iter(hits.values())).shape[0]
    mask = np.ones(n, dtype=bool)
    boot = paired_bootstrap_ci(hits, mask, N_BOOT, MASTER_SEED + 707)
    acc = {k: round(v, 4) for k, v in boot["acc"].items()}
    out: Dict = {"n_items": int(mask.sum()), "chance_1_over_n_anchors_eligible": round(chance, 6),
                "addressing_accuracy_tie_free_argmax": acc, "arm_digests": {
                    k: _digest(v) for k, v in hits.items()}}
    out["MARGIN_vs_chance"] = {k: {"point": round(acc[k] - chance, 4)} for k in hits}
    pairs = [("U0_UNCOMPRESSED", "C0_PROJECTED_256"), ("U0_UNCOMPRESSED", "N1_RANDOM_KEY_U0"),
             ("C0_PROJECTED_256", "N1_RANDOM_KEY_C0"), ("U0_UNCOMPRESSED", "K1_EXACT_KEY_U0"),
             ("C0_PROJECTED_256", "K1_EXACT_KEY_C0")]
    dm = {}
    for a, b in pairs:
        if a in hits and b in hits:
            dm["%s_vs_%s" % (a, b)] = margin(boot["boot"], a, b)
    out["DECISIVE_MARGINS"] = dm
    print("[addr:%s] n=%d chance=%.6f " % (name, mask.sum(), chance)
          + " ".join("%s=%.4f" % (k[:26], v) for k, v in acc.items()), flush=True)
    return out


def score_hit1(name: str, arms: Dict[str, np.ndarray], E: np.ndarray, GOLD: np.ndarray,
              chance: float, floors: Sequence[str]) -> Dict:
    per: Dict[str, Dict] = {}
    common = None
    for k, S in arms.items():
        h = hit_at_1_both_tie_conventions(S, E, GOLD)
        per[k] = h
        common = h["scored"].copy() if common is None else (common & h["scored"])
    nc = int(common.sum()) if common is not None else 0
    if nc < 30:
        return {"n_common_scored": nc, "VOID": "fewer than 30 commonly scored items"}
    hits_exp = {k: per[k]["hit_exp"] for k in arms}
    hits_opt = {k: per[k]["hit_opt"] for k in arms}
    hits_cons = {k: per[k]["hit_cons"] for k in arms}
    boot = paired_bootstrap_ci(hits_exp, common, N_BOOT, MASTER_SEED + 909)
    acc = {k: round(v, 4) for k, v in boot["acc"].items()}
    acc_opt = {k: round(float(np.asarray(v)[common].mean()), 4) for k, v in hits_opt.items()}
    acc_cons = {k: round(float(np.asarray(v)[common].mean()), 4) for k, v in hits_cons.items()}
    present = [f for f in floors if f in arms]
    binding = max(present, key=lambda f: acc[f]) if present else None
    out = {"n_common_scored": nc, "chance_for_this_pool": round(float(chance), 6),
          "hit_at_1_TIE_CORRECTED": acc, "hit_at_1_OPTIMISTIC": acc_opt,
          "hit_at_1_CONSERVATIVE": acc_cons, "BINDING_FLOOR": binding,
          "MARGIN_vs_binding_floor_TIE_CORRECTED": (
              {k: margin(boot["boot"], k, binding) for k in arms if k != binding}
              if binding else {})}
    print("[hit1:%s] n=%d chance=%.5f binding=%s " % (name, nc, chance, binding)
          + " ".join("%s=%.4f" % (k[:22], v) for k, v in acc.items()), flush=True)
    return out


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {}
    rng = np.random.default_rng(3)

    # T0 -- floor_battery's own self-test, the shared ruler.
    from tools import floor_battery
    res["floor_battery_selftest_keys"] = sorted(floor_battery.self_test().keys())

    # T1 -- symbol_vector is deterministic and matches an INDEPENDENT reimplementation of
    # context_vector's own inline per-word draw formula, on several words.
    for w in ("apple", "the-quick", "banana123", "a"):
        v1 = symbol_vector(w, 32)
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v2 = np.random.default_rng(seed).choice([-1.0, 1.0], size=32)
        assert np.array_equal(v1, v2), "symbol_vector diverges from the inline formula: %r" % w
        assert np.array_equal(symbol_vector(w, 32), v1), "symbol_vector is not deterministic"
    res["T1_symbol_vector_matches_inline_formula"] = True

    # T2 -- THE ENCODER IDENTITY, bit-exact, on synthetic sentences with repeats, stopwords,
    # punctuation and a target word that occurs multiple times (so masking removes >1 token).
    from hdlab.reading_grounding_loop import context_vector_masked as _cvm
    cases = [
        ("The quick brown fox jumps over the lazy dog and the dog barks", "dog"),
        ("Apple apple apple banana cherry", "banana"),
        ("Nothing but stopwords the a is of", "cat"),
        ("Trailing punctuation, does it matter? Yes! Really.", "matter"),
    ]
    max_err = 0.0
    for sent, target in cases:
        cnt = raw_counts_for_window(sent, target)
        recon = reconstruct_bipolar(cnt, 256).astype(np.float32)
        ref = _cvm(sent, target, d=256, graded=True).astype(np.float32)
        err = float(np.max(np.abs(recon - ref))) if (cnt or np.any(ref)) else 0.0
        max_err = max(max_err, err)
    assert max_err == 0.0, "encoder identity H^T p == context_vector_masked FAILED: max_err=%g" \
                           % max_err
    res["T2_encoder_identity_bit_exact"] = {"max_abs_error": max_err, "n_cases": len(cases)}

    # T3 -- the double-filter inside context_vector_masked is idempotent on already-filtered words
    # (this is WHY counting `words` directly, rather than re-tokenising " ".join(words), is valid).
    words = [w for w in content_words("The Dog runs Fast through tall Grass") if w != "dog"]
    refiltered = content_words(" ".join(words))
    assert words == refiltered, "double-filter is not idempotent: %r vs %r" % (words, refiltered)
    res["T3_double_filter_idempotent"] = True

    # T4 -- the sparse cosine pipeline (to_sparse + l2n_sparse + matmul) matches brute-force dense
    # cosine on a small synthetic vocabulary with partial overlap and one empty row.
    P = {"a1": Counter({"x": 2, "y": 1}), "a2": Counter({"y": 3, "z": 1}), "a3": Counter()}
    Q = {"i1": Counter({"x": 1, "y": 1}), "i2": Counter({"z": 5})}
    vocab = build_vocab([P, Q])
    Pm = l2n_sparse(to_sparse(P, ["a1", "a2", "a3"], vocab))
    Qm = l2n_sparse(to_sparse(Q, ["i1", "i2"], vocab))
    S = np.asarray((Pm @ Qm.T).todense(), dtype=np.float64)

    def dense_cos(a: Counter, b: Counter) -> float:
        keys = set(a) | set(b)
        va = np.array([a.get(k, 0) for k in keys], dtype=np.float64)
        vb = np.array([b.get(k, 0) for k in keys], dtype=np.float64)
        na, nb = np.linalg.norm(va), np.linalg.norm(vb)
        if na < 1e-12 or nb < 1e-12:
            return 0.0
        return float(va @ vb / (na * nb))
    ref = np.array([[dense_cos(P[a], Q[i]) for i in ("i1", "i2")] for a in ("a1", "a2", "a3")])
    assert np.allclose(S, ref, atol=1e-6), "sparse cosine pipeline diverges from brute force:\n%r\nvs\n%r" \
                                          % (S, ref)
    res["T4_sparse_cosine_matches_dense_bruteforce"] = True

    # T5 -- addressing accuracy: a cue that IS an anchor's own vector must address ITSELF (1.0),
    # and a permuted (misassigned) cue must fall to (near) chance.
    n_a = 60
    M = rng.standard_normal((n_a, 20)).astype(np.float32)
    Mn = l2n(M)
    valid = np.ones(n_a, dtype=bool)
    target = np.arange(n_a)
    S_self = Mn @ Mn.T
    h_self = addressing_hits(S_self, valid, target)
    assert h_self.mean() == 1.0, "self-cue addressing accuracy is not 1.0: %.4f" % h_self.mean()
    perm = rng.permutation(n_a)
    while np.any(perm == np.arange(n_a)):
        perm = rng.permutation(n_a)
    S_perm = S_self[:, perm]
    h_perm = addressing_hits(S_perm, valid, target)
    assert h_perm.mean() < 0.15, "permuted-cue addressing accuracy is not near chance: %.4f" \
                                 % h_perm.mean()
    res["T5_addressing_accuracy"] = {"self": float(h_self.mean()), "permuted": float(h_perm.mean())}

    # T6 -- score_addressing end-to-end: a planted arm reaches 1.0, a scrambled one sits at chance,
    # and the DECISIVE_MARGINS block resolves ABOVE for a genuinely better arm.
    hits = {"U0_UNCOMPRESSED": h_self.copy(), "C0_PROJECTED_256": h_perm.copy(),
           "K1_EXACT_KEY_U0": h_self.copy(), "N1_RANDOM_KEY_U0": h_perm.copy(),
           "K1_EXACT_KEY_C0": h_self.copy(), "N1_RANDOM_KEY_C0": h_perm.copy()}
    r6 = score_addressing("T6", hits, 1.0 / n_a)
    assert r6["DECISIVE_MARGINS"]["U0_UNCOMPRESSED_vs_C0_PROJECTED_256"]["band"] == "ABOVE"
    res["T6_score_addressing_end_to_end"] = True

    # T7 -- score_hit1 end-to-end: planted KA reaches ceiling, permuted NULL sits at chance, a
    # constant-prototype-shaped floor wins where it is the strongest member.
    n_i = 500
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    proto = np.linspace(1, 0, n_a).astype(np.float32)
    p = proto ** 6
    p = p / p.sum()
    g = rng.choice(n_a, size=n_i, p=p)
    GOLD[g, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    Splant = np.zeros((n_a, n_i), dtype=np.float32)
    Splant[g, np.arange(n_i)] = 1.0
    from tools.floor_battery import as_constant_matrix
    arms7 = {"U0_UNCOMPRESSED": rng.standard_normal((n_a, n_i)).astype(np.float32),
            "F4_CONSTANT_PROTOTYPE_U0": as_constant_matrix(proto, n_i),
            "K1_EXACT_KEY_U0": Splant, "N1_RANDOM_KEY_U0": rng.standard_normal(
                (n_a, n_i)).astype(np.float32)}
    r7 = score_hit1("T7", arms7, E, GOLD, 1.0 / n_a, ["F4_CONSTANT_PROTOTYPE_U0"])
    assert r7["hit_at_1_TIE_CORRECTED"]["K1_EXACT_KEY_U0"] >= 0.99
    assert r7["hit_at_1_TIE_CORRECTED"]["N1_RANDOM_KEY_U0"] < 0.05
    assert r7["BINDING_FLOOR"] == "F4_CONSTANT_PROTOTYPE_U0"
    res["T7_score_hit1_end_to_end"] = True

    # T8 -- the ruler-mode gate is CALLED, and '--smoke' is never in argv (this cell's flag is
    # --grid full|reduced for exactly the reason exp_task_degeneracy_v1:121 documents).
    g8 = DEG.ruler_mode_gate()
    assert g8.get("PASS") is True, g8
    assert "--smoke" not in sys.argv, sys.argv
    res["T8_ruler_mode_gate"] = g8

    # T9 -- constant_prototype_floor_sparse agrees with the dense floor when the sparse matrix IS
    # (a one-hot embedding of) a dense matrix -- proves the sparse analogue is the same computation.
    Mdense = np.abs(rng.standard_normal((40, 40)).astype(np.float32)) + 0.1
    f_dense = constant_prototype_floor(Mdense, normalize_rows_first=True)
    Msp = sp.csr_matrix(Mdense)
    f_sparse = constant_prototype_floor_sparse(l2n_sparse(Msp))
    assert np.allclose(f_dense, f_sparse, atol=1e-4), "sparse constant floor diverges from dense"
    res["T9_constant_floor_sparse_matches_dense"] = True

    print("[selftest] PASS " + json.dumps(res, default=str)[:1800], flush=True)
    return res


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir = _out_dir(grid)
    os.makedirs(out_dir, exist_ok=True)
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "out_dir": out_dir,
                "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                "RULER_MODE_GATE": DEG.ruler_mode_gate(), "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "progress_logging": True}

    # ---- harness cache (UNMODIFIED, shared with the sibling cells) ---------------------------
    cache_prov = DEG.build_cache_if_missing()
    C = DEG.load_cache()
    rep["cache_provenance"] = cache_prov
    anchors, mat, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    qidx_global = np.array([C["pos"].get(w, -1) for w in C["L_words"]], dtype=np.int64)
    print("[load] n_anchors=%d n_items=%d %.0fs" % (n_anchors, n_items_all, time.time() - t0),
         flush=True)

    # ---- gold + eligibility (byte-identical construction to exp_task_degeneracy_v1) ----------
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

    # ---- REGRESSION GATE: this cell's C0 arm must reproduce the landed number ------------------
    S_full = (l2n(mat) @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = hit_at_1_both_tie_conventions(S_full, E_ALL, GOLD_ALL)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    rep["REGRESSION_GATE"] = {
        "what": "C0_PROJECTED_256 on the FULL landed open pool must reproduce the landed A0 number.",
        "measured": round(a0_full, 4), "expected": REGRESSION_A0_PARTIAL, "tol": REGRESSION_TOL,
        "PASS": bool(abs(a0_full - REGRESSION_A0_PARTIAL) <= REGRESSION_TOL),
        "n_scored": int(m_full.sum())}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r"
                         % rep["REGRESSION_GATE"])
    print("[regression] C0_PROJECTED_256_FULL=%.4f (expected %.4f) PASS" % (
        a0_full, REGRESSION_A0_PARTIAL), flush=True)
    del S_full, h_full

    # ---- THE BLOCKING SUB-QUESTION: recoverability, checked here, never imported ---------------
    sents, buckets, counts, corpus_prov = load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    shim = _ShimSpace(anchors, C["pos"], mat)
    items, item_diag = C3.build_items(shim, buckets, counts, C3.MAX_ITEMS)
    recov = verify_recoverability(items, C, sents)
    rep["RECOVERABILITY_GATE"] = recov
    print("[recoverability] checked=%d L_mismatch=%d sentidx_missing=%d max_abs_err=%.3e "
         "ALL_EXACT=%s" % (recov["n_checked_full_pop"], recov["n_L_mismatch"],
                           recov["n_sentidx_none_but_cache_kept_true"], recov["max_abs_error"],
                           recov["ALL_EXACT"]), flush=True)
    if not recov["ALL_EXACT"]:
        rep["STOP_IF_FIRED"] = ("RECOVERABILITY_DID_NOT_REPRODUCE -- the held-out sentence behind "
                                "the partial cue could not be exactly reconstructed this run. The "
                                "U0_UNCOMPRESSED arm and the cue-kind split CANNOT be built (they "
                                "require the raw token stream). Reduced design: report REGRESSION "
                                "and RECOVERABILITY only. This is disclosed, not papered over.")
        rep["elapsed_s"] = round(time.time() - t0, 1)
        return rep

    L_of = {it["item_id"]: it["L"] for it in items}
    sentidx_of = {it["item_id"]: it["sent_idx"] for it in items}
    item_id_of_idx = [it["item_id"] for it in items]      # index-aligned with L_words/keep_ALL

    # ---- choose the working item/anchor pools per grid -----------------------------------------
    eligible_item_idx = np.flatnonzero(keep_ALL)
    if grid == "full":
        item_idx = eligible_item_idx
        anchor_ids = list(anchors)
    else:
        item_idx = eligible_item_idx[:N_SMOKE_ITEMS]
        own = sorted({L_of[item_id_of_idx[i]] for i in item_idx})
        rng = np.random.default_rng(MASTER_SEED + 1)
        pad_pool = [a for a in anchors if a not in set(own)]
        pad = rng.choice(pad_pool, size=max(0, ANCHOR_POOL_SMOKE - len(own)), replace=False).tolist()
        anchor_ids = sorted(set(own) | set(pad))
    n_items_w = int(item_idx.size)
    n_anchors_w = len(anchor_ids)
    rep["POOL"] = {"grid": grid, "n_items_working": n_items_w, "n_anchors_working": n_anchors_w,
                   "n_items_eligible_full_pop": int(eligible_item_idx.size),
                   "n_anchors_full_pop": n_anchors}
    print("[pool] grid=%s n_items=%d n_anchors=%d" % (grid, n_items_w, n_anchors_w), flush=True)

    anchor_pos_global = C["pos"]
    anchor_global_idx = np.array([anchor_pos_global[a] for a in anchor_ids], dtype=np.int64)
    mat_w = mat[anchor_global_idx]
    mat_ok_w = mat_ok[anchor_global_idx]
    E_w = E_ALL[anchor_global_idx][:, item_idx]
    GOLD_w = GOLD_ALL[anchor_global_idx][:, item_idx]
    local_pos = {a: i for i, a in enumerate(anchor_ids)}
    item_ids_w = [item_id_of_idx[i] for i in item_idx]
    L_w = [L_of[iid] for iid in item_ids_w]
    qidx_w = np.array([local_pos[L] for L in L_w], dtype=np.int64)
    Qpart_w = C["Q_part"][item_idx]

    # ---- aux (orthographic + frequency floors), reused unmodified from the sibling cell --------
    aux = DEG.load_aux(C)
    rep["aux_source"] = aux.get("source", "?")

    # ---- build P_a for the working anchor pool (checkpointed) ----------------------------------
    P, p_diag = build_store_counts(anchor_ids, buckets, sents, out_dir)
    rep["STORE_COUNTS_BUILD"] = p_diag

    # ---- build the three cue kinds for the working item pool ------------------------------------
    Qctx, qctx_diag = build_context_cue_counts(item_ids_w, L_of, sentidx_of, sents, out_dir)
    rep["CONTEXT_CUE_BUILD"] = qctx_diag
    Qsyn, Qons = build_synonym_and_onset_cues(item_ids_w, L_of)
    rep["CUE_KIND_COVERAGE"] = {
        "context_sentence": len(Qctx), "synonym_set_nonempty": len(Qsyn),
        "word_onset": len(Qons), "n_items_working": n_items_w}

    # ---- shared vocabulary + sparse matrices ----------------------------------------------------
    vocab = build_vocab([P, Qctx, Qsyn, Qons])
    rep["VOCAB"] = {"n_distinct_content_words": len(vocab)}
    Pm = l2n_sparse(to_sparse(P, anchor_ids, vocab))
    Qctx_m = l2n_sparse(to_sparse(Qctx, item_ids_w, vocab))
    Qsyn_m = l2n_sparse(to_sparse(Qsyn, item_ids_w, vocab))
    Qons_m = l2n_sparse(to_sparse(Qons, item_ids_w, vocab))

    # ---- SELF-TEST OF THE IDENTITY ON THE REAL DATA: H^T P_a == mat_w[a] for EVERY working anchor
    max_store_err = 0.0
    for a in anchor_ids:
        recon = reconstruct_bipolar(P[a]).astype(np.float32)
        idx = local_pos[a]
        err = float(np.max(np.abs(recon - mat_w[idx]))) if (P[a] or np.any(mat_w[idx])) else 0.0
        max_store_err = max(max_store_err, err)
    rep["ENCODER_IDENTITY_STORE_SIDE"] = {
        "n_anchors_checked": n_anchors_w, "max_abs_error_H_T_Pa_vs_mat": max_store_err,
        "BIT_EXACT": bool(max_store_err == 0.0)}
    print("[identity] H^T P_a vs mat_w: max_abs_error=%.3e over %d anchors BIT_EXACT=%s" % (
        max_store_err, n_anchors_w, max_store_err == 0.0), flush=True)
    if max_store_err != 0.0:
        rep["STOP_IF_FIRED"] = ("ENCODER_IDENTITY_FAILED_ON_REAL_DATA -- H^T P_a != mat[a] for at "
                                "least one working anchor (max_abs_error=%.3e). The U0 arm is NOT "
                                "trustworthy; publishing no quality number." % max_store_err)
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        return rep

    # ---- C0_PROJECTED_256 (context-sentence cue) ------------------------------------------------
    S_C0 = (l2n(mat_w) @ l2n(Qpart_w).T).astype(np.float32)
    S_U0 = np.asarray((Pm @ Qctx_m.T).todense(), dtype=np.float32)

    # ---- K1_EXACT_KEY (regime-only, not cue-kind-specific: query = the item's own store row) ----
    S_K1_C0 = (l2n(mat_w) @ l2n(mat_w[qidx_w]).T).astype(np.float32)
    S_K1_U0 = np.asarray((Pm @ Pm[qidx_w].T).todense(), dtype=np.float32)

    # ---- N1_RANDOM_KEY: the REAL cue reassigned to a DIFFERENT item (size-matched, permuted) ----
    rng_n1 = np.random.default_rng(MASTER_SEED + 501)
    perm = rng_n1.permutation(n_items_w)
    tries = 0
    while np.any(perm == np.arange(n_items_w)) and tries < 50:
        perm = rng_n1.permutation(n_items_w)
        tries += 1
    S_N1_C0 = S_C0[:, perm]
    S_N1_U0 = S_U0[:, perm]

    # ================================ PRIMARY: ADDRESSING ACCURACY ==============================
    target = qidx_w
    hits = {
        "C0_PROJECTED_256": addressing_hits(S_C0, mat_ok_w, target),
        "U0_UNCOMPRESSED": addressing_hits(S_U0, mat_ok_w, target),
        "K1_EXACT_KEY_C0": addressing_hits(S_K1_C0, mat_ok_w, target),
        "K1_EXACT_KEY_U0": addressing_hits(S_K1_U0, mat_ok_w, target),
        "N1_RANDOM_KEY_C0": addressing_hits(S_N1_C0, mat_ok_w, target),
        "N1_RANDOM_KEY_U0": addressing_hits(S_N1_U0, mat_ok_w, target),
    }
    chance_addr = 1.0 / max(int(mat_ok_w.sum()), 1)
    addr_report = score_addressing("CONTEXT_SENTENCE", hits, chance_addr)
    rep["ADDRESSING_ACCURACY_PRIMARY"] = {"CONTEXT_SENTENCE": addr_report}
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = {k: _digest(v) for k, v in hits.items()}
    assert len(set(rep["ARM_DIGESTS_ARMS_MUST_DIFFER"].values())) > 1, \
        "all addressing arms produced IDENTICAL hit vectors -- a construction bug, not a result"

    # ================================ SECONDARY: hit@1 vs WordNet gold ==========================
    # aux["t_mat"] / aux["Pq"] are built over the FULL anchor list (exp_task_degeneracy_v1.load_aux
    # indexes them by C["anchors"] order) -- must be sliced to anchor_global_idx for the working
    # (possibly smoke-restricted) anchor pool, or their shape silently disagrees with E_w/GOLD_w.
    S_trig = (aux["t_mat"][anchor_global_idx] @ aux["Tq"][item_idx].T).astype(np.float32)
    S_pref = aux["Pq"][item_idx][:, anchor_global_idx].T.astype(np.float32)
    S_freq_col = frequency_floor(np.expm1(aux["fq"][anchor_global_idx].astype(np.float64)))
    S_freq = np.repeat(S_freq_col[:, None], n_items_w, axis=1).astype(np.float32)
    F4_C0 = constant_prototype_floor(mat_w, mat_ok_w)
    F4_C0_mat = np.repeat(F4_C0[:, None], n_items_w, axis=1).astype(np.float32)
    F4_U0 = constant_prototype_floor_sparse(Pm)
    F4_U0_mat = np.repeat(F4_U0[:, None], n_items_w, axis=1).astype(np.float32)
    S_scramble_C0 = (l2n(scramble_null(mat_w, MASTER_SEED)) @ l2n(Qpart_w).T).astype(np.float32)
    perm_sc = np.random.default_rng(MASTER_SEED + 2).permutation(n_anchors_w)
    S_scramble_U0 = np.asarray(((Pm[perm_sc]) @ Qctx_m.T).todense(), dtype=np.float32)

    floors_shared = {"F1_TRIGRAM_ONLY": S_trig, "F2_PREFIX_ONLY": S_pref, "F3_FREQUENCY": S_freq}
    chance_hit1 = float(np.mean(GOLD_w[:, np.arange(n_items_w)].sum(axis=0)
                               / np.maximum(E_w.sum(axis=0), 1)))
    arms_C0 = dict(floors_shared)
    arms_C0.update({"C0_PROJECTED_256": S_C0, "F4_CONSTANT_PROTOTYPE_C0": F4_C0_mat,
                    "F5_SCRAMBLE_C0": S_scramble_C0, "K1_EXACT_KEY_C0": S_K1_C0,
                    "N1_RANDOM_KEY_C0": S_N1_C0})
    arms_U0 = dict(floors_shared)
    arms_U0.update({"U0_UNCOMPRESSED": S_U0, "F4_CONSTANT_PROTOTYPE_U0": F4_U0_mat,
                    "F5_SCRAMBLE_U0": S_scramble_U0, "K1_EXACT_KEY_U0": S_K1_U0,
                    "N1_RANDOM_KEY_U0": S_N1_U0})
    FLOORS_C0 = ("F1_TRIGRAM_ONLY", "F2_PREFIX_ONLY", "F3_FREQUENCY", "F4_CONSTANT_PROTOTYPE_C0")
    FLOORS_U0 = ("F1_TRIGRAM_ONLY", "F2_PREFIX_ONLY", "F3_FREQUENCY", "F4_CONSTANT_PROTOTYPE_U0")
    rep["HIT_AT_1_SECONDARY"] = {
        "chance_for_this_pool": round(chance_hit1, 6),
        "C0_PROJECTED_256_regime": score_hit1("C0_regime", arms_C0, E_w, GOLD_w, chance_hit1,
                                              FLOORS_C0),
        "U0_UNCOMPRESSED_regime": score_hit1("U0_regime", arms_U0, E_w, GOLD_w, chance_hit1,
                                             FLOORS_U0),
        "note": "K1_EXACT_KEY's hit@1-vs-WordNet-gold number here is NOT a validity gate (the "
                "item's own index is excluded from its eligible pool by construction -- see "
                "excl arrays), unlike its addressing-accuracy reading above which IS the gate. "
                "Reported for transparency only."}

    # ================================ CUE-KIND SPLIT (secondary) =================================
    S_C0_syn = (l2n(mat_w) @ l2n(np.stack(
        [reconstruct_bipolar(Qsyn.get(iid, Counter())) for iid in item_ids_w]).astype(
            np.float32)).T).astype(np.float32)
    S_U0_syn = np.asarray((Pm @ Qsyn_m.T).todense(), dtype=np.float32)
    S_C0_ons = (l2n(mat_w) @ l2n(np.stack(
        [reconstruct_bipolar(Qons[iid]) for iid in item_ids_w]).astype(np.float32)).T).astype(
            np.float32)
    S_U0_ons = np.asarray((Pm @ Qons_m.T).todense(), dtype=np.float32)

    n1_perm2 = perm     # reuse the same permutation across cue kinds for comparability
    hits_syn = {"C0_PROJECTED_256": addressing_hits(S_C0_syn, mat_ok_w, target),
               "U0_UNCOMPRESSED": addressing_hits(S_U0_syn, mat_ok_w, target),
               "K1_EXACT_KEY_C0": hits["K1_EXACT_KEY_C0"], "K1_EXACT_KEY_U0": hits["K1_EXACT_KEY_U0"],
               "N1_RANDOM_KEY_C0": addressing_hits(S_C0_syn[:, n1_perm2], mat_ok_w, target),
               "N1_RANDOM_KEY_U0": addressing_hits(S_U0_syn[:, n1_perm2], mat_ok_w, target)}
    hits_ons = {"C0_PROJECTED_256": addressing_hits(S_C0_ons, mat_ok_w, target),
               "U0_UNCOMPRESSED": addressing_hits(S_U0_ons, mat_ok_w, target),
               "K1_EXACT_KEY_C0": hits["K1_EXACT_KEY_C0"], "K1_EXACT_KEY_U0": hits["K1_EXACT_KEY_U0"],
               "N1_RANDOM_KEY_C0": addressing_hits(S_C0_ons[:, n1_perm2], mat_ok_w, target),
               "N1_RANDOM_KEY_U0": addressing_hits(S_U0_ons[:, n1_perm2], mat_ok_w, target)}
    rep["ADDRESSING_ACCURACY_PRIMARY"]["SYNONYM_SET"] = score_addressing(
        "SYNONYM_SET", hits_syn, chance_addr)
    rep["ADDRESSING_ACCURACY_PRIMARY"]["WORD_ONSET"] = score_addressing(
        "WORD_ONSET", hits_ons, chance_addr)
    rep["CUE_KIND_SPLIT_NOTE"] = (
        "SYNONYM_SET's hit@1-vs-WordNet-gold read (not computed here, addressing-accuracy only) "
        "would be INADMISSIBLE_CIRCULAR: the cue is built from the SAME WordNet relation that "
        "builds the gold set. The addressing-accuracy read above is NOT circular -- the item's own "
        "identity is never in its synonym/onset cue -- and is the one reported.")

    # ================================ STOP-IF DECISION, pre-registered above =====================
    k1c0 = addr_report["addressing_accuracy_tie_free_argmax"]["K1_EXACT_KEY_C0"]
    k1u0 = addr_report["addressing_accuracy_tie_free_argmax"]["K1_EXACT_KEY_U0"]
    instrument_loose = not (k1c0 >= KA_CEILING_MIN and k1u0 >= KA_CEILING_MIN)
    decisive = addr_report["DECISIVE_MARGINS"].get("U0_UNCOMPRESSED_vs_C0_PROJECTED_256")
    if instrument_loose:
        verdict = "ii_INSTRUMENT_STILL_LOOSE"
        headline = ("K1_EXACT_KEY did not reach %.4f in one or both regimes (C0=%.4f, U0=%.4f). "
                   "NO QUALITY NUMBER PUBLISHED beyond the raw diagnostics above." % (
                       KA_CEILING_MIN, k1c0, k1u0))
    elif decisive is None:
        verdict = "UNDETERMINED_missing_decisive_margin"
        headline = "the U0 vs C0 paired margin could not be computed."
    elif decisive["band"] == "ABOVE":
        verdict = "iii_U0_BEATS_C0_compression_is_the_defect"
        headline = ("U0_UNCOMPRESSED CI-separated ABOVE C0_PROJECTED_256 (%r): the 256-dim random "
                   "projection is destroying recoverable information. The sibling item's address "
                   "build becomes an EXPANSION question with this measured target." % decisive)
    elif decisive["band"] in ("NOT_SEPARATED", "BELOW") and decisive["point"] <= 0:
        verdict = "i_INFORMATION_NOT_IN_THE_CUE"
        headline = ("U0_UNCOMPRESSED does NOT beat C0_PROJECTED_256 (%r): removing the projection "
                   "buys nothing. THE INFORMATION IS NOT IN THE PARTIAL CUE. The address-side build "
                   "is VOID AS A CAPABILITY CLAIM; the blocker relocates to WHAT WE WRITE. This is "
                   "reported LOUDLY as the most valuable outcome available, not as a defeat." %
                   decisive)
    else:
        verdict = "UNCLASSIFIED"
        headline = "margin band %r did not match any pre-registered stop-if; reported as-is." % decisive

    rep["STOP_IF_VERDICT"] = {"verdict": verdict, "headline": headline,
                              "K1_EXACT_KEY_C0": k1c0, "K1_EXACT_KEY_U0": k1u0,
                              "decisive_margin_U0_vs_C0": decisive}
    print("[VERDICT] %s :: %s" % (verdict, headline), flush=True)

    rep["elapsed_s"] = round(time.time() - t0, 1)
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("WROTE " + os.path.join(out_dir, "metrics.json"), flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    out_dir = _out_dir(a.grid)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        run(a.grid)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(out_dir, "_crash_diagnostic.json"),
                    {"error": "%s: %s" % (type(exc).__name__, exc),
                     "traceback": traceback.format_exc(),
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
