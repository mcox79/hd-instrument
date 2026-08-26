---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT for problem: the_sign_quantiser_makes_the_substrate_an_averaging_machine
STATUS: PARTIAL  (read-out regime REFUTED; binding regime CONFIRMED-but-LATENT, coupled to B4)
LEDGER: python tools/problem_ledger.py --check  ->  malformed/incomplete: 0
NOTE TO STRATEGY: you already integrated the READ-OUT half (as REFUTED-VALUABLE). This submission
  ADDS two regimes filed AFTER that integration — the BINDING drill and the LIVE VERIFICATION — which
  move the verdict to PARTIAL. A SOLVER ADDENDUM is appended to SOLVED.md flagging exactly what to
  re-fold. Your read-out integration stands; these are additive.

REVERIFY (scaffold-free headline; deterministic reproducers write only their own dirs):
  .venv/Scripts/python.exe verification/test_sign_quantiser_not_the_bottleneck_on_hit1.py    <- headline
  .venv/Scripts/python.exe experiments/exp_superposition_capacity_binding_v1.py --mode full   <- binding
  .venv/Scripts/python.exe experiments/exp_live_binding_load_signgap_v1.py --mode full         <- live check

================================================================================
THE BAR (verbatim, PROBLEM.md §7)
================================================================================
"On a REAL downstream task (open-vocabulary read-out hit@1, or the meaning/recall instrument -- NOT a
bare 2AFC), on a held-out population with all floors recomputed on it: the graded (non-sign) path must
beat the sign'd path CI-separated over the strongest floor's UPPER bound (include the constant/prototype
floor), info-free twin LOSING, with the CI half-width and null p95 reported beside the margin. Sweep
WHICH sites are made graded (the whole point is to find where strength matters) and report the capacity
cost (does superposition collapse below B=4?)."

================================================================================
THE ANSWER IN ONE LINE
================================================================================
The brief's instinct about the OPERATION was right, but it named the wrong PLACE. `sign()` is NOT the
averaging machine at the READ-OUT (refuted; the loss there is a measurement-axis + supply + structure
matter). It IS an averaging machine at BINDING for CORRELATED codes (confirmed) -- but that does NOT
bite in the LIVE substrate today (atomic codes, load <=4), and becomes real only when binding is made
brain-faithful (graded/semantic fillers). So it is a LATENT liability COUPLED to the graded-code (B4)
fidelity fix, not a current bug and not a standalone win.

================================================================================
REGIME 1 — READ-OUT (REFUTED).  Instrument: C3 open-vocab hit@1, n=4000, 5491 anchors, WordNet gold
================================================================================
- graded vs sign = +0.0015 CI[-0.0055,+0.0083] NULL (ci_hw 0.0069, null_p95 0.0068). (2AFC +0.0602 is
  2AFC-only; does not transfer -- confirmed.)
- Best faithful format arm DN_CENTER (divisive normalisation) 0.0537 vs sign 0.0465 = +0.0073
  CI[+0.0000,+0.0145] (null_p95 0.0072 -- WITHIN NOISE, seed-flips); twin loses robustly.
- The WHOLE brain-faithful code-format family (sign, graded, divisive-norm read-out/composition/IDF,
  in-place sparse, DG expansive-sparse 256->2048 k-WTA) lands 0.029-0.062 -- ALL 0.09-0.14 CI-BELOW the
  best-constant floor 0.171. The averaging machine BEATS every per-item read-out.
- Self-supervised brain-faithful CBOW (predict-masked-word, delta-rule, co-learned rep) = 0.043 ~= the
  co-occurrence cosine 0.048 (delta -0.0053, CI incl 0) -- Levy&Goldberg: CBOW-NS factorises the same
  PMI. Only a SUPERVISED linear associator (WordNet labels the brain never gets) beats it: 0.108.
- CAPACITY (d 256->1024): read-out +0.010 > any format gain. Format is not the read-out lever.

FLOORS (read-out, recomputed on population): BEST_CONSTANT ("change") 0.1710 (d-independent, strongest);
nearest-centroid PROTOTYPE 0.1388 ("work", BRITTLE -> 0.0 at d=1024, do not lean on it); POPULARITY
0.0185; SCRAMBLE(info-free) 0.008; RANDOM 0.010.

FINER DRILLS (owner-directed -- "is the MEASUREMENT brain-foundational?"; WordNet-INDEPENDENT human
ratings; freq floor + shuffled twins ~0; intersection n=213 WordSim / 573 SimLex):
- DRILL 1: the "failed" distribution CAPTURES human RELATEDNESS (WordSim rho: CO_OCC 0.25, CBOW 0.21)
  but NOT SIMILARITY (SimLex 0.04, 0.03). It was graded on the WRONG axis -> partly a MEASUREMENT
  artifact.
