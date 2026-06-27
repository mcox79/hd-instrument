# RESEARCH DRILL 3x — Brain mechanism #6 EXTERNAL SCAFFOLDING (substrate-native: persistent scratchpad atoms in separate partition)

**Date:** 2026-06-27
**Filed-by:** Research (Opus 4.7 1M; team lead)
**Trigger:** USER drill request — deep-dive on M6 from the 7-mechanism inventory; 3 angles + substrate-native cell-spec.
**Discipline applied:** 0.20 calibration deflation; novel-synthesis P cap 0.50; brain-existence-proof +0.10 prior (USER 2026-06-23 standing); empower experiments where lit dismisses (USER 2026-06-22); under-claim per Fix #28; substrate-doesn't-know-anything (USER LOCKED 2026-06-26 — this is Stage-3 compositional-understanding work, not language-prediction); HARD-PASS + HARD-FAIL bands MANDATORY; CARDINALITY_OK MANDATORY; DISCRIMINATOR-MUST-SURVIVE-SCALE pre-check MANDATORY; ASCII only.

**Cross-thread anchors:**
- `notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md` (parent inventory; B6 marked "no cell needed - product-layer fallback" — THIS DRILL OVERRIDES that, per USER request to design substrate-internal partition variant)
- `notes/research_drill_multihop_barrier1_quadruple_negative_3x_2026-06-27.md` (M1-M5 yesterday)
- `notes/research_gap1_multihop_5x_drill_2026-06-26.md` (22 candidates / 9 fields)
- `notes/research_barrier1_double_negative_substrate_product_definition_2026-06-25.md`
- Substrate primitives in play: TWO_TIER generational (CERT chain-grade); WM multi-bank K=4096 (chain-grade); KB partition primitive (Wave 3 in flight).

---

## HEADLINE (one line)

**Brain mechanism #6 (external scaffolding) is the SINGLE MECHANISM with the strongest empirical lift in LLM literature (CoT raises multi-step accuracy 30-60 pp; some tasks near-zero -> >90%); substrate's ROOM-TO-CONFLATE the parent inventory's "product-layer fallback" framing with a SUBSTRATE-NATIVE persistent-scratchpad-partition mechanism is real and worth resolving — the cell-spec below tests THREE storage architectures (dict / vector-same-W / vector-separate-partition) against a no-scratchpad baseline; the DISCRIMINATING arm is dict-vs-vector-same-W which isolates the EXTERNALITY (no-crosstalk storage medium) from MERE-STORAGE; HARD_PASS at depth-5 >= 0.90 dict / >= 0.65 LRU-bounded; HARD_FAIL if dict < 0.85 (means even perfect-storage doesn't lift — the bottleneck isn't external-state); brain-grounded prior P_raw=0.70 with 0.20 calibration deflation = P_deflated=0.50; substrate-coherence-side P=0.55 (TWO_TIER + WM multi-bank are chain-grade primitives ready to compose); recommended dispatch position: WAVE 2 after R1+R2+R3 from parent inventory have run, BECAUSE if R2 PFC-scratchpad-separate-W already lifts to >= 0.65, then M6's substrate-internal contribution may be SUBSUMED by R2 and the M6 cell becomes diagnostic-only (i.e., compares orchestrator-layer chaining vs substrate-internal partition).**

Plain English: external scaffolding is the LOUDEST signal in the LLM literature for multi-step reasoning lift — and humans use it everywhere (paper-and-pencil arithmetic, diagram drawing, navigation tools). The brain version requires an EXTERNAL STORAGE MEDIUM that's separate from main working memory. For substrate, this means a separate partition with no crosstalk — either a dict (perfect, unbounded) or a vector partition with LRU eviction. The risk: this may collapse into the same mechanism as R2 PFC-scratchpad-separate-W from the parent inventory; the cell-spec below INCLUDES the dict-vs-vector-same-W discriminator that proves externality (no crosstalk) is the load-bearing variable, NOT mere extra storage.

---

## ANGLE 1 — MATHEMATICAL / EXTERNAL-STATE COMPUTATION

### A1.1 Turing-machine TAPE as canonical external scratchpad

