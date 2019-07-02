import random


def random_start_centers(elem_min:list, elem_max:list, elem_aver:list, k:int):
    centers = list()
    for _ in range(k):
        center = list()
        for cmin, cmax in zip(elem_min, elem_max):
            center.append(cmin + random.random() * (cmax - cmin))
        centers.append(center)
    assert(len(centers) == k)
    return centers

def generate_min_updater(min_target:list):
    def update_min_elem(elem): 
        for i in range(len(elem)):
            if elem[i] < min_target[i]:
                min_target[i] = elem[i]
    return update_min_elem

def generate_max_updater(max_target:list):
    def update_max_elem(elem):
        for i in range(len(elem)):
            if elem[i] > max_target[i]:
                max_target[i] = elem[i]
    return update_max_elem

def generate_sum_updater(sum_target:list):
    def update_sum_elem(elem):
        for i in range(len(elem)):
            sum_target[i] += elem[i]
    return update_sum_elem

def elem_dist2(e1, e2):
    dist2 = 0
    for e1i, e2i in zip(e1, e2):
        dist2 += (e1i - e2i)*(e1i - e2i)
    return dist2

def elem_mhdist(e1, e2):
    distabs = 0
    for e1i, e2i in zip(e1, e2):
        distabs += abs(e1i - e2i)
    return distabs

def KMeans(k:int, data:list):
    # 第一步：计算出数据的中心点，min,max
    min_elem = list(data[0])
    max_elem = list(data[0])
    sum_elem = [0 for i in range(len(data[0]))]
    
    update_min_elem = generate_min_updater(min_elem)
    update_max_elem = generate_max_updater(max_elem)
    update_sum_elem = generate_sum_updater(sum_elem)
    
    for elem in data:
        assert(len(elem) == len(min_elem))
        update_min_elem(elem)
        update_max_elem(elem)
        update_sum_elem(elem)
    
    aver_elem = [x / len(data) for x in sum_elem]
    
    # 变量和局部函数初始化
    labels = [-1] * len(data)
    centers = random_start_centers(min_elem, max_elem, aver_elem, k)
    center_sums = [[0]*len(min_elem) for _ in range(len(centers))]
    center_counts = [0] * len(centers)
    center_sum_updaters = [generate_sum_updater(csum) for csum in center_sums]
    any_change = True
    def get_nearest_center_idx(elem):
        nearest_dist2 = 100000 # magic
        best_idx = -1
        for i in range(len(centers)):
            dist2 = elem_mhdist(elem, centers[i])
            # dist2 = elem_dist2(elem, centers[i])
            if dist2 < nearest_dist2:
                nearest_dist2 = dist2
                best_idx = i
        assert(best_idx >= 0)
        return best_idx
    def reset_centersc():
        for i in range(len(center_sums)):
            center_counts[i] = 0
            for j in range(len(center_sums[0])):
                center_sums[i][j] = 0
                
        
    while any_change:
        # 第一步，更新所有元素
        print("*", end="")
        reset_centersc()
        any_change = False
        for i in range(len(data)):
            nearest_idx = get_nearest_center_idx(data[i])
            center_sum_updaters[nearest_idx](data[i])
            center_counts[nearest_idx] += 1
            if nearest_idx != labels[i]:
                labels[i] = nearest_idx
                any_change = True
        # 第二步，更新所有中心
        for i in range(len(centers)):
            if center_counts[i] > 0:
                for j in range(len(centers[0])):
                    centers[i][j] = center_sums[i][j] / center_counts[i]
            else:
                assert(not any(center_sums[i]))
    print()
    assert(len(set(labels)) == k)
    return [x+1 for x in labels]
        


def autoKMeans(kmin:int, kmax:int, data:list, repeat=8):
    from util.evaluate import calc_SSE
    print("# autoKMeans. test from %d to %d. repeat=%d." % (kmin, kmax, repeat))
    k_list = []
    sse_list = []
    cluster_list = []
    
    for k in range(kmin, kmax + 1):
        print("# k =", k)
        aver_sse = 0
        temp_sses = list()
        temp_clusters = list()
        
        # 求出本k的平均SSE
        for i in range(repeat):
            tmp_cluster = KMeans(k, data)
            my_sse = calc_SSE(data, tmp_cluster)
            aver_sse += my_sse
            temp_sses.append(my_sse)
            temp_clusters.append(tmp_cluster)
        aver_sse /= repeat
        
        # 找出最接近平均SSE的一组
        diffs = [abs(sse - aver_sse) for sse in temp_sses]
        idx = diffs.index(min(diffs))
        cluster = temp_clusters[idx] 
        
        # 插入这次k的数据
        k_list.append(k)
        sse_list.append(aver_sse)
        cluster_list.append(cluster)

    print("k: ", k_list)
    print("SSE: ", sse_list)
    
    dsse_list = [sse_list[i+1] - sse_list[i] for i in range(len(sse_list)-1)]
    print("k(SSE'): ", k_list[:-1])
    print("SSE': ", dsse_list)
    
    ddsse_list = [dsse_list[i+1] - dsse_list[i] for i in range(len(dsse_list)-1)]
    print("k(SSE''): ", k_list[1:-1])
    print("SSE'': ", ddsse_list)

    midx = ddsse_list.index(max(ddsse_list))
    best_k = k_list[1:-1][midx]
    print("\n# 最佳k =", best_k)

    best_cluster = None
    for i in range(len(k_list)):
        if k_list[i] == best_k:
            best_cluster = cluster_list[i]
    assert(best_cluster is not None)
    return best_cluster



# -------------------------------------------------------------------

def test():
    points = list()
    for i in range(200):
        points.append((random.randint(0, 100) / 100, random.randint(0, 100)/ 100))
    
    import matplotlib.pyplot as plt
    labels = KMeans(5, points)
    plt.scatter([x[0] for x in points], [x[1] for x in points], c=labels)
    plt.show()
    # print(labels)

def main():
    from util import getdata
    from util import evaluate
    from util import myprint
    dataset, real_labels = getdata.get_cluster_data()
    real_classes_count = len(set(real_labels))
    
    cluster_labels = KMeans(3, dataset)
    # cluster_labels = autoKMeans(3, 8, dataset, repeat=128)

    # output
    myprint.set_stdout("KMeans.csv")
    myprint.print_cluster_data(cluster_labels)
    myprint.reset_stdout()

    # evaluate
    purity, ri = evaluate.evaluate(cluster_labels, real_labels)
    print("data-size: %d, class-count: %d" % (len(dataset), real_classes_count))
    print(purity, ri)
    print("# Done.")


do_test = False
if __name__ == "__main__":
    if do_test:
        print("# KMeans test.")
        test()
    else:
        print("# Basic KMeans.")
        main()
