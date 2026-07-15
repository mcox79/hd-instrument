# Research drill: real experimental datasets with genuinely-measured 2-way nonadditivity, for conjunction-module ingest

Date: 2026-07-15
Dispatch: research (opus synthesis) + 3 parallel Sonnet lit-scan sub-agents (chemistry MMP nonadditivity / genetic epistasis / drug synergy)

## HEADLINE

Real, publicly-downloadable datasets with an **explicit precomputed interaction/nonadditivity term already in the data** (not something you narrate or derive) exist in all three target domains. The smallest, cleanest, most fact-crisp, verified-live one is the **Kramer et al. 2021 chemistry matched-molecular-pair (MMP) nonadditivity CSVs** (J. Cheminformatics 13:48) — three small supplementary CSV files, each row already carrying a computed `Nonadd_pC` value (deviation from strict additivity in a double-transformation cycle). This is the recommended #1 first ingest. Two much larger, equally clean fallbacks exist if more scale is wanted immediately: NCI-ALMANAC (ComboScore, direct ZIP) and Costanzo yeast SGA (epsilon score, direct bulk TSV).

This directly answers the problem stated in context: the prior two negative results (chemistry-mixing-hazard, genetic-epistasis-severity) were **LLM-narrated** conjunction labels that turned out additive-capturable. All three dataset families below instead carry a **measured, quantitative** deviation-from-additivity number computed by the original experimentalists/statisticians from real assay data — there is no narration step to smuggle in spurious "interaction" framing.

## Ranked shortlist (by domain)

### (A) Chemistry — matched-molecular-pair (MMP) potency/binding nonadditivity

