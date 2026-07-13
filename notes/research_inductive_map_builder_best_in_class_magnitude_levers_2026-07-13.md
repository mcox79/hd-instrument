# Research: best-in-class magnitude calibration + ranked levers for the proven ANCHOR_COMPOSE inductive map-builder

**Filed by:** research sub-agent. **Trigger:** mission directive — the glass-box degree-invariant additive-bundle inductive
entity-generalization mechanism (`ANCHOR_COMPOSE`) is now VET-confirmed CHAIN_GRADE (`data/exp_anchor_compose_inductive_
entity_cskg_v1/metrics.json`: `HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE`, oracle ratio 284x; `data/exp_anchor_compose_identity_
shuffle_cskg_v2/metrics.json`: `HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE_IDENTITY_CLOSED`, identity-leak collapse_ratio 0.016,
all gating leak vectors shut). Absolute magnitude is low: held-out filtered-MRR 0.1282, Hits@1 0.0521, Hits@3 0.1259,
Hits@10 0.2780, Hits@100 0.7879 (CSKG-12core, N=25,752 entities, `support_frac=0.50`, `n_heldout_eval=3000`, filtered
ranking against the full 25,752-entity pool, 3 seeds). This drill (1) calibrates that magnitude against published
inductive-KGE SOTA and (2) ranks levers — brain-grounded first, then field-mechanism — to raise it without breaking
glass-box/zero-training/native-store properties. 3 parallel Sonnet lit-scans (inductive-KGE benchmark calibration;
brain cleanup/aggregation mechanisms; field aggregation/iterative-refinement magnitude ablations), pure literature
research, no local compute. Extends `notes/research_inductive_entity_generalizing_factorized_map_builder_2026-07-12.md`
(designed the mechanism that this drill's Part A now benchmarks and Part B now optimizes).

---

## HEADLINE

1. **Our current number is roughly at the LOW END of the correct comparison class, not far below it — and the
   comparison class matters enormously.** Curated-ontology inductive benchmarks (WN18RR-inductive, FB15k-237-inductive)
   report MRR 0.37-0.73 and Hits@10 48-80% under full-entity-ranking — these look like a huge gap versus our 0.128/0.278,
   but they are NOT the right comparison: those graphs have clean, unambiguous relation semantics (9-222 sharply-defined
   relation types) that commonsense graphs do not have. The one genuinely apples-to-apples precedent — **InductivE on
   ConceptNet** (Wang et al., IJCNN 2021, arXiv:2009.09263), a trained-GNN-encoder method on a real commonsense KG with
   free-text node identities — reports inductive MRR in roughly the high-teens percent (~0.18-0.21) and Hits@10 ~0.29-0.50.
   **Our zero-training glass-box construction (MRR 0.128, Hits@10 0.278) already sits within ~60-95% of that number**,
   using NO gradient descent for the new entity at all, where InductivE uses a fully trained GNN encoder plus semantic
   text embeddings. On ATOMIC (much larger, sparser, free-text-entity commonsense KG), even trained methods only reach
   MRR ~0.02-0.08, Hits@10 ~0.05-0.12 — we already clear that floor by 1.5-6x. **TARGET RANGE: MRR 0.18-0.22, Hits@10
   0.40-0.50 is the concrete "close the gap to commonsense-KG-SOTA" bar** (InductivE-class, trained-encoder parity);
   MRR 0.35+/Hits@10 50%+ is the curated-ontology-benchmark bar and is NOT the right target for a commonsense KG.
2. **A hard evaluation-protocol trap sits in the middle of this literature and our own number happens to land on the
   harder side of it.** Two incompatible protocols are both called "inductive link prediction": GraIL/NBFNet's own
   papers rank each test triple against only **50 sampled negative entities** (Hits@10 inflated to 58-96%); RED-GNN/
   A*Net/ULTRA re-ran the SAME models under **full-entity-set filtered ranking** and Hits@10 collapsed (e.g. GraIL
   WN18RR v3: 58.4% at 50-neg -> 40.9% at full-ranking). **Our protocol (filtered MRR vs. the entire 25,752-entity pool)
   matches the harder, full-ranking family** — so our numbers should be compared ONLY against the full-ranking rows in
   the table below, never against the 50-neg rows, or the gap will look ~2x larger than it really is.
3. **Apples-to-apples direction, both ways.** HARDER for us: (a) zero gradient training for the held-out entity at all
   (InductivE/NBFNet/RED-GNN all use a trained forward pass, ours is pure closed-form composition); (b) only 50%
   support (`support_frac=0.50`) of each held-out entity's edges are visible — most inductive-KGE papers give the model
   the entity's FULL local subgraph at test time, we deliberately withhold half; (c) full-pool ranking (harder protocol,
   point 2). EASIER for us: (a) CSKG-12core is k-core=12 filtered — every entity has degree >=12, denser than raw
   ConceptNet/ATOMIC (which include many low-degree/singleton entities that drag ATOMIC's numbers to near-floor); (b)
   N=25,752 is a much smaller candidate pool than ATOMIC's 304K entities, which mechanically inflates Hits@k at fixed
   absolute skill; (c) 85% of the graph remains known/trained, a relatively rich reference frame. **Net read: our number
   is a genuinely respectable zero-training result sitting near the bottom of the correct (commonsense, trained-encoder)
   comparison band, not a large unexplained shortfall** — but there IS real headroom (60-95% of target, not 100%+), and
   concrete levers below could plausibly close it.
4. **Ranked-lever headline: the single most promising, cheapest, best-evidenced lever is SEQUENTIAL/ITERATIVE PEELING
   of the support bundle (replacing today's single-shot mean+one-pass-cleanup with a multi-round "decode strongest
   term, subtract, re-estimate residual" loop) — this has BOTH a strong brain precedent (theta-gamma sequential slotting
   avoiding flat simultaneous superposition; predictive-coding iterative error correction) AND a quantified computational
   precedent already inside the adjacent VSA literature: sequential/hybrid resonator decoding recovers up to **8x more
   components from a superposition than one-shot parallel decode** (Hersche et al./Karunaratne et al., arXiv:2412.00354).
   It reuses the substrate's OWN existing primitive (`hdlab/cleanup_family.py::peel_sic_readout`) as an outer loop, adds
   zero trained parameters, and is a cheap CPU-tractable re-run on the already-built harness.
5. **The proven capacity-tracks-LOCAL-DEGREE law is a hard ceiling on several levers, not just a caveat.** GrapHD's
   `SNR ~ 5*log(D/d)` (D=vector dimension, d=number of bound terms superposed per entity — see prior drill's
   triple-confirmation across VSA/KGE-rank-bottleneck/hippocampal-CA3 theory) means ANY lever that increases the
   effective bundle size `d` (2-hop expansion, larger anchor sets) trades SNR against dimension at FIXED D. Multi-hop
   expansion (lever with the single largest quantified field-literature gain, +5 to +20 MRR points per GA-S2S ablation)
   is therefore not a free win here — it must be paired with a `n_dim` increase or it will cannibalize its own gain
   through crosstalk, exactly the mechanism the `anchor_compose_scaling_ladder_cskg_v3` cell (in flight, not yet landed)
   was designed to characterize empirically.

---

## Part A — best-in-class calibration table (verbatim protocol notes; DO NOT cross-compare across protocol columns)

| Method | Dataset/split | MRR | Hits@10 | Protocol | Pool size | Comparable to us? |
|---|---|---|---|---|---|---|
| GraIL (Teru et al. ICML 2020, arXiv:1911.06962) | WN18RR/FB15k-237/NELL-995 v1-v4 | not reported | 58-96% | **50 sampled negatives** | 51 | NO — wrong protocol |
| GraIL (re-run by RED-GNN, full ranking) | WN18RR v1-v4 | .627/.625/.323/.553 | 76.0/77.6/40.9/68.7% | full entity ranking, filtered | full (~thousands) | YES (protocol match) |
| GraIL (re-run) | FB15k-237 v1-v4 | .279/.276/.251/.227 | 42.9/42.4/42.4/38.9% | full ranking | full | YES |
| NBFNet (Zhu et al. NeurIPS 2021, arXiv:2106.06935) | WN18RR/FB15k-237 v1-v4 | not reported | 83-96% | 50 sampled negatives | 51 | NO — wrong protocol |
| NBFNet (re-eval in A*Net paper) | WN18RR v1-v4 | .741/.704/.452/.641 | (appendix) | full ranking, filtered | full | YES |
| NBFNet (re-eval) | FB15k-237 v1-v4 | .422/.514/.476/.453 | (appendix) | full ranking | full | YES |
| RED-GNN (Zhang & Yao, WebConf 2022, arXiv:2108.06040) | WN18RR v1-v4 | .701/.690/.427/.651 | 79.9/78.0/52.4/72.1% | full ranking, filtered | full | YES |
| RED-GNN | FB15k-237 v1-v4 | .369/.469/.445/.442 | 48.3/62.9/60.3/62.1% | full ranking | full | YES |
| A*Net (Zhu et al. 2023, arXiv:2206.04798) | FB15k-237 v1-v4 | .457/.510/.476/.466 | — | full ranking, filtered | full | YES |
| A*Net | WN18RR v1-v4 | .727/.704/.441/.661 | — | full ranking | full | YES |
| ULTRA zero-shot (Galkin et al. ICLR 2024, arXiv:2310.04562), 18 inductive-entity graphs, avg | mixed general KGs | 0.431 | 56.6% | full ranking, filtered | full (varies) | YES, closest "generalist" comparison |
| ULTRA zero-shot, 23 inductive entity+relation graphs, avg | mixed | 0.345 | 51.3% | full ranking | full | YES |
| **InductivE (Wang et al., IJCNN 2021, arXiv:2009.09263) — ConceptNet, inductive** | ConceptNet CN-82K, 78,334 entities, 52.3% test triples w/ unseen entity | **~0.18-0.21** | **~0.29-0.50** | full entity ranking, filtered, both directions | 78,334 | **CLOSEST APPLES-TO-APPLES — commonsense KG** |
| RotatE / ConvE (same InductivE paper, same split) | ConceptNet | 0.21-0.32 | 0.40-0.50 | same | 78,334 | commonsense KG, trained encoder |
| **InductivE — ATOMIC, inductive** | 304,388 entities, 37.6% unseen-entity test triples | **~0.02-0.08** | **~0.05-0.12** | full ranking, filtered | 304,388 | commonsense KG, near-floor even for trained methods |
| **OUR RESULT — ANCHOR_COMPOSE, CSKG-12core, held-out ENTITY, `support_frac=0.50`** | N=25,752, k_core=12, `n_heldout_eval=3000` | **0.1282** | **0.2780** | full entity ranking (25,752 pool), filtered, 3 seeds | 25,752 | zero-training, closest structural cousin to ConceptNet row above |

**Calibration bands (MRR / Hits@10), from full-ranking-protocol rows only:**
- **Near-floor:** ATOMIC-inductive even with trained encoders, MRR 0.02-0.08, Hits@10 5-12% — huge sparse free-text
  entity vocabulary defeats even gradient-trained methods.
- **Working, commonsense-KG-class (OUR TARGET BAND):** ConceptNet-inductive (InductivE/RotatE/ConvE), MRR 0.18-0.32,
  Hits@10 29-50%. **This is the correct comparison class for CSKG** — same commonsense-graph character (noisy,
  overlapping, non-ontological relation semantics), same rough entity-count order of magnitude.
  We are at 0.128/0.278 — **roughly 60-70% of the MRR range, ~95% of the low end of the Hits@10 range** — with zero
  gradient training.
- **SOTA on curated ontological benchmarks (NOT our comparison class):** WN18RR/FB15k-237 v2/v4 best specialist
  methods, MRR 0.44-0.73, Hits@10 60-80%. These graphs have 9-222 crisply-defined relation types; CSKG's relations are
  schema-blurred (flagged as a live risk in the prior sibling drill, `research_kg_degree_community_diagnostic_2026-07-
  12.md`) — closing to THIS band would require solving a harder, separate knowledge-richness problem, not just an
  architecture upgrade, and should not be the working target.
- **Generalist/foundation-model class:** ULTRA zero-shot averaged across 18-51 graphs, MRR 0.35-0.43, Hits@10 51-57% —
  a useful reference for "how much a trained-but-graph-agnostic method loses relative to graph-specific SOTA" (ULTRA
  loses ~0.05 MRR vs. per-graph supervised baselines on average), interesting as an upper anchor for what a FUTURE
  trained (not zero-shot) version of our mechanism might approach, but not the near-term target.

**Verified count for Part A: 10 external sources (GraIL, NBFNet, A*Net, RED-GNN, NodePiece, ULTRA, InductivE, Malaviya
et al. 2020 baseline, ATOMIC2020, CSKG paper) + 1 on-disk metrics file (`exp_anchor_compose_inductive_entity_cskg_v1/
metrics.json`).** NodePiece V2-V4 numbers and CSKG's own published link-prediction numbers were searched for and NOT
found — flagged as a genuine literature gap (no paper publishes inductive link-prediction numbers on CSKG itself), not
a confirmed absence.

**P_deflated for the target-range claim (MRR 0.18-0.22 / Hits@10 0.40-0.50 is the correct near-term bar): 0.55** —
deflated from a higher confidence because the InductivE ConceptNet numbers themselves carry an extraction-scale caveat
(percentage-vs-decimal ambiguity in one baseline row, flagged honestly by the lit-scan; the qualitative ordering and
rough magnitude band is corroborated across two independent extraction passes, so the BAND is trustworthy even though
the exact decimal is not).

---

## Part B — ranked levers (brain-grounded first, then field mechanisms)

### Lever 1 (TOP RANK) — Sequential/iterative peeling of the support bundle (brain: theta-gamma sequential slotting + predictive-coding error correction; field: SIC / iterative message-passing)

**Mechanism:** replace today's single-shot `mean-then-one-pass-cleanup` with an outer loop: decode the strongest
recoverable anchor-bind term from the bundle, subtract its reconstruction, re-run `peel_sic_readout` on the residual,
repeat for a small fixed number of rounds (2-4). This is a genuinely closed-form iterative procedure over the EXISTING
primitive, not a new mechanism.

**Brain-analog:** (a) theta-gamma phase coding — multiple items held in WM via SEQUENTIAL phase/gamma-cycle slots
rather than one flat simultaneous superposition (Lisman & Idiart 1995; Kaminski et al. 2015, theta-gamma phase-phase
coupling scales with load) — direct qualitative precedent for "sequential beats flat superposition," though the
neuroscience evidence is coupling-strength-scored, not accuracy-scored. (b) Predictive-coding iterative error
correction (Salvatori et al. 2021, arXiv:2109.08063; Tang et al. 2023, PMC10132551) — hierarchical prediction-error
minimization reported to outperform (single-pass) Hopfield/autoencoder denoising, a direct brain-grounded analog of
"iteratively refine the noisy composite, don't just read it once."

**Field/computational precedent (quantified, DIRECT PRECEDENT):** hybrid sequential+parallel resonator decoding
recovers **up to 8x more additive components from a superposition** than one-shot parallel decode (Karunaratne,
Hersche, Sebastian, Rahimi, arXiv:2412.00354) — this is the single cleanest quantified number found across both
lit-scans for "iterative beats single-shot on a superposition-decode task," and it is evaluating literally the same
primitive family (`peel_sic_readout` IS a resonator-style SIC decoder) the substrate already has.

**Expected magnitude:** the 8x figure is for component-recovery-count in an idealized superposition-decode benchmark,
not directly transferable as "8x MRR" — deflate heavily. Realistic expectation: enough SNR recovery to matter at OUR
typical bundle sizes (median held-out-entity anchor-edge count, likely single digits given k_core=12 and
`support_frac=0.50`), i.e. plausibly +0.02-0.06 absolute MRR (roughly 15-45% relative), landing partway into the
target band from Part A. SIC's OWN literature caveat applies directly: gain is LOAD-DEPENDENT (bigger at higher
bundle sizes, ~0 at bundle size 1-2) and vulnerable to ERROR PROPAGATION if the first-peeled term is itself noisy —
this should be checked empirically, not assumed uniform across held-out entities.

