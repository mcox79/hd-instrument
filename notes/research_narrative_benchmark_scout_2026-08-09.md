# Research: narrative comprehension benchmark scout (the WHERE pillar)

**Filed:** 2026-08-09 by research (Sonnet synthesis over 4 parallel Sonnet lit-scan lanes, each
reading primary sources — ACL Anthology / arXiv / AAAI / TACL PDFs directly, not abstracts).
**Trigger:** program-gating question — which public narrative-comprehension benchmark should be
PRIMARY for the grounded self-growing narrative comprehension program (brain-faithful, glass-box,
CLS/sleep-consolidation acquisition loop, demonstrating the compounding property).
**Query-privacy:** all 4 lanes searched only public dataset/paper/author names (Ostermann, Weston,
Mostafazadeh, Rashkin, Chaturvedi, Zhou/Khashabi, Kočiský, etc.) — these ARE the public benchmark
identifiers, so no substrate-internal terms went off-platform.
**Scope:** VET 7 named candidates (MCScript/MCScript2.0, ROCStories/Story Cloze, Chaturvedi AAAI16,
Story Commonsense, NarrativeQA, MCTACO, bAbI) against 5 hard criteria: (1) deep-inference residual,
not artifact/noise; (2) glass-box-evaluable (classification/MC, no free-form generation); (3) a real
published baseline number to beat; (4) exercises grounded WORLD/SCRIPT knowledge specifically; (5) a
train/exposure split disjoint from held-out test, usable by the acquisition loop.

## HEADLINE

**Recommend MCScript2.0 (Ostermann, Roth & Pinkal, *SEM 2019, ACL Anthology S19-1012 /
arXiv:1905.09531) as the PRIMARY benchmark, with Story Commonsense (Rashkin et al., ACL 2018,
P18-1213) as a SECONDARY goal/motivation companion and MCTACO (Zhou et al., EMNLP 2019, D19-1332)
as a tertiary held-out cross-domain generalization probe.** MCScript2.0 is the only candidate in
the whole scan that is BY DESIGN, and by its own authors' explicit validated relabeling, a
deliberately rebalanced 50%-script-knowledge / 50%-text-based 2-way multiple-choice benchmark
(best published system 72% overall vs. 97% human vs. 50% chance — real, unsaturated headroom), with
clean disjoint train/dev/test splits BY TEXT (14,191q/2,500 texts train; 2,020q/355 texts dev;
3,610q/632 texts test) and — critically — a **built-in per-item ablation** (each question is
pre-labeled script-based / text-based / text-or-script by the dataset's own crowdsourced validation
protocol) that gives the acquisition loop a free, dataset-native falsifiable discriminator: if grown
script grounding is doing real work, held-out accuracy on the SCRIPT-BASED subset should improve
more than the TEXT-BASED subset as exposure grows — exactly the same "isolate the mechanism via a
pre-existing item-type label" pattern that made the DesireDB But-Present ablation the strongest
finding of the 2026-08-08 sibling drill. **The single biggest counter-finding of this whole scan is
a decisive negative: ROCStories/Story Cloze (both v1.0 and the "debiased" v1.5) must be AVOIDED as
a primary or even validating benchmark** — three independent primary sources (Cai et al. 2017;
Sharma et al. 2018's own admission that their debiased set still leaks 64.4% to a context-blind
classifier; and, most decisively, Yao et al. LREC 2022's direct dissociation study showing models at
93% Cloze accuracy collapse to 37-46% — barely above chance — when asked to identify WHICH kind of
narrative/causal reasoning justified their answer) prove that high Cloze accuracy does NOT entail
genuine script/causal understanding. Using Story Cloze as validation would risk a false-positive
confirmation of the program's central compounding-grounding claim. A second major finding worth
separate emphasis: MCScript v1 (the original, non-"2.0" version) is **self-refuted by its own
authors' follow-up paper** — a manual audit found script knowledge "only marginally relevant" for
over 90% of its nominally commonsense-labeled questions, meaning the field's own first attempt at
this exact benchmark type had to be rebuilt once already; MCScript2.0 is that rebuild, and its
recency plus lower external citation volume means its "script-based" label integrity has NOT yet
been independently artifact-audited by anyone outside the author group — this is the primary
residual risk on the recommendation (see Honest risks below), and this program should run its own
answer-only/passage-only artifact check (Kaushik & Lipton, EMNLP 2018 methodology) on the
script-based subset before fully trusting the number, exactly the audit MCScript v1 never got before
this program would have otherwise leaned on it.

