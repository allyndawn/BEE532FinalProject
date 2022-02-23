# BEE532FinalProject
Final Project for B EE 532 Acoustics 2

## Initializing the Virtual Environment the First Time

```
pip3 install virtualenv
cd ~/Repos/BEE532FinalProject
virtualenv venv
source venv/bin/activate
pip install numpy
pip freeze > requirements.txt
```

## Bootstrapping it thereafter

```
cd ~/Repos/BEE532FinalProject
source venv/bin/activate
pip install -r requirements.txt
```

## Running the main

If running from visual studio, don't forget to [select the interpreter first](https://code.visualstudio.com/docs/python/python-tutorial#_select-a-python-interpreter) or

```
python3 __main__.py
```

