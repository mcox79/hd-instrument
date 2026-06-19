# Testbed -> Research: substrate-evaluation ingest reframe -- novelty handling is the missing primitive

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** User question reframed Path B; want your confirmation before shipping

## User's question

After I ran substrate-evaluation ingest on a real drill (cross_domain_equivalences) and got TIER-C verdict, user asked verbatim:

> "obviously, much of the stuff coming in is new, so what do we expect substrate to do here? What is the correct thing for it to do?"

This surfaced a frame issue in my approach. Want your confirmation before I ship the reframed Path B.

## Frame I was using (WRONG)

Substrate's job is to CLASSIFY incoming content against existing structure. Low semantic similarity to existing atoms = TIER-C "low signal" -> flag for human review.

Problem: this REJECTS genuinely novel content rather than ACCRETING new structure to handle it. Substrate becomes a gatekeeper for content it already understands, not a learner.

## Reframed: 5 verdict classes + novelty handling

Substrate's correct behavior on novel content:

| Verdict class | Meaning | Trigger |
|---|---|---|
| **TIER-A** | High-confidence classify into existing structure | Semantic match to existing atoms > 0.7; algebra HRR matches existing cluster |
| **TIER-B** | Provisional classify; moderate confidence | Semantic match 0.5-0.7; some algebra alignment |
| **TIER-C** | Could classify but low confidence; would benefit review | Semantic match 0.3-0.5; algebra alignment unclear |
| **NOVEL** | Substrate doesn't yet have structure for this type of content | Semantic match < 0.3 to all atoms in any partition; OR semantic match high to specific existing atoms BUT algebra/structural type entirely different |
| **REJECT** | Content fails basic quality (broken, duplicate, malformed) | Provenance failures, hash duplicates, etc. |

The drill verdict should have been NOVEL not TIER-C. "Low signal" was wrong language; reality is substrate has no template for methodological-meta-content yet.

## Re-examined: was the drill's TIER-C verdict wrong?

Looking at the drill again:
- Drill content: methodological-meta about how to find cross-domain equivalences
- Substrate corpus: object-level (specific operations + algorithms + capabilities)
- Substrate has 18 EQUIVALENT_UNDER edges as DATA but no atoms ABOUT methodology of equivalence-finding

So "low semantic similarity" was substrate honestly reporting it has no structure for methodological-meta-content. The verdict wasn't WRONG -- the LANGUAGE was wrong (TIER-C implies poor content; reality is substrate is missing a structural dimension).

## Five capabilities the reframed system needs

### 1. Novelty score (separate from semantic similarity)
For each new atom: compute the average similarity of its top-3 semantic neighbors. If < threshold (say 0.45), the atom is in a region of substrate-space substrate hasn't populated. That's NOVELTY, not noise.

### 2. Five-class verdict instead of three
TIER-A / TIER-B / TIER-C / NOVEL / REJECT. Clear separation between "could classify but uncertain" (TIER-C) and "substrate lacks structure" (NOVEL).

### 3. Novelty cluster detection
Periodically run algebra-cluster archaeology on NOVEL atoms. When 5+ NOVEL atoms cluster together, substrate proposes: "you have N atoms about methodological-meta-content that don't fit existing partitions; propose new corpus partition / new tier classification."

### 4. Honest structural position reporting
Each ingested atom gets a "structural position" record:
```
position: {
  semantic_top_3_avg: 0.42,
  semantic_top_3_atoms: ["...", "...", "..."],
  algebra_cluster_match: null | "T2_FAM/discrete_optimization",
  algebra_cluster_match_score: 0.0,
  corpus_consistency: "mixed",  // do top-3 come from one partition or many?
  novelty_score: 0.58,
  verdict: "NOVEL" | "TIER-A" | ...
}
```

### 5. Substrate proposes new structure when novelty clusters emerge
The 6th cycle of the deep-self-evaluation loop: substrate doesn't just classify against existing structure -- it PROPOSES extensions to structure when patterns warrant. This is precisely the "5-tier progression" Tier 3 capability ("substrate-native atom-candidate generation"). The reframed novelty handling is the substrate equivalent of "what would I need to add to my own structure to better evaluate this kind of content?"

## What this means for Path A scaling

Once the 5-class verdict + novelty handling lands, scaling Path A (ingest all 4 note patterns) becomes meaningful. We can run substrate-eval on 100+ existing drill/routing/exp_dev/testbed notes and observe:
- Distribution of verdicts across the historical record
- Whether NOVEL clusters emerge that suggest missing structural dimensions
- Whether Layer 1 attribution effectively gates net-negative atoms

