# -*- coding:utf-8 -*-
from random import random
from time import time
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import os
import cv2 as cv

ANSWER_KEY_SCORE = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1}

ANSWER_KEY = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}

def showIMG(img):
    t= str(time())
    def click_event(event, x, y, flags, param):
        # 如果鼠标左键被单击
        if event == cv.EVENT_LBUTTONDOWN:
            # 在点击位置绘制一个圆圈
            cv.circle(img, (x, y), 3, (0, 0, 255), -1)
            # 在点击位置显示坐标
            text = f'({x}, {y})'
            cv.putText(img, text, (x - 20 , y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv.imshow(t, img)
    cv.namedWindow(t,cv.WINDOW_NORMAL)
    cv.imshow(t, img)
    cv.setMouseCallback(t, click_event)


def thresh(img,size):
    '''对图像二值化'''
    return cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, size, 4)

# 加载一个图片到opencv中
img = cv.imread(os.path.dirname(os.path.abspath(__file__))+ "\\" +'4370.jpg')
img = cv.resize(img, (0, 0), fx=0.4, fy=0.4)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
'''灰度图片'''
thresh2 = thresh(gray,51)
kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
morph = cv.morphologyEx(thresh2, cv.MORPH_CLOSE, kernel)

# showIMG(morph)
'''二值化后的图'''

edged = cv.Canny(morph, 70, 200)

# 寻找轮廓
# contours, hierarchy = cv.findContours(edged.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
cts, hierarchy = cv.findContours(thresh2.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# 给轮廓加标记，便于我们在原图里面观察，注意必须是原图才能画出红色，灰度图是没有颜色的
cv.drawContours(img, cts, -1, (0, 0, 255), 7)
# cv.namedWindow('aaa',cv.WINDOW_NORMAL)
# cv.imshow('aaa',img)


# # 按面积大小对所有的轮廓排序
list = sorted(cts, key=cv.contourArea, reverse=True)

# # print("寻找轮廓的个数：", len(cts))


# # 正确题的个数
# correct_count = 0

for c in list:
    # 周长，第1个参数是轮廓，第二个参数代表是否是闭环的图形
    peri = 0.01 * cv.arcLength(c, True)
    # 获取多边形的所有定点，如果是四个定点，就代表是矩形
    approx = cv.approxPolyDP(c, peri, True)
    # 打印定点个数
    print("顶点个数：", len(approx))
    if len(approx) == 4:  # 矩形
        # 透视变换提取原图内容部分
        ox_sheet = four_point_transform(img, approx.reshape(4, 2))
        # 透视变换提取灰度图内容部分
        tx_sheet = four_point_transform(gray, approx.reshape(4, 2))
        # cv.namedWindow('ox', cv.WINDOW_NORMAL)
        # cv.imshow("ox", ox_sheet)
        # cv.namedWindow('tx',cv.WINDOW_NORMAL)
        # cv.imshow("tx", tx_sheet)
        break

# ##################################
thresh2 = thresh(tx_sheet,251)
kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
erosion = cv.erode(thresh2, kernel, iterations = 1)

showIMG(erosion)
# 继续寻找轮廓
r_cnt, r_hierarchy = cv.findContours(erosion.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

print("找到轮廓个数：", len(r_cnt))

# 使用红色标记所有的轮廓
# cv.drawContours(ox_sheet,r_cnt,-1,(0,0,255),2)

# 把所有找到的轮廓，给标记出来

questionCnts = []
for cxx in r_cnt:
    # 通过矩形，标记每一个指定的轮廓
    x, y, w, h = cv.boundingRect(cxx)
    ar = w / float(h)

    if w >= 35 and w <=80 and h >= 30 and h <= 60 and ar >= 0.5 and ar <= 2:
        # 使用红色标记，满足指定条件的图形
        cv.rectangle(ox_sheet, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # 把每个选项，保存下来
        questionCnts.append(cxx)
showIMG(ox_sheet)
"""
            # 按坐标从上到下排序
            questionCnts = contours.sort_contours(
                questionCnts, method="top-to-bottom")[0]

            # 使用np函数，按5个元素，生成一个集合
            for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):

                # 获取按从左到右的排序后的5个元素
                cnts = contours.sort_contours(questionCnts[i:i + 5])[0]

                bubble_rows = []

                # 遍历每一个选项
                for (j, c) in enumerate(cnts):
                    # 生成一个大小与透视图一样的全黑背景图布
                    mask = np.zeros(tx_sheet.shape, dtype="uint8")
                    # 将指定的轮廓+白色的填充写到画板上,255代表亮度值，亮度=255的时候，颜色是白色，等于0的时候是黑色
                    cv.drawContours(mask, [c], -1, 255, -1)
                    # 做两个图片做位运算，把每个选项独自显示到画布上，为了统计非0像素值使用，这部分像素最大的其实就是答案
                    mask = cv.bitwise_and(thresh2, thresh2, mask=mask)
                    # cv.imshow("c" + str(i), mask)
                    # 获取每个答案的像素值
                    total = cv.countNonZero(mask)
                    # 存到一个数组里面，tuple里面的参数分别是，像素大小和答案的序号值
                    # print(total,j)
                    bubble_rows.append((total, j))

                bubble_rows = sorted(
                    bubble_rows, key=lambda x: x[0], reverse=True)
                # 选择的答案序号
                choice_num = bubble_rows[0][1]
                print("答案：{} 数据: {}".format(
                    ANSWER_KEY.get(choice_num), bubble_rows))

                fill_color = None

                # 如果做对就加1
                if ANSWER_KEY_SCORE.get(q) == choice_num:
                    fill_color = (0, 255, 0)  # 正确 绿色
                    correct_count = correct_count + 1
                else:
                    fill_color = (0, 0, 255)  # 错误 红色

                cv.drawContours(ox_sheet, cnts[choice_num], -1, fill_color, 2)

            #cv.imshow("answer_flagged", ox_sheet)

            text1 = "total: " + str(len(ANSWER_KEY)) + ""

            text2 = "right: " + str(correct_count)

            text3 = "score: " + \
                str(correct_count * 1.0 / len(ANSWER_KEY) * 100) + ""

            font = cv.FONT_HERSHEY_SIMPLEX
            cv.putText(ox_sheet, text1 + "  " + text2 + "  " +
                       text3, (10, 30), font, 0.5, (0, 0, 255), 2)

            #cv.imshow("score", ox_sheet)
"""
cv.waitKey(0)