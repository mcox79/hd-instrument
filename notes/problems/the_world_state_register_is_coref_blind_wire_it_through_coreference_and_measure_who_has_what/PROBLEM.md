---
priority: 3
review:
review_text:
---

# PROBLEM: the mutable world-state register (now WIRED, default-off `track_world_state`) tracks who-has-what by RAW head string, so it is COREF-BLIND — on real prose 81% of possession-transfer AGENTS are pronouns ("he gave it to her"), and the register keys `have(obj)` on "he"/"it"/"her" instead of the entity, so who-has-what collapses on natural text even though the register MECHANISM is proven (1.000 on gold). Wire the register's entity + object keys through the reader's OWN coreference (the substrate already resolves coref — `sm.coref_resolutions` / `hdlab.event_centrality_coref`), so a transferred object's holder is the ENTITY, not the last pronoun, and prove who-has-what recovers CI-separated over the raw-string (coref-blind) register on real prose — or locate precisely why coref-densification does not close it (coref recall vs recipient-PP vs verb-sense).

**slug:** `the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what` — **opened:**
2026-09-01 by the strategy session, the DEFINITIVELY-LOCATED #1 open-text residual of the just-integrated owner-DONE
problem `situation_model_has_no_mutable_world_state_register` (mechanism SOLVED 1.000 vs floor 0.750; open-text located
to coref — 81% pronoun agents — a NAMED existing organ, not the mechanism). **status:** OPEN — a WIRE-AND-MEASURE
problem (compose the wired register with the reader's coref; measure who-has-what on real prose). Strategy lands any
hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (RE-RANK PER THE OWNER):** filed at `3` — below the north-star meaning organ (1) and the register-native
> selectional store (2, the #1 who-did-what lever). This is the register's OWN #1 residual: the mechanism is proven, the
> capability is WIRED default-off, and the sole gap to a LIVE who-has-what win is entity identity across mentions (coref).
> It composes two already-built organs, so it is lower-risk than 1/2; raise it if you weight a live STATE-tracking win higher.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation, replicate
> that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker after your tools plateau.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method
> conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested,
> or a SPECIFIC reason it cannot be. Exhausting engineering variations is NOT convergence.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather high-value adjacent info (a control /
> curve / ablation / 2nd gold); enumerate what's LEFT + do it; MAP adjacent bottlenecks (name component + on-disk
> evidence + leverage) and EVALUATE each for brain-fidelity + optimization (seeds the next problem); hit a wall → run a
> FINER brain-foundational research drill, never stop. Implement → test (can-fail, strongest real floor, twin LOSING) →
> iterate. CANCEL + submit only when the mechanism bar is met AND the checklist yields nothing more.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any
> deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
As you read a story you track who currently has what. The reader can now do this (a mutable possession register), and it
is right 100% of the time when the people and objects are named cleanly. But real stories say "he handed it to her" — and
the register writes down that "he" has "it", not that Anna has the book. Most doers in real transfers are pronouns (about
4 out of 5). The reader ALREADY figures out who "he"/"she" refers to elsewhere; this problem connects that pronoun-
resolution to the possession tracker so the holder is the PERSON, not the word, and then measures how much of real-story
who-has-what that recovers.

## 2. WHY THIS ONE
It is the register's ONE located open-text residual. The mechanism is proven (register 1.000 vs the strongest stateless
floor 0.750, CI-sep; twins lose; change-point 100%/0%) and the capability is WIRED (default-off `track_world_state`), so
nothing else stands between the register and a LIVE who-has-what win EXCEPT entity identity across mentions. On real prose
the residual was measured and NAMED: role recovery agent 0.51, recipient-on-GIVE 0.33, and the dominant cause is that 81%
of real transfer agents are pronouns with no coref link into the register. It composes two already-built organs (the
register + the reader's coref), so it is a low-risk, high-clarity next step — and a live STATE dimension is a genuine step
toward comprehension the reader can be QUERIED on ("who has the key now?").

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: the situation model binds an event's participants to their DISCOURSE ENTITIES, not their surface forms — a
pronoun is resolved to its referent and the referent's state is updated (Zwaan & Radvansky 1998 event-indexing on the
protagonist dimension; the bridging/anaphora resolution that maintains entity coherence, Garrod & Sanford). Possession
availability tracks the ENTITY's current relation to the object (Glenberg/Meyer/Lindem 1987), which presupposes stable
entity identity. So the register must key on the coref-resolved entity, exactly as the brain updates the referent's state
regardless of whether the current mention was a name or a pronoun. REUSE the substrate's coref (the reader already runs
it), do NOT build a new resolver.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** register mechanism on gold 1.000 [1.000,1.000] vs strongest stateless floor
  last_obj_mention 0.750 (+0.250 CI-sep); open text via the substrate's OWN parser (MCScript2, 1467 transfer instances):
  role recovery theme 0.78 / agent 0.51 / recipient-on-GIVE 0.33 / source-on-GET 0.11; the end-to-end who-has-what
  residual is LOCATED as coref-bound (81% of real transfer agents are pronouns) + recipient-PP + verb-sense precision —
  NOT the mechanism or the operator lexicon. The register is now WIRED default-off (`track_world_state` → `sm.world_state`).
