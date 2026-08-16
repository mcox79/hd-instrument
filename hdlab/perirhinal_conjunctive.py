"""hdlab/perirhinal_conjunctive.py -- SPARSE CONJUNCTIVE context coding (perirhinal-style).

DEFAULT-OFF. Importing this module changes NOTHING on the live path: it adds a new encoder that
DUCK-TYPES hdlab.reading_grounding_loop.StructuralEncoder, so it reaches the reader through the
ALREADY-EXISTING default-off plug point `process_sentence(encoder=...)`. No file on the live
import closure is edited. `reading_grounding_loop` does NOT import this module.

--------------------------------------------------------------------------------------------
WHAT PROBLEM THIS ADDRESSES (measured, not assumed)
--------------------------------------------------------------------------------------------
The live read-out profile is a BARE FLAT SUM of per-content-word bipolar symbol vectors with NO
key of any kind applied -- verified by runtime reconstruction, bit-exact, order-invariant
(scratch/wall2_premises.json, premise C). Its similarity metric is therefore LINEAR in how many
context words two profiles share. Items that share many features are exactly the items the
read-out confuses.

--------------------------------------------------------------------------------------------
BRAIN FIDELITY -- SAY WHICH PART IS PINNED AND WHICH IS OURS
--------------------------------------------------------------------------------------------
PINNED-BY-EVIDENCE (as ARCHITECTURE, not as an equation):
  * Perirhinal cortex is implicated in telling apart items that SHARE FEATURES, and medial
    temporal codes are SPARSE rather than dense.
OUR-INVENTION-BEING-TESTED (do NOT present as brain fidelity):
  * The CONJUNCTION OPERATOR is UNPINNED in the literature. Nothing specifies elementwise
    product over unordered pairs. That choice is ours.
  * The perirhinal FEATURE-AMBIGUITY account is CONTESTED and has real failed replications.
    Whichever way this measures, it is evidence about THIS operator on THIS task, not about
    whether the brain does this.
  * The sparsity level here is a swept parameter, not the pinned ~0.2% MTL figure (that figure
    belongs to the medial-temporal INDEX; this is a cortical-profile code).

--------------------------------------------------------------------------------------------
THE OPERATOR, AND THE IDENTITY THAT MAKES IT FREE
--------------------------------------------------------------------------------------------
For a target lemma L in a sentence, let w_1..w_m be the content-word tokens of the sentence with
every token whose lemma is L removed (the SAME masked token list the live encoder uses), and let
phi_w be the SAME hashlib-seeded bipolar symbol vector the live encoder uses. Then

    BAG (live)  S = sum_i phi_i                      -- "feature A occurred"
    PAIR (ours) P = sum_{i<j} phi_i * phi_j          -- "feature A AND feature B occurred"

and because phi_i is bipolar so phi_i * phi_i = 1 elementwise,

    P = (S * S - m) / 2          (elementwise; EXACT in integers, proven bit-exact in self-test)

So the conjunctive code is an elementwise QUADRATIC of the live bag, costing O(m*d) not
O(m^2*d) -- the same cost as the live encoder, and a strict ONE-VARIABLE swap of the metric.

HONEST SCOPE, stated up front so it cannot be spun later: at a SINGLE occurrence P carries no
information S does not, because it is a deterministic pointwise function of S. What changes is
(1) the METRIC -- similarity becomes superlinear in shared context, ~C(j,2)/C(m,2) instead of
~j/m for j shared words of m -- and (2) what survives ACROSS occurrences, since
sum_occ P(S_occ) is NOT a function of sum_occ S_occ. Claim (2) is the testable one.

MODES
  "pair"   P                     -- conjunctions INSTEAD of features (the strict perirhinal read)
  "hybrid" S + P                 -- features AND conjunctions (cortical units plus perirhinal
                                    units, which is what the anatomy actually has)
  "sparse" kwta(P, k_frac)       -- conjunctions, sparsified. TWO variables vs the live path
                                    (conjunction AND sparsity); diagnostic only, never a primary
                                    verdict.

KNOWN COVERAGE PROPERTY, disclosed because it is a potential confound: with m < 2 context words
P is exactly zero, so "pair" and "sparse" contribute nothing from a one-content-word context that
the live bag would still have contributed to. The encoder COUNTS these (`n_zero_out`) so the rate
is reported rather than discovered later.

ASCII-only. No external model, no learned weights, no LLM: a fixed hash codebook and arithmetic.
Run:  .venv/Scripts/python.exe -m hdlab.perirhinal_conjunctive
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from typing import Dict, List, Optional, Sequence

import numpy as np

from hdlab.grounding_acquisition_loop import content_words
from hdlab.reading_grounding_loop import CTX_D, normalize_lemma, symbol_vector

# DEFAULT-OFF module switch. Nothing in hdlab reads this; it exists so that "is the perirhinal
# organ on?" has ONE answer that a witness can assert, and so turning it on is a visible,
# separate decision after a verdict rather than an import side effect.
PERIRHINAL_CONJUNCTIVE: bool = os.environ.get("HD_PERIRHINAL_CONJUNCTIVE", "0") == "1"

MODES = ("pair", "hybrid", "sparse")
DEFAULT_K_FRAC = 0.10


# ------------------------------------------------------------------ the operator
def masked_content_tokens(sentence: str, target_lemma: str) -> List[str]:
    """The EXACT token list the live encoder sums over, reproduced.

    `context_vector_masked` filters `content_words(sentence)` by lemma, re-joins with spaces and
    hands the string back to `context_vector`, which calls `content_words` a SECOND time. Both
    steps are reproduced here rather than approximated; `_selftest_bag_matches_live` asserts the
    resulting bag is bit-identical to `context_vector_masked(..., graded=True)`."""
    kept = [w for w in content_words(sentence) if normalize_lemma(w) != target_lemma]
    return content_words(" ".join(kept))


def bag_vector(tokens: Sequence[str], d: int = CTX_D) -> np.ndarray:
    """S = sum_i phi_i over the masked content tokens (the live flat bag, graded)."""
    acc = np.zeros(d, dtype=np.float64)
    for w in tokens:
        acc += symbol_vector(w, d)
    return acc


def pair_conjunction(bag: np.ndarray, m: int) -> np.ndarray:
    """P = sum_{i<j} phi_i * phi_j = (S*S - m)/2, elementwise. Exact for bipolar phi."""
    if m < 2:
        return np.zeros_like(bag)
    return (bag * bag - float(m)) / 2.0


def kwta(vec: np.ndarray, k_frac: float = DEFAULT_K_FRAC) -> np.ndarray:
    """Deterministic k-winners-take-all by |value|; ties broken by ascending index.

    An all-zero input returns all zeros (it has no winners), so a dropped occurrence stays
    dropped rather than becoming an arbitrary sparse pattern."""
    d = vec.shape[0]
    k = max(1, int(round(k_frac * d)))
    if k >= d:
        return vec.copy()
    mag = np.abs(vec)
    if not np.any(mag > 0.0):
        return np.zeros_like(vec)
    order = np.lexsort((np.arange(d), -mag))       # primary -|v| desc, secondary index asc
    out = np.zeros_like(vec)
    keep = order[:k]
    out[keep] = vec[keep]
    return out


def conjunctive_context_vector_masked(sentence: str, target_lemma: str, d: int = CTX_D, *,
                                      mode: str = "pair",
                                      k_frac: float = DEFAULT_K_FRAC,
                                      symbol_fn=None) -> np.ndarray:
    """Drop-in replacement for `context_vector_masked` producing a conjunctive code.

    `symbol_fn` exists ONLY for the between-random-projection-draw control (a salted codebook);
    at `symbol_fn=None` the canonical `symbol_vector` is used and the bag is asserted bit-identical
    to the live function."""
    if mode not in MODES:
        raise ValueError("unknown mode %r; known=%r" % (mode, MODES))
    toks = masked_content_tokens(sentence, target_lemma)
    m = len(toks)
    if m == 0:
        return np.zeros(d, dtype=np.float64)
    if symbol_fn is None:
        S = bag_vector(toks, d)
    else:
        S = np.zeros(d, dtype=np.float64)
        for w in toks:
            S += symbol_fn(w)
    P = pair_conjunction(S, m)
    if mode == "pair":
        return P
    if mode == "hybrid":
        return S + P
    return kwta(P, k_frac)


class PerirhinalEncoder:
    """Duck-types `hdlab.reading_grounding_loop.StructuralEncoder` so it plugs into the reader's
    EXISTING default-off port: `process_sentence(state, sent, ..., encoder=PerirhinalEncoder())`.
    `structural_vector_masked` calls exactly `encoder.vector(sentence, target_lemma)`."""

    def __init__(self, d: int = CTX_D, mode: str = "pair", k_frac: float = DEFAULT_K_FRAC,
                 symbol_fn=None) -> None:
        if mode not in MODES:
            raise ValueError("unknown mode %r; known=%r" % (mode, MODES))
        self.d = int(d)
        self.mode = mode
        self.k_frac = float(k_frac)
        self.symbol_fn = symbol_fn
        self.n_encodings = 0
        self.n_zero_out = 0
        self.n_tokens_total = 0

    def vector(self, sentence: str, target_lemma: str) -> np.ndarray:
        v = conjunctive_context_vector_masked(sentence, target_lemma, self.d, mode=self.mode,
                                              k_frac=self.k_frac, symbol_fn=self.symbol_fn)
        self.n_encodings += 1
        self.n_tokens_total += len(masked_content_tokens(sentence, target_lemma))
        if not np.any(v != 0.0):
            self.n_zero_out += 1
        return v

    def stats(self) -> dict:
        return {
            "organ": "perirhinal_conjunctive",
            "mode": self.mode,
            "k_frac": self.k_frac if self.mode == "sparse" else None,
            "d": self.d,
            "n_encodings": self.n_encodings,
            "n_zero_out": self.n_zero_out,
            "frac_zero_out": (self.n_zero_out / self.n_encodings) if self.n_encodings else None,
            "mean_masked_tokens": ((self.n_tokens_total / self.n_encodings)
                                   if self.n_encodings else None),
            "default_switch_PERIRHINAL_CONJUNCTIVE": PERIRHINAL_CONJUNCTIVE,
        }


# ===================================================================== self-tests (all can fail)
def _selftest_identity_matches_explicit_double_loop() -> dict:
    """P = (S*S - m)/2 must equal the literal sum over unordered pairs, BIT-EXACTLY."""
    rng = np.random.default_rng(0)
    worst = 0.0
    for trial in range(25):
        m = int(rng.integers(0, 12))
        d = 64
        phis = [rng.choice([-1.0, 1.0], size=d) for _ in range(m)]
        S = np.sum(phis, axis=0) if m else np.zeros(d)
        explicit = np.zeros(d)
        for i in range(m):
            for j in range(i + 1, m):
                explicit += phis[i] * phis[j]
        got = pair_conjunction(S, m)
        assert np.array_equal(got, explicit), (
            "pair identity broken at m=%d: max|diff|=%g" % (m, float(np.max(np.abs(got - explicit)))))
        worst = max(worst, float(np.max(np.abs(got - explicit))))
    return {"max_abs_diff_vs_explicit_double_loop": worst, "ok": True}


def _selftest_bag_matches_live() -> dict:
    """The bag this module sums is BIT-IDENTICAL to the live `context_vector_masked` graded
    output. Without this, the conjunctive arm would be a different vector space, not a swap."""
    from hdlab.reading_grounding_loop import context_vector_masked
    sents = [
        "Blood travels through the artery and reaches the beating heart.",
        "The lantern flickered in the storm beside the quiet harbour wall.",
        "She read verses from a book of poems at the library.",
    ]
    checked = 0
    for s in sents:
        for lem in ("artery", "blood", "lantern", "storm", "book", "verse", "zibbo"):
            toks = masked_content_tokens(s, lem)
            mine = bag_vector(toks, CTX_D)
            live = context_vector_masked(s, lem, graded=True)
            assert np.array_equal(mine, live), (
                "masked bag diverged from live context_vector_masked on %r/%r" % (s[:24], lem))
            checked += 1
    return {"n_checked": checked, "ok": True}


def _selftest_conjunction_is_superlinear_in_overlap() -> dict:
    """THE MECHANISM CLAIM, and it CAN FAIL. For two contexts of m words sharing j, the flat bag's
    cosine tracks j/m while the pair code's tracks C(j,2)/C(m,2). So at PARTIAL overlap the
    conjunctive similarity must be STRICTLY LOWER, and at FULL overlap the two must be EQUAL.
    A code that does not do this is not sharpening anything."""
    rng = np.random.default_rng(11)
    d, m = 4096, 10
    rows = []
    ok = True
    for j in (2, 4, 6, 8, 10):
        bag_cos, pair_cos = [], []
        for _ in range(20):
            shared = [rng.choice([-1.0, 1.0], size=d) for _ in range(j)]
            a = shared + [rng.choice([-1.0, 1.0], size=d) for _ in range(m - j)]
            b = shared + [rng.choice([-1.0, 1.0], size=d) for _ in range(m - j)]
            Sa, Sb = np.sum(a, axis=0), np.sum(b, axis=0)
            Pa, Pb = pair_conjunction(Sa, m), pair_conjunction(Sb, m)
            c = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12))
            bag_cos.append(c(Sa, Sb))
            pair_cos.append(c(Pa, Pb))
        mb, mp = float(np.mean(bag_cos)), float(np.mean(pair_cos))
        rows.append({"j_shared_of_10": j, "bag_cos": round(mb, 4), "pair_cos": round(mp, 4)})
        if j < m and not (mp < mb - 1e-3):
            ok = False
        if j == m and not (abs(mp - 1.0) < 1e-6 and abs(mb - 1.0) < 1e-6):
            ok = False
    assert ok, "conjunctive code is NOT superlinear in overlap: %r" % (rows,)
    return {"rows": rows, "ok": ok}


def _selftest_kwta_is_sparse_and_deterministic() -> dict:
    rng = np.random.default_rng(3)
    v = rng.normal(size=256)
    a, b = kwta(v, 0.10), kwta(v, 0.10)
    assert np.array_equal(a, b), "kwta is not deterministic"
    assert int(np.count_nonzero(a)) <= 26, "kwta kept more than k entries"
    assert int(np.count_nonzero(a)) >= 25, "kwta kept fewer than k entries"
    z = kwta(np.zeros(256), 0.10)
    assert not np.any(z != 0.0), "kwta invented winners from an all-zero input"
    # the kept set must be the true top-k by magnitude
    top = set(np.argsort(-np.abs(v), kind="stable")[:26].tolist())
    assert set(np.flatnonzero(a).tolist()) <= top, "kwta kept a non-top-k index"
    return {"k_kept": int(np.count_nonzero(a)), "ok": True}


def _selftest_hybrid_is_exactly_bag_plus_pair() -> dict:
    s = "Blood travels through the artery and reaches the beating heart."
    toks = masked_content_tokens(s, "artery")
    S = bag_vector(toks, CTX_D)
    P = pair_conjunction(S, len(toks))
    got = conjunctive_context_vector_masked(s, "artery", CTX_D, mode="hybrid")
    assert np.array_equal(got, S + P), "hybrid mode is not bag+pair"
    return {"n_tokens": len(toks), "ok": True}


def _selftest_default_is_off_and_reader_is_unchanged() -> dict:
    """WIRE-WITHOUT-CHANGING-THE-DEFAULT witness. Importing this module must leave the reader's
    default path BIT-IDENTICAL, and the encoder must reach the reader only when explicitly
    passed."""
    import hdlab.reading_grounding_loop as RGL
    from hdlab.hd_fact_store import HDFactStore

    assert PERIRHINAL_CONJUNCTIVE is False or os.environ.get("HD_PERIRHINAL_CONJUNCTIVE") == "1", \
        "the perirhinal switch defaulted ON"
    sent = "The zibbo flickered by the lantern in the storm."

    def _run(encoder):
        store = HDFactStore(n_dim=512, seed=11,
                            relation_cardinality={RGL.KNOWN_RELATION: "FUNCTIONAL",
                                                  RGL.MEANING_RELATION: "FUNCTIONAL"},
                            use_index=True)
        st = RGL.ReadingLoopState(store=store)
        RGL.seed_known_words(st, ["lantern", "storm", "fire"], source="t")
        RGL.process_sentence(st, sent, "e0", pass_idx=0, encoder=encoder)
        return st

    off_a, off_b = _run(None), _run(None)
    for a in off_a.space.anchors():
        assert np.array_equal(off_a.space.bundle(a), off_b.space.bundle(a)), "reader is nondeterministic"
        assert np.array_equal(off_a.space.bundle(a), RGL.context_vector_masked(sent, a)), \
            "importing perirhinal_conjunctive changed the reader's default encoding"

    on = _run(PerirhinalEncoder(d=RGL.CTX_D, mode="pair"))
    assert on.space.anchors() == off_a.space.anchors(), "the organ changed the anchor population"
    changed = 0
    for a in on.space.anchors():
        want = conjunctive_context_vector_masked(sent, a, RGL.CTX_D, mode="pair")
        assert np.array_equal(on.space.bundle(a), want), \
            "the plugged-in organ did not produce the conjunctive profile for %r" % (a,)
        if not np.array_equal(on.space.bundle(a), off_a.space.bundle(a)):
            changed += 1
    assert changed > 0, "the organ produced the SAME profile as the flat bag -- it is not wired"
    return {"anchors": on.space.anchors(), "n_profiles_changed_vs_flat": changed, "ok": True}


def _run_all_selftests() -> dict:
    return {
        "identity": _selftest_identity_matches_explicit_double_loop(),
        "bag_matches_live": _selftest_bag_matches_live(),
        "superlinear_overlap": _selftest_conjunction_is_superlinear_in_overlap(),
        "kwta": _selftest_kwta_is_sparse_and_deterministic(),
        "hybrid": _selftest_hybrid_is_exactly_bag_plus_pair(),
        "default_off_and_reader_unchanged": _selftest_default_is_off_and_reader_is_unchanged(),
    }


if __name__ == "__main__":
    import json
    r = _run_all_selftests()
    print(json.dumps(r, indent=1, default=str))
    print("[perirhinal_conjunctive selftest] PASS (6/6) switch_default_off=%s" %
          (not PERIRHINAL_CONJUNCTIVE))
