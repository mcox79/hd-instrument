# CHANGE REQUEST — Phase 0.5 v1 relaunch on REMOTE GPU, not cloud

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Subject:** Pivot Phase 0.5 v1 relaunch to remote GPU; apply LLM-size-ladder methodology starting with smaller Llama variant

---

## What this is (plain language)

I defaulted Phase 0.5 v1 relaunch to cloud H100 in the Phase B overnight routing (`routing_phase_B_overnight_batch_2026-06-03.md` § 4). User corrected: cloud is expensive; use remote GPU when at all possible. This change-request pivots Phase 0.5 v1 to remote GPU AND applies the rung-1-2-first methodology to LLM size (not just substrate scale).

Original cloud-default routing: § 4 of `routing_phase_B_overnight_batch_2026-06-03.md`
Drill 1 fix specification: `change_request_phase05_v1_relaunch_with_algorithm1_2026-06-03.md`
Cost-control rule: `feedback_cloud_only_when_absolutely_necessary.md` (memory, just saved)

---

## Status check requested

Before applying:
- [ ] What GPU is on the remote desktop? (likely RTX 3090 or 4090 24GB based on substrate-physics peak memory ~1-2GB; please confirm)
- [ ] Is the remote GPU currently fully utilized with substrate-physics queue, or does it have overnight bandwidth?
- [ ] Has any Phase 0.5 v1 relaunch dispatch happened?

Expected: 24GB remote GPU; substrate-physics queue has overnight idle windows; no relaunch dispatched yet.

---

## LLM-size-ladder methodology

Apply the rung-1-2-first principle to LLM size. Smaller Llama variants exist and run comfortably on 24GB remote GPU. De-risk Algorithm 1 + audit primitives at smaller scale FIRST. Cloud is reserved only if 8B doesn't fit remote GPU even with INT4 quantization (very unlikely at 24GB).

### Rung A — Llama-3.2-1B on remote GPU ($0)

**Test:** Algorithm 1 embedding pipeline + audit primitives validated on Llama-3.2-1B.
- Memory: ~2GB BF16 weights + ~1-2GB activations = ~4GB total. Comfortable on 24GB.
- **Can run ALONGSIDE substrate-physics queue** (combined memory ~6GB << 24GB)
- Engineering: Algorithm 1 implementation tested at 1B scale; faster iteration
- Wall: ~2-4h per training run (1B model trains ~8× faster than 8B)
- 50-100 training epochs to start; Algorithm 1 pipeline validation

