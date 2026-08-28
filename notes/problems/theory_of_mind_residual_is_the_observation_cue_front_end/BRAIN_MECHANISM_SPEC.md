# Brain-faithful spec for the observation cue (perceptual access -> knowledge)

Source: deep literature drill (4 web-verified passes), 2026-08-28. Tags: PINNED / CONTESTED / OUR-INVENTION.

## The core reframe (biggest correction to the naive gate)
The naive `observed = co_present AND available OR informed` is roughly right in outline but WRONG in
structure/timing. The literature (Butterfill & Apperly 2013, *Mind & Language* 28:606-637 — the most
directly formalized source) converges on a **sticky, procedurally-updated REGISTRATION LEDGER**, not a
boolean re-evaluated at query time.

```
STATE (maintained incrementally, clause by clause):
  location_register[X] = OPEN presence-interval (location_node, t_start, ->) per entity X
  registration[A][E]   = (E's last-registered state/location, t_of_last_registration)  -- STICKY

UPDATE RULE 1 -- perceptual route (fires only at the clause describing E):
  if presence_check(A, window(E))          -- A's OPEN interval contains E's event window (Allen containment)
  and E in field(A, window(E))             -- occlusion/line-of-sight gate (Butterfill&Apperly "field")
  then registration[A][E] := (state(E), window(E))

UPDATE RULE 2 -- testimony route (independent; source-tagged, revisable):
  if A in addressees(communication asserting E)
  then registration[A][E] := (asserted-state(E), t_utt)   weighted by reliability(speaker)

QUERY (only when ToM needs an answer):
  knows(A,E)        = registration[A][E] defined and matches ground truth
  false_belief(A,E) = registration[A][E] defined but STALE (truth changed via an update A never registered)
```
**KEY:** false belief is NOT a separate computation — it is the ledger being stale. This is exactly the
landed `believed_location(observed, initial, final)`: "observed" == "Rule 1 or Rule 2 fired for A on E".

## Per-area PINNED/INVENTED
1. **Seeing->knowing (Level-1)** PINNED: Pratt&Bryant 1990; Pillow 1989 (both directions by age 3);
   Flavell 1981 (Level-1 = whether-seen, occlusion geometry; Level-2 not needed). Autism dissociation
   (Baron-Cohen 1994) => dissociable computation. Graded/probabilistic credit = OUR-INVENTION (not evidenced).
2. **Spatial situation model** PINNED (event-triggered, NOT continuous): Zwaan&Radvansky 1998; Speer/Zacks
   2009 (parahippocampal+hippocampus activate on character location-change during ordinary reading);
   Rinck&Bower 1995 (accessibility ~ room-graph distance); Glenberg 1987 (sweater effect). CORRECTION:
   spatial monitoring is goal/map-gated (Zwaan et al. 1998 3-expt), not a standing default. Decay function
   form = OUR-INVENTION.
3. **Motion semantics** — resolve via FRAME + realized Source/Goal/Path arguments (mostly PP/particle:
   "into X", "out of X"), NOT a verb whitelist (Talmy typology; Papafragou 2008; FrameNet ~15-20 frames,
   does NOT collapse to a small primitive set). Goal-over-Source asymmetry PINNED (Lakusta&Landau 2005).
   => "she florped into the room" still updates via "into the room". **Hardcoding a 6-8 verb list is the
   IMPLEMENTATION TRAP, not a real wall.**
4. **Temporal alignment** — presence is an INTERVAL; departure closes, arrival opens; "while/meanwhile/
   during" nests, "after/then" sequences (Zacks EST 2007; Speer&Zacks 2005; O'Brien&Albrecht inconsistency
   cost 150-400ms). Allen-interval implementation = OUR-INVENTION (best-supported, not handed to us);
   the while/during->presence-window link is a genuine literature gap we fill.
5. **Occlusion / field** PINNED as a computational template (Butterfill&Apperly 2013):
   field(A,t) = { E : no opaque barrier between A and E } U { E recently in motion, not yet occluded }.
   Coarse single gate (not-in-room / asleep / blindfold / dark / barrier) is a defensible MVP (O'Neill&Chong
   2001: coarse present/absent before per-sense binding — matches development). Darkness/back-turned =
   OUR-INVENTION by analogy.
6. **Testimony** PINNED as an independent early channel (Harris&Koenig 2006; Koenig 2004 — source-tagged,
   reliability-weighted, revisable — asymmetric vs perception). The exact "addressee-of-assertion => knows"
   state-update = OUR-INVENTION (literature gap).
7. **Two-systems** (Apperly&Butterfill 2009): registration/minimal system IS where perceptual access lives;
   full propositional belief is the flexible system. CONTESTED at the infant/anticipatory-looking base
   (Heyes submentalizing; Kaltefleiter 2022 non-replication) — but UNPINNED != STOP; the registration
   FORMALISM is the right shape for adult-reading-scale.
8. **The precisely-diagnosed NLP WALL = occlusion/perceptual-availability reasoning** (FANToM Kim 2023:
   models score Belief >> InfoAccess, the access facts belief depends on; Ullman 2023 transparent-bag: adding
   "the bag is transparent" fails to flip the answer — isolated occlusion failure with coref/verb held
   constant). NOT coreference, NOT motion verbs. Build the occlusion gate most carefully.

## Build order (research NEXT STEPS)
1. Registration ledger + 2 update rules (core data structure) — BEFORE any "does A know E" classifier.
2. Occlusion/field gate first (the evidenced wall).
3. Presence as intervals with connective-driven nest/sequence.
4. Motion via frame/argument roles (Source/Goal/Path from PP), not a verb list.

## Do-not-requote
- Curse-of-knowledge (Birch&Bloom 2007) effect is SMALL post-replication (d~0.20-0.24, Ryskin&Brown-Schmidt
  2014), not the larger original d~0.469.
- Zwaan Langston&Graesser 1995 is a clause-clustering task, NOT the reading-time study (that's Zwaan et al.
  1998, Sci Studies of Reading).
