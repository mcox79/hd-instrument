# Research: The right benchmark for the extraction-as-foundation decisive test (2026-08-10)

Filed by: research (Sonnet, foreground synthesis of 4 parallel Sonnet lit-scan lanes). Dispatched
independent of the extraction-gate work, per explicit instruction, to close a problem that has now
burned this program 4 times: DesireDB / MCScript2.0 / WIQA all looked like reasoning benchmarks and
turned out to be either content-favorable (BoW wins) or extraction-favorable (the answer IS the
extracted structure). Task: find a benchmark that isolates NON-TRIVIAL REASONING over EXTRACTABLE
structure, cleanly, so a future glass-box loop win on it is actually attributable to reasoning.

KB-CHECK DONE FIRST: `bash tools/substrate_query.sh "benchmark reasoning non-trivial extractable
structure content ceiling ROCStories story cloze CLUTRR GLUCOSE narrative causal temporal multi-hop"`
returned top cosine=0.2861 (generic multi-hop-mechanism atom, not a substantive prior finding on
these specific candidates) — confirmed fresh ground. `research_field_advisor.py` run (110 drills, 22
fields); its heuristic covers substrate-physics fields (thermodynamics, spin-glass, free-probability),
not benchmark selection, so it does not rank this drill — noted, not force-fit, consistent with the
prior WIQA-scoping note's same finding.

Read in full this cycle: `notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_2026-08-10.md`
(the prior WIQA/TORQUE/MC-TACO scorecard — this drill does not re-derive that scorecard, it extends it
with the NEW lens the WIQA failure taught us) and the relevant blocks of
`notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`: the "ORACLE-STRUCTURE DIAGNOSTIC = HARD_FAIL"
finding (WIQA's causal sign di/dj reproduces answer_label 5005/5005 = 1.0 correlation — the extracted
fact IS the answer, no genuine chaining needed) and the "CEILING SYNTHESIS" block (independently
re-derives the same extraction-is-the-universal-wall conclusion from the crutch-fade/Social-IQa arc,
naming the "RECURRING BENCHMARK PROBLEM" this drill was dispatched to solve).

Dispatched 4 parallel Sonnet lit-scan sub-agents (public dataset/paper names used directly off-platform,
consistent with the prior note's established precedent that public benchmark names are not
substrate-novel terms): (A) CLUTRR compositional relational reasoning; (B) ProPara/OpenPI procedural
state-tracking; (C) TORQUE re-audit for the WIQA-pattern trap + narrative sentence-ordering; (D)
TRIP/e-CARE/GLUCOSE/TellMeWhy/ESTER/CRAB causal-chain broad net. ~40 distinct citations returned across
the four lanes (paper + arXiv/ACL Anthology + GitHub/HF dataset card triangulated per finding, see
Citations section).

---

## HEADLINE

**CLUTRR (Sinha et al. 2019, EMNLP-IJCNLP) is the least-compromised candidate and the recommended next
pick — but no candidate found cleanly passes all 5 criteria, and this must be said plainly rather than
glossed over a 5th time.** CLUTRR is the only candidate where non-triviality-given-structure is a
**structural guarantee by construction** (the data-generation algorithm samples the target kinship
relation first, then emits only *supporting* facts via >=2 steps of backward chaining that never
include the target fact itself — so, unlike WIQA, there is no possible single extracted fact that
equals the answer, by design, not by empirical luck) and where four years of independent follow-up
literature (CTP/Minervini 2020, Li & Minervini 2022, Edge Transformers, a 2026 depth-probe) all show the
SAME signature: every model's accuracy degrades monotonically as required chain length k grows — the
exact opposite of WIQA's chain-length-invariant leak. It cleanly separates two failure modes our system
will hit (extraction vs. composition), which none of the previous three benchmarks let us diagnose
separately. Its weakness is criterion 5: CLUTRR is never wild, unproduced text — it is always
graph-constructed and template/AMT-paraphrase-recombined, so it cannot itself demonstrate performance on
naturalistic prose. **Recommended sequencing: CLUTRR first (validates whether the composition organ
works at all, under the strongest available non-triviality guarantee), then ProPara (#2, genuinely
naturalistic elicited science-process text, implicit multi-step tracking empirically shown to matter —
rule-based baseline collapses to 2.4% F1 on the cross-step-dependent sub-metric while adding real
cross-step memory produces a 15x gain on that exact metric) as the real-prose stress test for the
extraction side.**

