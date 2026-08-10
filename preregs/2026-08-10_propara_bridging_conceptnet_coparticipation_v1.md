# Pre-registration: exp_propara_bridging_conceptnet_coparticipation_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator REUSE-vs-BUILD check-before-build
probe, following the real-KB go/no-go (NO-GO, survival 0.22: generic verb-lexicon + SRL + coref
structurally cannot source co-participation; the missing component is participant-role
co-participation world-knowledge). Decides: does an EXISTING KB (ConceptNet) supply it?

## Prior-work check (SUBSTRATE-KB)
Same arc (top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). Direct follow-up on the
real-KB cell's landed NO-GO; novelty inherited. Reuses the local ConceptNet 5.7.0 dump
(data/conceptnet/conceptnet-assertions-5.7.0.csv.gz), not re-sourced.

## The question
Does ConceptNet supply the co-participation knowledge SRL structurally cannot (link an unmentioned
participant to the process/other-entities at its change step)? GO -> REUSE ConceptNet for the KB
foundation; NO-GO -> the foundation must be BUILT (distilled process-physics KB).

## One clean variable
+ ConceptNet co-participation sourcing, added to the real-KB cell. Loop + all controls identical.
Computed in ONE run: without / with_oracle / with_real_generic (SRL+coref, the prior 0.22) /
with_real_cn (SRL+coref + ConceptNet) / prior_lesion.

## ConceptNet co-participation sourcing (NO gold)
Preprocessing: `tools/benchmark_trap_check/build_propara_conceptnet_index_v1.py` scanned the full
ConceptNet 5.7.0 dump ONCE (34M edges, 64s) -> ProPara-scoped index
(data/benchmark_trap_check/propara_conceptnet_index_v1.json): 1230 ProPara-vocab terms ->
[(relation, other_term, weight)], for co-participation relations. In-cell: at a step whose trigger
verb V (class -> effect E via the generic rule) has SRL surface argument-tokens A, EXPAND A over
CO_PART_RELS (PartOf/MadeOf/HasA/UsedFor/ReceivesAction/IsA/DerivedFrom/FormOf/Synonym/SimilarTo/
HasSubevent/Causes; loose RelatedTo/AtLocation excluded). If an UNMENTIONED participant p is
ConceptNet-linked to a surface entity in A, bind p as co-participant and emit the fact (E, V).
Targets exactly the SRL gap (generic pair_recall 0.235). ConceptNet FILLS the gap, does not
replace the verb-class->effect lexicon.

## Residual oracle dependency (flagged)
Event-COUNT budget only (granted to all arms, as before). Bridge FACTS in with_real_cn are 100%
real-sourced (generic semantics + SRL + coref + ConceptNet).

## Metric + decisive measurement
PRIMARY = per-step change-label macro-F1 on the UNMENTIONED subset. **SURVIVAL_CN =
(with_real_cn - without)/(with_oracle - without)** vs the generic 0.22. Reported: survival_cn,
survival_generic, cn_minus_generic; ConceptNet fact pair_recall/precision vs oracle (did it fix
0.235?); ConceptNet DOMAIN COVERAGE (for each gold unmentioned change, does ConceptNet link the
affected participant to any surface entity at that step? covered vs missed, with missed examples --
the scientific-domain coverage gap); cn binding stats (cn-only bindings); official metric (context).

## Survival bar (pre-registered BEFORE running)
- `SURVIVAL_HARD_PASS = 0.50`: with_real_cn recovers >= 50% of the oracle lift AND cn adds >=
  `CN_MUST_ADD_OVER_GENERIC = 0.05` survival over generic -> **HARD_PASS_REUSE_CONCEPTNET (GO:
  REUSE ConceptNet, build the foundation on it)**.
- `SURVIVAL_HARD_FAIL = 0.30`: survival_cn < 0.30 OR cn adds < 0.05 over generic ->
  **HARD_FAIL_CONCEPTNET_INSUFFICIENT (NO-GO: BUILD a distilled process-physics KB, not REUSE)**.
- MIDDLE_BAND = partial (0.30-0.50).
- Guards (same as prior cells): ablation must collapse (WITHOUT < 0.60, else void), no-leak
  (with_real_cn < 0.95), arms_differ, decode >= 0.99 all five arms.

## HP_SCOPE
`{conceptnet: [survival_cn_material, cn_adds_over_generic, cn_ablation_collapses, no_leak]}`.

## Cell-template mandates
arms_differ (asserted self-test + recorded); final_metrics_atomicity tmp_replace; except SystemExit
before except Exception (grep-verified); crlb_n/a; calibration_check default_ok; deterministic_seeding
(hashlib-seeded rng, no Python hash()/list(set())); progress_logging print_flush_true.

