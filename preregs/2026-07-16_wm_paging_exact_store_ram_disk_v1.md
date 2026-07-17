# Pre-reg: wm_paging_exact_store_ram_disk_v1 (Frontier-2 native advantage: "memory has its own N")

Cell: `experiments/exp_wm_paging_exact_store_ram_disk_v1.py`
Filed: 2026-07-16 (bands set BEFORE the full run)

## Question
Does EXACT external paging extend EFFECTIVE working memory LOSSLESSLY beyond the active-bundle
crosstalk cliff (~ N/16)? The substrate's native affordance (unlike the brain) is EXACT, addressable,
lossless external storage. A small active buffer + exact store, PAGING items in/out, should give
effective WM decoupled from the active N. RAM(registers)+disk thesis.

## Task
Stream m distinct (key -> value) FHRR items (m clearly EXCEEDS safe flat capacity N/16); query a random
subset of Q keys; recover the bound value. Correct answers need items no longer in the small active
window -> cannot be solved from the active buffer alone.

## Arms (differ ONLY in storage/paging; identical stream + geometry, benign)
- FLAT (baseline): all m items in ONE active bundle, no paging. Crosstalk ~ m -> craters past N/16.
- PAGED_EXACT (mechanism): B-item active FHRR bundle ("registers") + EXACT addressable key-value store
  ("disk"); evicted keys read back EXACTLY. Per-access crosstalk bounded by B, not m.
- PAGED_LOSSY (control): same B-buffer + same schedule, but evicted items re-bundled (compressed) into
  ONE super-vector; evicted readout carries crosstalk from all evicted items. Isolates EXACTNESS.

## Config
N=512, safe_cap=N//16=32, buffer B=16, Q=32, V_key=V_val=1024, seeds=5, m_grid=[8,16,32,48,64,96,128,256,512].

## Pre-reg bands (envelope-fail)
- HARD_PASS: at m_max=512 (>> N/16) PAGED_EXACT recall >= 0.90 AND FLAT craters (<= 0.50) AND PAGED_LOSSY
  degrades (<= 0.70) AND (PAGED_EXACT - PAGED_LOSSY) >= 0.20 (exactness load-bearing) AND effective-WM
  extension factor (m_paged_exact_hold / m_flat_crater) >= 4.0 AND FLAT actually craters in-range
  (discriminator fired).
- HARD_FAIL: (PAGED_EXACT - FLAT) < 0.10 at m_max (paging does not extend WM) OR (PAGED_EXACT -
  PAGED_LOSSY) < 0.10 (exactness does not matter) OR FLAT never craters (regime too easy).
- MIDDLE otherwise. Report extension factor + interface cost regardless.

## Discriminator / baseline-in-band
FLAT must be >= 0.90 below cliff (m=min) AND crater (<= 0.50) at m_max. Verified at self-test
(m=8 flat=1.000; m=512 flat<=0.50). META_RULE_AG baseline-in-band satisfied by the sweep spanning the cliff.

## Compute architecture
Class (b) sequential-CPU with justification: benign geometry, N=512, m<=512, 5 seeds; total wall < 10s;
mechanism-comparison at small scale (no GPU speedup for this size). numpy complex128. No queue/GPU/atoms/push.

## Hardening
except SystemExit: raise before except Exception (no BaseException / no bare except); atomic tmp+os.replace
metrics write; arms-must-differ self-test (3 recall arms distinct); leak guard (single-item unbind lossless);
discriminator-fires self-test at full-scale m=512 (survives-scale check A: self-test IS at full N and m_max).

## Brain-check (on HARD_FAIL)
Brain WM is tiny + lossy; if OUR paging also failed despite an EXACT store the brain lacks, that is an
implementation limit (exact recall is an existence-proof), not a structural bound. Report which.

## RESULT (full, landed 2026-07-16, run_mode=full verified on disk, 5 seeds)
HARD_PASS. m_max=512: paged_exact=1.000, flat=0.025, paged_lossy=0.081. FLAT craters at m=64;
PAGED_EXACT holds to m=512. Effective-WM extension factor = 8.0x. exact-lossy gap = +0.919 (exactness
load-bearing). exact-flat gap = +0.975. Interface cost = 0.97 store-writes/item + 0.94 store-reads/query
(amortized O(1), does not scale with m). Discriminator fired. MEASURED@data/exp_wm_paging_exact_store_ram_disk_v1/metrics.json.