The single biggest risk that CLUTRR is itself a hidden WIQA-in-disguise: **no paper has ever published a
bag-of-words/majority baseline for CLUTRR** — the same evidentiary gap WIQA had before we found the
sign-leak ourselves. The chain-length-degradation signature is reassuring but not dispositive: it rules
out a *total* leak (which would be chain-length-invariant) but does not rule out a *partial* shortcut,
specifically **predicting the relation from only the first and last stated fact in the chain, ignoring
the interior links** (kinship composition has enough regularity — e.g., two "child-of" hops usually
compose to "grandparent" regardless of the middle entity — that endpoint-only extraction could plausibly
recover a meaningful fraction of short-chain (k=2,3) answers without real multi-hop composition). This
exact probe is the mandatory precondition measurement before any engineering investment (Section: Cheap
decisive test) — this is the process fix that would have caught WIQA earlier if it had been run before
building instead of after.

P_deflated = **0.50** (capped at novel-synthesis per calibration) for "CLUTRR is the correct next
benchmark pick, surviving both traps that killed WIQA/MCScript2.0" — deflated harder than the prior
WIQA-pick's P=0.60 precisely because we were burned AGAIN after that earlier, less-cautious P=0.60
judgment; the structural guarantee is real but the endpoint-shortcut risk is unmeasured. P = **0.25**
(deflated) for "the CLUTRR-adapted composition loop HARD-PASSes its first pre-registered experiment" —
lower than WIQA's analogous P=0.32 because CLUTRR requires an entirely new extraction domain (kinship
relations from prose) with no existing owned-organ head start, unlike WIQA which reused
`CausalLinkRegister` almost directly.

---

## 1. Ranked shortlist — full trap-check per candidate

### #1. CLUTRR (Sinha, Sodhani, Dong, Pineau, Hamilton, EMNLP-IJCNLP 2019, arXiv:1908.06177)

| Criterion | Trap-check finding |
|---|---|
| **1. Content ceiling** | No published BoW/majority baseline exists (the honest gap — flagged, not glossed). Structural argument is strong: entity names are randomized/anonymized specifically to kill lexical shortcuts; 22-way label space; weak trained baselines (RN 0.49, BiLSTM 0.53-0.58) are far below the 1.0 GAT-given-oracle-graph ceiling and collapse toward ~4.5% chance by k=8-10. Order-blind bag-of-relation-words is architecturally insufficient in principle (composition order changes the answer) but this is inference, not a measured ablation. **PASS, moderate confidence** (no direct measurement yet). |
| **2. Reasoning non-trivial given structure** | **STRUCTURAL GUARANTEE, not empirical luck.** The generation algorithm samples the target relation FIRST, then runs backward chaining for exactly k>=2 steps to emit only *supporting* facts that never include the target — so no single extracted fact can equal the answer, by construction, for every reported k=2..10 example. Four years of independent follow-up work all show accuracy degrading monotonically with k (the opposite of WIQA's chain-invariant 1.0 leak). **STRONG PASS**, with one flagged residual risk: an endpoint-only (first+last fact) partial shortcut is UNMEASURED (see biggest-risk section above). |
| **3. Extractable structure** | HIGH. Kinship relations ("X is Y's father," "Y's sister Z") are short, templated-vocabulary predicate statements over named entities — well within reach of NER + simple relation-pattern extraction, easier than WIQA's causal-polarity extraction. |
| **4. Exercises our strongest organ** | Direct match. Multi-hop composition of a chain of extracted binary relations via a fixed composition rule (father-of + sister-of = aunt-of), validated hop-by-hop, is structurally isomorphic to the Stage-2A retrieve-VALIDATE-advance loop (HARD_PASS 013f1481e: VALIDATE arrests multiplicative error across multi-hop chains) — except CLUTRR's "validate" check is a hard symbolic composition-table lookup (even cleaner than WIQA's soft sign-multiply), and CLUTRR was NEVER given a real target by any of the 3 prior comprehension arcs. |
| **5. Real/naturalistic text + unproduced slice** | **WEAKEST axis.** Text is AMT-crowdsourced paraphrases (genuinely diverse: unigram Jaccard 0.201, bigram 0.0385 — not templated boilerplate) but always constructed as a recombination of a fixed pool of human-written sentence fragments describing an underlying logical graph. There is no wild/unproduced-text version and structurally cannot be, since the whole point is controlling the ground-truth composition depth k. **FAIL** on the strict "unproduced naturalistic mess" reading; PASS on "genuinely varied human-written phrasing." |
| **Data access** | HF `CLUTRR/v1` (splits: `gen_train23_test2to10` train 9,074/val 2,020/test 1,146; `gen_train234_test2to10` train 12,064/val 3,019/test 1,048; plus 4 robustness splits). GitHub `facebookresearch/clutrr` (generator code — lets us regenerate fresh splits with controlled k/noise, useful given documented label-quality issues). **License: CC BY-NC 4.0 — non-commercial.** Flag for product use: fine for R&D/validation: not directly usable for a commercial-product-facing claim without either a license clarification or regenerating an equivalent corpus via the open generator (feasible, since the generator itself has no restrictive license noted). |
| **Baseline vs SOTA vs human** | Weak text-baselines 0.49-0.67 (chance ~4.5%); best oracle-graph-given SOTA (CTP) 0.89-0.99 even at k=10; **timed humans drop from >70% (k<=3) to 40-50% (k>3)**, untimed humans hit 100%. The gap is almost entirely EXTRACTION (machines exceed humans once facts are correctly extracted), which is diagnostically useful: CLUTRR lets us tell whether OUR failure (if any) is extraction-side or composition-side — none of DesireDB/MCScript2.0/WIQA let us do that cleanly. |

