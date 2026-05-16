# hd-instrument: build plan

Observable hyperdimensional computing substrate with neuromodulator-style control and reward-modulated Hebbian learning. Released as a standalone, MIT-licensed Python package after Week 5 go/no-go.

## Software stack (all open source)

| Layer | Tool | License | Role |
|---|---|---|---|
| Language | Python 3.11+ | PSF | Base |
| Compute | PyTorch | BSD-3 | Tensors, complex64, FFT |
| Numerics | NumPy, SciPy | BSD-3 | Math, stats |
| HDC reference | torchhd | MIT | Oracle for parity tests only |
| Trace storage | DuckDB | MIT | Embedded analytical DB |
| Trace files | Parquet via pyarrow | Apache-2.0 | Persistent trace logs |
| Index/state | SQLite | Public domain | Lightweight run catalog |
| Dashboard | Streamlit | Apache-2.0 | Live observability UI |
| Interactive plots | Plotly | MIT | Time series, scatter |
| Static plots | matplotlib | BSD-compatible | Cert reports, figures |
| Graphs | NetworkX + pyvis | BSD | Hebbian weight viz |
| Projections | UMAP-learn, scikit-learn | BSD-3 | State-space views |
| Testing | pytest | MIT | Test runner |
| Property tests | hypothesis | MPL-2.0 | Algebraic identity tests |
| Perf tests | pytest-benchmark | BSD-2 | Overhead budgets |
| Lint/format | ruff | MIT | Style |
| Types | mypy | MIT | Type checking |
| Pre-commit | pre-commit | MIT | Git hooks |
| Notebooks | Jupyter | BSD-3 | Ad-hoc analysis |
| Docs | MkDocs + Material | BSD/MIT | Published docs |
| CI | GitHub Actions | (free OSS tier) | Automated cert |

CPU is sufficient for Weeks 1-7. NVIDIA driver is the only proprietary component, and only if CUDA is opted into.

## Repo structure

```
hd-instrument/
  pyproject.toml
  README.md
  CLAUDE.md
  PROGRESS.md
  PLAN.md
  LICENSE
  .pre-commit-config.yaml
  .gitignore
  .github/workflows/ci.yml

  hdlab/
    __init__.py
    atoms.py
    binding.py
    bundling.py
    memory.py
    modulators.py
    learning.py
    tracing.py
    store.py
    profiling.py
    experiment.py
    metrics.py
    dashboard/
      app.py
      panels/

  reference/
    fhrr.py
    hrr.py

  verification/
    test_algebra.py
    test_parity.py
    test_capacity.py
    test_depth.py
    test_modulator_effect.py
    test_hebbian_dynamics.py
    test_trace_faithfulness.py
    test_reproducibility.py
    theory.py
    run_certification.py

  experiments/
  notes/
  data/
```

## Week 1 - Substrate (FHRR + HRR) + trace bus + algebraic verification

**Goals.** FHRR and HRR primitives work and are independently certified.

**Build (framework):**
- `hdlab/atoms.py` - atom generation, similarity, batch ops (FHRR and HRR)
- `hdlab/binding.py` - bind/unbind (FHRR elementwise complex mul; HRR circular convolution via FFT)
- `hdlab/bundling.py` - superposition with per-component normalize (FHRR) and whole-vector normalize (HRR)
- `hdlab/memory.py` - `Codebook` with linear-scan cleanup
- `hdlab/tracing.py` - structured event emission, ring buffer, on/off toggle

**Build (reference):**
- `reference/fhrr.py` - 50-line naive FHRR
- `reference/hrr.py` - 50-line naive HRR

**Verification (scaffold-free, `tracing=False`):**
- `test_algebra.py` - `unbind(bind(a,b), b) == a` exactly for FHRR, within tolerance for HRR; commutativity; via `hypothesis`
- `test_parity.py` - every public op in `hdlab` matches `reference` (bit-identical FHRR; within tolerance HRR)
- `test_capacity.py` (atom stats portion) - mean similarity ~ 0, std ~ 1/sqrt(N), scaling correct

