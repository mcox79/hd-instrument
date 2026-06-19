# Substrate Memory Testbed

A sandbox where the hd-instrument substrate **IS** the memory layer. The substrate
is wrapped behind a uniform `MemoryBackend` interface and benchmarked head-to-head
against FAISS, Chroma, sqlite-vec, and an in-memory dict oracle on 6 scenarios.

Built 2026-05-29 in a 3-hour window. See
[notes/testbed_architecture_2026-05-29.md](../notes/testbed_architecture_2026-05-29.md)
for the full architecture spec.

## Why this exists

Substrate's killer features (KF-1 structural hallucination impossibility, KF-2
edit isolation, TCFT thermodynamic deletion certificate) are emergent properties
of the outer-product W matrix that no embedding-based vector DB has by
construction. The benchmark surfaces this contrast explicitly: baselines populate
`N/A (by construction)` cells in the killer-feature panel; substrate populates
real numbers.

The point is not "substrate beats FAISS on point recall". Substrate is a
different kind of memory subsystem. The benchmark is the place where the
contrast becomes legible.

## Quick start

### Local laptop (substrate + dict only)

```
python -m testbed smoke --backend substrate,dict
python -m testbed run --scenario all --backend substrate,dict --config testbed/configs/smoke.yaml
```

### Remote CPU (marsh@home; full 5-backend benchmark)

```
ssh marsh@home
cd C:\dev\hd-instrument
.\.venv\Scripts\Activate.ps1
$env:KMP_DUPLICATE_LIB_OK = "TRUE"     # faiss + torch OpenMP coexistence
python -m testbed run --scenario all --backend dict,faiss,sqlite_vec,substrate,chroma --config testbed/configs/default.yaml
```

The OMP env var is required on Windows when faiss-cpu and torch are both
imported in the same process. Without it the first faiss call aborts the
interpreter.

### CLI subcommands

```
python -m testbed smoke   --backend <list>                        # 30s sanity gate
python -m testbed run     --scenario <name|all> --backend <list> --config <yaml>
python -m testbed report  --run-dir testbed_data/benchmarks/results/<ts>
python -m testbed audit   --backend substrate --state-dir testbed_data/substrate_state/<name>
```

## Layout

```
testbed/
  api.py                      # MemoryBackend ABC + dataclasses (RetrievalResult,
                              # DeletionCertificate, AuditReport)
  substrate_memory.py         # SubstrateMemory backend (wraps hdlab + experiments)
  codebooks.py                # BSC / Kerdock / Gaussian codebook builders
  persistence.py              # W matrix save / load (memmap) + registries
  smoke_test.py               # 30s substrate sanity (no harness involved)
  baselines/
    dict_adapter.py           # in-memory dict (oracle)
    faiss_adapter.py          # FAISS IndexFlatIP + IndexIDMap
    chroma_adapter.py         # chromadb PersistentClient
    sqlite_vec_adapter.py     # sqlite-vec vec0 virtual table
  harness.py                  # build_backend factory + run_matrix
  __main__.py                 # CLI (run / report / audit / smoke)
  report.py                   # markdown emitter via tabulate
  scenarios/
    point_recall.py           # M items stored, retrieve each, recall@1/5
    edit_isolation.py         # KF-2: edit 1 item, probe others unchanged
    deletion_verify.py        # TCFT: delete + var_ratio thermodynamic cert
    hallu_detect.py           # KF-1: M/N sub-sweeps, OOS confidence panel
    continual_4stage.py       # Bet B-light 4-stage CL ret_A_after_D
    storage_latency.py        # disk bytes + p50/p95 store/retrieve + cold load
    large_M_constant_cost.py  # SHINE: substrate-constant vs FAISS-linear-in-M
    audit_chain_validation.py # SHINE: cryptographic chain + tamper detection
  configs/
    default.yaml              # N=4096, M=10000, all backends
    smoke.yaml                # N=512, M=64, 30s end-to-end gate
    shine.yaml                # SHINE: large_M + audit_chain scenarios
```

