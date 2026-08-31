---
priority:
review: EXCELLENT
review_text: Diagnoses the reader's ~0.33 event-detection recall to a single defect -- the live detector (T.extract_events) is TENSE-GATED and misses present-tense finite verbs (VBZ/VBP) 100% -- and fixes it with a brain-faithful, tense-agnostic UPOS==VERB detector (in-substrate UD tagger, NO LLM). Reverified 11/11 FIRST-HAND: end-to-end through the LIVE SituationReader.read() event recall 0.381->0.966 (+0.585), and it GENERALIZES OOD on pre-existing gold -- modern QA-SRL 0.373->0.836 and 19c LitBank 0.533->0.740, CI-separated on all three, two info-free twins losing (~0.15). Precision is neutral (RULE variant, gold-POS 0.9977->0.9985) / improves in-domain (0.911->0.941). This is THE keystone: it de-risks the whole assembly (every downstream dimension reads off the event set). Landed the detector behind a default-OFF `tense_agnostic_events` flag (witness: off byte-identical 104 events; on 104->219 2.11x through the canonical reader). EXCELLENT: rigorous diagnosis + OOD-generalizing fix + end-to-end + strong controls + self-corrected its own generalization-cell artifact + honest bounds (copular/nominal predications NOT fixed; precision gated on parser fidelity -> the incremental parser is the one-lever-three-payoffs follow-on; the precise_voice role wire measured through SYNTHETIC mentions -> QUEUED for full-reader validation).
---

> ## ✅ SOLVER REVIEW -- EXCELLENT (integrated by strategy 2026-08-31)
> **Why EXCELLENT, specifically:** it turned a vague "recall is a third" into a single, named, brain-faithful
> defect and fixed it. The reframe is the move: the detector gated on TENSE and missed present-tense finite verbs
> 100% (0/560) -- and the drill showed the brain detects predicates from LEXICAL CATEGORY, tense-agnostically
> (neo-Davidsonian event variable; LIFG/pMTG structure-building references no tense), with PAST being the harder,
> discourse-linked form -- so the detector "gated on exactly the tense the brain finds easier." The fix is a pure
> UPOS==VERB detector on the in-substrate UD tagger (no LLM). Crucially it GENERALIZES: measured on THREE
> pre-existing golds -- UD-EWT, modern QA-SRL (genre change), 19c LitBank (century change) -- CI-separated on all,
> with LitBank's HIGHER current recall (0.533) independently confirming the past-tense-tuning diagnosis. And it was
> validated END-TO-END through the actual SituationReader.read() (0.381->0.966), not gold-fed isolation, with two
> info-free twins losing and a precision control (neutral RULE / +0.030 in-domain REALIZED).
> **Reproduced under my check:** I re-ran `verification/test_extraction_frontend_recall.py` -- 11/11 PASS,
> scaffold-free; A (0.3317), C (+0.1704 precision-neutral), D (0/560 present-tense missed), E1/E2/E3 (OOD
> generalization CI-sep), F (who-did-what 0.2887->0.7461), G (end-to-end 0.4161->0.9463), H/I (precise_voice through
> the real hdlab _assign_roles) all reproduce from source. And my landing witness confirms the flag: default-off
> byte-identical, flag-on 104->219 events (2.11x) through the canonical reader.
> **The honest docks it volunteered (none fatal):** copular/nominal predications are NOT fixed (UPOS==VERB excludes
> them -- a named next problem); precision at REALIZED taggers dips OOD on QA-SRL (a documented LOWER bound -- QA-SRL
> under-annotates verbs); the precision fix is GATED ON PARSER FIDELITY (works at gold accuracy, not UAS 0.79) -> the
> deeper lever is the incremental/integrated argument-structure parser ("one lever, three payoffs"); the precise_voice
> role wire was measured through the real hdlab role organ but with SYNTHETIC one-per-nominal mentions, not full reader
> mentions. It even self-corrected a measurement artifact (the generalization cell's apparent -0.06 precision was
> giving CURRENT gold POS while giving FIX the learned tagger).
> **What I landed vs queued:** LANDED the tense-agnostic detector behind a default-OFF `tense_agnostic_events` flag
> (byte-identical off; witness `test_tense_agnostic_events_organ.py`), with an HONEST boundary -- it assigns a
> placeholder tense, so the TIME/timeline dimension must not consume it until a tense-preserving variant is validated.
> QUEUED (not landed): the `precise_voice=True, toks=` wire into `_read_events` (the synthetic-mention caveat -> needs
> full-reader-mention validation first, a phase-gate). This is the KEYSTONE for the assembly (DEBT 2): every dimension
> wiring reads off the event set, so turning this flag on is the prerequisite to re-measuring the assembly at real recall.

