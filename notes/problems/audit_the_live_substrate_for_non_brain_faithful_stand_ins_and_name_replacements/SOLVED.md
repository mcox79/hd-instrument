---
problem: audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements
status: SOLVED
bar: "PASS = a prioritized CATALOG of >= 8 LIVE non-brain-faithful stand-ins, EACH with all five fields VERIFIED ON DISK: (a) the brain's actual structure + computation, marked PINNED vs OUR-INVENTION, with a citation where PINNED; (b) why the current thing is NOT it (file:line); (c) the brain-faithful REPLACEMENT (named mechanism/organ); (d) blast radius = which LIVE board dim(s) it moves, OR 'dormant / no live consumer' backed by the grep that proves it; (e) a LOCAL-FIX vs RE-ARCHITECTURE verdict. PLUS the top-K (K >= 5) prioritized by blast x severity, AND the parser-scorer cluster (surface-feature arc scorer + ConceptNet/Lancaster/gold-coref cue proxies + pure-defer) resolved to a concrete brain-faithful replacement DESIGN that references the recurrent predictive-coding loop / pri-1 generative world-model (does not rebuild it). A component flagged and then found brain-faithful on deeper reading is a VALID catalog entry (a located negative), provided the deeper reading is shown."
result: "A prioritized CATALOG.md of 11 entries -- 8 LIVE non-brain-faithful stand-ins (C1-C8) + 3 located-negatives/corrections (C9-C11) -- each with all five fields verified on disk (file:line), top-K ranked by blast x severity, and the parser-scorer cluster resolved to a 4-move brain-faithful replacement DESIGN that references (does not rebuild) the pri-1 generative world-model. Enumeration denominator = ~45 organs situation_reader.py consumes at read() time (import set reconciled against the actual __init__ flag defaults at :851-923). Every live/dormant/remediated claim reproduced by verification/test_audit_live_standins.py (30/30, pure-disk witness)."
floor: "The strongest prior map actually run = the strategy first-pass BRAIN_FOUNDATIONAL_AUDIT.md sec.2b CONT-28 defect list. The catalog BEATS it: it recovers EVERY CONT-28-named component (positive control, witness W11 -- no silent miss), and CORRECTS 5 that the disk has moved past or mis-scoped (spaCy purge in perceptual_access_ledger/causation_typing already landed; context_grounded_valence FORCE_CLASS_HARM_REAL already retired; state_register + location_register WordNet fallbacks already landed; cleanup_family/hd_fact_store DORMANT wrt the reader not 'live via gap_detector'; coref name-Jaccard misattributed to a dormant module), and ADDS the self-containment-at-inference entry (C4) CONT-28 missed."
controls: "(1) LIVE-vs-DORMANT grep of situation_reader's import closure per item (witness W3/W7/W8/W9 -- excludes landed-not-live false positives: caught cleanup_family, gap_detector, hd_fact_store, coreference_resolver, scene_segment cue-detector, incremental_build, graded_parser all built-but-not-wired). (2) Disk RE-VERIFICATION excludes already-remediated items (W10: zero spaCy anywhere in hdlab; W12: state_register _wn_adj_antonyms + location_register WordNet fallback both present). (3) POSITIVE control (W11): the enumeration recovers every CONT-28-named component present on disk -- a can-fail check the catalog is not a shorter list than the prior map. (4) NEGATIVE / do-not-over-fire control: zero admissible static-foundation assets flagged (the affect + state/space cluster audits returned no false positives among WordNet/FrameNet/norm lexicons -- each verified to feed a separately-stated PINNED decision rule, not to BE the decision)."
files_changed: "verification/test_audit_live_standins.py (30/30 witness); notes/problems/audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements/CATALOG.md (the deliverable); .../PARSER_SIGNAL_TRACE.md (per-signal accuracy + per-consumer binding-constraint + generalization); experiments/exp_parse_confidence_shape_vs_magnitude_ood_v1.py (the OOD-confidence drill, metrics.json); .../SOLVED.md. NO hdlab/ writes (Q111 -- strategy lands any code change; this is a MAP + proposed fixes + one brain-foundational drill)."
reverify: ".venv/Scripts/python.exe verification/test_audit_live_standins.py"
---

