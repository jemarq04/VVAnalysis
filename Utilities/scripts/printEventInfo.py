#!/usr/bin/env python3
import ROOT
import argparse
import os
from python import ConfigureJobs
import datetime

parser = argparse.ArgumentParser() 
parser.add_argument("-f", "--filelist", 
                    type=lambda x : [i.strip() for i in x.split(',')],
                    required=True, help="List of input file names "
                    "to be processed (separated by commas)")
parser.add_argument("-s", "--selection", required=True)
parser.add_argument("-p", "--printEventNums", action='store_true')
parser.add_argument("-d", "--checkDuplicates", action='store_true')
parser.add_argument("-m", "--cut_string", required=False, type=str,
                    default="")
parser.add_argument("-c", "--channels", required=True,
                    choices=["eee", "eem", "emm", "mmm"])
args = parser.parse_args()

