---
problem: the_sign_quantiser_makes_the_substrate_an_averaging_machine
status: PARTIAL
bar: "On a REAL downstream task (open-vocabulary read-out hit@1, or the meaning/recall instrument -- NOT a bare 2AFC), on a held-out population with all floors recomputed on it: the graded (non-`sign`) path must beat the `sign`'d path CI-separated over the strongest floor's UPPER bound (include the constant/prototype floor), info-free twin LOSING, with the CI half-width and null p95 reported beside the margin. Sweep WHICH sites are made graded (the whole point is to find where strength matters) and report the capacity cost (does superposition collapse below B=4?)."
result: "On the C3 open-vocab hit@1 instrument (n=4000 items, 5491 anchors, argmax over the whole anchor field vs generous WordNet gold): graded vs sign = +0.0015 CI[-0.0055,+0.0083] NULL (ci_hw 0.0069, null_p95 0.0068). The best faithful code-format arm (divisive normalisation = anchor-field centering, DN_CENTER) = 0.0537 vs sign 0.0465, +0.0073 CI[+0.0000,+0.0145] (ci_hw 0.0073, null_p95 0.0072 -- WITHIN NOISE, seed-flips), twin loses robustly. The ENTIRE brain-faithful code-format family (sign, graded, divisive-norm read-out center/z/CH, IDF composition, in-place sparse, DG expansive-sparse 2->2048 k-WTA) lands 0.029-0.062 -- ALL 0.09-0.14 CI-BELOW the best-constant averaging floor 0.171. DECISIVE (drilled finer): a SELF-SUPERVISED brain-faithful predictive learner (from-scratch CBOW-NS: predict the masked word, online delta-rule, co-learned representation) lands at 0.0428, ~= the co-occurrence cosine 0.0480 (delta -0.0053, CI incl 0) -- exactly as Levy&Goldberg 2014 predict (CBOW-NS implicitly factorises shifted PMI, so it carries the SAME distributional information as the cosine). It only beats its info-free twin (+0.0333 CI-sep), i.e. weak-but-real, and is 0.096 CI-BELOW the prototype floor. The ONLY arm that exceeded the ceiling -- a linear associator at held-out 0.1081 (+0.0618 vs cosine) -- was SUPERVISED on WordNet-derived gold-anchor labels; the brain gets no such labels from reading. So NO unsupervised method (counting, graded, divisive-norm, sparse, DG-expand, or a faithful self-supervised learner) beats the averaging floor; only supplied-answer supervision does. FINER DRILLS then reframed it: on WordNet-INDEPENDENT human ratings the unsupervised distribution DOES carry meaning -- it captures RELATEDNESS (WordSim rho 0.25, twin-loses) though NOT SIMILARITY (SimLex 0.04); GROUNDING captures both and best (0.42/0.21); the SIMILARITY axis the WordNet instrument demands is recovered by brain-faithful STRUCTURE (narrow ordered context: SimLex 0.075->0.112) not by any read-out format. So on the READ-OUT the averaging machine is a measurement-axis + structure/grounding + semantic-control matter, never the sign(). BUT in the BINDING/SUPERPOSITION regime the sign() IS a real averaging machine: recovering B bound role-filler pairs from a bundle (MAP-VSA, 512-filler cleanup, 300 trials, d=256), GRADED beats SIGN by a CI-separated and GROWING margin for CORRELATED fillers (B6 0.98 vs 0.73; B8 0.88 vs 0.58; B12 0.67 vs 0.36), raising the capacity cliff from B*=8 to B*=12 (mean gap CORRELATED +0.146 vs RANDOM +0.080). So the brief is HALF right: sign() is not the read-out bottleneck but IS a superposition-capacity lever for correlated bound codes -- flip it at the binding sites, not the read-out."
floor: "BEST_CONSTANT (always name the single highest-gold-degree anchor, 'change') = 0.1710, d-independent -- the strongest averaging/prototype strategy. Also: nearest-centroid PROTOTYPE 0.1388 ('work', brittle -- flips to 0.0 at d=1024 by identity change, do not lean on it), POPULARITY 0.0185, SCRAMBLE(info-free) 0.008, RANDOM 0.0101. Every code-format read-out arm is CI-separated BELOW 0.171; the learned associator (0.108) closes ~2/3 of the gap but is still CI-below it."
controls: "info-free twin (deranged donor query) -- every arm's real hit@1 >> its scramble (0.008) CI-separated, so the read-out carries real per-item signal, and the twin does NOT reproduce the divisive-norm gain (excludes item-difficulty/base-rate). best-constant + nearest-centroid-prototype + popularity + random floors, all recomputed on this population. d-sweep 256->1024 separates FORMAT from CAPACITY. byte-identity self-test: equal-weight composition builder == context_vector_masked (IDF arm differs ONLY by weight). learned-associator probe: 50/50 train/test split (no leak), held-out eval. DRILL controls: Spearman rho on WordNet-INDEPENDENT human ratings with a frequency-product floor (~0) and shuffled-vector twins (~0); rho on the common intersection of pairs all reps cover (fair head-to-head); context-window is the ONLY variable in the structure drill. BINDING controls: shuffle-bundle info-free floor at chance (1/512); RANDOM-vs-CORRELATED filler conditions isolate the correlation effect; bootstrap CI on the graded-minus-sign gap at each B; self-test (B=1 inverts exactly, shuffle->chance, capacity degrades with load)."
files_changed: "experiments/exp_divisive_normalisation_readout_v1.py (format sweep: sign/graded/divnorm/IDF/sparse/DG-expand + floors + twin + d-sweep), experiments/exp_learned_readout_probe_v1.py (SUPERVISED linear-associator probe), experiments/exp_predictive_learner_readout_v1.py (SELF-SUPERVISED brain-faithful CBOW learner), experiments/exp_taxonomic_vs_thematic_gold_v1.py (DRILL 1+2: reps vs human relatedness/similarity + grounding + fusion), experiments/exp_structured_context_similarity_v1.py (DRILL 4: context-window sweep recovers similarity), experiments/exp_superposition_capacity_binding_v1.py (DRILL 5: sign-vs-graded superposition capacity, random vs correlated bound codes), experiments/exp_live_binding_load_signgap_v1.py (LIVE VERIFICATION: real StructuralEncoder load B, filler correlation, atomic-vs-semantic sign gap), verification/test_sign_quantiser_not_the_bottleneck_on_hit1.py (scaffold-free witness), data/exp_divisive_normalisation_readout_v1{,_idf,_d1024}/metrics.json, data/exp_learned_readout_probe_v1/metrics.json, data/exp_predictive_learner_readout_v1/metrics.json, data/exp_taxonomic_vs_thematic_gold_v1/metrics.json, data/exp_structured_context_similarity_v1/metrics.json, data/exp_superposition_capacity_binding_v1/metrics.json, data/exp_live_binding_load_signgap_v1/metrics.json. NO hdlab/ modified."
reverify: ".venv/Scripts/python.exe verification/test_sign_quantiser_not_the_bottleneck_on_hit1.py  (headline: sign not the bottleneck. Drill reproducers, deterministic, own-dir-only: .venv/Scripts/python.exe experiments/exp_taxonomic_vs_thematic_gold_v1.py --mode full  and  experiments/exp_structured_context_similarity_v1.py --mode full)"
---

