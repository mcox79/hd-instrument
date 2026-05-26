# Prereg: wave14_sagawa_ueda_pareto_multiprotocol_v1

**Date**: 2026-05-23 (emergency refill batch #3)
**Queue**: overnight_queue (GPU)
**Hypothesis class**: Cap 1 Pareto-front envelope multi-protocol

## Scientific claim under test
Existing Cap 1 work (CROOKS_NOISE_ENVELOPE_PARTIAL) showed the substrate satisfies delta_S < 0.05 under modest noise. This experiment maps the Pareto front: vary M_base (loading), p (noise rate), and noise injection point (fwd_only / rev_only / both_phases) to find the boundary of the Cap 1 envelope.

## Design
- N=4096 (GPU)
- M_base in {50, 100, 200, 400}
- p_noise in {0.0, 0.05, 0.10, 0.20}
- protocols in {fwd_only, rev_only, both_phases}
- 10 seeds (11..20), 30 trials per cell
- Standard Crooks-FT delta_S = |H_erased - H_baseline| (retrieval entropy diff after insert-erase round trip)

## Hard-fail thresholds
- Self-test 4/4 PASS
- p=0 baseline cell must satisfy delta_S < 0.05 (substrate is reversible without noise)
- metrics.json validate + atomic write

## Verdict labels
- CAP1_PARETO_PASS: pass rate (delta_S < 0.05) >= 0.7 across all (M, p, protocol) triples
- CAP1_PARETO_MIXED: pass rate in [0.4, 0.7]
- CAP1_PARETO_KILL: pass rate < 0.4
- CAP1_PARETO_INCONCLUSIVE: structural failure

## Expected runtime
N=4096 bf16 matmul; 4 M * 4 p * 3 protocols * 10 seeds * 30 trials = 14,400 trial-runs each ~6 matmuls. ~30-45 min wallclock GPU.

## Implications
- PASS => Cap 1 envelope is broad; safe operating regime spans M up to ~10% of N at p up to 0.10
- MIXED => maps the Pareto front: which (M, p, protocol) combinations work
- KILL => Cap 1 envelope is narrow; substrate fragile under multi-protocol noise
