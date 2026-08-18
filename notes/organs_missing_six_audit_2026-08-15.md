# The six "MISSING" organs: five of them are not missing

**BUILD-NOTHING audit pass, 2026-08-15.** Queue items `organ-missing-{d7,d8,e4,f5,f6,h2}`.
No experiment run. No file under `hdlab/`, `experiments/`, `data/foundation/`,
`data/exp_structured_code_vs_flat_bag_c3_v1*`, `data/exp_structured_comparator_v1/probes/` or
`data/capability_registry.jsonl` modified. No `metrics.json` written. `notes/ORGAN_MAP.md` READ ONLY
(the untested-organs agent owns it this session). Full per-organ detail with every number is in the
machine-readable fragment `.claude/scan-out/organs-missing-batch.json`; this note carries the
argument.

---

## 1. The headline

**One of the six is genuinely missing: D8, the cascade synapse. It is also the one that should not
be built.** The other five have an existing implementation, an existing floored result, or both.

| organ | verdict | final-pick rank |
|---|---|---|
| **F5** coherence monitor / N400 | operation CLASS built + **on the live path** + floored; the specific pinned quantity `‖Δ state‖` unbuilt | **1** |
| **F6** construction-integration | **NOT missing** — `hdlab/iterative_attractor.py` is **live**; 5 floored runs incl. a cell named after the organ | **2** |
| **D7** successor representation | **NOT missing** — a converging TD(0) SR learner with 6 consumers; no `hdlab/` module | 3 |
| **E4** discourse bridging | **NOT missing** — 3 floored full-run PASSes + a promoted `hdlab/` organ | 4 |
| **D8** cascade synapse | **GENUINELY MISSING** | 6= |
| **H2** information foraging | **NOT missing** (already corrected at ORGAN_MAP §10.1/H2b; re-verified here) | 6= |

The filter that produced the ranking: **retrieval is fine, the final pick is not.** An organ that
would improve retrieval is worth little right now. Independent corroboration recomputed off disk
this pass — in `data/exp_orthographic_floor_vet_v1/metrics.json`, `A1_BASE` **median_rank = 37.0**
and `A6_TRIGRAM_ONLY` **median_rank = 37.0**, *identical*, while hit@1 is 0.0480 vs 0.0870. Same
neighbourhood, worse pick, same 4,000 items and 5,491-anchor pool.

---

## 2. Why four of them were mis-labelled, and it is a fault we already named

ORGAN_MAP §8 discloses that its EVIDENCE column was built from module docstrings and cited cells.
**That is an absence claim made by SEARCH, and the naming convention was unknown.** Concretely:

- searching `hdlab/` for `construction_integration` returns nothing — the module is
  `iterative_attractor.py`;
- searching `hdlab/` for `successor` returns nothing — the SR is `train_sr_transport` inside
  `experiments/exp_pfc_gate_cfrpe_trained_v2.py`;
- searching for `bridging` returns a docstring *mention* in `coreference_resolver.py`, while the
  actual promoted organ is `context_grounded_valence.py`, whose name contains neither word.

**Search by SHAPE, not by keyword, and state how you enumerated.** This pass enumerated by
`os.scandir`: `notes/` 10,552 `.md` (7,923 excl. watchdog/ping), `experiments/` 5,778 `.py`,
`data/` 7,905 subdirectories, `hdlab/` 157 `.py` by `os.walk` — **157, not the 155 ORGAN_MAP
records**; the two new files are `information_foraging.py` and `corpus_registry.py`.
Live-path membership was decided by a **runtime `sys.modules` diff** on a fresh import of
`hdlab.reading_grounding_loop` (39 eager `hdlab.*` modules), never by grep.

This is the same finding the untested-organs pass made at §10.0, reproduced on a disjoint organ set.

---

## 3. F5 — coherence monitor. Rank 1, and the reason is a pun.

**Brain structure:** left temporal cortex — posterior MTG/STG with an anterior-MTL contribution
(Halgren et al. 2002 *NeuroImage* 17:1101; Lau, Phillips & Poeppel 2008 *Nat Rev Neurosci* 9:920).
Not a frontal conflict monitor; that would be a cognitive-theory relabel.

