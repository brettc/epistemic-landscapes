# distutils: language = c++
from libcpp.string cimport string
from libcpp.vector cimport vector

cdef extern from "agent_src.h":
    cdef cppclass Attributes:
        vector[int] v
        string s

# cdef Attributes a
# a.v.push_back(5)
# print a.v
cdef class Blarg:
    cdef Attributes a
    def __cinit__(self, list x):
        self.a.v = x
        self.a.s = 'blarg'

    property v:
        def __get__(self):
            return self.a.v

    property s:
        def __get__(self):
            return self.a.s
            # return self.a.s


