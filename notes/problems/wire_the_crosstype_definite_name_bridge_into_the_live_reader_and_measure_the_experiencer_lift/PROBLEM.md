---
slug: wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift
status: INTEGRATED
review: EXCELLENT
review_text: Reverified 6/6 first-hand. PARTIAL/located-negative -- the bridge SURVIVES the real consumer chain on the HONEST floor (+0.0528 experiencer CI-sep, twin loses, full reader.read() no-regress) but the literal wire yields no live BOARD gain because an UPSTREAM component -- the entity gate's GOLD-COREF INHERITANCE -- is a leak (owner ruled it a leak; filed as replace_the_entity_gate...). Full inventory tracked.
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-09-08 as PARTIAL/located-negative; live wire gated on the de-leak problem)
> Reverified FIRST-HAND **6/6** (`verification/test_crosstype_live_wire.py`): W1 deterministic known-answer through the REAL canonicalizer; W2 deployable conf_thr=-3.0 C3 experiencer 0.1548 -> 0.2077 (**+0.0528 CI[+0.0316,+0.0782] CI-sep**), twin LOSES (+0.0601 CI-sep, n=549); W3 no-regress (C1 up-or-flat, C2 +0.0071 CI-sep); W4 the gold-coref LEAK (real gate C3 gold-seed 0.828 vs honest-seed 0.134); W5 the cue_competed/cue_conf dial; W6 FULL `reader.read()` downstream no-regress (pronoun coref_acc byte-identical).
> **What makes it excellent:** it followed the disk over the brief. Wired the bridge through the reader's ACTUAL consumer chain (`_build_entities` -> `make_canonicalizer` -> `affect_register.bind_experiencers`), found the mechanism SURVIVES on the honest floor (+0.0528), then LOCATED why the literal wire moves no board dim: the gate silently reuses GOLD coref labels (~0.80-0.86 looks solved; strip it -> ~0.13-0.15). Escalated the "is gold-coref a legitimate given or a leak?" judgment call — I ruled **leak**.
> **What did not reproduce under my check:** nothing — 6/6 held.
> **FULL FIX/PROTOTYPE/UPSTREAM INVENTORY tracked (ledger CONT-26):** (1) the crosstype bridge SURVIVES the real consumer on the honest floor (+0.0528, twin loses, no-regress) — but stays LATENT (the live board gain is gated); (2) **UPSTREAM #1 (the blocker) = the entity gate's GOLD-COREF INHERITANCE — non-brain-foundational leak** -> filed `replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering`; (3) UPSTREAM #2 = the live parser/labeler (bridge precision 0.42-0.61 live vs 0.86-0.96 gold, near-ceiling, second-order); (4) LOCATED NEGATIVE: the Wikidata OCCUPATION KB is the wrong world-knowledge axis for this (people re-mentioned by relation/role/age-gender, not occupation) — reconciled with the coarse-person-typing route (a real distinct type constraint) -> `world_knowledge_common_noun_to_name_bridge`; (5) the cue_competed vs cue_conf conf-threshold dial (SAT operating point); (6) the ~81% world-knowledge residual = the honest name-bridge gap.
> **AUDIT UPDATE folded (§2b):** the entity gate's gold-coref inheritance is a live non-brain-foundational LEAK that masks every coref/name-bridge/experiencer gain; the crosstype bridge is brain-foundational + survives the honest floor. **status:INTEGRATED, priority 3 dropped.** **Realization (tracked): the two-part live wire (opt-in bridge + de-leak) lands once `replace_the_entity_gate...` is solved.**

# PROBLEM: `hdlab/crosstype_bridge.py` is landed and parity-exact but LATENT (no live consumer reads it) -- so wire it into the reader's DEFAULT common-noun gate behind an opt-in flag (byte-identical off), feeding it the reader's OWN parsed tokens, and prove the affect/goal EXPERIENCER consumer lifts CI-separated on modern GUM THROUGH THE LIVE READER (not the offline harness), with the info-free twin LOSING and no entity-layer/hard-link regress -- then flip per no-more-default-off.

