"""Per-op latency, FLOPs, and memory-access profiling for hardware-substrate analysis.

For Week 4 we measure per-op wall time inline at each emit call site and store it in
TraceEvent.elapsed_ns. FLOP estimators and memory-pattern hints are exposed here for
the Week 8 hardware analysis to consume against persisted trace data.
"""

from __future__ import annotations

import math
import time


def now_ns() -> int:
    """Monotonic timestamp in nanoseconds."""
    return time.perf_counter_ns()


def estimate_flops(op: str, inputs: dict) -> int:
    """Rough FLOP count for a given op given its trace-event inputs. 0 if unknown."""
    if op == "atoms.make_atom_fhrr":
        n = int(inputs.get("n", 0))
        return 5 * n  # rand + cos + sin + complex pack + cast
    if op == "atoms.make_atom_hrr":
        n = int(inputs.get("n", 0))
        return 2 * n  # randn + divide by sqrt(n)
    if op == "atoms.make_atoms":
        k = int(inputs.get("k", 0))
        n = int(inputs.get("n", 0))
        return 5 * k * n
    if op == "binding.bind":
        shape_a = inputs.get("shape_a", [0])
        n = shape_a[-1] if shape_a else 0
        # FHRR: 6n (complex mul). HRR: ~10 n log n (FFT round trip).
        return 6 * n  # FHRR-typical; HRR re-estimated by caller if needed
    if op == "binding.unbind":
        shape_c = inputs.get("shape_c", [0])
        n = shape_c[-1] if shape_c else 0
        return 6 * n
    if op == "bundling.bundle":
        shape = inputs.get("shape", [0, 0])
        if len(shape) >= 2:
            k, n = shape[0], shape[-1]
            return 2 * k * n + 4 * n
        return 0
    if op == "atoms.similarity":
        shape_a = inputs.get("shape_a", [0])
        n = shape_a[-1] if shape_a else 0
        return 6 * n  # complex inner product
    if op == "memory.lookup":
        k = int(inputs.get("k", 0))
        # query_shape is the query vector; k is codebook size
        return 6 * k  # k similarities of N each; rough
    return 0


def estimate_flops_fft(n: int) -> int:
    """FFT FLOP estimate: ~5 n log2(n) (standard Cooley-Tukey)."""
    return int(5 * n * math.log2(max(n, 2)))
