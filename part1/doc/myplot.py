from matplotlib import pyplot as plt


sel = 'DES'

if sel =='KNN':
    xs = [3,5,7,9,11]
    ys = [0.627222, 0.721764, 0.737046, 0.718467, 0.708487]


    plt.plot(xs, ys)
    plt.title('Micro F1 vs neighbor @KNN')
    plt.xlabel(u'neighbor')
    plt.ylabel(u'Micro F1')
    plt.ylim(ymin=0, ymax=1)
    # plt.legend()
    plt.show()

if sel == 'DES':
    xs = [0,3,5,10,20]
    ys = [0.555001, 0.554110, 0.548897, 0.525195, 0.447093]


    plt.plot(xs, ys)
    plt.title('Micro F1 vs minimum sample size @Decision Tree')
    plt.xlabel(u'minimum sample size')
    plt.ylabel(u'Micro F1')
    plt.ylim(ymin=0, ymax=1)
    # plt.legend()
    plt.show()

if sel == 'SVM':
    xs1 = []