# Milestone design: WIRE earned coref -> accumulate organ = the REAL situation model (2026-08-02)

## The milestone
Turn two independently-proven pieces into one working pipeline with NO oracle scaffolding for identity:
- EARNED coreference (match-or-allocate, our own; fair-test HARD_PASS commit 27e10d3a8; name F1 0.89) supplies WHO.
- The accumulate organ (hdlab/situation_model_accumulate.py, AccumulateRegister; atom 29609 accumulate=1.0 on ORACLE ids) tracks each entity's role trajectory across the discourse.

The scientific question: **the accumulate organ was validated on ORACLE entity ids. Does it still work fed EARNED coref cluster-ids (imperfect)?** = the honest end-to-end situation-model test on real McGuffey.

## Substrate
gold_multientity_dense_v1.jsonl (18 passages, 3.67 entities/passage, 66 entities, 37 role-varying).
Dense multi-entity co-presence makes coref non-trivial AND gives multi-role trajectories to track.
Role vocab (union across dense gold): agent, experiencer, theme, patient, recipient, possessor, addressee, goal, instrument (9). max_event_slots >= max clauses/passage (dense max 7; set 16 for headroom).

## The cell (dispatch AFTER step-1 possessive-fix lands, so best coref feeds the wiring)
For each passage:
1. build_mention_stream -> mentions with (gold_entity, clause, mention_text, role).
2. Run coref arm -> cluster-id per mention (in stream order).
3. AccumulateRegister(role_vocab, d, gen). For each mention: add_event(cluster_id, role, event_idx=clause_slot) where clause_slot = dense-ranked clause index within the passage (0..k).
4. Decode: for each mention event, decode(cluster_id, clause_slot) -> predicted role; score vs gold role.

## Arms (fair-test)
- ORACLE-coref (key = gold_entity): the CEILING, reproduces atom 29609 on this eval.
- EARNED-coref (key = predicted cluster-id from run_learnable): the REAL system.
- FLOOR(s): recency-floor coref keys (run_recency_floor) AND/OR every-mention-its-own-entity (no identity tracking). Earned must beat floor and retain a large fraction of the oracle ceiling.

## Metric
Fraction of mention-events whose role is correctly decoded from its assigned cluster's register (decode-argmax over role_vocab). Report overall + by coref-arm. VALUE-CEILING = earned/oracle. Also can cross-check against passage 'target_queries' (comprehension queries) as a secondary readout.
Why this penalizes coref errors correctly: a wrong MERGE piles two entities' bindings into one register -> cross-talk corrupts decode; a wrong SPLIT scatters an entity's events across clusters -> each decodes fine locally but the entity's trajectory is fragmented (caught if the query asks across the fragment). Decode-accuracy is the natural end-to-end penalty.

## Can-fail
- If EARNED-coref decode-accuracy ~= ORACLE ceiling: coref good enough to carry the situation model (milestone MET).
- If EARNED << ORACLE but >> floor: coref is the bottleneck (quantifies remaining coref headroom = the value of steps 1/2).
- If EARNED ~= floor: earned coref adds nothing at the situation-model level (would contradict the coref HARD_PASS -> investigate).

## Brain-faithfulness
Coref = identity tracking (DG/CA3 match-or-allocate + Centering salience, our own). Accumulate = Kintsch C-I / Zwaan multi-event indexing (FHRR bundle). No borrowed embeddings, no bolt-on reader. Roles are SUPPLIED gold here (the extraction organ is a separate, already-~0.60 layer); this cell isolates the identity+accumulate integration. A later cell can chain the real extraction in front (end-to-end from raw text).

## Sequencing
Step 1 (possessive-gender coref fix) in flight (hdi_exp_dev a86b7f30b). On land: dispatch this wiring cell using the possessive-fixed run_learnable. Then step 2 (pronoun coref) can be measured by its lift on THIS end-to-end metric, not just B3.
