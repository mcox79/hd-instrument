# Strategy request: Phase-3 experimental push (2026-06-01)

**To:** Strategy session (via orchestrator)
**From:** Research session
**Trigger:** User explicit ask "pull all this together for another big experimental push" — Phase 1 (20 game-changer + peak-performance drills) + Phase 2 (30 deeper drills) complete.
**Cost reserved:** $0 (no cloud — local CPU + local GPU only per user direction 2026-06-01).

---

## TL;DR

50 sonnet drills converge on three families of opportunity. The full capability questions, evidence, and tiered prioritization live in:

**`d:/AI/hd-instrument/notes/research_priorities_for_orchestrator_2026-06-01.md`** (rewritten as Phase-3 consolidation today)

This routing file is **just the queue-up hand-off**. Strategy + exp_dev own cell design from here.

---

## Recommended Tier-1 batch (4 capability questions, all local)

Per the priorities file Section 4, research recommends Strategy queue cells for these FOUR Tier-1 questions FIRST. They are the highest information-gain × cap_map-impact × cost-efficiency combinations:

1. **Q-A1** — Does polynomial DAM at p=3 deliver 2700× capacity at N=8192 while preserving the rank-1 deletion certificate?
2. **Q-A4** — Does implicit Gram-solve retrieval deliver 7.3× per-query speedup AND eliminate the dreaming-pass primitive entirely?
3. **Q-C2** — Does the Marchenko-Pastur spectral health-check operate reliably at N ≥ 4096 (after v323 smoke-N=1024 FAIL)?
4. **Q-C3** — Does the κ_3 Hutchinson fingerprint achieve 4.2% delta_α sensitivity at N=8192 with O(N log N) incremental update?

All four fit local laptop CPU + GPU. Compute estimate: ~3-5h on laptop GPU, ~1-2h on laptop CPU. Cloud spend: ZERO.

## Recommended Tier-2 follow (4 more questions, gated on Tier-1)

5. **Q-A3** — L=2 cross-layer composition (p=3 outer / p=2 inner) — addressable-pair envelope. **Gated on Q-A1 PASS.**
6. **Q-B1** — Heteroassociative directed-chain depth-3 + cert. **Orthogonal to A1; safe to queue in parallel if capacity allows.**
7. **Q-C5** — Cosine-gate τ recalibration from 0.9 → [0.82, 0.88]. **Cheap (<2 min); GDPR-grade non-repudiation lift.**
8. **Q-A2** — p=4 polynomial DAM for signed-AM parity-symmetry. **Gated on Q-A1 confirming p>2 is viable.**

## Tier-3, cloud-deferred, and out-of-scope

Per priorities file Section 4 — Tier-3 questions (Q-B3 GoT bundle, Q-B4 reasoning-oracle API, Q-C1 5-method API uniformity, Q-C4 NESS bulk attestation) follow Tier-2. Cloud-only deferred (Q-D1 N=32768 spectral primitives, Q-D2 DG(m,r) higher-r ETF) wait for D3-KV-cache cloud authorization.

---

## What changed since the earlier 16h-batch routing (now superseded)

The earlier `strategy_request_to_strategy_overnight_16h_batch_AMEND_local_only_2026-06-01.md` proposed 10 cells re-scoped to local capacity but was still framed in the older Round-6 + v321 lexicon (cells E/F/H/K/L/D/G/I/C etc.). That routing **carried implicit cell design** (anchor names, N values, seed counts), which violates the new research-vs-orchestrator role split.

The Phase-3 priorities file is the corrected hand-off:
- Capability questions only.
- No anchor names / sweep grids / threshold formulas / queue choices / ETAs.
- Strategy + exp_dev resolve every cell-level decision.
- Research retains the right to surface evidence + open questions but does not pre-commit cell design.

If Strategy wants to reuse cells from the earlier batch (e.g., Round-6 cell K "symbolic primitive battery"), that is fine; map them into the Tier-1/2/3 framing above first, then design.

---

## Discipline declarations

- Pre-PROT-018 anchor-name `_n<N>` binding contract holds.
- Each cell carries explicit HP/MID/HF bands; no batch-level expected-PASS framing.
- ASCII-only print; per-experiment `--timeout` required; `set -ex` + `python -u` + `stdbuf -oL` + `tee` for any remote-dispatched cell.
- Composition classification (SCORE / HANDOFF / PIPELINE) per protocol BEFORE queueing for Q-A3 and Q-B1.
- Q-C2 and Q-A1 are HARD-FAIL-flagged — pre-register the falsifying conditions explicitly.
- Q-A4 wall-clock claims must be measured at production load, not FLOPs.
- No padding: each shipped anchor must trace to one of the Tier-1/2/3 questions above. If queue would fall short, surface to orchestrator — do not pad with marginal variants.

---

## Cap_map integration (Strategy: please commit v323→v330 incrementally)

Cap_map at v322 reflects only the empirical-verdict batch. The priorities file Section 6 lists six integration-ready blocks: Round 6 deliveries, free-probability unification, CK/FRSB clarification, 50 Phase-1+2 drill findings, audit-layer strategic-framing convergence, v1b inversion implications.

Research will not pre-commit cap_map decisions. Strategy owns the cap_map; orchestrator commits.

---

**END OF ROUTING.** Strategy session: please pick up the priorities file, design Tier-1 cells, and queue. Research will dispatch the next research-cycle deliverables on the cadence (~24-48h cross-framework drill per `feedback_periodic_scope_expansion`) and surface fresh capability questions as they emerge.

<!-- routing-completed: Acted-on 2026-06-01: Phase 3 push absorbed into v324 spectral identity + native query API CONFIRMED + downstream Round 10 dispatches via exp_dev -->
