"""substrate_router -- M3 Phase 1 cortex layer above the HD substrate.

This is the EXTERNAL cortex layer, NOT a substrate primitive. Lives outside hdlab/
because it's the planner/router that sits above substrate and decides whether
substrate primitives can answer a USER query or whether to fall back to LLM.

Reference design: notes/director_M3_Phase1_LLM_router_architecture_sketch_2026-06-28.md

Phase 1 = LLM router that calls substrate primitives via SubstrateRouterAPI.
Phase 2 = learned classifier replaces LLM router.
Phase 3 = substrate-resident router (5+ yr aspirational).

M1.1 milestone (this scaffolding):
  - SubstrateRouterAPI class wraps intent classifier (chain-grade acc=0.754 cv=0.042),
    KG lookup (FB15k 1-hop r@1=1.000), and refuse-gate (V_REL=256 chain-grade).
  - router.route(query) returns RouterDecision with substrate-output OR fall_back_to_llm.
  - test_router_smoke.py verifies routing logic on 20 queries across 4 intent classes.
"""

from .api import SubstrateRouterAPI, IntentClass
from .router import RouterDecision, RouteOutcome, route

__all__ = [
    "SubstrateRouterAPI",
    "IntentClass",
    "RouterDecision",
    "RouteOutcome",
    "route",
]
