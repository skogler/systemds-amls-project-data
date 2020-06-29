from collections import Counter
import csv

with open("./data/affiliationstrings/affiliationstrings_ids.csv", "r") as infile, \
    open("./data/affiliationstrings/affiliationstrings_tokens.csv", "w") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    next(reader, None)
    for parts in reader:
        id = parts[0].strip("\"")
        sentence = parts[1].replace(",", "").replace(".", "").replace(":", "").replace("\"", "")
        # print(f"{id} - {sentence}")
        for token, count in Counter(sentence.split(" ")).most_common():
            if not token:
                continue
            # print(f"{token} - {count}")
            writer.writerow([id, token, count])

with open("./data/affiliationstrings/affiliationstrings_mapping.csv", "r") as infile, \
        open("./data/affiliationstrings/affiliationstrings_mapping_fixed.csv", "w") as outfile:
    for line in infile.readlines():
        fixed = line.replace("\"", "")
        outfile.write(fixed)
