import math
import time
import numpy as np

from typing import List

import scipy.sparse
from scipy.sparse import csc_matrix, coo_matrix

from qpsolvers import sparse_solvers
from qpsolvers import solve_qp

from util import getdata
from util import evaluate


def multiClassSVM(trainset, trainlabel, testset, testlabel, sigma=1, marginC=10, verbose=False):
    # trainset, trainlabel, testset, testlabel 是训练集和测试集
    # sigma=1 是默认的高斯核函数sigma值
    # marginC=10 是默认的软边界参数
    time_start = time.time()
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
        print(svm_dict[focus_class])

    # do predict
    print("# start predict. %d testcases total ..." % len(testset))
    predict_label = list()
    predict_counter = 0
    for elem in testset:
        best_class = None
        best_score = -100000 # magic
        for class_key in svm_dict:
            score = svm_dict[class_key].predict(elem)
            if score > best_score:
                best_score = score
                best_class = class_key
        assert(best_class != None)
        predict_counter += 1
        if predict_counter % 100 == 0:
            print("# predicting: ", len(predict_label))
        predict_label.append(best_class)
    
    # evaluate
    Accuracy, MacroF1, MicroF1 = evaluate.evaluate(classes, testlabel, predict_label, verbose=verbose)
    time_end = time.time()
    print("# multiClassSVM 用时:", time_end - time_start)
    return predict_label, Accuracy, MacroF1, MicroF1


def svm_kernel(x1:List[float], x2:List[float], sigma:float):
    if sigma == 0:
        return svm_linear_kernel(x1, x2)
    else:
        return svm_gauss_kernel(x1, x2, sigma)

def svm_linear_kernel(x1:List[float], x2:List[float]):
    # 线性核函数
    inner_product = 0
    for s1, s2 in zip(x1, x2):
        inner_product += s1 * s2
    return inner_product

def svm_gauss_kernel(x1:List[float], x2:List[float], sigma:float):
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
        vecsize = len(vecs)
        if vecsize > 5:
            vecs = vecs[:5]
            vecs.append('    ... (%d vectors hidden.)' % (vecsize - 5))
        tail = "\n</SVM vec-num:%d >" % len(self.alphas)
        return head + "\n".join(vecs) + tail


MATRIX_GEN_OPTIMIZE = False

def solve_sparse(trainset:List[List[float]], trainlabel:list, sigma:float, marginC:float, verbose=False):
    time_start = time.time()
    print("# solve_sparse. OPTIMIZE = %s" % MATRIX_GEN_OPTIMIZE)
    
    train_size = len(trainset)
    if MATRIX_GEN_OPTIMIZE:
        np_trainset1 = np.asarray(trainset)
        np_trainset2 = np.asarray(trainset)
        if sigma == 0:
            K = np.matmul(np_trainset1, np_trainset2.T)
        else:
            vecminus = np_trainset1[:,None] - np_trainset2[None,:]
            raise NotImplementedError
    else:
        if sigma > 0:
            K = [[svm_gauss_kernel(x1, x2, sigma) for x1 in trainset] for x2 in trainset]
        else:
            K = [[svm_linear_kernel(x1, x2) for x1 in trainset] for x2 in trainset]

    # no need to optimize this.
    nd_K = np.asarray(K, dtype=np.float)

    Y = np.asarray([trainlabel], dtype=np.float)
    YY = np.matmul(Y.T, Y)
    P = K * YY
    if sigma > 0:
        P = P + np.diag([1e-6]*len(trainset))
    
    P = csc_matrix(P)

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
    
    time_end = time.time()
    print("    | 用时 %s." % (time_end - time_start))
    print("# start solve... ")
    time_start = time.time()
    
    if 'osqp' not in sparse_solvers:
        print("# 不存在稀疏QP求解器。可安装osqp:  pip3 install osqp")
        assert(False)
    alpha_ans = solve_qp(P, q, G, h, A, b, solver='osqp')
    
    time_end = time.time()
    print("    | 用时 %s." % (time_end - time_start))
    return alpha_ans


def solve_dense(trainset:List[List[float]], trainlabel:list, sigma:float, marginC:float, verbose=False):
    time_start = time.time()
    print("# prepare dense... ")
    K = [[svm_kernel(x1, x2, sigma) for x1 in trainset] for x2 in trainset]
    nd_K = np.asarray(K, dtype=np.float)

    Y = np.asarray([trainlabel], dtype=np.float)
    YY = np.matmul(Y.T, Y)
    P = K * YY
    P = P + np.diag([1e-6]*len(trainset))

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
    
    time_end = time.time()
    print("    | 用时:", time_end - time_start)
    time_start = time.time()
    print("# solve dense... ")

    alpha_ans = solve_qp(P, q, G, h, A, b)

    time_end = time.time()
    print("    | 用时 %s." % (time_end - time_start))
    return alpha_ans

