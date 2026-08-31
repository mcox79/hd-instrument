---
priority:
review: STRONG
review_text: Wires the promoted force-dynamic typer into the LIVE reader's causation read, measured end-to-end through SituationReader.read() with the reader's OWN automatic extraction -- 3-way CAUSE/ENABLE/PREVENT AUTO 0.833 [0.714,0.929] > majority-CAUSE/untyped floor 0.429 CI-sep (+0.143), info-free force-class-shuffle twin p95 0.524 loses, PREVENT positive control 11/13 vs 0/13 (only force dynamics can represent a prevented endstate). I reverified 12/12 FIRST-HAND scaffold-free -- every headline (floors, bootstrap, construction generalization, force-event gate) recomputes from source; W1 default-off is byte-identical to the stock reader (the landing invariant). STRONG not EXCELLENT: the affirmative gold is small (n=42), single-adjudicator, partly self-authored (construction-proof risk), construction-generalization is on constructed sentences, and open-text precision is understood-but-NOT-solved (the event-hood gate cuts over-fire 34->22 but regresses curated 0.833->0.810, correctly left default-OFF). Load-bearing deviation vindicated: domain-general force typing 0.833 beats the brief's physical-only gate 0.762. Consistent with my generalization stress-test (the typer is narrow on FULL open text) -- the solver honestly scoped to the within-clause domain and diagnosed the open-text gap as a Stage-1 foreground/event-hood problem.
---

> ## ✅ SOLVER REVIEW -- STRONG (integrated by strategy 2026-08-31)
> **Why STRONG, specifically:** it did the thing all three prior causation cells only named -- replaced
> GIVEN extraction with the live reader's OWN automatic extraction and measured 3-way typing END-TO-END
> through `SituationReader.read()`, clearing the untyped/majority-CAUSE floor CI-separated (+0.143) with
> the info-free force-class-shuffle twin losing. The decisive evidence is the PREVENT positive control
> (AUTO 11/13 vs majority 0/13): only a force-dynamic representation can encode a prevented, never-happened
> endstate -- the untyped reader asserts a wrong-SIGN positive link, so this is a capability the stock
> reader structurally lacks, not a scoring nudge. Four brain-literature drills (within-clause causative
> extraction / construction-general typology / force-eventhood-off-the-arguments / event-model foreground
> decision), each PINNED, each confirming or CORRECTING the design (auto extraction 0.419->0.833 purely by
> replicating three named brain ops). The one deliberate brief deviation is load-bearing and measured:
> physical-only typing 0.762 LOSES; the Talmy/Wolff typology is domain-general, so typing any force event
> (incl. social/institutional) is what clears the bar.
> **Reproduced under my check:** I re-ran `verification/test_wire_causation_typer_organ.py` -- 12/12 PASS,
> scaffold-free; AUTO 0.833[0.714,0.929], majority 0.429, twin p95 0.524, PREVENT 11/13, W1 byte-identical
> (stock_links=4 unchanged), domain-general 0.833 > physical-only 0.762, construction routes 1.000 all
> reproduce independently from source. The result survives fully.
> **The honest docks from EXCELLENT (all solver-volunteered):** n=42 single-adjudicator gold, partly
> self-authored (construction-proof risk); the construction 1.000 is on constructed sentences (mechanism
> generalizes, not naturalistic scale); open-text precision is a WORST-CASE artifact on descriptive prose,
> materially higher on event-dense narrative, with an enumerable verb-class tail (possession/creation/
> naming/perception) -- improved, NOT solved. This converges with my integrated generalization stress-test
> (the force typer fires on ~16% of full-open-text causation and its twin is indistinct THERE): the two
> results are consistent -- 0.833 holds on the WITHIN-CLAUSE causative domain the brief scoped to, and open
> text is the separate Stage-1 gap.
> **What matters forward (the seeds, not fixes):** (1) the hdlab landing (add CausalLink.ctype +
> endstate_reached; promote _force_dynamics_lexicon/_patient_tendency/_literalness_gate; default-OFF
> causation_typed flag in `_read_causation`, byte-identical when off) is EARNED and QUEUED as the assembly
> (DEBT 2) -- strategy owns it (Q111). (2) The deepest thing this exposed -- a FOREGROUND / event-hood gate
> for causal encoding (only a foregrounded event is a causal-arc candidate; Zwaan & Radvansky, Hopper,
> Sanders) -- nothing owns it; PACKAGED as the next problem. (3) Reframe `no_glass_box_verb_sense_
> disambiguation` from "build a WSD gate" to "read force-eventhood off the arguments" (a working partial +
> PINNED architecture already exist here).

