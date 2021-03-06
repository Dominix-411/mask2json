'''
@lanhuage: python
@Descripttion:  (1)get a json file, an origin image \n
                (2)make a convertion \n
                (3)get corresponding json file and converted image
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-17 15:09:27
LastEditors: xiaoshuyui
LastEditTime: 2020-10-20 10:53:35
'''

import sys
sys.path.append('..')
# import warnings
from skimage import io
import skimage.util.noise as snoise
from skimage import morphology
import cv2
import os
from .json2mask.convert import processor
from .getMultiShapes import getMultiShapes
from .methods.img2base64 import imgEncode
from .methods import rmQ ,entity
import traceback
from .methods.entity import *
import numpy as np
import shutil
import json
from .methods.logger import logger
import random
from convertmask.utils.xml2json.xml2json import x2jConvert_pascal
from convertmask.utils.json2xml.json2xml import j2xConvert
from scipy import ndimage

import convertmask.utils.methods.configUtils as ccfg
LOGFlag = ccfg.getConfigParam(ccfg.cfp,'log','show')
del ccfg

kernel = np.ones((5, 5), np.uint8)


def _getZoomedImg(img, size):
    # pass
    if len(img.shape) == 3:
        zoomImg = ndimage.zoom(img, (size, size, 1), order=1)
    else:
        zoomImg = ndimage.zoom(img, size)
    # return zoomImg
    oriImgShape = img.shape
    zoomImgShape = zoomImg.shape
    # print(zoomImgShape)
    if size > 1:
        vDis = zoomImgShape[0] - oriImgShape[0]
        hDis = zoomImgShape[1] - oriImgShape[1]

        vDisHalf = int(vDis * 0.5)
        hDisHalf = int(hDis * 0.5)

        res = zoomImg[vDisHalf:zoomImgShape[0] + vDisHalf - vDis,
                      hDisHalf:zoomImgShape[1] + hDisHalf - hDis]
    elif size < 1:
        # return zoomImg
        vDis = abs(zoomImgShape[0] - oriImgShape[0])
        hDis = abs(zoomImgShape[1] - oriImgShape[1])
        vDisHalf = int(vDis * 0.5)
        hDisHalf = int(hDis * 0.5)

        res = cv2.copyMakeBorder(zoomImg,
                                 vDisHalf,
                                 vDis - vDisHalf,
                                 hDisHalf,
                                 hDis - hDisHalf,
                                 cv2.BORDER_CONSTANT,
                                 value=[0, 0, 0])
    return res


def _splitImg(maskImg):
    maxLabel = np.max(maskImg)
    # print(maxLabel)
    maskImgs = []
    if maxLabel == 0:
        pass
    else:
        for num in range(1, maxLabel + 1):
            tmp = maskImg.copy()
            tmp[tmp != num] = 0
            tmp[tmp != 0] = 255

            closing = cv2.morphologyEx(tmp, cv2.MORPH_CLOSE, kernel)  # remove small connected area
            
            closing[closing != 0] = num
            maskImgs.append(Img_clasId(closing, num))

            del tmp, closing
    return maskImgs


def imgDistort(oriImg: str, oriLabel: str, flag=True):
    pass


def imgZoom(oriImg: str, oriLabel: str, size: float = 0, flag=True):
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
        logger.error('input {} type {} error'.format('oriImg',type(oriImg)))
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

    if isinstance(oriLabel, str):
        mask = processor(oriLabel, flag=True)
    elif isinstance(oriLabel, np.ndarray):
        mask = oriLabel
    else:
        raise TypeError(
            "input parameter 'oriLabel' type {} is not supported".format(
                type(oriLabel)))

    maskImgs = _splitImg(mask)
    resMask = np.zeros((resOri.shape[0], resOri.shape[1]))
    if len(maskImgs) > 0:
        for m in maskImgs:
            # print(m.img.shape)
            res = _getZoomedImg(m.img, size)
            res[res > 0] = m.clasId
            res[res != m.clasId] = 0
            resMask += res
    resMask = resMask.astype(np.uint8)

    if np.max(resMask) == 0:
        logger.warning('After zoom,none ROIs detected! Zoomfactor={} maybe too large.'.format(size))
        # return

    if flag:
        parent_path = os.path.dirname(oriLabel)
        if os.path.exists(parent_path + os.sep + 'jsons_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json', '')

        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName + '_zoom.jpg',
            resOri)

        zoomedMask_j = getMultiShapes(parent_path + os.sep + 'jsons_' +
                                      os.sep + fileName + '_zoom.jpg',
                                      resMask,
                                      flag=True,
                                      labelYamlPath='')
        saveJsonPath = parent_path + os.sep + 'jsons_' + os.sep + fileName + '_zoom.json'
        if zoomedMask_j is not None:
            with open(saveJsonPath, 'w') as f:
                f.write(zoomedMask_j)
            logger.info('Done! See {} .'.format(saveJsonPath)) if LOGFlag == 'True' else entity.do_nothing()
        else:
            pass

    else:
        d = dict()
        # print(resOri.shape)
        d['zoom'] = Ori_Pro(resOri, resMask)
        return d


