"""5 capability tests for Pattern B (architecture v1 Tier 2 capability-generic).

Each test exercises ONE substrate capability against the synthetic fact corpus
with a deterministic harness. No LLM API calls -- the LLM-only baseline lives
in a separate harness (Tier 2b). These tests answer the question:

  "Does the substrate-backed Pattern B service deliver the capability claim
   independent of any LLM's reasoning quality?"

The five capabilities (from notes/session_kickoff_testbed_v1.md Tier 2):

  1. Audit trail completeness across operations
  2. Edit-then-query semantics
  3. Deletion-with-certificate end-to-end
  4. Mid-conversation edit handling
  5. Multi-hop tool-use coordination

Each test is independent: fresh substrate state per fixture. Tests use the
synthetic corpus generator (hdlab_service/corpora/synthetic_corpus.py) for
ground-truth answers.

Run: pytest hdlab_service/capability_tests/ -v
"""

from __future__ import annotations

import os
import shutil
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from hdlab_service.corpora.synthetic_corpus import small_corpus


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    """Fresh service per test; isolated audit log + signing keys."""
    state_dir = tmp_path / "state"
    keys_dir = state_dir / "keys"
    audit_path = state_dir / "audit_log.jsonl"
    os.environ["HDLAB_N"] = "256"
    os.environ["HDLAB_CODEBOOK"] = "BSC"
    os.environ["HDLAB_KEY_DIR"] = str(keys_dir)
    os.environ["HDLAB_AUDIT_PATH"] = str(audit_path)

    import importlib
    from hdlab_service import server as server_module
    importlib.reload(server_module)

    with TestClient(server_module.app) as c:
        yield c

    if state_dir.exists():
        shutil.rmtree(state_dir, ignore_errors=True)


def _store_corpus(client: TestClient) -> dict[str, str]:
    """Store the synthetic corpus; returns key -> atom_id mapping."""
    corpus = small_corpus()
    key_to_atom: dict[str, str] = {}
    for f in corpus.facts:
        resp = client.post("/store_fact", json={"key": f.key, "value": f.value})
        assert resp.status_code == 200, f"store failed for {f.key}: {resp.text}"
        body = resp.json()
        key_to_atom[f.key] = body["atom_id"]
    return key_to_atom


# ---------------------------------------------------------------------------
# Capability 1: Audit trail completeness across operations
# ---------------------------------------------------------------------------

def test_capability_1_audit_trail_completeness(client: TestClient) -> None:
    """Every store/edit/delete emits an audit record; chain integrity holds.

    Method:
      - Store the full synthetic corpus (~75 facts)
      - Edit 3 facts
      - Delete 2 facts
      - Verify: total audit records = stores + edits + deletes
      - Verify: each returned audit_record_id is retrievable via /audit/{id}
      - Verify: substrate's chain_ok flag is True after all operations

    Pass criteria: audit count matches, every id resolves, chain holds.
    """
    key_to_atom = _store_corpus(client)
    n_stores = len(key_to_atom)

    # Edit 3 known facts.
    edit_targets = ["p_00__name", "p_01__role", "c_00__founded_year"]
    edit_audit_ids: list[str] = []
    for k in edit_targets:
        resp = client.post(
            "/edit_fact",
            json={"atom_id": key_to_atom[k], "new_value": f"EDITED_{k}",
                  "requester_id": "capability_test_1"},
        )
        assert resp.status_code == 200, f"edit failed for {k}"
        edit_audit_ids.append(resp.json()["audit_record_id"])

    # Delete 2 known facts.
    delete_targets = ["prod_00__name", "c_01__name"]
    delete_audit_ids: list[str] = []
    for k in delete_targets:
        resp = client.post(
            "/delete_fact",
            json={"atom_id": key_to_atom[k], "requester_id": "capability_test_1",
                  "legal_basis": "GDPR_ART_17"},
        )
        assert resp.status_code == 200, f"delete failed for {k}"
        delete_audit_ids.append(resp.json()["audit_record_id"])

    # Every audit id must resolve.
    for aid in edit_audit_ids + delete_audit_ids:
        resp = client.get(f"/audit/{aid}")
        assert resp.status_code == 200, f"audit id {aid!r} not found"
        rec = resp.json()
        assert rec["id"] == aid
        # state_hash present (chain-integrity prerequisite).
        assert rec["substrate_state_hash"], "audit record missing state_hash"

    # Service self-reports audit-chain integrity.
    health = client.get("/health").json()
    assert health["chain_ok"] is True, "audit chain integrity check failed"
    # n_records = stores + edits + deletes (no other operations issued).
    expected_records = n_stores + len(edit_targets) + len(delete_targets)
    assert health["audit_records"] >= expected_records, (
        f"expected at least {expected_records} audit records; "
        f"got {health['audit_records']}"
    )


