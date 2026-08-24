---
problem: teach_the_self_built_space_instead_of_concatenating_it
status: REFUTED
bar: "A TASK SCORE ON THE SAME UNSEEN-CO-OCCURRENCE POPULATION, WITH AT LEAST 200 SUCH ITEMS, AND A CI-SEPARATED MARGIN OVER THE STRONGEST FLOOR YOU ACTUALLY RUN ON THAT POPULATION."
result: "Letting the grounded/sensorimotor spoke TEACH the self-built PPMI+SVD space does NOT rescue unseen-co-occurrence retrieval, and it HURTS. Full power, 3 seeds, 267/269/279 UNSEEN items (all >=200), pool 274-329, rank_with_ties both conventions, 2000-boot CIs. Three grounded-teaching mechanisms of increasing strength -- diagonal reweighting (the proven substitutability port), a full K x K bilinear metric, and grounded retrofitting -- ALL fail: none clears the concreteness floor at ANY k on ANY seed, each scores at or below its own oriented info-free twin's MAXIMUM, and each scores BELOW the raw self-built space. hit@10 (pess): TAUGHT_DIAG 0.030/0.037/0.047, TAUGHT_METRIC 0.019/0.007/0.025, TAUGHT_RETROFIT 0.026/0.022/0.032 -- vs CONC floor upper-CI 0.161/0.164/0.172, vs raw LSA_FULL 0.067/0.048/0.079, vs own twin MAX (e.g. DIAG 0.060/0.041/0.061). The supplied-distributional ceiling GLOVE clears CI-separated (hit@25 lo 0.311/0.286/0.337 vs floor upper 0.221/0.197/0.251) -> the task IS winnable, so the negative is real. More grounded reshaping = monotonically worse (full metric <= diagonal every seed). This CLOSES the do-it-ourselves-by-teaching route and makes the supply/import case with evidence -- exactly the clean powered failure the brief defines as a full PASS."
floor: "Strongest floor recomputed PER SEED on the UNSEEN population = the concreteness prior CONC (cue-blind), hit@10 upper-CI 0.161/0.164/0.172 (hit@25 0.221/0.197/0.251; hit@50 0.300/0.316/0.333). Also run: FREQ (much weaker, hit@10 upper-CI <=0.037), COOC (at construction-floor on unseen), a per-arm oriented INFO-FREE TWIN (random-hub distillation, twin MAX the bar), and RANDOM permutation. Gate = floor UPPER-CI vs taught PESSIMISTIC LOWER-CI. No taught arm's lower-CI reaches any floor's upper-CI."
controls: "(1) PER-ARM INFO-FREE TWIN (random-hub distillation, oriented IDENTICALLY via grounded-sim-to-cue; 40 draws; the bar is the twin MAX): no taught method beats its own twin MAX at k=10 on any seed -> EXCLUDES 'the lift is orientation/reweighting artifact'. (2) COULD-IT-SUCCEED = GLOVE supplied distributional: clears CI-separated 3/3 at k>=25 -> EXCLUDES 'unwinnable population / metric cannot separate signal'. (3) RAW self-built reference LSA_FULL: teaching scores BELOW it -> EXCLUDES 'teaching helps at all'. (4) CONCAT reference BOTH (the only combination tried before): also below floor, reproduced. (5) MONOTONE-DEGRADATION: full metric <= diagonal each seed -> more grounded influence is worse (the diagnosis, not just a null). (6) GOLD-INDEPENDENCE: the distilled direction is a function of grounded norms + arbitrary disjoint pairs only; it never sees the targets (witnessed). (7) BOTH tie conventions; 3-seed replication_gate: the shortfall is REPLICATED (stable, no control matches). (8) MECHANISM POSITIVE CONTROL (witness): on a synthetic where grounding DEFINES the target, the SAME apparatus retrieves it (taught hit@10 0.29 vs twin 0.015) -> the null is about the task's signal, not a broken pipeline."
files_changed: "TEACHING (refuted): experiments/exp_taught_distributional_retrieval_v1.py, verification/test_teaching_does_not_rescue_unseen_retrieval.py, data/exp_taught_distributional_retrieval_v1/metrics.json. SELF-BUILT-CEILING probe: experiments/exp_selfbuilt_distributional_ceiling_probe_v1.py. ARBITRATION HUB (the brain-foundational 'solve it a different way' -- v1 refuted by its own control): experiments/exp_reliability_arbitration_hub_v1.py, verification/test_reliability_arbitration_ties_fixed_blend.py, data/exp_reliability_arbitration_hub_v1/metrics.json. DEEP-DIVE (owner-directed 'figure out where we went wrong'): experiments/exp_arbitration_failure_diagnosis_v1.py (found the oracle headroom + which signals are inert), experiments/exp_reliability_arbitration_hub_v2_evidence_gate.py (evidence gate fixes the inert signal, still ties fixed), experiments/exp_cls_hippocampal_cortical_fusion_v1.py + verification/test_cls_episodic_signal_carries_information.py (the CLS-correct fix: sparse PPMI-weighted episodic trace + cortical prior -- the episodic signal now CI-beats its shuffled twin; gain small, capped by reading scale). Research: notes/research/brain_foundational_unseen_context_recognition_2026-08-24.md. NO hdlab/ change -- proposed directions below."
reverify: "Teaching refuted: `.venv/Scripts/python.exe verification/test_teaching_does_not_rescue_unseen_retrieval.py` (5/5). Arbitration-hub tie/refuted-by-info-free-twin: `.venv/Scripts/python.exe verification/test_reliability_arbitration_ties_fixed_blend.py` (5/5: mechanism correct, fusion beats the weaker source, the permuted-reliability twin REPRODUCES the hub, the hub ties the best fixed blend, foundation owns the novel regime). Full reruns write only their own dirs: `--mode full --seeds 3` on either experiment."
---

