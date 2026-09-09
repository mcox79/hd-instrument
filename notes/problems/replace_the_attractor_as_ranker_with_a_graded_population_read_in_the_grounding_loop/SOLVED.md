---
problem: replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop
status: PARTIAL
bar: "PASS = a brain-foundational GRADED POPULATION READ replacing the sign()+attractor as the RANKING step in the grounding-acquisition loop, that beats the incumbent attractor-as-ranker CI-separated on the loop's OWN ranking / growth-quality metric (its real live measure, not a synthetic proxy), with (a) the info-free twin (shuffled codebook / random ranker of equal size) LOSING, (b) high-degree-hub over-promotion MEASURABLY reduced (the named failure mode), and (c) the recall / recognition path (the attractor's correct job) byte-identical-or-better -- NO regression. A rigorous LOCATED NEGATIVE is a full pass IF it names, with a number, exactly why the graded read cannot beat the attractor here (e.g. the loop's ranking is already graded and the attractor only does recall, or the metric is saturated) -- quantify it."
result: "LOCATED NEGATIVE on the brief's named mechanism + a positive full-stack lever. (1) The live grounding-loop RANKING is ALREADY a graded population read: sense assignment routes through canonicalize_fast (cosine matvec, GRADED_COMPARATOR ON since 2026-08-14), NOT the attractor. Swapping the incumbent gate readout attractor->population changes ranking fidelity by -1.4e-5 (Spearman to grounded-meaning gold; 95% boot CI [-2.9e-5,+3.4e-6], INCLUDES ZERO; n=400 query words, 1600-word grounded codebook, d=512) -- the attractor, run at the gate's sharp temp (effective beta ~ temp*sqrt(d)), IS a population read. It only diverges at SOFT temps the gate never uses (attractor Spearman 0.73 at temp=0.25 vs 0.995 at temp>=8; readout_delta_vs_pop 0.000 at temp=8). Hub over-promotion is ~0.02 for EVERY arm at the gate's sharp temp (fix 0.0230 vs incumbent 0.0213) -- not an attractor artifact -> the named failure mode does not bite as configured. (2) The REAL signal-loss is the REPRESENTATION: the live familiarity cue is a random-symbol hash (gap_detector.content_key), whose ranking fidelity to true grounded meaning is Spearman -0.003 (either readout) -- it carries NO graded semantic distance. Feeding the comparator the GRADED GROUNDED MEANING (grounded_similarity.grounded_vector) + a graded population read lifts ranking fidelity to Spearman 0.9946 vs the live incumbent's -0.003 and the info-free twin's 0.0007 (CI-separated), and true-nearest rank-1 from 0.6525 (sign) to 0.8975 (graded). Gate exact-match recognition AUC stays 1.0 (no regression)."
floor: "Strongest floors actually run, all recomputed on this population (1600 real Lancaster/Brysbaert grounded words, 400 query words, d=512, 3000-sample paired bootstrap): (i) the INCUMBENT itself -- sign-quantized code + iterative_attractor readout, Spearman-to-grounded-gold 0.9855 (the fix beats it +0.0091 CI[+0.0085,+0.0099]); (ii) the INFO-FREE TWIN (grounded codebook rows shuffled vs the meaning gold), Spearman 0.0007 / rank-1 0.0 (the fix beats it +0.9939 CI[+0.9918,+0.9960]); (iii) the LIVE random-symbol content_key hash as the loop runs today, Spearman -0.003 either readout. Readout isolation (POP-minus-ATTRACTOR, same sign format) = -1.4e-5 CI[-2.9e-5,+3.4e-6] NULL; format isolation (GRADED-minus-SIGN, same pop read) = +0.0092 CI[+0.0085,+0.0099]."
controls: "INFO-FREE TWIN (shuffled code<->meaning correspondence) LOSES decisively (Spearman 0.0007, rank-1 0.0) -- the ranking carries real per-word signal, not base-rate. READOUT ISOLATION (attractor vs population, same format) excludes the readout as the harm (null, CI incl 0). FORMAT ISOLATION (graded vs sign, same population read) attributes the fidelity gap to the sign-quantiser, not the readout (+0.0092 CI-sep). TEMPERATURE SWEEP (temp 0.25->8.0) locates the attractor's divergence regime: it collapses ranking only at soft temps the live gate never uses. GATE EXACT-MATCH AUC control: known vs novel real-word separation stays 1.0 -- the fix does not regress the attractor's correct recognition job. RECALL byte-identity: the proposal touches only the gap-detection ranking comparator; hdlab.iterative_attractor.iterative_cleanup (the recall/completion primitive used by ca3_completer + hippocampal_encoder) is UNTOUCHED (witness A4). Positive control: JL random projection preserves grounded geometry (self-test Spearman>0.8); graded>=sign fidelity by construction (self-test)."
files_changed: "experiments/exp_graded_read_vs_attractor_ranker_v1.py (2x2 format x readout on REAL grounded meaning + live-hash fidelity + gate AUC + temp sweep + twin + floors), verification/test_graded_read_ranker.py (scaffold-free witness: 10 disk-fact + 5 mechanism-number checks, 15/15), data/exp_graded_read_vs_attractor_ranker_v1/metrics.json. NO hdlab/ modified (Q111 -- the hdlab proposal is stated below for the strategy session to land)."
reverify: ".venv/Scripts/python.exe verification/test_graded_read_ranker.py  (15/15; disk facts + mechanism numbers). Powered headline reproducer (own-dir only): .venv/Scripts/python.exe experiments/exp_graded_read_vs_attractor_ranker_v1.py --mode full"
---

