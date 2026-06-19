"""Substrate memory testbed.

See notes/testbed_architecture_2026-05-29.md for design.
Entry point: python -m testbed run --scenario X --backend Y --config Z
"""

__version__ = "0.1.0"

from testbed.api import (
    AuditReport,
    DeletionCertificate,
    MemoryBackend,
    RetrievalResult,
)

__all__ = [
    "AuditReport",
    "DeletionCertificate",
    "MemoryBackend",
    "RetrievalResult",
]
