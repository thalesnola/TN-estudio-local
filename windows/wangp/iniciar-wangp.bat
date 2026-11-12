@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File D:\WanGP\liberar-gpu.ps1
cd /d D:\WanGP
call env_uv\Scripts\activate.bat
python wgp.py --profile 4 %*
