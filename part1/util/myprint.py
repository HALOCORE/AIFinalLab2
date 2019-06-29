
def print_progress(current, total, describe="progress"):
    ratio = current / total
    print(" " + describe + " |", end="")
    for i in range(20):
        if i / 20 <= ratio:
            print("#", end="")
        else:
            print(" ", end="")
    print( "| %.1f%%\r" % (ratio * 100), end='')


def print_mdtable_head(head:list):
    print(" | " + " | ".join([str(x) for x in head]) + " | ")
    print(" | " + " | ".join([":------:" for _ in range(len(head))]) + " | ")


def print_mdtable_body(tab:list, rownames=None, append_gens=None, item_format="%s"):
    rowid = 0
    for row in tab:
        print("| ",end="")
        if rownames is not None:
            print(str(rownames[rowid]) + " | ", end="")
            rowid += 1
        for elem in row:
            print ( (item_format + " | ") % elem, end="")
        if append_gens is not None:
            for gen in append_gens:
                print((item_format + " | ") % (gen(row)), end="")
        print()