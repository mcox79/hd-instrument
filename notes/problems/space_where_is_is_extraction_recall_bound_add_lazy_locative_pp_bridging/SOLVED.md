---
problem: space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging
status: PARTIAL
bar: "PASS = where_is on the MODERN space gold CI-separated over BOTH the current motion-lexicon chain AND the strongest stateless floor (last-mention), with the info-free shuffled-place twin LOSING, motion-event recall materially recovered, and NO precision regression — landed through the LIVE reader (not just the prototype harness). A rigorous located NEGATIVE (the brain's on-demand locative bridging, faithfully built, does not hold end-to-end, with the exact stage that eats the gain named) is a FULL PASS. Report the recall + where_is deltas with CIs + the twin."
result: "where_is exact-node, GP._score-style, paired bootstrap. (1) BRIEF REFUTED: the lazy locative-PP bridge lifts motion-event extraction recall 0.444->0.889 but moves end where_is only +0.064 (modern, n=47, item CI [-0.021,+0.149], NOT CI-separated over the current chain). (2) REAL LEVER = NAMED-GROUND BINDING (a brain-foundational Ground extractor: verb-frame Goal gate + Figure-Ground compound-head + partitive + functional-locus typing): where_is MODERN 0.319->0.468 (+0.149, n=47) and REAL 19c LitBank 0.244->0.320 (+0.076, n=606, 24 timelines); beats the last-mention floor CI-separated on both; the shuffled-ground twin LOSES CI-separated on both (modern 0.468 vs 0.213; 19c 0.320 vs 0.213); precision IMPROVES on both (modern 0.571->0.696; 19c 0.163->0.215); through the LIVE SituationReader.read() stock 0.277->wired 0.447 (+0.170, 9 named grounds recovered). Gain over the CURRENT chain: item CI touches zero (modern [+0.000,+0.298]; 19c timeline [-0.034,+0.193] but 19c item-level separated) -> NOT cleared at the conservative unit. (3) UPSTREAM localized: a perfect ground node on already-fired events is worth +0.107 where_is (0.468->0.575), MORE than the downstream binder -- the shared role router's Ground selection is the biggest single lever; ground-extraction accuracy 0.692->0.731 with the fixes."
floor: "last-mention (strongest stateless): 0.1489 modern (n=47) / 0.0132 19c (n=606). Named-ground binding beats it CI-separated on both. Perfect-extraction CEILING (gold events folded) = 0.7872 modern -- the register/readout headroom the extraction front-end must reach."
controls: "shuffled-ground info-free twin (same firing rate, ground nodes permuted) LOSES CI-separated on both corpora (the ground CONTENT is load-bearing). Perfect-extraction ceiling (0.787) isolates the register/readout as not-the-bottleneck. Precision guardrail: motion-event precision IMPROVES on both (no gain bought with false firing). ADDITIVE-SAFETY (no other consumer regresses): the who-did-what events are BYTE-IDENTICAL with vs without the wire -- extract_events_in_substrate is called ONLY by _read_space (verified). Can-fail negatives: (a) the AGGRESSIVE binder (locative/stative PPs + protagonist fallback) REGRESSES on real 19c prose (-0.05..-0.08) -> only the high-precision motion-goal subset is robust; (b) ANTICIPATORY Goal binding (Altmann-Kamide) over-fires and HURTS both corpora (modern -0.021, 19c -0.059) -> agrees with Ferretti 2001 (verbs do not prime Locations as they prime Agents)."
files_changed: "experiments/exp_space_recall_e2e_ci_v1.py, experiments/exp_space_named_ground_binding_v1.py, experiments/exp_space_ground_binding_litbank_v1.py, experiments/exp_space_ground_binding_live_wire_v1.py, experiments/exp_route_ground_v2.py, experiments/_diagnose_where_is_errors.py, experiments/_localize_upstream_ground_lever.py, verification/test_space_ground_binding.py, notes/research_spatial_ground_role_assignment_2026-09-05.md (NO hdlab/ written)"
reverify: ".venv/Scripts/python.exe verification/test_space_ground_binding.py"
---

# Space where_is: the brief's premise is refuted; the real lever is NAMED-GROUND BINDING, and the biggest sub-lever is the UPSTREAM role router

