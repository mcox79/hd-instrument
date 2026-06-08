@echo off
echo === look for Wikipedia 100K dump on runner ===
dir C:\dev\hd-instrument\data\wikipedia* 2>nul
dir C:\dev\hd-instrument\data\wiki* 2>nul
dir C:\dev\hd-instrument\tools\dl_wikipedia*.py /b 2>nul
echo.
echo === look for any staging dirs ===
dir C:\dev\hd-instrument\data\ /AD /B 2>nul | findstr /I wiki
echo.
echo === spaCy install status ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import spacy; print('spacy', spacy.__version__)" 2>&1
echo.
echo === check HF datasets cache for wikipedia ===
dir C:\Users\marsh\.cache\huggingface\datasets\wikipedia* /b 2>nul | findstr /I wikipedia
echo.
echo === check HF datasets cache root ===
dir C:\Users\marsh\.cache\huggingface\datasets\ /b 2>nul
echo.
echo === look in any 'corpus' or 'raw' dir ===
dir C:\dev\hd-instrument\data\corpus 2>nul
dir C:\dev\hd-instrument\data\raw 2>nul
