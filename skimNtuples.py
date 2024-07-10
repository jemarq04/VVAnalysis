#!/usr/bin/env python3
import ROOT
import argparse
import os
import json
import sys
from collections import OrderedDict
from Utilities.python import ApplySelection
from Utilities.python.prettytable import PrettyTable
import pdb

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--selections", type=str,
                        required=True, help="Name of selections to apply, "
                        "separated by commas. They must be"
                        " mapped to a cuts json via Cuts/definitions.json")
    parser.add_argument("-t", "--trigger", type=str, default="",
                        choices=["EGamma", "DoubleEG","DoubleMuon", "MuonEG", 
                            "SingleMuon", "SingleElectron", "MonteCarlo", ""],
                        help="Name of trigger to select in data")
    parser.add_argument("-f", "--filelist", type=str,
                        required=True, help="List of input file names "
                        "to be processed (separated by commas)")
    parser.add_argument("-a", "--analysis", type=str,
                        required=True, help="Analysis name, used"
                        " in selection the cut json")
    parser.add_argument("-o", "--output_file_name", type=str,
                        required=True, help="Name of output file")
    parser.add_argument("-gen", "--save_genTrees", action='store_true',
                        help="Save genTrees in the skim as well")
    parser.add_argument("-d", "--no_deduplicate", action='store_true',
                        help="Don't remove duplicated events from ntuple")
    return vars(parser.parse_args())
def writeNtupleToFile(output_file, tree, state, cut_string, deduplicate):
    state_dir = output_file.Get(state)
    if not state_dir:
        state_dir = output_file.mkdir(state)
    state_dir.cd()
    #pdb.set_trace()
    save_tree = tree.CopyTree(cut_string if not deduplicate else "")
    save_tree.Write()
    # Remove AutoSaved trees
    output_file.Purge()
    ROOT.gROOT.cd()
    entries = save_tree.GetEntries()
    #tree.Delete()
    #save_tree.Delete()
    return entries
def getDeduplicatedListForTree(tree, analysis, state, cut_string):
    if "WZ" in analysis or "ZplusL" in analysis:
        selector = ROOT.disambiguateFinalStatesZL()
        zcand_name = "e1_e2_Mass" if state.count('e') >= 2 else "m1_m2_Mass"
        selector.setZCandidateBranchName(zcand_name)
    else:
        selector = ROOT.disambiguateFinalStates()
        if state.count('e') > 2:
            l1_l2_cand_mass = "e1_e2_Mass"
            l1_cand_pt = "e1Pt"
            l2_cand_pt = "e2Pt"
            l3_l4_cand_mass = "e3_e4_Mass"
            l3_cand_pt = "e3Pt"
            l4_cand_pt = "e4Pt"
            l1_cand_Tight = "e1ZZTightIDNoVtx"
            l2_cand_Tight = "e2ZZTightIDNoVtx"
            l3_cand_Tight = "e3ZZTightIDNoVtx"
            l4_cand_Tight = "e4ZZTightIDNoVtx"
            l1_cand_Iso = "e1ZZIsoPass"
            l2_cand_Iso = "e2ZZIsoPass"
            l3_cand_Iso = "e3ZZIsoPass"
            l4_cand_Iso = "e4ZZIsoPass"
        elif state.count('m') > 2:
            l1_l2_cand_mass = "m1_m2_Mass"
            l1_cand_pt = "m1Pt"
            l2_cand_pt = "m2Pt"
            l3_l4_cand_mass = "m3_m4_Mass"
            l3_cand_pt = "m3Pt"
            l4_cand_pt = "m4Pt"
            l1_cand_Tight = "m1ZZTightIDNoVtx"
            l2_cand_Tight = "m2ZZTightIDNoVtx"
            l3_cand_Tight = "m3ZZTightIDNoVtx"
            l4_cand_Tight = "m4ZZTightIDNoVtx"
            l1_cand_Iso = "m1ZZIsoPass"
            l2_cand_Iso = "m2ZZIsoPass"
            l3_cand_Iso = "m3ZZIsoPass"
            l4_cand_Iso = "m4ZZIsoPass"
        else: 
            l1_l2_cand_mass = "e1_e2_Mass"
            l1_cand_pt = "e1Pt"
            l2_cand_pt = "e2Pt"
            l1_cand_Tight = "e1ZZTightIDNoVtx"
            l2_cand_Tight = "e2ZZTightIDNoVtx"
            l1_cand_Iso = "e1ZZIsoPass"
            l2_cand_Iso = "e2ZZIsoPass"
            l3_l4_cand_mass = "m1_m2_Mass"
            l3_cand_pt = "m1Pt"
            l4_cand_pt = "m2Pt"
            l3_cand_Tight = "m1ZZTightIDNoVtx"
            l4_cand_Tight = "m2ZZTightIDNoVtx"
            l3_cand_Iso = "m1ZZIsoPass"
            l4_cand_Iso = "m2ZZIsoPass"
        selector.setZCandidateBranchName(l1_l2_cand_mass,l1_cand_pt,l2_cand_pt,l3_l4_cand_mass,l3_cand_pt,l4_cand_pt,l1_cand_Tight,l2_cand_Tight,l3_cand_Tight,l4_cand_Tight,l1_cand_Iso,l2_cand_Iso,l3_cand_Iso,l4_cand_Iso)
    ApplySelection.setAliases(tree, state, "Cuts/%s/aliases.json" % analysis)
    tree.Process(selector, cut_string)
    entryList = selector.GetOutputList().FindObject('bestCandidates')
    print("selector: ",selector.GetStatus())
    return entryList
