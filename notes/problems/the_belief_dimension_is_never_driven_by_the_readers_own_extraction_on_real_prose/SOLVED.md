---
problem: the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose
status: PARTIAL
bar: "PASS = answering 'what did agent A believe about fact F at time T' (belief-at-T) is CI-separated over BOTH floors -- (a) the REALITY floor (always report the true/final value -- this is what a beliefless reader does) and (b) a timeline-AGNOSTIC floor (last-mentioned value, no per-agent observation gating) -- with the info-free twin (shuffle the observation bits / random per-agent order) LOSING CI-separated, AND a FALSE-BELIEF discriminator (on the subset where A's belief DIFFERS from reality because A missed the change, the tracker beats the reality floor by MORE) + a persistence/distance signature (belief held across intervening unobserved events). ... A rigorous NEGATIVE is a full PASS: if the reader's OWN extraction (events + observation cues) is too weak to drive the belief timeline on real prose, name why -- enumerated."
result: "REAL LitBank (exact belief-value match, n=5 hand-adjudicated items / 6 queries): BELIEF_live 0.833; beats the beliefless REALITY floor 0.167 CI-separated (+0.667 [+0.333,+1.000]); false-belief recovery +0.800 [+0.400,+1.000] CI-separated. It does NOT clear the strongest-floor / twin CI-sep bar at n=5 -- COVERAGE-BOUNDED. MODERN control (n=12 items / 31 queries): the pivoted MECHANISM (oracle -> promoted belief_timeline) 1.000 beats the strongest floor (last-mention) 0.742 CI-separated (+0.258 [+0.103,+0.406]); the LIVE arm 0.774 is bounded entirely by extraction (live_vs_oracle +0.226 CI-sep); false-belief +0.857 CI-sep; twin loses (0.774 > null p95 0.613); persistence signature decisive (last-mention 1.0->0.33->0.0 across distance while the timeline HOLDS)."
floor: "strongest floor actually run: MODERN FLOOR_lastment 0.742 (mechanism beats it CI-sep, +0.258); REAL FLOOR_current(-belief) 0.667 and FLOOR_reality 0.167 (belief beats reality CI-sep, +0.667). Info-free twin-null p95: modern 0.613 (beaten), real 0.833 (tie, n-bound)."
controls: "object-move VIABILITY probe (refutes the brief: 0 objects with >=2 extracted moves / 8 LitBank books); channel-density probe (narrator-epistemic+testimony 4.2x object-moves); REALITY floor (beliefless reader); CURRENT-BELIEF floor (obs-gated, no time axis); LAST-MENTION floor (no obs gating); SHUFFLE-twin + R=25 twin-null; ORACLE upper-bound (gold belief chain -> isolates the extraction residual from the mechanism); FALSE-BELIEF discriminator; PERSISTENCE distance signature; per-channel + per-fact-type breakdown (generalization); extraction quality (reality-recall, belief-recall, obs-bit-acc)."
files_changed: "experiments/_belief_reader.py, experiments/belief_at_t_gold.py, experiments/exp_belief_at_t_end_to_end_v1.py, experiments/_build_real_belief_gold.py, data/belief_at_t_gold_v1/real.jsonl, experiments/_belief_probe_scratch.py, experiments/_belief_channel_probe_scratch.py, verification/test_belief_at_t_end_to_end_organ.py, notes/problems/the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose/{DESIGN_brain_and_mapping.md,SOLVED.md}"
reverify: ".venv/Scripts/python.exe verification/test_belief_at_t_end_to_end_organ.py"
---

# BELIEF/ToM driven by the reader's OWN extraction on real prose — a refute-and-rebuild

**One line:** the brief's object-move event source is refuted (empirically AND neuroscientifically); I rebuilt the
belief dimension on the brain's *actual* mechanism — a content-general propositional attitude fed by narrator-epistemic
+ testimony + perception — drove the PROMOTED `belief_timeline` from the reader's OWN 3-channel extraction, and proved
the mechanism beats every floor + recovers false beliefs + holds across time. On real prose it drives end-to-end and
beats the beliefless reality floor CI-separated, but the exact-value headline is **coverage-bounded** (clean small-valued
belief scenes are rare in literary prose) and **extraction-bounded** (the object-move channel — the brief's own source —
is the weak one). A rigorous, enumerated negative on the headline; a validated, generalizing mechanism underneath.

## What the brief assumed, and why the disk + the brain both refute it
The brief drives belief from OBJECT-LOCATION-MOVE extraction (Sally-Anne: "marble moved basket→box unobserved"). Two
independent lines kill this as the event source **for real prose**:
- **Viability probe (`_belief_probe_scratch`):** the reader's own in-substrate parse extracts ~1 object-move per LitBank
  book, **0 objects with ≥2 moves** across 12 books, most hits idiomatic ("threw glances→direction"). The Sally-Anne
  structure is essentially absent from literary prose.
