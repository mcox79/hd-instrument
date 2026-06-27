# 5x Research Drill — Barrier 1: Heterogeneous Multi-Hop Composition

Date: 2026-06-27
Discipline notes: 2x research drill (broad + narrow); lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50); generic terms only in web-equivalent reasoning; verify-the-referent for each proposed discriminator.

## Executive Summary

The substrate composes depth-15+ when every hop traverses the SAME relation (one-axis chain-following). It fails when each hop uses a DIFFERENT predicate / DIFFERENT operation. The diagnosis across all five angles converges: the substrate currently has no ROUTING layer that selects which binding to unbind next based on intermediate state. Chain-following works because the relation is held constant in superposition; heterogeneous composition demands a per-hop CONTROLLER that reads working state and chooses the next operator. Brain solves this via PFC-as-router over hippocampal/cortical schemas; classical AI solves it via interpreter-over-program; math says this is the difference between an iterated map and a stack machine. The top-3 cells below test ROUTING mechanisms (not bigger binding capacity), because the binding capacity we already have is wasted without a routing primitive that picks the right operator at each step.

## Angle 1 — Pure Math

The math literature treats heterogeneous composition as message-passing on a heterogeneous factor graph or as contraction of a TENSOR NETWORK with mixed bond dimensions. What we have not tried:

- **Tensor-network contraction order optimization (TN-CO):** treat each predicate as a tensor node; contract in an order that minimizes intermediate dimension. Cell: encode 4-hop heterogeneous query as small factor graph; run substrate-native contraction in two orders (greedy left-to-right vs min-degree heuristic); discriminator = lift of min-degree over greedy >= 0.10 cv<0.10.
- **Loopy belief propagation with damping (LBP-d):** iterate substrate-resident messages around a cycle; current substrate either does one pass (BP) or pure bidirectional. Cell: 3-iter damped LBP at damping=0.3 on 4-cycle heterogeneous query; discriminator = D2 (2-iter) > D0 (zero-iter) by >= 0.08 AND D5 (5-iter) does not diverge.
- **Free-monad interpretation:** represent the query as a free monad over predicate-functors; substrate interprets by unfolding. Cell: encode 3 different operator-kinds as separate bound role-filler vectors; iterate "unbind-operator, apply, rebind"; discriminator vs flat composition >= 0.10.

The crucial pure-math observation: noise compounding under random superposition is sqrt(k) for INDEPENDENT noises but k for CORRELATED ones. Heterogeneous hops should be more independent than chain hops, so the noise budget is actually LOOSER than chain-following. We are not capacity-bound; we are routing-bound.

## Angle 2 — Materials Science / Physics

- **Concatenated codes (inner Hamming + outer Reed-Solomon analog over HD):** chain-following is a single-code regime; heterogeneous hops are a code-on-code regime where the outer code names which inner code to apply. Cell: encode each predicate-class as a distinct cleanup codebook; outer "selector" vector indexes which codebook to clean against at each hop. Discriminator = 3-hop heterogeneous lift over single-codebook cleanup >= 0.12.
- **Kuramoto phase-coherence routing:** assign each predicate a distinct oscillator frequency; "routing" = which phase is currently in coherence with the working state. Cell: substrate stores 4 candidate operators as phase-tagged vectors; readout uses cosine-with-phase-mask to select which operator fires next. Discriminator = phase-mask arm beats no-mask by >= 0.10 at depth-4 heterogeneous.
- **Percolation on heterogeneous edge sets:** depth-k composition succeeds only if a giant component exists in the union-of-predicates graph. Predict the depth-cliff is a percolation threshold, not a capacity limit. Cell: vary density of cross-predicate edges; locate phase transition; discriminator = sharp transition (slope >= 0.5 per decade of edge density) at predicted p_c.

## Angle 3 — Biology / Brain

Primate heterogeneous composition uses three load-bearing pieces we have not implemented as a single integrated cell:

- **Schema-indexed PFC routing (Tse engram + Miller-Cohen PFC):** PFC holds a SCHEMA vector that names "which kind of inference applies here"; the schema gates which hippocampal index gets unbound next. Cell: substrate maintains a small (V_C ~ 8-16) schema bank; each hop first queries the schema bank with current state, then uses schema-as-mask on the operator codebook. Discriminator = schema-gated 4-hop > schema-free by >= 0.12.
- **Grid-cell relational coding (Whittington TEM):** entities and relations live in different bases; composition = ADD relation vector to entity vector to predict next entity. Substrate-native version: train a separate role-basis that is ORTHOGONAL to filler-basis; check whether heterogeneous hops compose by vector ADDITION in role-basis. Cell: orthogonalize relation-basis vs filler-basis via Gram-Schmidt at init; discriminator = depth-4 heterogeneous lift over shared-basis >= 0.10.
- **Hippocampal sequential reactivation (Pfeiffer-Foster preplay):** before executing a multi-hop query, hippocampus REPLAYS candidate paths and selects the highest-confidence one. Substrate version: generate K candidate hop-sequences via reverse-replay (already MIDDLE_BAND in M5), score each by total cleanup confidence, execute the winner. Cell: K=8 candidate path scorer with confidence-weighted selection; discriminator vs first-path-greedy >= 0.10.