# What this refutes, and the deeper thing it found

**The brief's mechanism is refuted on the real task: the terminal `sign()` is NOT what makes the
substrate an averaging machine.** On the open-vocabulary hit@1 read-out (the argmax the reading loop
actually performs, over all 5,491 anchors), removing the `sign()` (graded) buys nothing
(+0.0015, CI includes zero). More strikingly: the **averaging machine wins** -- always naming the
single most generic concept ("change", a valid WordNet meaning for 17.1% of items) BEATS every
per-item code-format read-out (all 0.029-0.062), CI-separated. The read-out is not being *dragged
toward* the prototype by `sign()`; it is strictly *worse than* the prototype.

Then, following the owner's push to find the brain's actual mechanism rather than stop at the
refutation, I swept the **entire brain-faithful code-format family** and it all hit the **same wall**
-- which, by the operating protocol's own logic, means none of those was the brain's mechanism:

| read-out format (d=256, same instrument, same data) | hit@1 | vs best-constant floor 0.171 |
|---|---|---|
| SIGN (the deviation under test) | 0.0465 | -0.125 (CI-sep below) |
| GRAD_RAW (graded; current default) | 0.0480 | -0.123 |
| **DN_CENTER (divisive normalisation, read-out)** | **0.0537** | -0.117 |
| DN_CENTER2 / DN_Z / DN_CH (divisive-norm variants) | 0.046-0.046 | -0.12 |
| IDF composition (divisive normalisation at the pooling step) | 0.047-0.049 | -0.12 |
| DN_SPARSE20 / DN_SPARSE10 (sparse+graded, in place) | 0.039 / 0.030 | worse |
| EXPAND2K_S02/10/30 (DG expansive-sparse, project up + k-WTA) | 0.035-0.048 | -0.12 |

**The wall is not the code format** -- every arm above is an *unsupervised* similarity over
co-occurrence statistics. So I built the two things the cortex does that they do not: learning, at
two fidelity levels.