def imgFlip(oriImg: str, oriLabel: str, flip_list=[1, 0, -1], flag=True):
    """
    flipList: flip type. see cv2.flip :
    1: 水平翻转 \n
    0: 垂直翻转 \n
    -1: 同时翻转 \n
    >>> import cv2
    >>> help(cv2.flip)
    """
    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    elif isinstance(oriImg, np.ndarray):
        img = oriImg
    else:
        logger.error('input {} type error'.format(imgFlip))
        return

    try:
        if len(flip_list) > 1 and (1 in flip_list or 0 in flip_list
                                   or -1 in flip_list):
            # mask = processor(oriLabel,flag=True)
            if isinstance(oriLabel, str):
                mask = processor(oriLabel, flag=True)
            elif isinstance(oriLabel, np.ndarray):
                mask = oriLabel
            else:
                raise TypeError(
                    "input parameter 'oriLabel' type is not supported")
            # print(type(mask))
            h_ori = cv2.flip(img, 1)
            v_ori = cv2.flip(img, 0)
            h_v_ori = cv2.flip(img, -1)

            h_mask = cv2.flip(mask, 1) if 1 in flip_list else None
            v_mask = cv2.flip(mask, 0) if 0 in flip_list else None
            h_v_mask = cv2.flip(mask, -1) if -1 in flip_list else None
            """
            maybe dict zip is better :)
            """

            if flag:
                parent_path = os.path.dirname(oriLabel)
                if os.path.exists(parent_path + os.sep + 'jsons_'):
                    pass
                else:
                    os.makedirs(parent_path + os.sep + 'jsons_')
                fileName = oriLabel.split(os.sep)[-1].replace('.json', '')

                io.imsave(
                    parent_path + os.sep + 'jsons_' + os.sep + fileName +
                    '_h.jpg', h_ori) if 1 in flip_list else do_nothing()
                io.imsave(
                    parent_path + os.sep + 'jsons_' + os.sep + fileName +
                    '_v.jpg', v_ori) if 0 in flip_list else do_nothing()
                io.imsave(
                    parent_path + os.sep + 'jsons_' + os.sep + fileName +
                    '_h_v.jpg', h_v_ori) if -1 in flip_list else do_nothing()

                h_j = getMultiShapes(
                    parent_path + os.sep + 'jsons_' + os.sep + fileName +
                    '_h.jpg',
                    h_mask,
                    flag=True,
                    labelYamlPath='') if h_mask is not None else None
                # h_j = getMultiShapes(parent_path+os.sep+'jsons_'+os.sep+fileName+'_h.jpg',h_mask,flag=True,labelYamlPath='D:\\testALg\\mask2json\\mask2json\\multi_objs_json\\info.yaml')
                v_j = getMultiShapes(
                    parent_path + os.sep + 'jsons_' + os.sep + fileName +
                    '_v.jpg',
                    v_mask,
                    flag=True,
                    labelYamlPath='') if v_mask is not None else None
                h_v_j = getMultiShapes(
                    parent_path + os.sep + 'jsons_' + os.sep + fileName +
                    '_h_v.jpg',
                    h_v_mask,
                    flag=True,
                    labelYamlPath='') if h_v_mask is not None else None

                for saveJsonPath in [
                        parent_path + os.sep + 'jsons_' + os.sep + fileName +
                        '_h.json', parent_path + os.sep + 'jsons_' + os.sep +
                        fileName + '_v.json', parent_path + os.sep + 'jsons_' +
                        os.sep + fileName + '_H_V.json'
                ]:

                    # if saveJsonPath is not None:
                    # print(saveJsonPath)
                    if saveJsonPath.endswith('_h.json'):
                        if h_j is not None:
                            with open(saveJsonPath, 'w') as f:
                                f.write(h_j)
                        else:
                            pass
                    elif saveJsonPath.endswith('_v.json'):
                        if v_j is not None:
                            with open(saveJsonPath, 'w') as f:
                                f.write(v_j)
                        else:
                            pass
                    elif saveJsonPath.endswith('_H_V.json'):
                        if h_v_j is not None:
                            with open(saveJsonPath, 'w') as f:
                                f.write(h_v_j)
                        else:
                            pass

                    rmQ.rm(saveJsonPath) if os.path.exists(
                        saveJsonPath) else do_nothing()

                return ""
            else:

                d = dict()
                d['h'] = Ori_Pro(h_ori, h_mask)
                d['v'] = Ori_Pro(v_ori, v_mask)
                d['h_v'] = Ori_Pro(h_v_ori, h_v_mask)

                return d

        else:
            logger.warning("<===== param:flip_list is not valid =====>")

    except Exception:
        # print(e)
        print(traceback.format_exc())