- **Research drill (`hdi_research`, cited in DESIGN):** the mentalizing network (rTPJ/dmPFC) holds a **content-general
  propositional attitude**, NOT an object-location register (Koster-Hale et al. 2017 MVPA — belief coded along abstract
  content-general dimensions, not object/location identity), and it **source-tags** how a belief was acquired (seen vs.
  heard; Koster-Hale et al. 2014). In natural narrative, belief is fed by *language about minds* — narrator-epistemic /
  free indirect discourse (dominant), testimony, and rare perception (Zwaan event-indexing; Zunshine; Dodell-Feder 2011
  verbal false-belief localizer; Jacoby et al. 2022). The Sally-Anne object-move is a developmental *diagnostic*, not the
  mechanism.
- **Channel-density measurement (`_belief_channel_probe_scratch`, 30 books):** narrator-epistemic + testimony belief
  signals outnumber (already-noisy) object-moves **4.2×**.

⇒ **Pivot — a FIDELITY UPGRADE, not a convenience:** drive the (already content-general) `belief_timeline` from the
reader's OWN extraction across the **three registration channels** — RULE0 narrator-epistemic (dominant), RULE2
testimony, RULE1 perception (the object-move as its degenerate special case) — reality tracked separately. This
replicates three properties the brain has and the object-move model lacks: content-generality, source-tagging, and
language as the driver of mentalizing.

## What I built (the mechanism — verdict-independent)
`experiments/_belief_reader.py` composes the reader's OWN extraction into the PROMOTED `hdlab.belief_timeline` (untouched)
on a uniform sentence-index time axis, merging two tracks:
1. **Perception track (RULE1):** each extracted reality value-change (in-substrate `pos_tagger`+`arc_parser`+role router,
   object-move goal-typing relaxed), observation-GATED by the PROMOTED `perceptual_access_ledger` (RULE0 explicit-
   epistemic / RULE1 co-presence+field / RULE2 informed) — event index + location come from EXTRACTION, never gold.
2. **Belief-assertion track (RULE0 + RULE2):** the believed VALUE read straight off mental-state / speech verbs
   ("believed her brother *dead*", "told her the ship was *lost*"), bound to the agent, marked a belief (may diverge from
   reality). This is the content-general path the object-move source cannot express — and it is the DOMINANT real-prose
   channel.
The gold (`belief_at_t_gold.py` + `data/belief_at_t_gold_v1/real.jsonl`) has a MODERN control (3 channels × 2 fact types,
definitional by construction — the verbal-ToM paradigm) and a hand-adjudicated, quote-verified REAL LitBank slice.

## What I measured
- **Mechanism is sound (modern control, n=12/31):** `BELIEF_oracle` (gold belief chain → promoted organ) = 1.000, beats
  the strongest floor (last-mention 0.742) **CI-separated (+0.258)**; false-belief recovery **+0.857 CI-sep** (belief
  0.857 vs beliefless reality 0.000); the info-free twin **loses** (0.774 > null p95 0.613); the **persistence signature
  is decisive** — as distance since the last update grows, the last-mention floor collapses 1.0→0.33→0.0 while the belief
  timeline HOLDS (oracle 1.0). It **GENERALISES**: both fact types reach oracle 1.0, and the dominant channels
  (epistemic, testimony) reach live 1.0 — one content-general mechanism, exactly the brain's single mentalizing system.
- **The wall is EXTRACTION, not the mechanism:** `live_vs_oracle` = **+0.226 CI-separated** — the entire live shortfall
  (0.774) is the reader's extraction residual. And the residual localizes precisely: the pivoted channels extract at 1.0;
  the **OBJECT-MOVE (perception) channel is the weak one (0.68)** — i.e. the brief's own intended source is exactly what
  under-extracts. Same object-move / parser-recall wall SPACE hit.
- **Real prose (headline, n=5 items/6 queries, exact-value):** the composition drives end-to-end on real LitBank; BELIEF
  0.833 beats the beliefless REALITY floor 0.167 **CI-separated (+0.667)** and recovers false beliefs **+0.800 CI-sep**.
  It does NOT clear the strongest-floor / twin CI-sep bar — **coverage-bounded**: clean small-valued belief-at-T scenes
  are rare in literary prose, and real scenes are single-assertion (all real queries are distance-0, so the persistence
  and twin signatures — which need the multi-change structure — are not testable on the real slice).

## What I did NOT establish (and would withdraw first)
- **A CI-separated real-prose value headline over the STRONGEST floor.** n=5 is honest but underpowered; the value-task's
  ingredients are genuinely rare in real literary prose. If any single claim is wrong, it is "the real slice clears the
  full bar" — it does not, and I have not claimed it. What IS solid on real prose: it beats the beliefless reality floor
  and recovers false beliefs, CI-separated.
- **Perception-channel extraction.** Object-move recall on real 19c prose is ~0 (status copular predications like
  "the master was in the field" also unextracted, 0%). The belief arm survives this because it rides the belief-assertion
  channels; but the perception channel is unproven on real prose (the SPACE parser wall).

