import argparse
import csv
import html
import lzma
import re
from collections import Counter, defaultdict
from pprint import pprint
from typing import Pattern, Dict, Tuple

import numpy as np


def tokenize(split_pattern: Pattern, col: str):
    parts = filter(lambda x: len(x) > 0, split_pattern.split(col.lower()))
    return parts


def read_embeddings(input_file_path: str) -> Tuple[np.ndarray, Dict[str, int]]:
    embedding_lookup_dict = dict()
    embeddings = []
    with lzma.open(input_file_path, mode='rt') as infile:
        for idx, line in enumerate(infile):
            parts = line.split(' ')
            embedding = np.fromiter(map(float, parts[1:]), dtype=np.float32)
            embedding_lookup_dict[parts[0]] = len(embeddings)
            embeddings.append(embedding)
    return np.stack(embeddings, axis=0), embedding_lookup_dict


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
                        help="The indices of columns to tokenize. Indices start with 0.")
    parser.add_argument('--preserve-case',
                        action='store_true',
                        help="Disable transforming all tokens to lower case.")
    parser.add_argument('-n', '--no-header',
                        action='store_true',
                        help="Also include the first line in the input CSV.")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help="Print more output.")
    parser.add_argument('--no-html-unescape',
                        action='store_true',
                        help="Disable HTML unescape.")

    args = parser.parse_args()

    embeddings_array, embedding_str_to_idx = read_embeddings("embeddings/glove.6B.50d.txt.xz")

    cnt = Counter()
    empty_embedding = np.zeros_like(embeddings_array[0,:])
    print(f"Embeddings dimension: {embeddings_array.shape[0]}x{embeddings_array.shape[1]}")
    with open(args.input_file, "r") as infile, open(args.output_file, "w") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONE, lineterminator='\n')
        if not args.no_header:
            next(reader, None)
        num_rows = 0
        for row_idx, columns in enumerate(reader):
            # id = quote_pattern.sub("", columns[args.id_column])
            embeddings = []
            for ci in args.columns:
                text = columns[ci]
                indices = []
                if not args.no_html_unescape:
                    text = html.unescape(text)
                tokens = tokenize(split_pattern=split_pattern, col=text)
                for token in tokens:
                    try:
                        indices.append(embedding_str_to_idx[token])
                    except KeyError:
                        cnt[token] += 1
                if indices:
                    embeddings.extend(np.mean(embeddings_array[indices, :], axis=0))
                else:
                    embeddings.extend(empty_embedding)
                    print(f"Row {row_idx} column {ci} with text |{text}| had no valid embeddings! (all out of vocab)")

            writer.writerow('{:.4f}'.format(x) for x in embeddings)
            num_rows += 1
        print(f"Wrote {num_rows} rows to {args.output_file}")
        print(f'Top 20 most out of vocab tokens:')
        for word, word_cnt in cnt.most_common(n=20):
            print(f'{word_cnt} - {word}')


if __name__ == '__main__':
    main()