# Breadth audit — the live reader's non-brain-foundational stand-ins

**The deliverable is `CATALOG.md` in this folder** (11 entries, five fields each, top-K, the parser-cluster replacement
design, the admissible-list, the positive control). This SOLVED.md is the summary + provenance + the required sections.

## What I built
- A disk-verified enumeration of the LIVE reader's consumption graph: every organ `hdlab/situation_reader.py` imports at
  read() time (module-level + lazy-in-method), reconciled against the ACTUAL `__init__` flag defaults (`:851-923`) rather
  than the inline comments — because several comments say "default OFF" while the signature is `True` (the stale-comment
  trap; catalogued, and it is itself why prior audits mis-scoped items). ~45 consumed organs, each checked.
- A prioritized `CATALOG.md`: **8 LIVE non-brain-foundational stand-ins** (C1 gold-coref-inheritance leak; C2
  `situation_predict` string-identity binder; C3 arc-eager surface-feature scorer; C4 `experiments/*` imported at
  inference; C5 `parse_confidence` fitted logistic + pure-defer; C6 `context_grounded_valence` cert-fit governor
  perceptron; C7 `cleanup_family` attractor-as-ranker; C8 `hd_fact_store` junk facts) + **3 located-negatives/corrections**
  (C9 `coref` name-Jaccard misattribution; C10 `scene_segment` dead-window; C11 `polarity_operator` surface-vs-parsed).
- The **parser-scorer cluster replacement design** (4 moves: globally-normalized Matrix-Tree posterior → commit-not-defer
  → graded-competition joint settle on the bounded incremental substrate → close the recurrent predictive-coding loop =
  pri-1). It references the posted pri-1 generative world-model as the convergent deep fix and does NOT rebuild it.
- A pure-disk witness `verification/test_audit_live_standins.py` (30/30) so the catalog's live/dormant/remediated claims
  are machine-checkable on the current bytes — not a keyword-grep list.

## What I measured (the verified, load-bearing facts)
- **C1 gold leak — the #1 blast, confirmed first-hand at the line level:** `situation_reader.py:4079` stashes the gold
  CoNLL coref column; `:3844` reads the gold cluster IDs; `:3854-3855` majority-votes them; `:3856-3861` overwrites the
  live clusters; `:4090` builds `sm.entities` from them. LIVE (`commonnoun_situation_gate=True`, `:914`). Masks C3
  experiencer honest-0.1548 vs leaked-~0.80. Already owner-ruled a leak and filed as pri-6.
- **C3 arc-eager is the sole head source** for the default wired who-did-what/theme/obl path (`:2031-2051`,
  `parser_arceager=True`); its brain-faithful replacements — `incremental_build` (measured +0.0352 F1 superior) and the
  `graded_parser` Matrix-Tree marginals — are both DORMANT (neither symbol appears in `situation_reader.py`).
- **C4 self-containment** spans ≥5 live read()-path sites (`context_grounded_valence.py:61-64` module-level;
  `situation_reader.py:2335/2351/2378/2436`; `temporal_reasoner.py:54-55`) — while many other organs deliberately
  byte-copy to avoid the import, so the standard is known and this is a genuine, fixable debt.
- **C5/C6 are live-computed but decision-inert:** `parse_confidence`'s logistic runs every event but its defer never
  fires (`precision_weight_tau=None`, gated `if ... and tau is not None`); the `context_grounded_valence` governor
  perceptron runs but its output is discarded by the reader's `_assign_affect` event-stage gate (`:840-841`).

## What I did NOT establish (honest bounds)
- I did NOT re-measure the board dims each defect masks — I quote the already-landed measurements (C3 experiencer
  0.1548/0.80 from the crosstype wire; `situation_predict` 0.4904 < string-identity 0.5412 from the typed_coref analysis;
  polarity 0.9091<0.9318 from the parsed-EWT metrics). The catalog's job is the MAP + the live-status proof, not fresh
  capability numbers.
- I did NOT build any replacement — per Q111 and the brief, re-architectures become their own follow-ons; I named the
  organ/mechanism for each. The parser-cluster design is a DESIGN, validated only insofar as its pieces are
  already-built-and-measured or PINNED.