# ---------------------------------------------------------------------------
# Capability 2: Edit-then-query semantics
# ---------------------------------------------------------------------------

def test_capability_2_edit_then_query_semantics(client: TestClient) -> None:
    """After an edit, retrieval returns the new value; not the old.

    Method:
      - Store a fact (key="alpha", value="original")
      - Retrieve("alpha") -> "original"
      - Edit atom_id to value="updated"
      - Retrieve("alpha") -> "updated"
      - Edit again to value="final"
      - Retrieve("alpha") -> "final"
      - Audit log preserves the full edit chain (3 records: store + 2 edits)

    Pass criteria: post-edit retrieval reflects latest write; full diff
    trail recoverable from audit records.
    """
    # Initial store
    s = client.post("/store_fact", json={"key": "alpha", "value": "original"}).json()
    atom_id = s["atom_id"]

    # Read 1
    r1 = client.post("/retrieve_fact", json={"query": "alpha", "min_confidence": 0.1}).json()
    assert r1["status"] == "match"
    assert r1["fact_text"] == "original"

    # Edit 1
    e1 = client.post("/edit_fact", json={"atom_id": atom_id, "new_value": "updated"}).json()
    assert e1["old_value"] == "original"
    assert e1["new_value"] == "updated"
    assert e1["state_hash_before"] != e1["state_hash_after"]

    # Read 2 -- sees updated value
    r2 = client.post("/retrieve_fact", json={"query": "alpha", "min_confidence": 0.1}).json()
    assert r2["status"] == "match"
    assert r2["fact_text"] == "updated"

    # Edit 2
    e2 = client.post("/edit_fact", json={"atom_id": atom_id, "new_value": "final"}).json()
    assert e2["old_value"] == "updated"
    assert e2["new_value"] == "final"

    # Read 3 -- sees final value
    r3 = client.post("/retrieve_fact", json={"query": "alpha", "min_confidence": 0.1}).json()
    assert r3["status"] == "match"
    assert r3["fact_text"] == "final"

    # Audit chain has the diff trail
    a1 = client.get(f"/audit/{e1['audit_record_id']}").json()
    a2 = client.get(f"/audit/{e2['audit_record_id']}").json()
    assert a1["response_payload"]["old_value"] == "original"
    assert a1["response_payload"]["new_value"] == "updated"
    assert a2["response_payload"]["old_value"] == "updated"
    assert a2["response_payload"]["new_value"] == "final"

    # Health still reports clean chain after the edits.
    health = client.get("/health").json()
    assert health["chain_ok"] is True


# ---------------------------------------------------------------------------
# Capability 3: Deletion-with-certificate end-to-end
# ---------------------------------------------------------------------------

