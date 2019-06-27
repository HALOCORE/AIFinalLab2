# 人工智能 Lab2-Part1 实验报告
> 实验题目：国际象棋Checkmate预测  
> 姓名：王博， 学号：PB16020870

## 1. 实验要求

### 1.1 数据集介绍
- Krkopt是一个国际象棋的残局数据集，在这张残局的棋盘上，只有白手国王（White King）、白手车（White Rook）、黑手国王（Black King）。本次实验的任务是在给定前面所述的三者的位置的前提下，预测白手玩家能将军所需要的最少步数（这里假设两个玩家的每步走法都是最优的）。
- 数据中包含7个属性（含类别），共有28056个样本，数据属性（含类别）如下所述：
  1. 白手国王的列坐标（White King Column）
  2. 白手国王的行坐标（White King Row）
  3. 白手车的行坐标（White Rook Column）
  4. 白手车的列坐标（White Rook Row）
  5. 黑手国王的行坐标（Black King Column）
  6. 黑手国王的列坐标（Black King Row）
- 类别：最优步数（optimal depth-of-win），从0~16取值，若无法取胜，则为draw，具体分布如下图所示

### 1.2 实现算法的要求
- 提交一个KNN.py文件，要求通过K近邻算法来解决多分类的问题。
- 提交一个decisionTree.py文件，要求调研决策树算法（ID3）并实现来解决多分类的问题。
- 提交一个SVM.py文件，要求通过多分类SVM算法来解决多分类的问题。
- 详细要求略。

### 1.3 评估要求
- 每个文件的核心函数都要返回对测试数据testset的预测ypred，以及与testlabel进行比较后计算得到的性能指标Accuracy、Macro F1和Micro F1。
- 详细要求略。

### 1.4 交叉验证/参数选择要求
- 在数据集上使用交叉验证法来进行训练集和验证集的划分及训练（使用5-fold交叉验证），同时为每个算法挑选合适的参数。
- 详细要求略。

### 1.5 提交报告要求

1. 给出你对各个属性间关系进行处理的思路（若是直接进行训练，可以不写）；
2. 分别给出算法的伪代码；
3. 根据评价指标，给出模型评估结果，要求给出对应的图表分析。

## 2. 算法实现

### 2.1 K近邻算法实现

实现K近邻算法需要实现如下函数。伪代码如下：
- KNN主函数：
```python
def knn(trainset:list, trainlabel:list, testset:list, testlabel:list, k:int):
    类别 = 对trainlabel去重
    预测标签列表 = list()
    for 测试元素 in testset:
        预测类别 = knn_core(测试元素, trainset, trainlabel, k)
        预测标签列表.append(预测类别)
    Accuracy, MacroF1, MicroF1 = 评估(类别, testlabel, 预测标签列表)
    return 预测标签列表, Accuracy, MacroF1, MicroF1
```

- KNN处理单个元素的函数：
```python
def knn_core(当前待处理元素, trainset:list, trainlabel:list, nb_num:int, debug=False):
    """knn算法"""
    创建邻居列表
    for 元素, 标签 in zip(trainset, trainlabel):
        更新邻居列表(当前待处理元素, 元素, 标签, 邻居列表, 邻居个数)
    预测结果 = 根据邻居列表判断最多类别(邻居列表)
    return 预测结果
```

- 更新邻居列表：
```python
def update_neighbors(中心元素, 元素, 标签, 邻居列表: list, 邻居个数限制: int):
    """更新邻居, 插入排序实现"""
    # 邻居按照小根堆堆排列。序为到中心元素的距离
    将新元素放在尾部
    调整小根堆
    if 堆元素超过邻居个数:
        移除堆尾部1个元素
```

### 2.2 决策树ID3算法实现

实现决策树ID3需要实现如下函数。伪代码如下：

- 决策树核心函数：
```python
def createTree(trainset:list, trainlabel:list, testset:list, testlabel:list):
    决策树 = 创建决策树(trainset, trainlabel)
    创建预测标签列表
    for 元素 in testset:
        预测标签列表.append(决策树.预测(元素))
    Accuracy, MacroF1, MicroF1 = 评估(训练集所有类别, testlabel, 预测标签列表)
    return predict_label, Accuracy, MacroF1, MicroF1
```

- 决策树生成函数：
```python
def createTree_core(dataset:list, datalabel:list):
    """递归建树函数
    返回：数根节点
    """
    最佳特征, 信息熵, 信息增益 = chooseBestFeature(dataset, datalabel)
    if 最佳特征存在:
        特征取值到数据集合映射 = 根据一个特征分割数据集(dataset, datalabel, 最佳特征)
        当前节点 = 创建决策树节点(最佳特征, 信息熵, 信息增益)
        for 特征取值 → (数据集合，标签集合) in 特征取值到数据集合映射:
            当前节点.该特征取值的孩子 = createTree_core(数据集合，标签集合)
        return 当前节点
    else:
        # 叶节点
        叶节点标签 = 当前数据集合的公共标签
        return (叶节点, 数据元素个数)
```

- 信息熵和条件熵的计算略，理论来自老师PPT:
  ![信息熵计算]()

