#!/usr/bin/env python3
import configparser
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("variable", type=str)
args = parser.parse_args()
config_name = "Templates/config.%s" % os.environ["USER"]
if not os.path.isfile(config_name):
    raise RuntimeError("%s must point to a valid configuration file" % config_name)

config = configparser.ConfigParser()
config.read_file(open(config_name))
if not args.variable in config['Setup']:
    raise ValueError("variable %s does not exist in config file Template/config" % args.variable)

print(config['Setup'][args.variable])

