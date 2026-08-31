---
priority:
review: STRONG
review_text: Replaces the keystone's placeholder tense with a REAL compositional Reichenbach parse (tense × aspect × voice) of each verb group, while preserving recall EXACTLY — the strongest possible no-regression: the event-index set through the live SituationReader.read() is byte-identical (219 events), tense goes from one constant label to 9 real ones. Reverified 12/12 FIRST-HAND. In-substrate word-tense 0.770 [0.7551,0.7856] CI-separated over placeholder 0.2955 / majority 0.3974 / shuffled-twin 0.3356; clausal ASPECT 0.987 and VOICE 0.933 (compositional content no word-tense label carries); FINITE clausal-tense 0.860 (the temporal anchors); every-event effective temporal location 0.712 [0.6945,0.7306] CI-sep over floors, twin losing. The mechanism is brain-faithful and PINNED (two literature drills): detection stays tenseless (neo-Davidsonian event variable); temporal LOCATION is a SEPARATE compositional parse of main-verb + auxiliary chain into a Reichenbach triple, reading the same morphosyntax the language network reads. The brief's negative hint (extra present-tense verbs unrecoverable) is REFUTED (VBZ 1.00, VBP 0.87); the real weak spot — bare infinitives/gerunds — was shown to be a CATEGORY ERROR not a bug: non-finite forms carry no independent tense and INHERIT it from the controlling finite verb (sequence-of-tense; Ogihara/Abusch), and MARK-AND-INHERIT lifts non-finite 0.337→0.674→0.876-with-the-gold-controller (matching the finite ceiling) — so the frame is correct and the entire residual is anchor-finding. PAYOFF (the point): fed to the timeline reconstructor the unified detector reproduces the flashback past-perfect signal (is_pp agreement 0.988), recovers 300+ events the narrow timeline extractor drops, and BEATS the stock path on a flashback gold (1.00 vs 0.88) — so the reader can finally have ONE complete event set that ALSO serves the TIME dimension (already landed). Generalizes to the train split (finite tense 0.912; not fit to any corpus). Grade STRONG: the bar (recall preserved + real tense beating floors CI-sep + twin losing) is fully cleared with brain-faithful compositional machinery, a dissolved "wall," cross-split generalization, and a real payoff to the landed timeline — held just below EXCELLENT because the single most-impressive number (word-tense 0.909) uses a separable NLTK fine-tag (the pure-in-substrate core is 0.770, itself CI-sep) and the timeline payoff rests on a small 8-item constructed flashback gold; both honestly flagged.
---

