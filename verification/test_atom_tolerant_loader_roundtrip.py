"""Verification: tolerant Atom.from_dict loader is round-trip stable (Option A read-path fix).

Scaffold-free witnesses (no tracing) for the 2026-07-09 canonical-loader change that
rescues author-drift atoms into _by_id (flush-safe) instead of silently skipping them:

  - unknown tier/kind strings coerce to the UNSPECIFIED sentinel, NOT a hard skip,
    while the ORIGINAL string is preserved in metadata['_raw_tier'/'_raw_kind'].
  - to_dict re-emits the ORIGINAL tier/kind strings (round-trip STABLE) so the first
    post-fix flush re-persists the raw values, never the sentinel.
  - `atom_id` is accepted as an alias for `id`; name/description synthesize from the id.
  - known tier/kind atoms are unaffected (idempotent).
"""

from __future__ import annotations

from backend.substrate_index.schema import Atom, AtomKind, Tier


def test_unknown_tier_kind_coerce_to_sentinel_and_preserve_raw():
    d = {
        "id": "X/drift_atom",
        "name": "drift",
        "corpus": "math",
        "tier": "SOME_AUTHOR_DRIFT_TIER",
        "kind": "some_author_drift_kind",
        "description": "an author-drift atom",
    }
    a = Atom.from_dict(d)
    assert a.tier is Tier.TIER_UNSPECIFIED
    assert a.kind is AtomKind.UNSPECIFIED
    assert a.metadata["_raw_tier"] == "SOME_AUTHOR_DRIFT_TIER"
    assert a.metadata["_raw_kind"] == "some_author_drift_kind"


def test_roundtrip_reemits_original_tier_kind_strings():
    d = {
        "id": "X/drift_atom",
        "name": "drift",
        "corpus": "math",
        "tier": "SOME_AUTHOR_DRIFT_TIER",
        "kind": "some_author_drift_kind",
        "description": "an author-drift atom",
    }
    out = Atom.from_dict(d).to_dict()
    # to_dict must emit the ORIGINAL strings, not the sentinel enum values
    assert out["tier"] == "SOME_AUTHOR_DRIFT_TIER"
    assert out["kind"] == "some_author_drift_kind"
    # and a second from_dict->to_dict cycle is stable
    out2 = Atom.from_dict(out).to_dict()
    assert out2["tier"] == "SOME_AUTHOR_DRIFT_TIER"
    assert out2["kind"] == "some_author_drift_kind"


def test_atom_id_alias_and_synthesized_name_description():
    d = {
        "atom_id": "X/aliased_id",
        "corpus": "meta",
        "tier": "NA",
        "kind": "primitive",
    }
    a = Atom.from_dict(d)
    assert a.id == "X/aliased_id"
    assert a.name == "X/aliased_id"
    assert a.description == "X/aliased_id"


def test_known_tier_kind_unaffected_no_raw_keys():
    d = {
        "id": "T2/fhrr_bind",
        "name": "bind",
        "corpus": "math",
        "tier": "T2",
        "kind": "primitive",
        "description": "known-good atom",
    }
    a = Atom.from_dict(d)
    assert a.tier is Tier.TIER_2_PRIMITIVE
    assert a.kind is AtomKind.PRIMITIVE
    assert "_raw_tier" not in a.metadata
    assert "_raw_kind" not in a.metadata
    out = a.to_dict()
    assert out["tier"] == "T2"
    assert out["kind"] == "primitive"
