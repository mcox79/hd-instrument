# Research drill — brain-check on ingest-gate Wikidata-vandalism negative

Filed by: research (Sonnet). Trigger: mandatory brain-check + drill-negative-2x on the
brain-faithful 4-signal ingest-gate's real-data negative (Wikidata vandalism detection:
degree/frequency baseline AUROC 0.735 vs claim-plausibility signals 0.51-0.61).

## HEADLINE

**Task-mismatch confirmed, not a real bound — with one load-bearing caveat that sharpens
rather than rescues the claim.** Wikidata revert/vandalism labels are an EDITOR-BEHAVIOR
task; our gate's structural signals (surprise, schema-fit) target CLAIM VALIDITY, a
genuinely different construct with its own real, frequency-controlled benchmarks in the
literature (VitaminC, Symmetric-FEVER). But the brain-consistent story is narrower than
"structure beats frequency": human truth judgment is dominated by
familiarity/fluency for claims that have been *seen before* (illusory-truth effect,
robust even against contradicting knowledge — "knowledge neglect," Fazio et al. 2015),
and only diverges toward structural/schema-coherence signals for **novel claims**, where
repetition-frequency is structurally uninformative (frequency ≈ 0 for both true and false
novel claims — it cannot discriminate by construction). So the correct claim is not "our
gate should beat frequency in general" but "our gate's structural signals should
specifically beat a frequency baseline on the frequency-blind subset: novel, never-seen
claims." That is a narrower, more falsifiable, and more defensible target than the
original framing — and it has not yet been tested.

## Cheap decisive test

Use **VitaminC** (Schuster et al., NAACL 2021 — >400K claim/evidence pairs built from
Wikipedia revisions that flip exactly one fact, so true/false pairs share near-identical
entities and wording) or the **Symmetric-FEVER** debiased eval split (Schuster, Shah, Ram
& Barzilay, EMNLP/TACL 2019 — explicitly constructed so p(label | any n-gram) = 0.5,
neutering surface-frequency artifacts by design).

Procedure:
1. Split examples into FAMILIAR (all entities/relations already present in whatever
   knowledge base the gate has ingested) vs NOVEL (claim introduces at least one
   never-seen entity or entity-relation pairing).
2. On the FAMILIAR subset: expect frequency/recurrence baseline to win (replicates
   illusory-truth — this is the brain-consistent, non-failure case, not something to
   "fix").
3. On the NOVEL subset: run the gate's structural signals (surprise, schema-fit) against
   a frequency/degree baseline. This is the fair test — frequency is close to
   uninformative here by construction (both true and false novel claims are equally
   "never seen").

## Falsifiable predictions

**HARD-PASS:** On the novel-only subset, structural-signal AUROC exceeds frequency-
baseline AUROC by ≥0.05, AND frequency-baseline AUROC on that subset is itself ≤0.55-0.60
(confirming frequency really is near-blind there, i.e. the test is fair and not silently
leaking a frequency proxy). This would validate the frequency-blind-spot theory directly.

