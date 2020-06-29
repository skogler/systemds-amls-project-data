from collections import Counter
import csv

with open("./data/DBLP-ACM/ACM.csv", "r") as infile, \
    open("./data/DBLP-ACM/ACM_tokens.csv", "w") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    next(reader, None)
    for parts in reader:
        id = parts[0].strip("\"")
        sentence = " ".join(parts[1:]).replace(",", "").replace(".", "").replace(":", "").replace("\"", "")
        # print(f"{id} - {sentence}")
        for token, count in Counter(sentence.split(" ")).most_common():
            if not token:
                continue
            # print(f"{token} - {count}")
            writer.writerow([id, token, count])

with open("./data/DBLP-ACM/DBLP2.csv", "r") as infile, \
    open("./data/DBLP-ACM/DBLP2_tokens.csv", "w") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    next(reader, None)
    for parts in reader:
        id = parts[0].strip("\"")
        sentence = " ".join(parts[1:]).replace(",", "").replace(".", "").replace(":", "").replace("\"", "")
        # print(f"{id} - {sentence}")
        for token, count in Counter(sentence.split(" ")).most_common():
            if not token:
                continue
            # print(f"{token} - {count}")
            writer.writerow([id, token, count])