**Operation:** N400 amplitude = magnitude of the update forced on a *running* representation of
meaning, `‖Δ situation_state‖` (Rabovsky, Hansen & McClelland 2018 *Nat Hum Behav* 2:693).
**The reference point is PINNED — the current discourse state, not a fixed template. The norm, the
update rule and the precision estimator are UNPINNED.** Rabovsky's quantity is *their SRN's* hidden-
state change: a model device, no measured coefficient. **CONTESTED**, for decades: semantic-update
(Rabovsky) vs graded ease-of-lexical-*access* with no update at all (Lau/Federmeier). Both camps
hold data. Do not present `‖Δ situation_model‖` to anyone as "what the brain does."

**Reuse, verified at runtime:** `hdlab/self_improving_loop.py::decode_coherence_margins` returns a
gold-free per-position top1-minus-runner-up role-decode margin over a freshly built situation
register, and `decide_keep_or_revert` adopts on the margin *delta* above an abstain band. Registry
`self_improving_loop_coherence_gated_keep_revert_controller` = WIRE/WIRED with a scaffold-free
witness. **`hdlab.self_improving_loop` and `hdlab.situation_model_accumulate` are BOTH on the live
eager closure.** `hdlab/predictive_coding.py` supplies the residual operator (ALREADY_WIRED, not
eager). Both halves of the N400 exist; only the composition is unbuilt.

**Why rank 1.** A pun is our failure geometry exactly: the *dominant* reading is the *wrong* one —
retrieval right, top-1 wrong — which is "right neighbourhood, wrong member" (axon→dendrite).
`data/exp_pun_coherence_alarm_viability_probe_v1/metrics.json` HARD_PASS, run_mode full: a
selectional-fit coherence alarm separates dominant-WRONG (0.9849) from correct (0.0) and control
(0.0), frac 1.0, p=3.81e-06, **scramble collapses to −0.0073**, cross-feature control −0.166.
Structurally, a coherence monitor is a *second, orthogonal* score over already-retrieved candidates:
it cannot help retrieval and can only help the pick.

**The counterweight, stated as hard as the positive — two of them.**
1. `data/exp_read_discourse_wsm_running_vs_static_coherence_v1/metrics.json` **HARD_FAIL**: RUNNING
   vs STATIC coherence, margin **−0.060** (adjacent-swap, all 16) and **−0.222** (long passages),
   non-negative on only 44% of passages. **The N400's defining property — reference = current state,
   not a template — is the property with a floored negative already on disk.** Any F5 pre-reg must
   confront this, not be written in ignorance of it.
2. `data/exp_coherence_selector_text_transfer_v1/metrics.json` **CANNOT_BRIDGE_REPRESENTATION_GAP**:
   intact in sim (0.8367) but 0.4286 on real text against random 0.4571 — *below* random.
   Registry row SHELVE / TRAPPED_SHARED.

So: **highest relevance AND already once-failed on real text for a diagnosed representational
reason.** Never "promising."

**Smallest can-fail move, and it is a re-score not a build.** Score the existing C3 top-50 with the
already-live `decode_coherence_margins` and re-rank. Floors: (i) the un-re-ranked 4.80% arm,
(ii) the 8.70% spelling arm, (iii) **a RANDOM permutation of the same 50**, (iv) the same score on a
**scrambled context**. If a random permutation matches it, the organ is decorative — the test that
killed `exp_rank1_common_mode_removal_v1`. Wire target `hdlab/self_improving_loop.py` is **on the
live path**, so this does not inherit the 83/155-unreachable problem.

---

## 4. F6 — construction-integration. Rank 2, and the machinery is already live.

**Brain structure: UNPINNED.** Kintsch's C-I is a cognitive architecture with no assigned neural
substrate. The nearest neurally grounded pieces are recurrent attractor settling as such (CA3
collaterals — Marr, Treves & Rolls; cortical CAN — Amari, Wilson & Cowan) and, for the
loose-then-narrow *shape*, pMTG/LIFG semantic control. Naming a structure here would be inventing
one.