**Glass-box compatibility:** FULL — zero trained parameters, deterministic fixed-point procedure, reuses existing
code (`cleanup_family.py::peel_sic_readout`) as a loop, not a new mechanism class.

**Cost:** LOW — CPU-tractable re-run of the already-built harness with the aggregation/cleanup step swapped; no new
infrastructure.

**Cheap-next-cell-vs-bigger-build:** **CHEAP NEXT CELL.** This is the single best candidate for the immediate follow-up
dispatch.

**P_deflated: 0.40** (capped under novel-synthesis ceiling; deflated from the 8x figure's face value because that
number comes from an idealized synthetic superposition-decode benchmark, not a real commonsense-KG task, and the
load-dependence / error-propagation caveats are real, unquantified-for-our-setting risks).

---

### Lever 2 — Hard-negative / self-adversarial retraining of the SHARED scorer (`W`) (field: KGE negative-sampling ablations; brain: none direct — flagged honestly)

**Mechanism:** the scorer (`W`, relation codebook `R`, `score_all`) is trained ONLY on known (non-held-out) triples
and is REUSED UNCHANGED for the held-out arm — this lever does not touch `E_derived` construction at all, only the
quality of the shared function the mechanism reads out through. If current training uses uniform/random negative
sampling, switching to self-adversarial hard-negative weighting (Sun et al., RotatE, arXiv:1902.10197) is a
same-architecture, same-training-loop upgrade.

