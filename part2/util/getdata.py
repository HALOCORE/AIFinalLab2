
def transform_elem(elem):
    # return (elem[0]*8 + elem[1], elem[2]*8 + elem[3], elem[4]*8 + elem[5]) 
    # return (elem[0]*elem[1], elem[2]*elem[3], elem[4]*elem[5]) 
    return elem


def transform_elemlist(elems):
    trans_elems = list()
    for elem in elems:
        trans_elems.append(transform_elem(elem))
    return trans_elems


def get_data(filename):
    """得到数据列表"""
    with open(filename, 'r') as myfile:
        lines = myfile.readlines()[1:]
        elems = list()
        labels = list()
        for line in lines:
            words = [x.strip() for x in line.split(',')]
            elems.append(tuple([float(x) for x in words[:-1]]))
            labels.append(words[-1])
        return transform_elemlist(elems), labels



def get_cluster_data():
    elems, labels = get_data("./data/Frogs_MFCCs.csv")
    return elems, labels


def get_fake_cluster_data():
    elems, labels = get_data("./data/fakedata.csv")
    return elems, labels