### #2. ProPara (Dalvi, Huang, Tandon, Yih, Clark, NAACL 2018, arXiv:1805.06975)

| Criterion | Trap-check finding |
|---|---|
| **1. Content ceiling** | Rule-based/lexical-pattern baseline collapses specifically on the cross-step-dependent sub-metric (Cat-3, location): **2.4% F1**, vs. adding real cross-sentence memory (ProGlobal) jumping to **35.9%** on that same sub-metric (a 15x gain) — the cleanest MECHANISM-ATTRIBUTABLE evidence found in this whole scan that genuine cross-step tracking, not surface pattern-matching, is what the task rewards. **PASS, empirically demonstrated** (not just structural inference, unlike CLUTRR). |
| **2. Reasoning non-trivial given structure** | Built in by explicit design: "things are by default unchanged unless told otherwise" — entities must be tracked through steps where they are NOT mentioned (implicit continuity), which is genuine multi-hop state propagation, not single-step extraction. **PASS**, with a 2025 caveat (ProPara-CRTS, IWCS 2025) that annotation schema ambiguities "hinder reliable evaluation" — a data-quality flag, not a reasoning-shortcut flag. |
| **3. Extractable structure** | MEDIUM-HIGH. Entity creation/move/destruction events + location spans are extractable via SRL + coref, comparable difficulty to WIQA's per-step event extraction (which our owned `extract_events`/`mcscript_extraction` organs already target). |
| **4. Exercises our strongest organ** | PARTIAL match — this exercises the `situation_model_accumulate` state-tracking/accumulate-register organ more than the causal-chain VALIDATE loop specifically. Real multi-hop, but a different flavor (temporal/procedural state persistence, not causal-sign propagation or relational composition). Good complement to CLUTRR, not a substitute. |
| **5. Real/naturalistic text + unproduced slice** | Real subject matter, real crowd-written prose (not templated), but MTurk-elicited from a process-name prompt — produced, not wild. No unproduced validation slice found. Similar honesty gap to CLUTRR, different flavor: naturalistic PROSE STYLE (declarative science-process English) but not naturalistic PROVENANCE (still elicited-to-spec). |
| **Data access** | GitHub `allenai/propara` (code Apache-2.0; data license unconfirmed — verify before redistribution), data.allenai.org/propara, official leaderboard. 488 paragraphs / 3,300 sentences / ~81K state annotations. |
| **Baseline vs SOTA vs human** | ProGlobal 45.1 (Cat-avg) vs. **Human 80.8** — a 36-point gap at launch (Cat-3 alone: 35.9 vs 63.0). Later SOTA (CGLI ~72.7 F1 document-level metric) narrows the launch-era gap but I could not confirm a matched-metric human ceiling on that later track — flagged, needs re-verification on whichever metric is adopted before quoting a "current" gap. |

### #3. TRIP (Storks, Gao, Zhang, Chai, EMNLP Findings 2021, arXiv:2109.04947)

