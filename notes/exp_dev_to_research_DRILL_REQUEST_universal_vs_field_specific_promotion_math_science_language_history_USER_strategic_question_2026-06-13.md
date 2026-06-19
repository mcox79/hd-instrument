# exp_dev -> research: DRILL REQUEST (USER strategic question) -- is knowledge promotion/interaction UNIVERSAL across fields, or must math / science / language / history be handled separately?

**Filed-by:** exp_dev (Opus) 2026-06-13, relaying a USER strategic directive verbatim + the empirical evidence I have in hand. Routing to Research per "get direction from research where needed" (NOT an AskUserQuestion).

## USER question (verbatim)

> "we need a way to organize and handle different fields - math, science, language, history blah blah - there needs to be a clear way we handle everything. It might be that we DON'T need to separate them and however we promote things to atoms is consistent, but I'm not certain. We may find that there is more or less a universal way to promote and interact with everything - I just don't know but it will be very interesting to find out."

So: **is there a UNIVERSAL promotion + interaction operator for all knowledge, or do fields need separate handling?** This is foundational for the substrate-on-all-knowledge vision (it decides whether ingest is one uniform lane or N per-field lanes).

## Empirical evidence I already have (it bears DIRECTLY on this -- the tension showed up in today's cells)

The current data points toward a **specific, testable hypothesis: UNIVERSAL OPERATORS + FIELD-SPECIFIC SIGNAL EXTRACTION.** Evidence:

1. **Promotion OPERATORS appear field-agnostic.** The KP operator's paths run over (atoms, relations, vectors) with NO field-specific code and HARD-PASS uniformly:
   - P1 frequency-promotion (in-degree across corpora) -- HARD-PASS, corpus-blind.
   - P4 sleep-replay (codebook-geometry clustering) -- HARD-PASS, ran over all T3 regardless of field.
   - P3 bisimulation, P5 Curry-Howard -- same graph machinery for any field.
   This suggests one promotion ladder (T3->T2->T1->T0) and one set of operators may suffice.

2. **But the SIGNALS feeding those operators behave DIFFERENTLY by field** -- I hit this concretely:
   - **SHARES_MATH auto-discovery (today):** I had to EXCLUDE *_history corpora. History-narrative atoms share DEPENDS_ON references through note cross-citations -> a 136-atom NOISE blob that is NOT shared mathematics. The SAME structural signal ("shared prerequisites") means "shared math" for math atoms but "co-mentioned in a report" for history atoms. After excluding history, math-fraction went to 1.0 and 9 genuine math-equivalence groups emerged.
   - **Retrieval (memory two-population finding):** the substrate ALREADY routes by field implicitly -- ~1245 history atoms are bge/TEXT-served by design; structured math atoms are algebra-HRR/STRUCTURE-served. The Stratified-Hybrid retrieval is, in effect, already a field-aware router.
   - **Proof depth (P5 Curry-Howard):** "a proof" (derivation chain to an axiom) is meaningful for math/science; what is the analogue for language (usage/distribution?) or history (source provenance / chronology / causation?)? The promotion CRITERION may be field-specific even if the OPERATOR is shared.

3. **The tier ladder (T0-T3) is nominally universal but its SEMANTICS may differ per field.** T1 "axiom" = mathematical axiom for math; for language maybe a phoneme/morpheme/closed-class function word; for history maybe a primary source or an uncontested fact. Is the ladder one universal scale, or one-ladder-per-field with a shared shape?

## Concrete sub-questions for the drill

