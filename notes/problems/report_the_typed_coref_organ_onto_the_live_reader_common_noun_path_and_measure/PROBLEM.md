---
slug: report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure
status: INTEGRATED
review: EXCELLENT
review_text: Reverified 19/19 first-hand. Rigorous PARTIAL/located-negative -- refuted the brief's OWN mechanism, isolated the deficit to the binder's binding, proved the typed_coref resolution fix (0.5671 vs 0.5412 CI-sep, +0.0767 over the deployed binder) + a clean AUDIT UPDATE. Realization wire (typed_coref resolution consumer + board arm) tracked.
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-09-08, as PARTIAL/located-negative; realization wire tracked)
> Reverified FIRST-HAND: **19/19 witness checks reproduced** (`verification/test_commonnoun_binder_live_report.py`), every headline recomputed from source on the full GUM modern TEST (n=2855). Nothing failed under my check.
> **What makes it excellent:** it followed the DISK over the brief. Asked to re-port two levers onto the live `commonnoun_binder`, it did so faithfully, found it reaches only PARITY (not a beat), and then LOCATED WHY -- the deployed binder is a LitBank cluster-F1 organ (person-gate + modifier-split + event-centrality) whose BINDING trails string-identity on per-mention RESOLUTION (0.4904 vs 0.5412), while the `typed_coref` binding on the identical schema BEATS it (+0.0767 CI-sep) and beats string-identity (0.5671, +0.0259 CI-sep). It proved the fix on the EXACT live dict schema (`typed_coref_liveschema_resolve` 0.5664, recovering the organ), with the info-free twin LOSING CI-sep, NAME no-regress (+0.0024), and an ORACLE-comparator ceiling (0.7492) that quantifies ~88% of the residual as WORLD KNOWLEDGE the WordNet comparator misses.
> **Volunteered against itself:** the honest headline "no CI-separated win via the re-port the brief specified"; the win is board-INVISIBLE today (no live resolution dim); OOD (GENTLE) is a direction+magnitude replication, NOT a CI-separated claim (n=275 underpowered).
> **What did not reproduce under my check:** nothing -- 19/19 held.
> **Not-claimed-that-matters:** it CONFIRMED the de-leak (its numbers never use the gold-coref peek in a resolution decision) and RECONCILED the occupation-KB located negative -- its coarse person-typing (+0.0102 CI-sep) is a real TYPE constraint distinct from the specific occupation-KB, cleanly handed to the `world_knowledge_common_noun_to_name_bridge` problem.
> **AUDIT UPDATE folded (§2b):** `commonnoun_binder` = a cluster-F1 organ, NOT a resolution organ, and person-gated (non-brain-foundational for coref); the `typed_coref` organ is the brain-foundational RESOLUTION path. **Realization (tracked):** the Q111 wire (serve the reader's common-noun RESOLUTION consumer from `hdlab.typed_coref`, additive/default-on-safe, + a `board_commonnoun_resolution_dimension` arm) -- lands next; the binder stays as-is for the clustering (`sm.entities`) consumer.

# PROBLEM: `hdlab/typed_coref.py` beats same-head string-identity on common-noun coref (0.5671 vs 0.5412, CI-sep) but ONLY on the URG board-instrument proxy -- the LIVE reader common-noun path (`hdlab/commonnoun_binder.py`) is a DIFFERENT mention schema and never uses it -- so re-port the two brain-faithful levers (a typed NOMINAL card identity separate from the pronoun-polluted full card; a NON-WRITING different-head type bridge) onto the live reader's coref stream, prove the live common-noun RESOLUTION accuracy lifts CI-separated on modern GUM with pronoun/kb no-regress and the info-free twin LOSING, then flip per no-more-default-off.

**slug:** `report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure` -- **opened:** 2026-09-07
by the strategy session. The typed common-noun coref win was PROMOTED to `hdlab/typed_coref.py` (committable, parity-exact
vs the reference), but it is `gum_coref.Doc`-schema typed and the win was measured on the URG board-instrument proxy, NOT the
live `commonnoun_binder` path. This is the "board-instrument proxy != live gain" step: re-port the levers onto the live
mention stream and measure the LIVE common-noun resolution. REUSE of a landed organ, fidelity-risky (schema re-port).

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**
>
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
>
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
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Re-recognising a character by a plain noun ("the company" -> Google, "the boy" -> the kid named earlier) is common-noun
coreference. We found the reader was WORSE at it than a dumb same-word rule, and fixed it with two brain-faithful ideas:
give each character a clean NAME/NOUN identity kept apart from its (only half-right) pronoun history, and resolve a
different-worded mention for the current sentence WITHOUT permanently merging it when unsure. That made the reader BEAT the
dumb rule on a clean statistical margin. But we proved it on a stand-in scorer, not the reader's real common-noun machinery.
This job moves the fix into the reader's actual path and checks the win survives there.

## 2. WHY THIS ONE
It converts a proven, committed, parity-exact organ (`hdlab/typed_coref.py`) from a board-instrument PROXY win into a LIVE
reader gain -- the second half of the same "landed != live" discipline as the crosstype-bridge wire. The levers are the
brain's (Ariel: identity is nominal, pronouns are transient pointers; Nieuwland: hold under uncertainty, don't merge). The
risk is purely the schema re-port (the organ is typed to the `gum_coref.Doc` mentions; the live reader uses a different
mention-dict stream), which is exactly the kind of fidelity-preserving port the substrate needs to get right, not skip.

