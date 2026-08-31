---
priority:
review: EXCELLENT
review_text: "SOLVED (owner-DONE) integrated 2026-08-30 — the generalization audit the owner has repeatedly demanded, delivered exhaustively and honestly, and it CORRECTS several credited organ wins + hands strategy the ranked next problems. Reverified FIRST-HAND: test_generalize_retrieval_real_codes.py 34/34 (scaffold-free; recomputes every headline over LitBank 28,569 events). A GENERALIZATION LEDGER over all 33 keyword-flagged organs: 10 FALSE POSITIVES (already held-out-validated at n=995..28,569 — confirms tools/generalization_audit.py OVER-FLAGS ~2.5x, exactly as I flagged when I built it), 9 ALREADY-NEGATIVES (the SOLVED is itself a refutation), 13 GENUINELY FRAGILE. FOUR rigorous reruns (8 of 13; all 13 accounted for; each with a POSITIVE CONTROL reproducing the synthetic headline — what licenses a negative): (1) STORE/RETRIEVAL/BINDING on real LitBank who-did-what (n=28,569, gold coref): HOLDS-DIRECTIONALLY / MAGNITUDE COLLAPSES 15-60x — separated-store over flat +0.94 synthetic → +0.060/+0.016 real (CI-sep but tiny), concentrated in the ~13% busy entities (≥4 events); 87% of real entities have ≤3 events where flat is already ≥0.98 → wire for busy entities ONLY; DG-at-retrieval HURTS distinct-address codes (a self-correction). (2) CAUSATION TYPERS on MAVEN-ERE (n=9,698): DOES NOT HOLD — the force typer fires on only 16.1% of real causal relations and its force signal is indistinguishable from a shuffled twin (+0.018 NOT_SEP), losing to majority by −0.679. (3) N400 EVENT SEGMENTER on MCScript2: DOES NOT HOLD (boundary-F1 0.122 vs synthetic 0.987; loses to a rate-matched random detector). (4) CONSOLIDATION STORE on Gutenberg OLD/NEW: DOES NOT HOLD (selective − uniform-twin −0.009 NOT_SEP; the brain-faithful need-priority arm ALSO ties → negative ROBUST). INFEASIBLE (3, documented blockers = a finding: ToM microworld, relcl-parser [already reran +0.001], reliability-signal). TWO RESEARCH REFRAMES, each brain-PINNED + EMPIRICALLY GATE-CLEARED: RETRIEVAL — event-count is the WRONG axis (Radvansky & Zacks); the load-bearing axis is similar-competitor cue-overload (Van Dyke & McElree 2006); content-only floor 0.398 on 22,123 real ambiguous queries → BUILD (honest: cue COMBINATION is the unbuilt uncertain step, P~0.50). CAUSATION — the force typer is the WRONG PRIMITIVE (word-grain force for a discourse-grain problem); real causation is covariation-based causal-GRAPH inference (Trabasso/van den Broek; Kintsch; Kuperberg 2011; Feng 2021 ALE; left IFG/MTG+rostral mPFC — force-dynamic verbs have a VERIFIED ABSENCE of neural study); a glass-box event-type covariation scorer beats its shuffled twin +0.094 and majority +0.056 (clears the +0.05 HARD-PASS) on the 84% the typer never fires → BUILD. THE META-PATTERN (the deliverable's core lesson): every synthetic win was measured at an operating point / population that does not occur in real text (orthogonal codes / balanced minimal pairs / clean topic-jumps / arbitrary splits) — the single highest-leverage upgrade is to RE-MEASURE every organ at the REAL operating point before crediting it. THE BIGGEST LEVER (flagged, not solved): the EXTRACTION FRONT-END (~0.32 event/role recall) — every organ number used GOLD extraction; end-to-end the front-end dominates. Exemplary discipline (reading the n corrects 10/33 keyword flags; positive control licenses each negative; drilling the negative with the brain-faithful alternative — twice confirmed by a gate, once refuted by the data). Grade EXCELLENT (the honest, rigorous, brain-foundational generalization audit the owner demanded; it re-baselines the substrate's credited wins and gate-clears the successors). STRATEGY ACTIONS (done + queued): (a) audit §2b folded (causation/N400/consolidation DON'T generalize; separated-store busy-entities-only; DG for confusable addresses only). (b) generalization_audit.py to gain a held-out-n column (adopt the method — the false-positive rate visible). (c) PACKAGED THE 3 RANKED SUCCESSORS: p1 `the_extraction_front_end_recovers_only_a_third_of_events_and_roles` (the biggest lever), p5 `narrative_causal_graph_missing_implicit_inference_organ` (the causation successor — course-corrects the force-typer approach), p6 `retrieval_interference_is_similar_competitor_cue_overload_not_event_count` (the retrieval reframe). ⚠️ COURSE-CORRECTION for the queue: the force-typer causation-wiring (p2) is now NARROW (16% explicit-physical only) per this audit — p5 is the real-text causation lever."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-30 (grade: EXCELLENT; SOLVED owner-DONE)
> **Verdict:** the generalization audit the owner demanded — exhaustive, honest, and it corrects credited wins + hands strategy
> the ranked next problems. Reverified first-hand (`test_generalize_retrieval_real_codes.py` **34/34**, over 28k LitBank events).
> **Ledger of 33 flagged organs:** 10 false positives (already held-out-validated — confirms my tool over-flags ~2.5×), 9
> already-negatives, 13 fragile. **4 rigorous reruns** (each with a positive control that licenses the negative): separated
> store **shrinks 15–60×** on real text (wire busy-entities-only); the **causation force-typer DOES NOT HOLD** (fires on 16% of
> real relations, twin-indistinguishable); the **N400 segmenter** and **consolidation replay** both DOES-NOT-HOLD. **2
> gate-cleared brain-PINNED successors:** covariation causal-GRAPH inference (+0.094 twin, +0.056 majority) and similar-competitor
> cue-overload retrieval (content under-determines at 0.398). **Meta-lesson:** every synthetic win was measured at an operating
> point that doesn't occur in real text — re-measure at the REAL operating point before crediting. **Biggest lever flagged:** the
> extraction front-end (~0.32 recall) caps everything. **Grade EXCELLENT.** Actions: audit §2b folded; **3 ranked successors
> PACKAGED (p1 extraction front-end, p5 causal-graph, p6 similar-competitor retrieval)**; the force-typer causation-wiring (p2)
> is now narrow per this audit. `priority:` cleared.

