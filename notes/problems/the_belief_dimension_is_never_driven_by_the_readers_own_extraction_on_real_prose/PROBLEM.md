---
priority:
review: EXCELLENT
review_text: "Reverified 19/19 first-hand. A rigorous REFUTE-AND-REBUILD: empirically refuted the brief's Sally-Anne object-move premise (0 objects with >=2 extracted moves / 8 LitBank books) AND showed it is the wrong brain mechanism (research drill: the mentalizing net holds a CONTENT-GENERAL, SOURCE-TAGGED propositional attitude fed by language about minds -- Koster-Hale/Saxe; object-move is a developmental DIAGNOSTIC, not the mechanism). Rebuilt: drove the PROMOTED belief_timeline from the reader's OWN 4-channel extraction (narrator-epistemic + testimony dominant + perception + inference). HEADLINE on an INDEPENDENT, POWERED, EXTERNAL benchmark (FANToM info-access ToM, Kim 2023, n=3572 judgments): reader 0.893 vs strongest floor 0.665 (+0.228 CI-sep), beats BOTH a shuffled-order twin (+0.138) and a random-presence twin (+0.337) CI-sep, false-belief says-ignorant 0.939 vs beliefless 0.000. LitBank narrative slice corroborates (knowledge-state +0.429 CI-sep, false-belief +0.600 CI-sep; exact-value slice honestly coverage-bounded -- a corpus property, FANToM supplies the powered population). Every extraction gap routed to a VETTED organ ONE AT A TIME (state_register for status, WordNet synonym+entailment for open-ended value, a 3-schema inference extractor) -- vetting caught TWO wrong picks (distributional_meaning_channel + conceptual_meaning REJECTED) before the right one. Dominant channels are substrate-native (belief carried with NO spaCy at inference); source-tagging 0.90; antonym-inflation control confirms no loosening; inference is evidence-gated (silent on unobserved premises). Honest bounds disclosed: location extraction is the shared parser-recall ceiling (routed to p2); narrative exact-value n is small (FANToM is the powered pop, a different genre -- dialogue not narrative -- but the mechanism is content-general and the narrative slice agrees). Brain-faithfulness is high (the drill CHANGED the design). WIRE: QUEUED (track_belief on SituationReader, the lazy-adapter track_space pattern) -- a substantial multi-channel assembly landing, its own focused effort; NOT faked."
---

# PROBLEM: the reader's BELIEF / Theory-of-Mind dimension has never been driven by the reader's OWN extraction on real prose. The pieces are built + PINNED-faithful and PROMOTED to hdlab — `belief_timeline.py` (per-agent belief as a PIECEWISE-CONSTANT sample-and-hold function of story-time — it JUMPS at an observed event and PERSISTS between), `belief_partition.py` (belief kept SEPARATE from reality, the FHRR banks), `perceptual_access_ledger.py` (the STICKY REGISTRATION LEDGER observation-cue front-end — "did A perceive/come to know E?"), and the landed `timeline_register` (event ORDER). But NOTHING composes them into the live reader, and the one end-to-end experiment (`exp_belief_timeline_live_e2e_v1`) scores its 0.902 on AUTHOR-CONSTRUCTED multi-event passages where the EVENTS are GOLD (anchored by sent_idx) and only the observation-BIT is extracted live (arms LIVE/ORACLE/FLOOR). So the belief timeline has NEVER been driven from the reader's OWN event extraction on natural narrative — exactly the gap the SPACE dimension just closed for WHERE. Drive `belief_timeline` from the reader's OWN event stream through `SituationReader.read()` → `timeline_register` (order) → `perceptual_access_ledger` (observation-gate) → per-agent belief, and PROVE on REAL narrative that it answers "what did agent A believe about fact F at time T" (and recovers FALSE beliefs) CI-separated over the floors with the info-free twin LOSING — or, if the reader's extraction is too weak to drive it, enumerate WHY (which, per SPACE, points at the parser-recall / forward-prediction ceiling). This is the WHO-BELIEVES-WHAT-WHEN dimension of the assembly, validated the same honest end-to-end way SPACE was.

