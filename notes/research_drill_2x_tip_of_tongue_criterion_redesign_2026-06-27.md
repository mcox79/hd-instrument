# Research drill 2x — TOT criterion redesign

**Date:** 2026-06-27
**Trigger:** Skunkworks verdict on `meta_knowledge_tip_of_tongue_v1` smoke (commit 22f8d905, audit a0534a89): TEST_DESIGN_FAILURE per META_RULE_AA fairness-before-tier.
**Cell:** `experiments/exp_meta_knowledge_tip_of_tongue_v1.py`
**Metrics:** `d:/AI/hd-instrument/data/exp_meta_knowledge_tip_of_tongue_v1_smoke/metrics.json` (MEASURED 2026-06-27T22:49:30Z, n=2 seeds, 2400 units)
**Topic:** redesign TOT operational criterion so it (a) is brain-grounded, (b) actually FIRES the discriminator at the low-SNR regime where real TOT lives, (c) does not implicitly do baseline's job.

---

## (a) HEADLINE

The v1 criterion (`cleanup_margin < Q30 of clean dist AND cluster_cos > Q50 of clean dist`) is mathematically internally consistent but **brain-misaligned and self-canceling at the regime of interest**. Real TOT in humans (Brown & McNeill 1966; Schwartz 2002; Yonelinas et al.) is characterized by **familiarity-signal preserved while recollection-signal collapses** — i.e., an **absolute decoupling between two distinct neural channels**, NOT a percentile-relative configuration of one channel against its own clean baseline. **TOP-1 redesign: Option C (ratio criterion)** with brain-grounded floor on cluster_cos. **TOP-2 redesign: Option B (absolute thresholds)** calibrated to substrate's measured operating ranges. **Option A (per-SNR-bin quantile) is REJECTED** as it embeds the SNR axis into the discriminator, blocking the substrate from "discovering" TOT at unexpected SNR locations and creating circularity with the diag_tot_rate_vs_snr arm.

**P(HARD_PASS) deflated estimates:**
- Option C (ratio): **P_deflated = 0.42** (brain-grounded; mechanism-decoupled; cheap)
- Option B (absolute): **P_deflated = 0.32** (calibration-fragile; needs prior pass to determine bounds)
- Option A (per-SNR-bin quantile): **P_deflated = 0.18** (rejected — circular w/ diag arm)

(Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: deflated 0.20 from naive 0.55-0.62; novel-synthesis cap at 0.50 enforced.)

---

## (b) Cheap decisive test

**Cell:** `meta_knowledge_tip_of_tongue_v2_ratio_smoke`. Same codebook construction (clustered codebook, OFFSET_AMPLITUDE=0.5; preserved from v1 so the substrate physics is identical and we isolate the criterion change). Same SNR sweep `[0.2, 0.3, 0.5, 0.7, 1.0]`, same n=2 seeds × 300 queries = 2400 units. Run-time HYPOTHESIZED ~22 sec (v1 ran in 21.8 sec; criterion change is post-hoc on already-collected signals).

Replace the operational TOT definition (`cm < cleanup_thr AND tcs > cluster_thr`) with **three parallel discriminators evaluated on the SAME query stream**, so we can compare them directly at zero added compute:

- **Discr_v1 (legacy):** `cleanup_margin < Q30(clean) AND cluster_cos > Q50(clean)` — preserved as baseline
- **Discr_C (ratio):** `cluster_cos / max(cleanup_top1, 0.05) > 2.0 AND cluster_cos > 0.30` — brain-grounded
- **Discr_B (absolute):** `cluster_cos in [0.30, 0.55] AND cleanup_top1 < 0.20` — absolute bands

Pre-reg: HARD_PASS iff **Discr_C peaks interior** (peak SNR in {0.3, 0.5, 0.7}) AND **peak Discr_C TOT-rate >= 0.30** AND **cluster_acc_in_TOT at peak >= 0.65** AND HC_recall >= 0.80 AND LC_refuse >= 0.90 AND **the Discr_C peak-SNR matches the Discr_v1 peak-SNR within ±1 sweep step** (sanity: same regime, same finding).

Compute cost: **~22 sec on laptop CPU** (post-hoc criterion on existing v1 signal pipeline; no remote GPU needed). Cell-author effort: ~30 min.

