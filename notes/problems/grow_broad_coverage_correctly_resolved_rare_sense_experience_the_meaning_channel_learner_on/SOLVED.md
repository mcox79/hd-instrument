---
problem: grow_broad_coverage_correctly_resolved_rare_sense_experience_the_meaning_channel_learner_on
status: PARTIAL
bar: "PASS = glass-box grounding-anchored propose-and-verify online growth (admitted through consolidation_gate + cls_growth; NO transformer, NO batch training, NO external LLM) such that the RARE-sense a_s RISES as coverage grows, CI-separated, with (a) a strict INDUCTIVE train-only W (no transductive leakage), (b) the MFS no-regression guard passing, and (c) a shuffled-experience info-free twin LOSING. A rigorous located NEGATIVE -- online bootstrapping cannot thicken the Zipf-thin rare-sense signal glass-box within the invariant, with the named cause + number -- is a FULL PASS."
result: "[STAGE 2 FULL PENDING -- headline to be filled from data/exp_rare_sense_coverage_growth_v1/metrics_full.json]. Established: (mechanism) episodic count-normalized MINERVA-2 echo beats prototype-averaging on the rare tail at the gold ceiling (PURE content vs shuffled-trace twin +0.038 CI-sep [0.006,0.071]); (upgrade) brain-foundational PBV-v2 (grounding-anchored propose + real cross-encounter Bush-Mosteller verify + prioritized replay + consolidation-gated commit) produces CLEAN traces (covered PURE episodic 0.763 vs twin 0.707, +0.056 CI-sep); (growth) reading external simplewiki online grows rare-sense coverage BREADTH (0.14 in-SemCor -> rising), and on covered senses episodic beats base and the shuffled twin CI-sep. Scorer: subject-weighted a_s on strict document-disjoint SemCor subordinate senses, n=2676, via hdlab/diagnostic_context_wsd, frozen 200-dim w2v, glass-box."
floor: "base = the wired diagnostic-context readout (WordNet rich-atom keys) on the same rare population: rare-covered 0.283 (STAGE 0) / 0.52 base-on-covered (STAGE 2 smoke); prototype-averaging (P9 R5 gold) 0.359 rare-covered; naive contaminated deploy 0.265 (the control the coverage-aware deploy must beat). base-rare-all 0.31-0.35."
controls: "(1) SHUFFLED-EXPERIENCE twin (committed sense->trace map permuted; identical coverage, content-isolated) LOSES CI-sep on every mechanism arm -- caught the coverage/attestation artifact in the fused arms. (2) count-normalized echo beats the RAW-SUMMED MINERVA-2 echo +0.096 CI-sep (the Zipf-swamp control; canonical raw-sum re-imports the frequency bias). (3) MFS no-regression guard on the full (sub+dom) population. (4) strict INDUCTIVE: external growth corpus (simplewiki) is disjoint from the SemCor test docs. (5) coverage-aware deploy vs NAIVE deploy (0.265) -- isolates the uncovered-competitor contamination. (6) concrete/abstract stratification (Brysbaert) -- the mechanism-diff predictor."
files_changed: "experiments/exp_rare_sense_episodic_vs_prototype_v1.py (STAGE 0); experiments/exp_rare_sense_propose_verify_episodic_v1.py (STAGE 1, vanilla-PBV located negative); experiments/exp_rare_sense_pbv_v2_brain_faithful_v1.py (STAGE 1.5, the brain-foundational PBV-v2 upgrade); experiments/exp_rare_sense_coverage_growth_v1.py (STAGE 2, external-corpus coverage growth); verification/test_rare_sense_episodic_coverage_growth.py (witness)."
reverify: ".venv/Scripts/python.exe verification/test_rare_sense_episodic_coverage_growth.py"
---

# Rare-sense meaning channel: the tail is the HIPPOCAMPAL-EPISODIC regime, and coverage growth is the lever

> **STATUS NOTE (WIP):** STAGE 2 full-corpus run is completing; its headline (does the deployed rare-sense a_s
> rise CI-separated over the base floor as coverage grows on all of simplewiki?) decides SOLVED vs PARTIAL. The
> mechanism (STAGE 0/1.5) and the coverage-growth *direction* (STAGE 2 smoke) are established and controlled. This
> file is WIP until `owner_verdict: DONE`.

