# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
import sys
import os

version = '0.0.1'

if __name__ == '__main__':
    setup(
        name='poolparser',
        version=version,
        description="A library to parse data from the city of Montreal",
        author='Mathieu Leduc-Hamel',
        author_email='mathieu@mtlpy.prg',
        license='LGPL',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'pdfminer', 
            'BeautifulSoup'
            ],
        entry_points="""
        [console_scripts]
        pinfo = poolparser.parser:pinfo
        """
        )