| Criterion | Trap-check finding |
|---|---|
| **1. Content ceiling** | **COMPLETELY UNMEASURED** — no BoW/lexical baseline ever published. This is a "nobody has looked" situation, structurally identical to WIQA's pre-discovery state. One informative signal exists: SOTA models reach 93-94% end-task accuracy but only 25-28% "verifiability" (fully-justified: plausibility + correct conflict pair + correct attribute states) — a 65-point gap between the easy top-level label and the hard causal trace, itself a warning that top-line accuracy alone may be a soft content-ceiling in disguise. **UNVERIFIED, high-risk-but-informative.** |
| **2. Reasoning non-trivial given structure** | Architecturally the best-shaped candidate found: violation only becomes visible after propagating physical state across multiple steps (avg 1.2 conflicting sentence-pairs per 5.1-sentence story), not from any single sentence in isolation. But no ablation (ours or published) confirms multi-sentence tracking is actually necessary for the CGLI-era SOTA's 93% accuracy — the paper itself has no single-sentence/no-context control. **UNVERIFIED**, same "nobody looked" caveat as criterion 1. |
| **3. Extractable structure** | MEDIUM. 20 physical attributes (location, existence, temperature, wetness, solidity, power, cleanliness, etc.) per sentence is a richer, more diverse extraction target than WIQA's single causal sign or CLUTRR's kinship relations — plausibly extractable but not yet attempted by any owned organ. |
| **4. Exercises our strongest organ** | GOOD FIT if verified — cross-sentence causal/physical-state propagation with a validation step (conflict detection) is close in spirit to the Stage-2A loop, applied to physical rather than abstract-causal or relational chains. |
| **5. Real/naturalistic text + unproduced slice** | MTurk-elicited plausible/implausible story pairs (freshly crowdsourced, NOT built on ROCStories, contrary to an initial assumption — confirmed this cycle). Produced, not wild; no unproduced slice found. |
| **Data access** | HF `sled-umich/TRIP`, GitHub sled-group. Size figures inconsistent across sources this cycle (one summary: 2,147 stories; HF card: ~4,600 examples across Cloze/Order splits) — needs direct reconciliation before committing. |
| **Baseline vs SOTA vs human** | Random ~48-50% accuracy / ~11% consistency / 0% verifiability -> SOTA (CGLI) ~93-94% accuracy / 76-77% consistency / only 25-28% verifiability. **No human-performance number was ever published** by the original authors (confirmed absent, checked twice) — a real evidentiary gap distinct from CLUTRR/ProPara's more complete pictures. |

### #4. TORQUE (Ning, Wu, Han, Peng, Roth, EMNLP 2020, arXiv:2005.00242) — re-audited, not re-scored from scratch

| Criterion | Trap-check finding |
|---|---|
| **1. Content ceiling** | No published BoW/lexical baseline (only BERT/RoBERTa variants evaluated), but the tense/aspect/reporting-verb structure of news text structurally resists a naive text-order shortcut — confirmed via a worked example (pluperfect "had found" temporally precedes a later-appearing "said" despite following it in surface order). **Lean PASS, unmeasured.** |
| **2. Reasoning non-trivial given structure** | **STILL THE OPEN QUESTION, exactly the one that killed WIQA.** No paper (including the original) analyzes whether TORQUE's questions require transitive composition through an UNSTATED intermediate relation, or reduce to N independent pairwise judgments against one query event bundled into a single question. This axis is UNVERIFIED, not passed — this is a genuine, not cosmetic, gap in the record 4 months after the benchmark was first scored favorably on a different axis (structural content-ceiling) without this specific check being run. |
| **3. Extractable structure** | Event triggers are PRE-TAGGED by the dataset (removes our hardest extraction failure mode entirely — a real advantage over every other candidate here). |
| **4. Exercises our strongest organ** | Exercises the adjacency-based temporal mechanism from the E4 gate-test (MIDDLE_BAND), NOT the causal VALIDATE loop — needs a genuinely new pairwise/transitive-relation extension, unproven at this granularity. |
| **5. Real/naturalistic text + unproduced slice** | Real news snippets (3.2k passages) — the most naturalistically-sourced text of any candidate here (found news text, not elicited-to-spec). No confirmed unproduced/held-out-in-the-wild slice, but closest of the shortlist to "real world" provenance. |
| **Data access** | GitHub `qiangning/TORQUE-dataset` only — **no canonical HF dataset found** (a HF hit named "TORQUE" is an unrelated Devanagari table-QA dataset — do not confuse). Test gold answers withheld for leaderboard. 24.9k events / 30.7k questions (21.2k human-generated + ~9.5k templated). |
| **Baseline vs SOTA vs human** | RoBERTa-large EM 51.1% / F1 75.2% vs. **Human F1 95.3% / EM 84.5%** — the largest human/SOTA gap of any candidate scanned (33.5 EM / 20 F1 points), genuinely unsaturated. |

