#!/usr/bin/env python
import csv
import sys
from pathlib  import Path
from itertools import (takewhile,repeat)

def linecount(filename: Path):
    with filename.open('rb') as f:
        bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
        return sum( buf.count(b'\n') for buf in bufgen )

delimiters=[',', ';', ' ']
quotechars=['"', "'", "|"]

def main():
    input_path = Path(sys.argv[1])
    nrow = linecount(input_path)
    with input_path.open(newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiters[0], quotechar=quotechars[0])
        first = next(reader)
        ncol = len(first)
    with input_path.with_name(input_path.name + '.mtd').open('w') as mtdfile:
        mtdfile.write(f'{{"rows": {nrow}, "cols": {ncol}, "format": "csv", "data_type": "frame"}}')


if __name__ == "__main__":
    main()