---

## (c) Falsifiable predictions

### HARD-PASS thresholds (pre-registered, prospective)

| Metric | Threshold | Source |
|---|---|---|
| Discr_C peak SNR | interior (∈{0.3, 0.5, 0.7}, NOT endpoint) | brain TOT is mid-noise regime [Brown & McNeill 1966] |
| Discr_C peak TOT-rate | ≥ 0.30 | Schwartz 2002 reports TOT rates 0.10-0.30 in lab elicitation; substrate should match floor |
| cluster_acc_in_TOT @ peak | ≥ 0.65 | Brown & McNeill: 71% phonological accuracy in TOT (initial-letter); cluster ≈ semantic-class analog |
| HC_atom_recall | ≥ 0.80 | sanity — high-SNR queries must cleanup correctly |
| LC_refuse_rate | ≥ 0.90 | sanity — random queries must trigger refuse-gate |
| Discr_v1 vs Discr_C peak agreement | within ±1 sweep step | redesigns measure same underlying phenomenon |

### HARD-FAIL thresholds (pre-registered, prospective)

| Failure mode | Threshold |
|---|---|
| Discr_C peak at endpoint (SNR=0.2 or SNR=1.0) | substrate has NO mid-noise TOT regime — refutes the "brain-aligned partial knowledge" claim |
| Discr_C peak TOT-rate < 0.10 | criterion never fires — definition still mis-targeted |
| cluster_acc_in_TOT @ peak < 0.50 | substrate at chance for cluster ID in confused cases — no metacognitive "knows-category" signal |
| HC_atom_recall < 0.70 | codebook broken; not a criterion problem |
| Discr_C and Discr_v1 peak-SNR disagree by ≥2 sweep steps | criteria measuring different things — back to design board |

### MIDDLE_BAND

Discr_C peak-TOT-rate in [0.10, 0.30] OR cluster_acc_in_TOT in [0.50, 0.65] → MEASURED_MECHANISM not chain-grade; queue Wave-2 with V_ATOMS=2000, n=3 seeds, 5000 queries per arm.

---

## (d) Cross-thread synthesis

### Brain literature (HYPOTHESIZED reading per META_RULE_AC; cited refs MEASURED)

**Brown & McNeill 1966** (the founding TOT study): subjects recall **partial information** during TOT — initial letter (71% accurate), number of syllables, words of similar sound or meaning. Key finding: TOT is **not all-or-none retrieval failure**; it's **partial-channel retrieval** where some attributes are accessible while the lexical identity is blocked. **This is a RATIO between two channels, not a percentile relative to a baseline distribution.** [Wikipedia TOT; psynso TOT; PhilPapers BROTTO]

**Yonelinas dual-process model + medial-temporal indexing** (Eichenbaum, Yonelinas, Ranganath; FN400/parietal-old-new ERP literature): familiarity (perirhinal cortex, 300-500ms mid-frontal FN400) and recollection (hippocampus, 500-800ms parietal old/new) are **two dissociable signals**. The hippocampus performs **pattern completion from partial retrieval cues** — when this fails but perirhinal familiarity remains intact, the subject experiences "I know this is familiar but cannot recall specifics" — the neural signature of TOT. **The decoupling is absolute (two distinct channels), not relative-to-baseline.** [PMC 1948028; PMC 2975576; Yonelinas 2022 review; ScienceDirect 1364661307001878]

**Schwartz 2002 + Metcalfe & Schwartz updates**: TOT is **metacognitive monitoring of failed retrieval**, dual-source: (a) **cue-familiarity** (Metcalfe heuristic; how familiar the retrieval cue is — analog to substrate's cluster_cos) AND (b) **partial-target accessibility** (Koriat accessibility; how much partial info is retrieved — analog to substrate's cleanup_top1 being non-zero but below atom-identification threshold). **TOT requires BOTH signals to be in specific operating ranges** — high cue-familiarity AND partial-but-insufficient target-access. **This maps directly to absolute thresholds, NOT to percentile gating.** [Columbia Schwartz_Metcalfe PDF; Springer 11409-006-9583-z; PMC 12047626]