- **INFERRED (you must measure):** whether keying the register through the reader's OWN coref (so "he"/"she"/"it" resolve
  to the tracked entity/object before the effect is applied) RECOVERS who-has-what CI-separated over the coref-blind
  raw-string register on a real-prose held-out test, and how much of the located 81%-pronoun gap it closes — or locate the
  remaining residual precisely (coref RECALL on transfer agents vs recipient-PP extraction vs verb-sense).

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- Do NOT rebuild the register or the operator lexicon (owner-DONE, mechanism SOLVED + FrameNet 105-verb lexicon WITH the
  recipient role). Do NOT rebuild a coref resolver — REUSE the substrate's (`sm.coref_resolutions` / `event_centrality_coref`).
- Do NOT chase ORDER with this (the register is a STATE organ; the serve-test PROVED it does not break the ~0.59 order
  wall — order is conventional, not state). Do NOT re-run the mechanism/precondition/learning arms (all PASS 36/36).
- BUILD ON: the wired `hdlab/world_state_register.py` + `hdlab/possession_operators.py` + the default-off `track_world_state`
  flow in `hdlab/situation_reader.py` (which already folds the reader's own events); the reader's coref output.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS (do these before proposing anything):** (1) understand ALL the existing organs — `python
  tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read the parent SOLVED.md
  (`situation_model_has_no_mutable_world_state_register`) IN ITS ENTIRETY — esp. the open-text arm + the located coref
  residual + `DISSECTION_before_after_order_wall.md`; and read how coref is produced in `hdlab/situation_reader.py`
  (`sm.coref_resolutions`) + `hdlab/event_centrality_coref.py`. Reuse, don't reinvent.
- Reproduce the coref-blind baseline on your own recomputation: run the wired reader with `track_world_state=True` on real
  prose and confirm the who-has-what failure is dominated by pronoun agents (81%), not the operator lexicon.
- Read the wired landing: `hdlab/world_state_register.py` (the core), the `_read_world_state` drive in
  `hdlab/situation_reader.py`, and the witness `verification/test_world_state_register_landing_organ.py`.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a coref-densified world-state register (entity + object keys resolved through the reader's OWN coref BEFORE the
effect is applied) RECOVERS who-has-what CI-separated over the coref-BLIND raw-string register on a HELD-OUT real-prose
test with state-CHANGING transfers, with a SHUFFLED-COREF twin (same clusters, wrong assignment) LOSING CI-sep and a
positive control that the answer CHANGES at the transferring event. A rigorous located negative is a full PASS if it names
the residual precisely (coref recall on transfer agents vs recipient-PP extraction vs verb-sense) with the number for each.
Report CI half-width + null p95. Do NOT grade on the same corpus the store/coref were tuned on without a held-out split.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. Reuse: `hdlab/world_state_register.py`, `hdlab/possession_operators.py`, the
`track_world_state` flow in `hdlab/situation_reader.py`, the reader's coref (`sm.coref_resolutions` /
`hdlab/event_centrality_coref.py`), the open-text arm `experiments/exp_world_state_realtext_mcscript_v1.py`. Strategy
lands any hdlab wire (Q111, default-off, witnessed — likely a coref-densification option on the `track_world_state` drive).
Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the register's open-text payoff is coref-bound; coref-
densification recovers/does-not-recover who-has-what by X).

## DO NOT QUOTE
- Do NOT quote the register's gold mechanism 1.000 as an OPEN-TEXT result — that is construction-gold, isolating the
  tracking mechanism; the open-text number is what THIS problem must produce.
- Do NOT claim a win without the shuffled-coref twin (the CORRECT entity assignment, not any coref-shaped signal, must do
  the work).
- Do NOT use an external LLM as the coref resolver or the corpus (the invariant). Reuse the substrate's glass-box coref.
