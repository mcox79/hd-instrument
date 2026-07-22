# Pre-reg: relational_vs_similarity_conflict_viability_probe_v1

Filed 2026-07-22 (bands registered BEFORE the full 5-seed run). LOCAL-ONLY viability probe.
Cell: `experiments/exp_relational_vs_similarity_conflict_viability_probe_v1.py`
Metrics: `data/exp_relational_vs_similarity_conflict_viability_probe_v1/metrics.json`

## Question (viability gate before the fork-A build)

The learned-composition leap (atom 29440) was REFUTED: the LINEAR atomize+sleep loop reduces
analytically to a fixed WordNet-hypernym similarity vote (parameter-free similarity-kNN matched it
70/70). Brain-check `notes/research_drill_does_brain_composition_beat_semantic_similarity_2026-07-22.md`
confirmed the CG bar is BRAIN-FAITHFUL: humans generalize composition to SEMANTICALLY-DISSIMILAR novel
combinations (Marcus 1999 infant ABA/ABB where similarity-nets fail; Berko wug; Lake-Baroni meaning-
free primitives; Gentner relational-shift). A linear associative matrix is a kernel machine (emits only
weighted-similarity outputs) -- the exact reason 29440 collapsed to kNN.

VIABILITY QUESTION: on a relational-vs-similarity CONFLICT corpus (where a similarity-kNN provably
fails by construction), does ANY glass-box NONLINEAR mechanism (role-binding + unbind-compare
coherence gate) BEAT the similarity-kNN? PASS -> green-light the full fork-A build. FAIL -> fork A
needs a genuinely different mechanism.

## Design-gate compliance

- REAL baseline: raw-similarity-kNN (1-NN over raw item vectors), the model to beat.
- CAN-FAIL: the nonlinear loop might ALSO reduce to similarity / not beat kNN (crosstalk-limited, or
  the readout latches an uninformative feature); the WRONG-ROLE must-fail must collapse or the signal
  is an artifact. Both are honest + a-priori plausible failure modes.
- DIFFICULTY-ON: TRAIN and HELD-OUT use DISJOINT filler pools (novel/orthogonal fillers) so surface
  similarity is provably useless on held-out; class = a filler-independent relational identity.
- ONE VARIABLE: mechanism (A raw-kNN / B linear-loop / C nonlinear-glassbox / D kNN-on-relational).

## Corpus (PART 2, decisive)

4-slot role-filler bundles, 4 distinct fillers per item; class = WHERE the one matched (repeated)
filler pair sits: class0 = match at roles (r0,r1) -> (a,a,b,c); class1 = match at (r2,r3) -> (a,b,c,c).
STRUCTURALLY SYMMETRIC (both classes have exactly one doubled pair + two singletons) so a raw-vector
kNN has no magnitude/energy fingerprint and sits at/near chance. N_DIM=1024 (HRR), 120 train + 120
held-out items, 20+20 disjoint fillers, 5 seeds {7,13,19,23,29}. Balanced 2-class -> chance = 0.50.

## Arms

- A RAW-SIMILARITY-kNN -- 1-NN over raw item vectors vs TRAIN. BASELINE to beat; fails by construction.
- B LINEAR-LOOP (29440) -- `replay_cycle` W over item vectors -> class readout (UNMODIFIED machinery).
- C NONLINEAR-GLASSBOX -- role-binding + unbind-compare coherence gate s_ij = cos(unbind_i,unbind_j)
  (a QUADRATIC/nonlinear, filler-independent form a linear/kernel loop cannot compute) -> LEARNED
  inspectable 6-weight logistic readout. THE PRIZE. (Multi-step codebook-free settling run as an
  ABLATION; it degrades and is reported, not primary.)
- D kNN-ON-RELATIONAL -- 1-NN over the SAME relational features, no learning. Attribution control.
- C-wrongrole (MUST-FAIL gate) -- unbind-compare with roles never used in the binding -> destroys the
  role-binding structure -> readout must collapse toward chance.
- C-scramble (INFORMATIONAL, not a gate) -- permuted train labels; because the relational features are
  two cleanly-separated blobs, GD recovers the true split regardless of labels (only the SIGN is
  label-set) -> acc is binary ~0/~1, NOT 0.5. Signature of near-label-free separability.

## Pre-registered bands (multi-seed means)

- CHANCE = 0.50
- KNN_CEIL = 0.65   (raw-kNN mean MUST be <= this; else HARD_FAIL_CORPUS_LEAK: baseline not failing)
- LINEAR_CEIL = 0.65 (linear-loop mean MUST be <= this)
- NONLINEAR_PASS_MEAN = 0.75 (C mean HARD-PASS floor)
- NONLINEAR_MARGIN = 0.20   (C - rawKNN mean; the "beat similarity" bar)
- NONLINEAR_EVERYSEED_MIN = 0.65 (every seed's C)
- WRONGROLE_CEIL = 0.65 ; WRONGROLE_COLLAPSE_MIN = 0.20 (C - C_wrongrole)
- NONLINEAR_FAIL_MAX = 0.62 (C mean at/below -> reduces to similarity -> HARD-FAIL)

HARD_PASS_VIABILITY = arms_differ + weights_nondegenerate + not corpus_leak + rawKNN<=KNN_CEIL +
linear<=LINEAR_CEIL + C>=NONLINEAR_PASS_MEAN + margin>=NONLINEAR_MARGIN + everyseed_C + wrong-role
collapses. HARD_FAIL_VIABILITY = C<=NONLINEAR_FAIL_MAX OR margin<NONLINEAR_MARGIN OR wrong-role does
NOT collapse OR arms identical/weights degenerate.

## PART 1 real-data feasibility diagnostic

Reuse the 29440 verb->required-feature setup + the SAME WordNet-hypernym verb-similarity code
(verb_code_real). For each held-out verb, is the nearest-similar TRAIN verb's feature != the held-out
true feature (a conflict)? Predicted ~0 conflict items because the 29440 rule is a similarity-CLASS
rule (similarity and rule co-extensive) -> a real-data conflict corpus is NOT buildable in this
testbed (which is WHY 29440 reduced to kNN). If conflict count < 10, fall back to the synthetic test.

## Cell-template mandates

arms_differ asserted; final_metrics_atomicity = tmp_replace; `except SystemExit: raise` before
`except Exception` (no BaseException); crlb_n/a (floor is HRR binding-crosstalk, reported as held-out
s01 class separation, not an argmax-capacity CRLB); baseline_in_band verified (raw-kNN ~0.5);
deterministic seeding (fixed ints + hashlib atoms, no hash()/list(set())); progress_logging flush;
cardinality_ok (n_seed_rows == len(seeds)); discriminator survives scale (smoke == FULL N_DIM=1024 +
full item counts, option A). Compute: sequential-CPU, ~10s, no storage. LOCAL ONLY -- no push / no
remote-persist / no queue / no store write / no atom bank.

## Honest scope

A synthetic HARD-PASS is CONSTRUCTION-FAVORABLE: it proves an EXISTENCE result (the substrate's role-
binding primitive CAN express a filler-independent relational feature that a linear/kernel similarity
loop cannot), NOT that the mechanism learns the RIGHT relational feature from HARD/REAL data. It is a
GREEN-LIGHT-PENDING-VET for fork A, never a self-declared CG. Arm D is included to attribute the lever
(representation vs learning); a pass requires fresh adversarial VET (kNN-identity attack over the
relational features) + a real-text attested-combo test before any CG claim.
