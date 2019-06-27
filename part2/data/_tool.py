import random
import sys

def rand_filelines(srcfilename, dstfilename, linecount, line_transformer=lambda x:x):
    wlines = list()
    with open(srcfilename, 'r') as f:
        lines = f.readlines()
        wlines.append(line_transformer(lines[0]) + "\n")
        if linecount > 0:
            selidx = random.sample(range(1, len(lines)), linecount)
        else:
            selidx = range(1, len(lines))
        for idx in selidx:
            wlines.append(line_transformer(lines[idx]) + "\n")
    with open(dstfilename, 'w') as f:
        f.writelines(wlines)


def line_trans(line:str, label_idx:int):
    elems = [x.strip() for x in line.split(',')]
    tr_elems = elems[0:-4] + [elems[-5 + label_idx]]
    return ",".join(tr_elems)


if __name__ != "__main__":
    print("# 该文件不能被import使用。只能作为命令行脚本。")
    assert(False)


data_size = int(sys.argv[1])
label_idx = int(sys.argv[2])

rand_filelines("./Frogs_MFCCs_origin.csv", "./Frogs_MFCCs.csv", data_size, lambda line:line_trans(line, label_idx))