'''
@lanhuage: python
@Descripttion: 
@version: beta
@Author: xiaoshuyui
@Date: 2020-07-10 10:09:24
@LastEditors: xiaoshuyui
@LastEditTime: 2020-07-10 14:17:16
'''
from utils import __version__
import os
from setuptools import setup,find_packages
import pypandoc



def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname),encoding='utf-8')
# long_description = pypandoc.convert_file(os.path.join(os.path.dirname(__file__), 'README.md'), 'rst')
# requestments = open_file('requirements.txt')

setup(
    name='convertmask',
    version=__version__,
    author='Chengxi GU',
    author_email='guchengxi1994@qq.com',
    packages = find_packages(),
    long_description_content_type='text/markdown',
    # extras_require={'speedup': ['python-levenshtein>=0.12']},
    url='https://github.com/guchengxi1994/mask2json',
    license="Apache License",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires = [
        'labelme==4.2.9',
        'numpy==1.18.4',
        'opencv_python==4.1.0.25',
        'xmltodict==0.12.0',
        'matplotlib==3.1.0',
        'scikit_image==0.15.0',
        'Pillow==7.1.2',
        'PyYAML==5.3.1',
        'scipy==1.5.1'
    ],
    description='mask imgs to labelme jsons,and so on',
    long_description=open_file('README.md').read(),
    zip_safe=True,
    # packages = find_packages()
    entry_points={
    'console_scripts':[
    'convertmask = mask2json.m2j:script'
    ]
    },
)