USE_SPARSE = True
AVER_B_SIZE = 10
def softSVM(trainset:List[List[float]], trainlabel:list, sigma:float, marginC:float, verbose=False):
    """C为soft margin控制参数"""
    alpha_ans = None
    if USE_SPARSE:
        alpha_ans = solve_sparse(trainset, trainlabel, sigma, marginC, verbose)
    else:
        alpha_ans = solve_dense(trainset, trainlabel, sigma, marginC, verbose)
    assert(alpha_ans is not None)

    if verbose:
        print("-----------------------")
        print("alphas:\n", alpha_ans)

    newSVM = SVM(sigma)
    ans_len = len(alpha_ans)
    ori_max_alpha = max(alpha_ans)
    threshold = ori_max_alpha * 0.005

    # 找最好 alpha
    max_alpha = 0
    max_alpha_idx = None
    for i in range(ans_len):
        if alpha_ans[i] > threshold:
            newSVM.add_support_vec(trainset[i], trainlabel[i], alpha_ans[i])
            if alpha_ans[i] > max_alpha:
                max_alpha = alpha_ans[i]
                max_alpha_idx = i
    
    # 求b列表
    b_list = list()
    for i in range(ans_len):
        if alpha_ans[i] > threshold and len(b_list) < AVER_B_SIZE:
            b_list.append(trainlabel[i] - newSVM.w_multi(trainset[i]))
    
    # 求b平均
    best_b = trainlabel[max_alpha_idx] - newSVM.w_multi(trainset[max_alpha_idx])
    aver_b = sum(b_list) / len(b_list)
    print("creating softSVM. best_b:", best_b, "  aver_b(%d):" % (AVER_B_SIZE), aver_b)# "  b_list:%s" % b_list)
    newSVM.set_b(best_b)
    return newSVM


def average_distance(trainset:List[List[float]]):
    dis = 0
    for e1 in trainset:
        for e2 in trainset:
            edsq = sum([(x1 - x2)*(x1 - x2) for x1, x2 in zip(e1, e2)])
            dis += edsq
    return dis / (len(trainset) * len(trainset))


# ----------------------------------------- 测试 -----------------------------------------
# minimize
#     (1/2) \* x.T \* P \* x + q.T \* x

# subject to
#     G \* x <= h   # 加每个alpha小于1的条件
                    # 加每个alpha大于0的条件
#     A \* x == b


def test_svm():
    # labeler = lambda x,y: 3*x - y - 1
    labeler = lambda x,y: 2*x + 3*y - 7
    trainset = list()
    trainlabel = list()
    testset = list()
    testlabel = list()

    scale = 100 
    factor = 1/10 
    thres = 2 # 间隔
    fillgap = False # 是否填充间隙
    import random
    for _ in range(500):
        x = random.randint(-scale, scale) * factor
        y = random.randint(-scale, scale) * factor
        
        if labeler(x,y) > thres:
            trainset.append((x, y))
            trainlabel.append(1)
        elif labeler(x,y) < -thres:
            trainset.append((x, y))
            trainlabel.append(-1)
        else:
            if fillgap:
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

    aver_dis = average_distance(trainset)
    print("# 平均距离:", aver_dis)
    mySVM = softSVM(trainset, trainlabel, aver_dis, 8)

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
    support_vecs = mySVM.sp_vectors

    # 数据点
    tsetx = [x[0] for x in trainset]
    tsety = [x[1] for x in trainset]
    plt.scatter(tsetx, tsety, c=trainlabel)
    
    # 支持向量
    spx = [x[0] for x in support_vecs]
    spy = [x[1] for x in support_vecs]
    max_alpha = max(mySVM.alphas)
    sizes = [300*x/max_alpha for x in mySVM.alphas]
    plt.scatter(spx, spy, color='', marker='o', alpha=0.8,s=sizes, edgecolors='g')
    # plt.scatter(spx, spy, color='', marker='o', edgecolors='g',s=300)

    #显示
    plt.show()


# ----------------------------------------- 主函数 -----------------------------------------
def main(sigma=1.3, marginC=10):
    print("# SVM.")
    trainset, trainlabel = getdata.get_traindata()
    testset, testlabel = getdata.get_testdata()
    ypred, Accuracy, MacroF1, MicroF1 = multiClassSVM(
        trainset, trainlabel, testset, testlabel, 
        sigma=sigma, marginC=marginC, verbose=True)

    print(Accuracy, MacroF1, MicroF1)


do_test = False
if __name__ == "__main__":
    if do_test:
        test_svm()
    else:
        sigma = 1.3
        import sys
        if len(sys.argv) >= 2:
            print("# 使用自定义sigma. ")
            print(sys.argv)
            sigma = float(sys.argv[-1])
        main(sigma=sigma)
