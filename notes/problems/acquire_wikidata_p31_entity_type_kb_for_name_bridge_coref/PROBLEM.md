---
priority:
slug: acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref
status: INTEGRATED
review:
review_text:
---

<!-- INTEGRATED 2026-09-07 (CONT-24). Owner-DONE, reverified 14/14, FULL-CHAIN per the implement-all-upstream
directive. Landed+verified: C8 directed entity-type spoke in hdlab/typed_spokes.py (664139141, DBpedia InstanceOf
on the ATL hub, name-bridge coref "the artist"<-Zurbaran, two-route CLS +0.1124 CI-sep); board_namebridge arm
(0e1fa55ba); compact-store swap (47ab3aec4, 523MB->79MB byte-equiv); C6 part-whole->bridging_inference HYBRID
flipped live (a057a63bc, c6pw fixes the distractor-pick). Remaining follow-on: the two-route LIVE-reader wire
(+entropy->coref confidence) = the careful reader-schema adapter task (mirrors the crosstype wire brief) + the
gitignored manifest reg. Priority dropped. Detail = ledger CONT-24 + audit §2b(newest). -->


# PROBLEM: common-noun-to-PROPER-NAME "name-bridge" coreference ("the artist" -> "Zurbaran"; ~10% of anaphoric common nouns on GUM) is UNREACHABLE by our WordNet typed spokes because proper names are not in WordNet -- so acquire a curated, pinned, OFFLINE entity-type KB (Wikidata P31 instance-of / DBpedia InstanceOf) under `data/corpora/`, build a DIRECTED TYPE-2 entity-type SPOKE on the ATL hub (extending `hdlab/typed_spokes.py`, keyed like C5/C6, admitted through the consolidation gate), and prove the spoke used as a bounded TYPE-LICENSING filter lifts name-bridge coref CI-separated over the strongest floor on modern gold, with a shuffled-KB info-free twin LOSING and no coref-dim regress -- glass-box, NO external LLM at inference.

**slug:** `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref` -- **opened:** 2026-09-07 by the strategy session.
Encyclopedic type facts about NAMED individuals ("Zurbaran is a painter") are a distinct typed relation WordNet omits;
they are the one common-noun coref slice a no-LLM reader legitimately cannot reach with lexical resources -- but an OFFLINE,
statically-built KB is admissible (the invariant is NO external LLM AT INFERENCE, not no offline asset). **status:**
CANDIDATE -- an ACQUIRE + BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111).
Glass-box, a static offline-built KB asset is admissible, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `8` because,
> although it is the ONLY brain-faithful way past the no-LLM common-noun ceiling for proper-name antecedents, it is a real
> ACQUIRE + BUILD (fetch + gate + spoke + glass-box entity linking), the name-bridge slice is a bounded ~10% of anaphoric
> common nouns (so its whole-dim move is capped), and it is downstream of the SIBLING candidate-quality brief -- a resolver
> that loses to string-identity must be fixed first so the KB's licensed candidates are ranked correctly. It stays CANDIDATE
> until its premise -- that the entity types recover name-bridge links CI-sep on the LIVE resolver -- is measured. Set the
> real priority when promoted from CANDIDATE to OPEN.

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
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a reader meets "the artist" and the only matching earlier mention is the name "Zurbaran", they resolve it instantly
because they KNOW Zurbaran is an artist -- an encyclopedic fact about a specific named individual. Our reader cannot do
this: the dictionary it uses to check "is X a kind of Y" (WordNet) contains common words but not people's or places'
proper names, so the bridge from a common noun to a name is simply missing. About one in ten common-noun references on
modern text is exactly this common-noun-to-name bridge. This job is to go get an open, OFFLINE list of "this named thing
is an instance of this type" (the kind of fact Wikidata records), fold it into the reader's typed-knowledge store as a new
spoke, and use it only to LICENSE a link (recency still chooses WHICH name) -- then prove it recovers name-bridge links
that were previously impossible, with a scrambled version of the list falling apart so we know the real facts are doing the
work. No outside AI reads at inference; the list is a static file built once, offline.

