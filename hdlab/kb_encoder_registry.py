"""KB encoder registry -- resolve a KB encoder instance by its manifest/schema name.

Single place both the KB ingest (hdlab.director_kb) and the KB query
(hdlab.director_kb_query) resolve which encoder to build, so a new encoder is
made SELECTABLE by name without touching the pipeline. Additive + no-regression:
the default resolves to CharTrigramEncoder (char_trigram_v1) exactly as the two
call sites did when they hard-coded it, so behaviour is bit-identical until a
manifest/schema explicitly names a different encoder.

Registered encoders:
  char_trigram_v1 (default) -- self-contained text->HD; zero external model.
  gsbc_graded_m5            -- certified graded-code GSBC (density m=5); consumes
                               DENSE vectors. Selectable + witnessed, but NOT the
                               operational default. Requires a text->dense teacher
                               front-end for KB TEXT ingest/query (see CAPABILITIES
                               requires_text_frontend); encode(text) fail-louds
                               without one.

ASCII-only. No emojis. No em dashes.
"""

from __future__ import annotations

from typing import Any, Optional

from .char_trigram_encoder import CharTrigramEncoder
from .gsbc_graded_encoder import (
    DEFAULT_BLK_L,
    DEFAULT_KB,
    DEFAULT_M,
    GsbcGradedEncoder,
)

DEFAULT_ENCODER = "char_trigram_v1"

# Static capability metadata (for callers that must know an encoder's input
# regime before wiring it into a text pipeline). Does not construct anything.
CAPABILITIES: dict[str, dict[str, Any]] = {
    "char_trigram_v1": {
        "input": "text",
        "requires_text_frontend": False,
        "external_model": False,
        "note": "substrate-native bag-of-char-trigrams; self-contained.",
    },
    "gsbc_graded_m5": {
        "input": "dense_vector",
        "requires_text_frontend": True,
        "external_model": True,
        "text_frontend": "backend.llm.bge_encoder + trained student MLP",
        "geometry": {"kb": DEFAULT_KB, "blk_l": DEFAULT_BLK_L, "m": DEFAULT_M},
        "note": ("certified graded-code GSBC (m=5); dense->graded re-encoder. "
                 "encode(text) needs a teacher front-end (fail-loud otherwise)."),
    },
}


def is_registered(name: str) -> bool:
    """True if `name` (or 'default') resolves to a registered KB encoder."""
    return name in ("default", None) or name in CAPABILITIES


def resolve_kb_encoder(name: Optional[str], n_dim: int,
                       teacher: Optional[Any] = None) -> Any:
    """Return a KB encoder instance for `name` at `n_dim` (default char_trigram_v1)."""
    key = DEFAULT_ENCODER if (name is None or name == "default") else name
    if key == "char_trigram_v1":
        return CharTrigramEncoder(n_dim=n_dim)
    if key == "gsbc_graded_m5":
        return GsbcGradedEncoder(n_dim=n_dim, m=DEFAULT_M, teacher=teacher)
    raise ValueError(
        f"unknown KB encoder {name!r}; registered: {sorted(CAPABILITIES)} "
        f"(or 'default' -> {DEFAULT_ENCODER})")
