from distutils.core import setup
from Cython.Build import cythonize

import sys
# HACK for now
# ext_modules = [Extension(..., include_path=[numpy.get_include()])]
sys.argv = ['setup.py', 'build_ext', '--inplace']

setup(ext_modules=cythonize(
      "epistemic/agent_base.pyx",
      # sources=["Blarg.cpp"],
      language="c++",
      ))
