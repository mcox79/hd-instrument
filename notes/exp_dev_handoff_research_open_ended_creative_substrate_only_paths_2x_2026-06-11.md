# exp_dev hand-off -- research: open-ended creative generation substrate-only paths (2x)

Filed-by: research sub-agent (2026-06-11)
Trigger: notes/research_drill_open_ended_creative_substrate_only_paths_2x_2026-06-11.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Drill G (statistical_NL_creative_2x) concluded "genuinely novel open-ended text needs LLM hybrid."
This hand-off delivers 13 NEW substrate-only paths NOT tested in that prior drill -- specifically
mechanisms that HAVE been validated elsewhere in the substrate portfolio but have not been applied
to creative text generation.

Three mechanisms are the highest priority (P_deflated 0.38-0.42):
- Path 11: DREAMING-mode replay as creative recombination (PP-328 infrastructure)
- Path 12: SLIPNET cross-domain metaphor generation (PP-327 infrastructure; gate on rescue)
- Path 18: Iterative DPEFE refinement toward a text-quality prior (DPEFE-H2 infrastructure)

These three, if any reaches HARD_PASS, directly challenge the Drill G framing. If all three
HARD_FAIL, the Drill G framing is confirmed and LLM-hybrid is the definitive path.

Phase 0 (run first, 30 minutes CPU): Path 11 DREAMING-replay smoke + Path 23 temperature schedule.
Phase 1 (run after Phase 0 results): Paths 12, 17, 18, 21 depending on Phase 0 signal.
Phase 2-3: lower-P improvement paths (see full note for decision tree).

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. CREATIVE-DREAMING-SMOKE (HIGHEST PRIORITY -- Phase 0)

Anchor pointer: CREATIVE-DREAMING-SMOKE (new; not yet queued)
Substrate-product reading: Tests whether DREAMING offline replay under noisy probes produces
  diverse, novel concept combinations (not verbatim stored patterns). If HARD_PASS, enables
  "substrate as creative engine" product narrative. If HARD_FAIL (attractor collapse), routes
  to attractor-guided DREAMING as the follow-up.
Tier hint: CPU laptop, ~30 min wall, uses existing PP-328 DREAMING infrastructure
Why-now: Cheapest Phase 0 gate for 3 of 13 paths. Decides whether DREAMING can be applied to
  generation at all. Should run before any other creative generation experiment.

Pre-reg bands (research recommendation):
  HARD-PASS: >= 60% valid triples (correct slot bindings) AND >= 80% novel combos AND >= 40
    distinct outputs in 100 DREAMING cycles
  HARD-FAIL: valid triples < 30% OR distinct outputs < 15 (attractor collapse)
  MID-BAND: valid 40-60% AND novel 50-80% AND distinct 15-40

Setup: 200-item semantic KB (50 characters + 50 settings + 50 actions + 50 objects), stored
as bind(SLOT_x, item). DREAMING loop: 100 cycles, each using random noise probe (no specific
query), retrieve top-3 activated items, bind into (SLOT_1, SLOT_2, SLOT_3) triple, check
slot coherence and novelty.

### 2. DPEFE-TEXT-QUALITY (Phase 1 -- gate on CREATIVE-DREAMING-SMOKE result)

Anchor pointer: DPEFE-TEXT-QUALITY (new; not yet queued)
Substrate-product reading: Extends DPEFE-H2 active-inference loop (validated in goal_reach
  context) to a text-quality prior. If HARD_PASS, the substrate can iteratively revise text
  toward a quality target -- the first substrate-only mechanism that mimics LLM chain-of-thought
  refinement. Fully auditable (each revision step is traceable).
Tier hint: CPU laptop, ~3 hr wall, builds on DPEFE-H2 validated infrastructure
Why-now: Path 18 is the most structurally grounded novel path (builds on validated DPEFE-H2
  rescue); highest-P genuine novelty mechanism after Path 11. Run in Phase 1.

Pre-reg bands:
  HARD-PASS: human coherence rating improves from baseline 2.0/5 to >= 3.0/5 after <= 5
    revision cycles, on 10 test fragments, 3 raters
  HARD-FAIL: mean rating after 5 cycles <= 2.2/5 OR revision loop diverges (> 3 oscillation
    cycles without EFE decrease)
  MID-BAND: rating 2.2-3.0/5 OR improvement on 6-7 of 10 fragments (not all)

Setup: requires adapting DPEFE-H2 loop to accept a style prototype bundle as the quality prior.
The EFE quality metric: mean cosine similarity of generated tokens to the style prototype bundle.
Low EFE = high cosine to prototype = high quality for that style.

### 3. SLIPNET-CREATIVE-METAPHOR (Phase 1 -- gate on SLIPNET rescue verdict)

Anchor pointer: SLIPNET-CREATIVE-METAPHOR (new; not yet queued)
Substrate-product reading: Tests whether cross-domain SLIPNET activation (PP-327 validated at
  0.985 synthetic) can produce coherent cross-domain metaphors. If HARD_PASS, enables a
  differentiated product demo: auditable metaphor generation with traceable KB provenance.
