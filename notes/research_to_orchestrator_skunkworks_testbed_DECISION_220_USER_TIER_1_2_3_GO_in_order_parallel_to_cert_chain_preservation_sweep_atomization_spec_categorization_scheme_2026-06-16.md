# Research (Director) -> Orchestrator + Skunkworks + Testbed + Exp-Dev: DECISION 220 -- USER confirms ALL 3 TIERS GO in order + parallel to cert chain + distinct kind:* for experiments + categorization scheme by knowledge-relevance-tier. TIER 1 (preservation; Orchestrator dispatch NOW) update .gitignore + bulk-add data/<exp>/metrics.json + results.json + provenance.json + commit + push. TIER 2 (atomization; Skunkworks dispatch parallel) author categorization scheme + kind:METHODOLOGY_RULE + kind:AUDIT_LESSON atom spec per option (c) confirmed. TIER 3 (Phase D prep; Exp-Dev dispatch low-priority) author tools/atomize_experiment_records.py substrate-internal atomizer script. USER constraint: do NOT derail current P1 cert chain progression. Categorization scheme: Tier-A always-load-bearing (METHODOLOGY/AUDIT/CAPABILITY/FINDING/FOUNDATION) + Tier-B selectively-load-bearing (EXPERIMENT_RECORD with relevance_tier + DECISION_RECORD with decision_class) + Tier-C historical-archive (HONEST_SIGNAL_RECORD + COMMUNICATION_RECORD). Distinct data objects via kind:* + relevance_tier filter prunes archaeology from Tier-A/B searches.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~19:51
**Re:** USER 3-tier + categorization confirmed; parallel-to-cert-chain dispatch.

## ACK USER strategic confirmations

```
USER (2026-06-16 ~19:50):
   "I think all three tiers in order"
   "Will there be a different data object for the experiments?"
   "How do we keep track of things that are knowledge but are related to
    substrate's creation / important to future improvement vs things that
    have nothing to do with it (like history etc)"
   "I don't want this to derail the current work though"

Director resolves:
   1. ALL 3 TIERS GO in order: Tier 1 (preservation) -> Tier 2 (atomization
      per (c)) -> Tier 3 (experiment-record archive atomizer)
   2. YES distinct data objects via kind:* differentiation (see categorization
      scheme below)
   3. Categorization by relevance-tier filters knowledge from history in
      automated queries
   4. PARALLEL to cert chain; this DECISION dispatches Tier 1 + Tier 2 NOW
      without interrupting P1 STEP-8/9 + P2 prereg DESIGN + STEP-7 VET reactive
   5. Tier 3 deferred (script authorship low-priority; not blocking)
```

## DECISION 220 -- Knowledge categorization scheme (substrate-wide)

```
Tier-A (ALWAYS load-bearing for substrate improvement; every automation
   query checks Tier-A first):

   kind:METHODOLOGY_RULE       (24 frozen; HOW substrate is built)
   kind:AUDIT_LESSON           (91 candidates today; HOW substrate
                                self-corrects)
   kind:CAPABILITY             (already exists; WHAT substrate can do)
   kind:FINDING                (already exists; WHAT substrate has measured)
   kind:FOUNDATION             (existing primitives + theorems like CRT;
                                WHAT substrate stands on)

Tier-B (SELECTIVELY load-bearing; queried when relevant to current question):

   kind:EXPERIMENT_RECORD with relevance_tier field:
      HIGH:    discovered a capability / new primitive / atomized finding
               (load-bearing experiments)
      MEDIUM:  produced honest-negative or honest-bounded result; shaped
               strategy (instructively informative)
      LOW:     confirmed-expected outcome (replication / sanity)
      ARCHIVE: redundant with another HIGH/MEDIUM experiment

   kind:DECISION_RECORD with decision_class field:
      STRATEGIC: USER calls + phase boundaries + scope decisions
      OPERATIONAL: cert-chain steps + dispatch decisions
      ROUTINE: heartbeat-style status + acks

Tier-C (HISTORICAL ARCHIVE; queryable for archaeology; not load-bearing
   for invention):

   kind:HONEST_SIGNAL_RECORD    (254+ signals today; chronological log)
   kind:COMMUNICATION_RECORD    (inter-session notes graph)

Query discipline:
   - Capability invention / cert authoring: query Tier-A always
   - Hypothesis-formation / experiment-design: query Tier-A + Tier-B (HIGH/MEDIUM)
   - Pattern-recognition / cross-experiment analysis: query Tier-A + Tier-B all
   - Archaeology / "when did we decide X": query Tier-C explicitly
   - Default automation behavior: Tier-A first; Tier-B-HIGH on close-context;
     Tier-C only on explicit archaeology request

Substrate-internal-first per 11th rule: all atomization deterministic;
   classification by deterministic rules (e.g., decision_class STRATEGIC if
   tag contains USER_call or phase_boundary; relevance_tier HIGH if linked
   to a CAPABILITY or FOUNDATION atom; etc.); NO LLM in classification.
```

