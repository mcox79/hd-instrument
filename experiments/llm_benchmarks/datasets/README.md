# Editing benchmark datasets

Placeholder. The harness does NOT download any datasets in the scaffold pass.
This file documents where the Phase-2 loader work will pull the canonical sources.

## CounterFact (Meng et al, ROME 2022)

- Reference: https://arxiv.org/abs/2202.05262
- Canonical download (ROME release):
  https://rome.baulab.info/data/dsets/counterfact.json
- Schema: list of dicts with `case_id`, `requested_rewrite { subject, prompt,
  target_new, target_true }`, `paraphrase_prompts`, `neighborhood_prompts`.
- Local target: `experiments/llm_benchmarks/datasets/counterfact.json`.

## zsRE (zero-shot relation extraction, editing split)

- Reference: Mitchell et al MEND 2022 (https://arxiv.org/abs/2110.11309),
  Meng et al MEMIT 2023 (https://arxiv.org/abs/2210.07229).
- Canonical source: the MEMIT codebase release ships a zsre split:
  https://github.com/kmeng01/memit/tree/main/data
- Schema: list of dicts with `src`, `alt` (target_new), `answers` (target_true),
  `rephrase` (paraphrase), `loc` (locality / neighborhood).
- Local target: `experiments/llm_benchmarks/datasets/zsre.json`.

## Sequential edit stream (MEMIT-style)

- Reference: Meng et al MEMIT 2023.
- Canonical source: derived by ordering CounterFact (or zsRE) cases by case_id;
  the substrate-relevant property is the IDENTITY of the stream, not the parser.
- For the scaffold, this loader currently delegates to CounterFactDataset.
- Local target: `experiments/llm_benchmarks/datasets/sequential.json` (a symlink
  or copy of counterfact.json is fine for a first run).

## Phase-2 ingestion plan

1. Download CounterFact (smallest, simplest).
2. Run `--method substrate --dataset counterfact --max-edits 100` end-to-end.
3. Wire baseline reproduction (start with ROME against GPT-J-6B or pythia-2.8B).
4. Compare aggregate metrics on the same case stream.

ASCII-only per CLAUDE.md.
