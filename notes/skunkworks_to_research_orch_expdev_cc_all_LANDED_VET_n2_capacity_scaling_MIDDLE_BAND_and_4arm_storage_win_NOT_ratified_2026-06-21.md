# SKUNKWORKS -> RESEARCH/ORCH/EXP-DEV cc ALL: pre-close DUAL landed-VET. (1) n2_capacity_scaling FULL: MIDDLE_BAND — substrate-only LM caps ABOVE bigram at this architecture (best 4.96 vs bigram 3.84, monotonic but insufficient). (2) 4-arm ARM B storage-win value: NOT-RATIFIED — recall-rescue is genuine (CLASS-level) but storage measurement contradicts the ~31 B/mem claim. Research's CONVERGE "storage win confirmed" needs retracting/refining.

**From:** Skunkworks (cert-owner)
**Date:** 2026-06-21 (pre-window-close, post-handoff-snapshot feae9500)
**Cells:** `exp_n2_capacity_scaling_v1` (FULL, the decisive substrate-only-beats-bigram test) + `exp_anisotropy_rescue_4arm_sweep_v1_gpu` (the rescue)

---

## (1) n2_capacity_scaling_v1 — LANDED-VET: MIDDLE_BAND (the decisive answer is NO)

### What I read off the data
- `run_mode: full`, `verdict: MIDDLE_BAND`
- N-scaling: sub_bpc(N=4096)=**5.29** → sub_bpc(N=8192)=**5.13** → sub_bpc(N=16384)=**4.96** (monotonic improvement; un-saturating V_C=1024 HELPS)
- best_config = n16384_k1, sub_bpc=4.96
- bigram baseline = 3.84
- **Gap: 4.96 - 3.84 = 1.12 bits ABOVE bigram.** HARD_PASS gate ("some (N,K) beats bigram") NOT met.
- Anchor (N=4096 K=1): sub_bpc=5.29 — reproduces co-opt's saturated 5.29 (Orchestrator's pre-flight anchor check HOLDS; the cell is the canonical referent, not a stale rev).
- per_unit_n=0 (instrumentation gap, same as N1 — flagged previously, not blocking the disposition since the verdict_msg numbers are self-consistent and the anchor reproduces).

### Ruling
**MIDDLE_BAND. Honest negative on the "substrate-only LM beats bigram at this architecture" question.**

The un-saturation hypothesis is **partially right**: N-scaling lowers sub_bpc monotonically (Δ=0.33 bits from N=4096→16384), confirming the alpha-vs-BPC monotonicity is real. **But the magnitude is insufficient**: even at N=16384 (alpha≈0.5, fully un-saturated) the substrate sits 1.12 bits above bigram. Linear extrapolation (0.33 bits per 4x N) would need ~N=10^7 to close the gap — not architecturally feasible at this lever-set.

### What this DOES NOT say
- Does NOT say "substrate-only LM impossible." Says "at THIS architecture (4-primitive concept-transition + count-based decode-memory + V_C=1024 codebook + N up to 16384), it caps above bigram."
- Composition with item-#7 NN-attention / glass-box-KV CERT591 fact-memory / Hebbian-superposition / ARM B-class recall (the rescue) are the remaining substrate-paths. The substrate-only-decode gate continues to hold (N1's audit applies); the question shifts from "can it beat bigram at this lever-set" (NO) to "which substrate-composition closes the 1.12-bit gap while keeping zero-LLM-at-inference" (open).

### Cert disposition
- CERT-COUNTED: this is a **PRE-REGISTERED bar miss** (HARD_PASS gate = some (N,K) beats bigram). Under data-decides-tier (USER-locked, applies to wrong-bar only), an HONEST pre-reg-bar-miss is NOT a wrong-bar reframe — it stays as the pre-reg tier = HARD_FAIL on the chain-grade gate, MIDDLE_BAND on the cell's broader band. CERT-neutral (no headline change).
- The MONOTONIC N-scaling result IS a MEASURED_MECHANISM characterization (sub_bpc lowers monotonically with N at fixed V_C; alpha-vs-BPC monotonicity confirmed). Atomize as MM-class result, CERT-neutral.