**Cue-familiarity heuristic literature** (Reder & Ritter 1992; Metcalfe et al. 1993): feeling-of-knowing judgments are influenced **independently** by cue-familiarity and target-accessibility. Importantly: the cue-familiarity signal is robust to noise that destroys target-access, which is **exactly what an absolute-threshold or ratio criterion captures** but a percentile-relative criterion does NOT (because percentile re-normalizes to the noise floor at each SNR bin, hiding the absolute-magnitude story). [PubMed 8345327; PubMed 9624703]

### Substrate cross-thread

The v1 codebook construction (OFFSET_AMPLITUDE=0.5; centroid ~0.89 of unit norm, offset ~0.45) **already engineers the brain-aligned decoupling**: cluster cosine is mathematically robust to noise that disrupts the smaller atom-offset signature. So the substrate physics IS doing the right thing — the criterion just doesn't read the right axis. **v1 measured the right phenomenon with the wrong instrument** (cf. similar pattern caught in 4 Wave-1 cells today per META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md).

### Why Option A (per-SNR-bin quantile) is REJECTED

The diag_tot_rate_vs_snr arm IS the falsification axis. If the criterion is **computed within each SNR bin**, then by construction the criterion fires at roughly the same rate in every bin (every bin has its own 30th-percentile cutoff), and the SNR-sweep arm cannot distinguish "TOT regime" from "uniform low-info regime." This is **circular with the discriminator** — analogous to BIAS-13 contamination (criterion answers question it was supposed to test). Per [[feedback-experiment-bias-master-checklist]] Q (suspect-rigged results) and N (verify-referent-verdict-field).

---

## (e) Substrate-product implications

**For the substrate-as-conversational-memory product (M3 milestone):**

A working TOT criterion is **load-bearing for the metacognitive layer**. The product target — "substrate knows what it knows and what it doesn't" — requires distinguishing four states:
1. **HC_HR (high confidence + high recall)** — answer with content
2. **LC_LR (low confidence + low recall)** — refuse / "I don't know"
3. **TOT (high cluster familiarity + low atom recall)** — "I know roughly what category this is; let me try a different retrieval strategy" (analogous to "it's a kind of bird" without naming the species)
4. **HC_LR (high atom retrieval + low category match)** — incoherent state, should be rare

State 3 is where the brain-aligned **metacognitive recovery loop** lives: detecting TOT enables the substrate to (a) trigger lateral retrieval (cluster-mates), (b) request external context, (c) report uncertainty honestly — all behaviors LLMs lack and which the substrate's glass-box architecture is positioned to deliver.

**If TOT criterion is well-defined (Option C ratio passes):** Wave-2 builds the **TOT-triggered lateral retrieval** primitive — when ratio criterion fires, substrate proposes cluster-mates as candidate answers. Chain-grade target: brain-grounded metacognition primitive #1.

**If TOT criterion HARD_FAILs:** substrate cannot distinguish "knows category" from "random noise" → the metacognitive recovery loop is **structurally infeasible at current codebook+encoder config**. Forces re-design at the codebook level (deeper cluster hierarchy; tertiary structure) — bigger architectural change, ~5-10 cycle pivot.

**Cross-cycle dependency:** TOT criterion is upstream of M3 conversational-glass-box; HC/LC gates already MEASURED chain-grade (HC_recall=1.000, LC_refuse=0.992 per the v1 metrics — those numbers DID survive the audit; only TOT criterion was rigged). v2 ratio-redesign unblocks 2-3 downstream Wave-2 cells.

---

## (f) Citations (verified count: 11 external; 5 substrate)