### #5. ROCStories-family sentence-ordering — NOT recommended, included to close the loop

Given N shuffled sentences of a real crowd-written short story, reconstruct order (Kendall-tau /
perfect-match-ratio). **Lean FAIL.** No random-baseline or LM-perplexity-only baseline was found
published for the ordering task itself, but a directly analogous result on the SAME corpus family
(Schwartz/Cai 2017's Story Cloze result: shallow candidate-ending stylistic features ALONE, no story
context read at all, hit 72.4% on a task that looked like it needed causal/commonsense reasoning) is a
strong content-ceiling red flag by direct analogy — unrefuted for ordering specifically because nobody
has checked. Structurally, ROCStories items are only 5 sentences, so reconstructing full order reduces
to 4 adjacent pairwise judgments plus MECHANICAL transitive closure — not a separately-exercised
reasoning step, unlike CLUTRR where composition depth is the entire independent variable under test.
Would need >10-sentence documents (where global-vs-local methods provably diverge, per B-TSort/topological-
sort literature) to plausibly avoid this trap, at which point it stops being "real short story" text and
starts being multi-paragraph document ordering — a different, larger engineering lift not scoped here.

**Also screened and ruled OUT by construction (single-hop, or confirmed content leak, regardless of
fresh measurement)**: e-CARE (explicit single-hop COPA-style, ~57%-vs-50%-chance hypothesis-only
artifact never fully eliminated); GLUCOSE (explicitly scored per-sentence, no cross-sentence
consistency, free-generation); TellMeWhy (self-reported: 71% of questions have the answer literally
stated in text, best model does well exactly when lexical overlap is high — a CONFIRMED content-ceiling
failure, disclosed by the original authors); ESTER (confirmed single-hop per question, self-reported
question-word/proximity leakage); CRAB (real, hard, actively-verified LLM-memorization shortcut found by
its own authors — a good methodological precedent, but each judgment is pairwise not
multi-fact-compositional, and inter-annotator agreement is low, alpha=0.28); OpenPI (state changes
generated from the CURRENT step via single-step commonsense, not composed across un-mentioned steps —
the same "structure = the answer" pattern as WIQA; separately, its scoring metric is documented as
gameable by cheap repetitive output, OpenPI-C Findings-ACL-2023).

---

## 2. #1 recommendation + why + biggest risk

**Recommend CLUTRR as the next flagship pick, with ProPara pre-committed as the immediate follow-on
(not a fallback — a planned second stage).**

**Why CLUTRR first:** it is the only candidate in this scan (and across the whole prior WIQA/TORQUE/
MC-TACO scorecard) where the non-triviality-given-structure property is a **guarantee of the data-
generation process**, not an emergent empirical property we have to hope holds. That is categorically
stronger evidence than anything WIQA or TORQUE offer, both of which rest on "no shortcut has been found
yet" — exactly the posture that failed us on WIQA. CLUTRR also uniquely lets us separate our own
EXTRACTION-organ performance from our COMPOSITION-organ (Stage-2A) performance, because the published
literature already shows text-models fail almost entirely on extraction while composition-given-correct-
extraction is easily learnable (GAT to 1.0, CTP 0.89-0.99 even at k=10) — meaning if our system
underperforms, CLUTRR tells us WHICH of our two owned capabilities is weak, a diagnostic no prior
benchmark in this program has offered.

**Why ProPara as the deliberate second stage, not a hedge:** CLUTRR's one real weakness is criterion 5
— it can never demonstrate a win on naturalistic prose, since it is always graph-constructed. ProPara
is the strongest naturalistic-prose complement found: real elicited science-process text, and the ONLY
candidate in this scan with a directly MEASURED (not just structural) demonstration that cross-step
memory beats surface pattern-matching specifically on the sub-metric that requires it (2.4% -> 35.9% F1
on Cat-3 location tracking). Sequencing CLUTRR -> ProPara answers "does our composition organ work at
all" before spending engineering effort on "does it work on real prose," instead of conflating the two
questions the way every prior arc did.

