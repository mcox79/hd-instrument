# Research: Target-scouting -- the next comprehension benchmark after ProPara-bridging exhaustion (2026-08-10)

> 🟡 **NOTE ADDED 2026-08-15 (correction C21) -- THIS NOTE IS CORRECT AND WAS MIS-QUOTED
> DOWNSTREAM. It is not demoted; it is the exonerating evidence.** Lines 11 and 301 say
> "native LOCAL thematic-role reading at **0.95 parse coverage**". That is a COVERAGE figure and
> this note states it accurately. Downstream it was transcribed as an ACCURACY figure --
> `notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md:158` reads "local thematic-role
> reading (0.95 held-out)". **There is no 0.95 accuracy for this organ on disk.** The real numbers:
> `exp_thematic_role_labeler_cue_integration_v1` HARD_PASS `mean_full_acc` **0.8666** at n_test=63,
> and `exp_thematic_role_labeler_qasrl_modern_revalidation_v1` **HARD_FAIL** at
> `mean_qasrl_noncanon` **0.7442**, n=3937. Anyone citing "0.95 held-out" is citing a transcription
> error, not this note.

Filed by: research (Sonnet). Trigger: explicit TARGET-SCOUTING dispatch -- ProPara-bridging is now
comprehensively exhausted for the glass-box approach (frame-activation build `exp_propara_bridging_
frame_activation_v1` landed with the PARENT task HARD_FAIL -- frame_f1=0.327 < oracle_f1=0.399 --
even though its convergence-gated frame-SELECTION sub-mechanism validated cleanly at 26x real-vs-
scramble discrimination; the ARM-1/ARM-2 lineage's natural-order win retro-corrected to mostly
order-invariant structural prior; the oracle ceiling on the unmentioned-participant subset is modest,
+0.075 absolute F1 over baseline). Task: MEASUREMENT, not build -- find 2-4 candidates that are
trap-free BY MEASUREMENT, have real headroom, are load-bearing for the two capabilities ProPara just
proved (convergence-gated frame/process SELECTION, and native LOCAL thematic-role reading at 0.95
parse-coverage), and whose residual is answerable from the prose + a learnable grounded binder, not
dominated by unmentioned world-knowledge (the trap that capped ProPara).

KB-CHECK DONE FIRST: `bash tools/substrate_query.sh "next comprehension benchmark after ProPara frame
selection thematic role local reading trap check headroom unmentioned world knowledge"` -- top
cosine=0.3008 (a starvation-diagnostic atom, not a substantive prior finding on this exact question)
-- confirmed fresh ground for the SPECIFIC lens this drill applies (scoring candidates against the
convergence-gated-frame-selection + local-thematic-role capabilities specifically, which did not exist
as proven capabilities when the earlier same-day WIQA/CLUTRR/TORQUE scorecards were written).

Read in full this cycle (all filed earlier the same day, all disk-verified, not re-derived):
`notes/research_frame_script_reading_build_spec_2026-08-10.md` (the frame-activation build spec + its
landed capability-registry outcome), `notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_
2026-08-10.md` (WIQA/TORQUE/MC-TACO scorecard -- WIQA since CONFIRMED dead via an oracle-structure
leak, per the backup doc), `notes/research_extraction_foundation_decisive_benchmark_2026-08-10.md`
(the CLUTRR/ProPara/TRIP/TORQUE trap-check that preceded ProPara's selection as primary),
`notes/research_comprehension_barrier_map_brain_foundational_2026-08-10.md` (the B1-B10/X1-X2 barrier
map), `notes/research_propara_content_driven_order_dependent_state_update_2026-08-10.md` (the ARM-1
sequential-state diagnosis), `notes/design_decisive_inference_test_propara_arm1_oracle_2026-08-10.md`
(why ProPara was chosen over TRIP/CLUTRR originally), `notes/research_islanded_comprehension_organs_
audit_2026-08-10.md` (nine independent real-text extraction attempts, same wall). Disk-verified this
cycle (read the files, not the labels): `data/capability_registry.jsonl` entries for
`convergence_gated_frame_selection` and `thematic_role_labeler_cue_integration` (incl. its
`propara_realprose_generalization_2026-08-10` annotation); the OWN measured trap-check results already
on disk at `data/benchmark_trap_check/{clutrr,trip,propara}_results.json` (built by
`tools/benchmark_trap_check/{clutrr,trip,propara}_trap_check.py`) -- these are OUR OWN numbers, not
literature citations, and are the strongest evidence in this note.

Dispatched 4 parallel Sonnet lit-scan sub-agents (public dataset/paper names only, off-platform, per
query-privacy discipline): (A) MCScript2.0 script-based-subset unmentioned-knowledge audit; (B)
ROPES/QuaRTz locality trap-check; (C) modern (2022-2025) event/frame-relation benchmark broad scan;
(D) CLUTRR/TORQUE re-score specifically against the frame-selection/thematic-role lens (not the
causal-VALIDATE lens the earlier same-day scorecard used) + SPRL/QA-SRL modern-status check. ~55
distinct external citations returned across the four lanes.

---

## HEADLINE

**MAVEN-ERE (Wang et al., EMNLP 2022) is the recommended next target -- it is the first candidate in
this program's whole benchmark-scouting history whose task SHAPE is a near-literal isomorph of the
capability that just validated (convergence-gated frame/relation-TYPE selection among a bounded
candidate set, using convergent textual evidence), on real modern prose, with headroom an order of
magnitude larger than ProPara's.** Event triggers are pre-tagged (the extraction burden TORQUE also
removes), the task is closed-set classification (CAUSE / PRECONDITION / no-relation for causal;
binary for subevent) over 57,992 causal and 15,841 subevent relation instances across 4,480 real
Wikipedia documents, and the field's own numbers show the task is nowhere near saturated even three
years on: SOTA ~30-32% F1 (ProtoEM 2023) against human inter-annotator agreement of kappa=69.5%
(causal) / 75.1% (subevent) -- a huge, still-open gap, versus ProPara's mere +0.075 oracle ceiling.
Relations are evaluated WITHIN-document, so the correct label is recoverable from textual/discourse
evidence plus a small, bounded relation-type inventory -- structurally the same "bounded knowledge,
not open-ended unmentioned participant space" shape that made ProPara's OWN oracle-structure test
tractable, without ProPara's problem (the oracle-multiset-given regime not surviving contact with
real extraction). **The one real gap: no BoW/majority baseline for MAVEN-ERE has ever been published
-- exactly the evidentiary hole that hid WIQA's oracle-structure leak until we measured it ourselves --
so a self-run trap-check (majority-class + adjacent-sentence-heuristic baselines) is the MANDATORY
first action before any build commitment, not an optional nicety.**

