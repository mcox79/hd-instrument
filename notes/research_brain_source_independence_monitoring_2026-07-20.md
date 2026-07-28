# Research: how the brain (fails to) detect non-independent sources — grounding for a real-document common-mode-detector validation

**Date:** 2026-07-20
**Dispatch:** research drill, 3-axis (biology-first, generic-terms external search per query-privacy discipline)
**Sub-agents:** 2 parallel Sonnet lit-scans (axis 1: source-monitoring/illusory-truth; axis 2: crowd-independence/echo-chamber) + Opus synthesis (axis 3, design)

---

## (a) HEADLINE

The brain has **no automatic, default mechanism** that discounts repeated information for shared origin — Johnson's source-monitoring framework shows source-tags are inferred heuristically and decay faster than content (sleeper effect), and the direct behavioral signature is the **illusory truth / illusion-of-consensus effect**: people rate a single source repeated N times as almost as credible as N genuinely independent sources. Detecting non-independence is a real but *fragile, effortful, non-default* competence (Lorenz et al. 2011 PNAS on crowd-wisdom collapse; illusion-of-consensus work 2022-2025) that only activates under deliberate structural conditions (explicit accuracy-focus, anonymized/decorrelated elicitation, a maximally salient/memorable source cue). This is a **negative-existence-proof for a "detect non-independence" competence being cheap/automatic** — which is informative for the substrate two ways: (1) it validates that a *dedicated, explicit* common-mode detector is doing something brains do NOT do for free, i.e. real added value, not redundant with an assumed-innate human skill; (2) the boundary conditions in the literature (verbatim > paraphrase > topic-only; salience of source cue matters) give a natural graded-difficulty axis to borrow directly for the real-document validation design in axis 3.

A fair, non-construction-determined real-document test looks **tractable** — genuine near-duplicate/paraphrase/same-source-derived document sets exist in public corpora (news-wire dedup, PAN plagiarism-detection corpus, MRPC/Turku paraphrase corpora) without needing to inject synthetic correlation.

---

## Axis 1 — Source monitoring, sleeper effect, illusory truth (mechanism + failure mode)

