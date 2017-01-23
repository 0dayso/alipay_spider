# -*- coding:utf-8 -*-
"""
author: liuyd
update_date: 2017/01/03
"""
from __future__ import unicode_literals
import pandas as pd
import numpy as np
import operator
from sklearn.decomposition import PCA
from sklearn import svm
from os import listdir
from io import BytesIO
from PIL import Image,ImageDraw
import requests
from pytesseract import image_to_string
import csv
import os

cur_dir=os.path.dirname(__file__)


#下载验证码
def load_image(url,**kwargs):
    """

    :param url: 验证码的url
    :param kwargs: 获取验证码的参数
    :return: image对象
    """
    pass

#将训练集写入CSV
def write_csv(path,data):
    """
    将List数据写入csv文件
    :param path:
    :param data:
    :return:
    """
    with open(path,'ab') as file:
        csv_file=csv.writer(file)
        csv_file.writerow(data)
    print "数据写入完成"

#必须是二值图转二值数据值，图片必须是经过处理的
def twoValue(image,type='list'):
    """

    :param image:
    :param type: 二值后返回的类型，list,dict,tuple
    :return: type数据
    """
    from numpy import zeros
    types={
        'dict':{},
        'array':zeros((image.size[1],image.size[0]),dtype=int),
        'list':[]
    }
    image_value=types[type]
    for y in xrange(0,image.size[1]):
        for x in xrange(0,image.size[0]):
            g=image.getpixel((x,y))
            if g<>0:
                if type=="dict":
                    image_value[(x,y)]=1
                elif type=='array':
                    image_value[y][x]=1
                else:
                    image_value.append(1)
            else:
                if type=="dict":
                    image_value[(x,y)]=0
                elif type=='array':
                    image_value[y][x]=0
                else:
                    image_value.append(0)
    return image_value

#获取二值图对象
def twoValueImage(image,G,background='white'):
    """

    :param image: image对象
    :param G: 閥值
    :param background: 背景颜色
    :return: Image对象
    """
    image=image.convert("L")
    t2val={}
    for y in xrange(0,image.size[1]):
        for x in xrange(0,image.size[0]):
            g=image.getpixel((x,y))
            if background=="white":
                if g>G:
                    t2val[(x,y)]=1
                else:
                    t2val[(x,y)]=0
            else:
                if g>G:
                    t2val[(x,y)]=0
                else:
                    t2val[(x,y)]=1
    image=Image.new("1",image.size)
    draw=ImageDraw.Draw(image)

    for x in xrange(0,image.size[0]):
        for y in xrange(0,image.size[1]):
            draw.point((x,y),t2val[(x,y)])
    return image


#去噪点
def clear(image,C=1,N=1):
    """

    :param image: twoValues Image Object
    :param C: counts of around
    :param N: times of clear
    :return: image object
    """
    image=image.convert("L")
    #去边框
    for y in range(0,image.size[1]):
        for x in range(0,image.size[0]):
            if x ==0 or x==image.size[0]-1:
                image.putpixel((x,y),255)
                continue
            if y==0 or y==image.size[1]-1:
                image.putpixel((x,y),255)
                continue

    #去中间图片的噪点
    for i in range(0, N):
        for y in range(1, image.size[1] - 1):
            for x in range(1, image.size[0] - 1):
                nearDots = 0
                d = image.getpixel((x, y))  # 中心点的灰度值
                if d == image.getpixel((x - 1, y - 1)):
                    nearDots += 1
                if d == image.getpixel((x, y - 1)):
                    nearDots += 1
                if d == image.getpixel((x + 1, y - 1)):
                    nearDots += 1
                if d == image.getpixel((x - 1, y)):
                    nearDots += 1
                if d == image.getpixel((x + 1, y)):
                    nearDots += 1
                if d == image.getpixel((x - 1, y + 1)):
                    nearDots += 1
                if d == image.getpixel((x, y + 1)):
                    nearDots += 1
                if d == image.getpixel((x + 1, y + 1)):
                    nearDots += 1
                if nearDots < C:
                    image.putpixel((x, y), 255)
    return image

