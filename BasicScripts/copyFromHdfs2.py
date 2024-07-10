#!/usr/bin/env python

import argparse
import glob
import os
import subprocess
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="path to files in hdfs")
parser.add_argument("--eos", action='store_true', help="Store files on eos instead of /data")
parser.add_argument("-s", "--selection", type=str, default="FinalSelection",
        help="Selection tier (default FinalSelection)")
args = parser.parse_args()
#maindir = glob.glob(args.path)
#subdir=[]
#print maindir
#for Dir in maindir:
#    subdir+=os.listdir(Dir)
for directory in glob.glob(args.path):
#for subDir in subdir:
    #directory=os.path.join(maindir[0],subDir)
    print("Copying directory", directory)
    if not os.path.isdir(directory):
        print("Invalid filename: %s" % directory)
        exit(1)
    dirs = directory.split("/")
    print("dirs:",dirs)
    dir_name = dirs[-2]
    if dir_name[:3] == "000" and len(dirs)>= 5:
        if "/hdfs" in directory:
            dir_name = "_".join(dirs[6:8])
        else:
            dir_name = "_".join(dirs[5:7])
    print("dir_name: ",dir_name)
    #new_dir = "/data/%s/ZZAnalysis_2018-03-14/%s/%s" % (os.getlogin(), args.selection.strip("/"), dir_name)
    #new_dir = "/data/%s/SkimmedZZNtuples_mc_2018-03-06_hadd/%s/%s" % (os.getlogin(), args.selection.strip("/"), dir_name)
    new_dir = "/data/%s/ZZRun2SkimmedFiles/ZplusL2016AnalysisJobs_2019-09-12/%s/%s"%(os.getlogin(), args.selection.strip("/"), dir_name)
    if args.eos:
        new_dir = "/".join(["/eos/user", os.getlogin()[0], os.getlogin(), args.selection, dir_name])
    if os.path.isdir(new_dir):
        print("Copying into existing directory, hopefully not duplicating")
    else:
        try:
            os.mkdir(new_dir)
        except OSError as e:
            print(e)
            continue
    filenames = [f if "hdfs" not in f else f[5:] for f in glob.glob(directory + "/*.root")]
    p = multiprocessing.Pool(processes=10)
    p.map(subprocess.call, [["xrdcp", 
            "root://cmsxrootd.hep.wisc.edu/%s" % filename, 
            new_dir] for filename in filenames]
        )
