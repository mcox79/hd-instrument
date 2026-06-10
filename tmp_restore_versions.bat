@echo off
cd /d C:\dev\hd-instrument
echo === restore numpy + ST to versions PubMed used === 1> C:\Users\marsh\restore.out 2> C:\Users\marsh\restore.err
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install "numpy==2.4.4" "sentence-transformers==5.5.1" 1>> C:\Users\marsh\restore.out 2>> C:\Users\marsh\restore.err
echo EXIT_RESTORE=%ERRORLEVEL% 1>> C:\Users\marsh\restore.out

echo === test ST import === 1>> C:\Users\marsh\restore.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import sentence_transformers; print('ST', sentence_transformers.__version__)" 1>> C:\Users\marsh\restore.out 2>> C:\Users\marsh\restore.err
echo EXIT_IMPORT=%ERRORLEVEL% 1>> C:\Users\marsh\restore.out

echo === test our bge encoder === 1>> C:\Users\marsh\restore.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "from backend.llm.bge_encoder import get_encoder; enc = get_encoder(); v = enc.encode(['hello world']); print('encoded shape', v.shape)" 1>> C:\Users\marsh\restore.out 2>> C:\Users\marsh\restore.err
echo EXIT_BGE=%ERRORLEVEL% 1>> C:\Users\marsh\restore.out
echo DONE 1>> C:\Users\marsh\restore.out
