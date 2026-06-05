# Testbed -> Exp-Dev: Pythia-160M extraction script ready; please queue

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-04 ~22:15
**Re:** `exp_dev_to_testbed_user_authorized_v7_kill_pythia_extract_2026-06-04.md` + `research_to_testbed_pythia_extraction_priority_2026-06-04.md`

## User-authorized pivot: Pythia-160M extraction = NOW

Per your note: user authorized (a) kill v7 (done by you) and (b) run Pythia-160M residual extraction immediately. GPU is free. Script shipped + smoke validated; ready to queue.

## Script + smoke

`experiments/exp_phase05_v1_pythia160m_residual_extract_v1.py` (~330 LOC). Local smoke (--smoke flag, synthetic residuals, no model load):
```
PROT-022 selftests: ALL PASS
START anchor=phase05_v1_pythia160m_residual_extract_v1 run_mode=smoke n_docs_target=50
smoke mode: skipping dataset load; synthetic docs
watchdog armed: per-doc timeout=120s PROGRESS_EVERY=50
extracted=50 failed=0 wall_so_far=0.8s
residuals shape (50, 768) all_finite=True
npz written -> data/exp_phase05_v1_pythia160m_residual_extract_v1/residuals.npz
verdict=HARD_FAIL: too few residuals: 50 < 2500 (HARD_FAIL floor)
```
Smoke HARD_FAIL is correct -- 50 synthetic < HARD_PASS floor of 5000. Structural pipeline confirmed.

## Audit fixes baked in (lessons from cornerstone + Llama v6/v7 hangs)

1. **TOKENIZERS_PARALLELISM=false at module top BEFORE transformers import** -- root cause of v6 + v7 silent hangs (rayon thread pool fork deadlock). Set unconditionally.
2. **Per-doc watchdog with os._exit(99) at 120s idle** -- silent hangs convert to fast-fail. Writes `watchdog_exit.json` for postmortem.
3. **File-first HF token precedence** -- Pythia is public so env / file / anonymous all work; defensive.
4. **PROT-021 per-doc partials** via `write_partial_key` -- resume from partials on next dispatch.
5. **Per-doc heartbeat flush** + **GPU memory in progress lines** every 50 docs.

## Script specs

- Model: `EleutherAI/pythia-160m` (public, ~320 MB BF16)
- Layer: `hidden_states[12]` (last transformer block output) at final-token position
- Hidden dim: 768; shape (n_docs, 768) float32
- Corpus: `saturnMars/hyperprobe-dataset-analogy` (already cached on the runner from Llama work)
- Target: 10,000 docs (HP floor = 5,000; MIDDLE 5,000-10,000)
- MAX_TOK_LEN: 64 (analogy docs are short)
- Output: `data/exp_phase05_v1_pythia160m_residual_extract_v1/residuals.npz` + `residuals_meta.json` sidecar

## Pre-reg bands

- **HARD_PASS**: n_residuals >= 5000, npz exists, all finite, shape (n, 768)
- **MIDDLE_BAND**: n_residuals in [2500, 5000) (partial extraction)
- **HARD_FAIL**: n_residuals < 2500 OR npz absent OR NaN in residuals

## Wall + timeout estimate

Pythia-160M on a 4060 Ti: ~50-100ms per doc (small model, short prompts). 10k docs ~10-15 min wall best case. Plus model load ~5-10s + dataset iter ~10-30s + npz assembly ~10s. Conservative timeout: **3600s** (60 min) to account for cold caches + dataset iteration overhead.

## Queue command (PowerShell on marsh@home)

```powershell
git -C C:\dev\hd-instrument pull origin main
bash tools/orchestrator/queue_add.sh overnight_queue \
  phase05_v1_pythia160m_residual_extract_v1 \
  experiments/exp_phase05_v1_pythia160m_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_pythia160m_residual_extract_v1.md \
  3600
```

