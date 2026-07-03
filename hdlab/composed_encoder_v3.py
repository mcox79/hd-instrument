"""Composed brain-analog concept encoder v3: VWFA + PPMI/SVD score-level late-combine.

INPUT REGIME DOCSTRING BLOCK:
    Input: raw text (unicode string; ASCII in current use) + supervised
        (sentence, concept_label) pairs at fit time.
    Output at encode_streams(text): dict {"vwfa": [n_dim] float32, "ppmi": [n_dim] float32};
        both L2-normalized.
    Output at retrieve_topk(text, k): [k] int64 top-k concept indices.
    Regime type: SUPERVISED CONCEPT RETRIEVAL over per-concept prototype tables
        built at fit() time from labeled sentences.
    Brain analog: parallel dorsal-VWFA (surface orthographic) + ATL-hub (amodal
        semantic co-occurrence) streams late-combined at the N400 window
        (Marinkovic 2003, Solomyak/Marantz 2010; Kutas/Federmeier 2011).  NOT
        sequential cascade; score-level integration matches N400 amplitude
        reflecting integration difficulty across streams.

Design (LOAD-BEARING):
    - VWFA and PPMI produce HDs in DIFFERENT HD codebook namespaces so vectors
      cannot be summed directly (per late_combine.py fit_weights_grid_2spoke
      comment).  Composition happens at SCORE-LEVEL: cos(query_vwfa, proto_vwfa)
      and cos(query_ppmi, proto_ppmi) are weighted-summed at retrieval time.
    - This makes the alpha=1,beta=0 / alpha=0,beta=1 identity BIT-IDENTICAL on
      retrieved top-k indices (score-scaling invariance of argmax).
    - Modern-Hopfield readout (Component C) is intentionally NOT included per
      2026-07-03 Skunkworks + 4/5 drill recommendation: HF at smoke; attenuation
      floor on sparse-bipolar equal-norm storage.

API (mirrors individual encoders):
    encoder = ComposedEncoderV3(n_dim=2048, alpha=0.5, beta=0.5, ...)
    encoder.fit(sentences, concept_labels)          # builds per-concept protos
    encoder.encode_streams(text) -> {"vwfa": v, "ppmi": v}  # L2-normalized
    encoder.retrieve_topk(text, k) -> [k] int64     # top-k concept indices
    encoder.cosine_argmax(text) -> int              # top-1 concept index

Scope caveat (LOAD-BEARING per USER 2026-07-02):
    Substrate KNOWS ALMOST NOTHING.  This composed encoder is a MECHANISM-
    composition primitive tested on SUPERVISED synthetic corpora + substrate-
    ingested WordNet symbolic content.  HP earned here does NOT grant
    "substrate understands English"; grants "brain-analog COMPOSITION rescues
    transfer failure on the SUPERVISED regime at this task".

Convention note: CLAUDE.md prefers torch tensors at API boundaries; both wrapped
    primitives (VWFAEncoder, PPMISparseEncoder) are numpy-native, so this
    wrapper stays numpy-native for zero-copy compatibility.  All arrays are
    float32 or int64 at API boundaries; explicit dtypes.

ASCII-only.  No emojis.  No em dashes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
from hdlab.vwfa import VWFAEncoder


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _l2_normalize(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """L2-normalize a 1-D float32 array; zero-vector stays zero."""
    n = float(np.linalg.norm(v))
    if n < eps:
        return v.astype(np.float32, copy=True)
    return (v / n).astype(np.float32)


def _l2_normalize_rows(mat: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """L2-normalize each row of a 2-D float32 array."""
    m = mat.astype(np.float32, copy=False)
    norms = np.linalg.norm(m, axis=1)
    safe = np.where(norms < eps, 1.0, norms)
    out = m / safe[:, None]
    # Zero rows stay zero.
    out[norms < eps] = 0.0
    return out.astype(np.float32)


def _cosine_scores(query: np.ndarray, protos: np.ndarray) -> np.ndarray:
    """Return [n_protos] float32 cosine scores of a query vs proto table."""
    q = query.astype(np.float32)
    p = protos.astype(np.float32)
    qn = float(np.linalg.norm(q))
    if qn < 1e-12:
        return np.zeros(p.shape[0], dtype=np.float32)
    pn = np.linalg.norm(p, axis=1)
    pn_safe = np.where(pn < 1e-12, 1.0, pn)
    scores = (p @ q) / (pn_safe * qn)
    scores = np.where(pn < 1e-12, -1e9, scores).astype(np.float32)
    return scores


# ---------------------------------------------------------------------------
# ComposedEncoderV3.
# ---------------------------------------------------------------------------


class ComposedEncoderV3:
    """Composed brain-analog encoder: VWFA + PPMI/SVD score-level late-combine.

    Attributes populated at fit():
        term_to_idx, term_embeddings: forwarded from PPMISparseEncoder.
        protos_vwfa: [n_concepts, n_dim] float32; per-concept L2-normalized
            VWFA prototype (mean of per-concept training-sentence VWFA HDs).
        protos_ppmi: [n_concepts, n_dim] float32; per-concept L2-normalized
            PPMI prototype (mean of per-concept training-sentence PPMI HDs).
        n_concepts: int.

    Retrieval uses score-level late-combine:
        combined_i = alpha * cos(v_vwfa_query, proto_vwfa_i)
                   + beta  * cos(v_ppmi_query, proto_ppmi_i)
        top-k = argsort(-combined)[:k]

    Formula identity (BIT-IDENTICAL on argmax; score-scaling invariant):
        alpha=1, beta=0 -> retrieved indices == pure-VWFA cosine argmax.
        alpha=0, beta=1 -> retrieved indices == pure-PPMI cosine argmax.
    """

    def __init__(
        self,
        n_dim: int = 2048,
        alpha: float = 0.5,
        beta: float = 0.5,
        vwfa_kwargs: Optional[Dict[str, Any]] = None,
        ppmi_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        if int(n_dim) <= 0:
            raise ValueError(f"n_dim must be positive; got {n_dim}")
        self.n_dim = int(n_dim)
        self.alpha = float(alpha)
        self.beta = float(beta)
        vk = dict(vwfa_kwargs) if vwfa_kwargs else {}
        pk = dict(ppmi_kwargs) if ppmi_kwargs else {}
        # Force n_dim parity so stream vectors have identical shape.
        vk["n_dim"] = self.n_dim
        pk["n_dim"] = self.n_dim
        self.vwfa = VWFAEncoder(**vk)
        self.ppmi = PPMISparseEncoder(**pk)
        # Fit-populated.
        self.n_concepts: int = 0
        self.protos_vwfa: Optional[np.ndarray] = None  # [n_concepts, n_dim] float32
        self.protos_ppmi: Optional[np.ndarray] = None  # [n_concepts, n_dim] float32
        self._fitted: bool = False

    # ---------- fit ----------

    def fit(
        self,
        sentences: Sequence[str],
        concept_labels: Sequence[int],
    ) -> "ComposedEncoderV3":
        """Fit PPMI encoder + build per-concept L2-normalized prototype tables.

        sentences: list of raw text strings.
        concept_labels: [N_sentences] int in [0, n_concepts).
        """
        n_sent = len(sentences)
        if n_sent != len(concept_labels):
            raise ValueError(
                f"len(sentences)={n_sent} != "
                f"len(concept_labels)={len(concept_labels)}"
            )
        if n_sent == 0:
            raise ValueError("empty training set")
        labels_arr = np.asarray(list(concept_labels), dtype=np.int64)
        n_concepts = int(labels_arr.max()) + 1

        # Fit PPMI on the labeled corpus.
        self.ppmi.fit(list(sentences), labels_arr)

        # Build per-concept prototypes (mean of per-sentence stream HDs; L2-norm).
        acc_vwfa = np.zeros((n_concepts, self.n_dim), dtype=np.float32)
        acc_ppmi = np.zeros((n_concepts, self.n_dim), dtype=np.float32)
        counts = np.zeros(n_concepts, dtype=np.float32)
        for s, lbl in zip(sentences, labels_arr):
            li = int(lbl)
            vw = self.vwfa.encode_sentence(str(s)).astype(np.float32)
            pp = self.ppmi.encode(str(s)).astype(np.float32)
            acc_vwfa[li] += vw
            acc_ppmi[li] += pp
            counts[li] += 1.0
        denom = np.where(counts > 0, counts, 1.0)
        mean_vwfa = acc_vwfa / denom[:, None]
        mean_ppmi = acc_ppmi / denom[:, None]
        self.protos_vwfa = _l2_normalize_rows(mean_vwfa)
        self.protos_ppmi = _l2_normalize_rows(mean_ppmi)
        self.n_concepts = int(n_concepts)
        self._fitted = True
        return self

    # ---------- encode ----------

    def encode_streams(self, text: str) -> Dict[str, np.ndarray]:
        """Return {vwfa, ppmi}: two [n_dim] float32 L2-normalized stream HDs.

        The encoder does NOT need fit() to encode streams -- but VWFA is
        codebook-hashed (fit-free) and PPMI needs fit() before encode.
        """
        vw = self.vwfa.encode_sentence(str(text)).astype(np.float32)
        if self.ppmi.term_embeddings is None:
            raise RuntimeError(
                "PPMI stream not fit; call fit() before encode_streams()"
            )
        pp = self.ppmi.encode(str(text)).astype(np.float32)
        return {
            "vwfa": _l2_normalize(vw),
            "ppmi": _l2_normalize(pp),
        }

    def encode(self, text: str) -> Dict[str, np.ndarray]:
        """Alias for encode_streams() -- returns dict of stream HDs."""
        return self.encode_streams(text)

    # ---------- retrieval ----------

    def retrieve_topk(self, text: str, k: int = 1) -> np.ndarray:
        """Top-k concept indices via score-level late-combine of stream cosines.

        Returns [k] int64 concept indices sorted by combined score descending.
        """
        if not self._fitted or self.protos_vwfa is None or self.protos_ppmi is None:
            raise RuntimeError("encoder not fit; call fit() first")
        streams = self.encode_streams(text)
        cos_vwfa = _cosine_scores(streams["vwfa"], self.protos_vwfa)
        cos_ppmi = _cosine_scores(streams["ppmi"], self.protos_ppmi)
        combined = (self.alpha * cos_vwfa + self.beta * cos_ppmi).astype(np.float32)
        n = int(combined.shape[0])
        k_eff = int(min(max(1, int(k)), n))
        if k_eff >= n:
            order = np.argsort(-combined)
        else:
            idx_part = np.argpartition(-combined, k_eff)[:k_eff]
            order = idx_part[np.argsort(-combined[idx_part])]
        return order.astype(np.int64)

    def cosine_argmax(self, text: str) -> int:
        """Return the top-1 concept index (convenience API parity)."""
        top = self.retrieve_topk(text, k=1)
        return int(top[0])

    def set_weights(self, alpha: float, beta: float) -> None:
        """Update (alpha, beta) without refitting."""
        self.alpha = float(alpha)
        self.beta = float(beta)

    def __repr__(self) -> str:
        return (
            f"ComposedEncoderV3(n_dim={self.n_dim}, alpha={self.alpha}, "
            f"beta={self.beta}, fitted={self._fitted}, "
            f"n_concepts={self.n_concepts})"
        )


# ---------------------------------------------------------------------------
# Self-test.
# ---------------------------------------------------------------------------


def _build_toy_corpus() -> Tuple[List[str], np.ndarray, List[Tuple[int, str]]]:
    """Small 5-concept synthetic corpus with disjoint semantic + surface signal."""
    sentences = [
        # concept 0: cat
        "cat feline pet purr whiskers",
        "cat kitten meow claws",
        "cat pet feline domestic",
        # concept 1: dog
        "dog canine bark loyal",
        "dog puppy leash walk",
        "dog canine pet fetch",
        # concept 2: airplane
        "airplane jet wing fly sky",
        "airplane pilot cockpit turbine",
        "jet aircraft engine wing",
        # concept 3: rose
        "rose flower red petal thorn",
        "rose bloom garden fragrance",
        "rose petal flower blossom",
        # concept 4: guitar
        "guitar string chord strum music",
        "guitar acoustic pluck song",
        "guitar chord fretboard instrument",
    ]
    labels = np.array(
        [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4], dtype=np.int64
    )
    # Held-out query per concept: an unseen surface phrase with related terms.
    queries = [
        (0, "feline purr claws whiskers"),
        (1, "canine bark loyal puppy"),
        (2, "aircraft pilot wing turbine"),
        (3, "flower petal bloom garden"),
        (4, "chord string strum acoustic"),
    ]
    return sentences, labels, queries


def _pure_vwfa_argmax(
    text: str,
    vwfa: VWFAEncoder,
    protos_vwfa: np.ndarray,
    k: int,
) -> np.ndarray:
    vw = _l2_normalize(vwfa.encode_sentence(text).astype(np.float32))
    scores = _cosine_scores(vw, protos_vwfa)
    n = int(scores.shape[0])
    k_eff = int(min(max(1, int(k)), n))
    if k_eff >= n:
        return np.argsort(-scores).astype(np.int64)
    idx_part = np.argpartition(-scores, k_eff)[:k_eff]
    return idx_part[np.argsort(-scores[idx_part])].astype(np.int64)


def _pure_ppmi_argmax(
    text: str,
    ppmi: PPMISparseEncoder,
    protos_ppmi: np.ndarray,
    k: int,
) -> np.ndarray:
    pp = _l2_normalize(ppmi.encode(text).astype(np.float32))
    scores = _cosine_scores(pp, protos_ppmi)
    n = int(scores.shape[0])
    k_eff = int(min(max(1, int(k)), n))
    if k_eff >= n:
        return np.argsort(-scores).astype(np.int64)
    idx_part = np.argpartition(-scores, k_eff)[:k_eff]
    return idx_part[np.argsort(-scores[idx_part])].astype(np.int64)


def _selftest() -> None:
    print("[composed_encoder_v3 selftest] START", flush=True)

    sentences, labels, queries = _build_toy_corpus()

    # ------- Selftest 1: shape at n_dim=2048 -------
    enc = ComposedEncoderV3(
        n_dim=2048, alpha=0.5, beta=0.5,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 11},
    )
    enc.fit(sentences, labels)
    streams = enc.encode_streams("cat pet")
    assert streams["vwfa"].shape == (2048,), (
        f"selftest 1a: vwfa stream shape {streams['vwfa'].shape} != (2048,)"
    )
    assert streams["ppmi"].shape == (2048,), (
        f"selftest 1b: ppmi stream shape {streams['ppmi'].shape} != (2048,)"
    )
    assert streams["vwfa"].dtype == np.float32
    assert streams["ppmi"].dtype == np.float32
    print("[selftest 1] shape @ n_dim=2048 PASS", flush=True)

    # ------- Selftest 2: L2-normalization of stream HDs -------
    vw_norm = float(np.linalg.norm(streams["vwfa"]))
    pp_norm = float(np.linalg.norm(streams["ppmi"]))
    # Non-degenerate: both streams should be unit-norm (or exactly 0 if OOV/empty).
    assert abs(vw_norm - 1.0) < 1e-4 or vw_norm < 1e-6, (
        f"selftest 2a: vwfa stream not L2-normalized; |v|={vw_norm}"
    )
    assert abs(pp_norm - 1.0) < 1e-4 or pp_norm < 1e-6, (
        f"selftest 2b: ppmi stream not L2-normalized; |v|={pp_norm}"
    )
    print(
        f"[selftest 2] stream L2-norm PASS  |vwfa|={vw_norm:.4f} |ppmi|={pp_norm:.4f}",
        flush=True,
    )

    # ------- Selftest 3: determinism -------
    s1 = enc.encode_streams("cat pet feline")
    s2 = enc.encode_streams("cat pet feline")
    assert np.array_equal(s1["vwfa"], s2["vwfa"]), "selftest 3a: vwfa non-deterministic"
    assert np.array_equal(s1["ppmi"], s2["ppmi"]), "selftest 3b: ppmi non-deterministic"
    print("[selftest 3] determinism PASS", flush=True)

    # ------- Selftest 4: retrieval sanity on trivial 5-concept synthetic set -------
    correct = 0
    for lbl, qtext in queries:
        top1 = enc.cosine_argmax(qtext)
        if top1 == lbl:
            correct += 1
    # equal-alpha on this trivial disjoint-vocabulary set should retrieve at
    # least 4 of 5; some noise permitted from SVD small-corpus artefacts.
    assert correct >= 4, (
        f"selftest 4: retrieval recall@1 = {correct}/5 on trivial disjoint corpus"
    )
    print(f"[selftest 4] retrieval sanity PASS  r@1={correct}/5", flush=True)

    # ------- Selftest 5: formula identity  alpha=1, beta=0  ==  pure VWFA argmax -------
    enc_vwfa_only = ComposedEncoderV3(
        n_dim=2048, alpha=1.0, beta=0.0,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 11},
    )
    enc_vwfa_only.fit(sentences, labels)
    assert enc_vwfa_only.protos_vwfa is not None
    for _, qtext in queries:
        composed_topk = enc_vwfa_only.retrieve_topk(qtext, k=5)
        pure_topk = _pure_vwfa_argmax(
            qtext, enc_vwfa_only.vwfa, enc_vwfa_only.protos_vwfa, k=5
        )
        assert np.array_equal(composed_topk, pure_topk), (
            "selftest 5 FORMULA-VWFA-ONLY: alpha=1,beta=0 top-5 diverges from "
            f"pure VWFA top-5.  composed={composed_topk.tolist()} "
            f"pure={pure_topk.tolist()}  query={qtext!r}"
        )
    print("[selftest 5] FORMULA-IDENTITY alpha=1,beta=0 == pure VWFA PASS", flush=True)

    # ------- Selftest 6: formula identity  alpha=0, beta=1  ==  pure PPMI argmax -------
    enc_ppmi_only = ComposedEncoderV3(
        n_dim=2048, alpha=0.0, beta=1.0,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 11},
    )
    enc_ppmi_only.fit(sentences, labels)
    assert enc_ppmi_only.protos_ppmi is not None
    for _, qtext in queries:
        composed_topk = enc_ppmi_only.retrieve_topk(qtext, k=5)
        pure_topk = _pure_ppmi_argmax(
            qtext, enc_ppmi_only.ppmi, enc_ppmi_only.protos_ppmi, k=5
        )
        assert np.array_equal(composed_topk, pure_topk), (
            "selftest 6 FORMULA-PPMI-ONLY: alpha=0,beta=1 top-5 diverges from "
            f"pure PPMI top-5.  composed={composed_topk.tolist()} "
            f"pure={pure_topk.tolist()}  query={qtext!r}"
        )
    print("[selftest 6] FORMULA-IDENTITY alpha=0,beta=1 == pure PPMI PASS", flush=True)

    # ------- Selftest 7: unfit-encoder guard -------
    unfit = ComposedEncoderV3(n_dim=512, alpha=0.5, beta=0.5,
                              vwfa_kwargs={"seed_prefix": "SELFTEST_V3"},
                              ppmi_kwargs={"min_term_freq": 1})
    try:
        unfit.retrieve_topk("cat", k=1)
        raise AssertionError("selftest 7: retrieve_topk on unfit encoder must raise")
    except RuntimeError:
        pass
    try:
        unfit.encode_streams("cat")
        raise AssertionError("selftest 7: encode_streams on unfit encoder must raise")
    except RuntimeError:
        pass
    print("[selftest 7] unfit-encoder guard PASS", flush=True)

    # ------- Selftest 8: empty-text handling -------
    empty_streams = enc.encode_streams("")
    # VWFA returns +1 sentinel for empty word / empty sentence; L2-normalize
    # gives 1/sqrt(n_dim) per element -> unit-norm; PPMI encode('') gives zeros.
    assert not np.any(np.isnan(empty_streams["vwfa"])), "selftest 8a: NaN in empty VWFA"
    assert not np.any(np.isnan(empty_streams["ppmi"])), "selftest 8b: NaN in empty PPMI"
    print("[selftest 8] empty-text handling PASS (no NaN)", flush=True)

    # ------- Selftest 9: set_weights re-parameterization -------
    top_before = enc.retrieve_topk("cat pet feline", k=3)
    enc.set_weights(alpha=1.0, beta=0.0)
    top_vwfa = enc.retrieve_topk("cat pet feline", k=3)
    enc.set_weights(alpha=0.0, beta=1.0)
    top_ppmi = enc.retrieve_topk("cat pet feline", k=3)
    enc.set_weights(alpha=0.5, beta=0.5)  # restore
    # Different weights should generally give different rankings on non-
    # degenerate data (score-level combine is non-trivial).  Do NOT assert
    # inequality strictly (there may be dominant signals where all weights
    # rank the same), but assert types + shapes.
    assert top_before.shape == (3,) and top_vwfa.shape == (3,) and top_ppmi.shape == (3,)
    print(
        f"[selftest 9] set_weights re-parameterization PASS  "
        f"top3@(0.5,0.5)={top_before.tolist()} "
        f"top3@(1,0)={top_vwfa.tolist()} top3@(0,1)={top_ppmi.tolist()}",
        flush=True,
    )

    # ------- Selftest 10: scale sentinel n_dim=8192 -------
    enc_big = ComposedEncoderV3(
        n_dim=8192, alpha=0.5, beta=0.5,
        vwfa_kwargs={"scales": (1, 2, 3, 4), "bind_position": True,
                     "seed_prefix": "SELFTEST_V3_BIG"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": 17},
    )
    enc_big.fit(sentences, labels)
    s_big = enc_big.encode_streams("cat pet feline")
    assert s_big["vwfa"].shape == (8192,), (
        f"selftest 10a: scale-sentinel vwfa shape {s_big['vwfa'].shape} != (8192,)"
    )
    assert s_big["ppmi"].shape == (8192,), (
        f"selftest 10b: scale-sentinel ppmi shape {s_big['ppmi'].shape} != (8192,)"
    )
    # Retrieval still non-degenerate.
    correct_big = sum(1 for lbl, qt in queries if enc_big.cosine_argmax(qt) == lbl)
    assert correct_big >= 4, (
        f"selftest 10c: scale-sentinel retrieval r@1={correct_big}/5"
    )
    print(
        f"[selftest 10] scale sentinel n_dim=8192 PASS  r@1={correct_big}/5",
        flush=True,
    )

    # ------- Selftest 11: dim mismatch guard (concept_labels vs sentences) -------
    try:
        bad = ComposedEncoderV3(n_dim=512,
                                vwfa_kwargs={"seed_prefix": "SELFTEST_V3"},
                                ppmi_kwargs={"min_term_freq": 1})
        bad.fit(sentences, list(labels)[:5])  # length mismatch
        raise AssertionError("selftest 11: fit did not raise on length mismatch")
    except ValueError:
        pass
    print("[selftest 11] dim-mismatch guard PASS", flush=True)

    # ------- Selftest 12: n_dim propagates into wrapped encoders -------
    assert enc.vwfa.n_dim == 2048, f"selftest 12a: vwfa n_dim {enc.vwfa.n_dim} != 2048"
    assert enc.ppmi.n_dim == 2048, f"selftest 12b: ppmi n_dim {enc.ppmi.n_dim} != 2048"
    assert enc_big.vwfa.n_dim == 8192
    assert enc_big.ppmi.n_dim == 8192
    print("[selftest 12] n_dim propagation PASS", flush=True)

    # ------- Selftest 13: proto tables shape + L2-normalization -------
    assert enc.protos_vwfa is not None and enc.protos_ppmi is not None
    assert enc.protos_vwfa.shape == (5, 2048), (
        f"selftest 13a: protos_vwfa shape {enc.protos_vwfa.shape} != (5, 2048)"
    )
    assert enc.protos_ppmi.shape == (5, 2048), (
        f"selftest 13b: protos_ppmi shape {enc.protos_ppmi.shape} != (5, 2048)"
    )
    row_norms_vw = np.linalg.norm(enc.protos_vwfa, axis=1)
    row_norms_pp = np.linalg.norm(enc.protos_ppmi, axis=1)
    # Every non-degenerate row is unit-norm; zero rows exempted.
    for i, n in enumerate(row_norms_vw):
        assert abs(n - 1.0) < 1e-4 or n < 1e-6, (
            f"selftest 13c: proto_vwfa row {i} not unit-norm; |v|={n}"
        )
    for i, n in enumerate(row_norms_pp):
        assert abs(n - 1.0) < 1e-4 or n < 1e-6, (
            f"selftest 13d: proto_ppmi row {i} not unit-norm; |v|={n}"
        )
    print("[selftest 13] proto tables shape + L2-norm PASS", flush=True)

    print(
        "[composed_encoder_v3 selftest] ALL PASS "
        f"(13 selftests; r@1_equal_alpha={correct}/5; "
        f"r@1_n8192={correct_big}/5)",
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
