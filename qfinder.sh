#!/bin/bash
set +m 

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while kill -0 "$pid" 2>/dev/null; do
        for i in $(seq 0 3); do
            printf "\r[%c] Loading..." "${spinstr:$i:1}"
            sleep $delay
        done
    done
    printf "\r"
}


run_with_spinner() {
    "$@" >/dev/null 2>&1 &
    spinner $!
    wait $!
}


run_with_spinner python3 -m venv dependencies
source dependencies/bin/activate
run_with_spinner pip install --upgrade pip
run_with_spinner pip install PyQt5 requests beautifulsoup4
python3 src/main.py
