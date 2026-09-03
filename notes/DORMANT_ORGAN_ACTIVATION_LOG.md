# DORMANT-ORGAN ACTIVATION LOG

> **Owner directive 2026-09-03:** apply the flag-flip treatment to every dormant/"vestigial" organ — DEEP-DIVE
> (what it does in the BRAIN + who its consumers/would-be-consumers are) → REFURBISH to the current substrate →
> WIRE default-off → EVALUATE downstream on the RIGHT instrument → keep net-positives / name located-negatives.
> "Vestigial" = dormant-unwired, NOT dead. An older organ may be built against an outdated reader/parser and a
> consumer may never have considered its importance. Method: `feedback_dormant_organ_activation...` memory +
> the DORMANT-ORGAN ACTIVATION CYCLE. Enumerate islands via `tools/wiring_debt.py` (~116 island-only organs).

---

## #1 — `verb_role_exemplar_selector` (VerbRoleExemplarSelector) — ❌ LOCATED NEGATIVE **LIVE** (NOT wired; corrected 2026-09-03)

> **⚠️ CORRECTION (2026-09-03, the wire attempt).** The "ACTIVATION NET-POSITIVE +0.024/+0.22" below was
> measured against a **STALE PRE-FLIP population** (`_population*.json`, 2026-09-01) whose `wired_pick` predates
> the 2026-09-03 flag flip, using **GOLD voice labels** for canonicity. Both confounds inflate it. Measured on the
> **CURRENT reader** (the consumed metric), the override is **net-NEGATIVE-to-flat and was NOT wired** (the reader
> was reverted clean). Details:
>
> | population | CURRENT reader (live OFF) | override ON | delta | reference claimed (stale) |
> |---|---|---|---|---|
> | **Modern QA-SRL** | **0.6441** | 0.4576 | **−0.1864 CI[−0.280,−0.102]** (every bootstrap neg) | +0.0237 |
> | **19c LitBank** | 0.3571 | 0.3571 | **+0.0000** (flat) | +0.2177 |
>
> **Why the reference was wrong, mechanistically:**
> 1. **Stale baseline.** The current reader scores **0.644** modern patient — far above the stale population's
>    `wired_pick` (0.481) AND above the reference's own best INTEGRATED number (0.505). **The flag-flip
>    (`predict_revise` + `verb_subcat_gate` + …) already delivers MORE than the store override could.** No headroom.
> 2. **Gold-voice dependence.** The reference's `canonical` used `noncanonical = passive OR gold_idx<verb_idx` —
>    i.e. the GOLD patient position, NOT gold-blind. With a realistic gold-blind parse voice detector
>    (`is_passive_real`/`robust_passive`/`precise`, all ~0.32–0.38 passive recall on QA-SRL) the modern win falls
>    to **+0.015 CI spanning 0**, and the verb-shuffle twin no longer separates.
> 3. **19c = position, not the store.** With `b_pos=1` always (no canonicity), the 19c delta is identical
>    (+0.216) and the verb-shuffle twin TIES under every canonicity source → the +0.22 was **position beating the
>    stale reader's broken 19c pick**, which the now-default `predict_revise` (nearest-nominal recovery) already
>    captures live (flat delta).
> 4. **The formula breaks correct passives.** On "the apple was eaten by the man" the current reader picks
>    `apple` (correct); `integrated_pick` (b_pos=0.15, apple fit 0.98 ≫ man 0.85) still returns `man` — the
>    position log-softmax gap (pre-verbal floor 0.15 vs post-verbal 7) SWAMPS the small exemplar margin even
>    down-weighted. So on 35% of overridden modern patients it flips right→wrong.
>
> **VERDICT: the store cannot beat the current reader on live who-did-what patient — its ceiling (INTEGRATED on
> the stale pop, 0.505) is below the current reader's floor (0.644).** REROUTE below. The store remains a valid
> ISLAND organ (modern thematic-fit, real on its isolated harness); its live niche (verb-specific disambiguation
> among multiple grounded post-verbal candidates on CANONICAL clauses) is not exercised enough to help, and the
> promoted formula cannot apply it safely. Helper `hdlab/verb_role_integrated.py` (committed `e51bf634d`) + selector
> (`e65664b34`) are kept as artifacts; the reader wire was reverted (never committed to the reader).
>
> **METHOD LESSON (load-bearing):** a dormant-organ downstream eval MUST run against the **CURRENT** reader, not a
> reference/stale population — a proxy "net-positive" can be a stale-baseline artifact, and the flip already moved
> the baseline. Also: verify a reference's canonicity/label is genuinely gold-BLIND before trusting the number.
>
> **REROUTE (verdict-independent):** the modern who-did-what patient lever is NOT this store — the current reader
> already leads. Any further gain routes through P1 (the meaning/individuation representation) + the cleaned-gold
> P2 (`the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning`), already filed.
>
> --- ORIGINAL (STALE, SUPERSEDED) ENTRY BELOW ---