**Second pick, with a mandatory self-controlled ablation first: ROPES** (Lin, Tafjord, Clark, Gardner,
MRQA-EMNLP 2019). Its entity-role-mapping requirement (which of two named situation-entities
instantiates the "more"/"less" side of an EXPLICITLY-STATED background relation) is a genuine,
load-bearing exercise of voice/position-invariant role assignment -- closer to native thematic-role
reading than anything else scanned -- and 87% of its residual is locally grounded (67% explicit +
20% paraphrased-but-stated) versus only 13% true unstated-commonsense leakage, the best "local not
unmentioned" ratio found outside MAVEN-ERE. But the published "minus-background" ablation is a real
red flag (RoBERTa-large scores 61.1 F1 WITH the background paragraph vs. 60.4 F1 WITHOUT it on test --
a near-tie that says a large fraction of the reported 27.4-point SOTA-to-human headroom may be
answerable from situation+question surface cues alone, never engaging the stated rule). This must be
re-measured on our own pull before ROPES is trusted, exactly the same "measure the shortcut yourself,
do not inherit the published number" discipline this program has now had to apply four times running.

**Sharp corrective finding, worth stating plainly because it overturns an earlier same-day
recommendation: MCScript2.0's script-based subset -- ranked #1 PRIMARY as recently as the 2026-08-09
narrative-benchmark-scout note -- is a WEAK fit for the capability that just proved out.** A dedicated
audit this cycle found the applicable everyday-scenario (going to a restaurant, baking a cake) is
GIVEN by the passage topic/title; the benchmark never asks a system to discriminate among competing
candidate scripts the way ProPara asked it to pick combustion-vs-erosion-vs-photosynthesis. Frame/
script SELECTION -- the mechanism that just validated at 26x -- is trivial on MCScript2.0 and would
sit unexercised. Worse, there is a secondary (medium-confidence) signal that the residual may lean
MORE open-commonsense than ProPara's own 18-process library, not less (a follow-on paper found
ATOMIC, not ConceptNet, the better knowledge-graph fit for this benchmark's script-based questions --
ATOMIC is broad social/if-then commonsense, not a bounded typical-order fact list). MCScript2.0
remains a legitimate SECONDARY target for the thematic-role-reading capability specifically (the
within-script "who does what" reading is real), but should NOT be re-promoted to PRIMARY on the
strength of the frame-selection win, because that win does not transfer to it.

**CLUTRR and TORQUE, re-scored against this specific lens (not the causal-VALIDATE lens the earlier
same-day scorecard used), are both WEAK matches for either proven capability and should stay
demoted.** CLUTRR's fact sentences are engineered by the authors to each express exactly ONE
unambiguous kinship relation -- there is no candidate-frame disambiguation to select among, so
frame-selection is not exercised; its real difficulty is coreference + logical composition (the
Stage-2A mechanism, already given its home-turf test in the ARM-1/ARM-2 lineage). Our OWN
already-measured trap-check numbers (below) additionally show CLUTRR's endpoint-only shortcut,
while it does degrade with chain length as predicted, PLATEAUS at a real, non-vanishing 0.25-0.33
accuracy for k>=6 (vs. a majority floor of 0.04-0.11) -- a partial, not clean, leak, consistent with
the program's prior decision to demote CLUTRR to a k>=4-only secondary diagnostic rather than a
flagship. TORQUE's relation TYPE is usually signaled by a single question word ("before" vs "after"),
not selected from convergent cross-sentence evidence, and it explicitly excludes thematic-role
assignment by design (event-to-event timing regardless of participant roles) -- confirmed this cycle
via primary-source re-read, not assumed.

P_deflated = **0.45** (novel-synthesis cap 0.50) for "MAVEN-ERE is the correct next primary target" --
this is a benchmark-fit/selection judgment (lower risk class than a mechanism claim, so less
deflated than a build-outcome estimate), held below the cap because the mandatory self-run trap-check
has not yet been executed and the class-imbalance risk (57,992 causal relations is very likely a small
fraction of all candidate event pairs, meaning a naive majority/no-relation baseline could be
deceptively strong) is a real, unmeasured, WIQA-and-CLUTRR-history-informed risk. P = **0.20**
(deflated) for "a convergence-gated relation-type-selection loop, adapted to MAVEN-ERE and reusing
the owned thematic_role_labeler for event-argument context, HARD-PASSes its first pre-registered
experiment" -- lower than any prior first-experiment P in this program's history, because MAVEN-ERE
needs an entirely new relation-type-classification adaptation with no existing owned-organ head
start comparable to WIQA's near-direct `CausalLinkRegister` reuse, and because the class-imbalance
risk above is genuinely unknown until measured.

---

## 1. Full candidate scorecard (trap-free-by-measurement, headroom, capability fit, locality)

### 1a. MAVEN-ERE (Wang et al., EMNLP 2022, ACL Anthology 2022.emnlp-main.60 / arXiv:2211.07342)