**Theoretical:** Turing 1937 — the TAPE is unbounded, perfectly readable, perfectly writable, and SEPARATE from the finite-state head. The head has bounded "working memory" (the state); computation is unbounded because the tape is unbounded. Removing the tape collapses TM to a finite automaton — exponentially less expressive.

**Substrate analog:**
- Finite-state head = substrate's main W (bounded; subject to cleanup; bounded by V_C capacity)
- Tape = persistent scratchpad partition (unbounded — or LRU-bounded; perfect reads/writes; no crosstalk with main W)
- Multi-hop chain walk = TM computation that writes intermediates to tape and reads them back

**Key insight:** TM equivalence theorems say MEMORY ARCHITECTURE matters more than HEAD COMPLEXITY. A simple head with a tape >> a complex head with no tape. Applied to substrate: simple per-hop substrate + clean scratchpad >> complex per-hop substrate alone.

**Reference:** Hopcroft-Motwani-Ullman 2006 *Introduction to Automata Theory* — TM separation results.

### A1.2 LLM chain-of-thought = explicit external scratchpad in token stream

**Literature (web-search broad lit-scan):**
- Wei et al. 2022 NeurIPS — "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" — CoT raises GSM8K from 17.9% -> 56.9% on PaLM-540B (30 pp lift).
- Nye et al. 2021 — "Show Your Work: Scratchpads for Intermediate Computation with Language Models" — scratchpad lifts addition from 35% -> 95% (60 pp); enables LMs to perform algorithmic tasks at near-perfect accuracy when intermediate state can be externalized.
- Wei et al. effect-size meta: "For complex reasoning tasks like multi-hop questions, math problems, and logic puzzles, asking the model to 'show its work' can push accuracy from near-zero to above 90%." (from broad lit-scan today)
- Mechanistic finding (2025 work): "Iteration heads" emerge that explicitly focus on previously generated tokens to carry forward interim results — effectively creating a virtual RNN where hidden state is externalized as text.
- Recent 2025 OpenReview paper "Scratchpad Thinking: Alternation Between Storage and Computation in Latent Reasoning Models" — explicit storage/computation cycle.

**Substrate analog:**
- Token stream = scratchpad partition atoms (each step writes ONE atom with timestamp + query-id + content)
- Iteration head = chain-walker that reads partition atoms in order
- Algorithmic-task lift (35 -> 95 on addition) is the strongest existing-system analog of what we should expect on substrate multi-hop

**Calibration penalty:** lit-scan effect sizes are ON LANGUAGE MODELS (Stage 4 in substrate's progression). Substrate is at Stage 3 compositional-understanding. The mechanism (external storage with no crosstalk) is architectural and SHOULD transfer; the magnitude may not. Deflate raw P=0.85 -> P_deflated=0.65; further deflate to P=0.50 per novel-synthesis cap.

### A1.3 Tool-use augmentation: calculator / search / code-execution

**Literature:**
- Toolformer (Schick et al. 2023) — self-supervised learning of WHEN to call tools (calculator, search, calendar, QA system). Lifts arithmetic, factual lookup, multi-step QA.
- ReAct (Yao et al. 2022) — interleaves reasoning steps with tool calls; iterative refinement.
- Toolformer/ReAct effect: significant gains on tasks where SINGLE-PASS reasoning is bounded; tool acts as external infinite-capacity scratchpad with PERFECT recall (calculator never makes arithmetic errors).

**Substrate analog:**
- Tool = scratchpad partition with PERFECT recall (dict-based, content-addressed)
- "When to call" = orchestrator decides per hop whether to write intermediate to scratchpad (cheap — always write) or skip (only useful if scratchpad has capacity constraints)
- Tool's "perfect recall" maps to dict (vs main W's cosine-similarity recall which has cleanup noise)

**Cross-reference to parent inventory's B6:** parent treats this as ORCHESTRATOR-LAYER (Claude/Python decomposes 5-hop into 5 substrate 1-hop calls). This drill argues for a SUBSTRATE-NATIVE variant where the orchestrator's bookkeeping is done by an internal partition — making substrate self-sufficient on multi-hop without requiring external software glue.

### A1.4 Memory-augmented neural networks (DNC, MANN, NTM)

