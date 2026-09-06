---
priority: 10
slug: reason_over_the_causal_network_multi_hop_chains_and_counterfactuals
status: CANDIDATE
review:
review_text:
---

# PROBLEM: the reader EXTRACTS a causal network (cause->outcome edges) but never REASONS over it -- it cannot answer multi-hop causal-chain questions ("what ULTIMATELY caused Z?", trace the chain of consequence, name the mediating cause) or COUNTERFACTUALS ("if X had not happened, would Y still have happened?"), which narrative comprehension requires. Build a glass-box reasoner OVER the already-extracted network: traverse it for multi-hop chains (ultimate/mediating cause) and evaluate counterfactual necessity by SIMULATED intervention (remove/negate a node, re-propagate, check whether the outcome still holds), CI-separated over a most-recent/adjacency floor (which must LOSE on the multi-hop items) and an info-free shuffled-edge twin, on MODERN non-circular causal/counterfactual gold.

**slug:** `reason_over_the_causal_network_multi_hop_chains_and_counterfactuals` -- **opened:** 2026-09-06 by the strategy
session. This is the REASONING-PHASE turn: the substrate has spent the program BUILDING the situation model (extracting
events, coref, time, and a causal network); this is the first problem that runs INFERENCE over that model. It COMPOSES the
already-built causal network + traversal primitives; it does NOT re-extract or re-type links. **status:** CANDIDATE -- a
MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). Glass-box, NO
external LLM at inference (the invariant) -- the traversal + counterfactual simulation is transparent graph reasoning, not a
learned model.

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed provisionally at `10`
> (a free rank clear of the contested band; a concurrent session is actively re-ranking, so treat the number as a
> placeholder to be reset when this is promoted from CANDIDATE to OPEN). It is HIGH-value -- the comprehension->reasoning pivot, the first inference organ over
> the situation model -- but it is a NEW capability that DEPENDS on the extracted network's quality, so it is ranked below the
> live-measurement/wiring jobs and the modern-corpus rebuild. The rank is a placeholder; set the real priority when this is
> promoted from CANDIDATE to OPEN.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **🎛️ (PHASE DIAGRAM — the substrate is not locked to one regime.)** The substrate's operating point — store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization — is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **🧠🔧 (FULL-STACK UPSTREAM — prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED — make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT — YOU AND UPSTREAM — TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too — and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a person reads a story, they don't just notice that one thing caused another -- they build a whole map of how the
story's events led to each other, and then they can REASON over that map. Ask "what ultimately caused the disaster?" and
they trace the chain back through the intervening events to the root. Ask "if she hadn't sent the letter, would he still
have left?" and they mentally rewind, take that event out, and see whether the ending still follows. Our reader now BUILDS
that map (it links cause to outcome across the text), but it never REASONS over it: it can only answer a one-step "what
caused this?" and even that is a placeholder. It cannot trace a chain to the ultimate cause, cannot name the middle link,
and cannot answer a "what if it hadn't happened?" question. Build the reasoning: walk the map for multi-step chains, and
answer "was this really necessary?" by taking the event out of the map and checking whether the outcome still holds.