## >>> THE ONE-PARAGRAPH ANSWER <<<
P9 concluded "even a perfect resolver doesn't help rare senses -- too few instances to consolidate." That was a fact
about **prototype-averaging** (the neocortical memory system), applied to the Zipf-thin tail -- **the wrong memory
system for that frequency band.** The 2026-09-04 neuroscience scan is one-directional: the rare tail is
*definitionally* the **hippocampal-EPISODIC** regime (CLS, McClelland 1995 / Davis-Gaskell 2009) -- store single
traces, retrieve the best-matching one by context (MINERVA-2 echo; Hintzman), commit via propose-but-verify
(Trueswell 2013), grounding-anchored (Gillette 1999). Switching from prototype-averaging to **count-normalized
episodic retrieval** recovers a real, controlled signal P9's averaging discarded (STAGE 0). A brain-foundational
**propose-and-verify upgrade (PBV-v2)** -- real cross-encounter Bush-Mosteller confirm/discard, grounding-anchored
proposal, prioritized replay, consolidation-gated commit -- produces traces clean enough that episodic retrieval
beats the shuffled-trace twin (STAGE 1.5), where a vanilla within-encounter margin gate could not (STAGE 1). And
**reading a large external corpus online grows rare-sense coverage breadth** (STAGE 2), which is the only
brain-foundational lever that thickens the Zipf-thin tail without a transformer. The remaining question the full run
answers: does the deployed rare-sense a_s rise **CI-separated** over the floor once all of simplewiki is read.

## THE CHAIN OF EXPERIMENTS (each a can-fail stage; each cell reproducible)

### STAGE 0 -- episodic vs prototype at the GOLD ceiling (`exp_rare_sense_episodic_vs_prototype_v1.py`)
Isolates the MEMORY MECHANISM from resolution quality: both arms see the same gold-resolved train evidence; they
differ only in how it is stored/retrieved. The controlled cue is the fixed diagnostic-context query (biased
competition, the P9-landable readout). On rare-covered (n=1396):