**slug:** `wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift` -- **opened:** 2026-09-07
by the strategy session. The cross-type definite->name bridge (a person role-noun "the doctor" binds to a prior NAMED
person, Elizabeth, by an in-text descriptive condition) was proven net-positive in the `route_the_unified_referent`
solution and PROMOTED to `hdlab/crosstype_bridge.py` (committable, parity-exact vs the reference). It is the "landed != live"
twin: the algorithm is version-controlled but nothing in the live read path calls it, so the measured +0.0528..+0.086
experiencer gain is not realized in any board number. This is a WIRING + LIVE-MEASUREMENT problem, REUSE of a landed organ.

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
When a story says "Elizabeth was a doctor ... the doctor smiled", a reader files the smile under Elizabeth. We built
exactly that -- a glass-box bridge that, given the sentence's grammar, links "the doctor" to the named person the text
predicated the role to, and only commits when a memory match is strong (else treats it as someone new). It measurably
helps "attach a feeling to the right character" -- about 5-9 more right in 100 -- and a scrambled version can't fake it.
But right now the reader never calls it: the tool sits in a drawer. This problem is to plug it into the live reading
pipeline, feed it the reader's own sentence parse, confirm the improvement survives end-to-end, and turn it on.

## 2. WHY THIS ONE
It cashes an ALREADY-PROVEN, already-committed win with no new research risk: the mechanism is validated (survives the
live parser at 0.86 precision; lifts the experiencer consumer +0.0528..+0.086 CI-separated; twin loses) and the organ
is parity-exact. The only thing between us and a live board gain is the wire + a live-reader measurement. It is the
single most-ready realization on the queue, and it exercises the exact "landed != live" discipline the substrate keeps
tripping on. Brain-foundationally it is the affect/goal EXPERIENCER binding getting its correct antecedent -- a real
comprehension gain, not a metric artifact.

## 3. HOW THE BRAIN DOES THIS
PINNED. A definite description is a LOW-accessibility referring expression (Ariel 1990) retrieved by DESCRIPTIVE CONTENT
(Almor 1999) + recency, via cue-based content-addressable retrieval over the discourse-entity file cards (Lewis-Vasishth
ACT-R; Heim/Kamp file-change). Commitment is gated by retrieval CONFIDENCE (Heim familiarity = a matching referent is
retrievable; McElree speed-accuracy = low activation means NO referent found -> treat as novel). ALL discourse referents
compete (DRT), so a cross-type name bind fires only when the name out-competes the same-head common referent. The organ
`hdlab/crosstype_bridge.py` already implements every one of these operations; this problem is about delivering its output
to the live entity clustering the affect/goal consumers read.

## 4. MEASURED vs INFERRED
- **MEASURED (reverified first-hand 29/29 + parity-exact):** offline on GUM (275 docs, live-parse path) the bridge lifts
  the affect/goal experiencer C3 +0.0328 (base) -> +0.0510 (graded competition) -> +0.0528 (gated cue_conf, conservative)
  -> +0.086 (full-referent competition, liberal), all CI-separated; the info-free shuffled-target twin loses CI-sep;
  live-parse survival 0.86 precision / 0.12 coverage; the entity-KB hard-link is up-or-flat; the organ reproduces the
  reference binds EXACTLY (0/600 calls across 5 conf thresholds).
- **INFERRED (this problem must MEASURE, not assume):** that the SAME lift appears THROUGH THE LIVE READER on `sm.entities`
  (the offline harness applied binds to a floor clustering directly; the live path routes them through
  `_apply_commonnoun_gate` -> `goal_register.make_canonicalizer` -> `affect_register.bind_experiencers`). The conservative
  vs liberal operating point (`conf_thr`) must be tuned ON THE LIVE PARSE and the no-regress on the entity-layer CoNLL (C1)
  + hard-link (C2) re-confirmed live.

## 5. ALREADY TRIED / DO NOT RE-RUN (the disk outranks this brief)
- **Routing the unified referent to these consumers: REFUTED** (flat-to-negative on modern GUM; the `route_the_unified_referent`
  SOLVED). Do NOT resurrect the unified-referent route; keep `hdlab/unified_referent.py` default-off.
- **A Wikidata occupation KB (P106/P39): MEASURED located negative** (+0.000 -- definites re-mention by age/gender/relation/
  context, not catalogued occupation, 1/16 match). Do NOT re-acquire it for this.
- **Force-binding without the anaphoricity/competition gate: net-NEGATIVE** (floods wrong merges, precision 0.32). The gate
  is load-bearing; it is already in the organ.
- The ungated cue-retrieval REGRESSES the entity-layer CoNLL (C1 -0.0058); the full-referent competition + confidence gate
  is what makes it safe. Use `bind_mode="cue_conf"` / `cue_competed`, NOT the ungated modes.