**Deep dive.** BRAIN: verb-specific SELECTIONAL PREFERENCE / thematic fit stored as an EXEMPLAR (instance)
distribution, NOT a centroid (McRae et al. 1998; Elman 2009; the eADM) — "which candidate is the right patient
*for this verb*," read out by NEAREST grounded exemplar (k-NN=1 / Chamfer max over the verb's attested OBJ fillers;
store `data/selectional_preferences_v1/selectional_slots_v1.pkl`, 14.7MB offline UD-parsed asset; grounded via the
wired `hdlab.grounded_similarity`). CONSUMERS: the reader's patient-selection tie-break — and the key point (owner's
"may not have considered its importance"): the live reader's patient pick (`route_predicate_arguments` /
`graded_role_assigner.competition_pick`/`hybrid_role_patient`) does NOT use verb-specific thematic fit for
SELECTION at all — only `predict_surprisal` uses a coarse grounded centroid *post-hoc* as an N400 error flag. So
this organ is a genuinely NEW selection signal the consumer under-uses.

**Reverify (functions):** eat→apple, read→book, drive→car, drink→water (not the distractors). Works.

**Evaluate downstream** (`exp_verbrole_exemplar_integrated_v1`, construction-conditional cue weighting — Competition
Model/Bates & MacWhinney: `score(c)=beta_pos(construction)·log_softmax(position)+beta_sel·log_softmax(exemplar_fit)`,
word-order weight COLLAPSES on non-canonical/archaic constructions; GOLD-BLIND canonicity from the parse):

| population | live reader WIRED | INTEGRATED | vs WIRED | verb-shuffled twin |
|---|---|---|---|---|
| **Modern QA-SRL** | 0.4808 | **0.5046** | **+0.0237 CI[+0.0040,+0.0431]** ✓ | +0.0164 (twin LOSES ✓) |
| **19c LitBank** | 0.1852 | **0.4029** | **+0.2177 CI[+0.2050,+0.2302]** ✓ | −0.0030 (twin TIES) |

**Honest read (two distinct wins):**
1. **Modern** — the verb-specific exemplar store does REAL work (beats WIRED +0.024 CI-sep AND beats its own
   verb-shuffled twin). The dormant organ delivers on its right corpus.
2. **19c** — a HUGE +0.22 over the live reader, but the twin TIES → on old prose the gain is NOT the verb store, it
   is the CONSTRUCTION-CONDITIONAL INTEGRATION mechanism itself. STRUCTURAL FINDING (a consumer blind spot surfaced
   by the activation): **the live reader's patient pick over-trusts WORD ORDER** (WIRED only 0.185 on 19c);
   down-weighting order on non-canonical/archaic constructions lifts it to 0.403. The register-native verb store is
   its own (already-filed) problem.

**WIRE OWED (default-off, Q111):** promote the construction-conditional integration (position × exemplar with
canonicity-gated beta) to hdlab + a default-off flag on the reader's patient path, byte-faithful to the validated
INTEGRATED arm; lazy-load the store + grounded space when on. Delivers: modern (verb store) + 19c (order-weighting).
Witness: default-off byte-identical + flag-on == INTEGRATED byte-for-byte + twin loses (modern). NOT the register-
native 19c store (separate problem). This is the FIRST proof the dormant-organ activation method yields a measured
downstream gain + a structural insight — exactly the owner's thesis.