## DECISION 220a -- Tier 1 preservation sweep DISPATCH (Orchestrator NOW)

```
Orchestrator: PARALLEL to cert chain monitoring (DECISION 215 active);
   USER loss-concern is urgent; dispatch immediately:

   STEPS:

   1. Audit current .gitignore for data/ exclusion patterns:
      Current: data/* (with carve-outs for specific files)
      Result: 127 data/ files tracked / 1968 data/ subdirectories
              -> ~94% of raw experimental measurements NOT in git

   2. Update .gitignore to include load-bearing data files by glob pattern:
      Add BEFORE the data/* exclusion (or use negation patterns):
         !data/*/metrics.json
         !data/*/results.json
         !data/*/provenance.json
         !data/*/verdict.json    (if present)
         !data/*/recent_verdicts.json    (if present)
         !data/audit/             (already tracked; verify pattern stays)
      KEEP excluded:
         data/*/  (the subdirectories themselves are present anyway)
         data/*/model_weights.* (large; not load-bearing for invention)
         data/*/*.npy           (raw tensor dumps; usually large)
         data/*/*.pkl           (pickled artifacts; large + unsafe)
         data/*/cache/          (transient)
         data/*/__pycache__/    (Python bytecode)
         data/.event_bus.lock
         data/event_bus_*.log   (transient logs)

   3. Bulk-add the previously-untracked metrics + results + provenance:
      git add data/*/metrics.json data/*/results.json data/*/provenance.json
      git status to verify scope (should reveal ~1800 newly-tracked files)
      Spot-check 3-5 specific files for content (no large model weights
         accidentally tracked; no secrets)

   4. Commit + push:
      git commit -m "Tier 1 preservation sweep: bulk-add data/<exp>/{metrics,
         results,provenance}.json across ~1934 historical experiments
         (DECISION 220 USER loss-concern)"
      git push origin main
      Verify GitHub web shows the commit + new file count

   5. Report back to Research (Director):
      - Bytes added to git
      - Files newly tracked count
      - Push confirmation
      - Any unexpected exclusions or oversized files flagged

   6. Light-rate-limited: this is ONE big commit; do not over-fragment;
      target wall-clock ~15-30 min total.

   YOU ARE GATING: substrate-wide preservation completion for USER
   loss-concern + Tier 2/3 atomization downstream (Testbed needs git-
   present metrics.json for substrate-internal atomization).

   DOES NOT INTERRUPT: cert chain (P1 STEP-9 / P2 prereg DESIGN are
   independent of this sweep).
```

## DECISION 220b -- Tier 2 atomization spec DISPATCH (Skunkworks parallel)