- DRILL 2: GROUNDED (sensorimotor) captures both and best (WordSim 0.42, SimLex 0.21). FUSION
  (dist+grounded) beats grounded on relatedness (0.431>0.417) but HURTS similarity (0.160<0.207) ->
  the two similarity systems need TASK-GATING (semantic control/IFG), not a fixed blend. (Consistent
  with landed exp_ownmetric_frequency_controlled_v1: grounded 0.744 vs PPMI floor 0.555 on ConceptNet.)
- DRILL 4: the SIMILARITY axis is recovered by brain-faithful STRUCTURE, not any read-out format --
  narrowing CBOW context bag->window lifts SimLex 0.075 -> 0.088 -> 0.100 -> 0.112 (window 0/5/2/1)
  while trading relatedness 0.282->0.262 (Levy&Goldberg topical-vs-functional, reproduced).

================================================================================
REGIME 2 — BINDING / SUPERPOSITION (CONFIRMED synthetic, then LIVE-VERIFIED as LATENT)
================================================================================
DRILL 5 (exp_superposition_capacity_binding_v1; MAP-VSA, 512-filler cleanup, 300 trials, d=256;
shuffle floor at chance 1/512; self-test: B=1 inverts, shuffle->chance, capacity degrades with load):
  d=256 CORRELATED fillers, GRADED vs SIGN recovery:  B4 1.00/0.92  B6 0.98/0.73  B8 0.88/0.58
  B12 0.67/0.36 (all gaps CI-separated).  Capacity cliff (acc>=0.5): B*=8 (sign) -> 12 (graded).
  Mean graded-minus-sign gap CORRELATED +0.146 vs RANDOM +0.080.  At d=1024 both hold through B16
  (capacity scales with dims).  => sign() lowers correlated-code capacity ~50% at d=256. The brief's
  "collapse below B=4" is beaten; sign() needlessly caps it.

LIVE VERIFICATION (exp_live_binding_load_signgap_v1; real StructuralEncoder over curriculum text,
n=6,020 encodings) -- does it bite live?
- NO reachable on-stream site meets B>4 AND correlated AND sign(): the only correlated-code binder
  (StructuralEncoder) has mean B=2.85 (median 3, max 15, 14% of encodings B>4), is already GRADED by
  default, and is islanded; the live sign()+high-B site (hd_fact_store, B=5-6) binds role-HETEROGENEOUS
  fillers, not similar concepts.
- WHY: the substrate binds ATOMIC RANDOM symbols (symbol_vector) -> fillers near-orthogonal (pairwise
  |cos| 0.06). The SAME fillers under a brain-faithful graded-semantic code are CORRELATED (|cos| 0.25).
- RECOVERY GAP at the live load: ATOMIC (current) +0.013 overall, ~0 for B<=4 -> SAFE TODAY.
  SEMANTIC (brain-faithful) +0.044 overall, +0.087 on the B>4 tail -> OPENS UP.
- VERDICT: SIGN_SAFE_TODAY_BUT_BITES_IF_BINDING_MADE_FAITHFUL. The binding sign() is a LATENT averaging
  machine COUPLED to the graded-semantic-code (B4) fix: ship graded fillers with a signed bundle and
  you re-create the averaging machine, worst on the 14% B>4 tail.

================================================================================
CONTROLS (what each excluded)
================================================================================
- info-free twin (deranged query) -- every read-out arm's real >> scramble 0.008 CI-sep; twin does NOT
  reproduce the divnorm gain (excludes item-difficulty/base-rate).
- best-constant + nearest-centroid + popularity + random floors, all recomputed on population.
- d-sweep 256->1024 separates FORMAT from CAPACITY.
- byte-identity self-test: equal-weight composition builder == context_vector_masked (IDF arm differs
  ONLY by weight).
- learned-associator: 50/50 train/test split (no leak), held-out eval.
- DRILLS: Spearman on WordNet-INDEPENDENT human ratings; freq-product floor ~0; shuffled-vector twins
  ~0; common intersection (fair head-to-head); context-window is the ONLY variable in the structure drill.
- BINDING: shuffle-bundle floor at chance 1/512; RANDOM-vs-CORRELATED isolates correlation; bootstrap CI
  on the gap per B; self-test.
