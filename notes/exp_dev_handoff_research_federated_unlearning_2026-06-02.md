# exp_dev hand-off -- research: federated unlearning + algebraic deletion cert

**Filed-by:** research sub-agent, 2026-06-02
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_federated_unlearning_2026-06-02.md
**Pause state:** Check data/orchestrator_paused.flag before dispatching any queue items

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off task + why + contract + autonomy. It does NOT specify anchor names, sweep grids, threshold formulas, or pre-committed cap_map decisions. exp_dev designs all of that.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_federated_unlearning_2026-06-02.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md (Cap 2 editable memory, Cap 3 provenance rows are load-bearing for this handoff)
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md

---

## Anchor candidates (rank-ordered)

### 1. Rank-1 parameter update exactness vs leave-one-out retrain (Cap 2 / deletion cert)
- **Anchor pointer:** Cap 2 (editable memory) row; algebraic deletion certificate sub-capability
- **Substrate-product reading:** Verify that the closed-form Woodbury rank-1 update to the substrate weight matrix produces output distributions statistically indistinguishable from full retrain-without-deleted-sample. If this holds, the algebraic cert primitive has a formal exactness claim for the linear/kernel regime.
- **Tier hint:** CPU smoke, < 5 min. Algebraic only -- no large-scale sweep needed; this is a correctness verification of the closed-form, not a capacity scan.
- **Why now:** Research confirmed this is the primary differentiator vs DP-SGD and SISA. The exactness claim must be grounded before any regulatory framing is made. No published benchmark of this specific combination (rank-1 Woodbury + hash chain + leave-one-out comparison) exists in the literature reviewed.

### 2. Hash chain provenance binding -- deterministic replay verification (Cap 3 / provenance)
- **Anchor pointer:** Cap 3 (provenance) row; per-fact audit trail sub-capability
- **Substrate-product reading:** Implement and verify that a SHA-256 (or BLAKE3) hash chain over (params_before, sample_id, params_after) is (a) deterministic across platforms, (b) verifiable in < 1ms, and (c) that the chain cannot be forged without access to the original params. This is the "audit trail" primitive that maps to regulatory audit-trail requirements.
- **Tier hint:** CPU smoke, < 2 min. Pure Python / hashlib verification, no GPU needed.
- **Why now:** The research note identifies this as the lowest-cost, highest-regulatory-differentiation primitive. The ZK-SNARK alternatives (zkUnlearner, ZK-APEX) are computationally expensive; if the hash chain is verifiable in milliseconds, this is the product claim.

### 3. Federated KFAC Hessian aggregation + rank-1 cert (Cap 2 / federated setting)
- **Anchor pointer:** Cap 2 (editable memory) federated extension; novel gap confirmed by research
- **Substrate-product reading:** Demonstrate that a block-diagonal KFAC approximation of the Hessian aggregated across federated clients supports a rank-1 Woodbury update with bounded approximation error. The research note found NO published work combining KFAC block-diagonal approx + rank-1 cert in a federated setting -- this is a genuine literature gap.
- **Tier hint:** CPU medium, ~30-60 min. Requires federated simulation with 2-5 clients. Not GPU-bound for the algebraic verification step.
- **Why now:** The federated unlearning literature (2023-2025) has no cryptographic cert format. If the substrate can deliver one via KFAC + rank-1 + hash chain, this widens the audit-moat to the federated ML market.

---

## Contract

exp_dev designs pre-reg bands (HARD-PASS / HARD-FAIL) per [[feedback-envelope-expansion-fail-bands]], selects queue (CPU vs GPU), sets timeout per [[feedback-per-experiment-timeout-required]], and verifies post-ship per role contract. Research has scoped the mechanism and confirmed the literature gap; exp_dev owns execution architecture.

## Autonomy declaration

exp_dev decides: anchor names, sweep parameters, N sizes, seed counts, queue assignment, timeout formula, pre-reg numerical thresholds, and post-ship verification steps. This file provides task + why + context pointers only.
