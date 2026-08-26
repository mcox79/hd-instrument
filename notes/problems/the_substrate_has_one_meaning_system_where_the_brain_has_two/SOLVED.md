---
problem: the_substrate_has_one_meaning_system_where_the_brain_has_two
status: PARTIAL
bar: "Two can-fail claims, both CI-separated, on held-out populations with floors recomputed on them: (1) The feature-similarity system beats the associative one on SIMILARITY. On a held-out FEATURE-SIMILARITY gold (SimLex-999, or a relation-controlled similarity gold), a brain-faithful feature-similarity representation (grounding + structured/local context, distinctive-feature weighted) must beat (a) the associative/relatedness representation AND (b) the strongest real floor's UPPER bound, CI-separated, info-free twin LOSING. (2) The semantic-control gate beats a fixed blend on a MIXED population. On a population mixing relatedness and similarity items, a task-gated selection (multiplicative gain choosing the system by the query's demand) must beat the best FIXED blend CI-separated -- the gate must recover BOTH axes where the fixed blend sacrifices one. Report CI half-width + null p95 beside every margin."
result: "BAR #1 MET (feature-similarity system built + proven). On held-out SimLex-999 the distinctive-feature-weighted grounding rep (ATL: whiten away the dominant shared axis) scores Spearman rho 0.236 vs the associative co-occurrence rep 0.039 on the co-occ-covered intersection (n=573): margin +0.197 CI[0.083,0.316]. On held-out SimVerb-test3000 (n_i=1525): 0.232 vs -0.002, margin +0.233 CI[0.171,0.298]. The distinctive-feature weighting itself beats RAW grounded cosine CI-separated on both (SimLex 0.291 vs 0.245, +0.046 CI_lo 0.019; SimVerb 0.287 vs 0.264, +0.023 CI_lo 0.008) -- the brain-faithful build earns its keep. Info-free twin (shuffled grounding rows) rho ~0.014-0.016 (LOSES); concreteness floor -0.138 (SimLex) / -0.073 (SimVerb) (cleared). BAR #2 REFUTED, ROBUSTLY -> two systems better FUSED than SWITCHED (a brief-named valid outcome). Task-gate over the mixed pool beats the best fixed blend by only +0.017 CI[0.005,0.028] but TIES its random-switch control (p95 0.017). On a CONFLICT population (same pairs, similarity vs USF-association tasks) the gate does NOT separate (both systems near-chance on conflict pairs). With a genuinely STRONG associative system (wide-window PPMI-SVD, WordSim 0.338), the FIXED BLEND BEATS the gate CI-separated (gate-minus-fixed -0.026 CI[-0.048,-0.006]) and recovers both axes best (sim 0.297, rel 0.459, mean 0.378 vs feature-pure 0.309 vs gate 0.352). Fixed integration wins; task-switching does not."
floor: "BAR #1 strongest floors recomputed on each scored population: info-free twin (shuffled grounding rows) rho 0.0139 (SimLex) / 0.0159 (SimVerb) [twin_p95 0.059 / 0.034]; CONCRETENESS single-dim floor -0.138 / -0.073; FREQ-product floor (co-occ-covered subset); RAW grounded cosine 0.245 / 0.264 (the un-improved feature rep, beaten CI-sep by the distinctive-feature build). BAR #2 floor: the best FIXED blend (swept alpha, dev-fit) 0.311 (weak assoc) / 0.378 (strong assoc), plus the RANDOM-SWITCH null (p95 0.017) -- the gate does not clear either robustly."
controls: "info-free twin (shuffled grounding rows -> rho ~0.01, LOSES: excludes the whitening/z-scoring machinery manufacturing structure); paired bootstrap CIs on every margin (DFW-vs-ASSOC, DFW-vs-RAW, DFW-vs-CONCRETENESS, gate-vs-fixed); held-out splits (hyperparams fit ONLY on SimVerb-dev500; SimLex-999 + SimVerb-test3000 fully held out; gate alphas fit on dev halves); vocab-disjoint gold-blind fit (whitening covariance excludes all benchmark words); RANDOM-SWITCH gate control (task-label scrambled -> ties the gate: excludes switching-machinery-not-task-signal-pays); CONCRETENESS item-gate negative control (dual-coding hypothesis REFUTED -> co-occ is subsumed by grounding, negative-rho on abstract pairs); STRONG-associative re-test (wide PPMI-SVD -> excludes our-co-occ-rep-was-just-too-weak); CONFLICT-population test (excludes the-mixed-pool-diluted-the-effect); FEAT-vs-ASSOC on the co-occ intersection (fair same-item head-to-head)."
files_changed: "experiments/exp_feature_similarity_system_v1.py (bar #1: distinctive-feature-weighted grounding + narrow-window PPMI-SVD structured context; held-out SimLex/SimVerb; floors; twins; bootstrap CIs), experiments/exp_distinctive_feature_mechanism_v1.py (bar #1 finer drill: per-concept NONLINEAR distinctiveness vs LINEAR whitening + semantic-dementia signature), experiments/exp_semantic_control_gate_v1.py (bar #2: task-gate vs best fixed blend, mixed pool, random-switch + concreteness controls), experiments/exp_semantic_control_conflict_v1.py (brain drill: IFG control-resolves-competition on a same-pairs two-task CONFLICT population), experiments/exp_semantic_control_strongassoc_gate_v1.py (brain drill: gate re-test with a strong wide-PPMI-SVD associative system), verification/test_two_meaning_systems_feature_similarity_and_gate.py (scaffold-free witness), data/exp_feature_similarity_system_v1/metrics.json, data/exp_distinctive_feature_mechanism_v1/metrics.json, data/exp_semantic_control_gate_v1/metrics.json, data/exp_semantic_control_conflict_v1/metrics.json, data/exp_semantic_control_strongassoc_gate_v1/metrics.json. NO hdlab/ modified."
reverify: ".venv/Scripts/python.exe verification/test_two_meaning_systems_feature_similarity_and_gate.py"
---