# PROBLEM: many integrated organ wins were established on a CONSTRUCTED gold (minimal pairs / hand-authored vignettes made FOR the mechanism) or a SMALL-N (n<30) real-text point estimate — and we do NOT know which of those wins SURVIVE on data that existed BEFORE the mechanism. The owner has repeatedly found that results don't generalize. The strongest free predictor (project audit 2026-08-18) is exactly this: did the TEST ITEMS EXIST BEFORE THE MECHANISM? A keyword scan CANNOT answer it — `tools/generalization_audit.py` (built 2026-08-30) triages ~33/81 organs as construction-headlined, but it OVER-FLAGS (two spot-checked "fragile" hits — `the_reading_extractor…`, `the_entity_store…` — were actually validated on 17,330 / 28,569 held-out items). The only real test is a held-out / OOV / modern RERUN. Build the generalization stress-test: for each LOAD-BEARING organ whose headline rests on a constructed or small-n gold, rerun it on a held-out / out-of-vocabulary / modern population that existed before the mechanism, its own strongest floor recomputed there, the info-free twin LOSING — and report a GENERALIZATION LEDGER (which wins hold, which do not). A win that does NOT survive is a rigorous NEGATIVE = a full PASS: it tells us to fix, de-scope, or stop trusting that organ before we wire it in.

**slug:** `stress_test_which_organ_wins_actually_generalize_on_held_out_text` — **opened:** 2026-08-30 by the strategy session
(owner-directed; owner has been pushing generalization as a first-class priority). **status:** OPEN — a MEASUREMENT + AUDIT
problem (rerun existing organs; build/extend NO new capability). You work in `experiments/`; strategy lands any hdlab change
(Q111) — but most outcomes are re-measurements + reclassifications, not new organs. NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — HIGH and owner-directed. Generalization is the risk that
> most undermines trust in the whole substrate: an organ that only wins on its made-for gold is not a real capability, and wiring
> it into the live reader imports that fragility. Ranked below the in-flight corpus-migration (p1) + owner-prereq sense-gate (p2)
> + the in-flight focus-stack (p3), ABOVE the QA capstone (p5) — because a capstone built on non-generalizing organs is worth less
> than knowing which organs to trust. **Re-rank per the owner.** This is a SWEEP: bounded by starting with the most load-bearing
> organs; even partial coverage (the top-N) is valuable.

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
When we build a piece of the reader, we usually test it on examples we wrote to show it off — "the wind opened the gate" vs
"the key opened the gate," a handful of hand-built sentences. It passes, and we move on. But a test we wrote FOR the mechanism
can't tell us whether it works on sentences we DIDN'T write — real books, modern text, words it never saw. The owner keeps
finding that our wins shrink or vanish on new data. This problem is a systematic check: take the pieces whose "win" was only
ever shown on made-for-it examples (or a tiny handful of real ones), and re-run them on a big pile of text that already existed
before we built them. Report honestly which ones still win and which fall apart. Finding one that falls apart is a GOOD result —
it stops us from trusting it.

