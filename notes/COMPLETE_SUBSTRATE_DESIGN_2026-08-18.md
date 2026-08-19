# THE COMPLETE SUBSTRATE — the whole organ set, the best filler for each slot, and the empties

**OWNER INSTRUCTION, VERBATIM, AND IT IS THE WHOLE BRIEF (2026-08-18):**

> *"we need to have a current best substrate is my assumption. you talk about parts wired into it - we
> should envision a complete substrate (or close to) and wire in the best versions of each."*

This corrects the Director, who had proposed wiring six good organs into a pipeline nobody had
characterised. **The complete organ set comes first; then each slot gets its best available filler;
then the slots with nothing in them get named, because an empty slot nobody has written down is the
most expensive kind.**

---

## 0. WHAT THIS DOC IS, AND WHAT IT DELIBERATELY DOES NOT REDO

**`notes/ORGAN_MAP.md` ALREADY EXISTS AND IS A 38-ORGAN BRAIN-FIDELITY MAP.** It gives, per organ,
the brain's equation (or `UNPINNED`), our code at HEAD, a fidelity grade, runtime wiring, and the
floored evidence. **This doc does NOT fork that taxonomy and does not re-derive it.** It adopts
ORGAN_MAP's IDs (`A1`…`H3`, `S1`) exactly, so the two documents can never drift into two
architectures.

What this doc adds, and it is all the owner asked for:

1. **THE SLOTS ORGAN_MAP STRUCTURALLY COULD NOT SEE.** ORGAN_MAP audits *what we built* against the
   brain. Derived instead from **the JOB** — text in, an answer out — **eleven slots appear that it
   never had a row for**, and the biggest hole in the substrate is among them.
2. **THE BEST FILLER PER SLOT**, adjudicated where two organs compete.
3. **THE EMPTIES, NAMED.**
4. **THE WIRING ORDER, ITS IMPORT-COST TAX, AND WHAT THE ASSEMBLED THING WOULD ACTUALLY DO.**

**Populations must not be mixed.** The CLAIMS layer is 30 vetted / 1 upheld; a `HARD_PASS` there is
an unverified claim. **The ORGAN layer is a different population in demonstrably better shape** —
163/163 import, 83/87 self-tests pass, 0 of the 13 largest unreached organs are constant-valued. Do
not import either base rate into the other.

**Evidence used here, all re-checked on disk today:** `scratch/organ_audit/{closure,import_results,
selftest_results,good_but_unused}.json`; a fresh AST survey of all 147 top-level modules written to
`scratch/organ_audit/slot_survey.json` by `scratch/organ_audit/slot_survey.py`;
`tools/experiment_index.py` (8,836 cells, prints rows scanned first); `tools/vetting_ledger.py
--cite`; `data/capability_registry.jsonl` (202 rows); and direct reads of the module sources named.
**`tools/substrate_query.sh` was not used — it returns zero bytes and exits 0.**

---

## 1. THE FRAME: THIS IS NOT ONE NETWORK, IT IS THREE — AND WE HAVE BUILT ONE AND A HALF

*Drill, 2026-08-18, generic-terminology search only.*

The human brain does **not** run comprehension, reasoning and speaking through one system. Three
systems are **dissociated by direct evidence**, and the dissociation is unusually clean — pairwise
correlations *within* the language network and *within* the multiple-demand network are high, while
correlations *across* the two are **close to zero**, and there is a **causal double dissociation**
(MD integrity ↔ degraded-speech perception; language-network integrity ↔ word-meaning priming).

| network | what it does | pinned? |
|---|---|---|
| **LANGUAGE network** (left fronto-temporal: pIFG, pMTG/pSTG, ATL) | builds meaning from words | **PINNED as a dissociable system** |
| **MULTIPLE-DEMAND network** (frontoparietal, domain-general) | reasoning, control, "work out the answer" | **PINNED as a dissociable system; its computation UNPINNED** |
| **PRODUCTION network** (left-lateralised: pIFG, mid/posterior MTG-STG, left thalamus) | turns an intention into words | **stages PINNED** (lemma selection ~150-350 ms, then form encoding ~217-530 ms, serially) |