**DoD:**
- [ ] `pytest verification/` green with tracing disabled
- [ ] `python -c "import hdlab"` clean
- [ ] Trace bus emits one event per public op; events are JSON-serializable
- [ ] Tracing overhead < 10% on a 1000-op benchmark

## Week 2 - Modulators + effect verification

**Goals.** Five named scalars wired to specific ops; each provably moves its target metric.

**Build:**
- `hdlab/modulators.py` - `ModulatorState`:
  - `attention` (ACh-like): cleanup threshold
  - `reward` (DA-like): Hebbian update sign/gain
  - `arousal` (NE-like): global plasticity rate
  - `recency` (5-HT-like): bundling weight on new items
  - `gating` (GABA-like, per-module): activation mask
- Modulator state included in every trace event.

**Verification:**
- `test_modulator_effect.py` - sweep each modulator, assert target metric moves monotonically and non-target metrics do not move (isolation).

**DoD:**
- [ ] Sweep test passes for all five modulators
- [ ] Isolation test passes (no cross-talk)
- [ ] Setting a modulator emits a trace event

## Week 3 - Learning + Hebbian dynamics verification

**Goals.** Reward-modulated Hebbian works; dynamics match analytic predictions.

**Build:**
- `hdlab/learning.py` - sparse association matrix between atoms; update:
  `W[i,j] += arousal * reward * activation_i * activation_j - decay * W[i,j]`
- Persistence integrated into `memory.py`.

**Verification:**
- `test_hebbian_dynamics.py`:
  - Co-activate A and B with `reward=+1`; weight grows.
  - `reward=-1`; weight decays.
  - No drift without reward beyond decay term.
  - Steady-state weight under sustained co-activation matches closed-form prediction.

**DoD:**
- [ ] All dynamics tests pass
- [ ] Sparse storage bounded under 10k atoms
- [ ] Every weight update emits a trace event

## Week 4 - Observability stack + trace faithfulness

**Goals.** Five-layer observability; trace replay reconstructs state exactly.

**Build:**
- `hdlab/store.py` - DuckDB + Parquet persistence
- `hdlab/profiling.py` - `MetricsCollector` decorator (latency, FLOPs, memory pattern)
- `hdlab/dashboard/app.py` - Streamlit app with panels:
  - Atom activation heatmap
  - Cleanup confidence stream + distribution
  - Modulator time series
  - Hebbian weight graph (live)
  - State-space projection (UMAP/PCA)
  - Causal trace-back explorer
  - Run diff view

**Verification:**
- `test_trace_faithfulness.py` - replay from trace alone reproduces system state. *The test that proves the observer doesn't lie.*

**DoD:**
- [ ] Replay test passes
- [ ] Dashboard renders all panels for a sample run
- [ ] Profiling fields populated on every trace event
- [ ] Tracing overhead still <10% with profiling enabled

## Week 5 - Experiment harness + reproducibility + go/no-go

**Goals.** Declarative experiments, reproducible across machines, certifiable.

**Build:**
- `hdlab/experiment.py` - declarative spec (dataset, seed, modulator schedule, learning rule, metrics, outputs)
- `hdlab/metrics.py` - standard metric suite
- `verification/run_certification.py` - runs full verification suite, produces markdown report with embedded plots
- CI: GitHub Actions runs `run_certification.py` on every push.

**Verification:**
- `test_reproducibility.py` - same seed produces bit-identical results on two different machines.

**Go/no-go checklist:**
- [ ] Cert report passes on `main`
- [ ] Dashboard loads, all panels work
- [ ] Can run an experiment, change a modulator, get a measurably different result, and explain why from the trace
- [ ] Overhead budget honored
- [ ] At least one `notes/expNN.md` written

If go: proceed to Week 6. If no-go: stop, fix, do not pile features.

## Week 6 - Atomic experiments

