# HOW WALLS WERE ACTUALLY BROKEN — farmed from the last 50 owner turns of the old main + four solver sessions (2026-09-12)

Companion to `WALL_PUSH_PROTOCOL_owner_motivation_messages.md` (the owner's messages, verbatim). This file is the EVIDENCE:
what the sessions declared as walls, what the owner said next, and what actually broke each wall. Every "ceiling" below was
declared by an Opus 4.8 session in good faith; most fell within hours of the push. Strategy (Fable) must read this before
writing any of: wall / ceiling / located negative / information limit / data-blocked / converged.

## 0. The headline, with counts

Across 5 sessions, ~60 declared walls were farmed. Roughly **two-thirds were broken** after a push; of the remainder most were
*understood and relocated* (the true limit named with a number) rather than left as "can't". **Not one wall was broken by
more of the same building.** Each break came from one of nine moves (section 2). The owner's pushes were short and nearly
identical; the content-bearing ones were the questions "have you researched and fully understood that negative?", "trace where
the signal is lost, all the way up", "was the data being fed to it brain-foundational?", "how does the brain do it?" and
"are you sure?".

## 1. Per-session ledger (wall → push → outcome), abbreviated

### Solver `5fb58138` — name-bridge (P1) → meaning-fusion live coverage (P2)
| wall declared | push (owner, verbatim) | what broke it |
|---|---|---|
| levers "dead ends"; residual facets "never stated" | *have you researched and fully understood those negatives?* | lever-2 had tested a strawman; READING the documents showed the facets were stated → extractor gap; scoped to `flat/appos` → doc-local +0.072 CI-sep |
| "genuinely missing entity knowledge" | *confirm upstream components are fully brain foundational, down to the math they do* | math audit found flat additive blend + linear recency; graded constraint-integration > hard gate; doc-local +0.080; whole-slice cap then confirmed GENUINE (understood, not broken) |
| "metric collapses (0.012) at full scale" | (cron push) | harness fidelity bug: ranked against 4400 vocab instead of the loop's ~556-anchor pool → +0.096 CI-sep |
| three NOT_BF rungs (bag, fixed 0.45 threshold, arc-eager) | *fix them, fully brain foundational, right not easy* | grounded-distinctive sidesteps bag+parser (+0.182); fixed cosine → self-calibrating SDT criterion |
| is-a "0.65 WordNet ceiling, circular" | (build it properly) | Rogers-McClelland property-SVD with no WordNet 0.260 vs 0.188 |
| "read is-a edges too sparse" | *I think we've done work on a read-edge genus — can you look?* / *can you grow the corpus?* | existing `definitional_extraction` found; simplewiki already on disk: 320 → 6,660 edges (43% coverage); fusion +0.055 CI-sep |
| "limit is referent-grounding DATA" | *why the fuck would we be focusing on prediction? How does the brain do what we're trying to do?* / *foundational data build — make it happen* | DINOv2 over THINGS; gold changed to THINGS-behaviour n=1438; later MEN 391 pairs; multi-exemplar +0.086; fused 0.72 vs best single 0.64 |
| "~18 pairs live coverage" (carried assumption) | (cron: any more we can push?) | tested the assumption: live SimLex 0 covered but MEN RSA n=125 visual ρ 0.698 vs incumbent −0.015, **+0.31 R²** — the biggest live number of the arc |

### Solver `83fd02db` — population code (PPC) → parser (pri-3) → is-a → reading-learned arc scorer
| wall | push | what broke it |
|---|---|---|
| reliability "sparse" (0.6% of reads) | *sparse? you know of the phase diagram right?* | moved the operating point: N=30 sub-readouts, Poisson noise ∝ 1/√gain → dense on 52%, deferral +0.049 CI-sep |
| "channels redundant, need depth" | *identify what that next gap is… reason what could provide it* / *has anyone worked on this in literature?* | measurement refuted redundancy; real gap = relation-blind (syn-vs-antonym AUC 0.51); Osgood evaluation axis via existing `affect_lexicon` → AUC 0.75, +0.183 CI-sep |
| "99% of head error is SCORER; first-step reading hits the right-branching trap" | *can you prototype the fix for the surface perceptron?* | the lexical term was POLLUTING: POS-only EM 0.312 → **0.463** (the earlier "text-only ceiling" was this artifact) |
| DMV negative | *research this negative until we understand it 100%, then tackle the actual wall with mathematical BF precision* | soft-EM inside-outside verified to 1e-14 → fair negative; per-arc decomposition: half the gap is treebank convention; nsubj via existing organ 0.565 → 0.714 |
| fully-BF chain collapses (UAS 0.03) | *do it — mathematically BF and right, not easy* | admitted k-means POS induction was "the easy path"; Brown MI-exchange clustering → 0.745, chain → 0.238 |
| "only the generative world model remains" | *do we fully understand the negative? … We have a world model — should we test it?* / *In another solver we found X. Are you sure?* | "I over-claimed"; errors are CONFIDENT (1.3% uncertain vs 21% wrong) → structure is the lever; coordination parallelism cc 0.078 → 0.218 |
| upstream NOT_BF | *are these BF confirmed mathematical? It's critical for upstream to be BF* | Gleitman closed-class scaffold + syntactic bootstrapping: fully-BF chain 0.238 → **0.4057**; NAMED categories beat higher-quality unnamed clusters |
| "acl out of scope; nmod ambiguity-limited" | *do research to verify the remaining levers, then implement BF and right, not easy* | relativizer/filler-gap cue + boost w=25 overcoming a prior penalty: acl 0.013 → **0.394**; nmod reframed by Ratnaparkhi 1994 as missing-statistic, not pinned |

### Solver `e6f6bac1` — grounding audit → reward cluster → harm/help → POS → who-was-affected → coref consolidation
| wall | push | what broke it |
|---|---|---|
| grounded read-out "tie" with counting (0.036 vs 0.046) | *brain foundational components rely on brain foundational components upstream — trace those signals back… don't half-ass this* | three upstream non-BF links: hardcoded `POS="N"`, raw centroid composition, syntagmatic bag → 0.147 > 0.143; then DIRECT grounding **0.475** vs ~0.04 for the whole distributional family |
| "the arc-factored scorer is the ceiling" | *we're clearly not deploying a mathematically correct parser, or something is not getting the right signal. Trace where that's being lost* | gold-ablation trace: POS 30% / head 36% / labeler 33%; labeler third fixed (voice correction + ranker) |
| POS third "not recoverable by any standalone correction" | *I feel like we do NOT understand what we're working on here… understand deeply how the brain does this, all the signals, then trace bottom-up* | instrument corrected; gold-parse ceiling 0.88 vs 0.80; decomposition parse .08 / labeler .09 / decision .03 |
| "the real B" refuted (cue-integration worse, MINERVA echo loses) | *research to understand why this didn't work, and then how to do it right* | WRONG LAYER: echo built for POS (already ECE 0.003) while the pathology was attachment; oracle kill-gate: 40% of hard cases have no selectional signal → knowledge sparsity |
| situation model | *do it and implement any optimizations… BF, right not easy* | a JOIN that did not exist (undergoer token ↔ coref chain): salience prior 0.4545 vs recency 0.1818, +0.27 CI-sep |
| fusion −0.026; IC below chance | *please research these negatives to fully understand — we clearly missed this* | Kehler-Rohde: only the PRIOR had been built, the LIKELIHOOD (grammar) was missing; dormant `_principle_b_filter` unwired; `ROLE_PROMINENCE` backwards for object anaphors; +0.093 |
| consolidation "STRONG, not complete (5 gaps)" | *please address those gaps and any other opportunities, bf and right, not easy* | 3 of 5 closed byte-identically |

### Solver `fa9e276f` — WIQA causal sign → common-noun binder → sense wire
| wall | push | what broke it |
|---|---|---|
| "text is exhausted for the sign (7 sources)" | *there must be databases that have implications for this… math and physics (which we do) and maybe economics?* | sign COMPUTED from a runnable formal model (stoichiometry reactant−/product+; ∂Y/∂X; 2nd law) + passage gate + direct-influence store + Levins press-perturbation: falsifier tie → **+0.175 CI-sep**; resolver 0.994 |
| expansion "collapsed precision to a falsifier tie" | (how did physics hold precision?) | GRAIN rule: store direct influences only, simulate net → +0.122; entropy organ pairing +0.062 |
| "information limit" on same-head coref | *do we understand this negative fully? What is the actual wall?* / *exploratory probes to really nail this down?* | merge-collapse found by COUNTING (0/3224 decisions held ≥2 same-head referents); oracle separation+recency **+0.363 CI-sep** → the wall is separation, not resolvability |
| "do not build the coordinate substrate" | *you made one component brain foundational and it didn't work? which one? was the data being fed it brain foundational?* | the SEM was fed a 12-dim norm-mean; per-entity D=2048 filler, unbind-recovery 1.0 |
| "FHRR is not a general comprehension lever" | *this seems like a very strange and wrong conclusion. We can encode anything we want in FHRR… how does the brain do it?* | cosine READOUT structurally cancels role bindings; unbind+cleanup 0.53 → **1.000** |
| sense wire "converged" | *research all these results so we fully understand them… does understanding provide additional opportunities* | root principle found: sense helps graded discriminative consumers (WiC 0.749, SCWS +0.016), never OR-over-senses licensing → the consumer is the lever |

### Old main `07552ac4` — strategy/integration (its own walls were process walls)
| wall | push | what broke it |
|---|---|---|
| full board `--run` "unreliable in this environment" | *isn't that alarming* | `_hashseed_guard.py` `os.execv` on import re-exec'd the run mid-flight (a 4-day-old regression); pinned the hash seed |
| "coref test failure is pre-existing" | (same press) | measured on real data: a real regression in the legacy join; bounded to the banned 19c eval; mis-call corrected on record |
| "nothing bounded left; disarm" (several times) | *have we resolved all the BF organs? logged which solutions require which updates?* / *identify the next 2 highest priority problems* / *we don't yet have a robust process* | propagation ledger; two problems posted; `substrate_health.py`; rung-3 abduction landed (had been deferred as "invasive") |
| "creating organs left and right" | *they're the same organ with different arms. Have we run this analysis against research?* | 83 organs → ~25 structures; coref 6→1 solved by the fleet, byte-identical |
| "fresh pass later" deferrals (×3) | (the loop itself) | "the loop is my working time — fresh capacity later isn't a real option"; all ported; 0.5818 CI-sep |

## 2. The nine moves that broke walls (the method; each tied to evidence above)

1. **Trace upstream until you find the part that is not brain-foundational.** Every "tie" or "collapse" traced upstream found
   one: hardcoded POS, raw centroids, a syntagmatic bag, k-means POS induction, a 12-dim norm-mean input, a fixed cosine
   threshold, a lexical term polluting an EM. *"If a truly BF component is not working, some component it relies on is not BF."*
2. **Check the INPUT the BF component received, and the READOUT applied to its output.** A brain-faithful SEM on non-BF input
   (12-dim) and a cosine readout that cancels role bindings both masqueraded as capability ceilings (0.53 → 1.000).
3. **Run an oracle-ceiling probe before calling a limit.** Perfect separation + recency showed +0.36 headroom behind an
   "information limit"; gold-parse oracle 0.88 vs 0.80; oracle selectional reranker 0.53 vs 0.47 (a justified stop).
4. **Count, don't narrate.** Merge-collapse (0/3224), confident-errors (1.3% uncertain vs 21% wrong), channel correlation
   (0.08–0.18, not redundant), "~18 pairs" (actually 0 live, 125 on MEN). Each story fell to a count.
5. **Check the floor and the instrument.** Weak left-adjacency floor; ranking against the wrong pool (0.012 → +0.096);
   the board's own re-exec bug; an empty mention column in a synthetic test; smoke underpowered for a real arm.
6. **Move the operating point (phase diagram), never accept "at this config".** N=30 population vote made a 0.6% signal
   dense; prior-penalty boost w=4 null, w=25 → acl 0.394; SVD densification HURT (identity lives in sparse contexts) — sweep.
7. **Supply the missing COMPUTATION SOURCE, not more text.** The causal sign was unreachable from 7 prose sources and came
   from runnable physics/stoichiometry models plus a direct-influence grain rule; referent grounding came from images, not text.
8. **Find the existing organ / the missing JOIN / the missing half of a pinned model.** `definitional_extraction`,
   `affect_lexicon`, `incremental_subject_before`, `_principle_b_filter`, the entropy organ; the undergoer↔coref JOIN that did
   not exist; a Bayesian model with only the prior built. "Landed ≠ live" recurred in every session.
9. **Change the gold to what the ability actually is.** SimLex (23 covered pairs) → THINGS-behaviour 1438 → MEN 391; the
   content-optimal configuration was not the task-optimal one (re-measure the real bar with the final scorer).

And the meta-pattern: **the wall was broken only when the session stopped defending the verdict and asked the owner's
question of itself.** Self-broken walls were mostly task-design; owner-broken walls were fidelity and framing.

## 3. Strategy's self-check before any "wall" is written (apply to self and to every dispatched agent)

- Which END component is this about, and is it 100% BF (the computation, not the name)? What signals does it need?
- Trace those signals up the chain with a NUMBER per rung (the gold-ablation / per-rung consistency table). Where is the loss?
- At the loss: is the INPUT BF? is the READOUT the brain's operation? is the FLOOR fair? is the INSTRUMENT measuring the live path?
- Have I run the oracle-ceiling probe? Have I COUNTED the claimed phenomenon?
- Have I swept the operating point (density, dimension, gain, threshold, prior weight)?
- Is there a missing computation source (a formal model, a perceptual modality, a curated asset) rather than missing text?
- Which existing organ computes this already? Which join is missing? Which half of the pinned model is unbuilt?
- Is the gold measuring the ability? Re-measure the real bar with the final configuration.
- Only after all of the above: file a SPECIFIC board question naming the slice, the count, and the two candidate next moves.

## 4. What this means for running the fleet from here

- Put the nine moves + the owner's messages into every brief's SOLVER OPERATING PROTOCOL (pointer to both files) and into every
  dispatched agent prompt verbatim (messages 1, 3/7, 9).
- The owner's live presence mattered most on: "are you sure?", "was the input BF?", "which databases exist for this?", and
  "how does the brain do it?" — the questions a session will not ask itself. Recommended live solver sessions: the generative
  world model (pri-1) and the reading-learned parser acquisition, where these questions will be needed most.
- Strategy must schedule its own end-of-arc gate (message 9) on every landing, including its own (done for pri-14 tonight).
