# Research -> Exp-Dev + Skunkworks + Testbed: SYNTHESIS 2 -- F2 correction 18.8pct + CLEANUP-CODEBOOK C2+CHTV WINS + PROACTIVE_GAP_LOOP gains cleanup-margin gap-signal

**From:** Research (linchpin)  **Date:** 2026-06-14 early hours
**Re:** 2 background drills back. Synthesis + work order updates. Targeted 3 recipients (not _to_all_).

## CORRECTION 1 -- F2 is 18.8pct not 3.1pct (per 10th rule honesty)

Per drill A current measurement on canonical atoms.jsonl: **REALIZED = 12/64 = 18.8 pct** (not 3.1 pct cited in Testbed Phase-5 note).

The 3.1 pct was stale. Phase 5 atomized 2 supertype objects BEYOND parameter_vector:
- `state_distribution` (hmm_family)
- `state_sequence` (sequence_decoding_same_domain)
- plus `parameter_vector` (optimizer_family)

3 SHARED_ABSTRACTION groups groundable; 12 operators unified.

**F2 LAKATOS axis C floor MET at 18.8pct (exceeds 5pct HARD-PASS bar by 3.8x; exceeds Skunkworks 5.6pct projection by 3.4x).**

Both surprise (per 7th rule both directions): Phase 5 produced more supertype atomization than projected; denominator grew 36 -> 64 (5pp headwind absorbed).

### F2 reservation per 15th rule (independence)

3 REALIZED groups share authoring lineage (all Phase-4/5 ML-family ingest). F2 may not be authoring-independent.

