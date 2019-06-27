import math
import numpy as np


import scipy.sparse
from scipy.sparse import csc_matrix, coo_matrix

from qpsolvers import sparse_solvers
from qpsolvers import solve_qp

from util import getdata
from util import evaluate


def multiClassSVM(trainset, trainlabel, testset, testlabel, sigma=1, marginC=10):
    # trainset, trainlabel, testset, testlabel 是训练集和测试集
    # sigma=1 是默认的高斯核函数sigma值
    # marginC=10 是默认的软边界参数
    assert(len(trainset) == len(trainlabel))
    assert(len(testset) == len(testlabel))
    classes = set(trainlabel)
    
    # fenerate svm
    svm_dict = dict()
    for focus_class in classes:
        myfilter = lambda elem: 1 if elem == focus_class else -1
        tr_trainlabel = [myfilter(x) for x in trainlabel]
        print("# start building SVM for %s..." % focus_class)
        svm_dict[focus_class] = softSVM(trainset, tr_trainlabel, sigma, marginC)
    
    # do predict
    print("# start predict. %d testcases total ..." % len(testset))
    predict_label = list()
    for elem in testset:
        best_class = None
        best_score = -100000 # magic
        for class_key in svm_dict:
            score = svm_dict[class_key].predict(elem)
            if score > best_score:
                best_score = score
                best_class = class_key
        assert(best_class != None)
        predict_label.append(best_class)
    
    # evaluate
    Accuracy, MacroF1, MicroF1 = evaluate.evaluate(classes, testlabel, predict_label)
    return predict_label, Accuracy, MacroF1, MicroF1


def svm_kernel(x1, x2, sigma):
    if sigma == 0:
        # 线性核函数
        inner_product = 0
        for s1, s2 in zip(x1, x2):
            inner_product += s1 * s2
        return inner_product
    else:
        # 高斯核函数
        invsq_sig = 1.0 / (sigma * sigma)
        vecmod2 = 0
        for s1, s2 in zip(x1, x2):
            vecmod2 += (s2 - s1)*(s2 - s1)
        inner_product = math.exp(-vecmod2 * invsq_sig)
        return inner_product


class SVM():
    def __init__(self, sigma:float, describe="not available"):
        self.describe = describe
        self.alphas = list()
        self.ys = list()
        self.sp_vectors = list()
        self.sigma = sigma
        self.b = None

    def add_support_vec(self, vec, y:float, alpha:float):
        self.sp_vectors.append(vec)
        self.ys.append(y)
        self.alphas.append(alpha)

    def set_b(self, b:float):
        self.b = b

    def predict(self, elem):
        assert(self.b != None)
        return self.w_multi(elem) + self.b

    def w_multi(self, elem):
        assert(len(self.alphas) == len(self.ys))
        assert(len(self.ys) == len(self.sp_vectors))
        wmult = 0
        for i in range(len(self.alphas)):
            inner_product = svm_kernel(elem, self.sp_vectors[i], self.sigma)
            wmult += self.alphas[i] * self.ys[i] * inner_product
        return wmult

    def __repr__(self):
        cst_sum = sum([self.alphas[i] * self.ys[i] for i in range(len(self.alphas))])
        head = "<SVM  sigma:%s, marginC:%s, CST-SUM: ** %4f ** >\n" % (self.sigma, "unknown", cst_sum)
        vecs = ["    alpha:%s, label:%s, vec:%s" % (self.alphas[i], self.ys[i], self.sp_vectors[i]) for i in range(len(self.alphas))]
        
        tail = "\n</SVM vec-num:%d >" % len(self.alphas)
        return head + "\n".join(vecs) + tail


def solve_sparse(trainset, trainlabel, sigma, marginC, verbose=False):
    train_size = len(trainset)
    K = [[svm_kernel(trainset[i1], trainset[i2], sigma)*trainlabel[i1]*trainlabel[i2]
            for i1 in range(train_size)]
         for i2 in range(train_size)]
    for i in range(train_size):
        K[i][i] += 1e-5
    P = csc_matrix(K)

    elem_count = len(trainset)
    q = - np.ones(elem_count)
    
    G1 = csc_matrix(scipy.sparse.eye(elem_count))
    G2 = csc_matrix(-scipy.sparse.eye(elem_count))
    G = scipy.sparse.vstack((G1, G2))

    h1 = np.ones(elem_count) * marginC
    h2 = np.zeros(elem_count)
    h = np.concatenate((h1, h2), axis=0)

    A = csc_matrix(trainlabel) 
    b = np.asarray([0])
    
    if verbose:
        print("-----------------------")
        print("P:\n", P)
        print("q:\n", q)

        print("-----------------------")
        print("G:\n", G)
        print("h:\n", h)

        print("-----------------------")
        print("A:\n", A)
        print("b:\n", b)
    
    print("# start solve... ")
    if 'osqp' not in sparse_solvers:
        print("# 不存在稀疏QP求解器。可安装osqp:  pip3 install osqp")
        assert(False)
    alpha_ans = solve_qp(P, q, G, h, A, b, solver='osqp')
    return alpha_ans


