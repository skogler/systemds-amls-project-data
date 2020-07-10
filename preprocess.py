import argparse
import csv
import html
import lzma
import string
from collections import Counter
from contextlib import ExitStack
from pathlib import Path
from typing import Tuple, Dict

import numpy as np


def tokenize(text: str, html_unescape: bool, trans_table):
    if html_unescape:
        text = html.unescape(text)
    text = text.translate(trans_table)
    parts = list(filter(lambda x: len(x) > 0, text.split(" ")))
    return parts


def read_embeddings(input_file_path: Path) -> Tuple[np.ndarray, Dict[str, int]]:
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
    filtered_chars = set(string.punctuation + string.whitespace + '—') - set('&')
    token_trans_dict = {c: ' ' for c in filtered_chars}
    token_trans_dict['&'] = ' and '
    token_trans_table = str.maketrans(token_trans_dict)
    quote_trans_table = str.maketrans('', '', "'`")

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        required=False,
                        help='The directory to write the output files to. Defaults to the dir of the input file')
    parser.add_argument('--embeddings-file',
                        type=str,
                        required=False,
                        default="embeddings/glove.6B.50d.txt.xz")
    parser.add_argument('--bow',
                        type=int,
                        nargs='+',
                        help='The indices of columns to compute bag-of-words tokens for. Indices start with 0.')
    parser.add_argument('--embed',
                        type=int,
                        nargs='+',
                        help='The indices of columns to compute embeddings for. Indices start with 0.')
    parser.add_argument('-i', '--id-column',
                        type=int,
                        default=0,
                        help='The index of the unique identifier column. Indices start with 0.')
    parser.add_argument('--preserve-case',
                        action='store_true',
                        help='Disable transforming all tokens to lower case.')
    parser.add_argument('-n', '--no-header',
                        action='store_true',
                        help='Do not ignore the first line in the input CSV.')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Print tokens while parsing.')
    parser.add_argument('--no-html-unescape',
                        action='store_true',
                        help='Disable HTML unescape.')
    parser.add_argument('--no-oov-to-bow',
                        action='store_true',
                        help='Disable adding tokens to the BOW if they were not found in the vocabulary of the embedding.')
    args = parser.parse_args()

    input_file_path = Path(args.input_file)
    if not input_file_path.is_file():
        print(f"Error: input file does not exist at '{input_file_path.absolute()}'")
        return

    output_dir = Path(args.output_dir) if args.output_dir else input_file_path.parent

    if args.embed:
        input_embeddings_path = Path(args.embeddings_file)
        if not input_embeddings_path.is_file():
            print(f"Error: input embeddings file does not exist at 'f{input_embeddings_path.absolute()}'")
            return
        embeddings_array, embedding_str_to_idx = read_embeddings(input_embeddings_path)
        oov_cnt = Counter()
        empty_embedding = np.zeros_like(embeddings_array[0, :])
        empty_embedding_col_cnt = {idx: 0 for idx in args.embed}
        print(f"Embeddings dimension: {embeddings_array.shape[0]}x{embeddings_array.shape[1]}")

    used_cols = set(args.embed + args.bow)
    with input_file_path.open('r') as infile, ExitStack() as stack:
        reader = csv.reader(infile)
        if not args.no_header:
            next(reader, None)

        if args.embed:
            embed_path = output_dir / (input_file_path.stem + '_embeddings.csv')
            embed_file = stack.enter_context(embed_path.open('w'))
            embed_writer = csv.writer(embed_file, lineterminator='\n')
        if args.bow:
            bow_path = output_dir / (input_file_path.stem + '_tokens.csv')
            bow_file = stack.enter_context(bow_path.open('w'))
            bow_writer = csv.writer(bow_file, lineterminator='\n')

        num_tokens = 0
        num_rows = 0
        for row_idx, columns in enumerate(reader):
            id = columns[args.id_column].translate(quote_trans_table)
            bow_tokens = ['[NIL]']
            embeddings = []

            if args.verbose:
                print(f"{id:6s} - {'|'.join(columns)}")
            for col_idx, text in enumerate(columns):
                if not args.preserve_case:
                    text = text.lower()
                if col_idx in used_cols:
                    col_tokens = tokenize(text=text, html_unescape=not args.no_html_unescape,
                                          trans_table=token_trans_table)
                    if args.verbose:
                        print(f"{id:6s} - {'|'.join(col_tokens)}")
                    if col_idx in args.bow:
                        bow_tokens.extend(col_tokens)

                    if col_idx in args.embed:
                        indices = []
                        for token in col_tokens:
                            try:
                                indices.append(embedding_str_to_idx[token])
                            except KeyError:
                                if args.bow and not args.no_oov_to_bow:
                                    bow_tokens.append(token)
                                oov_cnt[token] += 1
                        if indices:
                            embeddings.extend(np.mean(embeddings_array[indices, :], axis=0))
                        else:
                            embeddings.extend(empty_embedding)
                            empty_embedding_col_cnt[col_idx] += 1
                            print(
                                f"Row {row_idx} column {col_idx} with text |{text}| and tokens |{'|'.join(col_tokens)}| found no embeddings in vocab!")
            num_rows += 1
            if args.bow:
                # if len(bow_tokens) == 0:
                #     bow_tokens.append('[NIL]')
                cnt = Counter(bow_tokens)
                for token, count in cnt.items():
                    if not token or count <= 0:
                        continue
                    bow_writer.writerow([id, token, count])
                if len(cnt) == 1:
                    print(f"No tokens found for row {row_idx} with columns |{'|'.join(columns)}|")
                num_tokens += len(cnt)
            if args.embed:
                embed_writer.writerow('{:.4f}'.format(x) for x in embeddings)

        if args.bow:
            print(f"Wrote {num_rows} ids with {num_tokens} tokens to {bow_path.absolute()}")
            with bow_path.with_suffix(".csv.mtd").open('w') as mtdfile:
                mtdfile.write(
                    f'{{"rows": {num_tokens}, "cols": 3, "format": "csv", "data_type": "frame", "header": false}}')

        if args.embed:
            print(f"Wrote {num_rows} rows with {embeddings_array.shape[1]} columns to {embed_path.absolute()}")
            print(f"Empty embeddings rows per column: {empty_embedding_col_cnt}")
            print(f'Top 20 most out of vocab tokens:')
            for word, word_cnt in oov_cnt.most_common(n=20):
                print(f'{word_cnt} - {word}')

            with embed_path.with_suffix(".csv.mtd").open('w') as mtdfile:
                mtdfile.write(
                    f'{{"rows": {num_rows}, "cols": {embeddings_array.shape[1]}, "format": "csv", "data_type": "matrix", "header": false}}')


if __name__ == '__main__':
    main()
