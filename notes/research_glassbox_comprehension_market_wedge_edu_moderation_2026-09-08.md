# Research: Glass-box non-generative comprehension substrate — market wedge in Education & Content Moderation

Date: 2026-09-08
Type: market/product research (NOT substrate-physics drill) — supports strategy brainstorm
Sub-agents: research:sonnet x5 (adoption+products / detection+grading / privacy+policy / moderation adoption / moderation regulation+failures)
Calibration: novel market-synthesis — confidence capped, kill-criteria pre-registered.

---

## HEADLINE

The single sharpest wedge for a deterministic, traceable, no-hallucination, fully-local comprehension-and-audit engine is **the EU DSA Article 17 "statement of reasons" / moderation-audit layer** — a HARD legal requirement (billions of individualized reasons filed to a public EU database; X already fined EUR 120M Dec 2025; Meta/TikTok preliminary transparency-breach findings Oct 2025; 18/19 platforms got negative first-cycle audit opinions) that the incumbent technology (LLMs) **structurally cannot satisfy** because LLM moderation is non-deterministic (same content -> different verdict), black-box (cannot reproduce the logic), and demonstrably inconsistent (Fasching & Lelkes, ACL 2025: 7 major systems disagree on identical content; boundary shifts by demographic group named). The requirement is explicitly about producing a *specific, defensible, reproducible reason* — which plays to our strengths and **away from our weakness** (we do not have to be the best detector of nasty informal prose; we have to be the auditable reason-giver). The second wedge is **on-prem education content/comprehension assessment**, riding a hard regulatory tailwind (FTC COPPA 2025 AI-training-consent rule; FERPA; the 62M-student PowerSchool breach) where "student data never leaves the district" is a compliance story LLM-API tutors cannot match. Both verticals share ONE shape: *a decision that affects a person, must be explained, and must survive appeal.* We should NOT chase generative tutoring, AI-writing detection (a doomed category we also do not solve), holistic essay grading, the raw social-media moderation firehose, or deepfake/image detection.

P_deflated (that a real, defensible commercial wedge exists in >=1 of these two verticals) = **0.45** (novel-synthesis cap 0.50; deflated for: our extraction-quality weakness sits exactly on top of the messiest moderation content; regulatory tailwinds can shift; incumbents are entrenched on the generative side).

---

## Cheap decisive test

Before any build, run a **2-week desk validation + one design-partner call per vertical**, costing near-zero:

1. **DSA SoR wedge (moderation):** Pull 200 real Statement-of-Reasons records from the live DSA Transparency Database Research API (available since Feb 2025). Manually classify: what fraction are (a) text-only decisions, (b) about content structured/formal enough that a deterministic extraction engine could produce the required "specific facts + specific policy clause violated + why" mapping, vs (c) short informal/coded/multimodal posts where our extraction weakness dominates. If >=30% of SoRs are text-based and structurally tractable, the wedge is real; if <10%, it is a mirage (the firehose is mostly (c)).
2. **Education wedge:** Get one district CTO or one state assessment office (e.g., a Texas-STAAR-adjacent contact) on a call. Ask exactly one question: "Would a fully-local, deterministic, span-traceable rubric-scorer that shows *why* it scored each response — and produces the same score on re-run for an appeal — be procurement-relevant vs your current cloud AI scorer?" A "yes, because appeals/FERPA/board-defensibility" confirms; a "we just need it cheap and good-enough" kills it.

Decisive because both probes attack the exact failure mode (extraction on messy prose / cost-vs-audit priority) that would sink the wedge, at zero build cost.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Moderation / DSA Article 17 wedge**
- HARD-PASS: >=30% of a random 200-SoR sample are text-based decisions on content structured enough for deterministic extraction to produce an Art.17-compliant reason; AND at least one VLOP/mid-platform T&S or compliance lead confirms in interview that reproducibility-of-reason (not just detection accuracy) is a live audit pain they would pay to close.
- HARD-FAIL: <10% of SoRs are text-tractable (i.e., the bulk is short informal/coded/multimodal), OR compliance leads say a boilerplate template + human sign-off already satisfies auditors cheaply, making a deterministic reason-engine redundant.

