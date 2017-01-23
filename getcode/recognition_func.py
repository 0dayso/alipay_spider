# -*- coding:utf-8 -*-
"""
author: liuyd
theme:
update_date: 2017/01/01
"""
import csv
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from  sklearn import svm
import os
from CheckCode import twoValue,twoValueImage,cutAround,formatImg
import pdb

from PIL import  Image
pca=PCA(n_components=0.8,whiten=True)
svc=svm.SVC(kernel='rbf',C=10)


def cutUnion(image):
    '''返回四个image对象'''
    ux = image.size[0] / 4
    region = []
    for j in range(4):
        # （left, upper, right, lower），第二个参数与低四个参数决定图片的高度是不变的。
        rg = (ux * j, 0, ux * (j + 1), image.size[1])
        # 第个参数与第三个参数的差值决定图片的宽度，四个图片的差值都为1个ux
        region.append(rg)
    img1 = image.crop(region[0])
    img2 = image.crop(region[1])
    img3 = image.crop(region[2])
    img4 = image.crop(region[3])
    return img1, img2, img3, img4

def parse(train_x, train_y, image_array):
    obj_array = np.array(image_array)
    train_x = pca.fit_transform(train_x)
    obj_array = pca.transform(obj_array)
    svc.fit(train_x, train_y)
    obj_string = svc.predict(obj_array)
    return obj_string


def twoValue_1(im, G):
    im = im.convert('L')
    w, h = im.size
    imageList = []
    for x in xrange(0, w):
        #image_col = []
        for y in xrange(0, h):
            g = im.getpixel((x, y))
            print g
            if g > G:
                imageList.append(1)
            else:
                imageList.append(0)
    image_array = np.array(imageList)
    return imageList

def recognition_code(image):
    cur_path = os.path.dirname(__file__)
    train_path = os.path.join(cur_path, "TrainSet2.csv")
    train=pd.read_csv(train_path,low_memory=False)
    train_x=train.values[:,1:]
    train_y=train.values[:,0]
    countStr=''
    image_array=twoValue(image)
    obj_string=parse(train_x,train_y,image_array)
    countStr = countStr + obj_string
    return countStr



def getCaptcha(image):
    image = twoValueImage(image, 180)
    image.save('2linux.png')

    # 环切
    image = Image.open('2linux.png')
    image = cutAround(image)
    # # 切成四个未拉伸
    images = cutUnion(image)

    check = ''
    for each in images:
        image = formatImg(each,(25, 30))  # 更改尺寸为25*30
        result = recognition_code(image)[0]
        check = check + result
    return check


if __name__=="__main__":
    image_path='testimage/'
    image_lists=os.listdir(image_path)
    for each in image_lists:
        image=Image.open(image_path+each)
        print getCaptcha(image)
















