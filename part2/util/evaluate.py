

def cluster_purity(cluster_labels:list, real_labels:list):
    assert(len(cluster_labels) == len(real_labels))
    cluster_dict = dict()
    real_dict = dict()
    for i in range(len(cluster_labels)):
        # 构造聚类结果字典
        cluster_label = cluster_labels[i]
        if cluster_label not in cluster_dict:
            cluster_dict[cluster_label] = set()
        cluster_dict[cluster_label].add(i)
        # 构造真实分类字典
        real_label = real_labels[i]
        if real_label not in real_dict:
            real_dict[real_label] = set()
        real_dict[real_label].add(i)
    
    inter_sum = 0
    for cluster_key in cluster_dict:
        cluster_set = cluster_dict[cluster_key]
        max_intersize = 0
        for real_key in real_dict:
            inter_set = cluster_set.intersection(real_dict[real_key])
            inter_size = len(inter_set)
            if inter_size > max_intersize:
                max_intersize = inter_size
        assert(max_intersize > 0 and max_intersize <= len(cluster_set))
        inter_sum += max_intersize
    
    return inter_sum / len(cluster_labels)


def cluster_RI(cluster_labels:list, real_labels:list):
    assert(len(cluster_labels) == len(real_labels))
    data_size = len(cluster_labels)
    a = 0
    b = 0
    c = 0
    d = 0
    for i in range(data_size):
        for j in range(data_size):
            if real_labels[i] == real_labels[j]:
                if cluster_labels[i] == cluster_labels[j]:
                    a += 1
                else:
                    b += 1
            else:
                if cluster_labels[i] == cluster_labels[j]:
                    c += 1
                else:
                    d += 1

    return (a + d) / (a + b + c + d)


def evaluate(cluster_labels:list, real_labels:list, verbose=True):
    print("# cluster evaluate.")
    # 统计真实标签和聚类标签
    def get_descent_count(labels:list):
        label_set = set(labels)
        label_counts = sorted([(labels.count(key), key) for key in label_set], reverse=True)
        assert(sum([x[0] for x in label_counts]) == len(labels))
        return label_counts
    cluster_count_result = get_descent_count(cluster_labels)
    real_count_result = get_descent_count(real_labels)
    print("    CLUSTER_COUNT: ", cluster_count_result)
    print("    REAL_COUNT: ", real_count_result)
    purity = cluster_purity(cluster_labels, real_labels)
    print("    purity: %f" % purity)
    ri = cluster_RI(cluster_labels, real_labels)
    print("    ri: %f" % ri)
    return purity, ri


def calc_SSE(data:list, cluster:list):
    # 算出所有的中心
    elem_len = len(data[0])
    clusterset = set(cluster)
    count_dict = {key:0 for key in clusterset}
    center_dict = {key:[0 for _ in range(elem_len)] for key in clusterset}
    for elem, idx in zip(data, cluster):
        count_dict[idx] += 1
        for i in range(elem_len):
            center_dict[idx][i] += elem[i]
    for key in center_dict:
        for i in range(elem_len):
            center_dict[key][i] /= count_dict[key]
    # 求和求出SSE
    sse = 0
    for elem, idx in zip(data, cluster):
        for i in range(elem_len):
            sse += (elem[i] - center_dict[idx][i])**2
    return sse
    