**Source Monitoring Framework** (Johnson, Hashtroudi & Lindsay 1993, *Psych Bulletin*): there is no literal provenance tag stored with a memory. Origin is *inferred post hoc* from qualities of the trace — perceptual/sensory detail, contextual/spatiotemporal binding, semantic/emotional content, and a record of cognitive operations (effortful internal generation leaves a different signature than passive external perception). This is a **heuristic classifier over trace features**, not a lookup. **Source confusion** happens when two memories share overlapping features and the classifier misfires — the direct mechanism behind cryptomnesia (~3-9% of generation tasks in lab studies produce unconscious "plagiarism" of one's own prior exposure).

**Sleeper effect** (Hovland/Kelman/Pratkanis program): a low-credibility source's message can regain persuasive power after a delay. The **dissociation account**: message content and the source-discounting cue decay at different rates — the source-message *link* decays faster than the content itself. Net effect: "remembering what was said, forgetting who said it (or that it should be discounted)." This is the same asymmetry — source-tags are structurally more fragile than content — that drives illusory truth.

**Illusory truth effect** (Hasher/Goldstein/Toppino 1977; Begg/Anas/Farinacci 1992; Fazio et al. 2015-2019; Unkelbach/Dechêne/Nadarevic program): repetition raises perceived truth via **processing fluency misattributed to validity**, independent of source credibility or even explicit knowledge that the statement is false. Directly on point: recent direct tests of "repeated by many vs. repeated by one" and the **illusion-of-consensus** literature (2022-2025, incl. *Memory & Cognition* 2025 "Explaining away the illusion of consensus") show people rate a single source repeated N times as **nearly as credible/consensual as N independent sources** — by default, repetition is read as independent corroboration. A distinctive/memorable source can block the effect for known falsehoods (Begg et al. 1992); explicit front-loaded deception warnings cut the effect roughly in half but a 1-week delay reinstates it even in accuracy-primed subjects, because source memory decays faster than familiarity/fluency (parallel to the sleeper-effect dissociation). Making the repetition/common-origin **conspicuous** does let people correctly attribute the fluency to repetition rather than truth — but this is an effortful, salience-gated override, not the default read.

**Verdict axis 1:** the brain's default engine treats "repeated" ≈ "independently corroborated." There is no free, automatic non-independence discount; the override exists only when the shared-origin cue is unusually salient or actively primed for.

---

## Axis 2 — Redundant/correlated testimony and crowd wisdom

**Wisdom-of-crowds independence requirement**: Condorcet Jury Theorem / Galton-style averaging formally require independent errors — correlated errors erode or reverse the benefit of aggregation. **Lorenz, Rauhut, Schweitzer & Helbing (PNAS 2011)** directly tested this: groups given social information between estimation rounds showed **range reduction (opinions converged)** without accuracy improving, and — the key finding for this drill — **confidence rose even though accuracy did not**. Subjects did not discount that peers' later estimates were contaminated by the same shared information; convergence-via-contamination was read as independent confirmation.

**Redundant-witness / testimony-aggregation literature** (epistemology, legal-evidence theory): the formal principle is that correlated/derivative testimonies (witnesses who spoke to each other, or share one upstream source) should count as roughly *one* witness, not several ("corroborative rule" scholarship; Wüthrich & Steele 2025 "The problem of dependency," *Synthese*). The literature explicitly frames distinguishing true independence from apparent corroboration as **pervasive and harder in practice than the formal theory assumes** — i.e. this is a known, named failure mode, not a fringe curiosity.

**Echo chambers / illusion of consensus**: laypeople are demonstrably poor at distinguishing primary from secondary sourcing and tend to **count instances, not distinct origins** — mere repetition alone inflates estimates of how many people hold/know a claim, even absent real social signal ("Illusory Consensus Effect," Collabra: Psychology). This generalizes the illusory-truth finding from "belief in a claim" to "belief about how many independent people believe the claim."

**Positive/mitigating findings**: the competence is not zero, but it is *institutionally engineered rather than spontaneous* — Delphi-style expert elicitation explicitly anonymizes and structures rounds specifically to break contagion/correlation (and audits still find residual correlation above what the aggregation math assumes). Accuracy-focused encoding instructions reliably suppress the illusory-consensus/truth effects; passive misinformation warnings do not.

**Verdict axis 2:** detecting source non-independence is a **weak-to-largely-absent default competence** that becomes real and exercisable only under deliberate structural conditions (anonymized/decorrelated elicitation, accuracy-priming, salient shared-origin cues) — never as a spontaneous heuristic.

---

## Axis 3 — Design + fairness sketch for a real-document validation (Opus synthesis, no external search of substrate specifics)

### Framing from axes 1-2
The literature gives a **graded salience axis** for how detectable non-independence is to an observer, which maps naturally onto a graded-difficulty test design:
1. **Verbatim / exact repetition** — highest fluency signal, source-overlap most recoverable (people notice literal repeats fastest when attention is on it).
2. **Paraphrase / same content, different surface form** — fluency signal weaker, source-overlap harder to spot; this is exactly where the illusory-truth/illusion-of-consensus effect is strongest in the literature (surface novelty masks common origin).
3. **Distant / same-topic-different-content** (shared only via topic or distal common cause, not shared authorship) — genuinely ambiguous; even careful humans disagree here, and a detector *should* start to lose precision in this band, not just get harder.

### Candidate real-document construction (non-injected non-independence)
Public corpora already contain **real, naturally-occurring** near-duplicate/paraphrase/same-source-derived clusters, without needing to synthesize correlation:
- **Wire-service news dedup**: multiple outlets running the same AP/Reuters wire copy verbatim or lightly edited — real same-source-derived documents at web scale (news-clustering corpora, e.g. All-the-News / NELA-GT style collections cluster by story).
- **PAN plagiarism-detection corpus** — purpose-built with graded obfuscation levels (verbatim copy → paraphrase → summary-level derivation) from real source texts; this directly supplies the 3-tier difficulty ladder above, already human-annotated.
- **MRPC (Microsoft Research Paraphrase Corpus)** — real sentence pairs pulled from news articles over 18 months, labeled paraphrase/not; many pairs are literally two outlets' coverage of the same wire event (same-source-derived by construction of the corpus, not by injection).
- **Turku Paraphrase Corpus** — paraphrase pairs manually extracted from independently-produced subtitle translations of the *same underlying media* — a clean "two independently-authored surface forms, one shared origin" case.
- **Independent baseline**: documents from the same corpus but drawn from unrelated stories/topics/time windows — genuinely unrelated real text, not a stripped-down synthetic negative.

### Construction-determinism guards (explicit, pre-registered)
1. **Non-independence must be corpus-native, never injected.** Do not synthetically perturb one document to create a "paraphrase" for the test — use corpora where the paraphrase/duplicate relationship is a real editorial/authorial fact (wire dedup, PAN's real-source-derived pairs, MRPC/Turku pairs), so the detector cannot be gaming an artifact of the injection procedure.
2. **The independent baseline must be real, topically-diverse text, not a degenerate negative.** A baseline of literally-unrelated random sentences is too easy (any detector "passes"); the independent set should be drawn from the same domain/genre/time-period as the non-independent set so surface-level genre cues can't substitute for the actual agreement-structure signal.
3. **Graded difficulty must be pre-registered with an expected failure point**, not just measured post hoc: HARD-PASS should require correct classification on tiers 1-2 (verbatim, paraphrase); tier 3 (distant/same-topic) is explicitly allowed — even expected — to show degraded precision, mirroring where human judgment also degrades. A detector that claims perfect performance on tier 3 is a red flag for a construction-determined (too-easy) test, exactly per [[feedback-synthetic-toy-corpus-outcomes-can-be-construction-determined]].
4. **One variable must differ across arms** (per the standing design-gate discipline): the only thing distinguishing the "non-independent" and "independent" document sets should be genuine common-origin-or-not; document length, genre, topic-diversity, and vocabulary richness should be matched/controlled across both sets so the detector isn't keying on a confound (e.g. duplicate documents being shorter/more templated on average).
5. **A real forced-error control**: include a small set of documents that are topically identical and highly similar in content but demonstrably independently authored (e.g. two separate original reporting pieces on the same real-world event, not wire-copy) — this is the hardest and most important negative, because it's the exact case illusory-truth/illusion-of-consensus research shows humans conflate with true corroboration. The detector's ability to stay quiet here is the most substrate-product-relevant claim (does it beat the human default failure mode, not just detect literal copies).
6. **Report null-rate on the independent set**, not just hit-rate on the non-independent set — per lit-scan-calibration discipline, a detector could "fire on everything" and trivially pass a poorly-designed positive-only test.

### Cheap decisive test
Build a small pre-registered eval set: ~20-30 doc-pairs per tier (verbatim / paraphrase / distant-shared-topic) drawn from PAN plagiarism-corpus tiers (gives 1-2 for free) plus a hand-picked "same real-world event, independently authored" hard-negative set of ~10-15 pairs (news coverage of one dated event from two outlets with no shared wire copy, verified by byline/dateline). Run the detector's agreement-structure signature across all pairs; score against the pre-registered tier expectations before looking at results.

---

## Falsifiable predictions

**HARD-PASS** (detector behaves like a genuine, above-human-default competence):
- Fires (correctly flags non-independence) on ≥85% of tier-1 (verbatim/wire-dedup) pairs.
- Fires on ≥65% of tier-2 (real paraphrase, PAN/MRPC/Turku) pairs.
- Stays quiet (correctly does NOT flag) on ≥85% of the independent-baseline set (same-genre, unrelated topic).
- Stays quiet on ≥60% of the hard-negative set (same real event, independently authored, no shared wire copy) — this is the bar that would demonstrate the detector beats the well-documented human illusory-consensus failure mode.

**HARD-FAIL** (detector is not measuring genuine agreement-structure, or is construction-determined / trivial):
- Fires on <50% of tier-1 verbatim pairs (fails the easiest case — broken instrumentation, not a real negative).
- Fires on >30% of the independent-baseline set (false-fires on unrelated real text — the detector is picking up a genre/topic confound, not shared-origin structure).
- Fires on the hard-negative set (same-event-independent-authors) at a rate statistically indistinguishable from firing on the tier-2 paraphrase set — this would mean the detector, like the human default, cannot separate "same origin" from "same topic, coincidentally similar," and the validation would have reproduced the human bias rather than beaten it.
- Tier-3 (distant/same-topic) shows the SAME fire-rate as tier-1 (no graceful degradation across the difficulty ladder) — a flat response curve across genuinely different difficulty levels is itself evidence the test isn't discriminating real structure.

---

## Cross-thread synthesis

This drill's "independence" is a **different sense** of the word than the one used across the substrate's existing corroborated-signal / independent-witness threads (e.g. `research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`, `research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`, the INV2 authoring-confound-independence thread from 2026-06-13). Those threads are about whether internal *signal channels or estimators* are statistically independent of each other for error-compounding purposes — a within-substrate architecture question. This drill is about whether *external document sources* are independent of each other for evidential purposes — an input-validation question, closer in spirit to the `authoring_confound_audit` line ("independence claims may be single latent factor," 2026-06-13) which found the SAME generic hazard from the opposite direction: apparent independence across parallel authoring tracks was itself confounded by a shared latent factor. That precedent is a useful internal cross-check — the substrate has already, once, caught its own "these look independent but share a hidden common cause" failure mode in its own pipeline (skunkworks INV2 audit), which is encouraging: the underlying mathematical hazard (shared low-rank/common factor masquerading as several independent signals) recurs both in human cognition (this drill) and in the substrate's own authoring process (prior finding), suggesting the common-mode detector targets a real, recurring, non-substrate-specific structural hazard rather than a bespoke one-off concern.

## Substrate-product implications

A validated real-document common-mode detector is a genuine differentiator, not a redundant restatement of an assumed human skill: humans do not do this well by default (axes 1-2), so a system that reliably distinguishes "three corroborating sources" from "one source echoed three times" — especially on the hard case of same-event-independent-authorship — directly targets a documented, named, common failure mode (illusory truth / illusion of consensus / crowd-wisdom collapse under correlated information) rather than a strawman. The product framing should be: "catches what people systematically miss," grounded in cited literature, not "replicates an existing human competence." The graded-difficulty ladder (verbatim > paraphrase > same-event-independent > distant-topic) gives a natural user-facing confidence gradient rather than a binary flag.

## Citations (verified count: 20)

Source-monitoring / illusory-truth (axis 1, 15 sources returned by sub-agent, deduplicated to 15 unique):
Johnson, Hashtroudi & Lindsay 1993 (PubMed); source-monitoring feature-binding (Tandfonline); Sleeper Effect (iResearchNet, Wikipedia, Pratkanis et al. 1988 JPSP PDF); Begg, Anas & Farinacci 1992 (ResearchGate); Fazio et al. "Knowledge Does Not Protect Against Illusory Truth" (APA); "The Trajectory of Truth" longitudinal study (J. of Cognition); "Getting to the source of the illusion of consensus" (ScienceDirect); "Explaining away the illusion of consensus" (Mem. & Cognition 2025); "Repeated by many vs repeated by one" (ResearchGate); "An Illusory Consensus Effect" (Collabra: Psychology); "informative value of type of repetition" (ScienceDirect); Nadarevic & Aßfalg warnings work (ResearchGate); explicit-warnings multinomial modeling (ScienceDirect); "Questioning the truth effect" 2025 (Mem. & Cognition); Cryptomnesia (Wikipedia).

Crowd-independence / echo-chamber (axis 2, 11 sources returned by sub-agent, 5 net-new beyond axis-1 overlap):
Lorenz, Rauhut, Schweitzer & Helbing 2011 PNAS; Jury Theorems (Stanford Encyclopedia of Philosophy); Epistemological Problems of Testimony (SEP); Wüthrich & Steele 2025 "The problem of dependency" (Synthese); "The Corroborative Rule" comparative/critical perspective (SAGE journals); Delphi method (Wikipedia); repliCATS structured expert elicitation (PMC); illusory-truth meta-analysis (Nature Communications).

Note: several PAN-corpus / MRPC / Turku Paraphrase Corpus citations in axis 3 came from a general dataset-landscape web search (not full-text verified against the primary papers) — treat those specific corpus names as **candidate leads to verify at experiment-design time**, not confirmed-in-hand citations. Total distinctly verified academic sources across axes 1-2: 20 (after removing duplicate landing pages).

---

**P_deflated:**
- Axis 1/2 claim (default non-independence detection is weak/absent in humans): raw confidence ~0.90 (well-replicated, multi-decade literature) → deflated for lit-scan-calibration discipline to **P=0.70**.
- Axis 3 claim (a fair, non-construction-determined real-document validation is tractable with existing public corpora): raw confidence ~0.65 (corpora exist but not yet hand-verified/downloaded for this exact use) → deflated and capped per novel-synthesis rule to **P=0.45**.

**Hard-fail thresholds are pre-registered above** — this note should not be re-read as "detector validated" until the cheap decisive test is actually run against a real assembled eval set.