1. **Universal-operator hypothesis:** can ONE promotion operator + ONE tier ladder serve all fields, with field-specificity confined to the SIGNAL-EXTRACTION layer (how you compute "foundational" / "shares-structure" / "axiom" per field)? My evidence leans YES. Falsifier: a field whose promotion needs a fundamentally different operator (not just a different signal).
2. **Field representation:** should "field/domain" be a FIRST-CLASS partition (like L1 categorical routing -- which SC just validated survives to 10M), an atom attribute, or an emergent cluster? (SC HARD-PASS means partition-per-field is architecturally cheap at scale.)
3. **Interaction (not just promotion):** cross-field links are where the value is (today's auto-discovery found CROSSDISC atoms: ising_model<->modern_hopfield, percolation<->capability_path -- physics math reused for cognition). Does a universal representation make cross-field analogy a FIRST-CLASS operation (SHARES_MATH spanning fields), or do field silos block it? The cross-disc SHARES_MATH groups suggest universality ENABLES the most valuable interactions.
4. **History/language as the stress tests:** math/science are structural (where the substrate is strongest). Language (distributional/usage) and history (narrative/chronological/causal) are the hardest cases for a "universal" claim. A drill should target THOSE explicitly -- e.g. what is "promotion" for a language atom (morpheme->word->construction->grammar rule?) and a history atom (event->pattern->periodization->causal law?).

## Why this is high-value now

- It's the organizing principle for the entire ingest roadmap (one lane vs N lanes) -- decides architecture before the 4.37M-fact pour.
- If UNIVERSAL holds, it's a top-tier substrate-product positioning artifact: "one architecture promotes and relates ALL knowledge; LLMs have no explicit promotion/tier structure in any field."
- I can run cheap EMPIRICAL probes to test it (e.g. run P1/P4/P3 per-field and compare whether the same operators fire sensibly in language/history corpora vs math) -- happy to build whatever decisive cells the drill specifies. The signal-vs-operator split is already measurable on the current corpus.

**Request:** a research drill on universal-vs-field-specific promotion/interaction, returning (a) the hypothesis space, (b) falsifiable predictions, (c) cheap decisive cells for me to run per field. I'll execute the cells. Routing now; continuing on other ungated work meanwhile.

---

## ADDENDUM (same day): I ran the first decisive probe -- here is DATA for the drill

Cell `exp_substrate_cross_field_promotion_universality_probe_cpu_v1.py` (HEAD 77828b22). Per-field corroboration of the structural promotion
signal (fraction of "shares structure" pairs ALSO sharing an independent semantic property) + structural-metadata coverage:

| Field | atoms | pct_domain | pct_capability | signal corroboration | in-degree hubs |
|---|---|---|---|---|---|
| math | 239 | 0.80 | 0.24 | **0.953** | 47 (max 322) |
| science | 147 | 0.00 | 0.41 | **1.000** | 0 |
| language | 42 | 0.33 | 0.26 | **0.934** | 0 |
| cognition | 51 | 0.29 | 0.00 | 0.021 | 0 |
| history | 1245 | 0.00 | 0.00 | **0.000** | 0 |
| meta | 18 | 0.06 | 0.06 | n/a (0 pairs) | -- |

Verdict: **FIELD-SPECIFIC-LEANING at the current corpus**, spread=1.0. KEY REFINEMENTS for the drill:
1. **The divide is INSTRUMENTATION, not field-essence.** LANGUAGE corroborates at 0.934 -- it patterns WITH math/science, NOT with history. So it is NOT "formal/structural fields vs informal" -- it is "fields that carry structural metadata (domain/capability) vs those that don't." Where the metadata exists, the SAME universal operator works (0.93-1.0). This supports the UNIVERSAL-OPERATOR hypothesis with a per-field SIGNAL-INSTRUMENTATION layer.
2. **History is the lone un-instrumented mass.** 1245 atoms, 0% domain, 0% capability, 0 in-degree hubs; its raw structural signal (1021 shared-prereq pairs) is pure note-co-reference NOISE (corroboration 0.0). Either history is intrinsically non-structural OR (more likely) we simply have not authored its structural metadata. **This is the central drill question: FUNDAMENTAL vs UNBUILT.**
3. **Cross-field links are real and valuable.** 55 cross-field structural pairs at 0.69 corroboration -- the cross-disciplinary connections (physics-math reused in cognition) a universal representation enables.

Suggested drill focus: (a) author a SMALL structural-metadata pilot for history/language atoms (e.g. event->date/actor/causal-link for history; morpheme/POS/construction for language) and re-run this probe -- if corroboration jumps, the gap was UNBUILT (universal wins). (b) Define what "domain/capability/axiom" MEAN per field. I can run the re-probe cheaply on any pilot metadata you author.
