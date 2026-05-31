"""FastAPI wrapper around hdlab.memory.Codebook for Pattern B integration demo."""

from __future__ import annotations

import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from hdlab import atoms, binding, memory, modulators

from .audit_log import AuditLog, compute_state_hash
from .deletion_cert import (
    DeletionCertService,
    SignedCertificate,
    load_or_create_service,
)


DEFAULT_N = 1024
DEFAULT_M_FRAC = 0.25
DEFAULT_CODEBOOK = "BSC"
DEFAULT_KEY_DIR = os.path.join(os.path.dirname(__file__), "_state", "keys")
DEFAULT_AUDIT_PATH = os.path.join(os.path.dirname(__file__), "_state", "audit_log.jsonl")
HIGH_CONFIDENCE = 0.85
MIN_CONFIDENCE_DEFAULT = 0.6


class FactRetrieveRequest(BaseModel):
    """Single-fact retrieval input."""

    query: str = Field(..., description="Fact key / natural-language query")
    min_confidence: float = Field(MIN_CONFIDENCE_DEFAULT, ge=0.0, le=1.0)


class ProvenanceAtom(BaseModel):
    """Provenance entry for an atom matched during retrieval."""

    atom_id: str
    role: str | None = None
    similarity: float


class FactRetrieveResponse(BaseModel):
    """Single-fact retrieval result."""

    status: str = Field(..., description="match | no_match")
    fact_id: str | None = None
    fact_text: str | None = None
    confidence: float = 0.0
    provenance: list[ProvenanceAtom] = Field(default_factory=list)
    audit_record_id: str


class FactStoreRequest(BaseModel):
    """Store a (key, value) fact in substrate."""

    key: str
    value: str
    source_doc_id: str | None = None
    extraction_confidence: float = Field(1.0, ge=0.0, le=1.0)


class FactStoreResponse(BaseModel):
    """Atom id returned from store_fact."""

    atom_id: str
    audit_record_id: str


class FactDeleteRequest(BaseModel):
    """Delete a stored fact by id."""

    atom_id: str
    requester_id: str = "unknown"
    legal_basis: str = "GDPR_ART_17"
    notes: str | None = None


class FactDeleteResponse(BaseModel):
    """Deletion result including signed certificate."""

    status: str
    certificate: dict[str, Any]
    audit_record_id: str


class FactEditRequest(BaseModel):
    """In-place edit of a stored fact's value (preserves atom_id and key)."""

    atom_id: str = Field(..., description="Atom id of the fact to edit.")
    new_value: str = Field(..., description="New value to bind to the existing key.")
    requester_id: str = "unknown"
    notes: str | None = None


class FactEditResponse(BaseModel):
    """Edit result with before/after state hashes for audit-chain integrity."""

    status: str
    fact_id: str
    atom_id: str
    old_value: str
    new_value: str
    state_hash_before: str
    state_hash_after: str
    audit_record_id: str


class BindingPair(BaseModel):
    """Role-filler binding for compositional queries."""

    role: str
    filler: str


class CompositionalQueryRequest(BaseModel):
    """Multi-fact compositional query via binding algebra."""

    bindings: list[BindingPair]
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)


class CompositionalQueryResponse(BaseModel):
    """Result of a compositional query."""

    status: str
    fact_id: str | None
    fact_text: str | None
    confidence: float
    composition_path: list[str]
    audit_record_id: str


class AuditRecordResponse(BaseModel):
    """Public view of a stored audit record."""

    id: str
    ts_ns: int
    operation: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]
    latency_ms: float
    substrate_state_hash: str
    sha256_chain_prev: str
    sha256_self: str


class HealthResponse(BaseModel):
    """Service health summary."""

    status: str
    n: int
    codebook_size: int
    audit_records: int
    chain_ok: bool
    signer_pubkey: str
    codebook_kind: str