**The single biggest risk that CLUTRR is secretly a WIQA-in-disguise**, stated plainly per the
instruction not to gloss over this: **no bag-of-words or partial-extraction baseline has ever been
published for CLUTRR.** The specific failure mode to fear is a WIQA-style but PARTIAL leak: predicting
the target relation from ONLY the first and last stated fact in the chain (ignoring interior links)
could plausibly recover meaningful accuracy at short k, because kinship composition has real regularity
(two "child-of" hops frequently compose to "grandparent" almost regardless of the middle entity). The
published chain-length-degradation signature makes a TOTAL, chain-invariant leak (WIQA's exact failure)
implausible, but does not rule out THIS partial version, which would still corrupt any claimed
mechanism-attributable win at low k. This is the mandatory first measurement before any build commitment
(next section) — running it FIRST, not after building, is the actual process fix this drill is meant to
deliver, since every prior benchmark trap was discovered only after committing engineering effort.

---

## Cheap decisive test

Before building anything (no organ extension, no new extraction code): pull CLUTRR (`CLUTRR/v1` on
Hugging Face, `gen_train23_test2to10` split, dev = 2,020 items spanning k=2..10) and measure THREE
numbers, all off a single afternoon of scripting, no GPU:

1. **MAJORITY baseline** (most frequent relation label in the split) — sanity floor, expect near
   uniform-chance-ish given 22 balanced-ish classes (structural expectation ~4.5-10%, confirm directly).
2. **BAG-OF-RELATIONS baseline**: a classifier (even a lookup table / logistic regression) over the
   MULTISET of relation words that appear anywhere in the story text, with no chain-order or
   chain-position information — the CLUTRR-analog of MCScript2.0's BoW=0.629 measurement.
3. **ENDPOINT-ONLY shortcut baseline** (the critical, WIQA-history-informed probe): predict the target
   relation using ONLY the first and last stated relation in the chain (extract just those two facts,
   apply the composition rule as if the chain had length 2, ignore every interior link) — this is the
   CLUTRR-analog of WIQA's polarity-echo probe, the single most important number in this whole test
   given that WIQA's trap was exactly this shape (one directly-extractable fact standing in for the
   full reasoning chain).

Then check: does the ENDPOINT-ONLY baseline's accuracy **degrade as k grows** (k=2 vs. k=6 vs. k=10),
matching the published chain-length-degradation signature real composition requires — or does it stay
flat/high (the WIQA-leak signature)?

Cheap (public dataset, no GPU, a lookup-table/logistic-regression baseline is an afternoon of work),
can-fail (a genuine risk this baseline could reveal a real partial shortcut, not a strawman), one-lever
(measurement only, isolates exactly the two traps that have burned this program before any composition-
loop engineering is committed), reuses the design grammar (majority + surface-shortcut baseline +
chain-length-degradation-as-signature) already validated across MCScript2.0/WIQA/E4.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND)

- **HARD-PASS (clears CLUTRR for engineering investment):** MAJORITY <= 15% AND BAG-OF-RELATIONS <=
  MAJORITY + 15 points AND ENDPOINT-ONLY beats MAJORITY by < 20 points absolute at k=2 AND
  ENDPOINT-ONLY's edge over MAJORITY shrinks by >= 50% (relative) from k=2 to k=6 (degradation
  signature confirmed empirically, not just inferred from the literature). Predicted P ~ 0.50
  (deflated per calibration; the structural generation-process guarantee makes this more likely than a
  coin flip, but the endpoint-shortcut risk is genuinely unmeasured).
