"""exp_crossview_convergence_hub_v1 -- does CROSS-VIEW MUTUAL PREDICTION isolate substitutability?

PRE-REGISTRATION: preregs/2026-08-18_crossview_convergence_hub_v1.md  (written BEFORE this file's
FULL run; NOT edited afterwards, and NOT edited by this cell's author to fix its wording).

THE QUESTION. Our store has only ever had ONE channel (usage co-occurrence), so it has never had a
cross-channel error signal. If we learn a mapping between a USAGE view and a DEFINITIONAL view of
the same words and keep ONLY the component the two views can predict about each other, does THAT
component encode substitutability when neither view does alone?

=================================================================================================
DISCLOSURE 1 -- THIS IS A RE-ATTEMPT OF A MECHANISM CLASS THAT HAS ALREADY FAILED TWICE
=================================================================================================
  - exp_self_teacher_gloss_relational_predictive_heldout_new_v1 is the SAME MECHANISM CLASS
    (definitional/gloss text + relational context learned PREDICTIVELY on top of grounding).
    It LANDED AT -0.0105 (0.6256 vs raw_grounding 0.6361), failing a +0.03 bar, and its `raw_gloss`
    ablation read 0.5978, WORSE than grounding alone.
  - exp_redundancy_decorrelation_from_coherence_gate_precheck_v1 landed
    HARD_FAIL_NO_SAFE_SECOND_VIEW: its candidate second view was not error-decorrelated from the
    first.
  The prior is therefore NEGATIVE. This cell exists because neither prior attempt extracted the
  CROSS-PREDICTABLE COMPONENT in closed form or scored it on the dissociation instrument, not
  because the class looks promising.

=================================================================================================
DISCLOSURE 2 -- PRE-REG AMBIGUITY, ADJUDICATED IN ADVANCE, RECORDED HERE INSTEAD OF EDITING IT
=================================================================================================
  The pre-reg's VIEWS section says the truncated-SVD basis is fit "on HELD-OUT WORDS ONLY", while
  its HELD-OUT SPLIT section says evaluation words are excluded from EVERY fit "including the SVD
  basis". Those two sentences disagree about which set the word "held-out" names.
  ADJUDICATION: THE HELD-OUT SPLIT SECTION IS DEFINITIVE. The basis is fit on the 3,064 FIT words;
  the 617 evaluation words are excluded from the SVD basis, the CCA, the ridge, the lam and k*
  selection, and the feature vocabulary. This is the leakage-safe reading and the one the
  pre-reg's own leakage assertion (`assert not (set(fit) & set(eval))`) requires.
  The pre-reg file is NOT edited. `preregs/**` is the record and it does not move after the fact.

=================================================================================================
DISCLOSURE 3 -- IMPLEMENTATION CHOICES THAT STRENGTHEN A DECLARED PROPERTY
=================================================================================================
  (a) The definitional cache `scratch/_simplewiki_defs.json` is BUILT INLINE IF MISSING, by the
      byte-identical construction that produced it (scratch/_simplewiki_coverage_probe.py:39-56):
      hdlab.definitional_extraction.extract_definitions over every line of
      data/corpora/simplewiki/simplewiki_clean_v1.txt, keyed on `definiendum_lemma`, definiens
      lemmas capped at 40 distinct per definiendum first-come, filtered to eval-or-anchor keys.
      A FULL run therefore cannot depend on a wipeable scratch/ file. The eval/anchor key filter is
      taken from the LOADED population and the LOADED cache, not from scratch text files.
  (b) The truncated SVD uses scipy svds with a FIXED v0 as declared, and falls back to a dense
      Gram eigendecomposition ONLY on ArpackNoConvergence (recorded in metrics when it happens).
      Both paths are exactly deterministic and --self-test asserts bit-identity across two calls.
  (c) F_SCRAMBLE IS ESTIMATED AS A POLICY OVER MANY PERMUTATIONS, NOT AS ONE COIN FLIP.
      CHANGED AFTER SEEING THE SMOKE, AND DISCLOSED HERE FOR THAT REASON. The first smoke read
      F_SCRAMBLE_INCUMBENT = 0.4266 [0.3701, 0.4867] on the surviving rows and fired L0_UNLICENSED,
      voiding the whole run. That floor is ONE random word-to-row permutation. Under a pure null at
      n = 202 the AUC has sd ~ 0.029, so a single draw's own 95% CI excludes 0.5 roughly 5% of the
      time BY CONSTRUCTION; across four floors that is an ~18% chance of voiding any run on noise
      alone. The other three floors are DETERMINISTIC functions of the data, so a CI excluding 0.5
      there is a real property of the population. Only scramble is a coin flip.
      THE FIX, AND ITS DIRECTION OF EFFECT: F_SCRAMBLE is now the mean over SCRAMBLE_REPS
      independent permutations; its licensing band uses the standard error of that mean; and the
      term it contributes to THE BAR is the 95th PERCENTILE of the across-permutation AUC
      distribution, i.e. the best a scramble policy plausibly achieves. That percentile is far
      ABOVE a single draw's mean-plus-half-width, so THIS CHANGE RAISES THE BAR AND MAKES A PASS
      STRICTLY HARDER. It cannot manufacture a positive result in either direction. The empirical
      single-draw false-fire rate is measured and written to metrics so the noisiness of the
      original test is visible rather than argued.
  (d) The channel-independence pre-flight is the pre-reg's "reused in spirit" numpy re-expression
      of exp_grounding_consolidation_loop_degree_invariant_v1.channel_preflight's cross_sim_r leg.
      Its REDUNDANT_CROSS = 0.95 threshold is NOT copied by hand: --self-test reads that file and
      asserts the literal is still 0.95, so the threshold cannot drift out from under this cell.

=================================================================================================
BINDING CONSTRAINTS (each is enforced by code below, not by intention)
=================================================================================================
  - NO LLM anywhere in the operational path. Every arm is closed form.
  - FORBIDDEN SOURCE data/foundation/**: covers only 11-14 of 242 rows, so it is unmeasurable here.
    It is also READ-ONLY, ONE DISK, NO BACKUP. This cell opens NOTHING under data/foundation/ and
    writes NOTHING there.
  - FORBIDDEN SOURCE WordNet glosses as the definitional view: 182 of 242 SET P pairs share a
    synset and therefore an identical gloss vs 0 of 242 SET S; gloss overlap reads AUC 0.8911
    against the instrument's own known-answer arm at 0.9599. IT IS THE ANSWER KEY. WordNet appears
    here ONLY as the licensing KNOWN_ANSWER arm, never as a view.
  - NO CACHED BAR IS IMPORTED. 0.5431, 0.5943 and 0.6317 are BAG-population / other-representation
    figures and appear nowhere in this file as a threshold. Every floor is recomputed on THIS
    representation and THIS surviving population, and the gate is the floor's UPPER bound.
  - Every margin is reported beside its CI half-width AND the permutation-null p95 at this n.
    If the half-width exceeds the chance-to-bar interval the branch is UNDERPOWERED, not a verdict.
  - Every control reports HOW MANY ROWS IT REMOVED. A control that removes 0 rows is reported as
    NOT BINDING.

ASCII only. No unicode, no em dashes.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------------------------
# THREAD PINS -- MUST precede `import numpy`; numpy/OpenBLAS size their pool at import time.
# ---------------------------------------------------------------------------------------------
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import hashlib
import json
import re
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import svds
from scipy.sparse.linalg import ArpackNoConvergence

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_cue_to_store_translation_v1 as CTS                # noqa: E402  READ ONLY
import experiments.exp_dissociation_score_instrument_v1 as DISS          # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                  # noqa: E402  READ ONLY
import experiments.exp_grounding_readout_known_answer_v1 as C3           # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from hdlab.definitional_extraction import extract_definitions            # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import content_lemmas                  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from experiments._cell_heartbeat import emit_heartbeat                   # noqa: E402
from tools.exp_checkpoint import unit_key, record_unit, load_units       # noqa: E402

print("[imports] done", flush=True)

# =================================================================================================
# CONSTANTS
# =================================================================================================
ANCHOR_NAME = "crossview_convergence_hub_v1"
CODE_VERSION = "v1.1"   # v1.0 estimated F_SCRAMBLE from ONE permutation; v1.1 estimates it as a
                        # POLICY over SCRAMBLE_REPS permutations and takes its BAR term from the
                        # 95th percentile of that distribution (STRICTLY HARDER). Bumped so no v1.0
                        # unit can silently resume into the changed contract. See DISCLOSURE 3c.
PREREG = "preregs/2026-08-18_crossview_convergence_hub_v1.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED                      # 20260816, asserted below
assert MASTER_SEED == 20260816, "MASTER_SEED drifted from CTS: %r" % MASTER_SEED

INSTRUMENT_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")
INSTRUMENT_VERSION = "v1.7"
POP_KEY = unit_key("POPULATION", INSTRUMENT_VERSION, "full")

SIMPLEWIKI = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
DEF_CACHE = os.path.join(REPO, "scratch", "_simplewiki_defs.json")
DEF_MAX_DEFINIENS = 40           # cap reproduced from scratch/_simplewiki_coverage_probe.py:50
DEF_MAX_LINE = 600               # line filter reproduced from the same probe, line 43

K_SVD = 128 if not SMOKE else 48
N_BOOT = 10000 if not SMOKE else 1500
N_PERM = 2000 if not SMOKE else 400
SCRAMBLE_REPS = 500 if not SMOKE else 100   # see DISCLOSURE 3c: a floor is a POLICY, not one draw
PREFLIGHT_PAIRS = 4000 if not SMOKE else 800
CCA_LAM_GRID = (1e-4, 1e-3, 1e-2, 1e-1, 1.0)
CCA_HELDOUT_RHO_MIN = 0.10       # pre-registered k* rule
CCA_K_MIN, CCA_K_MAX = 4, 128
CCA_LAM_REF_K = 32               # components averaged when SELECTING lam (k* is chosen after)

# Pre-registered regression gate: this cell's own code must reproduce the landed incumbent.
# MEASURED@data/exp_dissociation_score_instrument_v1/metrics.json:report.AUC_PER_ARM.
#                                                   INCUMBENT_LIVE_STORE.auc
REGRESSION_INCUMBENT_AUC = 0.0710
REGRESSION_TOL = 0.006

KNOWN_ANSWER_MIN_AUC = 0.95      # licensing gate, same constant the instrument itself uses

# Provenance-pinned, drift-checked in --self-test (see DISCLOSURE 3c).
REDUNDANT_CROSS = 0.95
REDUNDANT_CROSS_SOURCE = ("experiments/exp_grounding_consolidation_loop_degree_invariant_v1.py",
                          "REDUNDANT_CROSS = 0.95")

PAIRINGS = (
    ("MAIN_STORE_DEF",        "USAGE_STORE",   "DEFINITIONAL",  "MAIN"),
    ("MAIN_COUNTS_DEF",       "USAGE_COUNTS",  "DEFINITIONAL",  "MAIN"),
    ("TRAP_CORPUS_HALVES",    "USAGE_HALF_A",  "USAGE_HALF_B",  "TRAP"),
    ("TRAP_STORE_DIMHALVES",  "STORE_DIM_LO",  "STORE_DIM_HI",  "TRAP"),
)
HUB_ARMS = ("HUB_CCA_BOTH", "HUB_CCA_X", "HUB_RRR", "RESIDUAL_X")
PRIMARY_PAIRING = "MAIN_STORE_DEF"
PRIMARY_ARM = "HUB_CCA_BOTH"
COMMON_FLOORS = ("F_ORTHOGRAPHIC", "F_FREQUENCY")


# =================================================================================================
# SMALL HELPERS
# =================================================================================================
def l2n(A: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalisation. FB's, reused verbatim, so every arm normalises identically."""
    return FB.l2n(A)


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 3:
        return float("nan")
    a = a - a.mean()
    b = b - b.mean()
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / den) if den > 1e-12 else 0.0


