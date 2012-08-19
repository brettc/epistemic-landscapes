from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize(
      "epistemic/agent_base.pyx",
      # sources=["Blarg.cpp"],
      language="c++",
      ))
