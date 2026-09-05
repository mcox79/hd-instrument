"""hdlab/meaning_foundation.py -- loader for the FROZEN curated sense-signature foundation
(owner-DONE build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift, Q111 landing
2026-09-05). The static offline asset data/frontend_assets/meaning_sense_signatures_v1.npz (117,614 WordNet
synsets, one 200-d mean-w2v UNIT signature each, float16, 44MB; on-disk per the project's data-asset
convention -- the whole data/ tree is gitignored). This is the DEFAULT sense-signature source for the meaning
channel (hdlab.diagnostic_context_wsd): the curated signatures deliver rare-sense a_s 0.2512 -> 0.3267
(+0.0755 CI-separated, SemCor subordinate, n=2675) vs computing gloss-only signatures on the fly, with the
shuffled-knowledge info-free twin LOSING and NO MFS regression (witness test_knowledge_factory_meaning_store.py
6/6). Glass-box, NO LLM (a curated static asset is admissible, owner 2026-08-16 -- NO transformer, NO training).

LATENT until a live consumer exists: NOTHING in hdlab/ or experiments/ calls diagnostic_context_wsd at read()
time yet (the reader_meaning_channel stage), so the +0.0755 is proven on the standard meaning INSTRUMENT but
felt by no live board dimension. The frozen store is READY the moment that stage lands; consolidation_gate stays
the mandatory admission guard for any online-grown knowledge (the propose-and-verify grow loop, filed separately).

Usage (drop-in for the caller's on-the-fly gloss signatures):
    from hdlab.meaning_foundation import sense_signatures
    G = sense_signatures(candidate_synsets)              # (K, D) float64, a ZERO row per absent/zero-norm sense
    idx = int(np.argmax(diagnostic_context_scores(context_vecs, G, gamma=gamma)))
"""
from __future__ import annotations

import os
from typing import List, Optional, Sequence

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSET = os.path.join(_REPO, "data", "frontend_assets", "meaning_sense_signatures_v1.npz")
_MANIFEST = os.path.join(_REPO, "data", "frontend_assets", "knowledge_foundation_manifest.json")
_STORE = None   # lazy singleton: (row_index dict, vecs matrix, dim)


def _load():
    """Load the frozen store ONCE per process. npz is a zip (no mmap); the 44MB float16 matrix loads into
    memory on first use, so a reader that never touches the meaning channel pays nothing."""
    global _STORE
    if _STORE is None:
        z = np.load(_ASSET, allow_pickle=True)
        names = [str(n) for n in z["names"]]
        vecs = z["vecs"]
        _STORE = ({n: i for i, n in enumerate(names)}, vecs, int(vecs.shape[1]))
    return _STORE


def dim() -> int:
    """The signature dimensionality (200)."""
    return _load()[2]


def covers(synset: str) -> bool:
    """Whether the frozen store has a signature for this WordNet synset name."""
    return synset in _load()[0]


def sense_signature(synset: str) -> Optional[np.ndarray]:
    """The frozen curated UNIT signature (float64) for a WordNet synset name, or None if the store has no row
    for it OR the row is a zero vector. Upcasting float16->float64 is exact, so this equals the on-disk row."""
    row, vecs, _ = _load()
    i = row.get(synset)
    if i is None:
        return None
    v = np.asarray(vecs[i], dtype=np.float64)
    return v if float(np.linalg.norm(v)) > 1e-6 else None


def sense_signatures(synsets: Sequence[str]) -> np.ndarray:
    """A (len(synsets), D) float64 matrix of frozen signatures IN ORDER, an absent/zero-norm sense a ZERO row
    (scores 0 -- matching diagnostic_context_wsd's missing-gloss convention). The DEFAULT candidate-sense source
    for the WSD/meaning readout: pass this as `sense_gloss_vecs` to diagnostic_context_scores."""
    row, vecs, D = _load()
    out = np.zeros((len(synsets), D), dtype=np.float64)
    for k, s in enumerate(synsets):
        i = row.get(s)
        if i is not None:
            v = np.asarray(vecs[i], dtype=np.float64)
            if float(np.linalg.norm(v)) > 1e-6:
                out[k] = v
    return out


def manifest_path() -> str:
    """The multi-index hub-and-spoke foundation registry (knowledge_foundation_manifest.json)."""
    return _MANIFEST
