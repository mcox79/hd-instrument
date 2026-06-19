# exp_dev hand-off -- research: bipolar-compatible alternative write rules (2x drill)

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_bipolar_compatible_alternative_write_rules_2x_2026-06-05.md
Date: 2026-06-05
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor.

Per [[feedback-no-experiment-design-in-prompts]]: this file names WHAT to test and WHY, not HOW. exp_dev designs the anchor sweep, pre-reg bands, timeout formula, and queue routing autonomously.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): k-gram context binding sweep
Anchor pointer: k-gram XOR-bind sweep over k=1,2,3 on conditional sequence prediction.
Substrate-product reading: If k=2 binding achieves >= 20% accuracy gain over k=1 at M/N=0.05, N=4096, the retrieval-side architectural change (no write change required) is sufficient to lift effective Markov order to 2 with zero write-cost overhead. This is the lowest-cost capability upgrade available.
Tier hint: CPU smoke (< 60s at N=4096), then CPU full (3 seeds x 3 k values x 5 M/N points).
Why now: Write rule drill confirmed context binding is the lever for Markov class; write rule is not. Cheapest actionable test. No queue slot waste risk.

### Anchor 2: PC residual sign-only update vs Hebbian on bipolar substrate
Anchor pointer: Sign-only PC residual update on W_bipolar, sequence prediction accuracy.
Substrate-product reading: If sign-only PC residual achieves >= 15% accuracy gain over Hebbian at M/N=0.10, N=4096, a cert-preserving write rule improvement exists. Combined with Anchor 1 (k-gram binding), this would confirm partial Outcome A.
Tier hint: CPU smoke (< 60s), then CPU full (3 seeds x 2 write rules x 5 M/N points).
Why now: Algebraic analysis says sign-only update loses magnitude; empirical check required to quantify the degradation vs Hebbian baseline.

### Anchor 3 (MEDIUM PRIORITY): Theta burst write K-sweep
Anchor pointer: Multi-step trajectory write at K=1..5, decaying weight schedule eta*gamma^k.
Substrate-product reading: Inspired by hippocampal theta-sequence write architecture (Neuron 2024). If K=3 achieves >= 15% gain in 3-step prediction accuracy at M/N=0.05, this is a novel write architecture with neuroscience precedent that improves multi-step prediction at modest cost.
Tier hint: CPU smoke (K=1,3 only, N=1024), then CPU full (N=4096, K=1..5, 3 seeds).
Why now: Novel finding from cross-domain probe; not previously in exp_dev queue. K is a small integer so compute cost scales linearly.

### Anchor 4 (LOWER PRIORITY): Shadow-W cert verification timing
Anchor pointer: Cert verification protocol on shadow real-valued W vs bipolar W.
Substrate-product reading: Shadow-W architecture enables PC residual write with preserved deterministic cert on the real-valued layer. Cert timing must be < 1ms per fact for product viability.
Tier hint: CPU smoke (N=4096, M=100 facts, single seed, timing measurement).
Why now: Blocking question for whether shadow-W architecture is viable for the cert moat. Quick test (< 10s wall).

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_bipolar_compatible_alternative_write_rules_2x_2026-06-05.md
Prior drill (context): d:/AI/hd-instrument/notes/ (search research_drill_bipolar* for prior entries)
Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Priorities: d:/AI/hd-instrument/notes/ (search priorities* for newest file)

---

## CONTRACT

exp_dev owns: anchor design, sweep grid, pre-reg bands, timeout formula, queue routing, smoke gate.
exp_dev does NOT own: cap_map decisions, verdict classification, strategic interpretation.
This handoff provides task + why. exp_dev provides autonomy over all implementation decisions.

## AUTONOMY DECLARATION

exp_dev has full autonomy over: anchor naming (including _n<N> suffix binding per PROT-018), parameter ranges, seed counts, queue assignment (remote_cpu_queue vs overnight_queue vs gpu_queue), timeout computation, and smoke/full sequencing. Do not wait for orchestrator approval on these choices.
