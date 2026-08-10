# Research: crutch-fade benchmark pick + fade-test design (DRILL 4 -- where we prove it)

Filed by: research (Sonnet, foreground, no nested sub-agents, per explicit dispatch OPS instruction --
direct WebSearch/WebFetch used instead of the usual 2-4-parallel-subagent breadth pattern).

Trigger: DRILL 4 of the simulation-engine arc. Drills 1-3 (SHAPE/MECHANICS/BUILD/CONTENT, 2026-08-09,
notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md +
research_brain_focus4_simulation_inference_mechanics_2026-08-09.md +
research_substrate_design_focus_simulation_2026-08-09.md +
research_content_causal_associative_knowledge_store_2026-08-09.md) converged on the architecture:
focus = a bounded cue/pointer (hdlab/situation_focus.py, Cowan-4) over an ACTIVATED-LTM FIELD (CSKG
1.24M causal edges, ATOMIC-dominated, exp_cskg_foundation_v1 HARD_PASS-certified + BEAGLE glass-box
associative), retrieved via cleanup_family.iterative_attractor / kg_traversal.KGStore, validated via
CausalLinkRegister typed cause/effect query (situation_model_accumulate.py) -- the retrieve-VALIDATE-
advance loop. Stage-2A (013f1481e) HARD_PASS 5/5 proved the LOOP mechanism works at toy scale (VALIDATE
arrests multiplicative error). Stage-2 sub-test B then HARD_FAILED the STORE at CSKG cardinality
(Hebbian single-[1024,1024]-W crosstalk collapse: relevant_recall 0.967 at 1K -> 0.000 at 30K+) --
a resonator-factorized rescue is testing now (af9073fbc), unresolved as of this drill. This note does
NOT touch that scale wall; it answers a different, parallel question the Director posed: **pick the
benchmark + design the can-fail test for the whole-arc THESIS** -- that a gap-driven external-knowledge
CRUTCH (the live pull-in/retrieve step) fires progressively LESS as exposure accumulates, WHILE held-out
comprehension RISES, because validated retrievals get consolidated into a fast internal library instead
of re-queried live every time. That specific curve has never been measured, at any scale, in this arc.

KB-CHECK DONE FIRST: read notes/research_narrative_benchmark_scout_2026-08-09.md (7-candidate MCQA
scout; ROCStories/StoryCloze AVOID, bAbI AVOID, MCScript2.0 was the pick THEN, now superseded) and
notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_2026-08-10.md (WIQA/TORQUE/MCTACO scored;
WIQA ranked #1 for the causal-VALIDATE-loop, but per this drill's own dispatch instruction WIQA is now
ruled OUT for the crutch-fade demonstration specifically because its ProPara-adjacent procedural/
scientific domain has no vetted everyday commonsense KB coverage -- CSKG's causal edges are ATOMIC/
ConceptNet-style everyday-event edges, not process-science facts, so the crutch would have nothing real
to pull in). Checked data/orchestrator_status_log.jsonl (last 5 research_delivery entries, reproduced
above under Trigger) -- confirms no prior drill scored GLUCOSE, Social IQa, TellMeWhy, or COPA/BCOPA
anywhere in this arc; this is new ground, not a rediscovery. research_field_advisor.py was run --
its 22-field coverage map is substrate-physics-oriented (thermodynamics/spin-glass/free-probability/
etc.), not benchmark selection, so it does not rank this drill's candidates; noted, not force-fit
(same disposition as the WIQA scoping note used for the same tool).

**CORRECTION caught mid-drill, disclosed rather than silently fixed:** the initial KB-check pass above
missed three SAME-DAY sibling drills, surfaced only via a second pass through
notes/research_decisions_2026-08-10.md (they postdate the two scout notes above and were not yet
cross-referenced by them): notes/research_crutch_design_and_generalization_2026-08-10.md (DRILL 1 --
crutch=CSKG spine, already landed; output-form schema already designed; fade-curve shape sharpened to
Pinker dual-mechanism regular/irregular frequency-inversion), notes/research_brain_scaffolding_that_
fades_2026-08-10.md (DRILL 2 -- brain-fidelity SHAPE+POSITION+METRIC audit of FLAG/CONSOLIDATE/FADE;
HEADLINE finding: the FADE is structurally IMPOSSIBLE today, not merely unbuilt -- BANK writes into a
plain in-memory dict, never into a natively-read distributed structure), and notes/research_crutch_
fade_loop_owned_organ_wiring_2026-08-10.md (DRILL 3 -- owned-organ wiring audit; every loop piece
already exists on disk, mostly self-test-verified; two small connectors are the actual gap, one of
which is exactly DRILL 2's BANK-target fix). These three drills own the INTERNAL mechanism question
(does a fade mechanism exist, is it wired, what does the brain say its shape should be) end-to-end;
none of them picked a BENCHMARK or designed an external, real-world validation test -- that is this
drill's (DRILL 4's) distinct job, and the two efforts compose rather than overlap (Cross-thread
synthesis, below, makes the seam explicit). This note's ORIGINAL first-draft Section 2a proposed a
generic new "memoization cache" as the missing piece; that was written before this correction and has
been revised in place to point at the ALREADY-DIAGNOSED, more precise fix DRILL 2/3 converged on
(hd_fact_store.py trust-promotion) instead of re-inventing a placeholder mechanism.

Extends, does not re-derive: the AVOID verdicts on ROCStories/Story Cloze (Yao et al. 2022 dissociation:
93% Cloze accuracy collapses to 37-46% on reasoning-type identification; Sharma 2018's own debiased set
still leaks 64.4% context-blind) and bAbI (Kaushik & Lipton 2018: passage-only baseline = 100%) are
carried forward unchanged from the 2026-08-09 scout note. Story Commonsense's SECONDARY ranking is
carried forward and refined with new baseline-table numbers found this cycle (below).