| Axis | Finding |
|---|---|
| **1. Trap-free by measurement** | NOT YET MEASURED BY US OR ANYONE -- no published majority/BoW baseline found for either the causal or subevent relation-classification task. This is the SAME evidentiary hole that hid WIQA's oracle-structure leak (5005/5005 correlation) until this program measured it directly. Structural risk flagged honestly: causal relations (57,992) across 4,480 documents' worth of ALL candidate event pairs is very likely a small minority class, so a naive "predict no-relation" majority baseline needs to be measured, not assumed low. **MANDATORY first action, not optional.** |
| **2. Headroom** | LARGE and apparently unsaturated three years post-release. Best published: RoBERTa-based joint model ~31.5% F1 causal / 27.5% F1 subevent (2022); ProtoEM (2023, arXiv:2309.12892) causal F1 31.96+/-0.24, subevent F1 29.73+/-0.26 -- essentially the SAME ceiling as 2022, meaning the field has NOT closed this gap in the interim. Human agreement: Cohen's kappa 69.5% (causal) / 75.1% (subevent) -- no single "human F1" published, but the high kappa implies a ceiling well above current SOTA. Compare ProPara's own oracle ceiling of +0.075 absolute F1 -- this headroom is qualitatively larger. |
| **3. Load-bearing for proven capabilities** | STRONG for frame/relation-TYPE SELECTION: the causal task is 3-way classification (CAUSE / PRECONDITION / no-relation) and the subevent task is binary -- both are closed-candidate-set decisions made from convergent textual/discourse evidence, the SAME shape as convergence-gated frame selection (multiple candidate frame/relation types, disambiguated by co-occurring cues), just with relation types instead of process types. WEAK/INDIRECT for thematic-role reading -- the ERE relation layer itself does not test AGENT/PATIENT assignment; that lives in the base MAVEN event-argument annotations (Wang et al. 2020, EMNLP, "MAVEN: A Massive General Domain Event Detection Dataset"), a companion corpus on the SAME documents. A combined MAVEN + MAVEN-ERE target could exercise both capabilities on one corpus family -- flagged as a promising extension, not independently verified this cycle. |
| **4. Locality (not the unmentioned-knowledge trap)** | GOOD. Relations are evaluated WITHIN-document; the correct label is derivable from the passage's own textual/discourse evidence plus a small, bounded relation-type inventory (3 causal labels, 2 subevent labels) -- there is no open-ended unmentioned-participant space analogous to ProPara's implicit oxygen/ash. This is the strongest "bounded, not open" story of any candidate scanned this cycle. |
| **5. Extractability / glass-box feasibility** | HIGH. Event triggers are PRE-TAGGED (built on MAVEN's own event-detection annotations) -- removes the single hardest failure mode this program has hit repeatedly (extraction). Classification output (not free-form generation) is directly glass-box scoreable. |
| **Data access** | Public. GitHub `THU-KEG/MAVEN-ERE` (code + data). No license blocker found this cycle (not independently re-verified). |

### 1b. ROPES (Lin, Tafjord, Clark, Gardner, MRQA workshop @ EMNLP 2019, ACL Anthology D19-5808 / arXiv:1908.05852)

| Axis | Finding |
|---|---|
| **1. Trap-free by measurement** | NOT YET MEASURED BY US -- but the ORIGINAL AUTHORS' OWN "minus background" ablation is a red flag we did not have to discover ourselves: RoBERTa-large scores 61.1 F1 WITH the background paragraph vs. 60.4 F1 WITHOUT it on test (near-identical). This means a meaningful share of the reported headroom may be answerable from situation+question surface cues alone, without applying the background's stated rule -- a construct-validity risk that MUST be re-measured on our own pull (with our own baselines: majority, no-background, BoW) before trusting any downstream number. |
| **2. Headroom** | LARGE at face value: RoBERTa-large+RACE-pretrain (SOTA at publication) 61.6 F1 vs. human 89.0 F1 (400-question expert sample) = 27.4-point gap. No confirmed 2020-2025 saturation found this cycle (unverified, not assumed solved). Honest caveat: the true, ablation-controlled headroom could be smaller than 27.4 points once the background-independence artifact above is priced in. |
| **3. Load-bearing for proven capabilities** | GOOD for thematic-role-style reading, WEAK for frame-selection. The paper's own question-type table: 71% "effect comparison" + 15% "cause comparison" (86% total) require determining WHICH of two named situation-entities instantiates the "more"/"less" or cause-present/cause-absent side of the background's stated relation -- genuine role-correspondence mapping, not trivial (the authors flag prior work, QuaRel, showing models "easily confuse the two situations"). Frame-selection is essentially ABSENT: each question is paired with exactly ONE background relation, no candidate-frame disambiguation. |
| **4. Locality** | GOOD, best outside MAVEN-ERE. The authors' own error analysis (n=100): 67% Explicit (relation directly restated), 20% Lexical gap (relation stated but paraphrased -- still local/text-internal), 13% Common sense (genuinely requires unstated world knowledge, e.g. inferring a freezer "removes energy"). 87% locally grounded is the best ratio found this cycle outside MAVEN-ERE, though the background-ablation near-tie (axis 1) muddies how much of that 87% is actually being exercised by current models. |
| **5. Extractability** | MEDIUM. Two-passage structure (BACKGROUND + SITUATION) is an extra layer of indirection our extraction pipeline has not exercised (flagged already in the earlier same-day WIQA-scoping note's Section 1d, not re-derived here). |
| **Data access** | Public, CC BY 4.0, `allenai/ropes` on Hugging Face. Hidden test partition (use dev for iteration). |

### 1c. QuaRTz (Tafjord, Gardner, Lin, Clark, EMNLP-IJCNLP 2019, ACL Anthology D19-1608 / arXiv:1909.03553) -- screened, NOT recommended

| Axis | Finding |
|---|---|
| **1. Trap-free by measurement** | FAILS, by the ORIGINAL AUTHORS' OWN numbers: the no-knowledge baseline (BERT-PFT, questions only, 68.8) BEATS the real-retrieval pipeline model (BERT-PFT+IR, 64.4) on their own benchmark table. This is a documented, author-disclosed artifact -- worse than ROPES's near-tie, an outright inversion. Ignoring the retrieved background sentence scores HIGHER than using it. |
| **2/3/4.** | Single-hop (simpler than ROPES, explicitly "no chaining" per the authors), closed 400-sentence knowledge corpus (bounded, good locality story in principle), real entity-role mapping via the "Multiple Worlds" phenomenon (~26% of items, two-entity comparison, also flagged confusable by prior work). But ~35% of items need "indirection and commonsense knowledge" beyond the closed corpus per the authors' own linguistic analysis -- and the axis-1 finding makes any headroom claim unreliable until re-measured. |
| **Verdict** | NOT RECOMMENDED as a primary or even a validated warm-up target given the disclosed no-knowledge-beats-pipeline artifact -- this is a WORSE-verified content-ceiling problem than any candidate that survived to the ranked shortlist below. Included here to close the loop per the prompt's instruction not to omit a screened candidate. |

### 1d. MCScript2.0 script-based subset (Ostermann, Roth & Pinkal, *SEM 2019) -- re-audited under the NEW lens, DEMOTED from the 2026-08-09 note's #1 PRIMARY ranking

| Axis | Finding |
|---|---|
| **1. Trap-free by measurement** | Original published numbers stand (majority 50%/50%, TriAN+ConceptNet 72% overall / 67% script-based / 78% text-based, human 97%) -- not re-measured this cycle, carried from the 2026-08-09 note. |
| **2. Headroom** | Real but MODEST on the script-based subset specifically (67% -> 97% = 30 points, smaller than MAVEN-ERE's ~40-point kappa-implied gap or ROPES's 27.4). |
| **3. Load-bearing for proven capabilities** | **WEAK for frame-selection -- the corrective finding of this drill.** The applicable everyday scenario (which of ~200 named scripts: restaurant, doctor, baking) is GIVEN by the passage's own topic/title; MCScript2.0 never asks a system to discriminate among competing candidate scripts, unlike ProPara's combustion-vs-erosion-vs-photosynthesis choice. The mechanism that just validated at 26x (co-participation coincidence gating over a CANDIDATE POOL) has no candidate pool to gate here -- it would sit structurally unexercised. GOOD for thematic-role reading (within-script "who does what" is real and non-trivial). |
| **4. Locality** | AMBIGUOUS-TO-RISKY, a new finding this cycle. The scenario space IS bounded and enumerable (200 named scripts, ~11x ProPara's 18 processes, with DeScript already publishing a structured typical-order/participant library for 40 of them) -- same SHAPE as the ProPara library that worked. BUT a follow-on knowledge-graph-integration paper (found this cycle, medium confidence, not independently PDF-verified) found ATOMIC -- broad social/if-then commonsense, NOT a bounded typical-order fact list -- a better conceptual fit for MCScript2.0's script-based residual than ConceptNet. This is a real amber flag that the residual may lean more open-ended than the 200-scenario framing suggests, closer to (not further from) the ProPara trap. |
| **Verdict** | SECONDARY at best, specifically for thematic-role validation; do NOT re-promote to primary on the strength of the frame-selection win -- that win does not transfer here. This directly corrects the 2026-08-09 narrative-benchmark-scout note's #1 PRIMARY ranking, which pre-dated the frame-selection capability existing at all and could not have applied this lens. |

### 1e. CLUTRR -- re-scored, OUR OWN disk-measured numbers (not literature)

| Axis | Finding |
|---|---|
| **1. Trap-free by measurement** | MEASURED ON DISK this session (`data/benchmark_trap_check/clutrr_results.json`, `tools/benchmark_trap_check/clutrr_trap_check.py`, HF `CLUTRR/v1` `gen_train23_test2to10` split). TEST (k=2..10, true held-out): majority=0.065, content_bow=0.134, bag_of_relations=0.120 (mostly majority-fallback, since only 9.9% of test keys were seen in train). ENDPOINT-ONLY (the WIQA-analog shortcut probe): overall 0.399, but broken out by k it DEGRADES as predicted -- k=3: 0.619, k=4: 0.50, k=5: 0.414, k=6: 0.262 -- then PLATEAUS at a real, non-vanishing 0.25-0.33 for k in {6..10} (vs. a majority floor that stays flat at 0.04-0.11 across the same range). Verdict: a PARTIAL, not a clean, leak -- consistent with the pre-registered MIDDLE_BAND outcome in the earlier same-day extraction-foundation note, not the HARD-PASS that note hoped for. (k=2's 1.0 endpoint-only accuracy is NOT evidence of a shortcut -- at k=2 the "first" and "last" facts ARE the whole chain by construction, so this is the oracle, not a leak.) |
| **2. Headroom** | Real at low k, genuinely uncertain at high k given the partial endpoint leak above. |
| **3. Load-bearing for proven capabilities** | **WEAK for frame-selection** (this cycle's Lane D re-audit, primary-source-confirmed): CLUTRR's fact sentences are deliberately engineered by the authors so each expresses exactly ONE unambiguous kinship predicate once parsed -- crowdworkers were instructed not to "reveal the implied relation," and there is no candidate-relation-type disambiguation task anywhere in CLUTRR's design. CLUTRR tests coreference + multi-hop logical COMPOSITION (the Stage-2A mechanism), not selection. **WEAK-TO-PRESENT for thematic-role reading**: sentences are mostly active-voice narrative prose (e.g. "Frank went to the park with his father, Brett"), not adversarially passive/inverted -- role assignment is rarely the bottleneck. |
| **Verdict** | Confirms the program's existing decision (per `design_decisive_inference_test_propara_arm1_oracle_2026-08-10.md`) to keep CLUTRR as a k>=4-only SECONDARY composition/extraction-diagnostic, not a flagship, and adds: it is ALSO not a good fit for the frame-selection/thematic-role capabilities this drill is specifically scouting for. Do not re-promote. |

### 1f. TRIP -- REJECTED, our own disk-measured numbers confirm the earlier "MCScript-trap" call

| Axis | Finding |
|---|---|
| **1. Trap-free by measurement** | FAILS, measured on disk this session (`data/benchmark_trap_check/trip_results.json`, `tools/benchmark_trap_check/trip_trap_check.py`). `content_bow_fulltext` (a full-story bag-of-words classifier, no reasoning) scores **0.714 (dev) / 0.704 (test)** against a **0.50 majority baseline** on TRIP's binary plausibility task -- BoW alone recovers roughly 40+% of the entire SOTA-to-majority gap (SOTA ~93-94% per the earlier same-day note) with zero causal/physical-state reasoning. This is the clean MCScript-v1-style content-ceiling failure the design note flagged from literature; now independently reproduced by direct measurement, not inferred. |
| **Verdict** | REJECTED, confirmed by measurement (not just literature triangulation). Do not revisit without a fundamentally different scoring protocol that neutralizes the BoW-recoverable signal. |

### 1g. TORQUE -- re-scored under the NEW lens

| Axis | Finding |
|---|---|
| **3. Load-bearing for proven capabilities** | **WEAK for frame-selection** (this cycle's Lane D re-audit, primary-source-confirmed): the correct temporal-relation TYPE is usually signaled by a single question word ("what happened BEFORE X" vs "AFTER X"), not selected from among competing candidates via convergent cross-sentence evidence -- a materially weaker frame-selection analog than MAVEN-ERE's genuine multi-class classification. A 2024 follow-on (arXiv:2408.07353) models temporal AMBIGUITY (multiple valid answers per question), which is a real, structurally distinct phenomenon, but is answer-SET ambiguity given a relation type, not relation-TYPE selection. **ABSENT for thematic-role reading**, confirmed via primary-source re-read this cycle: TORQUE is explicitly event-to-event timing "regardless of participant roles" by the authors' own framing against SQuAD-style predicate-argument QA -- no AGENT/PATIENT disambiguation is required to answer correctly. |
| **Verdict** | Remains a structurally clean content-ceiling story (candidates are drawn from the passage's own pre-tagged event vocabulary, so lexical overlap is close to vacuous) but is a weak match for either of the two specific capabilities this drill is scouting for. Keep as a reserve/near-term-follow-on per the earlier same-day WIQA-scoping note, not promoted here. |

### 1h. Also screened this cycle, not carried to the ranked shortlist

- **CRAB** (Romanou et al., EMNLP 2023, arXiv:2311.04284): modern (2023), real news events, glass-box (binary/4-class/MCQ causal classification), meaningful headroom (GPT-4 45.6-73.9% F1, not saturated). BUT 87% of pairs are CROSS-DOCUMENT (violates "locally grounded, single passage" -- most items require synthesizing across multiple articles about a story, closer to open retrieval than bounded local reading) and the graded-causality sub-task has low inter-annotator agreement (Krippendorff's alpha=0.28, a genuine measurement-noise risk). The binary sub-task is cleaner but the dataset's headline design leans cross-document. Not recommended as primary; worth a second look if MAVEN-ERE's mandatory trap-check fails.
- **ACCESS** (NAACL 2025, arXiv:2502.08148): built from GLUCOSE's implicit-commonsense-causality annotations -- explicitly requires OPEN/abstracted commonsense beyond the given text. Disqualified outright under the locality criterion; this is a near-textbook restatement of the ProPara trap on a different corpus.
- **Choice-75** (2023, arXiv:2309.11737, "A Dataset on Decision Branching in Script Learning"): flagged by Lane A as a modern, script-flavored candidate (75 scripts, 600+ scenarios) but NOT deeply vetted this cycle -- its DeScript lineage and locality profile are unconfirmed. Worth a follow-up drill if MAVEN-ERE and ROPES both stumble on their mandatory trap-checks.
- **QA-SRL Bank 2.0** (FitzGerald et al. 2018, arXiv:1805.05377): 250K+ QA pairs over 64K sentences, explicitly voice-parameterized questions ("Who was affected by X?"), span-scoreable (EM/F1), and evidence of CONTINUED modern use (QAPyramid, arXiv:2412.07096, 2024; QANom/QASem lineage). This is the single CLEANEST, LOWEST-RISK isolated test of the thematic-role-reading capability found anywhere in this scan -- but it is a semantic-role-labeling benchmark, not a comprehension benchmark (no inference beyond correctly reading roles off a sentence; no situation-model tracking, no cross-sentence composition). Recommend as a CHEAP, LOW-RISK calibration side-quest (confirm the owned thematic_role_labeler generalizes past its McGuffey-derived validation onto a genuinely modern, large, real corpus) rather than a flagship -- directly answers the standing wire-don't-island caveat already on that capability's registry row ("McGuffey is a USER-DEPRECATED source... re-validate on a modern-source held-out before wiring").
- **Schema/script-induction benchmarks** (Open-Domain Hierarchical Event Schema Induction, ACL 2023; Zero-Shot On-the-Fly Event Schema Induction, 2022) and **SCHEMA** (ICLR 2024, instructional video): ruled out -- generative/graph-similarity scoring (not glass-box classification/MC/span) or wrong modality (video), respectively.
- **MC-TACO non-ordering categories, e-CARE, GLUCOSE, TellMeWhy, ESTER, OpenPI**: carried, not re-screened, from the earlier same-day extraction-foundation note's exhaustive rule-outs (durational-KB dependency, single-hop, per-sentence scoring, confirmed lexical-overlap leak, confirmed proximity leak, structure-is-the-answer respectively) -- still valid, no new evidence this cycle changes any of these calls.

---

## 2. Ranked recommendation

1. **MAVEN-ERE (primary).** Best combination of headroom (largest of any candidate scanned, apparently unclosed since 2022), locality (bounded within-document relation-type inventory, no unmentioned-participant space), and DIRECT structural isomorphism to the capability that just validated (convergence-gated selection among a bounded candidate set via convergent evidence) -- with event triggers pre-tagged, removing this program's most consistently fatal failure mode. The one disqualifying-if-unmeasured risk (class imbalance / no published naive baseline) is exactly the kind of gap this program has now learned, four times over (WIQA, CLUTRR endpoint-shortcut, TRIP, QuaRTz's own authors), NOT to inherit on trust -- Section 3 makes the self-run trap-check the mandatory first move, before any organ-extension engineering.
2. **ROPES (strong second, ablation-gated).** Best thematic-role/entity-mapping fit of any candidate outside MAVEN-ERE, and the best locality ratio (87% explicit-or-paraphrased-local) outside MAVEN-ERE. Held below MAVEN-ERE specifically because its published background-ablation near-tie is a documented, not hypothetical, risk that must be resolved by our own re-measurement before any headroom number is trusted -- the same self-measurement discipline QuaRTz's OWN authors already model for us (they disclosed their own no-knowledge-beats-pipeline artifact rather than hiding it).
3. **MCScript2.0 script-based subset (demoted to secondary, thematic-role-only).** No longer the primary pick this program should chase, now that frame-selection is a proven, specific capability the benchmark does not exercise. Retains value as a low-risk thematic-role validation target, with an honest amber flag that its residual may lean more open-commonsense than its bounded-scenario-count story suggests.
4. **CLUTRR (k>=4-only secondary, unchanged status).** Confirmed by OUR OWN measurement to carry a partial, non-vanishing endpoint-only shortcut at high k, and confirmed by this cycle's re-audit to be a weak match for either of the two capabilities this drill specifically scouts for. No change from its existing scoped role.
5. **QA-SRL Bank 2.0 (cheap parallel calibration side-quest, not a flagship).** Recommended as a LOW-COST, LOW-RISK immediate action regardless of which flagship is chosen: it directly answers the open "does the thematic-role labeler generalize past its McGuffey-derived, USER-flagged-deprecated validation onto a modern, large, real corpus" question sitting on that capability's own registry row, with no comprehension-pipeline engineering required (pure SRL-as-QA scoring).

**REJECTED / not recommended, confirmed by measurement or primary-source re-read this cycle:** QuaRTz
(authors' own disclosed no-knowledge-beats-pipeline artifact), TRIP (our own BoW=0.70+ measurement),
TORQUE (weak fit for either target capability, though structurally content-clean, kept in reserve per
earlier scoping), CRAB (87% cross-document, low IAA on its graded sub-task), ACCESS (open-commonsense
by design, a restatement of the ProPara trap).

---

## 3. First-experiment design for the top pick (MAVEN-ERE) -- measurement, not build

**STEP 0 (BLOCKING, ~1 day, no organ engineering, exactly the "measure the shortcut before building"
discipline this program has had to re-learn four times):** pull MAVEN-ERE (`THU-KEG/MAVEN-ERE`), and
before writing any classifier, compute on the causal-relation subset (dev split):
1. **MAJORITY baseline** -- predict the single most frequent label (very likely "no-relation" given
   57,992 positive relations across a much larger space of all candidate event pairs). This is the
   single most important unmeasured number -- if majority alone scores near the ~30% F1 SOTA ceiling
   (a real risk given the likely severe class skew), MAVEN-ERE's headroom is illusory and the whole
   pick collapses, exactly the WIQA pattern.
2. **ADJACENT-SENTENCE-HEURISTIC baseline** -- predict CAUSE if the two events sit in the same or an
   adjacent sentence, connected by a small fixed causal-connective word list (because, so, as a
   result, due to, ...); this is the TORQUE/ProLocal-style surface-cue shortcut most likely to leak on
   this exact task shape.
3. **BAG-OF-EVENT-TYPES baseline** -- a lookup/logistic-regression classifier over the (event-type-A,
   event-type-B) pair alone, ignoring all surrounding text -- tests whether the relation TYPE is
   over-predictable from event-type co-occurrence statistics alone (the MAVEN-ERE-analog of WIQA's
   sign-leak and CLUTRR's bag-of-relations probe).

Only if MAJORITY and the two shortcut baselines all sit well below the published SOTA/kappa-implied
ceiling does STEP 1 (build a convergence-gated relation-type-selection classifier, reusing
`hdlab/thematic_role_labeler` for event-argument context and the same co-participation-coincidence
GATE pattern validated on ProPara, adapted from process-type candidates to relation-type candidates)
become a justified engineering investment.

**Why this is fair and can-fail:** majority and adjacent-sentence-heuristic are real, plausible
surface shortcuts for THIS exact task shape, not strawmen; bag-of-event-types isolates whether the
relation-type label is over-determined by static type co-occurrence (analogous to the leak that
killed WIQA); reuses the exact "measure before building" sequencing this program's own trap-check
tooling (`tools/benchmark_trap_check/`) already established for CLUTRR/TRIP/ProPara -- this drill
recommends extending that SAME tooling with a `maven_ere_trap_check.py`, not inventing a new
methodology. Cheap (public dataset, no GPU, three lookup/logistic-regression baselines is at most a
day of scripting); one-lever (measurement only, zero organ engineering committed until Step 0 clears).

---

## Cheap decisive test

Before any build commitment: does a `maven_ere_trap_check.py` (majority-class + adjacent-sentence-
heuristic + bag-of-event-types baselines, on MAVEN-ERE's causal-relation dev split) show BASELINE
performance materially BELOW the published ~30-32% F1 SOTA / kappa~0.70 human-agreement ceiling --
i.e., does real, uncontaminated headroom survive contact with the cheapest plausible shortcuts, the
same bar ProPara passed (majority macro-F1 0.216 vs. content-BoW unmentioned-subset macro-F1 0.238,
essentially flat) and every other candidate this cycle failed at some axis (WIQA's oracle leak, TRIP's
BoW=0.70+, QuaRTz's disclosed inversion, CLUTRR's partial endpoint leak)? This is cheap (public
dataset, no GPU), can-fail (three concrete, plausible shortcuts, not strawmen), one-variable
(measurement only), and directly extends the SAME trap-check harness already proven on ProPara/CLUTRR/
TRIP rather than inventing new methodology.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS (clears MAVEN-ERE for engineering investment):** MAJORITY <= 40% F1 on the causal
  3-way task (a real ceiling given probable class skew, DEV-calibrated not assumed) AND
  ADJACENT-SENTENCE-HEURISTIC <= MAJORITY + 10 points F1 AND BAG-OF-EVENT-TYPES <= MAJORITY + 10
  points F1 AND the gap between the best of these three baselines and the published SOTA (~31% F1)
  is >= 5 points (real headroom survives the cheapest shortcuts). Predicted P ~ 0.45 (deflated;
  the class-imbalance risk is the single largest unknown, and no published baseline exists to anchor
  against, exactly WIQA's pre-discovery evidentiary gap).
- **HARD-FAIL (reject MAVEN-ERE as primary; fall back to ROPES with its own ablation-controlled
  re-measurement, or MCScript2.0's thematic-role-only secondary role):** any of the three baselines
  scores within 5 points of the published SOTA (a majority-class or surface-cue leak dominates the
  task) OR the class skew is so severe that "majority" itself IS the effective SOTA (a degenerate,
  saturated-by-construction task, the CRAB-graded-subtask failure mode).
- **MIDDLE_BAND (proceed with a narrowed claim):** one of the two shortcuts (adjacent-sentence or
  bag-of-event-types) shows a real but partial edge -- narrow the flagship claim to the subevent
  relation task specifically (smaller, 15,841 instances, potentially cleaner) or to causal pairs
  that are NOT sentence-adjacent (the subset where the adjacent-sentence heuristic is structurally
  inapplicable), mirroring the E4/WIQA precedent of narrowing to a mechanism-distinctive subset.
- **Independent, parallel prediction (ROPES ablation, not gated on MAVEN-ERE):** re-running the
  "minus background" ablation ourselves on a ROPES dev pull will reproduce the published near-tie
  (background-present vs background-absent scores within ~2 F1 points of each other), confirming the
  published red flag rather than it being a one-off artifact of the original authors' specific model.
  Predicted with moderate confidence (P ~ 0.55) since this is reporting a measurement replication, not
  a mechanism claim, so it carries a lighter deflation than the MAVEN-ERE build-outcome estimate.

## Cross-thread synthesis

- Directly extends and re-scores `notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_
  2026-08-10.md` and `notes/research_extraction_foundation_decisive_benchmark_2026-08-10.md`: both
  scored candidates against the Stage-2A causal-VALIDATE mechanism, which was the only proven
  multi-hop-inference capability at the time. This drill applies a NEWER, MORE SPECIFIC lens
  (convergence-gated frame SELECTION at 26x, native LOCAL thematic-role reading at 0.95 parse
  coverage) that did not exist as a proven capability until the frame-activation build landed later
  the same day -- and under that lens, WIQA/CLUTRR/TORQUE all re-score WEAKER than under the older
  lens, while a genuinely new candidate (MAVEN-ERE) that neither earlier note considered scores
  materially stronger. This is not a contradiction of the earlier notes; it is the natural
  consequence of a new proven capability changing which benchmarks are load-bearing.
- Directly corrects `notes/research_narrative_benchmark_scout_2026-08-09.md`'s #1 PRIMARY ranking of
  MCScript2.0 -- that note pre-dated the frame-selection capability entirely and could not have
  applied this lens; Section 1d above supplies the correction with disk-and-literature evidence
  (script selection is trivial on MCScript2.0; the capability that just validated has no candidate
  pool to gate there).
- Extends `notes/research_frame_script_reading_build_spec_2026-08-10.md`'s own honest hard-tail
  disclosure ("open-domain frame coverage beyond the 18 hand-vetted processes... is the honest hard
  tail") by identifying a benchmark (MAVEN-ERE) whose relation-type inventory is ALREADY bounded and
  closed by the dataset's own design (3 causal labels, 2 subevent labels) -- sidestepping the
  open-domain-coverage problem entirely rather than requiring the substrate to grow its own frame
  library first, which is a materially cheaper near-term path than the frame-library-growth work that
  note flagged as a separate, later-gated decision.
- Confirms, via fresh independent primary-source re-reads (Lane D), the earlier same-day extraction-
  foundation note's TORQUE finding that "criterion 2 [structure-is-not-the-answer] is STILL THE OPEN
  QUESTION" -- this drill answers it: TORQUE's relation type is usually question-word-signaled, not
  selected from convergent evidence, so it does not exercise frame-selection even where it does pass
  the content-ceiling test.
- Uses OUR OWN previously-collected trap-check numbers (`data/benchmark_trap_check/{clutrr,trip,
  propara}_results.json`) as primary evidence for the CLUTRR/TRIP verdicts in this note, rather than
  re-deriving them from literature -- these are load-bearing, disk-verifiable facts, not estimates.

## Substrate-product implications

If the MAVEN-ERE Step-0 trap-check clears and the follow-on build lands, the defensible product claim
would be sharper than ProPara's: a glass-box system that reads real Wikipedia-sourced event narratives
and selects the correct causal/subevent relationship between two named events from a small, auditable
candidate set -- with a visible trace of WHICH textual/discourse cues drove the selection -- on a
benchmark where the field's own strongest published systems still solve barely a third of what human
annotators agree on, three years after release, with no LLM at inference anywhere in the pipeline.
That is a starker, more durable headroom story than ProPara's +0.075 oracle ceiling ever offered. The
correct product-safe sequencing, per the honest gaps disclosed above: (1) Step 0's trap-check FIRST
(one day, no engineering commitment); (2) only then adapt the convergence-gated-selection mechanism
(already validated at 26x on ProPara, reusable in SHAPE, not in content) to MAVEN-ERE's relation-type
inventory; (3) in parallel, and independent of MAVEN-ERE's outcome, run the QA-SRL Bank 2.0 calibration
side-quest to resolve the thematic-role labeler's own registry-flagged McGuffey-source caveat on a
modern corpus -- this is cheap, low-risk, and directly answers an already-open item rather than
deferring it further. Do not market or measure success on MCScript2.0's script-based subset as a
frame-selection win -- per Section 1d, that specific claim would not be earned by anything this
capability actually does on that benchmark, and asserting otherwise would repeat the exact kind of
over-claim this program has now had to walk back on DesireDB, MCScript2.0 (original scope), and WIQA.

## Honest deflated grade

**Deflated grade: MEDIUM on the MAVEN-ERE pick, MEDIUM-LOW-TO-LOW on any first-experiment win claim
made before Step 0 lands.** The RANKING (MAVEN-ERE > ROPES > MCScript2.0-secondary > CLUTRR-secondary)
is a benchmark-fit/selection judgment (P ~ 0.45, deflated per calibration, capped below the 0.50
novel-synthesis ceiling specifically because MAVEN-ERE's own class-imbalance risk is real and
unmeasured -- this program does not get to treat "structurally the best shape found" as equivalent to
"verified clean" until the Step-0 numbers are on disk, per the exact lesson WIQA/CLUTRR/TRIP/QuaRTz
each taught in turn this program's history). The build-outcome estimate (P ~ 0.20) is lower than any
prior first-experiment estimate in this program specifically because MAVEN-ERE requires a genuinely
new relation-type-classification adaptation with no `CausalLinkRegister`-style near-direct organ reuse
available, unlike WIQA. **Data-access blockers for the USER to clear: none identified.** MAVEN-ERE
(GitHub, public), ROPES (Hugging Face, public, CC BY 4.0), and QA-SRL Bank 2.0 (GitHub, public) are
all downloadable now with no paywall or login found in this scan. The one open item is MECHANICAL:
none of MAVEN-ERE's baselines were actually computed this cycle (Step 0 above is literature-scoped,
not disk-measured, unlike the CLUTRR/TRIP/ProPara numbers this note DOES carry from disk) -- that is
the explicit, undeferred next action, not a blocker requiring USER decision.

## Citations (verified count)

Four parallel Sonnet lit-scan lanes, ~55 distinct sources triangulated this cycle (paper +
arXiv/ACL-Anthology + GitHub/Hugging-Face dataset card cross-checked per major finding, consistent
with this program's citation-verification standard), PLUS three files of OUR OWN previously-computed,
disk-verified trap-check numbers (not literature citations):

**Own disk data (primary evidence for CLUTRR/TRIP/ProPara verdicts):** `data/benchmark_trap_check/
clutrr_results.json` (built by `tools/benchmark_trap_check/clutrr_trap_check.py` against HF
`CLUTRR/v1`, split `gen_train23_test2to10`); `data/benchmark_trap_check/trip_results.json` (built by
`tools/benchmark_trap_check/trip_trap_check.py`); `data/benchmark_trap_check/propara_results.json`
(built by `tools/benchmark_trap_check/propara_trap_check.py`, ProPara EMNLP18 dev/test, cites Dalvi et
al. 2018 Table Cat-3 rule-based F1=2.4 vs. ProGlobal F1=35.9 for corroboration, not re-derived).
`data/capability_registry.jsonl` entries `convergence_gated_frame_selection` and `thematic_role_
labeler_cue_integration` (incl. `propara_realprose_generalization_2026-08-10` annotation).

**Lane A (MCScript2.0):** Ostermann, Roth, Pinkal, *SEM 2019, ACL Anthology S19-1012 / arXiv:1905.09531;
Ostermann, Roth, Modi, Thater, Pinkal, LREC 2018, arXiv:1803.05223; Ostermann, Roth, Thater, Pinkal,
SemEval-2018 Task 11, ACL Anthology S18-1119; Wanzare, Zarcone, Thater, Pinkal (DeScript), LREC 2016;
Modi & Titov (InScript), arXiv:1703.05260; Choice-75, arXiv:2309.11737 (2023, flagged not deeply
vetted).

**Lane B (ROPES/QuaRTz):** Lin, Tafjord, Clark, Gardner (ROPES), MRQA-EMNLP 2019, ACL Anthology
D19-5808 / arXiv:1908.05852; Tafjord, Gardner, Lin, Clark (QuaRTz), EMNLP-IJCNLP 2019, ACL Anthology
D19-1608 / arXiv:1909.03553; both HF dataset cards (`allenai/ropes`, `allenai/quartz`); "Towards
Interpretable Reasoning over ROPES", EMNLP 2020, ACL Anthology 2020.emnlp-main.548 (located, not
needed once primary tables were read directly).

**Lane C (modern 2022-2025):** Wang et al. (MAVEN-ERE), EMNLP 2022, ACL Anthology 2022.emnlp-main.60
/ arXiv:2211.07342; GitHub `THU-KEG/MAVEN-ERE`; ProtoEM, arXiv:2309.12892 (2023); Wang et al. (base
MAVEN), EMNLP 2020 (companion event-argument corpus, cited not independently re-verified this cycle);
Romanou et al. (CRAB), EMNLP 2023, ACL Anthology 2023.emnlp-main.940 / arXiv:2311.04284, GitHub
`agromanou/CRAB`; ACCESS, NAACL 2025, arXiv:2502.08148; Open-Domain Hierarchical Event Schema
Induction, ACL 2023; Zero-Shot On-the-Fly Event Schema Induction, 2022; SCHEMA, ICLR 2024.

**Lane D (CLUTRR/TORQUE re-audit + SPRL/QA-SRL):** Sinha et al. (CLUTRR), EMNLP-IJCNLP 2019, ACL
Anthology D19-1458 / arXiv:1908.06177; GitHub `facebookresearch/clutrr`; Ning, Wu, Han, Peng, Gardner,
Roth (TORQUE), EMNLP 2020, ACL Anthology 2020.emnlp-main.88 / arXiv:2005.00242; "Only One Relation
Possible?", arXiv:2408.07353 (2024); Reisinger et al. (Semantic Proto-Roles) / White et al.
(Universal Decompositional Semantics, decomp.io); FitzGerald et al. (QA-SRL Bank 2.0), arXiv:1805.05377,
GitHub `uwnlp/qasrl-bank`, qasrl.org; QAPyramid, arXiv:2412.07096 (2024).

Two items flagged UNVERIFIED, explicitly not treated as settled: the exact TriAN 67%/78%/97.4%
MCScript2.0 script-vs-text breakdown and the ATOMIC-vs-ConceptNet finding (Lane A, PDF extraction
failed twice, sourced from AI-summarized secondary fetches -- carried here with the same caveat Lane A
attached); a claimed 2025/2026-dated cross-lingual QA-SRL scaling paper (Lane D flagged this as
likely-future/unverified, not cited as settled above). No citation fabricated; every load-bearing
number traces to a specific sub-agent WebSearch/WebFetch result or a directly-read on-disk JSON file
from this session. Applying the mandatory calibration penalty (deflate 0.15-0.25, novel-synthesis
capped at 0.50): see P_deflated values in the HEADLINE and Honest deflated grade sections above.
