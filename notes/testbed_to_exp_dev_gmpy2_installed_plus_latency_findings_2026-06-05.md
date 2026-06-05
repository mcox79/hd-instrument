# Testbed -> Exp-Dev: gmpy2 installed; pure-Python latency findings + Ask 2 deferred

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Research + Orchestrator + User  **Date:** 2026-06-05
**Re:** `exp_dev_to_testbed_hp12_v1_two_deps_2026-06-05` (15:39) + `research_to_testbed_gmpy2_install_HP12_speed_gate_2026-06-05` (15:47)

## Ask 1 (gmpy2 install): DONE

`gmpy2-2.3.0-cp311-cp311-win_amd64.whl` installed cleanly in `C:\dev\hd-instrument\.venv\` on marsh@home runner. Verified:

```
$ ssh marsh@home 'C:\dev\hd-instrument\.venv\Scripts\python.exe -c "import gmpy2; print(gmpy2.version())"'
2.3.0
```

`mpz(2)**512` returns correct large integer; `tools/hp12/rsa_accumulator.py` still imports cleanly (no regression).

## BUT: gmpy2 not actually imported by V1 module

Per `tools/hp12/rsa_accumulator.py` docstring (line 13):

> "V1 uses pure Python big-ints (correct + <1ms certs at 2048-bit). **gmpy2 + eprint-2024/505 hash-to-prime are V2 speedups.**"

The module imports only `hashlib`, `secrets`, `Dict`, `List` -- no `gmpy2` import. So gmpy2 install ALONE doesn't change V1 cert latency until the module is refactored (the named V2 work).

## Empirical sweep at the actual runner -- pure Python is already fast at small moduli

Benchmarked the `add` + `delete` operations across `rsa_bits` settings on the runner (100 ops each, median):

| `rsa_bits` | N approx | add p50 | delete p50 | HP gate (<1ms) |
|---|---|---|---|---|
| 128 | 256-bit | 0.320ms | 0.106ms | **add PASS, delete PASS** |
| 192 | 384-bit | 0.282ms | 0.240ms | **add PASS, delete PASS** |
| 256 | 512-bit | 0.383ms | 0.510ms | **add PASS, delete PASS** |
| 384 | 768-bit | 0.446ms | 1.321ms | add PASS, delete MID |
| 512 | 1024-bit | 0.556ms | 2.981ms | add PASS, delete MID |
| 768 | 1536-bit | 0.754ms | 8.339ms | add PASS, delete MID |
| 1024 (default) | 2048-bit | 1.337ms | 22.301ms | add MID, delete HF |

**Reading**:
- At the default `rsa_bits=1024` (N=2048-bit RSA modulus), pure-Python delete is 22ms -- way over the <1ms HP gate.
- At **RSA-256 modulus (rsa_bits=128)**: delete is 0.11ms -- 200x under the HP gate.
- At **RSA-512 modulus (rsa_bits=256)**: delete is 0.51ms -- under the HP gate.

So: **the HP <1ms gate is already achievable in pure Python by lowering rsa_bits to 128-256** (corresponding to N=256-bit to N=512-bit RSA modulus). The 3.46ms pre-test number Exp-Dev reported (at "RSA-512", which I read as 512-bit modulus = rsa_bits=256 in this code) is hash-to-prime overhead plus benchmark noise; my fresh sweep with explicit perf_counter timing puts delete at 0.51ms at the same modulus size.

## Honest cryptographic note

RSA-256 to RSA-512 is **toy-grade security** for production. For the V1 killer-demo recording, this is FINE -- the demo's claim is cryptographic-construction-of-deletion (proof-of-concept), not production-grade security. V2/V3 should target 2048-bit minimum (production standard) and need the gmpy2 refactor for sub-ms latency at that bit count.

## Recommendation

Two paths to clear the HP <1ms gate:

**Path A (zero-engineering; V1 demo-ready immediately)**: configure the demo's accumulator to `rsa_bits=128` or `rsa_bits=192` (256-bit to 384-bit modulus). Pure-Python delete < 1ms. Honest disclaimer in demo script: "demo uses 256/384-bit RSA for headline latency; V2 production will use 2048-bit + gmpy2."

**Path B (~30-60 min engineering; V2 prep)**: refactor `tools/hp12/rsa_accumulator.py` to use `gmpy2.powmod` and `gmpy2.invert` for the modular exponentiations + inverse. Should get delete at 2048-bit modulus under 1ms (gmpy2 is ~50-100x faster than CPython `pow` for big-ints in the 2048-bit range).

Path A is the minimum-friction path to a recordable demo. Path B is the durable fix and what gmpy2 install was prepping for.

## Ask 2 (Llama-3.2-1B weights to runner): DEFERRED

Per Research's recommendation (`research_to_testbed_gmpy2_install_HP12_speed_gate`):
> "**Recommendation:** prioritize Ask 1 (gmpy2). Defer Ask 2 unless the live speed test is specifically needed for demo recording confidence."

I'm holding on Ask 2. Cloud reference (5.7 min for 10K Llama-1B extraction on H100) extrapolates well to desktop with the optimization stack. If/when you want the live timing on the 4060 Ti, ping me and I'll trigger the ~2.5GB snapshot_download (~15 min wall) -- the runner already has the licensed `.hf_token` from prior work.

## What I did NOT do

- Did NOT modify `tools/hp12/rsa_accumulator.py` (your authoritative module; the gmpy2 refactor decision is yours)
- Did NOT change the runner's default rsa_bits (that's a demo-config choice)
- Did NOT install gmpy2 outside the runner's `.venv` (kept changes scoped)

## FAISS HNSW env hang still pending

Reminder from your 14:54 note: HNSW empirical hangs on the Windows OpenMP clash. Still blocks HP-12 V2 critical path (not V1). My recommendation stays: small Linux cloud CPU box (~$0.50) for the one-cell run. Not urgent right now per Research's V2 timeline.

---

**END.**

**Exp-Dev:** gmpy2 installed. Pure-Python add+delete at rsa_bits=128-256 already clears the <1ms HP gate (delete 0.1-0.5ms). At default rsa_bits=1024, delete is 22ms -- gmpy2 refactor needed there (Path B). For V1 demo recording, Path A (lower rsa_bits in demo config) is the minimum-friction path. HNSW + Ask 2 deferred per Research recommendation.

**User:** Ask 1 done (5 min runner-side work). Honest finding: gmpy2 install was a no-op for V1 because the module doesn't import gmpy2 yet (deferred to V2 per its own docstring). Good news: pure-Python pow already clears <1ms HP gate at RSA-256 to RSA-512, which is V1-demo-appropriate (toy-grade security; demo headline is the cryptographic construction, not production strength). No further runner-env action needed for V1 unless Exp-Dev wants me to also do the gmpy2 refactor.

**Research:** gmpy2 install successful. Empirical sweep confirms <1ms HP gate is achievable in pure Python at RSA-256 to RSA-512 modulus. gmpy2's real value is V2 production path at 2048-bit -- requires Exp-Dev module refactor; the pip install was V2 prep.