**Bottom line.** The brief said the SPACE where_is loss is motion-event **extraction recall** (fix: a lazy
locative-PP bridge). **The disk refutes it:** recovering that recall (0.444->0.889) moves where_is only +0.064. I
located the real bottleneck — **binding the correct NAMED GROUND to an already-detected motion event** — built the
brain-foundational mechanism for it, took it **all the way upstream to the shared role router** (which the
localization proves is the single biggest lever), confirmed **no other consumer regresses**, and confirmed each
upstream choice against the neuroscience/psycholinguistics. The robust result improves where_is on both a modern
and a real 19c corpus, at higher precision, holds through the live reader, and beats the floor and shuffled-ground
twin CI-separated. It does **not** CI-separate over the (already decent) current chain at the honest unit, so this
is **PARTIAL** — a real, validated, brain-foundational gain plus a first-class refutation and a named wall.

## 1. The refutation (`exp_space_recall_e2e_ci_v1.py`)
The LIVE reader runs `mode="prior_ext"` — the stative-locative gate, result/telic verbs and caused-motion routing
the brief's research proposed as "new gates" are **already built and live**. The only new piece the brief adds is
the locative-PP bridge, which lifts extraction recall a lot but moves end where_is only +0.064 (item CI
[-0.021,+0.149], not separated over the current chain). **Recovering change-point DETECTION does not recover
where_is.**

## 2. Where the signal actually goes (`_diagnose_where_is_errors.py`) — the reframe
Decomposing every where_is error against the perfect-extraction CEILING (0.787), with coref gold on the modern set:
**SCENE 34% (motion detected, entity present, but the NAMED place is never bound — `<scene>` not "office"),
WRONG_NODE 13%, SCORING_ARTIFACT 13% (ceiling also wrong), MISSING 2%.** ~49% of errors are named-ground binding
on already-detected motion, all recoverable per the ceiling. The bottleneck is **binding the Ground**, not
detecting the event.

## 3. The mechanism, all the way upstream (`exp_space_named_ground_binding_v1.py`, `_localize_upstream_ground_lever.py`)
**Brain frame (PINNED; `notes/research_spatial_ground_role_assignment_2026-09-05.md`):** a motion event updates the
model to its **Ground** — the reference place the Figure comes to be at (Talmy Figure/Ground; Landau & Jackendoff
1993 the "where" object; Rappaport Hovav & Levin 2008 argument structure). The Ground is bound by the verb's
argument-structure frame; a manner-of-motion verb is a **single-argument predicate** (the mover is the sole
argument, the path PP an adjunct — no theme to usurp the goal); a bare to/into PP is a spatial Goal only when the
verb's frame predicts a Goal slot (Altmann & Kamide 1999).

**The Ground extractor I built** (each choice research-backed): a verb-frame Goal gate (bind a goal only on a
genuine motion verb — the conservative subset); compound-noun **HEAD** selection ("meeting room"->room); a
**partitive** resolver ("the back **of** the hall"->hall); a curated **functional-locus** typer (desk/bed/seat/
plane/car/gate/ward — reference objects a person occupies that the WordNet location taxonomy misses); and dropping
the benefactive `for` from the spatial prepositions ("waited **for** the boarding call" is not a destination). It
binds the named Ground to the **mover directly**, sidestepping the role router's `goal_belongs_to` mislabel.

**The upstream localization (modern gold, the ladder the owner asked for):**

| where_is (modern, n=47) | value | lever |
|---|---|---|
| last-mention floor | 0.149 | |
| current chain | 0.319 | |
| + named-ground binding (ARM) | **0.468** | +0.149 (my mechanism) |
| + ORACLE ground node on fired events | **0.575** | **+0.107 — the UPSTREAM role-selection lever (biggest single)** |
| ceiling (perfect events) | 0.787 | +0.212 (firing/recall + over-fire residual) |

Ground-extraction accuracy per gold change-point rose 0.692->0.731. **The upstream Ground *selection* is worth more
than the downstream binder** — confirming the owner's thesis that the wall breaks only by making the shared
upstream brain-foundational.

**Two-corpus result (robust config; anticipatory OFF):**

| corpus | n | current | ARM | floor | twin | precision |
|---|---|---|---|---|---|---|
| MODERN (coref gold) | 47 | 0.319 | **0.468** (+0.149) | 0.149 | 0.213 | 0.571->0.696 |
| 19c LitBank (real) | 606 | 0.244 | **0.320** (+0.076) | 0.013 | 0.213 | 0.163->0.215 |

