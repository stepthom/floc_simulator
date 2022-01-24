# FLOC Simulation

How "sensitive" are the cohortIDs: given a string of domains, how often do changes "change" the cohortID?


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

## Building the Go Program

To build the go program, type:

```
go build -buildmode=c-shared -o getcohortid.so getcohortid.go
```

## Running the Simulation

The simulation can be run with a command like the following:

```
python sim1.py
```