---

## #2–#5 — TRIAGE (2026-09-03, researched aggressively; NONE a clean independent activation — recorded so they are not re-examined)

After #1's located negative I worked worst-first from `tools/substrate_map.py --gaps` (value is in the top gaps).
Each top-gap dormant organ was deep-dived (brain function + on-disk consumers + the [BROKEN]/[WEAK]/live path).
**Finding: the flag flip harvested the easy dormant-organ wins; the remaining high-value organs are either
net-negative, not live-deployable, orphaned, or the north-star P1 meaning cluster (P1 owner-DONE; its continuation
`build_sg_lite_...` is OPEN and owns the meaning unification).** A full Explore-agent map backs this (below).

- **#2 `distributional_meaning_channel`** (top gap [BROKEN] DECIDE WHAT WORDS MEAN) — **NOT live-deployable.**
  Substitutability specialist (AUC ~0.84) but WordSim rho −0.24 (actively bad as a general read-out), and its
  orientation sign is IRREDUCIBLY TRANSDUCTIVE (needs the presented candidate batch to orient — the live reader
  has none) + OFFLINE by design ("never live"). Docstring says so itself. Shelved-as-live (stays a valid island).
- **#3 `information_foraging`** (top gap [WEAK] KNOW WHAT IT IS MISSING; Charnov MVT, beautifully pinned) —
  **orphaned, uncertain live value.** NO experiment/live consumer imports it; the `aimed_reading_...` problem that
  spawned it PIVOTED to the meaning-integration mechanism (complementary fusion) and left the organ dormant. Its
  evidence beat RANDOM text (3.9×) but was never tested vs a FIXED schedule (the gap's own named missing test), and
  a build-plan note found its ablations "moved no counter." Wiring = build-a-consumer + a heavy grounding-coverage
  run for an only-beats-random signal. Not a clean flip; deferred (if pursued: run aimed-vs-fixed-schedule remote).
- **#4/#5 the meaning read-out cluster** (`meaning_fusion` 0.4455 WordSim; `conceptual_meaning` 0.521 SimLex /
  double-dissociation; `meaning_operation_router`; `convergent_cue_reader` 0.744 who-did-what @oracle-ceiling) —
  **P1-territory or no-live-consumer.** The board's ONLY meaning-consumed metric is WiC WSD via
  `grounded_semantic_graph.select_sense` (PPR), which imports NONE of these; none of the 30 live modules imports any
  of them. `meaning_fusion`/`router` are decontextualized with only their own witnesses as consumers (no live
  metric). `conceptual_meaning` + `convergent_cue_reader` are consumed by P1's `exp_generative_situation_sense_
  selector` and are folded into P1's shared-representation build; the only wiring that yields a live metric
  (meaning read-out → context-conditioned sense selection into `select_sense`) is exactly P1's DEBT-3 +
  `build_sg_lite`'s scope. **SEED handed to `build_sg_lite` (do NOT wire from strategy — it front-runs that OPEN
  problem): `conceptual_meaning` is STATIC-ASSET-READY (no offline store) — a synset-level IDF-Lesk score from its
  bag machinery, blended into `select_sense`/`select_sense_blended` on WiC, is the concrete testable hook for the
  bottom-up identity channel; measure it there.**

**Strategic conclusion (verdict-independent):** there is no free, non-P1, live-deployable dormant-organ flip left in
the top gaps. The remaining meaning value is the OPEN `build_sg_lite` continuation (context-conditioned generative
sense) — support it, don't duplicate it. The next verdict-independent strategy moves are the coverage-gap fix
(SOLVED +0.35, integrate on owner-DONE) and any NEW clean island with a genuine live consumer + headroom. Method
lesson reinforced (memory): a dormant organ only counts as activatable if it has a LIVE CONSUMER on a CONSUMED
metric; a validated island with no live consumer is not a flip.
