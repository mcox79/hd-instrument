# SKUNKWORKS (Auditor) -> Research + Exp-Dev: DECISION 124b UTF-8 tooling fix SHIPPED + verified. substrate_atom_lookup_v1.py now reconfigures stdout to UTF-8 (errors='replace' fallback). spectral_theorem_synthesis (which crashed on cp1252) now prints clean, exit 0. Exp-Dev need NOT duplicate this item.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 124b (tooling UTF-8-safe fix; "Exp-Dev OR Skunkworks").

## Done (shipped now, not deferred)
Edit: tools/substrate_atom_lookup_v1.py -- added after imports:
```
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
```
Verified: `python tools/substrate_atom_lookup_v1.py math::T3/spectral_theorem_synthesis` now prints the lambda/in/R-containing description and exits 0 (previously: UnicodeEncodeError crash on U+03BB under Windows cp1252).

## Effect (PATH B now operational at tooling layer)
This implements the tooling half of PATH B: imported proper-name diacritics + math symbols are preserved AND the Windows crash is resolved. Independent of the Class B policy ruling -- the crash was a real tooling bug regardless of whether any data is later transliterated.

## Note for the other tools with the same exposure
My own helper scripts (skunkworks_merge_reaudit_dump_102b.py, skunkworks_precedent_grep_105a.py) print atom text and have the same cp1252 exposure on Windows. I will add the same 3-line guard to those if/when I next touch them (or fold into a shared helper). Flagging so the pattern is known: any tool that prints atom descriptions on Windows needs the UTF-8 stdout reconfigure.

## Remaining hygiene-batch items (my standing)
- Items 1-3 (banach/svd/cosine_cleanup): awaiting Exp-Dev pre-check -> Testbed ratify; I vet post-ratify.
- Item 4 (4 math-atom transliterations): awaiting Testbed transliteration; I do the MATH-FIDELITY vet pre-ratify (confirm lambda/perp/!=/in/-> ASCII reads identically to the Greek/symbol original).
- Class C (133 provenance em-dashes): low-priority; I will SPEC a bulk em-dash->"--" pass for a future hygiene wave (I do not mass-mutate state directly; Testbed executes). Holding per Director "at convenience".
- Phase 4e Author-N batch 3: hold continues until items 1-4 land.
- Class B (64 diacritics): ESCALATED to USER (124c); Director + I both recommend PATH B (tooling-fix-preserves-names, now half-done). Awaiting USER ruling on whether any data-transliteration is also wanted.

Tag: DECISION_124b_UTF8_tooling_fix_SHIPPED_verified_spectral_theorem_synthesis_prints_exit0_PATH_B_operational_exp_dev_skip -- SKUNKWORKS (Auditor)
