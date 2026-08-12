# Island harvest assessment (hdi_skunkworks, AUDIT-ONLY, 2026-08-12)

Triage of the ~14 registry ISLAND rows that `notes/reinvention_and_registry_audit_2026-08-12.md`
judged REVIVABLE. Question asked of each row: **not** "was this good work" but "does anything need
it now, for a glass-box substrate that learns word meanings from reading well enough to reason and
eventually converse". Every verdict below was read off `data/<anchor>/metrics.json`, not off the
registry row.

---

## FINDING 0 (biggest one): the ISLAND census was partly an instrument artifact

`tools/integration_health.compute_import_graph()` matched only the `experiments.`-prefixed import
forms (`from experiments import X`, `from experiments.X import`, `import experiments.X`). The
DOMINANT idiom in `experiments/` is `sys.path.insert(0, EXP_DIR)` then a **bare**
`import exp_other_cell as v1`. Those edges were invisible, so a cell whose only consumers are other
cells could only ever be classified ISLAND.

Proven case, off disk: `experiments/exp_maven_ere_convergence_gated_subevent_v1.py` line 60-61
imports `exp_maven_ere_convergence_gated_causal_v1` and `_v2` -- and both causal rows read
`integration_status=ISLAND`, `used_by=[]`.

Measured delta (old vs new graph on the real repo, `data/session_local/skunkworks/graph_delta.py`):

| | old | new |
|---|---|---|
| exp modules with >=1 consumer | 497 | 597 |
| cells importing another cell | 4334 | 4563 |
| registry `integration_status` | ISLAND=34, TRAPPED_SHARED=22 | ISLAND=28, TRAPPED_SHARED=28 |

Six ISLAND rows were false: `maven_ere_..._causal`, `situation_model_assembly_binding_wm_coref_...`,
`encoder_retrain_minimal_unfreeze_...`, `wm_nl_binding_via_read_conditioning`,
`native_vsa_zeroshot_novel_role`, `coherence_selector_text_transfer`.

Also fixed a pre-existing phantom node: `from experiments import (  # noqa: E402,F401` was parsed
into a module named `F401`.

Correction to my own first pass: I initially measured "the exp-consumer detection was 100% dead".
That was wrong -- an artifact of loading the pre-fix module from a copied path, which made its
`__file__`-derived `EXP_DIR` point at an empty directory. Re-measured with explicit dirs; numbers
above are the real ones.

---

## Ranked triage

Ranked by usefulness to the CURRENT goal (reading/grounding path; expressive side). Evidence column
is the disk verdict, not the registry claim.

| # | island | evidence (off disk) | what would consume it | verdict |
|---|---|---|---|---|
| 1 | maven_ere causal / subevent | HARD-PASS, full dev 710 docs / 613,706 pairs. causal F1 14.78 (**P=11.49 R=20.73**), subevent 13.63 (P=8.22 R=39.94); scramble collapses 3.48 / 2.78 | nothing in the reading arc | **KEEP AS CREDENTIAL, DO NOT WIRE** |
| 2 | fastcoref neural coref | coref query-acc 0.684 -> 0.807 on McGuffey; parent gate stayed NO_GO (parity 0.731 < 0.80) | the reading loop, which today has NO coref at all | **NOT WIRE** (oracle/ceiling only) |
| 3 | read_xsent_coref_distractor_suppress | HARD_PASS real LitBank: +0.0434 (0.2487 vs 0.2053), **trust_pass=False** | grounding path | **NOT WIRE**, stays VET_PENDING |
| 4 | propara_official_eval_port | self_test exit 0 this session, bit-exact vs official fixtures (1.000 / 0.686 / 0.545) | nothing live (ProPara arc shelved) | **WIRED as rot-guard only** |
| 5 | situation_model_assembly_binding_wm_coref | HARD_PASS, MAIN=1.000 both seeds, 6 floors collapse | -- organs already in hdlab | **NOTHING TO HARVEST** |
| 6 | encoder_retrain_minimal_unfreeze | CLEAN_PASS, held-out 0.52 -> 0.83 | already wired as `hdlab.encoder_retrain_persist` | **ALREADY HARVESTED** |
| 7 | native_vsa_multirelation_composition | HARD-PASS but VET-scoped to templated slot-filling with explicit role words | organ = hdlab/binding.py (wired) | **SHELVE** |
| 8 | native_vsa_cross_slot_relational_binding | **verdict=PARTIAL** ("neither arm clears PROVEN_MIN=0.80") while the row carried gate=WIRE | organ already wired | **DEMOTED WIRE -> SHELVE** |
| 9 | read_conditioning_novel_filler_known_role | HAVE_COMPREHENSION_TARGET, Q1 0.989/0.972 vs chance 0.05 | -- | **SHELVE** (closed 20-filler synthetic vocab; "novel" = novel pairing, not a novel word) |
| 10 | theory_of_mind_sally_anne_nested_hrr | HARD_PASS, Q2 0.806 vs 0.138, 5 seeds cv 0.034 | its wire-target (coherence-selector) arc is itself SHELVED | **DEMOTED WIRE -> SHELVE** w/ revival criteria |
| 11 | capacity_scaling (k_cliff) | analytic K_cliff(N)=0.87N/log2(N), R^2=0.99; zero consumers for 15 days | -- | **DEMOTED WIRE -> SHELVE** |
| 12 | cskg_foundation_v1 | data-artifact producer | -- | expected island, no action |
| 13 | cls_discrete_budget_consolidate_v6_replay | v6 wiring HARD_FAIL; VET_PENDING 15.1 days stale | -- | owner should close as SHELVE |
| 14 | coherence_selector_text_transfer | flips to TRAPPED_SHARED under the fix, but arc shelved | -- | no action |

