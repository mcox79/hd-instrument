"""M1.9 SemanticParser -- intent + role-slot extraction from compositional HD bundles.

Extracted 2026-07-02 from exp_substrate_semantic_parser_intent_slot_extraction_v1
(M1.9 v1 Skunkworks CG a508452e; ARM_SUBSTRATE_FULL codepath). Cortex primitive
M1.9: given a pre-composed HD bundle carrying an intent term plus a sum of
role-key-bound slot bindings, recover the intent index and per-role slot
indices via k_NN_lookup cleanup on the intent codebook and HRR unbind +
per-role k_NN_lookup cleanup on sharded slot dictionaries.

============================================================================
INPUT REGIME (mandatory framing per USER 2026-07-02 discipline)
============================================================================
Inputs are **pre-composed HD bundles built from known codebooks**, NOT English
text. The bundle construction is:

    input_hd = INTENT_WEIGHT * intent_codebook[intent_id]
             + sum_r bind(role_key[r], slot_dict[r][slot_id_r])

where `intent_id` and `slot_id_r` are integer indices into random bipolar
codebooks. This primitive tests the SUBSTRATE MECHANISM of intent + slot
recovery from a compositional HD carrier. It does NOT test language
understanding: the substrate never sees characters, tokens, words, or any
linguistic surface. Full "language -> HD" encoding (Stage 4) is separate,
upstream, and not yet built.

Per feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_
USER_2026-07-02: framing this primitive as "the substrate parses natural
language" is a discipline violation. Frame as: "given a pre-composed HD
bundle encoding a known compositional structure, recover the structure via
substrate primitives (cleanup + unbind)."

============================================================================
COMPUTE ARCHITECTURE (mandatory per USER-locked storage-strategy substrate
physics law CG_META 2026-07-02: math4_v2 + math4_rung3_v2 chain-grade)
============================================================================
Storage strategy: **SHARDED** (per-role slot dictionaries).

Rationale:
- Each role r owns its own slot dictionary slot_dicts[r] of shape
  [slot_dict_size_per_role, n_dim]. Slot vectors are NEVER shared across
  roles; per-role SHARDED storage. This mirrors M1.7 RoleSlotSummarizer's
  SHARDED discipline: BUNDLED (shared vocab across roles) would collapse at
  chain depth L>=2 per math4_v2 law.
- The intent codebook itself is SHARDED across intent classes (one prototype
  vector per intent id). Cleanup via k_NN_lookup is a pure retrieval; no
  cross-class interference at parse time.
- The ARM_M16_ROUTER control (direct k_NN_lookup on input_hd without unbind)
  is the NEGATIVE control demonstrating that role-position information IS
  extracted from the bundle by the unbind step; skipping unbind collapses
  slot recovery toward chance.

Composition guarantee (L>=2 chain composition per math4_v2 discipline):
- Intent-recovery leg: 1 primitive (k_NN_lookup on codebook). Depth L=1.
- Slot-recovery leg per role: 2 primitives (unbind then k_NN_lookup).
  Depth L=2 per role. Each role is independent; no cross-role bundle inside
  bundle. SHARDED slot storage prevents the BUNDLED collapse regime.
- Composition-safe under M1.7 RoleSlotSummarizer downstream: SemanticParser
  outputs structured (intent_id, slot_ids) tuples that can feed the
  summarizer role-key partition without additional bundling.
============================================================================

Envelope (chain-grade-confirmed at ARM_SUBSTRATE_FULL; do not exceed without
rescue cell):
- N_DIM >= 8192 (Plate 1995 HRR capacity floor for K=5 role bundle)
- N_INTENTS up to 50 (CG regime seed 11/17/23 v1 smoke)
- N_ROLES = 5 (SUBJECT/OBJECT/ATTRIBUTE/TIME/LOCATION in source cell; any
  disjoint role_keys set works)
- SLOT_DICT_SIZE_PER_ROLE = 100 (per-role dict cardinality)
- INTENT_WEIGHT recommended >= 8.0 so intent term is not drowned by the
  K-role slot bundle (theoretical fraction = W/(W+sqrt(K)); at W=8, K=5,
  fraction ~= 0.78).
- Per-arm envelope numbers (from CG smoke on seed 11 at N_DIM=8192):
    intent_acc >= 0.85 (HP floor)
    slot_fill_overall >= 0.80 (HP floor)
    shuffled-key control slot_fill <= 0.20 (sanity ceiling)

References:
- Source cell: experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py
- Pre-reg: preregs/2026-07-02_substrate_semantic_parser_intent_slot_extraction_v1.md
- Related primitives: hdlab.intent_classifier (Hebbian regime is NARROW for
  bundle inputs -- direct cleanup is the correct primitive here), hdlab.binding
  (HRR bind/unbind), hdlab.cleanup_family (k_NN_lookup)

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np
import torch

from hdlab.binding import bind as hd_bind
from hdlab.binding import unbind as hd_unbind
from hdlab.cleanup_family import k_NN_lookup
from hdlab.intent_classifier import IntentClassifier


# CG-anchored envelope constants (M1.9 v1 seed 11/17/23 CG 2026-07-02).
CG_N_DIM_DEFAULT = 8192
CG_N_INTENTS_DEFAULT = 50
CG_N_ROLES_DEFAULT = 5
CG_SLOT_DICT_SIZE_DEFAULT = 100
CG_INTENT_WEIGHT_DEFAULT = 8.0
CG_INTENT_ACC_HP_FLOOR = 0.85
CG_SLOT_FILL_HP_FLOOR = 0.80
CG_SHUFFLED_SLOT_CEILING = 0.20


@dataclass
class ParseResult:
    """Structured semantic-parse output.

    Fields:
        intent_id: int -- recovered intent index (argmax over intent codebook)
        slot_ids: np.ndarray shape [n_roles] int64 -- per-role slot indices
        intent_conf: float -- cosine similarity of input_hd to recovered intent
                              prototype (higher = more confident)
        slot_confs: np.ndarray shape [n_roles] float32 -- per-role cosine
                     similarity of unbound query to recovered slot vector
    """
    intent_id: int
    slot_ids: np.ndarray
    intent_conf: float
    slot_confs: np.ndarray


@dataclass
class BatchParseResult:
    """Batched semantic-parse output.

    Fields:
        intent_ids: np.ndarray shape [n_batch] int64
        slot_ids: np.ndarray shape [n_batch, n_roles] int64
        intent_confs: np.ndarray shape [n_batch] float32
        slot_confs: np.ndarray shape [n_batch, n_roles] float32
    """
    intent_ids: np.ndarray
    slot_ids: np.ndarray
    intent_confs: np.ndarray
    slot_confs: np.ndarray


def _cosine_row_maxes(queries: np.ndarray, codebook: np.ndarray) -> tuple:
    """Return (argmax_idx [B], max_cosine [B]).

    queries: [B, N_DIM] float32
    codebook: [M, N_DIM] float32

    Uses unit-normalization on both sides so returned value is a true cosine
    similarity in [-1, 1] regardless of INTENT_WEIGHT bundle scaling.
    """
    q = queries.astype(np.float32)
    cb = codebook.astype(np.float32)
    q_norm = np.linalg.norm(q, axis=1, keepdims=True)
    q_norm = np.where(q_norm < 1e-12, 1.0, q_norm)
    cb_norm = np.linalg.norm(cb, axis=1, keepdims=True)
    cb_norm = np.where(cb_norm < 1e-12, 1.0, cb_norm)
    q_u = q / q_norm
    cb_u = cb / cb_norm
    scores = q_u @ cb_u.T  # [B, M]
    idx = scores.argmax(axis=1).astype(np.int64)
    conf = scores.max(axis=1).astype(np.float32)
    return idx, conf


class SemanticParser:
    """Compositional HD-bundle parser: recover (intent_id, slot_ids) from a bundle.

    Storage strategy: SHARDED (per-role slot dictionaries; disjoint slot
    vectors across roles).

    Mechanism (single query):
        1. intent_id = argmax_i cos(input_hd, intent_codebook[i])
        2. For each role r:
             unbound_r = hd_unbind(input_hd, role_keys[r])
             slot_id_r = argmax_j cos(unbound_r, slot_dicts[r][j])

    Args:
        intent_clf: IntentClassifier providing .codebook attribute
                    [n_intents, n_dim] float32 (bipolar prototypes).
                    Note: parse uses direct k_NN_lookup on .codebook; the
                    Hebbian W matrix is NOT used because Hebbian training on
                    compositional bundles is a narrow regime (see source cell
                    docstring).
        slot_dicts: List of length n_roles, each entry [slot_dict_size_per_role,
                    n_dim] float32 (bipolar per-role SHARDED dictionaries).
        role_keys: np.ndarray shape [n_roles, n_dim] float32 (bipolar role
                   keys for HRR unbind).
        n_roles: number of roles (must match len(slot_dicts) and
                 role_keys.shape[0]).
        slot_dict_size_per_role: number of slot vectors per role (must match
                                 slot_dicts[r].shape[0] for every r).

    Public API:
        parse(input_hd) -> ParseResult
        parse_batch(input_hds) -> BatchParseResult
    """

    def __init__(
        self,
        intent_clf: IntentClassifier,
        slot_dicts: Sequence[np.ndarray],
        role_keys: np.ndarray,
        n_roles: int,
        slot_dict_size_per_role: int,
    ) -> None:
        if not hasattr(intent_clf, "codebook"):
            raise ValueError("intent_clf must expose a .codebook attribute")
        if len(slot_dicts) != n_roles:
            raise ValueError(
                f"slot_dicts length {len(slot_dicts)} != n_roles {n_roles}")
        if role_keys.shape[0] != n_roles:
            raise ValueError(
                f"role_keys.shape[0] {role_keys.shape[0]} != n_roles {n_roles}")
        n_dim = intent_clf.codebook.shape[1]
        if role_keys.shape[1] != n_dim:
            raise ValueError(
                f"role_keys n_dim {role_keys.shape[1]} != intent codebook "
                f"n_dim {n_dim}")
        for r, sd in enumerate(slot_dicts):
            if sd.shape != (slot_dict_size_per_role, n_dim):
                raise ValueError(
                    f"slot_dicts[{r}].shape {sd.shape} != "
                    f"({slot_dict_size_per_role}, {n_dim})")
        self.intent_clf = intent_clf
        self.slot_dicts = [np.asarray(sd, dtype=np.float32) for sd in slot_dicts]
        self.role_keys = np.asarray(role_keys, dtype=np.float32)
        self.n_roles = int(n_roles)
        self.slot_dict_size_per_role = int(slot_dict_size_per_role)
        self.n_dim = int(n_dim)

    def parse(self, input_hd: np.ndarray) -> ParseResult:
        """Recover intent + slots from a single compositional HD bundle.

        input_hd: [n_dim] float32 pre-composed bundle
        Returns ParseResult.
        """
        if input_hd.shape != (self.n_dim,):
            raise ValueError(
                f"input_hd shape {input_hd.shape} != ({self.n_dim},)")
        # Intent leg: cosine argmax on intent codebook.
        intent_idx, intent_conf = _cosine_row_maxes(
            input_hd[None, :], self.intent_clf.codebook)
        intent_id = int(intent_idx[0])
        intent_confidence = float(intent_conf[0])
        # Slot leg: per-role unbind + cleanup.
        slot_ids = np.zeros(self.n_roles, dtype=np.int64)
        slot_confs = np.zeros(self.n_roles, dtype=np.float32)
        input_t = torch.from_numpy(input_hd.astype(np.float32))
        for r in range(self.n_roles):
            role_key_t = torch.from_numpy(self.role_keys[r])
            unbound_t = hd_unbind(input_t, role_key_t)
            unbound = unbound_t.numpy().astype(np.float32)
            idx, conf = _cosine_row_maxes(
                unbound[None, :], self.slot_dicts[r])
            slot_ids[r] = int(idx[0])
            slot_confs[r] = float(conf[0])
        return ParseResult(
            intent_id=intent_id,
            slot_ids=slot_ids,
            intent_conf=intent_confidence,
            slot_confs=slot_confs,
        )

    def parse_batch(self, input_hds: np.ndarray) -> BatchParseResult:
        """Recover intent + slots for a batch of compositional HD bundles.

        input_hds: [n_batch, n_dim] float32
        Returns BatchParseResult.

        Efficiency: intent leg is vectorized across the batch. Slot leg
        vectorizes across the batch for each role independently (one
        [B, n_dim] @ [slot_dict_size, n_dim].T per role).
        """
        if input_hds.ndim != 2 or input_hds.shape[1] != self.n_dim:
            raise ValueError(
                f"input_hds shape {input_hds.shape} != (B, {self.n_dim})")
        n = input_hds.shape[0]
        # Intent leg: batched cosine argmax.
        intent_ids, intent_confs = _cosine_row_maxes(
            input_hds, self.intent_clf.codebook)
        slot_ids = np.zeros((n, self.n_roles), dtype=np.int64)
        slot_confs = np.zeros((n, self.n_roles), dtype=np.float32)
        input_t = torch.from_numpy(input_hds.astype(np.float32))
        for r in range(self.n_roles):
            role_key_t = torch.from_numpy(self.role_keys[r])
            # Broadcast unbind across batch: hd_unbind supports batch via
            # torch elementwise op when inputs share final dim.
            # .contiguous() required: expand_as produces a non-contiguous view
            # and Windows MKL FFT rejects it with "Inconsistent configuration
            # parameters". Mirror of the fix at cell line 758 (M1.10 v1).
            role_key_expanded = role_key_t.unsqueeze(0).expand_as(input_t).contiguous()
            unbound_t = hd_unbind(input_t, role_key_expanded)
            unbound = unbound_t.numpy().astype(np.float32)
            idx, conf = _cosine_row_maxes(unbound, self.slot_dicts[r])
            slot_ids[:, r] = idx
            slot_confs[:, r] = conf
        return BatchParseResult(
            intent_ids=intent_ids,
            slot_ids=slot_ids,
            intent_confs=intent_confs,
            slot_confs=slot_confs,
        )


# ------------------------------------------------------------------------------
# Formula selftests (10 selftests; mirror smoke-arm expectations on synthetic
# clean bundles built with the same encoder used in the source cell).
# ------------------------------------------------------------------------------

def _make_role_keys(n_dim: int, n_roles: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(int(seed) * 4093 + 71)
    return (rng.integers(0, 2, size=(n_roles, n_dim)) * 2 - 1).astype(np.float32)


def _make_slot_dicts(n_dim: int, n_roles: int, slot_size: int,
                     seed: int) -> List[np.ndarray]:
    dicts = []
    for r in range(n_roles):
        rng = np.random.default_rng(int(seed) * 8191 + r * 251 + 13)
        d = (rng.integers(0, 2, size=(slot_size, n_dim)) * 2 - 1).astype(np.float32)
        dicts.append(d)
    return dicts


def _encode_bundle(
    intent_id: int,
    slot_ids: np.ndarray,
    intent_codebook: np.ndarray,
    role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
    intent_weight: float,
) -> np.ndarray:
    n_dim = intent_codebook.shape[1]
    n_roles = len(slot_dicts)
    role_keys_t = torch.from_numpy(role_keys)
    bundle = (intent_weight * intent_codebook[intent_id]).astype(np.float32)
    for r in range(n_roles):
        slot_hd = slot_dicts[r][int(slot_ids[r])]
        bound = hd_bind(role_keys_t[r], torch.from_numpy(slot_hd))
        bundle = bundle + bound.numpy().astype(np.float32)
    return bundle


def _build_parser(seed: int, n_dim: int = 8192, n_intents: int = 20,
                  n_roles: int = 5, slot_size: int = 50) -> SemanticParser:
    """Build a SemanticParser wired to random codebooks (CG-anchored N_DIM=8192
    per Plate 1995 HRR capacity floor for K=5 role bundle)."""
    clf = IntentClassifier(n_intents=n_intents, n_dim=n_dim, seed=seed)
    role_keys = _make_role_keys(n_dim, n_roles, seed)
    slot_dicts = _make_slot_dicts(n_dim, n_roles, slot_size, seed)
    return SemanticParser(
        intent_clf=clf,
        slot_dicts=slot_dicts,
        role_keys=role_keys,
        n_roles=n_roles,
        slot_dict_size_per_role=slot_size,
    )


def _selftest_1_single_parse_perfect_recovery() -> None:
    """Selftest 1: single-bundle parse recovers intent + all slots (100%)
    on clean synthetic input at N=4096, K=5 roles, W=8.0."""
    parser = _build_parser(seed=11)
    rng = np.random.default_rng(1234)
    intent_id = int(rng.integers(0, parser.intent_clf.n_intents))
    slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                            size=parser.n_roles).astype(np.int64)
    bundle = _encode_bundle(intent_id, slot_ids, parser.intent_clf.codebook,
                            parser.role_keys, parser.slot_dicts,
                            CG_INTENT_WEIGHT_DEFAULT)
    res = parser.parse(bundle)
    if res.intent_id != intent_id:
        raise AssertionError(
            f"selftest_1 intent recovery failed: got {res.intent_id} "
            f"want {intent_id}")
    if not np.array_equal(res.slot_ids, slot_ids):
        raise AssertionError(
            f"selftest_1 slot recovery failed: got {res.slot_ids.tolist()} "
            f"want {slot_ids.tolist()}")


def _selftest_2_batch_matches_scalar() -> None:
    """Selftest 2: parse_batch on a batch of 8 bundles matches per-item parse."""
    parser = _build_parser(seed=13)
    rng = np.random.default_rng(2)
    n_batch = 8
    intent_ids = rng.integers(0, parser.intent_clf.n_intents,
                              size=n_batch).astype(np.int64)
    slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                            size=(n_batch, parser.n_roles)).astype(np.int64)
    bundles = np.stack([
        _encode_bundle(int(intent_ids[i]), slot_ids[i],
                       parser.intent_clf.codebook, parser.role_keys,
                       parser.slot_dicts, CG_INTENT_WEIGHT_DEFAULT)
        for i in range(n_batch)
    ], axis=0)
    batch_res = parser.parse_batch(bundles)
    for i in range(n_batch):
        item_res = parser.parse(bundles[i])
        if item_res.intent_id != int(batch_res.intent_ids[i]):
            raise AssertionError(
                f"selftest_2 intent batch/scalar mismatch at i={i}")
        if not np.array_equal(item_res.slot_ids, batch_res.slot_ids[i]):
            raise AssertionError(
                f"selftest_2 slot batch/scalar mismatch at i={i}")


def _selftest_3_batch_perfect_recovery_on_clean() -> None:
    """Selftest 3: batch of 20 clean bundles recovers intent_acc=1.0 and
    slot_fill=1.0 (matches ARM_BASELINE_SYMBOLIC positive control envelope
    and mirrors smoke-arm expectation of >=0.85 intent, 1.0 slot on clean)."""
    parser = _build_parser(seed=17)
    rng = np.random.default_rng(3)
    n_batch = 20
    intent_ids = rng.integers(0, parser.intent_clf.n_intents,
                              size=n_batch).astype(np.int64)
    slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                            size=(n_batch, parser.n_roles)).astype(np.int64)
    bundles = np.stack([
        _encode_bundle(int(intent_ids[i]), slot_ids[i],
                       parser.intent_clf.codebook, parser.role_keys,
                       parser.slot_dicts, CG_INTENT_WEIGHT_DEFAULT)
        for i in range(n_batch)
    ], axis=0)
    res = parser.parse_batch(bundles)
    intent_acc = float(np.mean(res.intent_ids == intent_ids))
    slot_fill = float(np.mean(res.slot_ids == slot_ids))
    if intent_acc < CG_INTENT_ACC_HP_FLOOR:
        raise AssertionError(
            f"selftest_3 intent_acc {intent_acc:.3f} < HP floor "
            f"{CG_INTENT_ACC_HP_FLOOR}")
    if slot_fill < 1.0:
        raise AssertionError(
            f"selftest_3 clean-bundle slot_fill {slot_fill:.3f} < 1.0 "
            f"(clean recovery must be perfect)")


def _selftest_4_confidence_positive_for_correct() -> None:
    """Selftest 4: intent_conf and all slot_confs are strictly positive on
    correctly-parsed clean bundles (cosine > 0 for on-target prototype)."""
    parser = _build_parser(seed=19)
    rng = np.random.default_rng(4)
    intent_id = int(rng.integers(0, parser.intent_clf.n_intents))
    slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                            size=parser.n_roles).astype(np.int64)
    bundle = _encode_bundle(intent_id, slot_ids, parser.intent_clf.codebook,
                            parser.role_keys, parser.slot_dicts,
                            CG_INTENT_WEIGHT_DEFAULT)
    res = parser.parse(bundle)
    if res.intent_conf <= 0.0:
        raise AssertionError(
            f"selftest_4 intent_conf {res.intent_conf:.3f} not positive")
    if not np.all(res.slot_confs > 0.0):
        raise AssertionError(
            f"selftest_4 slot_confs {res.slot_confs.tolist()} not all positive")


def _selftest_5_shuffled_role_keys_collapse() -> None:
    """Selftest 5: parsing with cyclic-shifted role_keys (derangement) causes
    slot_fill to collapse below the shuffled-slot ceiling 0.20 -- reproducing
    ARM_SHUFFLED_ROLE_KEYS sanity control from source cell."""
    parser = _build_parser(seed=23)
    rng = np.random.default_rng(5)
    n_batch = 30
    intent_ids = rng.integers(0, parser.intent_clf.n_intents,
                              size=n_batch).astype(np.int64)
    slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                            size=(n_batch, parser.n_roles)).astype(np.int64)
    bundles = np.stack([
        _encode_bundle(int(intent_ids[i]), slot_ids[i],
                       parser.intent_clf.codebook, parser.role_keys,
                       parser.slot_dicts, CG_INTENT_WEIGHT_DEFAULT)
        for i in range(n_batch)
    ], axis=0)
    # Build a mutated parser with cyclic-shifted role_keys (derangement).
    perm = np.roll(np.arange(parser.n_roles), shift=1)
    shuffled_keys = parser.role_keys[perm].copy()
    shuffled_parser = SemanticParser(
        intent_clf=parser.intent_clf,
        slot_dicts=parser.slot_dicts,
        role_keys=shuffled_keys,
        n_roles=parser.n_roles,
        slot_dict_size_per_role=parser.slot_dict_size_per_role,
    )
    res = shuffled_parser.parse_batch(bundles)
    slot_fill = float(np.mean(res.slot_ids == slot_ids))
    if slot_fill > CG_SHUFFLED_SLOT_CEILING:
        raise AssertionError(
            f"selftest_5 shuffled slot_fill {slot_fill:.3f} > ceiling "
            f"{CG_SHUFFLED_SLOT_CEILING} (role-binding not doing work)")


def _selftest_6_shape_annotations() -> None:
    """Selftest 6: ParseResult and BatchParseResult have correct shapes and
    dtypes."""
    parser = _build_parser(seed=11, n_intents=10, slot_size=25)
    rng = np.random.default_rng(6)
    intent_id = int(rng.integers(0, parser.intent_clf.n_intents))
    slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                            size=parser.n_roles).astype(np.int64)
    bundle = _encode_bundle(intent_id, slot_ids, parser.intent_clf.codebook,
                            parser.role_keys, parser.slot_dicts,
                            CG_INTENT_WEIGHT_DEFAULT)
    r = parser.parse(bundle)
    if not isinstance(r.intent_id, int):
        raise AssertionError(f"selftest_6 intent_id not int: {type(r.intent_id)}")
    if r.slot_ids.shape != (parser.n_roles,):
        raise AssertionError(
            f"selftest_6 slot_ids shape {r.slot_ids.shape} != "
            f"({parser.n_roles},)")
    if r.slot_ids.dtype != np.int64:
        raise AssertionError(
            f"selftest_6 slot_ids dtype {r.slot_ids.dtype} != int64")
    if r.slot_confs.shape != (parser.n_roles,):
        raise AssertionError(
            f"selftest_6 slot_confs shape {r.slot_confs.shape} != "
            f"({parser.n_roles},)")
    br = parser.parse_batch(bundle[None, :])
    if br.intent_ids.shape != (1,):
        raise AssertionError(f"selftest_6 batch intent_ids shape wrong")
    if br.slot_ids.shape != (1, parser.n_roles):
        raise AssertionError(f"selftest_6 batch slot_ids shape wrong")


def _selftest_7_ctor_validation() -> None:
    """Selftest 7: constructor rejects mismatched shapes."""
    parser = _build_parser(seed=11, n_intents=10, slot_size=25)
    ok = False
    try:
        SemanticParser(
            intent_clf=parser.intent_clf,
            slot_dicts=parser.slot_dicts[:-1],  # length mismatch
            role_keys=parser.role_keys,
            n_roles=parser.n_roles,
            slot_dict_size_per_role=parser.slot_dict_size_per_role,
        )
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError(
            "selftest_7 expected ValueError on slot_dicts length mismatch")
    ok = False
    try:
        bad_keys = parser.role_keys[:, :parser.n_dim - 1].copy()  # wrong n_dim
        SemanticParser(
            intent_clf=parser.intent_clf,
            slot_dicts=parser.slot_dicts,
            role_keys=bad_keys,
            n_roles=parser.n_roles,
            slot_dict_size_per_role=parser.slot_dict_size_per_role,
        )
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError(
            "selftest_7 expected ValueError on role_keys n_dim mismatch")


def _selftest_8_parse_rejects_wrong_shape() -> None:
    """Selftest 8: parse() rejects input_hd with wrong shape."""
    parser = _build_parser(seed=11, n_intents=10, slot_size=25)
    ok = False
    try:
        parser.parse(np.zeros(parser.n_dim + 1, dtype=np.float32))
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError(
            "selftest_8 expected ValueError on wrong-shape input_hd")
    ok = False
    try:
        parser.parse_batch(np.zeros((3, parser.n_dim - 1), dtype=np.float32))
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError(
            "selftest_8 expected ValueError on wrong-shape input_hds batch")


def _selftest_9_per_role_slot_independence() -> None:
    """Selftest 9: changing slot_id for role r does NOT affect recovered
    slot_id for role r' != r (per-role SHARDED storage guarantee)."""
    parser = _build_parser(seed=11)
    rng = np.random.default_rng(9)
    intent_id = int(rng.integers(0, parser.intent_clf.n_intents))
    slot_ids_a = rng.integers(0, parser.slot_dict_size_per_role,
                              size=parser.n_roles).astype(np.int64)
    slot_ids_b = slot_ids_a.copy()
    # Flip only role 2's slot
    role_to_change = 2
    new_slot = (slot_ids_a[role_to_change] + 7) % parser.slot_dict_size_per_role
    slot_ids_b[role_to_change] = new_slot
    bundle_a = _encode_bundle(intent_id, slot_ids_a,
                              parser.intent_clf.codebook, parser.role_keys,
                              parser.slot_dicts, CG_INTENT_WEIGHT_DEFAULT)
    bundle_b = _encode_bundle(intent_id, slot_ids_b,
                              parser.intent_clf.codebook, parser.role_keys,
                              parser.slot_dicts, CG_INTENT_WEIGHT_DEFAULT)
    res_a = parser.parse(bundle_a)
    res_b = parser.parse(bundle_b)
    # Other roles must recover unchanged.
    for r in range(parser.n_roles):
        if r == role_to_change:
            continue
        if res_a.slot_ids[r] != res_b.slot_ids[r]:
            raise AssertionError(
                f"selftest_9 role {r} slot changed under unrelated role edit: "
                f"a={res_a.slot_ids[r]} b={res_b.slot_ids[r]}")
    # Changed role must reflect the new slot.
    if res_b.slot_ids[role_to_change] != new_slot:
        raise AssertionError(
            f"selftest_9 changed role slot recovery failed: "
            f"got {res_b.slot_ids[role_to_change]} want {new_slot}")