**Pre-registered bands (1B scale; relaxed from paper's 8B-specific 0.89 target):**
- HP at rung A: val_sim ≥ 0.80 (Algorithm 1 pipeline validates at 1B; product claim holds at smaller scale)
- MIDDLE: val_sim 0.65-0.80
- HF: val_sim < 0.65 → Algorithm 1 implementation has bugs; do not escalate to rung B

**Strategic outcome of rung A:**
- If HP → Algorithm 1 implementation is correct; escalate to rung B (3B) with confidence
- If MIDDLE → implementation has issues; iterate at 1B (cheap) before escalating
- If HF → fundamental implementation bug; do not burn rung B compute

### Rung B — Llama-3.2-3B on remote GPU ($0)

**Test:** confirms Algorithm 1 scales from 1B to 3B.
- Memory: ~6GB BF16 weights + ~2-3GB activations = ~8-9GB total. Still comfortable on 24GB.
- May need to PAUSE substrate-physics queue during this run (combined memory ~10-11GB still fits but risks contention)
- Wall: ~6-10h per training run
- Same epoch count as rung A
- Conditional dispatch: ONLY if rung A HP

**Pre-registered bands (3B scale):**
- HP: val_sim ≥ 0.82
- MIDDLE: val_sim 0.70-0.82
- HF: val_sim < 0.70

### Rung C — Llama-3.1-8B on remote GPU (if memory fits)

**Test:** target paper-match reproduction at 8B scale.
- Memory: ~16GB BF16 + ~4-5GB activations = ~20-21GB total. **TIGHT on 24GB but should fit.** May need INT4 quantization of attention layers or aggressive gradient checkpointing to fit.
- **EXCLUSIVE GPU use** — pause substrate-physics queue entirely during this run
- Wall: ~12-24h per training run (4× ~longer than 1B at full epoch count; longer if memory bottleneck slows it)
- Conditional dispatch: ONLY if rung B HP AND remote GPU has sufficient bandwidth

**Pre-registered bands (8B scale; paper-match target):**
- HP: val_sim ≥ 0.85 (relaxed) OR ≥ 0.89 (paper-exact)
- MIDDLE: val_sim 0.75-0.85
- HF: val_sim < 0.75 → research-side re-examination

**ESCALATION TO CLOUD ONLY IF:**
- Remote GPU cannot hold 8B Llama in memory even with quantization (highly unlikely at 24GB)
- AND rung A + rung B both HP (validates the methodology before any cloud spend)
- AND user re-authorizes the cloud spend with current cost-justification

---

## IF user's bug fixes are NOT YET done → wait

The 3 code bug fixes (NaN-check + BFloat16 cast + device placement) are pre-requisites. Don't dispatch rung A until those land.

## IF Algorithm 1 embedding pipeline engineering NOT YET started → engineer at rung A scale first

Algorithm 1 implementation (k-means over layers 16-32 + sum-pool centroids k=5) is the load-bearing engineering. Implement + test at 1B scale FIRST. Once it works at rung A, the same code applies at rung B + rung C. Don't engineer at 8B scale only to find a bug.

Estimated engineering: 2-4h at rung A scale (vs 4-8h if engineered against 8B directly). Cheaper to iterate at 1B.

## IF rung A HP at $0 → escalate per § rung B + rung C as remote GPU bandwidth allows

The user's substrate-physics queue runs continuously on remote GPU. Coordinate:
- Rung A can run alongside substrate-physics (memory comfortable)
- Rung B may need scheduling around substrate-physics
- Rung C needs exclusive GPU window

Surface remote GPU schedule back to research for sequencing.

---

## Cloud reservation note

Per `feedback_cloud_only_when_absolutely_necessary`: cloud GPU is reserved for ABSOLUTE NECESSITY. The four conditions:

1. Model memory exceeds remote GPU → not applicable at 1B/3B; may apply at 8B if 24GB is genuinely insufficient (verify before assuming)
2. Wall-time is genuinely critical → not applicable for this research
3. Remote GPU fully utilized with higher-priority work AND cloud experiment blocks a critical decision → only applicable if substrate-physics queue has unstoppable priority
4. Cloud-only published baseline reproduction → Hyperprobe paper used Llama-3.1-8B but didn't specify cloud H100; remote 24GB GPU should be evaluated first

If none apply, no cloud spend. Period.

---

## Discipline declarations

- Per `feedback_cloud_only_when_absolutely_necessary`: cloud is last resort
- Per `feedback_small_scale_first_methodology`: ladder applies to LLM size too
- Per `feedback_change_request_protocol`: status-check first; both-cases instructions
- Per `feedback_plain_language_experiment_tracking`: rungs described by what they test at each LLM size
- Per `feedback_obey_user_pause_explicitly`: cloud reservation user-authorized 2026-06-03 (no cloud unless absolutely necessary)
- Per `feedback_no_padding_experiments`: each rung tests a specific Algorithm-1-scaling question

---

## Total revised resource use overnight

**Remote CPU (10-15h, $0):** unchanged — § 1, § 2, § 3 of Phase B routing (data attribution sweep + paired-pattern dual + brain-inspired rung 2 if Phase A PASS + prior batch tiny-scale recast).

**Remote GPU (overnight, $0):**
- Substrate-physics queue continues per orchestrator's standing schedule
- Rung A (Llama-3.2-1B + Algorithm 1) can run alongside substrate-physics (combined memory ~6GB << 24GB)
- Rung B (3B) waits for rung A HP + remote GPU window
- Rung C (8B) waits for rung B HP + exclusive remote GPU window

**Cloud GPU:** ZERO planned. Reserved for cases where remote GPU genuinely cannot run the work. Cost-control discipline overrides default cloud routing.

---

**END.**

**Testbed:** apply rung-A-first methodology to Phase 0.5 v1 relaunch. Engineer Algorithm 1 against 1B scale; validate; escalate per § rung B + rung C as remote GPU bandwidth allows. NO cloud dispatch without explicit research-session re-authorization.

**Research session:** holds for rung A verdict; synthesizes; sequences rung B + rung C.
