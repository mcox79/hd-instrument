---
priority:
review: STRONG
review_text: A GRADED Hopper-Thompson event-hood gate (the three cleanest transitivity parameters -- ASPECT + INDIVIDUATION + REALIS -- with naming/stative vetoes + a from-complement bypass) that raises open-text causal-link PRECISION CI-separated over BOTH real floors while holding recall EXACTLY. Reverified 11/11 FIRST-HAND (rebuilds the gated reader + LitBank event gold + both floors + the p2 recall gold + the info-free twin + the doc-bootstrap fresh): precision 0.3015->0.3818 vs ungated (+0.0803 [0.0666,0.0945]) AND vs the p2 dep-label stopgap 0.2970 (+0.0848), holds the p2 within-clause 3-way recall EXACTLY (n=42: 0.8333==0.8333, +0.0000) where the stopgap regressed to 0.810, removes 1000/2823 over-fired links of which 84.5% are genuine LitBank non-events (base event-rate 30.1%). The decisive control -- the info-free shuffled-event-hood twin holding the abstention COUNT constant -- LOSES (paired +0.0801 CI-sep, observed > null p95), excluding the trivial 'abstain more -> higher precision' confound. GENERALIZES: CI-separated on BOTH genre strata (descriptive +0.0597, eventive +0.0923), BOTH held-out doc halves (+0.084/+0.077), AND cross-corpus on MAVEN/Wikipedia different-scheme (0.764->0.790, +0.0266 CI-sep). Brain-faithful (Hopper-Thompson grounding/transitivity, PINNED from the p2 drill; only foregrounded events are causal-arc candidates). Additive invariant (ungated base byte-identical to the p2 WiredCausationReader). Honest self-correction: the first submission's full 6-leg cluster gave only +0.0338; taking leg-alignment seriously and DROPPING the weak grounding proxy + the sense-gate-redundant dyn/affect legs MORE THAN DOUBLED the lift (leg alignment independently justified: aspect fg/bg event-rate gap +0.337 vs grounding-alone +0.009). Grade STRONG (excellent-grade rigor + cross-corpus generalization + recall-held-exactly + the decisive twin; deflated from EXCELLENT because the delivered capability is a modest precision refinement -- residual open-text precision is still ~0.38 -- on a dimension whose base typing landing (p2) is itself queued-not-landed).
---

> ## ✅ SOLVER REVIEW -- STRONG (integrated by strategy 2026-08-31)
> **Why STRONG, specifically:** it built the Stage-1 precision filter the p2 causation drop named as its deepest gap,
> and it did the two things that make an open-text precision claim real. First, RECALL HELD EXACTLY (0.8333 ==
> 0.8333 on the p2 within-clause gold, paired diff +0.0000) where the p2 stopgap gate regressed it to 0.810 -- so
> the precision came free, not by throwing away true positives. Second, the INFO-FREE shuffled-event-hood twin
> (permute the engage/veto decisions holding the abstention COUNT constant) LOSES CI-separated -- which excludes the
> trivial 'abstain more -> higher precision' confound that would otherwise sink any gate. On top of that it
> GENERALIZES the hard way: CI-separated across genre, across held-out doc halves, and CROSS-CORPUS on MAVEN
> (Wikipedia, a different annotation scheme) -- the owner-priority generalization bar, met. The mechanism is
> brain-faithful (Hopper-Thompson grounding: only FOREGROUNDED, high-transitivity events are causal-arc candidates),
> and the removal analysis confirms it targets event-hood (84.5% of removed links are genuine non-events vs a 30.1%
> base rate), not volume.
> **Reproduced under my check:** I re-ran `verification/test_causal_foreground_gate_organ.py` -- 11/11 PASS,
> scaffold-free; +0.0803 over ungated, +0.0848 over the stopgap, recall +0.0000, twin loses (+0.0801), MAVEN
> cross-corpus +0.0266, additive-invariant base (83 links identical to p2) all reproduce from source.
> **Exemplary honesty:** it REPORTED that its own first submission (the full 6-leg transitivity cluster) gave only
> +0.0338, then took the leg-alignment measurement seriously, dropped the weak grounding proxy + the sense-gate-
> redundant dyn/affect legs, and MORE THAN DOUBLED the lift -- leaner is cleaner, and the three chosen legs are
> independently justified by their fg/bg event-rate gaps.
> **Landing (QUEUED, coupled with p2):** the foreground gate is additive + recall-held + validated, so it EARNS a
> landing -- but its home is the `causation_typed` Stage-1 slot in `_read_causation`, which is COUPLED with the
> still-QUEUED p2 causation landing (Stage-2 force typer). Land them TOGETHER (default-off: Stage-1 foreground gate
> -> Stage-2 CAUSE/ENABLE/PREVENT typing), byte-identical when off. Honest bound: absolute open-text precision is
> still ~0.38 (the gate removes 35% of the over-fire; the residual is the next, smaller lever).