# PROBLEM: the reader's EXTRACTION FRONT-END recovers only ~1/3 of the events and roles in real text, and it caps EVERYTHING downstream — every organ win we have was measured with GOLD extraction handed to it. The generalization stress-test (`stress_test_which_organ_wins_actually_generalize_on_held_out_text`, integrated) made this the flagged #1 lever: "every retrieval/who-did-what number used GOLD extraction; end-to-end the front-end dominates; the robust full solution needs the front-end addressed before any of the above lands as a live-reader gain." The archetype measurement: event/role extraction recall ~0.32 on real SimpleWiki. So the live reader, reading raw text, misses ~2 of every 3 events/roles before any comprehension organ runs — which means our real end-to-end comprehension is bounded far below the organ-level numbers, and it is the ONE bottleneck that, if moved, lifts every dimension at once (who-did-what, coref, causation, QA). This is also the North Star's "narrative extraction → clean foundation" link: a noisy extraction front-end IS the noisy foundation the learner cannot yet grow on. Diagnose WHERE the ~0.32 recall is lost (event detection? argument attachment? role assignment? coref-gated mention linking?), then BUILD the highest-leverage fix, measured on a pre-existing gold, CI-separated over the current live extractor, with the info-free twin LOSING.

**slug:** `the_extraction_front_end_recovers_only_a_third_of_events_and_roles` — **opened:** 2026-08-30 by the strategy session
(the generalization stress-test's flagged BIGGEST LEVER). **status:** OPEN — a MECHANISM + BUILD problem (the upstream extraction
pipeline). You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1` — the HIGHEST-leverage problem in the substrate right now.
> It is the ONE upstream bottleneck that gates every downstream organ's REAL (non-gold) payoff, the generalization audit's own #1
> recommendation, and the North Star's clean-foundation link. Above the in-flight reader-fidelity problems because those improve
> ONE dimension each while this lifts the ceiling on ALL of them. **Re-rank per the owner.** ⚠️ SCOPE-FIRST: the first deliverable
> is the DIAGNOSIS (which stage loses the recall), because the fix depends on it — do not assume it is the parser.

> ## 📩 STRATEGY UPDATE — 2026-08-30 (a directly-relevant finding landed AFTER you started; READ THIS)
> The integrated `grounded_role_assignment_via_verb_keyed_thematic_fit` (rigorous negative, STRONG) is effectively a
> DIAGNOSIS of one stage of THIS problem. Its findings, verbatim, so you don't have to re-derive them:
> - **The non-canonical ROLE-assignment collapse is a PARSE-QUALITY problem, not a thematic-fit problem.** A grounded
>   thematic-fit + conflict gate was built and refuted: on clean parses structure/routing already wins; on weak parses the
>   fit gate has an IRREDUCIBLE canonical tradeoff. Do NOT re-open thematic-fit-vector work / a post-hoc fit gate /
>   fused-linear-precision combinations (all fenced dead-ends there).
> - **A modern dependency parser (spaCy, substrate-native, NO LLM) scores structural roles 0.9959 balanced non-canonical**,
>   dominating word-order, the landed `graded_role_assigner`, and every fit gate — the admissible-interim CEILING for the
>   role stage. If your per-stage diagnosis (§6) shows the role/attachment stage is a major recall loss, THIS is the ceiling
>   to close toward.
> - **The brain-faithful target is an INCREMENTAL, cue-integrated PREDICTIVE structure-builder** (Lewis-Vasishth / MacDonald /
>   Levy — order + morphology + thematic fit competing DURING attachment, fit ONLINE not post-hoc). A ready-made 8-section
>   brief for it exists: `notes/problems/grounded_role_assignment_via_verb_keyed_thematic_fit/FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md`.
>   If your diagnosis confirms the role/parse stage is the dominant loss, that IS the build; if the loss is elsewhere (event
>   detection / coref-gated linking), say so and the incremental-parser becomes a separate problem.
> - A small landable side-fix already validated in isolation: restricting `graded_role_assigner`'s structural override to
>   RELIABLE strong-passive markedness (+0.081 aggregate, fit-independent) — but it needs END-TO-END live-reader validation
>   (the phase-gate trap), which is exactly this problem's job.
> **Also see `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the grounded-role entry).**

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
Every clever "brain part" we've built is graded on a test where a perfect assistant first hands it a clean list of the events
and who-did-what in the sentence. But when the reader has to pull those events out of raw text ITSELF, it only catches about
one in three. So the real reader — reading a real page — is missing most of what happens before any of the smart parts even
get to run. That's why our end-to-end results are so much weaker than the individual part-scores suggest. Fixing the part
that reads events out of text is the single change that helps everything downstream at once. First figure out exactly where
those two-in-three go missing, then build the fix.