---

## HEADLINE

**Primary pick: Social IQa (SIQA; Sap, Rashkin, Chaturvedi, Bras, Choi 2019, EMNLP-IJCNLP D19-1454,
arXiv:1904.09728).** It is the strongest candidate found for the crutch-fade test specifically (not
generically "a good benchmark") because of one fact none of the other candidates share: **SIQA's
questions and multiple-choice distractors were constructed BY SAMPLING FROM ATOMIC** (Sap et al.'s own
construction pipeline: context+question drawn from ATOMIC if-then tuples, wrong answers drawn as
plausible-but-mismatched ATOMIC inferences for a different event/relation). CSKG -- the store already
sitting behind the crutch (exp_cskg_foundation_v1, 482,588 nodes / 1,238,686 causal-inferential edges,
HARD_PASS-certified, ATOMIC-dominated) -- is therefore not merely "adjacent" to SIQA's domain, it is
close to a DIRECT ANCESTOR of it. This is the everyday-narrative-with-real-KB-coverage property the
dispatch instruction asked for, satisfied about as cleanly as it can be satisfied by an existing public
benchmark. It cuts the opposite direction from WIQA/ProPara (no coverage) -- here coverage is close to
guaranteed, which is exactly what is needed to test the FADE dynamic cleanly (see the honest circularity
risk in Section 4 -- guaranteed coverage is a double-edged property and is NOT free).

Public, downloadable now: `allenai/social_i_qa` on Hugging Face (CC-BY-4.0, no login gate found this
session), train 33,410 / dev 1,954 QA tuples (exact figures confirmed directly from the paper's Table 1
via a full-text fetch this cycle, not a secondary summary). **No test-split labels exist** (HF dataset
card lists only train+validation configs) -- same shape as WIQA's hidden test; DEV is the correct
held-out split, same precedent WIQA already established.

**Honest content-ceiling number: NOT AVAILABLE from the literature.** The original paper's baseline
table (confirmed via full-text fetch, not summary) reports Random=33.3%, GPT=63.0-63.3%, BERT-base=
63.1-63.3%, BERT-large=64.5-66.0%, Human=84.4-86.9% (dev/test as applicable) -- **no word-overlap, TF-IDF,
PMI, or any non-neural lexical baseline is reported anywhere in the paper.** This is the identical honest
gap the WIQA note flagged for WIQA -- the field simply does not publish this number for either dataset --
and it must be measured on our own harness before any HARD-PASS claim, exactly the same Stage-0
discipline already established. Circumstantial case for a real ceiling: Random-to-Human gap is 51-54
points and BERT-large-to-Human is 18-22 points, both large; SIQA answers are freely-generated plausible
continuations (not text spans), so naive lexical overlap with the context has less to grab onto than in
a span-extraction task -- but this is a plausibility read, not a verified number, flagged as such.

**Secondary / validation companion (carried forward from the 2026-08-09 scout, refined): Story
Commonsense** (Rashkin et al., ACL 2018, P18-1213). New baseline-table numbers found this cycle sharpen
the prior note's caveat rather than reversing it: TF-IDF-baseline F1 (Maslow 32.00, Reiss 22.48, Plutchik
23.91) is already close to the paper's best 2018 neural baseline (Maslow 35.23, Reiss 24.51, Plutchik
30.15) -- gaps of only +3.2 / +2.0 / +6.2 F1 points. This is a THIN content-ceiling margin compared to
SIQA's 18-54-point gaps, confirming (with a harder number than the prior note had) that Story Commonsense
is a weaker standalone content-ceiling story and belongs in the SECONDARY/validation role, concentrated
on its harder Reiss/rare-category cells, not as the primary fade-curve target.

**Rejected candidates, with reasons (per "don't dismiss adjacent methods" -- all were scored, not waved
off):**
- **GLUCOSE** (Mostafazadeh et al., EMNLP 2020 Best-Paper-nominated, 2020.emnlp-main.370): excellent
  CONTENT -- 440K story-grounded causal statement+general-rule pairs across 10 causal-explanation
  dimensions, explicitly grounded in ROCStories -- but its native task is crowdsourced free-text
  GENERATION (elicit a causal statement + generalized rule), evaluated by ROUGE/semantic-similarity/
  human eval, not classification. No discriminative/multiple-choice reformulation was found this
  session (searched directly; came up empty; flagged as UNVERIFIED-ABSENT, not confirmed-absent). This
  disqualifies it as an EVAL target under the hard glass-box/no-free-form-generation constraint, the
  same reason NarrativeQA was rejected in the 2026-08-09 scout. **Recommended role: CONTENT DONOR, not
  benchmark** -- GLUCOSE was already independently named as a candidate CAUSAL content source in the
  2026-08-09 Content drill (alongside ATOMIC/ASER/ConceptNet-Causes) for growing the CSKG-adjacent
  store; this drill's finding is consistent with, not a departure from, that earlier recommendation.
- **TellMeWhy** (Lal, Chambers, Mooney, Balasubramanian, ACL Findings 2021, 2021.findings-acl.53): >30K
  why-questions over ROCStories, with a built-in EXPLICIT/IMPLICIT-answer label (>=2/3 annotators mark
  whether the answer is available in the text) -- structurally this is almost exactly the kind of
  free, dataset-native ablation label that made MCScript2.0's script/text split valuable, and the
  IMPLICIT subset is close to a direct proxy for "this item needs the crutch." But the task format is
  free-form generative answers, evaluated by a human/Likert rubric, not classification -- searched
  directly this cycle for a multiple-choice reformulation, found none. Same disqualification as GLUCOSE.
  Worth carrying forward as INSPIRATION (not data): its implicit/explicit label is the closest published
  precedent for the exact telemetry this drill's fade-test needs to build itself (per-item "did this
  require external knowledge" tag) -- see Section 2.