**Operation:** `A(t+1) = normalize(A(t) · W)` over a proposition-connectivity matrix `W` from
argument overlap and context fit, a small fixed number of cycles, not to an energy minimum
(Kintsch 1988 *Psychol Rev* 95:163). **⚠ UNVERIFIED-CITATION: ORGAN_MAP flags this equation as
"recalled/folklore, not freshly re-verified", and I did not re-verify it either** — no web access
this pass, and the prior drill `notes/research_drill_CI_comprehension_loop_situation_model_brain_
mechanism_2026-07-21.md` describes Integration only qualitatively and never states the matrix form.
**The flag is confirmed, not lifted.** **UNPINNED: how W is built**, the normalisation constant, and
the cycle count. **ACCEPTED SHARED LIMIT, not a bug:** bounded-iteration constraint satisfaction
converges to *a* stable answer, not the correct one; human garden-path roles linger too
(Christianson et al. 2001 *Cogn Psychol* 42:368).

**Not missing.** `hdlab/iterative_attractor.py::iterative_cleanup` computes
`state_{t+1} = normalize(softmax(temp·(state_t @ codebook.T)) @ codebook)`, `max_steps=8` — that IS
`normalize(A·W)` with W = codebook similarity, and **it is on the live eager closure**
(`cleanup_attractor` = ALREADY_WIRED). `hdlab/modern_hopfield_readout.py::top_k_by_retrieved` is a
written, registered within-neighbourhood re-ranker whose own docstring says its ranking *differs*
from `cos(q, K_i)` because `y` interpolates neighbours toward `q` (not eager). And
`data/exp_construction_integration_relation_inference_v1/metrics.json`, run_mode **full**,
**MECHANISM_WORKS**: mech 0.474 vs lexical 0.316 vs random 0.263 vs **integration-only 0.421**.

**Honest aggregate over five floored runs: settling beats one-pass, loses to well-chosen simpler
aggregators, and over-smooths at depth.** `settling_parse_selector_richness_v1` MIDDLE_BAND —
settle 0.531 loses to baseline 0.594 but **beats one-pass 0.448 (+0.083)**;
`settling_fix_learned_recurrent_v1` HARD_FAIL (rho vs gold ≈ 0 — graded but meaningless);
`exp_grounding_iterative_settling_cascade_depth_v1` HARD_FAIL with `OVERSMOOTH_DETECTOR_FIRES=True`;
`exp_arc_aggregation_retriever_bindsettle_v1` — **CI-settle 0.660 loses to single-fact 0.706 and to
SPA-bundle 0.766**, the cell noting "Kintsch selection discards the fact-count accumulation signal."
The negatives are about *depth*, and depth is exactly what Kintsch pins qualitatively and nowhere
numerically.

**Smallest can-fail move:** run the live `iterative_cleanup` over the C3 top-50, candidates as
codebook, context as initial state, sweeping `max_steps ∈ {1,2,3,5,8}`. Floors: 4.80%; 8.70%; a
RANDOM permutation of the same 50; **the same settle with a SCRAMBLED context** — which kills it if
the win comes from codebook geometry alone. **The real F6 gap is not the settling loop; it is `W`.**
Kintsch specifies *argument overlap*, and we have no argument structure over C3 candidates. Caveat
on promoting the existing CI cell: it leans on hand-written `CATEGORY_PROTOTYPES` and wish/resolution
marker lists — closer to hand-rules than glass-box.

---

## 5. D7 — successor representation. Rank 3. Built, converging, trapped, and falsified on real text.

**Brain structure:** hippocampal CA1/CA3 place cells + mEC grid modules — the specific claim being
that place-field rate maps are *rows* of M and grid modules are its *eigenvectors* (Dayan 1993
*Neural Comput* 5:613; Stachenfeld, Botvinick & Gershman 2017 *Nat Neurosci* 20:1643; Momennejad
2017 *Nat Hum Behav*).

