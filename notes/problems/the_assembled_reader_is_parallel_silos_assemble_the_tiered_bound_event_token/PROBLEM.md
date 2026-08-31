---
priority: 4
review:
review_text:
---

# PROBLEM: the assembled reader is N PARALLEL SILOS, not one integrated situation model — assemble the TIERED BOUND-EVENT-TOKEN backbone (the binding-problem fix). The full-system test (`the_assembled_reader_is_never_tested_as_a_whole_all_flags_on`, EXCELLENT) proved, byte-exactly, that turning all dimension flags ON produces N INDEPENDENT extractors sharing no token: perturbing the event set leaves every other dimension byte-identical (interaction exactly 0). "No regression" was TRIVIALLY true because composition-without-interaction is NOT integration. The precise name of the defect is the BINDING PROBLEM: each dimension stores the MARGINALS (the set of agents / the set of times / the set of causes) but nothing stores the JOINT (which agent goes with which time with which cause). On the real FHRR algebra this dissociates cleanly (joint disambiguation 1.00 + binding-shuffle SENSITIVE; marginal 0.47 chance + shuffle-INVARIANT). And the brain MUST CHUNK: a single passage-level bound register collapses ~1/√M (0.99 at 64 events → 0.12 at 512; a passage has ~100–250), while a SLOTTED multibank register stays flat — so the faithful shared event token is TIERED, not one superposition. Every tier is ALREADY a built hdlab organ, none wired into the reader: `slot_attention_wm` + `situation_model_multibank` (slotted active register), `n400_coherence_monitor` (prediction-error event-boundary segmentation), `hippocampal_encoder` (DG-sparse + CA3 + CLS episodic store). ASSEMBLE them into the reader as a tiered bound-event-token backbone that binds all dimensions onto ONE event token per event, chunked by event boundaries into an active WM register and consolidated to an episodic store — and PROVE it stores the JOINT the silos cannot, on real event-coreference, over a late-fusion-of-marginals baseline, with the binding-shuffle control LOSING.

**slug:** `the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token` — **opened:** 2026-08-31 by the
strategy session (the p4 assembled-reader test's own next-problem: it turned "test the whole" into the binding-problem
finding + the tiered-organ map, and reframed the fix from "build" to "ASSEMBLE existing organs"). **status:** OPEN — an
ASSEMBLE + VALIDATE problem (all tiers are built hdlab islands; this binds them into the reader onto one event token and
proves the JOINT). You build + validate in `experiments/`; strategy lands the hdlab wire (Q111, default-off, witness
required). ⚠️ GATED on the tense-preserving detector landing (`preserve_tense`, LANDED) — the shared token needs real
tense. NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — HIGH, and arguably the highest-leverage
> architectural work in the queue: it is what makes the assembled reader actually INTEGRATED (one bound event token),
> which every downstream capability — especially REASONING (p6, you cannot reason over silos) and the end-to-end
> comprehension win — depends on. Ranked below the learner endgame (live-canary p3) and the prediction-error lever (p2)
> only because those are further along; **strongly consider re-ranking it above p6 (reasoning), which it is a prerequisite
> for.** **Re-rank per the owner.** ⚠️ Compose with the reader's capable flags ON (`python tools/reader_capabilities.py`;
> the CORRECT fully-on baseline is recorded there). Do NOT re-quote DG's prior HARD_FAILs as a ceiling — they were tested
> on the WRONG TIER (active-read, not the episodic store that is DG's faithful job); re-scope.

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
Our reader now tracks a lot about a story — who did what, when, where, why — but it turns out it keeps each of those in a
SEPARATE list that don't talk to each other. It knows "the people are Mary and John," "the times are morning and night,"
"the moves are arrive and leave" — but NOT that "Mary arrived in the morning and John left at night." It has the pieces
but not which-goes-with-which. That "which-goes-with-which" is the whole point of understanding a story, and it's exactly
what the brain binds into a single event memory. Fix it: bind everything about ONE event into ONE linked token, keep a
small handful of recent events active (the brain can't hold the whole story at once — it chunks), and file the rest into
a longer-term memory it can look back into. Then prove it can do what the separate lists can't: tell whether two mentions
of an event are the SAME event (which needs same-who AND same-when AND same-where), beating a baseline that just checks
the separate lists, with a scrambled-bindings version that must fail.

## 2. WHY THIS ONE
It is the difference between "the reader has features" and "the reader UNDERSTANDS." Composition without binding is not
integration; the full-system test proved our reader is the former. Every capability that matters next — reasoning over
the story (you cannot reason over unbound lists), the real comprehension win, answering "what did X do after Y" — needs
one bound, queryable event representation. And the parts are all built; the work is assembling them the brain's way
(bound token, chunked into working memory, consolidated to episodic memory), not inventing from scratch.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate the operation):** comprehension builds ONE bound EVENT TOKEN per event, indexed on all situation
  dimensions simultaneously (Zwaan & Radvansky 1998 event-indexing; SEM / Franklin et al. 2020 — the event model is a
  bound representation, not parallel feature lists). Binding solves the MARGINALS-vs-JOINT problem (the classic binding
  problem; hippocampal conjunctive coding — the amnesia double dissociation). The brain CHUNKS: a small active WORKING-
  MEMORY register holds ~4 bound events (Cowan capacity; slot-based active maintenance — `slot_attention_wm` /
  `situation_model_multibank`), segmented at EVENT BOUNDARIES detected by PREDICTION ERROR (Event Segmentation Theory,
  Zacks 2007; the N400/coherence surprise — `n400_coherence_monitor` as the flush/reset controller), and the flushed
  events CONSOLIDATE into an EPISODIC store for later retrieval (hippocampus DG-sparse + CA3 pattern completion + CLS —
  `hippocampal_encoder`). A single flat superposition is NOT faithful (it collapses ~1/√M at passage scale) — the tiers
  are the fix.
- **OUR-INVENTION (sweep, do NOT adopt as truth):** the exact tier assembly (how the active register hands off to the
  episodic store), the slot count, the boundary-detection threshold, the bound-token codec (which FHRR roles). Glass-box,
  NO LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (INHERIT, do NOT re-derive):** the reader is parallel SILOS (interaction byte-exactly 0; p4). The JOINT-vs-
  marginal dissociation on the real FHRR algebra (joint 1.00 shuffle-sensitive; marginal 0.47 shuffle-invariant — the
  binding-shuffle discriminator is the non-gameable test; a naive constructed proof FAILS at type-cardinality 1). The
  1/√M single-register collapse vs a flat slotted multibank. The tiers exist as built hdlab islands (slot_attention_wm,
  situation_model_multibank, n400_coherence_monitor, hippocampal_encoder).
- **INFERRED (you must measure):** whether ASSEMBLING the tiers into the reader (bound event token → boundary-chunked WM
  register → episodic consolidation + retrieval) stores the JOINT the silos cannot — proven on REAL event coreference
  (same event mentioned twice ⇒ same agent+time+place) CI-separated over a LATE-FUSION-OF-MARGINALS baseline, with the
  BINDING-SHUFFLE control LOSING and the tiered register NOT collapsing at passage scale.

## 5. ALREADY TRIED / DO NOT RE-RUN
- `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on` (EXCELLENT) — INHERIT the silo finding + the FHRR joint
  PoC + the tiered-organ map; do NOT re-derive them. This is the ASSEMBLE + VALIDATE-on-real-event-coref step.
- The tiers are BUILT (slot_attention_wm, situation_model_multibank, n400_coherence_monitor, hippocampal_encoder) —
  ASSEMBLE them; do NOT rebuild. `hippocampal_encoder`/DG's prior HARD_FAILs were on the WRONG TIER (active-read, not the
  episodic store) — re-scope, do NOT re-quote as a ceiling.
