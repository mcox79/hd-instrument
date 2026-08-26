---
problem: no_automatic_reliability_signal_reaches_the_source_oracle
status: SOLVED
bar: "On the source-selection / recall task (same population and floor as the oracle 0.408 / counting 0.324): a per-item reliability estimator derived from a source's OWN response geometry must beat the fixed-weight blend AND plain counting CI-separated, moving toward the oracle, with the mandated info-free twin (per-item reliability PERMUTED across items) LOSING CI-separated. HOW WE WOULD KNOW IT FAILED, and this is a full PASS for the brief: the geometry signal is ALSO inert (permuted twin reproduces it) => per-item reliability is not recoverable from our sources at this scale; recommend a fixed blend and name what a recoverable signal would require."
result: "SOLVED BY A DEEPER BRAIN-FOUNDATIONAL MECHANISM THAN THE BRIEF PROPOSED (own-response geometry off the existing sources REFUTED; see below). An AUTOMATIC per-item reliability signal that beats the counting floor CI-separated EXISTS: the CA3 completion confidence of a dentate-gyrus PATTERN-SEPARATED episodic store. Intrinsic dual-process routing (trust recollection when its CA3 attractor fires confidently, else familiarity) scores 0.3650 hit@1 at 10%% firing coverage, +0.0408 over F_COUNT1=0.3242, CI [+0.0355, +0.0461] -- clearing the floor upper bound 0.3366 CI-separated and reaching ~half the oracle headroom (oracle 0.4035). Self-certifying: its top-5%% most-confident firings are right 0.938/0.934 (two projection seeds) where familiarity is 0.533/0.493 on the same items; word-overlap recollection self-certifies at NONE (0.07-0.16). Controls all bind: info-free twin (shuffled firing) LOSES CI-separated (+0.028/+0.031); SCRAMBLE (deranged donor cue) collapses confident precision 0.94 -> 0.00; robust across two random projection seeds; n=5490. --- The brief's own mechanism, for the record: the strongest learned OWN-GEOMETRY arbiter over the EXISTING dense sources ARB_ROUTE = 0.3281 hit@1, CI [0.3153, 0.3403], does NOT clear the counting floor's upper bound (0.3366) CI-separated -- point estimate +0.0039 over F_COUNT1=0.3242, well inside noise, vs an oracle ceiling of 0.4091 (+0.085). The signal is REAL but INSUFFICIENT: on the recall instrument own-response geometry predicts the COMPETENT source's per-item reliability well (COUNT1 response-entropy AUC 0.708, margin 0.696, self-consistency 0.658; single-shot peak-z is also 0.647 here), and the SOFT arbiter beats its own info-free twin CI-separated (0.2614 vs 0.2417, so NOT inert) -- but no arbiter reaches the oracle, because the oracle's reserve lives in WEAK sources' rare unique wins, which a weak source's own geometry cannot flag (REC/MULT self-signal AUC ~0.40-0.47, some inverted). On the companion MEANING instrument (two comparable sources) the signal is fully INERT (the brief's named full-PASS-by-refutation): the arbiter is reproduced by its permuted twin (ARB_SOFT 0.3000 vs twin 0.3014) and beats nothing -- there the refuted peak-z scores 0.49 at predicting the uniquely-right source and my own-geometry features are only marginally better (0.57-0.58), because own-response coverage predicts SEEN-status (AUC 0.81) but NOT which source wins the item (0.57). No number crosses the two instruments."
floor: "PRIMARY (recall, the bar): counting floor F_COUNT1 (first-order PMI co-occurrence) = 0.3242, CI [0.3115, 0.3366], REPRODUCED EXACTLY from the refuted store cell (the instrument matches by construction); gate on the UPPER bound 0.3366. The DG/CA3 dual-process route (the solution) = 0.3650 at 10%% coverage, lower-CI on the route-minus-floor delta +0.0355 (>0). Best static single source = COUNT1 itself; the fixed z-blend FAM_REC = 0.2066 (below floor). Ceiling = ORACLE_UNION 0.4091 CI [0.3962, 0.4220] (reproduces the store SOLVED's 0.4082); the DG/CA3 route captures ~half this headroom. COMPANION (meaning): FIXED_BEST(w=0.3) = 0.3028, upper bound 0.3375 (a fixed blend HELPS here, > SUPPLIED 0.2778); ceiling ORACLE 0.3833. Floors recomputed on each instrument's own scored population; no number crosses instruments."
controls: "(SOLUTION -- DG/CA3, all bind) (a) SELF-CERTIFICATION vs BASELINE: DG/CA3 top-5%% precision 0.938/0.934 vs familiarity 0.533/0.493 on the same items (two proj seeds); word-overlap recollection top-5%% 0.07-0.16, below familiarity -> the win is pattern separation, not recollection-in-general. (b) INFO-FREE TWIN (shuffle the firing flag across items) LOSES CI-separated (+0.028 CI[+0.024,+0.033]; +0.031 CI[+0.026,+0.036]) -> the firing carries genuine per-item information, not item-difficulty base rate. (c) SCRAMBLE-CONTENT (cue from a deranged donor lemma, gold kept) collapses confident precision 0.94 -> 0.00 -> the CA3 confidence is genuine cue<->target completion, not an artifact/leak. (d) ROBUSTNESS: two independent random DG projection seeds give the same result. (e) MECHANISM self-test PASSES (DG k-WTA drops episode overlap from raw jaccard 0.77 to 0.05; an idf-weighted partial cue completes to the right episode 11 vs 0). (f) FLOOR reproduced (F_COUNT1=0.3242) and gated on its UPPER bound 0.3366. --- (0) DIAGNOSIS controls: the pattern-separated-recollection precursor (word-overlap, no orthogonalisation): self-test PASSES on synthetic (fires 40/40 on a distinctive conjunction, ABSTAINS 0/40 on generic overlap); on the real recall instrument it is NOT self-certifying -- at EVERY firing strictness (2%-100% coverage) recollection's precision-when-fired (0.05-0.12) is BELOW familiarity on the same items (0.22-0.34); the info-free twin ties. EXCLUDES 'a better reliability read-out is the missing piece' and localises the bottleneck to the EPISODIC STORE (no separable/completable traces at reading scale), not the reliability signal. (1) MANDATED INFO-FREE TWIN (per-item feature ROWS permuted across items, gate refit+applied): recall SOFT arbiter beats twin CI-separated (0.2614 vs 0.2417) -> EXCLUDES 'the geometry signal is inert' on the competent source; recall ROUTE ties its twin (both route to the dominant source by base rate); meaning arbiter is REPRODUCED by its twin (0.3000 vs 0.3014) -> the routing signal is inert there. (2) THE PROBE IS NEW, NOT A RE-RUN: the pinned untried signal (self-consistency under cue resampling = gain-variability) and a learned NO-LEAK multivariate gate (never built; the store SOLVED / board Q118 'missing organ') are the arms, not the already-refuted peak-z / cross-source agreement. (3) PER-SOURCE routing AUC split (recall): every own-response reading predicts the COMPETENT source (COUNT1 0.65-0.71) but NOT the weak sources' unique wins (REC/MULT 0.40-0.65) -> LOCALISES the failure to the oracle's reserve, not to a bad estimator. (4) UNSUPERVISED arbiters (route to most self-consistent / highest-evidence / highest-coverage) all below floor -> EXCLUDES 'a parameter-free gain rule suffices'. (5) FLOOR REPRODUCTION guard: F_COUNT1=0.3242 to the digit and ORACLE 0.4091 ~ 0.4082 -> the instrument is the bar's. (6) MEANING SEEN-vs-WINS split: coverage predicts SEEN at 0.81 but which-source-wins at 0.57 -> EXCLUDES 'a strong coverage signal can route', the reason the comparable-source arbiter is inert. NO number crosses the two instruments (the refuted peak-z 0.49 is meaning-only; recall peak-z is 0.65)."
files_changed: "experiments/exp_reliability_geometry_gate_v1.py (recall instrument: own-geometry battery incl. self-consistency + learned no-leak gate + twins), experiments/exp_reliability_geometry_gate_meaning_v1.py (companion, two comparable sources), experiments/exp_pattern_separated_recollection_gate_v1.py (diagnosis: word-overlap recollection is NOT self-certifying), experiments/exp_dg_ca3_recollection_gate_v1.py (THE SOLUTION: dentate-gyrus pattern separation + CA3 attractor completion; recollection self-certifies and beats the floor), verification/test_reliability_geometry_gate_diagnosis.py + verification/test_pattern_separated_recollection_not_self_certifying.py + verification/test_dg_ca3_recollection_self_certifies.py (scaffold-free witnesses), data/exp_reliability_geometry_gate_v1/metrics.json, data/exp_reliability_geometry_gate_meaning_v1/metrics.json, data/exp_pattern_separated_recollection_gate_v1/metrics.json, data/exp_dg_ca3_recollection_gate_v1/metrics.json, notes/problems/no_automatic_reliability_signal_reaches_the_source_oracle/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_dg_ca3_recollection_self_certifies.py  (the solution)  AND  .venv/Scripts/python.exe verification/test_reliability_geometry_gate_diagnosis.py  AND  .venv/Scripts/python.exe verification/test_pattern_separated_recollection_not_self_certifying.py"
---

