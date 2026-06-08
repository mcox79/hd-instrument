"""
50 hand-crafted seed facts about AI companies for Tier 5 Sprint Panel A end-to-end testing.

This is the FIRST KB seed for the demo. Real Wikidata 100M + Wikipedia 5.84M ingest is
Week 1 Day 2-3. This 50-fact set lets us validate the full substrate-KV + Pythia query
path before tackling the bigger ingest.

Coverage: 6 AI labs (Anthropic, OpenAI, DeepMind, Mistral, Cohere, Stability) with
founding dates, founders, products, locations, and notable milestones. Picked to be
post-LLM-training-cutoff for several facts so substrate retrieval is non-trivial vs
bare LLM hallucination.
"""

SEED_FACTS = [
    # Anthropic
    "Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.",
    "Anthropic is headquartered in San Francisco.",
    "Claude is the AI assistant developed by Anthropic.",
    "Claude 4 was released by Anthropic in 2025.",
    "Claude Haiku 4.5 is the smallest model in the Claude 4.5 family.",
    "Claude Sonnet 4.6 is Anthropic's mid-tier production model.",
    "Claude Opus 4.7 is Anthropic's flagship model.",
    "Dario Amodei previously served as VP of Research at OpenAI before founding Anthropic.",

    # OpenAI
    "OpenAI was founded in December 2015 as a non-profit research organization.",
    "Sam Altman is the CEO of OpenAI.",
    "GPT-4 was released by OpenAI in March 2023.",
    "GPT-4o was released by OpenAI in May 2024.",
    "ChatGPT was released by OpenAI in November 2022.",
    "OpenAI is headquartered in San Francisco.",
    "Mira Murati served as interim CEO of OpenAI in November 2023.",
    "Greg Brockman is a co-founder and President of OpenAI.",

    # DeepMind / Google
    "DeepMind was founded in London in 2010 by Demis Hassabis, Shane Legg, and Mustafa Suleyman.",
    "DeepMind was acquired by Google in 2014.",
    "Google DeepMind was formed by merging Google Brain and DeepMind in April 2023.",
    "Demis Hassabis is the CEO of Google DeepMind.",
    "AlphaFold 2 was developed by DeepMind and predicted protein structures with near-experimental accuracy.",
    "Gemini is the AI model family developed by Google DeepMind.",

    # Mistral
    "Mistral AI was founded in 2023 in Paris, France.",
    "Mistral AI was founded by Arthur Mensch, Guillaume Lample, and Timothee Lacroix.",
    "Mistral released its first open-weight model in September 2023.",
    "Mixtral 8x7B was released by Mistral in December 2023 as an open-weight mixture-of-experts model.",

    # Cohere
    "Cohere was founded in 2019 by Aidan Gomez, Ivan Zhang, and Nick Frosst.",
    "Cohere is headquartered in Toronto, Canada.",
    "Aidan Gomez was a co-author of the original Attention Is All You Need paper.",

    # Stability AI
    "Stability AI was founded by Emad Mostaque in 2020.",
    "Stable Diffusion was released by Stability AI in August 2022.",
    "Stable Diffusion 3 was released in 2024.",

    # AI infrastructure
    "NVIDIA is the dominant GPU supplier for AI training workloads.",
    "Lambda Labs offers GPU cloud computing for AI research.",
    "Hugging Face is a platform for sharing open-source machine learning models.",

    # Notable papers
    "The Attention Is All You Need paper was published in 2017 by Vaswani et al at Google Brain.",
    "The original Transformer architecture replaced recurrence and convolution with self-attention.",
    "Hopfield Networks Is All You Need was published in 2020 by Ramsauer et al.",

    # Substrate / hyperdimensional computing
    "Hyperdimensional computing represents concepts as high-dimensional vectors.",
    "Fourier Holographic Reduced Representation uses complex phasor vectors for symbolic binding.",
    "K-hop graph traversal can be performed via FHRR unbind operations.",
    "Vector Symbolic Architectures provide algebraic operations over high-dimensional symbols.",

    # Misc 2024-2025 facts (post-cutoff for older LLMs)
    "The EU AI Act entered into force in August 2024.",
    "The EU AI Act Article 12 requires audit logs of AI system operations starting August 2026.",
    "GDPR Article 17 grants individuals the right to erasure of personal data.",
    "FB15K-237 is a standard benchmark dataset for knowledge graph completion.",
    "WebQSP is a benchmark for knowledge base question answering using Freebase.",
    "MuSiQue is a multi-hop question answering benchmark released by Allen AI.",
    "HotpotQA is a multi-hop question answering dataset over Wikipedia.",
    "Wikidata contains over 100 million structured facts about real-world entities.",
]


def load_seed_facts() -> list[str]:
    """Return the seed KB. Stable list; safe to call repeatedly."""
    return list(SEED_FACTS)
