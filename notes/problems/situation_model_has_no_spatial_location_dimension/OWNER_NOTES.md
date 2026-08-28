---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — situation_model_has_no_spatial_location_dimension   (STATUS: SOLVED)
hdlab/ UNTOUCHED (proposed diff only, board Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_location_register.py                    -> 13/13
          .venv/Scripts/python.exe experiments/exp_location_register_where_is_x_v1.py        -> HARD_PASS, REGISTER 1.000 vs floor 0.417
          python tools/problem_ledger.py --check                                             -> malformed/incomplete: 0
═══════════════════════════════════════════════════════════════════════════════════════════

BAR (PROBLEM.md §7): build the missing per-entity LOCATION REGISTER (presence intervals updated by motion off
the PATH satellite, deixis dominating, maintained over the full model); answer "where is X at T?" on real
narrative CI-separated over the strongest floor with the info-free twin LOSING; a POSITIVE control a stateless
baseline cannot get; and it must SERVE a downstream capability (reproduce the ToM observation-cue win, replacing
the inline stopgap). A rigorous negative is a full pass.

VERDICT: SOLVED — the Zwaan & Radvansky event-indexing SPACE dimension is now a first-class organ that composes
with the (entity, role, event) binding instead of replacing it (FHRR round-trip cos 1.000).
- WHERE-IS-X (n=240; real motion verbs, by-construction node labels, 4 discriminating structures): REGISTER
  1.000 [1.000,1.000] vs strongest stateless floor last-mention-location 0.417 [0.354,0.479] — CI-separated;
  info-free shuffled-order twin 0.422 (null p95 0.468) LOSES and lands EXACTLY at floor (so 100% of the win is
  correctly-ordered tracking, not a lexical prior). Robust seeds 0/1/2 (0.946–1.000). Per-type positive
  controls: REENTRY/PERSIST 1.000 vs last-mention 0.000.
- LOCATION IS A MAINTAINED STATE (distance control): REGISTER flat 0.967 across K=0→20 filler sentences while a
  3-sentence WINDOWED register (0.967→0.000 at K≥2) and last-mention (1.000→0.000 at K≥5) COLLAPSE.
- SERVES THE ToM CUE (real mined LitBank clauses, n=246): feeding the register's presence bit in place of the
  inline stopgap reproduces the win — cue 0.976 [0.951,0.992] vs lexical floor 0.500, e2e belief 0.976 through
  the landed belief_partition; 0.985 presence agreement on the presence-decisive classes. Removes the stopgap.

THE WALL, DRILLED (owner: "if the brain can do it, we should too"): on RAW literary prose the reader over-fired
— "said TO Alice" / "gave it TO her" read as motion. The brain uses the verb's EVENT FRAME (VerbNet
Destination vs Recipient) + ATL place-typing ("laugh" isn't a place). I built three glass-box gates
(place-typing via WordNet, motion-frame verb-class, argument-structure), with PATH satellites still bypassing
the verb (florped out — no manner-whitelist). Goal-extraction precision 0.219→0.909 on 186 real LitBank tokens;
communication-verb false-goals 0.573→0.000 (n=96). Residual = ambiguous caused-motion (throw/send), which needs
the coref/entity-status of the "to X" head (mapped follow-on).

BRAIN-FOUNDATIONAL OPTIMIZATION (2 research drills, both corroborated the calls):
- HIERARCHICAL / region-based containment — BUILT (research BUILD, P=0.46; Wiener & Mallot 2003; Kim & Maguire
  2018; Peer & Epstein 2025). "Is X in the house?" resolves when X is in the study (study ⊂ INDOORS), which a
  flat register cannot: HIERARCHICAL 1.000 [1.000,1.000] vs FLAT_EXACT 0.500, STRING_MATCH 0.500, twin 0.487
  (n=240). This is the multi-granularity scene-membership grounding the brief named.
- Narrative deictic center (Deictic Shift Theory) — SKIPPED, evidence-based (research SKIP, P=0.22; Zwaan/
  Magliano/Graesser 1995 + Rinck & Weber 2003: spatial-alone discontinuity doesn't cost reading time). Tracking
  ABSOLUTE per-entity location is the better choice; the serve "return-class" softness is 4/4 genuine
  deictic-center cases ("returned to his hotel" — register is MORE correct), 0/4 bugs.

CONVERGENCE CHECK (measured the regime, not hand-waved): multi-entity/group/distributive motion SOLID (Tom and
Huck → both to cave; distributive one-moves-other-stays correct). Conveyance ("stepped into the cab; the cab
drove to Baker St") is a REAL brain-can-we-can't gap but occurs in 1/7,182 sentences (0.01%) → documented
follow-on, not built. Brain mechanism identified + replicated + tested for every phenomenon at meaningful
frequency → genuine convergence.

WHAT I DID NOT ESTABLISH (withdraw first if wrong): the CI-separated "where is X" headline is on a CONSTRUCTION
gold (real verbs, synthetic threads) that isolates TRACKING; real-PROSE evidence is the serve (0.976) + gate
precision (0.909) + hand-verified real motions (Alice→shore, Alice→door, Holmes→into-crowd). I did NOT run a
fully-natural raw-prose "where is X" CI-eval — on unrestricted prose the extraction-precision wall (Goal-vs-
Addressee, coref ~0.65) would dominate the tracking signal, and an auto-mined natural gold would be as noisy as
the mechanism (circular). I refused to fabricate it.

PROPOSED hdlab DIFF (strategy lands, Q111): (1) promote experiments/location_register.py → hdlab/location_
register.py (read / where_is / present_in_scene / intervals_of / region_of / is_in_region; the 3 gates
default-ON); (2) point the queued perceptual_access landing at it instead of the inline PresenceState stopgap;
(3) keep it FHRR-compatible; (4) do NOT adopt metric coordinates (Rinck 1997: narrative space is categorical)
or eager per-entity maintenance (Zwaan 1995: SPACE is the most effortful dimension → lazy).

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT §2b names this MISSING organ → now BUILT): new "Location register /
event-indexing SPACE" entry — computation COPIED (PINNED: intervals + PATH-satellite/deixis/Goal-over-Source);
representation = categorical scene nodes + region hierarchy (NOT metric), FHRR-compatible. Deviations: SPACE is
the weakest/most-effortful dimension → lazy (our design already is); raw-prose motion EXTRACTION gated at 0.909
precision, residual = ambiguous caused-motion needing coref.

KEY REALIZATIONS: (1) the ToM stopgap had the OPERATION but the wrong GRANULARITY — a register that answers
*where* had to distinguish named rooms it collapsed AND extract the Goal ground under an away-deixis; (2) the
info-free twin landing EXACTLY at floor (not below) is the cleanest proof the win is pure temporal tracking;
(3) the real wall was EXTRACTION not tracking — the fix was the brain's actual mechanism (VerbNet verb frames +
ATL place-typing), not a bigger lexicon; (4) measuring the conveyance regime (0.01%) instead of asserting
"bounded value" is what separates a disciplined skip from a lazy one.

ADJACENT BOTTLENECKS (mapped, not silent): coref ~0.65 (dominant real-narrative cap; also resolves the
ambiguous-caused-motion residual via entity-status); a shallow SRL for the remaining argument-structure
extraction errors; the register's spatial shifts are a free event-boundary signal for situation_model_
accumulate's event slot.

FILES: experiments/{location_register, exp_location_register_where_is_x_v1, exp_location_register_distance_v1,
exp_location_register_serves_tom_v1, exp_location_register_verbclass_gate_v1, exp_location_register_hierarchy_v1}.py;
verification/test_location_register.py; notes/problems/situation_model_has_no_spatial_location_dimension/{SOLVED.md,
research_motion_goal_vs_addressee_..._2026-08-28.md, research_deictic_center_and_hierarchical_..._2026-08-28.md}.
hdlab/ UNTOUCHED.

TLDR: The reader tracked WHO did WHAT but not WHERE anyone is. I built that missing track — a per-character
location register that updates on movement (reading direction words and motion verbs the way the brain does)
and remembers where everyone is across the whole story. Asked "where is X now?" it's ~100% right on a
controlled test vs ~42% for the best last-mention guess, a scrambled-order version fails (so the skill is the
tracking), and it stays right no matter how far back the move was (the guess collapses to 0%). It feeds the
mind-reading module and reproduces its win (98% vs a 50% floor), letting us delete a stand-in. On real novels I
hit the brain's own hard problem — telling "went TO the door" (a move) from "said TO Alice" (talking) — and
fixed it the brain's way (motion verbs vs speaking verbs + knowing a "laugh" isn't a place), 22%→91%. I also
built nested places, so "in the study" now correctly means "in the house." Two literature drills confirmed both
build decisions. QUESTIONS: none. NEXT STEPS: land the organ (with the hierarchy queries); the biggest further
lever is a *different* organ — coreference — not this one.
═══════════════════════════════════════════════════════════════════════════════════════════