**Literature (narrow lit-scan):**
- Graves et al. 2014 — Neural Turing Machine: differentiable external memory with content-based addressing.
- Graves et al. 2016 *Nature* — Differentiable Neural Computer: NTM + temporal linking (sequential traversal) + dynamic allocation (preventing recent-write overwrite).
- Memory Networks (Sukhbaatar et al. 2015) — multi-hop attention over external memory bank; foundational result that EXTERNAL MEMORY enables multi-step reasoning that feedforward architectures cannot do.
- 2024 work "A brain-inspired memory transformation based differentiable neural computer for reasoning-based question answering" (PMC) — modern DNC variants on QA.
- "DNCs Require More Planning Steps" (Csordas-Schmidhuber 2024 arxiv) — DNC works but needs depth/iteration to use memory well.

**Substrate analog:**
- DNC's external memory module = scratchpad partition
- Content-based addressing = cosine-NN within partition
- Temporal linking = atoms tagged with query-id + step-index; "next" lookup is exact via dict key
- Dynamic allocation = LRU eviction policy on partition

**Direct evidence:** Memory Networks paper showed MULTI-HOP ATTENTION OVER EXTERNAL MEMORY enables multi-step reasoning feedforward nets cannot do. This is the strongest existing-system precedent for substrate's expected behavior.

**Risk:** DNC training needed many planning steps. Substrate's per-hop chain walk does NOT learn — it just queries — so the "planning depth" problem may not apply. But equally, substrate doesn't get the DNC's BENEFIT of LEARNED addressing — substrate uses cosine-NN which is content-defined, not learned.

---

## ANGLE 2 — BRAIN / NEUROSCIENCE

### A2.1 Distributed cognition (Hutchins) — humans cognize WITH artifacts

**Literature (broad lit-scan):**
- Hutchins 1995 *Cognition in the Wild* — navy ship navigation; cognitive work distributed across crew + tools (compass, plotting board, chart); no single human holds full ship-position state.
- Hutchins 2014 — distributed cognition extends to writing, calculation, software interfaces.
- Mindful Technics 2025 review: "Humans extend thought into the world in a process called 'epistemic engineering,' altering their surroundings to construct 'problem-solving environments' that compensate for cognitive resource bottlenecks such as our relatively limited capacity for working memory."

