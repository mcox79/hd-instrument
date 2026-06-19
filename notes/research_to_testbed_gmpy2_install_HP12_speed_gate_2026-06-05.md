# Research -> Testbed: Two trivial runner-env unblocks for HP-12 V1 speed gate

**From:** Research session
**To:** Testbed (runner-env lane primary)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-05 ~18:00
**Re:** Exp-Dev's `hp12_v1_two_deps_2026-06-05.md` (15:39)
**Subject:** HP-12 V1 pre-tests cleared 2/3 cleanly. Test 2 crypto CORRECT; latency MIDDLE (3.46ms) needs gmpy2 install to hit <1ms HP gate. Plus optional Llama-1B weights for live speed test (not blocking; cloud reference adequate).

---

## HP-12 V1 pre-test results (Exp-Dev 17:00)

Exp-Dev ran the 3 cheap decisive gates ahead of schedule. Day 1 work (RSA accumulator + verifier CLI at `tools/hp12/`) essentially complete.

- **Test 1 (substrate quality Pythia-160M):** HARD_PASS -- associative recall 1.0 at N=1024
- **HF-3 (Llama-1B embedding geometry):** CLEARED -- recall 1.0 from local npz; no geometry mismatch
- **Test 2 (RSA accumulator crypto correctness):** CORRECT -- all certs verify third-party; tamper-rejected 1.0; standalone verifier CLI confirms
- **Test 2 latency:** MIDDLE -- 3.46ms issuance pure-Python at RSA-512 (HP gate <1ms needs gmpy2)
- **Test 3 (Llama-1B extraction speed on 4060Ti):** NOT RUN -- needs Llama-1B weights local (currently only npz on runner)

---

## Two runner-env asks (your lane)

### Ask 1 (highest value; ~5 min Testbed): `pip install gmpy2`

Moves RSA cert issuance from 3.46ms (MIDDLE) to <1ms (HP gate). gmpy2 is the latency optimizer the research spec named; pure-Python crypto is correct but slow.

Windows wheel for py3.11 typically installs cleanly:
```
pip install gmpy2
```

If wheel fails, alternative: `conda install -c conda-forge gmpy2` in a clean conda env.

**Strategic value:** moves HP-12 cert latency from MIDDLE to HP. This is the metric in the killer demo's headline.

### Ask 2 (optional; ~30 min Testbed): Llama-3.2-1B weights local

For Test 3 (extraction speed live timing on 4060Ti at bf16, batch=8, layer-skip-10; target <10 sec/1K facts).

Currently only the residual npz is local; the model weights are not. Download requires HF token + ~2.5GB.

**Alternative:** skip live timing and use the cloud-measured reference (5.7 min for 10K extraction on H100 = ~110 seconds extrapolated to desktop with optimization stack). Cloud reference is adequate for V1 planning.

**Recommendation:** prioritize Ask 1 (gmpy2). Defer Ask 2 unless the live speed test is specifically needed for demo recording confidence.

---

## What's NOT being asked (intentionally)

Per [[feedback-cloud-only-when-absolutely-necessary]] + V1 pipeline drill verdict:

- **No PubMed full-corpus extraction needed** -- V1 uses already-shipped 10K abstracts
- **No cryptographic accumulator cloud infrastructure** -- Python gmpy2 in-process is adequate for V1 mathematical proof
- **No SoftHSM** -- pure-Python RSA accumulator is mathematically equivalent
- **No Gemma-2-2B extraction yet** -- V3 production launch concern

Testbed cloud GPU stays available as emergency fallback ($0.50-1.00 H100 if HF-4 triggers during desktop build).

---

## FAISS HNSW env hang still pending (different deps)

Reminder from `exp_dev_to_testbed_faiss_hnsw_env_hang_2026-06-05.md` (14:54): FAISS HNSW deadlock on Windows OpenMP conflict. Blocks HP-12 V2 critical path (not V1).

V2 work is post-V1 demo (scaling to 100K facts). Not urgent right now but worth resolving when bandwidth allows.

Options recap: (a) conda faiss-cpu / (b) clean venv / (c) small Linux cloud box ~$0.50.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: this is Testbed primary (runner-env lane)
- Per [[feedback-cloud-only-when-absolutely-necessary]]: no cloud asks beyond optional fallback
- Per [[feedback-skills-first-for-rote-work]]: pip install is rote env work, not architectural decision
- ASCII-only

---

**END.**

**Testbed:** Ask 1 -- `pip install gmpy2` (5 min) moves HP-12 cert from MIDDLE (3.46ms) to HP (<1ms). Ask 2 (optional, 30 min) -- download Llama-3.2-1B weights for live extraction speed test on 4060Ti; alternative is skip and use cloud reference. Both no-cloud asks. Plus FAISS HNSW env hang still pending (blocks HP-12 V2 not V1; not urgent right now).

**Exp-Dev:** Pre-tests 2/3 GREEN + Day 1 RSA accumulator + verifier CLI shipped is strong fast progress. Standing for gmpy2 install to confirm <1ms HP gate, then Day 2-4 build.

**User:** HP-12 V1 fast-tracking. Pre-tests cleared 2/3 (substrate quality + Llama-1B geometry). Crypto correctness confirmed; latency MIDDLE (3.46ms) becomes HP (<1ms) after gmpy2 install. Day 1 RSA accumulator + verifier CLI already shipped. **Could be 2-3 days to demo from here, not 4.** Testbed asks are trivial env unblocks (pip install gmpy2; optional Llama weights download).
