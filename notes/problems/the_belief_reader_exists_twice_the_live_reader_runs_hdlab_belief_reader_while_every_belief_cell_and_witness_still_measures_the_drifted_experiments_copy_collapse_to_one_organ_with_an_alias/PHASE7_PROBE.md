# pri 139 — PHASE 7 PROBE (strategy), 2026-09-16

Answers to A–F. Every number measured in this session; "not found after X" where nothing was found.
Arms live in `experiments/exp_belief_one_organ_v1.py` behind `--arms H,I,J` (they write to
`data/exp_belief_one_organ_v1_phase7/` and leave the landed A–G metrics untouched).

---

## C. THE STANDING ONE-OBJECT CHECK — shipped, and the census is worse than two pairs

**`verification/test_organ_copies_are_one_object.py`** — 4 checks, green today, proven can-fail.

**16 `hdlab/X.py` ↔ `experiments/_X.py` pairs on disk. 14 are DRIFTED COPIES. 2 are thin shims. NONE is
an alias.** pri 137 and pri 139 are 2 of the 14; **12 were unknown before this probe.**

| pair | organ compared | diff lines |
|---|---|---|
| `joint_relation_frontend` | `hdlab.joint_relation_frontend` | **491** |
| `temporal_ordering` | `hdlab.temporal_model` | **891** |
| `temporal_order_register` | `hdlab.temporal_model` | **847** |
| `temporal_ordering_multiframe` | `hdlab.temporal_model` | **834** |
| `space_reader` | `hdlab.space_reader` | 128 (pri 137, diff written) |
| `sem_event_segmenter` | `hdlab.sem_event_segmenter` | 82 |
| `composed_hub_predictor` | `hdlab.composed_hub_predictor` | 74 |
| `belief_reader` | `hdlab.belief_reader` | 51 (pri 139, diff written) |
| `causal_reasoner` | `hdlab.causal_reasoner` | 35 |
| `aspect_interval` | `hdlab.aspect_interval` | 33 |
| `structured_matcher` | `hdlab.structured_matcher` | 31 |
| `occ_appraisal` | `hdlab.occ_appraisal` | 23 |
| `causal_network` | `hdlab.causal_network` | 10 |
| `polarity_operator` | `hdlab.polarity_operator` | 6 |
| *(thin shims, safe)* | `force_dynamics_lexicon`, `patient_tendency` | — |

**Two classifier details that matter, because a naive version would have under-counted by four:**

1. **It resolves one level of hdlab-side re-export shim.** `hdlab/temporal_order_register.py` is 34 lines
   that re-export `hdlab/temporal_model.py` (the 2026-09-11 consolidation). Compared against the *shim*,
   the three `experiments/_temporal_*.py` files share no names and score UNRELATED — hiding three copies
   of the real organ, 834–891 diff lines each. Resolved to `hdlab.temporal_model` they are the largest
   drifts on the board.
2. **A "few top-level names" rule mis-clears a real copy.** `experiments/_structured_matcher.py` imports
   from `hdlab` and declares only 2 top-level names — but it is **354 lines of its own implementation**.
   The witness uses a ≤ 60-line cap instead.

**Can-fail, proven:** removing one name from the baseline (simulating a fresh promotion that leaves a copy
behind) turns W2 red and exits 1 — `FAIL W2 NO NEW DRIFT ... NEW DRIFTED PAIRS: ['occ_appraisal']`.

**The baseline is an inventory that should shrink, not an allowance.** Each of the 14 is a LOCATED item:
a set of measurements that may describe a module the product does not run. `joint_relation_frontend`
(491 lines) and the three `temporal_*` (834–891) are the ones I would look at next, because the drift is
large enough that the copy is a different organ, not a stale one.

---

## D. TORCH — measured, not inspected; and my Phase-6 framing was too narrow

**What I said in Phase 6:** torch is reachable from the read via `grounded_similarity.py:83`, used for
tensor arithmetic over static norms, therefore admissible.

**What is actually true — the scope was much larger than one file, and the conclusion survives anyway.**

