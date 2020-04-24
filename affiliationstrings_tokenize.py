from collections import Counter

with open("./data/affiliationstrings/affiliationstrings_ids.csv", "r") as infile, \
    open("./data/affiliationstrings/affiliationstrings_tokens.csv", "w") as outfile:
    infile.readline()
    for line in infile.readlines():
        parts = line.split(",")
        id = parts[0].strip("\"")
        sentence = " ".join(parts[1:]).strip("\"")[:-2]
        print(f"{id} - {sentence}")
        for token, count in Counter(sentence.split(" ")).most_common():
            if not token:
                continue
            print(f"{token} - {count}")
            outfile.write(f"{id},{token},{count}\n")