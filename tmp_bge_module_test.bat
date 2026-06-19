@echo off
cd /d C:\dev\hd-instrument
echo === test our backend.llm.bge_encoder path that PubMed used === 1> C:\Users\marsh\bge_test.out 2> C:\Users\marsh\bge_test.err
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "from backend.llm.bge_encoder import get_encoder; enc = get_encoder(); v = enc.encode(['hello world']); print('OUR bge ENCODER worked! shape:', v.shape)" 1>> C:\Users\marsh\bge_test.out 2>> C:\Users\marsh\bge_test.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\bge_test.out
echo DONE 1>> C:\Users\marsh\bge_test.out
