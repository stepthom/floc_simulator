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
    
    _n_visited_domains = random.randint(a=5, b=100)
    
    _sex = random.choice(['Male', 'Female'])
    if _sex == "Male":
        _first_name = faker.first_name_male()
    else:
        _first_name = faker.first_name_female()
    _last_name = faker.last_name()
        
    _persona = random.choice(df_personas['persona_id'])
    
    # Now, figure out the probability of visiting each domain. The prob is affected by:
    # - The domain's rank: higher if rank is lower, lower otherwise
    # - The domain's category: higher if category is in user's persona, lower otherwise
    
    _weights = np.array(1./df_domains['rank'])
    
    _category_ids = df_personas.iloc[_persona,]['category_ids']
    _cat_weights = np.array([0.99 if x in _category_ids else 0.01 for x in df_domains['category_id'] ])
    _weights = _weights * _cat_weights
    
    _visited_domain_ids = random.choices(
        population = df_domains['domain_id'], 
        weights = _weights,
        k=_n_visited_domains)
    
    _visited_domain_names = list(df_domains.loc[df_domains.index[_visited_domain_ids],'domain'])
    
    rows.append({
        'user_id': i,
        'sex': _sex,
        'first_name': _first_name,
        'last_name': _last_name,
        'persona_id': _persona,
        'visited_domain_ids': _visited_domain_ids,
        'visited_domain_names': _visited_domain_names,
    })

df_users = pd.DataFrame(rows)

# Calling our Go program to calcualte cohort IDs.
# Acutally calling a go executable from Python is hard; so we take a simple workaround:
# - This file outputs a file with domains for each user
# - This file spawns a subprocess, which runs the go executable and reads above file and outputs results
# - This file reads in results and appends to df_users dataframe

domains_fn = "{}/_domains.txt".format(args.out_dir)
ids_fn     = "{}/_ids.csv".format(args.out_dir)
with open(domains_fn, 'w') as the_file:
    for row in df_users['visited_domain_names']:
        the_file.write('{}\n'.format(" ".join(row)))
    

print("Calling go program..")
try:
    cmd = [ "./floc_simulation4", domains_fn, ids_fn ]
    p = subprocess.Popen(cmd, universal_newlines=True, bufsize=1)
    exit_code = p.wait()
except Exception as e:
    print("Exception caught from cmd.")
    print(e)
    sys.exit(1)
    
if exit_code != 0:
    print("Call to Go failed (exit code = {}). Exiting.".format(exit_code))
    sys.exit(1)

print("Done.")

df_cohort_ids = pd.read_csv(ids_fn)
df_users['cohort_id'] = df_cohort_ids['cohort_id']


print('\nUsers head and shape:')
print(df_users.head(10))
print(df_users.shape)

#################################################################################
# Print Results
#################################################################################

new_fn = "{}/domains.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df_domains.to_csv(new_fn, index=False)

new_fn = "{}/categories.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df_categories.to_csv(new_fn, index=False)

new_fn = "{}/personas.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df_personas.to_csv(new_fn, index=False)

new_fn = "{}/users_small.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df_users.to_csv(new_fn, index=False, columns=['user_id', 'persona_id', 'cohort_id'])

new_fn = "{}/users.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df_users.to_csv(new_fn, index=False)