# PROBLEM: the reader now TYPES causation within a clause (CAUSE/ENABLE/PREVENT, p2, owner-DONE, integrated) — but on real OPEN TEXT it OVER-FIRES, because it treats every clause as a potential causal event. The brain does not: causal encoding is a BY-PRODUCT of EVENT-MODEL construction, and only a FOREGROUNDED event (an asserted, main-line, eventive happening) is a causal-arc CANDIDATE. Backgrounded description, stative setting, and presupposed/subordinate material are NOT event nodes and must not spawn causal links. Build the missing STAGE-1 precision filter: a glass-box FOREGROUND / EVENT-HOOD gate that decides which events enter the event model as causal-arc candidates, and run causal typing only on those — raising real-text causal-link PRECISION without regressing the within-clause recall the typer already has.

**slug:** `causal_encoding_over_fires_without_a_foreground_event_hood_gate` — **opened:** 2026-08-31 by the strategy
session (the `wire_the_causation_typer_into_the_live_reader` p2 owner-DONE seed: "FILE A NEW PROBLEM — a foreground/
event-segmentation gate for causal encoding (Stage 1); nothing owns it; the deepest thing this exposed"). **status:**
OPEN — a MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO
external LLM at inference (the invariant); the foreground decision must be read from STRUCTURE, not a looked-up label.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGH. It is the precision half of making the
> reader's causal dimension work on REAL running text: the p2 typer is accurate on the within-clause causative domain
> (0.833) but honestly UNsolved on open descriptive prose (it over-fires; a stopgap event-hood gate cut Bleak-House
> over-fire 34→22 but at a curated-recall cost 0.833→0.810 — a MEASURED tradeoff, left default-OFF). The strategy
> session's own integrated GENERALIZATION STRESS-TEST independently named real-text causation precision as THE lever
> (the typer fires on ~16% of full-open-text causation and its info-free twin is indistinct THERE). This is that lever.
> Ranked below the North-Star clean-foundation core (p1 extraction in-flight; p4 knowledge-store consistency) because
> those gate the learner-on program, and above generic refinements. **Re-rank per the owner.**

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
When you read a story, you don't treat every sentence as "something that caused something." You quietly separate the
things that HAPPEN and move the plot (foreground) from the scenery, background description, and asides. Only the
foreground events get linked by "this made that happen." Our reader doesn't make that cut yet: it will try to read a
causal link off almost any clause, so on descriptive prose it invents causal links that aren't there. Build the cut:
a transparent test that decides which events are real, foreground, plot-moving happenings — and only look for
causation among THOSE. Then prove it removes the spurious causal links on real text without dropping the true ones.

## 2. WHY THIS ONE
The reader just gained within-clause causal TYPING (p2, owner-DONE): given a causative event it labels CAUSE/ENABLE/
PREVENT well (0.833). But "given a causative event" is the unsolved half on open text — it over-fires on non-events.
The p2 solver drilled the mechanism (causal encoding is decided at EVENT-NODE grain, only foregrounded events are
arc candidates; Zwaan & Radvansky; Hopper; Sanders causal-by-default) and built a FIRST default-off gate that trades
precision for recall — proof the signal is real but not yet a clean win. This problem is to build it RIGHT. It also
directly serves the clean-foundation North Star: a causal dimension that fires only on real events is a cleaner
foundation for the learner.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** comprehension builds an EVENT/SITUATION MODEL whose nodes are FOREGROUNDED events; causal
  connection is a by-product of that construction, computed over event NODES, not raw clauses (Zwaan & Radvansky 1998
  event-indexing; Radvansky & Zacks event models). FOREGROUNDING/GROUNDING is a real linguistic partition —
  foreground = asserted, sequenced, main-line, typically perfective/eventive; background = descriptive, stative,
  durative, subordinate, presupposed (Hopper 1979; Hopper & Thompson 1980 transitivity/grounding). The reader is
  CAUSAL-BY-DEFAULT (it assumes connection unless blocked — Sanders; so the filter is on event-hood, not on an
  explicit causal cue). ASPECTUAL eventivity (telic/eventive vs stative) is a graded, computable property (Gennari &
  Poeppel; Dowty).
- **OUR-INVENTION (build + sweep):** the exact foreground/event-hood FEATURES (main-clause vs subordinate/relative;
  perfective/eventive vs stative/progressive-descriptive; at-issue/asserted vs presupposed; narrative-sequence vs
  setting) and their combination into a graded event-hood score + the gate threshold. Glass-box, no LLM, structure-read.

## 4. MEASURED vs INFERRED
- **MEASURED (the gap):** p2 reports open-text over-fire (Bleak House 34 causal links ungated) and a default-OFF
  event-hood gate that cuts it to 22 but regresses the curated within-clause gold 0.833→0.810 — a real precision
  signal at a recall cost. The integrated generalization stress-test measured the typer firing on ~16% of full-open-
  text causation with an indistinct twin THERE (a precision problem, not a typing problem).
- **INFERRED (you must measure):** whether a foreground/event-hood gate can raise real-text causal-link PRECISION
  CI-separated over the ungated reader WITHOUT a CI-separated recall regression on the p2 within-clause gold — i.e.
  the descriptive/stative/subordinate false positives are separable from true foreground causal events by STRUCTURE.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The within-clause CAUSE/ENABLE/PREVENT typer itself (`wire_the_causation_typer…`, p2, integrated) — this is the
  STAGE BEFORE typing (decide WHICH events to type), not the typing. Compose with it; do not rebuild it.
- Cross-sentence / discourse causal-NETWORK edge typing (`causation_is_typed_per_clause_not_across_the_causal_
  network`, integrated NEGATIVE) — a DEAD real-text lever. This is NOT that: it is within-document event-hood, not
  cross-event edge typing.
- WSD / verb-sense gating of force verbs (measured NET-HARMFUL in p2: McRae 1998, Elman 2009) — do NOT reframe the
  gate as word-sense disambiguation; force-eventhood is read off the ARGUMENTS/aspect, not the verb sense.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the p2 `SOLVED.md` + its `research_discourse_decision_to_encode_causation_2026-08-30.md` and
  `research_force_event_discrimination_deep_2026-08-30.md` notes — the solver ALREADY drilled this mechanism and built
  a first default-off `force_engagement_score` / event-hood gate. BUILD ON IT (do not re-derive the literature).
- Read `hdlab/situation_reader.py::_read_causation` (the causation read the gate must precede) and the p2 witness
  `verification/test_wire_causation_typer_organ.py` (W12 is the current event-hood-gate tradeoff).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a REAL open-text corpus (event-dense LitBank narrative + descriptive prose; the p2 within-clause causative gold n=42
for the recall clause):
- **PASS =** the foreground-gated causal reader raises causal-link PRECISION on open text CI-separated over BOTH the
  ungated reader AND the p2 default-OFF stopgap gate (report precision on a hand-adjudicated or structurally-defined
  false-positive set), WITHOUT a CI-separated recall regression on the within-clause causative gold, AND with the
  info-free twin (SHUFFLE the foreground/event-hood labels across clauses) LOSING CI-separated. Report CI half-width +
  null p95; report the precision/recall operating point honestly.
- **A rigorous NEGATIVE is a full PASS:** if structural foreground/event-hood cannot separate spurious causal links
  from true ones without a recall cost (the p2 tradeoff is intrinsic), name why — enumerated — and what the brain uses
  that we cannot read from structure alone (e.g. it needs the full situation model / referential continuity), which
  re-points the causal-precision work to the assembly.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`; the gate composes BEFORE causal typing in `_read_causation`. Witness recomputes precision +
  recall from source (drive the LIVE `SituationReader.read()`; do NOT score in isolation — the phase-gate trap). Fold an
  **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the foreground/event-hood gate: PINNED event-model grain +
  OUR-INVENTION feature set + the measured precision/recall operating point). This is Stage-1 of the causal dimension;
  it composes with the p2 typer (Stage-2) whose hdlab landing is QUEUED (the assembly, DEBT 2).


## DO NOT QUOTE / DO NOT REDO
- 🚫 This problem is INTEGRATED — the honest result + caveats are in `review_text` (frontmatter) and `INTEGRATED_BY_STRATEGY` (SOLVED.md). Do NOT quote its numbers across a different scorer / population / representation (standing rule: no number crosses scorers or populations); recompute every floor on the target item's own population.
- 🚫 The direction is CLOSED for re-derivation — build ON it, do not re-run it.