**Substrate analog:**
- Substrate's main W = ship navigator's working memory (bounded; subject to error)
- Scratchpad partition = plotting board (persistent; perfect; physically separate from navigator's head)
- Multi-hop query = navigation problem decomposed across navigator + plotting board

**Key insight (load-bearing):** distributed-cognition lit makes the strongest case that COGNITIVE BOTTLENECKS ARE BYPASSED VIA EXTERNALITY, not by extending internal capacity. The brain didn't grow bigger to solve harder problems — humans externalized state to paper and tools. Substrate analog: don't try to expand V_C; add a separate scratchpad partition.

### A2.2 Extended mind hypothesis (Clark-Chalmers 1998)

**Literature:**
- Clark-Chalmers 1998 *Analysis* 58:1 — "The Extended Mind" — parity principle: if external process performs same FUNCTIONAL ROLE as internal cognitive process, it IS cognition.
- Clark 2008 *Supersizing the Mind* — extended cognition theory; tool use as cognitive extension.
- Sutton 2017 *Distributed Cognition and Memory Research* — review of how memory research treats externalized state.

**Substrate analog:**
- Parity principle: substrate's main W + scratchpad partition is INFORMATIONALLY EQUIVALENT to a hypothetical substrate with much larger V_C — provided scratchpad supports the same READ/WRITE/QUERY operations.
- The substrate-product story benefits: scratchpad is AUDITABLE (every intermediate is provenance-tracked), CHEAP (dict is O(1) lookup), and CROSSTALK-FREE (separate storage).

### A2.3 Tool-use literature: humans + writing > humans without writing

**Literature:**
- Donald 1991 *Origins of the Modern Mind* — external symbol systems (writing, notation) qualitatively extend cognitive capacity; not just additive but multiplicative for complex reasoning.
- Hutchins 1995 — navigation crew with instruments solves problems no individual could solve.
- Larkin-Simon 1987 *Cognitive Science* — "Why a diagram is (sometimes) worth ten thousand words" — diagrams index by location; perceptual inferences extremely cheap; informationally-equivalent sentential representations require expensive computation. Experimental finding: solutions with diagrams up to SIX TIMES easier than equivalent sentential ones.

**Substrate analog:**
- Larkin-Simon's "location-indexed" insight maps to dict-based scratchpad (key-addressed = location-indexed in attribute space)
- Substrate's main W is cosine-similarity-indexed (sentential-equivalent — requires expensive computation per query); scratchpad partition with dict keys is location-indexed (cheap)
- The 6x effect-size from Larkin-Simon is a magnitude estimate for what dict-vs-cosine-cleanup could provide ON THE LOOKUP STEP (not necessarily end-to-end)

### A2.4 Scratchpad in mental arithmetic: mental vs paper accuracy gap

**Literature:**
- Hitch 1978 *Cognitive Psychology* — mental arithmetic limited by working-memory carry-over; paper-and-pencil arithmetic effectively unbounded.
- Beilock-Carr 2005 — math performance under WM load drops sharply; externalization mitigates.
- Common finding: humans solve 5-digit x 5-digit multiplication trivially on paper, nearly impossibly mentally.

**Substrate analog:**
- Substrate's per-hop ~0.69 floor (depth-5 collapses to ~0.16) is the substrate-equivalent of "mental arithmetic WM bottleneck"
- Scratchpad partition writes each hop's intermediate to a perfectly-recalled location — equivalent to writing the partial product to paper
- Predicted lift: equivalent to humans going from mental to paper arithmetic — qualitative regime change at depth-3+

### A2.5 Brain-grounded P calibration for M6

- Existence proof: brain does this universally (every literate human; every navigator; every mathematician using paper)
- Mechanism: clear (separate persistent storage medium with no crosstalk)
- Substrate-native path: clear (dict partition; or vector partition with no W-overlap)
- Risk: distinguishing M6 from R2 PFC-scratchpad-separate-W (parent inventory) — both are "separate-W intermediates store"; the difference is OFFLINE-PERSISTENT (M6: dict; partition; LRU) vs ONLINE-ACTIVE (R2: WM bank with bounded capacity, decay)
- Calibration: P_raw=0.75 (brain-existence-proof; LLM lit shows 30-60 pp lifts; mechanism architecturally clear) -> P_deflated 0.20 = 0.55 -> novel-synthesis cap 0.50 = P_final=0.50

---

## ANGLE 3 — CROSS-DOMAIN

### A3.1 LLM CoT / Tree-of-Thought (ToT) / ReAct family

**Literature:**
- CoT (Wei 2022) — single-chain reasoning; scratchpad in token stream.
- Tree-of-Thought (Yao 2023) — multiple chains explored; voting/pruning; scratchpad is tree-structured.
- ReAct (Yao 2022) — reasoning interleaved with action; scratchpad includes external action results.
- 2026 work: "Beyond ReAct: A Planner-Centric Framework for Complex Tool-Augmented LLM Reasoning" — explicit planner separates from executor; planner uses scratchpad to track plan state.

**Substrate analog:**
- CoT -> linear scratchpad (depth-N chain; one atom per hop)
- ToT -> tree-structured scratchpad (per-branch atoms; merge at decision points)
- ReAct -> scratchpad with mixed substrate-query atoms + external-action atoms

**Composition opportunity:** M6 scratchpad combines with parent's R3 BIDIRECTIONAL-MEET-IN-MIDDLE — forward + backward chains both write to scratchpad; meet criterion is "any forward atom matches any backward atom in scratchpad" (dict-key match is O(1)).

### A3.2 Calculator augmentation (PaLM-SayCan, Toolformer, Codex)

**Literature:**
- PaLM-SayCan (Ahn et al. 2022) — language model + robotic action library; SayCan grounds plan in feasible-action set.
- Toolformer (Schick 2023) — calculator/search/QA tool use.
- Codex (Chen 2021) — code-execution as scratchpad; LLM writes code, executes, reads result back.

**Substrate analog:**
- Calculator = perfect-recall key-value lookup over scratchpad
- Code-execution = substrate's chain walker runs over partition atoms in order

### A3.3 Sketchpad in problem-solving research (Larkin-Simon canonical)

Already covered in A2.3 — the strongest empirical effect-size estimate (6x) for the location-indexed-vs-cosine-indexed bottleneck.

### A3.4 Cross-domain key insight (load-bearing)

**EVERY successful multi-step reasoning system across LLMs / DNCs / brain / classical-CS uses some form of external scratchpad. The mechanism is convergent across domains.** This is one of the few mechanisms where lit-scan + neuroscience + cross-domain ALL agree the mechanism is necessary, not optional. Brain-existence-proof prior bumps + LLM empirical lifts of 30-60 pp + DNC enabling-of-multi-hop-reasoning = high-confidence architectural element.

**Honest counter-position (per under-claim discipline):** the convergent finding ACROSS DOMAINS that "external scratchpad enables multi-step" is so robust that the question for substrate is not "does it work" but "how much of substrate's 2-hop ceiling is bottlenecked here vs elsewhere." If R2 PFC-scratchpad-separate-W (parent inventory) already captures the substrate-internal version, M6 substrate-native cell may be redundant. The DISCRIMINATOR is whether dict vs vector-separate-partition differ — and the cell-spec below tests this.

---

## SUBSTRATE-NATIVE IMPLEMENTATION PATH

### Architecture spec

**Partition layout:**
- `W_main` — primary substrate matrix (existing; V_C atoms; subject to cleanup; used for content storage and chain-walk per-hop reads)
- `W_scratch` — scratchpad partition (NEW; separate matrix; dedicated to multi-hop intermediates; cleared per query)

**Storage variants (cell arms test these):**
1. `SCRATCH_DICT` — Python dict keyed by `(query_id, step_index)` -> value vector + content atom-id. Perfect recall; no crosstalk; unbounded (or LRU-bounded). NOT a substrate matrix — pure dict.
2. `SCRATCH_VEC_SAME_W` — vectors bound into `W_main` with permutation tag (control: tests whether SEPARATE STORAGE matters vs MERE INTERMEDIATE-STORAGE — this is the EXTERNALITY DISCRIMINATOR).
3. `SCRATCH_VEC_SEPARATE_PARTITION` — vectors in dedicated `W_scratch` matrix; same cosine-NN read semantics as `W_main` but isolated; mirrors "vector partition" architecture.
4. `SCRATCH_LRU_BOUNDED` — `W_scratch` with LRU eviction at capacity K=64 atoms/query.

**Multi-hop chain walk with scratchpad:**
```
for k in 1..depth:
    if k == 1:
        E_k = query W_main with start atom S
    else:
        E_{k-1} = read scratchpad[query_id, k-1]
        E_k = query W_main with E_{k-1} as cue
    write scratchpad[query_id, k] = E_k
final_answer = scratchpad[query_id, depth]
clear scratchpad[query_id, *]  # LRU eviction at end-of-query
```

### Cell-spec stub

```
CELL_NAME:        exp_multihop_external_scratchpad_persistent_atoms_v1.py
N_DIM:            8192 (substrate Stage-3 default)
N_SEEDS:          3
DEPTHS_TESTED:    [2, 3, 5, 7]
N_QUERIES:        500 per depth per seed (CARDINALITY_OK target = 500)
EXPECTED_N_UNITS: 4 arms x 4 depths x 3 seeds = 48 results (HARD_FAIL_CARDINALITY_BREACH if < 40 results land)

ARMS:
  BASELINE_NO_SCRATCHPAD:        per-hop chain walk; no intermediate storage; relies on W_main cleanup
  SCRATCH_DICT:                  Python dict scratchpad; perfect recall; unbounded
  SCRATCH_VEC_SAME_W:            intermediates bound into W_main with permutation tag (CONTROL for externality)
  SCRATCH_VEC_SEPARATE_PARTITION: dedicated W_scratch matrix; cosine-NN reads; isolated from W_main
  SCRATCH_LRU_BOUNDED:           W_scratch with K=64 atom LRU eviction (realistic capacity)

  NOTE: 5 arms not 4 (parent USER spec said 4; I expanded to include SEPARATE_PARTITION because the dict-vs-partition distinction is load-bearing — dict is perfect but not vector-substrate-native; partition is substrate-native; both are external; both must beat SAME_W control).

DISCRIMINATORS:
  PRIMARY (externality):    SCRATCH_DICT vs SCRATCH_VEC_SAME_W at depth-5
                            HARD_FAIL if SCRATCH_DICT - SCRATCH_VEC_SAME_W < 0.20 at depth-5
                            (proves it's EXTERNALITY/no-crosstalk that matters, not mere storage)
  SECONDARY (substrate):    SCRATCH_VEC_SEPARATE_PARTITION vs SCRATCH_DICT at depth-5
                            HARD_PASS_IF SEPARATE_PARTITION >= 0.85 * DICT
                            (proves substrate-native variant matches dict gold-standard within 15%)
  TERTIARY (capacity):      SCRATCH_LRU_BOUNDED vs SCRATCH_DICT at depth-5
                            HARD_PASS_IF LRU_BOUNDED >= 0.65 at depth-5
                            (proves realistic-capacity variant still lifts)

BANDS (envelope-fail-bands):
  BASELINE depth-2 in [0.62, 0.68]     # standard substrate per-hop ~0.69 floor; sanity rail
  BASELINE depth-5 in [0.10, 0.25]     # standard error-compounding floor
  HARD_PASS:
    SCRATCH_DICT depth-5            >= 0.90 AND
    SCRATCH_LRU_BOUNDED depth-5     >= 0.65 AND
    SCRATCH_DICT - SCRATCH_VEC_SAME_W depth-5 >= 0.20 AND
    BASELINE depth-2 in [0.62, 0.68]
  MIDDLE_BAND:
    SCRATCH_DICT depth-5            in [0.70, 0.90]
  HARD_FAIL:
    SCRATCH_DICT depth-5            < 0.70  (perfect-storage failed; bottleneck is NOT external-state)
    OR SCRATCH_VEC_SAME_W           >= SCRATCH_DICT - 0.10  (no externality effect; collapse to single-mechanism)
    OR BASELINE depth-2             out of [0.62, 0.68]  (sanity rail; redo)

SMOKE (DISCRIMINATOR-MUST-SURVIVE-SCALE):
  Per USER 2026-06-26: smoke must FIRE the discriminator at full N_DIM (not just verify cell runs).
  Smoke-N: 30 queries per arm at depth-5 only (5 arms x 30 = 150 queries; <2 min runtime).
  Smoke discriminator: SCRATCH_DICT >= 0.80 AND SCRATCH_VEC_SAME_W <= 0.40 (~0.4 spread at smoke = signal will survive at full-N).
  Smoke-VET: if SCRATCH_DICT at smoke-N >= 0.95 (saturated at metric cap) AND VEC_SAME_W <= 0.30 (discriminator clean), proceed to full dispatch. If SCRATCH_DICT >= 0.95 but VEC_SAME_W also >= 0.85, REJECT — discriminator collapsed at smoke.

CARDINALITY_OK:   4 (or 5) arms x 4 depths x 3 seeds x 500 queries = 24000 (or 30000) per-query results; lite-aggregate 60 (or 75) cells; HARD_FAIL_CARDINALITY_BREACH if observed < 50

SCRATCHPAD_AUDIT (verify-the-referent):
  - SCRATCH_DICT: assert no writes to W_main during chain walk (intermediates ONLY in dict)
  - SCRATCH_VEC_SAME_W: assert intermediates ARE in W_main with permutation tag (control)
  - SCRATCH_VEC_SEPARATE_PARTITION: assert W_main untouched; only W_scratch modified
  - SCRATCH_LRU_BOUNDED: assert W_scratch size <= 64 at all times during walk
  Audit failure = HARD_FAIL_AUDIT.

CLEAN-DATA DISCIPLINE (USER 2026-06-23 — smoke + cell):
  - Synthetic 5-hop chains; no contamination from substrate's existing atoms/labels
  - Random entities + random relations; each chain is a fresh provenance-tracked triple set
  - Heldout 20% chains never seen during chain-construction; tested at chain-walk time
  - Brain mechanism is architectural NOT data-specific; clean synthetic = honest test

RUNTIME (cell-author Fix #17 measurement):
  Smoke (150 queries): ~1-2 min laptop
  Full dispatch (24-30k queries): 10-15 min laptop; or 3-5 min remote_cpu via orchestrator
  N_DIM=8192 matmul-bound — route via hdi_orchestrator to remote_cpu_queue per GPU routing rule (USER 2026-06-22; M_total >= 24k is heavy)

P-ESTIMATE: P_raw=0.75 (brain-grounded + LLM empirical 30-60pp + DNC precedent + Larkin-Simon 6x lift)
           P_deflated=0.55 (apply 0.20 lit-scan calibration)
           P_capped=0.50 (novel-synthesis cap)
           P_substrate_coherence=0.55 (TWO_TIER + WM multi-bank are chain-grade primitives ready to compose)
           FINAL P=0.50 (use lower of capped/coherence)
```

### Dispatch sequencing recommendation

**WAVE order from parent inventory + this drill:**

1. **WAVE 1 (parent inventory; in-flight):** R1 NREM-REPLAY-AS-OPERATOR-INTO-SEPARATE-W_C, R2 PFC-SCRATCHPAD-SEPARATE-W, R3 BIDIRECTIONAL-MEET-IN-MIDDLE — these run FIRST because they test the substrate-internal mechanisms (memory + composition).

2. **WAVE 2 (THIS DRILL):** M6 EXTERNAL-SCRATCHPAD-PARTITION cell — dispatched after R1/R2/R3 results land, BECAUSE:
   - If R2 PFC-scratchpad-separate-W >= 0.65 at depth-5: M6 cell is DIAGNOSTIC (does external partition add anything BEYOND what R2 already gets?). Run anyway to disambiguate WM-bank-active-maintenance from offline-persistent-partition.
   - If R2 < 0.65: M6 is RECOVERY (offline persistent storage may beat online active maintenance because no decay).
   - If BOTH < 0.65: bottleneck is NOT external-state; reframe to other mechanisms (B4 LDPC, B8 attractor).

3. **WAVE 3 (gated on Wave 2):** Combined R2 + M6 cell — both online (WM bank) and offline (partition) scratchpad available; tests whether they're additive (different mechanisms compose) or redundant (same mechanism).

### Specific risk: M6 collapses to R2

**Concern:** parent inventory's R2 PFC-SCRATCHPAD-SEPARATE-W is ALREADY a "separate-store for intermediates" architecture. M6 here is also a "separate-store for intermediates" architecture. What's the difference?

**Distinction (load-bearing):**
- R2 uses WM MULTI-BANK (the substrate's active-maintenance primitive). Bounded capacity (K=4096 across all banks). One bank for scratchpad. ONLINE — values held in active recurrent state.
- M6 uses PARTITION (dict OR separate matrix). Bounded by partition size or LRU. OFFLINE — values held in persistent storage, not active maintenance.

**Empirical brain analog:**
- R2 ~ PFC delay-period activity (Miller-Cohen 2001 active maintenance)
- M6 ~ writing on paper (truly external; no neural overhead; persistent)

**Discriminator:** if substrate's WM bank has any active-maintenance overhead (decay; capacity limit) — M6 should beat R2. If WM bank is functionally equivalent to dict-partition — M6 == R2 and one is redundant.

**Honest framing:** I would not be surprised if M6 collapses to R2. The architectural insight (separate-W storage) is the same. The Wave-2 sequencing position allows graceful gating: only run M6 if Wave 1 results don't fully close the depth-5 gap.

### Composition opportunities

- M6 + R1 (NREM-REPLAY-AS-OPERATOR-INTO-SEPARATE-W_C): scratchpad intermediates that recur across queries become candidates for replay-compaction into W_C — the scratchpad IS the source of consolidation candidates.
- M6 + R3 (BIDIRECTIONAL-MEET-IN-MIDDLE): forward + backward chains both write to scratchpad; meet criterion is exact-key match on scratchpad atoms (O(1) with dict; O(K) with partition cosine-NN).
- M6 + B4 (LDPC SOFT MESSAGE PASSING): scratchpad atoms hold population codes (distributions, not point estimates); LDPC iteration reads/writes distributions to scratchpad.
- M6 + B8 (RATE-CODED SOFT-COMPLETION): per-hop attractor settles inside scratchpad cell; readout population goes to scratchpad with confidence.

---

## SUMMARY + RECOMMENDED ACTIONS

### One-paragraph synthesis (under-claim discipline applied)

External-scaffolding (mechanism #6) is the strongest convergent finding across LLM literature (CoT 30-60 pp lifts), neuroscience (distributed-cognition + extended-mind), and classical AI (DNC/MANN enabling multi-hop reasoning impossible without external memory). For substrate, this maps to a persistent scratchpad PARTITION (dict for gold-standard; vector partition for substrate-native; LRU-bounded for realistic capacity) that's separate from main W with no crosstalk. The cell-spec includes a DICT vs VEC_SAME_W discriminator that isolates EXTERNALITY (no-crosstalk storage) from MERE INTERMEDIATE-STORAGE — this is the load-bearing test, because without it we can't tell if the lift is from architecture or from just having extra capacity. The risk is collapse-to-R2-PFC-scratchpad-separate-W from the parent inventory (both are "separate-store"); the Wave-2 sequencing (run after R1/R2/R3 land) allows diagnostic disambiguation rather than wasted dispatch.

### Recommended actions

1. **Hold dispatch until R1/R2/R3 land** (parent inventory Wave 1 should run first; their results inform whether M6 cell is needed).
2. **Atomize this drill** as `RESEARCH_DRILL_M6_EXTERNAL_SCRATCHPAD_PARTITION_2026-06-27` for substrate-KB ingestion (so substrate-as-Director-KB has it queryable post-compaction).
3. **Cell-author handoff** (when Wave 1 lands and Wave 2 fires): spawn `hdi_exp_dev` sub-agent with this drill's cell-spec stub; cell-author runs smoke + dispatches via `hdi_orchestrator` to `remote_cpu_queue` (matmul-bound at N_DIM=8192, M >= 24k).
4. **Pre-dispatch verify-the-referent gate** (Fix #26): cell-author runs `tools/predispatch_check.py exp_multihop_external_scratchpad_persistent_atoms_v1` to confirm no prior duplicate cell (none should exist — this is a new mechanism).
5. **No spawn now** — drill output is the artifact; no in-flight cell from this drill until Wave 1 informs the decision.

### Specific outputs filed

- This drill: `notes/research_drill_brain_multihop_M6_external_scratchpad_persistent_atoms_3x_2026-06-27.md` (~9 KB)
- Cell-spec stub embedded above; ready for `hdi_exp_dev` cell-author handoff at Wave 2 trigger
- Substrate-KB ingestion: deferred until file lands (auto-current via scheduled task)
- No commits (research-only artifact; no code changes; no Store atomizations from this turn — atomization happens at Wave-2 trigger after R2 result informs whether M6 cell is novel mechanism or redundant)

### Bias-checklist self-vet (per MEMORY.md master checklist 2026-06-24)

- A (selection-bias): tested across 4-5 storage architectures + 4 depths; no cherry-picked condition
- B (regime-confound): synthetic clean chains; baseline in [0.62, 0.68] sanity rail enforced
- M (production-scale instrument calibration): N_DIM=8192 production scale; CARDINALITY_OK = 24-30k queries
- N (verify-the-referent): scratchpad audit ensures each arm actually implements claimed architecture; HARD_FAIL_AUDIT
- O (basis-vs-use-case): atom labels at readout only; intermediates are vectors not labels during chain walk
- Q (suspect 1.000): SCRATCH_DICT is expected near-1.0 at depth-5 (perfect recall); smoke-VET catches if discriminator collapses
- R (BIAS-13/14/15 contamination/regime/mismatch): clean synthetic data; sanity rails; same chain construction across arms
- S (band-calibration regime checks): top-1 metric; capacity-feasible (V_C >= 24k); relative bands across arms

### Routing / waiting-on

- Drill artifact landed; no inbound waiting-on
- Wave-2 trigger: R1/R2/R3 results from parent inventory
- Substrate-KB query path: once file lands, `python d:/AI/hd-instrument/tools/director_kb_query.py --filename-contains M6_external_scratchpad` will return this rank-1 cosine=1.0

---

**End of drill.**