- **A SUPERVISED linear associator** (least-squares Hebbian map; the delta rule's fixed point),
  trained on WordNet-derived gold-anchor targets and evaluated on held-out items, scores **0.1081 vs
  cosine 0.0463** (+0.0618, CI[+0.046,+0.078]) -- it doubles the read-out.
- **BUT the brain gets no WordNet labels from reading.** So I built the fully-brain-faithful
  SELF-SUPERVISED learner -- from-scratch CBOW-NS: predict the masked word from its context, online
  delta-rule updates, a *co-learned* representation (not a frozen code). Given only the corpus, it
  scores **0.0428 -- statistically identical to the co-occurrence cosine 0.0480** (delta -0.0053, CI
  includes zero), and 0.096 CI-below the prototype floor. This is not a tuning miss: Levy & Goldberg
  (2014) proved CBOW-NS *implicitly factorises shifted PMI*, so it carries the SAME distributional
  information as the cosine -- they are two compressions of one signal and they land together.

**So the drilled-finer verdict corrects the tempting one.** It is NOT that "the signal is present but
unlearned." Every UNSUPERVISED method -- counting, graded, divisive-norm, sparse, DG-expansive, and a
faithful self-supervised predictive learner -- lands at the same distributional ceiling (~0.05), all
below the averaging floor. The ONLY thing that beat it needed the answer key (WordNet supervision).
**The signal that separates the specific meaning from the generic prototype is not IN the unsupervised
distribution of this corpus; it has to be SUPPLIED (grounding / a knowledge source).** The averaging
machine is a meaning-*supply* problem (LONG_TERM_PLAN Phase 1 / `reader_meaning_channel`), sitting
entirely UPSTREAM of the `sign()` this brief named and of every read-out mechanism I could change.

## FINER-RESOLUTION DRILLS (owner-directed: "is the measurement itself brain-foundational?")

The refutation above graded against WordNet gold, which is **taxonomic** (synonyms, hypernyms,
sisters). But the brain does not organise concepts primarily taxonomically -- it has TWO similarity
systems: **feature-correlational similarity** (ATL / grounded) and **associative relatedness**
(distribution / LIFG-pMTG). So before accepting "the signal isn't there," I asked whether the
instrument was measuring the wrong KIND of meaning. Scored the SAME representations against
WordNet-INDEPENDENT human ratings (Spearman rho; twins + frequency floor lose). **All numbers on the
intersection of pairs all three representations cover (n=213 WordSim, n=573 SimLex).**

**DRILL 1 -- the unsupervised distribution DOES carry brain-real meaning; WordNet gold could not see it.**

| representation | WordSim-353 (RELATEDNESS) | SimLex-999 (SIMILARITY) | freq floor / shuffled twin |
|---|---|---|---|
| CO_OCC (co-occurrence field) | **0.250** | 0.039 | 0.035 / -0.014 |
| CBOW (self-supervised) | **0.214** | 0.031 | -- / -0.027 |
| GROUNDED (sensorimotor) | **0.417** | **0.207** | -- |

The co-occurrence and CBOW reps that scored ~0.05 on WordNet-taxonomic hit@1 predict human
RELATEDNESS at rho 0.21-0.25 (vs a frequency floor of 0.03 and shuffled twins at ~0) -- they are NOT
broken. **The averaging machine was partly a MEASUREMENT ARTIFACT: a relatedness-carrying
representation graded against a taxonomic/similarity gold.** But distribution is genuinely ~0 on pure
SIMILARITY (SimLex 0.03-0.04, not significant) -- the classic distributional signature.

**DRILL 2 -- grounding supplies both axes and is best; the two systems are complementary but must be
task-GATED.** GROUNDED (Lancaster sensorimotor, the pinned Phase-1 supply) tops every benchmark
(WordSim 0.417, SimLex 0.207). FUSION (distribution + grounding, z-scored cosine average) BEATS
grounding alone on relatedness (WordSim 0.431 > 0.417; USF 0.296 > 0.279) but HURTS on pure similarity
(SimLex 0.160 < 0.207 -- blending the near-zero relatedness channel dilutes the similarity signal). So
the associative and feature-similarity systems are complementary, but a fixed blend is wrong: they
need the brain's **semantic control (IFG, task-gated multiplicative gain)** -- an audit deviation the
substrate does not have. (Consistent with the landed `exp_ownmetric_frequency_controlled_v1`: grounded
0.744 vs PPMI floor 0.555 on a ConceptNet associative gold, twins lose.)

**DRILL 4 -- the SIMILARITY axis the instrument demands is recoverable from brain-faithful STRUCTURE,
not any read-out normaliser.** Varying ONLY the CBOW context from the topical whole-sentence bag to a
narrow ORDERED window (fixing the order-blind-bag divergence too):

| context | SimLex (SIMILARITY) | WordSim (RELATEDNESS) |
|---|---|---|
| whole-sentence bag | 0.0745 | 0.282 |
| window +/-5 | 0.088 | 0.288 |
| window +/-2 | 0.100 | 0.266 |
| **window +/-1** | **0.112** | 0.262 |

Narrowing the window RAISES functional similarity monotonically (+50%, 0.075->0.112) and trades off
topical relatedness (0.282->0.262) -- the Levy & Goldberg (2014) topical-vs-functional result,
reproduced. The feature-similarity system uses STRUCTURED/local context (syntactic slots / thematic
roles, LATL); the associative system uses broad context. **So the similarity the WordNet instrument
wants is a STRUCTURE/GROUNDING problem, not a read-out-format or a `sign()` problem.**

**DRILL 5 -- BINDING / SUPERPOSITION (BUILT): this is where the brief was RIGHT, and it names the sites
to fix.** The averaging machine's deepest form is superposition blur: bind B role-filler pairs, sum
them, and `sign()` the bundle. I measured recovery (unbind + cleanup over a 512-filler codebook) vs
load B, for RANDOM vs CORRELATED fillers, GRADED vs SIGN, at d in {256,1024} (MAP-VSA, the substrate's
bipolar regime; 300 trials; shuffle floor at chance 1/512; self-test: B=1 inverts, shuffle->chance,
capacity degrades with load).

| d=256, CORRELATED fillers | B=4 | B=6 | B=8 | B=12 |
|---|---|---|---|---|
| GRADED | 1.00 | 0.98 | 0.88 | 0.67 |
| SIGN | 0.92 | 0.73 | 0.58 | 0.36 |
| gap (all CI-separated) | +0.08 | +0.24 | +0.30 | +0.31 |

**`sign()` DOES cost capacity here, and MORE for correlated codes** (mean graded-minus-sign gap
CORRELATED +0.146 vs RANDOM +0.080). At d=256 keeping strength raises the capacity cliff (accuracy
>=0.5) from **B*=8 (sign) to B*=12 (graded)** for correlated codes -- a 50% gain, straddling the
brain's ~4-7 working-memory span (Cowan/Miller). At d=1024 both formats hold through B=16 (capacity
scales with dimensions). So the brief's "superposition cliff below B=4" is beaten, and `sign()`
needlessly lowers the correlated-code capacity that graded would keep. **This is the brief's `sweep
WHICH sites` answer: strength matters at the SUPERPOSITION-of-correlated-bound-codes sites (binding
bundle / CA3 completion / working-memory buffer), NOT the read-out.**

**LIVE VERIFICATION (does the binding win bite in the LIVE substrate? -- turning the construction
proof into a live claim).** Recon + a live measurement over real curriculum text
(`exp_live_binding_load_signgap_v1`, StructuralEncoder, n=6,020 encodings):
- **No reachable on-stream site meets all three conditions (B>4 AND correlated AND sign()).** The one
  correlated-code binder (StructuralEncoder) has **mean B=2.85** (confirms the 2.82 on disk), is
  already GRADED by default, and is islanded; the live sign()+high-B site (`hd_fact_store`, B=5-6)
  binds role-HETEROGENEOUS fillers, not similar concepts.
- **The deeper reason, measured:** the substrate binds ATOMIC RANDOM symbols (`symbol_vector`), so
  fillers are near-orthogonal (**pairwise |cos| 0.06**) -- the correlated regime never arises. The
  SAME fillers under a brain-faithful graded-semantic code are genuinely **correlated (|cos| 0.25)**.
- **Sign-vs-graded recovery at the LIVE load:** ATOMIC (current) gap **+0.013** overall, **~0 for
  B<=4** -- `sign()` is SAFE today. SEMANTIC (brain-faithful) gap **+0.044** overall, **+0.087 on the
  14% tail with B>4** -- it opens up.

So the binding `sign()` problem is a **live NON-issue TODAY** (load mostly <=4; codes atomic/
orthogonal), and it becomes a real liability **exactly when binding is made brain-faithful** (graded
semantic fillers). **The `sign()->graded` binding fix is COUPLED to the graded-semantic-code fidelity
fix (B4): flipping the bundle to graded in isolation buys ~0 now; making fillers graded/semantic
WITHOUT also keeping the bundle graded RE-CREATES the averaging machine, worst on the B>4 tail.** This
also explains why `sign()` reads null everywhere live: atomic symbols at sub-cliff load.

**UNIFIED CONCLUSION -- the brief was HALF right, LOCATED, and shown to be LATENT-not-current.** Three
findings, one picture:
- **READ-OUT regime (open-vocab hit@1):** `sign()` is NOT the bottleneck (refuted). The averaging
  machine there is a confluence with nothing to do with `sign()`: (1) a MEASUREMENT-axis mismatch (an
  associative/relatedness representation graded against taxonomic/similarity gold); (2) a real
  SIMILARITY-axis gap filled brain-faithfully by GROUNDING and STRUCTURED/local context, not any
  read-out format; (3) a missing SEMANTIC CONTROL to gate the two similarity systems by task.
- **BINDING/SUPERPOSITION regime (correlated bound codes):** `sign()` IS a real averaging machine in
  principle (confirmed on the synthetic benchmark: caps correlated-code capacity at B*=8 where graded
  reaches 12, d=256) -- BUT it does NOT bite in the LIVE substrate today (load mean 2.85, mostly <=4;
  fillers are atomic/orthogonal, |cos| 0.06, so gap ~0). It becomes real only when binding is made
  BRAIN-FAITHFUL (graded semantic fillers, |cos| 0.25 -> gap +0.044, +0.087 on the B>4 tail). So it is
  a LATENT liability coupled to the graded-code (B4) fidelity program, not a current bug.

So the mechanism the brief named is REAL but (a) MIS-LOCATED -- a binding/working-memory capacity lever
for correlated codes, not the read-out bottleneck -- and (b) LATENT, not current: it is dormant while
binding uses atomic symbols at sub-cliff load, and activates precisely under the fidelity improvements
the project is pursuing. That precision -- refute the read-out regime, confirm-and-quantify the binding
mechanism, then show it is a coupled future guardrail rather than a present fix -- is the deliverable.

## What I built and measured

- **Instrument (reused verbatim):** `exp_grounding_readout_known_answer_v1`'s C3 open-vocab hit@1 --
  build the `ConceptSpace` from the corpus, argmax each held-out lemma's context bundle over all
  5,491 anchors, score hit@1 against a generous WordNet gold set. n=4,000 items.
- **Format sweep (`exp_divisive_normalisation_readout_v1`):** one graded field built once
  (GRADED_COMPARATOR=1 -> raw sums), then competing read-out transforms applied to *byte-identical*
  data so the only variable is the normaliser. Arms: SIGN, GRAD_RAW, divisive normalisation at the
  read-out (center / center-both / z / Carandini-Heeger within-vector), divisive normalisation at
  the *composition* step (IDF-weighted pooling), sparse+graded in place (k-WTA), and DG
  expansive-sparse recoding (project 256->2048, graded k-WTA at 2/10/30%). Floors, info-free twins,
  and a d=256->1024 capacity sweep.
- **Learned-read-out capstone (`exp_learned_readout_probe_v1`):** a closed-form ridge linear
  associator context-sum -> target-anchor identity, trained on a train split, hit@1 on a disjoint
  held-out split, vs the unlearned cosine and the floors on the same test split.

## The numbers with their caveats (no number crosses instruments)

- **graded vs sign (real hit@1): +0.0015, CI[-0.0055,+0.0083], NULL.** (The brief's own +0.0602 is
  2AFC-only and does not transfer -- confirmed.)
- **divisive normalisation (DN_CENTER) vs sign: +0.0073, CI[+0.0000,+0.0145], null_p95=0.0072.**
  Direction-correct (it is the only faithful op that point-beats both sign and raw-graded, twin
  losing) but the edge is *within bootstrap noise* -- it cleared zero at one seed (ci_lo +0.0003) and
  not another (ci_lo 0.0000). Not a capability.
- **Capacity (d 256->1024):** read-out rises ~+0.010 (0.048->0.058), MORE than any format gain --
  capacity is a bigger lever than de-signing, consistent with the prior 2AFC "capacity-limited not
  quantiser-limited" finding and the audit's B4 (16x dims = +0.0843).
- **best-constant floor = 0.1710** ("change"), d-independent. Every code-format arm is 0.09-0.14
  CI-below it.
- **learned associator (held-out): 0.1081 vs cosine 0.0463, +0.0618 CI[+0.0458,+0.0777].** Still
  -0.0244 CI-below the prototype floor on the test split -- so the *linear one-shot* form doubles the
  signal but does not by itself clear the averaging floor.

## HOW THE BRAIN DOES THIS -- PINNED vs OUR-INVENTION

- **PINNED, confirmed:** additive combination (the SUM the read-out sits on is faithful); divisive
  normalisation as the pooling op (direction-correct, but a *minor* lever here, +0.007 within noise);
  associative learning as the cortex's context->concept mechanism (the actual lever -- doubles hit@1).
- **OUR-INVENTION-UNDER-TEST, REFUTED:** (a) "the terminal `sign()` is the bottleneck on real tasks"
  -- refuted (null, and the wall is format-invariant). (b) "divisive normalisation at the
  read-out/composition step is a capability lever on the real task" -- refuted (marginal, within
  noise). (c) "the averaging machine is cured by the brain's code FORMAT (graded / sparse / DG
  expansion)" -- refuted (the whole family shares one wall).
- **OUR-INVENTION-UNDER-TEST, SUPPORTED:** the read-out being an *unlearned* cosine over
  co-occurrence statistics is the bottleneck -- a learned map doubles it.

## KEY REALIZATIONS (the enabling moves)

1. **The disk outranked the brief on a load-bearing point.** `GRADED_COMPARATOR` has been
   **default-ON since 2026-08-14** -- the comparator field AND query are already graded. The brief's
   "graded flags default-OFF / the default is sign'd" is stale; the "one-line sign->graded flip" was
   largely already landed, and it is null on the real task. The only unconditional `sign()` left on a
   live compose/read path is `canonicalize():896` (the banking query), separately measured to cost
   ~0. This reframed the whole problem from "flip the switch" to "the switch is already flipped and it
   didn't matter."
2. **The 2AFC/hit@1 split is structural, and it is why the prior work all plateaued.** On 2AFC the
   shared prototype component *cancels* in a 2-candidate argmax, so divisive normalisation is inert
   there; hit@1 (argmax over thousands) is the instrument where de-prototyping *can* matter -- yet even
   there it buys only +0.007. Picking the right instrument dissolved the "graded wins +0.0602" mirage.
3. **The floor no one had computed flips the whole framing.** The best-constant "averaging machine"
   (always say "change", 0.171) *beats* every per-item code-format read-out. So the read-out isn't a
   good extractor being blunted by `sign()`; it is *worse than naming the average thing*. "Averaging
   machine" is a signal-extraction failure, not a quantiser artifact.
4. **A shared wall across an entire faithful family is the tell to change KIND, not tune.** sign ->
   graded -> divisive-norm -> sparse -> DG-expansive all landed at ~0.05. Per the protocol, that means
   none was the brain's mechanism -- the missing thing is different in kind. Changing the code *format*
   cannot manufacture signal the read-out never learned to extract.
5. **Drilling finer separated SUPERVISED from SELF-SUPERVISED learning, and that flipped the
   conclusion.** A learned map doubling hit@1 (0.108) looked like "the averaging machine is a learning
   gap." But that map was trained on WordNet-derived labels. The fully-brain-faithful SELF-SUPERVISED
   learner (CBOW: predict the masked word, online delta-rule, co-learned representation), given only
   reading, lands right back at the co-occurrence cosine (0.043 vs 0.048) -- because CBOW-NS implicitly
   factorises the same PMI the cosine already reads (Levy & Goldberg 2014). So the lever is NOT
   "learning" in general; it is SUPPLIED answer-structure. The signal is not in the unsupervised
   distribution of this corpus. This is the highest-yield move of the whole problem, and it only
   appeared because the owner's "drill finer / don't diverge from brain foundation" directive forced
   the supervised-vs-self-supervised distinction instead of stopping at the flattering supervised
   number.
6. **The finest move was doubting the TARGET, not the mechanism.** After the mechanism sweep bottomed
   out, the highest-yield question was "is the GOLD brain-foundational?" -- and it was not: WordNet is
   taxonomic, the brain has two similarity systems, and the read-out was carrying the associative one
   (relatedness rho 0.21-0.25) while being graded on the taxonomic one. Recomputing against human
   relatedness/similarity ratings (WordNet-independent) turned a flat "signal absent" into a precise
   two-systems map. *Ask whether the experiment could have succeeded -- at the level of the metric,
   not just the method.*
7. **A refuted mechanism can be a MIS-LOCATED one -- test the OTHER regime before closing it.** The
   `sign()` looked dead on the read-out, but the brief itself named a second regime (superposition of
   correlated codes) that I had only cited. Building it showed `sign()` is a real, growing capacity
   lever there (cliff B*=8->12). The lesson: when a mechanism refutes in the regime you tested, ask
   which regime it was DESIGNED for before declaring it wrong -- the same operation can be inert in one
   place and load-bearing in another, and "which codes are being summed" decides which.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- strategy folds in at integration)

- **Deviation #2 (`sign()` quantiser) -- two corrections.** (1) STALE PREMISE: `GRADED_COMPARATOR` is
  **default-ON** at HEAD (env `HD_GRADED_COMPARATOR` defaults "1", flipped 2026-08-14); the comparator
  field+query are already graded, and the remaining unconditional live `sign()` is
  `reading_grounding_loop.canonicalize():896` (banking query), measured ~0 cost on hit@1. The audit's
  "graded flags exist default-OFF" (S5.2) should be corrected. (2) REFRAMED: on the REAL open-vocab
  hit@1 task, **no unsupervised method** (sign->graded, divisive normalisation at read-out or
  composition, in-place sparse, DG expansive-sparse, AND a faithful self-supervised CBOW learner)
  beats the prototype/averaging floor; they all sit at the distributional ceiling ~0.05. The loss is
  a meaning-**SUPPLY** gap (LONG_TERM_PLAN Phase 1 / `reader_meaning_channel`), NOT the quantiser and
  NOT the read-out mechanism. **Re-point the leverage ranking (S8 item #1, "sign->graded"): DOWN** --
  it is not the averaging-machine lever.
- **NEW cross-check for the "meaning is present-but-unwired" re-frame (audit S7):** on THIS instrument
  (open-vocab hit@1 vs WordNet gold, McGuffey-class corpus) the unsupervised distributional signal is
  NOT sufficient -- a self-supervised learner ties the counting cosine (both ~0.05) and both lose to a
  generic-word floor (0.171). Only WordNet-supervised learning exceeds it (0.108). This does not
  contradict S7's frequency-controlled win, but it bounds it: distribution alone does not place the
  specific gold meaning first here; supply/grounding is required. Reconcile S7 with this instrument.
- **B2 (per-occurrence pooling, divisive normalisation):** tested on a real task for the first time --
  direction-correct but a *minor* lever (+0.007, within noise). B4 (dense->sparse+graded): in-place
  sparsification and DG expansive-sparse recoding do NOT beat dense graded on this open-vocab task
  (the DG win is *episodic recall*, a different instrument). Capacity (more dense dims) still helps
  most among format levers (+0.010 for 256->1024).
- **NEW -- the TWO SIMILARITY SYSTEMS are measurable in our substrate (should be a first-class audit
  row).** On WordNet-independent human ratings: the distribution/co-occurrence channel carries
  ASSOCIATIVE RELATEDNESS (WordSim rho 0.25) but ~0 FEATURE SIMILARITY (SimLex 0.04); GROUNDING carries
  both (0.42 / 0.21). This is the ATL-feature-similarity vs LIFG/pMTG-associative dissociation, now
  quantified on our own reps. Two consequences the audit should record: (a) evaluating meaning against
  WordNet TAXONOMIC gold systematically UNDER-credits the associative channel -- prefer human
  relatedness/similarity or a relation-controlled gold; (b) the SIMILARITY axis is recovered by
  brain-faithful STRUCTURE (narrow/ordered context: SimLex 0.075->0.112 as window 0->+/-1) and by
  grounding, not by any read-out format -- and the two systems need SEMANTIC CONTROL (IFG) to be gated
  by task (naive fusion helps relatedness, hurts similarity). This connects the currently-THIN
  "semantic control" deviation to a concrete, measured need.

## WHAT I DID NOT ESTABLISH (withdraw these first if wrong)

- **The supervised linear associator (0.108) is a DIAGNOSTIC, not a capability and not the brain's.**
  It is trained on WordNet-derived labels the brain never receives from reading; the self-supervised
  learner (the faithful one) ties the cosine. Withdraw first any reading that "learning solves the
  averaging machine" -- only SUPPLIED supervision did, which is the point (supply, not read-out).
- **The self-supervised CBOW learner carries four named FIDELITY DIVERGENCES I did not drill out**
  (owner directive: "drill ever finer so we don't diverge from brain foundation"). It is faithful in
  the learning RULE (predictive, error-driven/delta, co-learned) but convenient in: (1) ORDER-BLIND
  bag context (cortical prediction is sequential/temporal, theta-gamma ordered); (2) RANDOM negative
  sampling (the brain's competitor-suppression is lateral inhibition among co-active neighbours, not
  unigram noise); (3) TWO embedding matrices (a word2vec convenience; a concept has one representation
  with distinct comprehension/production sites); (4) SIGMOID gain instead of the divisive-normalisation
  gain I argued was pinned. Theory (Levy&Goldberg: CBOW-NS ~ shifted-PMI factorisation) predicts these
  will not clear the floor because the limit is the corpus/supply, not the learner -- but I did NOT
  test the finer-grained faithful learner, so I cannot fully exclude that #1 (order/sequence) recovers
  some signal. That is the first thing to drill next.
- I did NOT test the full ~34-site `sign()` removal through a multi-step compose->bind->read
  pipeline END-TO-END. I DID now measure the superposition cliff for correlated *bound* codes (DRILL 5,
  no longer just cited): the cliff is at B*=8 (sign) / 12 (graded) at d=256 in a clean MAP-VSA
  benchmark. What I did NOT do is confirm those sites carry CORRELATED codes at load B>~4 in the LIVE
  substrate (the win applies only where they do) -- that per-site check is the first integration step.
  The binding OPERATION itself (which VSA/theory) I held fixed at MAP-VSA; other bindings may cliff
  differently.
- **CORRECTION (disk outranks recollection, 2026-08-26):** the corpus this instrument uses
  (`load_corpus_v5`) is NOT McGuffey/archaic -- it is MODERN (OneStopEnglish 2010s graded news +
  OpenStax biology + science process articles; there is an explicit "stop mcguffey" directive). So
  corpus-AGE is NOT the confound. The live alternative explanation for the ~0.05 ceiling is instead
  that the GOLD is WordNet TAXONOMIC while the brain (and distribution) organises concepts
  thematically -- i.e. we may be grading against the wrong KIND of semantic structure. That is under
  test next (see the taxonomic-vs-thematic follow-up); prior work already leans that way
  (`verification/test_wordnet_advantage_is_selection_not_meaning.py`: on SimVerb NONE pairs the
  grounded channel beats WordNet 2x).

## PROPOSED hdlab CHANGE (strategy lands it; board Q111)

1. **Do NOT flip `sign()` for a CURRENT win -- there is no live site where it pays.** Live verification:
   the read-out flip is null; the binding flip is ~0 today (load mean 2.85 <=cliff; fillers atomic/
   orthogonal). Flipping binding-bundle sites in isolation buys nothing now.
2. **COUPLED GUARDRAIL -- enforce a graded bundle JOINTLY with the graded-semantic-code (B4) fix.** The
   real result: making fillers brain-faithful (graded/semantic, correlated) WITHOUT also keeping the
   superposition bundle graded RE-CREATES the averaging machine (gap +0.044 overall, +0.087 on the 14%
   of encodings with B>4). So whenever a `sign()`-on-a-bundle site (`situation_focus.py`,
   `role_slot_summarizer.py`, `event_bundle.py` `_bipolar_quantize`, CA3 `cleanup_family.py`) is moved
   to graded/semantic fillers, its bundle MUST become graded in the same change, gated on a per-site
   superposition-recovery test like `exp_live_binding_load_signgap_v1` / `exp_superposition_capacity_
   binding_v1`. Bind the two fidelity fixes together; do NOT ship graded-semantic fillers with a signed
   bundle. Do NOT touch the read-out `sign()` (`canonicalize():896`) -- null.
3. **Optional, default-OFF, brain-faithful micro-win (read-out):** expose divisive normalisation
   (`freeze_graded(normalise="center")`) as a `ReadoutConfig` option (`center_field: bool`) in
   `canonicalize_fast`. Direction-correct (+0.007, twin-losing) -- an *option*, never a capability claim.
4. **RE-POINT the effort to SUPPLY, not the read-out.** The averaging machine is a meaning-*supply*
   gap: no unsupervised read-out (counting, format, or a faithful self-supervised learner) beats the
   generic-word floor on this corpus; only supplied WordNet supervision did. So the lever is grounding
   / a knowledge source feeding the reader (LONG_TERM_PLAN Phase 1 / `reader_meaning_channel` /
   `where_does_a_meaning_signal_come_from_without_labels`), NOT a better read-out and NOT the `sign()`.
   Before any learned-read-out build, first rule out the corpus-age confound (archaic corpus vs modern
   gold) and drill the CBOW divergence #1 (sequence/order), since theory says the rest won't move it.

---

## TLDR (plain language)

We thought a shortcut buried at the end of almost every step -- keeping only "positive or negative"
and throwing away "how strong" -- was quietly turning the system into a machine that always guesses
the average, generic answer. On the real task (guess the missing word from its context), that turns
out to be **wrong**: keeping the strength makes essentially no difference, and the system already
keeps it by default. Worse, the system does *worse* than a dumb strategy of always naming the single
most generic word ("change"). I tried every brain-shaped way of writing the code -- keeping strength,
dividing out the common part, making it sparse, spreading it into a higher dimension the way the
hippocampus does -- and they **all** landed in the same place, below that dumb baseline.

Then I built the brain's real trick: instead of just *counting* which words appear together, let the
system **learn to predict** the missing word from its neighbours -- which is how the cortex actually
learns. And here is the honest twist that only showed up because we kept drilling for fidelity: when
I let it peek at the dictionary's answer key while learning, the score doubled -- but a system that
learns purely from *reading*, with no answer key, lands **right back** where plain counting did. It
turns out those two are mathematically the same thing. So the real bottleneck was never the shortcut,
and it isn't even "learning" -- it is that **the information telling apart the specific meaning from
the generic one simply isn't in the raw text of the raw text **when you ask
for the librarian's taxonomy.** But when we kept drilling, a twist appeared: the reading-based system
is NOT useless -- it reliably captures which words are **related** (dog-leash, coffee-cup), matching
human judgement; it just can't tell which words are **alike in kind** (dog-wolf, coffee-tea). Those are
two different senses of "meaning," and the brain has two systems for them. We were grading it on the
"alike in kind" test while it was doing the "related" one. And the "alike in kind" sense IS
recoverable brain-faithfully -- by looking at a **tight window** of nearby words instead of the whole
paragraph, and by **grounding** words in the senses (what they look/feel/sound like). So the real work
is not a better shortcut and not even "learn harder"; it is (a) test meaning the right way, (b) build
the second system from grounding and sentence structure, and (c) let the brain switch between the two
depending on the question. None of that is the shortcut this problem named.

**One more twist, and it partly VINDICATES the original worry.** The shortcut (`sign()`) really IS
harmful -- just not where we first looked. When the system has to hold SEVERAL bound facts at once in
memory (like keeping "who did what to whom" for several people), and those facts are similar to each
other, the shortcut smears them together into the average and you lose track. Keeping the strength
instead lets the system hold about 12 such facts before they blur, versus about 8 with the shortcut --
a 50% bigger memory, right in the range of human working memory (~4-7 items). So the fix "keep the
strength" is real and worth doing -- but at the MEMORY/binding step, not at the reading step. The
original instinct was correct about the operation; it just pointed at the wrong place.

## QUESTIONS

None blocking. Status is **PARTIAL** by design: the brief's claim is REFUTED in the read-out regime
(sign null; the averaging machine there is measurement-axis + structure/grounding + control) but
CONFIRMED and QUANTIFIED in the binding/superposition regime (sign lowers correlated-code capacity,
cliff B*=8->12 at d=256). PARTIAL captures both halves honestly; a reviewer could read the read-out
half alone as REFUTED, but that would drop the real, actionable binding-capacity win and its "which
sites" answer. The numbers and controls are unambiguous in both regimes.

## NEXT STEPS

1. Strategy: fold the AUDIT UPDATEs into `BRAIN_FOUNDATIONAL_AUDIT.md` -- especially the NEW
   two-similarity-systems row and the measured need for SEMANTIC CONTROL (gating); re-point S8 item #1
   ("sign->graded") DOWN.
2. **Stop grading meaning against WordNet TAXONOMIC gold alone.** It under-credits the associative
   channel the substrate actually has. Adopt human relatedness/similarity (WordSim/SimLex) or a
   relation-controlled gold as the standing meaning metric. This is the cheapest, highest-leverage fix
   and it changes how several past "meaning is absent" verdicts should read.
3. Build the FEATURE-SIMILARITY system brain-faithfully: (a) grounding (already best: sensorimotor
   0.42/0.21), (b) STRUCTURED/local context (narrow window / dependency / thematic roles), which
   recovers similarity where the topical bag cannot. Then add SEMANTIC CONTROL to gate associative vs
   feature-similarity by task (fixed fusion hurts similarity). This is `reader_meaning_channel` +
   grounding + a new "semantic control gating" problem -- NOT the `sign()`.
4. Optional: land the default-off `center_field` divisive-normalisation option (micro-win, fidelity).
5. **COUPLE the graded bundle to the graded-semantic-code (B4) fix -- do NOT land it standalone.** Live
   verification shows the binding `sign()` is a live NON-issue today (atomic codes, load <=4). It
   becomes real ONLY when binding is made brain-faithful (graded/semantic fillers): then a signed
   bundle re-creates the averaging machine (+0.044, +0.087 on the B>4 tail). So when B4 makes fillers
   graded/semantic, the `sign()`-on-a-bundle sites (`situation_focus.py`, `role_slot_summarizer.py`,
   `event_bundle.py`, CA3 `cleanup_family.py`) must go graded in the SAME change, gated on
   `exp_live_binding_load_signgap_v1` / `exp_superposition_capacity_binding_v1`. Not a standalone win.
6. Deepest push (separate program): the role-filler BINDING operation itself is unpinned / 3-way
   contested -- which binding theory (theta-gamma / conjunctive / tensor-product) sets the true capacity
   is a deliberate binding-theory program, not this slug.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- REFUTED-VALUABLE, owner-authorized in-session ("be as brain foundational as possible"). Re-verified scaffold-free (test_sign_quantiser_not_the_bottleneck_on_hit1.py PASS; stale-premise HD_GRADED_COMPARATOR=default-ON confirmed on disk). The `sign()` (audit deviation #2 / the #1 leverage lever) is NOT the averaging-machine bottleneck: the whole brain-faithful code-format family + a faithful self-supervised CBOW learner all tie plain counting (~0.05), below the 0.171 generic-word floor; only WordNet-SUPERVISED learning beats it -> the wall is meaning SUPPLY. 3 AUDIT UPDATEs folded (deviation #2 refuted/re-pointed; §8 lever #1 demoted; §7 bounded; NEW two-similarity-systems row + measured semantic-control need). Review in PROBLEM.md; priority cleared. The brain-foundational next build packaged as `the_substrate_has_one_meaning_system_where_the_brain_has_two`. Optional default-off center_field micro-win NOT landed (within noise). Committed (no push).

## SOLVER ADDENDUM (2026-08-26, POST-INTEGRATION -- please RE-VERIFY & RE-FOLD, owner-directed)

The `INTEGRATED_BY_STRATEGY` block above integrated the **READ-OUT half only** (status REFUTED). After
it, the owner directed further pushes and I added TWO regimes that were NOT in that integration and
that **change the verdict to PARTIAL**:

1. **BINDING/SUPERPOSITION (DRILL 5, `exp_superposition_capacity_binding_v1`).** `sign()` DOES lower
   superposition capacity for CORRELATED bound codes (cliff B*=8->12 at d=256, CI-separated,
   correlation-specific). The brief's mechanism is REAL in this regime -- refuted at the read-out,
   confirmed here.
2. **LIVE VERIFICATION (`exp_live_binding_load_signgap_v1`).** It does NOT bite live today: real
   StructuralEncoder load mean B=2.85 (mostly <=4), fillers atomic/orthogonal (|cos| 0.06) -> gap
   +0.013 (~0). It becomes real ONLY under brain-faithful graded-semantic fillers (|cos| 0.25 -> gap
   +0.044, +0.087 on the 14% of encodings with B>4). So `sign()->graded` at binding is a **guardrail
   COUPLED to the graded-code (B4) fix**, not a standalone win.

**For re-integration:** (a) update the status/verdict to PARTIAL (read-out refuted; binding real but
latent-coupled); (b) add the AUDIT UPDATE that the `sign()` deviation #2 is COUPLED to B4 at the
binding sites -- shipping graded-semantic fillers with a signed bundle re-creates the averaging machine;
(c) the "flip binding sites for a win" reading is wrong -- it is a joint-with-B4 guardrail. The read-out
integration above stands; these two regimes are additive to it. Ledger status set to PARTIAL.

INTEGRATED_BY_STRATEGY: 2026-08-26 (FINAL, RE-INTEGRATION ON OWNER-DONE -- supersedes the earlier premature marker above). EXCELLENT; outcome PARTIAL. The earlier marker integrated the READ-OUT half off a DIRECTIONAL owner "yes" while the solver was still iterating; that was reverted (see OWNER_NOTES/PROBLEM.md history) and this is the proper re-integration on the owner's per-problem owner_verdict:DONE. ALL THREE regimes re-verified scaffold-free FIRST-HAND: (1) READ-OUT REFUTED (test_sign_quantiser_not_the_bottleneck_on_hit1.py PASS -- sign null; whole faithful format family + self-supervised CBOW tie counting ~0.05, below the 0.171 floor; only WordNet-supervised beats it -> meaning-SUPPLY wall). (2) BINDING CONFIRMED (exp_superposition_capacity_binding_v1 reproduces -- graded beats sign for CORRELATED codes, cliff B*=8->12 at d=256). (3) LIVE LATENT (exp_live_binding_load_signgap_v1 reproduces SIGN_SAFE_TODAY_BUT_BITES_IF_BINDING_MADE_FAITHFUL -- real load meanB=2.85, atomic |cos|0.06 -> gap +0.013 ~0 today; graded-semantic |cos|0.25 -> +0.087 on the B>4 tail). VERDICT: sign() is not the averaging machine at the read-out but IS at binding for correlated codes -- a LATENT guardrail COUPLED to the graded-code (B4) fix, NOT a current bug, NOT a standalone win. FOLDED into BRAIN_FOUNDATIONAL_AUDIT.md (§2b: deviation #2 = PARTIAL, binding-regime entry + read-out entry; §8 lever #1 demoted only as a read-out lever, alive as a binding-site guardrail). Review + SOLVER REVIEW block in PROBLEM.md; priority cleared. The read-out two-similarity-systems finding drives the new p1 build (the_substrate_has_one_meaning_system_where_the_brain_has_two). GUARDRAIL recorded for the B4/binding line (p3, p5): when B4 makes fillers graded-semantic, the sign()-on-a-bundle sites (situation_focus, role_slot_summarizer, event_bundle, CA3 cleanup_family) go graded in the SAME change, gated on the two binding cells. NO hdlab landing now. Committed (no push).
