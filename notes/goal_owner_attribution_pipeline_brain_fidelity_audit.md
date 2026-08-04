# Goal-owner-attribution pipeline — brain-fidelity element audit (per-component)

**USER directive:** drill EVERY component of the goal-owner-attribution pipeline against the EXACT brain mechanism, disk-verify (not label-trust), identify gaps, be clear.

**Method:** 3 parallel disk-verification sub-agents read the actual code (no docstring-trust) + `metrics.json` + `data/capability_registry.jsonl` + `notes/capability_integration_ledger.md`. Director (this note) maps each finding to the specific brain mechanism and classifies the gap. Two prior artifacts were consulted and are NOT re-derived: `notes/component_brain_fidelity_ledger.md` (different component set — encoder/readout/consolidation) and `notes/brain_component_functional_map_2026-08-04.md` (wiring status, corroborates several numbers below) and `notes/capability_reconciliation_invisible_islands_audit.md` (HIGH-tier island list — checked for a thematic-role-labeling island; **none found**, see synthesis).

---

## Component 1 — TEXT SEGMENTATION (event/clause units)

**(a) What we actually have.** `hdlab/scene_segment.py`: `sentence_opens_scene()` matches a hardcoded frozenset of ~50 temporal cue-phrases ("the next day", "meanwhile", "chapter"...) against the first 1-4 tokens of a sentence; `parse_conll_sentences()` reads pre-segmented (blank-line-delimited) LitBank CoNLL, it does not itself segment raw prose; `detect_scene_boundaries()` assigns one scene-id per already-given sentence via cue-regex + optional character-turnover heuristic. Pure Python dict/set/regex — explicit docstring "GLASS-BOX: pure symbolic; NO torch." `hdlab/semantic_parser.py` is unrelated to this task despite the name: it decodes pre-built synthetic HRR bundles (random `{-1,+1}` codebooks) via bind/unbind + cosine cleanup — it never sees English text at all (its own docstring states this). Neither file extracts clause-level or event-level (predicate+argument) units from continuous prose. Representation: symbolic string/regex (scene_segment), HRR-on-synthetic-bundles (semantic_parser, not applicable here). No registry row for either as a segmentation capability.

**(b) The exact brain mechanism.** Event Segmentation Theory (Zacks & Swallow 2007; Zacks-Franklin SEM extension of Rao-Ballard/Friston predictive coding). Perceptual/comprehension event boundaries are detected online, continuously, via transient spikes in prediction error from a hierarchical generative model of "what happens next" — posterior temporal cortex (MTG/STS) + hippocampus. Boundaries occur simultaneously at multiple grain sizes (fine-grained clause/action boundaries nested inside coarse-grained scene boundaries), not from a closed-class cue-word lookup. SHAPE: online PE-triggered, hierarchical, multi-grain. POSITION: early-to-mid in the comprehension hierarchy, downstream of lexical/perceptual input, directly upstream of situation-model updating (a new event boundary is exactly when the situation model gets a fresh entity/role write). METRIC: agreement with human event-boundary judgments (inter-subject reliability is very high, e.g. Newtson/Zacks segmentation-agreement studies), and correlation of transient BOLD/PE spikes with subject-marked boundaries.