- 选择最佳特征函数：
```python
def chooseBestFeature(dataset:list, datalabel:list):
    """选择最好的特征
    返回：最好的特征, 当前信息熵, 最佳特征的信息增益
    """
    当前信息熵 = 计算信息熵(dataset, datalabel)
    最低信息熵 = current_entropy
    最佳特征 = None
    for 特征 in 特征列表:
        条件熵 = 计算条件熵(特征, dataset, datalabel)
        更新最低熵和最佳特征(条件熵)
    信息增益 = 当前信息熵 - 最低信息熵
    return 最佳特征，当前信息熵，最佳特征的信息增益
```

- 决策树的预测方法：
```python
class DecisionTreeNode:
    ...
    def 预测(self, 元素):
        特征取值 = 元素[self.特征]
        if 特征取值 in self.tree_dict:
            # 这个feature值，在子树字典中存在
            子节点 = self.子节点映射(特征取值)
            if 子节点的类型是 DecisionTreeNode:
                return 子节点.预测(元素)
            else:
                return 本节点预测值
        else:
            # TODO:
    ...
```


### 2.3 多分类SVM实现

实现多分类SVM需要实现如下函数。伪代码如下：


- 多分类核心函数：
```python
def multiClassSVM(trainset, trainlabel, testset, testlabel, sigma=1, marginC=10):
    # trainset, trainlabel, testset, testlabel 是训练集和测试集
    # sigma=1 是默认的高斯核函数sigma值
    # marginC=10 是默认的软边界参数
    创建类别到SVM的映射
    for 目标类别 in 所有类别:
        myfilter = 
        过滤后标签列表 = 对于每个标签按照标签是否等于目标类别来置位 1 或 -1
        类别到SVM的映射[目标类别] = softSVM(trainset, 过滤后标签列表, sigma, marginC)
    
    # 做预测
    预测标签 = 列表()
    for 元素 in 测试集:
        for 类别 in 类别到SVM的映射:
            预测y值 = 类别到SVM的映射[类别].predict(元素)
            if 预测y值 > 最佳预测y值:
                最佳预测y值 = 预测y值
                猜测的类别 = 类别
        预测标签.append(猜测的类别)
    
    # 评估
    Accuracy, MacroF1, MicroF1 = 评估(所有类别, 测试标签, 预测标签)
    return 预测标签, Accuracy, MacroF1, MicroF1
```

- 核函数
```python
def svm_kernel(x1, x2, sigma):
    if sigma = 0: 返回线性核函数求值
    else 带入sigma返回高斯核函数求值
```

- 软间隔SVM生成
```python

def softSVM(trainset, trainlabel, sigma, marginC):
    """marginC为soft margin控制参数"""
    所有alpha = 求解所有向量alpha(trainset, trainlabel, sigma, marginC)
    创建一个SVM对象
    alpha阈值 = 6e-5
    将所有alpha超过阈值的向量加入支持向量列表
    找出最大alpha，最大alpha对应向量
    SVM的b = SUM(最大alpha的y值 - 所有向量与最大alpha支持向量核函数值)
    return 新建的SVM
```

- 求解所有向量的alpha
  - 本部分理论基础是老师的PPT:
  ![ppt](pics/svmth.png)
  - 本部分的实现需要如下依赖：
    - 使用了python的qpsolvers库来求解二次规划问题
    - 使用的二次规划求解器是osqp，其可以处理稀疏矩阵。
    - 使用的稀疏矩阵形式是scipy.sparse中的csc_matrix。
    - 私用的矩阵运算库是numpy。
  - qpsolvers要求的输入格式为：
  ```python
    def solve_qp(P, q, G=None, h=None, A=None, b=None, solver='quadprog',
             initvals=None, sym_proj=False):
    """
    Solve a Quadratic Program defined as:

        minimize
            (1/2) * x.T * P * x + q.T * x

        subject to
            G * x <= h
            A * x == b

    using one of the available QP solvers.
    ...

  ```
- 伪代码如下：
```python
def solve_sparse(trainset, trainlabel, sigma, marginC):
    train_size = len(trainset)
    K = 长宽为元素个数的核函数矩阵
    在K的对角线增加一个小量1e-5

    q = 长度为元素个数的全部由 -1 组成的向量
    
    G1 = 稀疏矩阵(长宽为元素个数的单位对角阵)
    G2 = 稀疏矩阵(长宽为元素个数的负单位对角阵)
    G = 纵向拼接G1, G2

    h1 = 长度为元素个数的全为marginC的向量
    h2 = 长度为元素个数的全为0的向量
    h = 纵向拼接h1和h2

    A = 稀疏矩阵(训练标签) 
    b = np.asarray([0])
    
    所有alpha求解结果 = 求解二次规划(目标函数(K, q), 小于约束(G, h), 等于约束(A, b), 求解器='osqp')
    return 所有alpha求解结果
```


### 3.1 评估算法实现

## 3. K折交叉验证

### 3.1 K折交叉验证算法实现

### 3.2 K近邻算法：5折交叉验证

### 3.3 决策树ID3算法：5折交叉验证

### 3.4 SVM算法：5折交叉验证
