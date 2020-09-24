'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-08-24 09:39:42
LastEditors: xiaoshuyui
LastEditTime: 2020-08-24 09:51:29
'''
import sys
sys.path.append("..")
from convertmask.utils.xml2yolo.xml2yolo import x2yConvert
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.getcwd())) +os.sep + 'static' + os.sep + 'test_xmls'

if __name__ == "__main__":
    # single test

    sfile = BASE_DIR + os.sep + '1187_3.xml'

    x2yConvert(sfile)

    # multi file test

    x2yConvert(BASE_DIR+os.sep+'xmls')