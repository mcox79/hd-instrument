"""distributional_meaning_channel -- the LIVE organ that turns the reading loop's separable
co-occurrence store into a taught substitutability read-out.

WHAT THIS ORGAN IS. `hdlab.reading_grounding_loop.ConceptSpace` now keeps a DEFAULT-OFF separable
co-occurrence store (`observe_context_counts` / `all_context_counts`, ROUTE B). This organ consumes
that store OFFLINE and produces a per-lemma distributional embedding plus a taught direction, so that
`substitutability(word_a, word_b)` answers "could a fluent reader swap one of these words for the
other?" -- higher is more substitutable. The signal is LABEL-FREE: it never touches WordNet, the gold
labels, or the benchmark. It is distilled from a supplied perceptual+affective TEACHER (the grounded
hub) across arbitrary word pairs; the distributional space amplifies that weak teacher.

This is the live-organ form of the SOLVED proof
  notes/problems/the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by/SOLVED.md
  experiments/exp_distributional_channel_store_representation_v1.py  (arm B_EXPLICIT_STORE)
  experiments/exp_crossmodal_distillation_substitutability_v1.py     (the landed 0.8388 distillation)
The PPMI+SVD math and the distillation regression are ported byte-for-byte from those cells so the
organ reproduces their consolidated space (asserted against the landed phi in the witness).

------------------------------------------------------------------------------------------------
BRAIN-FOUNDATIONAL LABELLING (which structure, and are we replicating it or substituting something?)
------------------------------------------------------------------------------------------------
PINNED-BY-EVIDENCE (we are replicating a described neural operation):
  * SEPARABLE STORE == hippocampal pattern separation. The reading loop's superposed d=256 `_sums`
    bundle blurs per-word counts once a lemma has >~d distinct neighbours; keeping the counts
    SEPARABLE (one Counter per lemma) is the pattern-separated store the hippocampus is thought to
    provide, and it is what makes the counts recoverable at all (proven in the store-representation
    cell: only arm B clears the floor).
  * OFFLINE PPMI+SVD == complementary-learning-systems slow consolidation. Neocortex slowly extracts
    distributional structure into a semantic manifold; PPMI+SVD is a standard model of that
    extraction. It is run OFFLINE (consolidation is slow relative to reading), never live.
  * DISTILLATION == anterior-temporal-lobe hub cross-modal agreement (Patterson 2007; Lambon Ralph
    2017). The ATL hub shapes each spoke by agreement across modalities; here the distributional
    spoke is shaped to agree with the perceptual+affective (grounded) spoke over arbitrary pairs.
  * SUPPLIED GROUNDED TEACHER == the FOUNDATION pivot (USER 2026-07-14): the grounded norms are an
    external, fully-built, static asset used as foundation, not learned at inference. NO LLM.

OUR-INVENTION-UNDER-TEST (we chose this; it is not pinned to a recording):
  * The DISTILLATION EXTRACTOR itself -- learning the distributional direction that reproduces
    grounded similarity by ridge regression over arbitrary pairs -- is our construction. The brain's
    binding of a distributional spoke to a perceptual spoke is not recorded at this resolution.
  * The multi-spoke grounded hub set (which 11 sensorimotor + 3 affect dimensions) is a convenience
    choice of teacher, not a pinned parcellation.
  * The INDUCTIVE fit-once-apply-anywhere read-out (see TRANSDUCTIVITY, below) is our design; the
    landed cell orients transductively. The witness measures whether the inductive form reproduces
    the number and this docstring is updated from that measurement, not from prediction.

------------------------------------------------------------------------------------------------
TRANSDUCTIVITY (the design risk this organ had to resolve -- RESOLVED BY MEASUREMENT, recorded here).
------------------------------------------------------------------------------------------------
MEASURED FINDING (witness_distributional_meaning_channel.py + diag_orientation.py, 2026-08-24):
the distilled DIRECTION w is inductive and reproduces (phi matches the landed space to 3e-4), BUT
the single orientation BIT is IRREDUCIBLY TRANSDUCTIVE for this task. A fit-once global sign fixed on
the fitting pairs (+1 by least-squares) scores the instrument at AUC 0.163 -- the exact sign-inverted
image of the landed 0.839. Every label-free proxy batch drawn from the vocabulary (random pairs, and
the top 1/5/10% most grounded-similar pairs) yields the SAME wrong +1 sign. Only orienting on the
PRESENTED candidate batch -- correlating the distilled axis against the grounded teacher's DIRECT
similarity on those pairs -- recovers the -1 that scores 0.839.

WHY: the instrument's candidate pairs are a MATCHED co-occurrence design (substitutable P vs
co-occurring-but-not S, matched on co-occurrence). On arbitrary pairs w weakly tracks grounded
similarity (corr +0.14); on the matched candidates the co-occurrence structure dominates the
phi-products and w tracks the SYNTAGMATIC signal instead (corr -0.05), scoring co-occurring S pairs
ABOVE substitutable P pairs (mean raw S=0.151 > P=0.016). The correct paradigmatic orientation is -w,
and that -1 is a property of the candidate population, not discoverable from the teacher on generic
vocabulary. A per-pair contrast (grounded-direct minus distilled-proxy) only interpolates 0.55 -> 0.84
toward -w and never exceeds it, so there is no free inductive per-pair orientation.

CONSEQUENCE FOR THE API: `substitutability_batch(pairs)` is the FAITHFUL read-out -- it orients the
one sign bit over the presented batch against the grounded teacher (label-free; never touches gold)
and reproduces the landed number. The single-pair `substitutability(a, b)` needs a reference batch to
orient; called without one it falls back to the fixed global sign, which is DOCUMENTED to invert on
matched-design candidate populations. The orientation remains LABEL-FREE (grounded norms only); it is
batch-transductive, not gold-transductive.

Glass-box, CPU-only, single-threaded pins at top, deterministic (fixed seed), NO LLM. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import csv
import io
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import svds

# ------------------------------------------------------------------------------------------------
# CONSTANTS -- ported verbatim from exp_crossmodal_distillation_substitutability_v1 so the organ's
# consolidated space and distilled direction reproduce the landed cell.
# ------------------------------------------------------------------------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # hdlab/ parent == repo root
_GDIR_DEFAULT = os.path.join(_REPO, "data", "grounding_testbed")

# grounded TEACHER hub columns (11 Lancaster sensorimotor means + 3 Warriner affect dims).
SENS = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
        "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]
AFF = ["V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"]
_LANC_NAME = "Lancaster_sensorimotor_norms_for_39707_words.csv"
_WARR_NAME = "Ratings_Warriner_et_al.csv"

MASTER_SEED = 20260824      # == X.MASTER_SEED
SVD_K = 100                 # == X.SVD_K
N_DISTILL_PAIRS = 8000      # == X.N_DISTILL_PAIRS
RIDGE = 1.0                 # == X.RIDGE
_SVD_SEED_OFFSET = 7100     # svds random_state == MASTER_SEED + 7100 (reproduces landed phi)
_DISTILL_SEED_OFFSET = 200  # fit seed == MASTER_SEED + 200 (== landed cell seed0)


# ================================================================================================
# math primitives -- byte-for-byte ports
# ================================================================================================
def l2n(A: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalize (== X.l2n)."""
    n = np.linalg.norm(A, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return A / n


def _count_matrix(words: Sequence[str], counts: Dict[str, "Counter[str]"],
                  vocab: Dict[str, int]) -> sp.csr_matrix:
    """Sparse [n_words, n_vocab] raw co-occurrence count matrix (== store cell true_count_matrix)."""
    rows: List[int] = []
    cols: List[int] = []
    data: List[float] = []
    for r, w in enumerate(words):
        for c, n in counts[w].items():
            rows.append(r); cols.append(vocab[c]); data.append(float(n))
    return sp.csr_matrix((data, (rows, cols)), shape=(len(words), len(vocab)), dtype=np.float64)


def ppmi_svd(M: sp.csr_matrix, svd_k: int = SVD_K, seed: int = MASTER_SEED) -> np.ndarray:
    """PPMI reweight then truncated SVD, L2-normalized rows. EXACT port of the store cell's ppmi_svd
    (which reproduces the landed cell's phi to ~1e-6 absmax abs-diff). Deterministic: svds
    random_state is fixed. Returns the per-lemma distributional embedding phi [n_words, svd_k]."""
    Mc = M.tocoo()
    rsum = np.asarray(M.sum(1)).ravel()
    csum = np.asarray(M.sum(0)).ravel()
    tot = float(M.sum())
    rsum[rsum < 1e-12] = 1
    csum[csum < 1e-12] = 1
    pmi = np.log(Mc.data / (rsum[Mc.row] * csum[Mc.col] / tot))
    P = sp.csr_matrix((np.maximum(pmi, 0.0), (Mc.row, Mc.col)), shape=M.shape)
    P.eliminate_zeros()
    U, S, _ = svds(P.asfptype(), k=svd_k, random_state=seed + _SVD_SEED_OFFSET)
    o = np.argsort(-S)
    return l2n(U[:, o] * np.sqrt(np.maximum(S[o], 0.0))[None, :])


# ================================================================================================
# grounded TEACHER hub -- ports X.load_norms / X.zblock / the GROUNDED branch of X.build_hubs
# ================================================================================================
def _load_norms(path: str, cols: Sequence[str], delim: str = ",") -> Dict[str, np.ndarray]:
    d: Dict[str, np.ndarray] = {}
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter=delim):
            w = (row.get("Word") or "").strip().lower()
            if w:
                try:
                    d[w] = np.array([float(row[c]) for c in cols], float)
                except (KeyError, ValueError, TypeError):
                    pass
    return d