def solve_dense(trainset, trainlabel, sigma, marginC, verbose=False):
    K = [[svm_kernel(x1, x2, sigma) for x1 in trainset] for x2 in trainset]
    nd_K = np.asarray(K, dtype=np.float)

    Y = np.asarray([trainlabel], dtype=np.float)
    YY = np.matmul(Y.T, Y)
    P = K * YY
    P = P + np.diag([1e-5]*len(trainset))

    elem_count = len(trainset)
    q = - np.ones(elem_count)

    G1 = np.eye(elem_count)
    G2 = - np.eye(elem_count)
    h1 = np.ones(elem_count) * marginC
    h2 = np.zeros(elem_count)
    G = np.concatenate((G1, G2), axis=0)
    h = np.concatenate((h1, h2), axis=0)

    A = Y 
    b = 0
    
    if verbose:
        print("-----------------------")
        print("P:\n", P)
        print("q:\n", q)

        print("-----------------------")
        print("G:\n", G)
        print("h:\n", h)

        print("-----------------------")
        print("A:\n", A)
        print("b:\n", b)
    
    print("# start solve... ")
    alpha_ans = solve_qp(P, q, G, h, A, b)
    return alpha_ans


def softSVM(trainset, trainlabel, sigma, marginC, verbose=False):
    """C为soft margin控制参数"""
    alpha_ans = solve_sparse(trainset, trainlabel, sigma, marginC, verbose)
    
    if verbose:
        print("-----------------------")
        print("alphas:\n", alpha_ans)

    newSVM = SVM(sigma)
    ans_len = len(alpha_ans)
    threshold = 6e-5

    max_alpha = 0
    max_alpha_idx = None
    for i in range(ans_len):
        if alpha_ans[i] > threshold:
            newSVM.add_support_vec(trainset[i], trainlabel[i], alpha_ans[i])
            if alpha_ans[i] > max_alpha:
                max_alpha = alpha_ans[i]
                max_alpha_idx = i

    b = trainlabel[max_alpha_idx] - newSVM.w_multi(trainset[max_alpha_idx])
    newSVM.set_b(b)
    
    return newSVM


# ----------------------------------------- 测试 -----------------------------------------
# minimize
#     (1/2) \* x.T \* P \* x + q.T \* x

# subject to
#     G \* x <= h   # 加每个alpha小于1的条件
                    # 加每个alpha大于0的条件
#     A \* x == b


def test_svm():
    labeler = lambda x,y: 1*x + 3*y + 6
    trainset = list()
    trainlabel = list()
    testset = list()
    testlabel = list()

    scale = 100
    factor = 1/10
    thres = 0
    import random
    for _ in range(300):
        x = random.randint(-scale, scale) * factor
        y = random.randint(-scale, scale) * factor
        
        if labeler(x,y) > thres:
            trainset.append((x, y))
            trainlabel.append(1)
        elif labeler(x,y) < -thres:
            trainset.append((x, y))
            trainlabel.append(-1)
        else:
            trainset.append((x, y))
            des = random.randint(0, 1)
            if des == 1:
                trainlabel.append(1)
            else:
                trainlabel.append(-1)

    
    for _ in range(100):
        x = random.randint(-scale, scale) * factor
        y = random.randint(-scale, scale) * factor
        testset.append((x, y))
        if labeler(x,y) > 0:
            testlabel.append(1)
        else:
            testlabel.append(-1)
    
    # trainset = [(1,1),(2,4), (1,1.5), (1,2), (2,3), (3,4), (5,1), (7,2),(7, 5), (5,3), (7,3),(4,3)]
    # trainlabel = [1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1]


    mySVM = softSVM(trainset, trainlabel, 2, 20)

    true_count = 0
    false_count = 0
    for elem, label in zip(testset, testlabel):
        predlabel = mySVM.predict(elem)
        # print("pred:%s, real:%s, check:%s" % (predlabel, label, predlabel * label > 0))
        if predlabel * label > 0:
            true_count += 1
        else:
            false_count += 1
    print(mySVM)
    print("\nTrue:", true_count, " False:", false_count)

    import matplotlib.pyplot as plt
    tsetx = [x[0] for x in trainset]
    tsety = [x[1] for x in trainset]
    plt.scatter(tsetx, tsety, c=trainlabel)
    plt.show()


# ----------------------------------------- 主函数 -----------------------------------------
def main():
    print("# SVM.")
    trainset, trainlabel = getdata.get_traindata()
    testset, testlabel = getdata.get_testdata()
    ypred, Accuracy, MacroF1, MicroF1 = multiClassSVM(trainset, trainlabel, testset, testlabel)
    print(Accuracy, MacroF1, MicroF1)


do_test = False
if __name__ == "__main__":
    if do_test:
        test_svm()
    else:
        main()