**Operation:** `M = (I − γP)⁻¹`. PINNED. But three things we would need are not:
**UNPINNED (1) the synaptic learning rule** — Stachenfeld et al. *fit* SR to firing rates and never
measure the update; TD(0) is a modelling choice. **UNPINNED (2) the state space and P for a
non-spatial semantic domain** — the space→concept transfer is theoretical, TEM being its strongest
version and TEM being a *model*. **UNPINNED (3) the multi-scale γ combination.**
**CONTESTED:** that grid cells *are* eigenvectors of M is a model fit; continuous-attractor accounts
explain grid firing with no SR at all.

**Not missing.** `experiments/exp_pfc_gate_cfrpe_trained_v2.py:456 train_sr_transport` learns
`M` s.t. `E[cur] @ M ≈ E[nxt] + γ(E[nxt] @ M)` — the SR Bellman equation in successor-features form,
γ=0.85, `sr_td_converged=True` (err 0.0221 → 0.0077). Its scorer `reach_value = cos(E[cand]@M,
E[goal])` is a candidate re-ranker, and it **already ships the control that decides it**:
`reach_control_targetcos` sets M := identity, which *is* raw cosine — so a win over it is provably
not cosine in disguise. Six consumers. **What is missing is an `hdlab/` module**: `--serves
successor` = 0/198 rows, and `kg_traversal` / `multi_hop` / `edge_importance` are all off the live
path. `edge_importance.py` cites PageRank but computes an *unconditioned* eigenvector — personalised
PageRank is SR-equivalent only *with* the restart vector, which it does not have. Adjacent, not
covering.

**Evidence is genuinely mixed and includes a pre-registered paradigm negative.** WINS:
`exp_grounding_multihop_sr_reachability_routing_v1` HARD_PASS on a **real CSKG subgraph** (10,577
nodes, 34,659 edges, 120 seeds) — SR_SEEDED @2 = 0.434 vs greedy 0.181 vs memoryless 0.121;
`exp_coherence_selector_insim_v2` HARD_PASS 1.0000 with a shuffled-structure control collapsing to
0.2700 — **in sim**. LOSSES: `exp_event_level_sr_td_contrastive_relation_inference_phase2_v1`
**MECHANISM_FALSIFIED** — trained 0.2590 vs copy-baseline 0.2565 (margin +0.0025 against a ≥0.05
gate, n=3,212), and the cell states this is a *genuine paradigm negative per pre-reg since both
prior confounds are fixed*; plus the text-transfer failure above. Both real-text failures are
**representational** (the SR was trained over a synthetic permutation grammar) — and the run that
used *real* transitions passed. That is the fork.

**Cost LOW-MEDIUM, and it is a re-score.** What would have to be true: a transition matrix over the
C3 answer pool whose edges are **not** the embedding cosine we already rank by (the 1.21M-edge CSKG,
read by nobody live, is the supply), and `reach_control_targetcos` must not match the trained-M
ranking. Prior conceptual work exists and should be built on, not re-derived:
`notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md` §3.1–3.3, which already
proposed the multi-scale γ bank.

---

## 6. E4 — discourse bridging. Rank 4. The map says "not even a negative result exists." Three PASSes say otherwise.

**Brain structure:** hippocampal relational binding (CA1 + subiculum) → anterior temporal / angular
gyrus. Per ORGAN_MAP's own standing insight it must **reuse E3**, and `hdlab/coreference_resolver.py`
is on the live path.

**Operation: UNPINNED, and CONTESTED on whether it happens at all.** Graesser, Singer & Trabasso
1994 *Psychol Rev* 101:371 gives a *taxonomy*, not an equation; McKoon & Ratcliff 1992 *Psychol Rev*
99:440 (minimalist) holds that elaborative bridges are not routinely drawn on-line. Live
disagreement, both camps with data.

**Not missing.** 82 bridging/discourse directories under `data/`.
`exp_affect_state_bridging_inference_v1` HARD_PASS (zero-overlap bridging 1.0 vs lexical-only 0.0,
bystander 1.0, scramble 0.0); `exp_evaluative_bridging_inference_v1` HARD_PASS, same shape;
`exp_causal_attribution_bridging_v1` BRIDGING_WORKS (0.750 = ORACLE 0.750 vs recency 0.500 vs
text-only 0.250, shuffle degrades). And the organ was promoted:
`hdlab/context_grounded_valence.py`, registry WIRE/WIRED.

