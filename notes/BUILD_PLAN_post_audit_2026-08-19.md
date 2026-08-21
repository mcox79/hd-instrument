# BUILD PLAN -- WHAT TO DO NEXT, POST-AUDIT. START HERE.

> # 📍 **STATE AS OF 2026-08-21 (late). ONE BLOCK, CURRENT ONLY.**
> *This block was 6,895 lines and 327 sub-headings before this rewrite -- 97% of the file -- which is
> exactly the failure its own predecessor warned about ("a reader could not tell which was live").
> **I caused that by appending all night to a document whose header forbids appending.** Every entry
> below cites the note holding its evidence; nothing is lost, and `git log` has the full sequence.*
>
> ## ⛳ **WHERE THIS STANDS**
> **The night's work was almost entirely MEASUREMENT and CORRECTION, not building.** *99+ commits,
> ~15% touching code, and **16 of my own claims withdrawn**. That is the honest headline.*
>
> ## 🧠 **THE ONE STRUCTURAL FINDING (everything else tonight is downstream of it)**
> **ONE REPRESENTATION IS DOING TWO JOBS THAT REQUIRE OPPOSITE THINGS.**
> *To learn what a word MEANS, `context_vector_masked` deletes the word from its own sentence -- the
> "no-leak fix", and correct, or grounding learns "artery means artery". But that deleted word is the
> strongest cue that two sentences concern the SAME word.* **Measured: masked hit@1 `0.1417` vs
> unmasked `0.4750`, chance `0.0167`.** *Same-word DG codes sit at `0.0056` against a cross-word
> `0.0015` -- both at the random floor.*
> ➡️ **THE BRAIN DOES NOT FACE THIS: word FORM (VWFA) and word MEANING (ATL hub + spokes) are
> SEPARATE SYSTEMS. And `notes/PLAN.md` ALREADY records this as one of its four founding anchors --
> "a spelling-derived code is a FORM code, and we have been calling it a meaning code".**
> ✅ **THE FORM ORGANS ARE ALREADY BUILT AND UNWIRED** (`char_trigram_encoder.py`, `vwfa.py`,
> `char_positional_encoder.py`; PLAN.md: *"all built, none on the live path"*, n-gram coding
> **PINNED-BY-EVIDENCE**). **So this is a WIRING decision, not a build -> board Q102.**
> ⚠️ **THE RISK, SHARPENED BY MEASUREMENT: the form channel scores `1.0000` on identification
> BECAUSE THE QUERY IS THE ANSWER. It will win any task where the word is the ANSWER; judge it only
> where the word is the QUESTION. Prior: spelling already beats our meaning read-out, `0.0767` vs
> `0.0480`.**
> `ONE_REPRESENTATION_TWO_OPPOSITE_JOBS_...` `THE_FORM_CHANNEL_SCORES_1_0000_...`
>
> ## 🔻 **THREE DEAD ENDS, ALL DOWNSTREAM OF THAT ONE CAUSE**
> 1. **CA3 cannot complete** -- our rule MERGES correlated memories (margin **−0.1021**; the local
>    error-driven rule fixes it to **+0.0975**, beating even the pseudo-inverse's +0.0839, and 16x
>    expansion cuts it from 38 passes to **8**, inside replay's `0,3,10`). ***BUT REAL WITHIN-LEMMA
>    OVERLAP IS 0.0056 AGAINST A 0.22 FAILURE THRESHOLD -- the regime never occurs on our data, so
>    DO NOT BUILD THIS FIX.*** `CA3_MERGES_...` `THE_50_PASS_...` `THE_CA3_FAILURE_DOES_NOT_ARISE_...`
> 2. **Surprise cannot gate writes** -- it has real spread (sd 0.096) but is UNCORRELATED with value
>    (r=+0.238, spans zero). ***That NAMES the mechanism for the write-gate null: gating on an
>    uncorrelated signal IS gating at random.*** `SURPRISE_IS_REAL_BUT_UNINFORMATIVE_...`
> 3. **12-dim feature context is FLAT** -- worse at every load and does not improve with more traces
>    (0.0266 at L=37 vs the incumbent's 0.1328). *NORMS12's own note predicted exactly this.*
>    `HIGHER_OVERLAP_DID_NOT_MEAN_BETTER_TASK_...`
>
> ## ✅ **WHAT IS ACTIONABLE AND MEASURED**
> - **THE LOOP STOPS ACCRUING WHERE ACCRUAL STILL PAYS.** *More traces help (hit@1 `0.0312 → 0.1328`,
>   CI-separated, shuffled control at chance) and the live MEDIAN word gets **10** -- ~60% of what
>   accumulation already buys.* ⚠️ *Combines three populations: direction is solid, "1.7x" is an
>   order-of-size estimate, NOT a measurement.* `THE_MEDIAN_WORD_LEAVES_1_7x_...`
> - **Owner Q98 APPROVED the write-rate extension** with a stopping rule: extend past p90, stop at the
>   last point where the fraction of test words with NO score is still zero (measured 0.0000
>   everywhere; tie mass 0.0000 too -- only the write-nothing arm ties, at 1.0000).
> - **WHY writing less helps: interference.** *Crosstalk DOMINATES capacity (r 0.976, n=11; rivals'
>   partials go NEGATIVE). And OUR KEYS ARE AT THE WELCH BOUND (`inv_e_sq/D = 1.000` vs the best
>   trained encoder's 0.179) -- **"better keys" is closed by GEOMETRY.** Two levers remain: FEWER
>   ITEMS and MORE DIMENSIONS.* `WHY_WRITING_LESS_HELPS_...`
>
> ## 🚫 **DO NOT RE-PROPOSE (each killed with numbers tonight)**
> *B1's "coverage cliff" (**INVERTED** -- the tiers are `cos_syn/cos_rel/cos_unrel`, so 0.002 on
> UNRELATED pairs is the GOAL and counting's 0.830 is the DEFECT); the dense-reading cell's "REFUTES"
> headline (its subset out-recalls its whole); D3's queued test (sweeps a variable that does not
> move); B1's queued floor test (its OUT stratum is EMPTY); a ceiling detector (48.5% base rate);
> sparsifying the stored key (DO-NOT-REDO 44) and DG-for-grounding (32).*
>
> ## 🧭 **METHOD -- THE ONLY RULE THAT PAID OUT**
> ***PUT A NUMBER BESIDE ANOTHER NUMBER THAT CONSTRAINS IT.*** *It killed 5 claims and cleared 3.
> Every big withdrawal was one fault: a number measured in one setting applied to another.*
> **AND: QUOTE THE NOTE, NEVER THE HEADLINE** -- all 3 passes were notes carrying a CI, a control and
> a stated limit; all 5 kills were summary headlines or same-day inferences.
> **AND: check prior work FIRST** -- it changed the answer 3 times tonight (the crosstalk mechanism,
> `ca3_completer`'s saturation guard, and the form organs already being built).
> `METHOD_REVIEW_...` `WHAT_PASSES_AND_WHAT_FAILS_...` `THE_PATTERN_ACROSS_SIX_...`
>
> ## ➡️ **NEXT**
> 1. **Q102 is with the owner** (wire the form organs). *Nothing else is blocked.*
> 2. **The encoding gap is the real target** and is upstream of all three dead ends.
> 3. *Nothing is running. The two runnable-unrun cells remain B4's d=1024 live-path 2AFC and D3's
>    test IF re-scoped to cue corruption -- both need cell authoring.*


## 🚨 [SUPERSEDED TWICE -- READ THE TWO CORRECTIONS BEFORE THE NUMBERS] PHASE 2 FINDING #1 -- THE ASSEMBLED SUBSTRATE LOSES TO WORD-COUNTING BY ~10x ON HELD-OUT TEXT
> **⛔ SUPERSEDED-BY, added 2026-08-19 rather than left for the next reader to trip over:**
> **(1) THE "~10x" IS AGAINST THE WRONG FLOOR.** `COUNT_FLOOR` is NOT the strongest floor the data
> supports -- cosine over the SAME co-occurrence counts scores **0.0300 against its 0.0125**. The
> real gap is LARGER, not smaller. See the diagnostic block above.
> **(2) THE CONSOLIDATION ORGAN NEVER FIRED IN THIS CELL.** It ran `max_patches=1`, and the
> substrate only consolidated when the forager changed corpus, so **every Phase 2 run grounded
> NOTHING**. The retrieval result stands -- both routes read from episodic writes and Library
> traces, which happen regardless -- but the ablation table must be re-run before it is quoted.
> **(3) ADDED 2026-08-19 WITH THE EVIDENCE, WHICH IS SHARPER THAN (2) AND CHANGES WHAT THE
> ABLATION NULL MEANT.** Re-read off disk (`scratch/phase2_cost_probe.py`): **`n_provenance` is 0
> on ALL 30 units, no exceptions**, and the `definitions` and `gap_detector` ablations returned
> **BIT-IDENTICAL episode counts to the control -- 8,394 in every single unit**. Those two organs
> feed the grounding path, and the grounding path never ran. **So "definitions and gap_detector
> change EXACTLY NOTHING" was the bug restated, NOT a measurement of two organs** -- and two slots
> the substrate calls FILLED were resting on it. *Also visible in the same data: the foraging twin
> read 4,000 sentences against the live arm's 1,150, 3.5x more text.*
> **THE CELL IS BEING RE-RUN AS `v3_consolidation`, DEMOTED FROM A REPORT CARD TO A WIRING
> DIAGNOSTIC.** Its score stays retired (best achievable 0.0300 vs our 0.0150 -- fixing every
> defect wins a tie with a floor); what it is for is one pre-registered question: **with
> consolidation firing, does the read-out change AT ALL?** A new `consolidation` ablation decides
> it, and its binding is proven BOTH WAYS by a substrate self-test (on -> 30 provenance rows and
> 91 refusals; off -> 0 and 0). **That two-way proof is the point: an ablation asserted only by
> "the ablated arm grounds nothing" would have PASSED on the broken run.**

**The first end-to-end measurement of the assembly, and it is a clean negative that INDEPENDENTLY
REPLICATES THIS PROJECT'S CENTRAL DOCUMENTED RESULT on a different task, a different instrument
and a different route.** `scratch/recall_route_compare.py`, 400 sentences read, 200 items,
pool 996, one corpus, one seed. **No CI yet, so these are measurements and not yet a verdict.**

| route | SEEN (exact key) hit@1 | **HELD-OUT hit@1** |
|---|---|---|
| EPISODIC (DG code overlap after CA3 settling) | **0.795** | **0.025** |
| SEMANTIC (cosine to the accumulated context profile) | 0.165 | **0.005** |
| **COOC floor** (raw co-occurrence counting) | **0.320** | **0.255** |
| **FREQ floor** (ignores the cue entirely) | 0.170 | **0.265** |

**⛔ NEVER QUOTE 0.795 AS A CAPABILITY.** The cue at exact key IS the vector the episode was
written from -- the same write-then-read-a-register shape that refuted
`exp_causal_link_comprehension_fuller_v2` ("no comprehension was tested"). **It is a CEILING
DIAGNOSTIC and it is doing one useful job: it proves the store, the encoder and the scorer all
work, so the held-out collapse is a REAL NEGATIVE and not a broken instrument.**

**THE NUMBER THAT MATTERS: on sentences it never read, the substrate scores 0.025 where COUNTING
WORDS SCORES 0.255, and where a floor that DOES NOT LOOK AT THE CUE AT ALL scores 0.265.**

### ❌ AND MY OWN BRAIN-FIDELITY PREDICTION WAS REFUTED IN THE SAME RUN, BEFORE IT COULD BE QUOTED
I predicted the episodic collapse was us asking the WRONG ORGAN -- the dentate gyrus exists to make
similar inputs DISSIMILAR, so pattern separation is the enemy of generalisation, and the
consolidated semantic route should therefore do better. **IT DOES NOT. SEMANTIC IS 5x WORSE THAN
EPISODIC ON HELD-OUT CUES (0.005 vs 0.025), and raw co-occurrence counting beats it in BOTH
regimes, including at exact key (0.320 vs 0.165).** *The elegant story was wrong and its own
control killed it inside one run. Recorded because the reasoning will look attractive again.*

### 🎯 WHAT IT ACTUALLY CONVERGES ON, AND THIS IS THE VALUABLE PART
**Our "semantic profile" is a SUM of context bags, and it is beaten by literally counting the same
co-occurrences.** That is exactly the ORGAN A write-rule result -- summing raises interference,
single-occurrence beats the sum, and no unsupervised transform extracts substitutability --
**reached again end-to-end through the assembled substrate on a retrieval task, rather than on the
dissociation instrument.** *Two instruments, two tasks, two populations, one diagnosis: the
missing ingredient is the LEARNING SIGNAL, and assembling the organs did not supply it.*

**CAVEATS THAT TRAVEL WITH EVERY NUMBER ABOVE:** n=200, ONE corpus (children's fiction), ONE seed,
NO confidence interval and NO null yet -- that is what the Phase 2 cell is for. **And a named
selection bias: items are the FIRST content lemma of each sentence that the store has seen, which
skews toward frequent words and INFLATES both floors.** *It does not rescue the mechanism -- the
gap is ~10x, not marginal -- but the cell must select items without that bias.*

---

## 🔬 PHASE 2 IN PROGRESS -- THE ABLATION HARNESS EXISTS AND IT HAS ALREADY PAID FOR ITSELF

`Substrate(ablate=[...])` supports four one-organ-at-a-time ablations. **Smoke run, 400 sentences,
2 corpora, one seed -- OBSERVATIONS, NOT RESULTS: no CI, no null, n=1, and they are not to be
quoted as findings until the cell runs.** They already change what to build.

| ablation | what moved | reading |
|---|---|---|
| `episodic` (D3 off) | **ONLY its own counter** (3400 -> 0) | **I WIRED THE EPISODIC STORE AS A WRITE-ONLY SINK.** 3,400 encounters written, nothing reads them. Provenance, refusals, profiles all bit-identical. *This is MY wiring defect, not the organ's -- `hippocampal_encoder.retrieve` exists and I never call it.* **BUILD TARGET.** |
| `definitions` (R1 off) | **ONLY its own counter** (5 -> 0) | the `definition_map` handed to `checkpoint()` changed NOTHING about what grounded. **Under-powered on fiction (5 definitions in 400 sentences) -- re-run on SimpleWiki before concluding anything.** |
| `gap_detector` (H1 off) | **NOTHING AT ALL** | **AND IT IS UNINFORMATIVE, NOT A NULL -- READ THE NEXT BLOCK BEFORE QUOTING IT.** |
| `foraging` (H2 off, rate-matched) | 7 of 8 counters | **FROZEN reads the SAME 400 sentences and grounds 9 where the forager grounds 19.** It touches MORE lemmas (1,320 vs 1,137) and grounds FEWER -- spreading thinner, which is what MVT says foraging avoids. |

**⚠️ THE H1 ABLATION CANNOT SUCCEED AND MUST NOT BE FILED AS A NEGATIVE.** Verified rather than
assumed (`scratch/gapcache_values.py`): the real detector and a stub that always answers GAP agree
on **all 1,137 shared lemmas, zero disagreements**. The 19 lemmas the cache marks known are
**exactly the 19 grounded words**, written back by the consolidation path, not by the detector.
**But the foundation starts with 107 seed words and nothing else, so every content word in
children's fiction genuinely IS a gap. The detector is answering correctly; the question has one
true answer at this scale.** *Discipline 17's first clause: establish the experiment could have
succeeded before concluding anything from it.* **RE-TEST H1 AGAINST A POPULATED FOUNDATION.**

**AND TWO OF MY OWN CONTROLS WERE DEFECTIVE BEFORE THEY WERE FIXED, WHICH IS THE POINT OF RUNNING
CONTROLS ON CONTROLS:**
1. **The foraging twin was NOT rate-matched.** A fixed harvests-per-patch constant let FROZEN read
   **150 sentences against the forager's 400**, so every downstream difference was attributable to
   reading LESS rather than to choosing worse. **That is the unmatched-twin defect that killed four
   apparent wins in this project's own record, rebuilt from scratch by me.** Now splits the same
   budget across the same patches; both arms read exactly 400.
2. **Ablating H1 by setting `state.gap_detector = None` CRASHED** (`is_gap` calls `.familiarity()`
   unconditionally) -- and would have been the wrong control anyway, since removing the call
   changes the PATH rather than the ANSWER. Replaced by a stub with the interface intact and the
   discrimination removed.

---

## PHASE 2 -- THE RISK, AND IT IS THE MOST IMPORTANT STEP IN THIS PLAN

**EVERY ORGAN HERE WAS VALIDATED IN ISOLATION. WIRING TEN TOGETHER IS PRECISELY HOW THE 0-FOR-30
CLAIMS LAYER HAPPENED -- components that each look fine and produce nothing jointly.**

**THE DELIVERABLE IS ONE CELL: `experiments/exp_substrate_end_to_end_readout_v1.py`.**
Per CLAUDE.md this is `hdi_exp_dev`'s lane; if agent dispatch is unavailable in the running session,
author it in the main thread **with every gate below intact** -- the gates are the point, the lane
is not.

**The gates, and none is optional:**
- text in, traceable facts out, **on a corpus the mechanism did not see**;
- **a REAL floor run STANDALONE** -- the dumbest thing that scores well on this data. Run the
  STRONGEST floor the cell's own data supports, not the most convenient one. Report how many items
  each control actually removed: **a control that excludes nothing is not a control.**
- **a scramble twin** -- if scrambled text produces the same output, the pipeline is not reading;
- **CI half-width AND the null p95 beside every margin**, and gate on the FLOOR'S UPPER BOUND
  (floor + its own half-width), never its point value;
- **an ORGAN-ABLATION arm per wired organ** -- turn one off, re-run, report the delta. *This is the
  only thing that distinguishes an assembled substrate from an expensive `Counter`, and no cell in
  this archive has ever run it.*
- **and the first question, free and non-statistical: DID THE TEST ITEMS EXIST BEFORE THE MECHANISM
  DID?** State the answer in the metrics. That predictor beat every statistical signal in the audit.

**PRE-COMMIT THE READINGS BEFORE ANY NUMBER EXISTS:** (α) beats the floor CI-separated AND at least
one ablation degrades it -> the assembly is doing work, name which organ. (β) beats the floor but NO
ablation moves anything -> **the floor is what is scoring, the organs are decoration** -- report it
that way, do not soften it. (γ) does not beat the floor -> a real negative; go to the brain-fidelity
drill (discipline 17), and ask FIRST whether the experiment could have succeeded at all.

**This test does not currently exist. Nothing downstream should be trusted until it does.**

---

## PHASE 3 -- BUILD THE EMPTY SLOTS (this is where the real gain is)

Ranked. **The first is the only slot where the brain hands us a closed form and we wrote none of it.**

1. **D7 successor representation -- EQUATION FULLY PINNED: `M = (I - gamma*P)^-1`.** Highest
   value-per-effort in the document.
2. **Q2 domain-general inference -- EMPTY, and it is a WHOLE NETWORK.** `multi_hop`'s default
   `beta = n_dim` collapses its softmax to a Dirac delta (identical to argmax); its own code says
   two prior cells were confounded by this. **This explains `reasoner` matching a similarity
   baseline on 38 of 40 questions -- not a broken reasoner, a missing network.**
3. **P1/P2 answer production -- EMPTY.** `generation.py` returns codebook INDICES: no lemma stage,
   no morphology, no string. Its docstring admits its test regime "cannot fail by construction."
   **This is the slot the no-LLM invariant created and nobody wrote down.**
4. **D5 working memory -- EMPTY, and the filename is a trap.** `working_memory.py` is 116 lines of
   assertion guards, and it is LIVE.
5. F5 coherence monitor, F6 multi-sentence integration.
**NOT a build target: E4 discourse bridging** -- two measured nulls, one the owner's own mechanism,
CI-separated BELOW neighbour-copying.

**FREE LEAD, hypothesis-pending-VET:** `information_foraging.SurpriseSegmenter` (`:194-224`) is a
literal Event Segmentation Theory boundary detector **already built**, sitting in a module nobody
imports, never run on discourse. It fills the "no prediction-error segmentation" gap the organ map
lists as missing.

---

## ✅ MIDDLE_BAND MINED -- `tools/middle_band_miner.py`. TWO CORRECTIONS TO THIS PLAN'S OWN PREMISE.

**CORRECTION 1 -- THE POPULATION IS 580, NOT 117.** Enumerated by walking **all 8,148 result
directories** under `data/` (the 117 figure came from the index's `data/exp_*` scan; results also
live under `data/results`, `data/lambda_batch_results`, `data/skypilot_results` and ~60
`substrate_*` directories). **Meaning-relevant MIDDLE_BAND: 580. HARD_PASS: 1,359.**

**CORRECTION 2 -- AND IT IS THE ONE THAT MATTERS, BECAUSE THE OWNER AUTHORISED WORK ON THIS
RATIONALE. THE STATED MECHANISM IS NOT SUPPORTED.** This plan said MIDDLE_BAND "is where the
HONEST SELF-ASSESSMENTS went". Measured with the **IDENTICAL detector on both tiers** (same
directories, same fields, only the tier pattern differs -- a cross-tool comparison would have been
the very thing discipline 11 forbids):

| property | MIDDLE_BAND | HARD_PASS | |
|---|---|---|---|
| **states a limitation about itself** | **4.5%** | **3.0%** | **NO REAL DIFFERENCE -- the stated rationale fails** |
| carries a CI | 10.3% | 5.4% | MB nearly 2x |
| carries a floor | 76.4% | 69.2% | MB higher |
| carries a scramble | 24.1% | 19.5% | MB higher |
| carries a held-out split | 23.6% | 20.2% | MB higher |
| carries a null | 4.0% | 2.7% | no real difference |

**SO THE PREMISE IS HALF RIGHT AND THE HALF THAT SURVIVES IS NOT THE HALF WE ARGUED.** MIDDLE_BAND
IS modestly better-evidenced -- **twice as likely to carry a confidence interval** -- but **it is
NOT a population characterised by honest self-assessment: 4.5% is not a culture of caveats, it is
a rounding error, and HARD_PASS is at 3.0%.** *The mining stays worth doing on the evidence
gradient. The story we told about WHY must not be repeated.*

**THE READ LIST IS RANKED BY HOW MUCH MECHANISM IS IN THE CELL, and the top of it is substantive:**
`exp_bootstrap_passage_context_binding_fade_v4` (discourse-level passage-context binding under a
fairness lockdown), `exp_agreement_attractor_role_binding_cg_viability_v1` -- **whose own
`honest_scope` names its real discriminator and rejects the trivial one**: *"Beating nearest-noun
is trivial here... the HONEST discriminator is beating the FIRST-NOUN positional heuristic on the
subject-not-first subset"* -- and `exp_grounding_quality_readout_v1`, which opens its limitations
with ***"THIS CELL MEASURES NO QUALITY."*** *Those three are exactly the honesty the premise
predicted; the measurement says they are the 4.5%, not the norm.*

**NOTHING MINED HERE IS CITABLE.** `tools/vetting_ledger.py --cite` still governs and still
refuses every one of them.

---

## PARALLEL TRACK -- MINE MIDDLE_BAND (owner: "it's worth it")

**117 meaning-relevant cells, never read.** Owner's framing, and it changes the brief:
*"understanding what it was trying and the signal may be very important for the harder to obtain
capabilities."* **READ FOR THE ATTEMPT AND THE SIGNAL, NOT FOR THE VERDICT.**
**Why this population and not HARD_PASS: selecting on HARD_PASS SELECTED FOR OVER-CLAIMING.** Two
cells were found whose honest tier was MIDDLE_BAND while an over-claimed sibling took HARD_PASS.

---

## DEFERRED, WITH A TRIGGER

**Instrument rebuild.** Both bars carry CIs including chance (0.5431 CI [0.4922, 0.5953]; 0.5943 CI
[0.4937, 0.6911]); at n=242 the half-width (~0.05) is as large as the whole chance-to-bar interval
(~0.04). **Nothing in Phases 0-3 uses it.** **TRIGGER: rebuild before the next GATED WORD-MEANING
experiment.**
***AND THE DEEPER POINT, WORTH MORE THAN THE POWER FIX: PREFER TASKS WITH LARGE EFFECT SIZES OVER
BUYING POWER ON A TASK WITH A TINY ONE.*** When a mechanism genuinely works you see pattern
completion **0.20 -> 0.92**, or **leave@3 vs leave@8 on an identical patch**. No CI needed. A whole
day of gated word-meaning arms fought over **0.63 vs 0.55** -- that gap is the problem, not n.

---

## STANDING RULES THAT MUST SURVIVE COMPACTION

- **`tools/substrate_query.sh` RETURNS ZERO BYTES AND EXITS 0.** Use `tools/experiment_index.py`,
  which prints rows scanned BEFORE results.
- **A HARD_PASS is an UNVERIFIED CLAIM** (30 vetted, 1 upheld). Check `tools/vetting_ledger.py
  --cite NAME` before citing anything.
- **The organ layer is a DIFFERENT population** -- 163/163 import, 83/87 self-tests pass. Do not
  import the claims base rate into it.
- **AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NEVER A SEARCH.** Four of my errors this session were
  this one fault.
- **ASK WHAT THE OPERATOR INTENDED BEFORE NAMING SOMETHING A DEFECT.** The remote is idle BY INTENT;
  results were deliberately SSH'd back. I called both defects.
- Never bundle a deletion with real work. Never `git add -A`. `data/foundation/` is READ-ONLY, one
  disk, no backup. Origin push needs USER AUTH.