* **68 of the `hdlab/` modules import torch**, not one. The op profile repo-wide is the substrate's own
  arithmetic: `torch.zeros` 51, `torch.stack` 48, `torch.tensor` 45, `torch.randn` 24, `torch.from_numpy`
  23, **`torch.complex` 23 / `torch.conj` 13 / `torch.real` 11 / `torch.fft` 6** — the last group is the
  **FHRR binding algebra** (circular convolution in the Fourier domain), which is the substrate, not a
  stand-in for it.
* **There ARE real learned modules and weight files in `hdlab/`:** `hdlab/entity_slot_gate.py:49
  EntitySlotGate(nn.Module)`, `hdlab/slot_attention_wm.py:58 SlotAttentionWM(nn.Module)`, and
  `torch.load` of weight files in `director_kb_query.py` (`R.pt`/`W.pt`/`E.pt`), `director_kb.py`,
  `director_kb_chunk_ingest.py`, and `context_grounded_valence.py:113` (`weights_only=False`).
  `context_grounded_valence` is named in `test_audit_live_standins.py:107` as a **transitive import of
  the reader**, so "is a model loaded at inference?" was a live question, not a rhetorical one.
* 🔻 **MEASURED ANSWER: no.** `torch.load`, `nn.Module.__init__` and `nn.Module.__call__` were each wrapped
  and the live reader run on 2 GUM documents plus a belief query on each:

  | wrapped | calls during `SituationReader.read` + `sm.believes(...)` |
  |---|---|
  | `torch.load` | **0** |
  | `nn.Module.__init__` | **0** |
  | `nn.Module.__call__` | **0** |

  **No learned weight is loaded and no neural module is instantiated or called on the read path.** That
  upgrades the Phase-6 "admissible" call from a source inspection to a measurement. The `nn.Module`
  classes and the `.pt` loads exist in `hdlab/` but are not reached by the reader.

**The numpy replacement — cost and numeric difference.**

* **Repo-wide it is not a swap, it is a port.** 68 modules, and the FHRR path uses complex tensors and
  FFT. numpy can express all of it, but this is a rewrite of the substrate's numeric layer with a
  bit-exactness risk on every landed number, for no BF gain — torch here is a linear-algebra library, and
  the owner's rule targets models and tools at inference, which D has now measured as absent.
