import argparse
import pandas as pd
import os
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
args = parser.parse_args()

faker = Faker()

start_domain = 0
start_category = 0
start_persona = 0
start_user = 0

#################################################################################
# Domains
#################################################################################
rows = []

for i in range(start_domain, args.n_domains):
    rows.append({
        'id': i,
        'domain': faker.unique.domain_name(levels=1)
    })

df_domains = pd.DataFrame(rows)

print('\nDomains head and shape:')
print(df_domains.head(10))
print(df_domains.shape)

#################################################################################
# Categories
#################################################################################

rows = []

for i in range(start_category, args.n_categories):
    
    _n_domains_in_category = 4
    _domain_ids = random.choices(list(df_domains['id']), k=_n_domains_in_category)
    
    rows.append({
        'id': i,
        'category': faker.unique.pystr(min_chars=3, max_chars=8),
        'domain_ids': _domain_ids,
    })

df_categories = pd.DataFrame(rows)

print('\nCategories head and shape:')
print(df_categories.head(10))
print(df_categories.shape)


#################################################################################
# Personas
#################################################################################

rows = []

for i in range(start_persona, args.n_personas):
    
    _n_categories_in_persona = 3
    _category_ids = random.sample(list(df_categories['id']), k=_n_categories_in_persona)
    
    rows.append({
        'id': i,
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
    
    _n_visited_domains = 4
    _sex = random.choice(['Male', 'Female'])
    if _sex == "Male":
        _first_name = faker.first_name_male()
    else:
        _first_name = faker.first_name_female()
        
    _persona = random.choice(df_personas['id'])
    
    _num_visted_domains = 3
    _visited_domain_ids = random.choices(df_domains['id'], k=_num_visted_domains)
    _visited_domain_names = list(df_domains.iloc[_visited_domain_ids,:]['domain'])
    
    rows.append({
        'id': i,
        'sex': _sex,
        'first_name': _first_name,
        'persona_id': _persona,
        'visited_domain_ids': _visited_domain_ids,
        'visited_domain_names': _visited_domain_names,
    })

df_users = pd.DataFrame(rows)

new_fn = "{}/users_tmp.csv".format(args.out_dir)
with open(new_fn, 'w') as the_file:
    for row in df_users['visited_domain_names']:
        the_file.write('{}\n'.format(" ".join(row)))
    

new_fn2 = "{}/ids_tmp.csv".format(args.out_dir)
print("Calling go program".format(new_fn))
try:
    cmd = [ "./floc_simulation4", new_fn, new_fn2 ]
    p = subprocess.Popen(cmd, universal_newlines=True, bufsize=1)
    exit_code = p.wait()
except Exception as e:
    print("Exception caught from cmd.")
    print(e)
    sys.exit(1)
    
if exit_code != 0:
    print("Call to Go failed (exit code = {}). Exiting.".format(exit_code))
    sys.exit(1)

df_cohort_ids = pd.read_csv(new_fn)
df_users['cohort_id'] = df_cohort_ids['cohort_id']

print('\nUsers head and shape:')
print(df_users.head(10))
print(df_users.shape)


new_fn = "{}/domains.csv".format(args.out_dir)
print("Writing file: {}".format(new_fn))
df_domains.to_csv(new_fn, index=False)

