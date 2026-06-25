# Next steps: post-basis-finalization substrate-product roadmap

**Date:** 2026-06-25
**Driver:** USER asked "do we know what next steps are after these results?"
**Context:** With the corrected capability inventory (`notes/research_capability_audit_CORRECTION_v2_2026-06-25.md`), substrate basis is essentially finalized. ~26 chain-grade capabilities across base primitives + Stage 2 architecture + Stage 3 application primitives + audit-device primitives + KV memory at scale.

## What the substrate-product IS (as of today, before pending Cell H' v2b + Cell 2 v6 land)

**An auditable, calibrated, 2-hop declarative knowledge device** with:
- Memory + composition + retrieval (chain-grade base)
- Working memory (30+ slots; beats brain's 7±2)
- Multi-axis refuse: (a) "don't know this domain" via audit+intent, (b) "I'm full" via graph-health, (c) "I'm uncertain" via CSP
- 4 calibrated audit primitives (audit-based refuse, graph-health refuse, CSP, deletion/hallucination detection)
- Stage 2 architectural depth: at least 2 chain-grade mechanisms (FREQ_ROUTED_DEEPER + MULTIPLICATIVE_LEVER)
- Encoder upgrade via learned contrastive projection (KV LEARNED_PROJECTION generalizes to held-out facts)
- KG retrieval at M=10,000 facts (M-independent O(d²) superposition store)
- 2 Stage 3 application primitives: intent classifier + templated response
- Graph traversal via cleanup-augmented walk (NESS envelope)

## What the substrate-product ISN'T (definitive)

- NOT a multi-hop reasoner beyond 2 hops (3-for-3 substrate-native multi-hop closure attempts REFUTED today)
- NOT a statistical LM competitor (per USER directive; Tier 4 deferred)
- NOT a compound-query composer (subsumed by Barrier 1 closure)

## Three priority next-steps (in order of leverage)

### NEXT-STEP 1 (immediate; ≤ 1 day): Cert-ledger back-fill + verification

**Problem:** Archaeology earlier today found 65% of recent HARD_PASS results NOT in cert ledger. Capability re-audit found 10 missed chain-grade capabilities. The cert ledger is incomplete.

**Action:** Comprehensive Skunkworks back-fill cycle.
- Atomize the 10 newly-found chain-grade capabilities from capability re-audit
- Atomize consolidation v3 HARD_FAIL (today's gap; ruling exists)
- Atomize META_M4 + META_M5 (ledger rows exist; atoms.jsonl missing)
- Verify cert N count converges (currently 594; should be higher post-back-fill)

**Why this matters:** Substrate-product positioning depends on cert-graded primitives. If we say "audit-device with 4 chain-grade primitives" externally, those primitives MUST be in cert ledger. Right now most aren't.

**Cost:** 1-2 Skunkworks cycles (~30-60min each).

### NEXT-STEP 2 (this week; 2-5 days): Stage 3 productionization smoke

**Problem:** The substrate has Stage 3 application primitives (intent classifier, templated response, audit refuse, CSP, KG retrieval at M=10k) but no demonstration of them composed into a shipping product surface.

**Action:** Build a minimal-viable "audit device" smoke that exercises the full Stage 3 stack on a realistic corpus:
- Input: query stream (mix of in-domain + out-of-domain + ambiguous)
- Pipeline: intent classifier → audit gate (subject + relation check) → graph-health gate → KG retrieval (M=10k) → templated response → CSP confidence label
- Output: answer-with-confidence OR refuse-with-reason (audit/health/uncertain)
- Test: 1000-query mixed corpus; measure (a) in-domain answer accuracy, (b) refuse correctness on 3 axes, (c) CSP calibration ECE, (d) end-to-end latency

**Why this matters:** This is the *product*. If the pipeline composes cleanly, we have an audit-device demo. If it doesn't, we find the integration gaps — which today's chain-grade primitives don't reveal individually.

**Cost:** 1 large cell author + smoke + dispatch; ~1-2 cycles.

### NEXT-STEP 3 (2-3 weeks): Scale-up to 100k-1M facts

**Problem:** KG retrieval is chain-grade at M=10k via dense projected KV (O(d²) M-independent). The substrate-product positioning would benefit from chain-grade at M=100k-1M.

**Action:** Capacity sweep on dense projected KV at progressively larger M:
- M=10k (verified chain-grade)
- M=100k (target chain-grade)
- M=1M (stretch goal)
- Measure recall, keysep, latency, memory footprint at each
- Identify O(d²) constant-factor scaling and find practical M-ceiling for d=768 sigma=0.1

**Why this matters:** "10k facts retrievable" is a small-corpus demo. "100k+ facts retrievable" is a real KG product. Substrate-product positioning shifts accordingly.

**Cost:** 1 GPU dispatch + capacity sweep cell; ~3-6h compute.

## Conditional follow-ups (depend on in-flight cell landings)

### IF Cell 2 v6 SEGREGATED_DUAL_W PASSES (Stage 2 mechanism #3)
- Author heterogeneous-routing v2 with segregated stores per relation type (closes a Tier 1 partial-tier capability)
- Decision criteria: SEGREGATED beats FREQ_ROUTED_DEEPER baseline by ≥ 0.02 BPC, cv ≤ 0.05

### IF Cell 2 v6 SEGREGATED_DUAL_W TIES baseline
- Brain theta-WHEN/gamma-WHAT analog doesn't transport to substrate
- Stage 2 stays at 2 mechanisms; close cleanly with informative null
- No heterogeneous-routing v2 needed

### IF Cell H' v2b NO_FOLDIAK shows 1+ biology arm beats random at production V
- Close encoder upgrade as 2-path positive (learned contrastive projection + biology-native)
- Replicate at adjacent V to establish operating envelope
- Optional: revisit Foldiak v3 redesign if axis-flip fix viable

### IF Cell H' v2b NO_FOLDIAK shows all biology arms TIE with random
- Close encoder upgrade as "learned projection is the substrate-native path; biology-native doesn't add"
- Mu-Viswanath confirmed empirically outside basis-layer cells
- No Foldiak v3 redesign needed

### IF Cell H' v2b NO_FOLDIAK shows biology arms WORSE than random
- Principle O empirically strengthened (engineered structure hurts beyond what we already showed)
- Add to cert as additional MM evidence
- Close encoder negative cleanly

## Strategic positioning summary

Pre-finalization substrate-product story (before today): "Memory + composition + retrieval + audit device; UNKNOWN multi-hop ceiling; UNKNOWN encoder upgrade need; PARTIAL refuse-gate."

Post-finalization substrate-product story (after today + corrected inventory):
**"Auditable 2-hop declarative knowledge device with calibrated uncertainty, multi-axis refuse, learned encoder upgrade, and 2 Stage 2 architectural mechanisms. Holds 30+ items in working memory and retrieves 10k+ facts at recall ≥ 0.80. Per-query latency < 1ms. Zero LLM forward calls at inference. Brain-aligned where the brain has the right answer; honest negative where it doesn't."**

This is shippable. The remaining work is productionization + scale-up + cert-ledger hygiene, not basis-finalization.

## What I'm NOT proposing

- Multi-hop closure retry (3-for-3 refuted; ceiling permanent)
- LM-equivalence pursuit (deferred per USER)
- Semantic consolidation under separate W (deferred; substantial new build for marginal product value)
- More Stage 2 architectural mechanisms beyond what's chain-grade (diminishing returns vs productionization)

## Decision points for USER

1. **Approve Stage 3 productionization smoke as next-step 2?** (this is the biggest item; everything else is housekeeping)
2. **Approve cert-ledger back-fill cycle as next-step 1?** (no new science; just hygiene)
3. **Approve KG scale-up sweep as next-step 3?** (this needs GPU; biggest compute investment)
4. **Anything missing from the substrate-product positioning?** (USER may have product features in mind I haven't surfaced)

— Research (Director)
