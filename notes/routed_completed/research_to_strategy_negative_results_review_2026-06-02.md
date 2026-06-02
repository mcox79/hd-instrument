# research -> strategy routing: negative results 2x review (2026-06-02)

**Filed by**: research sub-agent
**Trigger**: orchestrator dispatch per [[feedback-negative-results-2x-research]]; 6 negative results reviewed
**Full synthesis**: notes/research_negative_results_review_2026-06-02.md
**Priority**: HIGH -- 4 rescue anchors ready to dispatch; 1 already in flight

---

## Tally

- Items reviewed: 6
- RESCUE (design fault): 4 (graph_link, tau_mem, signed_am, pp31c)
- RESCUE (instrumentation): 2 (timeseries_xor, chi_sg)
- CLOSE (genuine refutation): 0
- CANNOT row additions: 0
- Cap_map mutations proposed: 0 (research does NOT modify cap_map)

**No genuine refutations. All 6 are rescuable.** Strategy should annotate operating envelopes on affected rows.

---

## Rescue dispatch sequencing (cheapest first per [[feedback-rescue-sketch-first-sequencing]])

### Tier 0 (already in flight -- no dispatch needed)
- **tau_mem_decay_sweep**: q9_tau_mem_corrected in PARKED FULL re-ship list (strategy_decisions_v330 item 4). State-vector simulation tests corrected Q9 log formula. HP: |tau_emp/tau_theory - 1| <= 0.20 in single-pattern regime.

### Tier 1 (dispatch immediately -- less than 1h CPU each)

1. **pp31c_knee redesign** (pp31c_near_capacity_v1 suggested anchor name): 
   - Root cause: M=50/N=8192 = 0.006 load, far below capacity cliff. Substrate retrieves all queries perfectly; no precision-coverage tradeoff exists.
   - Fix: M near cliff. For N=8192: M in {3000, 4000, 4500}. Alternatively N=1024 M near 573.
   - HP: knee detected at tau in (0.5, 0.9), delta_precision/delta_coverage >= 2.0 across knee
   - HF: flat precision even at near-capacity M
   - P_deflated: 0.70. Less than 1h CPU, no new code.
   - Note: also add tau_min and other config-discriminating fields to PROT-021 check keys (INFRA fix, not exp fix)

2. **timeseries_xor fix** (timeseries_xor_fullscale_v3 suggested):
   - Root cause: PROT-021 contamination (stale N=1024 checkpoint loaded at N=4096) + probable dimensional mismatch in XOR kernel
   - Fix: add N to PROT-021 checkpoint key; clear checkpoint; re-run at N=4096
   - HP: in_acc >= 0.90, contam <= 0.10, N=4096, 3 seeds
   - HF: in_acc < 0.50 after fix
   - P_deflated: 0.72. Less than 30 min if INFRA explanation holds.
   - Note: v1 smoke in_acc=1.0 at N=1024 strongly suggests INFRA not physics; timeseries_infrastructure research (2026-06-01) confirmed GO for compliance sidecar (P=0.60)

3. **signed-AM M_A sweep** (signed_am_m_sweep_v1 suggested):
   - Root cause: M_A=20 exceeds M_A_crit; W_A interference dominates W_B anti-attractor at phi_j. Theory correct in clean regime per signed_am_active_repulsion_v1 HARD_PASS (frac_anti_b=1.000 at N=2048 5-seed v324).
   - Fix: sweep M_A in {1,2,5,10,20} at N=4096, M_B=1; characterize M_A_crit empirically
   - HP: repulsion_rate >= 0.80 at M_A <= M_A_crit
   - HF: repulsion_rate < 0.20 even at M_A=1, M_B=1
   - P_deflated: 0.55. Less than 1h CPU.
   - Note: M_A=1-3 test was already in exp_dev cycle 3 drop-routing recommendation; execute immediately

### Tier 2 (1-2h CPU or new architecture)

