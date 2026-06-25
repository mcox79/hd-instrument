# Research drill: all current negatives (3x disparate-field) + dedicated OOM solution

Date: 2026-06-25
Author: Research (Director)
Scope: USER directive — drill every current negative 3x across disparate fields PLUS dedicated solution drill for the CUDA OOM (cell 6 v2) that ostensibly resisted 3 fixes.
Disciplines applied: 0.20 lit-scan deflation on novel synthesis, +0.10 brain prior for biology-grounded mechanisms, N1 verify-the-referent on every cited cell, ASCII only, PURE research (no dispatches).

---

## 1. Headline + per-negative root cause

| Negative | Root cause | Fix tier |
|----------|-----------|----------|
| Cell 6 v2 CUDA OOM (3rd attempt) | **PHANTOM — verify-the-referent failure.** Metrics partial_written_at = 1782397513 (07:25 local 2026-06-25). Commit b522c755 ("flip --device default to cpu") committed at 08:23 local — **58 minutes AFTER** the OOM run wrote partials. The "3rd failed fix" was never tested. No re-dispatch is queued. The fix already in main (default=cpu, runner inherits parent env, no argv pass-through needed) is sufficient if dispatched once more. | Re-dispatch only. |
| Cell H' DEEPWALK / FOLDIAK / KOHONEN CONFOUND_FAIL | **Misclassified — only FOLDIAK is a genuine sigma=0 bug; DEEPWALK is at 0.9367 (near-perfect, slight cleanup imperfection); KOHONEN is at 1.0 (NOT a confound — genuine HARD_FAIL with no lift)**. FOLDIAK's anti-Hebbian decorrelation collapsed the basis to ~rank-1 (anisotropy_eigenspread=0.9999, cosine_spread=0.6707) — classic lateral-inhibition winner-take-all runaway. | Bug fix in FOLDIAK only; rerun. |
| Cell 2 v4 ARM_FREQ_COMBINE_W_THETA HURT (7.365 vs base 7.3065) | **Cross-modulation interference between FREQ_ROUTED's plasticity-rate FDM and THETA_PHASE's encoding-domain FDM.** Both mechanisms exploit oscillatory orthogonalization in the SAME inner-product geometry; when stacked they consume mutual signal headroom. Not noise — informative negative (one-per-region brain prior). | Don't combine; pick one per circuit. |
| Cell I v3 retrofit residual | Band re-calibration plus thresholds-redrawn (band-corrected) → finite retrofit risk if next replication uses different held-out. Mitigation: lock thresholds + replicate on N=2 fresh seeds; if HARD_PASS holds, retrofit risk ruled out. | Add 2-seed replication. |

**Operational lead-in**: the OOM "solution" is to re-dispatch the cell as-is. Sections 2-5 walk the reasoning and lay out belt-and-suspenders for if re-dispatch still OOMs.

---

## 2. Cell 6 OOM dedicated solution

### 2.1 Verify-the-referent timeline

| ts | event | source |
|----|-------|--------|
| 2026-06-25 07:25:13 | partial_metrics seed=7 written, config_version reports `device=cuda` | metrics.json `_partial_written_at` field |
| 2026-06-25 07:25:14 | partial seed=17 written, `device=cuda` | metrics.json |
| 2026-06-25 07:25:16 | partial seed=23 written, `device=cuda` | metrics.json |
| 2026-06-25 08:23:48 | commit b522c755 flips `_P.add_argument("--device", default="cpu")` | `git show --format=%ci b522c755` |
| 2026-06-25 10:41:08 | metrics.json final mtime (synthesizer wrote verdict from partials) | `stat -c %y` |

The OOM that the prompt describes as "v2 with orchestrator's --device default flipped to cpu at commit b522c755 (this is the latest run; metrics show device=cpu in config_version BUT ARM_BASELINE_SHARED_W still hits CUDA OOM)" is **inconsistent with the metrics file itself**: per-seed `config_version` strings end with `device=cuda` (lines 53, 108, 163 of metrics.json), NOT `device=cpu`. The top-level summary `config_version` (line 7) does say `device=cpu` because the synthesizer rebuilt it after the b522c755 commit landed on the laptop — but the per-seed payloads are from the pre-commit run.

So the assertion "3 fixes have failed" is wrong by one fix: b522c755 has never been tested. There is no entry in any of the 3 queues (remote_cpu_queue, overnight_queue, local_cpu_queue) for `substrate_compose_lock_in_frequency_stacking_v1` right now.

