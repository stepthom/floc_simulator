from ctypes import *
from ctypes import cdll
import time

import argparse
import pandas as pd
import os
import numpy as np
import sys
import random
from faker import Faker
import subprocess

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
args = parser.parse_args()


# The following functions are the interface to call a Go library.

class GoSlice(Structure):
    _fields_ = [("data", POINTER(c_void_p)),
                ("len", c_longlong), 
                ("cap", c_longlong)]
    
def get_cohortId(domains):
    #lib = cdll.LoadLibrary('./getcohortid.so')
    #a0 = [cast(c_char_p(s.encode('utf-8')),c_void_p) for s in domains]
    #a1 = (c_void_p * len(a0))(*a0)
    #_domains = GoSlice(a1,len(a1),len(a1))
    #return lib.get_cohortId(_domains)
    try:
        cmd = [ "./floc_simulation5" ] + domains
        p = subprocess.Popen(cmd, universal_newlines=True, bufsize=1)
        exit_code = p.wait()
    except Exception as e:
        print("Exception caught from cmd.")
        print(e)
        sys.exit(1)
        
    if exit_code != 0:
        print("Call to Go failed (exit code = {}). Exiting.".format(exit_code))
        sys.exit(1)
    
    with open('_tmp_cohortID.txt') as f:
        for line in f:
            cohortId = int(line)
            
    return cohortId
    
#lib = cdll.LoadLibrary('./getcohortid.so')


# Should return 21454
test_domains = [
    "www.nikkei.com",
    "jovi0608.hatenablog.com",
    "www.nikkansports.com",
    "www.yahoo.co.jp",
    "www.sponichi.co.jp",
    "www.cnn.co.jp",
    "floc.glitch.me",
    "html5.ohtsu.org"
]


print( get_cohortId(test_domains))
    


# User faker package to randomly generate data, where necessary
faker = Faker()

# Randomly generate N domains;

res = []

N = [20, 50, 100, 500, 1000]

NUM_ADDS = [1, 2, 5, 10]

trials = 32
trial_steps = 100

total = len(N) * len(NUM_ADDS) * trials
cur = 1

for n in N:
    for num_add in NUM_ADDS:
        for trial in range(trials):
            print("{} / {}".format(cur, total))
            cur = cur + 1
            domains = [faker.domain_name(levels=1) for i in range(n)]
            cohortId = get_cohortId(domains)

            matches = 0
            for i in range(trial_steps):
                _domains = domains + [faker.unique.domain_name(levels=1) for i in range(num_add)]
                new_cohortId = get_cohortId(_domains)

                if new_cohortId == cohortId:
                    matches = matches + 1

            res.append({
                'n': n,
                'num_add': num_add,
                'trial': trial,
                'matches': matches,
                'percent': matches / trial_steps,
            })
    
df = pd.DataFrame(res)
print(df)
df.to_csv('out.csv', index=False)