P_deflated (bibliographic/numeric facts below are accurate, correctly cited, and correctly
characterize each benchmark's residual): **0.72** (high — 4 independent lit-scan lanes, ~112 total
tool-uses, each reading primary PDFs directly rather than secondary summaries; deflated from raw
~0.90 per lit-scan calibration discipline because several details are flagged UNVERIFIED inline:
MCScript2.0's current live-download status, whether any post-2019 SOTA update exists for it, and the
absence-not-confirmed-absence of an external artifact audit for both MCScript2.0 and Story
Commonsense).
P_deflated (the narrower claim that MCScript2.0 specifically is the RIGHT primary pick for THIS
program): capped at **0.50** per mandatory novel-synthesis ceiling — this is a plausibility read
connecting independently-verified external benchmark facts to this program's specific needs, not a
tested claim.

## Ranked shortlist

| Rank | Benchmark | Role | Verdict |
|---|---|---|---|
| 1 | **MCScript2.0** (Ostermann, Roth & Pinkal, *SEM 2019) | **PRIMARY** | Deliberately rebalanced script-knowledge residual, glass-box 2-way MC, clean disjoint splits, built-in per-item script/text ablation, real headroom (72% vs 97% human) |
| 2 | **Story Commonsense** (Rashkin et al., ACL 2018) | **SECONDARY** (goal/motivation companion) | Dense multi-label glass-box output (Maslow/Reiss/Plutchik), documented knowledge-injection improvement proves residual is knowledge-shaped, shares ROCStories exposure-corpus infra, directly complements the existing `goal_achievement.py` thread |
| 3 | **MCTACO** (Zhou, Khashabi, Ning & Roth, EMNLP 2019) | **TERTIARY** (held-out cross-domain probe only) | Glass-box, large headroom (69.9→87.1 F1), genuine world-knowledge-about-time residual, but NO native training set by explicit authorial design — cannot anchor the acquisition loop's exposure phase itself |
| 4 | **NarrativeQA** (Kočiský et al., TACL 2018) | REJECT (format) / informational | Best-evidenced deep causal/event residual in the ENTIRE scan (Mou et al. 2021: causal-relation questions are hardest for every system, ~75% event-centric) — validates the program's core thesis that real difficulty is causal/event-structural — but is free-form generation scored by ROUGE/BLEU/METEOR, disqualified by the glass-box hard constraint |
| 5 | **MCScript v1** (Ostermann et al., LREC 2018) | Superseded / fallback only | Self-critiqued by the authors' own MCScript2.0 paper: script knowledge "only marginally relevant" for >90% of inspected nominally-commonsense questions; 72.6% of items are plain text-based |
| 6 | **ROCStories / Story Cloze v1.0 & v1.5** (Mostafazadeh 2016; Sharma 2018) | **AVOID as primary/validation**; raw ROCStories corpus OK as unlabeled exposure text only | Decisively dissociated from genuine script/causal reasoning (Yao et al. 2022); still leaks 64.4% context-blind even after debiasing; re-saturated to 90%+ by generic transformer transfer within ~1 year |
| 7 | **bAbI (incl. Task 20)** (Weston et al. 2015) | **AVOID** as a target; OK only as a cheap CI sanity-check | Directly artifact-broken (Kaushik & Lipton: passage-only baseline = 100% with the question withheld); field's own 2022 ACL paper (Dyna-bAbI) calls it solved/toy |
| 8 | **Chaturvedi AAAI16** (Chaturvedi, Goldwasser & Daumé III) | Informational only, already covered | Own feature set is candidly connotation-lexicon/discourse-marker-driven, not real script knowledge; tiny (175-1000 instances, no dev set); already subsumed by the existing `research_desiredb_hard_residual_prior_art_2026-08-08.md` thread (DesireDB/Rahimtoroghi 2017 is its direct successor) |

## Recommended primary: MCScript2.0 — exact numbers