```
Skunkworks: PARALLEL to your DECISION 215 work (P2 prereg DESIGN + STEP-7
   VET reactive + post-write VET); USER (c) confirmed; light spec authoring
   ~30 min wall-clock:

   STEPS:

   1. Author kind:METHODOLOGY_RULE atom spec:
      - 24 FROZEN rules (USER-LOCKED + Director-introduced)
      - Atom template:
         math:: or concept:: T1/METHODOLOGY_<short_name>
         kind: methodology_rule
         metric_type: (none; not measured)
         description: full rule text
         rule_class: USER_LOCKED / DIRECTOR_INTRODUCED / SUBSTRATE_DERIVED
         provenance: source DECISION + date + USER_LOCKED flag
         DEPENDS_ON: (foundational; no edges OR composes_with relations
                      to other rules)
      - Determine corpus (math vs concept)
      - Tier (T1 foundation? or T2 process-tier?)
      - 11th-rule clean: substrate-internal deterministic authoring

   2. Author kind:AUDIT_LESSON atom spec:
      - 91 candidates today (88 confirmed + 3 candidates: 89th/90th/91st;
        also 92nd just filed today via Testbed pre-ratify catch)
      - Atom template:
         math:: or concept:: T2/AUDIT_LESSON_<short_name>
         kind: audit_lesson
         metric_type: (none; not measured)
         description: full lesson text + composes-with relationships
         lesson_class: VERIFY_DISCIPLINE / TYPE_DISCIPLINE / CERT_CHAIN /
                       INTEGRATOR_DISCIPLINE / etc.
         confirmed_or_candidate: CONFIRMED / CANDIDATE
         witnesses_count: number of independent witnesses
         provenance: first-witness source + composes-with prior lessons
         DEPENDS_ON: composes_with relations to related lessons + the
                     specific instances that triggered the lesson

   3. Author kind:EXPERIMENT_RECORD atom spec (for Tier 3 atomizer to use):
      - Field schema:
         atom_id: math:: T3/EXP_<short_name> or concept::
         kind: experiment_record
         experiment_path: experiments/<cell.py>
         prereg_path: preregs/<prereg.md> (if exists)
         metrics_path: data/<exp>/metrics.json
         cell_sha: git commit SHA at run time
         remote_run_id: orchestrator-assigned (if remote)
         hypothesis: extracted from cell prose or prereg
         verdict: PASS / HARD_FAIL / HONEST_NEGATIVE / HONEST_BOUNDED /
                  MIDDLE_BAND / LOAD_BEARING / etc.
         relevance_tier: HIGH / MEDIUM / LOW / ARCHIVE
            (derived: HIGH if linked to atomized CAPABILITY/FINDING;
                      MEDIUM if HONEST_NEGATIVE/BOUNDED in cell-internal;
                      LOW if confirmed-expected; ARCHIVE if redundant)
         DEPENDS_ON: primitives_used (T1/T2 atom references) +
                     capabilities_tested
         provenance: cell SHA + metrics SHA + date + session_authored

   4. Author kind:DECISION_RECORD + kind:HONEST_SIGNAL_RECORD +
      kind:COMMUNICATION_RECORD schemas (lighter; for Tier 3 script to use)

   5. Submit specs to Testbed for pre-receive verification (per 66th-rule
      integrator pre-scan discipline; catch any phantom-dep or schema-drift
      BEFORE Tier 3 atomizer runs)

   6. Report back to Research (Director) for ratify -> Testbed ingest

   YOU ARE GATING: Tier 2 atomization completion + Tier 3 atomizer script
   schema (Exp-Dev needs your specs to author the atomizer correctly).

   DOES NOT INTERRUPT: P2 prereg DESIGN authoring + STEP-7 VET reactive
   (your primary cert-chain work continues; this is parallel scope authoring).
```

## DECISION 220c -- Tier 3 atomizer script DEFERRED (Exp-Dev low-priority)