- **COPA / Balanced COPA** (Roemmele et al. 2011; Kavumba et al. 2019, arXiv:1911.00225): confirmed this
  cycle -- RoBERTa-large = 87.7% on original COPA (vs. BERT-large 76.5%), human ~100% on COPA / 97.0% on
  Balanced COPA. Real headroom is thin (~10-12 points at best, likely less once cue-robustness is priced
  in) and the dataset is TINY (1,000 items total, 500 test) -- both a statistical-power problem for a
  multi-checkpoint fade curve and a near-saturation problem for isolating a content-vs-inference gap.
  COPA premises are also isolated one-line events with no connected narrative to serve as an EXPOSURE
  corpus (unlike SIQA/Story Commonsense/ROCStories, which have thousands of situational texts to walk
  the acquisition loop through). Reject as primary or secondary; not recommended even as a cheap smoke
  precursor given the near-saturation (contrast with QuaRTz's role as a WIQA smoke-precursor in the prior
  note, where headroom was still large).
- **ROCStories / Story Cloze**: AVOID, unchanged from the 2026-08-09 scout (Yao et al. 2022 dissociation
  study is decisive: 93% Cloze accuracy, 37-46% causal-reasoning-type identification). Raw ROCStories TEXT
  (not the Cloze QA labels) remains usable as unlabeled exposure material only, and is in fact the shared
  substrate underlying SIQA-adjacent, Story-Commonsense, GLUCOSE, and TellMeWhy alike -- see Section 2.
- **bAbI**: AVOID, unchanged (Kaushik & Lipton 2018: passage-only baseline = 100%).

P_deflated for "Social IQa (+ Story Commonsense secondary) is the correct benchmark pick for the
crutch-fade demonstration" (benchmark-fit/selection judgment, lower-risk class than a mechanism claim,
same calibration tier as the WIQA ranking's 0.60): **0.55** -- deflated 0.05 below the WIQA-pick
precedent specifically because of the unresolved KB-circularity risk named in Section 4 (SIQA's
ATOMIC ancestry cuts both ways: it all-but-guarantees the crutch has real signal to fire on, but it
also means a "the crutch found the right answer" result could partly reflect near-verbatim KB overlap
between eval item and store rather than genuine incremental grounding -- Section 4 names the required
audit, it is not yet run).

P_deflated for "the fade-test itself HARD-PASSes" (the actual mechanism claim -- crutch-firing-rate
drops, comprehension rises, scramble collapses, consolidation is not lossy): **0.25** -- capped at
0.50 per novel-synthesis discipline and deflated further (toward the aggressive end of the mandated
0.15-0.25 band) for four concrete, named reasons, the first sharper than a first-pass estimate would
give it because of the DRILL 2/3 reconciliation (above): (1) **CONFIRMED, not merely suspected, that
the fade path is structurally broken today** -- DRILL 2's disk-read (not assumption) found BANK writes
into a plain in-memory dict with no path into any natively-read structure, so this test's
LIBRARY_RESOLVED telemetry category would read as permanently near-zero (no fade possible) UNTIL
DRILL 3's connector #4 (bank into `hd_fact_store` with trust-promotion) is actually wired -- a real,
named PRECONDITION this drill's own Stage-0 does not by itself satisfy (see the revised Cheap decisive
test, below); partially offsetting: the fix is no longer a vague gap, it has a concrete, small,
already-scoped target, a genuine (if modest) confidence increase over a first-pass "somewhere in the
loop, TBD" read; (2) the crutch-FADE dynamic, even once wired, has never been TESTED at any scale in
this arc -- Stage-2A validated the retrieve-VALIDATE-advance LOOP, not a fade-over-exposure curve,
these are different claims, and DRILL 2's own Test A (mechanism-internal, synthetic-corpus) is itself
unresolved as of this session; (3) this arc's one prior acquisition-loop growth result (2026-08-09, #4,
exp_grounding_acquisition_loop_v1) was a HOLLOW HARD_PASS -- the loop genuinely grew a library and
never mis-grounded anything (the safety guard is real and proven), but what it grew was dominated by
high-frequency function/light words, not content that helped comprehension -- a direct precedent for
the specific failure mode "the loop grows something, but not something that matters," which this
test's own bands are written to detect (the consolidation-fidelity criterion, Section 3, band 4) and
which DRILL 2's HEADLINE independently confirms has a structural, not just content-selection, cause;
(4) the store this fade-test's LIBRARY connects to (once wired) sits alongside the separate CSKG-field
KGStore Hebbian single-W substrate that Stage-2 sub-test B HARD_FAILED with a hard capacity cliff at
~30K items (relevant_recall collapses to 0.000 by 30K) -- an unresolved, in-flight scale wall
(resonator rescue testing now, af9073fbc); this drill's LIBRARY target (`hd_fact_store`) is a
DIFFERENT store than the collapsing one, so the two walls are not automatically the same risk, but
that has not been independently confirmed and is named as an open item, not assumed safe (Section
2b/4).

---

## 1. Ranked benchmark pick, with numbers