# What I found, and why the brief's fix is already on disk

**The one-line result.** The defect the brief names -- "an iterative attractor used as a graded
similarity RANKER over sign-quantized codes in the grounding loop" -- is **substantially already
remediated / mis-located on the current disk**. The live grounding loop's *ranking* is a graded
population read; the attractor is confined to the exact-match *recognition* gate, which is its correct
brain job. Swapping that gate's attractor for a population read is a **measured no-op**. Following the
protocol past the refutation, the REAL non-brain-foundational component upstream is the *representation*
the ranking reads -- a random-symbol hash carrying zero graded meaning -- and wiring the proven grounded
meaning in with a graded population read lifts ranking fidelity from ~0 to ~0.99. That positive lever is
**prototyped and CI-separated on ranking fidelity**, but I have NOT landed the live end-to-end
grounding-quality win, so this is honestly a **PARTIAL**, not a clean SOLVED.

## The disk, traced end to end (this is the located negative)
The brief points at `hdlab/cleanup_family.py` (`classical_hopfield`/`modern_hopfield_continuous`/
`iterative_attractor`) as a live sign()+attractor ranker via `gap_detector`. On disk:

1. **The sign()-quantized Hopfield primitives are called NOWHERE live.** `classical_hopfield` and
   `modern_hopfield_continuous` (the `np.sign` ones, cleanup_family.py:130/179) are imported by no
   hdlab module (witness A5). Only `iterative_attractor` (which wraps `iterative_cleanup` -- a GRADED
   L2-normalized soft-attractor, **not** sign-quantized) and `k_NN_lookup` are consumed. So the brief's
   "sign()-quantized attractor" is a mis-description of the live primitive.

2. **The live RANKING is already a graded population read.** The loop's semantic similarity ranking is
   nearest-anchor sense assignment (`canonicalize` / `canonicalize_fast`). The default reading entry
   (`checkpoint`, `refuse_non_groundings=True` -- "the fix, not an opt-in", reading_grounding_loop.py:1674)
   always runs the gate, whose proposer calls **`canonicalize_fast`** (reading_grounding_loop.py:1120):
   a single-shot cosine matvec `sims = mat @ nb / norms` with `GRADED_COMPARATOR` ON (default since
   2026-08-14), so both the query and the anchor field are graded -- **no attractor, no sign**. This is
   already the Georgopoulos-style graded population read the brief asks for. (The signed-query reference
   `canonicalize`, :896, is only the non-default `refuse_non_groundings=False` fallback.)