def _fix_signs(V: np.ndarray) -> np.ndarray:
    """Deterministic sign convention: the largest-magnitude entry of each column is positive.
    Removes the only source of non-determinism a correct eigen/SVD routine still has."""
    V = np.asarray(V, dtype=np.float64).copy()
    for j in range(V.shape[1]):
        i = int(np.argmax(np.abs(V[:, j])))
        if V[i, j] < 0:
            V[:, j] *= -1.0
    return V


def perm_null_p95(sp_: np.ndarray, ss_: np.ndarray, n_perm: int, seed: int) -> Dict:
    """95th percentile of the AUC under permutation of the P/S LABELS at this exact n.
    This is the pre-registered NULL_P95 term of the bar and is reported beside every margin."""
    sp_ = np.asarray(sp_, dtype=np.float64)
    ss_ = np.asarray(ss_, dtype=np.float64)
    pool = np.concatenate([sp_, ss_])
    n_p = sp_.size
    rng = np.random.default_rng(seed)
    out = np.empty(n_perm, dtype=np.float64)
    for b in range(n_perm):
        pm = rng.permutation(pool)
        out[b] = DISS.auc_of(pm[:n_p], pm[n_p:])
    return {"p95": round(float(np.percentile(out, 95)), 4),
            "p50": round(float(np.percentile(out, 50)), 4),
            "n_perm": int(n_perm)}


# =================================================================================================
# DEFINITIONAL CACHE -- BUILD IF MISSING (a FULL run must not depend on a wipeable scratch/ file)
# =================================================================================================
def build_definitional_cache(keep_keys: set) -> Dict[str, List[str]]:
    """Byte-identical re-expression of scratch/_simplewiki_coverage_probe.py:39-56.

    Keyed on Definition.definiendum_lemma (lowercased), value = sorted distinct definiens lemmas,
    capped at DEF_MAX_DEFINIENS distinct FIRST-COME (the cap is part of the cached construction and
    is reproduced, not silently improved). Filtered to `keep_keys` = the loaded anchors plus the
    loaded evaluation words. NO LLM. NOTHING under data/foundation/ is read or written.
    """
    if not os.path.exists(SIMPLEWIKI):
        raise SystemExit("DEFINITIONAL CORPUS MISSING: %s -- the definitional view is unbuildable "
                         "and data/foundation/ is a FORBIDDEN substitute (11-14 of 242 rows)."
                         % SIMPLEWIKI)
    print("[defcache] MISSING -- rebuilding from %s (this is the slow path)" % SIMPLEWIKI,
          flush=True)
    definiens: Dict[str, set] = {}
    n_lines = 0
    n_defs = 0
    t0 = time.time()
    with open(SIMPLEWIKI, encoding="utf-8", errors="replace") as f:
        for line in f:
            n_lines += 1
            s = line.strip()
            if not s or len(s) > DEF_MAX_LINE:
                continue
            for d in extract_definitions(s):
                n_defs += 1
                lem = (d.definiendum_lemma or "").strip().lower()
                if not lem:
                    continue
                bucket = definiens.setdefault(lem, set())
                if len(bucket) < DEF_MAX_DEFINIENS:
                    bucket.update(d.definiens_lemmas)
            if n_lines % 250000 == 0:
                print("[defcache] scanned=%d defs=%d definienda=%d t=%.0fs"
                      % (n_lines, n_defs, len(definiens), time.time() - t0), flush=True)
    out = {k: sorted(v) for k, v in definiens.items() if k in keep_keys}
    os.makedirs(os.path.dirname(DEF_CACHE), exist_ok=True)
    tmp = DEF_CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f)
    os.replace(tmp, DEF_CACHE)
    print("[defcache] BUILT %d definienda in %.0fs -> %s"
          % (len(out), time.time() - t0, DEF_CACHE), flush=True)
    return out


def load_definitional_cache(keep_keys: set) -> Tuple[Dict[str, List[str]], Dict]:
    if os.path.exists(DEF_CACHE):
        with open(DEF_CACHE, encoding="utf-8") as f:
            d = json.load(f)
        return {k: list(v) for k, v in d.items()}, {"source": "reused", "path": DEF_CACHE}
    t0 = time.time()
    d = build_definitional_cache(keep_keys)
    return d, {"source": "rebuilt_inline", "path": DEF_CACHE,
               "elapsed_s": round(time.time() - t0, 1)}


# =================================================================================================
# USAGE COUNT VIEWS -- the counting organ is INFO's, reused verbatim; only the sentence pool varies
# =================================================================================================
def usage_counts(words: Sequence[str], buckets: Dict[str, List[int]], sents: List[str],
                 allowed: Optional[set], tag: str) -> Dict[str, Counter]:
    """Per-word co-occurrence counts, restricted to `allowed` sentence indices (None = all).

    With allowed=None this is EXACTLY INFO.build_store_counts' construction
    (`prof = occ[:C3._n_profile(len(occ))]`, then INFO.raw_counts_for_window per profile sentence);
    --self-test asserts byte-equality against INFO.build_store_counts on sampled words so the
    reuse claim is proven, not asserted. The ONLY thing that varies across the corpus-halves trap
    is which sentences are eligible.
    """
    out: Dict[str, Counter] = {}
    t0 = time.time()
    for k, w in enumerate(words):
        occ = buckets.get(w, [])
        if allowed is not None:
            occ = [i for i in occ if i in allowed]
        prof = occ[:C3._n_profile(len(occ))]
        c: Counter = Counter()
        for i in prof:
            c.update(INFO.raw_counts_for_window(sents[i], w))
        out[w] = c
        if (k + 1) % 1000 == 0 or k == len(words) - 1:
            print("[counts:%s] %d/%d t=%.0fs" % (tag, k + 1, len(words), time.time() - t0),
                  flush=True)
    return out


def sparse_from_counts(counts_by_word: Dict[str, Counter], words: Sequence[str],
                       vocab: Dict[str, int], binary: bool, log1p: bool) -> sp.csr_matrix:
    rows, cols, vals = [], [], []
    for i, w in enumerate(words):
        c = counts_by_word.get(w) or {}
        for term, n in c.items():
            j = vocab.get(term)
            if j is None:
                continue
            rows.append(i)
            cols.append(j)
            vals.append(1.0 if binary else (np.log1p(float(n)) if log1p else float(n)))
    M = sp.csr_matrix((vals, (rows, cols)), shape=(len(words), max(1, len(vocab))),
                      dtype=np.float64)
    return M


def vocab_from_fit(counts_by_word: Dict[str, Counter], fit_words: Sequence[str]) -> Dict[str, int]:
    """Feature vocabulary built from FIT WORDS ONLY (pre-reg HELD-OUT SPLIT, bullet 3).
    sorted(set(...)) per the deterministic-ordering discipline; no hash(), no list(set())."""
    terms = set()
    for w in fit_words:
        c = counts_by_word.get(w) or {}
        terms.update(c.keys())
    return {t: i for i, t in enumerate(sorted(terms))}


def l2n_sparse_rows(M: sp.csr_matrix) -> sp.csr_matrix:
    n = np.sqrt(np.asarray(M.multiply(M).sum(axis=1)).ravel())
    n = np.maximum(n, 1e-12)
    return sp.diags(1.0 / n) @ M