| Rank | Benchmark | Role | Content ceiling | Data availability |
|---|---|---|---|---|
| 1 | **Social IQa** (Sap et al., EMNLP-IJCNLP 2019) | PRIMARY (fade-curve eval target) | UNMEASURED (no published lexical baseline; Random=33.3%, BERT-large=64.5-66.0%, Human=84.4-86.9%, gap 51-54pp random-to-human, 18-22pp neural-to-human) | Public, `allenai/social_i_qa` HF, CC-BY-4.0, train 33,410 / dev 1,954 (test hidden, use dev) |
| 2 | **Story Commonsense** (Rashkin et al., ACL 2018) | SECONDARY (validation companion, Reiss/rare-category slice) | THIN (TF-IDF F1 already 32.00/22.48/23.91 vs best-2018-neural 35.23/24.51/30.15 -- gaps +3.2/+2.0/+6.2 only) | Public (uwnlp/storycommonsense), built over ROCStories |
| -- | GLUCOSE | CONTENT DONOR only (not an eval benchmark) | N/A -- generative task, ROUGE/human-eval scored, disqualified by glass-box constraint | Public; 440K causal statement+rule pairs over ROCStories |
| -- | TellMeWhy | INSPIRATION only (its implicit/explicit label is the model for this test's own telemetry) | N/A -- generative task, disqualified | Public (StonyBrookNLP/tellmewhy), >30K why-Qs over ROCStories |
| REJECT | COPA / Balanced COPA | -- | Thin (RoBERTa 87.7% vs human ~100/97%), tiny (1,000 items), no exposure corpus | Public, but not fit for purpose here |
| AVOID | ROCStories / Story Cloze | raw text OK as unlabeled exposure only | Decisively dissociated from genuine reasoning (Yao et al. 2022) | Public |
| AVOID | bAbI | -- | Artifact-broken (Kaushik & Lipton 2018) | Public |

---

## 2. The fade-test design (the load-bearing part)

### 2a. What "crutch" and "fade" mean operationally, made precise

- **CRUTCH** = the live external-store pull-in step: `cleanup_family.iterative_attractor` /
  `kg_traversal.KGStore` querying the CSKG-ATOMIC causal store (+ BEAGLE associative store, per the
  2026-08-09 Content drill) at INFERENCE time, invoked only when a comprehension gap is flagged (BoW /
  passage-own-words resolution is low-confidence or absent) -- this is the already-validated
  retrieve-VALIDATE-advance loop (Stage-2A, HARD_PASS 5/5), reused unmodified as the crutch's retrieval
  engine.
- **LIBRARY** = NOT a new mechanism to invent -- per DRILL 2/DRILL 3 (both filed the same day, read in
  full during this drill's reconciliation pass), the destination already has a name and a diagnosis.
  DRILL 2 (brain-fidelity audit) found the FADE is structurally IMPOSSIBLE in the current code because
  `register_acquired_outcome` writes validated acquisitions into `verb_lexical_similarity`'s
  `ACQUIRED_OUTCOME_VERB_FEATURES`, a plain in-memory Python dict consulted by an explicit lookup call
  -- a permanent side-table, not a structure that can ever be folded into the "native," lookup-free
  pathway used for already-known words. DRILL 3 (owned-organ wiring audit), filed independently the
  same day, converges on the identical target and names the concrete fix as its "connector #4": persist
  a `GROUNDED_*` item into `hdlab/hd_fact_store.py` (source-trust-vetted fact store, CERT/chain-grade,
  provenance+trust natively bound INTO the fact vector, not side metadata) instead of the flat dict --
  "a crutch-assisted grounding can be tagged TRUST_MID/LOW at write time and a later independently-
  reconfirmed one promoted, giving the loop a SECOND place fade is visible: trust-weighted store
  confidence, not just vote dilution." This drill's LIBRARY (Section 2b/2d, the thing that makes
  `LIBRARY_RESOLVED` a real telemetry category rather than an always-empty one) IS that connector,
  scoped for the fade-test's purposes as: bank VALIDATED crutch retrievals (Stage-2A's VALIDATE step
  accepting a retrieval) into `hd_fact_store` at low/mid trust, promote trust as independent corroborating
  exposure accumulates, and prefer a sufficiently-trusted `hd_fact_store` hit over a fresh live CSKG
  query at resolution time. This is DRILL 3's connector #4, reused unmodified for this test's purposes,
  not a competing new design. Distinguish explicitly from the OLD verb-lemma `grounding_acquisition_
  loop.py` BANK path (2026-08-09, #4, HOLLOW HARD_PASS, superseded, and per DRILL 2 also the flat-dict
  side-table) -- wiring connector #4 is precisely what turns that hollow, non-fading write path into a
  genuinely fade-capable one.
- **FADE** = crutch_fire_rate(checkpoint) trending down across exposure checkpoints as the library fills,
  while comprehension(checkpoint) does not fall (target: rises).

### 2b. Exposure corpus and checkpoints

Use SIQA's own TRAIN split (33,410 QA tuples) as the exposure source, STRIPPED of its QA/answer labels
-- process only the situational CONTEXT text through the loop (same "texts not labels" discipline the
MCScript2.0 scout note used for its 2,500-text exposure corpus). Exact count of UNIQUE contexts within
the 33,410 tuples is UNVERIFIED this session (multiple questions share one context by construction) --
this is a Stage-0 item, cheap to resolve by a direct field-count on the downloaded file. Checkpoint at
0% / 10% / 25% / 50% / 100% of unique exposure contexts, evaluating FULL dev (1,954, frozen, never
exposed) at every checkpoint -- same protocol shape as MCScript2.0's compounding-property checkpoints.

**Scale guard (load-bearing, ties to the open Stage-2 store wall):** cap the library's entry count well
under the ~30K item threshold where Stage-2 sub-test B measured the Hebbian single-W KGStore's recall
collapsing to 0.000 -- SIQA's unique-context count is expected to be well under that ceiling (a low-
thousands estimate, unconfirmed), but this must be VERIFIED, not assumed, before the checkpoint sweep
runs, specifically so that a null/negative fade-test result is attributable to the fade mechanism itself
and not to a silent re-encounter of the already-known, separately-tracked store-capacity cliff. If the
library implementation reuses the same single-W KGStore substrate, either (a) confirm the resonator
rescue (af9073fbc) has landed and use it, or (b) use a capacity-safe alternative (a plain dict/hash
keyed by cue text with cosine-similarity lookup, no Hebbian binding at all, since the LIBRARY here is a
cache, not a distributed associative store -- it does not need the same crosstalk-prone architecture the
CSKG field itself uses) -- (b) is the cheaper, lower-risk choice and is recommended unless there is a
specific reason the library needs distributed/associative properties the crutch's own field-level store
already provides.

