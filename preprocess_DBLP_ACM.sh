#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "${SCRIPT_DIR}/preprocess.py" "${SCRIPT_DIR}/DBLP-ACM/ACM.csv" -i 0 --embed 1 --bow  1 2
python3 "${SCRIPT_DIR}/preprocess.py" "${SCRIPT_DIR}/DBLP-ACM/DBLP2.csv" -i 0 --embed 1 --bow 1 2