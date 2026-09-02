---
priority:
review: EXCELLENT
review_text: "Reverified 4/4 first-hand. A rigorous, multiply-controlled LOCATED NEGATIVE (a full PASS under the bar's located-negative clause) + a real READ-SIDE POSITIVE. Growing the meaning graph from reading does NOT improve WSD (Raganato argmax −0.0088; powered subordinate-override: growth HURTS rare senses −0.0148) — and the ROOT CAUSE is established from ~8 controlled angles: the discriminating signal for rare/subordinate sense selection is TOP-DOWN STRUCTURED COMPREHENSION (predictive coding; the N400 = semantic prediction error), NOT local co-occurrence (5 bottom-up routes all fail consistently). CONFIRMED brain sub-mechanism: naive Hebbian/PPMI growth is rich-get-richer (helps dominant, starves rare); the brain's HOMEOSTATIC BCM fix rescues rare senses (+0.0155 CI-sep) but does not beat static. READ-SIDE POSITIVE (validated, controlled): the graded COMPETITIVE-SETTLING readout recovers subordinate senses +0.19 over discrete argmax, context-driven (beats shuffled-context +0.17 CI-sep), strongest for homonyms; semantic_control reproduces. NOT a ceiling — the route to a positive is building the comprehension model (bootstrapping senses+comprehension). WIRE: TIER-1 = the read organ (reordered-access → competitive settling → semantic_control) is a real read-side meaning-channel upgrade (a scoped DEBT-2 wiring round — this is also the graph-organ DEBT-2 completion, 'emit the settled vector not argmax'); TIER-2 = do NOT wire the discrete-edge growth (confirmed non-improvement). Follow-on FILED: wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector (priority 1, north-star — the convergence point of all three recent submissions). Grade EXCELLENT (located-negative)."
---

<!-- RE-RANK 2026-09-01 (strategy): moved 1 -> 2, below the parser problem
(the_extraction_front_end_parser_is_the_cross_task_bottleneck...). The parser is the highest-COMPOUNDING lever
(three convergent solver lines) and it gates THIS learner's LIVE payoff too -- a meaning graph grown on a bad
parse inherits the parse errors. This remains the north-star meaning-organ work; unchanged in scope. RE-RANK PER THE OWNER. -->


# PROBLEM: the grounded semantic graph is STATIC — built offline from WordNet + ConceptNet + SyntagNet, it does NOT GROW from the reader's OWN reading. That growth is the North Star (LEARNER-ON via a clean foundation): the reader must grow new senses, tune edges, and re-carve granularity from its experienced text, by brain-faithful CONSOLIDATION. Build the LEARNED graph — REUSING the co-occurrence store + learner buffer as the FAST pattern-separated store, the WordNet++ settling graph as the SLOW cortical store, and WIRING the consolidation organ to REPLAY the fast store back into the graph (which also fixes the flagged "cleaned store written-but-never-read" bug — the real completion). Prove the grown graph improves settling-WSD on HELD-OUT MODERN text over the static graph CI-separated, or locate why (naive co-occurrence learning is already a clean NEGATIVE; the faithful fix is context-DISAMBIGUATED self-trained edges).

**slug:** `the_semantic_graph_is_static_needs_to_grow_from_reading_by_learned_consolidation` — **opened:** 2026-09-01
by the strategy session, from the owner-DONE `promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ` (its
NEXT-STEP #2 north-star follow-on; the solver specced the mechanism in `LEARNED_GRAPH_brain_mechanism_spec.md`). **status:**
OPEN — a BUILD problem (the WRITE/LEARN side of the meaning graph). ⚠️ HEAVY → run on REMOTE (this box kills heavy runs at
~250s). Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (RE-RANK PER THE OWNER):** filed at `1` — the North Star made concrete (grow a CLEAN meaning foundation
> from reading, then safe growth). It is the WRITE side of the just-integrated static READ organ, and it WIRES the
> consolidation organ that is currently built-but-disconnected. High leverage, but a LARGE program — expect a
> located-negative-with-a-clear-next-step as a valid first return, not a full win.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation; replicate
> that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker after your tools plateau.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method
> conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested,
> or a SPECIFIC reason it cannot be. Exhausting engineering variations is NOT convergence.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather high-value adjacent info (a control /
> curve / ablation / 2nd gold); enumerate what's LEFT + do it; MAP adjacent bottlenecks (name + on-disk evidence +
> leverage) and EVALUATE each for brain-fidelity + optimization; hit a wall → run a FINER research drill, never stop.
> Implement → test (can-fail, strongest real floor, twin LOSING) → iterate. CANCEL + submit only when the mechanism bar is
> met AND the checklist yields nothing more.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE.

