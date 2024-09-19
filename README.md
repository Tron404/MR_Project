# MR_Project

Welcome to our project's repo! Below you will see instructions on how to set up and use our code.

## Instalation

It is highly recommended that you set up a virtual environment to ensure there are no dependecy conflicts. You can either use a standard Python virtual environment or a Conda environment:

**Python venv**
```
python -m venv /path/to/new/virtual/env
```
**Conda**
```
conda create -n <env-name> python=3.12
```

Our project was created using version `3.12.x` of Python. The main libraries we used are VEDO and Trimesh, for 3D shape displaying and processing. They and all the necessary dependencies are listed in the `requirements.txt` file, which can be used as follows:

```
pip install -r requirements.txt
```

## Running the code

You can run the main part of the code using this code:

```
python main.py
```
