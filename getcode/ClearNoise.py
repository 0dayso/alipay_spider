# -*- coding:utf-8 -*-
'''
清除噪点
'''
from PIL import Image
from PIL import ImageDraw

def clearOne(image, C=1, N=1):
    '''
    :param image: twoValues Image Object
    :param C: counts of around
    :param N: times of clear
    :return: image object
    '''
    image = image.convert('L')  # black is 0, white is 255
    # 去边框
    for y in range(0, image.size[1]):
        for x in range(0, image.size[0]):
            if x == 0 or x == image.size[0] - 1:
                image.putpixel((x, y), 255)
                continue
            if y == 0 or y == image.size[1] - 1:
                image.putpixel((x, y), 255)
                continue
    for i in range(0, N):
    # 循环去噪点的次数
        for y in range(1, image.size[1] - 1):
            for x in range(1, image.size[0] - 1):
                nearDots = 0
                d = image.getpixel((x, y))  # 获取中心点的灰度值
                # 判断周围八个点
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