**(c) The gap:** SHAPE-mismatch + POSITION-mismatch at the coarse (scene) level — cue-word lookup table instead of PE-driven hierarchical segmentation. MISSING-ENTIRELY at the clause/event level — no organ anywhere in the repo extracts predicate+argument event units from continuous raw prose (the closest thing, `candidate_generator.py`'s UD parse, is examined under Component 3 and does produce verb-argument candidate pairs, which is a partial substitute, but it presupposes sentence-tokenized input, not boundary detection).

**(d) Severity.** Currently **masked, not acute** — most downstream cells in this pipeline consume pre-segmented (CoNLL / oracle) sentences, so the missing PE-driven segmenter isn't the thing failing today's tests. It becomes load-bearing the moment the pipeline is asked to run on raw, un-pre-chunked prose (which is the eventual target). Rank: latent dependency, not today's blocker.

---

## Component 2 — ENTITY IDENTITY + COREFERENCE

**(a) What we actually have.** `hdlab/coreference_resolver.py` is substantial and disk-verified WIRED+USED (registry row `coreference_resolver_match_or_allocate_strict_cb_principle_b`, `gate_decision: WIRE`, `pipeline_status: WIRED_AND_PIPELINE_USED`). Key selection function `_pick_strict_cb(compat, cur_clause)`:
```python
def _pick_strict_cb(compat, cur_clause):
    scored = [(e, e.most_recent_subject_clause(cur_clause)) for e in compat]
    with_subject = [(e, c) for e, c in scored if c is not None]
    if with_subject:
        best_c = max(c for _, c in with_subject)
        tied = [e for e, c in with_subject if c == best_c]
        return max(tied, key=lambda e: e.last_pos)
    return max(compat, key=lambda e: e.last_pos)
```
This is **not** a pure-recency selector: primary key = most recent clause where the candidate held a subject/agent role (a Centering-theory backward-looking-center pick); recency (`last_pos`) is only the tiebreak/fallback tier. A separate function, `run_match_or_allocate`, uses `TrackedEntity.salience(now) = count + beta * exp(-lambda * (now - last_pos))` — a frequency-primary, recency-secondary blend. `run_principle_b` layers a same-clause-agent exclusion filter before calling `_pick_strict_cb`; `run_principle_b_deixis` layers a quote-speaker/addressee exclusion. Disk metrics: match-or-allocate HARD_PASS vs recency-floor+random baselines; confidence-calibration AUC 0.65-0.75; deixis lever +0.035/+0.08 on identity-demanding queries; "honest mode" 136/136 correct "it/its" flags with 0 fabricated attaches on real Anne of Green Gables chapters.

**IMPORTANT CORRECTION TO THE TASK'S PREMISE:** the task brief states `_pick_strict_cb` is "recency-falsified 0/4." No file, comment, `metrics.json`, or verify script anywhere in `coreference_resolver.py` or its registry row corroborates this — and the code itself contradicts a pure-recency characterization (subject/agent-role history is the primary key, not mention position). This claim likely refers to a **different, not-yet-built** generalized coherence/binding selector (the goal-outcome discourse-binding work named elsewhere in project memory — a distinct experiment, not this organ). **This audit could not locate the "0/4" artifact and flags the discrepancy rather than propagating it.**

**(b) The exact brain mechanism.** Hippocampal relational/associative memory retrieval + Centering Theory (Grosz/Joshi/Weinstein) cue-based competition: multiple constraints (grammatical-role salience — subjecthood/topichood privileged as the "backward-looking center" — plus recency, gender/number agreement, semantic fit) are integrated in a competitive retrieval (cf. Gordon & Hendrick cue-based retrieval; Lewis & Vasishth ACT-R-style interference models). SHAPE: competitive multi-cue retrieval with grammatical-role-weighted salience as the dominant cue, not recency alone. POSITION: mid-level; depends on clause-level role assignment (subject/agent tagging) — i.e. depends on Component 3's output, at least for the `_pick_strict_cb` role-history feature. METRIC: accuracy resolving a pronoun/definite-NP among 2+ semantically-plausible antecedents (competitive-candidate tests), N400/ERP discourse-integration cost as a converging measure.

**(c) The gap:** essentially FAITHFUL at the algorithmic (Marr L2) level — role-salience-tiered backward search with recency fallback mirrors the Centering-Cb mechanism reasonably closely; representation is symbolic (dict/struct) rather than a neural population code, which is a Marr-L1 REPRESENTATION-mismatch but is accepted under this project's glass-box discipline (not itself the deficit being chased). One real gap: `_pick_strict_cb`'s role-history feature (`most_recent_subject_clause`) needs upstream SUBJECT/AGENT tags — which per Component 3 below are syntactic-position tags, not true thematic AGENT tags, so this organ's role-salience cue is only as good as the (currently syntactic, not thematic) tags feeding it.

**(d) Severity.** **NOT the current load-bearing gap.** This is the most mature, best-validated organ in the 6-component chain. The task's embedded premise that this organ is broken (recency-only, falsified) does not hold up on disk read; treat with caution until the actual "0/4" artifact is located (see (a)).

---

## Component 3 — THEMATIC ROLE LABELING

**(a) What we actually have.** THREE candidate organs checked; **none performs general thematic role labeling from text.**
- `hdlab/role_slot_summarizer.py`: "roles" = a fixed 4-way symbolic partition `S_ROLES = {SUBJECT, OBJECT, TEMPORAL, SCHEMA}` — syntactic storage buckets, not AGENT/PATIENT/EXPERIENCER/GOAL. The class never inspects text: `summarize_role(item_keys, role_assign, val_indices)` takes `role_assign` (an integer bucket index) as a **caller-supplied input parameter**. It's an HRR capacity/sharding primitive (flat-bundle-vs-sharded-storage), with role assignment happening entirely upstream, outside this module.
- `hdlab/candidate_generator.py`: produces unlabeled `(verb_idx, arg_idx)` pairs from an unlabeled dependency parse, tagged only by syntactic construction-pattern (`core_dep`/`relcl_gap`/`coord`/`conj_obj`) — explicitly documented as unable to distinguish subject from object ("HEURISTIC and OVER-GENERATES ... cannot tell subject from object").
- `hdlab/situation_reader.py::_assign_roles(pred_idx, sent_noms)` **is** a real text-facing AGENT/PATIENT assigner, and the closest thing to thematic-role labeling that exists: "AGENT = the subject-mention (rank 0) if before/at the predicate else nearest preceding nominal; PATIENT = nearest nominal strictly after the predicate" — a purely **positional heuristic**, not verb-semantic. Registry (`situation_model_accumulate_register_organ` row, `revival_criteria` field) records its measured real-text accuracy: **0.231 vs an oracle ceiling of 1.000** — i.e., near-floor on real text, and by construction it cannot handle passive voice, ditransitives, or experiencer-subject verbs (it will assign AGENT/PATIENT by clause position regardless of voice).
- `hdlab/event_bundle.py`: `DEFAULT_ROLES = (PRED, AGENT, PATIENT, TENSE)` is just the fixed HRR role-key vocabulary for binding — it consumes already-assigned AGENT/PATIENT strings, it does not assign them.
- `experiments/exp_coherence_role_compat_score_selector_v1.py`: roles are **100% hand-supplied hardcoded literals** authored directly in the item-construction code (`ROLE_TYPES = [AGENT_OF_ATTEMPT, EXPERIENCER_OF_OUTCOME, AGENT_OF_UNRELATED, EXPERIENCER_OF_UNRELATED]`), self-declared in its own docstring: "role LABELS are read symbolically for scoring, NOT via decode()... NOR that role-structure can be EARNED from raw text (supplied here, not learned)." Confirms it is not an extraction result.

No registry row anywhere grades a general thematic-role-labeling capability. `notes/capability_reconciliation_invisible_islands_audit.md` HIGH-tier list (ToM, grounded-appraisal, VAMP-EP, action_selection, slot_attention_wm) was checked and contains **no thematic-role-extraction island** — so this is not a "we already built it and forgot to wire it" situation.

**(b) The exact brain mechanism.** Verb argument-structure processing in posterior/mid temporal cortex + IFG (Broca's area homolog): thematic-role assignment integrates the verb's lexical-semantic selectional frame (what roles this specific verb licenses, e.g. experiencer-subject verbs like "fear" vs agent-subject "kick") with multiple probabilistic surface cues — word order, animacy, case-marking, voice-marking (competition-model integration, MacWhinney; agrammatic-comprehension deficits in Broca's aphasia, Grodzinsky/Caramazza, show role assignment fails specifically when word-order cues are stripped by passivization, demonstrating the brain's mechanism is NOT purely positional). SHAPE: verb-frame retrieval + multi-cue integration producing labels (agent/patient/experiencer/goal/instrument) that generalize across active/passive/ditransitive/experiencer-subject constructions. POSITION: mid-level, depends on lexical-semantic verb knowledge + syntactic parse; is the DIRECT upstream input to situation-model binding (Component 4) and to any coherence-based selection over that binding (Component 5). METRIC: role-assignment accuracy across construction types — the diagnostic test is specifically generalization to passive/non-canonical order, since a positional heuristic is definitionally unable to pass it.

**(c) The gap:** MISSING-ENTIRELY as a general (verb-semantic-cue-integrating) thematic-role labeler. The one real attempt (`_assign_roles`) is SHAPE-mismatch (position-only, no verb-frame/animacy integration) and independently measured near-floor on real text (0.231 vs 1.0 oracle).

**(d) Severity: LOAD-BEARING.** This is the direct upstream dependency of both Component 4 (situation-model binding needs role-tagged fillers) and Component 5 (coherence-scoring needs role labels to score over); every organ downstream currently either bypasses this step (oracle/hand-supplied roles, confirmed in Component 5) or inherits a 0.231 real-text ceiling. **This confirms the Director's hypothesis stated in the task brief** — thematic-role-labeling is the real bottleneck, not coherence-selection (which prior work already bounded, see Component 5).

---

## Component 4 — SITUATION-MODEL BINDING

**(a) What we actually have.** `hdlab/situation_model_accumulate.py`, FHRR complex64 representation (`unit_phase_vec`, random unit-magnitude phase vectors). `AccumulateRegister.add_event(entity, role, event_idx)`: `bound = bind(role_vecs[role], idx_vecs[event_idx])`, appended (or overwritten) into a per-entity list; `register(entity)` bundles (superposes) all bound pairs for that entity; `decode(entity, event_idx)`: unbinds by the event-slot key then cosine-cleanup-argmaxes against the role vocabulary to recover the role string. `CausalLinkRegister(AccumulateRegister)` repurposes the same machinery for CAUSE/EFFECT event-to-event links, writing both directions and tracking `_roles_present` to guard unbound decodes. Disk: registry row `situation_model_accumulate_register_organ`, status `vet_confirmed_measured_mechanism_construction_proof_2026-08-02`, WIRED+USED as the pipeline's hub (~20 frontier consumers per the functional map). Binds (role, event-slot) pairs **per entity** — entity is a dict key selecting which register to use, not itself bound into the FHRR vector, so this is N per-entity 2-slot registers rather than one joint (entity,role,event) 3-way bind — a modeling simplification, not a correctness bug (each entity's register is independently addressable, which is what's needed).

**(b) The exact brain mechanism.** Hippocampal relational/conjunctive binding (CA3 pattern-completion / associative binding), instantiating the Kintsch construction-integration situation model / Zwaan event-indexing model (protagonist, space, time, causality, intentionality dimensions), continuously updated as new information arrives (DMN/mPFC-hippocampal event-model circuit). SHAPE: binds role x filler into an addressable, incrementally-updatable per-entity representation supporting overwrite as well as accumulation. POSITION: consumes role-labeled arguments (Component 3 output) + coref-resolved entity identity (Component 2 output); feeds query/readout for goal-owner attribution. METRIC: accuracy of entity-state read-back after intervening updates (situation-model updating paradigms, e.g. Zwaan protagonist-location studies).

**(c) The gap:** broadly **FAITHFUL** — right SHAPE (bind + bundle/superpose + cleanup-decode), right POSITION (consumes role-labeled input, feeds query). The known limitation is a capacity/scaling gap, not a shape gap: the functional map documents a certified K=4096 multibank fix (`working_memory.py`/`situation_model_multibank.py`) sitting ISLANDED (unwired) while the live reader uses the flat, unsharded `AccumulateRegister` — this will wall on longer/denser passages but is orthogonal to the goal-owner question at typical passage lengths. `CausalLinkRegister`'s 0.9722 given-link read/write capacity is verified and explicitly documented as NOT a selector (that's Component 5's job) — consistent finding, no new gap here.

**(d) Severity.** **NOT the load-bearing gap.** This organ works correctly given correct role-labeled input; it is starved by Component 3's near-floor real-text role extraction, not broken itself.

---

## Component 5 — ROLE-FIT COHERENCE SCORE

**(a) What we actually have.** `experiments/exp_coherence_role_compat_score_selector_v1.py::_role_compat_score(established_props, w_table)`:
```python
def _role_compat_score(established_props, w_table):
    """Plain symbolic dict lookup + sum -- no FHRR cosine, no event-count term, no vector geometry anywhere."""
    return float(sum(w_table.get(role, 0.0) for role, _slot in established_props))
```
Confirmed deterministic symbolic dict+sum, no FHRR vector math anywhere on the scoring path (an `AccumulateRegister` is built and populated for "node provenance" only; `.decode()` is exercised only in `self_test()`, never in scoring). `w_table` (`W_GOAL_OWNER`) is a hand-authored weight dict; roles are the hand-supplied labels from Component 3's audit above. Disk verdict: `HARD_PASS_ROLE_COMPAT_SCORE_MECHANISM_CAPACITY_EXISTENCE_PROOF_N1`, explicitly self-scoped as a "mechanism-capacity proof over SUPPLIED role-structure," with a scrambled-weight-table control collapsing to `margin_mean = -2.0` — i.e. the "coherence" signal is literally "does the hand-labeled role match the hand-picked target label," a near-tautology by the cell's own admission.

Separately, `hdlab/self_improving_loop.py::decode_coherence_margins()` builds an `AccumulateRegister`, decodes each position, and returns `top1_score - runnerup_score` from the FHRR readout distribution — confirmed a purely geometric decode-separation ("cleanliness") measure; own docstring says "gold-free," never inspects role-label content. Its disk history: the cell that used it as the primary selector signal, `exp_coherence_role_conflict_crosstalk_v1`, registered `HARD_FAIL_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL` — motivating the symbolic workaround above.

Broader `coherence_selector` v1-v4 series (disk-verified metrics.json): v1 `HARD_FAIL`; v2 `HARD_PASS` (synthetic novel-entity, acc 1.0 vs recency 0.0); v3 `MIDDLE_BAND` (novel types, 1-hop acc 0.87, "right mechanism class, underpowered"); v4 `HARD_FAIL_NO_MULTIHOP_LIFT` (2-3 hop collapse to floor); `text_transfer_v1` `CANNOT_BRIDGE_REPRESENTATION_GAP` (sim acc 0.84 vs real-text near-chance 0.43); `grounded_coherence_selector_v1` `GROUNDED_PARTIAL_LEXICAL_PROXY` (text n=7 acc 0.71 vs gold-recency 0.0 — promising but n=7 is small).

**(b) The exact brain mechanism.** Coherence-based / abductive referent and role selection during discourse comprehension: plausibility-weighted competitive resolution combining thematic fit, causal-network coherence, and explanatory fit with the prior discourse (Kintsch construction-integration's constraint-satisfaction SETTLING dynamic; Trabasso & van den Broek causal-network coherence; Graesser constructionist inference). Critically this is NOT a static weighted-label-sum — it is an iterative, CONTENT-sensitive relaxation process over graded semantic representations, akin to attractor/pattern-completion settling, integrating multiple soft constraints simultaneously and able to reject a structurally-plausible-but-causally-implausible foil. SHAPE: iterative multi-constraint content-sensitive settling. POSITION: consumes role-labeled + bound situation model (Components 3+4 output); is the actual decision computation for "who owns this goal" among competing candidates. METRIC: correct selection among a structurally-matched but causally-wrong foil (an "anti-positional" control is the diagnostic test for whether real coherence, not surface position, is driving the choice).

**(c) The gap:** SHAPE-mismatch — static dict-lookup/weighted-sum instead of iterative content-sensitive constraint settling — compounded by the fact that its input isn't yet content-derived at all (roles are hand-supplied per Component 3), so there is currently no real coherence computation happening on real text; the existence-proof result is a label-matching tautology, not evidence the mechanism works on earned content. Classify: MISSING-ENTIRELY as a genuine real-text content-coherence selector; PARTIAL as a mechanism-capacity proof in the synthetic/idealized regime (useful as a scaffold, not as a working capability).

**(d) Severity.** Load-bearing IN PRINCIPLE (this is literally the "who owns the goal" decision), but **currently secondary to Component 3** — even a perfect coherence selector cannot discriminate on real text while its role-label input sits at 0.231 accuracy. This matches and confirms the framing already in project memory that coherence-selection was "already bounded" this session — the newly-confirmed reason is specifically the missing upstream role-extraction, not a flaw intrinsic to the coherence-selection idea.

---

## Component 6 — SELECTION + ABSTAIN

**(a) What we actually have.** `hdlab/self_improving_loop.py::decide_keep_or_revert`:
```python
def decide_keep_or_revert(agg_deltas, abstain_band=ABSTAIN_BAND_DEFAULT):  # ABSTAIN_BAND_DEFAULT = 0.02
    if not agg_deltas:
        return None
    best = max(agg_deltas, key=lambda name: agg_deltas[name])
    return best if agg_deltas[best] > abstain_band else None
```
Pure, stateless: argmax over a caller-supplied `{name: score}` dict, adopt iff strictly above the fixed 0.02 threshold, else abstain (`None`). No side effects — no store write, no logging inside this function; any persistence happens in the calling experiment cell. Confirmed disk-read, matches its own docstring accurately for once.

**(b) The exact brain mechanism.** ACC (anterior cingulate)/dlPFC conflict-monitoring and confidence-gated commitment (Botvinick conflict-monitoring theory; converges with drift-diffusion boundary/threshold models of perceptual decision-making) — a decision/update is committed only when accumulated evidence clears a threshold above baseline noise; otherwise the default (no-update / hold-prior) state persists. SHAPE: threshold-gated argmax-commit over an evidence signal, abstain within a noise band. POSITION: final-stage decision layer downstream of all evidence accumulation (Components 3-5); does not generate content, only gates commitment. METRIC: calibration — false-adopt rate under noise vs correct-adopt rate under real signal (an ROC/AUC-style property), not accuracy alone.

**(c) The gap:** essentially FAITHFUL at the algorithmic level — right function (threshold-gated commit-or-abstain). Minor fidelity note: a single fixed scalar threshold is a simplification of the brain's graded/probabilistic (drift-diffusion-style) boundary — a METRIC/calibration nuance, not a structural violation.

**(d) Severity.** PERIPHERAL. Correctly implements the gating function it claims to, but is entirely downstream-bound by signal quality from Components 3/5 — "garbage in, garbage out." Fixing this organ cannot fix goal-owner attribution.

---

## SYNTHESIS

### Summary table

| # | Component | Have (disk-verified) | Brain mechanism | Gap-class | Load-bearing? |
|---|---|---|---|---|---|
| 1 | Text segmentation | Rule-based scene-cue regex over pre-segmented sentences; no clause/event extraction | PE-driven hierarchical Event Segmentation (Zacks SEM) | MISSING-ENTIRELY (clause/event level); SHAPE-mismatch (scene level) | Latent — masked while pipeline consumes oracle-pre-parsed input |
| 2 | Coreference | Centering-Cb subject/agent-role-tiered backward search + salience blend; VET-confirmed, WIRED+USED | Hippocampal/Centering cue-based competitive antecedent retrieval | Largely FAITHFUL (representation-only Marr-L1 gap) | NOT currently load-bearing (task's "recency-falsified" premise not corroborated here) |
| 3 | Thematic role labeling | MISSING general labeler; sole real-text attempt is a positional heuristic at 0.231 acc vs 1.0 oracle; other organs use syntactic slots or hand-supplied roles | Verb-selectional-frame + multi-cue integration (temporal/IFG) | MISSING-ENTIRELY (general) / SHAPE-mismatch + near-floor (the one heuristic) | **LOAD-BEARING — confirms Director's hypothesis** |
| 4 | Situation-model binding | FHRR bind/bundle/cleanup AccumulateRegister/CausalLinkRegister; VET-confirmed, WIRED hub | Hippocampal relational binding (Kintsch CI / Zwaan event-indexing) | FAITHFUL (capacity-scaling gap only, islanded fix exists) | NOT load-bearing — starved by #3, not itself broken |
| 5 | Role-fit coherence score | Deterministic symbolic dict+sum over hand-supplied roles+weights (existence-proof only); decode_coherence_margins = content-blind geometric cleanliness; v1-v4 series fails to transfer to real text | Iterative content-sensitive constraint-satisfaction settling (Kintsch CI / Trabasso causal network) | SHAPE-mismatch (static lookup vs settling) + effectively MISSING on real text | Load-bearing in principle, but SECONDARY (bounded by #3) |
| 6 | Selection + abstain | Pure threshold-gated argmax/abstain function | ACC/PFC confidence-gated commitment | FAITHFUL (fixed vs graded threshold is a minor metric nuance) | Peripheral (garbage-in/garbage-out) |

### Ranked gaps

1. **Component 3 (thematic role labeling) is the top gap and the load-bearing one.** The Director's hypothesis holds: thematic-role-labeling, not coherence-selection, is the real bottleneck for goal-owner attribution. No organ in the repo does general verb-cue-integrating role assignment from text; the one real-text attempt is a positional heuristic independently measured at 0.231 accuracy against a 1.0 oracle ceiling (cross-corroborated between this audit's direct code read and the `situation_model_accumulate_register_organ` registry row's `revival_criteria` field — same number from two sources).
2. **Component 5 (role-fit coherence score) is the second-highest-leverage gap, but it is downstream-blocked by #1.** Its current form is a content-blind label-matching existence proof (scrambled-weight control collapses, confirming near-tautology), not a working real-text coherence mechanism. Building real content-sensitive coherence settling before role labels exist would test a mechanism with no real input to feed it — sequencing matters.
3. Components 2, 4, 6 are comparatively solid and should **not be re-touched** — they are FAITHFUL at the algorithmic level and are being starved, not broken. Component 1 (segmentation) is a real but currently-latent gap; it will matter once the pipeline stops consuming oracle-pre-parsed sentences.

### Is the top gap a BUILD, a FIX, or an ISLAND?

**BUILD NEW.** `notes/capability_reconciliation_invisible_islands_audit.md`'s HIGH-tier island list (ToM, grounded-appraisal, VAMP-EP, action_selection, slot_attention_wm) was checked directly and contains **no thematic-role-extraction organ** sitting unwired — this is not a "we already built it and forgot to wire it" case. The nearest asset, `situation_reader.py::_assign_roles`, is a positional heuristic near floor on real text; it is a starting scaffold at best (right POSITION and I/O shape — consumes nominal-mention data, emits AGENT/PATIENT strings that plug directly into `event_bundle.py`'s existing role-key vocabulary), not something to extend incrementally toward brain fidelity, since its SHAPE (position-only) is the actual defect, not a parameter to tune.

**Brain-faithful build direction:** a verb-lexicon-driven selectional-frame + cue-integration labeler (MacWhinney competition-model style) that combines (i) a small per-verb selectional-frame table (which argument slot maps to AGENT/PATIENT/EXPERIENCER/GOAL for that verb, keyed off a verb-class dictionary — glass-box, hand-supplied knowledge is acceptable per project convention, the MECHANISM must be earned/native, not the knowledge) with (ii) surface cues already available in the pipeline (voice detection, animacy via the existing `animacy_lexicon.py`, and the unlabeled dependency-arc structure `candidate_generator.py` already extracts) — explicitly designed to be tested for generalization across active/passive/ditransitive/experiencer-subject constructions, since that generalization test is exactly what falsifies a positional heuristic and exactly what the brain mechanism passes.

### Honest note: which components are done

Components 2 (coreference), 4 (situation-model binding), and 6 (selection+abstain) are genuinely FAITHFUL at the algorithmic level, VET-confirmed, and WIRED — do not re-audit or rebuild these without new evidence. Component 1 (segmentation) is a known, correctly-classified latent gap (not urgent). The real frontier is narrowly Components 3 and 5, in that dependency order.

---

**Caveats.** (a) The task brief's premise that `_pick_strict_cb` is "recency-falsified 0/4" could not be corroborated against `coreference_resolver.py` on disk — flagged, not silently accepted; likely conflates with a different, unbuilt generalized coherence-binding selector. (b) `_assign_roles`'s 0.231 real-text number and this audit's independent code read of the same function agree (cross-source corroboration), raising confidence in that figure specifically. (c) Two generic-term lit-scans were not dispatched this cycle — the audit is code/disk-only per the task's explicit instruction ("VERY careful and clear" on the pipeline, not a literature question); no query-privacy risk incurred.

P_deflated on the ranking (thematic-role-labeling as top load-bearing gap) = **0.65** (disk-verified from 3 independent code reads + cross-corroborated 0.231 number from two sources; deflated from a naive ~0.85 per lit-scan/audit calibration discipline because (i) the "0/4" discrepancy in Component 2 shows this audit's disk-read can diverge from prior-session claims and a similar undiscovered discrepancy could exist elsewhere, (ii) severity ratings for Components 1/5 as "secondary" rest on an assumption — that fixing #3 alone unblocks #5 — which is untested).
