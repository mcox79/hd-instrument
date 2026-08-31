---
priority: 2
review:
review_text:
---

# PROBLEM: the reader's extraction is a BATCH pipeline (tag → batch UD dependency parse → gate) that OVER-GENERATES arguments (+1.03 args/predicate vs gold), so extraction PRECISION is gated on parser fidelity — the just-landed keystone (`the_extraction_front_end…`, p1) proved the precision fix "works at gold accuracy, not at UAS 0.79", and named ONE lever with THREE payoffs: detection precision, copular/nominal recall, and the who-did-what role gap all need an incremental, integrated structure-builder. The brain does NOT parse in a batch: it builds structure INCREMENTALLY, left-to-right, under a bounded buffer, jointly projecting a verb's argument slots as the words arrive (left-corner; Now-or-Never; LIFG/pSTS). An `hdlab/incremental_parser.py` organ ALREADY EXISTS and beats the batch UD parse +0.0352 F1 via precision — but it is an ISLAND (the live reader never calls it; it still uses the over-generating batch parse). WIRE the incremental parser in as the reader's CANDIDATE SOURCE (behind a flag) and PROVE, END-TO-END through the live reader, that it delivers the three payoffs at REAL recall (with the new `tense_agnostic_events` flag ON) without regressing recall.

**slug:** `wire_the_incremental_parser_as_the_reader_extraction_front_end` — **opened:** 2026-08-31 by the strategy
session (the p1 keystone's honest bound: "the precision fix is gated on PARSER FIDELITY… the faithful fix is the
incremental/integrated argument-structure parser — one lever, three payoffs"). **status:** OPEN — a WIRE + END-TO-END
VALIDATION problem (the organ is built; this is compose-into-the-reader + measure the payoffs). You build + validate
the composition in `experiments/`; strategy lands the hdlab wire (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` — HIGH. It is the direct continuation of the
> just-landed keystone: p1 fixed detection RECALL (0.33→0.95) but its precision fix is CAPPED by the batch parser's
> over-generation, and the same parser gap caps role assignment (the who-did-what non-canonical gap) and blocks
> copular/nominal recall. One lever moves all three, and it is North-Star-central (a cleaner extraction foundation).
> Ranked above the knowledge-store consistency-cleanup (p4, the ALREADY-IN clean-foundation half) because it is the
> GOING-IN precision half and the organ already exists (fastest high-leverage win). **Re-rank per the owner.** ⚠️ The
> organ is validated ONLY in ISOLATION (+0.0352 F1); this problem is the phase-gate the p1 result explicitly warns
> about — does the isolation win SURVIVE the live reader at real recall?

> **STRATEGY NOTE (2026-08-31 component scan — a transitive payoff + one caveat):** `incremental_parser` imports
> `hdlab/predictive_reader.py` (the forward-prediction organ: verb+role → expected-argument selectional preference,
> PINNED — Altmann & Kamide / McRae). `predictive_reader` is currently an ISLAND reachable ONLY through this parser,
> so wiring the parser BRINGS THE FORWARD-PREDICTION SIGNAL LIVE too — a BONUS payoff beyond the three named ones: the
> selectional-preference prediction disambiguates competing post-verbal nominals, which targets the two-animate
> who-did-what gap (`the_live_front_end_mislabels_who_did_what_to_whom`). Measure that as a 4th payoff if it fires.
> ⚠️ CAVEAT: `predictive_reader` predicts in the COARSE grounded space (its own ceiling — grounded_similarity caps
> sofa/couch = apple/orange = dog/cat at 0.45), so the prediction's discriminative power is grounded-space-limited; a
> richer feature basis (the now-wired conceptual channel / a distributional space) would sharpen it — note it, do not
> chase it here (keep this problem scoped to the parser wiring).

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
To find "who did what to whom", our reader first tags the words, then runs a whole-sentence grammar parse, then filters
— three separate stages, so a mistake early is amplified late, and the parse hands the reader too many candidate
arguments (about one extra per verb). The brain doesn't wait for the whole sentence: it builds the sentence's structure
as it reads, word by word, guessing each verb's slots and filling them on the fly under a tiny memory buffer. We already
built a reader that does this and, tested on its own, it's more precise than the batch parse. But the live reader never
uses it. Plug it in as the source of candidate arguments and show — reading real text end to end — that it makes the
reader more precise about roles, catches "X is a Y" style events it currently misses, and doesn't lose events.

## 2. WHY THIS ONE
The keystone we just landed (tense-agnostic detection) took event RECALL from a third to nearly all — but its own honest
finding is that the remaining PRECISION and ROLE errors are gated on the batch parser, which over-generates. The same
batch parser is why the reader mislabels non-canonical roles and can't see copular/nominal events. So this is the single
highest-leverage next move on the extraction foundation, and the organ already exists — it just has to be wired and
proven through the live reader (not in isolation, which is where its current +0.0352 F1 lives).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** sentence comprehension is INCREMENTAL and PREDICTIVE — structure is built left-to-right as
  each word arrives, not in a batch (Marslen-Wilson 1973; LIFG-BA44 / pSTS incremental structure-building). A bounded
  working buffer forces immediate commitment (NOW-OR-NEVER; Christiansen & Chater 2016). LEFT-CORNER parsing (eager
  subject bind on seeing the verb, eager patient fill) matches human memory load better than pure top-down/bottom-up.
  Structure-building is SEPARATE from thematic role-binding (Beber 2025) — build candidate structure, THEN label. A
  selectional-preference PREDICTION disambiguates competing post-verbal nominals.
- **OUR-INVENTION (sweep, don't adopt):** the eager-bind heuristics, the buffer size, the revision (garden-path
  reanalysis) policy (default OFF), and the reversible-clause routing to the relcl filler-gap resolver. These are in the
  existing `incremental_parser` organ — inherit them; do not rebuild the parser.

## 4. MEASURED vs INFERRED
- **MEASURED:** `incremental_parser` (BUILT, hdlab) beats the batch UD parse +0.0352 F1 via precision IN ISOLATION; the
  batch parse over-generates +1.03 args/predicate; the reader still imports the batch parse (candidate_generator/
  arc_parser), so `incremental_parser` is a default-off ISLAND. p1 proved extraction precision is parser-fidelity-gated.
- **INFERRED (you must measure):** whether wiring `incremental_parser` as the reader's candidate source delivers the
  three payoffs END-TO-END through `SituationReader.read()` (with `tense_agnostic_events=True`, i.e. at real recall):
  (a) extraction precision up (args/predicate closer to gold), (b) role F1 up (esp. non-canonical who-did-what),
  (c) copular/nominal-predication recall up — WITHOUT a recall regression. The isolation win may or may not survive.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The incremental parser itself (`the_argument_parser_is_batch_where_the_brain_is_incremental`, owner-DONE, EXCELLENT,
  integrated) — it is BUILT and validated in isolation. Do NOT rebuild it; WIRE it and measure end-to-end.
- The tense-agnostic detection RECALL fix (p1, integrated, landed behind `tense_agnostic_events`) — this composes WITH
  it (turn it ON for the measurement); do not re-derive the recall result.
- Batch UD parse / arc_parser as the candidate source — that IS the current over-generating baseline you must beat.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/incremental_parser.py` + its `capability_registry.jsonl` entry (`incremental_parser_v1`, the WIRE_CANDIDATE
  target: "wire as the CANDIDATE SOURCE behind a flag; the role assigner labels the candidates; keep structure-building
  and role-binding SEPARATE; MEASURE on the live reader before any capability claim").
- Read `hdlab/situation_reader.py::_read_events` + `_read_events_wired` (the assembly role path; `role_route != "positional"`)
  and the p1 SOLVED (`the_extraction_front_end…`) — the parser-fidelity honest bound + the new `tense_agnostic_events` flag.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a REAL corpus (UD-EWT for gold structure + LitBank for narrative), through `SituationReader.read()` with
`tense_agnostic_events=True`:
- **PASS =** the incremental-parser-fronted reader beats the current batch-parse-fronted reader CI-separated on AT LEAST
  extraction PRECISION (args/predicate closer to gold) AND role F1, WITHOUT a CI-separated recall regression, with the
  info-free twin (shuffle the incremental candidate order / random same-count candidates) LOSING; report the
  copular/nominal-recall delta as a third payoff (honest even if it is the weakest). Report CI half-width + null p95.
- **A rigorous NEGATIVE is a full PASS:** if the isolation +0.0352 F1 does NOT survive the live reader at real recall
  (the batch parse's over-generation is not the live bottleneck, or the incremental candidates lose recall), name why —
  enumerated — which tells the assembly the parse front-end is not the lever and re-points precision work elsewhere.

## 8. FILES AND ENTRY POINTS
- Compose in `experiments/`: swap the reader's candidate source to `incremental_parser` (behind a flag, mirroring
  `role_route`), keep role-binding separate (the role assigner labels the candidates). Witness recomputes the three
  payoffs from source through the live `read()`. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it
  wins, strategy lands the hdlab wire (Q111, a new default-off `candidate_source` flag). This is the GOING-IN precision
  half of the clean-foundation North Star and a DEBT-2 assembly item (PARSE); it composes with the landed
  `tense_agnostic_events` keystone.
