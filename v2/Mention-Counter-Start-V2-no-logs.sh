#!/bin/bash

while true
do
    echo "----------------- Checking for Updates ----------------"
    git pull origin main

    echo "--------------------- Starting Up ---------------------"
    python3.13 -u ./main-v2.py

    clear
done