**Brain-analog:** none direct found in this scan (flagged honestly rather than force-fit) — this is a pure
statistical-learning-theory lever, not a brain-grounded one. Included because it is the single most consistently
QUANTIFIED lever in the whole scan and does not touch the new-entity representation at all.

**Expected magnitude (quantified, multiple independent sources):** RotatE self-adversarial ablation on FB15k-237:
MRR 0.295 -> 0.338, **+0.043 absolute (+14.6% relative)** (arXiv:1902.10197). MixKG hard-negative-mixing ablation:
**+0.0180 MRR (FB15k-237), +0.0115 MRR (WN18RR), +1.07 to +1.74 Hits@10 points** across 4 backbones (arXiv:2202.09606).
InCL-KGC contrastive/hard-negative variant: **+1.2% MRR, +6.8% Hits@10** on WN18RR. Consistent band across all three:
**roughly +0.02-0.04 absolute MRR, +1-7 Hits@10 points.**

**Glass-box compatibility:** FULL — this is standard training of the ALREADY-TRAINED shared scorer; the new entity
itself still receives zero gradient steps, so it does not compromise the mechanism's headline "zero training for new
entities" property at all.

**Cost:** LOW-MODERATE — requires re-fitting `W`/`R` with a different negative-sampling scheme (one training run,
not new infrastructure), then re-evaluating the SAME held-out split.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, can run in parallel with Lever 1 (orthogonal — one touches the
aggregation/readout, the other touches the shared scorer's training).

**P_deflated: 0.45** (highest of all levers — this is literature-CONVERGENT evidence across 3 independent papers on
KGE-specific benchmarks, closest thing to a "sure bet" in this scan, deflated modestly only because none of the 3
papers evaluate on a held-out-ENTITY inductive split specifically, all are transductive negative-sampling ablations —
whether the gain transfers cleanly to the inductive `E_derived` readout is the one open inference step).

---

### Lever 3 — Multi-hop (2-hop) anchor support, GATED by the degree/dimension ceiling (field: k-hop aggregation ablations; brain: weak/indirect — CA3 trisynaptic loop, grid-cell path integration)

**Mechanism:** extend the anchor-reaching BFS from 1-hop to 2-hop (an entity's bundle includes not just directly-adjacent
anchors but anchors reached via one intermediate hop, each 2-hop term bound through the COMPOSITION of two relation
operators rather than one — the natural generalization of the existing `bundle_{(v,p,a)} R[p]*E[a]` construction).

**Brain-analog:** weaker than Lever 1's. The hippocampal trisynaptic loop (DG -> CA3 -> CA1, with CA3's own recurrent
collaterals effectively integrating multi-step associative context) and grid-cell path integration (code accumulated
over MULTIPLE small steps, not a single jump) are structurally suggestive but not a tight, directly-cited precedent
for "2-hop bind-composition specifically improves retrieval accuracy" — flagged as the honest gap rather than
force-fitting a citation.

