"""distilled_substitutability -- the word-context DISTRIBUTIONAL meaning channel the live organ lacked.

Landed 2026-08-30 (Route A) from the integrated `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`
(owner-DONE, EXCELLENT; reverified 4/4 first-hand at HEAD). THE GAP it closes: `hdlab.grounded_similarity`
judges meaning only from grounded NORMS and pins synonyms and mere associates alike at GROUNDED_CAP=0.45
(sofa/couch == apple/orange == 0.45), because the live organ had NO word-context channel -- it folded each
word's co-occurrence neighbourhood into a dense d=256 random projection that STRUCTURALLY destroys the
per-word counts (crosstalk at support > d; the flat-store route is dead, proven).

THE BRAIN-FOUNDATIONAL FIX (three PINNED mechanisms composed): (1) hippocampal SPARSE PATTERN SEPARATION
-- keep the counts separable, do not project them away; (2) CLS neocortical consolidation -- extract the
distributional structure OFFLINE (PPMI + SVD over the reading co-occurrence counts); (3) the ATL hub shapes
each spoke by CROSS-MODAL AGREEMENT -- a grounded-hub-TAUGHT direction (cross-modal distillation over
arbitrary DISJOINT non-instrument pairs vs the supplied Lancaster+Warriner norms). OUR-INVENTION that was the
BUG: the d=256 dense projection (copied a NUMBER, not the operation). This channel copies the OPERATION.

A pair's substitutability score is  sign * (phi[a] * phi[b]) @ w  -- the element-wise product of the two
word vectors projected on the distilled direction. This CLEARS the licensed 484-pair substitutability
instrument at AUC 0.8388 (CI [0.803, 0.872], beating the info-free twin's MAX over 200 draws 0.705), where
the dense-bundle incumbent sits at chance and grounded_similarity's cap cannot separate the pairs at all.

DEFAULT-SEPARATE: this is a NEW, opt-in channel. `hdlab.grounded_similarity` is UNCHANGED; a caller that
wants the distilled substitutability score calls THIS module (or grounded_similarity's opt-in hook). The
scoring is a static dot product -- NO external LLM at inference. The asset is OFFLINE-built and LABELLED:
the PPMI+SVD space is offline consolidation, the grounded teacher is the supplied Lancaster/Warriner norms
(the FOUNDATION pivot, owner 08-16). It is a STATIC asset -- it does NOT grow with new reading (that is the
deferred Route B online sparse count-store, for when foundation-growth resumes).

    in_distilled_lexicon(word) -> bool
    distilled_substitutability(word_a, word_b) -> Optional[float]   # uncapped; None if either word OOV
    coverage_stats() -> dict

Asset: data/grounded_distilled_substitutability_v1/asset.npz (built by tools/build_distilled_substitutability_asset.py).
"""
from __future__ import annotations

import os
from typing import Dict, Optional

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_ASSET_PATH = os.path.join(_REPO, "data", "grounded_distilled_substitutability_v1", "asset.npz")

_ASSET: Dict[str, object] = {}


def _load() -> Dict[str, object]:
    """Load the static asset ONCE per process (phi space + distilled direction + orientation + row index)."""
    if "phi" not in _ASSET:
        if not os.path.exists(_ASSET_PATH):
            raise FileNotFoundError(
                "distilled_substitutability asset missing: %s -- build it with "
                "tools/build_distilled_substitutability_asset.py" % _ASSET_PATH)
        z = np.load(_ASSET_PATH, allow_pickle=True)
        _ASSET["phi"] = z["phi"]
        _ASSET["w"] = z["w"]
        _ASSET["sign"] = float(z["sign"])
        words = [str(x) for x in z["words"]]
        _ASSET["row_idx"] = {w: i for i, w in enumerate(words)}   # keys as-saved (reading-loop vocab)
    return _ASSET


def _row(word: str) -> Optional[int]:
    """Row of `word` in the consolidated space: exact match first, then lowercased (the reading loop's
    vocab is lowercased, but a caller may pass mixed case)."""
    ri: Dict[str, int] = _load()["row_idx"]  # type: ignore[assignment]
    i = ri.get(str(word))
    return i if i is not None else ri.get(str(word).lower())


def in_distilled_lexicon(word: str) -> bool:
    """True if `word` has a vector in the consolidated distributional space (is scorable)."""
    return _row(word) is not None


def distilled_substitutability(word_a: str, word_b: str) -> Optional[float]:
    """Substitutability score for (word_a, word_b): sign * (phi[a] * phi[b]) @ w. Higher = more
    substitutable (synonym-like) than a mere associate. UNCAPPED (this is exactly the signal
    grounded_similarity's 0.45 cap cannot carry). Returns None if EITHER word is out of the
    consolidated vocabulary (the honest 'no distributional evidence' response -- callers fall back)."""
    a = _load()
    ia = _row(word_a)
    ib = _row(word_b)
    if ia is None or ib is None:
        return None
    phi = a["phi"]           # type: ignore[assignment]
    w = a["w"]               # type: ignore[assignment]
    prod = phi[ia] * phi[ib]
    return a["sign"] * float(prod @ w)  # type: ignore[operator]


def coverage_stats() -> dict:
    a = _load()
    phi = a["phi"]           # type: ignore[assignment]
    return {"n_words": len(a["row_idx"]), "n_dims": int(phi.shape[1]),  # type: ignore[arg-type]
            "asset": _ASSET_PATH}