# What I built and what I measured

**The brain frame (opening move).** The brain has two similarity systems: the **ATL amodal hub** computes
FEATURE/correlational similarity weighted toward **DISTINCTIVE** features (Rogers & McClelland; Patterson,
Nestor & Rogers 2007; Lambon Ralph controlled-semantic-cognition), and a distributed **LIFG/pMTG** system
computes **ASSOCIATIVE** relatedness from broad context. **Semantic control (IFG)** applies a task-gated,
roughly multiplicative gain that selects between them. The substrate has the associative system (co-occurrence)
and lacks the feature system. I built the feature system and tested the gate.

## BAR #1 -- the feature-similarity system (SOLVED)

The carrier `hdlab/grounded_similarity.py` (11 Lancaster sensorimotor + Brysbaert concreteness, z-scored,
~36.8k words) has the right signal but its own docstring MEASURES the wrong metric: raw cosine cannot separate
a true synonym from a perceptually-similar sibling (apple/orange 0.952 ~ sofa/couch 0.968), because a
**dominant shared axis** (concreteness / general perceptual salience; top PC = **26.7%** of variance) swamps
the discriminating dims. That is precisely the ATL's job description in reverse. The brain-faithful fix is the
ATL's actual computation -- **privilege distinctive features / suppress the shared ones** -- which on a
continuous feature space is **decorrelation: WHITEN away the shared covariance** (equivalently, drop the top
shared axes and equalise the rest). This is a REPRESENTATION-level operation, not a read-out format (the
sign/graded/sparse family was already refuted).

- **Distinctive-feature weighting beats raw grounding**, CI-separated, on both held-out similarity golds:
  SimLex-999 rho 0.291 vs 0.245 (+0.046 CI_lo 0.019); SimVerb-test3000 0.287 vs 0.264 (+0.023 CI_lo 0.008).
  And it LOWERS relatedness (WordSim 0.409 -> ~0.40) -- the exact brain signature (specialises toward
  "alike-in-kind"). Hyperparameter (drop-k / whiten) fit ONLY on SimVerb-dev500; both similarity test sets
  fully held out. The whitening covariance is fit gold-blind and vocab-disjoint (benchmark words excluded).