> ## ✅ UNBLOCKED + READY (2026-08-30) — all three inputs are integrated and validated
> Re-ranked p6 → p2 (the prerequisite is done). **This is now a clean, buildable assembly step — wire the CAUSATION dimension
> into the live reader.** The three inputs the wiring composes are ALL integrated EXCELLENT + validated:
> 1. **Force typer** — `hdlab/force_dynamics_typer.py` (the Wolff CAUSE/ENABLE/PREVENT typer).
> 2. **Patient-tendency estimator** — `experiments/_patient_tendency.py` (the 4-cue force-sum; supplies the ENABLE-vs-CAUSE
>    tendency bit, so no more gating ENABLE to lexically-fixed letting verbs).
> 3. **Literalness veto gate** — `experiments/_literalness_gate.py` (integrated 2026-08-30; engage ONLY on ENGAGE_PHYSICAL,
>    abstain on figurative/idiom/bad-attachment — it HALVES figurative mislabels end-to-end).
> **Wire all three into `situation_reader._read_causation`:** gate → (if ENGAGE_PHYSICAL) type with the force typer + the
> patient-tendency bit; else abstain. The §7 bar below still holds (scope the WIN to the within-clause domain; the
> cross-sentence-link tie is the known integrated negative — report it, don't claim it).

# PROBLEM: the live reader records causation as an UNTYPED link — the promoted `hdlab/force_dynamics_typer.py` (Wolff/Talmy CAUSE/ENABLE/PREVENT typer, integrated EXCELLENT, real-text 0.917 on its within-clause domain) is a DEFAULT-OFF ISLAND the reader never calls. `situation_reader._read_causation` (hdlab/situation_reader.py:785) builds `CausalLink(sent_idx, cause, outcome, method)` with NO force type, so the reader cannot tell "the key OPENED the gate" (CAUSE) from "the wind LET the gate swing" (ENABLE) from "the bar KEPT the gate from opening" (PREVENT) — the core of the Zwaan CAUSATION dimension. WIRE the promoted typer into the live reader's causation read, measured END-TO-END, on the typer's PROVEN domain. This is the first CAUSATION entry in the wiring-map ASSEMBLY (`notes/WIRING_MAP.md`, DEBT 2): a promoted, witnessed organ that the live reader does not yet consult.

**slug:** `wire_the_causation_typer_into_the_live_reader` — **opened:** 2026-08-30 by the strategy session (wiring-map burn-down;
owner pressed 2026-08-30 "are you actually WIRING these in?"). **status:** OPEN — an ASSEMBLY (wire-a-promoted-organ-into-the-live-reader)
problem, following the proven who-did-what template (`wire_the_predarg_frontend_and_binder_into_the_live_reader`). You build +
validate the wired reader in `experiments/` (a live end-to-end measurement through the real `SituationReader.read()` class);
strategy lands the situation_reader edit (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` — HIGH. The owner's current directive is to WIRE the
> validated islands into the live reader ("an ever more complete substrate"), and this is the cleanest first CAUSATION assembly:
> the organ is promoted + witnessed, the wire point is a single isolated method (`_read_causation`), it does NOT collide with the
> coref-path work (p3 focus-stack) or the meaning path. Ranked below the owner-priority corpus migration (p1), above the
> focus-stack (p3, which attacks the coref #1 bottleneck) only because wiring is the owner's active ask. **Re-rank per the owner.**

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
When a story says one thing made another thing happen, there are three different flavours a good reader feels the difference
between: something FORCED a change ("the fire burned the house down"), something ALLOWED a change that was going to happen
anyway ("she let the door swing open"), and something STOPPED a change ("the lock kept the door shut"). Our reader currently
records "A is causally linked to B" but throws away which of the three it was — even though we already built and tested the
exact organ that tells them apart (it reads 0.917 on real single-clause causation). That organ sits in the library unused;
the live reader never calls it. This problem is: make the live reader actually consult it, so its causal record carries the
right flavour, and prove the wired reader gets these flavours right on real narrative where an untyped/"assume-forced" reader
gets them wrong.

## 2. WHY THIS ONE
It is the first CAUSATION step of the ASSEMBLY — turning validated-but-dormant organs into a reader that measurably does
more (the owner's explicit 2026-08-30 directive). The organ is already integrated EXCELLENT and promoted to hdlab; the only
thing missing is the ~15-line wire into `_read_causation` plus an honest end-to-end measurement. CAUSATION is one of the five
Zwaan situation-model dimensions, and force-dynamic typing is its pinned computational core. Low risk (isolated wire point,
default-off), high signal (a dimension the reader currently cannot represent at all).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (copy the computation exactly):** force dynamics (Talmy 1988; Wolff 2007) — CAUSE / ENABLE / PREVENT fall out of a
  small discrete truth-table over three (mostly binary) dimensions: does the patient TEND toward the endstate, do the affector
  forces OPPOSE or CONCUR, is the endstate REACHED. `hdlab/force_dynamics_typer.py` already implements this truth-table over a
  FrameNet Causation-family lexicon. This is the organ's already-integrated, already-witnessed core — you REUSE it, you do not
  rebuild it.
- **OUR-INVENTION (flag + sweep, do not adopt as truth):** the causative-clause DETECTOR that hands the typer its
  (affector, patient, verb, endstate) tuple from live parsed text; the connective/precedence heuristics in `_read_causation`;
  the ENABLE gate (see §5). These are front-end glue — glass-box, swept, honestly labelled.

## 4. MEASURED vs INFERRED (respect the integrated CAUSATION results — do NOT re-tread them)
- **MEASURED (integrated this session — a HARD constraint on your scope):** typing CROSS-SENTENCE causal links (the kind
  `_read_causation` currently finds via connectives) does **NOT** beat a majority-CAUSE baseline on real text — real
  cross-sentence non-CAUSE causation is RARE + lexically UNCOVERED + MENTAL (integrated `causation_is_typed_per_clause_not_across_the_causal_network`,
  STRONG negative). **So do NOT scope your win to cross-sentence link typing — that lever is measured dead.** Type there for
  completeness, but HONESTLY report it ties majority-CAUSE; do not claim a win you know is refuted.
- **MEASURED (the typer's REAL domain, where it wins):** WITHIN-CLAUSE / single-clause causation — "the wind opened the gate"
  (CAUSE) vs "the key opened the gate" (ENABLE) vs "the bar kept the gate shut" (PREVENT) — the typer reads 0.917 real-text on
  domain, PREVENT-killer 0.900 vs 0.000, CAUSE-vs-ENABLE verb isolation 1.000 (integrated `causation_has_no_force_dynamic_typing`,
  EXCELLENT). **This is where your end-to-end win must come from:** the wired reader must DETECT within-clause causative-verb
  events (which `_read_causation` currently does not) and TYPE them.
- **INFERRED (you must measure):** whether, once you add within-clause causative detection + typing to the live reader, the
  typed causal record beats the untyped/majority-flavour reader on real narrative, CI-separated, on the typer's domain.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The cross-sentence causal-network typer (a real-text NEGATIVE — see §4). Do not re-attempt a cross-sentence-coverage win.
- The single-clause force typer itself is DONE + promoted (`hdlab/force_dynamics_typer.py`, witness `test_force_dynamics_typer_organ.py`);
  reuse it, do not rebuild it.
- ENABLE-vs-CAUSE for tendency-ambiguous verbs needs a PATIENT-TENDENCY input; that is a SEPARATE in-flight problem
  (`causation_typing_needs_a_patient_tendency_estimator`, WIP). Per the integrated wiring target: **gate ENABLE to the
  lexically-fixed letting verbs {allow, enable, let, permit} until the patient-tendency input lands** — do NOT reinvent it here.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py:242` (`CausalLink`) and `:785` (`_read_causation`) — the exact untyped wire point.
- Read `hdlab/force_dynamics_typer.py` — the typer API + truth-table + lexicon you will call.
- Read the two integrated causation SOLVEDs (`causation_has_no_force_dynamic_typing`, `causation_is_typed_per_clause_not_across_the_causal_network`)
  and `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the two CAUSATION entries) — inherit their PINNED/negative verdicts.
- Confirm on disk that `_read_causation`'s links are untyped and that the reader never imports `force_dynamics_typer`
  (`tools/wiring_debt.py` will show it island-only). If any of this is already wired, SAY SO and stop.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
Through the LIVE `SituationReader.read()` class, on REAL narrative (LitBank / modern annotated text — MIND THE CORPUS-AGE
CONFOUND: prefer modern where causative-verb gold exists; McGuffey is ~200yr):
- **PASS =** on the typer's WITHIN-CLAUSE causative domain (a hand-adjudicated or lexicon-gated gold of causative-verb clauses,
  ≥ a real n with ≥ some ENABLE/PREVENT, not all-CAUSE), the wired reader's 3-way (CAUSE/ENABLE/PREVENT) accuracy beats the
  strongest real floor — the majority-flavour ("assume CAUSE") placeholder AND the untyped-reader baseline — CI-separated
  (bootstrap; report CI half-width + null p95), with the info-free **force-class-shuffle twin LOSING** CI-separated.
- **Positive control that only force dynamics can pass:** the PREVENT case (an outcome that never happens) — the untyped/majority
  reader cannot represent a prevented endstate at all.
- **Honesty gate:** separately report the cross-sentence-link slice and STATE that it ties majority-CAUSE (the known negative);
  do not fold it into the headline. NO number crosses populations/scorers; recompute every floor on the scored subset.
- **A rigorous NEGATIVE is a full PASS:** if a faithfully-built within-clause causative detector + typer, wired live, does NOT
  beat the floor on real text, that is a real result — say which sub-part failed and why (e.g. causative-clause extraction is
  the bottleneck, not the typer), with the enumeration.

## 8. FILES AND ENTRY POINTS
- Wire point (strategy lands the final edit, Q111): `hdlab/situation_reader.py` — `CausalLink` (add a `ctype` field +
  `endstate_reached`), `_read_causation` (:785, type the links + add within-clause causative detection), `read()` (:835).
- Organ to call: `hdlab/force_dynamics_typer.py` (promoted, witnessed). Default-OFF flag on the reader (`causation_typed: bool = False`)
  so `read()` is byte-identical when off.
- Build + validate in `experiments/` (a WiredSituationReader or an exp cell measuring end-to-end through `read()`), with a
  witness `verification/test_*_organ.py` that recomputes from source. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.
- The map this closes: `notes/WIRING_MAP.md` DEBT 2 (CAUSATION → live reader). Update the burn-down log on submit.
