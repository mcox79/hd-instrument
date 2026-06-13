@echo off
REM Start both desktop runners (GPU + remote-CPU) detached. Singleton-pid-file guards duplicates.
REM Launched via Win32_Process.Create so it survives the ssh session that started it.
cd /d C:\dev\hd-instrument
start "" /b .venv\Scripts\python.exe experiments\runner_v2_prod.py --queue-dir C:\dev\hd-instrument\data\overnight_queue --id gpu_runner_0 --idle-exit-minutes 10080 --singleton-pid-file C:\dev\hd-instrument\data\logs\gpu_runner_0.pid > C:\dev\hd-instrument\data\logs\gpu_runner_0.out 2>&1
start "" /b .venv\Scripts\python.exe experiments\runner_v2_prod.py --queue-dir C:\dev\hd-instrument\data\remote_cpu_queue --id cpu_runner_0 --idle-exit-minutes 10080 --singleton-pid-file C:\dev\hd-instrument\data\logs\cpu_runner_0.pid > C:\dev\hd-instrument\data\logs\cpu_runner_0.out 2>&1
