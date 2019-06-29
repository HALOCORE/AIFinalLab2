import math
from util import evaluate
from util import getdata
from util import gzwrite
import random

def count_dict_max(count_dict:dict):
    """找出最大值
    返回：最大key, 最大值
    """
    maxcount = -1
    maxkey = None
    for key in count_dict:
        if count_dict[key] > maxcount:
            maxcount = count_dict[key]
            maxkey = key
    assert(maxcount >= 0 and maxkey != None)
    return maxkey, maxcount

def count_dict_addto(dst_dict:dict, add_dict:dict):
    """合并计数字典"""
    for key in add_dict:
        if key in dst_dict:
            dst_dict[key] += add_dict[key]
        else:
            dst_dict[key] = add_dict[key]
    


def get_count_dict(mylist: list, tokey=lambda x:x):
    count_dict = dict()
    for elem in mylist:
        key = tokey(elem)
        if key not in count_dict:
            count_dict[key] = 1
        else:
            count_dict[key] += 1
    return count_dict


def get_entropy_from_dict(count_dict:dict):
    total_count = 0
    for key in count_dict:
        total_count += count_dict[key]
    entropy = 0
    for key in count_dict:
        p = count_dict[key] / total_count
        if p != 0:
            entropy += -p*math.log2(p)
    return entropy


def get_cond_entropy(feature_idx, dataset:list, datalabel:list):
    assert(len(dataset) == len(datalabel))
    total_count = len(dataset)
    if feature_idx == -1:
        # return label entropy.
        label_count_dict = get_count_dict(datalabel)
        return get_entropy_from_dict(label_count_dict)
    else:
        label_keys = set(datalabel)
        feature_count_dict = get_count_dict(dataset, tokey=lambda x:x[feature_idx])
        divide_count_dict = dict()
        
        # init a two-level dict.
        for feature_key in feature_count_dict:
            divide_count_dict[feature_key] = dict()
            for label_key in label_keys:
                divide_count_dict[feature_key][label_key] = 0
        # count
        for elem, label in zip(dataset, datalabel):
            divide_count_dict[elem[feature_idx]][label] += 1
        
        # calc cond entropy
        cond_entropy = 0
        for feature_key in divide_count_dict:
            part_entropy = get_entropy_from_dict(divide_count_dict[feature_key])
            cond_entropy += part_entropy * feature_count_dict[feature_key] / total_count

        # return cond entropy (by selected feature)
        return cond_entropy


def chooseBestFeature(dataset:list, datalabel:list):
    """选择最好的特征
    返回：最好的特征编号, 当前信息熵, 最佳特征的信息增益
    """
    feature_count = len(dataset[0])
    current_entropy = get_cond_entropy(-1, dataset, datalabel)
    smallest_entropy = current_entropy
    smallest_idx = -1
    for feature_idx in range(feature_count):
        cond_entropy = get_cond_entropy(feature_idx, dataset, datalabel)
        if cond_entropy < smallest_entropy:
            smallest_idx = feature_idx
            smallest_entropy = cond_entropy
    info_gain = current_entropy - smallest_entropy
    return smallest_idx, current_entropy, info_gain


class DecisionTreeNode:
    def __init__(self, feature_idx, entropy, info_gain, class_default):
        self.entropy = entropy
        self.info_gain = info_gain
        self.feature_idx = feature_idx
        self.class_default = class_default
        # tree_dict里是 {key1:子树, key2:(类别,个数), key3:子树, ...}
        self.tree_dict = dict() 
        # 用于对未知数据预测时，猜测label
        self._label_count = None

    def get_label_count(self):
        if self._label_count == None:
            self._label_count = dict()
            for key in self.tree_dict:
                sub_node = self.tree_dict[key]
                if isinstance(sub_node, DecisionTreeNode):
                    sub_label_count = sub_node.get_label_count()
                    count_dict_addto(self._label_count, sub_label_count)
                else:
                    count_dict_addto(self._label_count, {sub_node[0]:sub_node[1]})
        return self._label_count

    def predict(self, elem):
        feature_key = elem[self.feature_idx]
        if feature_key in self.tree_dict:
            # 这个feature值，在子树字典中存在
            subnode = self.tree_dict[feature_key]
            if isinstance(subnode, DecisionTreeNode):
                return subnode.predict(elem)
            else:
                return subnode[0]
        else:
            return self.class_default

    def accept_treevisitor(self, visitor):
        # 对树进行剪枝
        have_expand = False
        # 随机访问子节点的顺序
        keylist = list(self.tree_dict.keys())
        random.shuffle(keylist)
        for key in keylist:
            subnode = self.tree_dict[key]
            if isinstance(subnode, self.__class__):
                if have_expand is False:
                    have_expand = True
                    subnode.accept_treevisitor(visitor)
                else:
                    visitor.tree_visit(subnode, stoplevel=True)
            else:
                visitor.tree_visit(subnode)
        visitor.tree_visit(self)


