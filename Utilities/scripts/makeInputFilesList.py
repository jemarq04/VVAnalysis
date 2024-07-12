#!/usr/bin/env python3

# This script takes a directory as input and creates a new file (name 
# specifed by the user) with a list of filenames in the format required by 
# farmoutAnalysisJobs. 

#That is, containing a list of all the files in the directoy, one file 
# name per line. For filenames begining with /hdfs, /hdfs is removed. 
#
# Author: Kenneth Long, U. Wisconsin 01-10-2015

import glob
import argparse
import subprocess

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str,
                        required=True, help="Name of file containing file"
                        " to be created (containing list of files)")
    parser.add_argument("-p", "--file_path", type=str,
                        required=True, help="directory containing files")
    parser.add_argument("-r", "--only_root_files", action='store_true',
                        help="Only list .root files")
    return vars(parser.parse_args())
def makeFileList(output_file, file_path, only_root_files):
    out = subprocess.check_output(["hdfs", "dfs", "-ls", file_path.replace("/hdfs", "")], encoding="utf8")
    files = []
    for line in out.splitlines():
        split = line.split("/", 1)
        if len(split) != 2:
            continue
        else:
            files.append("/"+split[1])
    with open(output_file, "w") as file_list:
        for file_name in files:
            if only_root_files and ".root" not in file_name:
                continue
            file_list.write(file_name+"\n")
def main():
    args = getComLineArgs()
    makeFileList(args['output_file'], args['file_path'], args['only_root_files'])
if __name__ == "__main__":
    main()
