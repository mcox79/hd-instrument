"""End-to-end tests for the Pattern B FastAPI substrate service."""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Iterator

import pytest
from fastapi.testclient import TestClient


def _shape_ok(obj: dict, required: list[str]) -> bool:
    return all(k in obj for k in required)


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    """Fresh service instance per test (isolated audit log + keys)."""
    state_dir = tmp_path / "state"
    keys_dir = state_dir / "keys"
    audit_path = state_dir / "audit_log.jsonl"
    os.environ["HDLAB_N"] = "256"
    os.environ["HDLAB_CODEBOOK"] = "BSC"
    os.environ["HDLAB_KEY_DIR"] = str(keys_dir)
    os.environ["HDLAB_AUDIT_PATH"] = str(audit_path)

    # Reload server module so the fixtures pick up env vars at startup.
    import importlib
    from hdlab_service import server as server_module

    importlib.reload(server_module)

    with TestClient(server_module.app) as c:
        yield c

    # Cleanup
    if state_dir.exists():
        shutil.rmtree(state_dir, ignore_errors=True)


def test_health_startup(client: TestClient) -> None:
    """Service starts with substrate loaded."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert _shape_ok(body, ["status", "n", "codebook_size", "audit_records", "chain_ok", "signer_pubkey", "codebook_kind"])
    assert body["status"] == "ok"
    assert body["n"] == 256
    assert body["chain_ok"] is True


def test_retrieve_empty_returns_no_match(client: TestClient) -> None:
    """An empty codebook gracefully returns no_match."""
    resp = client.post("/retrieve_fact", json={"query": "anything", "min_confidence": 0.6})
    assert resp.status_code == 200
    body = resp.json()
    assert _shape_ok(body, ["status", "confidence", "provenance", "audit_record_id"])
    assert body["status"] == "no_match"


def test_store_then_retrieve_roundtrip(client: TestClient) -> None:
    """Storing a fact then retrieving by key returns a match."""
    s = client.post(
        "/store_fact",
        json={"key": "case_smith_v_jones", "value": "Holding for plaintiff."},
    )
    assert s.status_code == 200
    s_body = s.json()
    assert _shape_ok(s_body, ["atom_id", "audit_record_id"])
    assert s_body["atom_id"].startswith("atom_")

    r = client.post(
        "/retrieve_fact",
        json={"query": "case_smith_v_jones", "min_confidence": 0.5},
    )
    assert r.status_code == 200
    r_body = r.json()
    assert r_body["status"] == "match"
    assert r_body["fact_text"] == "Holding for plaintiff."
    assert r_body["confidence"] > 0.5
    assert len(r_body["provenance"]) >= 1


def test_delete_returns_signed_certificate(client: TestClient) -> None:
    """/delete_fact returns an Ed25519-signed cert that independently verifies."""
    s = client.post(
        "/store_fact",
        json={"key": "doomed_fact", "value": "Will be deleted."},
    )
    atom_id = s.json()["atom_id"]

    d = client.post(
        "/delete_fact",
        json={
            "atom_id": atom_id,
            "requester_id": "test_user",
            "legal_basis": "GDPR_ART_17",
        },
    )
    assert d.status_code == 200
    body = d.json()
    assert body["status"] == "deleted"
    cert = body["certificate"]
    for field in (
        "version", "cert_id", "fact_id", "audit_id", "deletion_ts",
        "state_hash_before", "state_hash_after", "signer_pubkey",
        "signing_algorithm", "signature",
    ):
        assert field in cert, f"missing field {field} in cert"
    assert cert["signing_algorithm"] == "Ed25519"
    assert cert["state_hash_before"] != cert["state_hash_after"]

    from hdlab_service.deletion_cert import verify_certificate

    assert verify_certificate(cert) is True

    # Tamper detection
    tampered = dict(cert)
    tampered["fact_id"] = "fact_tampered"
    assert verify_certificate(tampered) is False


def test_delete_unknown_returns_404(client: TestClient) -> None:
    """/delete_fact on unknown atom returns 404."""
    d = client.post(
        "/delete_fact",
        json={"atom_id": "atom_does_not_exist", "requester_id": "x", "legal_basis": "OTHER"},
    )
    assert d.status_code == 404


def test_audit_log_chain_integrity(client: TestClient) -> None:
    """Audit chain stays valid across multiple ops; /audit/{id} round-trip works."""
    client.post("/store_fact", json={"key": "k1", "value": "v1"})
    client.post("/store_fact", json={"key": "k2", "value": "v2"})
    r = client.post("/retrieve_fact", json={"query": "k1", "min_confidence": 0.5})
    audit_id = r.json()["audit_record_id"]

    g = client.get(f"/audit/{audit_id}")
    assert g.status_code == 200
    rec = g.json()
    assert rec["id"] == audit_id
    assert rec["operation"] == "retrieve_fact"
    assert rec["sha256_self"].startswith("sha256:")

    health = client.get("/health").json()
    assert health["chain_ok"] is True
    assert health["audit_records"] >= 3


def test_compose_query_binding_semantics(client: TestClient) -> None:
    """/compose_query returns valid shape; matches a stored bound fact."""
    client.post("/store_fact", json={"key": "case_X", "value": "stored_value_X"})
    client.post("/store_fact", json={"key": "case_Y", "value": "stored_value_Y"})

    c = client.post(
        "/compose_query",
        json={
            "bindings": [{"role": "case_X", "filler": "stored_value_X"}],
            "min_confidence": 0.1,
        },
    )
    assert c.status_code == 200
    body = c.json()
    assert _shape_ok(body, ["status", "confidence", "composition_path", "audit_record_id"])
    assert body["composition_path"] == ["case_X=stored_value_X"]
    # With single (role, filler) bind matching the stored fact, expect match.
    assert body["status"] == "match"
    assert body["fact_text"] == "stored_value_X"


def test_all_endpoints_json_schema_valid(client: TestClient) -> None:
    """Every endpoint returns the documented response shape."""
    # health
    h = client.get("/health").json()
    assert all(k in h for k in ["status", "n", "codebook_size", "audit_records", "chain_ok", "signer_pubkey", "codebook_kind"])

    # store
    s = client.post("/store_fact", json={"key": "k", "value": "v"}).json()
    assert all(k in s for k in ["atom_id", "audit_record_id"])

    # retrieve
    r = client.post("/retrieve_fact", json={"query": "k"}).json()
    assert all(k in r for k in ["status", "confidence", "provenance", "audit_record_id"])

    # compose
    cq = client.post(
        "/compose_query",
        json={"bindings": [{"role": "k", "filler": "v"}], "min_confidence": 0.0},
    ).json()
    assert all(k in cq for k in ["status", "confidence", "composition_path", "audit_record_id"])

    # delete
    atom_id = s["atom_id"]
    d = client.post(
        "/delete_fact",
        json={"atom_id": atom_id, "requester_id": "x", "legal_basis": "OTHER"},
    ).json()
    assert all(k in d for k in ["status", "certificate", "audit_record_id"])

    # audit
    a = client.get(f"/audit/{r['audit_record_id']}").json()
    assert all(k in a for k in ["id", "ts_ns", "operation", "request_payload", "response_payload", "latency_ms", "substrate_state_hash", "sha256_chain_prev", "sha256_self"])


def test_edit_fact_preserves_atom_id(client: TestClient) -> None:
    """Edit swaps the bound value but keeps atom_id + key addressable."""
    store = client.post(
        "/store_fact",
        json={"key": "edit_key_1", "value": "version_one"},
    ).json()
    atom_id = store["atom_id"]
    original_audit_id = store["audit_record_id"]

    # Retrieve to confirm initial state.
    r1 = client.post(
        "/retrieve_fact",
        json={"query": "edit_key_1", "min_confidence": 0.1},
    ).json()
    assert r1["status"] == "match"
    assert r1["fact_text"] == "version_one"

    # Edit.
    e = client.post(
        "/edit_fact",
        json={
            "atom_id": atom_id,
            "new_value": "version_two",
            "requester_id": "test_admin",
            "notes": "correction per test",
        },
    ).json()
    assert all(k in e for k in [
        "status", "fact_id", "atom_id", "old_value", "new_value",
        "state_hash_before", "state_hash_after", "audit_record_id",
    ])
    assert e["status"] == "edited"
    assert e["atom_id"] == atom_id      # atom_id preserved
    assert e["old_value"] == "version_one"
    assert e["new_value"] == "version_two"
    # State hashes differ -- the edit changed the substrate state.
    assert e["state_hash_before"] != e["state_hash_after"]
    # New audit record id, distinct from the store call.
    assert e["audit_record_id"] != original_audit_id

    # Re-query: gets the post-edit value.
    r2 = client.post(
        "/retrieve_fact",
        json={"query": "edit_key_1", "min_confidence": 0.1},
    ).json()
    assert r2["status"] == "match"
    assert r2["fact_text"] == "version_two"

    # Audit record for the edit includes the diff fields.
    a = client.get(f"/audit/{e['audit_record_id']}").json()
    assert a["operation"] == "edit_fact"
    resp = a["response_payload"]
    assert resp["old_value"] == "version_one"
    assert resp["new_value"] == "version_two"
    assert resp["state_hash_before"] == e["state_hash_before"]
    assert resp["state_hash_after"] == e["state_hash_after"]


def test_edit_fact_unknown_atom_id_404(client: TestClient) -> None:
    """Editing a non-existent atom_id returns 404 without mutating state."""
    resp = client.post(
        "/edit_fact",
        json={"atom_id": "atom_does_not_exist", "new_value": "x"},
    )
    assert resp.status_code == 404


def test_tool_definitions_well_formed() -> None:
    """tool_definitions exposes 6 tools in both formats with matching names."""
    from hdlab_service.tool_definitions import (
        SUBSTRATE_TOOLS_ANTHROPIC,
        SUBSTRATE_TOOLS_OPENAI,
    )

    assert len(SUBSTRATE_TOOLS_ANTHROPIC) == 6
    assert len(SUBSTRATE_TOOLS_OPENAI) == 6
    anthropic_names = {t["name"] for t in SUBSTRATE_TOOLS_ANTHROPIC}
    openai_names = {t["function"]["name"] for t in SUBSTRATE_TOOLS_OPENAI}
    assert anthropic_names == openai_names
    expected = {
        "substrate_retrieve_fact",
        "substrate_store_fact",
        "substrate_edit_fact",
        "substrate_delete_fact",
        "substrate_compose_query",
        "substrate_get_audit",
    }
    assert anthropic_names == expected
    for t in SUBSTRATE_TOOLS_ANTHROPIC:
        assert "input_schema" in t
        assert t["input_schema"]["type"] == "object"
        assert "required" in t["input_schema"]


def test_tool_call_handler_dispatches(client: TestClient) -> None:
    """tool_call_handler proxies to the running service via TestClient."""
    from hdlab_service.tool_definitions import tool_call_handler

    # Use the TestClient's underlying httpx client as the substrate API client.
    # TestClient is itself an httpx.Client subclass.
    result = tool_call_handler(
        "substrate_store_fact",
        {"key": "tk", "value": "tv"},
        client=client,  # type: ignore[arg-type]
    )
    assert "atom_id" in result

    r = tool_call_handler(
        "substrate_retrieve_fact",
        {"query": "tk", "min_confidence": 0.1},
        client=client,  # type: ignore[arg-type]
    )
    assert r["status"] == "match"
    assert r["fact_text"] == "tv"