def imgNoise(oriImg: str, oriLabel: str, flag=True):
    """
    see skimage.util.random_noise    
    """
    noise_type = ['gaussian', 'poisson', 's&p', 'speckle']

    l = np.random.randint(2, size=len(noise_type)).tolist()
    # print(l)
    p = list(zip(noise_type, l))

    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    elif isinstance(oriImg, np.ndarray):
        img = oriImg
    else:
        logger.error('input {} type error'.format(imgFlip))
        return

    for i in p:
        if i[1] != 0:
            img = snoise.random_noise(img, mode=i[0])

    img = np.array(img * 255).astype(np.uint8)

    if flag:
        parent_path = os.path.dirname(oriLabel)
        if os.path.exists(parent_path + os.sep + 'jsons_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json', '')

        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName + '_noise.jpg',
            img)

        try:
            if isinstance(oriLabel, str):
                shutil.copyfile(
                    oriLabel, parent_path + os.sep + 'jsons_' + os.sep +
                    fileName + '_noise.json')

                base64code = imgEncode(parent_path + os.sep + 'jsons_' +
                                       os.sep + fileName + '_noise.jpg')

                with open(
                        parent_path + os.sep + 'jsons_' + os.sep + fileName +
                        '_noise.json', 'r') as f:
                    load_dict = json.load(f)

                load_dict['imageData'] = base64code

                with open(
                        parent_path + os.sep + 'jsons_' + os.sep + fileName +
                        '_noise.json', 'w') as f:
                    # json.dump(load_dict,parent_path+os.sep+'jsons_'+os.sep+fileName+'_noise.json')
                    f.write(json.dumps(load_dict))

            elif isinstance(oriLabel, np.ndarray):
                """
                labeled file can be an Image
                """
                noisedMask_j = getMultiShapes(parent_path + os.sep + 'jsons_' +
                                              os.sep + fileName + '_noise.jpg',
                                              oriLabel,
                                              flag=True,
                                              labelYamlPath='')
                with open(
                        parent_path + os.sep + 'jsons_' + os.sep + fileName +
                        '_noise.json', 'w') as f:
                    f.write(json.dumps(noisedMask_j))

        except Exception:
            print(traceback.format_exc())

    else:
        d = dict()
        # mask = processor(oriLabel,flag=True)
        if isinstance(oriLabel, str):
            mask = processor(oriLabel, flag=True)
        elif isinstance(oriLabel, np.ndarray):
            mask = oriLabel
        else:
            raise TypeError(
                "input parameter 'oriLabel' type {} is not supported".format(
                    type(oriLabel)))
        d['noise'] = Ori_Pro(img, mask)

        return d


