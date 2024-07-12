#!/usr/bin/env python3

# Register datasets with proof to avoid loading files each time
# Only needs to be done once, valied until the file is modified
#
# Taken (almost verbatim) from Nick Smith, U. Wisconsin
# https://github.com/nsmith-/ZHinvAnalysis/blob/master/register_proof_datasets.py

import ROOT
ROOT.gROOT.SetBatch(True)
import user_input
import argparse
import os

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--selection", type=str,
                        required=True, help="Specify the selection level "
                        "of the dataset. Used to form a unique name")
    return parser.parse_args()
args = getComLineArgs()
reRegister = True

ROOT.TProof.Open('workers=8')
# TProof::Open returns pointer to proof-lite and messes with pyroot's
# inability to call virtual base class members
# gProof is base class type, so no issues
proof = ROOT.gProof
current_path = os.getcwd()
os.chdir(sys.path[0])
datasets = user_input.readJson("../MetaData/ntuple_info.json")
for name, info in datasets.items():
    proof_name = '_'.join([name, args.selection])
    if proof.GetDataSet(proof_name) == None or reRegister :
        filelist = ROOT.TFileCollection(proof_name, proof_name)
        num_files = filelist.Add(info["file_path"])
        proof.RegisterDataSet(proof_name, filelist, 'OVnostagedcheck:')
os.chdir(current_path)

