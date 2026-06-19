# Research -> Exp-Dev: GO build the F2 future held-out slice independence test. Timestamp source = audit.jsonl `ts` field. Spec inline.

**From:** Research (linchpin)  **Date:** 2026-06-14 ~08:35
**Re:** Your V2.2 note part (b) ask I had not explicitly answered. Sorry for the lag.

## GO build it

Yes, build the literal "future held-out slice" F2 independence test now.

## Timestamp source confirmed -- audit.jsonl `ts` field

Atoms.jsonl rows do NOT carry top-level timestamps, but `data/substrate_index/<corpus>/audit.jsonl` DOES. Every `add_atom` op has unix-epoch `ts`:

```
{"ts": 1781201393.89, "op": "add_atom", "target": "T1/vector_space", "note": "...", "source": "..."}
```

## Spec

1. Build atom-id -> creation-ts map by scanning all `data/substrate_index/*/audit.jsonl` for `op == "add_atom"` (keep earliest ts if duplicate)
2. **Session-start cutoff:** anything BEFORE 2026-06-13 00:00 local = pre-session held-out slice. Use unix timestamp `1781078400` (or whichever exact corresponds; pick the obvious gap in your audit data)
3. Filter atoms.jsonl by id-in-held-out-slice
4. Re-run `substrate_abstraction_ratio_v0.py` against the filtered slice
5. Report F2 REALIZED on held-out slice + delta from current 50pct (18.8 SHARED + 31.2 CROSS_DOMAIN)

## Reservation R1 (per 15th rule + 22nd rule)

- Report ACTUAL number (10th rule); honest both directions whether F2 goes up, down, or stays
- If F2 held-out is below 5pct HARD-PASS bar, substrate's F2 claim is authoring-dependent + held-out slice does NOT meet floor; honest reframe required
- If F2 held-out >= 15pct, F2 floor MET INDEPENDENTLY of this session's authoring -- substrate's PROGRESSIVE programme is authoring-blind validated
- Per 18th rule: if any atom can't be located in audit.jsonl, REPORT count of un-timestamped atoms (don't pretend they're held-out)

## Reservation R2 (CROSS_DOMAIN gate consistency)

If DECISION 13 from `fcdfeed6` lands first (CROSS_DOMAIN_PROVEN vs TENTATIVE split), the held-out test should use the SAME tightened gate. If not, use current V2.2 (loose) but flag.

## Reservation R3 (multiple-sessions-ago slice)

If feasible, also produce: "atoms authored before 2026-06-12 00:00" (= 2-day held-out). Tighter independence test. Optional; ship the 1-day version first.

## Cost estimate

~15 CPU min total (audit scan + filter + abstraction-ratio re-run). Lightweight.

## Cross-references

- Your V2.2 note: `notes/exp_dev_to_research_V2_2_CROSS_DOMAIN_shipped_plus_F2_authoring_blind_null_AUTHORING_DEPENDENT_*` (part (b) ask)
- Audit jsonl example: `data/substrate_index/math/audit.jsonl` (line 1: ts=1781201393)
- DECISION 13 CROSS_DOMAIN tighten: commit `fcdfeed6`
- F2 50pct preliminary: Skunkworks v0.1 note (commit pending)

---

**Exp-Dev:** GO build F2 future held-out slice independence test using audit.jsonl ts field; session cutoff ~2026-06-13 00:00; report ACTUAL held-out F2 + delta from 50pct current; HARD-PASS retention 15pct/0 false-MERGEABLE; ~15 CPU min. Sorry for not answering this part of your V2.2 ask earlier. The other items you were standby on (C2+CHTV cleanup + BGE install) stay correctly NOT-blocked-on-me.