## 3. HOW THE BRAIN DOES THIS
PINNED. A referent's descriptive IDENTITY is anchored on its naming/nominal descriptions; pronouns are transient
high-accessibility deictic pointers that do NOT re-describe the entity (Ariel 1990) -- so common-noun coref should be scored
on a NOMINAL identity view, kept separate from the pronoun-polluted full mention set. A definite with no same-head antecedent
resolves to the most type-compatible prior referent for THIS reference but is HELD, not merged, under uncertainty (Nieuwland
hold-under-uncertainty) -- committing the merge corrupts the same-head chain. The type comparator reuses the landed
`hdlab.typed_spokes.coref_type_license` (Lambon-Ralph typed spokes). All three are already in `hdlab/typed_coref.py`.

## 4. MEASURED vs INFERRED
- **MEASURED (reverified 9/9 + parity-exact):** on the URG board instrument (GUM TEST, n=2855 anaphoric common-noun mentions),
  `hdlab/typed_coref.py` scores common 0.5671 vs same-head string-identity 0.5412 (+0.0259 CI[+0.0134,+0.0385] CI-sep), +0.0792
  over the URG incumbent; the info-free twin loses; pronoun/kb byte-identical; name +0.024; the organ reproduces the reference
  EXACTLY (0/137 docs, 9782 mentions). The typed-view de-pollution alone is +0.0439 over the incumbent CI-sep.
- **INFERRED (this problem must MEASURE):** that the SAME de-pollution + non-writing-bridge win appears in the LIVE reader's
  common-noun path (`hdlab/commonnoun_binder.py` and whatever the live coref stream feeds), whose mention schema and same-head
  binding differ from the URG resolver. The win is per-mention RESOLUTION accuracy, NOT cluster-F1 -- carry that distinction.

## 5. ALREADY TRIED / DO NOT RE-RUN (the disk outranks this brief)
- **The typed-spokes organ as a WRITING type-license FILTER on the live pick: net-NEGATIVE** (regresses; the write is the cost).
  Use it as a NON-WRITING candidate SEED only (as `hdlab/typed_coref.py` does) -- do NOT re-file the writing filter.
- **Committing the different-head bridge to chase cluster-F1: corrupts the same-head chain** (0.769 -> 0.694). Hold, don't merge.
- **Re-tuning ranking / agreement / selector / splitting same-head: measured WASHES or regressions** -- ranking has no headroom
  (the info-free same-head twin ties). The only path higher is world-knowledge content (the P31 KB, filed separately) -- NOT ranking.
- The organ is already ~7x faster (memoized comparator); do not re-optimize the comparator.

## 6. VERIFY BEFORE YOU START
1. Understand the organs: `python tools/substrate_map.py`, skim `hdlab/typed_coref.py` (module docstring + `_self_test`),
   `hdlab/commonnoun_binder.py` (the live common-noun path), `hdlab/coref.py` / `hdlab/graded_coref_pick.py` (the live coref stream),
   `hdlab/typed_spokes.py::coref_type_license` (the reused seed).
