@echo off
cd /d C:\dev\hd-instrument
echo === isolate sentence-transformers sub-imports with faulthandler === 1> C:\Users\marsh\fault.out 2> C:\Users\marsh\fault.err

echo --- transformers --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import transformers; print('transformers', transformers.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo --- tokenizers --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import tokenizers; print('tokenizers', tokenizers.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo --- scipy --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import scipy; print('scipy', scipy.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo --- sklearn --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import sklearn; print('sklearn', sklearn.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo --- huggingface_hub --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import huggingface_hub; print('hf_hub', huggingface_hub.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo --- accelerate --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import accelerate; print('accelerate', accelerate.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo --- sentence_transformers FULL with faulthandler --- 1>> C:\Users\marsh\fault.out
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -X faulthandler -c "import sentence_transformers; print('st', sentence_transformers.__version__)" 1>> C:\Users\marsh\fault.out 2>> C:\Users\marsh\fault.err
echo EXIT=%ERRORLEVEL% 1>> C:\Users\marsh\fault.out

echo === DONE === 1>> C:\Users\marsh\fault.out
