# FLOC Simulation

Randomly create domains, categories, users, and user visits, and compute the FLOC cohort IDs for each user.


## Go/Python environment setup

First, make sure you are using the Python version/installation you want. Python 3.8+ is recomended. 

On the CAC Frontenac cluster, use the `module` system. Run the following commands (or better yet, add to your '.bashrc' file):

```
module load StdEnv/2020
module load python/3.9.6
module load nixpkgs/16.09
module load go/1.14.4
```

Double check that you have the right version of Python:

```
which python
python --version
```

Next, set up a virtual environment called, e.g., `floc_env`:

```
python -m venv ./floc_env
source ./floc_env/bin/activate
```

Never commit the resulting virtual environment folder (in the case, named `floc_env`) to this git repository. An easy way to ensure that
you don't is to add the folder name to the `.gitignore` file.

Install packages as needed; use `requirements.txt` file for best results:

```
pip install --upgrade pip
pip install -r requirements.txt
```

## Building the Go Program

To build the go program, type:

```
go build
```

After building, it should create an executable file named "floc_simulation4" in the current directory.

## Running the Simulation

The simulation can be run with a command like the following:

```
python gen_users.py --n-domains 1000 --n-categories 100 --n-personas 100 --n-users 10000 --out-dir ./out
```

replacing the values as desired.

To see all available options, run:

```
python get_users.py --help
```

The results of the simulation will be present in the output directory specified (`./out` in the example above).

For a really big scenario run:


```
python gen_users.py --n-domains 1000 --n-categories 100 --n-personas 500 --n-users 100000 --out-dir ./out
```

