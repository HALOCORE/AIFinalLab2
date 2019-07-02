from matplotlib import pyplot as plt


sel = 'KM'

if sel =='KM':
    xs = [2, 3, 4, 5, 6, 7, 8]
    ys = [2469.1713550990676, 2104.144132679775, 1872.0715124331293, 1681.9716027621166, 1535.2492174259896, 1442.6267458510413, 1362.1605437575822]
    plt.plot(xs, ys)
    plt.scatter(xs, ys, marker='o')
    
    dxs = xs[:-1]
    dys = [-365.0272224192927, -232.07262024664556, -190.0999096710127, -146.722385336127, -92.62247157494835, -80.46620209345906]
    plt.plot(dxs, dys)

    ddxs = xs[1:-1]
    ddys = [132.95460217264713, 41.972710575632846, 43.37752433488572, 54.09991376117864, 12.15626948148929]
    plt.plot(ddxs, ddys)

    plt.title('SSE vs k @KNN, 128 times average')
    plt.xlabel(u'k')
    plt.ylabel(u'SSE')
    # plt.ylim(ymin=0)
    plt.legend(['SSE', "SSE'", "SSE''"])
    plt.show()
