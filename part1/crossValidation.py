
def crossValidation(func, trainset, trainlabel, fold:int):
    split_trainset = [list() for _ in range(fold)]
    split_trainlabel = [list() for _ in range(fold)]
    datalen = len(trainset)
    for i in range(fold):
        start_pos = (i * datalen) // fold
        end_pos = ((i+1) * datalen) // fold
        split_trainset[i] = trainset[start_pos:end_pos]
        split_trainlabel[i] = trainlabel[start_pos:end_pos]
    accuracy_list = list()
    macroF1_list = list()
    microF1_list = list()
    aver_microF1 = 0
    for i in range(fold):
        tmp_testset = split_trainset[i]
        tmp_testlabel = split_trainlabel[i]
        tmp_trainset = list()
        tmp_trainlabel = list()
        for j in range(fold):
            if i != j:
                tmp_trainset.extend(split_trainset[j])
                tmp_trainlabel.extend(split_trainlabel[j])
        _, Accuracy, MacroF1, MicroF1 = func(tmp_trainset, tmp_trainlabel, tmp_testset, tmp_testlabel)
        accuracy_list.append(Accuracy)
        macroF1_list.append(MacroF1)
        microF1_list.append(MicroF1)
    print("# crossValidation. Fold = %d" % fold)
    print("    | Accuracy | Macro F1 | Micro F1 |")
    print("    |:--------:|:--------:|:--------:|")
    for ac, ma, mi in zip(accuracy_list, macroF1_list, microF1_list):
        print("    | %f | %f | %f |" % (ac, ma, mi))
    aver_microF1 = sum(microF1_list) / fold
    print("  aver_micro_F1 = %s" % (aver_microF1))
    return aver_microF1, microF1_list


def crossValidationParams(func_generator, params_list:list, trainset:list, trainlabel:list, fold:int):
    microF1_mat = list()
    microF1_avers = list()
    for params in params_list:
        func = func_generator(params)
        aver_microF1, microF1_list = crossValidation(func, trainset, trainlabel, fold)
        microF1_mat.append(microF1_list)
        microF1_avers.append(aver_microF1)
    max_miF1 = max(microF1_avers)
    max_miF1_idx = microF1_avers.index(max_miF1)
    return {
        "mat":microF1_mat,
        "avers":microF1_avers,
        "best_param":params_list[max_miF1_idx],
        "max_microF1": max_miF1,
        "idx":max_miF1_idx
    }


def main():
    from decisionTree import createTree
    from SVM import multiClassSVM
    from KNN import knn
    from util import getdata
    from util.myprint import print_mdtable_head, print_mdtable_body
    trainset, trainlabel = getdata.get_traindata()
    testset, testlabel = getdata.get_testdata()
    def knn_generator(params):
        return lambda trs, trl, tss, tsl: knn(trs, trl, tss, tsl, params[0])
    def decTree_generator(params):
        return lambda trs, trl, tss, tsl: createTree(trs, trl, tss, tsl, filter_size=params[0])
    def svm_generator(params):
        return lambda trs, trl, tss, tsl: multiClassSVM(trs, trl, tss, tsl, sigma=params[0], marginC=params[1])
    # results = crossValidationParams(knn_generator, [(3,),(5,),(7,),(9,),(11,)], trainset, trainlabel, 5)
    # results = crossValidationParams(decTree_generator, [(0,),(5,),(10,),(15,),(20,)], trainset, trainlabel, 5)
    # results = crossValidationParams(svm_generator, [(0,5),(0,10),(0,100),(2,5),(2,10),(2,100)], trainset, trainlabel, 5)
    results = crossValidationParams(svm_generator, [(2,5),(2,10),(2,100)], trainset, trainlabel, 5)
    print(results)
    print_mdtable_head(list(range(5)))
    print_mdtable_body(results['mat'])

if __name__ == "__main__":
    main()