#将而知二值对象进行环切
def cutAround(image):
    """

    :param image:二值Image对象
    :return:环切后的二值Image对象
    """
    x1,y1,x2,y2=0,0,1,1
    #右移
    a1=False
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            color=image.getpixel((x,y))
            if color==0:
                x1=x
                a1=True
                break
            else:
                continue
        if a1==True:
            break

    #左移
    a2=False
    for x in range(image.size[0]-1,-1,-1):
        for y in range(image.size[1]):
            color=image.getpixel((x,y))
            if color==0:
                x2=x+1
                a2=True
                break
        if a2==True:
            break
    #下移
    b1=False
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            color=image.getpixel((x,y))
            if color==0:
                y1=y
                b1=True
                break
            else:
                continue
        if b1==True:
            break
#上移
    b2=False
    for y in range(image.size[1]-1,-1,-1):
        for x in range(image.size[0]):
            color=image.getpixel((x,y))
            if color==0:
                y2=y+1
                b2=True
                break
            else:
                continue
        if b2==True:
            break
    image=image.crop((x1,y1,x2,y2))
    return image

def formatImg(image,new_size):
    '''
     :param image: Image对象
     :param new_size: 新的尺寸
     :return: Image对象
     '''
    # image_dict: 来自于twoValue的。使用前图片需做二值化处理,new_size is tuple。
    image_dict = twoValue(image,'dict')
    im = Image.new("1", (new_size[0], new_size[1]))
    draw = ImageDraw.Draw(im)
    for x in xrange(0, new_size[0]):
        for y in xrange(0, new_size[1]):
            if image.size[0] < new_size[0]:
                x0 = x - abs(new_size[0] - image.size[0]) // 2
            else:
                x0 = x + abs(new_size[0] - image.size[0]) // 2
            if image.size[1] < new_size[1]:
                y0 = y - abs(new_size[1] - image.size[1]) // 2
            else:
                y0 = y + abs(new_size[1] - image.size[1]) // 2
            if image_dict.has_key((x0, y0)):
                im.putpixel((x, y), image_dict[(x0, y0)])
            else:
                im.putpixel((x, y), 1)

    return im
# 读取训练集
def loadTrainSet(path):
    '''
    该函数读取加载训练集
    :param path: 训练集所在路径，csv文件，第一列为label，每行是一个样本
    :return: labels or trainX
    '''
    if '.csv' not in path:
        train_data = listdir(path)
        labels = []
        trains = []
        for i in range(len(train_data)):
            image = Image.open(path + train_data[i])
            array = twoValue(image, 'list')
            trains.append(array)
            labels.append(train_data[i][0])
        trains = np.array(trains)
        labels = np.array(labels)
    else:
        train = pd.read_csv(path)
        #values为值后面为 切片
        trains = train.values[:, 1:]
        #ix接受行与列的切片
        labels = train.ix[:, 0]

    return trains, labels

# 计算距离
def distance(array1, array2, axis=None):
    '''计算两个数组矩阵的欧式距离;
    axis=0，求每列的
    axis=1，求每行的'''
    distance = (np.sum((array1 - array2), axis) ** 2) ** 0.5

    return distance

# KNN分类
def classify_KNN(image, trains, labels, k):
    '''KNN'''
    unArray = twoValue(image, 'list')
    unArray = np.array(unArray) # 转换成一维数组
    diff = []

    # 依次计算距离
    for each in trains:
        dis = distance(unArray, each)
        diff.append(dis)

    # 统计距离最小的个数， 将diff与labels转换成array
    diff = np.array(diff)
    # labels = np.array(labels)

    # 排序后的数据在原数据中的下标
    index = np.argsort(diff)

    # 统计标签的个数
    count = {}
    for i in range(5):
        votelabel = labels[index[i]]
        count[votelabel] = count.get(votelabel, 0) + 1

    # 按Count字典的第2个元素（即类别出现的次数）从大到小排序
    sortedCount = sorted(count.items(), key=operator.itemgetter(1), reverse=True)

    return sortedCount[0][0]

# SVM分类
def classify_SVM(image, train_x, train_y):

    # 都是array，每个样本的唯独与image都是一维数组
    pca = PCA(n_components=0.8, whiten=True)
    svc = svm.SVC(kernel='rbf', C=10)

    train_x = pca.fit_transform(train_x)
    svc.fit(train_x, train_y)

    image_array = twoValue(image, 'list')
    obj_array = np.array(image_array)
    obj_array = pca.transform(obj_array)
    obj_string = svc.predict(obj_array)

    return obj_string[0]



# t,l=loadTrainSet("TrainSet.csv")
#
# print l

# def main():
#     image=Image.open('2.png')
#     # im=twoValueImage(image,200)
#     # cutAround(im).show()
#
#     #print twoValue(image)
#     formatImg(image,(25,30)).show()
#
#
# main()



