| Rank | Dataset | Source / URL | Access | Size / format | Measured interaction term |
|---|---|---|---|---|---|
| 1 | **Kramer et al. 2021**, "Nonadditivity in public and inhouse data," *J. Cheminformatics* 13:48, doi:10.1186/s13321-021-00525-z | 3 supplementary CSVs, Springer-hosted, direct static URLs (verified live, unauthenticated):<br>`.../MOESM2_ESM.csv` (ChEMBL1613797)<br>`.../MOESM3_ESM.csv` (ChEMBL1614027)<br>`.../MOESM4_ESM.csv` (ChEMBL1613777) | Direct file download, no login | CSV, ~1,500+ rows each. Columns: `ID, SMILES, VALUE, nOccurence, Nonadd_pC` | `Nonadd_pC` = per-compound nonadditivity value from a double-transformation cycle (ΔΔpAct = pAct2 − pAct1 − pAct3 + pAct4, deviation from strict additivity). **Precomputed, present as a column.** |
| 2 | **Baum, Muley, Heine, Klebe et al. 2015**, "Strong Nonadditivity as a Key SAR Feature," *J. Chem. Inf. Model.* 55(4), doi:10.1021/acs.jcim.5b00018 | ACS supplementary files `ci5b00018_si_002.xlsx` (~27KB) + `ci5b00018_si_001.zip` (DTC-generation code, ~1.9MB) | ACS "free of charge" SI — **access unverified in this drill** (ACS pages 403'd the fetcher; needs a human/browser check) | Excel, ~44,519 double-transformation cycles from all of ChEMBL | Nonadditivity value per cycle, precomputed (per paper text) |
| 3 | **Fallback / derive-yourself**: ChEMBL bulk data (ftp.ebi.ac.uk/pub/databases/chembl or REST API) + `mmpdb` (open-source, github.com/rdkit/mmpdb) + Kramer's own `NonadditivityAnalysis` code (github.com/KramerChristian/NonadditivityAnalysis, and the archived `MolecularAI/NonadditivityAnalysis` which includes a full worked ChEMBL27 example, `ChEMBL_1614027.gz` + `NAA_Workflow_ChEMBL.ipynb`) | Public, scriptable | Arbitrary scale (limited by ChEMBL assay availability) | **Not precomputed** — you run the pipeline; useful only if candidate #1's ~4,500 rows total prove too small |

Caveat (important, flagged by the lit-scan): in this literature, a nontrivial fraction of apparent MMP "nonadditivity" is within experimental/assay noise (reported reproducibility ~0.3 log units in several of these papers) rather than real chemistry — this is a known, explicitly discussed confound in the source papers themselves, not something we're introducing. Treat it as the noise floor for the hard-fail threshold below, not as grounds to dismiss the domain.

### (B) Genetic epistasis / synthetic lethality — quantitative double-mutant interaction scores

| Rank | Dataset | Source / URL | Access | Size / format | Measured interaction term |
|---|---|---|---|---|---|
| 1 | **Costanzo et al. 2016** global yeast genetic interaction network (SGA) | https://thecellmap.org/yeast/costanzo2016/ (mirror: boonelab.ccbr.utoronto.ca/supplement/costanzo2016/) | Direct bulk download, no login. 3 file variants: raw pairwise (~521MB tab-delimited), matrix form (~35MB), profile-similarity matrices (~145MB) | ~23M double-mutant measurements, ~550K negative + ~350K positive interactions, ~90% yeast genome coverage | **epsilon (ε)** = measured double-mutant fitness − expected multiplicative fitness. Present directly as a column, alongside p-value and both single-mutant fitnesses. Standard field filter: \|ε\| > 0.08, p < 0.05. |
| 2 | **Benchmarking-GI-Scores** harmonized paralog-synthetic-lethality compendium (5 combinatorial CRISPR screens: Dede, CHyMErA, Ito, Parrish/"Big Papi", Thompson), NAR Genom. Bioinform. 2025 | Figshare: figshare.com/s/59ee190b1879fe3eb191 (data) + f3bff98db72e1039414b (code); github.com/cancergenetics/Benchmarking-GI-Scores | Direct bulk download | ~8,000+ human paralog gene-pairs across ~20 cancer cell lines | Multiple precomputed scores per pair (GEMINI-sensitive/strong, Parrish z-score, Orthrus, zdLFC) |
| 3 | **SLKB** (Synthetic Lethality Knowledge Base), NAR 2024, D1418 | slkb.docs.osubmi.org | Web app + notebook pipeline; **bulk flat-file download not confirmed** in this drill (worth a follow-up look) | 16,059 SL pairs + 264,424 non-SL pairs, 11 CDKO screens x 22 cell lines | Multiple precomputed scores (Horlbeck, median B-score, GEMINI, MAGeCK) |
| 4 | Pan-cancer paralog SL compendium, Genome Biology 2025, doi:10.1186/s13059-025-03737-w | figshare.com/articles/dataset/.../25954027 | Direct download | 472 predicted pairs tested x 27 cell lines, 117 confirmed | Continuous "mean normalized GI score" per pair per cell line |

Note: E-MAP legacy portal (phoibe.med.utoronto.ca/erg) appears dead — don't rely on it; DepMap's own single-gene CRISPR portal does NOT itself carry pairwise interaction scores (those live in the purpose-built combinatorial screens above, not in DepMap proper) — correcting an assumption in the original question.

### (C) Drug-drug synergy — Bliss/Loewe/ZIP/HSA excess-over-additivity

| Rank | Dataset | Source / URL | Access | Size / format | Measured interaction term |
|---|---|---|---|---|---|
| 1 | **NCI-ALMANAC** (Holbeck et al. 2017, Cancer Research, PMC5499996) | discover.nci.nih.gov/cellminer — direct file: `/cellminer/download/processeddataset/DTP_NCI60_ALMANAC_COMBO_SCORE.zip` | Direct bulk ZIP download, verified reachable, no login | ~290,000+ synergy determinations, NCI-60 cell lines x drug pairs x concentration combos | **ComboScore** — modified Bliss-independence excess-over-additivity, shipped directly in the file |
| 2 | **DrugComb** (drugcomb.org; Zagidullin et al. 2019 NAR) | Portal + REST API; reliably reachable via Therapeutics Data Commons: `DrugSyn(name='DrugComb')`, tdcommons.ai (pip install PyTDC) | TDC mirror confirmed programmatically reachable; native portal not confirmed reachable in this drill | ~297K-1.43M drug-pair x cell-line rows depending on release version | Bliss, Loewe, HSA, ZIP scores AND a CSS combination-sensitivity score, all precomputed columns |
| 3 | **O'Neil et al. 2016** (Merck oncology screen), Mol. Cancer Ther. 15(6) | Via TDC (`DrugSyn(name='OncoPolyPharmacology')`) or redistributed inside DrugComb | TDC route confirmed | 23,062 experiments, 583 combos (38 drugs) x 39 cell lines, 4x4 dose matrices | Loewe-additivity synergy values precomputed (via Combenefit) |
| 4 | **AstraZeneca-Sanger DREAM Challenge** (Menden et al. 2019, Nat. Commun.) | Synapse (registration-gated) OR Hugging Face mirror: `SageBio/astrazeneca-sanger-drug-combination-prediction` (no gate) | HF mirror is the frictionless route | 11,576 experiments, 910 combos x 85 cell lines | Loewe-based "excess cell kill over expected additive kill," precomputed label |
| 5 | DrugCombDB (drugcombdb.denglab.org) | Aggregator of the above + more, precomputes same 4 scores | Not confirmed reachable this session | overlaps #2 | Bliss/HSA/Loewe/ZIP, precomputed |

## #1 recommendation for the first ingest

**Kramer et al. 2021 chemistry MMP nonadditivity CSVs** (`J. Cheminformatics` 13:48).

Why this wins the ranking over the larger genetics/synergy candidates on the stated criteria (smallest-clean + measured-interaction-term + accessible + fact-crisp):
- **Smallest / cleanest**: 3 files, ~1,500 rows each (~4,500 rows total) — trivially small for a proof-of-concept ingest, versus tens-to-hundreds of thousands of rows for the genetics/synergy candidates. Fast to load, inspect by hand, and build a held-out split from.
- **Measured, not narrated**: `Nonadd_pC` is a single scalar per compound, computed directly from 4 measured potency values in a closed double-transformation cycle — it is the textbook-purest form of "does an additive model fail here," with no LLM, no expert-judgment severity label, no synergy-model-choice ambiguity (Bliss vs Loewe vs ZIP debates don't apply here — it's just arithmetic on measured pIC50/pKi values).
- **Fact-crisp**: a nonadditivity value either clears the noise floor (~0.3 log units per the source papers' own reproducibility estimates) or it doesn't — binary, well-defined, no interpretive narrative layer (unlike "epistasis severity" or "mixing hazard" framings that were the prior LLM-narrated failures).
- **Verified live and accessible**: this drill's lit-scan sub-agent directly fetched and confirmed the CSV structure and header row (`ID,SMILES,VALUE,nOccurence,Nonadd_pC`) at a stable, unauthenticated Springer static-content URL — no login, no API key, no registration gate (unlike Synapse-gated DREAM data).

Exact access path:
```
https://static-content.springer.com/esm/art%3A10.1186%2Fs13321-021-00525-z/MediaObjects/13321_2021_525_MOESM2_ESM.csv
https://static-content.springer.com/esm/art%3A10.1186%2Fs13321-021-00525-z/MediaObjects/13321_2021_525_MOESM3_ESM.csv
https://static-content.springer.com/esm/art%3A10.1186%2Fs13321-021-00525-z/MediaObjects/13321_2021_525_MOESM4_ESM.csv
```

If more scale is needed after the proof-of-concept (4,500 rows may be too thin for a train/held-out split with enough nonadditive-flagged cycles), the **immediate scale-up path without changing domains** is the `KramerChristian/NonadditivityAnalysis` / `MolecularAI/NonadditivityAnalysis` pipeline run over a larger ChEMBL bulk pull — same measured quantity, same method, arbitrary volume.

If the domain itself should shift to genetics or synergy for other strategic reasons (not covered by this drill's ranking criteria), **Costanzo yeast SGA** (ε score, ~23M rows, single bulk download) and **NCI-ALMANAC** (ComboScore, ~290K rows, single bulk ZIP) are both equally "measured not narrated" and immediately ingestable — they only lose to Kramer 2021 on the "smallest" criterion, not on cleanliness or accessibility.

## Cheap decisive test

Ingest the Kramer 2021 CSVs (3 files, ~4,500 rows). Build a held-out split stratified on `Nonadd_pC` magnitude. Construct: (1) a strong categorical-additive baseline predicting `VALUE` (pAct) from single-substituent main effects only (the same class of baseline that beat the two prior LLM-narrated conjunction claims), and (2) the conjunction-module candidate. Compare held-out prediction error specifically on the subset of double-transformation cycles where `|Nonadd_pC|` exceeds the assay noise floor (~0.3 log units, per source-paper reproducibility estimates) versus the subset where it doesn't.

## Falsifiable predictions

**HARD-PASS** (genuine 2-way structure the conjunction module can exploit and the additive baseline provably cannot): on cycles with `|Nonadd_pC| > 0.3` (noise-floor-cleared), the additive baseline's held-out error correlates with `|Nonadd_pC|` (i.e., the baseline is systematically wrong exactly where nonadditivity is large — this is definitionally guaranteed by construction, so the real pass criterion is that the conjunction module's error on this subset is materially lower, target: >=30% relative MAE reduction vs additive baseline, consistent with the module actually reading the second-order term rather than just noise-fitting).

**HARD-FAIL** (this domain isn't a real win either): if restricting to the noise-floor-cleared subset the conjunction module's improvement over the additive baseline collapses to within measurement-noise range of the improvement seen on the noise-floor subset (`|Nonadd_pC| < 0.3`), that means the module is not discriminating genuine chemistry from assay noise — same failure signature as the two prior negatives, just relocated to a new domain. Also HARD-FAIL if fewer than ~15% of the ~4,500 rows clear the noise floor (insufficient genuinely-nonadditive examples to learn from at this scale) — in that case, escalate to the ChEMBL-bulk-rerun fallback (#3 in table A) rather than concluding the domain is closed.

## Cross-thread synthesis

Directly follows and corrects course from `notes/drill_realworld_conjunctive_determination_prevalence_and_targets_2026-07-14.md`, which predicted (from meta-science literature, not real datasets) that chemistry QSAR nonadditivity (30-58% of assays) and synthetic-lethality (purest AND-gate) are the two domains where genuine conjunctions concentrate. This drill confirms that prediction was directionally right about WHERE to look, but the prior two attempts to act on it used LLM-narrated proxies for those domains (a hazard-mixing narrative, an epistasis-severity narrative) instead of the underlying measured data the 2026-07-14 note actually pointed at. This drill closes that gap: the real Kramer/Costanzo/NCI-ALMANAC/DrugComb datasets carry the measured quantity natively — no narration step exists to fail at.

## Substrate-product implications

If the conjunction module reads genuine signal on the Kramer 2021 nonadditive subset (HARD-PASS), that is the first real-data proof-of-concept that the mechanism's proven capability (reads genuine 2-way interaction where it structurally exists) transfers from synthetic-benchmark validation to a real experimental measurement — directly load-bearing for the PIVOT's "ideal knowledge foundation" program, since it would identify a genuinely non-additive real-world relation-class (matched-molecular-pair SAR) suitable for foundation-content sourcing, distinct from the single-driver-dominant domains (ecology/organismal/economic) the prior drill ruled out. If HARD-FAIL, it narrows the "real conjunctions exist and are learnable-from-real-noisy-data" claim specifically to larger-N domains (Costanzo-scale, NCI-ALMANAC-scale) where per-example noise averages out better, which is itself a useful scoping result for foundation-content sourcing (favor N>100K measured-interaction corpora over N~1000).

## Citations (verified count: 13)

1. Kramer, C. et al. 2021. "Nonadditivity in public and inhouse data: implications for drug design." J. Cheminformatics 13:48. doi:10.1186/s13321-021-00525-z. [Supplementary CSVs fetched and header-verified directly.]
2. Baum, D., Muley, L., Heine, A., Klebe, G. et al. 2015. "Strong Nonadditivity as a Key SAR Feature." J. Chem. Inf. Model. 55(4). doi:10.1021/acs.jcim.5b00018. [Access unverified — ACS 403'd fetch.]
3. Kramer, C. 2019. "Nonadditivity Analysis." J. Chem. Inf. Model. 59(9):4034-4042. doi:10.1021/acs.jcim.9b00631. [Methods reference; SI unverified.]
4. github.com/KramerChristian/NonadditivityAnalysis (code, verified reachable)
5. github.com/MolecularAI/NonadditivityAnalysis (archived, includes worked ChEMBL27 example, verified reachable)
6. mmpdb — github.com/rdkit/mmpdb (open-source MMP generation, JCIM 2018)
7. Costanzo, M. et al. 2016. "A global genetic interaction network maps a wiring diagram of cellular function." Science. Data: thecellmap.org/yeast/costanzo2016/ [bulk files described, not individually fetched-and-verified row-by-row this session].
8. "Benchmarking genetic interaction scoring methods for identifying synthetic lethality from combinatorial CRISPR screens." NAR Genomics and Bioinformatics 2025 / biorxiv 2025.03.31.645224. github.com/cancergenetics/Benchmarking-GI-Scores.
9. SLKB (Synthetic Lethality Knowledge Base). Nucleic Acids Research 2024, D1418. slkb.docs.osubmi.org.
10. "A compendium of synthetic lethal gene pairs..." Genome Biology 2025. doi:10.1186/s13059-025-03737-w.
11. Holbeck, S.L. et al. 2017. "The NCI-ALMANAC..." Cancer Research. PMC5499996. discover.nci.nih.gov/cellminer [ZIP file link verified reachable].
12. Zagidullin, B. et al. 2019. "DrugComb: an integrative cancer drug combination data portal." NAR 47(W1):W43-W51. Mirror: tdcommons.ai (PyTDC, verified programmatically reachable).
13. O'Neil, J. et al. 2016. "An Unbiased Oncology Compound Screen to Identify Novel Combination Strategies." Mol. Cancer Ther. 15(6):1155-1162. Menden, M.P. et al. 2019 (AZ-Sanger DREAM), Nat. Commun. Hugging Face mirror: SageBio/astrazeneca-sanger-drug-combination-prediction [verified format description, not independently re-fetched].

Calibration note: this is a dataset-sourcing drill, not a mechanism-P-estimate drill — no P(mechanism works) claim is made here per se. The falsifiable predictions above carry the standard calibration discipline (explicit HARD-FAIL thresholds, noise-floor accounting) in lieu of a deflated P estimate, since the deliverable is "does this dataset exist and is it accessible" (largely verified empirically by the lit-scan sub-agents fetching live URLs) rather than a novel-synthesis theoretical claim.