```
Exp-Dev: Tier 3 experiment-record archive atomizer script:

   tools/atomize_experiment_records.py
      - Walks experiments/ + data/ + preregs/ for matched (cell.py,
        metrics.json, results.json, provenance.json, prereg.md) tuples
      - Extracts hypothesis (from cell docstring or prereg)
      - Extracts verdict (from cell-internal verdict tree OR post-hoc
        deterministic from metrics)
      - Derives relevance_tier deterministically:
         HIGH if cell's atom-write linked to an atomized CAPABILITY/FINDING
         MEDIUM if cell's verdict is HONEST_NEGATIVE/BOUNDED/MIDDLE_BAND
         LOW if cell's verdict is PASS-confirming-expected
         ARCHIVE if cell is duplicate-experiment-with-same-hypothesis-result
      - Builds kind:EXPERIMENT_RECORD atom per Skunkworks's spec
      - Batched commits (e.g., 50-100 atoms per batch; cap_pres=1.0
        verified between batches)
      - 11th-rule clean: deterministic; no LLM in any classification

   STATUS: LOW priority; not blocking Phase C; defer authorship until:
      (i) Skunkworks completes Tier 2 specs (Testbed verified)
      (ii) Tier 1 preservation sweep complete (Orchestrator committed)
      (iii) P1 atom ratified (current cert chain complete)

   Estimated authorship: 1 substantive cycle (~1-2 days);
   Estimated run time over full archive (~3000 experiments at ~5-10
   sec/experiment + cap_pres verification + batched commits): days to
   weeks running in background.

   NOT BLOCKING Phase C; defer until Phase C TIER-3 foundation complete.
```

## DECISION 220d -- USER constraint NOT-DERAIL enforced

```
USER constraint: "I don't want this to derail the current work"

Director enforces via parallel sectoring:

   ACTIVE THREAD 1: P1 cert chain (DECISIONS 218 + 219 active):
      - STEP-7 Exp-Dev results-read FILED (will process post-this-DECISION)
      - STEP-7 Skunkworks VET reactive
      - STEP-8 Director ratify endorses Option B per DECISION 219
      - STEP 9.1 Testbed authors T1/chinese_remainder_theorem
      - STEP 9.2 Testbed ratifies residue_fpe_encoding HONEST_BOUNDED

   ACTIVE THREAD 2: P2 prereg DESIGN (DECISION 215 PARALLEL):
      - Skunkworks active authoring
      - Exp-Dev ref-impl active
      - Continues independent of THREAD 1 + 3

   ACTIVE THREAD 3 (NEW per DECISION 220): Tier 1 + Tier 2 dispatch:
      - Orchestrator preservation sweep (Tier 1) ~15-30 min wall-clock
      - Skunkworks Tier 2 atomization spec authoring (parallel to P2 +
        STEP-7 VET reactive)
      - Independent of THREAD 1 + 2; can interleave

   Tier 3 (atomizer script): DEFERRED to post-Phase-C-TIER-3-complete;
      not dispatched in this DECISION

   NO INTERRUPTION of cert chain. All sessions retain their primary
   reactive duties; parallel work is additive not substitutive.
```

## Pipeline state (post-DECISION-220)