## Compute architecture
Sequential-CPU, justified: ConceptNet index built offline (one-time gz scan, 64s); the cell loads
the small JSON + reuses the diagnostic precompute (spaCy parse + coref) + CN expansion + firing +
FHRR decode. No batching. MEASURED self-test 0.5s. Expect smoke ~40-70s, full ~50-100s. Run
INLINE/LOCALLY foreground.

## Self-test findings (real code path)
**MEASURED@..._metrics.json (self_test, 0.5s):** CN index 1224 co-participation terms. On a synth
where "plants" is UNMENTIONED at "the fire consumes the material" (surface entity = material),
ConceptNet plants<->material link binds plants as co-participant -> sources (DESTROY, DESTROY) that
generic SRL MISSES (generic only sources CREATE). 1 cn-only binding; 3 verdict-logic unit checks
correct (go HARD_PASS / no_go HARD_FAIL / void HARD_FAIL). Confirms the probe isolates the
ConceptNet contribution.

## Smoke findings (DEV)
**MEASURED@..._smoke/metrics.json (dev):** survival_cn 0.037 vs survival_generic 0.134 (cn_add
-0.097 -- ConceptNet HURT on dev); cn_pair_recall 0.333 (up from generic 0.143), cn_domain_coverage
0.551; ablation collapsed, no leak. -> NO-GO on DEV (ConceptNet raised fact-recall but the noisy
links hurt net localization). Bar pinned before TEST.

## Full findings (TEST) -- the REUSE-vs-BUILD verdict: NO-GO on REUSE -> BUILD a process-physics KB
**MEASURED@data/exp_propara_bridging_conceptnet_coparticipation_v1/metrics.json (test, unmentioned
subset n=1119; run_mode=full, cardinality_ok, arms_differ True, decode 1.0 all five arms). Verdict:
HARD_FAIL_CONCEPTNET_INSUFFICIENT_BUILD_NOT_REUSE.**

UNMENTIONED macro-F1: prior_lesion 0.318, WITHOUT 0.356, with_real_generic 0.380, **with_real_cn
0.380**, with_oracle 0.463.
- survival_generic = 0.221, **survival_cn = 0.223, cn_add = +0.002** (negligible -- ConceptNet added
  essentially NOTHING to the survival). Both far below the 0.50 GO bar.

**WHY (the precise mechanism -- ConceptNet has coverage but not USABLE co-participation):**
- Fact coverage: generic pair_recall 0.235 -> **+CN pair_recall 0.321** (ConceptNet DID find more of
  the oracle facts), but pair_precision 0.096 -> **0.085** (stayed low / dropped). ConceptNet added
  174 co-participation bindings (99 participants got a CN-only link) -- raising recall -- but they
  are PROMISCUOUS generic-association links (PartOf/IsA/HasA/Synonym/...), not process-specific
  causal co-participation, so the extra recall is exactly cancelled by the extra noise -> net
  survival contribution ~0.
- Domain coverage: ConceptNet links the affected participant to a step surface entity for only
  **48% (50/104)** of unmentioned changes. The MISSED 52% are EXACTLY ProPara's scientific
  processes (MEASURED missed examples): plant/animal <- [mud, silt] (fossilization); bones <-
  [hardens, rock, sediment, time] (mineralization); soil <- [rock, time] (weathering); water <-
  [material, peat] (peat formation); electrochemical signals <- [brainstem, colliculus, eyes]
  (neural signaling); fixed/usable nitrogen <- [animals, plants, waste] (nitrogen cycle). Everyday-
  commonsense KBs do not encode which participant a SCIENTIFIC PROCESS consumes/produces/moves.

**Official (full set, context):** with_real_cn 0.669 ~= generic 0.669 ~= without 0.671, below
prior_lesion 0.722 -- lift concentrated in the unmentioned residual, as before.

**REUSE-vs-BUILD VERDICT: BUILD, not REUSE.** An existing KB (ConceptNet 5.7.0) does NOT supply the
co-participation knowledge SRL missed: it has partial coverage (48%, recall lifted to 0.32) but its
links are too promiscuous (precision 0.085) to convert into usable bridging, and it structurally
MISSES ProPara's scientific-process co-participations (fossilization / mineralization / weathering /
nitrogen cycle / neural signaling). Net survival contribution is ~0 (0.221 -> 0.223). This
QUANTIFIES and CONFIRMS the earlier WIQA-arc caution (CSKG/ConceptNet weak on ProPara's scientific
domain). -> The co-participation knowledge foundation must be BUILT: a distilled, process-physics-
specific co-participation KB (LLM-distilled offline + vetted per the 2026-07-14 foundation pivot:
foundation = any external tool full+vetted, runtime reasoning glass-box), NOT reused off-the-shelf.
The mechanism (loop) and the generic verb-class->effect lexicon are validated; the single remaining
foundation component is the process-specific co-participation KB.