**Education / on-prem comprehension-assessment wedge**
- HARD-PASS: >=1 district/state procurement contact confirms data-locality (no external LLM API) is a *decision-changing* procurement criterion post-COPPA-2025/PowerSchool, AND a rubric exists (lab reports, short-answer reading comprehension, structured argument) where scoring is content/logic-based (not voice/creativity) and appeal-defensibility is valued.
- HARD-FAIL: procurement says "good-enough + cheap + fluent feedback" dominates and they are comfortable with vendor no-training contractual assurances (OpenAI Edu no-train-by-default + 16-state DPA already neutralizes the locality argument for most), OR the only assessment they want is holistic/creative essay grading (needs judgment we lack).

**Universal kill-criterion:** if in BOTH verticals the buyer's binding constraint turns out to be cost-per-item or fluent generation rather than auditability/determinism/locality, the entire thesis fails — our engine only wins where an auditable, reproducible, source-traceable REASON is legally or institutionally mandatory.

---

## VERTICAL 1 — EDUCATION

### (a) LLM adoption level + flagship use cases (named, dated)
- **Khanmigo (Khan Academy, GPT-4):** piloted Mar 14 2023; **Microsoft partnership May 21 2024** made Khanmigo for Teachers **free for all US K-12 teachers** (Azure OpenAI donated infra). Statewide deals: New Hampshire (first, June 2024), Arizona (2nd). Khanmigo-for-Districts still in pilot as of Oct 2025 (the "2M users / 795 districts" figure is UNVERIFIED, low-authority source). Khan platform ~189M registered users (self-reported).
- **Google Gemini for Education / LearnLM:** launched ISTE 2025 (June 2025), free in Google Workspace for Education; claims 1,000+ US higher-ed institutions; higher-ed student access from Dec 1 2025. All figures vendor-reported.
- **OpenAI ChatGPT Edu:** launched May 2024 (ASU first partner Jan 2024, Wharton, Oxford, UT Austin, Columbia). 2025 mega-deployments: **Cal State University 460,000 students + 63,000 staff** (largest ever); Indiana University 120,000. Bloomberg (Dec 2025): **700,000+ licenses sold to ~35 US universities**. **ChatGPT for Teachers launched Nov 19 2025** (free K-12 workspace, no training on data, free through ~2027). **AFT partnership (June 2025):** OpenAI+Microsoft+Anthropic fund National Academy for AI Instruction, USD 23M/5yr, targeting 400,000 educators.
- **Microsoft Copilot Education:** Washington State free statewide (295 districts); Broward County FL 20,000 staff licenses.
- **Other funded vendors:** MagicSchool AI (Series B USD 45M Feb 2025, ~USD 63M total, 6-8M educators); Grammarly (USD 1B financing May 2025, ~USD 13B 2021 valuation, 3,000+ higher-ed institutions, "Authorship" integrity feature); Amira Learning (AI reading tutor, 5M+ students, 4,000+ districts); Duolingo Max (GPT-4, ~1.8M paid subs Q1 2026; AI inference compressed gross margin ~170bps); Speak (USD 78M Series C Dec 2024, USD 1B valuation — consumer, not classroom).
- **Adoption stats (2024-2026):** RAND — teacher AI use **25% (2023-24) -> 53% (2024-25)**. EdWeek Research Center — **32% (early 2024) -> 61% (late 2025)**. Walton/Gallup — 60% of teachers used AI in 2024-25; weekly users save ~5.9 hrs/wk. Common Sense Media — 70% of teens use AI for schoolwork. Pew (Dec 2025) — 54% of teens used chatbots for schoolwork; 59% say AI cheating is "a regular feature of student life."
- **Efficacy evidence (real RCTs):** Harvard physics AI-tutor (Kestin et al., *Scientific Reports* June 2025): AI-tutored learning gains ~2x in-class active learning (p<1e-8). World Bank Nigeria (WP 11125, May 2025): +0.23 SD English, +0.31 SD combined, 6 weeks, GPT-4/Copilot.