**Expected magnitude (quantified, field lit-scan, LARGEST single number in this whole drill):** GA-S2S ablation
(arXiv:2605.18211): 1-hop context alone improves MRR over no-context baseline by **+11.2%, +4.8%, +1.7%** across three
datasets; adding 2-hop ON TOP improves further by **+19.5%, +6.6%** MRR on two of them. This is the single largest
quantified per-lever gain found in either lit-scan.

**THE CEILING THIS DRILL MUST FLAG:** per HEADLINE point 5, GrapHD's `SNR ~ 5*log(D/d)` means 2-hop expansion
increases `d` (bound terms bundled per entity) substantially — a 2-hop bundle can be several times larger than the
1-hop bundle for the same entity. **At FIXED `n_dim`, this lever trades bundle-size for SNR and could net NEGATIVE**
unless `n_dim` is scaled up proportionally (the SNR formula gives a concrete, cheap pre-flight check: compute
predicted SNR at the actual 2-hop bundle-size distribution for held-out entities BEFORE running the full cell, per
the same discipline the prior drill flagged for the 1-hop case). Field-literature over-smoothing evidence (GNN
accuracy peaking at 1-2 hops then degrading) independently corroborates that this is a real risk, not just a
theoretical one.

**Glass-box compatibility:** FULL if implemented as a fixed 2-hop BFS + composition rule (no learned aggregation
weights) — same closed-form character as the current 1-hop construction.