- **The feature system beats the ASSOCIATIVE rep on similarity**, CI-separated, on the fair same-item
  intersection: SimLex +0.197 CI[0.083,0.316]; SimVerb +0.233 CI[0.171,0.298] (n_i 573 / 1525). Info-free
  twin loses; concreteness and frequency floors cleared.
- **Structured local context (secondary):** a narrow-window (+/-2) PPMI-SVD "linguistic spoke" (Levy &
  Goldberg 2014: local context -> functional similarity; PPMI = the same privilege-distinctive principle)
  fused with whitened grounding gives a small dev gain (alpha=0.25, dev rho 0.338 -> 0.351) on the corpus-
  covered subset; grounding carries the primary, full-coverage claim.

**Finer drill (owner-directed "drill ever finer for brain fidelity"): is the faithful op LINEAR whitening
or a PER-CONCEPT NONLINEAR distinctiveness?** The sharper neuroscience is per-concept and nonlinear -- a
concept's distinctive features are the dims where IT deviates from the prototype, and semantic dementia
loses those FIRST (zebra -> horse over-regularisation). I tested an expansive nonlinearity in the whitened
space, `sign(z)*|z|^p` (p>1 emphasises distinctive/deviant dims), sweeping p on SimVerb-dev500.
**Result: LINEAR whitening is sufficient -- p=1.0 is dev-optimal; the nonlinear emphasis does NOT beat it
CI-separated on either held-out set (delta 0.000), and the semantic-dementia SIGNATURE does NOT reproduce
(the synonym-minus-sibling margin FALLS as distinctiveness rises: 0.106 at p=0.25 -> 0.052 at p=3.0, the
opposite of the prediction).** The brain-foundational read is a FIDELITY BOUNDARY, not a failure: a 12-dim
CONTINUOUS grounding space is too coarse to carry the rich "few-concepts-have-this-feature" binary
structure the McRae/ATL distinctiveness account assumes, so linear decorrelation already captures the
distinctiveness that exists and a per-concept nonlinearity just amplifies outlier dims. Getting finer
requires a RICHER FEATURE SUPPLY (more sensorimotor modalities / actual feature norms), not a fancier
transform -- which is where the next fidelity gain lives.

## BAR #2 -- the semantic-control gate (REFUTED in favour of fixed integration)

I built the task-gated multiplicative gain (per-task alpha on the associative contribution, task = the
INSTRUCTION "judge similarity" vs "judge association", never the gold) and tested it three ways. **All three
say the two systems are better FUSED than SWITCHED** -- the brief's explicitly-named valid outcome for a #2 loss:

1. **Mixed pool (SimLex sim + WordSim rel).** Gate beats the best fixed blend by only **+0.017 CI[0.005,0.028]**
   but **TIES its random-switch control** (p95 0.017) -- the win is per-block alpha flexibility, not the task
   signal specifically.
2. **Conflict population** (same SimLex pairs, similarity vs USF-association tasks; the IFG mechanism is
   *conflict resolution*, so it should bite hardest where the two golds disagree). On AGREEMENT pairs
   gate=fixed (0.597, no switching needed). On CONFLICT pairs **both** systems collapse to near-chance
   (gate 0.032, fixed 0.047) so control has nothing to arbitrate; interaction -0.014 CI[-0.113,0.087] (null).
3. **Strong associative system** (wide-window PPMI-SVD, WordSim 0.338 -- genuinely strong, not the lossy
   d=256 bundle). Now the **FIXED BLEND BEATS the gate CI-separated** (gate-minus-fixed **-0.026
   CI[-0.048,-0.006]**) and recovers both axes best (sim 0.297, rel 0.459). Integration wins; switching loses.