> ## ✅ SOLVER REVIEW -- STRONG (integrated by strategy 2026-08-31)
> **Why STRONG, specifically:** it turned the keystone's placeholder tense into real WHEN-content the way the brain
> does — event detection stays tenseless (neo-Davidsonian), and temporal location is a SEPARATE compositional parse of
> the verb group into a Reichenbach tense × aspect × voice triple (Reichenbach 1947; Zwaan & Radvansky TIME) — and it
> preserved recall EXACTLY (the event set through the live read() is byte-identical; tense goes from one constant to
> nine real labels). That exact recall-preservation is the strongest form of no-regression, and the aspect/voice
> (0.987/0.933) is genuine content no single tense label carries. The deepest result is that the apparent "wall"
> (non-finite forms) was a CATEGORY ERROR, not a bug: non-finite verbs carry no independent tense and INHERIT it from
> their finite controller (sequence-of-tense), and mark-and-inherit takes them 0.337→0.674→0.876-with-the-gold-anchor,
> matching the finite ceiling — the residual is anchor-finding, not the frame.
> **Reproduced under my check:** re-ran `verification/test_tense_preserving_event_detector.py` — 12/12 PASS,
> scaffold-free, recomputed from UD-EWT gold + the live reader. Word-tense 0.77 [0.7551,0.7856] CI-sep over placeholder
> 0.2955 / majority 0.3974 / twin 0.3356; aspect 0.987, voice 0.933; finite clausal-tense 0.860; effective temporal
> location 0.712 CI-sep, twin losing; recall preserved (219 events identical, 1→9 tenses, W9); is_pp agreement 0.988 +
> 303 extra events (W10); flashback reconstruction 1.00 vs stock 0.875 (W11) — all reproduce from source.
> **Adversarial audit (what could have faked it):** (1) Is the tense win just a corpus-fit? No — the fixed composition
> holds on the train split (finite 0.912), so it is not tuned to test. (2) Is the recall-preservation claim real? Yes —
> checked structurally: the event-index set through the live read() is identical to the placeholder path (tense is a
> label on already-detected tokens, so preservation is FREE and EXACT). (3) Does the info-free twin help? No — it loses
> CI-separated on both word-tense and effective temporal location.
> **Honest bounds (solver-reported, so they cap nothing):** the 0.909 word-tense headline uses an NLTK fine tag — the
> fully in-substrate surface mode is 0.770 (an admissible separable morphology PARAMETER, not the core); the clausal
> aspect/voice gold is DERIVED from the UD tree (UD-EWT has no Aspect feature); the non-finite surface anchor-finder is
> a proxy (the inheritance FRAME, oracle 0.88, is the robust claim); the timeline payoff rests on is_pp fidelity + an
> 8-item constructed flashback gold (no large temporal-ordering benchmark on disk).
> **Landing (QUEUED, Q111 — COUPLED with p3 into ONE extraction-front-end landing):** replace the placeholder-tense
> line in `_tense_agnostic_extract` with the composed tense/is_pp (validated ref impl `assign_sentence` + `_stock_tense`
> in `experiments/exp_tense_preserving_live_reader_and_timeline_v1.py`), behind the same default-off flag
> (byte-identical off). Then the landed TIME dimension (`timeline_register`) consumes the unified is_pp-faithful detector
> and `EventRecord.tense` becomes real content for every dimension. Follow-on (solver-mapped): rebuild the reader's
> narrow `_read_timeline` (fires only on "had", the marked exception) into a DRT reference-time ordering graph that also
> advances on eventive simple-past clauses — needs a temporal-ordering gold ACQUIRED (MATRES, free on GitHub; none on
> disk).

# PROBLEM: the just-landed tense-agnostic event detector (the p1 keystone) maximised RECALL by firing on every UPOS==VERB — but it assigns a PLACEHOLDER tense (TENSE_SIMPLE_PAST) to every event, throwing away the tense/aspect the TIME dimension needs. Detection was correctly made tense-AGNOSTIC (event-hood is not tied to tense); but tense itself is real situation-model content (WHEN did it happen, before/after, is it ongoing). Build the tense-PRESERVING variant: detect events tense-agnostically (keep the keystone's ~0.95 recall) AND assign each event its correct tense/aspect — so the reader can have ONE complete event set that ALSO serves the TIME/timeline dimension (today the timeline does its OWN separate extraction because it needs real tense the keystone drops).