**Cost:** MODERATE — requires extending anchor-selection/BFS logic (the `anchor_compose_scaling_ladder_cskg_v3` cell,
already in flight per the status log, appears to probe an adjacent scaling axis and its landed result should be read
before committing further compute here) and likely a `n_dim` increase to stay clear of the SNR ceiling, which raises
compute cost non-trivially versus Levers 1-2.

**Cheap-next-cell-vs-bigger-build:** **BIGGER BUILD** — gate on (a) `anchor_compose_scaling_ladder_cskg_v3` landing
first (already dispatched, don't duplicate), and (b) a cheap SNR pre-flight calculation using the ALREADY-COLLECTED
held-out-entity degree distribution before committing to a `n_dim` increase.

**P_deflated: 0.30** (capped under novel-synthesis ceiling and further discounted for the real, literature-corroborated
risk that the gain inverts at fixed dimension — the largest quantified number in this drill comes with the largest
asterisk).

---

### Lever 4 — Degree-weighted (not learned-attention) aggregation in place of flat unweighted mean (field: GNN aggregation-function ablations; brain: none direct)

**Mechanism:** replace `bundle = mean(...)` with a closed-form degree-normalized weighting (GCN-style
`D^-1/2 sum D^-1/2`-analog) — NOT learned attention (disqualified: requires trained per-edge attention weights,
which would break the zero-training-for-new-entities property).

**Brain-analog:** none direct found — flagged honestly.

**Expected magnitude:** MIXED/INCONSISTENT evidence. On OGB link-prediction benchmarks, **GraphSAGE-mean actually
BEATS degree-normalized GCN** (ogbl-collab Hits@50: 48.45 vs 44.62; ogbl-ddi Hits@20: 0.539 vs 0.370) — i.e. the
sign of this lever is not even reliably positive. A 24-dataset ablation found the effect is graph-topology-dependent
(large gaps only on heterophilic/degree-skewed graphs) with no universal direction.

**Glass-box compatibility:** FULL (closed-form, zero learned parameters).

**Cost:** TRIVIAL — a one-line change to the existing bundle step, testable on the current harness in a CPU minutes-scale
rerun.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, but LOW EXPECTED VALUE — worth a quick free test given near-zero
cost, but should not be prioritized ahead of Levers 1-2.

**P_deflated: 0.20** (the literature genuinely does not support a confident directional bet here; testing is cheap
enough to be worth doing anyway, but expectations should be low).

---

### Lever 5 — Anchor-set decorrelation before bundling (brain: dentate-gyrus pattern separation)

**Mechanism:** apply a decorrelation/diversity constraint to anchor SELECTION (favor anchors whose codes/contexts are
maximally non-overlapping) so the bind-terms being bundled are less mutually correlated, analogous to DG's
expansion-recoding of EC input before it reaches CA3.

**Brain-analog:** DG pattern separation (Rolls 2013, PMC3812781; empirical ~0.26 rate-overlap decorrelation observed
between similar contexts at the DG stage, Cell Reports 2023) — a real, well-established mechanism, but the
quantification in this literature is at the level of DOWNSTREAM AUTOASSOCIATOR STORAGE CAPACITY (Treves-Rolls
`N/(a ln 1/a)` formula), not directly "% retrieval-accuracy gain from decorrelating inputs before averaging" — the
lit-scan explicitly could not find a clean accuracy-delta number for this specific transfer.

**Expected magnitude:** UNQUANTIFIED for this exact setting — qualitatively plausible (less correlated bind-terms
should bundle with less mutual crosstalk, consistent with the SNR-vs-degree formula's implicit assumption of
roughly-independent terms) but no paper gives a number to anchor an estimate.

**Glass-box compatibility:** FULL (a closed-form anchor-selection heuristic change, e.g. adding a diversity term to
the existing NodePiece-style PPR/degree/random anchor-selection split).

**Cost:** LOW — changes only the anchor-selection heuristic, no new primitives.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL but speculative — worth bundling as a secondary arm in the SAME
cell as Lever 1/2's ablation rather than a standalone dispatch, given the cost is low and it shares infrastructure.

**P_deflated: 0.25** (mechanism is real and well-established in neuroscience, but the missing accuracy-delta
quantification means this is closer to novel synthesis than literature-confirmation for THIS specific application).

---

### Lever 6 (LOWEST RANK) — Grid-cell/TEM factorized structural rebinding

**Mechanism:** as proposed in the prior drill, structurally separate "which relation composes" from "which anchor
content" more explicitly (already largely true of the current `R[p]*E[a]` construction) — this drill re-evaluated
whether pushing this further would move ABSOLUTE MAGNITUDE and concludes it likely would not, for a specific reason:

**Why deprioritized:** the brain lit-scan itself rates this mechanism "analogous to loose" for THIS specific question
— TEM's demonstrated capability is GENERALIZING RELATIONAL STRUCTURE ACROSS GRAPHS/CONTENT-SETS (a different
capability, matching this program's OTHER standing thread on relational generalization per
`project_relational_capability_is_the_core_requirement_...md`), not improving retrieval accuracy FROM A FIXED STORE
for an entity that is already structurally well-represented. No quantified accuracy number was found even after a
direct search. This lever is more relevant to a DIFFERENT open question (generalizing to unseen RELATION types, which
CSKG's `ANCHOR_COMPOSE` does not yet attempt) than to raising THIS metric's absolute magnitude.

**P_deflated: 0.15** for "this moves the held-out-entity magnitude specifically" — genuinely low, not a hedge;
redirect this idea toward the unseen-RELATION generalization question instead, where it is a better fit.

---

## Cheap decisive test

**Dispatch ONE cell, two orthogonal arms, reusing the EXISTING `anchor_compose_inductive_entity_cskg_v1/v2` harness
verbatim (same split, same seeds [7,13,17], same `n_heldout_eval=3000`, same controls):**

- **Arm A (Lever 1): `ANCHOR_COMPOSE_PEEL`** — swap the current single-shot mean+one-pass-cleanup for a 2-4 round
  sequential SIC-peel loop reusing `peel_sic_readout`, everything else unchanged.
- **Arm B (Lever 2): `ANCHOR_COMPOSE_HARDNEG`** — re-fit `W`/`R` with self-adversarial/hard-negative weighting
  (RotatE-style) on the SAME known-triple training set, then re-evaluate the SAME frozen `E_derived` construction
  through the new scorer.
- **Optional cheap third arm (Lever 5): `ANCHOR_COMPOSE_DECORR`** — add a diversity term to anchor selection,
  bundled into the same dispatch since it shares infrastructure and costs little extra.

**HARD-PASS (Lever 1, Arm A):** MRR gain `>= 0.02` absolute (`>=15%` relative over the 0.1282 baseline) with
oracle/random/scramble controls unchanged from the landed v1/v2 values (confirms no new leak introduced) — this
would clear roughly a third of the way into the Part A target band on its own.

**HARD-FAIL (Arm A):** MRR gain `< 0.005` absolute despite 2-4 peel rounds — this would be informative, not just
negative: per the SIC literature's own load-dependence caveat, it would mean typical held-out-entity bundle sizes on
CSKG-12core are too small for peeling to have material superposition to exploit, pointing toward Lever 3 (bigger
bundles via 2-hop, gated on dimension) rather than better decoding of the CURRENT bundle size.

**HARD-PASS (Lever 2, Arm B):** MRR gain `>= 0.02` absolute, matching the literature's +0.02-0.04 band, with the
gain observed EVEN THOUGH `E_derived` itself is completely unchanged (isolates the win to scorer quality, not
representation quality).

**HARD-FAIL (Arm B):** MRR gain `< 0.005` absolute — would suggest the bottleneck is NOT scorer calibration (current
negative sampling is already adequate) but IS the `E_derived` construction itself, redirecting priority fully onto
Levers 1/3/5.

**Middle band (either arm, gain in [0.005, 0.02)):** degree-stratify by held-out entity's anchor-bundle size
(Arm A) or query-frequency (Arm B, per the KGE literature's own finding that hard-negative gains concentrate on
LOW-frequency queries). If the gain scales with the stratifying variable in the literature-predicted direction, the
lever works but needs to be applied more aggressively/selectively, not universally — a scaling finding, not an
architecture failure.

**Must-fail control:** `BASELINE_POP` and `RANDOM_CODES` through the identical harness, unaffected by either arm
(reuses the existing control, per the landed v1/v2 cells).

---

## Falsifiable predictions summary

| Lever | HARD-PASS threshold | HARD-FAIL threshold | P_deflated |
|---|---|---|---|
| 1. Sequential SIC-peel (brain: theta-gamma / predictive coding) | MRR +>=0.02 abs | MRR +<0.005 abs | **0.40** |
| 2. Hard-negative scorer refit (field: KGE self-adversarial) | MRR +>=0.02 abs | MRR +<0.005 abs | **0.45** |
| 3. 2-hop anchor expansion, gated on SNR/dimension (field: k-hop; brain: weak) | MRR +>=0.03 abs AND SNR pre-flight check confirms `n_dim` clears crosstalk floor at 2-hop bundle size | margin flat or negative after `n_dim` compensation | 0.30 |
| 4. Degree-weighted (non-learned) aggregation | MRR +>=0.01 abs, either direction stable across seeds | no stable sign across seeds | 0.20 |
| 5. Anchor decorrelation (brain: DG pattern separation) | MRR +>=0.01 abs | MRR +<0.003 abs | 0.25 |
| 6. Grid-cell/TEM factorized rebinding | (redirect to unseen-relation question instead) | n/a for THIS metric | 0.15 |

All P values deflated 0.15-0.25 from a naive base rate per the standing lit-scan calibration discipline; none exceed
the 0.50 novel-synthesis cap.

---

## Cross-thread synthesis

- **Directly resolves the calibration gap left open by** `research_inductive_entity_generalizing_factorized_map_
  builder_2026-07-12.md`, which designed and predicted the mechanism (P=0.30 for HARD-PASS at the time) but did not
  yet have a landed number to calibrate against literature — that gate has now cleared (`HARD_PASS_INDUCTIVE_ANCHOR_
  COMPOSE`, both v1 and v2 identity-closed), and this drill supplies the "how good is 0.128 MRR, really" answer that
  drill explicitly deferred.
- **Directly reuses and extends the triple-confirmed capacity law** from the same prior drill (GrapHD SNR~5log(D/d) =
  KGE rank-bottleneck theory = hippocampal CA3 capacity law) — this drill's Lever 3 analysis is the first place that
  law is applied as a HARD GATING CONSTRAINT on a candidate uplift lever, not just a sizing footnote.
- **Connects to the standing relational-capability program spine** (`project_relational_capability_is_the_core_
  requirement_make_it_real_USER_2026-07-10.md`): Lever 6's deprioritization is itself informative for THAT thread —
  it clarifies that grid-cell/TEM-style structural generalization is the right tool for the UNSEEN-RELATION problem,
  not the held-out-ENTITY magnitude problem this drill addresses, sharpening which brain mechanism maps to which open
  capability gap rather than treating "brain-grounded" as one undifferentiated bucket.
- **New fact this drill adds that no sibling note surfaced:** the sequential-vs-parallel resonator decoding 8x figure
  (arXiv:2412.00354) as a DIRECT, quantified precedent for iterative peeling on bundled/superposed VSA codes — this
  is citable and load-bearing for any FUTURE cell that bundles multiple bind-terms into one composite vector across
  the substrate, not just this one.
- **Awaiting, not duplicating:** `anchor_compose_scaling_ladder_cskg_v3` (dispatched 2026-07-13 08:01, not yet
  landed as of this drill) already probes an adjacent scaling axis (k12/sf.50 -> sf.25 -> k8/bigN per the dispatch
  log) — Lever 3's build should read that landed result before committing further compute, per this drill's own
  "bigger build, gated" recommendation.

---

## Substrate-product implications

- **The honest, defensible product claim right now:** "we have a zero-gradient-training, glass-box mechanism for
  representing knowledge-graph entities never seen at training time, and its accuracy is already in the same ballpark
  as trained-encoder methods on the closest published commonsense-KG comparison (ConceptNet), not merely 'better than
  random.'" This is a materially stronger and more specific claim than "the mechanism works" alone — it is now
  calibrated against an external, defensible reference class.
- **If Lever 1 and/or 2 HARD-PASS:** the mechanism would cross into "matches commonsense-KG-SOTA despite zero training
  for new entities" territory — a genuine product differentiator (competitors' inductive methods all require a
  trained forward pass; ours would match their accuracy with none), not just a research curiosity.
