# Research decisions log — 2026-07-06

- Mechanism-level self-verification scoping drill (substrate reasoning about its OWN mechanism/codebooks, not
  the cert_ledger): -> `notes/research_mechanism_selfverification_scoping_2026-07-06.md`. Honest verdict: 3 of
  4 named candidates collapse into 1 genuine question (SB-vs-modulus decode-margin, never swept); CRT-uniqueness
  and homomorphism-exactness are tautological (BLR-theory-grounded) and explicitly NOT recommended for a cell.
  One ready, non-parked, remote-dispatchable cell spec delivered: `exp_rns_subblock_margin_selfcheck_v1`.