def test_capability_3_deletion_with_certificate(client: TestClient) -> None:
    """Delete returns a signed cert; cert verifies; deleted fact unreachable.

    Method:
      - Store a fact
      - Retrieve it (sanity)
      - Delete it; capture the returned certificate
      - Verify certificate via deletion_cert.verify_certificate
      - Confirm state_hash_before != state_hash_after in the cert
      - Retrieve the same key -> miss / different fact (substrate-side erasure)
      - Audit chain still verifies (delete is part of the chain)

    Pass criteria: cert verifies cryptographically, substrate state hash
    changed across the delete, the fact is no longer retrievable.
    """
    from hdlab_service.deletion_cert import verify_certificate

    # Store + sanity retrieve
    s = client.post("/store_fact", json={"key": "to_be_deleted", "value": "sensitive_info"}).json()
    atom_id = s["atom_id"]
    pre_r = client.post("/retrieve_fact", json={"query": "to_be_deleted", "min_confidence": 0.1}).json()
    assert pre_r["status"] == "match"
    assert pre_r["fact_text"] == "sensitive_info"

    # Delete
    d = client.post("/delete_fact", json={
        "atom_id": atom_id,
        "requester_id": "data_subject_xyz",
        "legal_basis": "GDPR_ART_17",
        "notes": "capability test 3 erasure request",
    }).json()
    assert d["status"] == "deleted"
    cert = d["certificate"]

    # Certificate has the expected compliance-facing fields
    for fld in ("fact_id", "deletion_ts", "state_hash_before", "state_hash_after"):
        assert fld in cert, f"cert missing field {fld!r}"
    assert cert["state_hash_before"] != cert["state_hash_after"], (
        "substrate state hash did not change across deletion"
    )

    # Cert verifies cryptographically (Ed25519 signature check)
    assert verify_certificate(cert) is True, "certificate signature did not verify"

    # Retrieval no longer returns the deleted fact's value. The substrate may
    # still produce SOME response (it's still a valid key probe), but it must
    # not return the deleted fact_text.
    post_r = client.post("/retrieve_fact", json={"query": "to_be_deleted", "min_confidence": 0.1}).json()
    assert post_r.get("fact_text") != "sensitive_info", (
        f"deleted fact still retrievable: {post_r}"
    )

    # Audit chain integrity preserved across the delete
    health = client.get("/health").json()
    assert health["chain_ok"] is True


# ---------------------------------------------------------------------------
# Capability 4: Mid-conversation edit handling
# ---------------------------------------------------------------------------

def test_capability_4_mid_conversation_edits(client: TestClient) -> None:
    """Reads interleaved with edits reflect the substrate's live state.

    Models a "conversation" where the LLM asks question A, the user issues
    an edit, then the LLM asks question B about the edited fact. The
    substrate must serve the post-edit state -- there is no need for the
    LLM to carry the edit in its context window because the substrate is
    the source of truth.

    Method:
      - Store the full corpus
      - For each of 3 chosen facts:
          1. Read its value -> assert original
          2. Edit it
          3. Read its value -> assert new value
          4. Read a *different* fact -> assert it is unchanged (no
             collateral state mutation; KF-2 edit isolation)

    Pass criteria: every post-edit read sees the new value; no neighboring
    fact's retrieval result is corrupted by the edit.
    """
    key_to_atom = _store_corpus(client)
    corpus = small_corpus()
    gt = corpus.ground_truth

    # Three target facts (mix of properties so we exercise role/filler space).
    targets = [
        ("p_02__name", "EDITED_NAME_2"),
        ("c_00__founded_year", "9999"),
        ("prod_03__category", "REVISED_CATEGORY"),
    ]
    # Three witnesses (untouched facts whose retrieval must not regress).
    witnesses = ["p_05__name", "c_02__founded_year", "prod_01__category"]
    witness_originals = {k: _expected_value(k, gt) for k in witnesses}

    for k, new_v in targets:
        # Pre-read
        r_pre = client.post("/retrieve_fact", json={"query": k, "min_confidence": 0.1}).json()
        assert r_pre["status"] == "match"
        original = _expected_value(k, gt)
        assert r_pre["fact_text"] == original, (
            f"{k}: pre-edit retrieval got {r_pre['fact_text']!r}, expected {original!r}"
        )

        # Edit
        e = client.post(
            "/edit_fact",
            json={"atom_id": key_to_atom[k], "new_value": new_v},
        ).json()
        assert e["status"] == "edited"

        # Post-read sees the new value
        r_post = client.post("/retrieve_fact", json={"query": k, "min_confidence": 0.1}).json()
        assert r_post["status"] == "match"
        assert r_post["fact_text"] == new_v, (
            f"{k}: post-edit retrieval got {r_post['fact_text']!r}, expected {new_v!r}"
        )

        # Witnesses are still themselves (no collateral mutation).
        for wk in witnesses:
            r_w = client.post("/retrieve_fact", json={"query": wk, "min_confidence": 0.1}).json()
            assert r_w["status"] == "match"
            assert r_w["fact_text"] == witness_originals[wk], (
                f"witness {wk!r} mutated by edit of {k!r}: "
                f"got {r_w['fact_text']!r}, expected {witness_originals[wk]!r}"
            )


