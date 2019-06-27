
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


def print_cluster_data(cluster_data:list):
    class_count = len(set(cluster_data))
    print(class_count)
    for data in cluster_data:
        print(data)

import sys
_real_console = None
_stdout_file = None

def set_stdout(filename:str):
    global _real_console
    global _stdout_file
    _stdout_file = open(filename, 'w')
    _real_console = sys.stdout
    sys.stdout = _stdout_file

def reset_stdout():
    sys.stdout = _real_console
    _stdout_file.close()

