#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "${SCRIPT_DIR}/tokenize.py" -c 1 2 -i 0 "${SCRIPT_DIR}/DBLP-ACM/ACM.csv" "${SCRIPT_DIR}/DBLP-ACM/ACM_tokens.csv"
python3 "${SCRIPT_DIR}/tokenize.py" -c 1 2 -i 0 "${SCRIPT_DIR}/DBLP-ACM/DBLP2.csv" "${SCRIPT_DIR}/DBLP-ACM/DBLP2_tokens.csv"