### (b) Named pain points blocking deeper deployment
- **AI-writing detection is collapsing (the marquee pain, but NOT our problem — see wedge):** Turnitin admitted false-positive rate 1% -> ~4% sentence-level; worse on <20%-AI documents. **60+ institutions across 5 countries disabled/banned it** (Vanderbilt Aug 2023, Michigan State, Northwestern, UT Austin, Waterloo Sept 2025, San Francisco State). Yale/Vanderbilt/Johns Hopkins/Indiana ban detector output as sole evidence.
- **Lawsuits / false accusations:** Yale MBA student (filed Feb 2025, GPTZero-based, national-origin discrimination); Palo Alto HS (filed May 2026, Turnitin flagged 76% +/-15, male students flagged 4-5x more); Hingham MA (federal ruling Nov 2024). **Stanford/Liang 2023:** detectors misclassify **61.3% of non-native-English (TOEFL) essays** as AI vs near-zero for native writers.
- **Automated essay-grading debacle:** Texas TEA STAAR automated scoring engine (Dec 2023, ~75% of constructed responses, cut human scorers 6,000 -> <2,000, saved USD 15-20M/yr). Fall 2023 English II: **~80% of responses scored zero** (baseline <=5%); Dallas ISD ~half of students scored zero. TEA never published a human-vs-machine agreement rate. Academic bias findings (Wetzler et al. 2025: proportional bias, lenient on weak/strict on strong essays; self-preference for low-perplexity/AI-written text).
- **Trust erosion:** PDK/EdWeek 2025 — support for AI lesson-planning dropped 62% -> 49% in one year; ~70% of parents oppose AI access to student grades/data. CDT Oct 2025 — 70-75% of teachers worry AI undermines critical skills; ~half of parents unaware of school AI policy.
- **Privacy/governance regime (the tailwind for locality):** FTC **COPPA 2025 amendments** (finalized Jan 16 2025, effective June 23 2025, full compliance Apr 22 2026) — **NEW: disclosing a child's data to train AI requires separate verifiable parental consent**; mandatory written data-retention policy; biometric identifiers added. **FERPA** — consumer AI accounts (free ChatGPT) fail the "school official" exception (no contract/control/FERPA terms) => pasting student work is unauthorized disclosure. **PowerSchool breach** (Dec 2024, ~62M students / 9.5M teachers, ~18,000 districts, SSNs back to 1985 — largest children's-data breach in US history; TX AG suit Sept 2025). **State activity:** ~37 states + PR have AI-in-schools guidance; ~100+ 2026 state bills; Idaho SB 1227 (data-privacy requirements), CA AB 1159 (would bar training on student data unless it benefits the school, private right of action). EU: Italian Garante fined OpenAI EUR 15M (Dec 2024, incl. minors age-verification). Vendor counters: OpenAI Edu no-training-by-default + **16-state data-privacy agreement**; Anthropic Claude for Education exempt from Sept 2025 consumer training shift.

