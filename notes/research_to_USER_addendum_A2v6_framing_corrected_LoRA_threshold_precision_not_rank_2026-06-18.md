# RESEARCH (Director) -> USER: brief addendum to the substantive update -- Skunkworks's A2 v6 verdict-VET LANDED with two refinements that correct my earlier framing. CERT 570->571 incoming (cert-grade ALREADY_SEPARATES). My earlier "LoRA Stage-2 has NO headroom" carried the cell's over-claim; Skunkworks's actual-not-bar (per-item inspection) refined it: LoRA has limited rank-headroom BUT possible threshold-precision headroom (boundary overlap). Plus a sharp misattribution catch: cell named WRONG gaps as precision-limit examples (Tarjan/Hopcroft are <0.70; real top-6 high-confidence gaps are different + unidentified). Plus Item 1 PART_OF SCHEMA-VET PASS (the ONE discriminating cert-experiment of the sprint -- now apply-GO). Substrate-discipline cuts both ways; I had under-applied it to my own USER note. Correcting.

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-18 ~19:35 PDT  **Re:** A2 v6 framing addendum + Item 1 PASS. ASCII; fname_v2.

## Bottom line

My earlier note had a too-strong reading of the A2 v6 verdict that Skunkworks's verdict-VET (actual-not-bar; read per-item confidences not just the AUROC headline) corrected. Three refinements:

1. **CERT 570 -> 571 incoming.** A2 v6 ALREADY_SEPARATES IS cert-grade-able (rank-separation is genuinely strong). Honest cert-additive growth.

2. **"LoRA NO headroom" was over-claim.** LoRA has LIMITED rank-headroom (0.965 already high) BUT POSSIBLE THRESHOLD-PRECISION headroom (boundary overlap). At a 0.70 threshold, ~6 false-positives + >=1 false-negative are irreducible -- a calibrated threshold gets close but not clean. The precision-limitation IS the LoRA headroom that "no headroom" dismissed.

3. **Misattribution catch (sharp).** The A2 v6 cell named Tarjan-SCC + Hopcroft-Karp as the precision-limit examples. BUT those gaps (A2-GAP-000 = 0.5691, A2-GAP-002 = 0.6858) are BELOW 0.70. The ACTUAL >0.70 high-confidence gaps are A2-GAP-009/015/013/012/014/020 -- DIFFERENT gaps with UNIDENTIFIED topics. The cell's caveat is mis-attributed; the real precision-limit is on different gaps + a topic-inspection is the recommended tightening.

## The corrected B-beta gate framing

Earlier framing: "LoRA Stage-2 has NO headroom; calibrated threshold suffices."

Corrected framing: "The untuned substrate RANKS in-cov above gaps at AUROC 0.965 -- a strong positive (don't under-sell). BUT the confidence-OVERLAP zone (top 6 gaps >0.70 exceed bottom 15 in-cov) means no clean threshold-separation; a calibrated threshold gets close (~6 FP at 0.70) but not clean. LoRA's possible headroom is in the THRESHOLD-PRECISION boundary, not the rank. Don't conclude 'LoRA unnecessary' from the rank-AUROC alone. Confirm on grown 43,892 post-push-fix (the C-deferred path)."

This is honest-positive: the substrate is good (strong rank); LoRA isn't necessarily worthless (might sharpen the boundary); the test should run on the grown corpus to be definitive.

## Substrate-discipline cuts both ways (NEGATIVITY-BIAS-symmetric)

I caught my own over-claim through Skunkworks's verdict-VET. The substrate-discipline pattern (cert-discipline catches its own custodians) extended to my USER-facing communication:
- Cell over-claimed -> Skunkworks verdict-VET caught it -> Director note carried the over-claim -> Director addendum corrects it

This is the SAME multi-layer pattern as the cert-discipline-in-substrate-mutation work. The discipline applies to ALL framing -- including my interpretations carried to you. NEGATIVITY-BIAS-symmetric is the rule that catches it (the substrate is "more capable than first-pass implies" cuts in BOTH directions: don't oversell + don't undersell).

## Plus: Item 1 PART_OF SCHEMA-VET PASS (the discriminating cert-experiment of the sprint)

Skunkworks SCHEMA-VET-PASS landed on the PART_OF 2-level confirmation cell. The dry-run shows the PART_OF subgraph had a 29% holonym-incompleteness (the meronym-ingest missed the holonym direction). This makes the test DEFINITIVE not trivial: the +125 completion edges have REAL discriminating power on the 2-hop gold.

Verdict tier-by-outcome:
- **Barely-moves**: the +125 didn't matter for the 2-hop gold -> PART_OF was complete-FOR-THE-GOLD -> depth-robustness IS a completeness artifact -> coverage story explains BOTH HYPERNYM cliff AND PART_OF non-cliff. Cert-grade discriminating null (Phase A FLAT pattern).
- **Jumps**: the +125 mattered -> PART_OF was coverage-limited too -> MEASURED_MECHANISM ATTRIBUTION + new-cause-to-investigate (Phase A2 pattern).

Either way the depth-cliff coverage-story gets a second relation-type data-point. This is the ONE discriminating cert-experiment of the 20h sprint -- the sprint's cert-growth ceiling.

Exp-Dev applies next (laptop-CPU; UN-gated by push-down); should land within the next short cycle.

## 6th-layer verify-the-referent extension (cumulative discipline)

The 5-layer verify-the-referent chain Skunkworks atomized earlier just got a 6th layer naturally:

1. field-EXISTS / 2. field-LOCATION / 3. value-RESOLVES / 4. id-FORM / 5. disagreement-as-information
6. **verify-on-actual-top-items-not-pre-named-examples** (the cell named the wrong gaps; the per-item sort finds the real ones)

The cell's deterministic harness verified what the cell DESCRIBED; the per-item sort surfaced what the cell DIDN'T KNOW about. Skunkworks's actual-not-bar discipline applied to a deeper layer. Likely to be atomized as the next AUDIT_LESSON extension.

## Substrate state right now

- LOCAL atoms 43,896 (no atomize this cycle yet; CERT 570 + 571 incoming with A2 v6 atomize)
- REMOTE atoms 41,330 (push-pipeline-DOWN persists; 17+ commits unpushed)
- Item 1 (PART_OF) apply imminent; Item 4 (ConceptNet) cell build continues
- Skunkworks reactive queue: A2 v6 atomize landed-verify + PART_OF tier-call + topic-inspection result + 3 phantom landed-verifies + ConceptNet SCHEMA-VET

## What I'm waiting on / who's blocking

- **Skunkworks**: A2 v6 atomize landed-verify (CERT 570->571 + corrected caveats) + PART_OF tier-call + topic-inspection result + GPU-routing cert-architecture call (the new note covering the USER catch on PROT-020 + import-torch + 0% GPU util)
- **Exp-Dev**: A2 v6 atomize + topic-inspection + PART_OF apply + BROAD --full re-run + atomize + ConceptNet cell continues + 3 phantom investigations
- **Orchestrator REPLACEMENT**: A2 v6 chain complete; reactive on push-fix + GPU-routing implementation per Skunkworks's cert-architecture call
- **USER (you)**: push-fix bandwidth (priority-0; gates C-grown-corpus + HYP-5 + ConceptNet apply + cert-durability)

The discipline-machine continues self-correcting in real-time. Sprint executing well.

-- Research (Director)
