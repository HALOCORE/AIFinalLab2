import PCA
from KMeans import KMeans

def KMeans_PCA(k:int, data:list, threshold:float):
    dataset, _, _, _ = PCA.PCA(data, threshold)
    # dataset, _, _, _ = PCA.standard_PCA(data, 8)
    cluster_labels = KMeans(k, dataset)
    return dataset, cluster_labels

def main():
    from util import getdata
    from util import evaluate
    from util import myprint
    dataset, real_labels = getdata.get_cluster_data()
    real_classes_count = len(set(real_labels))
    trans_dataset, cluster_labels = KMeans_PCA(3, dataset, 0.9)
    
    # output
    myprint.set_stdout("KMeans_PCA.csv")
    myprint.print_cluster_data(cluster_labels)
    myprint.reset_stdout()
    
    # evaluate
    purity, ri = evaluate.evaluate(cluster_labels, real_labels)
    print("data-size: %d, class-count: %d" % (len(dataset), real_classes_count))
    print(purity, ri)
    PCA.visualize_PCA_2D(trans_dataset, cluster_labels)
    print("# Done.")

do_test = False
if __name__ == "__main__":
    print("# PCA KMeans.")
    main()