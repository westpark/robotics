#
# Do just enough hackery to invoke the virtualenv
# while running as sudo
#
import os, sys
base_dir = os.path.dirname(os.path.abspath(__file__))
activate_this = os.path.join(base_dir, "/home/pi/.virtualenvs/piwars/bin/activate_this.py")
with open(activate_this) as f:
  exec(f.read(), dict(__file__=activate_this))

import runpy
modulename = sys.argv[1]
sys.argv = sys.argv[0:1] + sys.argv[2:]
runpy.run_module(modulename)
