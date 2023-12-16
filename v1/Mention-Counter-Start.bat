@echo off
echo Checking for updates...
git pull origin main
echo --------------------- Starting Up ---------------------
python3.11.exe ./v1/main.py
call Mention-Counter-Start.bat