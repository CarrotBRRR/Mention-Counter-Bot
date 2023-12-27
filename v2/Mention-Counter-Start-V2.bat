@echo off
echo Checking for updates...
git pull origin main
echo --------------------- Starting Up ---------------------
python3.11.exe ./main-v2.py
call Mention-Counter-Start-V2.bat