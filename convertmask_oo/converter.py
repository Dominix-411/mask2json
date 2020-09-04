'''
lanhuage: python
Descripttion: 
version: beta
Author: xiaoshuyui
Date: 2020-09-04 15:46:04
LastEditors: xiaoshuyui
LastEditTime: 2020-09-04 16:20:42
'''

from .entity.logger import logger


class Converter(object):
    def __init__(self,ori_folder_or_path:str,methods:list,
                mask_folder_or_path:str='',labelPath:str=''):
        self.ori_folder_or_path = ori_folder_or_path
        self.methods = methods
        self.mask_folder_or_path = mask_folder_or_path
        self.labelPath = labelPath

        logger.info("proceed {} on {}".format("".join(methods),ori_folder_or_path))

    
    def __str__(self):
        return """
                m2j     short for masks to jsons. 
                m2x     short for masks to xmls. 
                j2m     short for jsons to masks. 
                j2x     short for json to xml.
                aug     image augmentation. 
                """
    
    def _m2j(self,*args=None):
        pass

    def _m2x(self,*args=None):
        pass

    def _j2m(self,*args=None):
        pass

    def _j2x(self,*args=None):
        pass

    def _aug(self,*args=None):
        pass

    

        

        