## 6. VERIFY BEFORE YOU START
1. Understand the organs: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/crosstype_bridge.py`
   (the organ, with its module docstring + `_self_test`), `hdlab/situation_reader.py::_apply_commonnoun_gate` (the default gate,
   ~L3797-3841), `hdlab/goal_register.py::make_canonicalizer` + `hdlab/affect_register.py::bind_experiencers` (the live consumers).
2. Read IN FULL the SOLVED it came from: `notes/problems/route_the_unified_referent_to_its_non_coref_consumers_where_it_helps/SOLVED.md`
   (+ its OWNER_NOTES.md) -- the two-part result, the deployable config, the fidelity scan, the located negatives.
3. Confirm on disk: `hdlab/crosstype_bridge.py` self-test passes (`python -m hdlab.crosstype_bridge`); the reference witnesses
   still pass (`verification/test_crosstype_landable.py`, `..._upgrades.py`, `..._chain.py`). The organ is `gum_coref.Doc`-schema
   typed -- the live wire needs a Doc adapter from the reader's OWN parsed tokens (gidx/sent/idx/head/deprel/upos), NOT a second parse.

## 7. THE BAR
PASSES only with ALL of:
1. `hdlab/crosstype_bridge.py` wired into the reader's DEFAULT `_apply_commonnoun_gate` path behind a NEW opt-in flag
   (`crosstype_bridge`, default False), byte-identical when off (import + call inside `if self.crosstype_bridge:`), fed the
   reader's own parsed tokens via a Doc adapter (no second parse). NOT wired into the dormant `entity_kb_resolver` branch (that
   keeps it latent). Strategy owns the hdlab edit (Q111) -- the solver builds + measures the wire in `experiments/` and proposes it.
2. Through the LIVE reader, the affect/goal EXPERIENCER consumer beats its CURRENT live input CI-separated on MODERN gold (GUM),
   at a `conf_thr` tuned on the live parse; report the delta + doc-level paired-bootstrap CI.
3. The info-free shuffled-target TWIN LOSES CI-separated on the experiencer, live.
4. NO regress: the entity-layer CoNLL (C1) and the entity-KB hard-link (C2) are up-or-flat live; other reader consumers no-regress.
5. Per no-more-default-off: if net-positive live, propose the flip ON (with the tuned `conf_thr`); if a measured reason to hold, state it.
A rigorous NEGATIVE is a full pass (e.g. "the live-reader path introduces a coref-order difference that erases the offline lift, located and counted").

## 8. FILES AND ENTRY POINTS
- Organ: `hdlab/crosstype_bridge.py` (`crosstype_bridge_links(doc, gaz, *, conf_thr)` = the single entry; `gated_binds` bind_mode="cue_conf"/"cue_competed").
- Wire target: `hdlab/situation_reader.py::_apply_commonnoun_gate` (default-on path); flag alongside the `unified_referent`/`entity_kb_resolver` block (~L935-939).
- Live consumers: `hdlab/goal_register.py::make_canonicalizer`, `hdlab/affect_register.py::bind_experiencers`.
- Offline reference + measurement path (REUSE the scorer): `experiments/exp_crosstype_landable_validation_gum_v1.py` (live-parse + twin + C3), `experiments/exp_crosstype_upgrades_gum_v1.py::compare_conf` (the conf_thr sweep), `experiments/exp_route_unified_to_consumers_gum_v1.py::score_c3_experiencer` (the consumer scorer).
- Corpus: `data/corpora/gum/` (GUM V12.1.0, on disk). Gazetteer: `data/lexicons/name_gender_gazetteer.tsv`.

## DO NOT QUOTE / DO NOT REDO
- The offline +0.0528/+0.086 numbers are the OFFLINE-HARNESS lift (binds applied to a floor clustering) -- do NOT quote them as
  the live board number until re-measured through the live reader; that re-measurement IS this problem.
- Do NOT quote the unified-referent route as a lever (refuted) or the occupation KB as a follow-on (located negative).
- Do NOT run a second parse in the reader -- feed the bridge the reader's already-parsed tokens (the standing parser cost is reader-wide, not this organ's to double).

**TLDR (plain English):** We built a good tool for figuring out that "the doctor" is Elizabeth, proved it helps attach
feelings to the right character, and put it in the toolbox -- but the reader never reaches for it. This job is to plug it
in, feed it the reader's own sentence analysis, check the improvement still shows up when the whole reader runs (not just in
the lab bench), and switch it on if it does. Low research risk, real payoff, and it enforces the rule that a built thing
isn't a live thing until the pipeline actually uses it.

**QUESTIONS:** none blocking. One judgement call for the owner at flip time: the confidence threshold is a
conservative..liberal dial (safer entity layer vs bigger experiencer gain); the solver reports the curve, the owner/strategy picks the operating point.

**NEXT STEPS:** run VERIFY BEFORE YOU START; build the Doc adapter + the opt-in wire in `experiments/`; measure the live
experiencer lift + twin + no-regress; sweep `conf_thr` on the live parse; propose the flip. Strategy lands the hdlab edit and,
if net-positive, flips it on and adds a board arm.