def _selftest_10_ten_random_seeds_clean_recovery() -> None:
    """Selftest 10: 10 random (intent, slot_ids) tuples parsed cleanly must
    ALL recover correctly (deterministic clean-bundle regime). Mirrors
    ARM_BASELINE_SYMBOLIC positive control -- clean synthetic bundles at
    N_DIM=4096, K=5 roles, W=8.0 are fully separable."""
    parser = _build_parser(seed=11)
    rng = np.random.default_rng(10)
    # Use 30 internal samples to keep binomial variance under +/- 0.13 at
    # true rate 0.85 (n=10 has +/- 0.28 CI which is wider than the 0.05 slack
    # between measured mean 0.85 and floor).
    n_selftests = 30
    intents_ok = 0
    slots_ok = 0
    for _ in range(n_selftests):
        intent_id = int(rng.integers(0, parser.intent_clf.n_intents))
        slot_ids = rng.integers(0, parser.slot_dict_size_per_role,
                                size=parser.n_roles).astype(np.int64)
        bundle = _encode_bundle(intent_id, slot_ids,
                                parser.intent_clf.codebook, parser.role_keys,
                                parser.slot_dicts, CG_INTENT_WEIGHT_DEFAULT)
        res = parser.parse(bundle)
        if res.intent_id == intent_id:
            intents_ok += 1
        if np.array_equal(res.slot_ids, slot_ids):
            slots_ok += 1
    intent_frac = intents_ok / n_selftests
    slot_frac = slots_ok / n_selftests
    if intent_frac < CG_INTENT_ACC_HP_FLOOR:
        raise AssertionError(
            f"selftest_10 intent recovery {intent_frac:.2f} < HP floor "
            f"{CG_INTENT_ACC_HP_FLOOR}")
    if slot_frac < 1.0:
        raise AssertionError(
            f"selftest_10 slot recovery {slot_frac:.2f} < 1.0 "
            f"(clean-bundle regime must be perfect)")