* **For the one file where it IS a real option**, `hdlab/grounded_similarity.py` (24 torch references;
  ops: `linalg.vector_norm` ×2, `tensor`, `stack`, `sqrt`, `randperm`, `linalg.eigh`, `equal`, `dot`,
  `float`), I measured the numeric difference directly on its own `_distinctive_transform` covariance
  (36,810 words × 12 dims → a 12×12 matrix):

  | | |
  |---|---|
  | max abs eigenvalue difference, `torch.linalg.eigh` vs `numpy.linalg.eigh` | **8.88e-16** |
  | max abs eigenvector difference (sign-aligned) | **4.16e-15** |
  | relative to the smallest eigenvalue (0.1907) | **4.66e-15** |

  That is float64 round-off — the swap is numerically free *for this file*. It would remove torch from the
  **parser's** import chain (`frontend.py:105 → attachment_arm.py:234 verbarg_arcs →
  incremental_parser.py:49 → grounded_similarity.py:83`), which is the only reason it is interesting:
  it makes the parse path importable without torch. It does **not** remove torch from the substrate.

**Recorded as a lead, per your instruction, not as a defect:** *numpy-replaceable in one file
(`grounded_similarity.py`, 24 references, numerically identical to 4.7e-15); repo-wide it is the FHRR
numeric layer across 68 modules and should stay.*

---

## I. THE COPULA-AS-HEAD ASSUMPTION — counted, and it is contained

**7,984 files scanned** for the defect's signature (a `heads.get(k) == v` lookup within ~900 characters
of a `COPULAR` / `COP_FORMS` reference — "find what depends on the copula", which under UD is nothing).

**One real site:** `hdlab/belief_reader.py:188`. The other three hits are its promoted-away copy
(`experiments/_belief_reader.py:195`) and two lines of my own measuring cell.

➡️ **`hdlab/state_register.py` does NOT share the assumption** — it has no parse access at all (zero
`heads` lookups); it is a pure fold over already-extracted predications. Neither does the
`bind_entity_states` / `entity_states` path. **So there is no board state-row exposure, and B is a
single-site repair.** *(Answer to "count the sites": 1, plus 1 in the copy the pri-139 alias deletes.)*

🔑 **AND THE REUSE FINDING, WHICH CHANGES WHAT B SHOULD SHIP.** The reader already owns a
copular-subject organ: **`hdlab/attachment_arm.py:1274 cop_subject_pairs(toks, pos)`** returns
`(predicate, subject)` pairs for every copular predication in a sentence, built on the merged pri-113
construction set (inverted / fronted / locative / wh / clause-final / parenthetical) plus the two
corrections the **pri-117 board A/B** paid for (the right-hand-head rule across a hyphen; a clausal
subject is not a nominal subject). `attachment_arm.py:1157` even names this "the ROOT CAUSE of the
dominant copular-subject miss".

**So my Phase-6 UD prototype was the wrong shape: it re-implemented, from scratch, an organ the reader
already has and the board already validated.** ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS. The arm that
should ship deletes the belief reader's private copular scan and calls `cop_subject_pairs`. Measured
below (H).

---

## A. THE MENTION HAND-OFF — it measured ZERO, and the reason is one rung further up

**I prototyped the repair, measured it, and it buys nothing as written.** Reporting it as a negative with
the cause, not as a win.

**The 2×2 on 6 GUM documents / 63 tracked facts** (each = an entity file the reader built with ≥ 2
mentions; `fact_cluster` = the reader's own cluster id; value vocabulary = the document's own copular
predicates):

| | shipped extractor | `cop_subject_pairs` organ |
|---|---|---|
| mentions **OFF** (today) | 14 events, 0 by cluster | 15 events, 0 by cluster |
| mentions **ON** (the repair) | 14 events, **0 by cluster** | 15 events, **0 by cluster** |

**`by_cluster` is 0 in every cell — the hand-off changes nothing.** Three candidate causes, separated by
measurement rather than argument:

1. ❌ **Coordinate mismatch** (`wtok_start` document-global, so `_cluster_covering` can never match) —
   **ruled out**: `wtok_out_of_range = 0`, and `hdlab/coref.py:171` documents `wtok_start` as
   *within-sentence*. My bucketing matches `build_backbone`'s exactly.
2. ❌ **The mentions never reach the copular subjects** — **ruled out, and the opposite is true**: of 50
   copular pairs, **48 subjects are covered by a mention** (28 nominal, **20 pronoun**). The hand-off
   delivers real information.
3. ✅ **THE CLUSTER IDS CANNOT MATCH.** `cluster_not_alias = 0 of 48`: not one covered subject belongs to
   a tracked cluster without also matching the alias.

### 🔻 THE ROOT CAUSE: the reader's mention stream has TWO DISJOINT ENTITY-FILE ID SPACES

`hdlab/situation_reader.py:4920-4924`:

```python
for _m in role_mentions:
    if _m.get("is_pronoun"):
        continue                                   # pronouns KEEP the coref-column cluster id
    _c = _online_lab.get(_m["midx"])
    if _c is not None:
        _m["cluster"] = -(int(_c) + 1)             # nominals get a NEGATIVE online file id
