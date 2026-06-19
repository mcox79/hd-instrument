# N-mismatch eradication audit -- 2026-05-27

User mandate (verbatim): "did you resolve the experiment N assigment issue?
Apparently we've fucked that up 80 times do not let it happen again need to
figure out how to eradicate that error".

This note is the closure record. Three fixes landed earlier today; this commit
closes the remaining attack-surface holes (output-path patches, PROT-019
timeout floor, end-to-end refusal test, audit doc, HIGH-importance status_log).

ASCII-only per feedback_ascii_only_in_scripts.

---

## 1. Prior fixes (recap)

### 1a. 60d2147 -- PROT-018 runner-side N-suffix post-run validator

  experiments/runner_v2_prod.py: after every `--smoke`-gated FULL run that
  exits 0 and passes the schema check, the runner now re-reads
  data/exp_<name>/metrics.json and compares the recorded production N
  (summary.N / config.N / detail.N / N_run) against the anchor's _n<N>
  suffix. On mismatch the entry is marked FAILED with error=n_mismatch and a
  HIGH-importance status_log entry is appended. Catches:
    - Pre-PROT-018 backlog (anchors named _n<N> with no production N=<N> in
      the script source)
    - --allow-duplicate / --rerun-as bypass paths
    - Accidental smoke runs that escape queue_add gating

  Prevents: silent label-vs-honest drift at the RUNNER layer.

### 1b. e51aee7 -- verdict_handler remote-first metrics fetch

  tools/orchestrator/remote_state.py: get_metrics(name, prefer_remote=True)
  SSHs marsh@home and reads the remote /var/data/exp_<name>/metrics.json
  before falling back to local. Injects _source field. 12s timeout.
  tools/orchestrator/agents/verdict_handler.md: mandates get_metrics()
  in Self-discovery + Step 0; requires [metrics-source: ...] return prefix.

  Prevents: 78+ of today's catches that were verdict_handler reading stale
  LOCAL pre-ship smoke metrics while the remote FULL run was correct.
  This was the AMBIENT-NOISE source -- not a runner bug.