## KEY REALIZATIONS (the enabling moves)
- **The event source was the whole problem, not the organ.** The `belief_timeline` was already content-general and PINNED-
  faithful; the object-move viability probe (0 multi-move objects) + the neuroscience together said: stop extracting
  object-moves, extract the belief VALUE off mental-state/speech verbs. That one reframe took live accuracy on the
  dominant channels from 0.0 → 1.0.
- **Ignorance is `belief=None`, not a special case.** Literary belief is IGNORANCE-dominated ("did not know"); modelling
  ignorance as an unregistered belief (Butterfill & Apperly) let the same mechanism + the same reality-floor comparison
  score the abundant real-prose ignorance scenes with no new machinery.
- **Isolate the wall with an ORACLE arm.** Feeding the gold belief chain to the same organ (oracle=1.0) proved the live
  shortfall is 100% extraction — the difference between "the mechanism is wrong" and "the front-end under-reads," which
  is the difference between a dead route and a build target.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b — strategy to fold in)
The 2026-08-31 belief/ToM entry frames the wire as "drive belief_timeline from the reader's own EVENT stream" on the
implicit assumption of object-move events. **Correction:** the brain-faithful event source is NOT object-moves — belief
is a content-general propositional attitude (Koster-Hale 2017), source-tagged (Koster-Hale 2014), fed by narrator-
epistemic + testimony + rare perception. The object-move source is (a) ~absent from real prose (0 multi-move objects / 12
books) and (b) the developmental *diagnostic*, not the mechanism. New PINNED sub-claim (built + measured): the belief
dimension composes from THREE registration channels with the SAME content-general sample-and-hold; the mechanism beats
every floor + recovers false beliefs + holds across distance (oracle CI-sep). New MEASURED deviation: the real-prose
value headline is COVERAGE-bounded (clean small-valued scenes rare; literary belief open-ended + ignorance-dominated) and
the perception channel is EXTRACTION-bounded (object-move recall ~0, the SPACE parser wall) — **BELIEF converges with
SPACE on the same ceiling: front-end recall (p2 / the parser), not the tracker.**

## PROPOSED hdlab DIFF (default-off; strategy lands, Q111)
1. A default-off `track_belief` flag on `SituationReader` → `sm.belief_timeline` + `believes(A, F, T)`, following the
   causation/time/SPACE additive-landing pattern; byte-identical when off.
2. The event source is the **belief-assertion extractor** (RULE0 narrator-epistemic + RULE2 testimony) as PRIMARY (the
   dominant, extractable channels) + the RULE1 perception track as secondary; NOT object-move extraction.
3. Represent IGNORANCE natively (`belief=None`) and keep reality separate; do NOT gate belief on object-moves.
4. Flip on owner approval only; the real-prose value headline stays flagged as coverage-bounded until a larger real gold
   (or a modern-annotated corpus with more small-valued belief scenes) is built.

## TLDR (plain English)
When you read a story you keep track of what each character believes — and it can be wrong. We already built the
"belief board" that jumps when a character learns something and holds steady until they learn the next thing. The task
said to feed it by watching objects get moved around (the classic marble-in-the-box test). But real novels almost never
move objects around like that — and, it turns out, that's not how the brain tracks belief either: the brain reads belief
straight from the *words* ("she believed him dead," "he was told the ship was lost"). So I fed the belief board from the
words instead. It then works: it tells you what a character believed at an earlier moment, catches false beliefs the
"just-tell-me-the-truth" reader gets wrong, and holds a belief steady over time where a dumb "last thing mentioned" reader
loses it. On real 19th-century novels it still beats the truth-only reader and catches false beliefs — but only on a
handful of clean examples, because real literary belief is mostly open-ended ("she didn't understand what he meant")
rather than a tidy fill-in-the-blank, and the one part that needs watching objects move is exactly the part our reader
can't yet see well. So: the machine is right and matches the brain; the limit is how much of it real novels spell out and
how well the reader's eyes (the parser) pick up physical changes — the same limit the "where is everyone" work hit.

## QUESTIONS
None blocking. One design choice for the owner at landing: land `track_belief` now (default-off, belief-assertion-driven,
proven mechanism) OR wait for a larger real-prose belief gold. My recommendation: land default-off now — the mechanism is
proven and the wall is a known shared one (parser recall), so landing it wired-but-off compounds with the p2 parser work
rather than waiting on it.

## NEXT STEPS
1. (strategy) Fold the AUDIT UPDATE into §2b; land `track_belief` default-off per the proposed diff.
2. A larger real-prose belief gold — a modern annotated corpus (the McGuffey/LitBank-age confound also bites here) would
   raise both coverage (more small-valued belief scenes) and extraction (a modern parser).
3. The perception channel waits on the same front-end SPACE flagged: p2 forward-prediction / a stronger parser to lift
   object-move + copular-status recall. BELIEF and SPACE now point at ONE ceiling.
