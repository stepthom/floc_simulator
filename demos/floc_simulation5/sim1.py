from ctypes import *
from ctypes import cdll
import time

lib = cdll.LoadLibrary('./getcohortid.so')
    
class GoSlice(Structure):
    _fields_ = [("data", POINTER(c_void_p)),
                ("len", c_longlong), ("cap", c_longlong)]
    
def get_cohortId(domains):
    a0 = [cast(c_char_p(s.encode('utf-8')),c_void_p) for s in domains]
    a1 = (c_void_p * len(a0))(*a0)
    _domains = GoSlice(a1,len(a1),len(a1))
    return lib.get_cohortId(_domains)
    
c = get_cohortId([
  "www.nikkei.com",
  "yes.hatenablog.com",
  "nikkansports.com",
  "yahoo.co.jp",
  "sponichi.co.jp",
  "cnn.co.jp",
  "floc.glitch.me",
  "ohtsu.org"
])

print(c)
    