## 2. WHY THIS ONE
This is the comprehension->REASONING pivot. The whole situation-model program built the model; the QA capstone
(`the_reader_cannot_answer_a_question_over_its_situation_model`) then showed the reader can be ASKED a question -- but its
"why/causal" answer is a one-hop connective placeholder that LOSES to an adjacency floor, and that gold is
connective-reducible/circular, so it measures nothing about reasoning. Trabasso's own account says the payoff of a causal
network is exactly what we have not built: events ON the causal chain are recalled more and judged more important, and
explanation runs by COUNTERFACTUAL NECESSITY. So this is where the causal network stops being a data structure and starts
supporting inference. It REUSES the extracted network and the multi-hop traversal we already built for the goal hierarchy;
it does not re-extract or re-type anything.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation):** a reader represents a narrative as a CAUSAL NETWORK and reasons over it (Trabasso & van den
  Broek 1985; Trabasso, van den Broek & Suh 1989). Events on the connected cause->consequence CHAIN are better recalled and
  judged more important, and comprehension TRACES the chain (multi-hop: ultimate cause = the root ancestor of an outcome;
  the mediating cause = a node on the path between two events). Explanation/attribution uses COUNTERFACTUAL NECESSITY --
  "would the outcome have occurred WITHOUT the cause?" (Trabasso). At the computational level this is Pearl's structural
  causal models -- interventions + counterfactuals -- and Sloman's causal-model theory. Counterfactual reasoning is run as a
  MENTAL SIMULATION over the model (Khemlani & Johnson-Laird mental models), and Kahneman & Miller norm theory governs WHICH
  node gets mutated (the mutable/abnormal one). Salience = network CONNECTIVITY, not recency (PINNED Trabasso, already
  encoded in `goal_hierarchy_graph.connectivity`).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the traversal readout (how a surface question maps to a network
  query -- ultimate-cause / mediating-cause / chain-of-consequence), and the counterfactual-simulation rule (remove or
  NEGATE a node, re-propagate reachability along the edges, and read whether the outcome remains reachable / its endstate
  still holds). **Copy the COMPUTATION** (traverse for chains; simulate an intervention for necessity). SWEEP the traversal
  depth / abstention thresholds. LABEL the network<->simulation composition as OUR-SYNTHESIS.
- **NOT brain-faithful:** answering "what caused Z" by picking the most-recent prior event (that IS the adjacency floor);
  a LEARNED statistical do-calculus estimator over the network (interventional network inference HARD_FAILED here -- the
  glass-box graph-simulation counterfactual below is a DIFFERENT thing, Pearl's counterfactual at the computational level,
  not a fitted causal-discovery model); an external LLM; treating the connective-reducible board causal gold as a reasoning
  target.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The live reader BUILDS a causal network: `situation_reader._read_causation` populates `sm.causal_links`
    (`CausalLink(cause, outcome, method)` per sentence) via connective / bridge / **mental_bridge** methods (the mental
    half landed 2026-09-05). `experiments/_causal_network.py` already builds the WHOLE-passage network
    (`build_causal_edges`), does forward reachability to an outcome (`on_chain_events` -- the Trabasso on-chain vs dead-end
    set), and ingests edges into a `KGStore` for one-hop / n-hop causal traversal (the P12 chain-grade primitive).
  - `hdlab/goal_hierarchy_graph.py` ALREADY implements the multi-hop chain traversal you need, over the GOAL graph:
    `ancestors` / `root` / `why_chain` / `superordinate` ("why did X do this, ULTIMATELY?") + `connectivity` (the PINNED
    Trabasso salience). This is the traversal pattern to REUSE over the causal edges, not to re-derive.
  - `hdlab/event_type.py` types nodes (PHYSICAL / PERCEPTION / COGNITION / EMOTION / ...); the goal/affect registers carry
    motivation edges; `hdlab/graded_competition.py` is the graded-selection primitive.
  - The QA capstone's "why/causal" arm scored 0.442 vs an adjacency floor 0.652 (a LOSS) -- but that gold is
    CONNECTIVE-REDUCIBLE/circular (`PROVISIONAL_WIRINGS.md` sec.1+sec.4): a high score recovers the text's connective
    structure, not reasoning. It is a ONE-HOP placeholder measurement, not a chain/counterfactual number.
  - Do-calculus / interventional network inference HARD_FAILED (do NOT rebuild it).