**Deflation.** Those three run in **0.4496 / 0.1069 / 0.0400 s** on tiny hand-built items and score
exactly 1.000 against exactly 0.000 — suspect-1.000 territory, and a construction proof is not a
capability win. `context_grounded_valence`'s own docstring names its closed hand lists
(`FORCE_CLASS_HARM_REAL`, a 9-word `BODY_PART_SUPPLEMENT`) and its proven gaps. Runtime trace: it is
**not** on the live eager closure. EXISTS yes / IS-REACHED no / IS-GOOD unproven at scale.

**Rank 4** because bridging *adds* a link that was not in the text; our defect is choosing among
candidates already retrieved. The only route to relevance is indirect (a bridged context is a richer
re-ranking key) and that is retrieval-side. Nothing on disk shows bridging re-orders a candidate set.

---

## 7. D8 — cascade synapse. Genuinely missing. Do not build it.

**Brain structure:** the individual excitatory synapse / dendritic spine — its internal biochemical
state machine. **Subcellular; there is no region to name.**

**Operation:** depth-indexed cascade, plastic `q_k = q·x^(k−1)`, metaplastic `p_k = q·x^k`, `x=1/2`
(Fusi, Drew & Abbott 2005 *Neuron* 45:599; Ben Dayan Rubin & Fusi 2007). Capacity: binary-fast
`log N`; cascade `√N`; Benna & Fusi 2016 *Nat Neurosci* 19:1697 `N`.
**WRITE UNPINNED: no measured synapse has been shown to carry a depth-indexed cascade with
geometrically decreasing transition probabilities.** What *is* measured is tag-and-capture
timescales (Frey & Morris 1997 *Nature* 385:533), spine-size distributions, and behavioural
power-law forgetting. The mapping to `q`, `x`, `d` is a **model fit**. "The brain uses a cascade
synapse" is not a licensed statement — this is the perirhinal error waiting to happen.
**CONTESTED on α:** 3/4 (FDA 2005) vs 1 vs 0.5 (Benna-Fusi 2016) belong to three different models.
⚠ **The director-KB still holds a chunk quoting "Roxin-Fusi 2012" for α ≈ 0.5–1.0, which ORGAN_MAP
has since corrected to Roxin & Fusi 2013 *PLoS Comput Biol* 9(7):e1003146.** A future drill will
re-surface the stale form.

**Genuinely missing** — every `cascade` hit in `hdlab/` is pipeline usage (`goal_typing` ×7,
`late_combine`, `concept_encoder`, `composed_encoder_v3`, `gap_driven_reader`); zero hits for
`metaplast` / `memory_lifetime` / multi-timescale. But **the evidence column is NOT empty**:
`exp_forgetting_kernel_signreadout_v1` band **REFUTES** — it did measure power-law forgetting
(dAIC 40.5/44.9 over exponential, slopes −0.326/−0.294) and then killed its own reading with a
scramble-*order* control that moved the slope by 0.011: *"the curve is NOT measuring consolidation —
the accumulator is order-invariant."* `exp_c2_cascade_stc_swr_continual_v2` HARD_FAIL **at ceiling**
(1.000 vs 1.000) — not a fair test, so not evidence against the organ. `exp_a8` HARD_PASS shows no
catastrophic forgetting up to α=0.3, i.e. single-state stores are adequate in the regime we run.

**Rank 6=. Zero final-pick relevance** — the failure is a single-shot probe with no retention axis.
**Do not build.** Published cascade advantages need N > ~1e6 synapses; we run d = 256..4096.
**A negative here IS the published prediction.** What would have to be true: (i) ≥1e6 synapses AND
(ii) long-horizon retention becomes the measured bottleneck. Neither holds. And any arm that does
not show the **early-retention LOSS** (1/n cascade, 1/√m Benna-Fusi) is not implementing this organ,
whatever else it shows.

---

## 8. H2 — information foraging. Not missing, already corrected, and the wrong frontier.

