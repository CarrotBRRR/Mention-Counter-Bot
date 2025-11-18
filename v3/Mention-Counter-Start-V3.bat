cls
@echo off
echo ----------------- Checking for Updates ----------------
git pull origin main
echo --------------------- Starting Up ---------------------
python3.13.exe -u ./main-v3.py
cls
call Mention-Counter-Start-V3.bat