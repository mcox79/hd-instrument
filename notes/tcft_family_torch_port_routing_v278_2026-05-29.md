# TCFT family torch-port routing note (v278)

## Trigger

User flagged GPU underutilization 2026-05-29 20:30 ET. Audit found 2 recent
GPU-queue anchors were NumPy-only (cannot use GPU):

- `tcft_m_sweep_v3_n8192_5seed` (completed 2026-05-28; held GPU slot ~3h)
- `tcft_erase_robustness_n8192_v1` (running 4h before user noticed; killed
  20:31:50; runner marked failed 20:36:22)

Root cause: every script in the TCFT family is pure NumPy. They inherited
overnight_queue routing from the earliest TCFT smoke and the routing never
got revisited as production-N tests were added.

## Affected scripts (NumPy-only; cannot use GPU)

- exp_tcft_alpha_sweep_v1_n8192.py
- exp_tcft_erase_robustness_n2048_v1.py
- exp_tcft_erase_robustness_n8192_v1.py
- exp_tcft_fresh_erase_v1.py through v4.py
- exp_tcft_m_sweep_v1.py
- exp_tcft_m_sweep_v3_n8192_5seed.py
- exp_tcft_n8192_v5.py, v6.py, v7.py

12 scripts in total.

## Immediate mitigation (shipped 2026-05-29)

1. Killed orphaned NumPy job on GPU runner (pid 64380).
2. Re-queued the killed anchor on remote_cpu_queue as
   `tcft_erase_robustness_n8192_v1_cpu` (timeout 21600s).
3. Added PROT-020 to queue_add.py: NumPy-only scripts on overnight_queue
   exit 8 with a routing-fix message. Override flag `--allow-numpy-on-gpu`
   exists but should be rare. Verified guard fires correctly on the offending
   anchor and passes torch+cuda anchors (test commit pre-push).

## Forward options (pick one when capacity allows)

**Option A — leave as NumPy, route to remote_cpu_queue (no eng work).**
PROT-020 already enforces this for new ships. Future TCFT anchors get queued
to remote_cpu_queue and the GPU runner is freed up for torch+cuda work.
Cost: 0 eng. Tradeoff: TCFT runs at CPU speed forever; future production-N
sweeps could take 6-12h instead of ~1h on GPU.

**Option B — port TCFT to torch+cuda (medium eng work).**
The TCFT math is matrix-heavy (M-by-N weight matrices, alpha sweeps over
trajectory class). Should benefit from GPU significantly. Risk: numerical
divergence between NumPy float64 and torch float32 — verify_chain on a
known TCFT anchor's metrics must reproduce. Cost: ~half engineer-day per
script; 12 scripts; ~6 engineer-days total. Realistically port the
3-4 active production-N ones (n8192 m_sweep, n8192 erase_robustness,
v7) and leave the rest CPU.

**Recommendation: A now, B opportunistically.** PROT-020 already gates
the recurrence. Porting is a deliberate exp_dev task that needs verification
work (the NumPy reference output is the oracle). Schedule when there's a
clean half-day window.

## Status_log connection

For-You entry filed 2026-05-29 20:35 ET with importance=HIGH:
"4 hrs of GPU runner slot wasted on NumPy-only TCFT script. Killed,
re-queued on CPU. PROT-020 guard prevents recurrence."