- LIVE: real StructuralEncoder load measured; ATOMIC (current) vs SEMANTIC (faithful) filler codes is
  the only variable; gap stratified by B<=4 vs B>4.

================================================================================
BRAIN-FOUNDATIONAL LABELLING (PINNED vs OUR-INVENTION)
================================================================================
PINNED, confirmed: additive combination (the SUM is faithful); divisive normalisation as pooling op
(direction-correct, minor lever); two similarity systems (ATL feature-similarity vs LIFG/pMTG
associative -- now quantified on our reps); working-memory superposition capacity ~4-7 (Cowan/Miller);
grounding as the feature-similarity supply.
OUR-INVENTION-UNDER-TEST -- REFUTED: "the terminal sign() is the READ-OUT bottleneck / an averaging
machine on real tasks" (null; format-invariant; averaging floor beats the read-out); "divisive norm at
read-out is a capability lever" (within noise); "unsupervised learning fixes it" (CBOW ties counting).
OUR-INVENTION-UNDER-TEST -- CONFIRMED but LATENT: "sign() collapses CORRELATED superposed bound codes"
(true; cliff B*=8->12) -- but the live substrate dodges it with ATOMIC codes at sub-cliff load, so it
activates only under the B4 graded-code fidelity fix.

================================================================================
AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
================================================================================
1. Deviation #2 (sign quantiser): "graded flags default-OFF" is STALE -- HD_GRADED_COMPARATOR defaults
   "1" (ON) since 2026-08-14; comparator field+query already graded; the only unconditional live read
   sign is canonicalize():896 (banking), ~0 cost. Re-point S8 leverage lever #1 ("sign->graded") DOWN
   for the read-out.
2. Deviation #2 is COUPLED TO B4 AT THE BINDING SITES (new): flipping the read-out is null, but a signed
   bundle over graded/semantic fillers re-creates the averaging machine (+0.044, +0.087 on B>4). When B4
   makes fillers graded/semantic, the sign()-on-a-bundle sites (situation_focus, role_slot_summarizer,
   event_bundle, CA3 cleanup) MUST go graded in the SAME change. Not before, not standalone.
3. NEW two-similarity-systems row: distribution = associative relatedness (WordSim 0.25, SimLex 0.04);
   grounding = both (0.42/0.21). WordNet TAXONOMIC gold under-credits the associative channel -> prefer
   human relatedness/similarity or a relation-controlled gold. Similarity axis recovered by
   structure/grounding, not read-out format. The THIN "semantic control" deviation now has a measured
   need (task-gating; fixed fusion hurts similarity).
4. S7 bounded: on this instrument the unsupervised distribution alone does not place the specific gold
   meaning first; supply/grounding required. B2 divisive-norm: minor lever on a real task. B4: in-place
   sparse and DG-expansive do NOT beat dense on open-vocab (the DG win is episodic recall).
5. CORRECTION: the reading corpus here (load_corpus_v5) is MODERN (OneStopEnglish + OpenStax biology +
   science articles; explicit "stop mcguffey"), NOT McGuffey/archaic -- corpus-age is not the confound.

================================================================================
PROPOSED hdlab CHANGE (strategy lands; board Q111)
================================================================================
1. Do NOT flip sign() for a CURRENT win -- null everywhere live (read-out null; binding ~0 at load <=4,
   atomic codes). Keep GRADED_COMPARATOR default-ON (already is).
2. COUPLED GUARDRAIL: when B4 makes binding fillers graded/semantic, make the superposition BUNDLE graded
   in the same change, gated on exp_live_binding_load_signgap_v1 / exp_superposition_capacity_binding_v1.
3. Optional default-OFF read-out micro-win: freeze_graded(normalise="center") as a ReadoutConfig option
   (direction-correct +0.007, twin-losing) -- an option, never a capability claim.
4. RE-POINT effort to SUPPLY + the two-systems build: stop grading meaning against WordNet taxonomic gold
   alone; build feature-similarity from grounding + structured/local context; add semantic-control gating.
   (Already packaged as `the_substrate_has_one_meaning_system_where_the_brain_has_two`.)

================================================================================
KEY REALIZATIONS (the enabling moves)
================================================================================
- Disk outranked the brief: GRADED_COMPARATOR was already ON; the "flip" was largely landed and null.
- The floor no one computed flipped the framing: the best-constant "change" (0.171) BEATS every per-item
  read-out -- it's a signal-extraction failure, not a quantiser artifact.
- Supervised vs SELF-supervised split (drill finer) turned "learning gap" into "SUPPLY gap": the faithful
  self-supervised learner ties counting (Levy&Goldberg); only WordNet labels beat it.
