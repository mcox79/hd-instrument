# exp_dev hand-off -- research: late-layer retrieval crash in large causal LMs

**Filed-by:** research sub-agent 2026-06-06
**Trigger:** notes/research_drill_large_lm_late_layer_retrieval_crash_2026-06-06.md
**Pause state:** check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT +
AUTONOMY. It does NOT specify anchor names, sweep grids, threshold formulas, HF1/HF2/HF3
numerical bounds, queue choice + ETA, or pre-committed cap_map decisions. exp_dev designs
all of that.

---

## Anchor Candidates (rank-ordered)

### 1. fp16 70B late-layer sweep (HIGHEST PRIORITY -- already authorized)
**Anchor pointer:** Decisive H1-vs-H2 discriminator for 70B retrieval crash.
**Substrate-product reading:** If H2 confirmed (crash persists at fp16), the 1B fp16 L=15
production design is further validated as optimal; 70B is not a viable scale-up path.
If H1 confirmed (fp16 monotonic), 70B at fp16 becomes viable at ~L=74, opening a richer
representation path at 20x higher cost.
**Tier hint:** Cloud run (~$3-5). Same task as CLOUD-1b: top-5-RP on SQuAD-v2, 500 queries,
1000 passages, shuffled gold. Same 5 layer points: 50, 60, 68, 74 + at least one earlier (40
or 44). fp16 model weight (no quantization).
**Why now:** CLOUD-1b data is the empirical anchor; this is the immediate follow-up that was
authorized in the same run. Research drill provides the mechanistic framing; experiment
provides the ground truth. H1 vs H2 has major architectural implications.

### 2. Anisotropy diagnostic at L=50 vs L=74 in existing 70B NF4
**Anchor pointer:** Layer-wise average cosine similarity between 500 query embeddings at L=50
vs L=74. Near-zero cost (no new forward passes needed if CLOUD-1b activations are cached;
otherwise a quick additional pass on the saved checkpoint).
**Substrate-product reading:** Direct measurement of anisotropy increase confirms H2 mechanism
without ambiguity. If avg cosine similarity at L=74 >> L=50 (e.g., 0.92 vs 0.65), anisotropy
is confirmed as the discriminability killer.
**Tier hint:** Local CPU or remote CPU. Should take < 5 min if activations can be re-extracted
from the same model.
**Why now:** Cheapest possible diagnostic. Can be run before or alongside fp16 run.

### 3. Encoder vs decoder comparison at ~130M scale
**Anchor pointer:** Compare MiniLM-L6-v2 (22M) vs a ~130M causal LM (e.g., Llama-3.2-1B
early layers, or GPT2-small) vs a ~130M encoder-only model on the same SQuAD-v2 retrieval
task. Specifically: does the 3-5x MiniLM advantage hold at matched parameter count?
**Substrate-product reading:** If encoder-only models are categorically better at matched
scale, the substrate extraction architecture should migrate to encoder-only as a long-term
direction. If the advantage collapses at matched parameters, the gap is about bidirectionality
specifically.
**Tier hint:** Local CPU smoke. Cheap (<60s on laptop CPU for 130M model).
**Why now:** Informs the long-term extractor architecture decision without cloud cost.

### 4. 70B-Instruct NF4 layer sweep at same 5 points
**Anchor pointer:** Does instruction tuning shift the late-layer crash onset in 70B NF4?
**Substrate-product reading:** If Instruct shows milder crash, instruction-tuning partially
preserves semantic geometry in late layers -- suggesting fine-tuning path for future
large-model extraction. If same crash, the mechanism is baked into pretraining architecture.
**Tier hint:** Cloud run (~$3-5, same budget as fp16 sweep). Can be batched with anchor 1.
**Why now:** Directly tests whether the crash is fixable via post-training alignment, which
has large product implications for Phase 4 v3+.

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_large_lm_late_layer_retrieval_crash_2026-06-06.md
- CLOUD-1b empirical data: embedded in research note; original results from CLOUD-1b run
- Cloud portfolio synthesis: d:/AI/hd-instrument/notes/ (search for cloud portfolio synthesis 2026-06-06)
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

exp_dev is expected to:
1. Check pause flag before dispatching any anchor.
2. For anchor 1 (fp16 70B): batch with anchor 4 (70B-Instruct) on the same Lambda instance
   to amortize bootstrap cost. Both use same task setup; shared model load overhead.
3. For anchor 2 (anisotropy diagnostic): determine if CLOUD-1b activations are available
   cached; if not, estimate cost of a new extraction pass.
4. Pre-register HARD-PASS / HARD-FAIL bands per feedback-envelope-expansion-fail-bands
   before queueing. The research note section 4 provides the PREDICTED thresholds;
   exp_dev sets the FORMAL pre-reg bands.
5. Write metrics.json with required fields (verdict/verdict_msg/elapsed_s/summary)
   per feedback-metrics-required-fields-write-metrics.

## Autonomy Declaration

exp_dev has full autonomy over:
- Anchor naming (must satisfy _n<N> suffix contract per PROT-018)
- Sweep grid specifics, learning rates, seeds, batch sizes
- Queue selection (remote GPU, remote CPU, Lambda cloud)
- Exact threshold formulas and HF1/HF2/HF3 numerical bounds
- Whether to batch anchors 1+4 together or run separately
- Whether anchor 2 is worth the pass cost given cached activations

exp_dev does NOT have autonomy over:
- Whether to run anchors at all (orchestrator verdict; this handoff is the trigger)
- Overriding the pause flag (must check data/orchestrator_paused.flag)
- Cap_map decisions (verdict_handler owns)