## 1. THE PROBLEM IN PLAIN LANGUAGE
We just gave the reader a good "dictionary graph" of word meanings that it reads by letting activation spread through it.
But that graph is fixed — handed to it once, from generic reference text. A person's meaning-network isn't fixed: it
GROWS as they read — you meet a word in a new context, tentatively note a new sense, and if it keeps recurring in a way
that fits what you already know, it settles in as a real meaning; unused links fade; senses that blur together merge, and
ones that pull apart split. Build that growing side: let the reader add and tune the graph from its OWN reading, the way
the brain consolidates experience — reusing the memory pieces we already have, and finally connecting the "cleaned-up
knowledge" store that currently gets written but never read back into the graph.

## 2. WHY THIS ONE
It is the North Star made concrete (LEARNER-ON via a clean foundation) and the WRITE side of the static READ organ we
just integrated. It also does the real completion the audit keeps flagging: the consolidation organ is built but
DISCONNECTED (the cleaned cortical store is written-but-never-read) — this WIRES it (replay the fast store into the
graph). Meaning that grows from the reader's own domain is exactly the domain-match lever the who-did-what work also
located, from the meaning side.

## MEASURED vs INFERRED
- **MEASURED (inherit; do NOT re-derive):** the STATIC graph organ clears the context-shuffle twin on held-out WiC
  (+0.052 CI-sep) and beats MFS on all-words WSD (+0.030). NAIVE co-occurrence learning is a clean NEGATIVE (does not
  beat the shuffle twin). The residual of the static graph is context-signal strength (SyntagNet + freq-seeding), not
  granularity. `distributional_meaning_channel` (context vectors) + the consolidation organ are BUILT but unwired.
- **INFERRED (you must measure):** whether a graph GROWN from reading — fast-map + cross-situational confirmation +
  schema-gated consolidation + BCM/XCAL edge tuning + usage-based split/merge, with context-DISAMBIGUATED (self-trained)
  edges — improves settling-WSD on HELD-OUT MODERN text over the static graph CI-separated, or locates why not.

