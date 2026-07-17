# Research: classical Open-IE / glass-box parsing frontier vs. hand-built grammar tail

**Date:** 2026-07-17
**Trigger:** HARD_FAIL of glass-box, no-LLM, hand-built SVO/passive/coordination/relative-clause pipeline on real general-register prose. 58.6% of sentences unhandled ("other" bucket); precision collapsed to ~0.18 via spurious firing (not clean abstains) on unhandled constructions; closed relation vocabulary flagged as a second, possibly-larger bottleneck. Published classical (non-neural) Open-IE reaches ~0.40-0.57 precision on real prose — the question is whether to adopt that toolchain, keep hand-building, or add an abstain-gate first.
**Method:** 3 parallel Sonnet lit-scan sub-agents (psycholinguistics of parse failure; parser-architecture + verb-vocabulary acquisition; classical Open-IE/parser precision ceilings + glass-box legality), synthesized here. Calibration penalty per [[feedback-lit-scan-calibration-penalty]] applied throughout (deflate 0.15-0.25, cap novel-synthesis P at 0.50).

---

## HEADLINE

The biology does **not** license "graceful abstention" as the brain's default behavior on unparseable constructions — good-enough parsing research shows humans commit to confident, plausibility-driven, often-WRONG shallow interpretations (the same failure mode our pipeline exhibits), not silent abstains. But the brain *does* carry a detectable difficulty/anomaly signal (P600, regressions, reading-time slowdown) that is never wired into a hard pre-commit gate — that's an opportunity, not a mechanism to copy. Separately, the architecture question is unambiguous: human syntax is a single broad-coverage generalizing system, not a stack of hand-coded per-construction rules, and the open-class verb/relation lexicon is acquired by general, scale-agnostic mechanisms with no closed ceiling. Both lines of evidence point the same direction: **adopt the classical, non-neural, glass-box-legal toolchain (clause-typology parser + open relation vocabulary) as the coverage fix, and add a strict pattern-match abstain gate as a cheap, substrate-native (not brain-copied) precision fix on top of it.** The closed relation vocabulary is an implementation gap, not a fundamental wall.

---

## (a) Biology-first account

### 1. Graceful abstain vs. garbled misparse — NOT graceful abstain by default

Ferreira's "good-enough" (GE) parsing program (Ferreira 2003, *Cognitive Psychology*; Ferreira, Bailey & Ferraro 2002, *Current Directions in Psych. Sci.*; Ferreira & Patson 2007) is the direct evidence base. On noncanonical constructions (passives especially), readers default to a shallow **NVN "first-noun-is-agent" heuristic** that misfires and is reported as a *confident, single, often-wrong* interpretation — not a hedged or partial one. Christianson, Hollingworth, Halliwell & Ferreira (2001) — the classic "the horse raced past the barn fell" studies — show that even after readers correctly resolve the ambiguity, residual wrong-parse content lingers and gets affirmed alongside the correct answer (Slattery et al. 2013: "remnants of earlier parses linger and affect offline responses"). Qian, Garnsey & Christianson (2018) found **plausibility, not grammaticality, predicts what comprehenders land on** when a construction resists full parsing — i.e., the parser doesn't fail safe, it fails toward "a meaning that sounds sensible."

This is a load-bearing finding for the diagnosis: **our pipeline's spurious-firing failure mode (wrong triples, not clean abstains, on unhandled constructions) is brain-consistent, not a bug unique to a toy hand-built grammar.** The good-enough-parsing literature explicitly flags an evidence gap here too: no study found addresses explicit metacognitive/confidence *awareness* of misparses — humans are not shown to know they got it wrong.

### 2. Is there a confidence/gate signal? Yes, but post-hoc, not a pre-commit gate

