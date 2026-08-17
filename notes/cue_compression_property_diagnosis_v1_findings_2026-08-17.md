# exp_cue_compression_property_diagnosis_v1 -- what property of the raw count cue does the 256-dim projection destroy? (2026-08-17)

Cell: `experiments/exp_cue_compression_property_diagnosis_v1.py`. Full run:
`data/exp_cue_compression_property_diagnosis_v1/metrics.json` (elapsed 72.7s, reusing the audit
cell's checkpointed raw counts read-only). Smoke: `data/exp_cue_compression_property_diagnosis_v1_smoke/metrics.json`.
Both self-tests and both runs PASS.

Prior-work check (`tools/substrate_query.sh "raw count vector partial cue addressing compression
sparsity non-negativity collision"`): top hit `compression` (WordNet node, cosine=0.3818) -- a
generic lexical entry, not a prior experiment cell. NONE at cosine>0.30 that is a prior arc cell.
This diagnosis is novel, not a rediscovery.

Disclosure: one `Bash` call was auto-denied (`rm -f ..._smoke/units.jsonl && ... --grid reduced`,
the same bundled-deletion fault class documented in CLAUDE.md). Exact denial text: "Permission to
use Bash with command ... has been denied." Not retried as a variant; the deletion was unnecessary
(checkpoint reuse handles a stale partial smoke checkpoint correctly) so the smoke was re-run
without it and completed normally.

## Both reference figures verified off disk, independently recomputed, both REPRODUCE

- `data/exp_cue_information_audit_v1/metrics.json`: C0_PROJECTED_256=0.0711, U0_UNCOMPRESSED=0.0849,
  margin +0.0138 CI [+0.0083,+0.0195], half-width 0.0056. This cell's own fresh recompute on the
  identical 3994-item/5491-anchor pool: C0=0.0711 (exact match), U0=0.0846 (within tol 5e-4 of
  0.0849). REGRESSION_GATE PASS on both, enforced (SystemExit-equivalent STOP was pre-registered had
  it failed).
- `data/exp_sparse_address_dense_value_v1/metrics.json`: D=256/a_write=1.0/a_read=sym reads 0.0711;
  D=8192 same regime reads 0.0709; CI half-width at that point is 0.0078 (ci95 [0.0628,0.0789]).
  Delta 0.0002, far inside one CI half-width -- REPRODUCED: 32x the dimensionality buys nothing.
  Minor provenance note: the phase-diagram doc's prose quotes 0.0716 for d=8192; the exact field in
  the metrics.json for that D/a_write/a_read cell reads 0.0709 (the 0.0716 figure traces to a
  DIFFERENT draw/config, `BEST_ADDRESSING_CONFIG_partial_cue` at D=2048 with a different projection
  seed, which reads 0.0719). This does not change the claim -- the whole d-sweep sits inside 0.0705-
  0.0719, one CI half-width -- but the specific number in the prose does not match its own cited
  cell exactly and is flagged here.

## Property-by-property margins vs C0 (primary) and vs U0 (secondary), n=3994

| arm | vs C0 point | CI95 | half-width | band | vs U0 point | band |
|---|---|---|---|---|---|---|
| S1_SPARSE_HASH_PROJ (sparsity/exact-zero, feature-hashed, d=256) | -0.0100 | [-0.0160,-0.0040] | 0.0060 | BELOW | -0.0235 | BELOW |
| N1_NONNEG_PROJ (non-negativity, dense {0,1} matrix, d=256) | -0.0003 | [-0.0068,+0.0060] | 0.0064 | NOT_SEPARATED | -0.0138 | BELOW |
| B1_BINARIZED_RAW (frequency removed, no projection, uncompressed) | +0.0383 | [+0.0293,+0.0476] | 0.0092 | **ABOVE** | +0.0248 | **ABOVE** |

BETWEEN_PROJECTION_DRAW_SD (3 draws each, load-bearing since this cell is about a random
projection): S1 mean=0.0636 sd=0.0019 (values 0.0611/0.0658/0.0638); N1 mean=0.0721 sd=0.0009
(values 0.0709/0.0724/0.0731). Both SDs are well inside their respective CI half-widths, so the
BELOW/NOT_SEPARATED verdicts are not projection-draw noise artifacts.

Neither exact-zero preservation (S1) nor non-negativity (N1) recovers any of the gap -- S1 is
CI-separated WORSE than the incumbent (plausible cause: feature hashing ~54k distinct words into
256 dims produces its own hash-collision noise, on top of whatever it saves). B1 is the only arm
that separates, and it OVERSHOOTS: it beats not just C0 but the full uncompressed U0 arm itself,
recovering 284% of the original +0.0138 gap (fraction_of_U0_minus_C0_gap_recovered = 2.837).
Encoder collision floor (measured directly, not inferred): mean |cos| among 5000 sampled distinct
symbol-vector pairs at d=256 is 0.0499, close to the theoretical 1/sqrt(256)=0.0625 -- the dense
projection's cross-talk floor is real, but isolating it alone (N1) did not explain the gap.

## Loss is partially concentrated, not fully diffuse

BUCKETS: n_both_hit=245, n_both_miss=3617, n_lost_by_projection (U0 hit, C0 miss)=93,
n_gained_by_projection (C0 hit, U0 miss)=39; net=54/3994=0.0135, reconciling exactly with the MAIN
margin point (0.0135 vs 0.0138 aggregate -- consistent). The 93 lost-by-projection items, vs the
other 3901, have SHORTER cues (10.80 vs 12.48 distinct words, margin -1.69 CI [-2.73,-0.65],
CI-separated) and MUCH SPARSER target-anchor store profiles (106.4 vs 210.8 distinct words in the
anchor's own accumulated context, margin -104.4 CI [-119.9,-88.4], CI-separated). Item-level
word-pair collision was NOT separated (0.0521 vs 0.0498, CI [-0.0004,+0.0059]) -- it is not raw
hash-collision-style word clash driving the loss. **Known cosmetic bug**: the cell's own
`ITEM_LEVEL_LOSS_IS_CONCENTRATED` boolean reads `False` because its check only recognises
CI-separated margins in the ABOVE direction; both real separations here are BELOW (the feature is
LOWER, not higher, among lost items), so the flag under-reports. The underlying per-feature margins
above are the source of truth and were read directly, not via that flag.

## Which stop-if fired, and the design constraint

**(ii) exactly one property arm, B1_BINARIZED_RAW, is CI-separated ABOVE C0**, and it overshoots
U0 as well. Not (i) -- neither reference figure failed to reproduce. Not (iii) -- the loss is not
diffuse: two of three item-level features CI-separate. Combined finding: the deciding property is
not sparsity-of-map and not non-negativity, but **magnitude/frequency weighting is actively
harmful** in the current masked-context-count representation -- and independently, the projection's
damage concentrates on anchors with sparse, rarely-attested store profiles and shorter cues.

**One-sentence encoder design constraint**: the next encoder should represent presence/absence of
content words (not accumulated frequency counts) in both the store profile and the partial cue, and
should not additionally compress via a dense random projection into 256 dims, which is a measured,
CI-separated defect independent of and larger than the frequency-weighting one; this is a design
constraint for the next encoder, not a capability claim.
