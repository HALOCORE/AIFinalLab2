rules = """
classes 类别
predict_label 预测标签列表
evaluate.evaluate 评估
test_elem 测试元素
"""

pcode = """
def knn(trainset:list, trainlabel:list, testset:list, testlabel:list, k:int):
    classes = list(set(trainlabel))
    predict_label = list()
    for test_elem in testset:
        label = knn_core(test_elem, trainset, trainlabel, k)
        predict_label.append(label)
    Accuracy, MacroF1, MicroF1 = evaluate.evaluate(classes, testlabel, predict_label)
    return predict_label, Accuracy, MacroF1, MicroF1
"""


rules = rules.strip()
rules = [x.strip().split(' ') for x in rules.split('\n')]
for key, val in rules:
    pcode = pcode.replace(key, val)

print(pcode)