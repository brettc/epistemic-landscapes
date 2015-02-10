# Epistemic Landscapes

Get python:

You'll need python installed, plus numpy: http://www.numpy.org/.
To save yourself the pain of installing these packages, 
I highly recommend just getting the Anaconda python distribution 
from https://store.continuum.io/cshop/anaconda/.

Clone the code and install the dependencies.
(if git looks scary, then download the GUI: 
http://git-scm.com/downloads/guis)

```
$ git clone https://github.com/brettc/epistemic-landscapes 
$ cd epistemic-landscapes
$ sh setup.sh
```

Try running one of files in the example folder. Maybe read it first, 
as the output (by default) goes to the ~/Desktop folder.
```
$ python run_simulation.py examples/basic.cfg
```

Want to add some new strategies? Check out ./epistemic/agent.py. 
You can create a new class for an agent, just override the "step" method. 
You can specify this new class in the config file.





