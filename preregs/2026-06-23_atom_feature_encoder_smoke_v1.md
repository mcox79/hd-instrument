# Pre-reg: atom_feature_encoder_smoke_v1

Date: 2026-06-23
Anchor: `atom_feature_encoder_smoke_v1`
Cell: `experiments/exp_atom_feature_encoder_smoke_v1.py`
Queue: `local_cpu_queue` (smoke+full bundled; CPU; numpy-only; expected wall < 10 min)

## Motivation (USER reframe 2026-06-23)

char-trigram encoder spells ALL substrate data types (atoms, entities, relations,
capabilities) by their NAME. Two atoms with same FUNCTION but different names do
not cluster; two atoms with similar names but different functions DO cluster
(wrong direction for self-mapping). Gap 2 (substrate_self_map) keeps producing
weak / mechanism-null clusters because the atom encoder is keyed on the name
string, not on what the atom DOES.

Cheap MVP: encode atoms by their FEATURES (cert_tier + mechanism_family +
sigma_regime + metric_profile + graph_neighborhood) and test whether
mechanism-family-purity of k-means clusters lifts vs the char-trigram baseline.
If HARD_PASS, this is the right direction for Gap 2 (self-mapping).

## Design

For each chain-grade atom (sample N=100 from data/substrate_index/math/atoms.jsonl
joined to data/substrate_index/meta/cert_ledger.jsonl):

- `ARM_CHAR_TRIGRAM_NAME` (baseline): encode `atom_id` via
  `hdlab.char_trigram_encoder.CharTrigramEncoder` (current substrate).
- `ARM_ATOM_FEATURE` (new): bind
  - cert_tier_vec (chain_grade / measured_mechanism / honest_negative / other)
  - mechanism_family_vec (10 fixed families via keyword-substring match on name)
  - sigma_regime_vec (4 bins; sigma extracted from atom metadata if present;
    "sigma_unknown" otherwise)
  - metric_profile_vec (hash of verdict_prefix + cv_bucket + cert_increment_delta)
  - graph_neighborhood_vec (bundle of bipolar HVs for composes / typed_by /
    serves_capability / algebra fields; sign-bundled)
  - final: `sign(cert + family + sigma + metric + nbr_bundle)`

Discriminator: k-means K=10 on N=100 atoms in each arm. Compute mechanism-family
purity per cluster (modal-family fraction); weighted average across clusters.

Sanity self-test (PRE-DISPATCH): planted 3-atom block with IDENTICAL features
differing only by mechanism keyword in name. atom_feature should put each in
its own correct mechanism cluster (purity == 1.0).

## Pre-reg bands

HARD_PASS:
- `ARM_ATOM_FEATURE.mechanism_family_purity >= 0.60`
- AND `ARM_ATOM_FEATURE.purity >= ARM_CHAR_TRIGRAM_NAME.purity + 0.15`
- AND `planted_block_purity == 1.0`
- AND substrate-only-decode preserved (`n_llm_calls == 0`)

HARD_FAIL:
- `ARM_ATOM_FEATURE.purity <= ARM_CHAR_TRIGRAM_NAME.purity`
  (feature-encoding adds nothing or hurts)
- OR substrate-only-decode violated

MIDDLE_BAND:
- Positive lift but below HARD_PASS threshold (mechanism present, weak)

## By-construction-saturation note

Chain-grade atom names usually CONTAIN the mechanism keyword (cleanup, storage,
generation, etc.) by naming convention. So the char-trigram baseline may already
score high on mechanism-family-purity — not because trigrams capture function
but because the name string literally contains the family token. This is the
exact failure mode the USER reframe is calling out: char-trigram "works" on
chain-grade only because the family keyword leaks into the name; on
real cross-domain atoms (entities, relations, capabilities) it would NOT work.

If the smoke shows the baseline saturates near 1.0 on chain-grade atoms,
escalating to FULL with K=10/N=100 is still informative: a wider K + larger N
gives mechanism families their own granular clusters; baseline saturation will
either persist (confirms the by-construction lexical leak; we adjust the test by
either sampling cross-corpus atoms OR by stripping mechanism keywords from atom
names before encoding) or differentiate.

## Implementation

- N_DIM=4096 (FULL), K=10, N=100 chain-grade atoms; seeds=[7, 17, 23]
- Smoke: N_DIM=1024, K=5, N=30, seeds=[7]
- numpy-only k-means (Lloyd's); cosine-normalized rows
- Cell-local atom_feature encoder; promote to `hdlab/atom_feature_encoder.py`
  only if HARD_PASS
- Per-seed checkpoint via `experiments/_seed_checkpoint`
- ASCII-only; no emojis; no em-dashes

## Smoke gate result (PRE-DISPATCH)

Run `HDLAB_EXP_NAME=atom_feature_encoder_smoke_v1_smoke .venv/Scripts/python.exe
experiments/exp_atom_feature_encoder_smoke_v1.py --smoke`:

- `[selftest] PASS: feat=1.000 trig=1.000 n_llm_calls=0`
- N=30 sampled atoms, K=5, N_DIM=1024, seed=7
- `arm_atom_feature_purity = 1.000`
- `arm_char_trigram_purity = 0.967`
- `purity_lift = +0.033`
- `planted_block_purity = 1.000`
- `n_llm_calls = 0`
- elapsed = 0.03s
- verdict = MIDDLE_BAND (smoke; expected since char-trigram baseline saturates
  on chain-grade due to mechanism keyword in name; FULL with K=10/N=100 will
  give the discriminating gap if mechanism is genuinely separable)
- REQUIRED_FIELDS schema PASSED

## Expected FULL behavior

- If FULL_lift >= 0.15: HARD_PASS direction confirmed; promote atom_feature
  encoder to `hdlab/` + queue a v2 with cross-corpus atoms + name-stripped
  control arm.
- If FULL_lift < 0.15 but feat_purity >= trig_purity: MIDDLE_BAND, by-construction
  saturation likely; queue a v2 with name-stripped baseline (the honest
  discriminator) and broader atom pool.
- If feat <= trig: HARD_FAIL, signal that mechanism-family is leaking into name
  enough that even feature-binding doesn't help at this scale.

## Self-test command

```
HDLAB_EXP_NAME=atom_feature_encoder_smoke_v1_smoke .venv/Scripts/python.exe \
  experiments/exp_atom_feature_encoder_smoke_v1.py --self-test
```