- **Scope caveat, stated honestly:** the enumeration denominator is `situation_reader.read()` (the brief's LIVE reader).
  C7/C8 (`cleanup_family`, `hd_fact_store`) are DORMANT wrt that reader but LIVE in a SEPARATE live pipeline — the
  grounding/foundation-acquisition subsystem (`reading_grounding_loop.py`, `substrate.py`). I catalogue them with that
  precise blast attribution; a fuller audit of that second live entry point is a named follow-on.

## What I would withdraw first if wrong
The C7/C8 "dormant wrt the reader" verdict — it rests on `situation_reader.py`'s import closure not naming them (witness
W7). If a lazy/dynamic import reaches them on some non-default flag path I did not exercise, they would be live-in-reader
and their rank would rise. (I checked the default-flag call graph; I did not exhaustively execute every off-by-default
branch.) Everything in C1-C6 is anchored to a `situation_reader.py` line on the default path and reproduced by the witness.

## KEY REALIZATIONS (the enabling moves, per the owner's instruction)
- **The disk had moved hard under the brief — checking it first was the whole game.** Three of the brief's named "LIVE"
  defects were already remediated in the last 72h (spaCy purge, `FORCE_CLASS_HARM_REAL` retirement, state/location
  WordNet fallbacks). Re-verifying every claimed defect against current bytes BEFORE cataloguing turned a stale list into
  an accurate one — and is exactly the "brief goes stale" risk the protocol names.
- **"LIVE" has three distinct failure modes, and conflating them mis-ranks the work.** (i) live-and-defective (C1-C3);
  (ii) live-COMPUTED but decision-inert (C5 defer dead, C6 output discarded) — a fitted stand-in still executing but
  moving no number, so it is an efficiency/hygiene fix, not a capability blocker; (iii) DORMANT-wrt-this-reader but live
  in another pipeline (C7/C8). Only (i) earns top rank. The `__init__`-signature-vs-stale-comment check was the tool that
  separated them.
- **The parser cluster is not fixed by a better scorer — the stand-in is the ARCHITECTURE.** Surface-feature scoring +
  fitted calibration + abstain are all the same feed-forward, hard-committing, bottom-up error; the brain parses by
  constraint-satisfaction with top-down feedback. The replacement therefore CONVERGES on pri-1 (the recurrent generative
  loop supplies the top-down expectation that resolves the two-valid residual) — the same loop the arc-eager SOLVED, the
  front-end audit, and the pri-1 brief each named independently.
- **The do-not-over-fire discipline is a real control, not a caveat.** Distinguishing a hand-lexicon that SUPPLIES
  knowledge (admissible — the brain has that knowledge) from one that IS the decision (a blocker) kept ~7 lexicon organs
  off the defect list; the parallel-cluster audits returned zero static-foundation false positives.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b — strategy re-verifies + folds in)
1. **CONT-28 corrections (disk outranks the map):** `context_grounded_valence` should be re-verdicted — the
   `FORCE_CLASS_HARM_REAL` hand-list is RETIRED (→ `force_dynamics_valence`) and the cert-fit governor perceptron is
   DECISION-DEAD (discarded by `_assign_affect` at `situation_reader.py:840-841`); the genuine residual there is the
   `experiments/*`-at-inference self-containment import (C4), not the list or the perceptron. `perceptual_access_ledger`
   + `causation_typing` spaCy: PURGED (zero spaCy in hdlab, witness W10) — remove from the live-fail list.
   `cleanup_family`/`hd_fact_store`: NOT "live via gap_detector" wrt `situation_reader.read()` — DORMANT there, LIVE only
   in the grounding-acquisition subsystem (reattribute the blast). `coref` "name-Jaccard": misattributed — the Jaccard
   matcher is in the DORMANT `coreference_resolver.py`, not `coref.py`. `scene_segment` fixed-window: numerically DEAD
   under `graded_pick=True` (not a live proxy).
2. **NEW deviation (C4):** the live reader is NOT self-contained — it imports `experiments/*` scratch cells at inference
   on the default path (`context_grounded_valence`, `_space_reader`, `_belief_reader`, `_temporal_order_register`,
   `_forward_prediction_live`, `temporal_reasoner`). A reproducibility gate-violation (a clean `hdlab/` checkout fails to
   import the reader), fixable by the established VERBATIM-promotion pattern.