```
PHASE C TIER-3 ARC (cert chain on its own thread; this DECISION parallel):
   P1: STEP-7 results-read filed; STEP-7 VET reactive; STEP-8 endorses
       Option B; STEP-9.1 + 9.2 Testbed authoring
   P2: prereg DESIGN active (Skunkworks); ref-impl active (Exp-Dev);
       simplex-correlation diagnosis as known constraint
   P3: GHRR DEFERRED

USER 3-TIER STRATEGIC DISPATCH (this DECISION; parallel):
   TIER 1: Orchestrator preservation sweep DISPATCHED NOW
   TIER 2: Skunkworks atomization spec authoring DISPATCHED parallel
   TIER 3: Exp-Dev experiment-record atomizer script DEFERRED (post-Phase-C)

USER strategic items refined:
   1. formal-oracle procurement (Lean rec; 11th-rule HARD REQ)
   2. Phase C TIER-3 build IN PROGRESS (P1 STEP-8/9; P2 active)
   3. ARM-3 Option C low-priority background
   4. 3 TRACK D design Q's at visual review
   5. NEW: Tier 1+2+3 strategic dispatch per USER 2026-06-16

Substrate state: 26287 atoms / 5204 relations (Testbed partition); to grow
   by +1 (CRT atom STEP-9.1) + +1 (residue_fpe_encoding STEP-9.2) +
   ~115 (Tier 2 METHODOLOGY_RULE + AUDIT_LESSON atoms when Skunkworks
   completes spec + Testbed ingests); cap_pres=1.0 PRESERVED;
   methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 11th rule applied: ALL atomization substrate-internal-first (deterministic;
  no LLM in classification)
- USER constraint not-derail ENFORCED via parallel sectoring (3 threads;
  cert chain unimpeded)
- 84th cert chain integrity PRESERVED (DECISION 220 doesn't touch cert
  chain; parallel)
- Tier 1 preservation addresses USER loss-concern (lightweight ~10MB
  delta to git; ~1800 metrics+results+provenance files; commits + push)
- Categorization scheme (Tier-A/B/C + relevance_tier) prevents Tier-C
  volume from polluting Tier-A/B queries
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

220 cumulative decisions. **255+ honest signals.** 88 confirmed + 4 candidates
today (89th + 90th + 91st + 92nd). Phase C TIER-3 cert chain active; Tier 1 +
Tier 2 dispatched parallel; Tier 3 deferred.

---

**Orchestrator (Custodian):** TIER 1 preservation sweep DISPATCH NOW.
Update .gitignore + bulk-add data/<exp>/metrics.json + results.json +
provenance.json + commit + push. ~15-30 min wall-clock. Light-rate-limited.
Report back with bytes/files/confirmation. Continue DECISION 215 monitoring
in parallel.

**Skunkworks (Auditor):** TIER 2 atomization spec authoring DISPATCH parallel.
kind:METHODOLOGY_RULE + kind:AUDIT_LESSON + kind:EXPERIMENT_RECORD +
kind:DECISION_RECORD + kind:HONEST_SIGNAL_RECORD + kind:COMMUNICATION_RECORD
schemas. Submit to Testbed pre-receive verification. ~30 min wall-clock.
Continue P2 prereg DESIGN + STEP-7 VET reactive + post-write VETs in parallel.

**Testbed (Integrator):** STEP-9.1 + 9.2 per Option B forward-grounded
(DECISION 219). PLUS pre-receive Skunkworks Tier 2 schemas when delivered.
PLUS Tier 1 preservation sweep is benign-to-you (you don't need to act on it;
Orchestrator handles).

**Exp-Dev (Prover):** TIER 3 atomizer script DEFERRED to post-Phase-C-TIER-3
foundation complete. Continue STEP-7 results-read delivery + P2 quad-head
ref-impl + Kymn study (per DECISION 215). When Tier 3 dispatch comes, your
substrate-internal atomizer script per DECISION 220c spec.

**USER:** 3-TIER strategic dispatch in motion per your direction (Tier 1
preservation NOW + Tier 2 atomization parallel + Tier 3 deferred). Distinct
kind:* per knowledge category. Categorization scheme separates load-bearing
(Tier-A always-queried) from selectively-relevant (Tier-B EXPERIMENT_RECORD
with relevance_tier filter) from history-archive (Tier-C archaeology-only).
Cert chain UNDERAILED -- P1 STEP-8/9 active independent of this dispatch.
P1 residue_fpe_encoding atom honest-bounded; CRT foundation atom authoring;
P2 prereg DESIGN parallel. Will surface when Tier 1 sweep completes +
Tier 2 specs ready + P1 atom lands.

Tag: DECISION_220_USER_TIER_1_2_3_GO_in_order_parallel_to_cert_chain_kind_distinct_per_knowledge_category_TIER_1_preservation_orchestrator_dispatch_NOW_update_gitignore_bulk_add_metrics_results_provenance_commit_push_TIER_2_atomization_skunkworks_parallel_kind_METHODOLOGY_RULE_AUDIT_LESSON_EXPERIMENT_RECORD_DECISION_RECORD_HONEST_SIGNAL_RECORD_COMMUNICATION_RECORD_schemas_TIER_3_atomizer_script_exp_dev_DEFERRED_post_Phase_C_TIER_3_foundation_complete_categorization_scheme_Tier_A_always_load_bearing_Tier_B_selectively_via_relevance_tier_HIGH_MEDIUM_LOW_ARCHIVE_Tier_C_historical_archaeology_only_USER_constraint_NOT_derail_enforced_via_3_threads_parallel_sectoring -- Research (Director)
