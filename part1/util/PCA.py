import numpy as np

def PCA(data:list, threshold:float, verbose=True):
    """
    返回转换后数据，特征个数，特征比例，{转换信息...}
    """
    print("# PCA.")
    np_data = np.asarray(data, dtype=np.float).T
    data_shape = np_data.shape
    data_mean = np_data.mean(axis=1)
    for i in range(data_shape[0]):
        np_data[i] -= data_mean[i]
    cov_mat = (1 / data_shape[1]) * np.matmul(np_data, np_data.T)
    eig_vals, eig_vecs = np.linalg.eig(cov_mat)
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
    plt.scatter(arr_x, arr_y, c=cluster_labels)
    plt.show()
# --------------------------------------------------

if __name__ == "__main__":
    print("# _PCA.py for Chess. Must be imported by getdata.")