def imgRotation(oriImg: str, oriLabel: str, angle=30, scale=1, flag=True):
    """
    旋转
    """
    logger.warning(
        'rotation may cause salt-and-pepper noise. in order to solve this issue, small objects may be missing!'
    )
    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    elif isinstance(oriImg, np.ndarray):
        img = oriImg
    else:
        logger.error('input {} type error'.format(imgFlip))
        return

    imgShape = img.shape

    if isinstance(oriLabel, str):
        mask = processor(oriLabel, flag=True)
    elif isinstance(oriLabel, np.ndarray):
        mask = oriLabel
    else:
        raise TypeError(
            "input parameter 'oriLabel' type {} is not supported".format(
                type(oriLabel)))

    center = (0.5 * imgShape[1], 0.5 * imgShape[0])
    mat = cv2.getRotationMatrix2D(center, angle, scale)

    affedImg = cv2.warpAffine(img, mat, (imgShape[1], imgShape[0]))
    affedMask = cv2.warpAffine(mask, mat, (imgShape[1], imgShape[0]))

    if flag:
        parent_path = os.path.dirname(oriLabel)

        if os.path.exists(parent_path + os.sep + 'jsons_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json', '')

        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName +
            '_rotation.jpg', affedImg)

        affedMask_j = getMultiShapes(parent_path + os.sep + 'jsons_' + os.sep +
                                     fileName + '_rotation.jpg',
                                     affedMask,
                                     flag=True,
                                     labelYamlPath='')

        saveJsonPath = parent_path + os.sep + 'jsons_' + os.sep + fileName + '_rotation.json'

        if affedMask_j is not None:
            with open(saveJsonPath, 'w') as f:
                f.write(affedMask_j)
        else:
            pass

    else:
        d = dict()
        d['rotation'] = Ori_Pro(affedImg, affedMask)

        return d


def imgTranslation(oriImg: str, oriLabel: str, flag=True):
    """
    image translation
    """
    if isinstance(oriImg, str):
        if os.path.exists(oriImg):
            img = io.imread(oriImg)
        else:
            raise FileNotFoundError('Original image not found')
    elif isinstance(oriImg, np.ndarray):
        img = oriImg
    else:
        logger.error('input {} type error'.format(imgFlip))
        return

    imgShape = img.shape

    if isinstance(oriLabel, str):
        mask = processor(oriLabel, flag=True)
    elif isinstance(oriLabel, np.ndarray):
        mask = oriLabel
    else:
        raise TypeError(
            "input parameter 'oriLabel' type {} is not supported".format(
                type(oriLabel)))

    trans_h = random.randint(0, int(0.5 * imgShape[1]))
    trans_v = random.randint(0, int(0.5 * imgShape[0]))

    trans_mat = np.float32([[1, 0, trans_h], [0, 1, trans_v]])

    transImg = cv2.warpAffine(img, trans_mat, (imgShape[1], imgShape[0]))
    transMask = cv2.warpAffine(mask, trans_mat, (imgShape[1], imgShape[0]))

    if flag:
        parent_path = os.path.dirname(oriLabel)

        if os.path.exists(parent_path + os.sep + 'jsons_'):
            pass
        else:
            os.makedirs(parent_path + os.sep + 'jsons_')
        fileName = oriLabel.split(os.sep)[-1].replace('.json', '')

        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName +
            '_translation.jpg', transImg)
        transMask_j = getMultiShapes(parent_path + os.sep + 'jsons_' + os.sep +
                                     fileName + '_translation.jpg',
                                     transMask,
                                     flag=True,
                                     labelYamlPath='')

        saveJsonPath = parent_path + os.sep + 'jsons_' + os.sep + fileName + '_translation.json'

        if transMask_j is not None:
            with open(saveJsonPath, 'w') as f:
                f.write(transMask_j)
        else:
            pass

    else:
        d = dict()
        d['trans'] = Ori_Pro(transImg, transMask)

        return d


