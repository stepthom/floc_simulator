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
parser.add_argument('--n-personas', type=int, default=10)
parser.add_argument('--n-users', type=int, default=100)
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
# Personas
#################################################################################

rows = []

for i in range(start_persona, args.n_personas):
    
    _n_categories_in_persona = 3
    _category_ids = random.sample(list(df_categories['category_id']), k=_n_categories_in_persona)
    
    rows.append({
        'persona_id': i,
        'persona': faker.unique.pystr(min_chars=3, max_chars=8),
        'category_ids': _category_ids,
    })

df_personas = pd.DataFrame(rows)

print('\nPersonas head and shape:')
print(df_personas.head(10))
print(df_personas.shape)


#################################################################################
# Users
#################################################################################

rows = []


for i in range(start_user, args.n_users):
    
    print("User {}/{}".format(i, args.n_users))
    
    #_n_visited_domains = random.randint(a=5, b=100)
    _n_visited_domains = 20
    
    _persona_id = random.choice(df_personas['persona_id'])
    _category_ids = df_personas.iloc[_persona_id,]['category_ids']
    
    _cohort_ids = []
    
   # Now, figure out the probability of visiting each domain. The prob is affected by:
   # - The domain's rank: higher if rank is lower, lower otherwise
   # - The domain's category: higher if category is in user's persona, lower otherwise
    _weights = np.array(1./df_domains['rank'])
    _cat_weights = np.array([0.99 if x in _category_ids else 0.01 for x in df_domains['category_id'] ])
    _weights = _weights * _cat_weights
    
    for week_id in range(52):
        
        _visited_domain_ids = random.choices(
            population = df_domains['domain_id'], 
            weights = _weights,
            k=_n_visited_domains)

        _visited_domain_names = list(df_domains.loc[df_domains.index[_visited_domain_ids],'domain'])

        _cohort_id = get_cohortId(_visited_domain_names)
        _cohort_ids.append(_cohort_id)
        
    num_unique = len(set(_cohort_ids))
      
    rows.append({
        'user_id': i,
        'persona_id': _persona_id,
        'num_unique_cohort_ids': num_unique,
        'per_unique_cohort_ids': (num_unique/52.),
        'per_same_cohort_ids': (1. - (num_unique/52.)),
     })

    
df = pd.DataFrame(rows)
new_fn = "{}/user_weeks.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df.to_csv(new_fn, index=False)