P600 (Osterhout, Holcomb & Swinney 1994; Gouvea, Phillips et al. 2010) robustly indexes syntactic reanalysis / garden-path detection, and eye-tracking shows regressions land selectively back on the misanalysis locus (Meseguer, Carreiras & Clifton 2002) — evidence the system retains *some* diagnostic trace of what went wrong. ELAN (early phrase-structure violation detection, Friederici) is a candidate even-earlier signal but is contested in recent literature as possibly a spillover artifact rather than a genuine early detector. **Extrapolation, clearly flagged:** neither literature frames P600/ELAN as a decision-theoretic commit-vs-abstain gate — they are read out as *difficulty/anomaly* signals *after* a parse has already been attempted, used for repair/reanalysis, not for withholding output. The literature gives no evidence the brain uses these signals to suppress output the way an abstain-gate would.

**Strategic reading:** an explicit graceful-abstain gate is therefore a genuine substrate-native affordance, not a brain transplant. This matches the "two frontiers" doctrine already in force: brain-faithful-first, nativize-second, not as an escape hatch. Here the honest brain-faithful baseline is "commit to a wrong answer" — worse than what we want. The gate is a deliberate, well-motivated departure exploiting glass-box legibility (exact pattern-match/no-match readout) that a biological system can only approximate crudely via graded RT/regression/P600 signals. It should be justified on its own engineering merits (precision), not framed as "what the brain does."

### 3. Full parser vs. hand-coded rule stack