- **HARD-FAIL (reject CLUTRR, do not build; fall back to ProPara as primary or re-open the shortlist):**
  ENDPOINT-ONLY matches or nearly matches an oracle-given-full-chain accuracy at short k (the WIQA
  signature: one cheap extraction standing in for the whole reasoning chain) OR ENDPOINT-ONLY's edge
  over MAJORITY stays FLAT or GROWS from k=2 to k=6 (chain-invariant leak, ruling out genuine
  composition being required at the k values we'd actually build for).
- **MIDDLE_BAND (proceed with a narrowed claim):** ENDPOINT-ONLY shows a real but PARTIAL edge that
  degrades slower than expected — narrow the flagship claim to k>=4 (long-chain subset) where the
  shortcut is empirically shown to be weak, mirroring the E4/WIQA precedent of narrowing to a
  mechanism-distinctive subset rather than claiming an aggregate win the data doesn't support.
- **Independent prediction (benchmark-selection, not mechanism, so not subject to the same deflation):**
  TRIP and TORQUE will both remain UNVERIFIED against these same two traps until someone runs the
  equivalent measurement on them (P ~ 0.85, since this is simply reporting that "nobody has measured
  this yet" is a stable fact absent new information, not a probabilistic mechanism claim).

## Cross-thread synthesis

- Directly extends `notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_2026-08-10.md`: that
  note ranked WIQA #1 on a scorecard that (honestly, per its own text) had NOT yet measured a
  content-ceiling number for WIQA and had not yet discovered the sign-leak. This drill supplies the
  lens that scorecard was missing — an explicit, mandatory "does the answer reduce to one directly
  extractable fact" trap-check — and applies it prospectively to every new candidate BEFORE any build
  commitment, rather than discovering it after (which is exactly what happened to WIQA per the
  ORACLE-STRUCTURE DIAGNOSTIC in the backup doc).
- Directly answers the backup doc's "CEILING SYNTHESIS" strategic fork item (a): "find/build a benchmark
  that isolates non-trivial reasoning over EXTRACTABLE structure (may not exist in glass-box form)." This
  drill's honest answer: it does not exist in a form that passes all 5 criteria cleanly, but CLUTRR is a
  materially-better-verified candidate than anything scored before it, specifically on the two axes
  (content-ceiling, structure-is-not-the-answer) that killed the last three arcs.
- Confirms and sharpens (does not overturn) the prior note's TORQUE ranking: TORQUE remains a real
  candidate but its "criterion 2" status is now explicitly flagged UNVERIFIED rather than implicitly
  assumed passed on the strength of its clean content-ceiling story alone — the two criteria are
  independent and both must be checked, a distinction the earlier note did not have the WIQA post-mortem
  to sharpen yet.
- Extends the organ-inventory: this drill identifies that CLUTRR would need an entirely NEW extraction
  target (kinship-relation-from-prose) with no existing owned-organ head start, unlike WIQA (which
  reused `CausalLinkRegister` almost directly) — this is priced into the deflated P for the
  build-side claim (0.25, lower than WIQA's 0.32) and should be priced into any future engineering-cost
  estimate; do not assume CLUTRR is as cheap to build toward as WIQA was.

## Substrate-product implications

If CLUTRR clears the cheap decisive test and the composition loop then HARD-PASSes on it, the defensible
product claim is sharper than any prior arc: a glass-box system that reads short natural-language family
narratives, extracts individual stated relations, and answers questions about UNSTATED relations by
composing a validated symbolic chain — on a benchmark where, uniquely among everything scanned in this
program, the task's own construction GUARANTEES the answer cannot be read off any single sentence. This
directly demonstrates the multi-hop VALIDATE mechanism (arrests multiplicative error) on its actual home
turf for the first time in the program's history, since none of DesireDB/MCScript2.0/WIQA gave it a real
target. The honest limitation to state alongside any such win: CLUTRR text is not naturalistic prose, so
this alone would NOT be evidence the system works on real-world text — that claim requires the planned
ProPara follow-on (or, if ProPara's own build reveals problems, a fresh naturalistic-prose candidate),
and marketing/positioning must not conflate "wins on CLUTRR" with "reads real narratives," the same
discipline failure this program has now made three times (DesireDB, MCScript2.0, WIQA all over-claimed
briefly before an honest downgrade).

## Honest deflated grade

**Deflated grade: MEDIUM on the CLUTRR pick, MEDIUM-LOW on the first-experiment win, same as the WIQA
note's grading pattern but with the ranking judgment itself deflated further** (0.50 here vs. 0.60 for
WIQA), specifically because the WIQA pick's own P=0.60 later turned out to license real engineering
effort before the trap was found — a costlier failure mode than this drill is willing to repeat. The
ENDPOINT-ONLY shortcut check (Cheap decisive test, above) is the single highest-leverage next action:
it is cheap (an afternoon, no GPU) and directly answers the question that, unmeasured, would recreate
the exact WIQA failure a fourth time. Do not commit organ-extension engineering to CLUTRR (or any
candidate) before that number is on disk.

**Data-access blockers for the USER to clear:** none requiring USER action for the CLUTRR measurement
step (public HF dataset, no login found). One item to flag, not block on: CLUTRR's CC BY-NC 4.0 license
is non-commercial — fine for the validation/R&D use this drill recommends, but if a shipped product
claim is later built on CLUTRR-trained/CLUTRR-validated components, either regenerate an equivalent
corpus via the open `facebookresearch/clutrr` generator (unrestricted license on the code itself, not
independently re-verified this cycle) or get a license clarification before any commercial framing.

## Citations (verified count)

Four parallel Sonnet lit-scan lanes, ~40 distinct sources triangulated (paper + arXiv/ACL-Anthology +
GitHub/Hugging-Face dataset card cross-checked per major finding, consistent with this program's
citation-verification standard):

**Lane A (CLUTRR):** Sinha et al. 2019 EMNLP-IJCNLP D19-1458/arXiv:1908.06177 (full PDF read directly);
Minervini et al. 2020 (CTP) arXiv:2007.06477; Li & Minervini 2022 arXiv:2203.10620; Yang, Ishay & Lee
2023 (EMNLP) arXiv:2307.07696; HF dataset card `CLUTRR/v1`; GitHub `facebookresearch/clutrr` +
`koustuvsinha/clutrr-baselines`; a 2026 AAAI student-abstract depth-probe (title/authors not fully
resolved this cycle, flagged as weaker-sourced).

**Lane B (ProPara/OpenPI):** Dalvi et al. 2018 NAACL N18-1144/arXiv:1805.06975; GitHub `allenai/propara`
+ AI2 data/leaderboard pages; CGLI arXiv:2208.12848; MeeT arXiv:2210.06444; Du et al. "Be Consistent!"
NAACL 2019; ProPara-CRTS IWCS 2025 aclanthology.org/2025.iwcs-main.22; Tandon et al. 2020 (OpenPI)
arXiv:2011.08092; GitHub `allenai/openpi-dataset`; OpenPI-C (Findings ACL 2023) arXiv:2306.00887;
OpenPI2.0 (EACL 2024) arXiv:2305.14603.

**Lane C (TORQUE + ordering):** Ning et al. 2020 EMNLP 2020.emnlp-main.88/arXiv:2005.00242; GitHub
`qiangning/TORQUE-dataset`; ROCStories HF cards (`mintujupally/ROCStories`, `Ximing/ROCStories`);
Logeswaran et al. 2016; Gong et al. 2016 arXiv:1611.04953; Prabhumoye et al. 2020 (B-TSort)
arXiv:2005.00432; BERSON 2020; Cui et al. STaCK 2021; BERT4SO 2021; Chowdhury et al. (Re-BART) EMNLP
2021 arXiv:2104.07064; Schwartz et al. 2017 / Cai et al. 2017 (Story Cloze shallow-feature result).

**Lane D (TRIP/e-CARE/broad net):** Storks, Gao, Zhang, Chai 2021 (TRIP) EMNLP Findings
arXiv:2109.04947; HF `sled-umich/TRIP`; Coman et al. (Breakpoint Transformer) arXiv:2211.07950; CGLI
arXiv:2208.12848 (cross-referenced with Lane B); "From Heuristic to Analytic" arXiv:2310.18364; Elazar
et al. "Shortcutted Commonsense" EMNLP 2021; Du et al. 2022 (e-CARE) ACL arXiv:2205.05849; GitHub
`Waste-Wood/e-CARE`; COPA "Clever Hans" critique arXiv:1911.00225; Mostafazadeh et al. 2020 (GLUCOSE)
arXiv:2009.07758; Lal et al. 2021 (TellMeWhy) ACL Findings arXiv:2106.06132; Han et al. 2021 (ESTER)
EMNLP arXiv:2104.08350; Romanou et al. 2023 (CRAB) EMNLP arXiv:2311.04284 + GitHub `agromanou/CRAB`.

Carried (not re-derived) from prior notes, credited there: the WIQA ORACLE-STRUCTURE DIAGNOSTIC finding
(8bd8046f3, `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`); the MCScript2.0 BoW=0.629 measurement
(prior arcs); Stage-2A HARD_PASS result (013f1481e, `hdlab`/`experiments` — VALIDATE arrests
multiplicative error). No citation fabricated or asserted from memory without a live scan this cycle by
one of the 4 lanes; every unresolved/inconsistent figure (TRIP dataset size, ProPara data license,
CLUTRR generator code license) is flagged as such above, not presented as settled.
