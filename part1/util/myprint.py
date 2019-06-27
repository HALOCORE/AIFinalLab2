
def print_progress(current, total, describe="progress"):
    ratio = current / total
    print(" " + describe + " |", end="")
    for i in range(20):
        if i / 20 <= ratio:
            print("#", end="")
        else:
            print(" ", end="")
    print( "| %.1f%%" % (ratio * 100), end='\r')


def print_mdtable_head(head:list):
    print(" | " + " | ".join([str(x) for x in head]) + " | ")
    print(" | " + " | ".join([":------:" for _ in range(len(head))]) + " | ")


def print_mdtable_body(tab:list):
    for row in tab:
        print("| ",end="")
        for elem in row:
            print ( "%s | " % elem, end="")
        print()