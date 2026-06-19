# Week 5 Go/No-Go Review

**Date:** 2026-05-16
**Decision:** **GO** to Week 6 (atomic experiments).

## What's complete (Weeks 0–5)

- **Substrate** (FHRR + HRR): atoms, binding, bundling, cleanup, all algebra verified.
- **Modulators**: five named scalars; attention gates cleanup, recency biases bundling; both wired into trace events.
- **Learning**: reward-modulated Hebbian with lazy decay-on-read. Empirical steady-state matches `W_inf = eta/decay` to 9 significant figures.
- **Observability**: DuckDB-persisted traces, per-op `elapsed_ns` from `perf_counter_ns`, replay reconstructs Hebbian state to 1e-9.
- **PDF reporter** (`python -m hdlab.dashboard --trace ... --output ...`) and Streamlit dashboard share helpers.
- **Experiment harness** (`hdlab.experiment.run`) wraps the seed/trace/persist/PDF/log loop; reproducibility tests confirm same-seed determinism in process.
- **Results logging**: per-experiment artifacts in `data/<name>/` plus rolling `RESULTS.md`.

## Verification status

- **38 tests passing, 2 skipped** (the two skips are Week 7 placeholders: `capacity_curve` and `nested_structure_recovery`).
- Cert report regenerable via `python verification/run_certification.py`.

## Go/No-Go checklist (from PLAN.md)

- [x] Cert report passes on `main`.
- [x] Dashboard panels render (PDF reporter, 6 pages).
- [x] Run-an-experiment-and-explain-the-difference works: diagnostic attention sweep at `att ∈ {0, 0.2, 0.5, 0.9}` rejects the `0.9` query while accepting the others, with the rejection visible in the cleanup-outcomes page of the PDF.
- [x] Overhead budget: smoke test passes; full ratio-vs-baseline measurement deferred to Week 4's note about batched/sampled tracing.
- [x] At least one `notes/expNN.md` written (`notes/diagnostic.md` with pre-registered predictions and filled-in results).

## What we have NOT yet done

- Cross-machine reproducibility: only in-process determinism is asserted; bit-equality across two boxes will be confirmed by CI (GitHub Actions on `ubuntu-latest` plus a local Windows run).
- Tracing overhead ratio test under representative workload: deferred to Week 4's sampled/batched path when needed.
- Real experiments: Weeks 6–8 produce the first findings.

## Risks identified

1. **Diagnostic is a heartbeat, not a finding.** The PDF currently shows that the instrument works, not that anything novel is true.
2. **Attention sweep tolerance:** with stronger jitter (factor 3.0 phase noise) we now see 1 rejection out of 4 attention levels; the threshold curve will be properly characterized in Week 6 experiment A3.
3. **HRR inverse fidelity at low N** is asserted only as `sim > 0.5`; tighten after collecting empirical distribution during Week 6.

## Decision

The platform meets every Week 5 acceptance criterion. Proceed to Week 6 (atomic experiments A1–A4).
