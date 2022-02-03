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
parser.add_argument('--n-domains', type=int, default=10)
parser.add_argument('--n-categories', type=int, default=10)
parser.add_argument('--n-users', type=int, default=1000)
parser.add_argument('-o', '--out-dir', type=str, default="out")
parser.add_argument('--pre-domains', type=str, default="pre_domains.csv")
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
pre_cats = list(pre['category'].unique())

start_domain = pre.shape[0]
start_category = len(pre_cats)
start_persona = 0
start_user = 0

#################################################################################
# Categories
#################################################################################

rows = []

for i in range(len(pre_cats) + args.n_categories):
    
    #_n_domains_in_category = random.randint(a=2, b=20)
    #_domain_ids = random.choices(list(df_domains['id']), k=_n_domains_in_category)
  
    if i < len(pre_cats):
        _category = pre_cats[i]
    else:
        _category = faker.unique.pystr(min_chars=3, max_chars=8)
    
    rows.append({
        'category_id': i,
        'category': _category,
        #'domain_ids': _domain_ids,
    })

df_categories = pd.DataFrame(rows)

print('\nCategories head and shape:')
print(df_categories.head(10))
print(df_categories.shape)

#################################################################################
# Domains
#################################################################################
rows = pre.to_dict(orient='records')

for i in range(start_domain, start_domain+args.n_domains):
    
    rows.append({
        'domain_id': i,
        'domain': faker.unique.domain_name(levels=1),
        'category': random.choice(df_categories['category']),
        'rank': i,
    })

df_domains = pd.DataFrame(rows)
df_domains = df_domains.merge(df_categories, on='category', how='inner')
df_domains = df_domains.sort_values('domain_id')

print('\nDomains head and shape:')
print(df_domains.head(15))
print(df_domains.shape)



#################################################################################
# Users
#################################################################################

rows = []

NUM_WEEKS = 52

for i in range(start_user, args.n_users):
    
    if i % 10 == 0:
        print("User {}/{}  ({:.2f}%)".format(i, args.n_users, 100*(i/args.n_users)))
    
    #_n_visited_domains = random.randint(a=5, b=100)
    _n_visited_domains = 40
    
    _cohort_ids = []
    
    _weights = np.array(1./df_domains['rank'])
    
    _visited_domain_names = random.choices(
        population = df_domains['domain'], 
        weights = _weights,
        k=_n_visited_domains)
    
    for week_id in range(NUM_WEEKS):
        
        _num_to_add = random.randint(a=0, b=2)
        _num_to_remove = random.randint(a=0, b=2)
        
        _added = random.choices(
            population = df_domains['domain'], 
            weights = _weights,
            k=_num_to_add)
        
        _removed = random.choices(
            population = _visited_domain_names,
            k=_num_to_remove)
        
        _visited_domain_names2 = _visited_domain_names + _added
        
        if len(_removed) > 0:
            _visited_domain_names2 = [x for x in _visited_domain_names if x not in _removed]
        
        _cohort_id = get_cohortId(_visited_domain_names2)
        _cohort_ids.append(_cohort_id)
        
    num_unique = len(set(_cohort_ids))
      
    rows.append({
        'user_id': i,
        'num_unique_cohort_ids': num_unique,
        'per_unique_cohort_ids': (num_unique/NUM_WEEKS),
        'per_same_cohort_ids': (1. - (num_unique/NUM_WEEKS)),
        'cohort_ids': _cohort_ids,
     })

    
df = pd.DataFrame(rows)
new_fn = "{}/sim3_user_weeks.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df.to_csv(new_fn, index=False)