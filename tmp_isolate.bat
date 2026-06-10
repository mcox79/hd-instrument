@echo off
cd /d C:\dev\hd-instrument
echo --- TEST 1: python sys --- 1> C:\Users\marsh\isolate.out 2> C:\Users\marsh\isolate.err
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import sys; print('py', sys.version)" 1>> C:\Users\marsh\isolate.out 2>> C:\Users\marsh\isolate.err
echo EXIT_1=%ERRORLEVEL% 1>> C:\Users\marsh\isolate.out
echo --- TEST 2: numpy --- 1>> C:\Users\marsh\isolate.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import numpy; print('numpy', numpy.__version__)" 1>> C:\Users\marsh\isolate.out 2>> C:\Users\marsh\isolate.err
echo EXIT_2=%ERRORLEVEL% 1>> C:\Users\marsh\isolate.out
echo --- TEST 3: torch --- 1>> C:\Users\marsh\isolate.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 1>> C:\Users\marsh\isolate.out 2>> C:\Users\marsh\isolate.err
echo EXIT_3=%ERRORLEVEL% 1>> C:\Users\marsh\isolate.out
echo --- TEST 4: sentence-transformers --- 1>> C:\Users\marsh\isolate.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; print('st ok')" 1>> C:\Users\marsh\isolate.out 2>> C:\Users\marsh\isolate.err
echo EXIT_4=%ERRORLEVEL% 1>> C:\Users\marsh\isolate.out
echo --- TEST 5: bge load --- 1>> C:\Users\marsh\isolate.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-large-en-v1.5', device='cpu'); print('bge loaded')" 1>> C:\Users\marsh\isolate.out 2>> C:\Users\marsh\isolate.err
echo EXIT_5=%ERRORLEVEL% 1>> C:\Users\marsh\isolate.out
echo --- TEST 6: bz2 dump open --- 1>> C:\Users\marsh\isolate.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import bz2; f = bz2.open('data/wikidata_dump/latest-truthy.nt.bz2', 'rt', encoding='utf-8'); print('first line:', next(f)[:100])" 1>> C:\Users\marsh\isolate.out 2>> C:\Users\marsh\isolate.err
echo EXIT_6=%ERRORLEVEL% 1>> C:\Users\marsh\isolate.out
echo --- DONE --- 1>> C:\Users\marsh\isolate.out