| arm | a_s | note |
|---|---|---|
| WordNet-only (no experience) | 0.283 | floor |
| prototype-averaging (P9 R5 gold) | 0.359 | the P9 mechanism |
| raw-summed MINERVA-2 echo (Zipf-swamp) | 0.321 | **loses -0.038** (the exemplar memo's warning) |
| count-normalized episodic echo (PURE) | 0.373 | content-isolated |
| episodic CLS keep-both fused | 0.419 | +frequency prior |

Controls: **PURE count-normalized echo beats its shuffled-trace twin +0.038 CI-sep [0.006,0.071], beats null** (the
signal is genuine contextual retrieval, not a coverage artifact). Count-normalized beats raw-summed **+0.096 CI-sep**
(the Zipf-swamp; count-normalization is the fix). Strongest in the single-trace regime (+0.072 CI-sep) -- the
fast-mapping signature. Consumer guard +0.029 CI-sep. **The fused arm's larger +0.060 does NOT beat its twin** -- a
legitimate-but-non-mechanistic frequency prior the twin correctly exposes; not claimed.

### STAGE 1 -- vanilla propose-and-verify is a located negative (`exp_rare_sense_propose_verify_episodic_v1.py`)
A within-ENCOUNTER margin gate cannot break the precision/coverage tradeoff: loosen it -> rare coverage 0.23 at ~0.45
precision; tighten it -> precision 0.71-0.81 but rare coverage ~0. Confident cases are Zipf-DOMINANT-biased. At every
threshold the episodic store beats neither base nor the twin. Concreteness stratifies precision at every gate
(concrete 0.59-0.81 > abstract 0.41-0.67 -- the Trueswell/Gillette signal), just not enough inside one small corpus.

### STAGE 1.5 -- PBV-v2, the brain-foundational upgrade (`exp_rare_sense_pbv_v2_brain_faithful_v1.py`)
Replaces the within-encounter margin with the brain's actual mechanism (confirmed by literature scan):
- **Grounding-anchored PROPOSE** (concrete targets weight the diagnostic evidence more).
- **REAL cross-encounter VERIFY** (Bush-Mosteller: confirm `A<-A+g(1-A)` / disconfirm `A<-A(1-g)`, g=0.02 sweep;
  multiplicative penalty -> losers decay slowly, recoverable -- the Pursuit model, Stevens-Trueswell 2017).
- **PRIORITIZED REPLAY** (rare/surprising re-sampled; CLS multi-pass, licensed as short online re-presentations).
- **CONSOLIDATION-gated commit** (informative + confirmed only; Medina 2011 ~7% rule).
- **MINERVA-2 readout**: canonical raw-summed echo `I=SUM S^3` (labeled canonical); **count-normalized echo LABELED
  AS OUR EXTENSION** (non-canonical -- removes the frequency signal, which is what the tail needs; exponent 3 is
  canonical per Kelly 2017).

RESULT: on the confidently-COVERED subset (n=376, 14% of rare) PURE episodic beats the shuffled twin **+0.056 CI-sep
(0.763 vs 0.707)** and beats base by +0.247; concrete 0.727 > abstract. The cross-encounter verify produces CLEAN
traces where vanilla PBV could not. **Wall = coverage BREADTH (14% within SemCor):** rare senses are Zipf-thin in the
*training* corpus too.

### STAGE 2 -- coverage growth on external simplewiki (`exp_rare_sense_coverage_growth_v1.py`)
The decisive test of the bar. Online PBV-v2 over external, test-disjoint simplewiki accumulates traces for the fixed
SemCor test lemmas; the store is snapshot at increasing corpus fractions -> the coverage curve. **Smoke (120k
sentences, n_test=600) -- full-corpus pending:**

| corpus read | coverage breadth | covered PURE episodic | shuffled twin | base-on-covered | coverage-aware DEPLOY (all rare) | naive deploy |
|---|---|---|---|---|---|---|
| 25% | 0.14 | 0.835 | 0.694 | 0.565 | 0.338 | 0.205 |
| 50% | 0.25 | 0.808 | 0.676 | 0.510 | 0.353 | 0.255 |
| 100% (120k) | 0.33 | 0.728 | 0.492 | 0.523 | **0.363** | 0.265 |

- **Coverage breadth RISES with reading (0.14 -> 0.33 at just 120k of ~800k+ sentences).** The 14% within-SemCor wall
  breaks: more reading covers more rare senses.
- On covered senses, PURE episodic beats base AND the shuffled twin **CI-sep at every checkpoint** -- glass-box
  PBV-v2 traces are clean enough. Concrete stratum 0.80-0.94.
- **The coverage-aware deploy RISES with coverage (0.338 -> 0.363) above the base floor (0.35)**, while the NAIVE
  deploy (0.265) stays contaminated -- because on uncovered-gold rare items the covered *dominant* competitor is
  boosted (the STAGE 0 finding). The coverage-aware deploy lets episodic discriminate only among covered candidates
  (>=2), never penalizing uncovered ones -- brain-faithful controlled retrieval. **At 120k the deploy-vs-base margin
  is not yet CI-separated (breadth only 0.33); the full corpus is the decisive test.**

## WHAT I DID NOT ESTABLISH (yet) / WHAT I WOULD WITHDRAW FIRST
- **[decides status] Whether the deployed rare-sense a_s crosses the base floor CI-SEPARATED at full corpus.** Smoke
  shows it rising and just above; the full run resolves it. If it rises but does not CI-separate, this is a located
  negative with a named cause (Zipf breadth ceiling + coverage-asymmetry deploy contamination) -- still a full pass.
- **Surface==lemma matching** in STAGE 2 (no lemmatizer, for remote-safety) UNDER-counts coverage; real breadth is
  higher. A conservative measurement -- if wrong, it is wrong in the pessimistic direction.
- **The count-normalized echo is our EXTENSION, not canonical MINERVA-2.** If challenged, the canonical raw-summed
  echo is the fallback (it beats the twin but re-imports frequency bias); the count-normalization is the defensible
  tail-appropriate choice, flagged as such.
- First thing I would withdraw: the *fused* (frequency-prior) numbers, which the twin control already excludes.

## KEY REALIZATIONS (the enabling moves)
1. **P9's "perfect resolver doesn't help rare senses" was a statement about PROTOTYPE-AVERAGING, not a ceiling.** The
   neuroscience says the tail is the episodic regime; switching memory systems (not resolvers) is the unlock.
2. **The shuffled-trace twin, applied to episodic retrieval, separates COVERAGE from CONTENT** -- and it exposed that
   the fused arm's headline gain was a frequency prior, while the pure arm's smaller gain is the real mechanism.
3. **Count-normalization reconciles the neuroscience (episodic) with the exemplar memo (raw exemplar loses):**
   MINERVA-2's count-normalized/max echo IS the memo's prescribed fix for the Zipf-swamp -- they never disagreed.
4. **Vanilla propose-and-verify fails because the confident cases are Zipf-dominant-biased; the REAL cross-encounter
   verify is what produces clean rare traces** (STAGE 1 -> 1.5 is the whole difference).
5. **The deploy contamination (episodic boosts a covered dominant competitor on uncovered-gold items) is the same
   coverage-asymmetry finding from STAGE 0** -- fixed by a coverage-aware controlled-retrieval gate, not by a better
   resolver.
6. **The human subordinate-bias effect (Duffy-Morris-Rayner 1988) reframes the ceiling:** competent readers also miss
   subordinate senses without supporting context (frequency-limited). A rare-sense a_s in the 0.3-0.4 band is
   HUMAN-LIKE; the right target is context-gated recoverability, not context-free dominant parity.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
The meaning-channel WSD readout consumes a sense representation; the audit should record that the rare/subordinate
tail requires an EPISODIC (hippocampal, MINERVA-2 single-trace) store retrieved by controlled context-match, NOT the
neocortical prototype the consolidation gate builds -- these are complementary CLS systems and the substrate had only
the prototype half. PBV-v2 (grounding-anchored propose + cross-encounter Bush-Mosteller verify + prioritized replay)
is the brain-faithful acquisition loop; `hdlab/consolidation_gate` (prototype/neocortical) + a new episodic store
(hippocampal) together are the complete CLS pair.

## FOR STRATEGY (Q111 wire -- a PROPOSED change, not landed)
IF the STAGE 2 full run crosses CI-separated: add an **episodic sense-trace store** as a new organ
(`hdlab/episodic_sense_store` -- MINERVA-2 count-normalized echo) fed by the PBV-v2 acquisition loop, read through a
**coverage-aware controlled-retrieval deploy** that discriminates only among covered candidates (>=2) and never
penalizes uncovered ones. Compose with the owner-DONE `hdlab/consolidation_gate` (neocortical prototype) + `cls_growth`
(keep-both reversibility) -- the two CLS systems. Default-OFF until the full-corpus impact analysis on the live
consumer confirms net-positive with the coverage-aware deploy (the naive deploy REGRESSES -- do not ship it). Build ON
the P9 precision-weighting readout.

## TLDR (plain English)
The reader was weak at rare word meanings because it learned them the way the brain learns COMMON ones -- by averaging
many examples into one blurry summary. But a rare meaning only shows up once or twice, so the average is noise. The
brain uses a different memory for rare things: it keeps each clear encounter as its own trace and later recalls the
best-matching one. We rebuilt the reader that way, and it works -- on the rare meanings it has seen a clear example
of, it is far more accurate. The catch is it has seen a clear example of only about one in seven rare meanings from
its small training text. So we had it read a large amount of extra text the way a child does -- make one careful guess
per encounter, keep it only if later sentences agree, anchored to concrete words first -- and the number of rare
meanings it can handle grows as it reads more. Early results show the rare-meaning score rising as it reads; the full
reading run confirms whether that rise is large enough to be sure it is real and not luck. Notably, even fluent adult
readers miss rare meanings when the sentence doesn't hint at them, so a modest rare-meaning score is human-like, not a
bug -- the goal is that the rare meaning is recoverable when the context supports it, which is exactly what this does.

## QUESTIONS
One, and it is the owner's (carried from P9, unchanged): hold the no-transformer invariant and pursue this
episodic/coverage-growth route (the brain-faithful path, human-like ceiling), or relax it for one offline contextual
asset to chase a higher number? This work assumes the invariant HOLDS. No other questions.

## NEXT STEPS
1. Fill the STAGE 2 full-corpus headline (does deployed rare-sense a_s cross the floor CI-separated) -> set status.
2. If SOLVED: strategy lands the episodic store + coverage-aware deploy (default-off pending live impact analysis).
3. Adjacent components to evaluate (verdict-independent): (a) a lemmatizer on the growth corpus would raise coverage
   breadth (surface-match under-counts); (b) the coverage-aware deploy gate is OUR-INVENTION -- a precision-weighted
   (Friston/Ernst-Banks reliability) fusion is the higher-fidelity version to test; (c) grounding-anchored proposal
   currently uses concreteness as a scalar multiplier -- the full ATL hub-and-spoke grounded key is the richer form.