class SubstrateService:
    """In-memory substrate state shared across endpoints."""

    def __init__(
        self,
        n: int,
        codebook_kind: str,
        audit_path: str | None,
        key_dir: str,
    ) -> None:
        self.n = n
        self.codebook_kind = codebook_kind.upper()
        if self.codebook_kind not in {"BSC", "KERDOCK", "FHRR", "HRR"}:
            raise ValueError(f"Unsupported codebook kind: {codebook_kind}")
        # BSC/Kerdock are real-valued; map both onto HRR (real float32) primitives.
        self.dtype = torch.complex64 if self.codebook_kind == "FHRR" else torch.float32
        # Drop the lookup threshold to zero so the API decides match/no_match.
        modulators.set_attention(0.0)
        self.codebook = memory.Codebook(n=n, dtype=self.dtype)
        self.generator = torch.Generator()
        self.generator.manual_seed(0xC0DE_B00C)
        # fact_id -> {atom_id, key, value, vector, metadata, atom_index}
        self._facts: dict[str, dict[str, Any]] = {}
        # role label -> torch.Tensor (cached for compositional binds)
        self._roles: dict[str, torch.Tensor] = {}
        # filler label -> torch.Tensor
        self._fillers: dict[str, torch.Tensor] = {}
        self._tombstones: set[str] = set()
        self.audit = AuditLog(audit_path)
        self.cert_service: DeletionCertService = load_or_create_service(key_dir)

    def state_hash(self) -> str:
        """Snapshot of live atoms for audit log + cert chain."""

        def summary_iter() -> Any:
            for fid, info in self._facts.items():
                if info["atom_id"] in self._tombstones:
                    continue
                vec = info["bound_vector"]
                if vec.is_complex():
                    flat = vec.detach().cpu().real.flatten()[:8].tolist()
                else:
                    flat = vec.detach().cpu().float().flatten()[:8].tolist()
                yield (info["atom_id"], flat)

        return compute_state_hash(summary_iter())

    def _atom(self) -> torch.Tensor:
        """Generate a fresh atom for the configured codebook kind."""
        if self.dtype == torch.complex64:
            return atoms.make_atom_fhrr(self.n, self.generator)
        return atoms.make_atom_hrr(self.n, self.generator)

    def _role(self, label: str) -> torch.Tensor:
        if label not in self._roles:
            self._roles[label] = self._atom()
        return self._roles[label]

    def _filler(self, label: str) -> torch.Tensor:
        if label not in self._fillers:
            self._fillers[label] = self._atom()
        return self._fillers[label]

    def store_fact(self, key: str, value: str, metadata: dict[str, Any]) -> str:
        """Bind (key, value) into substrate; register a key-probe atom for cleanup."""
        role = self._role(key)
        filler = self._filler(value)
        bound = binding.bind(role, filler)
        fact_id = "fact_" + uuid.uuid4().hex
        atom_id = "atom_" + uuid.uuid4().hex
        # Codebook stores the key-probe vector (role) named by atom_id so single-
        # fact retrieval by key gets a clean cosine hit. The bound vector is held
        # for compositional matching.
        self.codebook.add(atom_id, role.clone())
        self._facts[fact_id] = {
            "atom_id": atom_id,
            "key": key,
            "value": value,
            "key_vector": role,
            "bound_vector": bound,
            "metadata": metadata,
            "atom_index": len(self.codebook) - 1,
        }
        return fact_id

    def retrieve_fact(self, query: str, min_confidence: float) -> dict[str, Any]:
        """Lookup the stored fact whose key vector is closest to the probe."""
        if not self._facts:
            return {
                "status": "no_match",
                "fact_id": None,
                "fact_text": None,
                "confidence": 0.0,
                "provenance": [],
            }
        probe = self._role(query) if query in self._roles else self._atom()
        # Scan live facts (codebook tombstones are tracked separately).
        best_fact_id: str | None = None
        best_score = -1.0
        for fid, info in self._facts.items():
            if info["atom_id"] in self._tombstones:
                continue
            sim = float(atoms.similarity(probe, info["key_vector"]))
            if sim > best_score:
                best_score = sim
                best_fact_id = fid
        if best_fact_id is None or best_score < min_confidence:
            return {
                "status": "no_match",
                "fact_id": None,
                "fact_text": None,
                "confidence": max(0.0, best_score),
                "provenance": [],
            }
        info = self._facts[best_fact_id]
        return {
            "status": "match",
            "fact_id": best_fact_id,
            "fact_text": info["value"],
            "confidence": best_score,
            "provenance": [
                {"atom_id": info["atom_id"], "role": info["key"], "similarity": best_score}
            ],
        }

    def compositional_query(
        self, pairs: list[BindingPair], min_confidence: float
    ) -> dict[str, Any]:
        """Bundle bound role-filler pairs into a probe; return cleanup hit."""
        if not pairs:
            return {
                "status": "no_match",
                "fact_id": None,
                "fact_text": None,
                "confidence": 0.0,
                "composition_path": [],
            }
        accum: torch.Tensor | None = None
        path: list[str] = []
        for pair in pairs:
            r = self._role(pair.role)
            f = self._filler(pair.filler)
            bound = binding.bind(r, f)
            accum = bound if accum is None else accum + bound
            path.append(f"{pair.role}={pair.filler}")
        assert accum is not None
        # Find best matching stored fact bound vector
        best_fact_id: str | None = None
        best_score = -1.0
        for fid, info in self._facts.items():
            if info["atom_id"] in self._tombstones:
                continue
            sim = float(atoms.similarity(accum, info["bound_vector"]))
            if sim > best_score:
                best_score = sim
                best_fact_id = fid
        if best_fact_id is None or best_score < min_confidence:
            return {
                "status": "no_match",
                "fact_id": None,
                "fact_text": None,
                "confidence": max(0.0, best_score),
                "composition_path": path,
            }
        info = self._facts[best_fact_id]
        return {
            "status": "match",
            "fact_id": best_fact_id,
            "fact_text": info["value"],
            "confidence": best_score,
            "composition_path": path,
        }

    def edit_fact(
        self, atom_id: str, new_value: str, requester_id: str, notes: str | None
    ) -> tuple[bool, str | None, str | None]:
        """In-place value swap for an existing fact (atom_id and key unchanged).

        Substrate-side semantics: preserves the key-probe atom (so retrieval
        by key still hits the same atom_id) but rebinds the value side via
        a fresh filler vector. This matches KF-2 edit-isolation discipline
        validated at the substrate-physics layer: only this fact's bound
        vector changes; all other facts' binding stays bit-identical.

        Returns (ok, fact_id, old_value).
        """
        target: str | None = None
        for fid, info in self._facts.items():
            if info["atom_id"] == atom_id:
                target = fid
                break
        if target is None or atom_id in self._tombstones:
            return False, None, None
        info = self._facts[target]
        old_value = info["value"]
        # Rebind: reuse the key vector (role); generate a fresh filler vector
        # for the new value; recompute the bound representation.
        role = info["key_vector"]
        new_filler = self._filler(new_value)
        new_bound = binding.bind(role, new_filler)
        info["value"] = new_value
        info["bound_vector"] = new_bound
        # Append to the fact's edit_history so the trail is recoverable from
        # the fact itself (independent of the global audit log).
        edits = info["metadata"].setdefault("edit_history", [])
        edits.append({
            "from_value": old_value,
            "to_value": new_value,
            "requester_id": requester_id,
            "notes": notes,
        })
        return True, target, old_value

    def delete_fact(
        self, atom_id: str, requester_id: str, legal_basis: str, notes: str | None
    ) -> tuple[bool, str | None]:
        """Tombstone the named atom; returns (deleted, fact_id) for the cert."""
        target: str | None = None
        for fid, info in self._facts.items():
            if info["atom_id"] == atom_id:
                target = fid
                break
        if target is None:
            return False, None
        self._tombstones.add(atom_id)
        # Zero both stored vectors in place to honour erasure semantics.
        info = self._facts[target]
        info["key_vector"] = torch.zeros_like(info["key_vector"])
        info["bound_vector"] = torch.zeros_like(info["bound_vector"])
        return True, target