The brain answer to "how does it do depth-7+" is: it does not do single-pass composition; it does plan-then-execute with REPLAY as the planner. Our substrate currently does single-pass.

## Angle 4 — Substrate-Native Theory

- **Routing is the bottleneck, not binding:** with D=8192 and random superposition, a single HD vector can hold ~D/(2 log D) ~ 320 independent bindings before retrieval falls below 0.9. We are nowhere near this. The depth-2 ceiling cannot be a binding-capacity ceiling; it must be a routing ceiling.
- **Per-hop controller as a small recurrent map:** define f(state, predicate_id) -> next_state where the predicate_id is selected from a small bank. Cell: tiny (V=16) operator bank, each operator = one bind+permute schema; controller picks operator by argmax cosine with state; discriminator = 4-hop heterogeneous with controller >= 0.10 lift over fixed-operator-sequence.
- **Cleanup-then-bind vs bind-then-cleanup ordering:** chain-following works because cleanup happens AFTER all binds. Heterogeneous fails because intermediate cleanup is needed between hops with different noise statistics. Cell: insert mandatory cleanup at each hop boundary for heterogeneous; discriminator = lift over end-only cleanup >= 0.08 at depth-4.

## Angle 5 — Cross-Domain

- **DNC/NTM read-write head as routing controller:** the DNC literature is precisely about composing heterogeneous operations via a learned controller over external memory. Substrate-native version: add a small differentiable-free controller that emits "which slot to read, which slot to write, which op to apply" at each step. Cell: 3-step controller-driven composition vs single-pass; discriminator >= 0.12.
- **MoE / Switch routing as operator selection:** treat each predicate-class as a separate "expert" cleanup table; a router picks one expert per hop based on current state. This is the simplest, lowest-risk version of brain-PFC routing. Cell: E=4 expert codebooks; gating via cosine-argmax over expert-centroid; discriminator = MoE-routed >= 0.10 over single-codebook at depth-3 heterogeneous.
- **Interpreter-over-program:** encode the QUERY itself as a substrate vector that names a small program (sequence of operator-ids); separate "interpreter" loop unbinds one op at a time and applies. Cell: query-as-program with 3-step interpretation; discriminator vs query-as-flat-bag-of-roles >= 0.12 at depth-3 heterogeneous.

## TOP-3 Cell Proposals (P-ranked, falsifiable discriminators)

**RANK 1 — `comp_router_moe_v1` (P ~ 0.45 post-deflation):** smallest, most decisive test of the routing-vs-capacity hypothesis. E=4 expert codebooks, cosine-argmax gating, 3-hop heterogeneous query. Discriminator = MoE-routed lift over single-codebook >= 0.10 cv < 0.10 across 5 seeds. If FAIL, routing-as-operator-select is not the answer and we should investigate state-representation. If PASS, escalate to E=16 + 5-hop and brain-schema variant.

**RANK 2 — `comp_pfc_schema_replay_v1` (P ~ 0.35):** integrated brain mechanism — schema bank (V_C=8) + K=8 candidate path replay + confidence-weighted selection. 4-hop heterogeneous query. Discriminator = full mechanism > schema-only > replay-only > baseline, with full-vs-baseline >= 0.15. Higher complexity, higher prior because brain proves it works; lower P because integration risk.

**RANK 3 — `comp_orthogonal_role_basis_v1` (P ~ 0.30):** Gram-Schmidt orthogonalize role-basis against filler-basis at init; pure-additive heterogeneous composition test. 4-hop heterogeneous query. Discriminator = orthogonal-basis arm >= 0.10 lift over shared-basis at cv < 0.10. Lowest P because grid-cell mechanism in brain is more subtle than pure orthogonality, but cheapest cell to ship — single init change, no controller plumbing.

## Risks / Anti-Negativity Backstop

The substrate could be routing-bound AND state-representation-bound; the MoE cell isolates routing assuming state is fine. If RANK 1 HARD_FAILs with high cv, that is evidence state-representation is the issue and we should run RANK 3 next (orthogonal basis = state cleanup) before RANK 2 (integrated). Symmetric correction: if RANK 1 PASSes by exactly the discriminator margin and no more, treat as MIDDLE_BAND not chain-grade and require capacity sweep before declaring victory.

End.