class DecisionTreeGZWriter(gzwrite.GzDigraphWriter):
    def __init__(self):
        super().__init__("decisionTree")
    
    def tree_visit(self, node, stoplevel=False):
        node_id = id(node)
        if isinstance(node, DecisionTreeNode):
            self.set_node(node_id, shape='box', label="特征%d\n默认:%s" % (node.feature_idx, node.class_default))
            if stoplevel is False:
                for key in node.tree_dict:
                    subnode = node.tree_dict[key]
                    subnode_id = id(subnode)
                    self.add_edge(node_id, subnode_id, label=chr(key))
            else: # 截停点
                sub_id = node_id + 1
                self.set_node(sub_id, color='gray', label="......", shape='plaintext')
                self.add_edge(node_id, sub_id, color='gray')
        else:
            self.set_node(node_id, shape='box', color="orange", label="类别:%s\n样本数%s" % (node[0], node[1]))
    
    # def tree_visit(self, node, stoplevel=False):
    #     node_id = id(node)
    #     if isinstance(node, DecisionTreeNode):
    #         self.set_node(node_id, label="F%d\n(%s)" % (node.feature_idx, node.class_default))
    #         if stoplevel is False:
    #             for key in node.tree_dict:
    #                 subnode = node.tree_dict[key]
    #                 subnode_id = id(subnode)
    #                 self.add_edge(node_id, subnode_id, label=chr(key))
    #         else: # 截停点
    #             sub_id = node_id + 1
    #             self.set_node(sub_id, color='gray', label="...")
    #             self.add_edge(node_id, sub_id, color='gray')
    #     else:
    #         self.set_node(node_id, color="green",label="%s\n%s" % (node[0], node[1]))


def split_dataset_by_a_feature(dataset:list, datalabel:list, feature_idx:int):
    """通过一个feature的取值来划分dataset
    返回：{key1:dataset1, key2:dataset2, ...}, {key1:label1, key2:label2, ...}
    """
    assert(len(dataset) == len(datalabel))
    dataset_dict = dict()
    datalabel_dict = dict()
    for elem, label in zip(dataset, datalabel):
        feature_key = elem[feature_idx]
        if feature_key not in dataset_dict:
            dataset_dict[feature_key] = list()
            datalabel_dict[feature_key] = list()
        dataset_dict[feature_key].append(elem)
        datalabel_dict[feature_key].append(label)
    return dataset_dict, datalabel_dict


def createTree_core(dataset:list, datalabel:list, filter_size:int):
    """递归建树函数
    返回：数根节点
    """
    bestf_idx, entropy, info_gain = chooseBestFeature(dataset, datalabel)
    count_dict = get_count_dict(datalabel)
    counts = sorted([(count_dict[key], key) for key in count_dict], reverse=True)
    assert(len(counts) > 0)
    assert(counts[0][0] >= counts[-1][0])
    
    class_default = counts[0][1]
    if bestf_idx >= 0 and len(datalabel) > filter_size:
        dataset_dict, datalabel_dict = split_dataset_by_a_feature(dataset, datalabel, bestf_idx)
        current_root = DecisionTreeNode(bestf_idx, entropy, info_gain, class_default)
        for key in dataset_dict:
            sub_dataset = dataset_dict[key]
            sub_datalabel = datalabel_dict[key]
            current_root.tree_dict[key] = createTree_core(sub_dataset, sub_datalabel, filter_size)
        return current_root
    else:
        # 叶节点了
        # assert 检查 是否还有不同元素（如果filter_size>0)
        if not (filter_size > 0 or len(set(datalabel)) == 1):
            print(set(datalabel), "filter_size:", filter_size)
            assert(False)
        leaf_label = datalabel[0]
        if filter_size > 0:
            leaf_label = class_default
        return (leaf_label, len(datalabel))


def createTree(trainset:list, trainlabel:list, testset:list, testlabel:list, filter_size=0, exportfile=False):
    print("# createDecisionTree. trainsize:%d, testsize:%d." % (len(trainset), len(testset)))
    assert(len(trainset) == len(trainlabel))
    des_tree = createTree_core(trainset, trainlabel, filter_size)
    if exportfile: # 导出决策树
        export_tree(des_tree)
    assert(len(testset) == len(testlabel))
    predict_label = list()
    # predict test elems
    for elem in testset:
        predict_label.append(des_tree.predict(elem))
    # evaluate
    classes = list(set(trainlabel))
    Accuracy, MacroF1, MicroF1 = evaluate.evaluate(classes, testlabel, predict_label, verbose=True)
    return predict_label, Accuracy, MacroF1, MicroF1


def export_tree(tree:DecisionTreeNode):
    """输出一个树"""
    writer = DecisionTreeGZWriter()
    tree.accept_treevisitor(writer)
    with open('_decisionTree_Visualize.dot', 'w') as f:
        f.write('\n'.join(writer.get_codes()))


# ------------------------------- 测试程序 -------------------------------
def test_entropy():
    # test1
    cdict = {"a":9, "b":5}
    ans = get_entropy_from_dict(cdict)
    print(ans)
    assert((ans - 0.940286) < 1e-5)
    
    # test2
    dataset = [
        ("SUNNY"   ,),("SUNNY"   ,),("OVERCAST",),("RAIN"    ,),("RAIN"    ,),("RAIN"    ,),("OVERCAST",),
        ("SUNNY"   ,),("SUNNY"   ,),("RAIN"    ,),("SUNNY"   ,),("OVERCAST",),("OVERCAST",),("RAIN"    ,)]
    labelset = [0,0,1,1,1,0,1, 0,1,1,1,1,1,0]
    ans = get_cond_entropy(0, dataset, labelset)
    print(ans)
    assert((ans - 0.693536) < 1e-5)

    # test3
    a = {'A':2, 'B':4, 'E':5}
    b = {'B':4, 'D':3}
    count_dict_addto(a, b)
    print(a)
    print(b)


def main():
    trainset, trainlabel = getdata.get_traindata()
    testset, testlabel = getdata.get_testdata()
    ypred, Accuracy, MacroF1, MicroF1 = createTree(trainset, trainlabel, testset, testlabel, filter_size=0, exportfile=True)
    print(Accuracy, MacroF1, MicroF1)

do_test = False
if __name__ == "__main__":
    if do_test:
        test_entropy()
    else:
        print("# decisionTree. ")
        main()