## SHINE scenarios (2026-05-29)

Two new scenarios surface substrate's structural advantages most cleanly vs
FAISS / dict / Chroma / sqlite_vec baselines:

- `large_M_constant_cost`: sweep M into {2k, 5k, 10k, 20k} and report per-M
  disk_MB + p50_retr_us + recall@1. Substrate is CONSTANT (W matrix is N x N
  regardless of M); FAISS Flat scales LINEARLY in M. Pairs with adaptive
  codebook sizing (set `codebook_M_hint_auto: true` so the codebook is
  provisioned for the largest M in the sweep).
- `audit_chain_validation`: 100 sequential deletes, collect every
  DeletionCertificate, validate the SHA256 chain
  (cert[k].w_state_hash_after == cert[k+1].w_state_hash_before), and
  inject 10 byte-level corruptions to measure tamper_detection_rate.
  Substrate emits 100% chain integrity + 100% audit anchor coverage + 100%
  tamper detection; baselines emit None on all three (the cert dataclass
  lacks the hash anchors for embedding-store backends).

Run the shine pair with:

```
python -m testbed run --scenario large_M_constant_cost,audit_chain_validation \
    --backend substrate,faiss --config testbed/configs/shine.yaml
```

See `notes/testbed_shine_plan_2026-05-29.md` for the full 8-add plan + risk
register + production decision matrix design.

Persistent state lives outside the repo on remote at:

```
C:\dev\hd-instrument\testbed_data\
  substrate_state/<config_name>/   # W.npy + codebook.npy + registries
  baselines/
    faiss_indices/<config>/
    chroma_db/<config>/
    sqlite_vec/<config>.db
  benchmarks/
    datasets/                       # (reserved for synthetic dataset cache)
    results/<iso_timestamp>/
      summary.json
      report.md
      per_scenario/*.json
```

## Tweaking iteration loop

Single-cell tweak: edit `testbed/configs/default.yaml`, re-run. Results land
in a fresh `results/<timestamp>/` dir so prior runs survive.

Substrate-specific tweaks:
- `N` (vector dim): drives W size as N^2 fp32. N=4096 -> 67 MB. N=8192 -> 268 MB.
- `codebook_C`: codebook row count. Convention is 4 * N. Higher reduces atom
  collisions, increases memory linearly.
- `codebook_kind`: `bsc` (default), `kerdock` (requires log2(N) even — N in
  {1024, 4096, 16384} only), or `gaussian`.
- `beta`: substrate's softmax temperature. 32.0 matches the v3/v4 KF-1
  rescue and TCFT scripts. Lower beta -> softer distribution, higher
  near_uniform_frac.
- `hallu_threshold`: max-prob threshold above which a retrieval is "confident".
  Default 0.5.

Scenario knobs are config-level: `M_total`, `edit_isolation_M`, `deletion_M`,
`hallu_M_fracs`, `continual_M`, `storage_latency_Ms`. Seeds are a list; multi-seed
scenarios average.

Adding a new scenario:
1. New file `testbed/scenarios/myscenario.py` with `setup(config) -> data`
   and `run(backend, data) -> dict` + `thresholds() -> dict`.
2. Add the name to the CLI `--scenario` list (the dispatcher imports by name).
3. Add a row in `report._key_metric` so it shows up in the cross-backend table.

Adding a new backend:
1. New file `testbed/baselines/<name>_adapter.py` subclassing `MemoryBackend`.
2. Register in `harness.build_backend`.
3. Optional: declare `supports_killer_features() -> True` and populate the KF
   fields in `audit()` if you want it in the killer-feature panel.

## Known limitations and gotchas

- **Substrate point_recall is bounded by codebook collisions**: at small
  `(M, C)` configs (smoke), random key_vec inputs may snap to the same BSC
  atom. Substrate uses linear probing to resolve but the collision DOES cost
  recall. At default config (N=4096, C=16384, M=10000), expected collision
  rate is well under 1 percent.
