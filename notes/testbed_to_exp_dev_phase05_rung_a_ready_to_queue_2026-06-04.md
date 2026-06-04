# Testbed -> Exp-Dev: Phase 0.5 v1 Rung A residual-extraction READY TO QUEUE

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** `testbed_to_exp_dev_phase05_rung_a_responses_2026-06-04.md` (open work) + `exp_dev_to_testbed_phase05_rung_a_division_of_labor_2026-06-04.md` (your division-of-labor request)

## Status

License acceptance: **DONE** (user accepted Llama-3.2-1B HF license; verified via `model_info` + `AutoConfig.from_pretrained` + `AutoTokenizer.from_pretrained` all returning OK with our `.hf_token`).

Script engineered + smoke-validated: **DONE** (1024 LOC at `experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py`).
- PROT-022 selftests pass at module import (token + layer band + parser + codebook + VSA shape)
- Synthetic-residual smoke (50 docs / VSA_D=512): HARD_PASS, 5.5s wall, npz schema validated
- Real-load CPU smoke (2 docs / Llama-3.2-1B BF16): HARD_PASS, 6.2s wall, residual std trajectory matches expected pre-norm signature `[0.11, 0.12, 0.15, ..., 2.26]`
- F:\ self-redirection patched and verified (local laptop without F:\ no-ops cleanly; on the 4060 Ti desktop with F:\ available, HF_HOME + output_dir both redirect automatically)

Prereg: **FILED** at `preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md`.

## Queue command for Exp-Dev to ship

```bash
bash tools/orchestrator/queue_add.sh \
  overnight_queue \
  phase05_v1_llama32_1b_residual_extract_v1 \
  experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
  10800
```

(`--skip-smoke` optional; smoke already ran locally + on real CPU load. The runner re-runs smoke by default per PROT discipline; this is fine.)

**Queue:** `overnight_queue` (the remote GPU queue → 4060 Ti). Not `remote_cpu_queue` (this is GPU work) and not cloud (Llama-3.2-1B fits 8GB comfortably; $0 per `feedback_cloud_only_when_absolutely_necessary`).

**Timeout:** 10800s (3h). Computed per PROT-019: ~50ms/doc * 100000 docs = 5000s extraction + ~210s overhead, ×1.5 safety = 7800s. Rounded up to 10800 (well under 14400 cap). Per-doc partial JSON checkpointing means restart-on-timeout doesn't lose progress.

## F:\ self-config (no setup needed on the desktop)

The script auto-detects F:\ on Windows. When present (the 4060 Ti desktop case):
- `HF_HOME` / `HUGGINGFACE_HUB_CACHE` / `TRANSFORMERS_CACHE` → `F:\hf_cache` (set at module init, before any HF imports)
- Output directory → `F:\hd_data\exp_phase05_v1_llama32_1b_residual_extract_v1\`
- ~7.5 GB total disk footprint (2.5 GB model + ~5 GB artifacts); 700 GB free on F:\

No admin / no `mklink` / no `setx` required. Just run the script.

When F:\ is absent (e.g., test machines, Linux runners), the script falls back to default paths transparently.

## Handoff artifacts schema (delivered to Exp-Dev's pipeline)

When the queued run completes, Exp-Dev's harness reads from
`F:\hd_data\exp_phase05_v1_llama32_1b_residual_extract_v1\llama32_1b_residuals.npz`
(SCP'd back to `data/exp_phase05_v1_llama32_1b_residual_extract_v1/` on the testbed clone via the existing heartbeat-watchdog bridge):

| Array | Dtype | Shape | Description |
|---|---|---|---|
| `residuals` | float32 | `(n_docs, 9, 2048)` | hidden_states[8:17] (outputs of layers 7..15), final-token position, BF16->FP32 |
| `doc_ids` | int32 | `(n_docs,)` | stable doc indices |
| `split` | uint8 | `(n_docs,)` | 0=train (80%), 1=val (10%), 2=test (10%) |
| `target_vsa` | float32 (bipolar) | `(n_docs, VSA_D)` | VSA encoding from `create_vsa_encodings` (or local fallback if hyperprobe import fails) |
| `vsa_dim` | int32 scalar | `()` | VSA_D (default 4096; see open question) |

Plus sidecar JSONs:
- `llama32_1b_residuals_meta.json`: `{model_id, layer_band_hidden_state_slice, n_train/val/test, codebook_concepts_count, vsa_dim, hidden_dim, extracted_at_iso}`
- `doc_id_to_doc_str.json`: traceability map (small)
- `metrics.json`: this anchor's HP/MID/HF verdict

## Open question to you (Exp-Dev)

**VSA dimension at 1B**: my script defaults to VSA_D=4096 (paper-matched; matches the prior 8B Hyperprobe-trained probe). If you'd prefer 2048 (clean Algorithm-1 sum-pool dim match), flag back and I'll override (one-line config change + ~minutes to regenerate target_vsa).

## Going-forward handshake (per user 2026-06-04: "exp_dev should be able to queue testbed experiments")

This anchor is the first instance of Testbed → Exp-Dev queueing handoff. The protocol going forward:

**Testbed produces, per LLM-integration anchor:**
1. Script at `experiments/<anchor>.py` (PROT-018/021/022 compliant; ASCII-only; F:\ self-config when applicable)
2. Prereg at `preregs/<DATE>_<anchor>.md` (per `preregs/_template.md`)
3. Handoff note `notes/testbed_to_exp_dev_<anchor>_ready_to_queue_<DATE>.md` (this file is the template) with:
   - Smoke status
   - Queue command (verbatim queue_add.sh invocation; you can copy-paste)
   - Timeout calc
   - F:\ status
   - Open questions
4. Commit + push to origin/main

**Exp-Dev consumes:**
- Polls `notes/testbed_to_exp_dev_*_ready_to_queue_*.md`
- Runs the queue_add.sh command verbatim (or with `--skip-smoke` since Testbed already validated)
- Reports back via the standard Exp-Dev shipped-cycle output file

I'll preserve this 4-artifact pattern (script + prereg + handoff note + commit) for all future Testbed-side LLM ships.

## Sequencing for THIS dispatch

1. **Testbed:** commit + push (this turn)
2. **Exp-Dev:** poll, see this note, queue via the command above
3. **Runner:** pulls latest, picks up the queue entry, runs on 4060 Ti
4. **Heartbeat watchdog:** SCP-back artifacts to local clone
5. **Testbed:** monitor verdict; ping Exp-Dev via `testbed_to_exp_dev_residuals_delivered_<date>.md` when npz lands
6. **Exp-Dev:** consumes npz; runs Algorithm 1 + Hyperprobe MLP + 3 audit primitives

---

**END.**

**Exp-Dev:** ready to queue. The queue_add.sh command is above; runs as-is. No script-side or env-side prep needed on the 4060 Ti (F:\ self-config). Please confirm VSA_D default (4096 vs 2048).

**Orchestrator:** informed; Phase 0.5 v1 Rung A subphase-1 dispatch ready; no cloud spend.

**User:** ready to push the green-light commit. Script + prereg are on local disk; will be visible to runner after my next `git push`.
