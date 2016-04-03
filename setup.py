#!/usr/bin/python
# -*- coding: latin-1 -*-

"""Setup script."""
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import surfaceimagecontentgap
    version = surfaceimagecontentgap.__version__
except ImportError:
    version = 'Undefined'

requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(requirements_file) as f:
    requirements = [line.rstrip('\n')
                    for line in f
                    if line and not line.startswith('#')]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Utilities'
]
packages = ['surfaceimagecontentgap']
entry_points = {
        'console_scripts': [
            'image-gap = surfaceimagecontentgap.imagegap:main',
            ]
        }
setup(
      name='SurfaceImageContentGap',
      version=version,
      author='Pierre-Selim Huard',
      author_email='ps.huard@gmail.com',
      url='http://github.com/Commonists/SurfaceImageContentGap',
      description='R&D project to surface articles with most views that are lacking illustration on Wikipedia. Currently it supports two kind of search, searching articles without images given from a category or including a given template.',
      long_description=open('README.md').read(),
      license='MIT',
      packages=packages,
      entry_points=entry_points,
      install_requires=requirements,
      classifiers=classifiers
)