3. **The attractor is confined to the exact-match RECOGNITION gate, which is its correct job, and it is
   inert there as a ranker.** The only live attractor call in the reader is `is_gap` ->
   `GapDetector.familiarity` -> `ca3_match_score`, which uses `iterative_attractor` to PICK the
   best-match row (recognition) and then reads its familiarity margin from the RAW, **pre-settle** cosine
   (gap_detector.py:111-117; the docstring pins this deliberately). Because the margin is read pre-settle,
   and the exact-match row is a fixed point the sharp attractor converges to, the attractor's settling
   does not shape the graded decision.

## The measurement (real grounded meaning, not a synthetic codebook)
`experiments/exp_graded_read_vs_attractor_ranker_v1.py` builds a codebook from **real** words with real
grounded meaning (Lancaster sensorimotor + Brysbaert concreteness, the live `grounded_similarity` asset),
projects them to a d=512 HD code (JL-preserving), and ranks candidates for each of 400 query words. Ground
truth = cosine in the 12-d grounded space (the graded distances a similarity ranker exists to preserve).

| arm (n=400 queries, 1600-word codebook, d=512) | Spearman->grounded gold | true-nearest rank-1 | hub-promotion |
|---|---|---|---|
| SIGN + ATTRACTOR  (incumbent-faithful) | 0.9855 | 0.6525 | 0.0213 |
| SIGN + POP        (readout swap only)  | 0.9855 | 0.6525 | 0.0213 |
| GRADED + ATTRACTOR                     | 0.9942 | 0.8825 | 0.0226 |
| **GRADED + POP**  (the fix)            | **0.9946** | **0.8975** | 0.0230 |
| TWIN (info-free, shuffled)             | 0.0007 | 0.0000 | -0.0119 |
| LIVE content_key hash (as it runs)     | **-0.003** (either readout) | -- | -- |

- **Readout swap = null:** POP - ATTRACTOR (same format) = **-1.4e-5, CI [-2.9e-5, +3.4e-6]** (includes
  zero). The brief's named fix -- "replace the attractor readout with a graded population read" -- buys
  nothing, because at the gate's sharp temperature the attractor already IS a population read.
- **Temperature sweep** locates where an attractor WOULD hurt a ranking: its Spearman collapses to 0.73
  at temp=0.25 (readout_delta -0.264 vs pop) but is identical to the population read at temp>=8
  (readout_delta 0.000). The live gate runs sharp (gap_detector temp=8; cleanup_family default temp=4),
  so it never enters the harmful regime.
- **Hub over-promotion is not the harm:** ~0.02 for every arm at sharp temp; the fix's 0.0230 is not below
  the incumbent's 0.0213. So bar-clause (b) is genuinely not met -- because the failure mode is absent as
  configured, quantified.
- **The real loss is the representation:** the live random-symbol `content_key` ranks grounded meaning at
  Spearman **-0.003** (noise) -- there is nothing for any readout to rank. Grounded meaning + a graded
  population read reaches **0.9946**, CI-separated above both the incumbent hash and the info-free twin,
  and lifts true-nearest rank-1 from **0.65 to 0.90** (the sign-quantiser's real cost is at the TOP of the
  ranking, even where the overall order-correlation is high). Recognition (gate exact-match AUC) stays 1.0.

## Full-stack, upstream: where the signal is lost, and that it IS brain-foundational
Per the owner's full-stack directive, tracing the ranking's inputs up the chain:
- **End component (the ranking / familiarity read):** brain-foundational as a *computation* -- a graded
  population-vector read (Georgopoulos 1986) / CA1 match comparator is the correct ranker; the attractor
  (CA3 pattern completion; Marr 1971) is correctly reserved for recall. Both already in place on disk.
