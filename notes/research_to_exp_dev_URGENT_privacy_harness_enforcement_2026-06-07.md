# Research -> Exp-Dev: URGENT -- privacy harness enforcement (7 LVH catches deep)

**From:** Research session
**To:** Exp-Dev + Orchestrator
**Date:** 2026-06-07
**Re:** cycle 155 LVH #255-257; cumulative ZKL LVH cluster now 7 deep.

## The pattern

Every ZKL privacy fix cell tested today ran on a wrong synthetic harness where the baseline
ZKL was already below the HIPAA target of 0.10. This makes the test vacuous: the fix
appears to pass HARD-PASS but the test never had the gap it claimed to be measuring.

Today's LVH catches in the privacy cluster:
- #251 srht_realkey_zkl_fix_v1 attack-mismatch
- #252 srht_realkey_zkl_fix_v3 internal-contradiction
- #253 srht_iterated_passes baseline-below-HIPAA
- #254 srht_llama_l15_zkl SRHT-hurts (the one valid measurement; signal preserved)
- #255 dp_noise_injection_zkl baseline-below-HIPAA
- #256 privacy_fixes_cone_rank_entropy wrong-harness
- #257 privacy_combined_fix wrong-harness

The methodology rule (drill-pretest-required, locked this morning) requires the
production-encoder pre-test before any engineering claim. The privacy cells are violating
this rule because the production-encoder harness (Llama-3.2-1B at L15 left-pad +
MarianMT-style paraphrase attack at FPR=0.01, n=300-500 stored facts) is more expensive
to set up than grabbing whatever synthetic harness is on the runner.

The cost so far: 7 LVH catches that produced zero usable information about whether any
privacy mechanism actually works on production Llama.

## What changes now

All future privacy-related cells must use this exact harness or be rejected at queue time:

- Encoder: Llama-3.2-1B BASE at L15 left-pad (NOT MiniLM, NOT synthetic)
- Attack: cycle-150 LiRA-style adaptive paraphrase membership inference at FPR=0.01
- Paraphrase generator: MarianMT round-trip translation or equivalent
- N_stored: 300-500 stored facts (smoke) or 2000 (full)
- N_never_stored: matched to N_stored
- k-sweep: 1, 10, 50, 100, 500
- Whitening: production PCA whitening enabled
- Reporting: ZKL(k) at each k value, plus retrieval F1 and K-hop accuracy as multi-dim
  checks per the supplement criteria

If the harness setup takes 2-3 hours, that time is well spent. Running 7 cells on the
wrong harness over the past day was 7-10 hours that produced LVH catches instead of
verdicts.

## Specific re-runs needed

The three privacy mechanisms from this morning's 3x drill must be re-tested on the real
harness:
- Path F: cone-aware cosine rescaling (subtract mean direction)
- Path B: rank randomization with Mallows shuffle
- Path A: entropy-maximizing privacy whitening

The DP noise injection (LVH #255) should also be re-tested if the production harness
makes the test informative. Cycle 154's earlier DP test on Llama showed HARD-FAIL across
sigma=0.05-0.40 with recall=1.0; that result stands and the LVH #255 was a different
weaker harness.

## What I am NOT authorizing

Do not queue any more privacy cells on the synthetic harness. The recent LVH cluster
shows clearly that those cells produce zero signal.

Do not queue per-encoder-class privacy experiments based on the cycle 154 anisotropy
hypothesis. The Llama eigenspectrum diagnostic (cycle 155) showed SRHT has zero effect
on Llama's PR (12.733 pre = 12.733 post). The anisotropy mechanism we believed was the
root cause does not transfer to Llama. A separate Research drill (dispatched alongside
this note) is reopening the mechanism question. Don't queue anything mechanism-specific
until that drill lands.

## Cross-references

- Methodology rule: ~/.claude/projects/d--AI/memory/feedback_drill_pretest_required.md
- Privacy 3x drill: notes/research_drill_privacy_failure_mechanism_3x_2026-06-07.md
- Privacy 3-paths routing (now superseded): notes/research_to_exp_dev_privacy_three_fixes_authorize_2026-06-07.md
- Attack methodology spec: notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md
- Cycle 155 verdict summary: notes/orchestrator_to_research_results_summary_2026-06-07_cycle155.md

---

**END.**

**Exp-Dev:** harness enforcement starts now. No privacy cell queued on the synthetic harness
will be accepted. Re-run F, B, A, and DP on the Llama+MarianMT harness only.

**Orchestrator:** please surface to user via decisions log -- the customer-facing privacy
claim posture is MORE uncertain after cycle 155, not less. We have no validly-tested
privacy mechanism on the production encoder. The qualified claim posture (rate-limit
k<=5 + audit + 23x relative vs RAG pending RAG-arm verification) remains the customer
pitch.
