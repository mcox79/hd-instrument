# Pre-registration: wave14xrd_walsh_spectrum

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14xrd_walsh_spectrum.py](../experiments/exp_wave14xrd_walsh_spectrum.py)

## Why

User's crystallography insight: in materials science, X-ray diffraction reveals
stored structure non-destructively. Bragg peaks in the diffraction pattern
correspond to periodic atomic order; diffuse background = amorphous/glassy
disorder. Our substrate's Walsh-Hadamard transform of W is the direct math
analog: each stored (v_k, k_k) outer product produces a peak at a specific
Walsh frequency.

## Hypothesis

For K << alpha_c * N, the Walsh spectrum of W shows K resolvable peaks above
a flat background (SNR >= 2). For K ~ alpha_c * N, peaks broaden and background
rises ("glass transition" in Walsh basis). For K >> alpha_c * N, spectrum
becomes random (no resolvable peaks).

## Kill criterion

If SNR remains > 2 at all K including K >> alpha_c * N, the WHT view is not
revealing the regime structure - the test is uninformative.

If SNR is always < 2 (even at K=50), the substrate's W is structurally not
"crystalline" in Walsh basis - the analogy is decorative not load-bearing.

## Operational definition

- N=4096, sweep K in {50, 100, 200, 400, 600, 900, 1300, 2000, 3000}
- For each K, generate K random +/-1 (v, k) pairs; build W = sum v_k k_k^T / N
- Apply FWHT to each row of W -> N x N spectral magnitude matrix
- Per-frequency mean magnitude across rows
- Sort, compute SNR = mean(top K) / mean(remaining N - K)
- Track transition K where SNR crosses 2.0

## Cited mechanism

- Crystallographic structure factor F(G) = sum_atoms f_j exp(2pi i G . r_j)
- Walsh-Hadamard is the natural Fourier basis on Z_2^N (Cayley graph of hypercube)
- Wavelet/Walsh decompositions of weight matrices: Magoarou-Gribonval arXiv:1406.5388
- Recent: butterfly/Monarch matrices Fu-Dao et al. 2023+

## Expected runtime

Smoke (N=512, 3 K values): ~5 sec
Full (N=4096, 9 K values): ~5-10 min on GPU

## Verdict labels

- `XRD_TRANSITION_FOUND`: SNR crosses 2.0 at specific K - "amorphous transition" measured
- `XRD_ALL_CRYSTALLINE`: SNR stays >= 2 - extend K_grid up
- `XRD_NO_PEAKS`: SNR < 2 throughout - analog fails
- `XRD_NONMONOTONIC`: non-monotonic SNR - investigate
- `XRD_INCONCLUSIVE`: empty data