- **If both HARD-FAIL:** still valuable and informative, not a dead end — it would mean the wall is specifically in
  bundle SIZE (too few anchor-edges per typical held-out entity to give iterative peeling material to work with) or
  scorer calibration is already adequate, redirecting cleanly to Lever 3 (bigger bundles, degree-ceiling-gated) as the
  next and more expensive move, rather than leaving "0.128 MRR, unclear why" as an unlocalized number.
- **Scope discipline, restated from the prior drill:** none of these levers address CSKG's own schema-blurred relation
  semantics (a knowledge-richness limit, not an architecture limit, per `research_kg_degree_community_diagnostic_2026-
  07-12.md`) — closing fully to the curated-ontology SOTA band (MRR 0.44-0.73) would need a different, harder fix on
  a different axis, and this drill's target band (MRR 0.18-0.22) is deliberately scoped to what an architecture-only
  fix can plausibly reach.

---

## Citations (verified count)

**On-disk, read in full this cycle:** `data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json` (landed
verdict + full metric spectrum); `data/exp_anchor_compose_identity_shuffle_cskg_v2/metrics.json` (identity-leak
closure verdict); `data/orchestrator_status_log.jsonl` (dispatch history for v1/v2/v3); `notes/research_inductive_
entity_generalizing_factorized_map_builder_2026-07-12.md` (mechanism design + GrapHD SNR law + prior citations).
**4 on-disk sources.**