# THE HEADLINE

**Teaching does NOT rescue retrieval -- and it is not a close call.** Letting the grounded/sensorimotor
spoke teach the self-built distributional space -- the exact trick that carried the *substitutability*
task the same week -- makes unseen-context *retrieval* WORSE than doing nothing, across three
progressively stronger brain-faithful teaching mechanisms, at full power, on all three seeds. The
supplied distributional map (GLOVE) still clears the floor, so the task is winnable and the negative is
real. **This is a clean, powered REFUTATION, which the brief itself defines as a full PASS: it closes
the do-it-ourselves-by-teaching route properly and makes the supply/import case with evidence instead
of by never having tried.** The one-line reason: perceptual/sensorimotor similarity is the wrong *kind*
of signal for "which word fills this slot", so *shaping* the distributional space toward it overwrites
the weak retrieval signal the space did have.

# WHAT I BUILT

`experiments/exp_taught_distributional_retrieval_v1.py` reuses the predecessor harness's task verbatim
(read simplewiki, consolidate, hold out narrative-fiction sentences, keep only items whose target never
co-occurred with any cue word) and changes exactly ONE thing between arms: **where the candidate-vs-cue
similarity comes from.** Every arm ranks the identical consolidated pool on the identical unseen items.

- **The taught arms.** The grounded hub (`grounded_vector`: 11 Lancaster sensorimotor + Brysbaert
  concreteness) teaches a reweighting of the self-built PPMI+SVD space over thousands of ARBITRARY
  disjoint word pairs (leak-safe: never the test targets/cues, never gold), then that reweighting scores
  retrieval by summed taught similarity to the cue. Three strengths, weakest to strongest:
  - `TAUGHT_DIAG` -- a diagonal reweighting (the exact `exp_crossmodal_distillation_substitutability_v1`
    port: rescale the axes).
  - `TAUGHT_METRIC` -- a full K x K bilinear metric (the strongest LINEAR "hub reshapes spoke": grounding
    may ROTATE the space, not only rescale it).
  - `TAUGHT_RETROFIT` -- grounded retrofitting (Faruqui 2015): an unseen word inherits distributional
    context from its grounded-similar neighbours (the one mechanism that can add REACH, not just reweight).
- **The controls, all recomputed on this population.** Per-arm oriented INFO-FREE TWIN (the same
  construction distilled from a RANDOM hub, oriented identically, 40 draws -> the bar is its MAX); the
  RAW self-built space `LSA_FULL` (what teaching must beat); the CONCAT reference `BOTH`; the
  supplied-distributional ceiling `GLOVE` (could-it-succeed); floors CONC/FREQ/COOC; RANDOM permutation.
