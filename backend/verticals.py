"""
Vertical demo landing pages per Research PRIORITY_RANKING_2026-06-09 P1 A1.

Four pages each anchored on a cycle-200 vertical proof:
  /demo/legal       PP-208 PACER docket-entry retrieval 99.9%
  /demo/healthcare  PP-209 drug-drug interaction lookup 100%
  /demo/finance     PP-211 SEC 10-K extraction 100%
  /demo/fda         PP-210 FDA audit simulation 100%

Each page is a self-contained HTML response (no remote assets); shared CSS via
SHARED_HEAD; per-vertical hero + capability matrix + sample Q/A + CTA.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from fastapi.responses import HTMLResponse


@dataclass
class Vertical:
    slug: str
    headline: str
    tagline: str
    proof_pp: str
    proof_metric: str
    problem: str
    capability_claims: List[str]
    sample_questions: List[dict]
    regulatory_context: str
    accent_color: str  # CSS color used for accents


VERTICALS = {
    "legal": Vertical(
        slug="legal",
        headline="Substrate for federal court records",
        tagline="Citation-grounded answers about case law and PACER filings",
        proof_pp="PP-208",
        proof_metric="99.9% accuracy on 1M PACER docket entries",
        problem=(
            "Litigators and paralegals need verifiable, citation-grounded answers "
            "about case law and federal filings. Bare LLMs hallucinate court records, "
            "invent docket numbers, and misattribute rulings. The cost of a wrong "
            "citation in a federal brief is severe: sanctions, malpractice exposure, "
            "loss of credibility."
        ),
        capability_claims=[
            "PP-208: 99.9% accuracy on 1M PACER docket entries (cycle 200)",
            "Sub-ms retrieval latency at production scale (PP-150 0.21 ms P95 at 1M facts)",
            "PP-228 + PP-261: Cryptographic Merkle audit chain — per response AND per generation token (cycle 214; EU AI Act Article 12 per-token granularity 100%)",
            "PP-229: GDPR exact erasure 0/0 false retentions/losses; 0.058 ms wall (cycle 211; sealed records categorical)",
            "PP-269: PII detection recall=1.000 false-positive=0.000 (cycle 215; sub-ms privacy gate before disclosure)",
            "PP-230: Multi-tenant isolation T=50; cross-leak 0.001 (cycle 211; firm-isolation moat)",
            "PP-237: FB15K-237 2-hop traversal top-1 = 1.000 on n=600 (first public benchmark win; cycle 211)",
        ],
        sample_questions=[
            {
                "q": "When did Apple file its motion to dismiss in the EDTX patent case docketed 2:21-cv-00091?",
                "a": (
                    "Substrate returns the exact docket entry with date, judge, and document number. "
                    "Audit chain reproduces the source filing's hash. "
                    "Bare LLM (GPT-4o-mini) typically: invents a plausible-sounding date that does not match the actual record."
                ),
            },
            {
                "q": "What was the Supreme Court's ruling in Loper Bright v. Raimondo on Chevron deference?",
                "a": (
                    "Substrate returns the specific holding with case citation and date (June 28, 2024). "
                    "Audit chain ties the answer to the seeded fact's Merkle hash. "
                    "Bare LLM may answer correctly but cannot cite which specific source grounded the answer."
                ),
            },
        ],
        regulatory_context=(
            "Federal Rules of Civil Procedure 11(b) require attorneys to certify that "
            "factual contentions have evidentiary support. Substrate's Merkle-chained audit "
            "trail makes that certification mechanically verifiable for every cited fact."
        ),
        accent_color="#8b9eff",
    ),
    "healthcare": Vertical(
        slug="healthcare",
        headline="Substrate for clinical decision support",
        tagline="Definitive drug-drug interactions, contraindication lookups, dose ranges",
        proof_pp="PP-209",
        proof_metric="100% accuracy on 50K drug-drug interaction corpus",
        problem=(
            "Clinicians and pharmacists need definitive DDI lookups with citation to "
            "the underlying interaction table. Bare LLMs invent contraindications and "
            "misstate severity classifications. A missed or fabricated DDI directly "
            "harms patients. Healthcare requires both correctness AND auditability."
        ),
        capability_claims=[
            "PP-209: 100% accuracy on 50K-pair drug-drug interaction corpus (cycle 200)",
            "PP-186 + PP-269: HIPAA-compatible PII handling; substrate PII detection recall=1.000 / false-positive=0.000 at sub-ms (cycle 215 production privacy gate)",
            "PP-229: GDPR-grade erasure for retracted records; 0/0 false retentions or losses; 0.058 ms (cycle 211)",
            "PP-230: Multi-tenant T=50 isolation cross-leak 0.001 (cycle 211; HIPAA section 164.312 access control)",
            "Substrate-direct latency 0.21 ms P95: faster than EHR lookup",
            "PP-231: 5 of 6 substrate primitives composing without interference (audit + erasure + multi-hop + contradiction + negation)",
        ],
        sample_questions=[
            {
                "q": "Can a patient on warfarin safely take ibuprofen?",
                "a": (
                    "Substrate returns the specific interaction: significant DDI; NSAIDs increase warfarin's "
                    "anticoagulant effect via platelet inhibition and gastric mucosa damage; bleed risk multiplied. "
                    "Bare LLM often answers correctly but without citation, leaving the clinician to verify manually."
                ),
            },
            {
                "q": "What's the contraindication profile for paroxetine in pregnancy?",
                "a": (
                    "Substrate returns FDA category D with specific 1st-trimester cardiac defect risk magnitudes. "
                    "Audit chain links to the original drug label citation. "
                    "Bare LLM may hedge; substrate is decisive with cryptographic provenance."
                ),
            },
        ],
        regulatory_context=(
            "HIPAA Privacy Rule and FDA labeling requirements demand that decision-support "
            "tools cite their evidence. Substrate's per-response Merkle audit chain is "
            "directly inspectable by regulators."
        ),
        accent_color="#4ade80",
    ),
    "finance": Vertical(
        slug="finance",
        headline="Substrate for SEC 10-K filings",
        tagline="Verifiable extraction from financial filings",
        proof_pp="PP-211",
        proof_metric="100% accuracy on 10K-document SEC 10-K extraction",
        problem=(
            "Equity analysts and compliance officers need verifiable extraction from "
            "10-K filings. Bare LLMs misquote earnings, conflate fiscal years, and "
            "invent line items. A misstated revenue number in a research note triggers "
            "fiduciary liability and regulatory scrutiny."
        ),
        capability_claims=[
            "PP-211: 100% accuracy on 10K-document SEC 10-K corpus (cycle 200)",
            "PP-228 + PP-261: Merkle audit chain reproducible per response AND per generation token (cycle 214 EU AI Act Article 12 per-token)",
            "PP-119 + PP-237 + PP-258: Multi-hop aggregation; FB15K-237 2-hop top-1 = 1.000; K-hop ladder depth 3/5/10 all at recall=1.000 (cycle 214)",
            "PP-238: FB15K-237 2-hop ranking Hits@1 = 0.956 / MRR = 0.974 (head-to-head vs KGE; cycle 211)",
            "PP-229: GDPR-grade erasure for retracted filings; 0/0 false retentions/losses; 0.058 ms (cycle 211)",
            "PP-230: Multi-tenant T=50 isolation cross-leak 0.001 (cycle 211; SOC 2 CC6.1 firm separation)",
        ],
        sample_questions=[
            {
                "q": "What was Apple's total revenue in fiscal year 2023 from their 10-K?",
                "a": (
                    "Substrate returns the exact number ($383.29B) with citation to the 10-K filing. "
                    "Audit chain reproduces the source filing's hash. "
                    "Bare LLM may guess plausibly but cannot ground the answer to a specific filing."
                ),
            },
            {
                "q": "Across the FAANG companies' 2023 10-Ks, what total cloud-services revenue was reported?",
                "a": (
                    "Substrate multi-hop traverses each company's 10-K, sums cloud-segment revenue, "
                    "returns total with per-company breakdown and citations. "
                    "Bare LLM cannot reliably aggregate across documents without hallucinating values."
                ),
            },
        ],
        regulatory_context=(
            "SOX Section 404 and SEC Regulation FD require verifiable disclosure trails. "
            "Substrate's Merkle audit chain provides per-response cryptographic proof of "
            "what source data grounded each answer."
        ),
        accent_color="#fbbf24",
    ),
    "fda": Vertical(
        slug="fda",
        headline="Substrate for FDA regulatory audit",
        tagline="Reproducible answers for compliance and inspection",
        proof_pp="PP-210",
        proof_metric="100% accuracy on FDA audit simulation",
        problem=(
            "Pharma sponsors and CROs need substrate-grounded answers to FDA queries "
            "that are reproducible across audits. Bare LLMs cannot satisfy 21 CFR Part 11 "
            "audit-trail requirements (each response must be reproducible from documented "
            "sources). LLM stochasticity is a regulatory non-starter."
        ),
        capability_claims=[
            "PP-210: 100% accuracy on FDA audit simulation corpus (cycle 200)",
            "PP-228 + PP-261: Per-response AND per-token Merkle audit chain reproducible bit-exactly (cycle 214 EU AI Act Article 12)",
            "PP-229: GDPR + 21 CFR Part 11 erasure; 0/0 false retentions/losses; 0.058 ms (cycle 211)",
            "PP-231: 5 of 6 substrate primitives composing without interference (cycle 211; audit + erasure + multi-hop + contradiction + negation)",
            "21 CFR Part 11 compatible: data integrity + auditability + electronic signature alignment",
            "Substrate-direct mode bypasses LLM stochasticity for verbatim recall",
        ],
        sample_questions=[
            {
                "q": "What's the clinical trial protocol number for compound MK-1234's Phase III trial?",
                "a": (
                    "Substrate returns the exact protocol number with cross-reference to ClinicalTrials.gov ID. "
                    "Audit chain proves the answer came from the seeded source filing. "
                    "Bare LLM might fabricate a plausible-looking number with no verification."
                ),
            },
            {
                "q": "What adverse events were reported in the Phase III for drug X?",
                "a": (
                    "Substrate returns the exact AE listing from the trial filing with frequency counts. "
                    "Audit chain enables an FDA inspector to verify each AE matches the source record. "
                    "Bare LLM produces a probabilistic summary not tied to the specific filing."
                ),
            },
        ],
        regulatory_context=(
            "21 CFR Part 11 mandates that electronic records be trustworthy, reliable, "
            "and equivalent to paper records. Substrate's deterministic retrieval + Merkle "
            "audit chain directly satisfies this. LLM-only solutions cannot."
        ),
        accent_color="#f472b6",
    ),
}


SHARED_HEAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <style>
    * { box-sizing: border-box; }
    body {
      background: #0a0a0f;
      color: #e8e8ed;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 0;
      line-height: 1.55;
    }
    .wrap { max-width: 980px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }
    .breadcrumb { font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; }
    .breadcrumb a { color: #8b9eff; text-decoration: none; }
    .breadcrumb a:hover { text-decoration: underline; }
    h1 { font-size: 2rem; color: #fff; margin: 0 0 0.35rem; font-weight: 600; letter-spacing: -0.02em; }
    .tagline { font-size: 1.1rem; margin: 0 0 1.5rem; font-weight: 500; }
    h2 { font-size: 1.25rem; color: #fff; margin: 1.75rem 0 0.75rem; font-weight: 600; }

    .pill {
      display: inline-block;
      padding: 0.2rem 0.7rem;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 500;
      border: 1px solid;
      margin-right: 0.4rem;
    }

    .card {
      background: #11111a;
      border: 1px solid #232333;
      border-radius: 12px;
      padding: 1.1rem 1.25rem;
      margin-bottom: 1rem;
    }
    .card p { margin: 0; color: #d0d0d8; }

    .claim-list { list-style: none; padding: 0; margin: 0; }
    .claim-list li {
      padding: 0.55rem 0 0.55rem 1.5rem;
      position: relative;
      color: #c5c5d0;
      border-bottom: 1px solid #1c1c28;
    }
    .claim-list li:last-child { border-bottom: 0; }
    .claim-list li::before {
      content: "+";
      position: absolute;
      left: 0;
      font-weight: 700;
    }

    .qa {
      background: #11111a;
      border: 1px solid #232333;
      border-radius: 12px;
      padding: 1.1rem 1.25rem;
      margin-bottom: 1rem;
    }
    .qa .q {
      color: #fff;
      font-weight: 600;
      margin: 0 0 0.5rem;
      font-size: 1.02rem;
    }
    .qa .a {
      color: #c5c5d0;
      margin: 0;
      font-size: 0.95rem;
    }

    .compliance {
      background: #11111a;
      border-left: 4px solid var(--accent, #8b9eff);
      border-radius: 6px;
      padding: 1rem 1.1rem;
      margin: 0.5rem 0 1.5rem;
      color: #c5c5d0;
      font-size: 0.95rem;
    }

    .cta-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 1.5rem; }
    .cta {
      display: inline-block;
      padding: 0.65rem 1.1rem;
      border-radius: 8px;
      font-weight: 500;
      text-decoration: none;
      font-size: 0.95rem;
    }
    .cta.primary { background: var(--accent, #8b9eff); color: #0a0a0f; }
    .cta.secondary { background: transparent; color: #e8e8ed; border: 1px solid #444; }
    .cta:hover { opacity: 0.92; }

    .footer { color: #888; font-size: 0.85rem; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid #232333; }
    .footer a { color: #8b9eff; text-decoration: none; }
  </style>
</head>
"""


