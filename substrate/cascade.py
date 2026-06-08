"""
substrate.cascade -- PP-123 native-first cascade router.

Port of exp_cascade_native_first_router_cpu_v1.py.

CORE IDEA:
For each query, try the cheap native K-hop FIRST. If the native confidence (PP-107)
is below the threshold, escalate to a costlier fuzzy/LLM-based fallback. This matches
best-of-both accuracy at a fraction of the cost.

Validated:
- Cycle 187: P95 latency = 0.22 ms on substrate-side at 1M facts (scale-invariant)
- Cycle 188: P95 = 0.21 ms; "demo latency is the LLM, not substrate"
- Cycle 187 cost: substrate-only path = 48% of always-fuzzy cost; same accuracy
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from substrate.confidence import DEFAULT_THRESHOLD


class RoutingPath(str, Enum):
    NATIVE = "native"            # substrate K-hop only
    FUZZY_FALLBACK = "fuzzy_fallback"  # substrate K-hop confidence low -> fuzzy stage
    BARE_LLM = "bare_llm"        # fuzzy also failed; fall back to bare LLM
    ABSTAIN = "abstain"          # all paths low-confidence; honest "I don't know"


@dataclass
class RouteDecision:
    path: RoutingPath
    confidence: float
    cost_usd: float              # cumulative cost across the stages used
    latency_ms: float            # end-to-end
    native_confidence: Optional[float] = None
    fallback_used: bool = False
    abstained: bool = False
    result: Optional[Any] = None


def cascade(
    native_call: Callable[[], tuple[Any, float, float]],     # returns (result, confidence, cost_usd)
    fuzzy_fallback: Optional[Callable[[], tuple[Any, float, float]]] = None,
    bare_llm_fallback: Optional[Callable[[], tuple[Any, float, float]]] = None,
    confidence_threshold: float = DEFAULT_THRESHOLD,
) -> RouteDecision:
    """Run the cascade. native -> fuzzy_fallback -> bare_llm -> abstain.

    Each callable returns (result, confidence, cost_usd). The cascade short-circuits
    as soon as a stage exceeds the threshold.
    """
    t0 = time.perf_counter()
    total_cost = 0.0
    native_result, native_conf, native_cost = native_call()
    total_cost += native_cost
    if native_conf >= confidence_threshold:
        return RouteDecision(
            path=RoutingPath.NATIVE,
            confidence=native_conf,
            cost_usd=total_cost,
            latency_ms=(time.perf_counter() - t0) * 1000,
            native_confidence=native_conf,
            result=native_result,
        )

    # Native failed -> try fuzzy
    if fuzzy_fallback is not None:
        fuzzy_result, fuzzy_conf, fuzzy_cost = fuzzy_fallback()
        total_cost += fuzzy_cost
        if fuzzy_conf >= confidence_threshold:
            return RouteDecision(
                path=RoutingPath.FUZZY_FALLBACK,
                confidence=fuzzy_conf,
                cost_usd=total_cost,
                latency_ms=(time.perf_counter() - t0) * 1000,
                native_confidence=native_conf,
                fallback_used=True,
                result=fuzzy_result,
            )

    # Fuzzy also failed -> bare LLM
    if bare_llm_fallback is not None:
        llm_result, llm_conf, llm_cost = bare_llm_fallback()
        total_cost += llm_cost
        return RouteDecision(
            path=RoutingPath.BARE_LLM,
            confidence=llm_conf,
            cost_usd=total_cost,
            latency_ms=(time.perf_counter() - t0) * 1000,
            native_confidence=native_conf,
            fallback_used=True,
            result=llm_result,
        )

    # All paths low-confidence -> honest abstain
    return RouteDecision(
        path=RoutingPath.ABSTAIN,
        confidence=native_conf,
        cost_usd=total_cost,
        latency_ms=(time.perf_counter() - t0) * 1000,
        native_confidence=native_conf,
        abstained=True,
    )


def _self_test():
    # Native-confident path
    decision = cascade(
        native_call=lambda: ("native_result", 0.95, 0.001),
        fuzzy_fallback=lambda: ("fuzzy_result", 0.99, 0.01),
    )
    assert decision.path == RoutingPath.NATIVE
    assert decision.cost_usd == 0.001
    assert decision.result == "native_result"

    # Native low -> fuzzy
    decision = cascade(
        native_call=lambda: ("native_result", 0.30, 0.001),
        fuzzy_fallback=lambda: ("fuzzy_result", 0.90, 0.01),
    )
    assert decision.path == RoutingPath.FUZZY_FALLBACK
    assert decision.cost_usd == 0.011
    assert decision.fallback_used

    # Both fail -> bare LLM
    decision = cascade(
        native_call=lambda: ("nx", 0.20, 0.001),
        fuzzy_fallback=lambda: ("fx", 0.30, 0.01),
        bare_llm_fallback=lambda: ("llm", 0.80, 0.05),
    )
    assert decision.path == RoutingPath.BARE_LLM

    # Abstain
    decision = cascade(native_call=lambda: ("nx", 0.10, 0.001))
    assert decision.path == RoutingPath.ABSTAIN
    assert decision.abstained

    print("[substrate.cascade] self-test PASS")


if __name__ == "__main__":
    _self_test()