**slug:** `the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension` — **opened:** 2026-08-31 by the
strategy session (the p1 keystone's own landed boundary note + the TIME-dimension scan, BRAIN_FOUNDATIONAL_AUDIT §2b:
"do NOT consume the tense_agnostic flag for the TIME dimension until a tense-preserving variant is validated").
**status:** OPEN — a MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands the hdlab
change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5`. HIGH-value but an ENABLER, not a master lever:
> it unblocks the SHARED-EVENT-SET architecture (one detector feeding all dimensions, including TIME) and a proper
> temporal-order dimension (the current `_read_timeline` is a narrow "had"-gated flashback proxy that runs its OWN
> extraction). Ranked below the recall/precision master levers (copular-recall p3-new; incremental-parser p2) because
> it refines an already-working detector rather than adding a dimension of recall. **Re-rank per the owner.**

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
We just fixed the reader to catch almost every verb-event, regardless of tense — good, because whether something is an
event doesn't depend on its tense. But in doing so it stamps every event as if it were simple past, throwing away
whether it actually happened, is happening, had already happened, or will happen. That tense information is exactly
what "when did this happen / what came before what" needs. So the timeline part of the reader currently has to redo
the work separately. Fix the detector to keep the recall win AND record each event's real tense/aspect, so one
complete event list can serve both "what happened" and "when."

## 2. WHY THIS ONE
Right now the reader has TWO event extractions: the high-recall keystone (tense dropped) and the timeline's own narrow
one (keeps tense but only fires on past-perfect "had" flashbacks). That split is a fidelity + architecture defect — the
brain builds ONE event/situation model indexed on multiple dimensions (Zwaan & Radvansky), not one per dimension. A
tense-preserving high-recall detector is the prerequisite to UNIFYING them (one event set, shared by all dimensions),
and to a proper temporal-order dimension.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** DETECTION is tense-agnostic (event-hood = lexical predication, not tense — the keystone's
  finding); but temporal LOCATION is a separate, real computation — Reichenbach's event / reference / speech time,
  read from tense + aspect + temporal adjuncts (Reichenbach 1947; the situation-model TIME dimension, Zwaan &
  Radvansky). Aspect (perfective/imperfective, telic/atelic) is a computable grammatical property (Bach eventualities).
- **OUR-INVENTION (build + sweep):** the tense/aspect assignment from the tagger's morphology (VBD/VBZ/VBP/VBG/VBN +
  auxiliaries have/be/will) — a transparent rule mapping surface form → (tense, aspect), NOT the placeholder constant.
  The stock (pre-keystone) `T.extract_events` already computed tense; the recall fix dropped it. Recover it on the
  UPOS==VERB detections. Glass-box, no LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (the gap):** the landed `_tense_agnostic_extract` sets `tense=TENSE_SIMPLE_PAST` for every event (verified
  on disk); the TIME dimension (`_read_timeline`) runs its OWN `M.extract_events_punct` because it needs real tense.
- **INFERRED (you must measure):** whether a tense-preserving variant KEEPS the keystone's event recall (no
  CI-separated recall regression vs `tense_agnostic_events=True`) AND assigns tense/aspect CI-separated over the
  placeholder-constant floor on a tense gold (UD verb features / a tense-annotated set), info-free twin (shuffled
  tense labels) LOSING — and, the payoff, that feeding the unified detector to the timeline MATCHES or beats the
  timeline's own separate extraction (so the two extractions can be UNIFIED without a TIME regression).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The tense-AGNOSTIC recall fix (p1, landed) — this KEEPS its detection + recall; it only adds back correct tense.
- The narrow "had"-gated flashback timeline (`_read_timeline`) — the goal is to let it (or its successor) consume the
  unified detector; do not re-derive its flashback logic.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py::_tense_agnostic_extract` (the placeholder-tense line) + the stock `T.extract_events`
  (`experiments/_temporal_ordering.py`, which DID compute tense) + `_read_timeline` (the current separate extraction) +
  the TIME-dimension scan in `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (2026-08-31).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a REAL corpus with tense-bearing gold (UD verb tense/aspect features + a timeline gold):
- **PASS =** the tense-preserving detector holds the keystone event RECALL (no CI-separated regression vs the
  placeholder-tense detector) AND its assigned tense/aspect beats the placeholder-constant floor CI-separated on the
  tense gold, with the info-free shuffled-tense twin LOSING; AND (the payoff) the unified detector, fed to the
  timeline, does not regress the TIME/flashback read vs the timeline's own separate extraction. Report CI half-width +
  null p95.
- **A rigorous NEGATIVE is a full PASS:** if correct tense cannot be recovered on the high-recall detections without a
  recall cost (e.g. the extra present-tense verbs the keystone recovered are exactly the ones whose tense is
  ambiguous), name why — enumerated — which tells the assembly the two extractions must stay separate.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`; land in `hdlab/situation_reader.py::_tense_agnostic_extract` (assign real tense/aspect
  instead of the constant, behind the same flag). Witness recomputes recall + tense accuracy from source through the
  live `read()`. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. This unblocks the SHARED-EVENT-SET
  architecture + a proper TIME dimension; it composes with the landed `tense_agnostic_events` keystone.


## DO NOT QUOTE / DO NOT REDO
- 🚫 **word-tense 0.909 uses an NLTK fine-tag** — NOT the pure-substrate number; the in-substrate core is 0.770. Quote 0.770 as the substrate result. The clausal aspect/voice gold is DERIVED from the UD tree (not hand-annotated); the timeline payoff rests on a small 8-item constructed flashback gold — do not over-quote.
- 🚫 INTEGRATED (STRONG) — build ON it (the composed tense feeds the landed TIME dimension); do not re-derive.