### 2c. Arms

1. **BoW baseline** (real, measured fresh on our own harness -- Stage-0, see Section "Cheap decisive
   test"): lexical-overlap / TF-IDF between context+question and each of the 3 candidates, no crutch, no
   library. The content-matching floor this whole thesis must beat.
2. **ALWAYS-CRUTCH-AT-INFERENCE** (diagnostic ceiling; explicitly NOT the target end-state; charter-
   violating per the dispatch instruction because it is the opposite of brain-faithful -- the brain does
   not keep performing effortful conscious retrieval forever on well-learned material; ACT-R declarative-
   to-procedural compilation and ordinary skill-automatization are the standard account, and this arc's
   own framing is explicitly that comprehension should compound via internalization, not stay
   externally-scaffolded forever). Forces a live crutch query on every item at every checkpoint,
   regardless of whether BoW/library could already resolve it. Gives the practical upper bound of "what
   if the crutch never faded" -- useful as a reference curve, not a deployment target. Compute-costly
   (every item queries the field); run at a subsample if full-scale is too slow.
3. **NEVER-CRUTCH** (floor/ablation): pull-in permanently disabled. Only BoW + whatever the library
   accumulates WITHOUT ever being seeded by a crutch retrieval (isolates whether the library can
   bootstrap any content on its own -- it should not be able to, by construction; if it does, that is a
   confound to catch, e.g. a leak from BoW into the library-write path).
4. **GAP-DRIVEN FADING CRUTCH** (the system under test): BoW/library-first; crutch fires only on a
   flagged gap (BoW confidence below threshold AND library has no sufficiently-similar cached cue);
   validated crutch retrievals get banked into the library at each checkpoint; subsequent similar gaps
   resolve from the library, not a fresh live query.
5. **SCRAMBLE-CRUTCH** (control, same firing SCHEDULE as arm 4, wrong CONTENT): every time arm 4 would
   fire the crutch, this arm instead retrieves a random OTHER CSKG neighbor unrelated to the actual cue
   (or permutes which candidate answer the retrieved content is attached to). Must fail to beat BoW at
   every checkpoint -- if it does not fail, the mechanism is not using real content, it is exploiting
   some structural artifact of "something got retrieved," which the scramble discipline exists to catch
   (same pairscramble-must-collapse logic used throughout this arc, e.g. Stage-1/1.5/2A, MCScript2.0's
   Stage-3 guard).

### 2d. Per-item telemetry (what makes the curve measurable, not just a final number)

Every held-out item, at every checkpoint, gets tagged with which path answered it: `BOW_RESOLVED`,
`LIBRARY_RESOLVED` (cache hit, no live query), `CRUTCH_RESOLVED` (live query fired), or `ABSTAINED`
(no path found, fall back to majority/BoW per the augment-not-replace no-regression discipline already
validated in the E4 design). `crutch_fire_rate(checkpoint)` = count(CRUTCH_RESOLVED) / total.
`library_resolved_rate(checkpoint)` = count(LIBRARY_RESOLVED) / total. This 4-way tag is the direct
generalization of TellMeWhy's implicit/explicit label and MCScript2.0's script/text label into a
telemetry signal this test builds itself, since no published benchmark carries a native "needs external
knowledge" tag matched to our own store.

---

## 3. Pre-registered CAN-FAIL bands

**HARD-PASS (all four required):**
1. `crutch_fire_rate` drops from checkpoint 0% to checkpoint 100% by >= 30% relative (e.g. 0.40 -> <=
   0.28) or >= 10 percentage points absolute, whichever is reached first, with a monotonic-or-noise-band
   trend across the intermediate checkpoints (no more than one checkpoint-to-checkpoint uptick > 3pp).
   **Shape refinement (per DRILL 2's brain-fidelity fade literature, Newell & Rosenbloom power-law-of-
   practice / Logan instance theory -- read in full during this drill's reconciliation pass, not
   re-derived here): the brain-faithful null hypothesis is STEEP-THEN-TAIL, not linear -- most of the
   drop should occur in the earlier checkpoints (0%->25%) with visibly diminishing further drop by
   50%->100%. A roughly LINEAR checkpoint-to-checkpoint drop is a MIDDLE_BAND-grade partial match (the
   aggregate direction is right, the brain-predicted shape is not) even if the aggregate >=30%/10pp
   threshold clears -- report the per-checkpoint delta explicitly, not just the endpoint delta, so this
   distinction is checkable.
2. Held-out comprehension (arm 4) at the 100% checkpoint beats the BoW baseline (arm 1) by >= +0.05
   absolute, AND never falls below BoW-baseline minus 0.02 at any checkpoint (no-regression guarantee,
   same discipline as E4's abstain-gate).
3. SCRAMBLE-CRUTCH (arm 5) stays within +/- 0.02 of the BoW baseline at every checkpoint -- i.e. never
   meaningfully beats BoW -- proving the real crutch's specific content, not the act of retrieval itself,
   does the work.
4. **Consolidation-fidelity (the check that distinguishes genuine fade from a broken gate):**
   accuracy on LIBRARY_RESOLVED items >= accuracy on CRUTCH_RESOLVED items minus 0.03, at every
   checkpoint where both categories have >= 20 items. This directly guards against the #4-acquisition-
   loop failure mode (HOLLOW HARD_PASS, 2026-08-09) recurring here in a new form -- a fade that happens
   because the gate quietly stopped trying (and got worse) rather than because it genuinely learned.

**HARD-FAIL (any one triggers):**
- `crutch_fire_rate` flat across all checkpoints (no drop beyond a +/-3pp noise band), OR
- comprehension flat/no rise over BoW baseline by the 100% checkpoint, OR
- SCRAMBLE-CRUTCH ties or beats the real GAP-DRIVEN arm at any checkpoint, OR
- LIBRARY_RESOLVED accuracy collapses relative to CRUTCH_RESOLVED accuracy (consolidation is lossy --
  the fade is fake, driven by a broken/over-eager gate rather than genuine internalization).

**MIDDLE_BAND (partial, pre-committed exit, same designed-exit pattern as E4/WIQA):**
- `crutch_fire_rate` drops but comprehension does not rise (efficiency-only gain, no accuracy payoff) --
  narrow the claim to "compute-cheaper, not yet better," or
- comprehension rises but `crutch_fire_rate` stays flat (the crutch got MORE accurate over exposure, not
  LESS necessary -- a real but different finding: the retrieval mechanism itself improved, not that
  reliance on it faded) -- narrow the claim accordingly and do not claim internalization/fade occurred.

---

## 4. Honest assessment: is a clean benchmark actually available?

**No candidate found this session cleanly isolates world-knowledge-inference from all possible content-
matching or KB-circularity confounds simultaneously; Social IQa is the least-bad available pick, not a
clean one, and it should be adopted with two explicit, disclosed caveats:**

1. **No published content-ceiling number exists for SIQA** (same gap WIQA had) -- the BoW baseline must
   be measured fresh (Stage-0 below) before any HARD-PASS claim about arm 1 vs arm 4 is trusted. This is
   a same-day, cheap, well-precedented step (identical to what the WIQA note already committed to).
2. **KB-circularity risk is real and specific to this pick, not generic:** SIQA was constructed by
   sampling FROM ATOMIC, and CSKG's causal-edge component is ATOMIC-dominated -- meaning some fraction of
   SIQA dev items may have a near-verbatim CSKG edge that essentially hands the crutch the answer, which
   would inflate "the crutch helps" without proving genuine incremental grounding beyond what the KB
   already encoded verbatim. The mandatory SCRAMBLE-CRUTCH control (arm 5, Section 2c) catches the
   weaker version of this risk (is content-SPECIFICITY load-bearing, or does any retrieval help) but does
   NOT by itself catch direct eval-set memorization via the KB. A dedicated **leakage audit** (sample
   ~100 dev items, check what fraction have a CSKG edge whose endpoints near-exactly match the item's
   context+correct-answer) should be run alongside Stage-0 and reported honestly in whatever cell
   ultimately runs this test -- if leakage is high, the fade-curve result should be reported on the
   leakage-excluded subset as the primary number, with the full-dev number reported as an upper bound,
   not the headline.

If this two-caveat package is judged too weak for a headline claim, the recommended fallback is NOT a
different single benchmark (nothing else scored this cycle is cleaner on both the everyday-domain and
the glass-box-format axes simultaneously) but a **combined report**: SIQA as primary fade-curve target
(caveated per above) + Story Commonsense as an independent secondary check on the harder Reiss/rare-
category cells (where its own thinner content-ceiling at least means a lift there is less likely to be
pure lexical artifact, per the 2026-08-09 note's own risk flag) -- convergent evidence across two
differently-flawed benchmarks is more defensible than either alone, the same logic this arc has used
before (e.g. the 9-cell convergent extraction-wall finding in the 2026-08-10 islanded-organs audit).

---

## Cheap decisive test

**Sequencing note added on reconciliation:** DRILL 3 named two connectors (wire the crutch into the
GUARDED consolidator; bank validated output into `hd_fact_store` instead of the flat dict) and DRILL 2
pre-registered its own "Test A" (mechanism-internal, reuses an EXISTING synthetic acquisition run,
correlates native-coverage against trace-count/vote-margin, no new corpus, no GPU) as cheaper,
faster-turnaround PRECONDITION checks than this drill's benchmark-level Stage-0. Recommended order for
the Director: DRILL 3's connector #4 (wire BANK to `hd_fact_store`) and DRILL 2's Test A should run
FIRST or IN PARALLEL with this drill's Stage-0 below, not after it -- if Test A HARD-FAILs (the
substrate's own codebook geometry does not organize acquired-item neighborhoods the way a
native-coverage fade signal needs), that is cheaper information than discovering the same underlying
problem after a multi-day SIQA checkpoint-sweep build. This drill's Stage-0 and DRILL 2/3's precondition
checks are independent and can run concurrently; only the FULL checkpoint-sweep build (Section 2) should
wait on all three clearing.

Before any acquisition-loop-over-exposure-checkpoints build commitment (the full Section 2 design is a
multi-day build): **Stage-0, same day, no GPU, ~2-3 hours total:**
(a) pull `allenai/social_i_qa` (HF `datasets`), confirm train=33,410 / dev=1,954 matches this drill's
    figures, count UNIQUE contexts in train (resolves the open exposure-corpus-size question, Section
    2b);
(b) compute the BoW/TF-IDF baseline on dev fresh (closes the "no published content ceiling" gap,
    Section 1/4);
(c) leakage audit: sample ~100 dev items, check CSKG-ATOMIC edge overlap rate against context+correct-
    answer (Section 4);
(d) confirm the library's target substrate stays under the ~30K Stage-2 capacity-cliff item count, or
    that a dict/cosine-lookup cache (not the Hebbian single-W KGStore) is used for the library
    specifically (Section 2b scale guard) -- and confirm DRILL 3's connector #4 (`hd_fact_store`
    trust-promotion bank path) is actually wired, per the sequencing note above, since without it
    LIBRARY_RESOLVED will read as structurally near-zero regardless of exposure.
If (a)-(d) all clear, proceed to the full checkpoint-sweep build (Section 2); if the BoW baseline in (b)
comes back unexpectedly high (e.g. > 55%, eating most of the Random-to-Human gap), or leakage in (c) is
high (> 30% of sampled items), STOP and re-score before committing further build effort -- exactly the
same design-gate discipline (real baseline, can-fail, one variable) already standing for this arc.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

See Section 3 in full; summarized: **HARD-PASS** requires all four of (1) firing-rate drop >=30%
relative/10pp absolute with a steep-then-tail (not linear) per-checkpoint shape, (2) comprehension beats
BoW by >=+0.05 with no regression, (3) scramble stays within +/-0.02 of BoW at every checkpoint, (4)
library-resolved accuracy within -0.03 of crutch-resolved accuracy. **HARD-FAIL** on any of: flat
firing-rate, flat/no comprehension lift, scramble ties/beats the real arm, or library-resolved accuracy
collapse. **MIDDLE_BAND**: efficiency-only, accuracy-only, or shape-only partial results, narrowed per
Section 3. P_deflated for HARD-PASS = **0.25** (see Headline for the four named deflators: the now-
CONFIRMED-broken fade path pending DRILL 3's connector #4, the untested fade mechanism even once wired,
the #4 hollow-acquisition-loop precedent, and the open Stage-2 store-capacity-cliff adjacency risk).

## Cross-thread synthesis

- **Composes with, does not overlap, the three same-day sibling drills** (surfaced only on a second
  KB-check pass, disclosed under Trigger above): notes/research_crutch_design_and_generalization_
  2026-08-10.md (DRILL 1 -- the crutch is already-landed CSKG data with a designed output-form schema;
  the fade curve should follow Pinker's dual-mechanism regular/irregular frequency-inversion shape),
  notes/research_brain_scaffolding_that_fades_2026-08-10.md (DRILL 2 -- brain-fidelity confirms the
  fade is structurally impossible today, names the exact broken pathway, and pre-registers its own
  mechanism-internal Test A), and notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md
  (DRILL 3 -- confirms it is a wiring job, names two small connectors, one of which -- connector #4,
  bank to `hd_fact_store` -- this drill's LIBRARY definition (Section 2a) now points at directly
  instead of proposing a new mechanism). Those three drills answer "does a fade mechanism exist inside
  the substrate, and what should its shape be" using internal code audits and synthetic/toy self-tests;
  this drill (DRILL 4) answers "which external, real, public benchmark proves the mechanism produces
  genuine comprehension gains, not just internal plumbing correctness" -- the two questions are
  different and this drill's SIQA fade-curve design is the natural external capstone once DRILL 3's
  connectors are wired and DRILL 2's Test A has cleared (see the resequenced Cheap decisive test,
  above). None of DRILL 1/2/3 picked a benchmark or scored SIQA/GLUCOSE/Story-Commonsense/COPA/TellMeWhy
  against each other -- that ranking (Section 1) is this drill's own, undupliated contribution.
- Directly extends notes/research_narrative_benchmark_scout_2026-08-09.md and
  notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_2026-08-10.md -- carries forward their
  AVOID verdicts (ROCStories/Story Cloze, bAbI) unchanged, refines Story Commonsense's SECONDARY role
  with new baseline numbers, and explicitly supersedes WIQA as *this specific test's* target (WIQA
  remains a valid pick for the separate causal-VALIDATE-loop demonstration the earlier note designed;
  it is simply the wrong domain for a world-knowledge-coverage-dependent crutch-fade test).
- Directly ties into the open Stage-2 store-capacity-cliff wall (notes/director_POST_COMPACTION_BACKUP_
  2026-08-04.md, "STAGE-2 SPLIT RESULT" entry, commit 013f1481e) -- Section 2b's scale guard is written
  specifically so this test's own result cannot be silently confounded with that separate, still-open
  wall; this is a new, explicit dependency the Director should track alongside the resonator rescue
  (af9073fbc).
- **Correction absorbed mid-drill (see Trigger and Section 2a):** this bullet originally claimed the
  LIBRARY connector was a build item "not previously scoped anywhere in this arc." That was written
  before the second KB-check pass surfaced DRILL 3, which had already scoped it (as connector #4,
  bank into `hd_fact_store`) the same day. The corrected framing: this drill did not discover a new
  gap, it independently arrived at needing the SAME connector DRILL 3 already named, from the opposite
  direction (this drill asked "what would make LIBRARY_RESOLVED telemetry real" and landed on the exact
  connector DRILL 2/3 diagnosed from "why can't BANK output ever become native"). What this drill adds
  on top is the reason connector #4 matters for EXTERNAL validation specifically: without it, there is
  nothing for real-benchmark exposure to cause a fade IN -- the loop as it exists today would fire the
  crutch identically at checkpoint 0% and 100% on SIQA, since it has no memory of prior validated
  retrievals, which is exactly why this drill's own Stage-0 (Cheap decisive test) now lists confirming
  connector #4 is wired as an explicit precondition rather than an assumption.
- Consistent with, and does not reopen, the 2026-08-09 MCScript2.0 verdict (script-structure dead end,
  content-matching caps ~0.61) or the 2026-08-10 islanded-organs audit (9+ independent real-text cells
  all show the same self-extraction wall) -- this drill's SIQA pick sidesteps the extraction-wall risk
  somewhat because SIQA's context sentences are short and pre-segmented (closer to the MCTACO/WIQA
  shape than to MCScript2.0's long free narrative passages), which should reduce (not eliminate) the
  extraction-failure mode that capped every real-narrative attempt so far -- worth flagging as a
  possible SECOND reason SIQA is a better-conditioned pick than a longer-narrative alternative would be,
  though this is a plausibility read, not a measured fact this cycle.

## Substrate-product implications

If the fade-test HARD-PASSes, the product claim is the sharpest one this arc has produced: not just "a
glass-box system beats a baseline" (MCScript2.0, WIQA's target claim) but "a glass-box system needs
external reference LESS over time on the same class of question, while getting the question right MORE
-- an auditable, measurable analog of learning-by-reading, with a trace showing exactly which answers
came from consolidated internal knowledge versus a live lookup at every single point in the curve." That
trace (the per-item BOW/LIBRARY/CRUTCH/ABSTAIN tag, Section 2d) is itself the differentiator no opaque
neural system can produce, regardless of accuracy. If it MIDDLE_BANDs or HARD_FAILs, the per-item
telemetry (Section 2d) plus the consolidation-fidelity check (Section 3, band 4) are built specifically
to diagnose WHICH of the three named risk factors (mechanism genuinely untested / hollow-acquisition-
loop-style false consolidation / store-capacity-cliff interaction) is responsible, rather than returning
an undiagnosed flat result -- per the standing "flat learning result means broken experiment, not a
ceiling" discipline. Recommended next action for the Director: dispatch Stage-0 (Section "Cheap decisive
test") as a same-day, cheap, no-GPU precondition check before committing to the full multi-day
checkpoint-sweep build; the LIBRARY cache layer (a small, well-scoped addition to already-proven
machinery) is the one new component that needs authoring, separate from and simpler than the still-
unresolved store-capacity rescue in flight.

## Citations (verified count)

Six generic-term web searches + three full-text fetches this cycle (public dataset/paper names used
directly, consistent with this arc's established query-privacy precedent that public benchmark
identifiers are not substrate-novel terms): (1) **Social IQa** -- Sap, Rashkin, Chaturvedi, Le Bras, Choi,
EMNLP-IJCNLP 2019, ACL Anthology D19-1454 / arXiv:1904.09728; train/dev/test split (33,410/1,954, no
labeled test) and full baseline table (Random 33.3%, GPT 63.0-63.3%, BERT-base 63.1-63.3%, BERT-large
64.5-66.0%, Human 84.4-86.9%) verified via a direct full-text fetch of the ar5iv HTML rendering (Table 1
and Table 2), which explicitly confirmed NO word-overlap/PMI/lexical baseline is reported anywhere in
the paper -- higher-confidence than a secondary-summary read, since the full table was read directly.
HF dataset-card facts (CC-BY-4.0 license, train=33,410/validation=1,954, no test config) verified via a
direct fetch of the `allenai/social_i_qa` HF page. (2) **GLUCOSE** -- Mostafazadeh, Kalyanpur, Moon,
Buchanan, Berkowitz, Biran, Chu-Carroll, EMNLP 2020, 2020.emnlp-main.370; 440K statements, 10 causal
dimensions, ROCStories-grounded -- verified via WebSearch (ACL Anthology abstract + Semantic Scholar);
its generative-task-format read is carried at moderate confidence (the ACL Anthology abstract page itself
does not state the eval metric explicitly, confirmed by a direct fetch this cycle that came back
inconclusive on that specific point -- flagged as UNVERIFIED-BY-ABSTRACT, asserted from general
knowledge of the paper's crowdsourcing-elicitation design plus the search snippets' "collects... causal
explanations" framing, not from a table read this session). (3) **TellMeWhy** -- Lal, Chambers, Mooney,
Balasubramanian, ACL Findings 2021, 2021.findings-acl.53; >30K questions, 464-question/190-story
implicit/explicit annotated subset, ROCStories+CATERS-sourced, Likert-scored generative task, no MC
reformulation found -- verified via WebSearch (GitHub README, ACL Anthology, HF dataset card summaries).
(4) **Balanced COPA** -- Kavumba, Inoue, Heinzerling, Singh, Reisert, Inui, COIN Workshop 2019,
arXiv:1911.00225; human 97.0% (Balanced) / 100.0% (original COPA), superficial-cue finding -- verified
via WebSearch (Hugging Face dataset card, project page, arXiv abstract). RoBERTa-large 87.7%/BERT-large
76.5% on original COPA verified via WebSearch (secondary summary, not a primary-table read this cycle --
flagged as MODERATE confidence, consistent with well-known SuperGLUE-era COPA numbers). (5) **Story
Commonsense** -- Rashkin, Bosselut, Farhadi, Choi, Le Bras, ACL 2018, P18-1213; per-category F1 baseline
table (Random/TF-IDF/GloVe/LSTM/CNN/REN across Maslow/Reiss/Plutchik) verified via WebSearch (secondary
summary of the paper's baseline table; MODERATE confidence, not a direct table fetch this cycle -- the
2026-08-09 scout note's qualitative characterization of this dataset is treated as HIGH confidence,
having been primary-source-verified there; only the specific numeric F1 values are new-this-cycle and
carry the lower MODERATE tag). (6) **CSKG/ATOMIC coverage** -- confirmed via WebSearch that CSKG is the
union of ATOMIC + CWWV(ConceptNet/Wikidata/WordNet/Visual-Genome), and that a prior academic overlap
study specifically measured CSKG's triple-retrieval advantage over ConceptNet on Social IQa among other
benchmarks (2-3x more connecting evidence triples) -- this is external, independent corroboration (not
this program's own CSKG instance) that the SIQA-CSKG domain alignment claimed in this note's Headline is
a recognized property in the field, not a novel-and-unverified assumption. All facts not independently
verified this session (GLUCOSE's exact eval metric, TellMeWhy's precise question-format breakdown beyond
the implicit/explicit split, COPA's exact RoBERTa number's primary-table source, Story Commonsense's
exact F1 table) are explicitly flagged above with their confidence tier, per lit-scan calibration
discipline -- none are asserted as settled beyond what was actually read this cycle.