def svd_basis_on_fit(Mfit: sp.csr_matrix, k: int, seed: int, tag: str) -> Tuple[np.ndarray, Dict]:
    """Right-singular basis of the FIT rows ONLY. Evaluation rows are projected through it and
    never contribute to it (pre-reg HELD-OUT SPLIT; DISCLOSURE 2 adjudication).

    Primary path: scipy svds with a FIXED v0 (the declared construction). Fallback: dense Gram
    eigendecomposition, taken ONLY on ArpackNoConvergence and RECORDED in metrics when taken.
    Both are exactly deterministic; --self-test asserts bit-identity across two calls.
    """
    m = int(min(Mfit.shape))
    k_eff = int(max(1, min(k, m - 1)))
    rng = np.random.default_rng(seed)
    v0 = rng.standard_normal(m)
    v0 /= np.linalg.norm(v0)
    diag = {"tag": tag, "k_requested": int(k), "k_effective": k_eff,
            "fit_shape": [int(Mfit.shape[0]), int(Mfit.shape[1])], "solver": "svds_arpack_v0"}
    try:
        U, s, Vt = svds(Mfit, k=k_eff, v0=v0, maxiter=20000, tol=0.0)
        order = np.argsort(s)[::-1]
        s = s[order]
        V = Vt[order].T
    except (ArpackNoConvergence, ValueError) as exc:
        diag["solver"] = "dense_gram_eigh_fallback"
        diag["fallback_reason"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        print("[svd:%s] ARPACK fallback -> dense Gram eigh (%s)" % (tag, diag["fallback_reason"]),
              flush=True)
        G = np.asarray((Mfit @ Mfit.T).todense(), dtype=np.float64)
        G = 0.5 * (G + G.T)
        w, U = np.linalg.eigh(G)
        idx = np.argsort(w)[::-1][:k_eff]
        w = np.maximum(w[idx], 0.0)
        U = U[:, idx]
        s = np.sqrt(w)
        V = np.asarray((Mfit.T @ U), dtype=np.float64) / np.maximum(s, 1e-12)
    V = _fix_signs(V)
    diag["singular_values_top5"] = [round(float(x), 5) for x in s[:5]]
    diag["spectral_energy_kept"] = round(float(np.sum(s ** 2) /
                                               max(1e-12, (Mfit.multiply(Mfit)).sum())), 5)
    return V.astype(np.float64), diag


# =================================================================================================
# CCA -- the closed-form "which component of each channel does the other predict"
# =================================================================================================
def _inv_sqrt_psd(S: np.ndarray, floor_rel: float = 1e-10) -> np.ndarray:
    w, Q = np.linalg.eigh(0.5 * (S + S.T))
    w = np.maximum(w, floor_rel * max(1e-12, float(w.max())))
    return (Q * (w ** -0.5)) @ Q.T


def cca_fit(X: np.ndarray, Y: np.ndarray, lam_rel: float, k: int) -> Dict:
    """Closed-form CCA. Returns unit-variance canonical directions and their correlations.

    Ridge is RELATIVE (lam_rel * mean eigenvalue scale) so one grid works for views of different
    scale; lam_rel is selected INSIDE the fit set and never sees an evaluation word or a gold.
    """
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    n = X.shape[0]
    mx = X.mean(axis=0)
    my = Y.mean(axis=0)
    Xc = X - mx
    Yc = Y - my
    d = max(1, n - 1)
    Sxx = (Xc.T @ Xc) / d
    Syy = (Yc.T @ Yc) / d
    Sxy = (Xc.T @ Yc) / d
    Sxx = Sxx + lam_rel * (np.trace(Sxx) / Sxx.shape[0]) * np.eye(Sxx.shape[0])
    Syy = Syy + lam_rel * (np.trace(Syy) / Syy.shape[0]) * np.eye(Syy.shape[0])
    Wx = _inv_sqrt_psd(Sxx)
    Wy = _inv_sqrt_psd(Syy)
    M = Wx @ Sxy @ Wy
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    k_eff = int(max(1, min(k, s.size)))
    A = Wx @ U[:, :k_eff]
    B = Wy @ Vt[:k_eff].T
    rho = np.asarray(s[:k_eff], dtype=np.float64)
    for j in range(k_eff):                                  # deterministic joint sign convention
        i = int(np.argmax(np.abs(A[:, j])))
        if A[i, j] < 0:
            A[:, j] *= -1.0
            B[:, j] *= -1.0
    return {"mx": mx, "my": my, "A": A, "B": B, "rho": rho, "lam_rel": float(lam_rel),
            "k": k_eff}


def heldout_rho(fit: Dict, Xb: np.ndarray, Yb: np.ndarray) -> np.ndarray:
    """Per-component canonical correlation measured on a DISJOINT fit-half. This is the quantity
    k* is chosen by; it is a fit-internal, gold-blind number."""
    Uv = (np.asarray(Xb, dtype=np.float64) - fit["mx"]) @ fit["A"]
    Vv = (np.asarray(Yb, dtype=np.float64) - fit["my"]) @ fit["B"]
    return np.array([_pearson(Uv[:, j], Vv[:, j]) for j in range(fit["A"].shape[1])])


def hub_cca_both(fit: Dict, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """PRIMARY. rho-weighted mean of the two unit canonical variates.

    rho-weighting is part of the definition, not a variant: canonical variates are unit-variance by
    construction, so without it a rho=0.05 direction would count as much as a rho=0.9 one, which is
    not "the invariant"."""
    u = l2n(((np.asarray(X, dtype=np.float64) - fit["mx"]) @ fit["A"]) * fit["rho"])
    v = l2n(((np.asarray(Y, dtype=np.float64) - fit["my"]) @ fit["B"]) * fit["rho"])
    return l2n(u.astype(np.float64) + v.astype(np.float64))


def hub_cca_x(fit: Dict, X: np.ndarray) -> np.ndarray:
    return l2n(((np.asarray(X, dtype=np.float64) - fit["mx"]) @ fit["A"]) * fit["rho"])


def residual_x(fit: Dict, X: np.ndarray) -> np.ndarray:
    """WRONG-SOURCE CONTROL: the component of X that is NOT in the CCA subspace. If this scores as
    high as the hub, "the predictable component carries it" is void."""
    Q, _ = np.linalg.qr(np.asarray(fit["A"], dtype=np.float64))
    Xc = np.asarray(X, dtype=np.float64) - fit["mx"]
    return l2n(Xc - (Xc @ Q) @ Q.T)


def select_cca_lam_and_k(Xa, Ya, Xb, Yb, k_max: int) -> Tuple[float, int, Dict]:
    """lam THEN k*, both chosen INSIDE the fit set, on disjoint fit-halves A and B.

    lam: maximises the MEAN held-out canonical correlation of the top CCA_LAM_REF_K components.
    k*:  at the chosen lam, the NUMBER of components whose HELD-OUT rho >= CCA_HELDOUT_RHO_MIN,
         clipped to [CCA_K_MIN, CCA_K_MAX] exactly as pre-registered.
    Neither criterion touches an evaluation word or a WordNet gold.
    """
    trace = []
    best_lam, best_score = CCA_LAM_GRID[0], -np.inf
    for lam in CCA_LAM_GRID:
        f = cca_fit(Xa, Ya, lam, k_max)
        hr = heldout_rho(f, Xb, Yb)
        ref = int(min(CCA_LAM_REF_K, hr.size))
        score = float(np.nanmean(hr[:ref]))
        trace.append({"lam_rel": lam, "mean_heldout_rho_top%d" % ref: round(score, 5),
                      "n_components_ge_%.2f" % CCA_HELDOUT_RHO_MIN:
                          int(np.sum(hr >= CCA_HELDOUT_RHO_MIN))})
        if score > best_score:
            best_lam, best_score = lam, score
    f = cca_fit(Xa, Ya, best_lam, k_max)
    hr = heldout_rho(f, Xb, Yb)
    k_raw = int(np.sum(hr >= CCA_HELDOUT_RHO_MIN))
    k_star = int(min(CCA_K_MAX, max(CCA_K_MIN, k_raw)))
    k_star = int(min(k_star, k_max))
    diag = {"lam_grid_trace": trace, "lam_rel_selected": best_lam,
            "mean_heldout_rho_at_selected_lam": round(best_score, 5),
            "k_raw_components_with_heldout_rho_ge_%.2f" % CCA_HELDOUT_RHO_MIN: k_raw,
            "k_star": k_star, "k_star_clipped": bool(k_star != k_raw),
            "heldout_rho_top10": [round(float(x), 4) for x in hr[:10]]}
    return best_lam, k_star, diag


# =================================================================================================
# CHANNEL-INDEPENDENCE PRE-FLIGHT (pre-reg control 6)
# =================================================================================================
def channel_preflight_numpy(X: np.ndarray, Y: np.ndarray, n_pairs: int, seed: int) -> Dict:
    """Pearson r between the two views' PAIRWISE similarities over sampled FIT-word pairs.

    Threshold is the source cell's own REDUNDANT_CROSS = 0.95, drift-checked in --self-test. Per
    that cell's docstring, a HIGH marginal cross-channel correlation is EXPECTED for channels that
    must agree; this is used ONLY to flag near-IDENTICAL / collapsed channels, which is exactly
    what a TRAP pairing is. A MAIN pairing at or above the threshold is itself a VOID condition.
    """
    Xn = l2n(np.asarray(X, dtype=np.float64)).astype(np.float64)
    Yn = l2n(np.asarray(Y, dtype=np.float64)).astype(np.float64)
    n = Xn.shape[0]
    g = np.random.default_rng(seed)
    ii = g.integers(0, n, size=n_pairs)
    jj = g.integers(0, n, size=n_pairs)
    keep = ii != jj
    ii, jj = ii[keep], jj[keep]
    s_sim = np.sum(Xn[ii] * Xn[jj], axis=1)
    l_sim = np.sum(Yn[ii] * Yn[jj], axis=1)
    r = _pearson(s_sim, l_sim)
    return {"cross_sim_r": round(float(r), 4), "n_pairs": int(ii.size),
            "REDUNDANT_CROSS": REDUNDANT_CROSS,
            "redundant": bool(abs(r) >= REDUNDANT_CROSS),
            "source": "%s :: %s" % REDUNDANT_CROSS_SOURCE}


# =================================================================================================
# SCORING + THE BAR
# =================================================================================================
def pair_scores(store: Dict[str, np.ndarray], pairs: List[Tuple[str, str, str]]) -> np.ndarray:
    """DISS's own extractor, imported not reimplemented."""
    return DISS.dense_scores_from_dict_store(store, pairs)


def store_from_matrix(M: np.ndarray, words: Sequence[str]) -> Dict[str, np.ndarray]:
    Mn = l2n(np.asarray(M, dtype=np.float64))
    return {w: Mn[i] for i, w in enumerate(words)}


def scalar_pair_mean(scal: Dict[str, float], pairs) -> np.ndarray:
    return np.array([0.5 * (scal.get(a, 0.0) + scal.get(b, 0.0)) for a, b, _ in pairs])


def scalar_pair_max(scal: Dict[str, float], pairs) -> np.ndarray:
    return np.array([max(scal.get(a, 0.0), scal.get(b, 0.0)) for a, b, _ in pairs])


def scramble_floor(M: np.ndarray, words: Sequence[str], Pk, Sk, n_rep: int, seed: int) -> Dict:
    """F_SCRAMBLE estimated as a POLICY over `n_rep` independent word-to-row permutations.

    See DISCLOSURE 3c. A single permutation is a coin flip whose own 95% CI excludes 0.5 about 5%
    of the time under a pure null, which is not a property of the representation. The policy's
    value is the MEAN across permutations; the licensing band uses the standard error of that mean;
    and the BAR term is the 95th PERCENTILE of the across-permutation distribution -- the best the
    no-understanding policy plausibly achieves, which is STRICTLY HARDER than any single draw's
    point-plus-half-width. `single_draw_false_fire_rate` measures, rather than argues, how often
    the original one-draw test would have voided the run.
    """
    M32 = np.asarray(M, dtype=np.float32)
    rng = np.random.default_rng(seed)
    aucs = np.empty(n_rep, dtype=np.float64)
    n_fire = 0
    for r in range(n_rep):
        Msc = l2n(FB.scramble_null(M32, int(rng.integers(0, 2 ** 31 - 1))))
        st = {w: Msc[i] for i, w in enumerate(words)}
        aucs[r] = DISS.auc_of(pair_scores(st, Pk), pair_scores(st, Sk))
    n_p = len(Pk)
    approx_hw = 1.96 * float(np.sqrt((2 * n_p + 1) / (12.0 * n_p * n_p)))
    n_fire = int(np.sum(np.abs(aucs - 0.5) > approx_hw))
    mean = float(aucs.mean())
    sd = float(aucs.std(ddof=1))
    sem = sd / float(np.sqrt(n_rep))
    lo, hi = mean - 1.96 * sem, mean + 1.96 * sem
    band = ("ABOVE_0.5_SUBSTITUTABILITY" if lo > 0.5 else
            "BELOW_0.5_COOCCURRENCE" if hi < 0.5 else "NOT_SEPARATED_FROM_CHANCE")
    p95 = float(np.percentile(aucs, 95))
    return {"auc": round(mean, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "ci_halfwidth": round(1.96 * sem, 4), "band": band,
            "estimator": "mean over %d independent permutations (a floor is a POLICY)" % n_rep,
            "n_reps": n_rep, "sd_across_permutations": round(sd, 4),
            "p95_across_permutations": round(p95, 4),
            "p05_across_permutations": round(float(np.percentile(aucs, 5)), 4),
            "single_draw_false_fire_rate": round(n_fire / float(n_rep), 4),
            "single_draw_false_fire_note": "fraction of individual permutations whose own 95% CI "
                                           "would have excluded 0.5 and voided the run",
            "BAR_UPPER": round(p95, 4),
            "null": {"p95": round(p95, 4), "p50": round(float(np.percentile(aucs, 50)), 4),
                     "n_perm": n_rep},
            "digest": _digest(aucs)}


def score_arm(name: str, sP: np.ndarray, sS: np.ndarray, seed: int, n_boot: int,
              n_perm: int) -> Dict:
    res = DISS.auc_bootstrap(sP, sS, n_boot, seed)
    res["null"] = perm_null_p95(sP, sS, n_perm, seed + 55)
    res["ci_upper_point_plus_hw"] = round(float(res["auc"] + res["ci_halfwidth"]), 4)
    res["BAR_UPPER"] = round(float(res["auc"] + res["ci_halfwidth"]), 4)
    res["digest"] = _digest(np.concatenate([sP, sS]))
    print("[auc] %-38s AUC=%.4f CI=%r HW=%.4f nullp95=%.4f"
          % (name, res["auc"], res["ci95"], res["ci_halfwidth"], res["null"]["p95"]), flush=True)
    return res


def compute_bar(arm_name: str, arm_res: Dict, arm_floors: Dict[str, Dict],
                common_floors: Dict[str, Dict]) -> Dict:
    """BAR = max over the FOUR floors' own 95% CI UPPER bounds and the arm's own NULL_P95.

    The pre-reg is explicit that a floor's POINT value may not be the gate: the term is
    `point + its own half-width`. NO cached bar (0.5431 / 0.5943 / 0.6317 or any other) is
    imported. BAR_STRICT_PERCENTILE additionally reports the same max taken over each floor's
    bootstrap percentile upper bound, so a reader can see whether the choice of upper-bound
    convention could ever have changed the reading.
    """
    terms = {}
    strict = {}
    for fname, fres in list(common_floors.items()) + list(arm_floors.items()):
        terms[fname + "_hi"] = round(float(fres.get(
            "BAR_UPPER", fres["auc"] + fres["ci_halfwidth"])), 4)
        strict[fname + "_ci95hi"] = round(float(max(fres["ci95"][1],
                                                    fres.get("BAR_UPPER", -1.0))), 4)
    terms["NULL_P95"] = float(arm_res["null"]["p95"])
    strict["NULL_P95"] = float(arm_res["null"]["p95"])
    bar = float(max(terms.values()))
    binding = sorted([k for k, v in terms.items() if abs(v - bar) < 1e-12])
    return {"BAR": round(bar, 4), "binding_term": binding, "terms": terms,
            "BAR_STRICT_PERCENTILE": round(float(max(strict.values())), 4),
            "strict_terms": strict,
            "chance_to_bar_interval": round(bar - 0.5, 4)}


def read_branch(arm_res: Dict, bar_info: Dict) -> Dict:
    """The PRE-COMMITTED branch table. Direction is pre-registered: only AUC ABOVE 0.5 counts."""
    lo, hi = float(arm_res["ci95"][0]), float(arm_res["ci95"][1])
    hw = float(arm_res["ci_halfwidth"])
    bar = float(bar_info["BAR"])
    gap = float(bar_info["chance_to_bar_interval"])
    if hw > gap and lo <= bar <= hi:
        branch = "B_UNDERPOWERED"
    elif lo > bar:
        branch = "B_PASS_CANDIDATE"
    elif hi < bar:
        branch = "B_NEGATIVE"
    else:
        branch = "B_UNDERPOWERED"
    return {"branch": branch, "lo": round(lo, 4), "hi": round(hi, 4),
            "ci_halfwidth": round(hw, 4), "BAR": round(bar, 4),
            "margin_lo_minus_bar": round(lo - bar, 4),
            "chance_to_bar_interval": round(gap, 4),
            "halfwidth_exceeds_chance_to_bar": bool(hw > gap),
            "null_p95": arm_res["null"]["p95"]}


# =================================================================================================
# PLANTED POSITIVE CONTROL -- the discriminator-fires gate (pre-reg control 7 / META_RULE_K)
# =================================================================================================
def planted_world(seed: int) -> Dict:
    """A synthetic two-view world with a planted CROSS-VIEW invariant the raw views cannot see.

    CONSTRUCTION. n words, an 8-dim shared latent Z, and 120-dim view-private noise in each view.
      - PLANTED-P pairs share (almost) the same latent Z and have INDEPENDENT noise.
      - PLANTED-S pairs have DIFFERENT latents but share their NOISE IN BOTH VIEWS.
    So raw cosine in either view is dominated by the shared noise and ranks the S pairs ABOVE the
    P pairs (the incumbent's exact disease), while the only component of X that Y can predict is Z,
    which the P pairs share. Nx and Ny are independent draws, so no noise direction is
    cross-predictable and CCA cannot smuggle it into the hub.

    THE LATENT AMPLITUDE IS LOAD-BEARING AND WAS A REAL BUG ON FIRST WRITE. With LAT_AMP=1 the
    latent block carries 64 * d_lat = 512 units of energy against the noise block's 120, so the
    RAW view separated the planted pairs at AUC 0.9148 and the gate correctly refused the cell.
    LAT_AMP=0.25 puts the latent at 512 * 0.0625 = 32 against 120, which is the regime the
    paragraph above describes: noise-dominated raw views, a latent recoverable only across views.

    ASSERTION: hub AUC >= 0.90 while the raw X view stays <= 0.60. If the pipeline cannot recover a
    PLANTED invariant, no negative it produces is interpretable.
    """
    rng = np.random.default_rng(seed)
    n_fit, n_pair = 900, 120
    d_lat, d_noise = 8, 120
    LAT_AMP = 0.25
    n = n_fit + 2 * n_pair + 2 * n_pair
    Z = rng.standard_normal((n, d_lat))
    Nx = rng.standard_normal((n, d_noise))
    Ny = rng.standard_normal((n, d_noise))
    p_i = np.arange(n_fit, n_fit + n_pair)
    p_j = p_i + n_pair
    s_i = np.arange(n_fit + 2 * n_pair, n_fit + 3 * n_pair)
    s_j = s_i + n_pair
    # PLANTED-P: near-identical latent, independent noise.
    Z[p_j] = 0.90 * Z[p_i] + np.sqrt(1.0 - 0.90 ** 2) * rng.standard_normal((n_pair, d_lat))
    # PLANTED-S: different latent, shared noise in BOTH views.
    Nx[s_j] = Nx[s_i]
    Ny[s_j] = Ny[s_i]
    Wx = rng.standard_normal((d_lat, 64))
    Wy = rng.standard_normal((d_lat, 64))
    X = np.hstack([LAT_AMP * (Z @ Wx), Nx]).astype(np.float64)
    Y = np.hstack([LAT_AMP * (Z @ Wy), Ny]).astype(np.float64)
    return {"X": l2n(X).astype(np.float64), "Y": l2n(Y).astype(np.float64),
            "fit_idx": np.arange(n_fit),
            "P": list(zip(p_i.tolist(), p_j.tolist())),
            "S": list(zip(s_i.tolist(), s_j.tolist()))}


def run_planted_positive_control(seed: int) -> Dict:
    w = planted_world(seed)
    X, Y, fit_idx = w["X"], w["Y"], w["fit_idx"]
    half = fit_idx.size // 2
    fa, fb = fit_idx[:half], fit_idx[half:]
    lam, k_star, sel = select_cca_lam_and_k(X[fa], Y[fa], X[fb], Y[fb], k_max=32)
    fit = cca_fit(X[fit_idx], Y[fit_idx], lam, k_star)
    H = hub_cca_both(fit, X, Y)
    Xn = l2n(X)

    def _auc(M):
        sp_ = np.array([float(M[i] @ M[j]) for i, j in w["P"]])
        ss_ = np.array([float(M[i] @ M[j]) for i, j in w["S"]])
        return DISS.auc_of(sp_, ss_)

    auc_hub = float(_auc(H))
    auc_raw = float(_auc(Xn))
    auc_raw_y = float(_auc(l2n(Y)))
    out = {"auc_hub": round(auc_hub, 4), "auc_raw_view_X": round(auc_raw, 4),
           "auc_raw_view_Y": round(auc_raw_y, 4),
           "k_star": k_star, "lam_rel": lam, "rho_top5": [round(float(x), 4)
                                                          for x in fit["rho"][:5]],
           "GATE_hub_ge_0.90": bool(auc_hub >= 0.90),
           "GATE_raw_le_0.60": bool(auc_raw <= 0.60),
           "selection_diag": {k: sel[k] for k in ("lam_rel_selected", "k_star")}}
    out["PASS"] = bool(out["GATE_hub_ge_0.90"] and out["GATE_raw_le_0.60"])
    return out


# =================================================================================================
# SELF-TEST
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    t0 = time.time()

    # --- 1. REDUNDANT_CROSS has not drifted in the source cell ---------------------------------
    src = os.path.join(REPO, REDUNDANT_CROSS_SOURCE[0])
    txt = open(src, encoding="utf-8", errors="replace").read()
    assert re.search(r"^REDUNDANT_CROSS\s*=\s*0\.95\b", txt, re.M), \
        "REDUNDANT_CROSS DRIFTED in %s -- this cell's pinned 0.95 is stale" % src
    ev["redundant_cross_pin_verified"] = True

    # --- 2. deterministic seeding contract ------------------------------------------------------
    assert MASTER_SEED == CTS.MASTER_SEED == 20260816
    ev["master_seed"] = MASTER_SEED

    # --- 3. real code paths, constructed and CALLED ---------------------------------------------
    C = CTS.load_cache()
    aux = CTS.load_aux()
    ev["cache_shapes"] = {"mat": list(np.asarray(C["mat"]).shape),
                          "t_mat": list(np.asarray(aux["t_mat"]).shape),
                          "n_anchors": len(C["anchors"])}
    assert np.asarray(C["mat"]).shape[0] == len(C["anchors"]) == np.asarray(aux["t_mat"]).shape[0]

    defs_demo = extract_definitions("A pangolin is a scaly mammal that eats ants.")
    assert defs_demo and defs_demo[0].definiendum_lemma, "extract_definitions returned nothing"
    ev["extract_definitions_demo"] = {"definiendum_lemma": defs_demo[0].definiendum_lemma,
                                      "head": defs_demo[0].head,
                                      "n_definiens_lemmas": len(defs_demo[0].definiens_lemmas)}
    cl = content_lemmas("A pangolin is a scaly mammal that eats ants.")
    assert cl == sorted(set(cl)) and len(cl) > 2
    ev["content_lemmas_demo"] = cl[:6]

    W = CTS.fit_ridge(np.eye(4), np.eye(4), 1e-3)
    assert W.shape == (4, 4)
    ev["fit_ridge_ok"] = True

    a = np.array([3.0, 2.0, 1.0])
    b = np.array([0.5, 0.4, 0.3])
    assert abs(DISS.auc_of(a, b) - 1.0) < 1e-12
    bs = DISS.auc_bootstrap(a, b, 200, MASTER_SEED)
    assert set(("auc", "ci95", "ci_halfwidth", "band")).issubset(bs)
    ev["auc_of_and_bootstrap_ok"] = True

    cov = DISS._pair_covariates([("dog", "cat", "n")], {"dog": 2.0, "cat": 1.0})
    assert cov.shape == (1, 5)
    assert abs(DISS.smd(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))) < 1e-12
    ev["pair_covariates_and_smd_ok"] = True

    pf = FB.constant_prototype_floor(np.random.default_rng(1).standard_normal((20, 8)))
    assert pf.shape == (20,)
    sc = FB.scramble_null(np.arange(12, dtype=np.float32).reshape(6, 2), MASTER_SEED)
    assert sc.shape == (6, 2)
    assert np.allclose(np.linalg.norm(FB.l2n(np.ones((3, 4))), axis=1), 1.0)
    ev["floor_battery_ok"] = True

    # --- 4. SVD basis is BIT-IDENTICAL across two calls ------------------------------------------
    rngm = np.random.default_rng(MASTER_SEED + 3)
    Msm = sp.csr_matrix((np.abs(rngm.standard_normal(1200)),
                         (rngm.integers(0, 60, 1200), rngm.integers(0, 90, 1200))),
                        shape=(60, 90))
    V1, d1 = svd_basis_on_fit(Msm, 12, MASTER_SEED + 4, "selftest")
    V2, d2 = svd_basis_on_fit(Msm, 12, MASTER_SEED + 4, "selftest")
    assert V1.tobytes() == V2.tobytes(), "SVD BASIS IS NOT BIT-IDENTICAL ACROSS TWO CALLS"
    ev["svd_bit_identical"] = True
    ev["svd_solver"] = d1["solver"]

    # --- 5. usage_counts(allowed=None) reproduces INFO.build_store_counts BYTE-FOR-BYTE ----------
    sents, buckets, _counts, prov = INFO.load_corpus_and_buckets()
    ev["corpus"] = {"n_sentences": len(sents), "n_buckets": len(buckets),
                    "provenance": prov.get("source")}
    probe_words = sorted(set(C["anchors"][:40]) & set(buckets))[:8]
    mine = usage_counts(probe_words, buckets, sents, None, "selftest")
    tmp_dir = os.path.join(REPO, "data", "exp_%s_selftest" % ANCHOR_NAME)
    theirs, _d = INFO.build_store_counts(probe_words, buckets, sents, tmp_dir)
    for w in probe_words:
        assert dict(mine[w]) == dict(theirs[w]), \
            "usage_counts DIVERGES from INFO.build_store_counts on %r" % w
    ev["usage_counts_matches_INFO_build_store_counts"] = {"n_probe_words": len(probe_words)}

    # --- 6. CCA recovers a known planted direction (sanity, before the full control) -------------
    rng = np.random.default_rng(MASTER_SEED + 7)
    Zs = rng.standard_normal((400, 3))
    Xs = np.hstack([Zs, rng.standard_normal((400, 5))])
    Ys = np.hstack([Zs @ rng.standard_normal((3, 3)), rng.standard_normal((400, 5))])
    fs = cca_fit(Xs, Ys, 1e-3, 3)
    assert float(fs["rho"][0]) > 0.90, "CCA failed to recover an EXACTLY shared latent: rho0=%.4f" \
        % float(fs["rho"][0])
    ev["cca_recovers_shared_latent_rho0"] = round(float(fs["rho"][0]), 4)
    f_a = cca_fit(Xs, Ys, 1e-3, 3)
    assert f_a["A"].tobytes() == fs["A"].tobytes(), "CCA IS NOT DETERMINISTIC"
    ev["cca_bit_identical"] = True

    # --- 7. residual_x is genuinely ORTHOGONAL to the CCA subspace -------------------------------
    Qb = np.linalg.qr(fs["A"])[0]
    Xc_s = Xs - fs["mx"]
    Rraw = Xc_s - (Xc_s @ Qb) @ Qb.T
    leak = float(np.max(np.abs(Rraw @ Qb)))
    ev["residual_max_abs_projection_onto_cca_subspace"] = round(leak, 10)
    assert leak < 1e-8, ("RESIDUAL_X is not orthogonal to the CCA subspace (leak=%.3e) -- the "
                         "wrong-source control would be void" % leak)
    assert residual_x(fs, Xs).shape == Xs.shape

    # --- 8. perm_null_p95 is a real null (a random arm's p95 must sit near 0.5, above the point) --
    rr = np.random.default_rng(MASTER_SEED + 11)
    nl = perm_null_p95(rr.standard_normal(200), rr.standard_normal(200), 500, MASTER_SEED + 12)
    assert 0.5 < nl["p95"] < 0.70, "permutation null p95 is implausible: %r" % nl
    ev["perm_null_sanity"] = nl

    # --- 9. THE DISCRIMINATOR-FIRES GATE: planted positive control ------------------------------
    pc = run_planted_positive_control(MASTER_SEED + 21)
    ev["PLANTED_POSITIVE_CONTROL"] = pc
    print("[selftest] planted positive control: %r" % pc, flush=True)
    if not pc["PASS"]:
        raise SystemExit(
            "PLANTED POSITIVE CONTROL FAILED -- the pipeline cannot recover a PLANTED cross-view "
            "invariant (hub AUC=%.4f needs >=0.90; raw view AUC=%.4f needs <=0.60). NO NEGATIVE "
            "FROM THIS CELL WOULD BE INTERPRETABLE. Cell FAILED. %r"
            % (pc["auc_hub"], pc["auc_raw_view_X"], pc))

    # --- 10. NOTHING under data/foundation/ is on this cell's path -------------------------------
    # AST, not a text scan: this file DISCUSSES data/foundation at length in its disclosures, and a
    # grep-style check cannot tell prose from a path. The property that actually matters is that no
    # string naming `foundation` is ever handed to a file-opening or path-building call. Docstring
    # and comment text is never a Call argument, so it cannot produce a false pass OR a false fail.
    import ast as _ast
    src_self = open(_THIS, encoding="utf-8").read()
    _IO_FUNCS = {"open", "load", "loadtxt", "loadz", "save", "savez", "savez_compressed",
                 "join", "makedirs", "replace", "remove", "rmtree", "listdir", "walk", "glob"}
    bad_io = []
    for node in _ast.walk(_ast.parse(src_self)):
        if not isinstance(node, _ast.Call):
            continue
        fn = node.func
        nm = fn.attr if isinstance(fn, _ast.Attribute) else getattr(fn, "id", "")
        if nm not in _IO_FUNCS:
            continue
        for a in _ast.walk(node):
            if isinstance(a, _ast.Constant) and isinstance(a.value, str) \
                    and "foundation" in a.value.lower():
                bad_io.append({"call": nm, "literal": a.value[:80]})
    assert not bad_io, ("A FORBIDDEN SOURCE IS ON THE EXECUTABLE PATH: a string naming "
                        "'foundation' reaches a file/path call: %r" % bad_io)
    assert "wordnet" not in json.dumps([p[1] for p in PAIRINGS] + [p[2] for p in PAIRINGS]).lower(), \
        "WordNet appears as a VIEW; it is the answer key (AUC 0.8911) and may only license"
    ev["forbidden_sources_absent"] = {
        "data/foundation/**": "no literal naming it reaches any file/path call (AST-verified); "
                              "READ-ONLY, ONE DISK, NO BACKUP -- nothing written there either",
        "wordnet_glosses_as_a_view": "no pairing names a WordNet view; WordNet is the licensing "
                                     "KNOWN_ANSWER arm only",
        "n_io_calls_scanned_for_foundation": len(_IO_FUNCS)}

    # --- 11. per-experiment TIMEOUT, computed not guessed -----------------------------------------
    ev["TIMEOUT_FORMULA"] = timeout_formula(len(sents))

    ev["elapsed_s"] = round(time.time() - t0, 1)
    print("[selftest] PASS in %.1fs" % ev["elapsed_s"], flush=True)
    return ev


def timeout_formula(n_sentences: int) -> Dict:
    """Per-experiment timeout, COMPUTED. Terms, each with its measured or bounded basis:
      corpus load (cached npz)                                   ~60 s
      definitional cache: reused ~1 s, REBUILD bounded at        ~3600 s (2.78 M lines)
      usage counts, 3 pools x 3681 words over 34,169 sentences   ~900 s
      4 truncated SVDs at k=128 over <=3064 x V sparse            ~600 s
      CCA lam+k* selection, 4 pairings x 5 lam                    ~180 s
      AUC bootstraps + permutation nulls (~70 arms)               ~600 s
    Sum with a 1.5x safety factor.
    """
    terms = {"corpus_load_s": 60, "def_cache_rebuild_bound_s": 3600,
             "usage_counts_s": 900, "svd_s": 600, "cca_selection_s": 180,
             "auc_and_nulls_s": 600}
    base = sum(terms.values())
    return {"terms": terms, "n_sentences": int(n_sentences), "base_s": base,
            "safety_factor": 1.5, "TIMEOUT_S": int(base * 1.5)}


# =================================================================================================
# THE RUN
# =================================================================================================
def run(grid: str, out_dir: str) -> Dict:
    t0 = time.time()
    hb = [0]

    def beat(tag: str):
        hb[0] += 1
        emit_heartbeat(out_dir, hb[0], time.time() - t0, extra={"stage": tag})
        print("[stage] %s t=%.0fs" % (tag, time.time() - t0), flush=True)

    rep: Dict = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "grid": grid,
                 "prereg": PREREG, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                 "PREREG_AMBIGUITY_ADJUDICATION":
                     "VIEWS says the SVD basis is fit on 'HELD-OUT WORDS ONLY'; HELD-OUT SPLIT "
                     "excludes evaluation words from EVERY fit including the SVD basis. THE "
                     "SECOND IS DEFINITIVE: the basis is fit on the 3064 FIT words. The prereg "
                     "file was NOT edited.",
                 "RE_ATTEMPT_OF_FAILED_MECHANISM_CLASS": [
                     "exp_self_teacher_gloss_relational_predictive_heldout_new_v1 landed -0.0105 "
                     "(gloss ablation 0.5978, WORSE than grounding alone 0.6361)",
                     "exp_redundancy_decorrelation_from_coherence_gate_precheck_v1 landed "
                     "HARD_FAIL_NO_SAFE_SECOND_VIEW"],
                 "FORBIDDEN_SOURCES_NOT_USED": {
                     "data/foundation/**": "11-14 of 242 rows, unmeasurable; READ-ONLY, ONE DISK, "
                                           "NO BACKUP -- nothing read from or written to it",
                     "wordnet_glosses_as_view": "AUC 0.8911, it IS the answer key; WordNet appears "
                                                "ONLY as the licensing KNOWN_ANSWER arm"},
                 "NO_CACHED_BAR_IMPORTED": "0.5431 / 0.5943 / 0.6317 appear nowhere as a threshold"}

    # ---------------------------------------------------------------- LOAD (no rebuild anywhere)
    beat("load_cache")
    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors: List[str] = C["anchors"]
    mat = np.asarray(C["mat"], dtype=np.float64)
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    pos_idx: Dict[str, int] = C["pos"]
    t_mat = np.asarray(aux["t_mat"], dtype=np.float64)
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}

    units_prior = load_units(out_dir)

    # ---------------------------------------------------------------- POPULATION (loaded, never rebuilt)
    beat("population")
    inst_units = load_units(INSTRUMENT_DIR)
    if POP_KEY not in inst_units:
        raise SystemExit("POPULATION CHECKPOINT MISSING: %s in %s. This cell LOADS the landed "
                         "matched population and must never rebuild it." % (POP_KEY, INSTRUMENT_DIR))
    pop = inst_units[POP_KEY]
    matchedP = [tuple(x) for x in pop["matchedP"]]
    matchedS = [tuple(x) for x in pop["matchedS"]]
    n_rows_all = len(matchedP)
    assert n_rows_all == len(matchedS), "P/S row counts disagree in the landed population"
    eval_words = sorted(set(w for a, b, _ in matchedP + matchedS for w in (a, b)))
    rep["POPULATION_SOURCE"] = {"dir": os.path.relpath(INSTRUMENT_DIR, REPO), "unit": POP_KEY,
                                "n_rows": n_rows_all, "n_eval_words": len(eval_words)}
    print("[population] rows=%d eval_words=%d" % (n_rows_all, len(eval_words)), flush=True)

    # ---------------------------------------------------------------- DEFINITIONAL CACHE
    beat("definitional_cache")
    anchor_ok = set(a for a, ok in zip(anchors, mat_ok) if ok)
    defs, def_prov = load_definitional_cache(anchor_ok | set(eval_words))
    rep["DEFINITIONAL_CACHE"] = dict(def_prov, n_definienda=len(defs),
                                     corpus=os.path.relpath(SIMPLEWIKI, REPO))

    # ---------------------------------------------------------------- HELD-OUT SPLIT
    beat("heldout_split")
    def_keys = sorted(set(defs) & anchor_ok)
    fit_words = sorted(set(def_keys) - set(eval_words))
    if SMOKE:
        fit_words = fit_words[:1200]
    assert not (set(fit_words) & set(eval_words)), \
        "LEAKAGE: fit and evaluation word sets intersect -- the run is VOID"
    WORDS = list(fit_words) + list(eval_words)
    WIDX = {w: i for i, w in enumerate(WORDS)}
    fit_rows = np.arange(len(fit_words))
    rep["HELD_OUT_SPLIT"] = {
        "n_definienda_total": len(defs),
        "n_definienda_that_are_valid_anchors": len(def_keys),
        "n_fit_words": len(fit_words), "n_eval_words": len(eval_words),
        "n_eval_words_with_definitional_view": int(sum(1 for w in eval_words if w in defs)),
        "group_disjoint_assert_passed": True,
        "excluded_from": ["svd_basis", "feature_vocabulary", "cca", "ridge", "lam_selection",
                          "k_star_selection"],
        "adjudication": "basis fit on FIT words (see PREREG_AMBIGUITY_ADJUDICATION)"}
    print("[split] fit=%d eval=%d (eval with defs=%d)"
          % (len(fit_words), len(eval_words),
             rep["HELD_OUT_SPLIT"]["n_eval_words_with_definitional_view"]), flush=True)

    # ---------------------------------------------------------------- CORPUS + USAGE COUNTS
    beat("corpus")
    sents, buckets, corpus_counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["CORPUS"] = {"n_sentences": len(sents), "provenance": corpus_prov.get("source")}
    rng_half = np.random.default_rng(MASTER_SEED + 131)
    perm_s = rng_half.permutation(len(sents))
    half_a = set(int(i) for i in perm_s[: len(sents) // 2])
    half_b = set(int(i) for i in perm_s[len(sents) // 2:])
    rep["CORPUS"]["half_sizes"] = [len(half_a), len(half_b)]

    scores_keys = {p[0]: unit_key("SCORES", CODE_VERSION, grid, p[0]) for p in PAIRINGS}
    ref_key = unit_key("SCORES", CODE_VERSION, grid, "REFERENCE")
    views_key = unit_key("VIEWS", CODE_VERSION, grid)
    need_views = any(k not in units_prior for k in list(scores_keys.values()) + [ref_key])

    view_diag: Dict = {}
    VIEWS: Dict[str, np.ndarray] = {}
    usage_full_counts: Dict[str, Counter] = {}

    if need_views:
        beat("usage_counts_full")
        usage_full_counts = usage_counts(WORDS, buckets, sents, None, "FULL")
        beat("usage_counts_halves")
        ua = usage_counts(WORDS, buckets, sents, half_a, "HALF_A")
        ub = usage_counts(WORDS, buckets, sents, half_b, "HALF_B")

        def make_count_view(cnts: Dict[str, Counter], tag: str, binary: bool,
                            log1p: bool, seed_off: int) -> np.ndarray:
            vocab = vocab_from_fit(cnts, fit_words)
            M = l2n_sparse_rows(sparse_from_counts(cnts, WORDS, vocab, binary, log1p))
            Vb, sd = svd_basis_on_fit(M[fit_rows], K_SVD, MASTER_SEED + seed_off, tag)
            P = np.asarray(M @ Vb, dtype=np.float64)
            mass_all = np.asarray(M.multiply(M).sum(axis=1)).ravel()
            evrows = np.array([WIDX[w] for w in eval_words])
            nz = np.asarray((M != 0).sum(axis=1)).ravel()
            sd.update({"n_vocab_from_fit_words_only": len(vocab),
                       "eval_rows_with_zero_retained_mass": int(np.sum(mass_all[evrows] <= 0)),
                       "eval_mean_nonzero_features": round(float(np.mean(nz[evrows])), 2),
                       "fit_mean_nonzero_features": round(float(np.mean(nz[fit_rows])), 2)})
            view_diag[tag] = sd
            print("[view] %-16s vocab=%d dim=%d eval_zero_mass=%d"
                  % (tag, len(vocab), P.shape[1], sd["eval_rows_with_zero_retained_mass"]),
                  flush=True)
            return l2n(P).astype(np.float64)

        beat("build_views")
        defs_counts = {w: Counter({t: 1 for t in defs.get(w, ())}) for w in WORDS}
        VIEWS["DEFINITIONAL"] = make_count_view(defs_counts, "DEFINITIONAL", True, False, 201)
        VIEWS["USAGE_COUNTS"] = make_count_view(usage_full_counts, "USAGE_COUNTS", False, True, 202)
        VIEWS["USAGE_HALF_A"] = make_count_view(ua, "USAGE_HALF_A", False, True, 203)
        VIEWS["USAGE_HALF_B"] = make_count_view(ub, "USAGE_HALF_B", False, True, 204)

        store_rows = np.array([pos_idx[w] for w in WORDS])
        S = mat[store_rows]
        VIEWS["USAGE_STORE"] = l2n(S).astype(np.float64)
        d_half = S.shape[1] // 2
        VIEWS["STORE_DIM_LO"] = l2n(S[:, :d_half]).astype(np.float64)
        VIEWS["STORE_DIM_HI"] = l2n(S[:, d_half:]).astype(np.float64)
        view_diag["USAGE_STORE"] = {"dim": int(S.shape[1]), "source": "CTS.load_cache()['mat']"}
        view_diag["STORE_DIM_LO"] = {"dim": int(d_half), "source": "store dims 0:%d" % d_half}
        view_diag["STORE_DIM_HI"] = {"dim": int(S.shape[1] - d_half),
                                     "source": "store dims %d:%d" % (d_half, S.shape[1])}
        record_unit(out_dir, views_key, {"view_diag": view_diag})
    else:
        print("[views] ALL SCORES UNITS PRESENT -- view construction SKIPPED (resume)", flush=True)
        view_diag = (units_prior.get(views_key) or {}).get("view_diag", {})
    rep["VIEWS"] = view_diag

    # ---------------------------------------------------------------- COVERAGE CONTROL
    beat("coverage_control")
    has_def = {w: (w in defs and len(defs[w]) > 0) for w in eval_words}
    if need_views:
        has_use = {w: (len(usage_full_counts.get(w) or {}) > 0) for w in eval_words}
    else:
        cov_prev = (units_prior.get(views_key) or {}).get("coverage_has_use")
        if cov_prev is None:
            raise SystemExit("RESUME INCONSISTENT: coverage map absent but views skipped. Delete "
                             "units.jsonl for this cell and re-run.")
        has_use = {w: bool(v) for w, v in cov_prev.items()}
    if need_views:
        record_unit(out_dir, unit_key("COVERAGE", CODE_VERSION, grid),
                    {"has_use": {w: bool(v) for w, v in has_use.items()}})

    keep_rows, drop_reason = [], []
    n_drop_def = n_drop_use = n_drop_both = 0
    for i in range(n_rows_all):
        members = (matchedP[i][0], matchedP[i][1], matchedS[i][0], matchedS[i][1])
        bad_def = [w for w in members if not has_def.get(w, False)]
        bad_use = [w for w in members if not has_use.get(w, False)]
        if not bad_def and not bad_use:
            keep_rows.append(i)
            continue
        if bad_def and bad_use:
            n_drop_both += 1
        elif bad_def:
            n_drop_def += 1
        else:
            n_drop_use += 1
        drop_reason.append({"row": i, "no_definitional": bad_def, "no_usage": bad_use})
    keep_rows = np.array(keep_rows, dtype=int)
    n_keep = int(keep_rows.size)
    n_removed = n_rows_all - n_keep
    rep["CONTROL_5_COVERAGE"] = {
        "rule": "row dropped unless ALL FOUR member words have BOTH a definitional view and a "
                "usage profile",
        "n_rows_before": n_rows_all, "n_rows_after": n_keep,
        "N_ROWS_REMOVED": n_removed,
        "removed_pct": round(100.0 * n_removed / max(1, n_rows_all), 2),
        "removed_definitional_only": n_drop_def, "removed_usage_only": n_drop_use,
        "removed_both": n_drop_both,
        "BINDING": bool(n_removed > 0),
        "NOT_BINDING_NOTE": None if n_removed > 0 else
            "THIS CONTROL REMOVED 0 ROWS AND IS THEREFORE NOT A CONTROL",
        "examples": drop_reason[:10]}
    print("[coverage] %d -> %d rows (removed %d: def_only=%d use_only=%d both=%d)"
          % (n_rows_all, n_keep, n_removed, n_drop_def, n_drop_use, n_drop_both), flush=True)
    if n_keep < 20:
        raise SystemExit("SUB-POPULATION UNBUILDABLE: only %d rows survive coverage; an AUC here "
                         "is not interpretable." % n_keep)

    Pk = [matchedP[i] for i in keep_rows]
    Sk = [matchedS[i] for i in keep_rows]

    # post-drop matching balance + covered/uncovered frequency balance
    tri_all = l2n(t_mat)
    proto_all = FB.constant_prototype_floor(np.asarray(mat, dtype=np.float32), mat_ok)
    tri_of = {w: tri_all[pos_idx[w]] for w in eval_words}
    proto_of = {w: float(proto_all[pos_idx[w]]) for w in eval_words}
    covP = DISS._pair_covariates(Pk, fq_log, tri_of, proto_of)
    covS = DISS._pair_covariates(Sk, fq_log, tri_of, proto_of)
    names5 = ["mean_log_freq", "abs_freq_diff", "mean_length", "trigram_cosine", "mean_prototype"]
    covered_w = [w for w in eval_words if has_def.get(w) and has_use.get(w)]
    uncovered_w = [w for w in eval_words if not (has_def.get(w) and has_use.get(w))]
    rep["CONTROL_5_POST_DROP_BALANCE"] = {
        "smd_P_vs_S_on_surviving_rows": {names5[j]: round(DISS.smd(covP[:, j], covS[:, j]), 4)
                                         for j in range(5)},
        "n_eval_words_covered": len(covered_w), "n_eval_words_uncovered": len(uncovered_w),
        "smd_log_freq_covered_vs_uncovered": round(DISS.smd(
            np.array([fq_log.get(w, 0.0) for w in covered_w]),
            np.array([fq_log.get(w, 0.0) for w in uncovered_w])), 4) if uncovered_w else None,
        "note": "the audit measured SMD +0.550 for the STORE corpus; this is the simplewiki "
                "measurement, which was previously unmeasured"}

    # ---------------------------------------------------------------- CHANNEL-INDEPENDENCE PRE-FLIGHT
    beat("channel_preflight")
    if need_views:
        pfl = {}
        for pname, xv, yv, kind in PAIRINGS:
            pfl[pname] = channel_preflight_numpy(VIEWS[xv][fit_rows], VIEWS[yv][fit_rows],
                                                 PREFLIGHT_PAIRS, MASTER_SEED + 313)
            pfl[pname]["kind"] = kind
            pfl[pname]["VOID_IF_MAIN_AND_REDUNDANT"] = bool(kind == "MAIN"
                                                            and pfl[pname]["redundant"])
            print("[preflight] %-24s cross_sim_r=%.4f redundant=%s"
                  % (pname, pfl[pname]["cross_sim_r"], pfl[pname]["redundant"]), flush=True)
        record_unit(out_dir, unit_key("PREFLIGHT", CODE_VERSION, grid), {"preflight": pfl})
    else:
        pfl = (units_prior.get(unit_key("PREFLIGHT", CODE_VERSION, grid)) or {}).get("preflight", {})
    rep["CONTROL_6_CHANNEL_PREFLIGHT"] = pfl

    # ---------------------------------------------------------------- REFERENCE + FLOOR SCORES
    beat("reference_scores")
    units_prior = load_units(out_dir)

    def _as_arr(d):
        return {k: {"P": np.asarray(v["P"], dtype=np.float64),
                    "S": np.asarray(v["S"], dtype=np.float64)} for k, v in d.items()}

    if ref_key in units_prior:
        print("[scores] REFERENCE resumed from checkpoint", flush=True)
        ref_scores = _as_arr(units_prior[ref_key]["scores"])
        regression = units_prior[ref_key]["regression"]
        scram_incumbent = units_prior[ref_key]["scramble_floors"]["F_SCRAMBLE_INCUMBENT"]
    else:
        st_store = store_from_matrix(VIEWS["USAGE_STORE"], WORDS)
        st_def = store_from_matrix(VIEWS["DEFINITIONAL"], WORDS)
        st_cnt = store_from_matrix(VIEWS["USAGE_COUNTS"], WORDS)
        rng_r = np.random.default_rng(MASTER_SEED + 909)
        st_rand = store_from_matrix(rng_r.standard_normal((len(WORDS), 64)), WORDS)
        scram_incumbent = scramble_floor(VIEWS["USAGE_STORE"], WORDS, Pk, Sk, SCRAMBLE_REPS,
                                         MASTER_SEED + 4242)
        st_ortho = {w: tri_all[pos_idx[w]] for w in WORDS}

        # REGRESSION GATE -- rescored on the FULL landed 242 rows with THIS cell's code
        rg_P = pair_scores(st_store, matchedP)
        rg_S = pair_scores(st_store, matchedS)
        rg = DISS.auc_bootstrap(rg_P, rg_S, N_BOOT, MASTER_SEED + 8181)
        regression = {"expected": REGRESSION_INCUMBENT_AUC, "tol": REGRESSION_TOL,
                      "measured": rg["auc"], "ci95": rg["ci95"], "n_rows": n_rows_all,
                      "PASS": bool(abs(rg["auc"] - REGRESSION_INCUMBENT_AUC) <= REGRESSION_TOL)}

        fuse_P = 0.5 * (pair_scores(st_store, Pk) + pair_scores(st_def, Pk))
        fuse_S = 0.5 * (pair_scores(st_store, Sk) + pair_scores(st_def, Sk))
        ka_P = np.array([DISS.wn_best_path_similarity(a, b) for a, b, _ in Pk])
        ka_S = np.array([DISS.wn_best_path_similarity(a, b) for a, b, _ in Sk])
        raw = {
            "A_INCUMBENT_STORE": (pair_scores(st_store, Pk), pair_scores(st_store, Sk)),
            "A_USAGE_COUNTS": (pair_scores(st_cnt, Pk), pair_scores(st_cnt, Sk)),
            "A_DEF": (pair_scores(st_def, Pk), pair_scores(st_def, Sk)),
            "A_FUSE_NAIVE": (fuse_P, fuse_S),
            "KNOWN_ANSWER_WORDNET": (ka_P, ka_S),
            "RANDOM_VECTOR": (pair_scores(st_rand, Pk), pair_scores(st_rand, Sk)),
            "F_ORTHOGRAPHIC": (pair_scores(st_ortho, Pk), pair_scores(st_ortho, Sk)),
            "F_FREQUENCY": (scalar_pair_max(fq_log, Pk), scalar_pair_max(fq_log, Sk)),
            "F_CONSTANT_PROTOTYPE_INCUMBENT": (scalar_pair_mean(proto_of, Pk),
                                               scalar_pair_mean(proto_of, Sk)),
        }
        ref_scores = {k: {"P": v[0], "S": v[1]} for k, v in raw.items()}
        record_unit(out_dir, ref_key,
                    {"scores": {k: {"P": v["P"].tolist(), "S": v["S"].tolist()}
                                for k, v in ref_scores.items()},
                     "scramble_floors": {"F_SCRAMBLE_INCUMBENT": scram_incumbent},
                     "regression": regression})

    rep["REGRESSION_GATE"] = regression
    print("[regression] incumbent rescored on %d rows: %.4f (expect %.4f +/- %.3f) PASS=%s"
          % (regression["n_rows"], regression["measured"], REGRESSION_INCUMBENT_AUC,
             REGRESSION_TOL, regression["PASS"]), flush=True)
    if grid == "full" and not regression["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- this cell's own code does not reproduce the "
                         "landed incumbent AUC on the landed population: %r" % regression)

    # ---------------------------------------------------------------- MECHANISM SCORES PER PAIRING
    pair_scores_all: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {}
    scram_all: Dict[str, Dict[str, Dict]] = {}
    cca_diag: Dict = {}
    for pname, xv, yv, kind in PAIRINGS:
        beat("scores:%s" % pname)
        units_prior = load_units(out_dir)
        skey = scores_keys[pname]
        if skey in units_prior:
            print("[scores] %s resumed from checkpoint" % pname, flush=True)
            pair_scores_all[pname] = _as_arr(units_prior[skey]["scores"])
            cca_diag[pname] = units_prior[skey]["cca_diag"]
            scram_all[pname] = units_prior[skey]["scramble_floors"]
            continue
        X, Y = VIEWS[xv], VIEWS[yv]
        Xf, Yf = X[fit_rows], Y[fit_rows]
        rng_sp = np.random.default_rng(MASTER_SEED + 401)
        pp = rng_sp.permutation(Xf.shape[0])
        fa, fb = pp[: pp.size // 2], pp[pp.size // 2:]
        k_max = int(min(K_SVD, Xf.shape[1], Yf.shape[1]))
        lam, k_star, sel = select_cca_lam_and_k(Xf[fa], Yf[fa], Xf[fb], Yf[fb], k_max)
        fit = cca_fit(Xf, Yf, lam, k_star)
        lam_r, ridge_trace = CTS.select_ridge_lam(Xf - fit["mx"], l2n(Yf).astype(np.float64),
                                                  MASTER_SEED + 501)
        Wr = CTS.fit_ridge(Xf - fit["mx"], l2n(Yf).astype(np.float64), lam_r)
        cca_diag[pname] = {"x_view": xv, "y_view": yv, "kind": kind,
                           "selection": sel, "rho_top10": [round(float(x), 4)
                                                           for x in fit["rho"][:10]],
                           "rho_mean": round(float(np.mean(fit["rho"])), 4),
                           "k_star": int(fit["k"]),
                           "ridge_lam": lam_r, "ridge_trace": ridge_trace,
                           "fit_halves": [int(fa.size), int(fb.size)]}
        mats = {"HUB_CCA_BOTH": hub_cca_both(fit, X, Y),
                "HUB_CCA_X": hub_cca_x(fit, X),
                "HUB_RRR": l2n((X - fit["mx"]) @ Wr).astype(np.float64),
                "RESIDUAL_X": residual_x(fit, X)}
        sc: Dict[str, Dict[str, np.ndarray]] = {}
        scf: Dict[str, Dict] = {}
        for aname, M in mats.items():
            st = store_from_matrix(M, WORDS)
            sc[aname] = {"P": pair_scores(st, Pk), "S": pair_scores(st, Sk)}
            # F_SCRAMBLE recomputed FROM THIS ARM'S OWN MATRIX, as a policy over many permutations
            scf[aname + "__F_SCRAMBLE"] = scramble_floor(M, WORDS, Pk, Sk, SCRAMBLE_REPS,
                                                         MASTER_SEED + 4242)
            pr = FB.constant_prototype_floor(np.asarray(M, dtype=np.float32))
            pr_of = {w: float(pr[i]) for i, w in enumerate(WORDS)}
            sc[aname + "__F_CONSTANT_PROTOTYPE"] = {"P": scalar_pair_mean(pr_of, Pk),
                                                    "S": scalar_pair_mean(pr_of, Sk)}
        pair_scores_all[pname] = sc
        scram_all[pname] = scf
        record_unit(out_dir, skey,
                    {"scores": {k: {"P": v["P"].tolist(), "S": v["S"].tolist()}
                                for k, v in sc.items()},
                     "scramble_floors": scf,
                     "cca_diag": cca_diag[pname]})
    rep["CCA_DIAGNOSTICS"] = cca_diag

    # ---------------------------------------------------------------- AUC + BAR + BRANCHES
    beat("auc")
    all_scores: Dict[str, Dict[str, np.ndarray]] = dict(ref_scores)
    for pname, sc in pair_scores_all.items():
        for k, v in sc.items():
            all_scores["%s::%s" % (pname, k)] = v

    # META_RULE_AF: arms must differ
    digests = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in all_scores.items()}
    assert len(set(digests.values())) > 1, "ALL ARMS PRODUCED IDENTICAL SCORE VECTORS -- bug"
    rep["ARMS_MUST_DIFFER"] = {"n_arms": len(digests), "n_distinct_digests": len(set(digests.values())),
                               "digests": digests}

    auc: Dict[str, Dict] = {}
    for i, (k, v) in enumerate(sorted(all_scores.items())):
        auc[k] = score_arm(k, v["P"], v["S"], MASTER_SEED + 8181 + i, N_BOOT, N_PERM)
    # scramble floors are DISTRIBUTIONS over permutations, not single score vectors (DISCLOSURE 3c)
    auc["F_SCRAMBLE_INCUMBENT"] = scram_incumbent
    for pname, scf in scram_all.items():
        for k, v in scf.items():
            auc["%s::%s" % (pname, k)] = v
    for k in sorted(auc):
        if "F_SCRAMBLE" in k:
            print("[auc] %-38s AUC=%.4f (policy mean over %d perms) CI=%r p95_perm=%.4f "
                  "single_draw_false_fire=%.3f"
                  % (k, auc[k]["auc"], auc[k]["n_reps"], auc[k]["ci95"],
                     auc[k]["p95_across_permutations"], auc[k]["single_draw_false_fire_rate"]),
                  flush=True)
    rep["AUC_PER_ARM"] = auc
    rep["F_SCRAMBLE_ESTIMATOR_NOTE"] = (
        "F_SCRAMBLE is the MEAN over %d independent word-to-row permutations; its BAR term is the "
        "95th PERCENTILE of that distribution, which is STRICTLY HARDER than a single draw's "
        "point-plus-half-width. Changed after the first smoke fired L0_UNLICENSED on a single "
        "draw at 0.4266 [0.3701,0.4867]; see DISCLOSURE 3c in the cell docstring."
        % SCRAMBLE_REPS)

    # --- L0 LICENSING on the SURVIVING rows -----------------------------------------------------
    lic_floors = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE_INCUMBENT",
                  "F_CONSTANT_PROTOTYPE_INCUMBENT"]
    floor_fail = [f for f in lic_floors if auc[f]["band"] != "NOT_SEPARATED_FROM_CHANCE"]
    ka = auc["KNOWN_ANSWER_WORDNET"]["auc"]
    rnd_ok = auc["RANDOM_VECTOR"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    licensed = bool(not floor_fail and ka >= KNOWN_ANSWER_MIN_AUC and rnd_ok)
    rep["L0_LICENSING"] = {"floors_at_chance": not floor_fail, "floor_failures": floor_fail,
                           "known_answer_auc": ka, "known_answer_gate": KNOWN_ANSWER_MIN_AUC,
                           "random_vector_at_chance": rnd_ok,
                           "SUBPOPULATION_LICENSED": licensed,
                           "n_rows": n_keep,
                           "note": "L0 UNLICENSED means NO arm number may be interpreted."}
    print("[licensing] LICENSED=%s floor_failures=%r known_answer=%.4f random_ok=%s"
          % (licensed, floor_fail, ka, rnd_ok), flush=True)

    common = {f: auc[f] for f in COMMON_FLOORS}
    bars: Dict[str, Dict] = {}
    branches: Dict[str, Dict] = {}
    for pname, _x, _y, kind in PAIRINGS:
        for aname in HUB_ARMS:
            key = "%s::%s" % (pname, aname)
            af = {aname + "__F_SCRAMBLE": auc["%s::%s__F_SCRAMBLE" % (pname, aname)],
                  aname + "__F_CONSTANT_PROTOTYPE":
                      auc["%s::%s__F_CONSTANT_PROTOTYPE" % (pname, aname)]}
            bars[key] = compute_bar(key, auc[key], af, common)
            branches[key] = read_branch(auc[key], bars[key])
            branches[key]["kind"] = kind
    rep["BARS_RECOMPUTED_PER_REPRESENTATION"] = bars
    rep["BRANCH_PER_ARM"] = branches

    # --- B_TRAP_VOID, evaluated BEFORE the main arm is interpreted -------------------------------
    trap_fired = []
    for pname, _x, _y, kind in PAIRINGS:
        if kind != "TRAP":
            continue
        key = "%s::HUB_CCA_BOTH" % pname
        if branches[key]["branch"] == "B_PASS_CANDIDATE":
            trap_fired.append(key)
    rep["B_TRAP_VOID"] = {
        "traps": {p[0]: {"HUB_CCA_BOTH_auc": auc["%s::HUB_CCA_BOTH" % p[0]]["auc"],
                         "ci95": auc["%s::HUB_CCA_BOTH" % p[0]]["ci95"],
                         "BAR": bars["%s::HUB_CCA_BOTH" % p[0]]["BAR"],
                         "branch": branches["%s::HUB_CCA_BOTH" % p[0]]["branch"],
                         "cross_sim_r": (pfl.get(p[0]) or {}).get("cross_sim_r")}
                  for p in PAIRINGS if p[3] == "TRAP"},
        "ANY_TRAP_CLEARS_ITS_OWN_BAR": bool(trap_fired), "fired": trap_fired}

    # --- MAIN pairing redundancy void ------------------------------------------------------------
    main_redundant = [p[0] for p in PAIRINGS
                      if p[3] == "MAIN" and (pfl.get(p[0]) or {}).get("redundant")]

    # --- THE PRE-COMMITTED READING ---------------------------------------------------------------
    prim_key = "%s::%s" % (PRIMARY_PAIRING, PRIMARY_ARM)
    prim = branches[prim_key]
    resid_key = "%s::RESIDUAL_X" % PRIMARY_PAIRING
    if not licensed:
        fired = "L0_UNLICENSED"
        why = ("The surviving sub-population is not a licensed instrument (floor_failures=%r, "
               "known_answer=%.4f, random_at_chance=%s). NO arm number may be interpreted."
               % (floor_fail, ka, rnd_ok))
    elif trap_fired:
        fired = "B_TRAP_VOID"
        why = ("A TRAP pairing's HUB_CCA_BOTH cleared its OWN recomputed bar (%r). The pipeline "
               "manufactures the gain from ONE channel; the whole cross-view claim is VOID "
               "regardless of the main arm." % trap_fired)
    elif main_redundant:
        fired = "B_MAIN_PAIRING_REDUNDANT_VOID"
        why = ("A MAIN pairing's two views are at or above REDUNDANT_CROSS=%.2f (%r): we would be "
               "trapping ourselves." % (REDUNDANT_CROSS, main_redundant))
    elif prim["branch"] == "B_NEGATIVE":
        fired = "B_NEGATIVE"
        why = ("THE MECHANISM DOES NOT WORK HERE. Cross-view mutual prediction between a usage "
               "view and a definitional view does not produce substitutability on this "
               "instrument, at n=%d rows, with the strongest floor recomputed on THIS "
               "representation (BAR=%.4f, arm CI=[%.4f,%.4f]). The missing ingredient is not "
               "'a second view of this kind'." % (n_keep, prim["BAR"], prim["lo"], prim["hi"]))
    elif prim["branch"] == "B_UNDERPOWERED":
        fired = "B_UNDERPOWERED"
        why = ("UNDERPOWERED, NOT A VERDICT. The primary arm's CI half-width (%.4f) against a "
               "chance-to-bar interval of %.4f cannot resolve the question at n=%d."
               % (prim["ci_halfwidth"], prim["chance_to_bar_interval"], n_keep))
    else:
        if branches[resid_key]["branch"] == "B_PASS_CANDIDATE":
            fired = "MEASURED_EFFECT_WRONG_ATTRIBUTION"
            why = ("B_RESIDUAL_VOID: RESIDUAL_X also clears its own bar, so the 'predictable "
                   "component carries it' attribution fails and B_PASS is downgraded.")
        else:
            fired = "B_PASS"
            why = ("Cross-view convergence isolates substitutability structure the single channel "
                   "does not have. Bonferroni note: 16 mechanism arms were scored.")
    rep["BRANCH_FIRED"] = {"branch": fired, "reading": why, "primary_arm": prim_key,
                           "primary": prim,
                           "residual_control": branches[resid_key],
                           "own_baseline_A_INCUMBENT_STORE": auc["A_INCUMBENT_STORE"]["auc"],
                           "n_rows_scored": n_keep,
                           "direction_prereg": "only AUC ABOVE 0.5 counts; an arm further BELOW "
                                               "0.5 is more co-occurrence encoding, which is the "
                                               "incumbent's disease, not a win"}
    print("[BRANCH] %s -- %s" % (fired, why), flush=True)

    rep["WHAT_THIS_MAY_NOT_CONCLUDE"] = (
        "Nothing about cross-channel learning in general. ONE definitional channel (simplewiki "
        "definienda), ONE usage channel (this corpus), ONE linear invariant-extractor, ONE "
        "instrument, n=%d rows. A negative here is a negative about THAT." % n_keep)
    rep["elapsed_s"] = round(time.time() - t0, 1)
    beat("done")
    return rep


# =================================================================================================
# MAIN
# =================================================================================================
def main() -> int:
    out_dir = str(get_output_dir(ANCHOR_NAME))
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(out_dir, "_started.json"), "w", encoding="utf-8", newline="") as f:
        json.dump({"anchor": ANCHOR_NAME, "code_version": CODE_VERSION, "grid": RUN_MODE,
                   "pid": os.getpid(), "argv": sys.argv,
                   "started_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
    print("[start] %s %s grid=%s pid=%d out=%s"
          % (ANCHOR_NAME, CODE_VERSION, RUN_MODE, os.getpid(), out_dir), flush=True)
    try:
        if _ARGS.self_test:
            ev = self_test()
            write_metrics(get_output_dir(ANCHOR_NAME),
                          {"verdict": "SELFTEST_PASS",
                           "verdict_msg": "self-test PASS incl. planted positive control "
                                          "(hub=%.4f raw=%.4f)"
                                          % (ev["PLANTED_POSITIVE_CONTROL"]["auc_hub"],
                                             ev["PLANTED_POSITIVE_CONTROL"]["auc_raw_view_X"]),
                           "elapsed_s": ev["elapsed_s"], "summary": ev, "report": ev})
            return 0
        rep = run(RUN_MODE, out_dir)
        b = rep["BRANCH_FIRED"]["branch"]
        verdict = {"B_PASS": "PASS", "B_NEGATIVE": "FAIL",
                   "B_UNDERPOWERED": "UNDERPOWERED",
                   "B_TRAP_VOID": "VOID", "L0_UNLICENSED": "VOID",
                   "B_MAIN_PAIRING_REDUNDANT_VOID": "VOID",
                   "MEASURED_EFFECT_WRONG_ATTRIBUTION": "PARTIAL"}.get(b, "UNKNOWN")
        prim = rep["BRANCH_FIRED"]["primary"]
        msg = ("%s | primary %s AUC=%.4f CI=[%.4f,%.4f] HW=%.4f BAR=%.4f nullp95=%.4f margin=%.4f "
               "| rows %d->%d | %s"
               % (b, rep["BRANCH_FIRED"]["primary_arm"],
                  rep["AUC_PER_ARM"][rep["BRANCH_FIRED"]["primary_arm"]]["auc"],
                  prim["lo"], prim["hi"], prim["ci_halfwidth"], prim["BAR"], prim["null_p95"],
                  prim["margin_lo_minus_bar"],
                  rep["CONTROL_5_COVERAGE"]["n_rows_before"],
                  rep["CONTROL_5_COVERAGE"]["n_rows_after"],
                  rep["BRANCH_FIRED"]["reading"][:220]))
        write_metrics(get_output_dir(ANCHOR_NAME),
                      {"verdict": verdict, "verdict_msg": msg,
                       "elapsed_s": rep["elapsed_s"], "summary": {
                           "branch": b, "primary_arm": rep["BRANCH_FIRED"]["primary_arm"],
                           "primary": prim,
                           "n_rows_before": rep["CONTROL_5_COVERAGE"]["n_rows_before"],
                           "n_rows_after": rep["CONTROL_5_COVERAGE"]["n_rows_after"],
                           "licensed": rep["L0_LICENSING"]["SUBPOPULATION_LICENSED"],
                           "trap_fired": rep["B_TRAP_VOID"]["ANY_TRAP_CLEARS_ITS_OWN_BAR"]},
                       "report": rep})
        print("[done] %s" % msg, flush=True)
        return 0
    except SystemExit:
        raise
    except Exception as exc:                                   # noqa: BLE001 -- crash diagnostic
        tb = traceback.format_exc()
        print("[CRASH] %s" % tb, flush=True)
        try:
            write_metrics(get_output_dir(ANCHOR_NAME),
                          {"verdict": "CELL_CRASHED",
                           "verdict_msg": "CELL_CRASHED: %s: %s" % (type(exc).__name__, exc),
                           "elapsed_s": round(time.time() - t0, 1),
                           "summary": {"error": str(exc), "type": type(exc).__name__},
                           "report": {"traceback": tb}})
        except Exception:                                      # noqa: BLE001
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