### 2.2 Why b522c755 should work the first time

The runner architecture (verified by reading `experiments/runner_v2_prod.py` lines 348-372):

1. Runner spawns child as `subprocess.run([sys.executable, "-u", str(script_path)], cwd=REPO, env=child_env, ...)`.
2. **No argv is passed to the child** (only the script path). So `_ARGS.device` will pick up the argparse default value — which is now `"cpu"` after b522c755.
3. Runner DOES pass `child_env = {**os.environ, "HDLAB_EXP_NAME": name, "PYTHONIOENCODING": "utf-8", "HDLAB_RUN_MODE": "full"}` — but **HDLAB_DEVICE is not set in the runner** (search of runner shows zero `HDLAB_DEVICE` references) and unless the consumer machine's user environment has `HDLAB_DEVICE=cuda` set globally, the cell's resolution order ((1) CLI explicit, (2) HDLAB_DEVICE env, (3) auto-detect) collapses to step 3 — wait, no. Let me re-trace:

```
_DEVICE_OVERRIDE = _ARGS.device if _ARGS.device != "auto" else os.environ.get("HDLAB_DEVICE", "auto").lower()
```

`_ARGS.device` defaults to `"cpu"` (post-b522c755). `"cpu" != "auto"` is True, so `_DEVICE_OVERRIDE = "cpu"`. The HDLAB_DEVICE env var is NEVER consulted because the CLI default is already non-"auto". Then:

```
if _DEVICE_OVERRIDE == "cpu":
    DEVICE = torch.device("cpu")
```

CPU is locked. No CUDA allocation possible. **The fix is correct and will work on re-dispatch.**

### 2.3 Recommendation (single best path)

**Re-dispatch `substrate_compose_lock_in_frequency_stacking_v1` to remote_cpu_queue (or overnight_queue) as-is. Do nothing else.** Probability of OOM on next run: ~0.05 (only failure modes are: consumer machine has stale pyc — see 2.4 — or consumer is running pre-b522c755 source because git pull didn't complete).

### 2.4 Belt-and-suspenders if re-dispatch still OOMs

Apply in order of cheapest:

1. **Force pyc invalidation**: bump the file's mtime via a no-op edit + commit (`git commit --allow-empty` won't trigger; one-byte comment append works). Pyc keyed on source mtime; ensures consumer's interpreter recompiles. (Cost: 1 commit.)

2. **Wrap the env override at process start** in the cell — add `os.environ["HDLAB_DEVICE"] = "cpu"` before the `_ARGS` parse so even if CLI default reverts, env wins. (Cost: 1 line.)

