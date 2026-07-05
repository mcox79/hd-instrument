# Research drill: capability-gap map + brain-grounded build roadmap toward a standalone glass-box-LLM substrate

Date: 2026-07-05. Owner: Director (research). Type: constructive build-roadmap (USER REFRAME).

## Framing (USER-locked)
DROP the "where do we WIN vs LLM+RAG" competitive framing entirely. The question is CONSTRUCTIVE:
to build a fully-functional substrate that HAS glass-box-LLM capabilities (perception, memory,
reasoning, generation, continual learning -- all interpretable, brain-grounded), what are the
capability GAPS from where we are today, and what is the ordered BUILD PATH? For each capability an
LLM has that we lack, name the BRAIN-GROUNDED mechanism to BUILD it (not borrow from an LLM).
No "is it worth it vs LLM." The LLM capability list is a build INVENTORY, not a comparison bar.

Substrate concept-query run 2x before drafting (per USER-locked discipline):
- "targeted unlearning..." -> top hit `notes/research_drill_llm_substrate_integration_survey_5x_2026-06-09.md` (unlearning taxonomy; NOT reused -- competitive angle dropped)
- "mechanical faithfulness guarantee..." -> wordnet atoms only; no prior build-roadmap overlap. Prior arc work on THIS (build-roadmap) concept: NONE.

## Current state (grounded off-disk: director_plan.json U0-U4 + 07-04 state pointer + memory)
| Capability | State today | Evidence |
|---|---|---|
| PERCEPTION (encoder) | PARTIAL, in-flight rescue | GSBC_EXPAND2X done; concept-encoder ~0.66 CHARPOS vs 0.85 target; distillation FAILED full-scale (BLOCK 0.31); R1 objective-fix VALIDATING |
| MEMORY (algebra+storage) | WORKS-TYPICAL, hub-limited | FHRR bind/bundle typical; mediocre-on-hubs (superposition crowding); dense-projected-KV recall 0.83-0.96 (CERT 591); attention-over-substrate-keys for fact recall |
| REASONING (cortex) | ~40%, primitives not composed | CG primitives refuse-gate / KG-2hop / depth-5-compose + CG-verified plumbing; cortex.py integration module PROPOSED not built |
| GENERATION | ~0 (LARGEST GAP) | U0 fork USER-ratified substrate-native (LM INSIDE substrate, no external transformer); N1 concept-LM revival + N2 past-bigram pending |
| WORLD KNOWLEDGE | NEAR-ZERO | "Substrate KNOWS NOTHING"; U1 ingest-real-KB planned; open-relation-vocab designed, not ingested at scale |
| CONTINUAL LEARNING | STRUCTURAL-ONLY | append-only store exists; NO abstraction/consolidation (schema formation) step |
| INSTRUCTION-FOLLOWING / CONTROL | MINIMAL | refuse-gate + fixed primitives; no goal-driven dynamic composition |
| LONG-CONTEXT | SHALLOW | depth-5 compose, 2-hop; no working-memory + episodic-retrieval loop |

## Capability an LLM has that we lack -> brain-grounded mechanism to BUILD it

### 1. FLUENT GENERATION -> resonator-factorization decoder + sequence-unroll + cleanup lexicon
Brain analog: Levelt speech production (conceptualization -> formulation -> articulation); Dell
spreading-activation (lemma -> lexeme); Hickok-Poeppel dual-stream.
Mechanism (substrate-native, NOT borrowed):
- (a) **Resonator network** factorizes a bound proposition HV back into its role-filler components.
  Resonator networks (Frady/Kent/Sommer/Olshausen) are the proven VSA readout: they interleave
  VSA-multiply + pattern-completion to solve the exponential factorization search in superposition.
- (b) **Positional/temporal binding** (theta-phase / positional role vectors) imposes serial order
  on the factored fillers -> an ordered token sequence.
- (c) **Associative cleanup memory** = the "mental lexicon": maps each factor HV through the inverse
  concept-encoder + cleanup to a surface lexeme.
- Interpretable BY CONSTRUCTION: every emitted token traces to one unbind op on a specific bound structure; faithfulness is mechanical, not observed.
- KNOWN RISK: resonator operational capacity is BOUNDED; factorization search grows exponentially
  with factor count. Must map the operating envelope at our N + codebook sizes BEFORE any full build
  (discriminator-survives-scale). The cleanup lexicon under load IS the hub-superposition limit, so
  this probe simultaneously stress-tests memory's known weak spot.

