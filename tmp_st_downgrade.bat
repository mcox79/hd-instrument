@echo off
cd /d C:\dev\hd-instrument
echo === downgrade sentence-transformers to 3.x stable === 1> C:\Users\marsh\st_down.out 2> C:\Users\marsh\st_down.err
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install "sentence-transformers<4" 1>> C:\Users\marsh\st_down.out 2>> C:\Users\marsh\st_down.err
echo EXIT_DOWNGRADE=%ERRORLEVEL% 1>> C:\Users\marsh\st_down.out

echo === verify with faulthandler === 1>> C:\Users\marsh\st_down.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import sentence_transformers; print('ST', sentence_transformers.__version__)" 1>> C:\Users\marsh\st_down.out 2>> C:\Users\marsh\st_down.err
echo EXIT_IMPORT=%ERRORLEVEL% 1>> C:\Users\marsh\st_down.out

echo === bge load smoke === 1>> C:\Users\marsh\st_down.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-large-en-v1.5', device='cpu'); v = m.encode(['hello world']); print('bge encode shape', v.shape)" 1>> C:\Users\marsh\st_down.out 2>> C:\Users\marsh\st_down.err
echo EXIT_BGE=%ERRORLEVEL% 1>> C:\Users\marsh\st_down.out
echo DONE 1>> C:\Users\marsh\st_down.out