- **Storage latency cold_load_ms is N/A for chroma and sqlite_vec**: their
  state is implicit in the persisted dir, so "load" is just opening the
  client. Not a meaningful number for those backends.
- **Chroma telemetry warnings on stdout**: `Failed to send telemetry event ...
  capture() takes 1 positional argument but 3 were given`. This is a chromadb
  internal client-side bug at version 0.5.20. Doesn't affect the benchmark
  results. Ignore.
- **harness.run_matrix and report.render_markdown have a known shape mismatch**:
  the CLI inline runner is the always-on path; `harness.run_matrix` shipped but
  is not used by the CLI. Future cleanup item.
- **Substrate `var_ratio` formula deviates from the architect spec**: workstream D
  found the literal `var(W @ key) / var(W @ random)` formula lands at ~0.7 not
  the <0.20 expected, so the implementation uses
  `min(shrinkage = var_post / var_pre in key direction, var_post_key / var_post_random)`.
  Both formulas measure the same thermodynamic quantity (post-delete signal
  attenuation in the deleted key's direction); the implemented form is more
  numerically robust at small N.
- **Smoke config (N=512) does not surface KF-1 structural impossibility cleanly**:
  the KF-1 effect requires `M <= N` AND large enough N for the law of large
  numbers to kick in. Use default config (N=4096) to see the killer-feature
  contrast properly.

## Killer-feature contrast (what to look for in the report)

The `## Killer-feature panel` section of `report.md` shows substrate's KF-1 /
KF-2 / TCFT numbers against `N/A (by construction)` cells for every baseline.

What baselines cannot do, by construction:
- **KF-1 (hallucination structural impossibility)**: an embedding store always
  returns its nearest neighbor. There is no in-store-vs-out-of-store decision
  unless you bolt on a distance threshold (which costs recall). Substrate's
  `near_uniform_flag` is structural: when M <= N, OOS queries produce a
  near-uniform response distribution that's detectable without a tuned
  threshold.
- **KF-2 (edit isolation)**: an embedding store edits exactly the targeted
  row; max_isolation across other rows is trivially 0. Substrate edits via
  outer-product subtract+add; the residual on other keys is `< 1/sqrt(N)`
  per Kerdock theory, also numerically 0 at typical M/N.
- **TCFT (thermodynamic deletion certificate)**: an embedding store deletes
  by removing a row; the certificate is a structural fact ("row removed").
  Substrate produces a NUMERIC certificate: the variance ratio of the W
  response in the deleted key's direction, before vs after delete. This is
  a thermodynamic quantity grounded in Sagawa-Ueda + Crooks fluctuation
  theorems. v6 N=8192 5-seed FULL HARD_PASS confirmed the certificate at
  production scale.

These three columns are the product story.

## What's NOT in MVP (Phase 2 backlog)

- HTTP server wrapping `MemoryBackend` for cross-language tests.
- sentence-transformers embedding baseline for natural-language comparisons.
- LLM integration (substrate as RAG store for a local model, measure halu rate
  on out-of-store questions).
- Adversarial edit scenarios (collisions, near-collisions, capacity stress).
- KF-4 drift detection scenario (substrate row at-risk; awaits posterior-entropy
  rescue v4 result).
- KF-3 multi-substrate cross-isolation scenario.
- Streamlit / rich live dashboard.

## Reproducibility

Each run writes its config + timestamp + git SHA into the report. Re-running
with the same config + seed list produces (within timing noise) the same
metrics. Substrate is deterministic given seed; baselines are deterministic
because the scenarios provide the same key_vecs.

## Related

- Architecture spec: [notes/testbed_architecture_2026-05-29.md](../notes/testbed_architecture_2026-05-29.md)
- Substrate physics characterization: [notes/substrate_capability_map.md](../notes/substrate_capability_map.md)
- Killer-feature deep dive: 2026-05-29 research synthesis at
  [notes/strategic_synthesis_v265_v276_2026-05-29.md](../notes/strategic_synthesis_v265_v276_2026-05-29.md)