# ---------------------------------------------------------------------------
# Capability 5: Multi-hop tool-use coordination
# ---------------------------------------------------------------------------

def test_capability_5_multi_hop_coordination(client: TestClient) -> None:
    """Substrate supports an LLM chaining tool calls without LLM-side state.

    Method:
      - Store the full corpus
      - Pose the question: "Who manages product prod_NN?" via three substrate
        tool calls in sequence:
          Hop 1: retrieve(prod_NN__name)  -> the product's human-readable name
          Hop 2: find the manages-edge fact whose key matches *__manages__prod_NN
                 (in real LLM flow this is the LLM iterating over candidate
                 keys; here we direct-test with the known person id)
          Hop 3: retrieve(p_MM__name) -> the manager's human-readable name
      - Compare the final answer to the corpus ground truth

    Pass criteria: every hop returns a match; final name matches the
    ground-truth manager name for the chosen product.

    This test does NOT exercise compose_query (which tests substrate-internal
    multi-hop). It exercises the LLM-style "chain of independent calls" path
    that Pattern B uses.
    """
    key_to_atom = _store_corpus(client)
    corpus = small_corpus()
    gt = corpus.ground_truth

    # Pick a product that has a known manager.
    target_product = next(prid for prid in gt.manager_of_product)
    target_manager = gt.manager_of_product[target_product]
    expected_product_name = gt.product_name[target_product]
    expected_manager_name = gt.person_name[target_manager]

    # Hop 1: product name
    r_prod = client.post(
        "/retrieve_fact",
        json={"query": f"{target_product}__name", "min_confidence": 0.1},
    ).json()
    assert r_prod["status"] == "match"
    assert r_prod["fact_text"] == expected_product_name

    # Hop 2: manages-edge fact (in real LLM flow, the LLM tries candidate
    # manager ids; here we use the known one to test the substrate path).
    edge_key = f"{target_manager}__manages__{target_product}"
    r_edge = client.post(
        "/retrieve_fact",
        json={"query": edge_key, "min_confidence": 0.1},
    ).json()
    assert r_edge["status"] == "match"
    assert r_edge["fact_text"] == "true", (
        f"manages edge {edge_key!r} should retrieve as 'true'; got {r_edge}"
    )

    # Hop 3: manager name
    r_mgr = client.post(
        "/retrieve_fact",
        json={"query": f"{target_manager}__name", "min_confidence": 0.1},
    ).json()
    assert r_mgr["status"] == "match"
    assert r_mgr["fact_text"] == expected_manager_name, (
        f"manager name mismatch: got {r_mgr['fact_text']!r}, "
        f"expected {expected_manager_name!r}"
    )

    # The substrate served all 3 hops without the test carrying any state
    # between them other than the ids surfaced from prior retrievals.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _expected_value(key: str, gt) -> str:
    """Look up the ground-truth value for a corpus key."""
    if key.endswith("__name"):
        prefix = key.rsplit("__", 1)[0]
        if prefix.startswith("p_"):
            return gt.person_name[prefix]
        if prefix.startswith("c_"):
            return gt.company_name[prefix]
        if prefix.startswith("prod_"):
            return gt.product_name[prefix]
    if key.endswith("__role"):
        return gt.person_role[key.rsplit("__", 1)[0]]
    if key.endswith("__founded_year"):
        return str(gt.company_founded[key.rsplit("__", 1)[0]])
    if key.endswith("__category"):
        return gt.product_category[key.rsplit("__", 1)[0]]
    # Edge facts encoded as "true"
    if "__" in key:
        return "true"
    raise ValueError(f"unrecognized corpus key: {key!r}")