_SELFTESTS = [
    ("1_single_parse_perfect_recovery", _selftest_1_single_parse_perfect_recovery),
    ("2_batch_matches_scalar", _selftest_2_batch_matches_scalar),
    ("3_batch_perfect_recovery_on_clean", _selftest_3_batch_perfect_recovery_on_clean),
    ("4_confidence_positive_for_correct", _selftest_4_confidence_positive_for_correct),
    ("5_shuffled_role_keys_collapse", _selftest_5_shuffled_role_keys_collapse),
    ("6_shape_annotations", _selftest_6_shape_annotations),
    ("7_ctor_validation", _selftest_7_ctor_validation),
    ("8_parse_rejects_wrong_shape", _selftest_8_parse_rejects_wrong_shape),
    ("9_per_role_slot_independence", _selftest_9_per_role_slot_independence),
    ("10_ten_random_seeds_clean_recovery", _selftest_10_ten_random_seeds_clean_recovery),
]


def _run_all_selftests() -> dict:
    passed: List[str] = []
    failed: List[tuple] = []
    for name, fn in _SELFTESTS:
        try:
            fn()
            passed.append(name)
            print(f"[semantic_parser selftest] PASS {name}")
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"[semantic_parser selftest] FAIL {name}: {e}")
    return {
        "n_passed": len(passed),
        "n_failed": len(failed),
        "passed": passed,
        "failed": failed,
        "cg_source": "M1.9 v1 seed 11/17/23 Skunkworks CG a508452e 2026-07-02",
    }


if __name__ == "__main__":
    import sys
    result = _run_all_selftests()
    if result["n_failed"] > 0:
        print(f"[semantic_parser selftest] FAIL {result['n_failed']} of "
              f"{len(_SELFTESTS)} selftests failed")
        sys.exit(1)
    print(f"[semantic_parser selftest] PASS {result['n_passed']} of "
          f"{len(_SELFTESTS)} selftests passed")