## 2. WHY THIS ONE
It de-risks the entire substrate and it is owner-directed. Every organ we wire into the live reader imports its own fragility;
a comprehension capstone built on organs that only win on their own golds is worth little. We ALREADY have proof the check
pays off: `the_reading_extractor_may_not_beat_a_two_line_rule` re-ran the elaborate role reader on 17,330 held-out QA-SRL items
and found it LOSES to a two-line rule (a rigorous negative → REPLACE). That is exactly the outcome we want more of, done on
purpose across the load-bearing organs. Baking "does it hold on data that existed before the mechanism?" into how we validate is
the single highest-leverage upgrade to our trustworthiness.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the standard the rerun enforces):** generalization / systematicity — the brain applies a learned computation to
  NOVEL instances (new words, new sentences); a competence that only fires on its training exemplars is not the brain's
  operation, it is a lookup. The faithful organ generalizes to items drawn from the same distribution it claims to model.
- **OUR-INVENTION (flag + sweep):** the specific held-out / OOV / modern populations chosen per organ (must be pre-existing and
  distribution-matched to the organ's claim); the reclassification thresholds. Glass-box, no external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (a HARD constraint):** `tools/generalization_audit.py` is a keyword TRIAGE and OVER-FLAGS — do NOT trust its FRAGILE
  list as a verdict (two spot-checked hits were actually validated on 17k/28k held-out items). Use it only to seed candidates,
  then CONFIRM each by READING the SOLVED for its actual held-out n and real-text number.
- **INFERRED (you measure):** for each CONFIRMED-fragile load-bearing organ, does its headline win SURVIVE on a held-out / OOV /
  modern population that existed before the mechanism?

## 5. ALREADY TRIED / DO NOT RE-RUN
- `the_reading_extractor_may_not_beat_a_two_line_rule` (n=17,330 held-out) + `the_entity_store_is_a_dense_bundle_that_fans`
  (28,569 LitBank) already have LARGE held-out validation — they are NOT fragile; do not re-audit them (they are the template).
- Do not re-derive an integrated result on its OWN gold; the whole point is a DIFFERENT, pre-existing population.
- The corpus-age confound is a related but SEPARATE effort (`the_reader_eval_is_scored_on_200_year_old_mcguffey…`, p1) — coordinate,
  don't duplicate; a modern held-out population also relieves corpus-age.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `python tools/generalization_audit.py` → candidate list. For each candidate, READ its SOLVED `result:`/`controls:`/`floor:`
  and record: was the headline CONSTRUCTED or held-out? what n? is there a real-text number? — the CONFIRMED-fragile shortlist.
- Rank the shortlist by LOAD-BEARING (live-wired in `situation_reader` / assembly-bound / a foundational primitive) × fragility.
  Start at the top; the sweep is valuable even partial.
- Check `data/corpora/` for the pre-existing held-out populations already on the shelf (LitBank, UD-EWT, QA-SRL, SimLex/SimVerb,
  MCScript, OntoNotes) — pick the one distribution-matched to each organ's claim; MIND THE CORPUS-AGE CONFOUND (prefer modern).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
Per organ, on a HELD-OUT / OOV / modern population that existed before the mechanism (n large enough to power it):
- **HOLDS (the win generalizes) =** the organ's headline metric beats its strongest floor recomputed ON THAT population,
  CI-separated (bootstrap; report CI half-width + null p95), with the info-free twin LOSING. NO number crosses populations/scorers.
- **DOES NOT HOLD =** a rigorous NEGATIVE and a full PASS: the constructed win did not survive → reclassify the organ (fix path,
  de-scope, or "constructed-only, do not wire") with the number that shows it. This is the MOST valuable outcome per organ.
- **DELIVERABLE = a GENERALIZATION LEDGER** (per audited organ: constructed number → held-out number → HOLDS/DOES-NOT-HOLD +
  the population + the floor + the twin). Plus an AUDIT UPDATE to `BRAIN_FOUNDATIONAL_AUDIT.md` per reclassified organ.

## 8. FILES AND ENTRY POINTS
- Triage: `tools/generalization_audit.py` (seed only — over-flags). Pre-existing populations: `data/corpora/` (+ QA-SRL, SimLex/SimVerb).
- Build the rerun harness in `experiments/`; a witness `verification/test_*_organ.py` per audited organ that recomputes on the
  held-out population from source. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b for every reclassification.
- Coordinate with `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end` (integrated) — the live-reader end-to-end
  is itself a generalization gauntlet; this problem covers the ISLAND organs that never faced it.


## DO NOT QUOTE / DO NOT REDO
- 🚫 This problem is INTEGRATED — the honest result + caveats are in `review_text` (frontmatter) and `INTEGRATED_BY_STRATEGY` (SOLVED.md). Do NOT quote its numbers across a different scorer / population / representation (standing rule: no number crosses scorers or populations); recompute every floor on the target item's own population.
- 🚫 The direction is CLOSED for re-derivation — build ON it, do not re-run it.
