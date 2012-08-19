# distutils: language = c++
from libcpp.string cimport string
from libcpp.vector cimport vector

# cdef vector[int] intvect
# cdef intvec v = xrange(1, 10, 2)
# print v
cdef extern from "agent_src.h":
    cdef cppclass Attributes:
        vector[int] v

# cdef Attributes a
# a.v.push_back(5)
# print a.v
cdef class Blarg:
    cdef Attributes a
    def __cinit__(self):
        self.a.v = xrange(1, 10, 2)

    property v:
        def __get__(self):
            return self.a.v