2. Read IN FULL the two SOLVEDs: `notes/problems/improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity/SOLVED.md`
   (+ OWNER_NOTES) and the typed-spokes foundation `.../expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md`.
3. Confirm on disk: `python -m hdlab.typed_coref` self-test passes; `verification/test_commonnoun_typed_identity.py` passes 9/9.
   The organ's `resolve_doc(doc)` consumes the `gum_coref.Doc` mention schema (`.eid/.order/.mtype/.text/.lemma_head/.head_g/.gender/.number`)
   -- the live reader's stream differs; the re-port must preserve the three-view card + the non-writing hold EXACTLY.

## 7. THE BAR
PASSES only with ALL of:
1. The two levers (typed NOMINAL card view; non-writing type bridge seeded by `typed_spokes.coref_type_license`) re-ported onto the
   LIVE reader common-noun path behind a NEW opt-in flag (default False, byte-identical off). Strategy owns the hdlab edit (Q111);
   the solver builds + measures + proposes in `experiments/`.
2. LIVE common-noun RESOLUTION accuracy beats the live floor CI-separated on MODERN gold (GUM), reported with a doc-level paired-bootstrap CI.
3. The info-free twin (bridge fires to a RANDOM type-compatible antecedent) LOSES CI-separated.
4. NO regress: pronoun and named-antecedent (kb) consumers byte-identical or up; no other reader consumer regresses.
5. Per no-more-default-off: if net-positive live, propose the flip ON; else state the measured reason to hold.
A rigorous NEGATIVE is a full pass (e.g. "the live path's same-head binding already captures the nominal view, so the re-port ties -- subsumption, located and counted").

## 8. FILES AND ENTRY POINTS
- Organ: `hdlab/typed_coref.py` (`TypedCorefResolver.resolve_doc`, the 3-view `TypedRef` card, `appos_copula_isa`, `crosstype`... reuse the levers).
- Live target: `hdlab/commonnoun_binder.py` + the live coref stream in `hdlab/coref.py` / `hdlab/graded_coref_pick.py`; wire the flag near the reader's coref config.
- Reused seed: `hdlab/typed_spokes.py::coref_type_license`.
- Reference cells + witness (REUSE the scorer): `experiments/exp_commonnoun_typed_identity_gum_v1.py`, `experiments/exp_unified_referent_gum_v1.py` (the URG proxy), `verification/test_commonnoun_typed_identity.py`.
- Corpus: `data/corpora/gum/` (GUM V12.1.0). Gazetteer: `data/lexicons/name_gender_gazetteer.tsv`.

## DO NOT QUOTE / DO NOT REDO
- The 0.5671 vs 0.5412 numbers are on the URG board-instrument PROXY -- do NOT quote them as the live `commonnoun_binder` number until re-measured on the live path; that re-measurement IS this problem.
- Do NOT re-file the typed-spokes WRITING filter (net-negative) or chase cluster-F1 by committing bridges (corrupts the chain).
- Do NOT lean on 19c gold (owner 2026-09-06); grade on modern GUM.

**TLDR (plain English):** We fixed the reader's ability to recognise a character by a plain noun and proved the fix beats a
dumb baseline -- but on a stand-in bench, not the reader's real machinery. This job moves the fix into the reader's actual
path (keeping the two brain-faithful ideas exactly), checks the win still holds there, leaves pronoun tracking untouched, and
turns it on if it does. It's the twin of the other "plug in a built tool" job.

**QUESTIONS:** none blocking. One scope note: the win is per-mention RESOLUTION accuracy (what downstream binding needs), not
clustering-F1 -- the "hold the merge" step trades cluster shape for resolution correctness; keep the resolution-accuracy framing.

**NEXT STEPS:** run VERIFY BEFORE YOU START; re-port the two levers onto the live stream in `experiments/`; measure live
common-noun resolution + twin + pronoun/kb no-regress; propose the flip. Strategy lands the hdlab edit and, if net-positive, flips it on.