## 3. HOW THE BRAIN DOES THIS (the opening move — the solver already specced it)
See `LEARNED_GRAPH_brain_mechanism_spec.md` (deep drill). PINNED: (1) Complementary Learning Systems — a FAST
pattern-separated store (keeps a new sense distinct) + a SLOW distributed cortical graph, with REPLAY/INTERLEAVE the only
stable fix for catastrophic interference (McClelland/McNaughton/O'Reilly 1995). (2) SCHEMA-GATED cortical learning — a
schema-CONSISTENT new sense integrates fast/safely, an inconsistent one stays slow (Tse 2007; McClelland 2013; Rodd &
Davis 2012 on THIS task: a new word-meaning is fragile immediately, needs overnight consolidation to become a stable
competitor). (3) Senses = regions of a CONTINUOUS space (Rodd) — split when usages become contextually separable, merge
when basins overlap (usage-based; Srinivasan 2019). (4) Edges = BCM/XCAL co-activation with a sliding threshold
(self-normalizing); resting levels = log-frequency → basin depth; cross-situational accumulation (Yu & Smith 2007) is the
evidence gate. SUBSTRATE ROLE MAP: co-occurrence store + learner buffer = the FAST store; the WordNet++ settling graph =
the SLOW store; the consolidation organ = replay/interleaving (WIRE it to read the fast store + write back to the graph).

## 4. PINNED vs OUR-INVENTION
- **PINNED (COPY):** CLS fast/slow split with replay; schema-gated learning rate; continuous-space senses with
  usage-based split/merge; BCM/XCAL edges; cross-situational confirmation as the crystallization gate; a shared
  divisive-normalization pool for read AND write.
- **OUR-INVENTION-UNDER-TEST (SWEEP):** τ_split / τ_merge; the η_fast/η_slow ratio magnitude (the KIND is pinned:
  hippo ≫ cortex, schema raises cortical rate); k cross-situational confirmations. (θ_M is self-adjusting — NOT a swept
  constant.)

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- ⛔ NAIVE co-occurrence learning = a clean NEGATIVE (doesn't beat the shuffle twin) — do NOT re-run it; the faithful fix
  is context-DISAMBIGUATED self-trained edges (not MFS-disambiguated, not raw co-occurrence).
- BUILD ON / REUSE (do NOT reinvent): the static `grounded_semantic_graph_organ.py` (the SLOW store + settling READ), the
  co-occurrence store + `hdlab/learner/*` recent-buffer (the FAST store), the consolidation organ (replay — WIRE it), the
  `distributional_meaning_channel` (context vectors), `ultrametric_clustering` (sense split/merge substrate). No external LLM.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS (before proposing anything):** (1) understand ALL the existing organs — `python tools/substrate_map.py`,
  `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read the parent SOLVED.md
  (`promote_the_grounded_semantic_graph…`) AND `LEARNED_GRAPH_brain_mechanism_spec.md` IN FULL. Reuse, don't reinvent.
- Enumerate the substrate role map on disk: the co-occurrence store + learner buffer (FAST), the settling graph (SLOW),
  the consolidation organ (replay — confirm the "written-but-never-read" wiring gap), `distributional_meaning_channel`.
- Route heavy runs to REMOTE (this box kills them at ~250s).

## THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST lose)
PASS = a graph GROWN from reading (fast-map + cross-situational confirmation + schema-gated consolidation + BCM/XCAL
tuning + usage-based split/merge, context-DISAMBIGUATED edges) improves SETTLING-WSD on HELD-OUT MODERN text CI-separated
over the STATIC WordNet++ graph (gated on the static upper bound; recompute the floor on the held-out population), with an
info-free twin (shuffled-context / naive-co-occurrence edges) LOSING CI-sep, AND an anti-interference control (the grown
graph does NOT DEGRADE on already-known senses — catastrophic-interference check). Report CI half-width + null p95. A
rigorous located NEGATIVE is a full PASS: if faithfully-built growth does not beat the static graph, name which mechanism
(fast-map / schema-gate / split-merge / edge-rule) fails and why.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/` (REMOTE for heavy runs). Reuse `grounded_semantic_graph_organ.py` (static
graph + settling), the co-occurrence store + `hdlab/learner/*`, the consolidation organ, `distributional_meaning_channel`,
`ultrametric_clustering`. Strategy lands any hdlab wire (Q111, default-off, witnessed) — the payoff wire is the
consolidation organ reading the fast store and writing the grown graph. Fold an AUDIT UPDATE into
`BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the meaning graph grows from reading by CLS consolidation; the cleaned store is now read).

## DO NOT QUOTE
- Do NOT quote the static organ's numbers (+0.052 WiC, +0.030 WSD) as YOUR result — MOTIVATION. Re-measure the GROWN vs
  STATIC delta on held-out modern text.
- Do NOT claim a win without the anti-interference control (growth must not degrade known senses) and the shuffled/naive
  twin (the DISAMBIGUATED growth, not any edge addition, must do the work).
- Do NOT use an external LLM to disambiguate the self-trained edges (the invariant) — use the substrate's own settling +
  context vectors.
