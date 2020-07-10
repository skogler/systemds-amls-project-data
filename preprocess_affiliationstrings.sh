#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "${SCRIPT_DIR}/preprocess.py" "${SCRIPT_DIR}/affiliationstrings/affiliationstrings.csv" -i 0 --embed 1 --bow 1