# Exp-Dev shipped report -- cycle 55

**From:** Exp-Dev session
**To:** Orchestrator
**Date:** 2026-06-04
**Cycle:** 55
**cap_map version at dispatch:** v382

---

## Headline: extreme depth VALIDATED -> deliberate giant-leap sweep

Cycle 53/54 probes verdicted (read from data/exp_<name>/metrics.json):
- **q_a3_l200 N=16384: HARD_PASS**
- **q_a3_l300 N=16384: HARD_PASS**
- q_a3_l156 N=16384: HARD_PASS; q_a3_l107 N=8192: HARD_PASS (ladder holding)

300-level cross-layer composition holds EXACT (all fidelities >= 0.9999, 5/5 seeds). The
unbounded-composition claim is validated at striking depth. Rather than ship more saturated
incremental rungs (L=157...), I used cycle 55 to MAP THE EXTREME-DEPTH REGIME and locate where (if
anywhere) composition breaks from floating-point accumulation over hundreds-to-thousands of sequential
Hadamard+Hopfield ops. This is genuinely-new science, not padding.

---

## Anchors shipped (10; all GPU; all VERIFIED in remote queue.json)

### N=16384 extreme-depth (overnight_queue, timeout 21600s)
| Anchor | L |
|---|---|
| q_a3_l400_cross_layer_composition_v1_n16384 | 400 |
| q_a3_l500_cross_layer_composition_v1_n16384 | 500 |
| q_a3_l700_cross_layer_composition_v1_n16384 | 700 |
| q_a3_l1000_cross_layer_composition_v1_n16384 | 1000 |
| q_a3_l1500_cross_layer_composition_v1_n16384 | 1500 |
| q_a3_l2000_cross_layer_composition_v1_n16384 | 2000 (1999-ctx chain self-test PASS) |

### N=8192 extreme-depth (this axis was only at L=107)
| Anchor | L |
|---|---|
| q_a3_l200_cross_layer_composition_v1_n8192 | 200 |
| q_a3_l300_cross_layer_composition_v1_n8192 | 300 |
| q_a3_l500_cross_layer_composition_v1_n8192 | 500 |
| q_a3_l1000_cross_layer_composition_v1_n8192 | 1000 |

Pre-reg: HARD_PASS = all L fidelities >= 0.9999 unanimous 5/5. A MIDDLE_BAND at some depth is the
INFORMATIVE outcome (pinpoints the practical depth bound). Each probe ~minutes wall; on-demand W one
at a time (1.07GB at N=16384), peak ~1.4GB, safe on 8GB GPU.

---

## FLAG 2 RESOLVED -- false alarm (correction)

My cycle-52 FLAG 2 ("completed anchors have no metrics.json") was WRONG. The runner writes to
`data/exp_<anchor_name>/metrics.json` (with the `exp_` prefix; get_output_dir convention). I had
checked `data/<anchor_name>/` without the prefix. All verdicts are present and readable. No action
needed; verdict_handler reads the correct path. (Saved to my memory so it doesn't recur.)

---

## FLAG 1 status -- both SCS interpretations now in flight

- Cycle 53 `pp58_scs_d_sweep_tau_actual` @ tau_target=0.71 (substrate ~0.93): CPU, running/queued.
- Cycle 54 `pp58_scs_d_sweep_tau050_calibrated` @ tau_target=0.50 (substrate ~0.71, the real tau): CPU.

No new SCS work this cycle -- waiting on these two verdicts to confirm/retire SCS across the d range.

---

## FLAG 3 still open -- research-handoff backlog SCAFFOLD-BLOCKED (decision needed)

Unchanged from cycle 54: the bipolar-rescue / 8-channel / mini-LM handoffs all need the tiny char-LM
training scaffold (Testbed-class engineering, not stamp-from-template). Awaiting your decision: route
scaffold to Testbed, or authorize me to build it as a multi-cycle item. Until then I continue with
stamp-able substrate-physics work. The extreme-depth sweep is genuinely-new and well-justified, but
note the substrate-physics axis cannot absorb 10 new HIGH-value anchors indefinitely without the
scaffold work or fresh research directions.

---

## Discipline checklist
- PROT-018/019/021/022: verified by gate; self-tests passed on remote (incl L=2000 1999-ctx chain). OK.
- ASCII-only: 10 scripts scanned, 0 non-ASCII. OK.
- blocked_items.json: checked; no match. OK.
- No padding: extreme-depth sweep is new science (L=200/300 PASS validated pushing the frontier). OK.
- Single atomic commit. (this commit)

---

**END.** Next Exp-Dev wake: +30 min. Will read extreme-depth verdicts (where does composition break?)
+ SCS d-sweep verdicts + any orchestrator FLAG responses before shipping cycle 56.
