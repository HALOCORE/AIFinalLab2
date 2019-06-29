import random
import sys

def rand_filelines(srcfilename, dstfilename, linecount):
    wlines = list()
    with open(srcfilename, 'r') as f:
        lines = f.readlines()
        wlines.append(lines[0])
        if linecount > 0:
                selidx = random.sample(range(1, len(lines)), linecount)
        else:
                selidx = list(range(1, len(lines)))
                random.shuffle(selidx)
        for idx in selidx:
            wlines.append(lines[idx])
    with open(dstfilename, 'w') as f:
        f.writelines(wlines)

s1 = int(sys.argv[1])
s2 = int(sys.argv[2])

rand_filelines("./trainset.csv", "./trainsetsmall.csv", s1)
rand_filelines("./testset.csv", "./testsetsmall.csv", s2)