def aug_labelme(filepath, jsonpath, augs=None, num=0):
    """
    augs: ['flip','noise','affine','rotate','...']
    """
    default_augs = ['noise', 'rotation', 'trans', 'flip','zoom']
    if augs is None:
        augs = ['noise', 'rotation', 'trans', 'flip','zoom']

    # elif not isinstance(augs,list):
    else:
        if not isinstance(augs, list):
            try:
                augs = list(str(augs))
            except:
                raise ValueError(
                    "parameter:aug's type is wrong. expect a string or list,got {}"
                    .format(str(type(augs))))
        # else:
        augs = list(set(augs).intersection(set(default_augs)))

        if len(augs) > 0 and augs is not None:
            pass
        else:
            logger.warning(
                'augumentation method is not supported.using default augumentation method.'
            )
            augs = ['noise', 'rotation', 'trans', 'flip','zoom']

    # l = np.random.randint(2,size=len(augs)).tolist()

    if 'flip' in augs:
        augs.remove('flip')
        augs.append('flip')

    l = np.random.randint(2, size=len(augs))

    if np.sum(l) == 0:
        l[0] = 1

    l[l != 1] = 1

    l = l.tolist()

    p = list(zip(augs, l))

    img = filepath
    processedImg = jsonpath

    for i in p:
        # if i[0]!='flip':
        if i[1] == 1:
            if i[0] == 'noise':
                n = imgNoise(img, processedImg, flag=False)
                tmp = n['noise']
                img, processedImg = tmp.oriImg, tmp.processedImg

                del n, tmp

            elif i[0] == 'rotation':
                angle = random.randint(-45, 45)
                r = imgRotation(img, processedImg, flag=False, angle=angle)
                tmp = r['rotation']
                img, processedImg = tmp.oriImg, tmp.processedImg

                del r, tmp

            elif i[0] == 'trans':
                t = imgTranslation(img, processedImg, flag=False)
                tmp = t['trans']
                img, processedImg = tmp.oriImg, tmp.processedImg

                del t, tmp

            elif i[0] == 'zoom':
                zoomFactor = random.uniform(0.8, 1.8)
                z = imgZoom(img,processedImg,zoomFactor,flag=False)
                # print(type(z))
                tmp = z['zoom']
                img = tmp.oriImg

                del z,tmp

            elif i[0] == 'flip':
                imgList = []
                processedImgList = []

                f = imgFlip(img, processedImg, flag=False)

                tmp = f['h_v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['h']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                img, processedImg = imgList, processedImgList

                del tmp, f, imgList, processedImgList

    parent_path = os.path.dirname(filepath)

    if os.path.exists(parent_path + os.sep + 'jsons_'):
        pass
    else:
        os.makedirs(parent_path + os.sep + 'jsons_')

    # fileName = jsonpath.split(os.sep)[-1].replace(".json", '')
    (_,fileName) = os.path.split(jsonpath)
    fileName = fileName.replace(".json", '')

    if isinstance(img, np.ndarray):
        io.imsave(
            parent_path + os.sep + 'jsons_' + os.sep + fileName +
            '_{}_assumble.jpg'.format(num), img)
        assumbleJson = getMultiShapes(parent_path + os.sep + 'jsons_' +
                                      os.sep + fileName +
                                      '_{}_assumble.jpg'.format(num),
                                      processedImg,
                                      flag=True,
                                      labelYamlPath='')
        saveJsonPath = parent_path + os.sep + 'jsons_' + os.sep + fileName + '_{}_assumble.json'.format(
            num)
        with open(saveJsonPath, 'w') as f:
            f.write(assumbleJson)

        print("Done!")
        print("see here {}".format(parent_path + os.sep + 'jsons_'))

    elif isinstance(img, list):
        for i in range(0, len(img)):
            io.imsave(
                parent_path + os.sep + 'jsons_' + os.sep + fileName +
                '_{}_assumble{}.jpg'.format(num, i), img[i])
            assumbleJson = getMultiShapes(parent_path + os.sep + 'jsons_' +
                                          os.sep + fileName +
                                          '_{}_assumble{}.jpg'.format(num, i),
                                          processedImg[i],
                                          flag=True,
                                          labelYamlPath='')
            saveJsonPath = parent_path + os.sep + 'jsons_' + os.sep + fileName + '_{}_assumble{}.json'.format(
                num, i)
            with open(saveJsonPath, 'w') as f:
                f.write(assumbleJson)

        print("Done!")
        print("see here {}".format(parent_path + os.sep + 'jsons_'))


def aug_labelimg(filepath, xmlpath, augs=None, num=0):
    default_augs = ['noise', 'rotation', 'trans', 'flip','zoom']
    if augs is None:
        augs = ['noise', 'rotation', 'trans', 'flip','zoom']

    # elif not isinstance(augs,list):
    else:
        if not isinstance(augs, list):
            try:
                augs = list(str(augs))
            except:
                raise ValueError(
                    "parameter:aug's type is wrong. expect a string or list,got {}"
                    .format(str(type(augs))))
        # else:
        augs = list(set(augs).intersection(set(default_augs)))

        if len(augs) > 0 and augs is not None:
            pass
        else:
            logger.warning(
                'augumentation method is not supported.using default augumentation method.'
            )
            augs = ['noise', 'rotation', 'trans', 'flip','zoom']

    # l = np.random.randint(2,size=len(augs)).tolist()

    if 'flip' in augs:
        augs.remove('flip')
        augs.append('flip')

    l = np.random.randint(2, size=len(augs))

    if np.sum(l) == 0:
        l[0] = 1

    l[l != 1] = 1

    l = l.tolist()
    # print(l)

    p = list(zip(augs, l))

    img = filepath
    # processedImg = xmlpath

    jsonpath = x2jConvert_pascal(xmlpath, filepath)
    processedImg = jsonpath

    # logger.warning(processedImg)
    for i in p:
        # if i[0]!='flip':
        if i[1] == 1:
            if i[0] == 'noise':
                n = imgNoise(img, processedImg, flag=False)
                tmp = n['noise']
                img, processedImg = tmp.oriImg, tmp.processedImg

                del n, tmp

            elif i[0] == 'rotation':
                angle = random.randint(-45, 45)
                r = imgRotation(img, processedImg, flag=False, angle=angle)
                tmp = r['rotation']
                img, processedImg = tmp.oriImg, tmp.processedImg

                del r, tmp

            elif i[0] == 'trans':
                t = imgTranslation(img, processedImg, flag=False)
                tmp = t['trans']
                img, processedImg = tmp.oriImg, tmp.processedImg

                del t, tmp
            
            elif i[0] == 'zoom':
                zoomFactor = random.uniform(0.8, 1.8)
                z = imgZoom(img,processedImg,zoomFactor,flag=False)
                tmp = z['zoom']
                img = tmp.oriImg

                del z,tmp

            elif i[0] == 'flip':
                imgList = []
                processedImgList = []

                f = imgFlip(img, processedImg, flag=False)

                tmp = f['h_v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['h']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                tmp = f['v']
                imgList.append(tmp.oriImg)
                processedImgList.append(tmp.processedImg)

                img, processedImg = imgList, processedImgList

                del tmp, f, imgList, processedImgList

    parent_path = os.path.dirname(filepath)

    if os.path.exists(parent_path + os.sep + 'xmls_'):
        pass
    else:
        os.makedirs(parent_path + os.sep + 'xmls_')

    # fileName = jsonpath.split(os.sep)[-1].replace(".json", '')

    (_,fileName) = os.path.split(jsonpath)
    fileName = fileName.replace(".json", '')

    if isinstance(img, np.ndarray):
        io.imsave(
            parent_path + os.sep + 'xmls_' + os.sep + fileName +
            '_{}_assumble.jpg'.format(num), img)
        assumbleJson = getMultiShapes(parent_path + os.sep + 'xmls_' + os.sep +
                                      fileName +
                                      '_{}_assumble.jpg'.format(num),
                                      processedImg,
                                      flag=True,
                                      labelYamlPath='')
        saveJsonPath = parent_path + os.sep + 'xmls_' + os.sep + fileName + '_{}_assumble.json'.format(
            num)
        with open(saveJsonPath, 'w') as f:
            f.write(assumbleJson)

        j2xConvert(saveJsonPath)
        os.remove(saveJsonPath)
        print("Done!")
        print("see here {}".format(parent_path + os.sep + 'xmls_'))

    elif isinstance(img, list):
        for i in range(0, len(img)):
            io.imsave(
                parent_path + os.sep + 'xmls_' + os.sep + fileName +
                '_{}_assumble{}.jpg'.format(num, i), img[i])
            assumbleJson = getMultiShapes(parent_path + os.sep + 'xmls_' +
                                          os.sep + fileName +
                                          '_{}_assumble{}.jpg'.format(num, i),
                                          processedImg[i],
                                          flag=True,
                                          labelYamlPath='')
            saveJsonPath = parent_path + os.sep + 'xmls_' + os.sep + fileName + '_{}_assumble{}.json'.format(
                num, i)
            with open(saveJsonPath, 'w') as f:
                f.write(assumbleJson)

            j2xConvert(saveJsonPath)
            os.remove(saveJsonPath)

        print("Done!")
        print("see here {}".format(parent_path + os.sep + 'xmls_'))
