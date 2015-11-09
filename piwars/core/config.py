# -*- coding: utf-8 -*-
import os, sys
import configparser
import warnings

#
# Look for a global .ini in the current directory. If none is
# there, raise an exception and exit. Look for a local .ini
# in the same directory. If that isn't present, issue a warning
# but carry on and use the global values
#
global_filepath = os.path.abspath("piwars.ini")
if not os.path.isfile(global_filepath):
    warnings("No global ini found at %s" % global_filepath)
local_filepath = os.path.join(os.path.dirname(global_filepath), "piwars.local.ini")
if not os.path.isfile(local_filepath):
    warnings.warn("No local ini found at %s" % local_filepath)

ini = configparser.ConfigParser()
ini.read([global_filepath, local_filepath])

#
# Since we already have code which expects to find a set of simple
# module constants, keep that approach alive. This does however preclude 
# the easy possibility of a reload-while-running
#
LISTEN_ON_IP = ini['network']['listen_on_ip']
LISTEN_ON_PORT = ini['network']['listen_on_port']
CODEC = ini['i18n']['codec']
