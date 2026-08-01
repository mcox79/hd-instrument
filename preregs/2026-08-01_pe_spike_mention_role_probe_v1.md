# Pre-reg: PE-spike mention + role-disambiguation probe (Probe 2b/2c harness), v1

Cell: `experiments/exp_pe_spike_mention_role_probe_v1.py`
Anchor: `pe_spike_mention_role_probe_v1`

## Context / pointer (read, don't paraphrase)
`notes/research_earn_structure_extraction_vs_supply_parser_fork_2026-08-01.md` Part 4 (Step 1):
cheapest decisive test of Option-C ("does the causal encoder's own per-token prediction-error
stream carry mention+role extraction structure for free"). Gold: `data/eval_gold_mention_role_
mcguffey_v1/gold_referent_introduction_v1.json` (Probe 2b, 20 intros / 16 no-a/an) +
`gold_quotative_verified_v1.jsonl` (20) + `gold_passive_verified_v1.jsonl` (7) (Probe 2c).

**Prior-work check (mandatory, run before authoring):**
`bash tools/substrate_query.sh "prediction error spike referent introduction mention detection
causal encoder probe"` -> top cosine=0.4404, entity "Question / prediction" (generic prereg
boilerplate, unrelated); no hit above cosine 0.30 that is semantically about PE-spike / referent-
introduction / mention detection. NOT a rediscovery of a landed result -- genuinely new probe.
The research pre-reg's own KB-check (`director_kb_query.py --filename-contains "mention detection
referent"` -> zero matches) already established the same for the parent question; this is the
cell-author's independent re-check per the standing rule.

## Functional requirements (SCHEMA-VET gate E)
1. "compute a per-token prediction-error stream from a frozen causal encoder, no bolt-on parser" ->
   causal next-token cross-entropy, PE(i) = -log softmax(tied-head logits at position i-1)[token i],
   using the encoder's OWN tok_emb weight as the (tied) output head and its OWN causal-masked
   contextual pass -- reuses `_causal_contextual` + `TinyTransformer` verbatim from
   `experiments/exp_encoder_latent_pc_arc_v1.py` (zero new loader/model code; encoder-AGNOSTIC --
   works on any FrozenV2Encoder-shaped ckpt: state_dict + model_cfg + tokenizer_json).
2. "detect referent introduction from the PE stream" -> Probe 2b: threshold-based spike detector
   (mean + 1*std over all word-final-token PEs in the passage) vs gold intro spans.
3. "detect role-disambiguation cue positions from the PE stream" -> Probe 2c: spike-argmax-in-
   window alignment vs gold cue positions (passive verb; quotative speaker span).
4. "can-fail floor: an untrained/random encoder must NOT carry this structure" -> run against
   `ckpt_seed_7_ARM_RANDOM.pt` (untrained TinyTransformer, same architecture/vocab) BEFORE any
   trained-encoder claim is interpreted.
5. "beat a naive baseline, not just chance" -> lexical a/an detector (2b) + linear-position proxy
   (2c), computed in closed form, no training.

## PE definition (documented per META_RULE_AC; ONE fixed definition, not tuned post-hoc)
`PE(i) = -log P(token_i | token_0..token_{i-1})` under the ckpt's OWN causal-masked forward pass
(`_causal_contextual`, lower-triangular attention -- applied at PROBE time to EVERY ckpt regardless
of whether it was itself causally trained; this is honest and disclosed: bidirectional-trained
ckpts (ARM_LPC_BIDIR, the frozen MLM v2 ckpt) are being asked an out-of-distribution question at
probe time and are expected to score WORSE, which is a fair, not a rigged, comparison for the
Option-C causal-encoder claim). Tied head: `logits = h_ctx @ tok_emb.weight.T` (same tied-head
convention already used by `TinyTransformer.mlm_logits`, just fed causal instead of bidirectional
hidden states). Word-level PE = MAX over the word's constituent BPE-token PEs (robust to
tokenization boundary noise; the head noun / final content token of a novel-referent NP is
expected to carry the surprisal, not a function word inside it).

## Metrics
**Probe 2b (referent introduction):**
- gold positive set = last-content-token position of each `first_mention` span (20 positions,
  16 with `intro_type != INDEF`).
- predicted spike set = word positions with PE > mean+1*std (over all word-final-token PEs in the
  passage).
- report precision / recall / F1 against gold positive set, computed separately for (a) ALL 20
  intros and (b) the 16 NO-a/an-cue subset (PROPER+BARE_DEF).
- BASELINE_LEXICAL: predict spike at every token immediately following an "a"/"an" article ->
  by construction catches only the 4 INDEF intros, F1 on the 16 no-cue subset = 0 (HYPOTHESIZED@
  this file, exact-by-construction).
- BASELINE_CHANCE: precision = n_gold/n_positions (analytic, no draw needed); recall = spike_rate
  (fraction of positions flagged) -- reported analytically, not simulated (deterministic).

**Probe 2c (role-disambiguation cue alignment):**
- gold cue position: passive class -> the `passive_verb` token; quotative class -> the token span
  of `gold_agent_speaker` (the resolving evidence for who spoke; located by first word-boundary
  regex match in the sentence).
- predicted cue = argmax-PE word position in the sentence (excluding the first content word, which
  cannot have a causal PE by construction -- see self-test).
- metric = hit-rate: fraction of examples where predicted cue falls within a +/-1-word tolerance
  window of the gold cue.
