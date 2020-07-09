import argparse
import re
from collections import Counter
from pathlib import Path
from typing.re import Pattern
import csv
import html


def tokenize(split_pattern: Pattern, col: str):
    parts = filter(lambda x: len(x) > 0, split_pattern.split(col.lower()))
    return parts


def main():
    quote_pattern = re.compile(r'["\'`]')
    split_pattern = re.compile(r'["\'\s:,.;—\-\\()*$?^!{}@/]')

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('-c', '--columns',
                        type=int,
                        nargs='+',
                        required=True,
                        help="The indices of columns to compute embeddings for. Indices start with 0.")
    parser.add_argument('-i', '--id-column',
                        type=int,
                        default=0,
                        help="The index of the unique identifier column. Indices start with 0.")
    parser.add_argument('--preserve-case',
                        action='store_true',
                        help="Disable transforming all tokens to lower case.")
    parser.add_argument('-n', '--no-header',
                        action='store_true',
                        help="Also include the first line in the input CSV.")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help="Print tokens while parsing.")
    parser.add_argument('--no-html-unescape',
                        action='store_true',
                        help="Disable HTML unescape.")

    args = parser.parse_args()
    with open(args.input_file, "r") as infile, open(args.output_file, "w") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, lineterminator='\n')
        if not args.no_header:
            next(reader, None)
        num_tokens = 0
        num_rows = 0
        for columns in reader:
            id = quote_pattern.sub("", columns[args.id_column])
            tokens = ["<<<CLS>>>"]
            for ci in args.columns:
                text = columns[ci]
                if not args.no_html_unescape:
                    text = html.unescape(text)
                tokens.extend(tokenize(split_pattern=split_pattern, col=text))
            if args.verbose:
                print(f"{id:6s} - {'|'.join(tokens)}")
            cnt = Counter(tokens)
            for token, count in cnt.items():
                if not token or count <= 0:
                    continue
                writer.writerow([id, token, count])
            num_tokens += len(cnt)
            num_rows += 1
        print(f"Wrote {num_rows} ids with {num_tokens} tokens to {args.output_file}")
        with Path(args.output_file + ".mtd").open('w') as mtdfile:
            mtdfile.write(
                f'{{"rows": {num_tokens}, "cols": 3, "format": "csv", "data_type": "frame", "header": false}}')


if __name__ == '__main__':
    main()