- Doubt the TARGET, not just the method: WordNet is taxonomic; the substrate was carrying the associative
  system. Human-rated relatedness/similarity turned "signal absent" into a two-systems map.
- A refuted mechanism can be MIS-LOCATED: testing the OTHER regime (binding) found sign() real there.
- Construction-proof != capability: the live check turned a synthetic binding "win" into a LATENT coupled
  guardrail -- and prevented an unsupported "flip binding sites" recommendation.

================================================================================
WHAT I DID NOT ESTABLISH (withdraw first if wrong)
================================================================================
- The supervised 0.108 is a DIAGNOSTIC (WordNet labels), not the brain's and not a capability.
- The self-supervised CBOW carries 4 named fidelity divergences not drilled out (order-blind bag, random
  negatives vs lateral inhibition, two matrices, sigmoid vs divisive-norm gain); theory says they won't
  clear the floor, but #1 (order/sequence) is the first to try.
- Binding held fixed at MAP-VSA; the brain's binding OPERATION is unpinned/3-way contested -- other
  bindings may cliff differently. The live liability is confirmed as CONDITIONAL on B4 being adopted;
  I did NOT land B4 or the graded bundle.

================================================================================
DO NOT QUOTE
================================================================================
- Do NOT quote the 2AFC +0.0602 as evidence graded fixes the system (2AFC-only).
- Do NOT quote the supervised associator 0.108 as "learning solves it" (WordNet labels).
- Do NOT quote the binding cliff B*=8->12 as a CURRENT live win -- it is LATENT (gap ~0 live today).
- Do NOT quote the nearest-centroid PROTOTYPE floor (0.1388) -- brittle; use best-constant 0.171.
- No number crosses instruments (read-out hit@1 vs 2AFC vs human-rating rho vs binding recovery).

================================================================================
FILES
================================================================================
experiments/exp_divisive_normalisation_readout_v1.py       (format sweep + floors + twin + d-sweep)
experiments/exp_learned_readout_probe_v1.py                (supervised linear associator)
experiments/exp_predictive_learner_readout_v1.py           (self-supervised CBOW)
experiments/exp_taxonomic_vs_thematic_gold_v1.py           (DRILL 1+2: human ratings + grounding + fusion)
experiments/exp_structured_context_similarity_v1.py        (DRILL 4: structure recovers similarity)
experiments/exp_superposition_capacity_binding_v1.py       (DRILL 5: binding capacity, sign vs graded)
experiments/exp_live_binding_load_signgap_v1.py            (LIVE VERIFICATION)
verification/test_sign_quantiser_not_the_bottleneck_on_hit1.py   (scaffold-free witness, PASS)
data/exp_*/metrics.json for each.  NO hdlab/ modified.

================================================================================
PLAIN-LANGUAGE TLDR
================================================================================
We suspected a shortcut buried at the end of almost every step -- keeping only "positive or negative"
and throwing away "how strong" -- was quietly making the system always guess the average, generic word.
On the reading/understanding task that's wrong: keeping the strength makes no difference, and the system
already keeps it. The real trouble there is subtler -- we were grading it on "name a dictionary cousin"
(dog->wolf) when what reading actually learns is "name a related thing" (dog->leash); those are two
different kinds of meaning and the brain has two systems for them. The "alike-in-kind" kind is recovered
by looking at a tight window of nearby words and by grounding words in the senses, not by any reading
trick. BUT the original worry was partly right, just in the wrong place: when the system has to hold
several SIMILAR facts in memory at once, the shortcut really does smear them into the average -- keeping
the strength lets it hold ~12 such facts instead of ~8 (human working-memory range). We then checked the
live system and found it dodges this today only because it stores memories as unrelated random tags, not
as real meanings -- so the moment we make memory more brain-like, the shortcut starts smearing again. The
fix "keep the strength" is real, but it must be turned on TOGETHER with making the codes meaningful; on
its own, today, it changes nothing.

QUESTIONS: none blocking. One call for you: I filed PARTIAL (read-out refuted; binding real-but-latent);
a reviewer could file the read-out half alone as REFUTED, but that drops the binding + coupling result.

NEXT STEPS: (1) re-fold the binding + live-verification regimes (SOLVER ADDENDUM in SOLVED.md); (2) stop
grading meaning against WordNet taxonomic gold alone; (3) build the two-similarity-systems + grounding +
semantic-control gating (already packaged); (4) couple any graded-bundle change to the B4 graded-code fix;
(5) optional default-off center_field read-out micro-win.