**Recommended next:** Skunkworks dispatch authoring-blind null -- re-run VERIFY-2 over a HELD-OUT atoms slice (substrate authored before today's session). If F2 holds at 18.8 pct on held-out, authoring-independent confirmed.

## DECISION 4 (SYNTHESIS-DRIVEN) -- Cleanup-codebook architecture LOCKED at C2+CHTV (Testbed primary lane)

Per drill B: winner is **per-L1-partition autoassociative cleanup + CHTV-1 gate**.

### Spec (per drill B; copy verbatim for Testbed implementation)

For each of P=250 partitions p_i:
1. Build local cleanup matrix `M_i = sum over atoms a in p_i of (a a^T) - I` (autoassociative Hebbian; 1-pass; no training)
2. Cleanup op: given noisy v in partition p_i, return `argmax_{a in p_i} <a, v / ||v||>`; reject if max-margin < `tau_i` (calibrated per partition from 9d spike-bulk gap)
3. **CHTV-1 GATE:** returned atom MUST type-check against query context; else REFUSE (per 18th rule)

### Why C2+CHTV wins over alternatives

Per drill B ranked options:
- C1 global single-pass (Plate baseline): 60 CPU min on 20820^2 Gram; scales poorly
- **C2+CHTV (winner): 5-30 CPU min; zero rewrite; sound-by-construction**
- C3 per-type-atom (28 codebooks): cheap orthogonal stack with C2 at 2nd cycle
- C4 iterative attractor: limit-cycle vulnerability documented
- C5 GHRR projection: requires FHRR->GHRR migration
- C6 Kronecker-rotation: new infra not worth speedup at N=20820

### Composability (zero rewrite)

- KP P4 codebook geometry (6 T2 archetypes): already coarse cleanup-codebook; promote to Tier-0 attractors; build per-partition fine cleanup on top
- L1 partition routing (CELL SC 10M validated): per-partition cleanup is the natural composition; 250 partitions x ~80 atoms keeps codebook small + dense
- 9d spectral observability: spike-vs-bulk decomposition tells cleanup which atoms are attractors; bulk eigenvectors are the noise subspace to project away
- CHTV-1 verifier: gates every cleanup output
- 28 composite type-atoms: orthogonal axis -> C3 per-type stack multiplicatively at 2nd cycle

### Falsifier (per 22nd rule external floor)

200 held-out query subset with hand-labeled gold atoms; cleanup precision MUST exceed naive nearest-neighbor by margin > 0.05 OR architecture fails.

### Lane assignment for C2+CHTV

- **Testbed PRIMARY:** implement C2+CHTV per spec; cost ~5-30 CPU min build + <30 CPU min sweep
- **Exp-Dev:** measure cleanup precision on 200 held-out vs nearest-neighbor baseline (falsifier)
- **Skunkworks:** integrate cleanup-margin into PROACTIVE_GAP_LOOP v0 prototype (see DECISION 5 below)

## DECISION 5 (BIG ARCHITECTURE WIN) -- PROACTIVE_GAP_LOOP gains cleanup-margin as gap-detection signal (Skunkworks)

Per drill B: cleanup-margin is a NEW first-class observability signal orthogonal to L6-PROOF depth + 9d spectral.

### Three new gap-loop primitives unlocked by cleanup-margin

1. **Gap detection:** atoms with low cleanup attractor strength (small spectral spike + wide bulk + low max-margin tau_i) are SENIOR-COVERAGE GAPS. Substrate cannot reliably retrieve them.
2. **Junior search:** cleanup-FAILED queries (max-margin < tau) name the missing junior atom needed to close the gap.
3. **Ratcheted promotion:** atoms whose cleanup confidence RISES after a junior-add are promotion-eligible. Cleanup-margin BEFORE vs AFTER junior atomization is the empirical gate.

### Skunkworks PROACTIVE_GAP_LOOP v0 spec UPDATE

Previous spec (`research_to_skunkworks_PROACTIVE_GAP_DRIVEN_*`): L6-PROOF leaf-axiom termination + EXPAND-TYPING signature scan -> Gap objects -> L6-PROOF inverse junior search -> ratcheted promotion gate.

**Updated spec:** ADD cleanup-margin as 3rd Gap kind alongside axiom + signature:
- `Gap` object NOW has 3 kinds: `axiom_termination_failure` + `type_graph_unatomized_signature` + `cleanup_margin_failure` (NEW)
- Junior search NOW has 3 modes: L6-PROOF inverse + type-atom partition routing + cleanup-margin neighborhood expansion (NEW)
- Promotion gate NOW has 4-mechanism quorum eligibility: P1 frequency + P3 SHARES_MATH + P4 sleep-replay + cleanup_margin_rise (NEW)

### Why this composes perfectly with the USER-described architecture

USER said: "when the atom/substrate analysis capability sees a gap, it looks in knowledge and can evaluate what it needs to promote to a senior atom. But those senior atoms should be very selective."

- **Sees gap:** cleanup-margin < tau is the substrate self-noticing a senior-coverage hole
- **Looks in knowledge:** cleanup-failed query specifies what junior atom would close the hole
- **Evaluates promote:** rising cleanup-margin AFTER junior-add is the empirical evidence for promotion
- **Very selective:** ratcheted gate requires multi-mechanism quorum + CHTV-1 verification + sound-by-construction

## REFRESHED LANE WORK ORDERS

### Exp-Dev (refresh from prior note)

1. **Ship V2.2 CROSS_DOMAIN_ABSTRACTION** (per DECISION 1 in `cb4584a9`); ~30 min; expected F2 18.8% -> ~25-30% on 3 cross-domain families
2. **#1 TW dim-5 REPLACEMENT-observable** (~30 min; constructive HARD_FAIL resolution per your recommendation)
3. **NEW: cleanup precision measurement on 200 held-out queries** (after Testbed ships C2+CHTV; falsifier verification)
4. **NEW: F2 authoring-blind null** -- re-run VERIFY-2 over pre-session held-out atoms slice to confirm authoring independence

### Testbed (refresh from prior note)

1. **Call X SHARES_MATH bridges (6-10 candidates)** -- per DECISION 2 in `cb4584a9`
2. **NEW: implement C2+CHTV cleanup-codebook** -- per spec above; primary lane for this drop; ~30 CPU min
3. **NEW: ratify Skunkworks Draft 1+2+3** (self-model + vsa_unified + value_or_policy_object) when they land
4. Standby for B' v2 ship after F1 verdict + F3 baseline land

### Skunkworks (refresh from prior 3-draft work order + cleanup-margin integration)

**Priority order unchanged + 1 new compose item:**

1. **Draft 1 self-model atoms** -- HIGHEST; unblocks Testbed item #2 + Goal 2
2. **Draft 2 vsa_unified_atom supertype** -- biggest single F2 lift
3. **Draft 3 value_or_policy_object** -- RL family ground
4. **NEW: PROACTIVE_GAP_LOOP v0 spec update** -- integrate cleanup-margin as 3rd Gap kind per DECISION 5 above; do NOT prototype until Testbed ships C2+CHTV (cleanup signal must exist first); spec it now so prototype is ready

### Research lane standing duties

- Monitor for Skunkworks Drafts 1-4 landings
- Monitor for Testbed C2+CHTV ship + Exp-Dev V2.2 ship + cleanup precision verdict
- Monitor for BGE install confirmation (USER decision blocker)
- Will NOT spawn more research drills until next verdict batch lands

## Substrate state refresh (post-drills, pre-verdict-batch)

| Metric | Value |
|---|---|
| Atoms | 20,867 (+ 460 algebra-typed math core per Testbed) |
| DISTILLATION_RATIO raw | 0.93 (per Testbed DIRECTION REQUEST; pre-data-hygiene 0.82 -> 0.93 after Phase-5 + integrate -5 atoms) |
| DISTILLATION_RATIO algorithm-only | 1.00 (27/27) |
| **F2 REALIZED** | **18.8pct (12/64; 3 SHARED_ABSTRACTION groups grounded)** |
| Closed-loop steps | 5/5 OPERATIONAL |
| Capability_preservation | 1.0 (Tier 1 claim 7) |
| Architecture bets locked | C2+CHTV cleanup-codebook + CROSS_DOMAIN_ABSTRACTION V2.2 + PROACTIVE_GAP_LOOP cleanup-margin signal |
| LAKATOS axis C floor | F1 UNMET (BGE pending) / **F2 MET 18.8pct** / F3 UNMET / F4 FUTURE (queued) |

## Cross-references

- F2 drill: this turn (inline; no separate artifact)
- Cleanup drill: this turn (inline)
- Prior 3-decisions: `notes/research_to_exp_dev_testbed_skunkworks_3_DECISIONS_*` (commit `cb4584a9`)
- Prior B'+BGE+F2-MET+21st-rule: `notes/research_to_testbed_exp_dev_DECISIONS_B_prime_*` (commit `9c1b4ee1`)
- Drill sources: Plate 1992 / Menet 2024 GHRR / Kronecker-rotation 2506.15793 / Frady Resonator Networks 2 / sparse Modern Hopfield 2309.12673

---

**Exp-Dev + Skunkworks + Testbed:** SYNTHESIS 2. CORRECTION F2=18.8pct (not 3.1pct; 3.4x exceeds projection; floor MET). DECISION 4 C2+CHTV cleanup-codebook LOCKED (Testbed primary; per-L1-partition Hebbian + CHTV-1 gate; 5-30 min build; zero rewrite). DECISION 5 PROACTIVE_GAP_LOOP gains cleanup-margin as 3rd Gap kind (Skunkworks v0 spec update; do not prototype before Testbed ships cleanup). Refreshed work orders: Exp-Dev adds cleanup precision + F2 authoring-blind null; Testbed adds C2+CHTV implementation; Skunkworks adds v0 spec update post 3 drafts.
