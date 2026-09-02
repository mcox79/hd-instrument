# Measured findings (smoke = 4 SemCor files, 2658 polysemous items, 696 subordinate; full 30-file run pending)

All numbers glass-box, LM-free at inference, deterministic. Reused organs: `_settle` competitive attractor
settling, `hdlab/semantic_control` LIFG signed suppression, `_sense_prior` reordered-access frequency prior,
grounded WordNet++ (cn_syn) graph. Cell: `experiments/exp_topdown_situation_sense_selector_v1.py`.

## 1. The DETECTOR works — and it CONTRADICTS the brief's "AUC ~0.51" (disk outranks brief)
Gold-blind when-to-suppress detector = a conflict/prediction-error signal over the target's senses. AUC at
separating subordinate (suppress-me) from dominant, on struct-covered items (n=2009, 522 sub):
- BAG symmetric conflict: **0.678**
- STRUCT (dependency governor+co-args+modifiers) symmetric conflict: **0.712** (frequency-independent signal beats bag)
- **STRUCT directional `domI` (1 - dominant_coherence = N400 prediction error on the DOMINANT reading): 0.737** (best)
- BAG directional domI: 0.733
The brief/parent §D claimed "no gold-blind detector exists (all AUC ~0.51)". On THIS setup (settling coherence
over the grounded graph, SemCor) the detector is clearly real (0.68-0.74). WALL-1 CONFIRMED: the DIRECTIONAL
predictive-error detector (N400-on-the-dominant) beats symmetric conflict — the brain-faithful improvement predicted.

## 2. The info-free control LOSES (the structural signal is real)
At matched fire-count (q=0.70, 603 fired): REAL structure recovers subordinate **0.1724** vs shuffled-structure
twin **0.0733** (+0.099) at similar dominant cost. Structure beats bag at every operating point.

## 3. Discourse aggregation DILUTES (a real, brain-relevant negative)
Pooling the entity's structural role-history across all same-(doc,lemma) mentions (coref-by-repetition proxy,
~20x more neighbours, 71% of items multi-mention) gives a WORSE detector: DISC AUC **0.635** < struct 0.712.
Reason: an entity appears in DIFFERENT roles/senses across a document, so naive pooling mixes sense-specific
contexts. Sentence-local structure is the better (if sparse: 1.49 neighbours/item) sense signal. => The situation
signal that helps is the LOCAL predicate-argument structure, not a flat discourse aggregate (echoes the parent's
proto4b "flat discourse is redundant"; here structured-but-pooled also dilutes).

## 4. THE WALL: a BASE-RATE see-saw. No gated config nets a CI-separated gain on the full population.
prior_floor (MFS) = overall 0.7291, **dominant 0.9878**, subordinate 0.0 (MFS wrong on subordinate by construction).
Subordinate = 26% of items. Best full-population net over MFS across ALL detector/override/threshold combos:
**~0.000** (disc:sym +0.0004; struct:domI -0.001; all null). Large SUBORDINATE recovery (+0.14 to +0.18) and
COARSE/homonym recovery (+0.18 to +0.22) are REAL but bought with dominant loss.

## 5. WALL DECOMPOSITION — exactly how we differ from the brain (quantified)
net = fired * [ p*a_s - (1-p)*c_d ], measured on the fired set (det=struct:domI, ov=bag):
| q | fired | p (detector precision) | a_s (override acc on fired-sub) | c_d (dominant disruption) | need p*a_s> | got | net |
|---|---|---|---|---|---|---|---|
| 0.85 | 302 | 0.507 | 0.340 | 0.564 | 0.278 | 0.172 | -0.010 |
| 0.95 | 101 | 0.485 | 0.388 | 0.577 | 0.297 | 0.188 | -0.003 |
| 0.98 |  35 | 0.371 | 0.538 | 0.545 | 0.343 | 0.200 | -0.001 |
THREE quantified fidelity gaps vs the brain:
- **p ≈ 0.5** (detector fires ~coin-flip subordinate). Brain: a sharp situational constraint.
- **a_s ≈ 0.35** (even when we correctly detect, we pick the RIGHT subordinate sense ~35%). Brain: predicts the
  SPECIFIC sense from world knowledge. THIS is the binding limit — the "which sense" problem = comprehension.
- **c_d ≈ 0.56** (we disrupt dominant when we fire there). Brain asymmetry: dominant needs NO inhibition -> c_d≈0.
Break-even needs p*a_s ~0.28-0.34; we get ~0.17-0.20 -> must roughly DOUBLE detector-precision x override-accuracy.
A maximally-conservative override (fire only on a specific+strong competitor: margin/abs thresholds) does NOT
lower c_d enough (net stays -0.005 to -0.018). => the wall is NOT a threshold-tuning problem.

## VERDICT (pending research drill + full-run CIs)
The wall is a QUANTIFIED FIDELITY GAP, not a fundamental impossibility: detector-precision and override-accuracy
both fall ~2x short of break-even, and both are capped by the RICHNESS of the top-down prediction. Our predictor
is a bag/graph spreading-activation signal; the brain's is a generative world-knowledge situation model that makes
high-precision, sense-SPECIFIC predictions (activates unmentioned scripts/schemas). The brain-faithful direction is
CONFIRMED at every step (frequency-independent structural signal > bag; directional N400 detector > symmetric;
info-free twin loses), but the magnitude needs the North-Star comprehension/situation model. Open: how much of the
a_s≈0.35 cap is genuine task difficulty (human inter-annotator ceiling) vs our fidelity gap — the research drill answers this.