### The MAVEN question, answered straight
It is a real public-benchmark, full-dev-set, glass-box, no-LLM-at-inference win, and it is a
**different arc**: event-event discourse relations over Wikipedia news, not word-meaning grounding.
Two concrete reasons not to pull it into the live goal:
1. **Precision 11.49%.** ~9 of every 10 asserted causal relations are wrong. The foundation is
   already measured at 65.7% tautological groundings; adding a 9-in-10-wrong relation stream makes
   the diagnosed problem worse. It is not a knowledge source at this operating point. (A
   precision-first operating point -- require all cues to fire -- was never measured. That is a
   legitimate open question for a cell author, not something an auditor should assume.)
2. F1 14.78 vs SOTA 31.96 is ~46% of SOTA; "unused win" overstates it.

What IS transferable is already owned: `hdlab.learner.plugins.gam_plugin` as a glass-box learned
readout over auditable cues. The grounding path currently accepts facts on hand-set thresholds
(`GAP_FLOOR=0.625`, PMI p75=2.10); the MAVEN cells are the evidence that a learned glass-box readout
works on real text at 613k-pair scale. That is a reuse pointer for whoever owns the grounding
accept/reject decision -- not a promotion I should make.

Registry bookkeeping done: the causal row's own promotion trigger ("promote the gate when a 2nd
discourse-relation task needs it") is **already met** by the subevent cell, and the subevent row had
silently restated it as "a 3rd task". Recorded. Promotion still DEFERRED on purpose: extracting the
gate means editing two cells that carry bit-exact full-dev reproduction claims, for zero live
consumer.

### Expressive side: nothing to harvest
Scanned all 123 rows for generation/production/dialogue capability. The only row is `generation`
(`hdlab/generation.py`, walk/sequence-completion decode, 2 HotpotQA consumers) and it is already
WIRED. **There is no shelved expressive capability waiting to be revived** -- that side has to be
built, harvest cannot help it.

---

## What was wired

1. **`tools/integration_health.py`** -- bare cell-to-cell import edges now visible; phantom `F401`
   node removed. Witness: **`verification/verify_integration_health_import_graph.py`**, 3 tests,
   scaffold-free (runs against the real repo). Can-fail proven: against the pre-fix module both
   assertions fail (`consumers of causal_v1 = []`, `phantom F401 present = True`).
   `capability_registry_audit.py --self-test` still passes; `--dry-run --json` still runs clean.
2. **`verification/verify_propara_official_eval_port.py`** -- 3 tests, pins the official ProPara
   metric bit-exact on the vendored fixtures. Rot-guard for a scorer nobody was running. Explicitly
   NOT a capability revival; the ProPara task rows stay SHELVED.

`pytest verification/verify_integration_health_import_graph.py
verification/verify_propara_official_eval_port.py
verification/verify_situation_model_multibank_dropin.py` -> **11 passed**.

Registry: 12 rows annotated with `audit_note_2026_08_12_island_harvest`; 3 gate demotions
(`native_vsa_cross_slot_relational_binding`, `theory_of_mind_sally_anne_nested_hrr`,
`capacity_scaling`); witness path added to `propara_official_eval_port`. A5-gated write (tmp ->
os.replace, verify-load, row-count + duplicate-id asserts, CRLF preserved) -- row-scoped diff, 12
insertions / 12 deletions on 123 rows.

## What was deliberately NOT wired
Everything else. Nine of the fourteen are cells whose load-bearing organ is **already** in `hdlab/`
and wired (`binding`, `situation_model_accumulate`, `situation_model_multibank`,
`coreference_resolver`, `encoder_retrain_persist`, `coref_distractor_suppress`) -- their ISLAND flag
described the terminal experiment file, not an unharvested capability. Of the rest, MAVEN is a
different arc with disqualifying precision, fastcoref would contaminate the reading claim and could
not be executed here, and the coref suppressor fails its own trust axis. **The honest headline is
that this island set contains almost nothing the live goal needs.**

## Caveats
- Another agent's `tools/_tmp_skunkworks_register_batch_2026-08-12.py` is untracked on disk and
  `tools/session_start_hook.py` is modified by someone else; my registry write was a
  read-edit-replace with a ~1s window and is NOT concurrency-safe. If a second agent wrote the
  registry in that window, re-check `git log -p data/capability_registry.jsonl`.
- The bare-import regex is textual: an `import exp_x` inside a docstring would register an edge.
  Names are filtered against real `experiments/` basenames, so the failure mode is a spurious edge
  between two real cells, never a phantom module.
