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
parser.add_argument('--pre-domains', type=str, default="pre_domains.csv")
parser.add_argument('--n-domains', type=int, default=10)
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


#################################################################################
# Pre-defined, not random domains
#################################################################################

pre = pd.read_csv(args.pre_domains)
start_domain = pre.shape[0]

#################################################################################
# Domains
#################################################################################
rows = pre.to_dict(orient='records')

for i in range(start_domain, start_domain+args.n_domains):
    
    rows.append({
        'domain_id': i,
        'domain': faker.unique.domain_name(levels=1),
        'rank': i,
    })

df_domains = pd.DataFrame(rows)
df_domains = df_domains.sort_values('domain_id')

print('\nDomains head and shape:')
print(df_domains.head(15))
print(df_domains.shape)
df_domains.to_csv('sim1_domains.csv', index=False)


res = []

# Number of trials 
T = 1000

# Number of visted domains (to start) per user
D = [50, 100, 500, 1000]

# Percentage of added/new domains per trial
A = [.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50]

_weights = np.array(1./df_domains['rank'])

for d in D:
    for trial in range(T):
        print("{} {} / {}".format(d, trial, T))
        user1_domains = random.choices(
            population = df_domains['domain'], 
            weights = _weights,
            k=d)
        user1_cohortId = get_cohortId(user1_domains)
    
        for per_add in A:
            
                num_add = round(per_add * d)
        
                user2_domains = user1_domains + random.choices(
                    population = df_domains['domain'], 
                    weights = _weights,
                    k=num_add)
                user2_cohortId = get_cohortId(user2_domains)
   
                match = 0
                if user1_cohortId == user2_cohortId:
                    match = 1

                res.append({
                    'd': d,
                    'trial': trial,
                    'per_add': per_add,
                    'num_add': num_add,
                    'user1_cohortId': user1_cohortId,
                    'user2_cohortId': user2_cohortId,
                    'match': match,
                })
    
df = pd.DataFrame(res)
print(df)
df.to_csv('sim1_out.csv', index=False)