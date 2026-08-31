---
priority: 5
review:
review_text:
---

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