- **Its INPUT (upstream signal-loss):** the familiarity cue is a RANDOM-SYMBOL HASH (`codec._sym_vec`,
  sign-quantized in `content_key`). A random hash makes two related words orthogonal, so the graded
  distances a ranking needs are not merely degraded -- they are ABSENT (Spearman -0.003). This is the
  component that is not brain-foundational: the brain's familiarity/similarity is computed over a
  similarity-structured semantic code (ATL amodal hub; Cox et al. 2024; Lynott/Connell/Brysbaert 2020),
  not an arbitrary hash. The fix is to read the ranking over GRADED GROUNDED MEANING
  (`grounded_similarity.grounded_vector`), which is a PINNED brain-foundational representation and is the
  substrate's proven-but-unwired meaning signal (`substrate_map`: "DECIDE WHAT WORDS MEAN" is BROKEN
  precisely because that signal is unwired). Prior work `the_sign_quantiser_makes_the_substrate_an_averaging_machine`
  already established the companion facts: sign() is a real averaging machine at BINDING/superposition
  sites (which `content_key` is), and grounded meaning carries the SIMILARITY axis that co-occurrence
  distributional codes miss (grounded 0.42/0.21 vs distributional 0.25/0.04 on human relatedness/similarity).

## The hdlab proposal (for the strategy session to land, Q111)
This is a map + a witnessed prototype, not a landed diff. Two changes, both LOCAL to the ranking
comparator; the store's recall/recognition path stays byte-identical:
1. **Route the grounding loop's SIMILARITY RANKING through a graded population read over grounded meaning.**
   Wherever the loop ranks candidate concepts by *relatedness* (canonicalize_fast's sense assignment;
   identify_missing_prerequisites' candidate ranking), add the grounded-meaning channel to the population
   read (convergent-cue fusion of the distributional context bundle with `grounded_vector`, per the landed
   `hdlab/convergent_cue_reader.py` Bayes-product rule) instead of ranking on the distributional/hash cue
   alone. Keep it a single-shot graded read -- do NOT introduce an attractor here.
2. **Reserve the attractor for recall only, and remove the residual signed query in the reference
   `canonicalize` fallback** (reading_grounding_loop.py:896 `np.sign(new_raw_sum)`) so the non-default path
   matches `canonicalize_fast`'s graded convention (a latent format-mismatch the module docstring at :110
   already flags). Leave `iterative_cleanup` (recall) and the gap-gate recognition untouched.
No other downstream consumer of the attractor regresses: it is only otherwise consumed by
`ca3_completer` / `hippocampal_encoder` for RECALL, which this proposal does not touch (witness A4).

## What I did NOT establish (and would withdraw first if wrong)
- I did **not** measure the positive lever on the loop's live END-TO-END grounding-quality metric
  (sense-assignment accuracy against a gold, over real read-accumulated context bundles). My ranking-
  fidelity metric (Spearman to grounded gold on real words) is a faithful proxy for "does the readout
  preserve the graded distances a ranking needs" -- the exact C7 claim -- but it is not the loop's own
  sense-assignment accuracy. **The first thing I would withdraw is any implied end-to-end grounding-
  coverage gain.** The next iteration is to run canonicalize_fast on real context bundles with vs without
  grounded fusion, against a synonym/hypernym gold, and show the sense-assignment lift with the info-free
  twin losing.
- The sign-format effect on OVERALL order-correlation is small at substrate d (+0.0092 Spearman); its real
  cost is concentrated at rank-1 (0.65->0.90). I do not claim sign is the dominant loss -- the dominant
  loss is the random-hash representation (Spearman -0.003 -> 0.99), consistent with the prior finding that
  sign is a capacity lever at binding sites, not the read-out bottleneck.