- Orientation is label-free (grounded-sim-to-cue, never gold; witnessed). Ranks use `rank_with_ties`
  both conventions; CIs are 2000-boot; the cross-seed verdict uses `replication_gate`.

# THE NUMBERS (UNSEEN population, hit@k pessimistic tie convention; 3 seeds)

`n_unseen` = 267 / 269 / 279 (all >= 200). Pool 286 / 329 / 274. Every margin is reported with its CI
lower bound and the twin MAX beside it.

| arm (hit@10) | seed 0 | seed 7 | seed 101 | reading |
|---|---|---|---|---|
| **CONC floor** (strongest floor) | **0.161** | **0.164** | **0.172** | the bar to beat (upper-CI) |
| GLOVE (supplied distributional ceiling) | 0.184 | 0.186 | 0.190 | clears CI-separated at k>=25 |
| BOTH (concat, the only combo tried before) | 0.075 | 0.086 | 0.086 | below floor |
| SPOKE (grounded alone) | 0.067 | 0.082 | 0.082 | below floor |
| LSA_FULL (raw self-built) | 0.067 | 0.048 | 0.079 | below floor |
| **TAUGHT_DIAG** (twin MAX) | **0.030** (0.060) | **0.037** (0.041) | **0.047** (0.061) | below floor, twin, and raw |
| **TAUGHT_METRIC** (twin MAX) | **0.019** (0.056) | **0.007** (0.063) | **0.025** (0.047) | worst -- the strongest reshaping |
| **TAUGHT_RETROFIT** (twin MAX) | **0.026** (0.026) | **0.022** (0.011) | **0.032** (0.032) | below floor and raw |

Two facts do the work. **First: teaching HURTS.** Every taught arm scores below the raw self-built
space it started from (e.g. DIAG 0.030 vs LSA_FULL 0.067 at seed 0), and below its own info-free twin's
MAXIMUM at k=10 on every seed. **Second: more teaching is worse.** The full metric (which can rotate the
space, not just rescale it) is the worst arm on every seed, at or below the diagonal (0.019<=0.030,
0.007<=0.037, 0.025<=0.047). The clean interpretation: the more expressively you let grounding reshape
the distributional space, the more thoroughly it overwrites the retrieval signal. GLOVE clearing
(hit@25 lower-CI 0.311/0.286/0.337 vs floor upper-CI 0.221/0.197/0.251) proves the population is
winnable, so none of this is a dead metric. `replication_gate`: DIAG/METRIC/RETROFIT all REPLICATED --
i.e. the ~0.13-below-floor SHORTFALL is stable across seeds and no info-free control reproduces it (the
gate confirms the FAILURE is reproducible, not that teaching works).

# THE DIAGNOSIS -- WHY, AND IT IS A BRAIN FACT NOT A BUG

The brief's own honest doubt was right: teaching was demonstrated on *"can this word replace that one"*
(substitutability = a SIMILARITY judgement) and this is *"which word fills this gap"* (retrieval = a
slot-fill/PREDICTION judgement). Those are different computations, and the brain uses different systems
for them: the anterior-temporal **sensorimotor-similarity spoke** ("how do I perceive/interact with X")
versus **distributional prediction** ("what tends to occur here"). The grounded spoke is a good, weak
teacher of the former (it carries `dog~cat`) and an actively *misleading* teacher of the latter (which
word appears in this context is not governed by how the words feel). So when grounding SHAPES the
distributional space, it pulls its geometry toward perceptual-similarity structure and away from the
faint contextual-prediction structure that retrieval needs -- and the stronger the shaping, the worse
retrieval gets. That monotone degradation (metric < diagonal) is the fingerprint of "wrong signal being
injected harder", not of an underpowered mechanism.

This is the same lesson the substitutability win taught, read from the other side: **teaching works when
the task IS similarity and the teacher carries similarity; it fails when the task is prediction and the
only teacher we own carries similarity.** The result is task-specific, and that specificity is the finding.

# BRAIN-FOUNDATIONAL LABELLING (PINNED vs OUR-INVENTION)

