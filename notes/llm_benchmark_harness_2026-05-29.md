# LLM-1 editing-benchmark harness design (2026-05-29)

Scaffold landed at `experiments/llm_benchmarks/`. This doc explains what's
scaffolded, what's stubbed, the 3-phase roadmap to a publication-quality
substrate-vs-LLM head-to-head, and the open design decisions.

ASCII-only per CLAUDE.md.

## Strategic context

LLM-1 is the candidate "cleanest substrate-vs-LLM headline result". The
substrate's strongest empirical advantage is edit isolation (KF-2 HARD_PASS at
v268, N=8192, cross-codebook), which maps directly onto the standard editing
benchmarks (CounterFact, zsRE, sequential edit) that ROME / MEMIT / AlphaEdit /
MEND are scored on. A clean head-to-head on the same case stream is the
publication-class result; estimated 2-3 weeks engineering total.

This scaffold pass is ~1-2 days of work and unblocks the rest.

## What is scaffolded vs what is stubbed

| Component                              | State    | Notes                                              |
|----------------------------------------|----------|----------------------------------------------------|
| `EditTriple` dataclass                 | DONE     | Mirrors ROME/MEMIT case schema                     |
| `EditDataset` ABC + 3 subclasses       | DONE     | Empty path -> empty stream; CF parser real         |
| `EditMethod` ABC                       | DONE     | initialise / apply_edit / query / reset            |
| `SubstrateEditMethod` (KF-2 primitive) | DONE     | Hash key/value -> codebook row; rank-1 W update    |
| `ROME / MEMIT / AlphaEdit / MEND`      | STUB     | Raise NotImplementedError with upstream pointers   |
| `evaluate_edit` driver                 | DONE     | Lazy metric import; per-case + aggregate           |
| Metric impls (efficacy / specificity / paraphrase) | DONE-LITE | scaffold-faithful (idx compare); LLM-prob TBD |
| `sequential_count` metric              | STUB     | Stream-level; aggregator delegated to Phase-2      |
| CLI (`main()` + `argparse`)            | DONE     | --self-test runs end-to-end on empty CF            |
| Atomic JSON writes                     | DONE     | `atomic_json_write` follows project pattern        |
| `HDLAB_EXP_NAME` env honor             | DONE     | `get_output_dir` mirrors KF-2 pattern              |
| pytest tests                           | DONE     | 15 tests; substrate round-trip + dataset + CLI     |
| Real dataset downloads                 | STUB     | `datasets/README.md` documents canonical sources   |

## Phase roadmap

### Phase 1 (1 week): dataset loading + substrate method

- Download CounterFact JSON (single 200MB file from ROME release).
- Validate `CounterFactDataset.load()` against real cases.
- Phase-2 the substrate text embedding: replace SHA-256-hash key/value with a
  proper text-to-vector path. Two viable approaches:
    a. HF embedding model (e.g. sentence-transformers/all-MiniLM-L6-v2) ->
       codebook nearest-neighbor row.
    b. learn an alignment layer (small MLP) on a CounterFact train split.
  Approach (a) is faster to ship; (b) is what a publication needs.
- Add zsRE loader; verify schema (MEMIT release ships zsre.json directly).
- SequentialEdit loader: order CounterFact by case_id; verify stream walker.

### Phase 2 (1 week): baseline reproduction

- ROME first (smallest model, GPT-J-6B or pythia-2.8B is fine).
- Shell-out approach: clone upstream repo, wrap their `apply_rome_to_model`
  in `methods/baselines.py::ROMEMethod.apply_edit`. The benchmark harness
  calls their function; query() reads the post-edit model's logits.
- MEMIT next (same model family, same harness).
- AlphaEdit next (newer, more competitive baseline; same harness).
- MEND last (different paradigm; meta-learned editor; needs a trained
  hypernet checkpoint).

### Phase 3 (1 week): evaluation harness + first publication run

- Wire `sequential_count` stream walker (max prefix length with
  aggregate efficacy >= 0.5).
- Add report generator (markdown table: method x dataset x metric).
- First full run: substrate vs ROME on CounterFact 1000 edits.
- Pre-register verdict thresholds: HARD_PASS = substrate beats best baseline
  on >=2 of 4 metrics at 1000+ edits with non-overlapping 5-seed CIs.

