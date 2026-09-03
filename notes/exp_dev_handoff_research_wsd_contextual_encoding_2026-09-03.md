# exp_dev hand-off — research: WSD contextual-encoding vs bag-of-context-words

**Filed by:** research sub-agent, 2026-09-03.

**Trigger:** `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` — drill into
why the bag-of-context-words / WordNet-gloss comparator caps at ~0.33-0.35 on rare (subordinate)
senses while a supervised bi-encoder reaches ~0.53 on the same population. Finding: the cap is
upstream of every lever already tried on `reader_meaning_channel` (additive frequency-prior:
REFUTED, MFS floor not cleared; per-dimension multiplicative gain C3: HARD_FAIL on estimation noise,
blocked behind B4; attractor settling C4: explicitly declined). Two new candidates target the QUERY
CONSTRUCTION itself rather than re-scoring or re-settling the existing 256-dim comparator, and are
NOT blocked behind B4 the way C3 is.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent).

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, seed count, threshold bands, corpus split sizes, queue choice, cell name,
smoke profile, FULL profile. This hand-off does NOT specify numerical parameters beyond the
HARD-PASS/HARD-FAIL logic already pre-registered in the research note.

---

## Anchor candidates (rank-ordered)

1. **Dependency-filtered second-order context vector, replacing the flat bag-of-context-words query**
   (PRIMARY — cheap decisive test).
   - Anchor pointer: `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md`,
     section "Cheap decisive test" + Arm 1 falsifiable predictions.
   - Substrate-product reading: drop-in replacement for the query representation ONLY — same
     WordNet gloss targets, same argmax decision rule, same corpus. Requires a dependency parse
     (infrastructure already scoped for the verb-affectedness problem, `notes/research_drill_word_
     sense_disambiguation_frame_selectional_2026-07-21.md`) + a relation-typed co-occurrence table.
     No training. Mechanism: Erk & Padó 2008 (ACL D08-1094) / Thater, Fürstenau & Pinkal 2011
     (ACL I11-1127) — weight/gate context words by dependency relation to the target instead of
     flat-window averaging.
   - Mandatory control: same-cardinality RANDOM subset of context words (rules out "fewer/sparser
     context words helps" as the real driver instead of syntactic relevance).
   - Split requirement: score separately on TOPIC-CONFOUNDED items (rare sense's context shares
     topic with its dominant twin — the case this drill targets) vs TOPIC-DISTINCT items (control
     bucket). HARD-PASS requires the gain to concentrate on the TOPIC-CONFOUNDED bucket, not just a
     uniform lift.
   - Tier: likely CPU/local (parse + co-occurrence table build, no GPU training).
   - Why now: two independently-converging literatures (psycholinguistic governor/frame primacy,
     2026-08-05 deepdrill; pre-transformer computational semantics) name the same fix; not blocked
     behind any open substrate-capacity question.

2. **Exemplar retrieval instead of per-sense centroid averaging** (companion, cheap, near-zero
   additional infrastructure).
   - Anchor pointer: same research note, Arm 2 falsifiable predictions.
   - Substrate-product reading: do not collapse a sense's training context instances into one
     averaged vector before comparison — keep individual instances, do k-NN retrieval/similarity
     voting at inference. Mechanism: Erk & Padó 2010 (ACL P10-2017, exemplar-based WSD); grounded in
     Nosofsky's Generalized Context Model and this project's own already-PINNED Tyler & Moss CSA
     finding (ORGAN_MAP C4) that averaging washes out weakly-correlated distinctive features.
   - Mandatory control: replace retrieved exemplars with same-count RANDOM noise vectors (per this
     project's own "an empty/degenerate representation can score perfectly on a rank metric"
     finding — report tie density and both rank conventions, not just the optimistic one).
   - HARD-PASS should concentrate on senses with FEW training exemplars (< 5), where centroid
     dilution by a topic-sharing dominant twin is most severe.
   - Tier: local (no parse needed, reuses existing context-instance storage if the accumulator is
     changed to retain instances rather than sum-then-discard — same diagnosed pattern as ORGAN_MAP
     B3's "graded quantity built and thrown away one line before use").
   - Why now: fallback if anchor 1 HARD-FAILs; attacks the same diagnosed failure (averaging
     destroys discriminating minority signal) from the storage side rather than input-construction.

3. **Small recurrent "Sentence Gestalt"-style contextual encoder** (ceiling candidate, NOT a
   first-build — flag for scoping only if 1-2 both under-deliver).
   - Anchor pointer: same research note, mechanism candidate #3 (Rabovsky, Hansen & McClelland 2018,
     *Nat Hum Behav*, full text read — architecture: ~100-hidden-unit RNN, gestalt state updated
     word-by-word, N400 = magnitude of state update, validated against 16 N400 phenomena).
   - Substrate-product reading: the only candidate that gives a genuinely BERT/BEM-like
     representation (computed over full sentence history, not a window) while staying glass-box and
     tiny — but requires a real build decision (train from scratch on this project's actual corpus
     vs. port the published SG-model's artificial-microworld training regime) that this hand-off
     does NOT make. No falsifiable prediction pre-registered — exp_dev should NOT build this without
     a separate scoping pass.
   - Why now: held in reserve, not dispatched this cycle.

---

## Context pointers (pointers, not summaries)

- `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` — this drill, full
  mechanism detail + citations + cross-thread synthesis.
- `notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md` — the REFUTED
  frequency-prior arm; do not re-propose the additive-scalar-term fix.
- `notes/ORGAN_MAP.md` sections C2/C3/C4/B3/B4 — REQUIRED READ before building: C3's HARD_FAIL
  mechanism (estimation noise at 256-dim/~70-obs, not mechanism-wrong), C4's explicit
  do-not-build-attractor-settling recommendation and its Tyler & Moss CSA citation, B4's
  representation-capacity framing.
- `notes/research_drill_word_sense_disambiguation_frame_selectional_2026-07-21.md` — existing
  dependency-parse + VerbNet-frame infrastructure anchor 1 should reuse.
- `notes/lit_scan_semantic_control_near_neighbour_2026-08-13.md` — Tyler & Moss CSA distinctive-
  feature-fragility finding anchor 2 builds on.
- `notes/STATUS.md` (search "reader_meaning_channel") — current REFUTED verdict and its numbers
  (0.4702 vs 0.4778, MFS floor).

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands are already
  drafted in the research note; exp_dev finalizes exact N / seed count / thresholds before smoke.
- Self-test per [[feedback-formula-selftests]].
- Mandatory controls are NOT optional: random-subset-of-context-words control (anchor 1),
  random-noise-exemplar control (anchor 2) — both required per this project's own repeated finding
  that a sparser/emptier representation can look like a win on a rank-based metric for reasons
  unrelated to information content.
- Multi-seed FULL on smoke clearance; replication gate per `tools/replication_gate.py`.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: cell name, N, seed count, threshold bands (within the HARD-PASS/HARD-FAIL
logic pre-registered above), queue choice, ETA, smoke profile, FULL profile, and whether to build
anchor 1, anchor 2, or both in this cycle. This hand-off passes anchor POINTERS + mandatory-control
requirements only — not numerical parameters. Anchor 3 is explicitly NOT authorized for build this
cycle without a separate scoping pass.