**slug:** `the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose` — **opened:** 2026-08-31 by
the strategy session (ARCHITECT HEARTBEAT scan, BRAIN_FOUNDATIONAL_AUDIT §2b: belief_timeline + perceptual_access_ledger
are PINNED-faithful + promoted but a PURE ISLAND whose 0.902 rests on GOLD events + constructed passages — never driven
from the reader's own extraction). **status:** OPEN — a WIRE + END-TO-END VALIDATION problem (the organs are built +
promoted; this drives them from the reader's OWN parse+coref+events on REAL prose and measures it). You build + validate
in `experiments/`; strategy lands the hdlab wire (Q111, default-off flag, witness required). NO external LLM at inference.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5`. A genuine missing comprehension dimension (the
> reader tracks WHO/WHAT/WHEN/WHERE/WHY but not WHO-BELIEVES-WHAT-WHEN on real prose), additive and North-Star-aligned (a
> more complete situation model = a cleaner foundation). Ranked below the endgame (learner-on p1, prediction-error p2,
> full-system validation p4) because those are the critical path, but it is the clearest ready NEXT dimension after SPACE,
> and the SPACE template makes it tractable now (the extraction front-end — tense-agnostic keystone + copular/nominal +
> verb_subcat — is much stronger than when belief was first built). **Re-rank per the owner.** ⚠️ Compose with the
> reader's capable flags ON (`python tools/reader_capabilities.py`, incl. `timeline_register`); measure against the
> correct reader state, not the artificially-weak default. ⚠️ MIND the parser-recall ceiling SPACE hit — it likely
> bounds this too; a rigorous negative that localizes the ceiling is a full PASS.

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
When you read a story you keep track of what each character KNOWS — and that it can differ from the truth and from what
other characters know (Othello believes Desdemona is unfaithful; the reader knows she isn't). Our reader can't do this
on a real story. We BUILT the machinery — a per-character "belief board" that only updates when that character actually
witnesses something, and holds steady until they see the next thing — and it scored well, but only on hand-made toy
passages where we HANDED it the events. It has never read a real novel and worked out, from its own reading, who
believed what and when. Wire it to the reader's own understanding of each sentence and prove — on real stories — that it
answers "what did this character think was true at this point" better than the dumb baselines (just say the truth; just
say the last thing mentioned), and that it catches FALSE beliefs. If the reader can't extract the moves reliably enough
to drive it, say exactly why (that points back at the parser, same wall the where-is dimension hit).

## 2. WHY THIS ONE
It is the one situation-model dimension with organs BUILT + promoted but never tested end-to-end on real prose — a
who-believes-what tracker is core comprehension (false belief is the classic Theory-of-Mind test), and it is the natural
next dimension after WHERE. It is ALSO a foundation-cleanliness contribution: a per-agent belief is structured knowledge
the situation model should hold. The pieces are all in place (the belief board, the "did they see it?" ledger, the event
timeline) — what is missing is composing them from the reader's OWN reading and MEASURING it honestly, exactly the gap
the SPACE dimension just closed for WHERE (and its finding — the ceiling is parser recall — probably applies here too).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate the operation):** per-agent belief is kept SEPARATE from reality by the mentalizing network
  (TPJ/mPFC; Saxe & Kanwisher 2003). Belief updates ONLY on OBSERVED events ("seeing leads to knowing"; Wimmer & Perner
  1983) — a FALSE belief is one formed before an UNobserved change. Belief about a fact is a PIECEWISE-CONSTANT
  sample-and-hold function of story-time — it jumps at an observed event and PERSISTS between (default-persist / temporal
  inertia; Dowty 1986 — the same persistence SPACE and entity-state use); "what did A know at T" is that function read at
  T. Event ORDER comes from the temporal-order register (Reichenbach reference time carried across discourse). WHO
  observed an event is a STICKY REGISTRATION LEDGER (Butterfill & Apperly 2013): register on perceptual co-presence
  (in the scene + in the field) OR testimony (an addressee of an assertion) — NOT a boolean re-evaluated at query time.
- **OUR-INVENTION (sweep, do NOT adopt as truth):** the observation-cue EXTRACTION from real prose (who was present /
  in-field / addressed — off the reader's own parse+coref, no gold), the belief-timeline REPRESENTATION (interval
  sample-and-hold vs alternatives), and the where-is read-out format. Glass-box, no LLM.

## 4. MEASURED vs INFERRED
- **MEASURED:** `belief_timeline` + `belief_partition` + `perceptual_access_ledger` are promoted + PINNED-faithful; the
  ToM organ reports ~0.821 and the e2e serve reports 0.902 — but BOTH on AUTHOR-CONSTRUCTED passages with GOLD events
  (only the observation-bit live). INHERIT these as the isolated/upper-bound baselines; do NOT re-derive them. The
  `timeline_register` (event ORDER) is landed. SPACE independently MEASURED that on real prose the ceiling is parser
  recall (parse-as-truth == the info-free null; the predict-and-revise prior is the lever).
- **INFERRED (you must measure):** whether driving `belief_timeline` from the reader's OWN event extraction +
  observation-gate on REAL narrative answers "what did A believe about F at T" (and recovers FALSE beliefs) CI-separated
  over the floors with the info-free twin LOSING — WITHOUT it, the BELIEF dimension is unwired + unproven on real prose.

## 5. ALREADY TRIED / DO NOT RE-RUN
- `the_reader_has_no_belief_timeline_what_an_agent_knew_when` (integrated EXCELLENT — built belief_timeline) + the
  perceptual-access ToM residual problem (integrated — the sticky registration ledger) — INHERIT the organs + their
  GOLD-fed results; this is the END-TO-END-on-real-prose test, NOT a re-derivation of the organs.
- `wire_the_incremental_parser…` (integrated — parser-as-role-candidate-source is a proven NEGATIVE). Do NOT re-wire the
  parser as the role source; drive belief off the reader's EXISTING extraction (which now includes the copular/nominal +
  tense-preserving + verb_subcat gains).
- Do NOT score on GOLD events — that is the exact confound this problem exists to remove. The events + observation cues
  must come from the reader's OWN read() on real prose.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `python tools/reader_capabilities.py` (flag/default manifest; turn `timeline_register` ON — belief needs ORDER).
  Read `hdlab/belief_timeline.py`, `hdlab/perceptual_access_ledger.py`, `hdlab/belief_partition.py`, and the
  BRAIN_FOUNDATIONAL_AUDIT §2b 2026-08-31 belief/ToM entry. Read `experiments/exp_belief_timeline_live_e2e_v1.py` to see
  EXACTLY what it fed gold (the events) vs extracted (the observation-bit) — your job is to extract BOTH from real prose.
- Read how SPACE did the same end-to-end validation (`experiments/exp_space_where_is_end_to_end_v1.py`,
  `verification/test_space_where_is_end_to_end_organ.py`) — the template: real LitBank, the reader's own extraction,
  floors + twin + distance signature + a corpus-age control.
- Pick a belief gold on REAL prose: a small hand-adjudicated "what did A believe about F at T" set on LitBank passages
  with an observed/unobserved change (false-belief cases are the sharp ones); report n honestly. MIND the corpus-age
  confound (add a modern slice if reachable — the SPACE solver constructed 8 modern passages).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On REAL narrative through the LIVE `SituationReader.read()` (capable flags + `timeline_register` ON), driving
`belief_timeline` from the reader's OWN event extraction + `perceptual_access_ledger` observation-gate:
- **PASS =** answering "what did agent A believe about fact F at time T" (belief-at-T) is CI-separated over BOTH floors —
  (a) the REALITY floor (always report the true/final value — this is what a beliefless reader does) and (b) a
  timeline-AGNOSTIC floor (last-mentioned value, no per-agent observation gating) — with the info-free twin (shuffle the
  observation bits / random per-agent order) LOSING CI-separated, AND a FALSE-BELIEF discriminator (on the subset where
  A's belief DIFFERS from reality because A missed the change, the tracker beats the reality floor by MORE) + a
  persistence/distance signature (belief held across intervening unobserved events). Report the observation-cue
  extraction quality (recall/precision) as an honest bound + CI half-width + null p95 beside every margin. Default-off,
  additive (`sm.belief_timeline` / `believes(A,F,T)`), byte-identical when off.
- **A rigorous NEGATIVE is a full PASS:** if the reader's OWN extraction (events + observation cues) is too weak to drive
  the belief timeline on real prose (belief-at-T not beaten CI-separated), name why — enumerated (which observation
  constructions / which events fail) — which, per SPACE, likely localizes to the parser-recall / forward-prediction
  ceiling (the shared wall) and tells the assembly BELIEF waits on a stronger front-end (p2 prediction-error / the parser).

## 8. FILES AND ENTRY POINTS
- Build in `experiments/` (compose the reader's own event+observation extraction → `perceptual_access_ledger` →
  `belief_timeline` over the `timeline_register` order, driven by `SituationReader.read()`). A scaffold-free witness
  recomputes belief-at-T accuracy + both floors + the twin + the false-belief discriminator + the distance signature
  from source through the live reader. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it clears the
  bar, strategy lands the hdlab wire (Q111): a default-off `track_belief` flag on `SituationReader` → `sm.belief_timeline`
  + `believes(A,F,T)`, following the causation/time/SPACE additive-landing pattern. This is the BELIEF dimension of the
  assembly.

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the belief organs' GOLD-fed numbers (ToM ~0.821, e2e 0.902) as a real-prose result — they feed gold
  events / constructed passages; this problem measures the belief timeline driven by the reader's OWN extraction on real
  narrative (a different population). No number crosses scorers/populations.
- 🚫 Do NOT score on GOLD events or CONSTRUCTED passages for the headline — that is the exact confound being removed.
- 🚫 Do NOT re-wire the incremental parser as the role candidate source (a proven fidelity-error NEGATIVE); drive belief
  off the reader's existing extraction.

> ## ✅ SOLVER REVIEW (strategy, 2026-08-31) — EXCELLENT
> A model refute-and-rebuild. The brief's premise (drive belief from Sally-Anne object-moves) was empirically REFUTED —
> object-moves are ~absent from real prose (0 objects with ≥2 moves / 8 LitBank books) — and shown to be the wrong brain
> mechanism by a research drill (the mentalizing network holds a CONTENT-GENERAL, SOURCE-TAGGED propositional attitude fed
> by language ABOUT minds; the object-move is a developmental diagnostic, not the mechanism). Rebuilt on that mechanism:
> drive the promoted belief_timeline from the reader's OWN 4-channel extraction (narrator-epistemic + testimony + perception
> + inference), reality separate, ignorance = None. Validated on an INDEPENDENT, POWERED, EXTERNAL benchmark (FANToM
> info-access ToM, n=3572): reader 0.893 vs floor 0.665 (+0.228), beats a shuffled twin (+0.138) AND a random-presence twin
> (+0.337) CI-sep, false-belief 0.939. Reverified 19/19 first-hand. Every extraction gap routed to a VETTED organ (two wrong
> picks caught in isolation). Honest about the extraction wall (location = the shared parser-recall ceiling → p2) and the
> small narrative exact-value n (FANToM is the powered population). WIRE: QUEUED — track_belief on SituationReader via the
> lazy-adapter track_space pattern (drive from experiments/_belief_reader; sm.belief_timeline/believes/knows; witness =
> the 19/19 + FANToM; register belief_dimension_live_reader_v1). A substantial multi-channel assembly landing = its own
> focused effort (WIRING_MAP DEBT 2), NOT a heartbeat cram. Flipping it on is default-off/owner-gated.