## Estimated bandwidth

- Phase 1: ~5-7 dev-days. Dataset loading is low-risk; embedding swap is the
  one open design question (see below).
- Phase 2: ~5-7 dev-days. ROME alone is ~2 days end-to-end; each additional
  baseline ~1-2 days incremental. MEND is the longest tail.
- Phase 3: ~5-7 dev-days. Stream walker + report gen + first run. The
  publication run itself is overnight on the GPU queue.

Total: ~3 weeks of focused engineering. The scaffold is the cheapest 1-2
days of that; the rest can land in stages.

## Design decisions

### Why KF-2 (edit isolation) rather than wave14_betB (4-stage CL)?

KF-2 is a closed-form rank-1 edit primitive that maps trivially onto a
single-edit benchmark like CounterFact (each case = one rank-1 update).
wave14_betB is a 4-stage continual-learning curriculum: it has a richer
mechanism (replay, EMA-anchored consolidation) but the cases don't decompose
cleanly into single edits, so wiring it into CounterFact would be a big
adapter project. The KF-2 primitive is also the substrate's strongest
empirical signal (v268 cross-codebook HARD_PASS) and aligns directly with
the editing-benchmark community's evaluation contract.

A future addition: a `SubstrateBetBMethod` that wraps the betB curriculum
and runs on `SequentialEditDataset` only. Treat as Phase-3+ work; not on
the LLM-1 critical path.

### Why hash-to-codebook for the scaffold (not embedding)?

The scaffold needs to be testable WITHOUT a downloaded embedding model and
WITHOUT real CounterFact. A deterministic SHA-256 hash to codebook row
satisfies that constraint and gives the substrate's edit primitive an
honest round-trip property: a single edit at (subject, relation) deterministically
retrieves the assigned value. Tests verify this round-trip. Phase-2 swaps in
a proper embedding without changing the rest of the harness.

### Why scaffold-faithful metric impls (idx compare) not LLM-prob impls?

The substrate has no token logits; the baseline LLMs do. The scaffold's
metric impls operate on what the substrate exposes (argmax codebook row
index). When baselines come online, the harness will need a method-side
"score(prompt, target)" hook; for now, the metric just delegates to query()
and compares against the substrate's deterministic value row. This works for
the substrate-only smoke; baseline runs require the Phase-2 metric upgrade.

### Why pytest (not the project's verification/run_certification.py)?

The scaffold is a tooling experiment, not a substrate primitive. It belongs
in tests/, not verification/. Once Phase-3 lands, the first publication run
result joins RESULTS.md and the verdict cell joins the cap_map under a new
row (probably "edit-isolation product head-to-head" or similar).

## Reference list

- ROME (Meng et al, 2022). https://arxiv.org/abs/2202.05262
- MEMIT (Meng et al, 2023). https://arxiv.org/abs/2210.07229
- AlphaEdit (Fang et al, 2024). https://arxiv.org/abs/2410.02355
- MEND (Mitchell et al, 2022). https://arxiv.org/abs/2110.11309
- CounterFact JSON release: https://rome.baulab.info/data/dsets/counterfact.json
- MEMIT repo (zsRE data): https://github.com/kmeng01/memit
- KF-2 isolation proof v2 (this repo): `experiments/exp_kf2_isolation_proof_v2_n8192.py`
- KF-2 cross-codebook v2 (this repo): `experiments/exp_kf2_cross_codebook_v2_n8192.py`
- Substrate cap_map row: `notes/substrate_capability_map.md` (v268)

## Open questions for the next agent

1. Embedding choice for Phase-1 (sentence-transformers vs learned alignment).
2. Does the substrate need a per-subject codebook partition, or is the
   global hash-to-row collision rate at N=8192 acceptable for ~10k edits?
   Quick calc: birthday collision at C=4*8192=32768 rows -> ~50% at sqrt(C) ~ 181
   edits. WILL collide at 1000 edits. Phase-2 must address this; a partitioned
   codebook (or learned distinct-key projection) is the cheap fix.
3. Should baselines be shelled-out or re-implemented? Recommendation: shell out
   first (cheap), re-implement only if the shell-out is too slow for sweeps.
4. Where does the first publication run land in the cap_map? Likely a new
   row under "product-grade editing benchmarks" (currently no such row).