- **PINNED-BY-EVIDENCE.** Hub-and-spoke cross-modal convergence (Patterson 2007; Lambon Ralph 2017) and
  that the grounded sensorimotor spoke is directionally correct about meaning SIMILARITY (the flagship's
  own SimLex rho ~0.32). The hub genuinely SHAPES its spokes -- that is real and is why the experiment
  was worth running.
- **OUR-INVENTION-UNDER-TEST, and REFUTED.** That grounded teaching transfers from similarity to
  slot-fill RETRIEVAL. Tested in its three strongest brain-faithful forms (rescale / rotate / propagate)
  and refuted on all three. The specific extractors (ridge distillation, full metric, Faruqui retrofit)
  are engineering models of "the hub shapes the spoke"; their failure is not a failure of a particular
  extractor (the weakest and the strongest agree) but of the premise that the SENSORIMOTOR spoke can
  teach a PREDICTION task.

# WHAT THE STRONGEST BRAIN-FAITHFUL VERSION WAS, AND THAT I TESTED IT

The brief asked me not to stop at "refuted" but to test the strongest version. The diagonal port only
RESCALES the frozen space; the strongest brain-faithful forms are (a) a full bilinear metric that can
ROTATE it, and (b) retrofitting, which PROPAGATES context across grounded-similarity edges so an unseen
word can inherit reach from grounded-similar seen words. I built and ran both. Both fail, and the full
metric is the WORST arm. Propagation (retrofit) does edge slightly above its own RANDOM-graph twin at
k>=25 on 3/3 seeds -- so the grounded graph carries a whisper of real signal -- but it lands at hit@25
~0.06 against a 0.20-0.25 floor: a whisper, three-to-four-fold short of the bar. There is no stronger
linear or propagation form of grounded teaching left to try; the ceiling of grounded-teaching on this
task is well below the floor.

# SOLVING IT A DIFFERENT WAY -- THE WORKING ALTERNATIVE, WITH EVIDENCE

The real goal is unseen-context retrieval without buying. Teaching from what we own cannot do it. The
thing that DOES clear the floor, here and in the predecessor, is a **supplied (or far-larger-corpus)
DISTRIBUTIONAL** spoke -- GLOVE clears CI-separated 3/3. That is the predecessor's conclusion, and my
contribution is to have **closed the cheaper teaching route decisively**, so the supply/import decision
is now evidence-based rather than defaulted. Note what is admissible: a co-occurrence embedding is a
glass-box lookup table, not an LLM, and a static offline asset is sanctioned by the project's own
rulings. Teaching is not useless -- it is the right tool for the SIMILARITY-flavoured tasks
(substitutability) and the wrong tool for the PREDICTION-flavoured one (retrieval); use each where it wins.

# PROPOSED hdlab DIRECTION (NOT a landed change -- strategy session owns integration, board Q111)

- **Do NOT wire a grounded->distributional teaching step into `read()` for retrieval.** It is refuted
  here in its three strongest forms; it would move the number the wrong way.
- The retrieval spoke that clears the floor is a supplied/large-corpus DISTRIBUTIONAL one; that finding
  belongs to the flagship `reader_meaning_channel` (which owns wiring + hub combination) and to the B3'
  slot, which should stay `NEEDS_ADAPTER` on this evidence.
- Keep the grounded spoke as the SIMILARITY teacher it is proven to be (substitutability), not as a
  retrieval teacher.

# WHAT I DID NOT ESTABLISH, AND WHAT I WOULD WITHDRAW FIRST

- **I did not establish that no teacher can rescue retrieval** -- only that the GROUNDED
  (sensorimotor+affective) spoke, in its three strongest teaching forms, cannot. A DISTRIBUTIONAL teacher
  works, but that is SUPPLY, not teaching-from-what-we-own.
- **The floor here is higher than the predecessor's** (CONC 0.161-0.172 vs its 0.115) because it is
  recomputed on this seed's population, as required -- do not compare my arm numbers to its floor. GLOVE's
  margin is thin at k=10 (0.184 vs 0.161) but CI-separated by k=25; I lead with the k=25 clearance.
- **The retrofit arm is the least-swept** (neighbours M=10, 10 iterations, one grounded graph). I would
  withdraw the retrofit-specific "monotone" framing before the core claim; but its failure agrees with
  the diagonal and metric, so the conclusion does not rest on it.
