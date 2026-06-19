# Exp-Dev -> Research: staging result + a data gap (NQ/TriviaQA staged are NOCONTEXT) + composition-regime-A HF

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** data_staging_v1_demo_priorities

## Staging result
- trivia_qa (rc.nocontext): STAGED
- nq_open: STAGED
- hotpot_qa fullwiki: STAGED
- longmemeval: FAILED -- 'xiaowu0162/longmemeval' not found on HF. Need the correct repo id (LongMemEval's HF path; the
  original is on GitHub/Google-Drive, may not have an HF mirror). Please point me at the right id or a direct URL.

## Data gap (important for the 3-baseline plan)
nq_open and trivia_qa-nocontext are **closed-book Q/A only -- they have NO passage corpus**. So they support the BARE-Qwen
arm but NOT the vanilla-RAG or substrate arms (nothing to retrieve from). The 3-baseline head-to-head needs PASSAGES. Options:
1. Use hotpot_fullwiki (HAS full-Wikipedia paragraphs) for a harder multi-hop 3-baseline -- buildable now.
2. Stage a Wikipedia passage corpus (or the CELL-2 v3 5.84M-article cache you referenced) so NQ/TriviaQA can do RAG.
3. trivia_qa has an "rc" (reading-comprehension WITH context) config -- I staged "rc.nocontext"; I can re-stage "rc" (with
   evidence docs) so TriviaQA supports RAG. Want me to?
Recommend: I build the **hotpot_fullwiki 3-baseline** now (harder than the distractor version already passed) + re-stage
trivia_qa "rc" (with context) for a TriviaQA RAG cell. NQ needs a Wikipedia corpus (CELL-2 cache) -- your call.

## composition-regime-A: HARD_FAIL (honest)
brute@K10=0.553, brute@K50=0.587, substrate-filtered@K50=0.438 (n=30). Brute context does NOT degrade at K=50 (Qwen-1.5B
handles 50 sentences fine) and filtering to 2 facts LOSES information. No "filtering beats brute under context pressure"
regime at this scale. Consistent with cycle-161 (substrate selection <= brute context); the substrate's value is the moat
features, not context-filtering for answer F1. (Regime exists in theory only above the context-window crossover, which
Qwen-1.5B's 32k window doesn't hit at K=50.)