def getDeduplicatedListForChain(input_files, analysis, state, cut_string):
    fullEntryList = ROOT.TEntryList() 
    for i, input_file in enumerate(input_files):
        rtfile = ROOT.TFile.Open(input_file)
        tree = rtfile.Get("%s/ntuple" % state)
        entryList = getDeduplicatedListForTree(tree, analysis, state, cut_string) 
        entryList.SetName(rtfile.GetName())
        entryList.SetTreeNumber(i)
        entryList.SetTree(tree)
        fullEntryList.Add(entryList)
    return fullEntryList
def writeMetaTreeToFile(output_file, metaTree):
    output_file.cd()
    meta_dir = output_file.mkdir("metaInfo")
    meta_dir.cd()
    save_mt = metaTree.CopyTree("")
    save_mt.Write()
#Write Gen Trees to File
def writeGenTreeToFile(output_file, state,GenTree):
    Genstate=state+"Gen"
    Genstate_dir = output_file.Get(Genstate)
    if not Genstate_dir:
        Genstate_dir = output_file.mkdir(Genstate)
    Genstate_dir.cd()
    #pdb.set_trace()
    save_gt = GenTree.CopyTree("")
    save_gt.Write()
    # Remove AutoSaved trees
    output_file.Purge()
    ROOT.gROOT.cd()