### 1c. 37f576f -- exp_bet_b_n8192_4stage_v1.py reads HDLAB_EXP_NAME

  Patched in the v1 4-stage Bet B script: get_output_dir(default_name) now
  reads HDLAB_EXP_NAME from os.environ; run() also reads it for the
  exp_name banner + metrics-path. Was the 81st catch (bet_b_4stage_v2
  writing to v1's data/exp_bet_b_n8192_4stage_v1/metrics.json).

  Prevents: cross-anchor output-path collision when multiple versions of a
  script-family ship in parallel.

---

## 2. Output-path bug sweep (this commit)

### 2a. Pattern

  - Audit target: every experiments/exp_*.py file potentially still
    hard-coding an output directory literal instead of honoring the
    runner-set HDLAB_EXP_NAME env var.
  - Detection: grep -c "HDLAB_EXP_NAME" per file. Files with 0 hits AND a
    write to data/exp_<literal>/metrics.json are bug candidates.
  - Verification: trace the metrics-write call back to the exp_name source.
    If the source is a hard-coded string literal, patch it.

### 2b. Scripts patched (11 files)

  All patches: (a) get_output_dir signature changed from `name: str` /
  `name: str = "<literal>"` to `default_name: str = "<literal>"`;
  (b) inside the function, `name = os.environ.get("HDLAB_EXP_NAME",
  default_name)`; (c) where the script also assigned a local literal
  `exp_name = "<literal>"`, that line was changed to
  `exp_name = os.environ.get("HDLAB_EXP_NAME", "<literal>")`.

  Patched files:
    1. experiments/exp_saad_solla_v8_n2048.py
    2. experiments/exp_saad_solla_v10_n8192.py
    3. experiments/exp_skahm_subclass_discriminator_v1.py
    4. experiments/exp_skahm_moe_shift_predictor_v1.py
    5. experiments/exp_fluctuation_dissipation_ooe_v1.py
    6. experiments/exp_hatano_sasa_v3_n8192_multiseed.py
    7. experiments/exp_large_deviations_substrate_v1.py
    8. experiments/exp_wave14_1rsb_hysteresis_v5_n4096_gpu.py
    9. experiments/exp_wave14_1rsb_hysteresis_v6_n4096.py
   10. experiments/exp_wave14_saddle_solla_v7_n4096.py
   11. experiments/exp_anchor_novel_phase_battery_v3_n8192.py (exp_name
       literal only; get_output_dir was already inherited from v1_mod
       which honors the env var)

  Verification: `python experiments/<patched>.py --self-test` exits 0 for
  all 11 scripts (run inline pre-commit).

### 2c. Scripts audited and CONFIRMED CLEAN

  (each had has_env >= 1 AND the env-var was wired into the actual output
  path -- no hard-coded literal escapes the env-var honor)

    exp_bet_b_n8192_4stage_v1.py, exp_bet_b_4stage_rehab_epochs_v3.py,
    exp_bet_b_hebb_consolidation_v1.py, exp_bid_order_parameter_v1.py,
    exp_bid_order_parameter_v2.py, exp_bid_order_parameter_v3_full.py,
    exp_bid_substrate_probe_v1.py,
    exp_cellular_automata_substrate_v1.py, exp_cellular_automata_substrate_v2.py,
    exp_drift_diffusion_bp_substrate_v1.py,
    exp_drift_diffusion_bp_v2.py, exp_drift_diffusion_bp_v3.py,
    exp_hatano_sasa_v4_glauber.py,
    exp_max_plus_algebra_substrate_v1.py,
    exp_mode_coupling_theory_substrate_v1.py,
    exp_network_percolation_substrate_v1.py,
    exp_quantum_error_correction_substrate_v1.py,
    exp_saad_solla_v9_n4096.py,
    exp_sagawa_ueda_deletion_cert_v1.py, exp_sagawa_ueda_deletion_cert_v2.py,
    exp_sagawa_ueda_deletion_cert_v3.py, exp_sagawa_ueda_v4_n8192.py,
    exp_skahm_subclass_discriminator_v2.py,
    exp_spectral_graph_lambda2_v2.py, exp_spectral_graph_lambda2_v3.py,
    exp_tcft_fresh_erase_v1.py through v4.py,
    exp_tcft_n8192_v5.py, v6.py, v7.py,
    exp_tropical_geometry_substrate_v1.py,
    exp_wave14_corpus_N_scaling_tau_unblock_v1.py,
    exp_wave14_moe_attention_routing_v1.py

  Note: exp_bid_order_parameter_v1_nsweep.py is a delegating wrapper around
  exp_bid_order_parameter_v1.py; it inherits the env-var honor via the
  parent module's get_output_dir. Confirmed safe; no patch needed.

### 2d. Scripts intentionally NOT patched

  experiments/exp_anchor_novel_phase_battery_v1.py and the SKAH-M variant
  imports of get_output_dir from v1_mod -- already correct via the parent.
  Earlier audits of older v_* sub-versions and pre-2026-04 charLM /
  wave10..13 experiments are out of scope (not active anchors today). If
  any older script is ever re-queued under a new anchor, queue_add.py's
  PROT-018 check (exit 6) and the runner's post-run validator will refuse
  the ship; the bug-class is structurally closed regardless of source.

---

## 3. PROT-019 spec

### 3a. Trigger event

  tcft_n8192_v5 (the 83rd catch). The anchor name promised N=8192 5-seed
  FULL; the script was correctly bound to N=8192 (PROT-018 satisfied);
  but the queue_add ship used --timeout 1800 (the historical default).
  The runner hit timeout at seed=41 and recorded a 4-of-5 partial. The
  metrics.json showed N=8192 (the runner's post-run validator passed),
  but the verdict was structurally wrong: a partial-seed result was
  promoted to the FULL-result slot.

### 3b. Spec

  tools/queue_add.py:check_timeout_floor():
    - Triggers on any --timeout combined with anchor name carrying
      _n<N> suffix where N >= PROT019_LARGE_N_MIN (= 4096).
    - REJECTS (sys.exit(7)) when --timeout < PROT019_TIMEOUT_FLOOR_S
      (= 3600s).
    - No-op when anchor has no _n<N> suffix or N < 4096.

  Wired into main() immediately AFTER check_n_suffix_binding (PROT-018,
  exit 6) and BEFORE the script self-test. Both gates run before any
  actual subprocess spawn.

### 3c. Exit-code map

    exit 0 -- success
    exit 1 -- generic gate failure (script not found / metrics invalid / etc.)
    exit 6 -- PROT-018 N-suffix binding violation
    exit 7 -- PROT-019 timeout-floor violation  [NEW]

### 3d. Verification (CLI smoke test)

  Reject case:
    python tools/queue_add.py local_cpu_queue test_fake_n8192_v999 \
      experiments/exp_saad_solla_v10_n8192.py \
      --prereg preregs/2026-05-27_saad_solla_v10_n8192.md \
      --timeout 1800
    -> exit 7 with [gate] PROT-019 REJECT banner. CONFIRMED.

  Pass case (in unit tests):
    check_timeout_floor("tcft_n8192_v6", 5400)  -> no exception. CONFIRMED.

---

## 4. End-to-end "runner refuses" smoke test

### 4a. Test contract

  tests/test_runner_n_suffix_validator.py::
  test_runner_refuses_mismatched_n_suffix_in_real_run

  - Stages a real metrics.json in a tempdir with the exact schema a smoke
    leak would produce: verdict=HARD_PASS, summary.N=512, config.mode=smoke.
  - Calls validate_n_suffix_binding("fake_test_n8192_v1", metrics_path).
  - Asserts:
      (1) error string is non-None (REFUSAL fired)
      (2) error starts with "n_mismatch:" (the contract token the runner
          writes into queue.json error= field)
      (3) error mentions BOTH 8192 (contracted N) AND 512 (recorded N)
      (4) error cites PROT-018

### 4b. Test results

  Total: 28 tests, 28 passed, 0 failed.

  Breakdown:
    20 baseline tests (60d2147)                                  -- all PASS
     1 end-to-end runner-refuses test (this commit)              -- PASS
     7 PROT-019 timeout-floor tests (this commit)                -- all PASS

  Command:    `python tests/test_runner_n_suffix_validator.py`
  Exit code:  0

---

## 5. Direct-invocation runner smoke test

  Two anchor names that the runner SHOULD refuse:

    name = fake_test_n8192_v1     (mismatched smoke leak)
    name = saad_solla_v9_n4096    (real anchor name from today's queue)

  Both invoked against metrics.json with summary.N=512, config.mode=smoke.

  Direct call:

    python -c "from runner_v2_prod import validate_n_suffix_binding; ..."

  Anchor 1 (fake_test_n8192_v1, N=512):
    n_mismatch: anchor _n8192 but metrics recorded N=512 mode=smoke
    (PROT-018: anchor-name _n<N> suffix is a binding contract; this run is
    NOT acceptable as the FULL N=8192 result the anchor name promises)

  Anchor 2 (saad_solla_v9_n4096, N=512):
    n_mismatch: anchor _n4096 but metrics recorded N=512 mode=smoke
    (PROT-018: anchor-name _n<N> suffix is a binding contract; this run is
    NOT acceptable as the FULL N=4096 result the anchor name promises)

  Both refused. Runner contract verified end-to-end.

---

## 6. Remaining attack-surface (post-eradication)

### 6a. Closed

  - HARD-CODED output dir literals in priority scripts          : CLOSED (11 patched)
  - Runner-side post-run N validation                           : CLOSED (60d2147)
  - verdict_handler reading stale local metrics                 : CLOSED (e51aee7)
  - queue_add accepting under-budgeted large-N ships             : CLOSED (PROT-019)
  - --allow-duplicate / --rerun-as N-suffix bypass               : CLOSED (60d2147)
  - Cross-anchor output-path collision (bet_b v1 vs v2)          : CLOSED (37f576f
                                                                    + this sweep)

### 6b. Still open / lower-priority

  1. Pre-2026-04 charLM and wave10..13 experiments may still have hard-coded
     output dirs. They are not in any active anchor / queue entry. If any
     is ever re-shipped under a new anchor name, BOTH PROT-018 (queue-side,
     exit 6) AND the runner-side post-run validator will REFUSE the ship --
     so the bug-class is structurally closed even without retroactively
     patching all 100+ old scripts. Out of scope for this commit.

  2. The verdict_handler.md prompt is the policy enforcement -- it could
     theoretically be ignored by a future agent revision that decides to
     trust local metrics. Mitigation: the prompt mandate is paired with
     the [metrics-source: ...] return-prefix contract that the orchestrator
     audits, so a regression is observable.

  3. PROT-019 floor of 3600s is a single global constant. If a future
     experiment legitimately needs N=4096 with sub-3600s timeout (e.g. a
     genuinely 60-second test), the floor can be relaxed in the spec.
     For now no such case exists and the conservative floor is correct.

### 6c. Layer summary

    LAYER 1 (queue_add):
      - PROT-018 (exit 6): refuse anchor _n<N> if script lacks N=<N> assign
      - PROT-019 (exit 7): refuse _n>=4096 anchors with timeout<3600s [NEW]

    LAYER 2 (script source):
      - HDLAB_EXP_NAME env var honored by ALL active output-writing scripts
      - get_output_dir / exp_name banner read from os.environ first
      - Self-test 5 enforces env-var honor for bet_b_n8192_4stage_v1
        (could be extended cross-script in a future hygiene pass)

    LAYER 3 (runner post-run):
      - validate_n_suffix_binding (60d2147): post-run schema check
      - Marks failed + HIGH status_log on n_mismatch

    LAYER 4 (verdict_handler):
      - get_metrics(prefer_remote=True) (e51aee7): remote-first read
      - Step 0 honest re-read mandate

  Four independent layers, all enforcing the same invariant: the anchor
  name's _n<N> suffix is a BINDING CONTRACT with the production N.
  An attempt to violate the invariant must trip at least one layer.

---

## 7. Action items (none open)

All deliverables in the user's mandate are closed:
  (1) Output-path bug sweep:           DONE  (11 scripts patched + self-tested)
  (2) PROT-019 timeout floor:          DONE  (queue_add.py + 7 unit tests)
  (3) End-to-end smoke test:           DONE  (1 new test + direct-invoke verify)
  (4) Audit doc:                       THIS FILE
  (5) HIGH-importance status_log:      DONE  (appended to
                                              data/orchestrator_status_log.jsonl)

Per feedback_no_label_vs_honest_anchor_names, feedback_ship_before_dependency_verified,
feedback_ascii_only_in_scripts, feedback_lock_in_inefficiency_fixes.


---

## 8. PROT-019 extension: per-seed checkpoint resume (2026-05-28)

### 8a. Trigger event

  Three multi-seed losses in one day:
    - saad_solla_v10_n8192:  3235s, seed=7 5/5 cells HARD_PASS clean,
                             CUDA crash at seed=17 -- ALL data lost on reship.
    - saad_solla_v18_n16384: 800s, OOM crash -- ALL seed data lost on reship.
    - tcft_n8192_v5:         1800s, 4 of 5 seeds completed, lost on retry.

  Common failure mode: multi-seed scripts aggregate seed results in an
  in-process dict and only write metrics.json AT THE END. A mid-run crash
  loses every completed seed in that run, and the reship starts from seed 0.

### 8b. Spec

  Per-seed atomic checkpoint contract:

    experiments/_seed_checkpoint.py exposes:
      list_completed_keys(out_dir)        -> list[str]
      resumable_seeds(seeds, out_dir)     -> (done, remaining)
      write_partial(out_dir, seed, body)  -> Path        # atomic
      write_partial_key(out_dir, key, body)              # for inverted loops
      load_partial_key(out_dir, key)      -> dict | None
      aggregate_partials(out_dir, seeds)  -> dict[str,dict]
      clear_partials(out_dir)             -> int

    Disk layout under data/exp_<name>/ :
      partial_metrics_<seed>.json         -- one per completed seed
      partial_metrics_<seed>.json.tmp     -- crash residue (ignored)
      metrics.json                        -- final aggregate

    Script adoption pattern (outer-loop seed):
      done, remaining = resumable_seeds(seeds, out_dir)
      for seed in remaining:
          r = run_one_seed(seed, ...)
          write_partial(out_dir, seed, r)        # atomic .tmp + os.replace
      per_seed = aggregate_partials(out_dir, seeds)

    Inverted-loop variant (outer = N or M, inner = seed):
      cell_key = f"N{N_val}_seed{seed}"
      if cell_key in list_completed_keys(out_dir): continue
      r = run_one_cell(N_val, seed)
      write_partial_key(out_dir, cell_key, {"N": N_val, "cell": r})

### 8c. Atomicity guarantee

  Writes go to <name>.json.tmp first, fsync()ed, then os.replace()d to the
  final name. os.replace is atomic on both POSIX (within filesystem) and
  Windows (NTFS overwrite). A crash mid-write leaves the .tmp orphan but
  the .json never half-formed.

  Recovery scan validates each partial_metrics_<seed>.json by:
    1. json.load succeeds (not truncated)
    2. top-level is dict
    3. recorded "seed" field matches filename
  Any failure -> the seed is treated as not-done and re-runs.

### 8d. Retrofitted scripts (2026-05-28 first pass)

  - experiments/exp_saad_solla_v15_n8192_5seed.py      (5 seeds at N=8192)
  - experiments/exp_saad_solla_v18_n16384.py            (2 seeds at N=16384)
  - experiments/exp_tcft_m_sweep_v3_n8192_5seed.py      (5 seeds at N=8192)
  - experiments/exp_bid_n_stability_v4_n12288.py        (inverted loop)

  These are the high-rerun scripts that experienced losses today. Retrofit
  is a small mechanical edit (~10 lines per script): import the helper,
  scan for done seeds at top of run(), write partial after each seed,
  aggregate at the end. The remaining ~50 multi-seed scripts can be
  retrofitted in a separate pass when they next get re-shipped or
  modified -- the helper is reusable.

### 8e. Tests

  tests/test_seed_checkpoint.py (21 tests, all pass):
    Empty dir / nonexistent dir   -- all seeds remain (2 tests)
    Partial dir with N of M done  -- only remaining run (3 tests)
    Atomicity / crash recovery    -- .tmp residue ignored, corrupted
                                      partials re-run (5 tests)
    Write / load round-trip       -- payload fidelity (5 tests)
    Aggregate                     -- {seed: payload} dict (3 tests)
    clear_partials                -- cleanup utility (2 tests)
    End-to-end resume scenario    -- run 1 crashes after 2 seeds, run 2
                                      resumes and completes (1 test)

  Run with: python -m pytest tests/test_seed_checkpoint.py -v

### 8f. Implication for timeout budgeting

  Before: a 5-seed run with a 14400s budget that crashes at seed 4 wastes
  all 14400s (and all 4 completed seeds) on the reship.

  After: the same crash wastes only the in-flight seed. Reship has 1 seed
  of remaining work -- nominally 14400/5 = 2880s of compute, even if the
  reship is granted the full original budget.

  Timeout budgets become effectively PER-SEED budgets across the
  crash-and-resume sequence. A 5-seed 24h run tolerates up to 4 crashes
  (each consuming one seed's worth of work) before the budget is
  exhausted -- a 4x effective reliability multiplier for the
  CUDA-crash-prone large-N regime.

  NOTE: the 21600s / 14400s PROT-019 floors are still required for
  FRESH-RUN safety (no partials present). They are not lowered. The
  checkpoint contract is a recovery accelerant, not a budget shrinker.

### 8g. Remote-git divergence dependency

  These scripts must be propagated to the GPU/CPU runner hosts before the
  resume contract is live in production. The runner-pickup invariant is
  "next ship uses the new code AFTER the remote-git divergence is
  resolved". The helper file is self-contained and adds no new runtime
  deps (stdlib json/os/re/time only) -- propagation is a single git
  fetch + checkout on each runner host.