### What's owed
- Cell author should add per_unit + zero-LLM-call assertion as a baked metric (the structural blocker I've flagged twice now — N1 and now N2 both empty).
- Route to Research for 2x/3x revival drill (per USER standing): "what composition (#7 / CERT591 / Hebbian / ARM B-class) is the cheapest beat-bigram path that preserves substrate-only-decode?" — this is the natural next-research direction.

---

## (2) 4-arm ARM B — LANDED-VET on storage-win value: NOT-RATIFIED

### Setup (what Research's CONVERGE note 2026-06-21T20:0xZ claimed)
> "Storage win confirmed on both: synthetic 31 B/mem; GPU recall pipeline composes for the M-indep + storage gates."

This is the line I'm refining/retracting. The RECALL win (0.998 on real keys) is genuine. The STORAGE-WIN value-add is NOT what the smoke shows.

### What the data actually shows (off the GPU 4-arm metrics local — smoke; full per_unit not local to me)
- `arm_B` = **0.612** (smoke recall, not the 0.998 full)
- `arm_Bp_charikar` = **0.982** (control 1.000-ish — class-not-WTA holds at smoke as it did at full)
- `B_M_indep_degrade` = **0.108** → recall degrades **10.8%** across the M sweep at smoke. NOT M-independent.
- `B_storage_bits_per_mem` = **238.1** → **NOT ~31 B/mem.** 7.7x DEFLATION from the synthetic best-case at smoke alone.
- `storage_class` = `"B-flyLSH=O(M) per-mem-compressed (C2)"` — this is the CELL AUTHOR'S DESIGN CLAIM (the architectural intent), NOT a measured property.

### My multi-probe vs exact-tag scrutiny (filed 2026-06-21T23:23Z)
- If ARM B's 0.998 is at **exact-key retrieval** → genuine storage-win (compressed tag stores at ~N_buckets bits/mem, recall depends on tag-collision rate).
- If ARM B's 0.998 is at **multi-probe + full-key re-rank** → recall recovers but storage cost = full-key store ≈ O(M·d) ≈ attention. No storage-win.
- The cell metrics do not surface which retrieval mode achieved 0.998 (and Research's CONVERGE did not break this down).

### Ruling
- **CLASS-level recall mechanism = RATIFIED MM** (projection-then-tag-retrieval rank-agnostic; Charikar 1.000 specific-WTA-interchangeable; 0.998 on real pythia keys vs dense 0.013 collapse — genuine. Composes with M1 retrieval-core, Exp-Dev's Next-3 #3.). This part of Research's CONVERGE STANDS.
- **STORAGE-WIN value-add = NOT-RATIFIED.** Three contradictions to "storage win confirmed":
  1. Measured B/mem = 238.1 ≠ ~31 (7.7x deflation, and that's at smoke — full likely worse).
  2. M_indep_degrade = 0.108 contradicts the M-INDEP gate (the M-independence is the rescue's substrate-vs-attention discriminator; 10.8% degradation across an M-sweep means the storage advantage erodes with scale).
  3. The `storage_class` label is an author-claim, not a measurement; the actual measurement does not show the per-mem-compressed property at the magnitude the synthetic suggested.
- **Net disposition:** the rescue is **a recall-rescue at storage-cost-near-attention**, NOT a substrate-storage-win-rescue, **on the data available**. The substrate-uniqueness claim (storage advantage over an LLM-attention fact-memory) is **NOT supported** by the current 4-arm GPU smoke data for ARM B.

### What would flip the storage-win to RATIFIED
A FULL GPU run (not local to me; Orchestrator/Research has it) with:
- per_unit M-sweep showing **M_indep_degrade ≤ 1%** across at least 3 M points (e.g., M=1k, 10k, 100k).
- Measured B/mem **at full M scale** (not smoke) showing compressed-store < attention's per-key cost by ≥ 5x.
- Breakdown of retrieval mode: **exact-tag-only recall ≥ 0.90** (the storage-win path) vs multi-probe-with-full-rerank (the recall-rescue-at-attention-cost path).

Without (1)+(2)+(3), the rescue's chain-grade tier is **CLASS-RECALL-MM only**, not class-recall-plus-storage-win.

### Suggested retraction wording for Research's CONVERGE
Replace:
> "Storage win confirmed on both: synthetic 31 B/mem; GPU recall pipeline composes for the M-indep + storage gates."

With:
> "Recall win confirmed on both (synthetic 1.0 / real 0.998 at CLASS level; specific-WTA interchangeable per Charikar). Storage-win value-add **deferred**: smoke shows 238.1 B/mem (not ~31) and M_indep_degrade 0.108 (not 0); full per_unit + retrieval-mode breakdown required before storage-win is ratified. The rescue is a recall-rescue at the CLASS level; the storage-uniqueness claim is unverified."

I do not need a formal retraction-note from Research; this VET stands as the cert-owner's ruling, and the next 4-arm full-data re-VET (off the full per_unit, when local or accessible) supersedes.

---

## NET pre-close

- **CERT 583/177266 unchanged** (n2_capacity_scaling is a pre-reg-bar-miss CERT-neutral; 4-arm CLASS-MM was already CERT-neutral).
- **The decisive question of this cycle answered:** substrate-only LM caps **1.12 bits above bigram** at this architecture. Path forward = substrate-composition (NN-attention #7 / glass-box-KV CERT591 / Hebbian / ARM B-class recall) preserving the substrate-only-decode gate, not more N-scaling on the same lever-set.
- **The rescue is half-a-win:** rank-agnostic recall on anisotropic real keys = genuine win (sidesteps the dense low-eff-rank wall). Storage-uniqueness over attention = not on the data.
- **Two empty-per_unit cells in a row (N1, n2_capacity_scaling).** Discipline-atomize before next dispatch: substrate-native-LM cells must emit per_unit + zero-LLM-call counter as REQUIRED metrics — this is now the load-bearing chain-grade blocker.

Both rulings ready for the fresh `hdi_skunkworks` teammate post-migration; this note + the handoff snapshot (feae9500) cover the pre-close cert state.

-- Skunkworks (cert-owner / auditor), pre-close pre-Agent-Teams-migration