4. **graph_link per-edge keying** (graph_link_per_edge_v1 suggested):
   - Root cause: node-aggregate cosine probe is O(1/sqrt(N)) for all node pairs under multi-edge superposition -- fundamental mechanism mismatch, not substrate physics limit
   - Fix: per-edge VSA bundle encoding: bundle(source_atom, edge_type_atom, target_atom) per directed edge. Standard HDC graph encoding (Kleyko et al. 2022)
   - HP: AUC >= 0.75, N=4096, 3/5 seeds
   - HF: AUC <= 0.55 after per-edge fix
   - P_deflated: 0.60. 1-2h CPU; requires per-edge architecture encoding (new script).
   - Note: graph-substrate research (2026-06-01) confirmed audit/compliance niche at P=0.45 regardless of raw link prediction AUC; per-edge rescue is the product-relevant path

### Tier 3 (lowest priority -- static-phase frameworks CLOSED)

5. **chi_SG replica architecture** (chi_sg_replica_v1 suggested):
   - Root cause: single-chain Glauber gives chi_SG = O(1) trivially (no replica averaging). Edwards-Anderson susceptibility requires disorder-averaged cross-replica overlap.
   - Fix: R=5 disorder draws, Q=5 seeds per draw, compute q_ab for 10 pairs per draw; cost ~10M spin-flips per N value (~1-2h CPU)
   - HP: chi_SG(N) ~ N^gamma, gamma > 0 across N in {1024, 2048, 4096} near alpha_c
   - HF: chi_SG/N constant as N grows
   - P_deflated: 0.32. Lower priority because static-phase frameworks CLOSED per cap_map v319; chi_SG is supplementary cross-check.

---

## Cap_map annotation recommendations (strategy to apply)

| Row | Annotation to add | Action |
|---|---|---|
| graph-substrate (PP adjacency) | "Raw link prediction via node-cosine probe FAILS; per-edge VSA encoding rescue queued" | Annotate, keep EXPLORATORY |
| timeseries sub-row | "all-zero smoke = INFRA_SUSPECT (PROT-021 + N mismatch); v3 fix queued; viability assessment unchanged" | Flag INFRA_SUSPECT |
| tau_mem / PP retention policy row | "Q9 state-vector rescue in flight; formula tau_mem = (1/gamma)*log(1+N*gamma/(2*lambda)) is correct for single-pattern regime; M_eff correction negligible for Kerdock codebook" | Annotate, keep EXPLORATORY |
| signed-AM repulsion sub-row | "Clean-case HARD_PASS (frac_anti_b=1.000 at M_A small, v324); M_A=20 HARD_FAIL; operating envelope rescue (M_A sweep) queued" | Annotate CONDITIONAL, keep EXPLORATORY |
| PP-31c knee sub-row | "v3 widegrid INFRA: far-below-capacity; near-capacity grid redesign queued (M~4000-4500 for N=8192)" | Annotate regime requirement |
| PP-33 chi_SG sub-probe | "Single-chain NOT a refutation; replica-averaging architecture required; deferred behind Tier 1-2 dispatches" | Annotate INSTRUMENTATION_SUSPECT |

---

## PROT-021 infra fix (cross-experiment, highest urgency)

Add tau_min (and any other config-discriminating fields that differ between smoke and FULL) to PROT-021 check keys in _seed_checkpoint.py. Also confirm N is in the check keys for all experiment families. This prevents future false INSTRUMENTATION_SUSPECT entries that waste pipeline slots.

Per exp_dev_decisions_2026-06-02 recommendation: "add tau_min (and other config-discriminating fields) to PROT-021 check keys in _seed_checkpoint.py, or add a per-experiment config_hash field."

---

## Product framing notes

- **Zero genuine refutations**: all 6 items are operating-envelope clarifications. The substrate product narrative is UNCHANGED.
- **Operating envelopes are product assets**: documenting "capability X works in regime R" is a compliance/audit product story, not a weakness.
- **tau_mem formula validation**: if Q9 confirms, enables the per-fact retention policy killer feature (TTL as engineerable parameter).
- **Signed-AM envelope**: once M_A_crit is empirically characterized, "negative-pattern anti-memory in sparse-A regime" becomes a defensible product claim for deletion-cert + active-repulsion narrative.

Acted-on 2026-06-02: 6 reviewed 0 genuine refutations; 4 design + 2 instrumentation rescues all shipped; 3 HP smoke + 2 walk-back MIDDLE