- **INFERRED (you must prove):** that TRAVERSING the extracted causal network answers multi-hop chain questions
  (ultimate cause / mediating cause / chain-of-consequence) CI-separated over a most-recent/adjacency floor that LOSES on
  the multi-hop items (proving the traversal is load-bearing), AND that COUNTERFACTUAL-NECESSITY questions ("if X had not
  happened, would Y still have?") answered by simulated node-removal intervention beat the info-free shuffled-edge twin
  CI-separated, on MODERN non-circular gold -- OR a rigorous located NEGATIVE (e.g. the reader's extracted per-document
  network is too SPARSE/NOISY to support >1-hop reasoning: median chain depth ~1, so multi-hop items collapse to one hop and
  the traversal cannot separate from adjacency; named with counts).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-extract or re-TYPE causal links. Link TYPING/extraction is a DIFFERENT, already-worked line -- read
  `causation_is_typed_per_clause_not_across_the_causal_network` (integrated NEGATIVE) IN FULL, and be aware of
  `causation_typing_needs_a_patient_tendency_estimator`, `causation_has_no_force_dynamic_typing`,
  `wire_the_causation_typer_into_the_live_reader` (all about TYPING the network's edges, not REASONING over the network).
  This problem CONSUMES the already-typed/extracted network and reasons over it.
- Do NOT rebuild do-calculus / learned interventional network inference (HARD_FAILED). The counterfactual here is glass-box
  graph simulation (remove/negate a node, re-propagate), not a fitted estimator.
- Do NOT rebuild the covariation causal-graph organ (`narrative_causal_graph_missing_implicit_inference_organ`, integrated)
  -- it is CORPUS-level causal KNOWLEDGE across documents; this is REASONING within one document's extracted network.
- Do NOT answer by re-reading / question-word overlap against the raw text (that IS the floor). Do NOT use the board's
  connective-reducible causal QA gold as the reasoning gold.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "causal"` /
  `"chain"` / `"counterfactual"` / `"necessity"` / `"trabasso"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py`, skim `hdlab/`, so you build
  ON the existing organs, not beside them.
- READ IN FULL (the fence -- so you frame this as REASONING, not TYPING): `notes/problems/
  causation_is_typed_per_clause_not_across_the_causal_network/{PROBLEM.md,SOLVED.md}`. Note it CLOSED discourse-level edge
  TYPING as a real-text lever; this problem is a different level (chain + counterfactual reasoning over the network).
- INSPECT what you REUSE: `hdlab/situation_reader.py::_read_causation` + the `CausalLink` dataclass (the live network +
  connective/bridge/mental_bridge methods); `experiments/_causal_network.py` (`build_causal_edges`, `on_chain_events`
  reachability, `KGStore` n-hop traversal); `hdlab/goal_hierarchy_graph.py` (`ancestors`/`root`/`why_chain`/`superordinate`/
  `connectivity` -- the multi-hop chain traversal + Trabasso salience already built for goals); `hdlab/event_type.py`;
  `hdlab/graded_competition.py`; the goal/affect registers.
- READ: `notes/PROVISIONAL_WIRINGS.md` sec.1 + sec.4 (the causal QA gold is connective-reducible/circular -- a
  causal-REASONING gold must be non-circular) and `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b causal entries.
- GOLD: inspect `data/corpora/wiqa` (on-shelf: WIQA "What-If QA", Tandon et al. 2019 -- MODERN, with influence-graphs +
  multi-hop in-para / out-of-para / no-effect counterfactual perturbation questions). Decide fit vs its PROCEDURAL-text
  genre confound (narrative is the target). You are PRE-AUTHORIZED to acquire an open MODERN narrative causal/counterfactual
  set (or construct a modern multi-hop-chain + counterfactual-necessity set) under `data/corpora/<name>/` with a REPRODUCIBLE
  pinned fetch script in `experiments/` + a provenance note. Do NOT use a 19c corpus (McGuffey/LitBank) as load-bearing gold.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box reasoner OVER the extracted causal network** (built in `experiments/`, reasoning over `sm.causal_links` /
   `_causal_network`; REUSE the `goal_hierarchy_graph` traversal pattern + `event_type` node typing), doing BOTH:
   (a) **MULTI-HOP chain traversal** -- ultimate cause (root ancestor of an outcome), mediating cause (a node on the path
   between two events), chain-of-consequence (forward reachability); and (b) **COUNTERFACTUAL NECESSITY by SIMULATED
   intervention** -- remove/negate a node, re-propagate reachability along the edges, and read whether the outcome still
   holds ("would Y still have happened without X?"). NO do-calculus, NO external LLM. Copy the Trabasso/Pearl-counterfactual
   COMPUTATION; SWEEP the traversal-depth / abstention thresholds.
2. **Answers CI-separated over BOTH controls on MODERN non-circular gold:**
   (a) a **most-recent / adjacency floor** recomputed on the same population, which MUST LOSE on the multi-hop items (the
   1-hop answer is wrong exactly when the ultimate cause is not the immediately-prior event -- this is what proves the
   traversal is load-bearing, not a coincidence with recency); and
   (b) the **info-free SHUFFLED-EDGE twin** (permute the causal edges, keep the node set) LOSES CI-separated on both the
   chain and the counterfactual items.
   Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses populations
   (report chain and counterfactual separately, and aggregate). A **POSITIVE control** the metric can move: an item where
   the ultimate cause != the most-recent cause (multi-hop), or a counterfactual where removing the node DISCONNECTS the
   outcome vs one where it does not.
3. **Isolates the REASONING from extraction/typing** -- ablate to a 1-hop readout (and to the untyped adjacency network) and
   show the lift is the network TRAVERSAL + counterfactual SIMULATION, not re-running the one-hop link readout or the edge
   typing.
4. **One-screen summary:** network source -> gold -> floors -> twin -> multi-hop + counterfactual accuracy -> what breaks ->
   verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the counterfactual simulation is sound on constructed graphs -- node-removal
disconnects the outcome 1.00 vs the shuffled twin -- but the reader's REAL extracted network is too sparse to support
multi-hop chains: median depth ~1.2, so N of M multi-hop items reduce to one hop and cannot separate from adjacency; the
bottleneck is the extracted network's missing edges, enumerated with counts").

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated -- do NOT rebuild):** `hdlab/situation_reader.py` (`sm.causal_links` + `_read_causation`:
  connective/bridge/mental_bridge); `experiments/_causal_network.py` (`build_causal_edges` / `on_chain_events` /
  `KGStore` n-hop traversal); `hdlab/goal_hierarchy_graph.py` (the multi-hop chain traversal + PINNED Trabasso
  connectivity salience, already built for goals -- the pattern to lift onto causal edges); `hdlab/event_type.py`
  (node typing); `hdlab/graded_competition.py`; the goal/affect registers (motivation edges); the causal mental-bridge
  edges (landed 2026-09-05).
- **Gold:** `data/corpora/wiqa` (on-shelf modern what-if/counterfactual QA + influence graphs); or a pre-authorized modern
  NARRATIVE counterfactual/multi-hop-causal set under `data/corpora/` with a pinned fetch script in `experiments/`.
- **Motivation + fence:** `causation_is_typed_per_clause_not_across_the_causal_network/SOLVED.md`; the QA capstone's
  why/causal one-hop NEGATIVE; `notes/PROVISIONAL_WIRINGS.md` (the circular causal gold). Audit + heavy->REMOTE
  (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Build in `experiments/` + `verification/`; strategy lands any hdlab
  change (Q111). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b.

## DO NOT QUOTE / DO NOT REDO
- Do NOT use the board's causal QA gold as the reasoning gold -- it is connective-reducible/circular, so a high score
  recovers the text's connective structure, not chain/counterfactual reasoning (`PROVISIONAL_WIRINGS.md` sec.1+sec.4).
- Do NOT quote the QA capstone's why/causal 0.442-vs-0.652 as a reasoning number -- it is a one-hop connective-placeholder
  measurement on a circular gold, not a multi-hop or counterfactual result.
- Do NOT re-TYPE or re-extract causal links (that is the fenced TYPING line) and do NOT rebuild do-calculus / learned
  interventional inference (HARD_FAILED). The extracted network + the typer are the INGREDIENTS; the deliverable is
  REASONING over the network -- multi-hop chains + counterfactual necessity.
- Do NOT use a 19c corpus (McGuffey/LitBank) as load-bearing gold; do NOT use an external LLM at inference (the invariant).
  Strategy owns any hdlab landing.
