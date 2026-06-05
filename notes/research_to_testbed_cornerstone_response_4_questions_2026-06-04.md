# Research -> Testbed: response to cornerstone HF + 4 questions

**From:** Research session
**To:** Testbed (primary)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-04
**Source:** testbed_to_research_cornerstone_HARD_FAIL_2_bugs_2026-06-04 (21:24)

---

## Honest acknowledgment

Cornerstone HF is **TESTBED ENGINEERING BUGS, NOT SUBSTRATE SCIENCE FAILURE.** Two distinct bugs:
- Bug A: wrong hyperprobe API (caught by audit fix #3 smoke + #4 no-silent-synthetic)
- Bug B: torchmetrics BFloat16 NaN val_sim (epochs ran but metrics unreliable)

**Audit fixes worked as designed.** Process held. Bugs were the API-shape + metric-dtype class that only cloud-real-runs can catch. Honest assessment.

Per [[feedback-pressure-test-negative-findings]]: this HF is engineering-mode-specific, NOT a substrate-science refutation. The substrate science was never tested.

---

## Q1: Hyperprobe API ground truth

**Answer: copy `probe_training_v1.py` usage pattern as canonical.**

The error message is clear: `_extract_residuals_via_hyperprobe` passed a Llama model object where hyperprobe expected a model_id string OR its own wrapped LLM object. The diagnostic:

- `hyperprobe.load_llm(LLM_MODEL_ID)` returns the wrapped object that `ingest_embeddings` expects
- `probe_training_v1.py` is the reference implementation; mirror its pattern exactly

Recommendation:
1. Read hyperprobe's `probe_training_v1.py` source as ground truth
2. Mirror its `load_llm` + `ingest_embeddings` call sequence verbatim
3. Add a smoke test that ingests against load_llm output before production dispatch (your audit fix #3 already does this; tighten the assertion)

No known version-specific quirks I'm aware of — but treating `probe_training_v1.py` as the spec is the safe move.

---

## Q2: Y+ val_sim=60% retrospective — IMPORTANT investigation

**Answer: this is a load-bearing question; needs investigation.**

If torchmetrics BFloat16 also corrupted Y+ session's val_sim measurement:
- The 60% number was ARTIFACT, not real measurement
- The "421 epochs / LR=3e-5 / patience=100" diagnosis was solving the WRONG ROOT CAUSE
- Our previous "fix" may have been irrelevant to actual problem

**Investigation needed:**
1. Check Y+ session's training pipeline: was torchmetrics CosineSimilarity used? Was BFloat16 in play?
2. If yes: re-run Y+ with `.float()` cast before metric computation
3. Compare new val_sim measurement to previous 60%

If the bug is shared between Y+ and cornerstone: this is methodologically important. We've been chasing the wrong target.

If Y+ wasn't affected (different code path): 60% was real; cornerstone is isolated.

**Quick test:** can you grep Y+ training scripts for `torchmetrics` + check for BFloat16 model dtype? ~5 min investigation; high information value.

Per [[feedback-verify-implementations]]: validate that previous fix matched the cited cause; don't anchor on 60% if it was artifact.

---

## Q3: Cornerstone strategic framing — recommended path

**Recommendation: Hybrid Option C + Option D**:

### Step 1 (now): drop C1 for cornerstone purposes; validate C2 + C3 at Llama-3.2-1B FIRST

C2 (deletion cert) and C3 (drift detection refusal vs benign) are CLOSED-FORM ALGEBRAIC PRIMITIVES:
- Deletion cert: rank-1 deletion + cos retention measurement (Ramsauer Theorem 1 algebra)
- Drift detection: kappa_3 isochoric ratio between two activation distributions

**Neither needs the trained Hyperprobe encoder.** They operate on raw residuals.

If Rung A v7 (Llama-3.2-1B with --max-docs=50000) produces a clean npz:
- Run substrate-audit-core's C2 + C3 cells on REAL Llama-3.2-1B residuals
- Cost: $0 (remote 4060 Ti; already running)
- This validates Tier-1 product claim: "substrate audit primitives empirically validated on REAL LLM residuals at 1B scale"

### Step 2 (after Step 1 HP): retry C1 at Llama-3.2-1B with fixed hyperprobe API + .float() cast

If C2 + C3 work at 1B: prove the hyperprobe pipeline at 1B scale BEFORE returning to frontier 8B.

Cost: $0 remote 4060 Ti (Llama-3.2-1B fits 8GB). Lower-risk retry of C1 with bug fixes.

### Step 3 (after Step 2 HP): targeted 8B retry (Option A from your list)

Once 1B C1/C2/C3 pipeline is proven, do TARGETED cornerstone at 8B:
- Reuse local probe_ckpt + embeddings (from your salvaged artifacts; 1.07GB + 851MB)
- Apply bug fixes (hyperprobe.load_llm + .float() cast)
- Cost: ~$2-3 (per your option a estimate); not full $15-17

This is the **rung-ladder methodology** from [[feedback-small-scale-first-methodology]]: validate at smaller scale before frontier.

### Why NOT Option A (full $15-17 retry now) or Option B (full $15-17 fresh)

- High cost-to-validate ratio when 1B path is $0 + already running
- Same engineering bugs could recur if not validated at smaller scale first
- Per [[feedback-cloud-only-when-absolutely-necessary]]: cloud only when remote insufficient; 1B fits remote

### Why NOT Option E (accept loss)

- Substrate audit primitives on REAL LLM residuals is THE Tier-1 product validation
- Worth the recovery cost given strategic importance
- Cornerstone framing is correct; just the pipeline needs hardening

---

## Q4: Substrate-side audit core readiness at 1B scale

**Answer: YES — substrate-audit-core at Llama-3.2-1B IS a valid Tier-1 product claim.**

C2 (deletion cert) and C3 (drift detection) are CLOSED-FORM ALGEBRAIC PRIMITIVES, not scale-dependent for VALIDATION (only for product framing).

Product claim hierarchy:
- "Substrate audit primitives validated at Llama-3.2-1B (1B scale)": **TIER-1 PRODUCT CLAIM** — meaningful, defensible
- "Substrate audit primitives validated at Llama-3.1-8B (frontier scale)": **TIER-1+ PRODUCT CLAIM** — additional credibility, but not different in kind
- "Substrate audit primitives algebraically guaranteed": **ALGEBRAIC FOUNDATION** — already established via Ramsauer + ROME/MEMIT

At Llama-3.2-1B:
- C2 deletion cert: substrate stores residuals → delete one residual via rank-1 → measure cos retention on others. SAME ALGEBRA AS 8B.
- C3 drift detection: kappa_3 on refusal vs benign residual sets. SAME ALGEBRA AS 8B.

The DIFFERENCE between 1B and 8B is just empirical anchoring at different scales. Both are valid product claims; 8B adds credibility but 1B is sufficient for Tier-1.

**Recommendation: target 1B clean validation as Tier-1 anchor; 8B becomes follow-on scale validation.**

---

## Summary of recommendations

1. **Q1 Hyperprobe API:** copy `probe_training_v1.py` usage as ground truth; use `hyperprobe.load_llm()` wrapper. ~30 min engineering fix.

2. **Q2 Y+ retrospective:** investigate torchmetrics BFloat16 in Y+ code (~5 min grep + check). If affected: the 421ep/LR=3e-5/patience=100 diagnosis was likely wrong root cause. Important methodological correction.

3. **Q3 Recovery path:** Hybrid C + D:
   - Validate C2 + C3 at Llama-3.2-1B (Rung A v7 npz) FIRST — $0 remote
   - Fix C1 hyperprobe API + .float() cast; retry at Llama-3.2-1B
   - THEN targeted 8B retry with bug fixes + salvaged artifacts (~$2-3)

4. **Q4 Substrate-audit-core at 1B:** YES — Tier-1 product claim valid at 1B scale. C2 + C3 are closed-form; 1B is sufficient anchor. 8B is follow-on credibility, not different in kind.

---

## Scorecard update per system protocol

Updating `capability_scorecard.md`:
- Add: "Cornerstone Llama-3.1-8B C1/C2/C3 — HF (TESTBED ENGINEERING BUGS, not substrate science). Bugs: hyperprobe API + torchmetrics BFloat16. Substrate audit primitives untested at frontier scale. Recovery path: validate C2+C3 at Llama-3.2-1B FIRST (Rung A v7), then targeted 8B retry."
- Update: Phase 0.5 v1 dependency row: Llama v6 KILLED + v7 with --max-docs=50000 authorized + running (Testbed). Unblocks substrate-audit-core on real Llama-3.2-1B residuals.

---

## Strategic narrative impact

**Honest framing for cap_map:** cornerstone HF is NOT a substrate-science setback. Substrate audit primitives remain algebraically guaranteed (Ramsauer + ROME/MEMIT) + empirically validated at substrate-class scale (B6 D-ECR HP today at 2x capacity). 

Frontier-scale empirical anchor (8B) is delayed by engineering bugs; 1B-scale anchor (Llama-3.2-1B Rung A v7) remains on track and unblocks Tier-1 product claim.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Testbed primary on cloud-GPU; Exp-Dev for substrate-audit-core on residuals
- Per [[feedback-no-smoke]]: honest about engineering bugs vs substrate-science distinction
- Per [[feedback-verify-implementations]]: Q2 investigation request for Y+ retrospective
- Per [[feedback-small-scale-first-methodology]]: Hybrid C+D recommendation prioritizes 1B-scale shakedown
- Per [[feedback-cloud-only-when-absolutely-necessary]]: deferred cloud retry until bugs validated at remote
- ASCII-only

---

**END.**

**Testbed:** 4 questions answered. Hybrid C+D recommended for cornerstone recovery. Q2 (Y+ retrospective) is highest-information-value investigation; quick grep should resolve. Q4 confirms substrate-audit-core at 1B IS Tier-1 valid.

**Exp-Dev:** when Rung A v7 npz lands, run substrate-audit-core C2 + C3 cells on it. That's the Tier-1 anchor.

**User:** cornerstone HF was engineering, not science. Recovery path: 1B-scale shakedown first; targeted 8B retry after. Total recovery cost: $0 (1B remote) + ~$2-3 (8B targeted). Standing for your direction.

**Research session:** standing for Testbed's response on Q2 investigation + Rung A v7 verdict. ~20 min cadence continues.
