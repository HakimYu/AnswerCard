# -*- coding:utf-8 -*-
from time import time
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import concurrent.futures
import os
import cv2 as cv
from progress.bar import IncrementalBar

listeningCA = None
readingCA = None
fillingCA = None

workingPath = os.path.dirname(os.path.abspath(__file__))

with open(workingPath + "\\" + "answer.txt", 'r') as f:
    content = f.readlines()
    if len(content) < 3:
        raise ValueError('File does not have enough lines')
    listeningCALine = content[0].strip()
    readingCALine = content[1].strip()
    fillingCALine = content[2].strip()
    listeningCA = [c for c in listeningCALine]
    readingCA = [c for c in readingCALine]
    fillingCA = [c for c in fillingCALine]

def showIMG(img):
    t= str(time())
    def click_event(event, x, y, flags, param):
        # 如果鼠标左键被单击
        if event == cv.EVENT_LBUTTONDOWN:
            # 在点击位置绘制一个圆圈
            cv.circle(img, (x, y), 3, (0, 0, 255), -1)
            # 在点击位置显示坐标
            text = f'({x}, {y})'
            cv.putText(img, text, (x - 20 , y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv.imshow(t, img)
    cv.namedWindow(t,cv.WINDOW_NORMAL)
    cv.imshow(t, img)
    cv.setMouseCallback(t, click_event)

def resize(img,h):
    height, width = img.shape[:2]
    aspect_ratio = h / height
    new_width = int(width * aspect_ratio)
    return cv.resize(img, (new_width, h))

def thresh(img,size):
    '''对图像二值化'''
    return cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, size, 4)

def adjustBrightnessContrast(img, brightness=0, contrast=0):
    # 调整亮度和对比度
    b = brightness / 255.0
    c = contrast / 255.0
    k = np.tan((45 + 44 * c) / 180 * np.pi)
    img = (img - 127.5 * (1 - b)) * k + 127.5 * (1 + b)
    # 对图像进行裁剪，保证像素值在0-255之间
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def ansList(imgName):
    # 加载一个图片到opencv中
    img = cv.imread(workingPath + "\\pic\\" + imgName)
    img = resize(img,1280)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray,(5,5),0)
    # gray = adjustBrightnessContrast(gray,20,120)
    # showIMG(gray)
    thresh2 = thresh(gray,131)
    # showIMG(thresh2)

    # 寻找轮廓
    cts, hierarchy = cv.findContours(thresh2.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # 给轮廓加标记，便于我们在原图里面观察，注意必须是原图才能画出红色，灰度图是没有颜色的
    # cv.drawContours(img, cts, -1, (0, 0, 255), 7)

    # showIMG(img)

    # # 按面积大小对所有的轮廓排序
    list = sorted(cts, key=cv.contourArea, reverse=True)
    # cv.drawContours(img, list[0], -1, (0, 0, 255), 7)

    # showIMG(img)

    for c in list:
        # 周长，第1个参数是轮廓，第二个参数代表是否是闭环的图形
        peri = 0.02 * cv.arcLength(c, True)
        # 获取多边形的所有定点，如果是四个定点，就代表是矩形
        approx = cv.approxPolyDP(c, peri, True)
        # 打印定点个数
        # print("顶点个数：", len(approx))
        if len(approx) == 4:  # 矩形
            # cv.drawContours(img, c, -1, (0, 0, 255), 7)

            # showIMG(img)
            # 透视变换提取原图内容部分
            origin_sheet = four_point_transform(img, approx.reshape(4, 2))
            # 透视变换提取灰度图内容部分
            gray_sheet = four_point_transform(gray, approx.reshape(4, 2))
            # showIMG(origin_sheet)
            # cv.namedWindow('tx',cv.WINDOW_NORMAL)
            # cv.imshow("tx", gray_sheet)
            break

    gray_sheet = resize(gray_sheet,1040)
    origin_sheet = resize(origin_sheet,1040)
    thresh2 = thresh(gray_sheet,101)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (11, 11))
    erosion = cv.erode(thresh2, kernel, iterations = 1)

    # showIMG(erosion)
    # 继续寻找轮廓
    ans_cnt, ans_hierarchy = cv.findContours(erosion.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # print("找到轮廓个数：", len(ans_cnt))

    # 使用红色标记所有的轮廓
    # cv.drawContours(origin_sheet,ans_cnt,-1,(0,0,255),2)

    listeningAnsCross=[]
    readingAnsCross=[]
    fillingAnsCross=[]
    listeningAns=[]
    readingAns=[]
    fillingAns=[]
    for cross in ans_cnt:
        # 通过矩形，标记每一个指定的轮廓
        x, y, w, h = cv.boundingRect(cross)
        # ar = w / float(h)

        if x>8 and w >= 30 and w <=80 and h >= 15 and h <= 60:
            #  and ar >= 0.5 and ar <= 3
            # 标记
            # cv.putText(origin_sheet, str(x)+ ',' + str(y), (x - 5 , y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            if y < 310:
                cv.rectangle(origin_sheet, (x, y), (x + w, y + h), (0, 0, 255), 2)
                listeningAnsCross.append(cross)
            elif y<790:
                cv.rectangle(origin_sheet, (x, y), (x + w, y + h), (0, 0, 255), 2)
                readingAnsCross.append(cross)
            else:
                cv.rectangle(origin_sheet, (x, y), (x + w, y + h), (0, 0, 255), 2)
                fillingAnsCross.append(cross)
    # showIMG(origin_sheet)
    listeningAnsCross = contours.sort_contours(listeningAnsCross)[0]
    readingAnsCross = contours.sort_contours(readingAnsCross)[0]
    fillingAnsCross = contours.sort_contours(fillingAnsCross)[0]
    for i in listeningAnsCross:
        x, y, w, h = cv.boundingRect(i)
        if y<110:
            listeningAns.append('A')
        elif y<169:
            listeningAns.append('B')
        else:
            listeningAns.append("C")
    for i in readingAnsCross:
        x, y, w, h = cv.boundingRect(i)
        if y<390:
            readingAns.append('A')
        elif y<450:
            readingAns.append('B')
        elif y<505:
            readingAns.append("C")
        elif y<560:
            readingAns.append("D")
        elif y<610:
            readingAns.append("E")
        elif y<670:
            readingAns.append("F")
        else:
            readingAns.append("G")
    for i in fillingAnsCross:
        x, y, w, h = cv.boundingRect(i)
        if y<850:
            fillingAns.append('A')
        elif y<910:
            fillingAns.append('B')
        elif y<965:
            fillingAns.append("C")
        else:
            fillingAns.append("D")
    return ([listeningAns,readingAns,fillingAns],origin_sheet)




def worker(imgName):
    finalScore = 0
    ori_sheet = None
    ans = None
    fail = False
    try:
        ans,ori_sheet = ansList(imgName)
    except Exception as e:
        e = e
        fail = True
    for CANum, CA in enumerate(listeningCA):
        try:
            if ans[0][CANum] == CA:
                finalScore += 1.5
        except Exception as e:
            e=e
            fail = True
    for CANum, CA in enumerate(readingCA):
        try:
            if ans[0][CANum] == CA:
                finalScore += 2.5
        except Exception as e:
            e = e
            fail = True
    for CANum, CA in enumerate(fillingCA):
        try:
            if ans[0][CANum] == CA:
                finalScore += 1
        except Exception as e:
            e = e
            fail = True
    if fail:
        with open(workingPath+ "\\result\\" + 'wrong.txt', "w") as file:
            file.write(filename+'\n')
    if ans!=None:
        # 设置文本信息
        text = str(finalScore)
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 4
        thickness = 2
        color = (0, 0, 255)
        # 获取文本大小
        text_size, _ = cv.getTextSize(text, font, font_scale, thickness)
        # 计算文本位置
        text_x = ori_sheet.shape[1] - text_size[0] - 10
        text_y = ori_sheet.shape[0] - text_size[1] - 10
        # 在图像上添加文本
        cv.putText(ori_sheet, text, (text_x, text_y), font, font_scale, color, thickness, cv.LINE_AA)
        cv.imwrite(workingPath+ "\\result\\" + imgName, ori_sheet)

img_files = []  # 保存 JPG 文件名的数组
# 遍历目录下的所有文件
for filename in os.listdir(workingPath + '\\pic'):
    # 判断是否为 JPG 文件
    if filename.lower().endswith('.jpg'):
        # 将文件名保存到数组中
        img_files.append(filename)

# ansList('1.jpg')

futures = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    for i in img_files:
        futures.append(executor.submit(worker, i))
    with IncrementalBar('Processing', max=len(futures)) as bar:
        for future in concurrent.futures.as_completed(futures):
            bar.next()
# cv.waitKey(0)