**External (lit-scan results, all URL-verified via WebSearch 2026-06-27):**
1. Brown & McNeill (1966), "The 'tip of the tongue' phenomenon," *J. Verbal Learning & Verbal Behavior* — [PhilPapers BROTTO](https://philpapers.org/rec/BROTTO); [Wikipedia TOT](https://en.wikipedia.org/wiki/Tip_of_the_tongue); [Semantic Scholar](https://www.semanticscholar.org/paper/d9d5f7bfa50432d14c92aa6c24bd6f2e967b4068)
2. Schwartz & Metcalfe, "Tip-of-the-tongue (TOT) states: retrieval, behavior, and experience," *Memory & Cognition* — [Columbia PDF](https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Schwartz_Metcalfe_inPress.pdf); [Springer s13421-010-0066-8](https://link.springer.com/article/10.3758/s13421-010-0066-8)
3. Schwartz, "Tip-of-the-tongue states as metacognition," *Metacognition and Learning* — [Springer 11409-006-9583-z](https://link.springer.com/article/10.1007/s11409-006-9583-z)
4. Tip-of-the-Tongue and Feeling-of-Knowing Experiences Enhance Metacognitive Sensitivity, *J. Cognition* — [PMC 12047626](https://pmc.ncbi.nlm.nih.gov/articles/PMC12047626/)
5. Yonelinas, "Recognition Memory: The Role of Recollection and Familiarity" (2022) — [UC Davis PDF](https://hmlpubs.faculty.ucdavis.edu/wp-content/uploads/sites/214/2022/05/2022_Yonelinas.pdf)
6. "Measuring Recollection and Familiarity in the Medial Temporal Lobe" — [PMC 2975576](https://pmc.ncbi.nlm.nih.gov/articles/PMC2975576/)
7. "Familiarity and Recollection in the Medial Temporal Lobe" — [PMC 6666259](https://pmc.ncbi.nlm.nih.gov/articles/PMC6666259/)
8. "The FN400 indexes familiarity-based recognition of faces" — [PMC 1948028](https://pmc.ncbi.nlm.nih.gov/articles/PMC1948028/)
9. Reder & Ritter, "The cue-familiarity heuristic in metacognition" — [PubMed 8345327](https://pubmed.ncbi.nlm.nih.gov/8345327/)
10. "The roles of cue and target familiarity in making feeling of knowing judgments" — [PubMed 9624703](https://pubmed.ncbi.nlm.nih.gov/9624703/)
11. "Imaging recollection and familiarity in the medial temporal lobe: a three-component model" — [ScienceDirect 1364661307001878](https://www.sciencedirect.com/science/article/abs/pii/S1364661307001878)

**Substrate (internal, paths absolute):**
1. v1 metrics (MEASURED): `d:/AI/hd-instrument/data/exp_meta_knowledge_tip_of_tongue_v1_smoke/metrics.json`
2. v1 source: `d:/AI/hd-instrument/experiments/exp_meta_knowledge_tip_of_tongue_v1.py`
3. Skunkworks fairness pattern: `d:/AI/hd-instrument/notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md`
4. v4 nrem replay fairness drill (recent parallel TEST_DESIGN_FAILURE): `d:/AI/hd-instrument/notes/research_drill_v4_nrem_replay_fairness_violation_3x_2026-06-27.md`
5. exp_dev TOT handoff target (this note's downstream): `d:/AI/hd-instrument/notes/exp_dev_handoff_research_tip_of_tongue_v2_ratio_redesign_2026-06-27.md`

---

## META_RULE_AC discipline tag

- HYPOTHESIZED: substrate cluster_cos/cleanup_top1 ratio at SNR=0.5 ≈ 3.0-5.0 (extrapolated from v1 OFFSET_AMPLITUDE=0.5 construction; NOT measured at v2 ratio criterion)
- HYPOTHESIZED: v2 ratio criterion will fire at TOT-rate 0.30-0.50 at peak (deflated from naive 0.50-0.70)
- HYPOTHESIZED: P_deflated estimates above are calibration-deflated lit-scan inferences, not chain-grade priors
- MEASURED: v1 HC_recall=1.000, LC_refuse=0.992, peak_SNR=0.7, peak_cluster_acc=0.746, peak_tot_rate=0.525 (from `metrics.json` lines 3-4, verified)
- MEASURED: v1 ran in 21.8 sec with cardinality_ok=true (metrics line 207-209)
- MEASURED: brain literature citations (11 sources, all URL-verified via WebSearch 2026-06-27)
- MEASURED: v1 codebook OFFSET_AMPLITUDE=0.5 with centroid ~0.89 contribution (source line 221)

Per [[feedback-no-hallucinated-numbers-verify-on-disk]] — every quantitative claim about v1 sourced to metrics.json line numbers; every brain-literature claim sourced to WebSearch URL; the lit-scan-to-substrate-mapping ("ratio criterion matches cue-familiarity dual-channel") IS HYPOTHESIZED and could fail at v2 smoke.