def _zblock(nd: Dict[str, np.ndarray], nk: int, words: Sequence[str]) -> Tuple[np.ndarray, np.ndarray]:
    """z-score the covered rows of a norm block over the covered population; zero-fill the rest.
    (== X.zblock)."""
    raw = np.zeros((len(words), nk))
    c = np.zeros(len(words), bool)
    for i, w in enumerate(words):
        v = nd.get(w.lower())
        if v is not None:
            raw[i] = v
            c[i] = True
    if c.any():
        mu = raw[c].mean(0); sd = raw[c].std(0); sd[sd < 1e-9] = 1.0
        raw[c] = (raw[c] - mu) / sd
    raw[~c] = 0.0
    return raw, c


def build_grounded_hub(words: Sequence[str], grounding_dir: Optional[str] = None
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """The perceptual+affective TEACHER: z-scored [11 Lancaster sensorimotor + 3 Warriner affect]
    per lemma, L2-normalized; plus a coverage mask (True where BOTH norm sources cover the lemma).
    == the GROUNDED entry of X.build_hubs. Returns (hub [n_words, 14], cov_mask [n_words])."""
    gdir = grounding_dir or _GDIR_DEFAULT
    lanc = _load_norms(os.path.join(gdir, _LANC_NAME), SENS)
    warr = _load_norms(os.path.join(gdir, _WARR_NAME), AFF)
    sm, c_sm = _zblock(lanc, len(SENS), words)
    af, c_af = _zblock(warr, len(AFF), words)
    hub = l2n(np.concatenate([sm, af], 1))
    cov = c_sm & c_af
    return hub, cov


def hub_sim(hub: np.ndarray, ia: np.ndarray, ib: np.ndarray) -> np.ndarray:
    """Teacher similarity for pairs (ia, ib): scalar-hub product, else cosine. == X.hub_sim."""
    if hub.shape[1] == 1:
        return hub[ia, 0] * hub[ib, 0]
    hn = l2n(hub)
    return np.einsum("ij,ij->i", hn[ia], hn[ib])


# ================================================================================================
# distillation -- port of X.distill_direction, made inductive (query-independent fit + fixed sign)
# ================================================================================================
def fit_direction(phi: np.ndarray, hub: np.ndarray, cov_idx: np.ndarray,
                  seed: int, n_pairs: int = N_DISTILL_PAIRS, ridge: float = RIDGE
                  ) -> Tuple[np.ndarray, float]:
    """Learn w minimizing ||X_arb w - hubsim_arb|| over n_pairs arbitrary pairs sampled from cov_idx
    (== X.distill_direction), and fix the orientation SIGN on those same fitting pairs (inductive:
    never reads the query). Returns (w [svd_k], sign in {+1, -1}). Sign is +1 by least-squares
    construction whenever the teacher is informative; it is computed, not assumed."""
    rng = np.random.default_rng(seed)
    ii = rng.choice(cov_idx, size=(n_pairs, 2))
    ii = ii[ii[:, 0] != ii[:, 1]]
    Xa = phi[ii[:, 0]] * phi[ii[:, 1]]
    ga = hub_sim(hub, ii[:, 0], ii[:, 1])
    ga = (ga - ga.mean()) / (ga.std() + 1e-9)
    A = Xa.T @ Xa + ridge * np.eye(Xa.shape[1])
    w = np.linalg.solve(A, Xa.T @ ga)
    pred = Xa @ w
    denom = pred.std() * ga.std()
    sign = 1.0 if (denom < 1e-12 or np.corrcoef(pred, ga)[0, 1] >= 0) else -1.0
    return w, sign


# ================================================================================================
# the organ
# ================================================================================================
class DistributionalMeaningChannel:
    """Consolidated distributional space + taught direction + grounded teacher hub.

    Faithful read-out: substitutability_batch(pairs) -- orients the one sign bit over the presented
    batch against the grounded teacher (label-free) and reproduces the landed number. Single-pair
    substitutability(a, b) needs a reference batch to orient (see the module TRANSDUCTIVITY note)."""

    def __init__(self, words: List[str], row_idx: Dict[str, int], phi: np.ndarray,
                 freq: np.ndarray, w: np.ndarray, global_sign: float,
                 hub: np.ndarray, hub_cov: np.ndarray, fit_pool_size: int) -> None:
        self.words = words
        self.row_idx = row_idx
        self.phi = phi
        self.freq = freq
        self.w = w
        self.global_sign = float(global_sign)   # inductive sign on the fitting pairs (fallback only)
        self.hub = hub                          # grounded teacher, indexed by row_idx (for orienting)
        self.hub_cov = hub_cov
        self.fit_pool_size = int(fit_pool_size)
        self.n_words = len(words)
        self.n_dim = int(phi.shape[1])

    def _index(self, word: str) -> Optional[int]:
        i = self.row_idx.get(word)
        if i is None:
            i = self.row_idx.get(word.lower())
        return i

    def _raw(self, ia: np.ndarray, ib: np.ndarray) -> np.ndarray:
        return (self.phi[ia] * self.phi[ib]) @ self.w

    def substitutability_batch(self, pairs: Sequence[Tuple[str, str]]) -> List[Optional[float]]:
        """THE faithful read-out. Higher == more substitutable. None for any pair where either word
        is OOV of the consolidated space. Orients the single sign bit over the in-vocabulary subset of
        `pairs` by correlating the distilled axis against the grounded teacher's DIRECT similarity on
        those pairs (LABEL-FREE -- grounded norms only, never gold). Reproduces the landed cell when
        `pairs` is the licensed instrument."""
        idx = [(self._index(a), self._index(b)) for (a, b) in pairs]
        covered = [k for k, (ia, ib) in enumerate(idx) if ia is not None and ib is not None]
        out: List[Optional[float]] = [None] * len(pairs)
        if not covered:
            return out
        ia = np.array([idx[k][0] for k in covered])
        ib = np.array([idx[k][1] for k in covered])
        raw = self._raw(ia, ib)
        sign = self._orient(raw, ia, ib)
        oriented = sign * raw
        for j, k in enumerate(covered):
            out[k] = float(oriented[j])
        return out

    def _orient(self, raw: np.ndarray, ia: np.ndarray, ib: np.ndarray) -> float:
        """Sign that makes the distilled axis agree with the grounded teacher's DIRECT similarity on
        the presented pairs; falls back to the fixed global sign if the batch cannot orient (<2 pairs
        or a degenerate correlation)."""
        if raw.size < 2:
            return self.global_sign
        href = hub_sim(self.hub, ia, ib)
        if raw.std() < 1e-12 or href.std() < 1e-12:
            return self.global_sign
        return 1.0 if np.corrcoef(raw, href)[0, 1] >= 0 else -1.0

    def substitutability(self, word_a: str, word_b: str,
                         reference_pairs: Optional[Sequence[Tuple[str, str]]] = None) -> Optional[float]:
        """Single-pair read-out. Higher == more substitutable. None if either word is OOV.

        Orientation is batch-transductive (see the module TRANSDUCTIVITY note): pass `reference_pairs`
        -- a representative batch of candidate pairs the query is drawn from -- to orient faithfully.
        Called WITHOUT a reference batch it uses the fixed global inductive sign, which is DOCUMENTED
        to invert on matched-co-occurrence candidate populations; the value is returned but the sign
        is not trustworthy in isolation."""
        ia = self._index(word_a)
        ib = self._index(word_b)
        if ia is None or ib is None:
            return None
        if reference_pairs is not None:
            scored = self.substitutability_batch(list(reference_pairs) + [(word_a, word_b)])
            return scored[-1]
        return float(self.global_sign * ((self.phi[ia] * self.phi[ib]) @ self.w))


def build(context_counts: Dict[str, "Counter[str]"], *,
          grounding_dir: Optional[str] = None,
          svd_k: int = SVD_K, ridge: float = RIDGE, n_distill_pairs: int = N_DISTILL_PAIRS,
          seed: int = MASTER_SEED, exclude_lemmas: Optional[set] = None,
          hub_override: Optional[Tuple[np.ndarray, np.ndarray]] = None
          ) -> DistributionalMeaningChannel:
    """OFFLINE consolidation + distillation from the reading loop's separable co-occurrence store.

    context_counts : Dict[lemma -> Counter(context_lemma -> count)] == ConceptSpace.all_context_counts().
    grounding_dir  : dir holding the Lancaster + Warriner norm CSVs (default data/grounding_testbed).
    exclude_lemmas : lemmas to keep OUT of the distillation fitting pool (e.g. an evaluation set, to
                     make the direction provably disjoint from it). Default None == fit over all
                     hub-covered lemmas (a general, query-independent read-out).
    hub_override   : (hub_matrix, cov_mask) to substitute a different teacher (used for the info-free
                     random-hub twin in the witness). Default None == the grounded teacher.

    Deterministic (fixed seed). Steps: (1) count matrix over the store's lemmas, (2) PPMI+SVD -> phi,
    (3) grounded teacher hub, (4) inductive distilled direction + fixed sign. Returns the organ."""
    words = list(context_counts.keys())
    if not words:
        raise ValueError("empty context_counts: nothing to consolidate")
    vocab: Dict[str, int] = {}
    for w in words:
        for c in context_counts[w]:
            vocab.setdefault(c, len(vocab))
    M = _count_matrix(words, context_counts, vocab)
    freq = np.asarray(M.sum(1)).ravel()
    phi = ppmi_svd(M, svd_k=svd_k, seed=seed)
    row_idx = {w: i for i, w in enumerate(words)}

    if hub_override is not None:
        hub, cov = hub_override
    else:
        hub, cov = build_grounded_hub(words, grounding_dir)

    excl = exclude_lemmas or set()
    cov_idx = np.array([i for i in range(len(words)) if cov[i] and words[i] not in excl])
    if cov_idx.size < 2:
        raise ValueError("distillation needs >=2 hub-covered lemmas outside exclude_lemmas; got %d"
                         % int(cov_idx.size))
    w_dir, sign = fit_direction(phi, hub, cov_idx, seed + _DISTILL_SEED_OFFSET,
                                n_pairs=n_distill_pairs, ridge=ridge)
    return DistributionalMeaningChannel(words, row_idx, phi, freq, w_dir, sign, hub, cov,
                                        int(cov_idx.size))


# ================================================================================================
# self-test -- data-free formula checks (no store, no CSVs). Full end-to-end validation lives in
# the witness (witness_distributional_meaning_channel.py), which drives the live store path.
# ================================================================================================
def self_test() -> Dict:
    ev: Dict[str, object] = {}
    # l2n normalizes nonzero rows to unit length and leaves zero rows at zero.
    A = np.array([[3.0, 4.0], [0.0, 0.0]])
    An = l2n(A)
    assert abs(np.linalg.norm(An[0]) - 1.0) < 1e-9 and np.allclose(An[1], 0.0), "l2n"
    ev["l2n_ok"] = True

    # ppmi_svd on a small block-structured count matrix returns finite unit-norm rows [n, k].
    rng = np.random.default_rng(0)
    blocks = np.repeat(np.eye(4), 6, axis=0) * rng.integers(1, 5, (24, 4))
    M = sp.csr_matrix(blocks.astype(np.float64))
    phi = ppmi_svd(M, svd_k=3, seed=0)
    assert phi.shape == (24, 3) and np.all(np.isfinite(phi)), "ppmi_svd shape/finite"
    norms = np.linalg.norm(phi, axis=1)          # l2n leaves sub-1e-12 rows unnormalized by design
    assert np.allclose(norms[norms > 1e-6], 1.0, atol=1e-6), "ppmi_svd unit rows"
    ev["ppmi_svd_ok"] = True

    # the distillation solve recovers a planted linear target over sampled phi-products (== the
    # flagship's distill_recovers_planted check).
    p = l2n(rng.standard_normal((200, 20)))
    wtrue = rng.standard_normal(20)
    ia = rng.integers(0, 200, 3000); ib = rng.integers(0, 200, 3000)
    Xa = p[ia] * p[ib]; ga = Xa @ wtrue
    w_hat = np.linalg.solve(Xa.T @ Xa + 1e-6 * np.eye(20), Xa.T @ ga)
    ev["distill_recovers_planted"] = float(np.corrcoef(w_hat, wtrue)[0, 1])
    assert ev["distill_recovers_planted"] > 0.99, "distillation must recover a planted target"

    # hub_sim: scalar-hub product branch and multi-dim cosine branch.
    hs1 = hub_sim(np.array([[2.0], [3.0], [4.0]]), np.array([0, 1]), np.array([1, 2]))
    assert np.allclose(hs1, [6.0, 12.0]), "hub_sim scalar branch"
    h2 = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    hs2 = hub_sim(h2, np.array([0, 0]), np.array([1, 2]))
    assert abs(hs2[0] - 1.0) < 1e-9 and abs(hs2[1]) < 1e-9, "hub_sim cosine branch"
    ev["hub_sim_ok"] = True

    # orientation flips a sign-inverted reference (the batch-transductive sign bit).
    ch = DistributionalMeaningChannel.__new__(DistributionalMeaningChannel)
    ch.global_sign = 1.0
    raw = np.array([1.0, 2, 3, 4]); href_ia = np.array([0, 1, 2, 3]); href_ib = np.array([0, 1, 2, 3])
    ch.hub = np.array([[4.0], [3.0], [2.0], [1.0]])   # scalar hub anti-ranked vs raw indices
    assert ch._orient(raw, href_ia, href_ib) == -1.0, "orientation must detect an inverted reference"
    ev["orientation_flips_inverted"] = True
    return ev


if __name__ == "__main__":
    print("[selftest] %r" % self_test())