**Citation:** Simon Ostermann, Michael Roth, Manfred Pinkal, "MCScript2.0: A Machine Comprehension
Corpus Focused on Script Events and Participants," *SEM 2019 (Joint Conference on Lexical and
Computational Semantics), ACL Anthology S19-1012 / arXiv:1905.09531. (Correction to the task's own
framing: this is NOT SemEval-2019 Task 10 — that task-number slot in SemEval 2019 was actually "Math
Question Answering" [S19-2153], unrelated. MCScript2.0 is a standalone *SEM 2019 paper, not a
SemEval shared task. MCScript **v1** was the SemEval-2018 Task 11 shared task.)

**Task format:** 2-way multiple-choice QA. Narrative texts about everyday scenarios (going to the
doctor, eating at a restaurant, etc.), each with several questions, each question with exactly 2
candidate answers (one plausible-correct, one plausible-incorrect).

**Dataset size / splits (by TEXT, avoiding leakage):**
- Total: 19,821 questions over 3,487 texts.
- Train: 14,191 questions / 2,500 texts.
- Dev: 2,020 questions / 355 texts.
- Test: 3,610 questions / 632 texts.

**Item-type label (the free built-in ablation):** every question is pre-labeled by the dataset's own
validated crowdsourcing protocol as script-based (9,935), text-based (7,908), or text-or-script
(1,978) — the deliberate design fix for MCScript v1's flaw, confirmed via the authors' own
validation numbers.

**Exact baseline table (from the *SEM 2019 paper):**

| Model | Overall | Script-based | Text-based |
|---|---|---|---|
| Chance / majority | 50% | 50% | 50% |
| Logistic Regression | 61% | 56% | 67% |
| Attentive Reader | 65% | 63% | 68% |
| **TriAN + ConceptNet (best published)** | **72%** | **67%** | **78%** |
| Human | 97% | — | — |

**Baseline-to-beat for this program:** the exact number to beat is **72% overall accuracy
(TriAN+ConceptNet)**, with the more mechanism-diagnostic target being the **67% script-based-subset
accuracy** specifically (since the program's central claim is about SCRIPT knowledge, not overall
reading comprehension) — a glass-box system that beats 67% on the script-based subset while a
simple/no-exposure baseline sits near the 56% logistic-regression floor would be the clean,
citable win.

## Acquisition-loop mapping (exposure / held-out split)

- **EXPOSURE phase:** the 2,500-text / 14,191-question TRAIN split. The acquisition loop
  (`hdlab/grounding_acquisition_loop.py` — `Library`, `Trace`, `consolidation_pass`,
  `schema_consistency_split_half`, `surprise_order`, the flag-not-understood -> library ->
  consolidate -> bank -> grow loop with the escalate-don't-commit guard) processes these TEXTS
  (not necessarily the QA labels) as exposure narratives from which script-role bindings and
  script-effect templates are grown.
- **DEV split (2,020q / 355 texts):** used as the visible, iterable checkpoint during acquisition-
  loop development — NOT the final reported number.
- **HELD-OUT TEST (3,610q / 632 texts, disjoint by TEXT from train/dev):** stays blind until the
  final compounding-property demonstration run. Report the split BY THE DATASET'S OWN script-based
  vs. text-based item-type label, since that split is what makes the mechanism claim falsifiable
  (see Cheap decisive test below).
- **Compounding-property protocol:** run TEST accuracy at multiple exposure checkpoints (e.g., after
  0%, 25%, 50%, 100% of the 2,500 TRAIN texts have passed through the acquisition loop). The
  trend — improving accuracy specifically on the script-based TEST subset as exposure text count
  grows, with generalization holding on texts never seen during exposure — is the compounding
  signal the program needs to demonstrate. This also gives a natural per-checkpoint curve, not just
  a single before/after number, which is more convincing evidence of "improves with exposure" than
  a single endpoint comparison.

## Cheap decisive test

**Stage 0 (BLOCKING — do this FIRST, before any build commitment, ~30 min):** confirm a live,
current, gold-labeled download of MCScript2.0 (train+dev+test with labels) actually exists and is
obtainable. Lane A's search found MCScript v1 has an active third-party mirror (via Ashutosh Modi's
personal datasets page) but **could not confirm the same for MCScript2.0** — it is not listed there,
not found as a standalone Hugging Face `datasets` entry, and only appears indirectly, reformatted,
inside the Natural Instructions collection (`task165_mcscript_question_answering_commonsense`,
`task164_mcscript_question_answering_text` — unclear which MCScript version these wrap). Contingency
if MCScript2.0 truly cannot be obtained: fall back to MCScript v1 filtered to ONLY its
commonsense/script-labeled subset (~3,914 of 13,939 questions) — weaker (the v1 authors' own
follow-up paper says script relevance is marginal for >90% of even that subset) but usable as a
degraded Plan B rather than abandoning the whole benchmark family.

