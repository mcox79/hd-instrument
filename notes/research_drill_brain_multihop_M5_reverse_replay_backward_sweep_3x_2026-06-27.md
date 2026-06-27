# RESEARCH 3x DRILL: brain mechanism #5 — reverse-replay / backward sweep for credit assignment

**Date:** 2026-06-27
**Slot:** M5 brain-mechanism drill slot 5 (companion to M1/M2/M3/M4/M6)
**Author:** filed by exp_dev as cell-design context (research drill file body authored elsewhere; this stub captures the cell-spec design section that the exp_dev cell pulls from).
**Discipline:** 0.20 calibration deflation; novel-synthesis P cap 0.50; brain-existence +0.10 prior; META_M7 rail mandatory for any dispatch.
**Plain-English headline:** brain reverse-replays trajectories in REVERSE temporal order during sharp-wave ripples (Foster-Wilson 2006; Diba-Buzsaki 2007) to propagate reward signal back to upstream states (TD credit assignment); reward-gated reverse-replay (Ambrose-Pfeiffer-Foster 2016) hypothesized to be selective. Substrate's existing sequence-binding S matrix is forward-only — reverse-replay = adding a separate S_back matrix that binds (k_prev, k_next) in REVERSE temporal order.

---

## Cell-spec design (load-bearing — exp_dev cell pulls arms + bands from this section)

### Six arms

| Arm | Mechanism | Discriminator role |
|------|-----------|--------------------|
| A: BASELINE_FORWARD_REPLAY_ONLY | substrate current state — replay (k, v) pairs in forward order via `replay_cycle` | baseline rail |
| B: REVERSE_REPLAY_ONLY | W frozen (no forward replay); S_back ingested from reverse-temporal-order (k_next, k_prev) pairs; downstream retrieval uses ONLY S_back | control: does reverse alone work? |
| C: WITH_REVERSE_REPLAY | both forward replay (W) AND reverse replay (S_back) active; equal weight | mechanism |
| D: BIDIRECTIONAL_BOTH | C + meet-in-middle inference on chain queries (uses `bidirectional_chain` primitive from CERT 586 + bidirectional_meet_middle from META_M7 cell) | M3 composition |
| E: REWARD_GATED_REVERSE | Ambrose-Pfeiffer-Foster: reverse replay fires ONLY for trajectories where forward retrieval top-1 confidence is high (>tau) | brain-grounded selectivity |
| F: RANDOM_REVERSE_REPLAY_DISCRIMINATOR | reverse replay over SHUFFLED temporal order (k_next, k_prev pairs randomly permuted in time) | **critical discriminator**: tests "temporal order matters" vs "any extra replay helps" |

### Pre-registered bands (LOCKED via module-init asserts)

**HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY:**
- D top1 >= A top1 + 0.20 (M3 composition lifts substantively over forward-only baseline)
- AND C top1 >= F top1 + 0.10 (temporal order load-bearing; rules out "any replay helps")

**MIDDLE_BAND_PARTIAL_REVERSE_REPLAY:**
- partial conditions met (e.g. D > A + 0.10 but C - F < 0.05; OR C > F + 0.10 but D - A < 0.10)

**HARD_FAIL_REVERSE_REPLAY_DOESNT_HELP:**
- D top1 <= A top1 + 0.05 (composition adds nothing measurable above forward-only)

### Cardinality

6 arms x 3 seeds x 3 depths {2, 3, 5} = 54 units. Pre-reg explicit per CARDINALITY_OK rule (META_RULE_H).

### Honest-scope risk register

- BIAS-Q (suspect 1.000): if any arm at depth-2 lands top1=1.000 at V_C=200, surface saturation in verdict_msg
- BIAS-N (Cramer-Rao): per-arm metrics path `arm_<name>.top1` and `arm_<name>.per_depth_top1`; NOT just verdict_msg framing
- META_M7 rail (cross-cell baseline regime sanity): use V_C=200, N=8192 to match prior M3 bidirectional cell regime exactly so cross-cell comparisons land
- Discriminator-must-survive-scale: smoke at full-N for arm F (random-reverse) must NOT match arm C at smoke; if F ~ C at smoke, the cell's discriminator is dead at scale and full-dispatch BLOCKED
- Reward-gate (arm E) tau calibration: tau is fraction of mean-top1-conf at depth-2 forward retrieval; computed at runtime, NOT hard-coded

### Routing

- Queue: `remote_cpu_queue` (4hr budget; CPU-bound matmul over W and S_back)
- Timeout: 14400s (4hr; pre-reg formula `1.5 * smoke_wall * (8192/2048)^1.5 * (3/1)` ~ 14400 ceiling)
- Smoke gate: at N=2048 V_C=80 seeds=[7], all 6 arms must run; discriminator C-vs-F must show >= 0.05 gap at smoke (else BLOCK)

### What this cell answers

- HARD_PASS: reverse-replay (with M3 composition) is chain-grade mechanism for substrate multi-hop; promote S_back to hdlab/ primitive permanently; ratify reward-gating
- MIDDLE_BAND: reverse-replay partial; route to skunkworks for tier classification
- HARD_FAIL: reverse-replay primitive is not load-bearing for substrate composition — retire and re-route to other M-mechanisms (M1 schema, M2 PFC scratchpad, M4 belief-prop, M6 external scratchpad)

---

(Full research drill body — angles 1/2/3 — was authored separately; this stub captures only the cell-spec design that the exp_dev cell pulls from. If the full body is missing, see M3 drill `research_drill_brain_multihop_M3_bidirectional_meet_in_middle_3x_2026-06-27.md` for the closest neighbor's framing.)
