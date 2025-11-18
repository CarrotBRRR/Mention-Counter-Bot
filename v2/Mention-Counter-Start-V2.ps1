# Set the console code page to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Get the current date and time for the log file
$LOGFILE_TIME = (Get-Date).ToString("HHmm")
$LOGFILE = "./logs/$(Get-Date -Format 'yyyy-MM-dd')_$LOGFILE_TIME.log"

# Display message for checking updates
Write-Host "----------------- Checking for Updates ----------------"

# Perform a git pull
git pull origin main

# Display message for starting up
Write-Host "--------------------- Starting Up ---------------------"

# Run the Python script and append its output to the log file and the terminal
python3.11.exe -u ./main-v2.py | Tee-Object -FilePath $LOGFILE -Append

# Clear the console screen
Clear-Host

# Call the PowerShell script itself
& $MyInvocation.MyCommand.Definition