**MEASURED CONSEQUENCE FOR US, AND IT REFRAMES A NEGATIVE WE ALREADY HAVE.** We have built a partial
LANGUAGE network and a partial EPISODIC system. **We have essentially no multiple-demand network and
no production network at all.** That is exactly what the `reasoner` probe found without knowing to
look for it: `DerivationReasoner.reason` produces **an answer identical to a plain similarity
baseline on 38 of 40 questions**, and derivation reaches only 7 of 40. *That is not a broken
reasoner. That is a language-network similarity read with no domain-general system behind it.*

**Do not read this as licence to build a "reasoning module" from whatever is convenient.** The MD
network's *existence* is pinned; **its computation is UNPINNED**, so anything we put in that slot is
our invention under test and must be labelled so.

Sources: [Blank & Fedorenko, robust dissociation](https://www.sciencedirect.com/science/article/abs/pii/S0028393218304536) ·
[MD network does not support core comprehension](https://www.biorxiv.org/content/10.1101/744094v1.full) ·
[causal contributions of MD vs language networks](https://pmc.ncbi.nlm.nih.gov/articles/PMC9893226/) ·
[spatial/temporal signatures of word-production components](https://pure.mpg.de/rest/items/item_59611_3/component/file_59612/content) ·
[Levelt, lexical access in speech production](https://www.pnas.org/doi/10.1073/pnas.231459498)

---

## 2. PART 1 — THE COMPLETE ORGAN SET

Derived from the job, not the inventory. `PINNED` = the brain correspondence is fixed by published
evidence. `INVENTION` = we chose it and it is under test. `PINNED-SYSTEM/UNPINNED-EQUATION` = the
structure is real, the maths we put in it is ours.

### 2.1 THE 38 SLOTS ORGAN_MAP ALREADY DEFINES — status only, no re-derivation

Read ORGAN_MAP for each. Summarised here so the complete set is visible in one place, with **three
corrections this pass makes to it**:

| ID | the job | brain structure | pinned? |
|---|---|---|---|
| A1 | letters → a word-form code | VWFA (left occipitotemporal) | PINNED structure, UNPINNED update rule |
| B1 | what is this concept LIKE | ATL amodal hub | PINNED structure, **UNPINNED equation** |
| B2 | one encounter → a vector | cortical pooling + divisive normalisation | **PINNED** (Carandini-Heeger; pool-SHARED denominator) |
| B3 | many encounters → a concept | replay-driven cortical consolidation | PINNED shape, UNPINNED weight function |
| B4 | representation format / capacity | IT / ATL population code | **PINNED** (dense, graded, low effective dim) |
| B5 | sensorimotor grounding spokes | modality-specific cortex | PINNED spokes, **UNPINNED combination rule** |
| C1 | score two representations | recurrent settling trajectory | **UNPINNED** ("there is no cosine in the brain") |
| C2 | pick the winner | graded competition in the normalisation pool | PINNED |
| C3 | task/context reshapes the comparison | IFG → spoke multiplicative gain | PINNED form, **UNPINNED gain function** |
| C4 | settle / stabilise | attractor settling | PINNED — **and DECLINED on purpose; do NOT build** |
| D1 | make similar episodes distinct | dentate gyrus | **PINNED** (~0.2% MTL sparsity) |
| D2 | complete a pattern from a partial cue | CA3 recurrent collaterals | PINNED structure, **UNPINNED update rule** |
| D3 | one-shot episodic write / index | hippocampal index | **PINNED** (index, not content) |
| D4 | consolidation / replay schedule | SWR replay, CLS | PINNED partly; **selection function UNPINNED** |
| D5 | hold items actively | PFC persistent activity / synaptic WM | **CONTESTED which dominates** |
| D6 | order / sequence | CA3 asymmetric weights, phase precession | PINNED op-class |
| D7 | predictive relational map | grid/place cells as SR | **FULLY PINNED — `M = (I − γP)⁻¹`** |
| D8 | memory lifetime | cascade / complex synapse | **FULLY PINNED — and PARKED-BY-SCALE** |
| D9 | which write gets consolidated | synaptic tag & capture | PINNED (`tag × PRP > θ`) |
| **E1** | **bind role to filler** | **NO RECORDING SHOWS IT** | **🚨 UNPINNED — OUR INVENTION UNDER TEST** |
| E2 | situation-model register | event indexing + PE segmentation | PINNED segmentation trigger, UNPINNED update |
| E3 | who is "he" | cue-based parallel retrieval | PINNED *ordering*, **UNPINNED arithmetic** |
| E4 | bridge what is not stated | discourse inference | UNPINNED |
| E5 | ordered multi-item buffer | theta-gamma slots | PINNED counts, **UNPINNED encoding op** |
| F1 | word class | posterior temporal lexical access | UNPINNED |
| F2 | who did what to whom, structurally | LIFG / pSTS | UNPINNED |
| F3 | assign thematic roles | Competition Model | **PINNED** (cue validity vs cue cost) |
| F4 | learn a verb's frame | syntactic bootstrapping | UNPINNED; graded-not-veto PINNED |
| F5 | notice comprehension has failed | N400 generator | PINNED reference point (‖Δ situation model‖) |
| F6 | settle a multi-sentence reading | Construction-Integration | equation flagged unverified |
| G1 | the cortical learning rule | cortex | **bifurcates; lexical-semantic half UNPINNED** |
| G2 | surprise gates plasticity | predictive coding | **PINNED** (residual is the signal) |
| G3 | neuromodulatory gain | ACh / NE | PINNED form, UNPINNED setpoint |
| G4 | select an action | basal ganglia Go/NoGo | **PINNED** |
| H1 | do I already know this | perirhinal familiarity | PINNED shape, UNPINNED criterion |
| H2 | what should I read next | ACC patch-leaving / MVT | **PINNED** (Charnov 1976) |
| H3 | accept / clarify / refuse | metacognitive criterion (SDT) | PINNED form, UNPINNED criterion |
| S1 | the long-term semantic store | distributed cortical semantic memory | **UNPINNED — an engineering organ** |

**🚨 E1 IS THE ONE TO SAY OUT LOUD.** *No recording shows neurons computing an algebraic binding over
two full-rank vector codes.* Three live accounts compete (algebraic; coarse-coded conjunctive;
synchrony), all with published objections. **So our core operation is OUR INVENTION UNDER TEST, not
biology.** Any brief, prereg or registry row calling it brain-derived is mislabelled. This is not
"abandon it" — it is a labelling rule.

**THREE CORRECTIONS TO ORGAN_MAP, ALL MADE FROM DISK THIS PASS:**

1. **H2 is no longer MISSING.** ORGAN_MAP §1 still counts 7 missing organs including information
   foraging; `hdlab/information_foraging.py` was built 2026-08-14 (registry:
   `landed_2026-08-14_c97ecbef2_organ_map_MISSING_organ_now_built`), self-test passes, and the probe
   found it FUNCTIONAL. **The tally line "MISSING entirely 7/38" is stale; it is 6.**
2. **The live-closure count of 31 UNDERCOUNTS by exactly 3.** `scratch/organ_audit/closure.json`
   lists `pos_tagger`, `arc_parser` and `arc_labeler` under `unused`. They are imported **inside a
   function body** — `hdlab/reading_grounding_loop.py:343-345`, in `StructuralEncoder._load` — so
   importing the entry point never touches them, and the trace cannot see them. **Live = 34, not 31.**
   *(ORGAN_MAP already knew this and cites the same site at its pre-edit line numbers 300-303 / 305-307;
   the line numbers have since moved to 343-345. The organ-accounting note did not carry the correction.)*
3. **ORGAN_MAP's E2 says we have "no PE signal, no segmentation."** We do, and it is hiding inside a
   module nobody imports: **`information_foraging.SurpriseSegmenter`** (`:194-224`) is a literal Event
   Segmentation Theory boundary detector — post a boundary when surprise exceeds `mean + k·sd` of the
   recent window. **It was built for foraging patches and has never been run on discourse.**
   *Hypothesis-pending-VET; it is a candidate filler, not a filled slot.*

### 2.2 THE ELEVEN SLOTS ORGAN_MAP HAS NO ROW FOR

**This is the part of the design that did not exist before.** These are jobs the substrate must do
that a brain-fidelity audit cannot surface, because several of them have **no brain organ at all** —
and a map organised by brain organ will never grow a row for them.

| ID | the job | brain structure | pinned or invention |
|---|---|---|---|
| **P1** | intention → an ordered sequence of word meanings | production network; lemma selection | **PINNED stage, UNPINNED equation** |
| **P2** | word meanings → an actual string a person reads | grammatical + phonological encoding | **PINNED stage, UNPINNED equation** |
| **P3** | every answer carries where it came from | source monitoring (mPFC/hippocampal) — **weak** | **INVENTION**, and a deliberate super-brain target |
| **Q1** | a question → a retrieval cue + what kind of answer is wanted | language network parses; MD sets the task | PINNED-SYSTEM / UNPINNED-EQUATION |
| **Q2** | **work the answer out** (domain-general inference) | **MULTIPLE-DEMAND network** | **PINNED SYSTEM, UNPINNED COMPUTATION** |
| **Q3** | accept / clarify / refuse *the answer* (H3 gates the *write*) | metacognitive criterion | PINNED form, UNPINNED criterion |
| **R1** | read a definition out of running prose | **NONE — literacy is cultural, it recycles VWFA + language net** | **INVENTION, honestly so** |
| **R2** | know what material exists to read at all | **NONE — the brain does not own the library** | **INVENTION** |
| **R3** | the foundation survives a restart | none (systems consolidation is a loose analogy) | **INVENTION** |
| **R4** | promote provisional knowledge to durable knowledge | CLS hippocampus → neocortex | **PINNED as a systems claim** |
| **X1** | split text into the units everything else consumes | no clean analogue | **INVENTION** |

**Why P1/P2 matter more than their position on this list suggests:** the substrate's entire stated
purpose is glass-box runtime reasoning with **no LLM at inference**. An LLM would have supplied
production for free. **We forbade the thing that was going to do our talking and never wrote down the
slot.**

---

## 3. PART 2 — FILL EACH SLOT

Adjudicated on **runtime and on-disk evidence**, never a docstring and never a verdict string.
Where a slot is EMPTY it is called EMPTY in bold. Where two organs compete the loser is named, because
"which one do we use" is a question that has cost this project time before.

### 3.1 THE CONTESTS, DECIDED

| slot | winner | loser(s), and why they lose |
|---|---|---|
| A1 orthography | **`char_trigram_encoder`** on measured grounds | `vwfa` is more brain-faithful (multi-scale, position-bound) but the **orthography-ONLY trigram arm reads 0.0870 [0.0783,0.0960] against the live path's 0.0480** — the crude one wins the only comparison that was run. `char_positional_encoder` untested against either. **Wire the trigram, keep vwfa as the fidelity target.** |
| D2 cleanup | **`vsa_cleanup_memory`** | It is the only cleanup organ that ships **five independently-failable self-tests** — `selftest_not_inert`, `selftest_null_and_known_answer_fail_independently`, `selftest_capacity_is_measurable`, `selftest_fixed_point`, `selftest_incumbent_is_argmax_preserving`. `cleanup_family` + `iterative_attractor` are the live incumbents and every one of them terminates in `sign()`. **⚠️ This is a HYGIENE swap, not a capability bet: settling has been tested three times and buys +0.005 / +0.003 / −0.020.** |
| D3 episodic write | **`hippocampal_encoder`** | Fidelity **SAME** per ORGAN_MAP; probe: pattern completion **cos 0.2000 → 0.9173**, sparsity 0.0195, 12/12 distinct outputs. |
| D2-addressed read | **`ca3_completer`** | Complements rather than competes with the above — it is completion **routed through an address**. Note its own `selftest_default_is_off`: it is OFF by default and wiring it is an explicit decision. |
| E3 coreference | **`coreference_resolver`** as the base | It is LIVE and it is the only one with a **same-run** floor comparison: **0.7193 vs recency 0.5614 and singleton 0.3860**, oracle 0.9298. `coref` is the cross-sentence extension (cross 0.3610 vs single-sentence 0.2116) but the ledger requires its narrowing to travel with it: ***"the mechanism is a 5-sentence WINDOW, not 'scenes'."*** `bundle_focus_coref`, `event_centrality_coref`, `coref_distractor_suppress`, `scene_segment` are four further coref organs — **do not wire five.** |
| G1 learning rule | **`compose_freq_routing`** for the update; **`learner/`** stays the gate | `compose_freq_routing:110-111` is the **only genuine delta rule we own** (`error = tgt − ctx@Wᵀ; W += lr·(errorᵀ@ctx)`), chain-grade **+0.1477, cv 0.0009, 5 seeds, cross-N — and it has ZERO consumers.** `learning.py` is reward-gated pure Hebbian with no error term. Per the project's own MISSING-LEARNING rule, expand the learner; do not build a parallel one. |
| G3 gain | **`excitability`** | Real per-ROW multiplicative write gain, **HARD_PASS gated_hi 1.000 vs ungated_hi 0.500 at K=1200**, and **zero consumers**. `modulators` is LIVE but is five global scalars, one of which (`attention`) is used as a hard cutoff rather than a gain. |
| H2 foraging | **`information_foraging` + `corpus_registry` + `gap_driven_reader`**, as a trio | `information_foraging` alone is not the organ: the ledger's narrowing is that it is **A FLOOR-BEATER, NOT A SHELF-BEATER — FROZEN, the fixed schedule it exists to replace, scores HIGHER (0.0743 vs 0.0617).** It needs a shelf to forage over. **`corpus_registry` IS that shelf and ORGAN_MAP does not know it exists**: it enumerates all 36 entries of `data/corpora/` where the live loop's readable universe is a hard-coded 4-entry dict. |
| R1 definitions | **`definitional_extraction`** | 228,133 definitions from 2.78 M SimpleWiki lines in 426 s; probe 9 distinct outputs / 12 inputs, all **5/5 pattern families fire**, disagrees with a naive `contains " is "` heuristic on 3 of 12. **`definitional_predicate_v61` LOSES OUTRIGHT: it fires on 1 of 375 already-definitional sentences — 0.27% of its own intended population.** |
| Q3 answer gate | **`cortex`** | Probe: **monotone confidence 1.0 → 0.0256**, ACCEPT/CLARIFY/REFUSE at documented taus, 11/11 distinct. **⚠️ Wire it with `atom_consultation` OFF** — that sub-organ has `applied` hard-coded `False` and **cannot change a decision by construction.** `conformal` is the only statistically principled criterion we own (split-conformal quantile) and is unwired; `clarify_gate`/`refuse_gate` are percentile heuristics. |
| P3 provenance | **`tracing`** (LIVE) + `hd_fact_store` SOURCE/TRUST fields | `per_item_log`, `session_log`, `snapshots` are additive; keep. This slot is genuinely **FILLED**. |

### 3.2 THE EMPTY SLOTS — THE MOST VALUABLE OUTPUT IN THIS DOCUMENT

**Seven slots have nothing in them. Two more have something that cannot work. One is a whole network.**

1. **🔴 Q2 — DOMAIN-GENERAL INFERENCE. EMPTY, AND IT IS AN ENTIRE NETWORK, NOT AN ORGAN.**
   `reasoner` returns **an answer identical to a similarity baseline on 38 of 40 questions**, and its
   derivation path reaches 7 of 40 — probe verdict **THIN**. `multi_hop`'s default **β = n_dim makes
   its "soft" softmax a Dirac delta, i.e. bit-identical to hard argmax**, and the module's own code
   records that **two prior cells were confounded by exactly this**. `kg_traversal` is hard argmax
   with no soft state between hops. `bayesian_inference`, `gather_reason` and `glass_box_loop` are
   real but are retrieval and audit, not inference. **The brain's answer to this slot is a network
   that is dissociated from language by direct evidence, and we have none of it.**

2. **🔴 P1 + P2 — ANSWER PRODUCTION. EMPTY.** `hdlab/generation.py` is the only candidate. Read at
   HEAD, it walks a codebook: `k_t = S @ k_{t-1}` + Langevin noise + nearest-codebook snap, returning
   **a list of codebook INDICES** (`generate_with_names` maps them through a caller-supplied name
   list). **There is no lemma stage, no grammatical encoding, no morphology, no surface string.** And
   its own docstring disqualifies its evidence: the test regime ran *"BELOW substrate Hebbian
   capacity ~327 — substrate cannot fail by construction at that density."* **A self-declared
   non-can-fail test is not evidence.** *This is the slot the no-LLM invariant created and nobody
   wrote down.*

3. **🔴 D5 — ACTIVE WORKING MEMORY. EMPTY, AND THE FILENAME IS A TRAP.** `hdlab/working_memory.py` is
   116 lines: **two `ValueError`-raising assertion guards and some envelope constants. No bank, no
   state, no update rule** — verified by reading it this pass. It is LIVE, which means the substrate
   imports a module named after the organ and gets nothing. The two real candidates both fail:
   `slot_attention_wm` was gated **SHELVE**, and `situation_focus.ChunkedFocus` **HARD_FAILs on real
   prose at 0.0154 against a bag-of-words 0.1448 with a scramble control that does not collapse —
   i.e. its order channel is measurably empty.**

4. **🔴 D7 — SUCCESSOR REPRESENTATION. EMPTY, AND ITS EQUATION IS FULLY PINNED.** `M = (I − γP)⁻¹`;
   grid cells are its eigenvectors. **This is the only slot in the whole substrate where the brain
   hands us a closed-form equation and we have written none of it.** It is also the organ that blocks
   the one normative replay-selection rule, so D4 is blocked behind it.

5. **🔴 F5 — COHERENCE MONITOR. EMPTY.** Nothing computes `‖Δ situation model‖`. The system cannot
   notice that it has misunderstood something. *(And this is a legitimate later super-brain target —
   humans miss 40-50% of controlled semantic anomalies.)*

6. **🔴 F6 — MULTI-SENTENCE INTEGRATION. EMPTY.** No constraint-satisfaction settle over propositions.
   ⚠️ Its brain-side equation is flagged in ORGAN_MAP as *recalled, not freshly re-verified* — **verify
   before building.**

7. **🔴 E4 — DISCOURSE BRIDGING. EMPTY, AND THIS ONE IS NOT A BUILD TARGET RIGHT NOW.** It is **two
   measured nulls**, one of them the owner's own proposed mechanism, CI-separated **below** a
   neighbour-copying incumbent. **Do not fill this slot until something upstream changes.**

8. **🟠 B1 out-of-lexicon — EMPTY IN EFFECT.** `lexical_similarity` is LIVE and works **inside a
   hand-authored lexicon of ~359 concepts**; on tiers 1/2/3 it reads **0.931 / 0.304 / 0.002** against
   a window baseline's 0.859 / 0.852 / 0.830. **A cliff, not a pass.** For the ~99.4% of vocabulary
   outside that lexicon there is no working comparator. `grounded_similarity` is capped below the
   decision threshold by construction and is on a DO-NOT-REDO list (76.18% of SimLex on two values).

9. **🟠 G2 — PREDICTION-ERROR GATE. PRESENT AND INERT.** `predictive_coding` exists and self-tests,
   but measured at threshold 0.3 the **skip rate is 0.00 — byte-identical to ungated. The gate never
   fires.** A knob that reads as live and is not.

**And one slot is deliberately left empty: C4 settling.** ORGAN_MAP declines it on fidelity grounds —
adding CA3-style completion to the comparator would make near-neighbour discrimination **worse**.
**The standing "reuse the owned organ" rule must not fire here.**

### 3.3 THE STANDING FILLERS, FOR COMPLETENESS

`gap_detector` (H1) is the healthiest organ in the map — floored, passing, with a real ablation
control; caveat, AUC 1.000 on synthetic probes. `thematic_role_labeler` (F3) is LIVE but its
revalidation cell is **HARD_FAIL** because `animacy_only` reproduces the full model to within 0.05 —
**one cue is doing the work.** `frame_induction` (F4) is LIVE and **loses to a position-majority
baseline** (0.833 vs 1.000). `action_selection` (G4) is fidelity-SAME and unwired, with self-reported
decay 0.653@depth-4 → 0.075@depth-6. `situation_model_accumulate` (E2) is LIVE. `hd_fact_store` (S1)
is LIVE and genuinely glass-box — every field including provenance recovers by role-query unbind.
`foundation_persistence` (R3), `prelim_tier` + `three_tier_loop` (R4), and `corpus_registry` (R2) all
self-test clean and are all **unwired**.

---

## 4. PART 3 — WIRING ORDER, WHAT IT COSTS, AND WHAT IT WOULD ACTUALLY DO

### 4.1 THE ORDER, AND WHAT FORCES IT

**Dependencies, not preferences:**

```
 TIER 0  (no dependencies, unblocks everything downstream)
   R2 corpus_registry ──► H2 information_foraging ──► R1 definitional_extraction
        the shelf            what to read next          what to take from it
   P3 tracing  [already live — keep]
   X1 sentence splitting  [already live inside the loop]

 TIER 1  (needs a stream of new material, i.e. needs Tier 0)
   D3 hippocampal_encoder ──► D2 ca3_completer ──► R4 prelim_tier/three_tier_loop ──► R3 foundation_persistence
        write an episode        read it back           promote it                       make it survive

 TIER 2  (needs a populated store)
   E3 coreference_resolver (+coref, narrowing attached) ──► E2 situation_model_accumulate
   Q1 semantic_parser ──► Q3 cortex

 TIER 3  (BUILD, not wire — these are the empties)
   Q2 domain-general inference   [EMPTY — a whole network]
   P1/P2 answer production       [EMPTY]
   D5 working memory             [EMPTY — the module is a stub]
   D7 successor representation   [EMPTY — equation fully pinned]
   F5 coherence monitor          [EMPTY]
```

**Hard orderings, each with its reason:**
- **R2 before H2.** A foraging controller with no shelf can only re-rank what it is handed; that is
  precisely why the live loop reads the same 4 segments forever while 36 corpora sit on disk.
- **H2 before R4/D4.** Interleaved-retention and promotion tests are untestable without a stream of
  genuinely new material to forget.
- **D3 before D2-addressed.** Nothing to complete until something is written.
- **E3 before E2.** The situation-model assembly hits coreference as its organic wall.
- **B4 (capacity) strictly before B1/B2 (content).** ORGAN_MAP: without a `d` where capacity is not
  the limiter, a content effect and a capacity effect are confounded — **a mistake this programme has
  already made once.**

### 4.2 THE IMPORT-COST TAX, HONESTLY

Import times below are from `scratch/organ_audit/import_results.json`, a **parallel** sweep, so they
are inflated — `import torch` alone measures ~20 s under the same contention. **Treat them as an
ordering, not as absolute seconds**, and note the organ-accounting note quotes `situation_reader` at
**204.5 s** where this sweep reads 171 s.

| module | sweep import (s) | verdict |
|---|---|---|
| `situation_reader` | **171** (204.5 elsewhere) | **DO NOT WIRE AS-IS.** `:108` runs a **full frame-induction training at IMPORT time**, deliberately. Its self-test **TIMED OUT at 240 s** — a budget result, not a breakage result. It also imports from `experiments/`, a layering inversion. **Make the training lazy first.** |
| `_scratch_orig_goal_owner_select` | **100** | **DELETE.** A `_scratch_*` file in the durable organ directory, registered as a capability, and inside the 67 "recoverable" list. |
| `definitional_extraction` | **75** | Acceptable — pay it once at loop start, not per document. |
| `closed_class_lexicon` / `animacy_lexicon` | 71 / 66 | already live. |
| `definitional_predicate_v61` | 63 | **do not wire** (0.27% fire rate). |
| everything else on the wire list | ≤ 40 | `hippocampal_encoder` 4, `information_foraging` 10, `corpus_registry` 36, `cortex` 38, `coref` 23, `vsa_cleanup_memory` 3. |

**The honest total:** the Tier-0 + Tier-1 + Tier-2 wire list costs roughly **75 s of one-time import
dominated entirely by `definitional_extraction`**, provided `situation_reader` is excluded and
`_scratch_orig_goal_owner_select` is removed. **The 204.5 s organ is not on the wire list, and that
is the single biggest cost decision in this document.**

### 4.3 WHAT THE ASSEMBLED SUBSTRATE WOULD ACTUALLY DO — TEXT IN, WHAT OUT

**This is the question the Director could not answer, and it is what the owner is really asking.**

**INGEST (this works, end to end, today plus the Tier-0/1 wiring):**

> A corpus goes in. `corpus_registry` enumerates the 36 available bodies of text and hands the
> forager a shelf. `information_foraging` decides which one to open and, using its own surprise
> profile, when to leave it. Sentences are split, POS-tagged and dependency-parsed by our own
> perceptrons (`pos_tagger`, `arc_parser`, `arc_labeler`). `definitional_extraction` pulls explicit
> definitions out of the running prose. `coreference_resolver` decides which later mention is which
> earlier entity, `thematic_role_labeler` assigns who-did-what-to-whom, and
> `situation_model_accumulate` keeps a running per-entity register across sentences.
> `hippocampal_encoder` writes each episode one-shot into a sparse store, `gap_detector` says whether
> we already knew it, `prelim_tier` promotes what recurs coherently, and `foundation_persistence`
> makes it survive a restart. `tracing` records every step.
>
> **WHAT COMES OUT: a persisted, queryable, fully auditable store of facts and grounded concepts,
> where every entry can be traced back to the sentence and source it came from.** That is real, and
> it is more than most systems can show.

**QUERY (this is where it stops):**

> A question goes in. `semantic_parser` extracts an intent and role slots. The store is addressed —
> `ca3_completer` completes from a partial cue, `vsa_cleanup_memory` denoises the result,
> `gather_reason` gathers what is relevant. `cortex` returns a confidence and one of **ACCEPT /
> CLARIFY / REFUSE**.
>
> **WHAT COMES OUT: a retrieved store entry, a confidence number, a three-way decision, and a
> provenance trace.**
>
> **WHAT DOES NOT COME OUT: an answer that was worked out rather than looked up, and a sentence.**
> Anything requiring domain-general inference falls through to a similarity read (Q2 EMPTY — measured:
> the reasoner equals a similarity baseline on 38 of 40). And the result is a store entry plus a
> confidence, **not language** (P1/P2 EMPTY).

**So, in one line: the assembled substrate is a self-directed READER that builds an auditable
knowledge store and can tell you what it retrieved and how sure it is — and it is not yet a system
that reasons or that talks.** Both of those are named, empty slots with build targets, not vague
shortfalls.

---

## 5. DISCLOSURES

- **No experiment was run and no `hdlab/` or `experiments/` file was modified for this document.** The
  only file written outside `notes/` is `scratch/organ_audit/slot_survey.py` and its JSON output.
- **No tool call was denied during this pass.**
- **Strategic reads, marked as such, all hypothesis-pending-VET:** (a) that the missing multiple-demand
  network *explains* the reasoner's similarity-equality rather than merely being consistent with it;
  (b) that `SurpriseSegmenter` will transfer from foraging patches to discourse boundaries — it has
  never been run on discourse; (c) that swapping `vsa_cleanup_memory` for the live cleanup family is a
  net gain — it is a hygiene argument, and settling has three floored results at +0.005 / +0.003 /
  −0.020.
- **Numbers carried from other documents are cited to them and were not re-measured here:** the
  0.7193 / 0.5614 / 0.3860 coref triple, the 0.0870 / 0.0480 orthographic pair, the tier
  0.931/0.304/0.002 cliff, the +0.1477 `compose_freq_routing` figure, and the 1.000/0.500 excitability
  pair all come from ORGAN_MAP §4 and §10.1. **Re-verify before leaning on any of them** — a note is a
  measurement with a timestamp, not a standing fact.
- **What I verified directly on disk this pass:** the 147-module enumeration and every import time /
  self-test status quoted; the lazy-import site at `reading_grounding_loop.py:343-345`;
  `working_memory.py`'s 116 lines and two guards; `generation.py`'s full source; `continual.py`'s
  header; `SurpriseSegmenter` at `information_foraging.py:194-224`; `corpus_registry`'s docstring; and
  the two vetting-ledger narrowings for `information_foraging` and `coref`.
- **Triple-check statement** (CLAUDE.md Evidence discipline 5), for the one place this doc calls
  something worse than documented — `definitional_predicate_v61` and `atom_consultation` as false
  coverage: right file (HEAD `hdlab/`), right version (HEAD), right env (`.venv` throughout), right
  corpus (`data/corpora/simplewiki`), right metric (source-verified keys), right arm (flags toggled one
  at a time). Both findings are carried from the constant-behaviour probe in
  `notes/ORGAN_ACCOUNTING_2026-08-18.md`, not newly asserted.