def skimNtuple(selections, analysis, trigger, filelist, output_file_name,saveGenTrees, deduplicate):
    ROOT.gROOT.SetBatch(True)
    output_file = ROOT.TFile(output_file_name, "RECREATE")
    ROOT.gROOT.cd()
    with open(filelist) as input_file:
        input_files = [('root://cmsxrootd.hep.wisc.edu/' + i.strip()) \
            if "store" in i[:6] else i.strip() for i in input_file.readlines()]
        print(input_files)
    metaTree = ROOT.TChain("metaInfo/metaInfo")
    for file_path in input_files:
        metaTree.Add(file_path)
    #event_counts for writing the tree to the File with all selections together
    event_counts = OrderedDict({"Input" : {}})
    for selection_group in selections.split(";"):
        event_counts[selection_group] = {}
    states = []
    if "WZ" in analysis or "ZplusL" in analysis:
        states = ["eee", "eem", "emm", "mmm"]
    elif "ZZ" in analysis:
        states = ["eeee", "eemm", "mmmm"]
    selection_groups = selections.split(";")
    tmpfile = 0
    for state in states:
        if saveGenTrees:
            print("Saving GenTrees in the skimmed files")
            if len(input_files) > 1:
                Gentree = ROOT.TChain("%sGen/ntuple" % state)
                for file_path in input_files:
                    Gentree.Add(file_path)
            else: 
                input_file = ROOT.TFile.Open(input_files[0])
                Gentree = input_file.Get("%sGen/ntuple" % state)
            writeGenTreeToFile(output_file,state,Gentree)
        else:
            print("Skipping GenTrees in making skim")
        if len(input_files) > 1:
            tree = ROOT.TChain("%s/ntuple" % state)
            for file_path in input_files:
                tree.Add(file_path)
        else: 
            input_file = ROOT.TFile.Open(input_files[0])
            tree = input_file.Get("%s/ntuple" % state)
        event_counts["Input"][state] = tree.GetEntries()
        if len(selection_groups) > 1:
            tmpfile = ROOT.TFile("tmpfile.root", "UPDATE")
        for i, selection_group in enumerate(selection_groups):
            applyDeduplicate = deduplicate if i == 0 else False
            print(applyDeduplicate)
            print("selection_group: ", selection_group)
            cuts = ApplySelection.CutString()
            cuts.append(ApplySelection.buildCutString(state, 
                selection_group.split(","), analysis, trigger if i == 0 else "").getString())
            cut_string = cuts.getString()
            print("INFO: Cut string for channel %s is: %s" % (state, cut_string))
            ApplySelection.setAliases(tree, state, "Cuts/%s/aliases.json" % analysis)

            isFirstOfMultistep = (i == 0 and len(selection_groups) > 1)
            print(selection_group)
            if applyDeduplicate:
                print(cut_string)
                entryList = getDeduplicatedListForTree(tree, analysis, state, cut_string) \
                    if len(input_files) == 1 else getDeduplicatedListForChain(input_files, analysis, state, cut_string) 
                tree.SetEntryList(entryList)
            if not isFirstOfMultistep:
                event_counts[selection_group][state] = writeNtupleToFile(output_file, tree, state, 
                    cut_string, applyDeduplicate)
                print("Entries after each step: ", event_counts[selection_group][state]) 
            else:
                event_counts[selection_group][state] = writeNtupleToFile(tmpfile, tree, state, 
                    cut_string, applyDeduplicate)
                tree = tmpfile.Get("%s/ntuple" % state)
                print("Entries after first step: ", tree.GetEntries())
        if tmpfile:
            tmpfile.Close()
    writeMetaTreeToFile(output_file, metaTree)
    
    if "WZ" in analysis or "ZplusL" in analysis:
        event_info = PrettyTable(["Selection", "eee", "eem", "emm", "mmm"])
        for selection, events in event_counts.items():
            event_info.add_row([selection, events["eee"], events["eem"], events["emm"], events["mmm"]])
    elif "ZZ" in analysis:
        event_info = PrettyTable(["Selection", "eeee", "eemm", "mmmm"])
        for selection, events in event_counts.items():
            event_info.add_row([selection, events["eeee"], events["eemm"],events["mmmm"]])

    print("\nResults for selection: %s" % selections)
    if deduplicate:
        print("NOTE: Events deduplicated by choosing the ordering with m_l1_l2 " \
                "closest to m_{Z}^{PDG} \n      after selection: %s" % selections.split(";")[0])
    else:
        print("NOTE: Events NOT deduplicated! Event may appear in multiple rows of ntuple!\n")
    print(event_info.get_string())
    
    if tmpfile != 0:
        os.remove(tmpfile.GetName())
def main():
    args = getComLineArgs()
    print(args['filelist'])
    skimNtuple(args['selections'], args['analysis'], args['trigger'], args['filelist'], 
        args['output_file_name'], args['save_genTrees'], not args['no_deduplicate'])
    exit(0)
if __name__ == "__main__":
    main()
