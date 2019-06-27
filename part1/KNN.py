"""
KNN分类算法实现模块
"""

from util import evaluate
from util import getdata
from util.myprint import print_progress

def elem_dist(in_elem1, in_elem2):
    """计算距离"""
    dis = 0
    for x1, x2 in zip(in_elem1, in_elem2):
        dis += (x1-x2)*(x1-x2)# abs(x1 - x2)
    return dis

def update_neighbors(center_elem, elem, label, nb_dists: list, nb_num: int, debug=False):
    """更新邻居, 插入排序实现"""
    nb_len = len(nb_dists)
    check_dist = elem_dist(center_elem, elem)
    if nb_len < nb_num: # 邻居未填满
        nb_dists.append((check_dist, label))
        for i in range(nb_len, 0, -1):
            if nb_dists[i - 1][0] > nb_dists[i][0]:
                tmp = nb_dists[i - 1]
                nb_dists[i - 1] = nb_dists[i]
                nb_dists[i] = tmp
    else:
        farest_dist = nb_dists[-1][0] # 邻居已填满
        if check_dist < farest_dist: # 最后一个被挤掉
            inserted = False
            for i in range(nb_num - 1, 0, -1):
                if nb_dists[i - 1][0] > check_dist:
                    nb_dists[i] = nb_dists[i - 1]
                else:
                    inserted = True
                    nb_dists[i] = (check_dist, label)
                    break
            if not inserted:
                nb_dists[0] = (check_dist, label)
    if debug:
        print("# update_neighbors. check: (%d, %d) \tnb_dists: %s" % (check_dist, label, nb_dists))


def judge_by_neighbors(nb_dists: list):
    """根据邻居距离列表 [(距离, 类型), ...] 完成判断，假设类型为 1/2"""
    counter = dict()
    for dis, label in nb_dists:
        if label not in counter:
            counter[label] = 1
        else:
            counter[label] += 1
    maxlabel = "NO_LABEL"
    maxcount = 0
    for label in counter:
        if counter[label] > maxcount: # TODO: 大于还是大于等于
            maxlabel = label
            maxcount = counter[label]
    assert(maxlabel != "NO_LABEL")
    return maxlabel


def knn_core(center_elem, trainset:list, trainlabel:list, nb_num:int, debug=False):
    """knn算法"""
    assert(len(trainset) == len(trainlabel))
    nb_dists = list()
    for elem, label in zip(trainset, trainlabel):
        update_neighbors(center_elem, elem, label, nb_dists, nb_num)
    result = judge_by_neighbors(nb_dists)
    if(debug):
        print("# naive_knn. elem: %s, dataset_size: %d, result: %s" % (center_elem, len(trainset), result))
    return result




def knn(trainset:list, trainlabel:list, testset:list, testlabel:list, k:int):
    print("# knn. trainsize:%d, testsize:%d." % (len(trainset), len(testset)))
    classes = list(set(trainlabel))
    predict_label = list()
    elem_count = 0
    for test_elem in testset:
        elem_count += 1
        if (elem_count % 50 == 0):
            print_progress(elem_count, len(testlabel))
        label = knn_core(test_elem, trainset, trainlabel, k)
        predict_label.append(label)
    Accuracy, MacroF1, MicroF1 = evaluate.evaluate(classes, testlabel, predict_label)
    return predict_label, Accuracy, MacroF1, MicroF1


# ----------------------------------------------------------------------


def main():
    trainset, trainlabel = getdata.get_traindata()
    testset, testlabel = getdata.get_testdata()
    ypred, Accuracy, MacroF1, MicroF1 = knn(trainset, trainlabel, testset, testlabel, 5)
    print(Accuracy, MacroF1, MicroF1)


if __name__ == "__main__":
    print("# KNN.py 被调用")
    main()