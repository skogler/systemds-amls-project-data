#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "${SCRIPT_DIR}/embed_glove.py" "${SCRIPT_DIR}/DBLP-ACM/ACM.csv" "${SCRIPT_DIR}/DBLP-ACM/ACM_embeddings.csv" -c 1
python3 "${SCRIPT_DIR}/embed_glove.py" "${SCRIPT_DIR}/DBLP-ACM/DBLP2.csv" "${SCRIPT_DIR}/DBLP-ACM/DBLP2_embeddings.csv"  -c 1