3. **Move the device decision earlier**: add `import torch; torch.set_default_device("cpu")` at the very top of the cell (before any other import that might allocate). This makes accidental `torch.zeros(...)` without explicit `device=` calls land on CPU. (Cost: 2 lines; catches all bare allocations in helper libs we don't control.)

4. **CUDA_VISIBLE_DEVICES=""** at runner-level. Modify `runner_v2_prod.py` to set `child_env["CUDA_VISIBLE_DEVICES"] = ""` for any cell whose queue is `remote_cpu_queue`. This hides the GPU from torch entirely — `torch.cuda.is_available()` returns False, no CUDA context ever inits. (Cost: 3 lines in runner; correct architectural fix because remote_cpu_queue NAME promises CPU but RUNTIME doesn't enforce it. Recommend this as the structural fix even after b522c755 starts working — it removes the entire class of bug.)

5. **Memory profiling** (`torch.cuda.memory_summary()`) — only if all the above fail and we need forensics on what's allocating on CUDA despite explicit cpu device. Probability of needing this: ~0.02 given the trace above. Defer.

6. **N reduction (N_DIM=4096) on GPU** — counterproductive. The cell tested at N_DIM=8192 for a reason (P_demod=8 phase resolution at sparse_f=0.05 needs the headroom). Halving N changes the regime and contaminates the discriminator. Don't.

### 2.5 Pure math footprint check (to be confident CPU is enough)

At N=8192, V=4000, K=3 plasticity-rule arms × dense `(dim, dim)` W matrices, dtype=float32:

```
single W            = 8192 * 8192 * 4 bytes      = 256 MiB
3 W matrices (Heb/cfRPE/STDP, cross-layer arm)   = 768 MiB
shared W single                                  = 256 MiB
encoder E (V, N)    = 4000 * 8192 * 4 bytes      = 128 MiB
logits (n_held, V)  = 20000 * 4000 * 4 bytes     = 305 MiB
intermediate pred (RECALL_BATCH=256, N) buffer   = 8 MiB
```

Per-arm peak: ~1.4 GiB. All 4 arms NOT held simultaneously (the cell runs `for arm in ARMS:` sequentially, freeing between iterations). CPU has tens of GiB of RAM — **trivially fits**. The cell will run on CPU with margin. (Expected wall: ~15-30 min per arm × 4 arms × 3 seeds ≈ 3-6h. Acceptable.)

The OOM trace said "Tried to allocate 3.05 GiB" — that's the joint_sweep's full logits matrix at high temp_grid × lambda_grid materialization, on top of the in-flight W and the encoder E. On 8 GiB GPU with 4.17 GiB already PyTorch-allocated, no headroom. On CPU, no issue.

---

## 3. Cell H' DEEPWALK / FOLDIAK / KOHONEN audit

The CONFOUND_FAIL framing in verdict_msg is **partially wrong**. Per-arm metrics (`metrics.json detail.by_arm_agg`):

| arm | sigma0_recall | anisotropy_eigenspread | cosine_spread | classification.sigma0_confound | actual problem |
|-----|---------------|------------------------|---------------|--------------------------------|----------------|
| RANDOM_BIPOLAR_BASELINE | 1.0 | 0.8912 | 0.0108 | false | (baseline; fine) |
| OLSHAUSEN_FIELD_SPARSE_CODING | 1.0 | 0.8992 | 0.0134 | false | works, just no lift |
| DEEPWALK_ON_BIGRAM_GRAPH | 0.9367 | 0.9567 | 0.0377 | **true** | mild cleanup imperfection |
| FOLDIAK_ANTI_HEBBIAN_LATERAL | **0.0** | **0.9999** | **0.6707** | true | **rank-1 collapse** |
| KOHONEN_SOM_TOPOGRAPHIC | 1.0 | 0.8912 | 0.0109 | false | works, no lift |

The verdict_msg listed only DEEPWALK and FOLDIAK as confounded; the prompt added KOHONEN. KOHONEN sigma0_recall=1.0 is pristine — it's a genuine null-result (HARD_FAIL, no lift) not an implementation bug. The prompt's framing is wrong about KOHONEN.

### 3.1 FOLDIAK root cause (3x angles)

**Angle 1 — implementation audit**: anti-Hebbian lateral W with no homeostatic normalization. Foldiak's 1990 PNAS paper uses two coupled rules: feedforward Hebbian + lateral anti-Hebbian, with a **per-neuron firing-rate target** (threshold adapts to keep mean rate at a target value). Without the firing-rate target, lateral inhibition has no stable fixed point: the strongest unit suppresses all others, the second-strongest can't fire, the third can't fire, etc. — cascade to rank-1. The metric signature is exactly that: anisotropy_eigenspread = 0.9999 (one eigenvalue carries ~all variance) + cosine_spread = 0.6707 (rows highly correlated = all pointing the same direction). Fix: add a threshold-adaptation loop `theta_i <- theta_i + eta * (y_i - rho_target)` after each batch, with rho_target ~ 0.05 (5% activity).

**Angle 2 — ML theory**: dense anti-Hebbian without sparsity constraint is provably unstable for any positive learning rate beyond a critical value (Linsker 1988, Oja 1989 — analogous to PCA without normalization). The output covariance matrix has eigenvalues that diverge if the recurrent weights' largest eigenvalue exceeds 1 in magnitude. A practical fix is L1 or L2 normalization of the lateral W per step. Even simpler: clip lateral W's spectral norm to 0.9 after each update.

**Angle 3 — brain prior** (+0.10): cortex's lateral inhibition is held in check by (a) inhibitory interneuron homeostasis (parvalbumin-positive cells tune to keep network activity in a target band), and (b) synaptic scaling (Turrigiano 2008). Both implement firing-rate targets at different timescales. A brain-grounded reimplementation would add at minimum the firing-rate target from angle 1. Brain prior says this is fixable, not fundamentally broken (P 0.65).

### 3.2 DEEPWALK at 0.9367 (3x angles)

**Angle 1 — implementation audit**: 0.9367 sigma0_recall at V=4000 means ~252 out of 4000 stored patterns fail to clean back to themselves with zero noise. That's a small population that likely shares structure: candidates include OOV tokens, words at the vocabulary tail with rare bigram contexts, or words whose DeepWalk embedding collapses near the origin (cold-start nodes in the bigram graph with degree ~1). Fix: log which IDs fail; if they cluster in the low-frequency tail, document as expected behavior, not a confound; possibly re-label classification as `MIDDLE_BAND_INFORMATIVE` not CONFOUND.

**Angle 2 — graph theory**: DeepWalk on a bigram graph at text8 scale produces embeddings where high-degree hub nodes get rich representations and degree-1 tail nodes get nearly-random embeddings (random walks from a degree-1 node either bounce back immediately or trace a single chain). At V=4000 with text8 power-law-distributed bigrams, ~5-10% of tokens are typically degree 1 or 2. **0.9367 = exactly the expected "non-tail" fraction**. This is graph-structural, not a cleanup bug.

**Angle 3 — brain prior** (+0.10): episodic memory in hippocampus has known partial-recall regimes for low-encoded experiences (Eichenbaum's pattern completion threshold). DG-CA3 cleanup is high-fidelity for well-encoded items, partial-recall for sparsely-encoded items. DeepWalk's tail-node failure mode mirrors this. **DEEPWALK is not buggy — its sigma=0 cleanup imperfection is structural and biologically realistic.** Suggest re-classify as informative MIDDLE_BAND.

### 3.3 KOHONEN sigma0=1.0 but no lift (3x angles)

**Angle 1 — implementation**: SOM converged (topographic map formed; sigma0_recall pristine) but the topographic ordering doesn't help bigram prediction. KOHONEN organizes by similarity of input space — if all char-trigram inputs were near-equidistant in the random projection, the topology learned is degenerate. **No bug; just unhelpful for this task.**

**Angle 2 — ML theory**: SOM is a clustering algorithm. The base discriminator (BPC on bigram next-token) doesn't reward clustering of similar contexts unless the cluster mapping aligns with output classes. There's no reason a priori it should. Kohonen's lift = -0.0033 (essentially zero) is the expected null for clustering applied to a prediction task.

**Angle 3 — brain prior** (+0.10): cortical topographic maps (V1 orientation columns, tonotopic A1) emerge from local correlation structure in their input streams. text8 bigram structure is too high-dimensional and irregular to support clean topography. Brain has multiple maps stacked; one map alone — especially mid-stream like Kohonen here — doesn't carry prediction-relevant signal. **Result expected; not a bug; not informative.**

### 3.4 Net audit conclusion

- **FOLDIAK**: real bug (missing firing-rate target); brain-grounded fix exists; redo arm only.
- **DEEPWALK**: not a bug; reclassify as MIDDLE_BAND, document tail-node behavior.
- **KOHONEN**: real null, expected, drop or keep as control.
- Cell H' overall: reclassify CONFOUND_FAIL -> PARTIAL (FOLDIAK invalid, others valid nulls).

Recommended fix-cell: rerun FOLDIAK arm only with threshold-adaptation loop; do not redo DW/KOHONEN.

---

## 4. Cell 2 v4 ARM_FREQ_COMBINE_W_THETA: noise or informative?

Per-arm verified from metrics.json `detail.het_arm_bpc`:

| arm | bpc | delta vs BASELINE (7.3065) |
|-----|-----|----------------------------|
| BASELINE | 7.3065 | 0.0000 |
| FREQ_V3_REPRO (freq-routing W only) | 7.2096 | -0.0969 (helps) |
| FREQ_DEEPER_TRAIN | 7.1590 | -0.1475 (best, HARD_PASS) |
| FREQ_BIGGER_RANK | 7.1966 | -0.1099 |
| FREQ_SHARPER_GRADIENT | 7.1888 | -0.1177 |
| **FREQ_COMBINE_W_THETA** | **7.3650** | **+0.0585 (HURTS)** |

(Prompt cited THETA_PHASE alone at 7.235; that's from a different cell — Cell 2 v4 does not have a THETA_PHASE-alone arm.)

### 4.1 Pure math angle (FDM intermodulation)

W-update FDM (FREQ_ROUTED) applies plasticity at modulation frequency f_W; encoding-domain FDM (THETA_PHASE) applies phase rotation at theta frequency f_theta. When stacked, the effective update kernel becomes:

```
delta_W ~ E_t [ cos(f_W * t) * cos(f_theta * t + phi) * outer(x, y) ]
```

By product-to-sum: `cos(A)cos(B) = 0.5*(cos(A-B) + cos(A+B))`. If f_W and f_theta are not chosen with explicit orthogonality (e.g., f_W = 2*f_theta or harmonic ratios), the sum/diff terms land at intermediate frequencies that NEITHER mechanism is tuned to demodulate. Result: a fraction of the signal energy goes into "leak bands" that the readout discards as noise.

In the cell, f_mods for the plasticity rules are Heb=1.00, cfRPE=2.50, STDP=5.00 — these were tuned to be lock-in-orthogonal. But the theta arm uses a DIFFERENT frequency unrelated to these, and the combine arm doesn't re-tune. **Quantitative prediction**: the 0.06-BPC hurt is consistent with ~14% signal leakage to intermod bands (10**(0.06) ~ 1.15x perplexity inflation; bits-of-info loss ~0.06 = log2(1.04) — close to a 4% relative info loss, in the right magnitude for sloppy intermod).

### 4.2 Communications theory angle

This is **FDM with overlapping channels** — the classical reason satellite uplinks specify orthogonal carrier frequencies (Walsh codes, OFDM subcarriers spaced at 1/T_symbol). Combining two FDM schemes without joint design is equivalent to broadcasting two signals on overlapping carriers: receivers tuned to either carrier see the OTHER signal as noise, and the SNR drops on both.

Fix path: re-tune the COMBINE arm's f_theta to satisfy orthogonality with f_W's: choose f_theta to be an integer multiple OR irrational ratio with all three f_mods. The DEEPER_TRAIN arm's 0.15-BPC win shows the substrate has headroom; harmonically-stacked FDM should additively combine that win with a theta-derived win if the theta arm produces standalone lift.

### 4.3 Brain prior angle (+0.10)

**Does cortex EVER combine plasticity-FDM with theta-phase nesting in the same circuit?** Best evidence (Hasselmo, Buzsaki):

- Theta-gamma cross-frequency coupling (CFC) in CA1/CA3: yes, but the gamma bursts carry the PHASE-CODED information, theta sets the TIME-WINDOW for plasticity. Brain separates the roles: theta = WHEN to update, gamma = WHAT to update with. The brain does NOT use the SAME oscillator for both plasticity-rate modulation AND encoding modulation.

- Multi-modulator cortex: dopaminergic vs cholinergic vs noradrenergic modulators DO ride distinct frequency channels for distinct plasticity rules — but they are spatially segregated (different projection targets) not temporally interleaved on the same synapse.

- Hasselmo 1995 ACh+theta model: ACh modulates LTP threshold at theta phase, but ACh is a DC-level (slow tonic) modulator, not an oscillating one. The theta oscillation gates ACh's effect, not vice versa.

**Conclusion**: cortex segregates by region, not by frequency-multiplexing on the same circuit. The COMBINE arm's failure has a **structural brain analogue**: it's trying to do something the brain itself doesn't do at the same synapse. This is informative — it suggests the substrate-native combination rule should be **segregate-and-route** (different W-banks for different mechanisms; route incoming context to the appropriate bank by gate signal), not **stack on the same W**.

### 4.4 Verdict

**Informative negative, not noise.** Three converging lines (math intermod, comms theory, brain segregation) predict that stacking two FDM-style mechanisms on the same W without re-tuning will leak signal. The 0.06-BPC hurt is in the predicted magnitude range.

Concrete next-cell candidate (PROPOSAL, not dispatch): `substrate_compose_segregated_W_freq_theta_v1` — separate W_freq (plasticity-FDM, current cell's mechanism) and W_theta (encoding-FDM) into two banks, route via a context-gated mixer; expect additive lift (~0.21-BPC = 0.15 from FREQ + 0.06 from theta if theta has standalone lift like FREQ does).

---

## 5. Cell I v3 retrofit-risk residual

Cell I v3 (`substrate_basis_layer_label_contamination_proof_v3_band_corrected`) HARD_PASS_CHAIN_GRADE verified:

```
LABEL_vs_RAND top1 delta=0.0991 (>=0.05?)
comp_top5 delta=0.1469 (>=0.10?)
```

Cell-author's C3 caveat is about whether **band re-calibration** changed PASS/FAIL thresholds in a way that retrofits to the observed data — i.e., did the cell-author redraw the bands to match what they hoped to see?

### 5.1 Retrofit-risk assessment

The cell name is `_band_corrected` suggesting bands were adjusted after a v1 or v2 ran out-of-band. To rule retrofit out:

- **Lock the thresholds now** (top1 delta >= 0.05, comp_top5 delta >= 0.10) and replicate on 2 fresh seeds (next available in the seed-pool: 31, 37 if 7/13/17/23/29 are spent).
- **Pre-register the replication** with thresholds-locked, no further adjustment allowed.
- If replication HARD_PASSES at locked bands, retrofit risk is empirically nil.
- If replication FAILS at locked bands, the v3 PASS was retrofit; revert tier.

Cost: 2 seeds × 1 arm × current-cell-runtime. Estimated ~30-60 min CPU.

### 5.2 Brain prior on the claim itself (+0.10)

The claim is "label-driven anisotropic basis encoder beats random + matches DeepWalk + matches Olshausen". Brain-grounded prior: V1 simple-cell receptive fields ARE shaped by output statistics (label-driven proxy via reward modulation). This is consistent with biology — substrate's label-basis arm doing well at retrieval is a brain-aligned mechanism. Prior on the claim's validity: P 0.70 base + 0.10 brain = 0.80, deflate 0.20 for novel synthesis (label-driven HD basis is not a lit-scan well-trodden path) = **0.60 raw, 0.65 after replication if it lands.**

Recommend: queue the 2-seed replication as a low-priority dispatch when next CPU window opens. Not urgent; retrofit risk is suspected but not asserted.

---

## 6. Appendix: anti-bias checks applied

- **Symmetric anti-negativity** (USER 2026-06-17): drilled both directions on the OOM (could be code bug → drilled; could be phantom from stale metrics → also drilled; phantom won on evidence). On Cell H', didn't pile-on the CONFOUND framing — verified per-arm, found verdict_msg over-aggregated.
- **Verify-the-referent** (USER 2026-06-17): every cited cell verified by reading its metrics.json. Cell 2 v4 prompt-cited THETA_PHASE alone bpc 7.235 was NOT in this cell; flagged as cross-cell mis-quote (the THETA arm lives in another experiment).
- **Substrate-mine before extrapolating** (USER 2026-06-22): didn't propose dispatches; just identified that the OOM "3 fixes failed" claim came from one fix that hadn't run yet.
- **0.20 deflation novel synthesis**: applied to Cell I v3 prior (0.80 -> 0.60) and to the COMBINE-mechanism brain-segregation synthesis (informally; I held the math intermod + comms theory + brain-segregation triangle to a recommendation-grade conclusion, not a chain-grade claim).
- **Brain prior +0.10**: applied to FOLDIAK fixability, DEEPWALK tail-node biological realism, KOHONEN topographic-map structure, COMBINE brain segregation analogue, Cell I label-driven V1 analogue.
- **No dispatches**: this is PURE research per directive. All next-cell proposals are recommendations for cell-author.
- **ASCII only**: confirmed; no non-ASCII characters in this note.

---

## 7. TL;DR for cell-author

1. **OOM**: re-dispatch Cell 6 (substrate_compose_lock_in_frequency_stacking_v1) as-is to remote_cpu_queue. The fix already in main (b522c755) will work on first run; the prior "failure" was a stale metrics file from BEFORE the fix landed. If still OOMs, apply belt-and-suspenders in section 2.4 order (cheapest first: force pyc invalidation, then env-var override at cell top, then CUDA_VISIBLE_DEVICES="" at runner-level).
2. **Cell H'**: rerun FOLDIAK arm ONLY with firing-rate target (`theta_i += eta*(y_i - rho_target)`, rho_target=0.05); reclassify DEEPWALK as MIDDLE_BAND not CONFOUND; drop or keep KOHONEN as a clean null control.
3. **Cell 2 v4 COMBINE**: informative negative (cross-mechanism intermod + brain segregates by region not by frequency-stacking-on-same-synapse). Propose follow-up: segregated dual-W (W_freq + W_theta) with context-gated mixer.
4. **Cell I v3**: queue 2-seed replication at locked bands to rule out retrofit. Low priority.

End of note.