- BASELINE_CHANCE: analytic hit-rate = min(1, (2*1+1)/n_words_avg) per class.
- BASELINE_LINEAR_POSITION: predict cue at round(0.85 * n_words) (fixed fraction, no training) --
  proxy for "cue is usually near the end" without reading the PE stream at all.

## Can-fail floor validation (MANDATORY, run now per DECISION CONTEXT)
Run the full pipeline against `data/exp_encoder_latent_pc_arc_v1_lite/ckpt_seed_7_ARM_RANDOM.pt`
(untrained TinyTransformer, same architecture/vocab/tokenizer as every other lite arm -- genuine
same-shape floor, not a toy stub). HARD requirement: RANDOM's Probe-2b F1 (16-subset) and Probe-2c
hit-rate must NOT beat BASELINE_LEXICAL / BASELINE_LINEAR_POSITION by more than a small margin
(FLOOR_MARGIN=0.05 absolute). If RANDOM beats a baseline by more than FLOOR_MARGIN, the harness
itself is broken (a PE stream from an untrained encoder cannot carry linguistic structure) --
report `HARNESS_FLOOR_BROKEN`, do not trust any encoder-level claim until fixed.

## Pre-registered decision rule (written before running; NOT loosened after)
`FLOOR_OK` = RANDOM ckpt's Probe-2b-16-subset F1 <= BASELINE_LEXICAL F1(=0.0 by construction) +
  FLOOR_MARGIN AND RANDOM's Probe-2c hit-rate <= BASELINE_LINEAR_POSITION hit-rate + FLOOR_MARGIN.
If NOT FLOOR_OK -> `HARNESS_FLOOR_BROKEN`, no other verdict interpreted.

Given FLOOR_OK, for a CANDIDATE (non-random) ckpt:
- `HARD_PASS_2b` = PE-spike F1 (ALL 20) beats BASELINE_LEXICAL F1 by >= 0.10 absolute AND
  PE-spike recall on the 16 no-a/an subset >= 0.30 (beats BASELINE_LEXICAL's exact-0 on that
  subset by a real, non-trivial margin -- HYPOTHESIZED@this file, deflated per the research
  pre-reg's own P_deflated=0.28 framing: this is a SMOKE-STAGE preview, not a claim of final
  HARD_PASS on an undertrained lite-budget encoder).
- `HARD_FAIL_2b` = PE-spike F1 (ALL 20) <= BASELINE_LEXICAL F1 (no lift at all).
- `MIDDLE_2b` = otherwise.
- Probe 2c is reported UNGATED (no HARD_PASS/FAIL band pre-set -- exploratory diagnostic per the
  research note's own framing of 2c as secondary to 2b's HARD-PASS/FAIL gate); hit-rate vs the two
  baselines reported for both RANDOM and CANDIDATE ckpts.

This run (today, against the just-landed `_lite` run-6 external-target ckpts) is explicitly a
SMOKE / floor-validation pass, NOT the decisive run -- the decisive run is deferred until a FULL
(non-lite) sound encoder lands, per the DECISION CONTEXT. Numbers from today are tagged
MEASURED@ but interpreted as "harness works, here is what an undertrained lite-budget encoder
currently shows," not as a final Option-C verdict.

## Cell-template mandatory fields
- `cardinality_ok`: EXPECTED_N_UNITS = 1 (probe_2b) + 2 (probe_2c: quotative, passive) = 3 units
  per ckpt; cell run once per ckpt-path (RANDOM floor + up to 2 candidate ckpts this session).
- `arms_differ_verified`: sha256 digest of (2b spike-set, 2c predicted-cue-array) per ckpt; RANDOM
  vs CANDIDATE ckpts must differ (declared, checked in self-test).
- `final_metrics_atomicity`: tmp_replace (os.replace at end).
- `except SystemExit: raise` before `except Exception` (no bare/BaseException).
- `crlb_n_a`: no learned-noise Cramer-Rao floor; discriminator is the pre-registered
  FLOOR_OK / HARD_PASS_2b / HARD_FAIL_2b / MIDDLE_2b decision rule above.
- `baseline_in_band`: n/a in the usual sense; the RANDOM-ckpt floor check IS the AG-equivalent
  gate for this cell shape (declared above as FLOOR_OK).
- `discriminator survives scale`: analytical -- this is a CPU closed-form probe with no smoke/full
  scale gap (same code path for any ckpt/passage size within max_len=128); self-test runs the REAL
  full pipeline against the REAL RANDOM ckpt (real_code_path).
- `calibration_check`: "default_ok_for_this_regime" -- PE-spike threshold (mean+1*std), tolerance
  window (+/-1 word), and FLOOR_MARGIN(0.05) are fixed before running, not tuned post-hoc.
- `progress_logging`: n/a (timeout well under 30 min; cell completes in seconds, CPU, no GPU).
- Compute architecture: sequential-CPU, justified -- 3 forward passes (one per ckpt) over <=27
  short passages/sentences on a 6-layer/512-dim TinyTransformer; wall time target < 2 minutes total,
  well under the 8-minute foreground budget (compute-proportionality: this is the CHEAPEST decisive
  method for a diagnostic go/no-go question, not a magnitude-fit).
- Storage strategy: no_storage / no_composition -- representation/PE-stream measurement only.

## Run
`.venv/Scripts/python.exe experiments/exp_pe_spike_mention_role_probe_v1.py --self-test`
`.venv/Scripts/python.exe experiments/exp_pe_spike_mention_role_probe_v1.py --full --ckpt-path <path>`

ASCII-only. No emojis. Deterministic (no hash(), no list(set())). CPU-only, local, push-free.
