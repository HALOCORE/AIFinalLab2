

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