```

**Measured on 3 GUM documents:**

| | |
|---|---|
| nominal mentions, **all** with negative cluster ids | **744** |
| pronoun mentions, **all** with non-negative cluster ids | **345** |
| pronoun cluster ids that ANY nominal mention also carries | **0 of 345** |
| per document (pronoun files / nominal files / **shared**) | 25/201/**0**, 188/129/**0**, 132/151/**0** |

**So binding a tracked entity across a name → pronoun boundary through `m["cluster"]` returns nothing BY
CONSTRUCTION**, for every consumer, not just belief. The hand-off diff I prepared would have landed and
measured exactly zero.

### The join already exists — as pri 137's unlanded proposal

`hdlab.situation_reader.unify_entity_files` **is not on the tree**: it is proposed by pri 137's
`space_ground_lever_patch.diff`, with a cell-local copy at
`experiments/exp_space_ground_lever_live_v1.py:75 _unify_local(mentions, resolutions, ...)`. It bridges
the two id spaces using the reader's **own pronoun resolutions** (`sm.coref_resolutions`), and pri 137
measured it worth **+0.3617** on the space dimension (where-is 0.0426 → 0.4043, protagonist files
8.9 → 2.6). This is the same defect, seen from the belief side.

➡️ **THE BELIEF HAND-OFF IS SEQUENCED BEHIND pri 137, not independent of it.** It must pass the
**unified** stream; passing the raw one is a no-op. Re-measured with `_unify_local` applied — numbers in
the addendum below.

### A, re-measured on the UNIFIED stream — and it is real

Re-run as a **3x2** (mentions OFF / RAW / UNIFIED x shipped / `cop_subject_pairs`), 6 GUM documents,
71 tracked facts. `unify_provenance: cell-local (patch not on the tree)`.

| mentions | shipped extractor | `cop_subject_pairs` organ |
|---|---|---|
| **OFF** (today) | 13 events, 0 by cluster | 14 events, 0 by cluster |
| **RAW** (the naive hand-off) | 14 events, **1** by cluster | 14 events, **0** by cluster |
| **UNIFIED** (after pri 137's join) | **31** events, **18** by cluster | **40** events, **26** by cluster |

* **The naive hand-off buys 1 cluster bind out of 71 facts.** That is the id-space split, confirmed.
* **The unified hand-off buys 18** (shipped) **/ 26** (with the copular organ) — the same wiring, 2.4x-3.1x
  the extracted events, from mentions the reader already had and was not passing.
* ➡️ **`belief_mentions_handoff_patch.diff` must NOT land before pri 137.** On today's tree it is a no-op
  (+1 bind); its value is entirely contingent on `unify_entity_files`. Shipped as a diff with that
  sequencing stated, not as a standalone win.

*(Power note: this arm is a COVERAGE/STRUCTURE measurement, not a quality one -- 13-40 events over 71
tracked facts. The load-bearing output is `by_cluster`, not the event counts.)*

---

## B. THE COPULAR ORGAN ON THE WHOLE INSTRUMENT — a coverage gain, not a discrimination gain

Swapping the belief organ's private copular scan for `hdlab.attachment_arm.cop_subject_pairs` and
re-running `exp_belief_at_t_end_to_end_v1` end to end (modern n_items 13 / n_queries 33; real 6 / 7;
n_boot 2000). **57 of 231 flattened metrics moved.**

**What improved:**

| metric (modern unless noted) | before | after | delta |
|---|---|---|---|
| `extraction_quality.reality_event_recall` | 0.6071 | **0.7143** | +0.1071 |
| `extraction_quality.reality_event_recall` **(real prose)** | **0.0000** | **0.3333** | +0.3333 |
| `by_fact_type.status.BELIEF_live` | 0.7500 | **1.0000** | +0.25 |
| `by_channel.perception.BELIEF_live` | 0.6364 | 0.7273 | +0.0909 |
| `pop_acc.BELIEF_live` | 0.7576 | **0.8182** | +0.0606 |
| `knowledge_state.reader_acc` | 0.7576 | 0.8182 | +0.0606 |
| `false_belief.belief_acc_on_fb` | 0.8571 | 0.9286 | +0.0714 |
| `false_belief` CI half-width / lo | 0.2083 / 0.5833 | **0.1250 / 0.7500** | tighter AND higher |
| `gates.live_vs_oracle.delta` (the extraction gap) | 0.2424 | **0.1818** | **-0.0606** |
| `extraction_quality.belief_update_recall` | 0.7273 | 0.7727 | +0.0455 |

**🔻 AND WHAT THIS IS NOT, WHICH MATTERS MORE THAN THE ABOVE.** The headline `+0.0606` is **exactly
2 of 33 queries**, and the *same two* flipped for every arm that consumes the extracted reality chain:

| arm | before | after |
|---|---|---|
| `BELIEF_live` | 25/33 | 27/33 |
| `FLOOR_current` | 20/33 | 22/33 |
| `TWIN_shuffled` (info-free) | 16/33 | 18/33 |
| `FLOOR_lastment` (does **not** read the chain) | 23/33 | **23/33** |
| **`gates.vs_twin.delta`** | **9/33 (0.2727)** | **9/33 (0.2727)** |

**The margin over the info-free twin is UNCHANGED.** Two facts that previously had *zero* extracted
reality events now have one, so every chain-consuming arm answers them — including the shuffled twin. The
stateless last-mention floor, which does not read the chain, did not move at all. **That is the signature
of a COVERAGE gain, and it is not evidence that the belief DECISION got better.** The gates remain
un-separated: `vs_lastment.lo` -0.182 -> -0.1212 and `vs_strongest_floor.lo` -0.1875 -> -0.1212, both
still **negative**.

**The one thing that is a genuine quality signal** is `gates.live_vs_oracle.delta` 0.2424 -> 0.1818: the
oracle is pinned at 1.000, so a narrowing live-to-oracle gap is exactly what an extraction repair should
produce, and it cannot be explained by coverage alone.

**And a real cost, named:** `extraction_quality.belief_assertion_precision` **1.0000 -> 0.9474** — one
wrong assertion in 19. The organ fires more often and is not perfect when it does.

➡️ **Shipped as `belief_ud_copula_patch.diff`**, because it is a **deletion** — it removes a duplicate
copular scan in favour of the reader's own board-validated organ (one structure, one organ) — and because
extraction strictly improves on both slices. The precision cost and the flat twin margin are stated here
so the diff is not read as a discrimination win.

---

## E. THE `track_*` AUDIT — brief-ready

**23 dimensions are ON by default on every read. For the 10 whose situation-model field I could map,
8 are read by NO board row; only 2 are scored.**

| flag | field it produces | scored by a board row? |
|---|---|---|
| `bind_entity_states` | `entity_states`, `state_register` | ✅ `entity_states` |
| `resolve_commonnouns` | `commonnoun_resolution` | ✅ |
| `track_belief` | `believes`, `knows` | ❌ |
| `track_space` | `locations` | ❌ (pri 137 found the same) |
| `track_world_state` | `world_state` | ❌ |
| `track_goals` | `goals` | ❌ |
| `bind_event_tokens` | `event_tokens`, `episodic_store` | ❌ |
| `track_spatial_reasoning` | `spatial_still_at` | ❌ |
| `predict_surprisal` | `surprisal` | ❌ |
| `discover_pronouns` | `pronoun_abstentions` | ❌ |

🔻 **HONEST LIMIT OF THIS AUDIT:** the other **13** default-ON flags (`track_affect`,
`track_affected_entity`, `track_bridges`, `track_causal_reasoning`, `track_goal_thwart`,
`track_infer_emotion`, `track_natural_logic`, `track_prediction`, `track_predictive_causal`,
`track_senses`, `track_temporal_reasoning`, `track_tom_action`, `predict_revise`) have **no field mapping
in my table**, so their "no board row" is NOT CHECKED, not established. The brief's first job is to
complete that map from `situation_reader.py` itself.

**Read-time cost — MEASURED ONCE AND THE MEASUREMENT FAILED; re-measured.** The first pass (all-default
591.8s vs five-dimensions-off 633.9s over 6 documents) returned a cost of **-42.0s (-7.1%)**: switching
five dimensions OFF made the read *slower*. A negative cost is not a finding, it is ordering plus a noisy
neighbour (cold caches on pass 1; another solver's job on the same laptop). Re-measured paired and
alternating (ON,OFF,OFF,ON per document, min per arm) -- numbers below.

**What a row would need**, per dimension: a gold the reader can be scored against on MODERN prose, and a
read-out that consumes the field. `track_belief` has the gold (`belief_at_t_gold`, FANToM) and no row;
`track_space` has a register and no modern where-is gold (pri 137 says so explicitly). Those two are the
cheapest rows to add.

