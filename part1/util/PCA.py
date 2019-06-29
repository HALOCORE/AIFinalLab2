import numpy as np

def PCA(data:list, threshold:float, verbose=True):
    """
    返回转换后数据，特征个数，特征比例，{转换信息...}
    """
    print("# PCA. ver2")
    np_data = np.asarray(data, dtype=np.float).T
    data_shape = np_data.shape
    data_mean = np_data.mean(axis=1)
    for i in range(data_shape[0]):
        np_data[i] -= data_mean[i]
    cov_mat = (1 / data_shape[1]) * np.matmul(np_data, np_data.T)
    eig_vals, eig_vecs = np.linalg.eig(cov_mat)
    eig_vecs = eig_vecs.T
    sort_eigs_list = [(eig_vals[i], i) for i in range(len(eig_vals))]
    sort_eigs_list.sort(reverse=True)
    eig_vals_sorted = np.asarray([x[0] for x in sort_eigs_list])
    eig_sum = eig_vals_sorted.sum()
    eig_ratios = eig_vals_sorted / eig_sum
    eig_ratioacc = 0
    pc_count = 0
    for i in range(eig_ratios.shape[0]):
        eig_ratioacc += eig_ratios[i]
        pc_count += 1
        if eig_ratioacc > threshold:
            break
    trans_mat = np.asarray([eig_vecs[es[1]] for es in sort_eigs_list[0:pc_count]])
    print("   eig_ratios:", eig_ratios)
    print("   selected: %f, pc_count:%d" % (eig_ratioacc, pc_count))
    pc_data = np.matmul(trans_mat, np_data).T.tolist()
    trans_info = {"mean": data_mean, "trans_mat": trans_mat}
    return pc_data, pc_count, eig_ratioacc, trans_info


# from sklearn.decomposition import PCA as skPCA

# def standard_PCA(data:list, n:int):
#     np_data = np.asarray(data, dtype=np.float)
#     pca = skPCA(n_components=n)
#     newX = pca.fit_transform(np_data)
#     print("standard_PCA ratio:", pca.explained_variance_ratio_)
#     return newX, n, None, None


def apply_PCA_transform(testdata:list, trans_info):
    np_data = np.asarray(testdata, dtype=np.float).T
    for i in range(np_data.shape[0]):
        np_data[i] -= trans_info["mean"][i]
    np_data_trans = np.matmul(trans_info["trans_mat"], np_data)
    return np_data_trans.T.tolist()


def visualize_PCA_2D(pca_data:list, cluster_labels:list):
    print("# INFO: assume input dimensions already be transformed and sorted by PCA.")
    arr_x = [x[0] for x in pca_data]
    arr_y = [x[1] for x in pca_data]
    import matplotlib.pyplot as plt
    plt.scatter(arr_x, arr_y, c=cluster_labels, linewidths=0.01)
    plt.show()
# --------------------------------------------------

def test():
    data = [(1,2,4,5), (2,3,1,1), (3,5,6,-3), (6,4,9,6), (7,7,4,8), (8,8,6,4), (8,2,1,6),(5,9,0,1),(1,7,7,8)]
    pc_data, pc_count, eig_acc, trans_info = PCA(data, 0.8)
    print(trans_info)


if __name__ == "__main__":
    print("# PCA.py warning: This module should be imported by other. Only test is runnable.")
    test()