def _render(v: Vertical) -> str:
    proof_pill = (
        f'<span class="pill" style="color:{v.accent_color};border-color:{v.accent_color}">'
        f"{v.proof_pp} {v.proof_metric}</span>"
    )

    claims_html = "".join(f"<li>{c}</li>" for c in v.capability_claims)

    qa_html = "".join(
        f'<div class="qa"><p class="q">{qa["q"]}</p><p class="a">{qa["a"]}</p></div>'
        for qa in v.sample_questions
    )

    pretty_slug = "FDA" if v.slug == "fda" else v.slug.title()
    head = SHARED_HEAD.replace(
        "{title}", f"Substrate for {pretty_slug} - v1 Demo"
    ).replace(
        "{description}", v.tagline
    )

    body = f"""
<body style="--accent: {v.accent_color}">
  <div class="wrap">
    <div class="breadcrumb"><a href="/">v1 demo</a> / verticals / {v.slug}</div>
    <h1>{v.headline}</h1>
    <p class="tagline" style="color: {v.accent_color}">{v.tagline}</p>
    <div>{proof_pill}</div>

    <h2>The problem</h2>
    <div class="card"><p>{v.problem}</p></div>

    <h2>What substrate provides</h2>
    <ul class="claim-list">{claims_html}</ul>

    <h2>Sample queries</h2>
    {qa_html}

    <h2>Regulatory alignment</h2>
    <div class="compliance">{v.regulatory_context}</div>

    <div class="cta-row">
      <a class="cta primary" href="/chat">Try in /chat</a>
      <a class="cta secondary" href="/demo">See decisive test</a>
      <a class="cta secondary" href="/">Back to overview</a>
    </div>

    <div class="footer">
      Substrate v1 demo / observable hyperdimensional computing /
      <a href="/api">API</a> /
      <a href="/benchmark">Benchmark</a>
    </div>
  </div>
</body>
</html>
"""
    return head + body


def vertical_response(slug: str) -> HTMLResponse:
    v = VERTICALS.get(slug)
    if v is None:
        return HTMLResponse(content=f"<h1>404</h1><p>No vertical {slug}</p>", status_code=404)
    return HTMLResponse(content=_render(v))
