
def transform_elem(elem):
    # return (elem[0]*8 + elem[1], elem[2]*8 + elem[3], elem[4]*8 + elem[5]) 
    # return (elem[0]*elem[1], elem[2]*elem[3], elem[4]*elem[5]) 
    # return (elem[2]-elem[0], elem[3]-elem[1], elem[4]-elem[0], elem[5]-elem[1])
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
            elems.append(tuple([ord(x) for x in words[:-1]]))
            labels.append(words[-1])
        return transform_elemlist(elems), labels



_PCA_enabled = False

if _PCA_enabled is True:
    from .PCA import PCA, apply_PCA_transform
    print("# PCA启用.")

_PCA_info = None


def get_traindata():
    #elems, labels = get_data("./data/trainset.csv")
    elems, labels = get_data("./data/trainsetsmall.csv")
    if _PCA_enabled:
        global _PCA_info
        trans_elems, _, _, pca_info = PCA(elems, 0.8)
        _PCA_info = pca_info
    else:
        trans_elems = elems
    return trans_elems, labels


def get_testdata():
    #elems, labels = get_data("./data/testset.csv")
    elems, labels = get_data("./data/testsetsmall.csv")
    if _PCA_enabled:
        global _PCA_info
        trans_elems = apply_PCA_transform(elems, _PCA_info)
    else:
        trans_elems = elems
    return trans_elems, labels