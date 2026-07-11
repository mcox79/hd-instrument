# Pre-registration: gt_rankfair_fb15k237_lowmid_v2

HD/feature-rich RANKER of already-reached candidates on the FAIR (low+mid degree) stratum of
FB15k-237. Tests whether a NON-SYMBOLIC discriminative signal (substrate HD-code cosine +
relation-type consistency, with a brain-DDM capped-frequency architecture) converts the reasoner's
own reach into a result that beats the frequency baseline where pure-symbolic ranking cannot.

- **Cell**: `experiments/exp_gt_rankfair_fb15k237_lowmid_v2.py`
- **Anchor**: `gt_rankfair_fb15k237_lowmid_v2`
- **Corpus**: FB15k-237 standard split at `data/fb15k237_testbed/` (train 272115 / valid 17535 / test 20466).
- **Filed**: 2026-07-10 by hdi_exp_dev. Redirect after VET ad72003c + brain drill
  `notes/research_brain_beats_frequency_relational_inference_deep_drill_2026-07-10.md`.

## Prior-work check (concept-query before authoring)
`bash tools/substrate_query.sh "popularity residualization rank confidence frequency empirical bayes
smoothing relation"` top hit cosine 0.345 (framenet Condition_symptom_relation::Frequency) -- NOT a
prior ranker cell. No prior arc cell at cosine>0.30 is a KG-ranker-vs-frequency test. Direct lineage:
`gt_rankfair_fb15k237_lowmid_v1` (this cell's parent, HARD_FAIL: 7 symbolic rankers all lose to POP),
`crux_engine_v2_resonator_decode_v1` (the HD signal reused here; cond_mrr 0.464 > symbolic 0.404).
**Verdict: continuation of the rankfair arc, NOT a rediscovery** -- first cell adding a NON-symbolic
(HD-code + relation-type) discriminative ranker with the brain-DDM capped-frequency architecture.

## Why (VET ad72003c refuted the v1 premise)
The 7 symbolic rankers are ALREADY frequency-orthogonal (Spearman(score,tail_freq)=0.23,
(score,degree)=0.02; over-ranked candidates out-frequency gold only 52.7% = coinflip). Residualizing
frequency adds nothing. The true diagnosis: pure-symbolic path-support is NON-DISCRIMINATIVE for gold
vs co-reached distractors (gold sits at the feature-median). BUT a perfect ranker on the reasoner's
OWN reached sets scores 0.424 vs POP 0.256 = +0.164 exploitable headroom. The fix must add
NON-SYMBOLIC discriminative features. CITED@VET ad72003c relay + MEASURED@data/exp_gt_rankfair_fb15k237_lowmid_v1_smoke/metrics.json.

## Arms (all ranked over the SAME reached candidate set unless noted)
- **POP** -- per-relation tail frequency, ranked over ALL entities. Baseline to beat.
- **FREQ_LEAK = POP_REACHED** -- tail frequency ranked over the reached set only. Doubles as the
  apples-to-apples popularity baseline AND the must-fail leak control. FAIR_POP = max(POP, FREQ_LEAK).
- **SYM_BASE + 6 panel** (add_g05_b0, add_g10_b0, max_conf, rule_count, noisyOR_rule, add_g05_b03) --
  symbolic context (BEST_FAIR = max). Adjacency-only.
- **RESID_CONF** -- EB-smoothed per-(relation-type,rule-length) confidence, popularity-residualized
  (OLS within reached set). CONTROL: expected FLAT (confirms the VET -- residualization adds nothing).
- **HD_RANK** -- substrate HD-VSA matched-filter cosine between a query-composed FHRR bundle
  (bind head-relation-paths, unbind readout; crux primitives reused) and each candidate's entity code.
- **TYPE_RANK** -- relation-type consistency: mean compatibility of the candidate's tail-relation
  profile with relation r's expected tail-type profile W[r][r'] = P(r'-tail | r-tail), derived from
  train adjacency (glass-box, no external type labels; mean-normalized -> decoupled from popularity).
- **HD_TYPE** -- z(HD) + z(TYPE) within reached set (combined structural evidence).
- **HD_TYPE_CAPPOP** -- brain-DDM architecture: z(HD) + z(TYPE) + POP_CAP * clip(z(pop), -1, 1),
  POP_CAP=0.5. Structural evidence UNCAPPED drift; frequency a BOUNDED starting-point nudge.
- **HD_TYPE_POP_UNCAP** -- same with an UNCAPPED z(pop) term (capped-vs-uncapped architecture test).
- **SCRAMBLE** -- add_g05_b0 scores permuted across reached set. Must-fail #1.
- **SHUF_RELLABEL** -- RESID_CONF with per-relation EB priors shuffled across relations. Must-fail #2.
- **SHUF_TYPELABEL** -- TYPE_RANK scored against a shuffled (wrong) relation's expected type. Must-fail #3.

BEST_STRUCT = max over {HD_RANK, TYPE_RANK, HD_TYPE, HD_TYPE_CAPPOP} (headline).

## Fairness-hardening (USER standing directive)
- LOW-only stratum (POP weakest ~0.11 = truly-fair arena) AND low+mid stratum both reported.
- Apples-to-apples: FAIR_POP = max(POP-all, FREQ_LEAK/POP-reached) -- the stricter bar; the reached-set
  restriction can only HELP a freq guesser, so BEST_STRUCT must beat FAIR_POP not just POP.
- Degree-stratified: low / mid / low+mid / high (high = unfair saturation contrast, POP ~0.97).

## Pre-registered bands (low+mid PRIMARY, low-only co-primary; META_RULE_L strict-above-floor)
HARD_PASS (ALL):
- BEST_STRUCT beats FAIR_POP on low-only OR low+mid: (h@10 - FAIR_POP_h@10 >= 0.02) OR
  (mrr - FAIR_POP_mrr >= 0.01), AND BEST_STRUCT > FREQ_LEAK on that winning stratum (freq not the mechanism)
- SCRAMBLE does not beat POP on low+mid (SCR_h@10 <= POP_h@10 + 0.01)
- SHUF_RELLABEL does not beat POP by pass-margin on low+mid (< POP_h@10 + 0.02)
- SHUF_TYPELABEL does not beat POP by pass-margin on low+mid (< POP_h@10 + 0.02)
- BEST_STRUCT h@10 <= per-stratum reach ceiling (fair-bounded); arms differ
HARD_FAIL (ANY):
- BEST_STRUCT does NOT beat FAIR_POP (h@10 AND mrr) on EITHER fair stratum -> even HD/feature-rich
  ranking cannot beat frequency on the fair stratum -> the CORPUS (a378f27) is the lever, not the
  ranker. Clean, decisive negative (deflated P ~0.28-0.35).
- SCRAMBLE beats POP on low+mid OR arms identical
Anything between = MIDDLE_BAND.
RESID_CONF reported (resid_conf_flat = RESID_CONF_h@10 <= FAIR_POP_h@10 + 0.02 on low+mid) to CONFIRM
the VET; not gated.

## SCHEMA-VET fields
- cell_chunked: false (3 seeds in-cell; symbolic+small-HD, per-seed <1min, low zombie risk)
- start_marker_written: true ; crash_diagnostic_present: true ; heartbeat_present: true (per-seed)
- defensive_error_checking: passed_all_4_patterns
- final_metrics_atomicity: tmp_replace (write_metrics + crash-writer os.replace)
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (verdict counts per_seed)
- arms_differ_verified: true (POP/SCR/SYM_BASE/add_g05_b0/RESID_CONF/HD_RANK/TYPE_RANK/FREQ_LEAK hashes distinct)
- discriminating: baselines in band (POP low+mid 0.256, low 0.112; high POP 0.97 saturated contrast);
  discriminator fires (5 self-tests D_SYM/D_HD/D_RES/D_LEAK/D_TYPE; smoke arms distinct + must-fails all fire)
- discriminator_survives_scale: N_DIM=2048 (crux-validated) + full rule-mining params in BOTH smoke and
  full; only N_EVAL reduced in smoke (800 vs 3000)
- crlb_n/a: symbolic + HD matched-filter + type-profile rank test; info-ceiling = per-stratum reach (reported)
- calibration_check: default_ok_for_this_regime (MIN_SUPPORT/MIN_CONF from Step-1; N_DIM/M_SMOOTH/POP_CAP declared)
- progress_logging: print_flush_true (per-seed print + heartbeat.jsonl; flush=True everywhere)
- compute_architecture: mixed-CPU (torch 2.12.0+cpu, cuda=False -> remote_cpu_queue); HD ops vectorized
  over the small reached set; entity codebook 14541 x 2048 complex64 (~238MB) built once per seed

## Self-test discriminators (ALL must fire; verified locally)
D_SYM (add-dedupe promotes low-mult gold over grounding-hub + scramble + no-leak);
D_HD (bind recovers planted 2-hop gold, bind margin 0.360 >> add-ablation 0.014 = bind load-bearing);
D_RES (popularity-residualization promotes a freq-orthogonal gold raw confidence buries);
D_LEAK (shuffled-relation prior changes eb_conf; FREQ_LEAK tracks frequency);
D_TYPE (type-consistency GOLD 1.0 > WRONG 0.0; shuffled-relation type sep -1.0 = type-specific).

## Smoke (1 seed, N_EVAL=800, full N_DIM/rule params) -- MIDDLE_BAND, discriminator fires
MEASURED@data/exp_gt_rankfair_fb15k237_lowmid_v2_smoke/metrics.json:
LOW-only POP h@10=0.112 mrr=0.049 | BEST_STRUCT h@10=0.108 mrr=0.053 (TYPE_RANK) -- ties/edges POP on
mrr, just below h@10. low+mid POP h@10=0.256 | BEST_STRUCT 0.121 (HD_RANK). All must-fails FIRE
(scramble_fails, shuf_rel_fails, shuf_type_fails, arms_differ all True); resid_conf_flat True (VET
confirmed). TYPE_RANK is the strongest structural signal on the fair stratum -> FULL (3 seeds,
N_EVAL=3000) resolves the LOW-only boundary (~266 low queries in smoke -> ~1000/seed at FULL).

## Dispatch
SMOKE (local) = PASS (discriminator fires, must-fails fire, MIDDLE_BAND near-boundary). FULL -> 3 seeds,
N_EVAL=3000, remote_cpu_queue (CPU-only torch; no GPU). timeout 1800s.
