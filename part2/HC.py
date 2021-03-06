
def elem_dis_mh(e1, e2):
    dis = 0
    for e1i, e2i in zip(e1, e2):
        dis += abs(e1i - e2i)
    return dis

def elem_dis_euler(e1, e2):
    dis = 0
    for e1i, e2i in zip(e1, e2):
        dis += (e1i - e2i) * (e1i - e2i)
    return dis

def clus_dis_averdis(clus1_ids:list, clus2_ids:list, elem_dis, elem_mapper):
    min_dis = elem_dis(elem_mapper(clus1_ids[0]), elem_mapper(clus2_ids[0]))
    sum_e1 = [0 for _ in range(len(elem_mapper(clus1_ids[0])))]
    sum_e2 = [0 for _ in range(len(elem_mapper(clus2_ids[0])))]
    for c1_id in clus1_ids:
        e1 = elem_mapper(c1_id)
        for i in range(len(e1)):
            sum_e1[i] += e1[i]

    for c2_id in clus2_ids:
        e2 = elem_mapper(c2_id)
        for i in range(len(e2)):
            sum_e2[i] += e2[i]

    for i in range(len(sum_e1)):
        sum_e1[i] /= len(clus1_ids)
    for i in range(len(sum_e2)):
        sum_e2[i] /= len(clus2_ids)
    return elem_dis_mh(sum_e1, sum_e2)


def clus_dis_maxdis(clus1_ids:list, clus2_ids:list, elem_dis, elem_mapper):
    max_dis = elem_dis(elem_mapper(clus1_ids[0]), elem_mapper(clus2_ids[0]))
    for c1_id in clus1_ids:
        for c2_id in clus2_ids:
            e1 = elem_mapper(c1_id)
            e2 = elem_mapper(c2_id)
            current_dis = elem_dis(e1, e2)
            if current_dis > max_dis:
                max_dis = current_dis
    return max_dis


def clus_dis_mindis(clus1_ids:list, clus2_ids:list, elem_dis, elem_mapper):
    min_dis = elem_dis(elem_mapper(clus1_ids[0]), elem_mapper(clus2_ids[0]))
    for c1_id in clus1_ids:
        for c2_id in clus2_ids:
            e1 = elem_mapper(c1_id)
            e2 = elem_mapper(c2_id)
            current_dis = elem_dis(e1, e2)
            if current_dis < min_dis:
                min_dis = current_dis
    return min_dis

from util.evaluate import calc_SSE