**Stage 1 (calibration, ~1-2 hrs):** run the existing (pre-acquisition-loop, zero-exposure)
architecture on the MCScript2.0 test set as-is, with no grown grounding. This replicates a published
number on our own harness before any exposure-driven delta is trusted.

**Stage 2 (the real test — the compounding claim):** run the acquisition loop over the 2,500-text
TRAIN exposure corpus, then re-evaluate on held-out TEST, broken out by the dataset's own
script-based / text-based item-type label.

**Stage 3 (false-consolidation guard — pairscramble control):** re-run Stage 2 with the exposure
texts' internal event order pair-scrambled (the same pairscramble-must-collapse discipline already
used elsewhere in this program) — this must NOT reproduce the same gain, or the mechanism is
absorbing lexical frequency rather than genuine sequential/script structure.

## Falsifiable predictions

**HARD-PASS (Stage 0):** a gold-labeled MCScript2.0 train/dev/test package is obtained and its
question counts match the paper's published table (14,191/2,020/3,610) within rounding — confirms
the harness is reading the real dataset, not a corrupted or mismatched mirror.
**HARD-FAIL (Stage 0):** no working download exists anywhere (including the Natural Instructions
repackaging, once its underlying MCScript version is confirmed) — triggers immediate fallback to
the MCScript v1 script-labeled-subset Plan B, or, if that also proves too degraded on inspection,
escalates to Story Commonsense as the de-facto primary instead.

