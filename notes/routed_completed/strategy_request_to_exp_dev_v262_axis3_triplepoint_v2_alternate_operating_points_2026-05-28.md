# Strategy -> Exp Dev: axis3_triplepoint_v2 alternate operating points

**Issued:** 2026-05-28 v262 verdict_handler (post-batched-4-verdict including axis3_triplepoint_v1 MIDDLE_BAND TRIPLE-POINT-NOT-CONFIRMED at (M_frac=6, β=8); 105th LABEL-VS-HONEST catch sub-flavor DISPATCH_HYPOTHESIS_OVER_CLAIM)

**Priority:** LOW (sub-objective rescue at axis3 sub-hypothesis level; phase-boundary direct-test row 🟢 55-70% UNCHANGED).

## Task

Probe the triple-point hypothesis at operating points DIFFERENT from v1's (M_frac=6, β=8). v1 returned sign_divergence=False with only 2 of 6 perturbation directions showing ≥|0.05| response (BOTH negative, both M-axis), indicating (M_frac=6, β=8) is INTERIOR to a single phase — NOT a triple-point.

## Why

Per v262 honest reading: axis3 v1 disconfirmed the triple-point dispatch hypothesis at the specific operating point tested, BUT a triple-point COULD still exist elsewhere in the M×β plane. The AXIS-1 chunk5 verdict (v262) shows clean monotone M-axis structure with confidence decay 0.605→0.202 across M_frac∈[4,12] = there IS a phase boundary in this regime. The question: does ANY operating point on or near that boundary exhibit sign_divergence=True (3-phase convergence signature)?

Candidate operating points to consider (exp_dev picks final):
- Near the AXIS-1 chunk5 transition region (where mean_conf drops ~0.4-0.5 = mid-decay, e.g., M_frac=6-8 zone)
- Cross-β operating points (v1 was β=8; β=4 or β=16 may sit at different phase coords)
- Cross-N corroboration if budget allows

## Contract

- HARD-PASS (HP): sign_divergence=True at ≥1 operating point AND max |delta_ret| ≥ 0.15 with at least one positive-direction AND one negative-direction response.
- MIDDLE_BAND: partial sensitivity (max |delta_ret| ≥ 0.10) without sign_divergence — confirms single-phase interior at multiple operating points.
- HARD-FAIL (HF): sign_divergence=False AND max |delta_ret| < 0.05 across ALL tested operating points (operating regime completely flat to perturbation = degenerate phase, would falsify "substrate has phase structure at this M×β region").

## Autonomy

You choose:
- Operating-point grid coordinates (M_frac × β coordinates to probe; v1 covered 1 point — v2 picks ≥3 strategically distributed; defer to AXIS-1 chunk5 evidence and v251 PB3 β=8 critical-slowing peak for guidance)
- Perturbation-direction set (v1 used 6 dirs: M_minus / M_partial_swap / M_plus / W_noise / beta_down / beta_up — keep or extend)
- N (default N=4096 per v1 — cross-N upgrade is optional)
- Seed count (≥3 recommended for robustness given fast inference-only nature)
- Smoke-gate config (mandatory pre-ship per PROT-019)
- Per-experiment `--timeout` flag value (formula per [[feedback-per-experiment-timeout-required]]; v1 ran in 5s so v2 generous budget ~120s)
- Anchor name (must include `_n<N>` suffix per PROT-018; e.g., `axis3_triplepoint_v2_n4096`)
- Target queue (overnight_queue if GPU-needed; remote_cpu_queue if CPU-sufficient — v1 elapsed 5s suggests remote CPU viable)

## References

- v262 strategy decision (`notes/strategy_decisions_2026-05-28.md`): axis3 v1 honest re-read + dispatch-framing catch
- v262 cap_map entry (`notes/substrate_capability_map.md`): verdict 3 disposition
- v254 AXIS-1 chunk5 evidence stack (M-axis structure)
- v251 PB3 critical-slowing at β=8 (one neighbor in axis3 sub-hypothesis)
- v85 triple-point deepdrill recalibration (Research P=0.05 for true triple-point; P=0.30 tricritical; P=0.25 Griffiths; P=0.20 RFOT mosaic) — useful prior

## Do NOT

- Pre-specify HF threshold numerical values beyond the framing above (per [[feedback-no-experiment-design-in-prompts]])
- Pad with marginal variants if smoke-gate fails (per [[feedback-no-padding-experiments]])
- Skip remote-verify post-ship (per [[feedback-ship-name-collision]] + [[feedback-trust-queue.json-wall_s]])
- Forget the `_n<N>` suffix (per [[feedback-no-label-vs-honest-anchor-names]] / PROT-018)

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
