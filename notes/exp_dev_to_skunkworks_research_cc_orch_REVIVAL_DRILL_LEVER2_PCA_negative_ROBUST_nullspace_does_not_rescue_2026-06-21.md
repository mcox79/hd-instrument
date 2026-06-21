# EXP-DEV -> SKUNKWORKS + RESEARCH (revival-drill 2x closeout); cc ORCH: LEVER #2 PCA-negative is ROBUST -- the discardable-null-space hypothesis does NOT rescue it. Brief.

**Revival-drill item** (Skunkworks 2x): "a non-cosine/non-normalized readout where a discardable null-space exists" -- does PCA-dim-selection help THERE? Tested directly.

## Probe: PCA (k=rank+8) vs full-N, across readout x noise-locality (rank16/N512 anisotropic, query-noise sf scaled to norm)
```
                 noise=all-dims        noise=null-space-only (orthogonal to signal)
cosine readout:  PCA delta +0.00..-0.12   PCA delta +0.00..-0.19   (PCA never helps; WORSE at high noise)
raw-dot readout: PCA delta +0.00..-0.14   PCA delta +0.00..-0.19   (same)
```
(delta = selk_recall - full_recall; discrimination only at sf>=5 where full drops below 1.0)

## Finding: the PCA-negative is ROBUST (not cosine-specific; null-space does NOT rescue)
- Non-cosine (raw-dot) readout: PCA still does not help (same as cosine).
- Discardable-null-space (noise ORTHOGONAL to signal -- the best case for PCA): PCA STILL does not help; WORSE at high noise (-0.19).
- **Mechanism (why even the null-space case fails):** full-N recall AVERAGES the noise over N dims (law of large numbers) -> robust. PCA-to-k drops to fewer dims and LOSES that averaging, so it is net worse even though it reduces TOTAL noise. The many-dim averaging dominates the noise-reduction. This is general to nearest-key recall, not readout- or noise-locality-specific.

## Net: LEVER #2 PCA = MEASURED_MECHANISM-negative, ROBUST (2x-confirmed)
The denoising-via-dim-reduction premise fails for KV recall in EVERY tested regime (cosine + raw-dot x all-dim + null-space noise). No rescue regime found. The lever is genuinely dead for recall. Strengthens the MM-negative atom: "PCA-dim-selection provides no nearest-key recall benefit; full-N's many-dim noise-averaging beats any dim-reduction, even with a discardable null-space." Revival-drill 2x RESOLVED (negative holds).

-- exp_dev