### (c) Wedge analysis — Education
**WHERE IT WEDGES:**
1. **On-prem, deterministic, span-traceable content/rubric assessment (formative + defensible summative).** Direct answer to the STAAR failure mode: a scorer that shows *why* (traceable to spans of the student's own text), gives the *same* score on re-run (survives an appeal/parent conference), and runs **fully local** (no student data to a cloud LLM — sidesteps COPPA-2025 AI-training consent, FERPA disclosure, PowerSchool-class exposure). Applies to content/logic-based rubrics: lab reports (hypothesis/method/result/conclusion + causal consistency), short-answer reading comprehension (does the answer's who-did-what-to-whom match the passage's situation model), structured argument (thesis stated? supported? coherent reference?). Auditability + determinism + locality are the three wins; fluent feedback generation is NOT required for a *score with evidence*.
2. **Reading-comprehension assessment / literacy screening** (Amira-sized market, 5M students): judging whether a student's answer demonstrates comprehension is itself a comprehension/extraction task — deterministic, explainable to teachers.
3. **Cross-cutting: data-locality as procurement differentiator** post-COPPA-2025/PowerSchool.

**WHERE IT CANNOT (be skeptical):**
- **AI-writing detection** — doomed category (field retreating; lawsuits) AND not our problem shape (detecting "AI-ness" is stylometric/statistical fingerprinting, not comprehension). Do NOT enter.
- **Open-ended tutoring / lesson-planning copilots** (Khanmigo, ChatGPT Edu, MagicSchool) — need fluent Socratic generation. We cannot generate. This is where the money and adoption are, and we lose outright.
- **Holistic/creative essay grading** (voice, persuasiveness, style) — needs judgment an extraction engine reads poorly.
- Note the locality argument is partially neutralized by OpenAI's 16-state DPA + no-train pledges; the wedge holds only for buyers who treat *no external API at all* + *reproducible-for-appeal* as binding (high-stakes assessment offices, privacy-maximalist districts).

---

## VERTICAL 2 — CONTENT MODERATION / TRUST & SAFETY / MISINFORMATION

### (a) LLM adoption level + flagship use cases (named, dated)
- **Meta:** **Jan 7 2025 ended US third-party fact-checking -> Community Notes** (US-only; kept fact-checkers in ~119 countries). Community Notes testing Mar 2025, public Oct 1 2025, ~250K contributors but **only ~6% of notes published**. **NPR (May 31 2025, internal docs): Meta plans to automate up to 90% of risk/integrity assessments** via AI "instant decision" (EU exempted for DSA). **Mar 19 2026: Meta cutting third-party moderation vendors in favor of in-house AI.** May 2026: ~8,000 jobs cut.
- **X:** Community Notes at scale (1.88M notes, 1.15M contributors Mar 2025; >90% never published). **AI Note Writer pilot (July 1 2025, Grok + third-party AI).** R Street study (Sept 2025-Mar 2026): AI-written notes "Currently Rated Helpful" 18.0% vs human 8.9% — AI notes ~2x more effective. PNAS (Sept 2025): notes cut reposts -46%.
- **YouTube:** automated-detection share ~95-97% (2024); 178.5M videos removed 2019-2024; ~34,000 channels removed for foreign-influence 2025.
- **TikTok:** automated detection 86.5-91.2% of removals (2025); **human-moderator layoffs** Malaysia Oct 2024 (~500-700), Singapore/UK 2025, second round July 2026; USD 2B T&S spend 2024 claim.
- **T&S / AI vendors:** OpenAI Moderation API (free; omni-moderation-latest GPT-4o multimodal Sept 2024). Hive AI (DoD deepfake contract USD 2.4M Dec 2024; customers Reddit/Truth Social/NBCU). Cinder (USD 41M Series B May 2026; customers OpenAI/Spotify/Midjourney). ActiveFence -> rebranded **Alice**, pivoted to AI-model security (USD 140M Aug 2026, ~USD 100M ARR). Checkstep (claims 98%+ automation). Reality Defender (deepfake, USD 33M Series A Oct 2024). Sensity, GetReal Labs (Hany Farid, USD 17.5M Mar 2025).
- **Fact-checkers:** Full Fact AI (40+ orgs, 30 countries, ~330K sentences/weekday); ClaimBuster; **Logically AI COLLAPSED July 2025** (pre-pack administration after losing Meta AND TikTok contracts — the canary for the platform-side fact-check retreat); Factiverse; EU EDMO (EUR 2.5M July 2025).
- **Independent reality check:** Zefr/ICCV 2025 (arXiv 2508.05527) — human reviewers **outperformed** multimodal LLMs (Gemini/GPT/Llama) on every brand-safety category across 1,500 videos.

### (b) Named pain points blocking deeper deployment
- **DSA Article 17 "Statement of Reasons" (the core):** every removal/demotion/restriction requires an individualized statement with (a) action + scope + duration, (b) specific facts relied on, (c) **whether automated means were used** (taxonomy: not/partially/fully automated), (d/e) the **specific legal provision or contract clause violated + why**, (f) redress path. Art. 24(5): **every SoR filed to the DSA Transparency Database** (widely-cited ~3.52B SoRs over 20 months; ITIF single-24h sample = 57.4M decisions, 97% automated detection, >50% fully-automated removals).
- **Enforcement is live and expensive:** **X fined EUR 120M (Dec 8 2025)** — first DSA non-compliance fine (appealed Feb 2026). **Meta + TikTok preliminary breach findings (Oct 24 2025)** on transparency/Art.40 researcher access + Meta notice-and-appeal; potential fines up to 6% of global turnover. First-cycle independent audits: **18 of 19 platforms got negative (adverse/qualified) opinions.** New Jan 2026 investigation into X's Grok-based recommender.
- **Appeals volume / error rates:** **165M+ moderation appeals since 2024, ~30% reversed (~50M reversals).** Meta's own Jan 2025 admission: **"1 to 2 out of every 10" enforcement actions may be mistakes** (10-20% self-reported false-positive rate). Appeals Centre Europe caseload grew 9x (Apr 2025-Mar 2026), finding platforms BOTH over- and under-removing. Study: 87.5-99.7% of deleted FB/YouTube comments in FR/DE/SE were legally permissible speech.
- **LLM-specific technical failures (the incumbent-tech gap):** Fasching & Lelkes (ACL 2025): 7 major moderation systems give **markedly different classifications on identical content**; boundary **shifts by demographic group named**. arXiv 2505.23914: advanced models show **stronger topic-stereotype bias despite lower overall FP rate**. "Policy-as-Prompt" (FAccT 2025): prompt-encoded policy is fast but **hard to audit/version**. "Arbiters of Ambivalence" (ACL 2025): LLMs **collapse to one fixed stance** on no-consensus topics — cannot represent human disagreement. Non-determinism: identical input -> variable output (sampling + GPU batch-order); "determinism dramatically improves auditability" (arXiv 2605.23955, finance analogy). **WHITE-SPACE: no source yet explicitly names the "LLM non-determinism vs Art.17 reproducible-reason" tension** — first-mover positioning.
- **Cost driver toward automation:** vendor-cited AI ~USD 0.008-0.015/item vs human ~USD 0.50-1.00/item (up to ~70% cost cut) — this is why platforms automate DESPITE the audit problems, and why our wedge must be the *legally-required-audit* slice, not the firehose.
- **Overlapping regimes:** DSA Art.17 + GDPR Art.22 (right to human intervention + explanation of logic) + EU AI Act Art.50 (disclosure, in force Aug 2 2026) — no unified standard; "black-box systems reach their limits when even the controller can barely explain the model logic."

### (c) Wedge analysis — Moderation
**WHERE IT WEDGES (strongest wedge in the whole report):**
1. **DSA Article 17 statement-of-reasons + moderation-audit layer.** The requirement is *by construction* our engine's spec: a **deterministic** (same content -> same reason on appeal/re-run), **source-traceable** (specific spans -> specific policy clause -> reason), **no-hallucination** (can only cite what is in the text/policy) reason for every action, filed to a public DB. LLMs structurally fail this (non-determinism, black-box, cross-model inconsistency proven in ACL 2025). We do NOT have to win at detection — we sit as the **auditable reason/explanation + reproducibility layer** on top of whatever flags content, turning an unexplainable LLM verdict into a defensible, reproducible, Art.17-compliant statement. Buyers: VLOP compliance teams facing 6%-turnover fines, Appeals Centre Europe-style dispute bodies, mid-size platforms that cannot afford a compliance-audit failure. The reproducibility angle is un-owned white-space.
2. **Misinformation claim-matching for fact-checkers** (Full Fact-sized): deciding whether a new statement asserts the same proposition as a previously-checked claim is a comprehension task — deterministic + auditable, and fact-check orgs value traceability as core to journalistic credibility. Caution: platform-side demand shrank (Meta exit; Logically collapse); EU/DSA keeps it alive.

**WHERE IT CANNOT (be skeptical — our weakness sits here):**
- **Detecting nuanced hate speech / harassment / sarcasm / coded language / novel slang in short informal posts** — this is precisely our stated extraction weakness (Oversight Board "Polish trans" case: automated systems failed on coded-language context). This is the BULK of moderation volume. LLMs/humans are better. Do NOT position as the detector.
- **The high-volume firehose** where cost-per-item ($0.008) and "good-enough" black-box already win and platforms are automating anyway (Meta 90%, TikTok 90%+). We compete ONLY on the EU/DSA-exposed, audit-required decisions, not the global stream.
- **Image / video / deepfake / synthetic-media detection** — not text, not our shape (Hive, Reality Defender, Sensity, GetReal, C2PA own it).
- **Hardest categories** (CSAM: only ~4% automated on Meta) need human review regardless.

---

## Cross-thread synthesis

Both verticals reduce to ONE buyable shape: **a decision that materially affects a person, is legally/institutionally required to be explained, and must survive an appeal.** Education grading due-process (Yale/Palo Alto/Hingham lawsuits; STAAR mistrust; parent conferences) and DSA Article 17 (individualized reason + reproducibility + redress) are the *same* requirement in two domains. In both, the incumbent (LLM) is fluent but non-deterministic, black-box, and hallucination-prone — the three properties that fail an audit. Our engine is the inverse on exactly those three axes (determinism, traceability, no-hallucination) plus a fourth (full data-locality) that is independently mandated by COPPA-2025/FERPA/GDPR. The engine loses wherever the value is fluent dialogue (tutoring), raw cheap throughput (the firehose), non-text (deepfakes), or messy-informal extraction (the nastiest short posts). Strategic read: **do not sell "comprehension" or "better AI"; sell "the auditable, reproducible, on-prem reason-layer for regulated decisions."** The detection can stay probabilistic/human; we own the *defensible-reason* seam.

Adjacency note (do not dismiss prematurely): the misinformation claim-matching seam and the education rubric-scoring seam are the same underlying operation (proposition-equivalence + situation-model matching), so a single core competency serves both — de-risking the build if either desk-test passes.

---

## Substrate-product implications

- **Lead product hypothesis:** a "Statement-of-Reasons / Decision-Audit engine" — input: (content span, policy/rubric) -> output: (deterministic verdict *with* a source-traceable, reproducible, human-readable justification + full inspection trail). Same core serves DSA moderation-audit and education assessment-with-evidence.
- **Positioning:** not "AI that understands text," but "the reproducible, on-prem reason-layer that makes an automated decision defensible under DSA Art.17 / FERPA / due-process appeal." Sell determinism + traceability + locality, not fluency.
- **Do-not-build list:** AI-content detection, generative tutoring, holistic essay grading, image/deepfake detection, the raw high-volume moderation firehose.
- **Biggest risk to de-risk first (cheap test above):** whether enough real regulated decisions are on *text structured enough* for our extraction to work — because our extraction-on-messy-prose weakness sits exactly on top of the highest-volume moderation content.
- **Timing tailwinds:** COPPA-2025 full-compliance deadline Apr 22 2026; DSA fines now live (X EUR 120M); EU AI Act Art.50 in force Aug 2 2026; the reproducible-reason white-space is currently un-named in the literature.

---

## Citations (verified count)

~90 sources gathered across 5 sub-agent scans; the load-bearing, reasonably-reputable ones (primary/regulator/peer-reviewed/major outlet):
- Moderation regulation: about.fb.com "More Speech Fewer Mistakes" (Jan 7 2025); EU digital-strategy.ec.europa.eu (Meta/TikTok preliminary findings Oct 24 2025; X EUR 120M fine Dec 8 2025); DSA Transparency Database docs + FAQ; ITIF Oct 2025 transparency report; Fasching & Lelkes ACL 2025 (aclanthology.org/2025.findings-acl.1144); arXiv 2502.18695 (Policy-as-Prompt, FAccT 2025); arXiv 2505.23820 (Arbiters of Ambivalence); NPR (Meta 90% automation, May 31 2025); R Street (AI Note Writer study).
- Education: RAND RRA134-25 & RRA4180-1; EdWeek Research Center 2026; Nature/Scientific Reports (Kestin Harvard physics, June 2025); World Bank WP 11125 (Nigeria, May 2025); Inside Higher Ed (Turnitin retreat, 60+ institutions); The Markup (Stanford/Liang non-native-speaker bias); Texas Tribune (STAAR automated scoring, Apr 2024); FTC COPPA final rule (ftc.gov + Federal Register 2025-05904); TechCrunch (PowerSchool breach); OpenAI enterprise-privacy + 16-state DPA.

VERIFIED (primary/regulator/peer-reviewed/major-outlet, high confidence): ~35.
FLAGGED UNVERIFIED / vendor-self-reported / secondary-only (do NOT quote as fact): Khanmigo "2M users/795 districts"; Meta "50% error reduction"; ~$9.87B/$1.38B Meta/TikTok fine estimates (press arithmetic, no finalized fine); UMass Amherst lawsuit (not found; conflated); WHO fact-check tool (does not exist); Hive 2024-25 funding round; all market-size figures; AI/human cost-per-item numbers (vendor blogs); the 3.52B cumulative SoR count (secondary-only).

---

## TLDR (plain language)
We looked at whether a tool that reads text and shows its work — never inventing anything, giving the exact same answer every time, and keeping all data on the customer's own computers — could sell into schools or into social-media content policing. The clearest opening is in Europe: the law now forces platforms to give every user a specific, appealable reason each time a post is removed, and file it in a public database — and the AI language models everyone uses can't do this reliably because they give different answers to the same post and can't explain themselves. Our kind of tool is built exactly for producing a fixed, traceable reason. The second opening is school grading and reading tests, where new child-privacy rules and a huge student-data breach make "nothing leaves the building" valuable, and where a score you can defend to a parent or in an appeal matters. We should NOT try to be a chat tutor, an "is-this-AI-written" detector, or a deepfake-image catcher — we lose those. Confidence is moderate (~45%): the biggest danger is that most real-world posts are messy slang our tool reads poorly. Two cheap phone-call tests would settle it before building anything.

## QUESTIONS
None — scope was well-defined; all requested areas covered with sourced findings.

## NEXT STEPS
1. Run the two cheap desk-tests above (200-SoR DSA sample classification; one procurement call per vertical) before any build.
2. If moderation desk-test passes, prototype the "Art.17 reproducible statement-of-reasons" layer against real SoR records as the lead wedge.
3. Read Fasching & Lelkes ACL 2025 in full — it is the strongest peer-reviewed evidence of LLM moderation inconsistency and the natural benchmark a deterministic engine would beat.
