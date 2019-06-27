from PIL import Image
import numpy as np

import random
import matplotlib.pyplot as plt  

def img_to_nparray(filename):
    # 读取图片
    im = Image.open(filename)
    # 显示图片
    # im.show()  
    width,height = im.size
    im = im.convert("L") 
    data = im.getdata()
    data = np.matrix(data,dtype=np.float)/255.0
    #new_data = np.reshape(data,(width,height))
    new_data = np.reshape(data,(height,width))
    return new_data

def randpoints_from_img(filename, probability):

    dep_nparray = img_to_nparray(filename)
    dep_shape = dep_nparray.shape
    dep_list = dep_nparray.tolist()

    fake_data = list()

    for i in range(dep_shape[0]):
        for j in range(dep_shape[1]):
            y = i / dep_shape[0]
            x = j / dep_shape[1]
            prob = dep_list[i][j]
            assert(prob >= 0 and prob <= 1)
            if random.random() < prob * probability * 0.005:
                fake_data.append((x, y))
    
    return fake_data

import sys
def main():
    input_filename = sys.argv[1]
    probability = float(sys.argv[2])
    assert(probability >= 0 and probability <= 1)
    points = randpoints_from_img(input_filename, probability)
    print("# write %d points to file: %s" % (len(points), input_filename))
    with open("fakedata.csv", 'w') as myfile:
        myfile.write('x,y,l\n')
        for point in points:
            myfile.write('%s,%s,%s\n' % (point[0], point[1], 0))
    print("# done.")


main()