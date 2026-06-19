@echo off
cd /d C:\dev\hd-instrument
echo === STEP 1: snapshot pip state === 1> C:\Users\marsh\fix_numpy.out 2> C:\Users\marsh\fix_numpy.err
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip freeze 1> C:\Users\marsh\pip_freeze_before_fix.txt 2>> C:\Users\marsh\fix_numpy.err
echo snapshot saved to pip_freeze_before_fix.txt 1>> C:\Users\marsh\fix_numpy.out

echo === STEP 2: pin numpy^<2 === 1>> C:\Users\marsh\fix_numpy.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install "numpy<2" 1>> C:\Users\marsh\fix_numpy.out 2>> C:\Users\marsh\fix_numpy.err
echo EXIT_NUMPY=%ERRORLEVEL% 1>> C:\Users\marsh\fix_numpy.out

echo === STEP 3: verify import after numpy fix === 1>> C:\Users\marsh\fix_numpy.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import numpy; print('numpy now', numpy.__version__); from sentence_transformers import SentenceTransformer; print('ST import ok')" 1>> C:\Users\marsh\fix_numpy.out 2>> C:\Users\marsh\fix_numpy.err
echo EXIT_VERIFY=%ERRORLEVEL% 1>> C:\Users\marsh\fix_numpy.out

echo === STEP 4: smoke bge load === 1>> C:\Users\marsh\fix_numpy.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-large-en-v1.5', device='cpu'); v = m.encode(['hello world']); print('bge encoded shape', v.shape)" 1>> C:\Users\marsh\fix_numpy.out 2>> C:\Users\marsh\fix_numpy.err
echo EXIT_BGE=%ERRORLEVEL% 1>> C:\Users\marsh\fix_numpy.out

echo === DONE === 1>> C:\Users\marsh\fix_numpy.out