Re-verified independently from disk rather than cited. `hdlab/information_foraging.py` (80 keyword
hits: charnov, forag, mvt, patch_), registry `information_foraging_mvt_leave_rule` = WIRE/WIRED,
witness `verification/test_information_foraging_organ_witness.py`,
`data/exp_information_foraging_reading_v1/metrics.json` run_mode **full**, 5 arms × 10,000
sentences. **New, and not in ORGAN_MAP: `hdlab/corpus_registry.py` also exists** — `hdlab/` is 157
`.py`, not 155. **IS-REACHED = NO**: neither module is in the 39-module eager closure. Tier per
§10.1/H2b-5: **MIDDLE_BAND_COMPARATOR_SELECTED**, not HARD_PASS — FROZEN beats FORAGE on held-out
coverage (0.0743 vs 0.0617) and n_grounded (696 vs 604), RANDOM beats it on WordNet agreement.

Operation PINNED (Charnov 1976 *Theor Popul Biol* 9:129; Constantino & Daw 2015 Table 2; Hayden,
Pearson & Platt 2011 *Nat Neurosci* 14:933 — longer travel *raises* the threshold, so a fixed
threshold is a broken organ). **UNPINNED: the ρ_fast/ρ_slow mixing weight** (Wittmann 2016
*Nat Commun* 7:12327) — and the module says so and declares it a fallback, which is the right
handling and worth copying.

**Rank 6=.** Foraging changes *what we read* — supply. It moves the 55.65% top-50 containment (which
already **ties** the spell-checker's 54.55%, i.e. is not the deficient number) and leaves the 8.6%
where it is. Wiring it now buys more items whose top-1 is still wrong. **Defer**, despite ORGAN_MAP
§6 naming it STEP 1.

---

## 9. Recommended corrections to ORGAN_MAP (NOT applied — that file is owned by another agent)

- **D7 OURS** "NONE" → `experiments/exp_pfc_gate_cfrpe_trained_v2.py:456 train_sr_transport`,
  TD(0) linear SR, converging, 6 consumers, **not in `hdlab/`**; EVIDENCE → one HARD_PASS on a real
  CSKG subgraph, one pre-registered MECHANISM_FALSIFIED on real text.
- **E4** "never attempted; not even a negative result exists" → three floored full-run PASSes plus
  a promoted `hdlab/` organ, all on tiny hand-built items.
- **F6 OURS/EVIDENCE** "NONE / none / UNTESTED" → `hdlab/iterative_attractor.py` **on the live
  path**, plus five floored runs.
- **§1** `.py` in `hdlab/` **155 → 157**.

---

## 10. Disclosures

- **No tool call was denied during this pass.** Two `ls`/`Grep` calls against `notes/` and
  `experiments/` timed out (10,552 and 5,778 entries) and were replaced with `os.scandir` /
  `os.walk` in `.venv` Python — a timeout, not a denial.
- **Right environment:** `D:/AI/hd-instrument/.venv/Scripts/python.exe` throughout, never bare
  `python`. Absolute paths throughout; no empty `Glob` was trusted.
- **Files written:** `data/dispatch_queue.jsonl` (claim/done fields on the six `organ-missing-*`
  rows only, read-modify-write preserving every other line byte-for-byte),
  `.claude/scan-out/organs-missing-batch.json`, this note, and three `scratch/` scripts.
- **`.git/index.lock` is present** (0 bytes, mtime 2026-08-15 11:16) and contended by a concurrent
  agent. **It was NOT force-cleared and no commit was attempted.** A later pass should stage these
  paths explicitly (`git add <path>` per file, never `-A`) and check `git show --stat`.
- **Not verified, flagged:** the Kintsch 1988 matrix-update equation (ORGAN_MAP's
  unverified-citation flag propagated, not laundered; no web access this pass, and the July CI drill
  does not state it either); `director_kb_query.py` query 5 was still running at write time and
  nothing here depends on it.
- **KB instrument caveat:** `director_kb_query.py` uses the `char_trigram_v1` encoder and matches
  orthographically as much as semantically — the successor-representation question returned
  "Representative" and "union representative" at cosine 0.3623. The `os.scandir` enumeration, not
  the KB, is what the absence claims rest on.
