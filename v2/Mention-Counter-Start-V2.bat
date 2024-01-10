@echo off
chcp 65001 > NUL
set LOGFILE_TIME=%TIME:~0,2%-%TIME:~3,2%
set LOGFILE=./logs/%DATE%_%LOGFILE_TIME%.log
echo ----------------- Checking for Updates ----------------
git pull origin main
echo --------------------- Starting Up ---------------------
python3.11.exe -u ./main-v2.py | tee -a %LOGFILE%
cls
call Mention-Counter-Start-V2.bat