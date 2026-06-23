# Pre-reg: atom_feature_encoder_PRODUCTION_stripped_v1

Date: 2026-06-23
Anchor: `atom_feature_encoder_PRODUCTION_stripped_v1`
Cell: `experiments/exp_atom_feature_encoder_PRODUCTION_stripped_v1.py`
Queue: `local_cpu_queue` (CPU; numpy + gensim word2vec; expected wall ~10-20min full,
mostly word2vec model load on first call)

## Why (production upgrade of smoke parent)

Parent `atom_feature_encoder_smoke_v1` landed FULL 2026-06-22:
- feat=0.940, trig=0.887, lift=+0.053, planted=1.000, verdict=MIDDLE_BAND
- HP needed lift >= 0.15; missed by ~3x.

Diagnosis (USER 2026-06-23 reframe): the char-trigram baseline is artificially
high because the mechanism keyword (cleanup / storage / generation / etc.)
appears IN THE ATOM_ID STRING by naming convention. char-trigram bag-of-trigrams
trivially captures `_cleanup_`, `_storage_`, `_generation_` substrings and
clusters atoms by name-leak rather than by what they actually do. The "win"
is by-construction-saturation: trig=0.887 reflects keyword presence, not
mechanism representation.

Production fix: ship a NAME-STRIPPED baseline (mechanism keywords replaced by
stable random-hash tokens) so char-trigram has no name-leak boost. Test
substrate-feature encoder against BOTH baselines + compose substrate-feature
with word2vec(description) to add semantic content the substrate feature
cannot encode directly.

## Cell design (4 arms x 3 seeds [7,17,23] x k-means K=10 x N=100 chain-grade atoms x N_DIM=4096)

- `ARM_CHAR_TRIGRAM_NAME_LEAK` — char-trigram over ORIGINAL atom_id; reproduces
  parent baseline; documents name-leak ceiling.
- `ARM_CHAR_TRIGRAM_STRIPPED` — char-trigram over atom_id with every mechanism
  keyword scrubbed via stable hash (`cleanup`, `storage`, ... -> 6-hex tokens).
  This is the honest baseline.
- `ARM_ATOM_FEATURE` — substrate-feature binding (cert_tier + mechanism_family
  + sigma_regime + metric_profile + graph_neighborhood); per parent.
- `ARM_ATOM_FEATURE_PLUS_WORD2VEC_DESC` — atom_feature + word2vec(description)
  encoding bundled via sign. Tests whether semantic content from atom
  descriptions adds the discrimination the substrate-feature cannot supply.

word2vec source: `data/gensim_cache/word2vec-google-news-300/` (already cached
from `encoder_word2vec_substrate_bind_v1`). Per-seed Gaussian projection
300d -> 4096d so word2vec contribution lives in the same HD space as the
substrate-feature HVs and can be sign-bundled.

Description-keyword extraction: lowercased, stopword-stripped, alpha-only,
dedup, capped at 20 tokens, drawn from `description` / `summary` / `note` /
`claim_text` / `name` fields of the atom dict (in priority order; all
concatenated and tokenized).

Discriminator: mechanism-family-purity of k-means K=10 clusters
(modal-family fraction per cluster; weighted average).

Sanity self-test (pre-dispatch): 3-atom planted partition with distinct
mechanism keywords clusters by family (atom_feature purity == 1.0). Same
test as parent; mechanism known sound.

## Pre-reg bands

HARD_PASS (atom-feature + word2vec encoder lifts mechanism-family clustering
on honest baseline; chain-grade-eligible substrate-native atom encoder):
- `ARM_ATOM_FEATURE_PLUS_WORD2VEC_DESC.purity_mean >= 0.75`
- AND `lift_w2v_over_stripped_mean >= 0.20`
- AND `lift_w2v_over_name_leak_mean >= 0.05`
- AND `planted_block_purity_mean == 1.0`
- AND substrate-only-decode preserved (`n_llm_calls == 0`)

HARD_FAIL: `lift_w2v_over_stripped_mean <= 0.05`
  (atom-feature + word2vec doesn't help even on honest baseline -> the
  composition cannot recover mechanism representation; substrate self-mapping
  via atom-feature is a dead direction)
  OR substrate-only-decode violated.

MIDDLE_BAND: positive lift but below HARD_PASS threshold; partial.

## Predispatch verify-the-referent (Fix #26)

Ran `tools/predispatch_check.py atom_feature_encoder_PRODUCTION_stripped`:
- 0 matching prior landings (lookback 30d)
- 0 matching atoms
- RECOMMENDATION: PROCEED
- Distinct from parent: name suffix `_PRODUCTION_stripped_v1` differs;
  4 arms vs 2; honest baseline + word2vec composition both new.

## Implementation

- N_DIM=4096 (FULL), K=10, N=100 chain-grade atoms; seeds=[7, 17, 23]
- Smoke: N_DIM=1024, K=5, N=30, seeds=[7]
- numpy-only k-means (Lloyd's); cosine-normalized rows
- word2vec loaded once per process via gensim downloader; cached in-process
- Per-seed checkpoint via `experiments/_seed_checkpoint`
- ASCII-only; no emojis; no em-dashes

## Smoke timeout sizing

Smoke wall expected ~14-17min (mostly first-call word2vec load ~14min;
4 arms x 30 atoms x 1 seed x K=5 numpy is ~seconds). Override
HDLAB_SMOKE_TIMEOUT_S=1800 (30min ceiling well above 17min smoke + buffer;
< 3600s gate ceiling).

## FULL timeout sizing

FULL wall: word2vec load ~14min (cached after first run on same host) +
3 seeds x 4 arms x 100 atoms x K=10 numpy is ~seconds total. Total ~15-20min
fresh; ~1-2min cached. Use 1800s (30min); well within local_cpu_queue norms.

## Self-test command

```
HDLAB_EXP_NAME=atom_feature_encoder_PRODUCTION_stripped_v1_smoke \
  .venv/Scripts/python.exe \
  experiments/exp_atom_feature_encoder_PRODUCTION_stripped_v1.py --self-test
```

## Smoke gate command

```
HDLAB_EXP_NAME=atom_feature_encoder_PRODUCTION_stripped_v1_smoke \
  HDLAB_SMOKE_TIMEOUT_S=1800 \
  .venv/Scripts/python.exe \
  experiments/exp_atom_feature_encoder_PRODUCTION_stripped_v1.py --smoke
```

## Expected FULL behavior

- HARD_PASS: word2vec_purity >= 0.75 AND lift_over_stripped >= 0.20 AND
  lift_over_name >= 0.05 -> substrate-feature + semantic encoder is the
  honest discriminator; promote ATOM_FEATURE_PLUS_WORD2VEC_DESC encoder to
  `hdlab/` + chain-grade-classification.
- MIDDLE_BAND: partial -- atom-feature helps but doesn't clear chain-grade
  bar; queue v2 with broader description sources OR larger N pool.
- HARD_FAIL: lift_over_stripped <= 0.05 -- substrate-feature + word2vec
  doesn't recover mechanism beyond what name-leak gave for free; the
  atom-feature direction itself is the bottleneck; pivot to text-only
  encoders OR richer per-atom metadata.