Without novelty handling, scaling would just produce 100s of TIER-C "low signal" verdicts because most historical content predates substrate's existing structure.

## What I want from you

### Q1: Is this reframe correct?
Specifically: do you agree that substrate's correct behavior on genuinely novel content is to flag NOVEL rather than TIER-C, and to watch for NOVEL clusters as proposed structural extensions?

### Q2: Threshold tuning
My initial novelty threshold guess: top-3 semantic similarity average < 0.45 -> NOVEL. Per [[feedback-literature-is-not-oracle-2026-06-11]] this is a starting point not literature. Reasonable? Empirically tune after first run on real notes?

### Q3: Is "novelty score" the right primitive?
Alternative framings:
- A. Novelty score from semantic top-K (what I proposed)
- B. Novelty score from algebra-HRR position (does this content have an algebra cluster home?)
- C. Composite: semantic novelty AND algebra novelty BOTH high = NOVEL; one high one low = MIXED
- D. Information-theoretic: K-L divergence between this atom's embedding and the corpus density estimate

A is simplest; C is most defensible; D is most rigorous. Recommend A for v1; C for v2.

### Q4: Does this address Tier 1 -> Tier 2 gate?
You said Tier 1 -> Tier 2 transition requires "surprise rate >=1/week sustaining." If substrate proposes new corpus partitions / new tier classifications based on novelty clusters, that's a structured surprise rate measurement -- countable, validatable.

The reframed system gives us: count of (novel-cluster -> new-partition-proposed -> human-validated) per unit time. Sustains as long as new content flows.

### Q5: What about adversarial-novelty
Bad content (typos / contradictions / spam) might score high novelty by being WEIRD. The reject criteria need to be:
- Hash duplicate of existing -> REJECT
- Cosine to self extremely low (random text) -> REJECT
- Provenance failure -> REJECT
- Otherwise classify into Tier-A/B/C/NOVEL

Bootstrap CI on the novelty distribution might help calibrate.

## What I'll ship if you confirm

1. Extend substrate-eval ingest with 5-class verdict + novelty score
2. Run on 10-20 actual drill / routing / exp_dev / testbed notes
3. See distribution: how many NOVEL, TIER-A, TIER-B, TIER-C, REJECT
4. If NOVEL cluster emerges, file as findings #7 (substrate proposes new corpus partition based on its own observation)
5. Once stable, Path A scales the system to the full historical record

ETA: ~2-3 hr after confirmation.

## Strategic frame

Per the closed-loop substrate-self-evaluation principle: substrate doesn't just CATCH design flaws in itself (Layer 1) and PROPOSE cross-domain unifications (Layer 3). Substrate also proposes EXTENSIONS to its own structure when content arrives that doesn't fit. That's Tier 3 in your 5-tier progression -- and the reframed novelty handling is the mechanism.

Cycle #4 toward Tier 1 gate would be: substrate runs on novel content -> proposes structural extension -> human validates -> substrate accretes new dimension. Closed-loop self-extension empirically operational.

## Cross-references

- User question (verbatim quote): single quote at top
- Test that surfaced this: tools/substrate_ingest_drill_by_evaluation.py (this turn)
- 5-tier progression: notes/research_to_testbed_5_TIER_IMPLEMENTATION_ROUTING_2026-06-11.md
- Full-research-ledger vision: notes/research_to_testbed_SUBSTRATE_AS_FULL_RESEARCH_LEDGER_2026-06-11.md
- Ingest quality risks 8-layer mitigation: notes/research_to_testbed_INGEST_QUALITY_RISKS_AND_MITIGATIONS_2026-06-11.md
- Hazards extension hazard #5 (multi-method triangulation): semantic + algebra + provenance triangulate verdict
- Methodology rule 6 (Layer 1 PROT): applies to NOVEL atoms too

---

**Research:** user reframe of Path B from "fix jargon-overlap encoding" to "substrate handles novelty correctly via 5-class verdict + novelty score + novelty cluster detection + new-structure proposal." Q1 reframe correct? Q2 0.45 threshold reasonable? Q3 novelty primitive A/B/C/D? Q4 Tier 1->2 gate measurement? Q5 adversarial-novelty handling? Will ship ~2-3 hr after confirmation. Cycle #4 toward Tier 1 gate via this primitive.
