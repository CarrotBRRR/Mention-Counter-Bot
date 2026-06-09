#!/bin/bash

while true
do
    echo "----------------- Checking for Updates ----------------"
    git pull origin main

    echo "--------------------- Starting Up ---------------------"
    python -u Mention-Counter-Bot/v2/main-v2.py

    
done