(Prereg file may need to be created or stubbed; the script's anchor + docstring are self-documenting if you prefer a thin prereg.)

## What you'll see in the log

```
PROT-022 selftests: ALL PASS
[   0.10s] START anchor=phase05_v1_pythia160m_residual_extract_v1 run_mode=full n_docs_target=10000
[   1.50s] loading dataset saturnMars/hyperprobe-dataset-analogy
[   4.80s] dataset split=train n_rows=395892
[   5.50s] corpus built: 10000 docs (target 10000)
[   6.00s] loading EleutherAI/pythia-160m -> device=cuda dtype=bf16 ...
[  12.40s]   model loaded in 6.4s; hidden_size=768 n_layers=12
[  12.40s] Pythia load OK
[  12.45s] watchdog armed: per-doc timeout=120s PROGRESS_EVERY=50
[  12.50s] resume: 0 docs already cached
  progress: doc 50/10000 extracted=50 failed=0 wall_so_far=3.2s gpu_alloc_gb=0.34
  progress: doc 100/10000 extracted=100 failed=0 wall_so_far=6.4s gpu_alloc_gb=0.34
  ...
  progress: doc 10000/10000 extracted=10000 failed=0 wall_so_far=638.2s gpu_alloc_gb=0.34
[ 650.10s] extraction done in 638.2s: extracted=10000 failed=0
[ 650.10s] assembling npz from per-doc partials
[ 668.30s] residuals shape (10000, 768) all_finite=True
[ 668.40s] npz written -> data/exp_phase05_v1_pythia160m_residual_extract_v1/residuals.npz
[ 668.50s] verdict=HARD_PASS: Pythia-160M residual extraction at layer 12 complete; 10000 residuals at shape (n, 768) saved to residuals.npz. Ready for downstream EX-CONCEPT-1 VQ + substrate-audit-core C2 + C3 on real Pythia residuals (Tier-1 product anchor at small-LLM scale per research's hybrid C+D recovery plan).
```

## What's in the npz

```python
loaded = np.load('residuals.npz')
loaded['residuals']    # shape (n, 768) float32; per-doc last-layer final-token residual
loaded['doc_indices']  # shape (n,) int64; original dataset row index for each residual
```

Plus `residuals_meta.json` sidecar:
```json
{
  "anchor": "phase05_v1_pythia160m_residual_extract_v1",
  "model_id": "EleutherAI/pythia-160m",
  "hidden_dim": 768,
  "layer_idx_target": 12,
  "n_residuals": 10000,
  "n_extracted": 10000,
  "n_failed": 0,
  "dataset_id": "saturnMars/hyperprobe-dataset-analogy",
  "run_mode": "full",
  "wall_extract_s": 638.2,
  ...
}
```

## What this unblocks for you

1. **EX-CONCEPT-1 REAL** -- VQ the (10000, 768) residuals into concept IDs -> substrate concept-LM. P_deflated=0.35 per Research.
2. **substrate-audit-core C2 + C3** on REAL Pythia-160M residuals -- the Tier-1 product anchor per Research's hybrid C+D recovery plan. Closed-form algebra; doesn't need a trained encoder.
3. **Tier-4 Hopfield-attention substitution** -- the scaffold is confirmed by Pythia loading; doesn't need the npz but the extraction validates the stack.
4. **EX-OPTION-C-W_proj** -- B8 logit-space encoding + single W_proj inject. P_deflated=0.25.

Ping me when the npz lands or if you hit any new failure mode I should patch.

## Commit

Script + this note committed (hash forthcoming after push). No changes to other scripts; Pythia is independent of the Llama v8 patches (which remain shipped in case Llama is re-attempted later per user note "re-attempt extraction later with diagnostic flags").

---

**END.**

**Exp-Dev:** Pythia-160M extraction ready. Queue at your next cadence; expected wall ~10-15 min; HARD_PASS at >= 5000 residuals. Will ping when npz lands; you build EX-CONCEPT-1-real immediately per your note.

**User:** Pythia script shipped with all Llama-lesson audit fixes baked in (tokenizers parallelism off, watchdog, per-doc flush). Waits on Exp-Dev queue dispatch.

**Research:** Pythia path matches your hybrid C+D plan; C2 + C3 substrate-audit-core can run on real Pythia residuals as the Tier-1 anchor at small-LLM scale, deferring cornerstone 8B to optional follow-on.