**External literature (3 parallel Sonnet lit-scans, generic ML/neuroscience terms only, no substrate-novel names/
configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*Inductive-KGE benchmark calibration (10):* Zhu et al. (NBFNet, NeurIPS 2021, arXiv:2106.06935); Zhu et al. (A*Net,
2023, arXiv:2206.04798); Teru, Denis, Hamilton (GraIL, ICML 2020, arXiv:1911.06962); Zhang & Yao (RED-GNN, WebConf
2022, arXiv:2108.06040); Galkin et al. (NodePiece, ICLR 2022, arXiv:2106.12144); Galkin et al. (ULTRA, ICLR 2024,
arXiv:2310.04562); Wang et al. (InductivE, IJCNN 2021, arXiv:2009.09263); Malaviya, Bhagavatula, Bosselut, Choi
(commonsense KB completion baseline, AAAI 2020, arXiv:1910.02915); Hwang et al. (ATOMIC 2020, AAAI 2021,
arXiv:2010.05953); Ilievski, Szekely, Zhang (CSKG, ESWC 2021).

*Brain cleanup/aggregation mechanisms (14):* Treves & Rolls (CA3 capacity theory, Network 1994); Krotov & Hopfield
(Dense Associative Memory, arXiv:1606.01164); Demircigil et al. (exponential-capacity modern Hopfield, 2017);
Ramsauer et al. (Hopfield Networks is All You Need, 2020); Wyatte et al. (recurrent pattern completion, PNAS,
PMC6126774); Franks/Bolding (piriform recurrent circuitry, biorxiv); Rolls (pattern completion/separation review,
PMC3812781); Leutgeb et al. (DG rate remapping, 2007; Cell Reports 2023 follow-up); Babadi & Sompolinsky (sparse
expansion recoding, Neuron 2014); Cayco-Gajic & Silver (cerebellar granule-cell decorrelation, Nat Commun);
Whittington, Muller, Barry, Behrens et al. (TEM, Cell 2020); Lisman & Idiart (theta-gamma WM model, Science 1995);
Kaminski et al. (theta-gamma phase-phase coupling, 2015); Salvatori et al. (predictive-coding associative memory,
arXiv:2109.08063); Tang et al. (recurrent predictive coding, PMC10132551); Karunaratne, Hersche, Sebastian, Rahimi
(sequential vs. parallel resonator decoding, arXiv:2412.00354).

*Field aggregation/iterative-refinement magnitude ablations (9):* GraphSAGE vs. GAT link-prediction ablations
(PMC12225800; ResearchGate 376815287); RRA-GAT (ACM 2024, WN18RR MRR ablation); "When Design Rules Break" (24-dataset
aggregation ablation, arXiv:2606.10249); OGB leaderboard GraphSAGE-mean vs. GCN (ogbl-collab, ogbl-ddi); GA-S2S
(1-hop/2-hop MRR ablation, arXiv:2605.18211); k-hop GNN literature synthesis; over-smoothing/over-squashing survey
(SciOpen 2023); Sun et al. (RotatE self-adversarial negative sampling, arXiv:1902.10197); MixKG (hard-negative
mixing, arXiv:2202.09606); InCL-KGC (contrastive hard-negative KGE, arXiv:2510.11868); Ihler, Fisher, Willsky
(loopy BP convergence, JMLR 2005).

**Total: 4 on-disk sources + 33 external sources across 3 parallel lit-scans = 37 verified checks.**

---

## Intuitive summary

**The question:** we just proved a way for our knowledge-graph system to instantly build a usable description of a
brand-new concept it has never seen, using zero training — just quick arithmetic over how the new concept connects to
familiar landmarks. But the accuracy of that instant description (correct answer in the top 10 guesses about 28% of
the time) is objectively low on its own. Is that actually bad, or is it about where it should be given how hard the
task is and that no training was used at all?

**What we found on calibration:** we compared against the closest real-world precedent we could find — other systems
that also try to handle brand-new concepts on messy, real-world "common sense" knowledge graphs (not clean textbook
databases). Those systems, even though they DO use extensive training, land in a similar range to ours on the
commonsense-style graphs, and often do far worse on the largest, messiest ones. Our zero-training result is
respectably close to the bottom of that band, not embarrassingly far below it. There's a much higher-scoring
benchmark family out there (some systems score 3-5x higher), but that family uses cleanly-labeled, unambiguous
relationship types — a different and easier kind of graph than the noisy, overlapping "commonsense" relationships
ours has to work with. Comparing against that family would be an unfair, apples-to-oranges target.

**What we found on how to improve it, brain-first:** the most promising fix mirrors something the brain does when
holding several things in mind at once — rather than blending everything together in one flat average and reading it
once, take the strongest, most confident piece first, "peel it off," and then re-examine what's left, repeating a few
times. This mirrors both a memory mechanism (the brain checking and re-checking a noisy memory trace rather than
reading it in one shot) and a mathematical technique from signal processing that our system already has a working
version of — we would just need to run it more than once per lookup instead of once. A second, equally promising and
completely independent fix doesn't touch the new-concept mechanism at all — it just makes the underlying "how well do
we score candidate answers" function pickier during its normal training, a small, well-proven training tweak.

**The honest caveat, and the trap we specifically avoided:** the field's numbers are riddled with an apples-to-oranges
trap where two very different difficulty levels of the SAME-NAMED test get compared as if they were equivalent, making
some systems look 2x better than they really are on a fair footing. We made sure to only compare our number against
the numbers using the SAME, harder testing rule ours uses. We also flagged, honestly, that our biggest single possible
improvement (letting a new concept "look" two steps away instead of just one) comes with a real mathematical catch: it
can backfire unless we also make our internal number-storage roomier at the same time, because cramming in more
information without more room causes it to blur together — exactly the same tradeoff a brain faces when trying to
remember more things without enough neurons to keep them separate.