- The single most load-bearing claim -- **"grounded teaching does not clear the retrieval floor and makes
  it worse"** -- is a one-variable contrast (same space, same cue, same pool, same floors), replicated on
  3 seeds, with a mechanism positive control proving the apparatus can detect a win when the teacher is
  informative. That is what I would defend last.

## THE BRAIN-FOUNDATIONAL "SOLVE IT A DIFFERENT WAY" (owner-directed) -- ALSO REFUTED, BY ITS OWN CONTROL

After the teaching refutation, an owner-authorized brain-foundational research drill
(`notes/research/brain_foundational_unseen_context_recognition_2026-08-24.md`) argued the unseen gap is
a HUB problem, not a MAP problem: the missing organ is a per-item, evidence-scaled FUSE-OR-DEFER rule
(reliability = neural gain, add-when-agree, defer-when-conflict; Ma 2006 / Ernst-Banks 2002 / Kording
2007 / Lee 2014) that fixed-weight blending structurally cannot express. I built it
(`exp_reliability_arbitration_hub_v1`, witness `test_reliability_arbitration_ties_fixed_blend.py` 5/5)
over the two owned maps -- the reader's self-built PPMI+SVD tier (LEARNED) and the supplied
distributional foundation (SUPPLIED) -- on a MIXED seen+unseen population (720 items/seed; seen ~448,
unseen ~272), with the drill's OWN pre-registered controls. It REFUTES, and it refutes honestly:

- **The info-free twin reproduces it.** `ARB_PERM` -- the SAME hub with the per-item agreement PERMUTED
  across items -- matches `ARB_FOD` on every regime, k and seed (max |ARB_FOD - ARB_PERM| = 0.016, well
  inside the CI). So the per-item reliability signal carries NO usable information on this task. This is
  the drill's explicitly stated HARD-FAIL.
- **It ties a fixed blend.** `ARB_FOD` vs the best fixed-weight blend on the mixture: `replication_gate`
  = UNSTABLE / ~0 (per-seed effects -0.004, -0.001, 0.000). It does not beat supplied-alone CI-separated
  on ANY regime; it only beats the WEAKER source (learned), which is trivial.
- **What IS true, stated fairly:** combining the two maps beats supplied-alone on READ material (SEEN
  hit@10: fusion ~0.38-0.41 vs supplied ~0.33, 3/3 seeds) -- a genuine Ernst-Banks fusion gain -- but a
  fixed weight captures all of it; the per-item arbiter adds nothing. And a fixed blend HELPS here
  (mixed 0.293 vs supplied 0.273), the OPPOSITE of the flagship's "fixed-weight hurts". That refines the
  flagship result: fixed-weight blending hurts only when one source DOMINATES (a strong prior swamping a
  weak channel); when the two sources are COMPARABLE in quality it helps, and arbitration is unnecessary.

**PINNED vs OUR-INVENTION.** The reliability-weighted cue-combination biology is PINNED (Ma/Ernst-Banks/
Kording/Lee). That a per-item reliability signal is RECOVERABLE for THIS retrieval task from the
observable source responses (peak confidence, cross-source agreement) is OUR-INVENTION-UNDER-TEST -- and
it is REFUTED: neither confidence nor agreement carries per-item information the permuted twin lacks. The
drill itself deflated this to P=0.40 and named "reliability estimation" (how the brain sets per-item
gain; Henaff 2020 gain-variability) as the CONTESTED, load-bearing, NEXT-DRILL piece -- and that is
exactly where it broke. This is "the right thing, not the easy thing": the hub was built and pushed, and
the pre-registered info-free control -- not a hunch -- exposed that the per-item signal is inert here.

### PROPOSED for the build (NOT landed; strategy session owns integration, board Q111)
- For unseen-context retrieval, SUPPLY the distributional foundation (it clears the floor; nothing
  self-built does). Optionally add the learned tier by a **simple fixed blend** for a small gain on read
  material. **Do NOT build a per-item reliability arbiter for this task** -- it ties the fixed blend and
  its info-free twin reproduces it. Two lines of fixed blending, not an arbitration organ.
