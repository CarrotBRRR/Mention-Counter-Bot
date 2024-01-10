@echo off
set LOGFILE_TIME=%TIME:~0,2%-%TIME:~3,2%
set LOGFILE=./logs/%DATE%_%LOGFILE_TIME%.log
echo ----------------- Checking for Updates ----------------
git pull origin main
echo --------------------- Starting Up ---------------------
python3.11.exe ./main-v2.py >> LOGFILE

call Mention-Counter-Start-V2.bat