Incremental/predictive parsing accounts (surprisal theory: Hale, Levy; PLTAG: Demberg & Keller) model human sentence processing as **one general probabilistic mechanism operating over a broad-coverage grammar** — garden-path effects, frequency effects, and antilocality effects all emerge from this single mechanism, not from separate per-construction handlers. Compositional-generalization work (e.g. AM-parser on COGS) shows generalization is best achieved by building compositionality into the parser architecture itself, not by stacking special-case rules. Construction Grammar is not a counter-argument: constructions are learned *inductively via general statistical/associative mechanisms* into one gradient network of item-specific and schematic knowledge, not enumerated as isolated handlers (Boas; children's productive extension of syntactic frames to novel verbs, Journal of Child Language). **Net verdict: broad-coverage single-mechanism parsing is the human architecture; hand-coding one construction at a time is not the human strategy, and (extrapolated, engineering-implication) is not the right strategy for an engineered glass-box system either.**

### 4. Open-class relation/verb vocabulary — acquisition is general and unbounded

Verbs pattern with the open lexical class: vocabulary growth is front-loaded on nouns then verbs/adjectives (the "vocabulary spurt," ~18-24 months, MB-CDI data), with closed-class function words not appearing in bulk until roughly the 400-word mark. The acquisition mechanisms for new verbs — fast-mapping, cross-situational statistical learning (Scott & Fisher 2012, extended to 2.5-year-olds), syntactic bootstrapping (Landau & Gleitman 1985; meta-analytically confirmed across 60 experiments / 849 participants, Nature Reviews Psychology 2024), semantic bootstrapping (Pinker 1984/1994), and usage-based generalization from entrenched exemplars — are all **general-purpose and scale-agnostic**: the same apparatus that learns the first 50 verbs learns the next 20,000, with no closed-set ceiling or qualitative regime change. (Flagged gap: no source in this scan gives a clean verb-only count at each age; the total-vocabulary trajectory — ~500 words at 2yo to ~18,000-20,000 productive adult words — is the direct evidence, and the open-vs-closed growth *pattern* is directly evidenced even though the verb-only absolute counts are not.)

**Verdict on the relation-vocab bottleneck: implementation gap, not fundamental.** Nothing in the acquisition literature supports a small closed relation set as an architectural necessity; it supports exactly the opposite — an open-class, continuously-extended lexical mechanism is how the biological system does it at every scale.

---

## (b) Engineering read: adopt the classical toolchain, glass-box confirmed

### Numbers that matter (deflate: benchmark corpora are general-register news/Wikipedia, not literally blogs/reviews — directionally close but not identical to our eval slice)

- **CaRB** (Bhardwaj et al. 2019): OLLIE P=0.505 R=0.346 F1=0.411; **ClausIE P=0.411 R=0.496 F1=0.450** (best F1 of the three).
- **WiRe57** (Léchelle et al. 2018): ReVerb P=0.569 R=0.121 F1=0.200; OLLIE P=0.347 R=0.175 F1=0.239; ClausIE P=0.401 R=0.298 F1=0.342.
- These numbers directly corroborate the task-prompt's cited 0.40-0.57 classical frontier — confirmed, not just asserted.
- ClausIE's advantage traces to a structural fact directly relevant to our 58.6% unhandled bucket: **ClausIE is built on the full Quirk clause-type taxonomy (SV, SVA, SVC, SVO, SVOA, SVOC, SVOO)**, which explicitly includes copular (SVC) and adjunct (SVA) clause types — exactly the constructions our toy grammar's "other" bucket flags as unhandled (copular, adjuncts, PPs). Adopting a ClausIE-style clause grammar is not a generic upgrade; it directly targets named gaps in the failure report.

### Failure modes of the classical systems themselves (so we know the frontier we'd be buying)

- **Negation and modality are explicitly unhandled** by ReVerb/OLLIE/ClausIE-class systems — a negated claim can be extracted as if asserted positively. This is a spurious-firing failure, structurally identical to our own current bug, just smaller in surface area.
- **Coordination scope** is a known, only partially-fixed error source (ClausIE bolts on a per-conjunct substitution heuristic, not general scope resolution).
- **Non-verbal relations beyond ClausIE's clause types** (deep appositives, complex nominalizations, anaphora, implicit arguments) are still out of scope for all three systems — explicitly flagged as such in the original papers.
- **Parser-error propagation dominates ClausIE's own error analysis**: "most extraction errors were due to incorrect parse trees," i.e., these systems inherit whatever the underlying dependency parser gets wrong and do not gracefully absorb parser mistakes.
- **The upstream parser is itself degraded on real prose.** Google Web Treebank / SANCL-2012 shared task: best classical systems (feature-based, non-neural, of the same generation as MaltParser/Stanford-classic) reach only **80-84% F1/LAS on web text**, versus >90% F1 and ~97% POS accuracy on WSJ newswire — a real, load-bearing ceiling below which our F1 cannot rise no matter how good the clause grammar is. (One secondary, less-certain figure: MaltParser on Twitter specifically showed an ~20-point absolute LAS drop from in-domain, only partially recoverable via uptraining — flagged as less-verified, PDF fetch failed.)

### Glass-box legality — confirmed, not assumed

- **MaltParser**: transition-based shift-reduce, classified per-decision by SVM (LIBSVM) or MaxEnt (LIBLINEAR) over hand-engineered features (POS tags, stack/buffer state). No neural component in the classic/default configuration. Every decision traces to an inspectable feature vector.
- **Charniak / Collins parsers**: lexicalized PCFG with bilexical head-word statistics, max-entropy-style scoring. Classical generative/statistical, no neural net (neural rerankers are separate, later systems).
- **Stanford Parser (classic, pre-2015)**: PCFG + dependency-conversion rules; Stanford's neural dependency parser (Chen & Manning 2014) is a distinct, later system — the classic PCFG parser used by ReVerb/ClausIE is not it.
- **ReVerb / OLLIE / ClausIE**: rule/pattern-based on top of POS tags + dependency parses (syntactic + lexical constraints for ReVerb; bootstrapped dependency-path patterns with logistic-regression confidence for OLLIE; hand-built clause-type grammar, no training data at all, for ClausIE). Every extraction traces to a specific rule/pattern/dependency-path match.
- **Verdict: genuinely non-neural and glass-box-legal when pinned to the classic backend**, confirmed across all five systems checked.

### Engineering cost

Low. All three OIE systems ship as standalone prebuilt Java `.jar` files runnable from the command line, with source available (knowitall/reverb, knowitall/ollie on GitHub; ClausIE has a mavenized fork). OLLIE needs a separate MaltParser model download; ClausIE bundles the Stanford Parser jar directly; ClausIE requires no training data (pure rule-based). Realistic integration cost is JVM interop plus output-format adaptation — on the order of 1-2 days, not a multi-week reimplementation. This is "install a library," not "rebuild the system."

---

## (c) Recommendation

**Two-track fix, both cheap relative to continuing to hand-build the 58.6% tail one construction at a time:**

1. **Coverage fix (primary, do first): adopt a classical clause-typology parser+extractor pinned to a non-neural backend** — ClausIE-style (or reimplement its clause-type grammar directly in-house if avoiding a JVM dependency is preferred; the grammar itself, not just the jar, is the transferable asset) on top of MaltParser or a classic PCFG parser (Charniak/Collins/Stanford-classic). This directly targets the named unhandled-construction categories (copular/SVC, adjuncts/SVA) and buys the ~0.40-0.50 F1 classical frontier — with the important caveat that ~15-20 points of headroom is structurally capped by real-prose parser accuracy itself (80-84% F1 ceiling on web text), not by clause-grammar coverage.
2. **Precision fix (do alongside or slightly after, cheap either order): add a strict pattern-match abstain gate** — require ALL syntactic slots of a candidate construction pattern to be satisfied before emitting a triple; abstain (emit nothing) on partial/ambiguous matches rather than partial-firing. This is NOT a brain-copied mechanism (the brain does not do this by default — see biology section) but a deliberate exploitation of glass-box exactness that a biological system can only approximate. It should improve precision on the CURRENT grammar even before the parser upgrade lands, and should compound with it afterward — note that even classical systems still spuriously fire on negation/coordination-scope, so a stricter internal gate has headroom to beat the classical precision numbers, not just match them.
3. **Open the relation vocabulary**: extract the lexicalized predicate/verb itself as the relation (open-class, unbounded) rather than mapping into a small closed set; add clustering/normalization as a downstream, separate step. Per the acquisition literature, gating extraction on a small fixed relation list is an implementation shortcut, not a structural requirement.

---

## Falsifiable predictions — HARD-PASS / HARD-FAIL

### Cell 1: classical-toolchain-frontier cell (clause-typology parser + open relation vocab, non-neural backend)

- **Prediction A:** unhandled ("other") bucket drops from 58.6% to well below 30% on the same real-prose eval set, because ClausIE-class clause typology explicitly covers copular/adjunct constructions currently bucketed as "other."
- **Prediction B:** precision rises from ~0.18 toward, but likely below, the published 0.40-0.50 classical frontier (deflate for open relation-vocab noise and smaller/dirtier eval set than CaRB/WiRe57).
- **HARD-PASS:** precision >= 0.35 AND unhandled-bucket <= 30% on held-out real-prose sentences, with zero neural components verified in the parse path (no torch/embeddings/learned weights anywhere in the pipeline — pure feature/rule/lexicon, auditable per-decision).
- **HARD-FAIL:** precision stays < 0.25 after the clause-grammar upgrade (would indicate the bottleneck is NOT construction coverage but real-prose parser accuracy itself — the 80-84% web-text parser ceiling capping everything downstream) OR unhandled-bucket stays > 45% (would indicate real prose has construction diversity beyond even the full classic clause typology, e.g. discourse-level/cross-sentence phenomena not addressable by a sentence-local grammar).

### Cell 2: graceful-abstain-gate cell (cheap, can run before or independent of Cell 1)

- **Prediction:** gating each rule-firing on full-slot-match (abstain on partial/ambiguous match) raises precision substantially on the CURRENT toy grammar at the cost of recall/coverage.
- **HARD-PASS:** precision >= 0.40 on the subset of sentences where the gate fires (gated-precision beats the classical published floor), even if overall coverage/recall stays low.
- **HARD-FAIL:** precision on the gated-fire subset stays < 0.25 — this would mean the spurious firing is not from partial/ambiguous matches at all but from genuinely miscalibrated pattern-to-construction mapping even within the grammar's intended scope (a grammar-correctness bug, not a confidence/coverage problem) — a different, more serious diagnosis requiring the toy grammar's core rules to be re-derived, not just gated.

---

## (d) Relation-vocab bottleneck: implementation gap, not fundamental

Directly supported by the acquisition literature (fast-mapping + cross-situational learning + syntactic/semantic bootstrapping + usage-based generalization all scale-agnostic, open-class, no closed ceiling observed from ~50 to ~20,000 words). Recommend open-vocabulary extraction (lexicalized predicate as relation) over closed-list mapping. This is the smaller of the two engineering asks (no new parser/toolchain needed) and should be bundled into Cell 1 rather than run separately.

---

## Cross-thread synthesis

This connects to the standing "two frontiers" doctrine ([[project_two_frontiers_brain_faithful_world_plus_substrate_native_world_later_thrust_USER_2026-07-16]]): the biology here gives a brain-faithful baseline that is itself mediocre (confident misparse, not graceful abstain) — a case where nailing the brain-faithful baseline first (Cell 1, the clause-grammar/broad-coverage-parser fix, which mirrors "the brain uses one general mechanism not per-construction rules") should be optimized to frontier BEFORE the substrate-native augmentation (Cell 2, the abstain gate, which the brain does not do) is layered on. This also reads as a direct instance of [[feedback_nail_the_brain_baseline_first_then_shore_up_real_weaknesses_USER_2026-07-16]]: our hand-built grammar losing badly to the classical-but-still-glass-box frontier is presumptively an implementation gap (too few constructions handled), not a structural wall — confirmed here by both the parser-architecture literature (broad-coverage beats hand-coded stacks) and by the direct numeric comparison (0.18 vs 0.40-0.50 on the same problem class with published, reproducible systems).

## Substrate-product implications

A no-LLM, glass-box reading pipeline that can only handle ~40% of real-sentence constructions with ~0.18 precision is not usable for grounding real prose into the substrate's fact store — most extracted "facts" would be noise. Closing this gap via a classical, inspectable, non-neural clause-grammar + open relation vocabulary is directly on the critical path for the "PIVOT — build the ideal knowledge foundation" program's read-side: it converts real prose into a usable trickle of verified relational facts instead of a flood of wrong ones, while preserving the no-LLM-at-runtime invariant (the parser components run at ingest/build time under human/tooling supervision, and remain fully auditable). The abstain gate additionally gives an exact, substrate-native precision lever (glass-box exact-match gating) that has no clean biological analog but is cheap and directly buys precision without waiting on the parser-upgrade cell.

## Citations (verified count)

Directly-cited, traceable to specific papers/benchmarks (not just secondary summaries): **~18** distinct primary/benchmark sources across the three lit-scans (Ferreira 2003; Ferreira Bailey Ferraro 2002; Ferreira & Patson 2007; Christianson et al. 2001; Qian Garnsey Christianson 2018; Slattery et al. 2013; Meseguer Carreiras Clifton 2002; Osterhout Holcomb Swinney 1994; Gouvea/Phillips et al. 2010; Hale/Levy surprisal; Demberg & Keller PLTAG; Landau & Gleitman 1985; Pinker 1994; Scott & Fisher 2012; syntactic-bootstrapping meta-analysis 2024; Fader Soderland Etzioni 2011 ReVerb; Mausam et al. 2012 OLLIE; Del Corro & Gemulla 2013 ClausIE; Bhardwaj et al. 2019 CaRB; Léchelle et al. 2018 WiRe57; McClosky Charniak Johnson domain-adaptation; Petrov & McDonald 2012 SANCL web-treebank shared task). Several numeric claims (exact ReVerb/OLLIE/ClausIE original-paper P/R tables, MaltParser-on-Twitter LAS drop) came from secondary/survey sources because primary PDFs failed to render for the sub-agent — flagged inline above as less-certain; the CaRB and WiRe57 benchmark numbers, which are the load-bearing numbers for the recommendation, ARE directly sourced from those benchmark papers' own reported tables.

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis claims here (the "two frontiers" framing, the P600/ELAN-as-gate extrapolation, the engineering-implication inferences from developmental literature) are capped at P<=0.50 and explicitly flagged as extrapolation throughout. Direct empirical claims (CaRB/WiRe57 numbers, non-neural confirmation, good-enough-parsing findings) carry higher confidence (~0.65-0.75 after the standard 0.15-0.25 deflation) since they are direct, converging, peer-reviewed citations, not synthesis.
