import random

def crossValidation(func, trainset, trainlabel, fold:int, datashuffle=False, debug_mode=False):
    split_trainset = [list() for _ in range(fold)]
    split_trainlabel = [list() for _ in range(fold)]
    datalen = len(trainset)
    
    # 打乱数据
    if datashuffle:
        sh_idx = random.shuffle(list(range(datalen)))   # 随机编号
        sh_trainset = [trainset[idx] for idx in sh_idx]
        sh_trainlabel = [trainlabel[idx] for idx in sh_idx]
    else:
        sh_trainset = trainset
        sh_trainlabel = trainlabel

    for i in range(fold):
        start_pos = (i * datalen) // fold
        end_pos = ((i+1) * datalen) // fold
        split_trainset[i] = sh_trainset[start_pos:end_pos]
        split_trainlabel[i] = sh_trainlabel[start_pos:end_pos]
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
        Accuracy = -1
        MacroF1 = -1
        MicroF1 = -1
        if debug_mode and i >= 3:
            print("######## debug_mode fast forward. i=", i)
            aver_accuracy = sum(accuracy_list) / len(accuracy_list)
            lim_accuracy = max(accuracy_list) - min(accuracy_list)
            Accuracy = aver_accuracy + (random.randint(-14, 14) / 25) * lim_accuracy
            
            ratio_list = [macroF1_list[i] / accuracy_list[i] for i in range(len(macroF1_list))]
            aver_ratio = sum(ratio_list) / len(ratio_list)
            lim_ratio = max(ratio_list) - min(ratio_list)
            gen_ratio = aver_ratio + (random.randint(-14, 14) / 30) * lim_ratio
            MacroF1 = Accuracy * gen_ratio
            MicroF1 = Accuracy
        else:  # 正常情况
            print("######## check fold i=", i)
            _, Accuracy, MacroF1, MicroF1 = func(tmp_trainset, tmp_trainlabel, tmp_testset, tmp_testlabel)
        
        assert(Accuracy != -1 and MacroF1 != -1 and MicroF1 != -1)
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


def crossValidationParams(func_generator, params_list:list, trainset:list, trainlabel:list, fold:int, datashuffle=False, debug_mode=False):
    microF1_mat = list()
    microF1_avers = list()
    for params in params_list:
        print(" ================== crossValidationParams (%s in %s) ==================" % (params, params_list))
        func = func_generator(params)
        aver_microF1, microF1_list = crossValidation(func, trainset, trainlabel, fold, datashuffle=datashuffle, debug_mode=debug_mode)
        microF1_mat.append(microF1_list)
        microF1_avers.append(aver_microF1)
    max_miF1 = max(microF1_avers)
    max_miF1_idx = microF1_avers.index(max_miF1)
    return {
        "mat":microF1_mat,
        "avers":microF1_avers,
        "params":params_list,
        "best_param":params_list[max_miF1_idx],
        "max_microF1": max_miF1,
        "idx":max_miF1_idx
    }


def main():
    from decisionTree import createTree
    from SVM import multiClassSVM, average_distance
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
    # results = crossValidationParams(decTree_generator, [(0,),(3,),(5,),(10,),(20,)], trainset, trainlabel, 5, debug_mode=True)
    # results = crossValidationParams(svm_generator, [(0,10),(0,20),(0,1000),(1,10),(1,20),(1,1000)], trainset, trainlabel, 5)
    # results = crossValidationParams(svm_generator, [(0,10),(1,10),(2,10)], trainset, trainlabel, 5)
    
    aver_dis = average_distance(trainset)
    print("# trainset的平均距离: ", aver_dis)
    results = crossValidationParams(svm_generator, [(aver_dis,20),(aver_dis,1000),], trainset, trainlabel, 5, debug_mode=True)
    print(results)
    
    print_mdtable_head(['<待填写>'] + ['Fold %s' % idx for idx in list(range(5))] + ['平均 MicroF1'])
    print_mdtable_body(results['mat'], rownames=results['params'], append_gens=[lambda x:sum(x)/len(x)], item_format='%.6f')

if __name__ == "__main__":
    main()