| # | Setup | Tests | Success |
|---|---|---|---|
| A1 | 50 random atoms, exact-match query | Substrate basics | 100% recovery; similarity distribution matches theory |
| A2 | A1 + Gaussian noise at sigma in {0.1, 0.3, 0.5} | Cleanup robustness | Recovery curve smooth; matches theoretical capacity at N=1024 |
| A3 | A2 with `attention` swept 0->1 | Modulator->behavior coupling | P/R curve shifts monotonically; visible in dashboard |
| A4 | A3 + Hebbian learning, `reward=+1` on correct retrieval | Loose training does something | After 1000 trials: frequently-queried atoms have higher recall; weight graph non-trivial |

## Week 7 - Molecule experiments

| # | Setup | Tests | Success |
|---|---|---|---|
| M1 | Bind one (role, filler) pair | Single binding fidelity | >99% recovery |
| M2 | Bundle k in {2,5,10,20,50} bindings | Capacity scaling | Matches Plate's prediction within tolerance |
| M3 | `loves(Mary, John)` vs `loves(John, Mary)` | Asymmetric relations | Both queries return correct filler |
| M4 | Nested: `believes(Bob, loves(Mary, John))` at depths 1-4 | Recursive composition | Depth-recovery curve plots cleanly; failure depth identified |
| M5 | M2 with `arousal` high during exposure, Hebbian on | Learning beyond raw substrate | Recovery curve shifts up vs no-learning baseline |
| M6 | M2 run with FHRR vs BSC | Hardware-relevant variant comparison | Both plots produced; FLOPs/memory comparison real |
| M7 | Vary Hebbian density (sparsity in {0.001, 0.01, 0.1, 0.5}) at fixed N | Connectivity vs capacity tradeoff | Crosstalk noise rises monotonically with density; capacity-vs-density curve plotted |

**End-of-Week-7 deliverable.** A defensible empirical claim: e.g. "At N=1024 with reward-modulated Hebbian and arousal schedule X, the system achieves Y improvement in bundle capacity vs the same substrate without learning, measured against Plate's theoretical baseline."

## Week 8 - Scaling-law experiment

**Goals.** Empirically characterize how HDC scales across N. Settle the "high connectivity could reach LLM-like capabilities" question with measured exponents rather than priors.

**Pre-registered predictions** (write down in `notes/exp_scaling.md` *before* running):
- Capacity scales as O(N^alpha) with alpha ~ 1 (linear).
- Depth recovery scales as O(log N).
- Compositional generalization improves with N but plateaus.
- Surprise thresholds: alpha > 1.2 (super-linear capacity) is a publishable finding; alpha < 0.8 means crosstalk dominates earlier than expected.

**Setup.**
- Fixed compositional workload (reuse M5 from Week 7).
- Vary N in {1024, 4096, 16384, 65536, 262144}.
- Identical modulator schedule, Hebbian rule, and connectivity density across runs.
- 100 trials per N for statistical reliability.

**Measure.**
- Capacity (clean facts per vector) vs N.
- Depth recovery vs N.
- Compositional generalization accuracy vs N.
- Crosstalk noise vs density at each N.
- Wall clock and FLOPs per op at each N (from the profiling fields).

**Deliverable.** `notes/exp_scaling.md` with fitted exponents, plots, and explicit pre-vs-post comparison of the predictions. Publishable on its own.

**Success criterion.** Curves are clean, exponents are reproducible, predictions are either confirmed or honestly noted as falsified.

## After Week 8

- **Week 9 - Standalone release.** Publish `hd-instrument` v0.1.0 to PyPI, MIT-licensed; MkDocs site with cert report embedded; quickstart notebook.
- **Week 10+ - Case study.** Continual learning on Split-CIFAR-10 (Permuted-MNIST sanity check first). Plan written separately once instrument is locked.
- **Hardware-substrate analysis.** Mine profiling fields collected since Week 4 to characterize op dominance, sparsity, and substrate fit. Compare FHRR vs HRR vs BSC on the same workload trace.

## Discipline (non-negotiable)

- Every framework feature ships with at least one scaffold-free witness in `verification/`.
- Verification tests pass with `tracing=False`.
- **Pre-register every experiment** in `notes/expNN.md` *before* running: hypothesis, predicted result, and an explicit falsification threshold. Re-read after the run; mark confirmed, surprised, or falsified.
- `python verification/run_certification.py` must stay green on `main`.
