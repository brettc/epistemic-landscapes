import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    # Otherwise, we import it locally. This forces it to load
    __import__(module[:-3], locals(), globals())
del module