## 2. WHY THIS ONE
It is the audit-identified #1 lever and the North Star's clean-foundation link. Every other queued problem improves ONE
comprehension dimension on GOLD inputs; this lifts the ceiling on ALL of them on REAL inputs. A noisy extraction front-end is
literally the "noisy foundation" the learner is being held OFF from growing on — so this is the same problem as "make the
substrate extract clean knowledge." Nothing else in the queue compounds this broadly.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** event/predicate–argument extraction in the brain is incremental syntactic parsing (LIFG/pSTS) feeding
  thematic role assignment (posterior temporal / inferior parietal; the Competition Model cue-integration + the graded
  cue-based retrieval the substrate already pins), gated by referential/coref linking of mentions to entities (the situation
  model). The recall loss is a FIDELITY gap in one of those stages, not a ceiling.
- **OUR-INVENTION (flag + sweep):** whatever specific detector/attacher/booster you add; thresholds; any lexicon. Glass-box,
  no external LLM. If the faithful fix is a better incremental parser vs a role-recall booster vs a coref-gated re-linker, the
  DIAGNOSIS decides — say which stage and why.

## 4. MEASURED vs INFERRED
- **MEASURED (the constraint):** event/role extraction recall ~0.32 on real SimpleWiki (the archetype); every integrated organ
  number used GOLD extraction (the audit's central caveat). The gap between organ-on-gold and organ-on-live-extraction is the
  prize.
- **INFERRED (you must measure):** WHERE the ~0.32 is lost (event detection vs argument attachment vs role assignment vs
  coref-gated mention linking), and whether the highest-leverage brain-faithful fix raises real event/role recall CI-separated
  over the current live extractor without wrecking precision.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The incremental left-corner arg-structure builder (`the_argument_parser_is_batch_where_the_brain_is_incremental`, integrated
  HOLDS on QA-SRL 28k) — a validated identification gain; BUILD ON it, do not redo it.
- `the_reading_extractor_may_not_beat_a_two_line_rule` (a role-assignment negative on QA-SRL 17k) — the elaborate perceptron
  LOSES to a two-line word-order+voice rule; do not re-run that arm; it says the ROLE stage's fancy version is not the lever.
- The archaic-prose parse confound is RETIRED (spaCy subject-ID is not CI-degraded on 19c prose) — corpus-age is not the cause.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Reproduce the ~0.32 recall: run the live extractor (`situation_reader._read_events` → `experiments._temporal_ordering.extract_events`,
  + `predicate_argument_frontend` + `thematic_role_labeler`) against a pre-existing gold (QA-SRL / LitBank / UD-EWT) and report
  the per-stage recall (events detected → arguments attached → roles assigned → mentions linked). The DIAGNOSIS is the first deliverable.
- Read the two integrated parser/extractor results (§5) so you build on the identification gain and avoid the role-perceptron dead end.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a pre-existing gold (QA-SRL / LitBank / UD-EWT; MIND THE CORPUS-AGE CONFOUND — prefer modern where possible):
- **PASS =** the fixed extraction front-end raises real event/role RECALL on the diagnosed-lossy stage, CI-separated over the
  current live extractor (bootstrap; CI half-width + null p95), WITHOUT a CI-separated precision regression, with the info-free
  twin (shuffled cues / permuted attachment) LOSING; AND show ONE downstream organ's end-to-end number improves when fed the
  better extraction (the point of the whole thing).
- **A rigorous NEGATIVE is a full PASS:** if the recall is lost at a stage that a faithfully-built fix cannot move (e.g. it is
  genuinely a coref/world-knowledge bottleneck), name the stage + why, enumerated — that redirects the whole substrate.

## 8. FILES AND ENTRY POINTS
- Live extractor: `hdlab/situation_reader.py` (`_read_events`), `experiments/_temporal_ordering.py` (`extract_events`),
  `hdlab/predicate_argument_frontend.py`, `hdlab/thematic_role_labeler.py`, the coref path.
- Golds: `data/corpora/` (QA-SRL, LitBank, UD-EWT). Build + validate in `experiments/`; witness recomputes per-stage recall from source.
- Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the extraction-recall diagnosis + the stage fixed). This is the
  gate on every organ's real-text payoff — coordinate with the assembly + the QA measurement instrument.


## DO NOT QUOTE / DO NOT REDO
- 🚫 This problem is INTEGRATED — the honest result + caveats are in `review_text` (frontmatter) and `INTEGRATED_BY_STRATEGY` (SOLVED.md). Do NOT quote its numbers across a different scorer / population / representation (standing rule: no number crosses scorers or populations); recompute every floor on the target item's own population.
- 🚫 The direction is CLOSED for re-derivation — build ON it, do not re-run it.
