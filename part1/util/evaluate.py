
def evaluate(classes:list, testlabel:list, predictlabel:list, verbose=False):
    if verbose:
        print("# evaluate (verbose output):")
    assert(len(testlabel) == len(predictlabel))
    test_classes = set(testlabel)
    pred_classes = set(predictlabel)
    for test_class in test_classes:
        assert(test_class in classes)
        # if test_class not in classes:
        #     print("# warning. test_class not in classes.")
    for pred_class in pred_classes:
        assert(pred_class in classes)
    
    class_count = dict()
    notclass_count = dict()
    pred_count = dict()
    notpred_count = dict()
    truepos_count = dict()
    trueneg_count = dict()
    for key in classes:
        class_count[key] = 0
        notclass_count[key] = 0
        pred_count[key] = 0
        notpred_count[key] = 0
        truepos_count[key] = 0
        trueneg_count[key] = 0
    
    for tlab in testlabel:
        class_count[tlab] += 1
        for label in notclass_count:
            if label != tlab:
                notclass_count[label] += 1
        
    for ptab in predictlabel:
        pred_count[ptab] += 1
        for label in notpred_count:
            if label != ptab:
                notpred_count[label] += 1

    for i in range(len(testlabel)):
        if testlabel[i] == predictlabel[i]:
            truepos_count[testlabel[i]] += 1
        for label in trueneg_count:
            if label != predictlabel[i] and label != testlabel[i]:
                trueneg_count[label] += 1
    
    MacroF1 = 0
    
    MicroTP = 0
    MicroRealP = 0
    MicroPredP = 0
    MicroF1 = 0

    for key in classes:
        TP = truepos_count[key]
        RealP = class_count[key]
        PredP = pred_count[key]
        # print("  [%8s] TP:%6d, RealP:%6d, PredP:%6d" % (key, TP, RealP, PredP))
        if TP != 0:
            P = TP / RealP
            R = TP / PredP
            F1 = 2*P*R /(P+R)
        else:
            P = 0
            R = 0
            F1 = 0
        if verbose:
            print("  [%8s] TP:%6d, RealP:%6d, PredP:%6d, P:%5f, R:%5f, F1:%5f" % (key, TP, RealP, PredP, P, R, F1))
        MacroF1 += F1
        
        if RealP > 0: # 计算MicroP, 仅考虑GroundTruth有
            MicroTP += TP
            MicroRealP += RealP
            MicroPredP += PredP
        
    MacroF1 /= len(classes)

    MicroP = MicroTP / MicroRealP
    MicroR = MicroTP / MicroPredP
    MicroF1 = 2 * MicroP * MicroR / (MicroP + MicroR)
    Accuracy = MicroTP / len(testlabel)
    if verbose:
        print("  Accuracy: %f" % (Accuracy))
        print("  MacroF1: %f" % (MacroF1))
        print("  MicroF1: %f" % (MicroF1))
        
    return Accuracy, MacroF1, MicroF1