## 2. WHY THIS ONE
This is the one common-noun coref slice a no-LLM reader legitimately CANNOT reach with lexical resources -- the modern
blind-head ceiling is ~0.541 with "~81% needs world-knowledge" barred at inference (`INTEGRATION_LEDGER.md`), and the
proper-name bridge is a concrete, ACQUIRABLE piece of that world knowledge (an admissible OFFLINE static asset). It is a
distinct, ADDITIVE lever from the candidate-quality problem (the SIBLING brief): candidate quality closes the gap to
string-identity on same/different-head common nouns; the entity-type KB extends REACH to proper-name antecedents that
string-identity can NEVER reach. And it GENERALIZES the ATL hub-and-typed-spoke store the world-knowledge integration
already built (C5/C6/C7) to the proper-name entities WordNet omits. Test 4 (does a NUMBER show the DEFECT costs us?): YES --
name-bridge is ~10% of anaphoric common nouns on GUM and is at 0.000 today (WordNet cannot type a proper name); that is a
measured coverage hole, not merely "an alternative exists".

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Encyclopedic knowledge of a named individual's TYPE is a distinct semantic relation stored
  on the anterior temporal lobe (ATL) HUB-AND-SPOKE conceptual system (Patterson, Nestor & Rogers 2007; Lambon Ralph et al.
  2017): the ATL is a transmodal hub binding modality- and relation-specific spokes, and unique-entity / person knowledge
  is a documented ATL specialization (Binder & Desai 2011 -- the TYPE-OF-RELATION is a spoke, not the hub's dense blend).
  "Zurbaran is-a painter" is a DIRECTED taxonomic instance-of edge from a proper-name node to a type node -- the SAME
  directed is-a computation the landed C5 taxonomy spoke already realizes (Collins-Quillian 1969), extended to the
  PROPER-NAME entities WordNet omits. Coreference then uses this as a bounded TYPE-LICENSE: the anaphor's head type must be
  compatible with the antecedent's entity type (Ariel accessibility + agreement), and recency SELECTS among licensed candidates.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** Which KB (Wikidata P31 vs DBpedia InstanceOf) and which pinned
  dump/version; the type-node granularity (map P31 classes onto the C5 WordNet type space vs a native class set); the gate's
  admission margin for a noisy source; the licensing threshold; and HOW the proper-name node keys onto the hub (surface name
  -> entity id -> type). SWEEP these, adopt no number.
- **NOT brain-faithful (do NOT do).** An external LLM / entity-linker API at inference (the invariant -- the KB is a STATIC
  file, and surface name->id linking is GLASS-BOX exact/alias matching); a dense-blend read that cannot represent a directed
  instance-of (the C5/C6 SOLVED proved the dense 200-d hub is analytically INCAPABLE of a directed relation -- this MUST be a
  DIRECTED typed spoke); using the KB as a general knowledge oracle rather than a bounded type-license for coref; a 19c
  corpus as load-bearing gold (BANNED 2026-09-06).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The typed-spoke store is the correct substrate and is LANDED: `hdlab/typed_spokes.py` carries C5 (is-a taxonomy,
    DIRECTED transitive-closure, gate-admitted), C6 (part-whole / instrument, DIRECTED), C7 -- keyed by the SAME hub nodes
    as C1/C2, with a consolidation gate that admits by provenance + resolution and an offline `--build` freeze path
    (`data/frontend_assets/`). It ALREADY exposes a "TYPE-LICENSING read for common-noun coreference (C5 is-a + C6 mero)".
    Proper names are the documented HOLE (WordNet has none).
  - The WordNet type-license as a common-noun lever was MEASURED net-negative on the LIVE resolver (0.4879 -> 0.4683) -- but
    that was COMMON-noun-to-COMMON-noun; the PROPER-name bridge is the untested, WordNet-UNREACHABLE slice (the
    `form_a_discourse_referent...` SOLVED named it; the STAGED `seed_the_entity_world_model_resolver...` entity-KB two-pass
    reader_coref is at 6/6 and named a board-mover in `INTEGRATION_LEDGER.md`).
  - The modern blind-head coref ceiling is ~0.541 with ~81% needing world-knowledge (`INTEGRATION_LEDGER.md`) -- the ceiling
    a lexical resolver cannot pass; the entity-type KB is the admissible offline piece of that world knowledge.
  - The consolidation gate + the offline build path are proven: `python -m hdlab.typed_spokes --build` fits + freezes the
    C6/C7 assets -- the pattern for admitting a NEW directed spoke through the gate exists and is re-runnable.
- **INFERRED (you must prove):** that a curated, pinned, OFFLINE entity-type KB (Wikidata P31 / DBpedia InstanceOf) built
  into a DIRECTED TYPE-2 entity-type SPOKE, used as a bounded TYPE-LICENSE (recency selects), lifts name-bridge (common-noun
  -> proper-name) coref CI-separated over the strongest floor (string-identity / the WordNet-only resolver) on modern gold,
  with a shuffled-KB info-free twin LOSING and no coref-dim regress; OR a located negative with counts (e.g. "the KB types
  the antecedent name X% of the time but coref does not move because surface-name->id linking on ambiguous names is the
  bottleneck, N of M -- a distinct glass-box entity-linking organ").

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-file the WordNet C5+C6 type-license -- MEASURED net-negative on common-noun-to-common-noun (0.4879 -> 0.4683,
  twin indistinguishable). THIS problem is the proper-NAME bridge WordNet CANNOT reach -- a different KB, a different slice.
- Do NOT rebuild the typed-spoke store or its consolidation gate -- `hdlab/typed_spokes.py` + the gate are landed. ADD an
  entity-type spoke keyed like C5/C6 (directed, gate-admitted); REUSE `--build` to freeze it offline.
- Do NOT build a RUNTIME entity-linker that calls an external service -- the KB is a static pinned file; surface name->id
  linking is glass-box (exact / alias match, ambiguity abstains).
- Do NOT re-derive the candidate-quality lever (the SIBLING brief -- salience ranking of common-noun candidates); this brief
  supplies REACH (proper-name types), not the ranking fix.
- Do NOT use a 19c corpus as load-bearing gold; do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "entity"` /
  `"typed"` / `"spoke"` / `"wikidata"` / `"instance"` / `"namebridge"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm the C5/C6/C7 typed
  spokes are landed and the type-license read path exists; skim `hdlab/typed_spokes.py` so you EXTEND it (a new spoke), not
  build beside it.
- READ IN FULL (build ON them, credit them):
  `notes/problems/form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref/SOLVED.md` (the name-bridge
  slice + the WordNet type-license regression) and
  `notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md` (the
  C5/C6/C7 gate + the DIRECTED-spoke store-organization principle + the offline `--build` path) -- and
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` ATL hub-and-spoke entry. Note the STAGED `seed_the_entity_world_model_resolver...` in
  `notes/INTEGRATION_LEDGER.md` so you build ON it.
- INSPECT what you REUSE: `hdlab/typed_spokes.py` (C5 `close_isa` / `gate_isa_edges` / the is-a-license read; C6 build; the
  hub keying + the `--build` freeze path); `hdlab/situation_reader.py` `commonnoun_type_license` wire (where a licensing
  filter plugs into the pick -- MEASURED-OFF for WordNet); `hdlab/commonnoun_binder.py` + `hdlab/unified_referent.py` (the
  resolver the license feeds).
- ENUMERATE (an absence claim requires an enumeration, not a search): on a sample of GUM common-noun anaphors whose gold
  antecedent is a PROPER NAME, count how many the KB can type (name resolved to a P31 type compatible with the anaphor head)
  vs how many fail, splitting "name not in KB" from "name in KB but not linkable" from "typed but mis-ranked". State how you
  enumerated in your submission.
- GOLD + KB: modern GUM coref is on disk (`data/corpora/gum/`). You are PRE-AUTHORIZED to acquire the entity-type KB: put
  Wikidata P31 (or DBpedia InstanceOf) under `data/corpora/<name>/` (`data/` is gitignored -> write a REPRODUCIBLE,
  VERSION-PINNED fetch script in `experiments/` + a provenance note: source URL, dump date, license). Prefer a truthy P31
  subset (person / place / org / creative-work types) sized for coref. Do NOT lean on 19c.

## 7. THE BAR
PASSES only with ALL of:
1. **A curated, pinned, OFFLINE entity-type KB acquired under `data/corpora/<name>/` (reproducible fetch script +
   provenance) AND a DIRECTED TYPE-2 entity-type SPOKE built on the ATL hub, extending `hdlab/typed_spokes.py`** (keyed like
   C5/C6, admitted through the consolidation gate, frozen via `--build`; built + validated in `experiments/`, strategy lands
   the hdlab change, Q111). COPY the directed instance-of computation (proper-name -> type edge); SWEEP the KB choice, the
   type granularity, the gate margin, the licensing threshold. NO external LLM / linker at inference (static file + glass-box
   surface linking).
2. **The spoke used as a bounded TYPE-LICENSE (recency selects, the spoke only licenses) lifts NAME-BRIDGE (common-noun ->
   proper-name) coref CI-separated over the STRONGEST floor recomputed on the SAME population** (string-identity AND the
   WordNet-only resolver -- name-bridge is 0.000 for string-identity, so ALSO report the whole-common-noun-coref number so the
   slice's contribution is visible). Report CI half-width + null p95; recompute each floor on the item's OWN population; NO
   number crosses populations.
3. **The info-free twin LOSES CI-separated:** SHUFFLE the KB (permute the name->type map / assign each name a random other
   type, keeping shape + coverage) -- the gain must come from the REAL types, not from "any type-token helps".
4. **NO coref-dim regress + directed-store no-regress.** Enumerate every consumer of the typed spokes + the resolver clusters
   and confirm none regress (the WordNet C5/C6 reads, the common-noun / pronoun coref dims). A can-fail POSITIVE control
   NEITHER string-identity NOR WordNet can pass: "the painter" ... "Zurbaran" resolved via the KB type.
5. **NO-regress full-stack (FULL-STACK UPSTREAM).** Prototype THIS spoke AND its upstream (surface name -> KB entity-id
   linking; the gate admission) all the way to EXCEL/EXCEED; then CONFIRM no other consumer regresses and note which should
   be REVISITED to exploit encyclopedic types (relational reference, affect experiencers, the meaning channel). The reader
   stays byte-identical where the spoke / license is off.
6. **One-screen summary:** KB + provenance + version -> spoke design + gate -> string-identity / WordNet floor -> twin ->
   name-bridge + whole-common-noun-coref margin (CI half-width + null p95) -> upstream-linking no-regress -> what breaks ->
   verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the KB types the antecedent name X% but coref does not move because surface-name->id
linking on ambiguous names is the bottleneck, N of M -- a distinct glass-box entity-linking organ"; OR "name-bridge coref
lifts CI-sep but only Y% of GUM anaphors are name-bridge so the whole-dim move is bounded at +Z, enumerated -- the residual is
the common-noun candidate-quality problem, the sibling brief").

## 8. FILES AND ENTRY POINTS
- **REUSE / EXTEND (landed -- do NOT rebuild):** `hdlab/typed_spokes.py` (add the entity-type spoke keyed like C5/C6,
  directed, gate-admitted, `--build`-frozen); `hdlab/commonnoun_binder.py` + `hdlab/unified_referent.py` (the resolver the
  license feeds); `hdlab/situation_reader.py` `commonnoun_type_license` wire (the licensing plug-in point).
- **CONSUME (do NOT re-derive):** `notes/INTEGRATION_LEDGER.md` (the ~0.541 no-LLM blind-head ceiling / ~81%-world-knowledge;
  the STAGED `seed_the_entity_world_model_resolver...`); the `form_a_discourse_referent...` SOLVED (the name-bridge slice).
- **Gold + KB:** modern GUM coref (`data/corpora/gum/`); the acquired Wikidata P31 / DBpedia InstanceOf under
  `data/corpora/<name>/` with a pinned fetch script in `experiments/`.
- **Motivation + fence:** the two SOLVED.md files + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` ATL hub-and-spoke entry. Build in
  `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy -> REMOTE
  (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (an
  entity-type spoke for proper-name types now extends the ATL typed-spoke store; name-bridge coref reachable / located
  negative on surface-linking).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the WordNet type-license regression (0.4879 -> 0.4683) as evidence THIS fails -- that was
  common-noun-to-common-noun over WordNet; this is the proper-name bridge over an entity KB, a different slice and resource.
- Do NOT quote the ~0.541 blind-head ceiling across populations -- recompute floors on your own population; NO number crosses
  scorers / populations.
- Do NOT build a runtime external entity-linker or use an external LLM at inference (the invariant); do NOT re-file the
  common-noun candidate-quality lever (the sibling brief); do NOT lean on 19c gold (BANNED 2026-09-06). Strategy owns any
  hdlab landing (Q111).

---

**TLDR (plain English):** Our reader can't link "the artist" back to the name "Zurbaran" because the dictionary it checks
"is-a" against contains ordinary words but not people's names -- so about one in ten common-noun references, the kind that
point back to a name, are simply unreachable. The fix is to go get an open, offline list of "this named thing is an instance
of this type" (the kind of fact Wikipedia/Wikidata records), fold it into the reader's typed-knowledge store as a new kind
of fact, and use it only to allow a link (recency still picks which name), then prove it recovers name-to-word references
that were impossible before -- with a scrambled list falling apart so we know the real facts carry the load. The list is a
static file built once, offline; no outside AI is consulted while reading.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the C5/C6/C7 typed spokes are landed and proper names are the
hole), reads the two SOLVEDs in full, acquires a pinned Wikidata P31 / DBpedia InstanceOf subset under `data/corpora/` with a
reproducible fetch script, builds a directed entity-type spoke through the existing consolidation gate, enumerates on GUM how
many proper-name antecedents the KB can type vs link vs rank, and reports the name-bridge + whole-common-noun-coref margin over
string-identity / WordNet with the shuffled-KB twin and no coref-dim regress -- or a located negative naming the residual
(most likely glass-box surface-name->id linking on ambiguous names).
