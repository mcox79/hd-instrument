---
priority: 6
review:
review_text:
---

# PROBLEM: the reader still cannot answer "WHERE is each thing?" over a story. The situation model's SPACE dimension (Zwaan & Radvansky) is UNWIRED end-to-end: the tracking CORE is built and promoted (`hdlab/location_register.py` — per-entity presence intervals, `where_is(entity,t)` / `present_in_scene(entity,t)`), and a motion-event extraction adapter exists (`experiments/location_register.py`), but NOTHING drives the tracker from the live reader on general narrative, and the QA capstone HARD-ABSTAINS on "where" questions. Unlike causation and time (which had validated end-to-end reader paths and are now landed), SPACE has never been measured end-to-end through `SituationReader.read()` on real prose — the tracker was validated on abstract motion events, not on the reader's OWN extraction. Build + validate the SPACE dimension end-to-end: extract motion/location events from the reader's parse, feed the tracker, expose `sm.locations` (or where-is answers), and PROVE it answers "where is X at time T" on real narrative CI-separated over the floors — so the reader gains the missing WHERE dimension, the same additive default-off way causation and time landed.

**slug:** `the_reader_has_no_spatial_location_dimension_end_to_end` — **opened:** 2026-08-31 by the strategy session
(the assembly survey: SPACE was the one promoted dimension with NO validated end-to-end reader path; the copular/
nominal + tense extraction wins + the incremental parser make the motion adapter feasible now). **status:** OPEN —
a WIRE + END-TO-END VALIDATION problem (the tracking organ is built; this drives it from the reader on real prose
and measures it). You build + validate in `experiments/`; strategy lands the hdlab wire (Q111, default-off flag,
the causation/time landing pattern). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6`. A genuine missing comprehension dimension
> (the reader has WHO/WHAT/WHEN/WHY but not WHERE), additive and North-Star-aligned (a more complete situation
> model). Ranked below the endgame (learner-on p1, parser p2, full-system end-to-end p4) because those are the
> critical path, but it is the clearest ready NEW dimension — the extraction improvements (copular/nominal + tense,
> just integrated) and the incremental parser (p2) directly raise the motion-event adapter's quality. **Re-rank per
> the owner.** ⚠️ Compose with the reader's flags ON (see `python tools/reader_capabilities.py`); measure against the
> correct reader state, not the artificially-weak default.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When you read a story you keep a rough map of where everyone is — who's in the kitchen, who just went outside, who
came back. Our reader doesn't. We built the "map keeper" (it can hold where each character is over time and answer
"where is Mary now?"), but nothing actually feeds it from reading real prose, so the reader can't answer "where"
questions at all. Wire the map keeper up: pull the moves ("went upstairs", "came into the room", "left the house")
out of the reading, keep each character's location updated, and prove — on real stories — that it can answer "where
is X at this point" better than the obvious dumb baselines. If it can't be done reliably from the current reading,
say exactly why (that points at the extraction/parser work).

## 2. WHY THIS ONE
It is a whole comprehension dimension the reader is missing (it has who/what/when/why but not where), and it is the
next clean ADDITIVE assembly dimension. The pieces are now in place: the tracker is built and promoted, and the
recent extraction wins (catching non-verb events, keeping tense) plus the incremental parser sharpen the motion-
event extraction the tracker needs. Landing it the same additive, default-off way as causation and time grows the
situation model without risk to the existing reader.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** the situation model tracks per-entity LOCATION as STATE, updated ONLY by MOTION events and
  PERSISTING between updates (Zwaan & Radvansky 1998 event-indexing SPACE; hippocampal place / entorhinal grid
  allocentric map; parahippocampal place area — Speer & Zacks 2009). Narrative space is CATEGORICAL/topological, not
  metric (Rinck 1997) — scene nodes, containment, deixis-relative. Motion reading is Source-Path-Goal with GOAL
  dominant (Talmy; the tracker + adapter already encode this).
- **OUR-INVENTION (sweep):** the motion/location-event EXTRACTION from the parse (which verbs/prepositions move an
  entity to which node; deixis resolution; the VerbNet Destination-vs-Recipient + place-typing gates — already in
  the adapter), and the where-is read-out format. Glass-box, no LLM.

## 4. MEASURED vs INFERRED
- **MEASURED:** `hdlab/location_register.py` (the tracking CORE) is promoted + validated on ABSTRACT motion events
  (where_is / present_in_scene / region-containment). The motion-event extraction adapter exists in
  `experiments/location_register.py`. But there is NO end-to-end measurement through `SituationReader.read()` on real
  prose (the reader has no `sm.locations`; the QA capstone hard-abstains on "where").
- **INFERRED (you must measure):** whether driving the tracker from the reader's OWN motion-event extraction answers
  "where is X at time T" on REAL narrative CI-separated over the floors — WITHOUT it, the SPACE dimension is unwired.

## 5. ALREADY TRIED / DO NOT RE-RUN
- `situation_model_has_no_spatial_location_dimension` (integrated; promoted `location_register`) — the tracking CORE
  + the abstract-motion-event validation are DONE. Do NOT rebuild the tracker; this is the END-TO-END wire + validate
  on the reader's own extraction (the gap that integration left, coupled to the assembly).
- The perceptual-access / belief work consumes location; do not re-derive it.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/location_register.py` (the tracking core: `where_is`/`present_in_scene`/`spatial_region`) and
  `experiments/location_register.py` (the motion-event extraction adapter + its deps). Read how causation + time
  landed (`hdlab/situation_reader.py` `causation_typed` / `timeline_register` flags + `hdlab/causation_typing.py`) —
  the additive default-off pattern to follow. Run `python tools/reader_capabilities.py`.