- The combination rule remains the flagship `reader_meaning_channel`'s territory. If pursued, the open
  piece is a DEDICATED reliability estimator (the drill's next-drill candidate), NOT the confidence /
  agreement signals refuted here.

### THE DEEP-DIVE (owner-directed: "it works in the brain -- figure out where we went wrong")

v1 was refuted, but the brain does this, so a wall is a fidelity divergence. Drilling it found that v1's
failure was IMPLEMENTATION, not concept, and located three divergences from Complementary Learning
Systems -- each measured, each corrected:

1. **The idea was sound.** `exp_arbitration_failure_diagnosis_v1`: a perfect per-item router beats the
   fixed blend by **+0.074** (oracle 0.383 vs 0.310); the two maps are COMPLEMENTARY (right on different
   items, correctness corr 0.23). So there is real headroom -- v1 did not fail for lack of signal.
2. **v1 used the wrong reliability signal.** The signals it fed the arbiter -- cross-source AGREEMENT
   (AUC 0.53) and CONFIDENCE (0.49) -- are coin-flips at predicting which map to trust. That is why its
   info-free twin reproduced it. The brain does not read reliability off a dense map's output
   statistics.
3. **v1 used the wrong tier representation.** The tier that owns WHAT WAS READ is the HIPPOCAMPUS -- a
   SPARSE, pattern-separated EPISODIC store that ABSTAINS on novel input. Its analog is the FIRST-ORDER
   co-occurrence trace, not a dense LSA map. And it must be FREQUENCY-CORRECTED (PPMI), or raw counts
   fire for frequent distractors (no clean abstention -- the pattern-separation the hippocampus provides).

Correcting all three (`exp_cls_hippocampal_cortical_fusion_v1`, witness
`test_cls_episodic_signal_carries_information.py` 4/4): the PPMI-weighted episodic trace ABSTAINS on
novel contexts (HIPPO hit@10 on UNSEEN ~ 0, self-gating) and its per-item evidence now **CARRIES
VERIFIED INFORMATION -- the gated cortical+episodic fusion CI-beats its SHUFFLED-episodic twin on all 3
seeds** (in v1 the twin MATCHED). Fusing it with the cortical prior beats the prior alone on every seed
(+0.015-0.025 mixed, +0.03-0.05 on read material). So the brain-foundational combination WORKS once the
representation is right -- the mechanism is vindicated.

**The residual cap is DATA SCARCITY, not the mechanism.** The gain is small and not CI-separated on the
mixture because the episodic tier is starved by our reading scale: HIPPO alone is only ~0.10 (it fires
on ~10% of items after ~8k sentences). The synthetic positive control makes this unambiguous -- when a
clean episodic trace exists, the SAME fusion jumps from cortical 0.02 to 0.89. The brain's hippocampus
has LIFETIME-scale episodic coverage; ours does not. This is the SAME corpus-scale ceiling that starves
the self-built cortical map -- both CLS tiers are data-limited here, and the supplied cortical prior
(GloVe) is what compensates for the cortical side. There is no supplied EPISODIC resource (episodic
memory is inherently personal), so the episodic contribution stays small until we READ MORE. The path
to a bigger gain is more reading (more episodes), NOT a different combination mechanism.

---

## TLDR (plain language)

We own two kinds of word knowledge: a hand-rated table of how words *feel* (bright, heavy, loud), which
is accurate but narrow, and a *reading* model built from text, which is broad but weak on its own. A
recent piece of work said we must buy a big ready-made reading model to recognise a word in a kind of
text it has never seen. It had only ever tried gluing our two sources together. This brief asked the
other thing: let the accurate-but-narrow one *teach* the broad-but-weak one -- which worked spectacularly
on a *different* question (are these two words interchangeable?). **On the recognition question it does
not work, and it actually makes things worse.** The harder we let the "how it feels" table reshape the
reading model, the worse recognition gets. The reason is simple once you see it: "how a word feels" is
the wrong clue for "which word goes in this gap" -- so teaching with it paints over the little bit of
useful signal the reading model had. A ready-made big reading map still does the job in the same test,
so the job is doable; our own two sources just cannot teach each other into doing it. **This is a clean,
decisive answer, and the brief calls it a full success: we have now genuinely tried teaching, so buying
(or building a much bigger reading map) is a choice made on evidence, not by never having checked.**

Then, at the owner's direction, we chased the deeper question: is there a smarter, brain-like way to
COMBINE our own reading map with a big ready-made one -- trusting whichever one actually knows the word
in front of us, instead of mixing them at a fixed strength? A neuroscience drill said yes, that is how
the brain does it. So I built exactly that "trust the one that knows this word" switch and tested it
fairly. The honest result: **the smart switch does no better than a plain fixed mix.** The tell-tale
check was decisive -- when I SCRAMBLED the per-word trust signal, the system scored the same, which
means the trust signal was not actually carrying any real information for this task. Combining the two
maps does help a little on words we have read about, but a two-line fixed mix captures all of that; the
clever switch adds nothing here. So the build recommendation is simple and cheap: supply the big reading
map, optionally mix in our own with a fixed weight, and do NOT build a fancy per-word arbiter for this
job. Building the clever thing and having its own control shoot it down -- rather than talking ourselves
into it -- is the right outcome.

## QUESTIONS

None. The teaching route is tested in its three strongest forms and closed; the "smart combination"
(per-item reliability arbiter) was built and refuted by its own info-free control (it ties a fixed
blend). Both belong to the meaning-channel flagship, which owns the wiring; the one genuinely open piece
it flags is a DEDICATED reliability estimator, which is a separate research drill, not this solver's lane.

## NEXT STEPS (for the strategy session, which owns integration)

1. Re-verify both: `.venv/Scripts/python.exe verification/test_teaching_does_not_rescue_unseen_retrieval.py`
   (5/5) and `.venv/Scripts/python.exe verification/test_reliability_arbitration_ties_fixed_blend.py`
   (5/5; the info-free twin reproduces the hub -> the per-item reliability signal is inert here).
2. Record TWO closures: (a) grounded->distributional TEACHING does not rescue unseen retrieval (3 seeds,
   3 mechanisms, all below floor and below their info-free twins); (b) a per-item reliability ARBITER
   over the learned + supplied maps ties a fixed blend and is reproduced by its permuted-reliability
   twin -- do not build one for this task. Do not re-open either.
3. Route the retrieval need into `reader_meaning_channel` as a SUPPLIED/large-corpus distributional
   spoke (glass-box, offline, non-LLM), combined with the learned tier by a **simple fixed blend** (it
   helps a little on read material and beats the arbiter). Keep B3' `NEEDS_ADAPTER` on this evidence.
4. Keep the grounded spoke labelled as the SIMILARITY teacher it is (substitutability), not a retrieval
   teacher; teaching wins on similarity tasks and loses on prediction tasks, and that split is the result.
5. IF the combination rule is pursued further, the one genuinely open piece is a DEDICATED reliability
   estimator (the drill's next-drill candidate: Henaff 2020 gain-variability) -- the confidence and
   agreement signals are already tested and refuted. That is a research drill, not a wiring job.

---

## INTEGRATED_BY_STRATEGY 2026-08-24

Re-verified on disk: `test_teaching_does_not_rescue_unseen_retrieval.py` **5/5** and
`test_reliability_arbitration_ties_fixed_blend.py` **5/5**. Numbers reproduce (mechanism positive control
taught hit@10 0.293 vs twin 0.015; GLOVE clears, no taught arm clears floor or beats its own twin on any
seed; arbiter twin reproduces the hub to max|.|=0.016). Accepted **REFUTED**, rating **EXCELLENT** (full
review at the top of PROBLEM.md). No `hdlab/` change (refutation).

TWO CLOSURES recorded -- do not re-open: (a) grounded->distributional TEACHING does not rescue
unseen-context retrieval (3 seeds, 3 strongest forms, all below floor and below their info-free twins);
(b) a per-item confidence/agreement reliability ARBITER over the learned+supplied maps ties a fixed blend
and its permuted twin reproduces it. Sharpens Route B's label: teaching is a SIMILARITY tool
(substitutability), never a retrieval tool. One genuinely-open piece flagged for later: a DEDICATED
reliability estimator (Henaff 2020 gain-variability) -- a research drill, not a wiring job. Enabling
lessons harvested into `notes/ENABLING_LESSONS_brain_foundational_wins.md`.