def _make_service() -> SubstrateService:
    n = int(os.environ.get("HDLAB_N", DEFAULT_N))
    codebook_kind = os.environ.get("HDLAB_CODEBOOK", DEFAULT_CODEBOOK)
    audit_path = os.environ.get("HDLAB_AUDIT_PATH", DEFAULT_AUDIT_PATH)
    key_dir = os.environ.get("HDLAB_KEY_DIR", DEFAULT_KEY_DIR)
    return SubstrateService(
        n=n,
        codebook_kind=codebook_kind,
        audit_path=audit_path,
        key_dir=key_dir,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize substrate state on startup."""
    app.state.svc = _make_service()
    yield


app = FastAPI(
    title="hdlab_service",
    version="0.1.0",
    description="Pattern B FastAPI wrapper around hdlab substrate",
    lifespan=lifespan,
)


def _svc() -> SubstrateService:
    svc = getattr(app.state, "svc", None)
    if svc is None:
        # Allow direct call (TestClient without lifespan) to lazy-init.
        app.state.svc = _make_service()
        svc = app.state.svc
    return svc


def _record(
    op: str, req: dict[str, Any], resp: dict[str, Any], latency_ms: float
) -> str:
    """Append an audit record and return its id."""
    svc = _svc()
    rec = svc.audit.append(
        operation=op,
        request_payload=req,
        response_payload=resp,
        latency_ms=latency_ms,
        substrate_state_hash=svc.state_hash(),
    )
    return rec.id


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Service status snapshot."""
    svc = _svc()
    return HealthResponse(
        status="ok",
        n=svc.n,
        codebook_size=len(svc.codebook),
        audit_records=len(svc.audit),
        chain_ok=svc.audit.verify_chain(),
        signer_pubkey=svc.cert_service.public_key_b64,
        codebook_kind=svc.codebook_kind,
    )


@app.post("/retrieve_fact", response_model=FactRetrieveResponse)
def retrieve_fact(req: FactRetrieveRequest) -> FactRetrieveResponse:
    """Query substrate for the closest stored fact."""
    svc = _svc()
    t0 = time.perf_counter()
    result = svc.retrieve_fact(req.query, req.min_confidence)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    audit_id = _record(
        "retrieve_fact",
        req.model_dump(),
        result,
        latency_ms,
    )
    return FactRetrieveResponse(
        status=result["status"],
        fact_id=result["fact_id"],
        fact_text=result["fact_text"],
        confidence=result["confidence"],
        provenance=[ProvenanceAtom(**p) for p in result["provenance"]],
        audit_record_id=audit_id,
    )


@app.post("/store_fact", response_model=FactStoreResponse)
def store_fact(req: FactStoreRequest) -> FactStoreResponse:
    """Add a (key, value) atom binding to substrate."""
    svc = _svc()
    t0 = time.perf_counter()
    metadata = {
        "source_doc_id": req.source_doc_id,
        "extraction_confidence": req.extraction_confidence,
    }
    fact_id = svc.store_fact(req.key, req.value, metadata)
    atom_id = svc._facts[fact_id]["atom_id"]
    latency_ms = (time.perf_counter() - t0) * 1000.0
    audit_id = _record(
        "store_fact",
        req.model_dump(),
        {"fact_id": fact_id, "atom_id": atom_id},
        latency_ms,
    )
    return FactStoreResponse(atom_id=atom_id, audit_record_id=audit_id)


@app.post("/edit_fact", response_model=FactEditResponse)
def edit_fact(req: FactEditRequest) -> FactEditResponse:
    """Update the value of an existing fact in place; preserves atom_id + key.

    Emits an audit record with state_hash_before / state_hash_after so the
    chain integrity check covers the edit. No deletion certificate is issued
    -- edits are not deletes -- but the audit record + state hashes provide
    equivalent verifiability for compliance review.
    """
    svc = _svc()
    t0 = time.perf_counter()
    state_before = svc.state_hash()
    ok, fact_id, old_value = svc.edit_fact(
        req.atom_id, req.new_value, req.requester_id, req.notes
    )
    if not ok or fact_id is None or old_value is None:
        raise HTTPException(status_code=404, detail=f"atom_id not found: {req.atom_id}")
    state_after = svc.state_hash()
    latency_ms = (time.perf_counter() - t0) * 1000.0
    audit_id = _record(
        "edit_fact",
        req.model_dump(),
        {
            "status": "edited",
            "fact_id": fact_id,
            "atom_id": req.atom_id,
            "old_value": old_value,
            "new_value": req.new_value,
            "state_hash_before": state_before,
            "state_hash_after": state_after,
        },
        latency_ms,
    )
    return FactEditResponse(
        status="edited",
        fact_id=fact_id,
        atom_id=req.atom_id,
        old_value=old_value,
        new_value=req.new_value,
        state_hash_before=state_before,
        state_hash_after=state_after,
        audit_record_id=audit_id,
    )


@app.post("/delete_fact", response_model=FactDeleteResponse)
def delete_fact(req: FactDeleteRequest) -> FactDeleteResponse:
    """Erase a stored fact and issue a signed deletion certificate."""
    svc = _svc()
    t0 = time.perf_counter()
    state_before = svc.state_hash()
    ok, fact_id = svc.delete_fact(
        req.atom_id, req.requester_id, req.legal_basis, req.notes
    )
    if not ok:
        raise HTTPException(status_code=404, detail=f"atom_id not found: {req.atom_id}")
    state_after = svc.state_hash()
    latency_ms = (time.perf_counter() - t0) * 1000.0
    # Audit FIRST so we have a record id to embed in the cert
    audit_id = _record(
        "delete_fact",
        req.model_dump(),
        {
            "status": "deleted",
            "fact_id": fact_id,
            "state_hash_before": state_before,
            "state_hash_after": state_after,
        },
        latency_ms,
    )
    cert: SignedCertificate = svc.cert_service.issue_certificate(
        deleted_fact_id=fact_id or req.atom_id,
        audit_record_id=audit_id,
        ts_ns=None,
        substrate_state_before_hash=state_before,
        substrate_state_after_hash=state_after,
    )
    return FactDeleteResponse(
        status="deleted",
        certificate=cert.to_dict(),
        audit_record_id=audit_id,
    )


@app.post("/compose_query", response_model=CompositionalQueryResponse)
def compose_query(req: CompositionalQueryRequest) -> CompositionalQueryResponse:
    """Multi-fact compositional query via binding algebra."""
    svc = _svc()
    t0 = time.perf_counter()
    result = svc.compositional_query(req.bindings, req.min_confidence)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    audit_id = _record(
        "compose_query",
        req.model_dump(),
        result,
        latency_ms,
    )
    return CompositionalQueryResponse(
        status=result["status"],
        fact_id=result["fact_id"],
        fact_text=result["fact_text"],
        confidence=result["confidence"],
        composition_path=result["composition_path"],
        audit_record_id=audit_id,
    )


@app.get("/audit/{record_id}", response_model=AuditRecordResponse)
def get_audit(record_id: str) -> AuditRecordResponse:
    """Retrieve a single audit record by id."""
    svc = _svc()
    rec = svc.audit.get(record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail=f"audit record not found: {record_id}")
    return AuditRecordResponse(**rec.to_dict())
