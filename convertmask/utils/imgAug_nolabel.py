'''
lanhuage: python
Descripttion:  this file is just like the imgAug.py ,but don`t need to input a label file(path)
version: beta
Author: xiaoshuyui
Date: 2020-08-21 08:27:05
LastEditors: xiaoshuyui
LastEditTime: 2020-10-19 10:10:23
'''
import sys
sys.path.append('..')
from skimage import io
import skimage.util.noise as snoise
import cv2
from .methods.entity import *
import numpy as np
from .methods.logger import logger
import random
import os
from convertmask.utils.imgAug import _getZoomedImg


def imgZoom(oriImg, size, flag=True):
    """
    size : The zoom factor along the axes, default 0.8~1.8
    """
    # pass
    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    elif isinstance(oriImg, np.ndarray):
        img = oriImg
    else:
        logger.error('input {} type error'.format('oriImg'))
        return

    try:
        size = float(size)
        # if size == 0.0:
        #     raise ValueError('zoom factor cannot be zero')
    except:
        logger.warning('input {} type error ,got {}.'.format(
            'size', type(size)))
        size = random.uniform(0.8, 1.8)
        size = round(size, 2)

    if size <= 0 or size == 1:
        size = random.uniform(0.8, 1.8)
        size = round(size, 2)

    resOri = _getZoomedImg(img, size)

    if flag:
        parent_path = os.path.dirname(oriImg)
        if os.path.exists(parent_path + os.sep + 'jsons_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'jsons_')
        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]

        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName + '_zoom.jpg',
            resOri)

    else:
        d = dict()
        d['zoom'] = Ori_Pro(resOri, None)
        return d


def imgFlip(oriImg: str, flag=True, flip_list=[1, 0, -1]):
    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    h_ori = cv2.flip(img, 1)
    v_ori = cv2.flip(img, 0)
    h_v_ori = cv2.flip(img, -1)

    if flag:
        parent_path = os.path.dirname(oriImg)
        if os.path.exists(parent_path + os.sep + 'augimgs_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'augimgs_')
        # fileName = oriLabel.split(os.sep)[-1].replace('.json','')
        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]

        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_h.jpg', h_ori) if 1 in flip_list else do_nothing
        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_v.jpg', v_ori) if 0 in flip_list else do_nothing
        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_h_v.jpg', h_v_ori) if -1 in flip_list else do_nothing

    else:
        d = dict()
        d['h'] = Ori_Pro(h_ori, None)
        d['v'] = Ori_Pro(v_ori, None)
        d['h_v'] = Ori_Pro(h_v_ori, None)

        return d


def imgNoise(oriImg: str, flag=True):
    noise_type = ['gaussian', 'poisson', 's&p', 'speckle']
    l = np.random.randint(2, size=len(noise_type)).tolist()
    p = list(zip(noise_type, l))

    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    for i in p:
        if i[1] != 0:
            img = snoise.random_noise(img, mode=i[0])

    # print(np.max(img))
    # print(np.min(img))

    img = np.array(img * 255).astype(np.uint8)

    if flag:
        parent_path = os.path.dirname(oriImg)
        if os.path.exists(parent_path + os.sep + 'augimgs_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'augimgs_')
        # fileName = oriLabel.split(os.sep)[-1].replace('.json','')
        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]
        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_noise.jpg', img)

    else:
        d = dict()
        d['noise'] = Ori_Pro(img, None)

        return d


def imgRotation(oriImg: str, angle=30, scale=1, flag=True):

    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    imgShape = img.shape

    center = (0.5 * imgShape[1], 0.5 * imgShape[0])
    mat = cv2.getRotationMatrix2D(center, angle, scale)

    affedImg = cv2.warpAffine(img, mat, (imgShape[1], imgShape[0]))

    if flag:
        parent_path = os.path.dirname(oriImg)

        if os.path.exists(parent_path + os.sep + 'augimgs_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'augimgs_')

        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]
        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_noise.jpg', img)

    else:
        d = dict()
        d['rotation'] = Ori_Pro(affedImg, None)
        return d


def imgTranslation(oriImg: str, flag=True):
    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    else:
        img = oriImg

    imgShape = img.shape

    trans_h = random.randint(0, int(0.5 * imgShape[1]))
    trans_v = random.randint(0, int(0.5 * imgShape[0]))

    trans_mat = np.float32([[1, 0, trans_h], [0, 1, trans_v]])
    transImg = cv2.warpAffine(img, trans_mat, (imgShape[1], imgShape[0]))

    if flag:
        parent_path = os.path.dirname(oriImg)

        if os.path.exists(parent_path + os.sep + 'augimgs_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'augimgs_')

        tmp = os.path.splitext(oriImg)[0]
        fileName = tmp.split(os.sep)[-1]
        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_translation.jpg', img)

    else:
        d = dict()
        d['trans'] = Ori_Pro(transImg, None)

        return d


def aug(filepath, augs=['noise', 'rotation', 'trans', 'flip','zoom'], num=0):
    # augs = ['noise','rotation','trans','flip']

    l = np.random.randint(2, size=len(augs))

    if np.sum(l) == 0:
        l[0] = 1

    l = l.tolist()
    p = list(zip(augs, l))
    img = filepath

    for i in p:
        if i[1] == 1:
            if i[0] == 'noise':
                n = imgNoise(img, flag=False)
                tmp = n['noise']
                img = tmp.oriImg
                del n, tmp

            elif i[0] == 'rotation':
                angle = random.randint(0, 45)
                r = imgRotation(img, flag=False, angle=angle)
                tmp = r['rotation']
                img = tmp.oriImg

                del r, tmp

            elif i[0] == 'trans':
                t = imgTranslation(img, flag=False)
                tmp = t['trans']
                img = tmp.oriImg

                del t, tmp
            
            elif i[0] == 'zoom':
                zoomFactor = random.uniform(0.8, 1.8)
                z = imgZoom(img,zoomFactor,flag=False)
                tmp = z['zoom']
                img = tmp.oriImg

                del z,tmp


            elif i[0] == 'flip':
                imgList = []

                f = imgFlip(img, flag=False)
                tmp = f['h_v']
                imgList.append(tmp.oriImg)

                tmp = f['h']
                imgList.append(tmp.oriImg)

                tmp = f['v']
                imgList.append(tmp.oriImg)

                img = imgList

                del tmp, f, imgList


    parent_path = os.path.dirname(filepath)

    if os.path.exists(parent_path + os.sep + 'augimgs_'):
        pass
    else:
        os.makedirs(parent_path + os.sep + 'augimgs_')

    tmp = os.path.splitext(filepath)[0]
    fileName = tmp.split(os.sep)[-1]

    if isinstance(img, np.ndarray):
        io.imsave(
            parent_path + os.sep + 'augimgs_' + os.sep + fileName +
            '_{}_assumble.jpg'.format(num), img)

        logger.info("Done!")
        logger.info("see here {}".format(parent_path + os.sep + 'augimgs_'))

    elif isinstance(img, list):
        for i in range(0, len(img)):
            io.imsave(
                parent_path + os.sep + 'augimgs_' + os.sep + fileName +
                '_{}_assumble{}.jpg'.format(num, i), img[i])

        logger.info("Done!")
        logger.info("see here {}".format(parent_path + os.sep + 'augimgs_'))