**HARD-PASS (Stage 1):** the zero-exposure architecture-only baseline scores in the 50-65% range on
MCScript2.0 overall (i.e., is in the neighborhood of the published Logistic-Regression/Attentive-
Reader band) — confirms the harness/parsing pipeline is comparable to the field's own baselines
before any acquisition-loop claim is trusted.
**HARD-FAIL (Stage 1):** score is below 45% (parsing/harness bug, distrust everything downstream) or
already above 72% with zero exposure (something is leaking test information or the "zero-exposure"
condition isn't actually zero-exposure — investigate before proceeding).

**HARD-PASS (Stage 2, the real compounding claim):** held-out TEST accuracy on the SCRIPT-BASED
subset improves by a measurable margin (>=5 percentage points) relative to the Stage-1 zero-exposure
baseline as the acquisition loop processes the 2,500-text exposure corpus, AND this improvement is
significantly larger than any concurrent improvement on the TEXT-BASED subset — isolating that the
gain traces specifically to grown script knowledge, not generic reading-comprehension drift or a
side effect of processing more text in general.
**HARD-FAIL (Stage 2):** no measurable script-based-vs-text-based improvement differential (or a
negative one), OR overall accuracy does not move beyond noise (~+/-2pp) as exposure text count grows
from 0 to 2,500 texts. Per the "flat learning result = broken experiment, not a ceiling" discipline
(MEMORY.md), a flat result here triggers a DIAGNOSE response (not-actually-learning /
no-genuinely-new-content / underpowered exposure corpus), not a conclusion that script-grounding
acquisition has hit an intrinsic limit.

**HARD-PASS (Stage 3, false-consolidation guard):** the pair-scrambled-exposure condition produces a
substantially SMALLER script-based-subset gain than the ordered-exposure condition (ideally near
zero) — confirms genuine sequential/script-structure learning, not surface lexical-frequency
absorption.
**HARD-FAIL (Stage 3):** pair-scrambled exposure produces the SAME gain as ordered exposure —
signals a false-consolidation failure (the acquisition loop is banking something real but not
script-structural), which per the acquisition loop's own escalate-don't-commit guard should block
promotion of whatever got banked during that run.

## Honest risks

1. **MCScript2.0 download availability is UNCONFIRMED** (see Stage 0 above) — this is the single
   most concrete near-term blocker and must be resolved before any further build commitment.
2. **No external artifact audit exists for MCScript2.0's script-based label.** Unlike ROCStories/
   Story Cloze (which got extensively artifact-hunted by three independent groups over 2017-2022)
   or bAbI (Kaushik & Lipton 2018), MCScript2.0 has had essentially no independent scrutiny since
   its 2019 release — the only critique of the MCScript family is the authors' OWN critique of their
   OWN prior version. Given that MCScript v1's "script-based" label was itself later shown to be
   largely spurious by the same author group, this program should not assume MCScript2.0's relabel
   is clean without running its own answer-only/passage-only baseline (Kaushik & Lipton methodology)
   on the script-based subset specifically, before trusting any exposure-driven gain as genuine.
3. **No confirmed post-2019 SOTA update** for MCScript2.0 was found — meaning we don't know how far
   a modern (non-glass-box) system could push this benchmark, so 72% may understate how much
   headroom is realistically closable by ANY method, glass-box or not. This is a minor risk (doesn't
   affect the glass-box-vs-published-baseline comparison) but affects how we frame "state of the
   art" in any external write-up.
4. **LLM-dependence / moving-target risk is comparatively LOW for this specific pick** relative to
   Story Cloze — MCScript2.0 has almost no citation/leaderboard activity after 2019 (unlike Story
   Cloze, which was re-saturated to 90%+ by BERT+MNLI transfer within about a year of its 2018
   debiasing), so there is no visible arms race pushing the ceiling up while we work — but this cuts
   both ways: it could also mean the benchmark quietly fell out of use because it wasn't compelling
   to the field, which is worth being aware of rather than assuming is purely a neutral fact.
5. **Story Commonsense's "easy" categories are lexically anchored** (per Rashkin et al.'s own
   discussion: food/eating words trivially predict physiological-need labels) — when using it as
   the secondary benchmark, the diagnostic value is concentrated in the HARDER Reiss/rare-category
   cells (F1 ~20-40), not the headline aggregate number; report broken out by category, not as one
   pooled score.
6. **Glass-box friction on MCTACO:** its explicit no-training-set design (authors' own words: "not
   reasonable to expect a system to be trained solely on this data... development data [is] only
   providing a definition of the task") means it cannot anchor the acquisition loop by itself. It
   should be used ONLY as a zero-shot cross-domain generalization check after the loop has been
   grown on MCScript2.0/Story Commonsense text — using its dev split as pseudo-training would
   violate the authors' own stated design intent and likely produce a spuriously optimistic number.

## Cross-thread synthesis

- **Extends `notes/research_desiredb_hard_residual_prior_art_2026-08-08.md`.** That drill deeply
  vetted DesireDB/Rahimtoroghi 2017 (goal fulfillment in first-person blog narrative) and found it
  NOISE-CAPPED (~45% of its hard residual is data-noise) — the wrong benchmark for deep-inference
  demonstration. This drill's Chaturvedi AAAI16 finding reinforces that diagnosis from the opposite
  direction: DesireDB's own direct predecessor (Chaturvedi et al. 2016) is shown here to be
  candidly connotation-lexicon/discourse-marker-driven, not real script/world-knowledge-dependent,
  by the ORIGINAL authors' own feature description — the entire Chaturvedi-lineage (Chaturvedi 2016
  -> DesireDB 2017) is consistently thinner on genuine script knowledge than either MCScript2.0 or
  Story Commonsense. This is convergent evidence (2 independent drills, different methods) that the
  desire/goal-fulfillment benchmark family generally is a weaker match for THIS program's specific
  "grounded script/world knowledge" claim than the script-focused or naive-psychology-focused
  families scouted here — though it remains directly useful for the SEPARATE, already-in-flight
  `goal_achievement.py` program thread (valence + action-recurrence + PDTB channels), which is a
  different (though related) research question from benchmark selection for the acquisition loop.