3. **Sharpened verdict (C3/C5):** the arc-eager scorer's fix is not a better scorer — it is the graded globally-normalized
   posterior + commit + top-down loop (pri-1). The `graded_parser` Matrix-Tree marginals and `incremental_build` are the
   built-but-DORMANT ingredients.
4. **NEW DRILL (2026-09-09) — the parser-CONFIDENCE OOD collapse is the frozen weights, not the readout.** Building the
   full parser signal trace (`PARSER_SIGNAL_TRACE.md`) surfaced that the parse-reliability signal reads AUC ~0.82
   in-domain but ~0.55 OOD. I hypothesized (Hale precision) the posterior's SHAPE (entropy) would be register-robust
   where its MAGNITUDE is not, and tested it fair (`exp_parse_confidence_shape_vs_magnitude_ood_v1.py`): **REFUTED at
   power** (QA-SRL n=8173) — in-domain MAGNITUDE 0.775 > SHAPE 0.62; OOD BOTH collapse (MAGNITUDE 0.548 [0.534,0.563],
   SHAPE 0.536 [0.522,0.549], twin 0.502). The whole frozen posterior is miscalibrated off-register → the brain-faithful
   fix is CONTINUOUS/ADAPTIVE parsing (online, never-frozen — the project invariant) + top-down constraints (pri-1), NOT
   a static confidence readout. A rigorous located negative that corrects my own trace-doc line and converges on C3.

## TLDR (plain English)
I hunted through the part of the system that reads text and builds meaning, and made one ranked list of every place it
takes a convenient shortcut instead of working the way a brain does. I found eight real shortcuts that are switched on
right now. The worst by far: when the reader groups repeated mentions of a person, it secretly peeks at the answer key
that came with the practice text — so several of our scores are inflated, not earned. The next two: the part that decides
which words attach to which is a plain pattern-matcher with no understanding feeding back into it, and the part that
groups common nouns ("the boy", "the child") just matches identical words and actually does worse than the dumbest
possible method. A few more are switched on but harmless (they run and their answer is thrown away — wasted effort, not
wrong answers), and a couple that an earlier note called live turned out to be asleep in this reader (they're only awake
in a different part of the system). For the biggest cluster — the attaching-words machinery — I wrote out exactly how a
brain would do it instead (keep all the options open, commit to the best one, and let an expectation of what the sentence
is about feed back and help), and showed that this is the same "imagine the story forward" engine already queued as the
project's number-one job. I did NOT fix anything (that's a separate lane) and I was careful not to flag dictionaries and
knowledge lists as shortcuts — the brain has knowledge too; the shortcuts are the guessing done while reading.

## QUESTIONS
None blocking. One scoping choice worth confirming at integration: the catalog's denominator is the `situation_reader`
reading path; the grounding/foundation-acquisition pipeline (`reading_grounding_loop.py`/`substrate.py`) is a SECOND live
entry point where C7/C8 are actually live — I named it as a follow-on rather than expanding scope mid-audit.

## NEXT STEPS (the re-architectures this catalog seeds — each a properly-scoped follow-on for strategy to file)
1. **C1 gold-coref de-leak** — already filed pri-6 (`replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering`); the precondition for every downstream entity/experiencer/meaning gain to show a LIVE number.
2. **The parser-scorer cluster (C3/C5)** — LAND the local moves now (Matrix-Tree marginals + commit + drop the logistic; the obl-spatial promote module already packages the commit), then close the loop via pri-1. Converges on the posted pri-1 generative world-model — do not duplicate.
3. **C2 `situation_predict` → `typed_coref` binding** for the CLUSTERING consumer (not just the parallel resolution field); de-restrict the person-gate. Payoff is leak-masked until C1 lands.
4. **C4 self-containment promotion** — promote the load-bearing functions of the ~6 `experiments/*` cells the reader imports live into `hdlab/` (mechanical; the standard is already followed elsewhere). A hygiene/reproducibility fix, not a fidelity one.
5. **C7/C8 grounding-subsystem audit** — a breadth pass over the SECOND live entry point (`reading_grounding_loop.py`/`substrate.py`) where the attractor-ranker and the 66%-junk fact store are actually live.
