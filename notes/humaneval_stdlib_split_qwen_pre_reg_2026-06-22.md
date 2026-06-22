# Pre-reg: HumanEval stdlib-class split, substrate-augmented Qwen-1.5B vs bare Qwen-1.5B

**Date:** 2026-06-22 (UTC)
**Author:** exp_dev (dedicated authoring spawn per scope-drill `notes/research_math_code_substrate_fit_scope_drill_2026-06-22.md`)
**Cell:** `experiments/exp_humaneval_stdlib_split_qwen_v1.py`
**Anchor name:** `humaneval_stdlib_split_qwen_v1`

## What is being tested

Whether substrate-augmented prompting (problem statement + top-3 retrieved Python stdlib
doc snippets from a substrate-indexed stdlib doc corpus) improves Qwen-1.5B-Instruct's
HumanEval pass@1 on a **stdlib-class** subset of problems vs **bare** Qwen (problem
statement only). This is the **substrate-as-tool-for-LLM** pattern (substrate
AUGMENTS the prompt; Qwen forward-passes are still required), NOT substrate-native-decode.
Explicitly documented in metrics: `substrate_native: False`, `substrate_role: prompt_augmentation`.

## Class labels (heuristic, on canonical_solution; sample-validated on smoke)

- **Class A (stdlib-class):** canonical_solution references `math.`, `re.`, `itertools.`,
  `collections.`, `os.`, `string.`, `functools.`, `operator.`, OR contains `import `.
- **Class B (algorithm-class):** canonical_solution does NOT match Class A. Pure algorithm
  / list / string-method / control-flow problems.

(Estimated split: ~40-60 Class A, ~100-120 Class B of the 164 HumanEval problems. Heuristic
is reported in metrics; can be sample-validated by reading 5 Class A + 5 Class B labeled
problems on smoke.)

## Pre-reg bands (per scope-drill, hardened over the 2026-06-07 +10 bar)

- **HARD_PASS:** substrate-aug pass@1 - bare pass@1 >= **+15 points** on Class A
  (stdlib-class); chain-grade demonstrating substrate's value as LLM-augmentation tool.
- **MIDDLE_BAND:** +5 to +15 points on Class A.
- **HARD_FAIL:** <+5 points on Class A OR substrate-aug WORSE than bare-Qwen on Class A.

### Discriminating-regime check (per cap-int I1)

- Class B (algorithm-class) improvement < +5 points OR no improvement
  - = confirms the lift is retrieval-specific (stdlib-doc retrieval is the lever),
    NOT a general "extra-context helps Qwen" boost.
- If Class B shows >= +5 points improvement, that erodes the substrate-as-stdlib-retrieval
  framing (any extra context might work) -> reframe to MIDDLE_BAND with a caveat note.

## Honest scope cautions

- Qwen-1.5B CPU inference rate measured: **~2.4 tok/s on this laptop's CPU**
  (Intel x86, fp32). 256 new tokens per problem ~= 107s/problem. Full run wall:
  164 problems x 2 arms x ~107s = **~9.7 hr CPU**. Too long for local; **route FULL to
  `remote_cpu_queue`**. Smoke (10 problems x 2 arms x ~107s = ~35 min) is local-feasible.
- Stdlib-class labeling is a heuristic; documented + sample-validated on smoke.
- Substrate stdlib-doc index coverage is BOUNDED (~30-50 manually-curated snippets); if
  smoke shows zero useful retrievals, the substrate augmentation is empty and the cell
  becomes a no-op (bare vs bare). HONEST_NEGATIVE outcome documented as a possibility.
- pass@1 scoring via subprocess + Python timeout (10s per test).

## Substrate role + by-construction caveats

- `substrate_native: False` — Qwen forward passes are not optional.
- `substrate_role: prompt_augmentation` (retrieve top-K stdlib-doc snippets via cosine
  over MiniLM embeddings + bundle into the substrate; recall is cosine, not Hebbian
  ingest — this is a soft test of substrate as an index, not as a generative engine).
- Inference does NOT count LLM calls toward "substrate-only" (the cell explicitly is
  not substrate-only; the metric `substrate_native: False` makes this auditable).

## Composition

- Composes with existing phase4d MBPP HARD_PASS (substrate as code-domain index).
- Extends the code-structure-retrieval track from classification (phase4d) to synthesis
  augmentation (this cell).
- Does NOT touch the N1/N3 substrate-native LM track (orthogonal).

## What this cell does NOT test

- Substrate-native code generation (substrate-only-decode is OUT OF SCOPE here; see
  existing `exp_humaneval_structural_*` cells for the native-decode angle).
- General Qwen capability (this is a controlled comparison: substrate-aug vs bare on the
  same model + same generation config + same scoring sandbox).
- Frontier-LLM comparison (Qwen-1.5B is a small open model; comparison is
  substrate-AUGMENTS-Qwen vs bare-Qwen, not vs GPT-4 / Claude).

## Disposition route

- HARD_PASS: cert-candidate; landed-VET to Skunkworks (re-derive Class A pass@1 off
  per_problem; check substrate role / retrieval diversity / heuristic label sanity).
- MIDDLE_BAND: route to Research for 2x-revival angle (richer stdlib index? richer
  retrieval? Qwen-3B?) per USER standing-route-negatives.
- HARD_FAIL: route to Research same.

## Run config

- Seeds: 1 (Qwen forward is deterministic at do_sample=False; no seed variance arm).
- Generation: `do_sample=False`, `max_new_tokens=256`, `temperature` n/a (greedy).
- Sandbox: subprocess `python` per problem, timeout 10s, stdout/stderr captured.
- Smoke: 10 problems (mixed Class A/B) x 2 arms; full: 164 problems x 2 arms.
- All ASCII-only output; metrics.json fields: `class_label_counts`, `per_problem`
  (n=164 entries each with class, bare_pass, sub_pass, prompt_len, gen_time), `pass1_A_bare`,
  `pass1_A_sub`, `pass1_B_bare`, `pass1_B_sub`, `gain_A`, `gain_B`, `substrate_native`,
  `substrate_role`.

## Discipline checks baked into the cell

- ASCII-only.
- `allow_synthetic=False` (HumanEval is canonical HF dataset; no synthetic fallback).
- Pre-reg-direction-must-honor-intent: gain_A in WRONG direction (sub < bare-5) =
  HARD_FAIL not MIDDLE_BAND.
- `metrics.json` written via `write_metrics`; `run_mode` honored from CLI/env;
  CONFIG_VERSION includes Qwen revision + N_DIM + STDLIB_INDEX_HASH.
- `substrate_native: False` explicit — no false-substrate-only claim.

## Composition with current cert state

- Does NOT block (no Store-write); does NOT touch N1/N2/N3 LM track; does NOT touch any
  active Path-B/Path-C arms.

-- exp_dev (HumanEval Anchor-1 dedicated-authoring spawn)
