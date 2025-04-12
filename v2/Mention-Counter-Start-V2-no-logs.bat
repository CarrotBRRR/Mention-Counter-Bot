@echo off
echo ----------------- Checking for Updates ----------------
git pull origin main
echo --------------------- Starting Up ---------------------
python3.11.exe -u ./main-v2.py
cls
call Mention-Counter-Start-V2.bat