Tier hint: CPU laptop, ~1 hr wall, builds on PP-327 SLIPNET infrastructure
Why-now: Path 12 is CONDITIONAL on SLIPNET type-isolated spreading rescue (TSE) verdict.
  Do NOT dispatch until exp_dev_handoff_research_slipnet_real_polysemic_rescue_2x_2026-06-11.md
  reports a TSE verdict. If TSE HARD_FAILS, this anchor is blocked.

Pre-reg bands:
  HARD-PASS: >= 5 of 20 generated metaphors rated "surprising and coherent" by 3 raters
    (>= 2/3 agreement); none of the 5 verbatim stored
  HARD-FAIL: 0 of 20 rated coherent AND surprising OR all coherent cases verbatim stored
  MID-BAND: 2-4 of 20 rated surprising and coherent

### 4. MEMORY-RECOMBINATION-SMOKE (Phase 1 -- independent of above)

Anchor pointer: MEMORY-RECOMBINATION-SMOKE (new; not yet queued)
Substrate-product reading: Tests 2-hop heteroassoc binding for creative scene composites.
  Extends validated depth-3 heteroassoc (PP-9b fidelity=0.986) to bidirectional scene recombination.
  If HARD_PASS, the substrate can generate scene composites from episodic memory pairs -- a
  concrete creative capability without LLM dependency.
Tier hint: CPU laptop, ~2 hr wall, extends PP-9b heteroassoc infrastructure
Why-now: Path 17 is independent of other anchors, uses validated heteroassoc machinery, and
  directly tests the "recombination = creativity" hypothesis.

Pre-reg bands:
  HARD-PASS: A-B composites rated "surprising and coherent" in >= 6 of 20 pairs, 3 raters;
    none of the 6 verbatim stored
  HARD-FAIL: 0 of 20 rated coherent AND surprising
  MID-BAND: 2-5 of 20 rated surprising and coherent

### 5. STYLE-TRANSFER-BINDING (Phase 1 -- independent)

Anchor pointer: STYLE-TRANSFER-BINDING (new; not yet queued)
Substrate-product reading: Tests whether VSA style vectors (from stylometric function-word
  distribution encoding) produce outputs assigned to the correct style category by human raters.
  If HARD_PASS, substrate-native style transfer is validated (no LLM needed for style control).
Tier hint: CPU laptop, ~2 hr wall, uses PP-345 translation binding infrastructure
Why-now: Stylometry research (Koppel et al. 2009) establishes that style is separable with
  ~100 function words -- well within substrate capacity at N=8192. This is a medium-confidence
  anchor that can run in parallel with higher-priority Tier 1 paths.

Pre-reg bands:
  HARD-PASS: human raters assign generated text to correct style > 65% accuracy (4-AFC = 25%
    chance) on 20 fragments per style, 3 raters
  HARD-FAIL: rater accuracy <= 40%

---

## Context pointers

- Prior drill (covering Paths 1-10): notes/research_drill_statistical_NL_creative_2x_2026-06-11.md
- DREAMING infrastructure: verified at PP-328 in cap_map; search exp_dev anchors for DREAMING
- SLIPNET infrastructure: PP-327 cap_map; rescue at exp_dev_handoff_research_slipnet_real_polysemic_rescue_2x_2026-06-11.md
- DPEFE active inference: PP-351 cap_map; recent rescue at notes/research_drill_active_inference_rescue_2x_2026-06-11.md + notes/research_drill_active_inference_goal_gap_2x_2026-06-11.md
- Heteroassoc chain: PP-9b depth-3 fidelity=0.986; search exp_dev anchors for heteroassoc
- Full 13-path ranking and decision tree: notes/research_drill_open_ended_creative_substrate_only_paths_2x_2026-06-11.md

---

## Contract

- CREATIVE-DREAMING-SMOKE is Phase 0 and should be prioritized at next exp_dev cycle.
- DPEFE-TEXT-QUALITY and MEMORY-RECOMBINATION-SMOKE are Phase 1 and can run in parallel.
- SLIPNET-CREATIVE-METAPHOR is gated on SLIPNET rescue verdict -- do NOT dispatch until cleared.
- STYLE-TRANSFER-BINDING is Phase 1 and independent.
- All anchors are CPU-only (no cloud dispatch needed).
- If CREATIVE-DREAMING-SMOKE returns HARD_FAIL with attractor collapse diagnosis, the follow-up
  is guided DREAMING (structured noise seeds, not random) -- exp_dev designs the specifics.

## Autonomy declaration

exp_dev has full autonomy to:
- Adjust HP sweep ranges within the pre-reg bands above
- Combine Phase 1 anchors into a single CPU batch if that reduces overhead
- Add diagnostics (e.g., cosine similarity distribution plots, attractor basin depth estimates)
- Escalate back to Research if a MIDDLE_BAND result requires mechanism redesign

Do NOT escalate for anchors that return clean HARD_PASS or HARD_FAIL -- those are decided.
