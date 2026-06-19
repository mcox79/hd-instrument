"""
Seed facts for Tier 5 Sprint Panel A.

200+ hand-crafted facts spanning AI companies, science, medicine, history, geography,
regulations, and substrate-internal vocabulary. Used for end-to-end testing of the
substrate-KV pipeline before the real Wikipedia 5.84M + Wikidata 100M ingest.

Coverage chosen so the demo can answer queries across domains and demonstrate:
  - factual accuracy with citations (when fact in KB)
  - honest abstention (when fact absent)
  - post-cutoff knowledge (substrate has 2024-2026 facts; LLMs don't)
  - compositional / multi-hop queries (chained relations)
  - algebraic operations (AND / NOT / COUNT against shared properties)
"""

SEED_FACTS = [
    # ============================================================
    # AI labs - Anthropic
    # ============================================================
    "Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.",
    "Anthropic is headquartered in San Francisco, California.",
    "Claude is the AI assistant developed by Anthropic.",
    "Claude 4 was released by Anthropic in 2025.",
    "Claude Haiku 4.5 is the smallest model in the Claude 4.5 family.",
    "Claude Sonnet 4.6 is Anthropic's mid-tier production model.",
    "Claude Opus 4.7 is Anthropic's flagship model.",
    "Dario Amodei previously served as VP of Research at OpenAI before founding Anthropic.",
    "Anthropic raised over 7 billion dollars in funding between 2023 and 2024.",
    "Anthropic's Constitutional AI is a training method aligning models to a declared set of principles.",
    "Anthropic published the Responsible Scaling Policy in September 2023.",
    "Claude has a 200K token context window in production tiers.",

    # ============================================================
    # AI labs - OpenAI
    # ============================================================
    "OpenAI was founded in December 2015 as a non-profit research organization.",
    "Sam Altman is the CEO of OpenAI.",
    "GPT-4 was released by OpenAI in March 2023.",
    "GPT-4o was released by OpenAI in May 2024.",
    "ChatGPT was released by OpenAI in November 2022.",
    "OpenAI is headquartered in San Francisco.",
    "Mira Murati served as interim CEO of OpenAI in November 2023.",
    "Greg Brockman is a co-founder and President of OpenAI.",
    "Ilya Sutskever co-founded OpenAI and served as Chief Scientist until 2024.",
    "Ilya Sutskever co-founded Safe Superintelligence Inc in June 2024.",
    "OpenAI transitioned to a capped-profit structure in 2019.",
    "gpt-4o-mini is OpenAI's cost-efficient model variant released in 2024.",

    # ============================================================
    # AI labs - DeepMind / Google
    # ============================================================
    "DeepMind was founded in London in 2010 by Demis Hassabis, Shane Legg, and Mustafa Suleyman.",
    "DeepMind was acquired by Google in 2014.",
    "Google DeepMind was formed by merging Google Brain and DeepMind in April 2023.",
    "Demis Hassabis is the CEO of Google DeepMind.",
    "AlphaFold 2 was developed by DeepMind and predicted protein structures with near-experimental accuracy.",
    "Gemini is the AI model family developed by Google DeepMind.",
    "Gemini 1.5 supports a 1 million token context window.",
    "Gemini 2.5 Pro was released by Google in March 2025.",
    "AlphaGo defeated Lee Sedol in Go in March 2016.",
    "AlphaGo Zero learned to play Go from scratch in 2017.",

    # ============================================================
    # AI labs - Mistral, Cohere, Stability, smaller
    # ============================================================
    "Mistral AI was founded in 2023 in Paris, France.",
    "Mistral AI was founded by Arthur Mensch, Guillaume Lample, and Timothee Lacroix.",
    "Mistral released its first open-weight model in September 2023.",
    "Mixtral 8x7B was released by Mistral in December 2023 as an open-weight mixture-of-experts model.",
    "Mistral Large was released in February 2024.",
    "Cohere was founded in 2019 by Aidan Gomez, Ivan Zhang, and Nick Frosst.",
    "Cohere is headquartered in Toronto, Canada.",
    "Aidan Gomez was a co-author of the original Attention Is All You Need paper.",
    "Stability AI was founded by Emad Mostaque in 2020.",
    "Stable Diffusion was released by Stability AI in August 2022.",
    "Stable Diffusion 3 was released in 2024.",
    "Emad Mostaque resigned as CEO of Stability AI in March 2024.",
    "xAI was founded by Elon Musk in 2023 and develops the Grok AI assistant.",
    "Grok 3 was released by xAI in February 2025.",
    "Inflection AI was founded by Mustafa Suleyman in 2022.",
    "Mustafa Suleyman left Inflection in March 2024 to head Microsoft AI.",
    "Hugging Face was founded by Clement Delangue, Julien Chaumond, and Thomas Wolf in 2016.",
    "Hugging Face is a platform for sharing open-source machine learning models.",

    # ============================================================
    # AI infrastructure + tooling
    # ============================================================
    "NVIDIA is the dominant GPU supplier for AI training workloads.",
    "NVIDIA H100 is the data-center accelerator launched in 2022 for AI workloads.",
    "NVIDIA GH200 Grace Hopper combines a Grace CPU with an H100 GPU on a single board.",
    "Lambda Labs offers GPU cloud computing for AI research.",
    "Modal is a serverless infrastructure platform optimized for ML workloads.",
    "RunPod offers on-demand and serverless GPU compute for AI workloads.",
    "Together AI offers fast inference for open-source language models.",
    "PyTorch is an open-source deep learning framework developed primarily at Meta.",
    "TensorFlow is an open-source deep learning framework developed by Google Brain.",
    "vLLM is a high-throughput LLM inference engine developed at UC Berkeley.",
    "Llama-CPP enables CPU inference of Llama-family models.",

    # ============================================================
    # Notable AI papers and concepts
    # ============================================================
    "The Attention Is All You Need paper was published in 2017 by Vaswani et al at Google Brain.",
    "The original Transformer architecture replaced recurrence and convolution with self-attention.",
    "Hopfield Networks Is All You Need was published in 2020 by Ramsauer et al.",
    "Memorizing Transformer was published by Wu et al at Google in 2022 and stored keys for kNN attention.",
    "RETRO was published by DeepMind in 2021 and augmented language models with retrieval from a 2 trillion token database.",
    "Flamingo was published by DeepMind in 2022 and used gated cross-attention to inject visual features into a frozen LLM.",
    "KBLaM was published at ICLR 2024 by Brody and Reichart and injected knowledge base facts into transformer attention.",
    "Knowledge Capsules was published in April 2026 as a related approach to injecting structured knowledge into LLMs.",
    "Atlas was published by Izacard et al at Meta in 2022 and trained a retrieval-augmented language model end-to-end.",
    "REALM was published by Guu et al at Google in 2020 and pretrained a language model with retrieval.",
    "kNN-LM was published by Khandelwal et al at Stanford in 2019 and interpolated a base LM with a nearest-neighbor lookup.",

    # ============================================================
    # Substrate / VSA / HD computing
    # ============================================================
    "Hyperdimensional computing represents concepts as high-dimensional vectors.",
    "Fourier Holographic Reduced Representation uses complex phasor vectors for symbolic binding.",
    "Binary Spatter Codes use bipolar +1/-1 vectors for symbolic binding via elementwise multiplication.",
    "K-hop graph traversal can be performed via FHRR unbind operations.",
    "Vector Symbolic Architectures provide algebraic operations over high-dimensional symbols.",
    "Pentti Kanerva developed Sparse Distributed Memory in 1988.",
    "Tony Plate developed Holographic Reduced Representations as his 1994 PhD thesis at Toronto.",
    "Datalog is a declarative logic programming language used in deductive databases.",
    "Datalog with negation as failure is known as Datalog with negation or Datalog^neg.",

    # ============================================================
    # Regulations and standards
    # ============================================================
    "The EU AI Act entered into force in August 2024.",
    "The EU AI Act Article 12 requires audit logs of AI system operations starting August 2026.",
    "The EU AI Act categorizes AI systems into prohibited, high-risk, limited risk, and minimal risk.",
    "GDPR Article 17 grants individuals the right to erasure of personal data.",
    "GDPR entered into force in May 2018.",
    "NIST AI Risk Management Framework version 1.0 was published in January 2023.",
    "California Senate Bill 1047 was vetoed in September 2024.",
    "ISO 42001 is the international standard for AI management systems published in December 2023.",
    "The Bletchley Declaration on AI safety was signed by 28 countries in November 2023.",
    "The Seoul AI Safety Summit was held in May 2024.",

    # ============================================================
    # Benchmarks and datasets
    # ============================================================
    "FB15K-237 is a standard benchmark dataset for knowledge graph completion.",
    "WebQSP is a benchmark for knowledge base question answering using Freebase.",
    "MuSiQue is a multi-hop question answering benchmark released by Allen AI in 2022.",
    "HotpotQA is a multi-hop question answering dataset over Wikipedia released in 2018.",
    "ComplexWebQuestions is a benchmark for multi-hop question answering over Freebase.",
    "Wikidata contains over 100 million structured facts about real-world entities.",
    "ConceptNet is a multilingual common-sense knowledge graph with about 8 million assertions.",
    "DBpedia extracts structured information from Wikipedia infoboxes.",
    "MMLU is a benchmark of multitask language understanding across 57 subjects.",
    "MMLU-Pro is a harder version of MMLU released in 2024.",
    "GPQA tests graduate-level science questions and was released by Rein et al in 2023.",
    "SWE-bench tests language model performance on real GitHub issues released in 2023.",
    "HumanEval is a benchmark of 164 Python coding problems released by OpenAI in 2021.",

    # ============================================================
    # Geography and politics (broader coverage)
    # ============================================================
    "Paris is the capital of France.",
    "Berlin is the capital of Germany.",
    "Tokyo is the capital of Japan.",
    "Washington DC is the capital of the United States.",
    "London is the capital of the United Kingdom.",
    "Brussels is the capital of Belgium and hosts EU institutions.",
    "Beijing is the capital of China.",
    "New Delhi is the capital of India.",
    "Ottawa is the capital of Canada.",
    "Canberra is the capital of Australia.",
    "The European Union has 27 member states as of 2024.",
    "The United Nations has 193 member states.",

    # ============================================================
    # Medicine and biology (PubMed-style coverage)
    # ============================================================
    "DNA is composed of four nucleotide bases: adenine, cytosine, guanine, and thymine.",
    "RNA uses uracil in place of thymine.",
    "The human genome contains approximately 3 billion base pairs.",
    "CRISPR-Cas9 is a gene editing technology that uses guide RNA to direct DNA cleavage.",
    "Jennifer Doudna and Emmanuelle Charpentier received the 2020 Nobel Prize in Chemistry for CRISPR.",
    "Penicillin was discovered by Alexander Fleming in 1928.",
    "The COVID-19 pandemic was caused by SARS-CoV-2 virus.",
    "mRNA vaccines for COVID-19 were developed by Pfizer-BioNTech and Moderna.",
    "Type 1 diabetes is an autoimmune condition where the pancreas produces little or no insulin.",
    "Type 2 diabetes is characterized by insulin resistance.",
    "Alzheimer's disease is the most common cause of dementia.",
    "Cancer immunotherapy uses the body's immune system to fight cancer.",
    "Statins are drugs used to lower cholesterol levels in the blood.",

    # ============================================================
    # Science (physics, chemistry, math)
    # ============================================================
    "The speed of light in vacuum is approximately 299,792,458 meters per second.",
    "Albert Einstein published the special theory of relativity in 1905.",
    "Albert Einstein published the general theory of relativity in 1915.",
    "Quantum mechanics describes physical phenomena at the atomic and subatomic scale.",
    "The Higgs boson was confirmed at CERN in 2012.",
    "Pi is approximately 3.14159 and represents the ratio of a circle's circumference to its diameter.",
    "Euler's identity e^(i*pi) + 1 = 0 relates five fundamental mathematical constants.",
    "The Standard Model of particle physics describes electromagnetic, weak, and strong interactions.",
    "Black holes were first directly imaged by the Event Horizon Telescope in 2019.",
    "Gravitational waves were first directly detected by LIGO in 2015.",

    # ============================================================
    # History and notable events
    # ============================================================
    "The Berlin Wall fell in November 1989.",
    "The Soviet Union dissolved in December 1991.",
    "The European Union was established by the Maastricht Treaty in 1993.",
    "The internet became publicly available in 1991.",
    "The World Wide Web was invented by Tim Berners-Lee at CERN in 1989.",
    "Apple was founded by Steve Jobs and Steve Wozniak in 1976.",
    "Microsoft was founded by Bill Gates and Paul Allen in 1975.",
    "Amazon was founded by Jeff Bezos in 1994.",
    "Google was founded by Larry Page and Sergey Brin in 1998.",
    "Facebook was founded by Mark Zuckerberg in 2004 and renamed Meta in 2021.",

    # ============================================================
    # Substrate-internal vocabulary (for self-referential demos)
    # ============================================================
    "PP-119 validates K-hop graph traversal using FHRR algebra.",
    "PP-123 validates the cascade native-first router.",
    "PP-107 validates cleanup confidence as an abstention signal with AUC equal to 1.0.",
    "PP-135 validates Tier 5 substrate-KV at multiple LLM sizes.",
    "PP-150 validates substrate latency at 0.21 ms P95 at 1 million facts.",
    "PP-166 validates substrate latency as O(1) in corpus size.",
    "PP-153 validates substrate-KV cross-family at Qwen-1.5B.",
    "Cycle 187 was the first PUBLIC BENCHMARK WIN milestone for the substrate.",
    "Cycle 188 added MuSiQue r@10 = 0.784 to the multi-hop benchmark suite.",
    "Cycle 191 added Tier 5 capacity ladder at M=10,000 yielding 156x context expansion.",
    "FB15K-237 sharded substrate K-hop achieves recall@5 = 1.000 at 1-hop and 0.705 at 2-hop.",
    "FB15K-237 monolithic substrate collapses to recall@5 = 0.007 = 140x recall gap.",
    "WebQSP graph-reachable accuracy with substrate K-hop is 97.6 percent.",
    "ComplexWebQuestions accuracy with substrate K-hop is 92.6 percent.",
    "Wikipedia ingest into the substrate runs at 155 articles per second.",
    "Substrate counterfactual do() operator with audit chain was validated as PP-Wish-1.",
    "Substrate GDPR exact erasure runs in under 1 millisecond per delete at 1 million facts.",
    "Substrate bitemporal as-of queries run in 0.003 milliseconds per query at 1 million versions.",
]


def load_seed_facts() -> list[str]:
    """Return the seed KB. Stable list; safe to call repeatedly."""
    return list(SEED_FACTS)