Beats the floor CI-separated on both; the shuffled-ground twin LOSES CI-separated on both; precision improves on
both. Over the current chain: modern item CI [+0.000,+0.298] (touches zero); 19c timeline CI not separated (item
level is). **Live reader (`exp_space_ground_binding_live_wire_v1.py`): stock 0.277 -> wired 0.447 (+0.170), 9 named
grounds recovered through the full `read()` pipeline** (room, desk, garage, balcony, ...).

## 4. The shared role router upstream (`exp_route_ground_v2.py`) — brain-foundational, but the label is not the lever
The research's two PINNED route-internal fixes: (1) **valency gate** — a strictly-intransitive self-motion verb has
no theme, so force `theme=None`; the goal falls to the agent by construction (fixes "she headed into the locker
room"). (2) **verb-frame Goal-slot gate** — a bare to/into goal only counts when the verb's frame predicts one.
Implemented as an additive post-process of the shipped `route_predicate_arguments` (agent untouched; theme changed
only where there is no theme; goal dropped only where the frame predicts none). **Measured effect on the live base
chain: modern +0.000, 19c +0.010** — brain-foundational and correct, but low-yield, because the dominant ground
error is token/node **selection** (which PP, which noun), not the `goal_belongs_to` label. This is the honest split:
the label fix is right but minor; the Ground-*selection* upgrade (Section 3) is the real upstream lever.

## 5. No other consumer regresses (verified)
The ground-binding emits ONLY `(entity, kind, node, t)` SPACE events into the LocationRegister. `extract_events_in_
substrate` is called **only** by `_read_space`, so it cannot touch any other role or dimension. Verified: the
who-did-what events are **byte-identical** with vs without the wire (witness W5). The role-router fixes (Section 4)
are additive (agent untouched; theme changed only for strictly-intransitive verbs, where a theme was always
spurious; goal dropped only off non-Goal-frame verbs).

## 6. THE PROPOSED hdlab/experiments DIFF (Q111 — strategy lands it)
1. Add `ground_bind_events(..., conservative=True)` (from `exp_space_named_ground_binding_v1.py`) into
   `experiments/_space_reader.py`; in `extract_events_in_substrate`, add a `ground_bind=False` kwarg that appends
   the conservative named-ground events (SAME parse provider); default it ON in `read_locations_in_substrate`'s
   `prior_ext` mode. Land the `conservative=True` path ONLY.
2. Fold the Ground-selection helpers (`_ground_node`/`_pp_ground` compound-head + partitive, `_FUNCLOC`, `for`
   removed from spatial preps) into the shared `hdlab/predicate_argument_frontend` place-typing/goal extraction so
   any Ground consumer benefits.
3. Optionally land the `route_v2` valency + verb-frame Goal gates (brain-foundational, low-yield, no-regress).
4. **Do NOT land:** the aggressive locative/stative + protagonist-fallback path (regresses real prose), or the
   anticipatory Goal fill (over-fires — Section 7).
Because coref/precision improve and no other dimension changes, recommend landing ON with witness
`verification/test_space_ground_binding.py`.

## 7. What I did NOT establish / would withdraw first
- **Withdraw first:** the modern +0.149 as a stand-alone claim — n=47, CI over the current chain touches zero. The
  robust claims are the 19c no-regression + net-positive, the floor/twin separations, the precision improvement,
  and the additive-safety.
- I did **not** clear the where_is-vs-current-chain CI bar at the honest (character-timeline) unit. The current
  chain is already decent (0.24-0.32 vs a 0.79 ceiling); my lever adds ~8-15 points, real but sub-threshold.
- **Anticipatory Goal binding is a located negative:** eager location anticipation over-fires (modern -0.021, 19c
  -0.059). This AGREES with the neuroscience (Ferretti, McRae & Hatherell 2001 — verbs prime Agents/Instruments but
  NOT typical Locations), so an eager anticipatory location-fill is not brain-faithful. Kept OFF.
- The residual gap to the ceiling (0.575->0.787 after a perfect ground node) is firing/recall + raw parse
  mis-attachment ("reached the office" -> goal on the comma) — an arc-eager attachment limit, not a Ground-role
  limit.

## 8. ADJACENT COMPONENTS — brain-foundational status + opportunities (seeds the next problems)
- **The arc-eager PARSE (all the way upstream):** the residual after a perfect ground node is partly raw goal-PP
  mis-attachment. Space recall is parse-*quality*-independent (prior work) but Ground-NODE binding is NOT — a
  goal PP attached to the wrong head drops the ground. **Opportunity:** a Ground-aware attachment probe; likely a
  parser problem already in flight — coordinate, do not duplicate.
- **`route_predicate_arguments` (shared role router):** its Ground/goal role is only ~0.73 accurate on the space
  gold; the compound-head + partitive + functional-locus typing I built should be folded in so the who-did-what
  and copular consumers get the better place typing too. Brain-status: the graded cue-integration is
  brain-foundational; the goal-token SELECTION was under-built.
- **The copular / entity_states reader (`_read_entity_states`):** reads "X is in the Y" locations with the OLD
  place typing (no functional loci) — a candidate to revisit with the new Ground typer.
- **`grounded_semantic_graph` ConceptNet AtLocation:** could replace the curated `_FUNCLOC` set with a broader
  glass-box place/at-location taxonomy (the brief's INFERRED reuse — untested; a follow-on).
- **Mover-coref (`EntityBinder`):** not the bottleneck on these gold-coref corpora, but the aggressive-variant
  regression shows binding to a wrong mover costs more than it buys on real (non-gold) coref — wire it before any
  aggressive binding.

## KEY REALIZATIONS
- **The diagnosis that names a metric is not the diagnosis that moves it.** "Extraction recall 0.44" was a
  change-point DETECTION number; where_is is a node-at-query-time number. The ceiling control (perfect events ->
  0.79, our chain -> 0.38 at 0.89 recall) forced the reframe: the loss is Ground BINDING.
- **The oracle-node ablation localized the biggest lever upstream.** Feeding a perfect ground node to the events we
  already fire was worth MORE (+0.107) than the whole downstream binder — that is the number that said "go
  upstream", exactly as the owner directed.
- **A win on constructed clean data can be a loss on real prose.** The aggressive binder gained +0.17 on my modern
  sentences and LOST on real 19c prose; only the high-precision subset generalized. The two-corpus test (one I
  authored, one I did not) caught it.
- **The neuroscience predicted my located negative.** Anticipatory Goal binding failed empirically AND the
  literature says the brain does not anticipate Locations the way it anticipates Agents — the mechanism and the
  measurement agreed, which is the strongest kind of negative.

## AUDIT UPDATE (for `BRAIN_FOUNDATIONAL_AUDIT.md`)
- SPACE extraction front-end (`_space_reader` / `route_predicate_arguments`): correct the verdict — **the where_is
  cap is NAMED-GROUND BINDING (Talmy Figure/Ground), not change-point recall** (ceiling 0.787 vs live 0.32-0.47).
  The shared role router's Ground/goal SELECTION (~0.73) is the single biggest lever. Deviation: Ground selection
  was under-built (no compound-head/partitive/functional-locus typing; `for` wrongly spatial). Anticipatory Goal
  binding is NOT brain-faithful for Locations (Ferretti 2001) — do not build it.

## TLDR (plain English)
The reader often knows a character moved but fails to record WHERE — it says "she's in the scene" instead of "in
the office." The brief guessed the problem was missing too many moves; I checked, and fixing that barely helped —
the real problem is attaching the specific PLACE. I built the fix (bind the named place a character ends up at),
grounded every design choice in how the brain assigns "where", and traced it all the way up to the shared component
that reads sentence roles — which turned out to be the biggest lever of all (getting the place right on moves we
already catch would help more than anything downstream). The fix helps on both modern and old text, never hurts,
gets more places right, improves precision, runs correctly inside the real reader, and provably changes nothing
about any other part of the reader. I also tested the brain's "expect a destination" trick (like "eat" makes you
expect food) — it backfired, and the neuroscience agrees the brain doesn't expect *places* that way, so I left it
out. It is a genuine, well-grounded improvement but a modest one: the reader was already fairly good here, so I'm
calling it a partial win and naming exactly what's left (getting the parser to attach place-phrases correctly).

## QUESTIONS
None.

## NEXT STEPS
1. **Land the conservative named-ground binding** (Section 6, `conservative=True` only) + fold the Ground-selection
   typing into the shared role router. Net-positive, precision-improving, holds live, no other consumer regresses.
2. **File the next problem: Ground-aware goal-PP ATTACHMENT** — the residual after a perfect ground node is raw
   parse mis-attachment; this is the last big lever to the 0.79 ceiling. Coordinate with in-flight parser work.
3. Revisit the copular/entity_states reader and `grounded_semantic_graph` AtLocation with the new Ground typer
   (adjacent brain-foundational opportunities, Section 8).
4. Do NOT land the aggressive binder or the anticipatory Goal fill (both located negatives).
5. Fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md`.
