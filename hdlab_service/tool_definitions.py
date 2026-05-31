"""Anthropic + OpenAI tool-use schemas for the substrate service."""

from __future__ import annotations

import json
from typing import Any

import httpx


SUBSTRATE_TOOLS_ANTHROPIC: list[dict[str, Any]] = [
    {
        "name": "substrate_retrieve_fact",
        "description": (
            "Retrieve a verifiable fact from the substrate corpus. Returns the matched "
            "fact text, similarity confidence, provenance atoms, and audit record id. "
            "Use this for any factual claim the user wants verified against the corpus."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language fact key to retrieve.",
                },
                "min_confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.6,
                    "description": "Minimum similarity score for a match.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "substrate_store_fact",
        "description": (
            "Store a new (key, value) fact in the substrate corpus with optional "
            "source-document provenance. Returns the new atom id and audit record id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Fact key / role label."},
                "value": {"type": "string", "description": "Fact value / filler text."},
                "source_doc_id": {
                    "type": "string",
                    "description": "Identifier of the document this fact was extracted from.",
                },
                "extraction_confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 1.0,
                },
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "substrate_edit_fact",
        "description": (
            "Update the value of an existing stored fact in place. The atom_id "
            "and key remain unchanged; only the bound value is swapped. Emits an "
            "audit record with substrate state hashes before and after the edit "
            "for chain-integrity verification. Use this whenever the user "
            "corrects, updates, or refines a previously stored fact."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "atom_id": {
                    "type": "string",
                    "description": "Atom id of the fact to edit (from store_fact response).",
                },
                "new_value": {
                    "type": "string",
                    "description": "New value text that replaces the previously bound value.",
                },
                "requester_id": {"type": "string", "default": "unknown"},
                "notes": {
                    "type": "string",
                    "description": "Optional human-readable reason for the edit.",
                },
            },
            "required": ["atom_id", "new_value"],
        },
    },
    {
        "name": "substrate_delete_fact",
        "description": (
            "Delete a fact from substrate and emit an Ed25519-signed deletion "
            "certificate (GDPR Article 17 aligned). Returns the certificate for "
            "downstream audit retention."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "atom_id": {"type": "string", "description": "Atom id to delete."},
                "requester_id": {"type": "string", "default": "unknown"},
                "legal_basis": {
                    "type": "string",
                    "enum": [
                        "GDPR_ART_17",
                        "HIPAA_INDIVIDUAL_REQUEST",
                        "PRIVILEGE_PURGE",
                        "ADMIN_RETENTION_EXPIRY",
                        "OTHER",
                    ],
                    "default": "GDPR_ART_17",
                },
                "notes": {"type": "string"},
            },
            "required": ["atom_id"],
        },
    },
    {
        "name": "substrate_compose_query",
        "description": (
            "Multi-fact query via substrate binding algebra. Specify role-filler "
            "pairs and the substrate composes a retrieval over the bound bundle. "
            "Use for queries like 'cases citing X ruled by judge Y'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "bindings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "filler": {"type": "string"},
                        },
                        "required": ["role", "filler"],
                    },
                    "description": "Role-filler pairs to compose into a probe.",
                },
                "min_confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                },
            },
            "required": ["bindings"],
        },
    },
    {
        "name": "substrate_get_audit",
        "description": (
            "Retrieve a single audit record by id. Used for post-hoc audit / "
            "compliance review of any prior substrate call."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string", "description": "Audit record id."},
            },
            "required": ["record_id"],
        },
    },
]


def _to_openai(tool: dict[str, Any]) -> dict[str, Any]:
    """Convert one Anthropic tool definition into OpenAI function-calling format."""
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }


SUBSTRATE_TOOLS_OPENAI: list[dict[str, Any]] = [_to_openai(t) for t in SUBSTRATE_TOOLS_ANTHROPIC]


_TOOL_ROUTES: dict[str, tuple[str, str]] = {
    "substrate_retrieve_fact": ("POST", "/retrieve_fact"),
    "substrate_store_fact": ("POST", "/store_fact"),
    "substrate_edit_fact": ("POST", "/edit_fact"),
    "substrate_delete_fact": ("POST", "/delete_fact"),
    "substrate_compose_query": ("POST", "/compose_query"),
    "substrate_get_audit": ("GET", "/audit/{record_id}"),
}


def tool_call_handler(
    tool_name: str,
    arguments: dict[str, Any],
    base_url: str = "http://localhost:8000",
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Dispatch a tool-use call to the running substrate service and return JSON."""
    if tool_name not in _TOOL_ROUTES:
        raise ValueError(f"Unknown substrate tool: {tool_name}")
    method, path = _TOOL_ROUTES[tool_name]
    own_client = False
    if client is None:
        client = httpx.Client(base_url=base_url, timeout=30.0)
        own_client = True
    try:
        if method == "GET":
            url = path.format(**arguments)
            resp = client.get(url)
        else:
            resp = client.post(path, json=arguments)
        resp.raise_for_status()
        return resp.json()
    finally:
        if own_client:
            client.close()


def tools_as_anthropic_json() -> str:
    """Serialize Anthropic tool list as JSON for inline use in prompts/docs."""
    return json.dumps(SUBSTRATE_TOOLS_ANTHROPIC, indent=2)


def tools_as_openai_json() -> str:
    """Serialize OpenAI tool list as JSON for inline use in prompts/docs."""
    return json.dumps(SUBSTRATE_TOOLS_OPENAI, indent=2)