## KEY REALIZATIONS
- **Read the live path before believing the brief's mechanism.** The brief said "attractor-as-ranker over
  sign codes"; the disk said the ranking is already a graded cosine population read (GRADED_COMPARATOR ON,
  2026-08-14) and the attractor is a recognition gate. Verifying which function the DEFAULT entry actually
  calls (`canonicalize_fast`, not the signed reference) turned a build into a rigorous located negative.
- **Isolate readout from representation.** The 2x2 (format x readout) showed the readout swap is null and
  the representation is everything -- so "swap the ranker" was the wrong lever and "ground the cue" is the
  right one. The owner's rule held exactly: a brain-foundational computation (the graded read) was already
  in place; what was not brain-foundational was the INPUT it relied on (a random hash).
- **A "hub" claim needs the operating point.** The attractor over-blends a ranking only at soft temps; at
  the substrate's sharp temp it equals the population read. The phase-diagram note is literal here -- the
  harm is a temperature regime, not a fixed property.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, C7)
C7 ("cleanup_family/iterative_attractor sign()+attractor-as-RANKER, LIVE in the grounding loop, active
harm") is **overstated on the current disk** and should be re-scored: (i) the sign()-quantized primitives
are called nowhere live; (ii) the live grounding-loop ranking is already a graded population read
(canonicalize_fast, GRADED_COMPARATOR ON); (iii) the attractor is live only as an exact-match recognition
GATE (gap_detector), where a readout swap is a measured no-op (-1.4e-5, CI incl 0) and hub over-promotion
is absent at the gate's sharp temperature. The genuine residual deviation is upstream and different in
kind: the ranking/familiarity cue is a random-symbol hash with zero graded-meaning fidelity (Spearman
-0.003); the brain-foundational fix is to read the ranking over grounded meaning, not to change the readout.

---
## TLDR (plain language)
When the system reads to learn new words, it constantly asks "which thing I already know is this most
like?" The brief worried it answers that with the wrong kind of machinery -- a "snap to the nearest
memory" process that rounds everything off and distorts the ranking. I checked the live code carefully,
and that worried-about machinery has already been replaced for the ranking step: the system already ranks
by a smooth, distance-preserving comparison, and the "snap to nearest" process is only used where it
belongs, for recognising an exact word it has seen. Swapping it out changes nothing measurable. The real
problem is one step upstream: the system compares words using a meaningless random code, so two clearly
related words look totally unrelated to it. I showed that if you instead compare words by their real
grounded meaning (a signal we already have but have not plugged in), the ranking goes from essentially
random to almost perfect, without breaking the exact-word recognition. So the fix is not "change the
ranker" -- it is "feed the ranker real meaning."

## QUESTIONS
None blocking. One judgement call for the owner: I stopped at a rigorous located-negative plus a
ranking-fidelity prototype rather than building the full live end-to-end grounding-quality test (which
needs a read-accumulated corpus + a sense gold). If you want the end-to-end number before this is landed,
that is the next iteration; say the word and I will build it.

## NEXT STEPS
1. **(this problem, to reach SOLVED)** Measure the live sense-assignment lift: run `canonicalize_fast` on
   real read-accumulated context bundles WITH vs WITHOUT grounded-meaning fusion, against a synonym/hypernym
   gold, info-free twin losing -- the loop's own growth-quality metric.
2. **(hand-off to strategy, Q111)** Land the two-part proposal above: grounded-meaning graded population
   read for the similarity ranking; reserve the attractor for recall; de-sign the reference `canonicalize`
   fallback. Recall path byte-identical.
3. **(adjacent, seeds a problem)** The distributional context bundle canonicalize ranks on captures
   relatedness but not similarity (prior finding); a convergent-cue fusion (episodic context x grounded
   semantic, per convergent_cue_reader) is the higher-fidelity ranker and is the natural follow-on.
