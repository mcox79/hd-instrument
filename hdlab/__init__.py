"""hd-instrument: observable hyperdimensional computing substrate."""

__version__ = "0.1.0.dev0"

# Import order matters: tracing must exist before modulators registers its state provider.
from . import tracing  # noqa: F401
from . import modulators  # noqa: F401
from . import atoms, binding, bundling, memory  # noqa: F401
from . import semantic, ablation, snapshots  # noqa: F401

__all__ = [
    "atoms",
    "binding",
    "bundling",
    "memory",
    "modulators",
    "tracing",
    "semantic",
    "ablation",
    "snapshots",
]
