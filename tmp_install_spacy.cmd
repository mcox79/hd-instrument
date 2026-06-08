@echo off
echo === install spaCy in .venv-demo ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install spacy 2>&1 | findstr /I "Successfully Installing Collecting"
echo.
echo === download en_core_web_sm model ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m spacy download en_core_web_sm 2>&1 | findstr /I "Success linked python download"
echo.
echo === sanity test spaCy NER ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import spacy; nlp = spacy.load('en_core_web_sm'); doc = nlp('Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei in San Francisco.'); print('entities:'); [print(' ', e.text, '->', e.label_) for e in doc.ents]"
echo.
echo === peek at existing wikipedia ingest dir ===
dir C:\dev\hd-instrument\data\exp_wikipedia_ingest_100k_gpu_v1 /b 2>nul