def HC(data, n_clusters, cluster_ratio=0.95):
    """增加了第三个默认参数，用于防止离群点干扰。
    当前4大的cluster加起来占比超过cluster_ratio，第一阶段结束。然后对于剩下的点，就近分配。"""
    datalen = len(data)
    print("# HC 初始化. datasize=", datalen, " n_clusters=", n_clusters, "  ratio=", cluster_ratio)
    
    # 每个数据元素所属的cluster编号 
    idx_list = list(range(datalen))
    
    # 每个cluster含有的数据元素编号
    cluster_dict = {i:[i,] for i in range(datalen)}

    # 距离计算函数
    def calc_distance(idx1, idx2):
        return clus_dis_averdis(
            cluster_dict[idx1], cluster_dict[idx2],
            elem_dis=elem_dis_mh, # 选择元素距离函数
            elem_mapper=lambda id: data[id])
    
    # 不同cluster对之间的距离
    dis_dict = {i:{j:calc_distance(i, j) for j in range(datalen) if j != i} for i in range(datalen)}
    
    # 合并两个cluster
    def combine_cluster(idx1:int, idx2:int):
        # 更新idx_list
        for elem_id in cluster_dict[idx2]:
            idx_list[elem_id] = idx1
        # 合并cluster
        cluster_dict[idx1].extend(cluster_dict[idx2])
        # 删掉第二个cluster
        del cluster_dict[idx2]
        # 更新距离字典
        del dis_dict[idx2]
        for cidx in dis_dict:
            del dis_dict[cidx][idx2]
        for cidx in dis_dict:
            if cidx != idx1:
                dis_dict[cidx][idx1] = calc_distance(idx1, cidx)
                dis_dict[idx1][cidx] = dis_dict[cidx][idx1]

    # 获取距离最近的cluster对
    def get_nearest_cluster_idx():
        """返回：最近两个cluster的编号，以及cluster距离"""
        best_cid1 = -1
        best_cid2 = -1
        best_dis = 10000000 # magic
        for src in dis_dict:
            for target in dis_dict:
                if src != target:
                    if dis_dict[src][target] < best_dis:
                        best_dis = dis_dict[src][target]
                        best_cid1 = src
                        best_cid2 = target
        return best_cid1, best_cid2, best_dis

    print("# HC 开始合并.")

    # 第一阶段：合并簇，使得最大的n个簇总元素个数超过指定比例
    biggest_total = 0
    biggest_ratio = 0
    
    # 本阶段的图表统计信息
    sse_list = list()

    while len(cluster_dict) > n_clusters and biggest_ratio < cluster_ratio: # 引入最大n个占比控制

        # 添加步骤：统计各个cluster含有的元素个数，排序
        cluster_size_list = sorted([(len(cluster_dict[k]), k) for k in cluster_dict], reverse=True)
        
        # 添加步骤：找出最大n_cluster个看占比
        biggest_clusters = cluster_size_list[:n_clusters]
        biggest_total = sum([tp[0] for tp in biggest_clusters])
        biggest_ratio = biggest_total / datalen

        # 计算SSE
        sse = calc_SSE(data, idx_list)
        sse_list.append(sse)

        # 添加步骤：调试
        print("ratio: %5f" % biggest_ratio, "  target_ratio: %5f" % cluster_ratio, 
            "  cluster-count: %4d  " % len(cluster_dict), "  SSE: %5f |  " % sse,
            biggest_clusters)

        cid1, cid2, _ =  get_nearest_cluster_idx()
        combine_cluster(cid1, cid2)

    # 第二阶段：就近指派离群簇 （不再保证数据结构一致性。直接修改idx_list元素归属簇列表）
    if len(cluster_dict) > n_clusters:
        print("# 就近指派离群点.")
        cluster_size_list = sorted([(len(cluster_dict[k]), k) for k in cluster_dict], reverse=True)
        big_clusters = [pr[1] for pr in cluster_size_list[:n_clusters]]
        small_clusters = [pr[1] for pr in cluster_size_list[n_clusters:]]
        for small_idx in small_clusters:
            # 对每个小簇
            best_idx = big_clusters[0]
            best_distance = calc_distance(small_idx, best_idx)
            for cur_idx in big_clusters:
                # 找出距离最近的大簇
                if cur_idx != best_idx:
                    cur_distance = calc_distance(small_idx, cur_idx)
                    if cur_distance < best_distance:
                        best_distance = cur_distance
                        best_idx = cur_idx
            # 修改idx_list
            small_elem_idxs = cluster_dict[small_idx]
            for elem_idx in small_elem_idxs:
                idx_list[elem_idx] = best_idx
    else:
        print("# 无需处理离群点，簇个数已满足.")

    print("# HC 完成. SSE历史:", sse_list)
    idxset = set(idx_list)
    assert(len(idxset) == n_clusters)
    st_idx = 1
    idx_trdict = dict()
    for idx in idxset:
        idx_trdict[idx] = st_idx
        st_idx += 1
    return [idx_trdict[idx] for idx in idx_list]

    
# -----------------------------------------------------------------------

def test():
    from util import getdata
    from util import evaluate
    from util import myprint
    import matplotlib.pyplot as plt

    dataset, _ = getdata.get_fake_cluster_data()
    plt.scatter([x[0] for x in dataset], [x[1] for x in dataset])
    plt.show()

    cluster_labels = HC(dataset, 7, cluster_ratio=1.1)
    
    print(cluster_labels)
    plt.scatter([x[0] for x in dataset], [x[1] for x in dataset], c=cluster_labels)
    plt.show()


def main():
    from util import getdata
    from util import evaluate
    from util import myprint
    dataset, real_labels = getdata.get_HC_cluster_data()
    real_class_count = len(set(real_labels))
    
    cluster_labels = HC(dataset, real_class_count, cluster_ratio=0.95)

    # output
    myprint.set_stdout("HC.csv")
    myprint.print_cluster_data(cluster_labels)
    myprint.reset_stdout()

    # evaluate
    purity, ri = evaluate.evaluate(cluster_labels, real_labels)
    print("data-size: %d, class-count: %d" % (len(dataset), real_class_count))
    print(purity, ri)
    print("# Done.")


def analyze_main():
    from util import getdata
    from util import evaluate
    from util import myprint
    dataset, real_labels = getdata.get_HC_cluster_data()
    real_class_count = len(set(real_labels))
    
    for clu_count in [82]: #231 #57
        cluster_labels = HC(dataset, clu_count, cluster_ratio=1.1)
        # evaluate
        purity, ri = evaluate.evaluate(cluster_labels, real_labels)
        print("target_cluster_count:", clu_count)
        print("data-size: %d, class-count: %d" % (len(dataset), real_class_count))
        print("eval: ", purity, ri)
    

do_test = False

if __name__ == "__main__":
    if do_test:
        print("# HC test.")
        test()
    else:
        print("# PC.")
        main()
        # analyze_main()
else:
    print(__name__)
    print("# this is imported by other.")