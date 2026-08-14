# AMENDMENT A1 to `preregs/2026-08-13_task_local_normalisation_pool.md`

Filed 2026-08-14, **BEFORE any arm of the cell has been scored on real data** and before the cell
has been smoked. The base pre-registration is committed at `e07d8ffb3`. This amendment exists
because the base pre-reg contains a MATHEMATICAL ERROR THAT I MADE, found by the cell's own
self-test, and correcting it changes which arm is primary.

## 1. THE ERROR

The base pre-reg (and `notes/comparator_component_fidelity_audit_2026-08-13.md` row C1) cite
Carandini & Heeger 2012 (*Nat Rev Neurosci* 13:51-62) for the operation

    r_i = x_i^n / (sigma^n + SUM_{j in pool} x_j^n)

and I then implemented "the pool" as a PER-DIMENSION statistic across a population of concepts.
**That is not what the cited equation says.** In Carandini & Heeger the pool index `j` ranges over
OTHER NEURONS IN THE SAME POPULATION at the same moment, so the denominator is a **SCALAR for the
whole representation**, identical for every component of `x`. Two consequences follow immediately
and neither was noticed when the base pre-reg was written:

1. **Canonical divisive normalisation is a scalar rescale, and cosine is invariant to a scalar
   rescale. In its true form it CANNOT change a two-candidate argmax at all.** It is not a weak
   effect on this task; it is an identically-zero effect.
2. What I actually implemented and measured in `exp_graded_divisive_comparator_v1` — per-dimension
   mean/sd across the anchor population — is **efficient-coding ADAPTATION** (a neuron setting its
   gain from its own response distribution; Laughlin 1981; Fairhall et al. 2001), a different and
   also-real mechanism. It was measured NULL (+0.0018, CI [-0.0030,+0.0065]).

So the predecessor's null is now explained twice over, and the base pre-reg's proposed fix
inherited the same confusion: `g_j = 1/(sigma + |a_j| + |b_j|)` is a per-dimension transposition of
a scalar operation, and it has a specific pathology. **It assigns the LARGEST gain to the dimensions
where BOTH candidates have the least evidence** — dimensions that are noise for both concepts. That
is the same noise-amplification defect the audit convicted `sign()` of, arriving from the other
direction.

**Measured, before any real arm was scored** (the cell's self-test S3, synthetic, d=64, n=300):

| distinctive scale | query noise | pool-inverse gain | plain (no gain) |
|---|---|---|---|
| 0.30 | 0.3 | 300/300 | 300/300 |
| 0.15 | 1.0 | 219/300 | **237/300** |
| 0.15 | 2.0 | 188/300 | **203/300** |
| 0.10 | 2.0 | 178/300 | **190/300** |

The pool-inverse gain LOSES wherever the task is hard enough to discriminate.

## 2. THE CORRECTION, TAKEN FROM THE BIOLOGY AND NOT FROM A RESULT

The C4 mechanism in the audit is **semantic control gain**, not divisive normalisation, and the
literature is specific about what control weights: IFG "dynamically heightens its connectivity with
relevant components of the representation system" — the components RELEVANT TO THE CURRENT TASK
(Chiou & Lambon Ralph 2018 *Cortex*, DCM, F(2,34)=3.86, p=.03). When the task is to tell two
specific concepts apart, the task-relevant dimensions are **the dimensions on which they differ**,
which is also exactly what "distinctive feature" means in Cree/McNorgan/McRae and in Tyler & Moss's
Conceptual Structure Account: a feature present in FEW concepts — here, present in one candidate and
not the other.

    g_j = |a_j - b_j| / mean_j(|a_j - b_j|)        <- CONTROL GAIN, the corrected primary

This has none of the pathology: it is ~0 where the two candidates agree (shared features) AND ~0
where both are absent (joint noise), and large only where they genuinely differ.

## 3. WHAT CHANGES

- **`P_CONTROL` (`g = |a - b|`, mean-normalised) becomes the PRE-DESIGNATED PRIMARY ARM.** It was
  arm `S_DIFF` in the base pre-reg, where it was an ablation with no verdict weight.
- **`P_LOCAL` (`g = 1/(sigma + |a| + |b|)`) is DEMOTED to a scored arm with NO VERDICT WEIGHT.** It
  is retained rather than dropped because the base pre-reg predicted it would win, and a filed
  prediction should be scored and reported, not quietly removed. **Registered prediction: it will
  score at or below `R_BASE`, for the noise-amplification reason above.**
- **`W_WRONGPOOL` is redefined to be the wrong-source control for the NEW primary**: `g = |a' - b'|`
  computed from a DIFFERENT item's candidate pair via the same deterministic derangement, applied to
  this item's comparison. Its role is unchanged and it still OUTRANKS the pass: if the wrong pair's
  gain reproduces the win, the gain is generic and `HARD_FAIL_GENERIC_NOT_TASK_LOCAL` fires.
- **Every band, floor, tolerance and instrumentation gate is UNCHANGED** (`d >= +0.03`, CI excludes
  0, wrong-source control must not reproduce it, `F_SCRAM <= 0.55`, `R_LIVE` 0.6395 +/- 0.02,
  `R_BASE` 0.6997 +/- 0.02). The primary contrast is now `d = acc(P_CONTROL) - acc(R_BASE)`.
- The sigma sweep now applies to the demoted `P_LOCAL` arm only; `P_CONTROL` has **no free
  parameter at all**, which is a strict improvement in falsifiability.

## 4. DISCLOSURE

No arm of this cell has been scored on the real item set. Nothing in this amendment is informed by
any real-data result; it is informed by (a) re-reading the cited equation and finding I had
transposed it, and (b) a synthetic self-test constructed before the run. The base pre-reg is left
in place unedited so the error and its correction are both on the record. The audit note is being
corrected in the same commit, because the same mis-citation appears in its row C1 prescription.