- Do NOT "flip more dimension flags on" and call it integration — the p4 test proved that is silos.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the four tier organs + their witnesses; read the p4 cell (`experiments/exp_*assembled_reader*` /
  `verification/test_assembled_reader_all_flags_on.py`) for the silo proof + the FHRR joint PoC + the binding-shuffle
  discriminator + the 1/√M curve. Run `python tools/reader_capabilities.py` (the CORRECT fully-on baseline is recorded).
- ACQUIRE an event-coreference gold: ECB+ (the standard within-/cross-document event coref corpus; free) is named by the
  p4 submission; a small hand-adjudicated same-event set on LitBank is an acceptable start (report n). MIND corpus age.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On real event coreference through the assembled tiered reader:
- **PASS =** the bound-event-token reader resolves whether two event-mentions co-refer (needs the JOINT: same agent AND
  time AND place/cause) CI-separated over (a) a LATE-FUSION-OF-MARGINALS baseline (score the separate dimension lists,
  combine) and (b) a lexical/surface baseline — with the BINDING-SHUFFLE control (permute the within-event bindings; the
  marginals are invariant, the joint breaks) LOSING CI-separated, AND the tiered register NOT collapsing at passage scale
  (the single-superposition 1/√M collapse is the can-fail control the tiers must beat). Report CI half-width + null p95
  beside every margin; glass-box, inspectable bound token.
- **A rigorous NEGATIVE is a full PASS:** if the assembled tiers do not beat late-fusion-of-marginals on real event
  coref, name WHY — enumerated (is it the extraction recall feeding the token [the parser wall], the boundary detection,
  or the binding codec?). That tells the assembly whether the integration gap is the front-end or the binding mechanism.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`: assemble the bound event token (FHRR bind of the dimension fillers) → the boundary-chunked
  slotted WM register (`slot_attention_wm`/`situation_model_multibank`, flushed by `n400_coherence_monitor`) → episodic
  consolidation + retrieval (`hippocampal_encoder`), driven by `SituationReader.read()`; a scaffold-free witness
  recomputes event-coref accuracy + the late-fusion-of-marginals floor + the binding-shuffle control + the passage-scale
  collapse curve from source. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it clears the bar,
  strategy lands the hdlab wire (Q111, default-off): a tiered bound-event-token backbone the dimensions bind onto. This
  is the INTEGRATION the assembly was for — the step from "features" to "understanding."

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the p4 no-regression "interaction = 0" as a good result — it is TRIVIALLY true BECAUSE the dimensions
  are silos; composition-without-interaction is NOT integration.
- 🚫 Do NOT quote DG/hippocampal prior HARD_FAILs as a ceiling — they were on the wrong tier (active-read, not episodic).
- 🚫 Do NOT re-derive the FHRR joint-vs-marginal PoC or the 1/√M curve — inherit them; this is the REAL-event-coref test.
- 🚫 Do NOT use a JOINT proof at type-cardinality 1 (the joint is recoverable from the marginals there — a design
  artifact); the non-gameable discriminator is BINDING-SHUFFLE invariance.