**HARD-FAIL:** Structural-signal AUROC ≤ frequency-baseline AUROC + 0.02 on the novel-only
subset, OR frequency-baseline AUROC on the novel-only subset is >0.65 (meaning some proxy
— entity-type frequency, relation frequency, degree of a *neighboring* entity — is
leaking through and the "novel" split isn't actually frequency-blind). Either outcome
would mean the vandalism-task result generalizes: frequency/degree dominates even in the
theoretically-favorable regime, and this is a genuine bound on the gate's real-world
value, not a task-mismatch artifact.

**MIDDLE-BAND:** Structural signal beats frequency on novel-only but by <0.05 — directionally
consistent but too weak to claim the frequency-blind-spot mechanism is doing real work;
treat as inconclusive, not a pass.

## Cross-thread synthesis

This is the same underlying pattern already logged 3x this program on other real-data
tests (chem QSAR nonadditivity, LLM-gen epistasis, Costanzo genetic-interaction fair-test
— all refuted/HARD-FAIL at bulk/population scale) and already diagnosed in
[[project_real_data_negatives_are_bulk_measurement_artifacts_curate_to_nearzero_singles_pockets_2026-07-15]]:
a real phenomenon can be present but diluted to invisibility at the wrong aggregation
scale / wrong reference class, and the fix is not "abandon the domain" but "curate to the
regime where the phenomenon is actually isolated from the confound." There: near-zero-
singles genetic pockets isolate epistasis from allele-frequency/bulk-averaging. Here:
novel-claim-only splits isolate claim-plausibility from editor-behavior/frequency
confounds. Also ties directly to the schema-conditioned-surprise finding from the
foundation-builder v1→v4 arc (session-state note, 07-16): the v4 decisive result was that
surprise detects whole-relation-PRESENCE, not within-schema semantic novelty — i.e. the
gate's surprise signal needs to be conditioned on the right reference class to mean
anything, which is structurally the same fix needed here (condition the test on
"novel-relative-to-what's-already-known," not "reverted-relative-to-editor-reputation").

This is Trigger-D-style rescue (dispatch into a DIFFERENT field than the one that closed):
psychology/cognitive-science literature on truth judgment, not the substrate-physics
field list tracked by `research_field_advisor.py` (which covers spin-glass/free-
probability/coding-theory and returned no directly relevant candidate for this drill —
correctly so, since this is a task-design question, not a substrate-math question).

## Substrate-product implications

Do NOT position the ingest-gate as a general-purpose "content quality / vandalism
filter" — a cheap frequency/reputation heuristic already wins that job outright (AUROC
0.735 vs 0.51-0.61), and there is no product differentiation in re-deriving that with
more expensive machinery. DO position it narrowly as a **novel-assertion triage** stage:
pre-screening brand-new facts / new entities / cold-start KB assertions for structural
plausibility BEFORE costly human or LLM-based review — precisely the regime where a
frequency-based filter is blind by construction (a genuinely new claim has no edit
history, no prior view count, no reputation signal to lean on). That is a real, narrower,
defensible niche, contingent on the cheap decisive test above actually passing.

## Answers to the four resolve questions

**1. Real bound vs task-mismatch:** Task-mismatch, with high confidence on the
categorical distinction (editor-behavior ≠ claim-validity) and medium confidence that the
gate would actually win the corrected test (untested). Concrete claim-validity, real,
frequency-controlled datasets exist and pre-date this program by years, built by
independent researchers for the general problem of debiasing fact-verification models
from surface/frequency artifacts:
- **VitaminC** (Schuster et al., NAACL 2021) — contrastive revision pairs, near-identical
  entities/wording between true/false, the most direct entity-frequency match available.
- **Symmetric-FEVER** (Schuster, Shah, Ram & Barzilay, EMNLP/TACL 2019) — explicit
  p(label|n-gram)=0.5 debiasing construction.
- **CoDEx hard negatives** (Safavi & Koutra, EMNLP 2020) — type-constrained, KGE-ranked
  plausible negatives (partial frequency control, not guaranteed).
- **Wikidata constraint-violation sets** (Ferranti et al. 2024, Semantic Web Journal;
  arXiv 2410.13707) — naturally-occurring type/range/disjointness violations, not
  vandalism-labeled.
- **Wikinegata** (Arnaout, Razniewski & Weikum, VLDB/WWW 2021) — peer-based negative
  mining, structurally frequency-comparable by construction (compares entities to
  same-type peers).

**2. Does the brain beat frequency — is frequency-dominance brain-consistent or a
failure?** Brain-consistent, not a failure, for FAMILIAR claims: the illusory-truth
effect is one of the most robust findings in judgment-and-decision-making (Hasher,
Goldstein & Toppino 1977 onward), and Fazio et al. (2015, JEP:General) show it survives
even when the perceiver's own stored knowledge contradicts the repeated claim
("knowledge neglect" — familiarity overrides known structural implausibility). Fazio,
Rand & Pennycook (2019) show repetition and plausibility act as independent, additive
contributions to perceived truth, not as fluency swamping structure — so structural
signals aren't erased, but they don't dominate either, once frequency is available.
The brain's advantage is confined to the regime frequency cannot reach: at the
zero-repetition (novel) baseline embedded in these same study designs, plausibility/
coherence with prior knowledge is the sole discriminator and does discriminate reliably
(concept/word-coherence plausibility-judgment literature; Johnson-Laird's mental-model
coherence account; schema-congruency effects on novel-scenario judgment). So: **frequency
winning at population/bulk scale on FAMILIAR-claim tasks (like Wikidata vandalism, which
is entirely a familiar-claim/familiar-editor regime) is brain-consistent, not a
failure of brain-faithfulness.** The gate's real theoretical edge is narrower and
specific to novel claims — matching the Director's sharpened frame exactly.