**The brain-grounded reason (not an exhausted-engineering wall), sharpened by the drills.** The IFG gate's
operation -- resolve COMPETITION / SELECTION -- is CONTEXT-DRIVEN: it uses the current context/goal to bias
which representation wins. A **decontextualised word pair gives it nothing to gate on**: the only "context"
my benchmark supplies is the coarse task label (similarity vs association), and a task label is not a context
that disambiguates a competition. The conflict drill makes this concrete -- on the pairs where the two systems
most disagree, BOTH collapse to near-chance (there is no signal for control to arbitrate WITHOUT context), so
the gate cannot help. And with a strong associative system a **fixed multiplicative integration** already
captures the benefit and beats switching. So the precise statement is: *for context-free, graded
similarity/relatedness RATING, semantic control has no context to act on and fixed integration is the faithful
operation; the gate needs a task where CONTEXT selects among competing senses* (homonym WSD -- "bank" near
"river" vs "money"). **I deliberately did NOT build that WSD test here: it is owned by the `reader_meaning_channel`
brief (whose `exp_context_conditioned_sense_selection_v1/v2` already HARD_FAILED), and building it would compete
with filed work.** The honest boundary of THIS brief: the feature system is built and proven; the two systems
are best fused, not switched, for decontextualised rating; and the gate's proving ground is a context-selection
task owned elsewhere.

## The actual answer to "one system where the brain has two"

The deliverable is not a switch. It is (a) the missing **feature-similarity system**, built brain-faithfully
(distinctive-feature-weighted grounding + structured local context), which beats the associative rep on
similarity CI-separated; and (b) the finding that the two systems, once both are strong, are best combined by
**fixed integration** (a per-pair multiplicative fusion), which recovers BOTH axes better than either system
alone (mean 0.378 vs feature-pure 0.309 vs associative-pure 0.338). Wire the feature system and the fixed
fusion; do NOT wire a task-switch gate for graded rating.

## KEY REALIZATIONS

- **The grounding organ's own documented failure IS the ATL's job description.** Its docstring measures that
  raw cosine can't separate apple/orange from sofa/couch because a dominant shared concreteness axis swamps
  the distinctive dims -- which is exactly "the ATL privileges distinctive features" stated as a bug. The fix
  was already named by the brain; whitening is that fix in the continuous-feature analog. (Read the carrier's
  own honesty section before reaching for a new mechanism.)
- **Distinctive-feature weighting is decorrelation, not a read-out format.** The refuted sign/graded/sparse
  family all operated on the read-out; the win here is at the REPRESENTATION -- suppress shared covariance.
  Different-in-kind from what was already swept.
- **The gate's null survived every attempt to rescue it, which is the finding.** The decisive move was to
  strengthen the COMPETITOR (a real wide-PPMI-SVD associative system) rather than tune the gate: with a strong
  second system, fusion beat switching MORE clearly, not less. A shared wall across weak-assoc / conflict /
  strong-assoc means switching is genuinely the wrong operation for graded rating -- not that I under-tuned it.
- **Same pairs, two golds is the cleanest gate test.** SimLex ships both a similarity and a free-association
  rating on identical pairs; using both holds vocabulary/frequency/difficulty fixed so ONLY the task varies --
  the perfect control for a task-gating claim.
- **Drilling the mechanism finer told me WHERE fidelity is supply-limited, not transform-limited.** The
  per-concept nonlinear distinctiveness (the sharper ATL/semantic-dementia account) did NOT beat linear
  whitening and the zebra->horse behavioural signature did not reproduce -- because 12 continuous grounding
  dims lack the rich binary-feature structure that account assumes. The lesson: when a finer-fidelity MECHANISM
  stops paying, the next fidelity gain is usually in the SUPPLY (richer features), not a cleverer operation.
- **The gate's null is a statement about the TASK, not the mechanism.** Semantic control is context-gated;
  a context-free word pair offers no context to gate on, which is WHY fixed integration wins. The mechanism
  isn't wrong -- it is being asked to work where its input (context) is absent.

## AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **Tier-2 "Sensorimotor spokes / Amodal concept hub" -- the RIGHT-OP-WRONG-METRIC deviation now has a fix
   and a number.** The measured ceiling (raw cosine can't separate synonym from sibling; apple/orange 0.952)
   is a MISSING DISTINCTIVE-FEATURE WEIGHTING. Whitening the grounding space (suppress the top shared axis,
   27% of variance) beats raw grounding CI-separated on SimLex (+0.046) and SimVerb (+0.023) and specialises
   it toward similarity (relatedness drops). The ATL "unweighted feature overlap is the INVERSE of privileging
   distinctive features" note (`lexical_similarity.py`) applies equally to the grounding carrier and now has a
   concrete, held-out-proven correction. FINER (exp_distinctive_feature_mechanism_v1): the faithful op AT THIS
   FIDELITY is LINEAR decorrelation -- a per-concept NONLINEAR distinctiveness (the sharper semantic-dementia
   account) does NOT add on a 12-dim continuous grounding space and the zebra->horse signature does not
   reproduce; that space lacks the binary few-concepts-have-it structure, so the next distinctiveness gain is
   a richer feature SUPPLY, not a fancier transform.
2. **Semantic control (IFG) -- the THIN deviation is DECISION-RELEVANT: for graded similarity/relatedness the
   faithful operation is FIXED multiplicative INTEGRATION, not a task-SWITCH.** A task-gate does not beat a
   fixed blend even with a strong associative system (gate-minus-fixed -0.026 CI[-0.048,-0.006]) or on conflict
   pairs. The gate's competition/selection mechanism needs a genuine-selection task (WSD) to bite; it should
   NOT be wired for graded rating. Re-point the "semantic control THIN" gap: the near-term win is the fixed
   two-system fusion; the gate is a later, selection-task deliverable.
3. **The two-similarity-systems row (from the sign_quantiser drill) is CONFIRMED and BUILT:** feature system =
   distinctive-feature-weighted grounding (+ narrow-window PPMI); associative system = wide-window co-occurrence /
   PPMI-SVD. The feature system is the genuinely-missing one; the associative system, when built strongly
   (wide PPMI-SVD, WordSim 0.338), is complementary and best FUSED, not switched.

## WHAT I DID NOT ESTABLISH (withdraw first if wrong)

- The structured-context (narrow PPMI-SVD) contribution is SMALL and only on the corpus-covered subset; I did
  NOT establish it adds beyond whitened grounding on full coverage. Grounding carries the bar-#1 claim.
- I did NOT test the gate on a genuine SELECTION task (homonym WSD). My claim is only that the gate does not
  beat fixed integration on graded similarity/relatedness RATING. The gate may still be the right mechanism for
  selection/interference tasks -- that is the named next step, not a closed door.
- The whitening transform is fit on the Lancaster/Brysbaert norm population; it is gold-blind but I did not
  test transfer to a grounding source built differently (e.g. learned sensorimotor spokes).
- SimVerb is verbs and SimLex is mixed POS; both are held out, but I did not build a relation-controlled
  similarity gold beyond these standard benchmarks.

## PROPOSED hdlab CHANGE (strategy lands it; Q111)

1. **Wire the distinctive-feature transform into the grounding carrier** as an optional default-off
   `distinctive=True` path on `grounded_similarity` / `lexical_similarity`'s grounded fallback: whiten the
   z-scored grounding vector (population covariance, gold-blind) before cosine. It beats raw grounding CI-
   separated on similarity; keep the existing raw path for relatedness. (A representation option, gated on the
   held-out SimLex/SimVerb margins, not a capability claim.)
2. **For a two-system meaning read-out, use FIXED multiplicative INTEGRATION** (per-pair z-fusion of the
   whitened-grounding cosine and a wide-PPMI-SVD associative cosine), NOT a task-switch gate. It recovers both
   axes (mean 0.378) better than either system alone.
3. **Do NOT wire a semantic-control task-switch gate for graded rating.** File it as a future deliverable
   contingent on a genuine-selection task (WSD / homonym disambiguation) where competition actually exists.

## TLDR (plain language)

Our system was good at telling which words go together (dog-leash) and bad at telling which words are alike
in kind (dog-wolf) -- the brain has two separate machineries for these and we only had the first. I built the
missing one, brain-faithfully. The key was noticing that our sensory-grounding data already contains the right
information but a single loud "how concrete/vivid is this word" signal drowns out the fine distinguishing
details; the brain's known trick is to turn DOWN the shared signal and turn UP the distinguishing ones, and
doing exactly that made the system markedly better at "alike in kind" -- clearly and repeatably, on words it
was never tuned on. I then tested whether a "switch" that picks the right machinery per question helps. It
does not: it is better to always BLEND the two machineries with a fixed recipe than to switch between them --
and this held up even after I made the second machinery much stronger and even on the hardest disagreeing
pairs. The brain's switch (which lives in the frontal lobe) is for questions where you must actively suppress
a competing meaning; a plain "how similar/related are these two words" rating is not that kind of question, so
a fixed blend wins. Net: the missing machinery is built and proven; the right way to combine the two is a
fixed blend, not a switch.

## QUESTIONS

None blocking. One call for the strategy session: I filed this PARTIAL -- bar #1 (feature system) is met
CI-separated; bar #2 (the gate) is a rigorous, robust NEGATIVE that the brief itself names as a valid outcome
("better fused than switched"). If you prefer, it reads as SOLVED-with-a-refuted-half; I chose PARTIAL to keep
the unmet gate claim visible.

## NEXT STEPS

1. Wire the distinctive-feature (whitening) transform + the fixed two-system fusion (proposed diff above).
2. Build a relation-controlled similarity gold (or add SimVerb dev/test into the standing meaning metric) so
   the feature system is scored on its own axis, not taxonomic WordNet.
3. If a semantic-control gate is still wanted, build it on a GENUINE-SELECTION task (homonym WSD / lexical
   ambiguity), where the IFG's suppress-the-competitor operation actually has competition to resolve -- that is
   where a task-switch should finally beat a fixed blend.
4. Enrich the feature space beyond 12 grounding dims (more modalities / learned spokes) -- the distinctive-
   feature transform's ceiling is set by how many discriminating dims exist to privilege.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT (owner-DONE); verdict PARTIAL. Full SOLVED re-read FRESH per the standing rule (the solver added the finer nonlinear-distinctiveness drill + the strong-associative gate re-test since the earlier WIP read). Re-verified scaffold-free FIRST-HAND (test_two_meaning_systems_feature_similarity_and_gate.py PASS: SimLex DFW 0.2907 vs RAW 0.2449 d=0.0458 CI_lo 0.0187 twin 0.0139; SimVerb DFW 0.2865 vs RAW 0.2638 d=0.0227 CI_lo 0.0083; both bars). BAR #1 MET: the missing FEATURE-SIMILARITY system built brain-faithfully = the ATL's "privilege distinctive features" as DECORRELATION (whiten the dominant shared concreteness axis, top PC 26.7%); beats raw grounding CI-separated on two held-out golds + lowers relatedness (the brain signature); a REPRESENTATION-level op, different-in-kind from the refuted read-out family. FINER DRILL = a fidelity BOUNDARY (linear whitening sufficient; nonlinear per-concept distinctiveness doesn't add on 12-dim continuous space; next gain = richer feature SUPPLY). BAR #2 REFUTED robustly (fixed FUSION beats the task-SWITCH even with a strong associative system; the gate ties its random-switch control) -> for graded rating the faithful op is fixed multiplicative integration; the IFG gate needs a genuine SELECTION task (WSD) to bite. 3 AUDIT UPDATEs folded into BRAIN_FOUNDATIONAL_AUDIT.md (Tier-2 ATL whitening fix+number; semantic-control re-pointed to fixed fusion; two-systems row confirmed+built); §8 lever #1 marked DELIVERED. Review + SOLVER REVIEW block in PROBLEM.md; priority cleared. hdlab landing EARNED (whitening transform default-off on the grounding carrier + fixed two-system fusion) -> queued as a focused default-off landing with its own witness; measure on the live read-out before any capability claim. NO hdlab landing yet. Committed (no push).
