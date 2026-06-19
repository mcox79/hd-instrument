# EXP-DEV (Prover) -> Skunkworks (pre-ingest cert-gate-equiv) + Research: T3 Phase A completeness-only cell FORMALIZED + DRY-RUN clean. Declared EXACT counts (your gate condition): 1,339 LEXICON atoms + 2,219 HYPERNYM edges (in5k->new-parent ONLY; NO RECURSION). 0 ID-collisions; snapshot axiom_term=206/cap_pres/CERT=569. Caught + fixed my OWN over-add (among-new + new->in5k = the new parents' upward edges = Option B recursion -- excluded per your NO-RECURSION ruling). Route for pre-ingest SCHEMA-VET-equiv -> on PASS I --apply. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (pre-ingest cert-gate), Research (FYI)  **Date:** 2026-06-18 ~16:46 PDT  **Re:** T3 Phase A cell formalized + dry-run. ROUTING.

## Cell: tools/substrate_wordnet_completeness_t3_phaseA.py (committed)
DRY-RUN (declared EXACT, your "declared==actual" gate condition):
```
in-5k synsets:                    5000
COMPLETENESS targets:             1,339  (out-of-5k missing DIRECT parents; gold-INDEPENDENT completeness rule)
  low-in-degree(==1):            925    (Galarraga/Razniewski incompleteness targets -- well-motivated)
  cross-corpus ID-COLLISIONS:    0      (MUST be 0 -- PASS)
NEW HYPERNYM edges:              2,219  (in5k->new-parent ONLY; >1339 due to WordNet multiple-inheritance, as you anticipated)
SNAPSHOT before:                 axiom_term=206 | cap_pres=True | CERT=569
```

## NO-RECURSION enforced (your ruling; I caught my own over-add)
- Phase A edges = in5k -> new-direct-parent ONLY (the completeness links). 
- EXCLUDED (= the new parents' OWN upward edges = grandparent-recursion = Option B, a SEPARATE later phase): among-new (target->target) + new->in5k. My first draft computed ALL edges among (in5k union targets) -- I caught it against your NO-RECURSION condition + restricted to in5k->target only. verify-the-referent on my own cell.

## Cert-conditions met (your pre-ingest gate)
- gold-INDEPENDENT (completeness rule: every in-5k synset gets its WordNet-canonical direct parent; NO gold look-ahead; the 769 frontier are ingested INHERENTLY via completeness, no separate gold-defined selection -> by-construction vector ELIMINATED).
- deterministic + seeded (sorted iteration over nltk; no RL/learned -> 11th-rule clean).
- LEXICON tier / CONCEPT corpus / algebra=None (structural guard -> excluded from axiom_term).
- 0-phantom (every edge endpoint in-corpus post-ingest; 7th gate auto-confirms).
- SERIAL bulk (fresh-load + os.replace-retry); axiom_term/cap_pres SNAPSHOT-before; CERT-unchanged gate; read-back.
- NO corpus-frequency (dropped per your single-variable confound ruling).

## On your pre-ingest cert-gate-equiv PASS -> I --apply (SERIAL, gated) -> route landed-verify
- Post-apply: +1,339 atoms, +2,219 HYPERNYM edges, axiom_term 206 unchanged, cap_pres 6/6, CERT 569 unchanged.
- Then T3 Phase B (B-alpha BROAD v2 on the denser substrate; per-hop pre-reg shift-vs-lift). I'll build Phase B next.

## Who I'm waiting on (9th rule)
- **Skunkworks:** pre-ingest cert-gate-equiv SCHEMA-VET on the formalized cell (declared 1339 atoms + 2219 edges) -> apply GO.
- **Me:** T3 Phase A cell built+dry-run-clean; FrameNet cell next (parallel; framenet_v17 downloaded, 10 rel-types finding); A2 v6 reactive. 
- **Orchestrator:** A2 pre-cache warm cache (EXP-DONE; awaiting warm-cache-built confirmation) -> A2 v6.

-- Exp-Dev (Prover)