### 2. BROAD WORLD KNOWLEDGE -> CLS fast-bind + slow-consolidate (schema formation)
Brain analog: Complementary Learning Systems (McClelland/McNaughton/O'Reilly): hippocampus =
fast, sparse, pattern-separated episodic binding; cortex = slow, overlapping consolidation that
extracts statistical regularities into generalizable SCHEMAS.
Mechanism: U1 ingest (text -> propositions bound with OPEN relation vocab, hippocampal role-filler,
no closed enum) is the fast-binding half we already have designed. The MISSING half is a
CONSOLIDATION pass that abstracts across episodes into overlapping cortical schemas -- this is what
turns a triple-store into world knowledge that generalizes rather than a pile of stored episodes.

### 3. FLEXIBLE INSTRUCTION-FOLLOWING -> PFC gating + basal-ganglia action selection (PBWM)
Brain analog: Miller-Cohen PFC cognitive control; O'Reilly PBWM (prefrontal-basal-ganglia working
memory gating).
Mechanism: encode an instruction as a goal-HV; a CONTROL layer above the cortex uses it to SELECT +
SEQUENCE the reasoning primitives (a program synthesized from the primitive library) and gate what
enters working memory. Converts today's hand-wired primitive pipelines into goal-driven dynamic
composition. This is the cortex-layer control + stochastic-noise-at-boundary already flagged.

### 4. LONG-CONTEXT REASONING -> small WM register + hippocampal episodic index + attention-gated retrieval
Brain analog: WM capacity is small (~4 items); long context handled by chunking + episodic retrieval,
NOT a giant buffer.
Mechanism: a small working-memory register holds active bound state; a hippocampal episodic index
retrieves relevant stored structure on demand; attention gates retrieval into WM; an iterative
retrieve-compose loop extends effective context. Not a bigger window -- an iterated retrieve-into-WM
loop. The hub-superposition fix (sparse high-fidelity binding / better cleanup for high-degree nodes)
is the capacity enabler here.

## SINGLE most important next capability to build
**Substrate-native generative readout = resonator-factorization decoder** (invert a bound HV structure
back to an ordered surface sequence). Rationale:
- It is the LARGEST missing capability (~0 built) and the DEFINING glass-box-LM capability (U0: a
  language model INSIDE the substrate). Without it the substrate can comprehend/reason but not speak.
- It is the clean INVERSE of the just-built encoder (concept -> HV; decoder = HV -> language) and
  CLOSES THE LOOP: encode -> reason -> generate -> verify-faithfulness end-to-end.
- Dependency: the encoder rescue (R1 objective-fix, in flight) must land first -- the decoder inverts
  that geometry; a degraded encoder yields a degraded decoder. So encoder-close is the gating step,
  and it is already the active PRIMARY (not a new decision).

## Ordered build path
1. [IN FLIGHT] Close encoder rescue (R1 global-objective fix) -> clean concept geometry. Gating dep.
2. [NEXT] **Factorization-envelope probe**: map the resonator operating range at our N + codebook
   sizes (how many role-filler factors reliably recovered from a bound HV; where the capacity cliff
   is). Smoke at full-N. Doubles as the hub-superposition stress test. This is the go/no-go gate.
3. If envelope adequate: build the 3-stage decoder -- (a) resonator factorize, (b) positional-binding
   sequence unroll, (c) cleanup-lexicon lexeme readout. Metric: does the generated string entail
   EXACTLY the source structure (mechanical faithfulness by construction).
4. Feed the decoder real content: U1 ingest (hippocampal fast-bind) + CONSOLIDATION (CLS schema
   formation) -> world knowledge to generate about.
5. Wrap: PBWM control layer (instruction-following) + WM/episodic loop (long-context).

## Honest P
P(generative-readout produces fluent, faithful substrate-native generation at useful scale) ~ 0.40,
gated on (a) encoder rescue landing and (b) factorization envelope adequate at our N. NOT a
nice-story -- resonator decoding is a proven VSA readout mechanism -- but capacity-at-scale and
encoder-cleanliness are real risks. Lit-scan calibration penalty applied; novel-synthesis cap honored.

## Minimal proving move
The factorization-envelope probe (step 2) IS the minimal experiment: it proves or kills the whole
generation path cheaply, on-CPU, at full-N, before any generator is built.

## Sources
- Resonator networks: Frady/Kent/Sommer/Olshausen, "Resonator Networks 1 & 2", Neural Computation 2020.
- Complementary Learning Systems: McClelland/McNaughton/O'Reilly; Schapiro et al. Phil Trans R Soc B 2017.
- PBWM: O'Reilly & Frank; PFC control: Miller & Cohen 2001.
- Speech production: Levelt 1989; Dell 1986; Hickok-Poeppel dual-stream 2007.