- Pick a where-is gold: LitBank has coref+entities; a small hand-adjudicated where-is set on real passages is fine
  (report n honestly). MIND THE CORPUS-AGE CONFOUND (prefer a modern held-out set too if reachable).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On REAL narrative (LitBank + a small where-is gold; add modern if reachable), through `SituationReader.read()`:
- **PASS =** driving `location_register` from the reader's OWN motion-event extraction answers "where is X at time T"
  (and/or present-in-scene) CI-separated over BOTH floors — (a) the current reader (no location output = 0/abstain)
  and (b) a parse-free positional/last-mention-location baseline — with the info-free twin (shuffle the motion
  events / random node assignment) LOSING CI-separated, and a DISTANCE curve (accuracy vs #intervening events) as
  the graded brain signature. Report the extraction quality (motion-event recall/precision) as an honest bound + CI
  half-width + null p95. Default-off, additive (`sm.locations`), byte-identical when off.
- **A rigorous NEGATIVE is a full PASS:** if the reader's motion-event extraction is too weak to drive the tracker on
  real prose (where-is not beaten CI-separated), name why — enumerated (which motion constructions fail) — which
  points the SPACE dimension at the extraction/parser work (p2 / the extraction extensions) and tells the assembly
  SPACE waits on a stronger front-end.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/` (compose the motion-event adapter → `hdlab.location_register` → a where-is read-out driven
  by `SituationReader.read()`). Witness recomputes where-is accuracy + floors + twin + the distance curve from source
  through the live reader. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it clears the bar,
  strategy lands the hdlab wire (Q111): a default-off `track_space` flag on `SituationReader` → `sm.locations`,
  following the causation/time additive-landing pattern. This is the SPACE dimension of the assembly.


## DO NOT QUOTE / DO NOT REDO
- 🚫 No end-to-end result yet — OPEN. Do NOT quote the tracker's ABSTRACT-motion-event validation as an end-to-end SPACE number (it was validated on abstract events, not the reader's own extraction). Recompute where-is accuracy through the live `read()` on real prose.
