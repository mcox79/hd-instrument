# TIER-4a PULL-ON-DEMAND BACKLOG (cited-but-unconsumed foundationals)

**Owner:** Skunkworks (Auditor)  **Created:** 2026-06-16  **Status:** LIVING (append as new citations arise)
**Endorsed:** Testbed pre-receive + Director (DECISION 227/229) -- record as git-tracked, grep-searchable file.

## Model (why this file exists)
The consumer-pull discipline (Tier-4c assessment, Director-validated DECISION 227): atomize a foundational IFF a
primitive DEPENDS_ON it (the CRT precedent -- CRT was pulled when P1 needed it). The ~50-100 "cited foundationals"
are mostly CITED-SOMEWHERE with NO current consumer = floating facts; bulk-atomizing them is the source-push
anti-pattern (the 5510-Wikidata-84%-stale failure mode). So they live HERE -- git-preserved + grep-searchable --
and each is PULLED (authored as a Tier-4a foundation atom, CRT-pattern) when a primitive needs it as a real
DEPENDS_ON edge. This gives "substrate knows its foundations" ON-DEMAND, without graph bloat.

**To pull an entry:** when a primitive needs it, move it from this file to a Tier-4a atom (id below), author per
CRT-pattern (kind=primitive; tier T1/T2; corpus=math; canonical ref; substrate-internal; no LLM), wire the real
DEPENDS_ON edge, and delete the entry here. **To find a candidate:** `grep -i <topic> notes/tier_4a_pull_on_demand_backlog*.md`.

## Already PULLED (atomized; not in backlog -- for reference)
- chinese_remainder_theorem (T1; pulled for P1 residue_fpe_encoding; 8f96cb93)
- sparse_hopfield_hu_santos, kymn_residue_resonator_ols, simplex_correlation_bound (Tier-4a batch; pulled for P2)
- fractional_power_encoding, sinc_characteristic_function (Tier-4a clean-lineage batch; O_xunb DEFERRED -> backlog below)
- modern_hopfield_ramsauer (T2; pre-existing; P2 HEAD-2), resonator_network_decoder (T3; P2 HEAD-4)
- bocpd_changepoint, kullback_leibler_divergence, mp_bulk_kl (pre-existing; 190f drift lineage)

## BACKLOG (no current consumer; PULL-ON-DEMAND)
```
  id (candidate)                     | canonical ref                                  | consumer-slot IF needed
  -----------------------------------|------------------------------------------------|---------------------------------
  T2/krotov_hopfield_dam             | Krotov & Hopfield 2016 (dense associative mem) | alt dense cleanup head; energy capacity
  T1/demircigil_exp_capacity         | Demircigil et al. 2017 (exp storage capacity)  | capacity bound for cleanup heads
  T2/entmax_alpha_general            | Peters, Niculae, Martins 2019 (entmax family)  | HEAD-3 alpha-sweep generalization
  T2/plate_hrr                       | Plate 1995/2003 (Holographic Reduced Repr.)    | VSA binding lineage; real-valued binding
  T2/gayler_map                      | Gayler 2003 (Multiply-Add-Permute VSA)         | alternative binding op
  T2/frady_resonator_networks        | Frady, Kent, Olshausen, Sommer 2020 (Reson 1&2)| general factorization (vs residue-specific)
  T1/kanerva_hdc_foundations         | Kanerva 2009 (What is HDC / hyperdimensional)  | HDC foundational framing
  T2/steinert_threlkeld_quantifiers  | Steinert-Threlkeld (semantic automata/monotone)| generalized-quantifier capability
  T1/oeis_residue_sequences          | OEIS (totient / CRT-adjacent sequences)        | residue/combinatorics extensions
  T1/O_xunb_cosine_identity          | 85th audit candidate (unbind-cosine algebra)   | unbind==cosine equivalence (no math consumer yet; distinctness lesson is the AUDIT_LESSON in Tier-2)
```

## Exclusions (NOT math foundationals -> not pulled here)
Methodology/framing references (Newell 1990 unified theories; Lakatos research programmes; Toroghi "Less is More"
selectivity) are PROCESS/FRAMING knowledge, handled via Tier-2 methodology atomization, NOT Tier-4a math
foundationals. arXiv-prose bulk is REJECTED (11th-rule: would need LLM extraction; per Tier-4c assessment).

## Notes
- This is a STARTING list, not exhaustive; append candidates as future citations arise (cross-domain probes, new
  primitives). Each entry must remain FORMALIZABLE-as-theorem/identity (not vague prose) to be pull-eligible (the
  92nd-candidate phantom-dep discipline: a pulled atom must be a real, statable foundation, not a hand-wave).
- entmax_alpha_general is borderline: the alpha=2 sparsemax is ALREADY consumed (P2 HEAD-3 via sparse_hopfield_hu_
  santos); only the general-alpha family is backlog (pull if a future head sweeps alpha).
- frady_resonator_networks is borderline: the residue-specific Kymn-OLS variant is being atomized; pull the general
  resonator only if a non-residue factorization consumer emerges.
