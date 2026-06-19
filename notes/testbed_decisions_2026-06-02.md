# Testbed decisions 2026-06-02

Session-end bookmark so the next testbed session resumes cleanly.

## Headline state at compaction

- **Wave 5 cloud bundle DISPATCHED** (background id `bbelw34ap`; Lambda
  instance `bd9c5a0fce10451ba0449183ca9ff009` in us-south-2; H100 SXM5
  $4.29/hr; predicted $21.45 / 5h wall; max-cost cap $30). 5 cells:
  qd1_spectral_primitives, kappa46_fingerprint (Part A + Part B
  sensitivity sweep), deletion_cert_zratio, combo3_unified_api,
  q_b1_depth_extended. Each anchor binds `_n32768` per PROT-018.
- **PP-8 stays at cap_map 0.60-0.78** post v1b grid (cap_map v316-v317
  pre-committed). Substrate-LLM coupling empirically a memorization
  mechanism (97% overlap; 0/1000 held-out across 3 LR schedules + 2
  key types). Mechanism 2 (Phi-3 embedding generalization) REFUTED.
  Pre-committed product framing: "audit-cert infrastructure for LLM
  memory and caching" -- regulatory moat over technical-novelty moat.
- **Round 6 DECLINED** per user preference [[feedback-short-cloud-runs-preferred]].
  Cells A + B routed back to orchestrator with local-GPU alternatives.
- **Cell 5 (COMBO-1) + Cell 7 (PP-12 L=2)** dropped from Wave 5 per
  research decisions. Cell 5 deferred pending COMBO-1 v3; Cell 7 dropped
  because infrastructure-constrained M_outer < 1.24x10^6 ceiling fails
  the load-bearing envelope-expansion claim.
- **Cumulative Lambda spend today (entering Wave 5)**: $21.49 + Wave 5
  $21-30 predicted = ~$42-51 cumulative day end.

## Pushed commits (this session, chronological)

Recent (today, 2026-06-02):
- 66894a0: Wave 5 Cell 2 (ADD-2 refinement) -- delta-alpha sensitivity sweep added
- 3b1f8d1: Wave 5 Cell 6 (ADD-1) BUILT; batch JSON updated dropping Cell 5
- d83eb8a: Wave 5 cloud N=32768 bundle: 5-anchor scripts + batch JSON (DISPATCH DEFERRED)
- 88eca56: Round 6 declined per user preference; routing + feedback memory filed
- 071ebe6: PP-8 v1b 10-cell deliverable + strategy escalation (FINAL: HARD-PASS overlap + HARD-FAIL held-out)

Earlier yesterday-today chain:
- ccf8ba2, dec52bf, 8d1e44a, c54948b, af5e06a, 4ec7eb2 -- PP-8 phase progression
  (Phase 1 -> Phase 2 -> Phase 2.5 STE -> Phase 2.5 soft -> Path 1c -> Path 1a
  -> v1b 10-cell -> v1+v1' HARD-PASS chain)

## Wave 5 bundle: monitoring paths

1. Launcher polls every 30s -> tee'd to
   `data/testbed_pp8_week2/launch_logs/wave5_*.log`
2. Dashboard "Live" tab reads `progress.json` per cell
3. Per-cell stdout streams real-time (kappa, sigma_sep, depth fidelities)
4. SCP-back at each anchor: `data/lambda_batch_results/<anchor>_<inst>/metrics.json`
5. Harness notifies when full batch completes (id `bbelw34ap`)

## Next-session start: Wave 5 verdict + deliverable

When `bbelw34ap` completes, the next session should:

1. Read full output (5 cells × ~30-60 min each = ~3-5h expected wall)
2. For EACH cell: extract HARD-PASS / MIDDLE / HARD-FAIL verdict per pre-reg
3. File deliverable: `notes/testbed_wave5_unified_n32768_results_2026-06-02.md`
4. File strategy routing if any cell escalates:
   - Cell 2 Part A typically HARD-FAILs at smoke (N=4096); production
     N=32768 should PASS due to large-N cumulant convergence
   - Cell 2 Part B (sensitivity) should HARD-PASS easily (smoke already
     shows 320/93/9.4 at delta-alpha 0.04/0.01/0.001)
   - Cell 6 should HARD-PASS at d5>=0.95, d10>=0.90 per per-hop math
5. STOP after deliverable per [[feedback-no-padding-experiments]] +
   strategy's "no auto-iterate" lock from prior dispatches

## What's still pending (parallel work; not blocking)

- Anthropic Phase 2 production query eval ($20-50; pre-authorized)
- Dashboard Part B (pipeline state view) + Part D (session staleness)
- PP-3 atom-registry design review (research drill in flight from earlier)
- Lambda API key rotation (leaked in earlier transcript; user-flagged
  but not done yet)
- Hard-neg full 50K run ($50-350; awaiting EXPLICIT user auth)
- Cosmetic: N=8192 store + phi3_token_latency.py verdict band

## Key empirical claims standing post v1b grid

PP-8 substrate-LLM coupling:
- 97% memorization accuracy on stored keys (6/6 overlap cells HARD-PASS)
- Substrate is M1-DOMINANT: frozen random keys match Phi-3-derived keys
  at 97% (no Phi-3 forward at init needed)
- Held-out generalization REFUTED: 0/1000 across all 3 LR schedules
- LR-bug hypothesis REFUTED: was eval-sampling artifact (every 50 vs 25)
- Product framing locked: "audit-cert infrastructure for LLM caching"

## Key memory updates this session

- `feedback_short_cloud_runs_preferred.md` (NEW): user prefers short
  cloud runs; long ones ($50+, 10+h) need explicit per-case auth not
  generic envelope
- MEMORY.md updated with the new entry

## Files of interest

- Wave 5 batch config: `tools/cloud/batch_examples/wave5_unified_n32768.json`
- 5 anchor scripts: `experiments/exp_qd1_spectral_primitives_n32768_v1.py`,
  `experiments/exp_kappa46_fingerprint_n32768_v1.py`,
  `experiments/exp_deletion_cert_zratio_n32768_v1.py`,
  `experiments/exp_combo3_unified_api_n32768_v1.py`,
  `experiments/exp_q_b1_depth_extended_n32768.py`
- Cell 5 (deferred but kept): `experiments/exp_combo1_gram_kappa3_n32768_v1.py`
- Research amendment: `notes/research_wave5_cloud_bundle_amendment_2026-06-02.md`
- v1b grid deliverable: `notes/testbed_pp8_v1b_grid_plus_path_a_paraphrase_2026-06-01.md`
- Strategy escalation: `notes/strategy_request_to_strategy_pp8_v1b_grid_findings_2026-06-01.md`
- Wave 5 escalation: `notes/strategy_request_to_strategy_wave5_amendment_addressed_2026-06-02.md`