- **Extends `notes/prior_art_modern_neurosymbolic_narrative_2026-08-06.md`.** That scan found "no
  modern working interpretable system tracks goals -> outcomes as a first-class representation" and
  separately flagged ROCStories/Story Cloze's style-artifact finding (Schwartz 2017, Cai 2017) as a
  "cautionary result... warns any goal/outcome benchmark must guard against this exact style-artifact
  shortcut." This drill independently and much more strongly confirms that warning was correct and
  underestimated the severity — the newer Yao et al. 2022 dissociation study (93% Cloze accuracy vs.
  37-46% causal-reasoning-category identification) is decisive primary-source evidence that the
  concern wasn't just a historical 2017-era exploit that debiasing later fixed; the field's own 2022
  paper shows the dissociation persists even post-debiasing. This upgrades that prior note's
  "cautionary result" framing to an outright AVOID recommendation for Story Cloze as validation.
- **Directly informs the acquisition-loop / script-bridge grounding threads** (`hdlab/
  grounding_acquisition_loop.py`; the toy-scale script-bridge grounding proofs referenced in the
  task brief) — this drill supplies the first concrete, real (non-toy), publicly-benchmarked corpus
  with a native train/exposure vs. held-out split and a built-in mechanism-isolating ablation
  (script-based vs. text-based item labels) that those mechanisms have not yet been run against.
  Everything proven so far (the acquisition loop's growth+guard behavior, the script-bridge
  mechanism at toy scale) has been validated on synthetic/toy material; MCScript2.0 is the natural
  next rung — real crowdsourced narrative text, with a residual the field's own authors specifically
  engineered to require script knowledge.

## Substrate-product implications

Never framed as publication value — product-relevant only. The concrete next action is Stage 0
(confirm MCScript2.0 is actually downloadable with gold labels) — this is a same-day, near-zero-cost
check that gates everything else and should happen before any further planning or build investment.
If Stage 0 clears, the natural sequencing is: (1) Stage 1 harness calibration against the published
Logistic-Regression/Attentive-Reader baseline band, cheap and fast; (2) run the acquisition loop over
the 2,500-text exposure corpus and report the script-based-vs-text-based split at multiple exposure
checkpoints — this is the actual product claim ("comprehension improves with exposure, specifically
on the script-knowledge-dependent items, generalizing to held-out narratives") and is exactly the
demonstration this program has been building toward; (3) the pair-scramble false-consolidation guard
run, which reuses the same discipline already applied elsewhere in this program, so no new
methodology needs to be invented, only re-pointed at this corpus. Story Commonsense is lower-priority
but cheap to add later as a second benchmark point, reusing the same ROCStories-family exposure-
corpus infrastructure and directly complementing the existing goal_achievement.py thread with a
denser, more diagnostic (5+19+8-dim) motivation/emotion label space. MCTACO should be held in
reserve as a "does the grown knowledge generalize to a genuinely different narrative register"
stretch check, not built into the primary pipeline.

## Citations (verified count)

**~30 distinct primary sources verified via WebSearch/WebFetch across 4 parallel lit-scan lanes**
(ACL Anthology, arXiv/ar5iv, AAAI proceedings, TACL, plus one *SEM/starsem venue), each lane reading
full paper text (not abstracts) for its assigned candidates. Two factual corrections made to the
task's own framing: (1) MCScript2.0 is a standalone *SEM 2019 paper (S19-1012), NOT "SemEval-2019
Task 10" (that slot was a different, unrelated math-QA task); (2) confirmed Chaturvedi AAAI16 and
DesireDB/Rahimtoroghi 2017 are genuinely distinct datasets (different corpora, different label
schemes) as the task brief anticipated, with a direct, primary-source-confirmed comparison (the
DesireDB authors re-ran their models on Chaturvedi's original test sets, per their own published
slides). Confidence is HIGH on essentially all bibliographic (author/year/venue) and headline-metric
facts (all read from primary PDFs, not secondary summaries); several secondary details are flagged
UNVERIFIED inline where a primary source could not be reached in-session (MCScript2.0 current
download status, whether a post-2019 SOTA exists for MCScript2.0 or MCTACO, whether an external
artifact-critique paper exists for MCScript2.0 or Story Commonsense specifically — absence of
evidence from a bounded search session, not confirmed absence).