**3. Curated pocket — skeptical read:** Medium-low-to-medium probability this is genuine
signal rather than rescue-fishing. Arguments FOR genuine signal: VitaminC and
Symmetric-FEVER were built by independent NLP researchers years before this program
existed, for the general and well-recognized problem of "claim-only/surface-artifact
bias in fact verification" — this is not a pocket invented post-hoc to rescue a specific
result; it is an established task category with its own literature. That is a materially
different situation from "we redefined success until something worked." Arguments FOR
caution: this program has now hit real-data walls on 3 separate prior tests (chem QSAR,
LLM-gen epistasis, Costanzo fair-test) before this one, all following the same shape
(structural signal drowned by a bulk/frequency/degree confound) — a 4th "the real test is
actually X" reframe is exactly the pattern a motivated-reasoning process would produce
even when unwarranted, so the prior on "this particular reframe pays off" should sit
below its face-value plausibility. Net: ~0.35-0.40 that the gate's structural signals
demonstrably beat a frequency baseline on a genuinely frequency-matched novel-claim test,
before running it.

**4. Verdict:** **(a)** — real value contingent on testing against a claim-validity task,
not the editor-behavior task tested so far. Not **(b)** a hard bound, because the
frequency-blind-spot regime (novel claims) has not actually been tested and the human
literature suggests structure DOES carry information there. Not primarily **(c)**
implementation weakness — the signals (surprise, schema-fit) may well be measuring the
right thing; they were just evaluated against the wrong construct (editor reverts) at
the wrong reference class (familiar-claim regime where frequency legitimately wins).

## Deflated P

P(overall diagnosis correct: task-mismatch not bound, frequency-dominance on familiar
Wikidata task is brain-consistent) = **0.65** (well-grounded in a highly robust,
independently-replicated literature — illusory truth is one of the most reproduced
effects in the field; deflated from a higher raw confidence per lit-scan calibration
penalty for the un-run empirical test).

P(gate's structural signals actually beat a frequency-matched baseline on a real
novel-claim-only split, e.g. VitaminC novel subset) = **0.30** (capped below the
novel-synthesis 0.50 ceiling and further deflated given this program's 3-for-3 recent
real-data-wall track record on structurally analogous claims; this is the number that
should gate whether to spend a cell on it).

## Citations (verified count: 17, of which 15 directly confirmed via search/fetch, 2
medium-confidence / secondary reference only — degree-bias-in-KGC papers not fully
text-extractable)

Psychology / truth-judgment:
1. Hasher, Goldstein & Toppino (1977) — origin of illusory truth effect.
2. Fazio, Rand & Pennycook (2019), *Psychonomic Bulletin & Review* — repetition and
   plausibility act additively.
3. Fazio et al. (2015), *J. Exp. Psych: General*, PubMed 26301795 — "Knowledge does not
   protect against illusory truth."
4. Shechter & Klauer (2025), *Pers. Soc. Psychol. Bull.* — replication / boundary
   conditions.
5. Reber & Schwarz (1999) — perceptual fluency alone shifts truth ratings.
6. Unkelbach (2007) — fluency-attribution / discrepancy-reduction model of truth.
7. Hansen, Dechêne & Wänke (2008) — discrepant fluency.
8. "Modeling the link between plausibility and truth effect" (2025), *Psychon Bull Rev*.
9. Concept/word-coherence plausibility-judgment study (ResearchGate).
10. Johnson-Laird — mental-models coherence account (PNAS).
11. Schema-congruency and associative encoding (ScienceDirect).

Claim-validity / KG datasets:
12. VitaminC — Schuster et al., NAACL 2021 (GitHub TalSchuster/VitaminC; ACL Anthology
    2021.naacl-main.52).
13. Symmetric-FEVER — Schuster, Shah, Ram & Barzilay, EMNLP/TACL 2019, "Towards
    Debiasing Fact Verification Models."
14. CoDEx — Safavi & Koutra, EMNLP 2020.
15. Wikinegata — Arnaout, Razniewski & Weikum, VLDB 2021 / WWW 2021.
16. Wikidata constraint-violation / disjointness study — Ferranti et al. 2024, *Semantic
    Web Journal*; arXiv 2410.13707.
17. Degree-bias-in-KGC (arXiv 2302.05044; arXiv 2606.08921) — medium confidence, cited
    for context only, not load-bearing to the verdict.
