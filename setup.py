# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------
# !/usr/bin/env python

from distutils.core import setup
import os


def get_all_pck(_path):
    return __get_packages__(os.walk(_path).next(), 'plugin')


def __get_packages__(_tree, _path):
    _packages = []
    if _tree[2].count('__init__.py') > 0 and len(_tree[1]) > 0:
        for _subpackage in _tree[1]:
            _packages.extend(
                __get_packages__(os.walk(os.path.join(_path, _subpackage)).next(), _path + '.' + _subpackage))
    _packages.append(_path)
    return _packages


packages = ['pyFind']
packages.extend(get_all_pck('plugin'))
print packages
setup(name='pyFind',
      version='0.01',
      description='pyFind Framework',
      author='Christian Garbers',
      author_email='christian@stuebeweg50.de',
      url='http://www.atomkraftprotz.de',
      packages=packages, requires=['numpy', 'scipy']
      )
