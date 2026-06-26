"""Verification: TokenVocab — deterministic codebook, growth, persistence round-trip."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from hdlab.token_vocab import (
    ENCODER_PROVENANCE,
    UNK_TOKEN,
    TokenVocab,
    _bipolar_hv,
    _seed_for_token,
)


def test_provenance_is_substrate_native() -> None:
    """ENCODER_PROVENANCE constant marks Path C compliance for downstream cells."""
    assert ENCODER_PROVENANCE == "SUBSTRATE_NATIVE"
    v = TokenVocab(n_dim=256)
    assert v.provenance == "SUBSTRATE_NATIVE"


def test_deterministic_seed_for_token() -> None:
    """Same token same salt always produces same 64-bit seed (>32-bit range)."""
    s1 = _seed_for_token("hello")
    s2 = _seed_for_token("hello")
    s3 = _seed_for_token("world")
    assert s1 == s2
    assert s1 != s3
    # Witness 64-bit (not 32-bit) seed space: at least one of 100 random
    # tokens MUST exceed 2**32 (negligible-probability false-failure).
    seeds = [_seed_for_token(f"token_{i}") for i in range(100)]
    assert any(s >= (1 << 32) for s in seeds), "seed range looks 32-bit not 64-bit"


def test_salt_changes_basis() -> None:
    """Same token with different salt -> different HV (re-basis for ablation cells)."""
    n = 1024
    hv_a = _bipolar_hv(_seed_for_token("the", salt=0), n)
    hv_b = _bipolar_hv(_seed_for_token("the", salt=42), n)
    # Bipolar HVs with independent random seeds have ~0 cosine sim.
    cos = float(np.dot(hv_a, hv_b) / (np.linalg.norm(hv_a) * np.linalg.norm(hv_b)))
    assert abs(cos) < 0.15, f"salted basis should be independent; cos={cos}"


def test_same_token_same_codebook_entry() -> None:
    """token_to_id + id_to_codebook_vec idempotent across multiple TokenVocab inits."""
    n = 1024
    v_a = TokenVocab(n_dim=n)
    v_a.add_token("apple")
    v_a.add_token("banana")
    hv_apple_a = v_a.id_to_codebook_vec(v_a.token_to_id("apple"))

    v_b = TokenVocab(n_dim=n)
    v_b.add_token("zebra")
    v_b.add_token("apple")
    hv_apple_b = v_b.id_to_codebook_vec(v_b.token_to_id("apple"))

    # IDs MAY differ (insertion order) but HVs MUST be identical.
    assert np.array_equal(hv_apple_a, hv_apple_b)


def test_vocab_growth_preserves_prior_ids() -> None:
    """Adding new tokens never re-maps existing token -> id assignments."""
    v = TokenVocab(n_dim=512)
    v.add_token("alpha")
    v.add_token("beta")
    id_alpha = v.token_to_id("alpha")
    id_beta = v.token_to_id("beta")
    v.add_token("gamma")
    v.add_token("delta")
    assert v.token_to_id("alpha") == id_alpha
    assert v.token_to_id("beta") == id_beta
    assert v.token_to_id("gamma") == 2
    assert v.token_to_id("delta") == 3


def test_unk_handling() -> None:
    """OOV token maps to unk_id; UNK has its own deterministic HV."""
    v = TokenVocab(n_dim=512)
    v.add_token("seen")
    assert v.token_to_id("seen") == 0
    assert v.token_to_id("never_seen") == v.unk_id
    hv_unk_1 = v.id_to_codebook_vec(v.unk_id)
    hv_unk_2 = v.id_to_codebook_vec(v.unk_id)
    assert np.array_equal(hv_unk_1, hv_unk_2)
    # UNK distinct from "seen"
    hv_seen = v.id_to_codebook_vec(v.token_to_id("seen"))
    assert not np.array_equal(hv_unk_1, hv_seen)


def test_bipolar_property() -> None:
    """All codebook entries are bipolar {-1, +1}; correct shape."""
    n = 1024
    v = TokenVocab(n_dim=n)
    for t in ["one", "two", "three"]:
        v.add_token(t)
    cb = v.codebook_matrix()
    assert cb.shape == (v.v_tok + 1, n)
    assert cb.dtype == np.float32
    uniq = np.unique(cb)
    assert set(uniq.tolist()).issubset({-1.0, 1.0}), f"non-bipolar values: {uniq}"


def test_build_from_corpus_by_frequency() -> None:
    """build_from_corpus picks top-V by descending frequency, deterministic ties."""
    stream = ["the", "cat", "the", "dog", "the", "cat", "bird"]
    v = TokenVocab(n_dim=256)
    v.build_from_corpus(stream, v_top=3)
    assert v.v_tok == 3
    # 'the' (3), 'cat' (2), 'dog' (1) ties with 'bird' (1) -> 'dog' first (first-seen)
    assert v.id_to_token(0) == "the"
    assert v.id_to_token(1) == "cat"
    assert v.id_to_token(2) == "dog"


def test_freeze_blocks_growth() -> None:
    """add_token after freeze() raises; existing tokens still encodable."""
    v = TokenVocab(n_dim=256)
    v.add_token("a")
    v.freeze()
    assert v.frozen
    v.add_token("a", frequency=5)  # existing OK (only bumps freq)
    with pytest.raises(RuntimeError):
        v.add_token("b")


def test_persistence_round_trip() -> None:
    """save -> load reproduces vocab AND codebook (codebook regenerates from seed)."""
    v = TokenVocab(n_dim=512, seed=7)
    for tok in ["alpha", "beta", "gamma"]:
        v.add_token(tok, frequency=10)
    v.add_token("alpha", frequency=5)  # bump existing
    v.freeze()
    cb_before = v.codebook_matrix()

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "tokens.jsonl"
        v.save(p)
        v_loaded = TokenVocab.load(p)

    assert v_loaded.v_tok == v.v_tok
    assert v_loaded.n_dim == v.n_dim
    assert v_loaded.seed == v.seed
    assert v_loaded.frozen == v.frozen
    for i in range(v.v_tok):
        assert v_loaded.id_to_token(i) == v.id_to_token(i)
    cb_after = v_loaded.codebook_matrix()
    assert np.array_equal(cb_before, cb_after)


def test_unique_codebook_entries_at_scale() -> None:
    """At V=50 / N=512, no two distinct tokens produce identical bipolar HVs."""
    v = TokenVocab(n_dim=512)
    for i in range(50):
        v.add_token(f"token_{i}")
    cb = v.codebook_matrix()[:50]
    # Pairwise: any duplicates?
    seen: set[bytes] = set()
    for i in range(50):
        b = cb[i].tobytes()
        assert b not in seen, f"duplicate codebook entry at id {i}"
        seen.add(b)


def test_v_max_capacity_raises() -> None:
    """add_token beyond v_max raises ValueError; growth bounded."""
    v = TokenVocab(n_dim=64, v_max=3)
    v.add_token("a")
    v.add_token("b")
    v.add_token("c")
    with pytest.raises(ValueError):
        v.add_token("d")


def test_repr_and_unk_token() -> None:
    """__repr__ informative; UNK constant exported."""
    v = TokenVocab(n_dim=64)
    r = repr(v)
    assert "TokenVocab" in r
    assert "n_dim=64" in r
    assert UNK_TOKEN == "<UNK>"