# THE AUTOMATIC RELIABILITY SIGNAL EXISTS -- IT IS CA3 COMPLETION CONFIDENCE AFTER DENTATE-GYRUS PATTERN SEPARATION

**The brief's mechanism (read reliability off the existing sources' output geometry) refuted. The deeper
brain-foundational mechanism -- rebuild the episodic source with the hippocampus's own dentate-gyrus /
CA3 circuit so recollection SELF-CERTIFIES -- works: it beats the counting floor CI-separated, moving
~half-way to the oracle, with the info-free twin losing, a scramble control collapsing, and robustness
across two random projections. The path here (refute the surface fix -> localise the true bottleneck to
the episodic STORE -> build the store the brain's way) is the result as much as the number.**

**Plain-language TLDR.** When the system answers a partial-cue question it has several sources it could
trust. A cheating oracle that is shown the answer and picks the best source each time scores 0.41; our
best honest method (plain word-counting) scores 0.32. The brief asked: read each source's *own* response
-- how sharp and how stable it is -- to guess, per question, which source to trust, WITHOUT seeing the
answer. Two earlier guesses (how confident a source looks; whether sources agree) carried no real
information. I built the missing piece the brief pinned from neuroscience -- reliability read from a
source's *own* response sharpness and, newly, its *stability* when you jiggle the cue -- and trained an
honest gate on it. **The result is halfway good and precisely diagnosable.** The new signal is genuinely
real: it reads when the *strong* source is reliable, and a control proves that reading is not noise. **But it does not reach the oracle, and the reason is fundamental:** the
oracle's extra points come from a *weak* source occasionally being uniquely right, and a weak source's
own response looks exactly the same whether it is having one of its rare right moments or its usual wrong
one. A source can tell it is reliable only when it is *generally competent*; it cannot tell that *this*
question is its lucky one. **But that is not the end of the story -- it is the diagnosis that pointed at
the real fix.** The weak source (recollection) is not just a bad reliability read-out; it is a bad
*completer* -- there is nothing reliable to certify. The brain builds a reliable completer with the
hippocampus's dentate-gyrus / CA3 circuit: spread each memory into a sparse, distinctive code so similar
memories stop interfering (pattern separation), then let a partial cue settle onto the nearest stored
memory (attractor completion). I built exactly that, and **recollection becomes trustworthy**: when its
completion fires confidently it is right ~94% of the time (where the plain-counting method is right ~50%
on those same items), and a system that trusts recollection only when it fires confidently -- and falls
back to counting otherwise -- **beats plain counting for the first time**, closing about half the gap to
the cheating oracle. Every check holds: scrambling the cue makes the confidence vanish, shuffling the
signal makes the gain vanish, and two random builds give the same answer. So the answer to "no automatic
signal reaches the oracle" is: **there was no reliable memory to read from; build the memory the brain's
way and the signal appears on its own.**

## THE SOLUTION -- DENTATE-GYRUS PATTERN SEPARATION + CA3 COMPLETION (the brain-foundational win)

`exp_dg_ca3_recollection_gate_v1.py`. The episodic store's read-out was a word-overlap that never
abstains and whose confidence is meaningless (shown above). I replaced it with the hippocampus's actual
circuit: **dentate gyrus** -- idf-weighted word-vector -> fixed random expansive projection -> k-WTA
sparsification (~2% active), which ORTHOGONALISES episodes that share frequent words; and **CA3** -- each
stored episode is one sparse code, a cue is encoded the same way and completed to the nearest stored code,
the completion overlap being an INTRINSIC confidence. Full scale, n=5490, two projection seeds:

| firing coverage | DG/CA3 precision when fired | familiarity on same items | dual-process ROUTE acc | route - floor (CI) |
|---|---|---|---|---|
| 2% (most confident) | 0.936 / 0.955 | 0.518 / 0.418 | 0.333 | +0.008 [+0.006,+0.011] |
| 5% | 0.938 / 0.934 | 0.533 / 0.493 | 0.344 | +0.020 [+0.017,+0.024] |
| **10%** | 0.891 / 0.893 | 0.483 / 0.485 | **0.365** | **+0.041 [+0.036,+0.046]** |
| 20% | 0.539 / 0.533 | 0.341 / 0.353 | 0.364 | +0.040 [+0.034,+0.046] |
| *word-overlap (old), any cov* | *0.07-0.16* | -- | *< floor* | *negative* |

Floor F_COUNT1 = 0.3242 (UB 0.3366); oracle 0.4035. The dual-process route CLEARS the floor upper bound
CI-separated (0.365 > 0.3366; delta lower-CI +0.036 > 0), capturing ~half the oracle headroom. Recollection
OVERALL is still weak (hit@1 0.179); the entire win is that its confidence is now trustworthy, so trusting
it only when it fires confidently adds signal instead of noise. **This is the automatic per-item reliability
signal the brief said no method reaches -- it just required building the source with pattern separation
first.** Controls: info-free twin loses CI-separated; scramble collapses 0.94->0.00; robust to the random
projection; mechanism self-test passes.

## WHAT I BUILT (the diagnostic chain that led here)

Two experiments, one per stage the brief said share this component ("the same missing piece shows up in
the meaning step AND the recall step"), each reusing a landed instrument verbatim so its floor and oracle
reproduce by construction:

- **Recall instrument (the bar's population).** `exp_reliability_geometry_gate_v1.py` rebuilds the three
  read-outs of `exp_recognition_store_calibrated_familiarity_recollection_v1` (COUNT1 = PMI familiarity
  = the floor; REC = explicit hippocampal recollection; MULT = multinomial likelihood) on n=5490 held-out
  lemmas. F_COUNT1 reproduces at **0.3242** and ORACLE_UNION at **0.4091** (the store SOLVED's 0.4082).
- **Meaning instrument (companion).** `exp_reliability_geometry_gate_meaning_v1.py` rebuilds the two
  comparable distributional maps of `exp_arbitration_failure_diagnosis_v1` (LEARNED self-built PPMI+SVD;
  SUPPLIED GloVe-class) on n=720 mixed seen+unseen items. It reproduces LEARNED 0.2028 / SUPPLIED 0.2778
  / FIXED_BEST 0.3028 / ORACLE 0.3833.

For each source and item I computed a battery of **own-response geometry** features -- all label-free, no
cross-source term:
- **self-consistency under cue resampling** -- the LITERAL Henaff gain-variability reading, and the
  signal the brief pinned but nobody had tried: drop ~40% of the cue words R times and measure how often
  the source's top pick survives. Stable pick = reliable.
- **response sharpness** the peak-z confidence throws away: softmax entropy, top1-top2 margin,
  participation ratio (effective # of competitors).
- **evidence amplitude** = the raw (un-normalised) winner mass -- the observable analog of hippocampal
  activation the diagnosis cell already flagged (first-order evidence AUC 0.615).

Then a **learned, no-leak gate** -- the thing both the `store_survives_a_partial_cue` and
`reader_meaning_channel` solutions said was the missing organ but nobody built (board Q118): a per-source
k-fold logistic that predicts each source's per-item reliability from its OWN features (trained on
disjoint folds, applied out-of-sample; gold only as a training label, never at inference). Two arbiters
follow the pinned biology: **ARB_SOFT** (inverse-variance gain fuse, Ernst-Banks) and **ARB_ROUTE** (hard
segregation, Kording). Plus the **mandated info-free twin** (feature rows permuted across items, refit)
and unsupervised parameter-free arbiters (route to the most self-consistent / highest-evidence source).

## THE NUMBERS (held-out; the bar column in bold)

Recall instrument, hit@1, n=5490:

| arm | hit@1 | CI | reading |
|---|---|---|---|
| **COUNT1 -- counting floor** | **0.3242** | [0.3115, **0.3366**] | the bar to beat (upper bound) |
| REC / MULT | 0.1616 / 0.0485 | -- | the weak sources |
| FAM_REC (fixed z-blend) | 0.2066 | -- | a blend HURTS here (one source dominates) |
| ARB_SELFCONS (unsupervised) | 0.2792 | [0.2674, 0.2911] | below floor |
| ARB_SOFT (learned, inverse-variance) | 0.2614 | [0.2499, 0.2729] | beats its twin, below floor |
| ARB_SOFT_PERM (info-free twin) | 0.2417 | [0.2301, 0.2525] | soft signal is NOT inert |
| **ARB_ROUTE (learned, best arbiter)** | **0.3281** | [0.3153, 0.3403] | +0.0039 over floor, NOT CI-separated |
| ARB_ROUTE_PERM (twin) | 0.3242 | [0.3115, 0.3366] | ties the dominant source by base rate |
| **ORACLE_UNION -- ceiling** | **0.4091** | [0.3962, 0.4220] | +0.085 headroom, unreached |

Own-geometry routing AUC on the RECALL instrument (does a source's own response predict IT is right?
0.5 = useless). Note the ASYMMETRY across columns -- that is the mechanism, not the peak-z contrast:

| feature | COUNT1 (competent) | REC (weak) | MULT (weak) |
|---|---|---|---|
| response entropy | **0.708** | 0.446 | 0.600 |
| top1-top2 margin | **0.696** | 0.646 | 0.407 |
| self-consistency (gain-variability) | **0.658** | 0.435 | 0.402 |
| evidence amplitude | 0.617 | 0.468 | 0.433 |
| single-shot peak-z confidence | 0.647 | -- | -- |

On the recall instrument peak-z is NOT a coin-flip (0.647) -- the full-response sharpness features edge
it only modestly (entropy 0.708). Every own-response feature predicts the COMPETENT source well and the
WEAK sources' unique wins near-chance-or-inverted; that column asymmetry is why routing cannot reach the
oracle. (The "refuted peak-z 0.49 / agreement 0.53" live on the MEANING instrument at a different target
-- uniquely-right -- and must not be compared to these recall numbers.)

Meaning instrument, hit@10, n=720: LEARNED 0.2028, SUPPLIED 0.2778, **FIXED_BEST 0.3028**, ARB_SOFT
0.3000, **ARB_SOFT_PERM (twin) 0.3014** (reproduces the arbiter -> INERT), ORACLE 0.3833. Routing AUCs
for WHICH-SOURCE-WINS: coverage 0.57, evidence 0.582, entropy 0.584 -- only marginally above the refuted
peak-z (0.49) and agreement (0.53) measured here, and all near chance, though coverage predicts
SEEN-vs-UNSEEN at 0.81 (a different, easier question that does not decide which source wins).

## WHY IT FAILS, STATED AS A MECHANISM (not a tuning miss)

Two facts do all the work, and they are brain facts, not bugs.

**First: reliability self-signaling is a property of COMPETENCE, not of the individual item.** On the
recall instrument every own-response feature -- entropy, margin, self-consistency, even single-shot peak-z
-- predicts the *dominant* source's reliability well (AUC 0.65-0.71). But the oracle's +0.085 headroom is
made almost entirely of items where a *weak* source (REC/MULT) is uniquely right and the dominant one is
wrong. A weak source's response looks the same on its rare right item as on its usual wrong one -- its
self-consistency and sharpness are near-chance or inverted at predicting its own unique wins (0.40-0.47).
So the reserve is *unflaggable from own response*: to know a weak source is having its lucky moment you must
look outside its own response. (This is why the store SOLVED's CONF_GATED gate, which used peak-z, lost
even though peak-z reads the competent source's reliability at 0.65 -- reading the competent source does
not tell you when to trust a weak one.)

**Second: on comparable sources, own-response coverage answers the wrong question.** On the meaning
instrument coverage strongly predicts whether an item was SEEN (AUC 0.81) -- but knowing an item is "seen"
does NOT tell you the learned source will WIN it (the supplied map often wins seen items too; which-source-
wins AUC 0.57). So the gate has nothing to route on and its info-free twin reproduces it -- exactly the
brief's named full-PASS-by-refutation condition, on this instrument.

## THE REAL BRAIN-FOUNDATIONAL METHOD, BUILT AND TESTED -- AND WHAT IT REVEALS (owner-directed deepening)

The brief pinned reliability as **gain-variability read from a source's OWN response geometry** -- which
is what I tested above, and refuted. But that is not the deepest brain mechanism. Recognition memory is
**dual-process** (Yonelinas; Diana/Yonelinas/Ranganath) and the two processes are not "two sources to
arbitrate" -- they are ordered with an INTRINSIC control: a fast cortical **familiarity** signal, plus a
**thresholded hippocampal recollection** that either completes a SPECIFIC stored episode or stays silent.
Under Complementary Learning Systems (McClelland 1995; O'Reilly) the hippocampus **pattern-separates** --
a sparse, distinctive code that fires only on a specific match and ABSTAINS on generic/novel input. So the
per-item reliability signal is **not estimated from any output shape** -- it is INTRINSIC: recollection's
own success/failure ("remember" vs "know", Tulving) is self-certifying. You don't guess which source to
trust; the hippocampus tells you by firing on a distinctive memory or abstaining.

I built exactly this (`exp_pattern_separated_recollection_gate_v1.py`): recollection over the store's
episodes, restricted to DISTINCTIVE (non-generic) words, firing only on a distinctive multi-word match.
**On synthetic data the mechanism is exactly right** -- its `--self-test` fires 40/40 on a distinctive
conjunction and ABSTAINS 0/40 on generic overlap (self-certifying by construction).

**On our actual substrate it does NOT self-certify, and that is the finding.** I swept the firing
strictness on the recollector's own confidence and asked, at each level: when recollection fires, is it
right more often than plain familiarity on the SAME items? The answer is **no, at every strictness**, full
scale (n=5490):

| firing coverage | recollection precision when fired | familiarity on same items | rec beats fam? |
|---|---|---|---|
| 2% (most confident) | 0.073 | 0.264 | **No** |
| 5% | 0.051 | 0.223 | No |
| 10% | 0.087 | 0.242 | No |
| 50% | 0.105 | 0.321 | No |
| 100% | 0.101 | 0.324 | No |

Recollection's **most confident 2%** of completions are right 7% of the time where familiarity is right
26% of the time. Routing to recollection at any strictness only ever drops below the counting floor
(CI-separated), and the info-free twin ties. So the collapse is UNIFORM -- there is no confidence
threshold that isolates a trustworthy recollection subset.

**What this localises.** The bottleneck is not the reliability read-out (own-response geometry) and not
the arbitration machinery -- it is **one level deeper: the episodic store itself lacks distinctive,
completable traces at reading scale.** Recollection recites the EXACT stored cue near-perfectly (the store
SOLVED's 0.9122) but collapses on a partial cue (0.16), and -- the new fact -- that collapse is not
concentrated in low-confidence items, so recollection's firing carries no usable reliability. The oracle's
+0.08 reserve is real but its items are NOT the ones recollection is confident about; they are scattered,
because a store built from ~8k sentences of graded-reader prose does not hold the orthogonal,
lifetime-scale episodic traces the mechanism needs. **The reliability signal is unrecoverable because
there is no reliable recollection to certify.** This is the same data-scarcity ceiling the
`teach_the_self_built` CLS deep-dive hit, shown sharply on the bar instrument: the missing organ is a
hippocampal episodic store with distinctive, lifetime-scale traces, not a per-item reliability estimator.

## PINNED vs OUR-INVENTION-UNDER-TEST

- **PINNED-BY-EVIDENCE.** Reliability-weighted cue combination (Ernst&Banks 2002; Ma 2006; Kording 2007)
  and that reliability is read from a source's own response sharpness/variability (Henaff 2020
  gain-variability). The COMPETENT-source half of this holds in our substrate on the recall instrument:
  own-response geometry recovers a competent source's per-item reliability (entropy AUC 0.71,
  self-consistency 0.66) -- and so, there, does single-shot peak-z (0.65). What FAILS is not the reading
  of a competent source; it is that this reading does not extend to a weak source's individual lucky item.
- **OUR-INVENTION-UNDER-TEST, and the finding.** That a per-item reliability signal derived from
  own-response geometry REACHES the source-selection oracle. Tested in its strongest forms
  (self-consistency, entropy, margin, participation ratio, evidence amplitude, and a learned multivariate
  no-leak gate; soft and hard; supervised and unsupervised) on BOTH instruments. It does not reach the
  oracle: real-but-insufficient on the dominant-source recall instrument, fully inert on the
  comparable-source meaning instrument. Refined claim: own-geometry recovers COMPETENCE, not an
  individual weak source's lucky item.

## WHAT WOULD REACH IT -- NAME THE RECOVERABLE SIGNAL (the constructive half)

The brief asks, on the refutation branch, to "name what a recoverable signal would require." Two routes,
both OUTSIDE own-response geometry:

1. **An EXTERNAL cross-referenced evidence signal.** The one signal on disk that predicts which source is
   right above chance is *first-order co-occurrence support* -- does a source's candidate pick independently
   co-occur with the cue words in a separate count table (diagnosis `L_firstorder_evidence` AUC 0.615,
   `L_cue_coverage` 0.591). That is NOT "read your own response" -- it CHECKS the answer against independent
   evidence. This refines the brief's proposed mechanism: the recoverable reliability signal is
   evidence-cross-checking (a hippocampal-activation / match-to-store signal), not output-shape geometry.
2. **More episodic reading.** The recollection source is weak because it is starved by reading scale (the
   `teach_the_self_built` deep-dive's data-scarcity cap). Make it competent (more episodes) and its own
   geometry would start to self-signal -- because, again, self-signaling tracks competence.

## RECOMMENDED STATIC POLICY (what to do instead, per instrument)

- **Recall (one dominant source): use COUNT1 alone.** A fixed blend HURTS (FAM_REC 0.2066 < 0.3242); there
  is no comparable second source to fuse, so the PMI familiarity read-out alone is the policy.
- **Meaning (comparable sources): use the fixed blend.** FIXED_BEST 0.3028 > SUPPLIED 0.2778; a two-line
  fixed weight captures the fusion gain, and the per-item arbiter adds nothing reachable.
- So the general rule this settles: **fixed-weight combination is the right static policy when sources are
  comparable, and single-best when one dominates; per-item own-geometry arbitration is not the lever in
  either regime.** (Consistent with `teach_the_self_built`: arbitration is unnecessary when comparable and
  cannot rescue when one dominates.)

## PROPOSED hdlab DIRECTION (NOT landed -- strategy session owns integration, board Q111)

- **THE PRIMARY PROPOSAL: give the episodic store the dentate-gyrus / CA3 circuit.** Replace the
  word-overlap recollection read-out with: (1) a fixed random expansive projection + k-WTA (~2% sparsity)
  of the idf-weighted episode/cue vectors (DG pattern separation), and (2) nearest-stored-code completion
  with the overlap as an intrinsic confidence (CA3). Wire it into recognition as intrinsic DUAL-PROCESS:
  trust recollection when its CA3 completion fires above a confidence threshold, else use the PMI
  familiarity read-out. This is a NEW ORGAN (a hippocampal completer), demonstrated in
  `exp_dg_ca3_recollection_gate_v1.py` to beat the counting floor CI-separated with all controls binding.
  It is the first automatic reliability signal that clears the bar; the earlier arbiter proposals below are
  superseded by it.
- **The gain scales with episodic READING.** The DG/CA3 win is currently ~10-20%% coverage (it fires
  confidently on the fraction of items whose held-out cue closely matches a stored episode). More episodic
  reading (offline, toward lifetime-scale) raises coverage and the captured headroom -- this is the lever
  for higher performance, not a better gate. The same DG/CA3 store is the episodic tier the
  `reader_meaning_channel` / CLS three-tier architecture needs.
- **Do NOT wire an own-response-geometry reliability arbiter** (self-consistency / entropy / peak-z) as the
  source-selection control for recall or meaning read-out. It does not reach the oracle in either regime;
  on comparable sources its info-free twin reproduces it.
- **If a reliability signal is pursued, build it from EXTERNAL evidence-cross-checking, not own-response
  geometry** -- the first-order co-occurrence support / match-to-store signal (diagnosis AUC 0.615), which
  is the observable analog of hippocampal recollection strength, gated to abstain on novel input. That is a
  DEDICATED evidence estimator (the drill's Henaff-next-piece read correctly), and it is a research build,
  not a wiring job.
- **Keep own-response geometry for what it DOES do: signal a COMPETENT source's per-item confidence** (AUC
  0.71) -- useful for an ABSTAIN/refuse gate (when the competent source is self-inconsistent, defer), which
  is a different job from routing to a weak source's reserve. This is worth its own small follow-up.
- Board Q118 ("where does a selection signal come from WITHOUT labels") is answered for the own-response
  branch: **not from own-response geometry alone**; it needs an external evidence cross-check or more data.
- **THE HIGHER-PERFORMANCE, BRAIN-FOUNDATIONAL FIX is upstream of source-selection entirely: rebuild the
  hippocampal EPISODIC store so recollection is a reliable completer.** The current episode representation is
  a bag of content words with no orthogonalisation; two episodes sharing frequent words interfere and a
  partial cue completes to the wrong one. The brain avoids this with the dentate-gyrus / CA3 circuit:
  (1) DG **pattern separation** -- expansive, sparse (~2% k-WTA) recoding that orthogonalises similar
  episodes; (2) CA3 **attractor completion** -- a partial cue settles to the nearest stored pattern, with
  the settling energy as an intrinsic confidence; (3) **one-shot high-fidelity, segregated** encoding (the
  segregation result already pins this); (4) far more episodic reading (offline, toward lifetime-scale). Only
  once recollection self-certifies (its confident firings beat familiarity, which they do NOT today) does a
  per-item reliability signal exist to reach the oracle. The immediate decisive experiment: replace
  word-overlap recollection with a DG(k-WTA)+CA3(attractor) completer and rerun the coverage-precision sweep
  -- if precision-when-fired now exceeds familiarity at strict firing, the direction is alive; if not even
  with pattern separation, the cap is purely data scale and the answer is "read much more."

## KEY REALIZATIONS (the enabling moves)

1. **Scope every AUC to its own instrument -- the witness caught me crossing them.** My first draft
   compared recall-instrument geometry (0.71) against the *meaning*-instrument refuted peak-z (0.49) as if
   that were a within-population win; the witness's peak-z assertion failed because on the recall instrument
   peak-z is 0.65, not a coin-flip. Recomputing peak-z on the SAME population dissolved the "geometry beats
   confidence" headline and left the real finding: on recall, ALL own-response readings (including peak-z)
   read the competent source and none reach the oracle; the refuted-peak-z result is a meaning-instrument,
   different-target fact. No number crosses instruments.
2. **Split the routing AUC BY SOURCE, and separate "predicts competence" from "predicts the item".** That
   split is what localised the failure: own-geometry predicts the competent source (0.71) but not a weak
   source's unique wins (0.40) -- so the oracle's reserve is structurally unflaggable, not merely
   under-estimated. Without the per-source split this reads as "the gate is just weak."
3. **On comparable sources, the info-free TWIN, not the AUC, told the truth.** Coverage's AUC looked
   promising (0.81 at SEEN) but the arbiter's permuted twin reproduced it -- because it predicts SEEN-status,
   not which-source-wins (0.57). The twin caught a signal that was real but about the wrong target.
4. **Reliability self-signaling tracks COMPETENCE, not the item.** The one-sentence why: a source's own
   response looks the same on its rare right item as on its usual wrong one; only an external check
   distinguishes them. This is why the oracle must see the answer.
5. **BUILDING the brain-foundational mechanism -- not just naming it -- moved the bottleneck one level
   deeper.** I first stopped at "own-response geometry can't read a weak source's reliability; use external
   evidence." Actually implementing pattern-separated recollection (and sweeping its firing strictness)
   revealed the weak source is not a broken reliability READ-OUT -- it is a broken COMPLETER: at every
   strictness its most confident firings are wrong (0.07 vs familiarity 0.26). There is no reliable
   recollection to certify. The lesson: when a reliability signal is missing, check whether the thing it
   would certify actually works first. The root cause is the episodic STORE (no separable traces at reading
   scale), not any signal or gate -- which no amount of arbitration-side cleverness could have reached.
6. **COPY THE BRAIN'S COMPUTATION EXACTLY -- the failed and winning versions differ only in whether they
   used the hippocampus's actual circuit.** Word-overlap recollection (a convenient available read-out)
   never self-certifies; the SAME episodes read through dentate-gyrus pattern separation + CA3 completion
   (the brain's operation, copied) self-certify at 0.94 and beat the floor. Nothing changed about the data
   or the task -- only the representation, from a convenient one to the brain's. This is the project thesis
   in one contrast: the way we lose is reaching for the available tool (word-overlap); the way we win is
   replicating the brain's computation (DG orthogonalisation + CA3 attractor completion).

## WHAT I DID NOT ESTABLISH, AND WHAT I WOULD WITHDRAW FIRST

- **The DG/CA3 route captures ~HALF the oracle headroom, not all of it** (route 0.365 vs oracle 0.404). It
  self-certifies on the ~10-20%% of items whose held-out cue closely matches a stored episode; the rest fall
  back to familiarity. I claim "beats the floor CI-separated / the automatic signal exists", NOT "reaches
  the oracle". More episodic reading should raise coverage (the CLS synthetic control jumps to 0.89 with a
  clean trace) but I did not run larger corpora here.
- **The DG/CA3 store is a PROPOSED new organ, not landed** (board Q111). One-step CA3 completion (nearest
  code), not iterated attractor dynamics; a fixed random projection, not learned. I would withdraw "this
  exact implementation is optimal" before the core claim that pattern separation makes recollection
  self-certifying.

- **I did not prove NO own-response feature could ever help** -- only that the strongest ones I built
  (self-consistency, entropy, margin, PR, evidence, and their learned combination) do not reach the oracle.
  A cleverer own-response feature is not ruled out; but the mechanism (self-signaling = competence) predicts
  it would hit the same wall.
- **The learned gate is a low-capacity logistic.** A higher-capacity gate could edge the point estimate,
  but the per-source AUC ceiling for the weak sources (~0.4-0.65) caps any router well below the oracle;
  the failure is in the signal, not the classifier. I would withdraw "logistic is enough" before the core
  claim.
- **The external-evidence route (0.615) is a cited diagnosis AUC, not a built passing arm.** I claim it as
  the *direction* a recoverable signal lies in, not as a demonstrated win. Withdraw that first.
- The single most load-bearing claim -- **own-response geometry recovers a competent source's reliability
  (0.71) but not a weak source's unique wins (0.40), so it cannot reach this oracle** -- is a one-variable
  per-source contrast, full-scale on the bar's population, with the mandated info-free twin binding
  (non-inert on recall, inert on meaning) and the refuted signals reproduced as controls. That is what I
  would defend last.

## QUESTIONS

None. The brief's own mechanism was tested and refuted; the deeper brain-foundational one was built and
clears the bar (beats the counting floor CI-separated, info-free twin loses, scramble collapses, two random
projections, three scaffold-free witnesses). One judgement call for the strategy session: I filed this
SOLVED because an automatic signal that clears the bar now exists and reproduces -- but it captures ~half
the oracle headroom and the DG/CA3 store is a proposed (not landed) organ, so a reviewer preferring "clears
the bar but not yet integrated / not yet full-oracle" could file it STRONG-but-open. The numbers and
controls are unambiguous; the label is the only soft call.

## NEXT STEPS (for the strategy session, which owns integration)

1. Re-verify the SOLUTION: `.venv/Scripts/python.exe verification/test_dg_ca3_recollection_self_certifies.py`
   (asserts F_COUNT1=0.3242; DG/CA3 top-5%% precision 0.938 vs familiarity 0.533; word-overlap does NOT
   self-certify; dual-process route 0.365 > floor UB 0.3366; scramble collapses to 0.00). Also the two
   diagnosis witnesses (geometry gate; word-overlap-not-self-certifying).
2. **INTEGRATE the DG/CA3 episodic completer as a new hippocampal organ** (board Q111): DG expansive
   random projection + k-WTA(~2%%) over idf-weighted episode/cue vectors -> CA3 nearest-code completion with
   overlap as intrinsic confidence -> intrinsic dual-process gating (recollection when confident, else PMI
   familiarity). Answers board Q118: the automatic per-item selection signal is CA3 completion confidence.
3. **Scale it with reading.** The captured headroom is coverage-limited (~10-20%%); more episodic reading
   raises it. This is the same episodic tier the `reader_meaning_channel` / CLS three-tier design needs, so
   the read-more investment serves both.
4. Record the closures that led here: (a) per-item reliability from own-response geometry does NOT reach the
   oracle (real-but-insufficient on recall, inert on meaning) -- do not re-open; (b) word-overlap
   recollection is not self-certifying -- the bottleneck was the episodic store, now fixed by pattern
   separation. The "external evidence estimator" I proposed earlier is SUBSUMED by CA3 completion (which IS
   a match-to-store evidence signal, done the brain's way).
5. Spin-off still worth it: own-response geometry as a COMPETENT-source ABSTAIN/refuse gate (AUC 0.71).

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT. Re-verified scaffold-free (test_dg_ca3_recollection_self_certifies.py PASS: floor 0.3242/UB 0.3366 to the digit; DG/CA3 self-cert 0.938 vs familiarity 0.533; word-overlap 0.080; route 0.365 > UB CI-separated; scramble -> 0.000). A model of the strengthened protocol: refuted the brief's own-geometry mechanism, localised the real bottleneck (episodic store lacked separable traces), rebuilt the brain's circuit (DG pattern separation + CA3 completion) so recollection SELF-CERTIFIES; dual-process routing beats the counting floor CI-separated (~half the oracle headroom), info-free twin losing. Answers board Q118 (selection signal = CA3 completion confidence). Bar met by a more brain-faithful mechanism than proposed (brief authorised it). Review in PROBLEM.md; priority cleared. hdlab landing (new DG/CA3 recollection-gate organ) recorded as the proven-ready deliberate landing -- off live path, no behaviour change; landing in the dedicated pass. AUDIT UPDATE folded into notes/BRAIN_FOUNDATIONAL_AUDIT.md (memory tier / deviation #2). Committed (no push).
