#!/usr/bin/env python
import ROOT
import argparse
import os
import sys
from collections import OrderedDict
from python import ApplySelection
from python.prettytable import PrettyTable

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--selections", type=str,
                        required=True, help="Name of selections to apply, "
                        "separated by commas. They must be defined in "
                        "Cuts/<analysis>/<selection_name>.json")
    parser.add_argument("-t", "--trigger", type=str, default="",
                        choices=["DoubleEG", "DoubleMuon", "MuonEG", 
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
    parser.add_argument("-d", "--no_deduplicate", action='store_true',
                        help="Don't remove duplicated events from ntuple")
    return vars(parser.parse_args())
def writeNtupleToFile(output_file, tree, state, cut_string, deduplicate):
    state_dir = output_file.Get(state)
    if not state_dir:
        state_dir = output_file.mkdir(state)
    state_dir.cd()
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
    selector = ROOT.disambiguateFinalStates()
    zcand_name = "e1_e2_Mass" if state.count('e') >= 2 else "m1_m2_Mass"
    selector.setZCandidateBranchName(zcand_name)
    ApplySelection.setAliases(tree, state, "Cuts/%s/aliases.json" % analysis)
    tree.Process(selector, cut_string)
    entryList = selector.GetOutputList().FindObject('bestCandidates')
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
def skimNtuple(selections, analysis, trigger, filelist, output_file_name, deduplicate):
    ROOT.gROOT.SetBatch(True)
    output_file = ROOT.TFile(output_file_name, "RECREATE")
    ROOT.gROOT.cd()
    with open(filelist) as input_file:
        input_files = [('root://cmsxrootd.hep.wisc.edu/' + i.strip()) \
            if "store" in i[:6] else i.strip() for i in input_file.readlines()]
    metaTree = ROOT.TChain("metaInfo/metaInfo")
    for file_path in input_files:
        metaTree.Add(file_path)
    event_counts = OrderedDict({"Input" : {}})
    for selection_group in selections.split(";"):
        event_counts[selection_group] = {}
    states = []
    if "WZ" in analysis:
        states = ["eee", "eem", "emm", "mmm"]
    elif "ZZ" in analysis:
        states = ["eeee", "eemm", "mmmm"]
    selection_groups = selections.split(";")
    tmpfile = 0
    for state in states:
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
            cuts = ApplySelection.CutString()
            cuts.append(ApplySelection.buildCutString(state, 
                selection_group.split(","), analysis, trigger if i == 0 else "").getString())
            cut_string = cuts.getString()
            print("INFO: Cut string for channel %s is: %s" % (state, cut_string))
            ApplySelection.setAliases(tree, state, "Cuts/%s/aliases.json" % analysis)

            isFirstOfMultistep = (i == 0 and len(selection_groups) > 1)
            if applyDeduplicate:
                entryList = getDeduplicatedListForTree(tree, analysis, state, cut_string) \
                    if len(input_files) == 1 else getDeduplicatedListForChain(input_files, analysis, state, cut_string) 
                tree.SetEntryList(entryList)
            if not isFirstOfMultistep:
                event_counts[selection_group][state] = writeNtupleToFile(output_file, tree, state, 
                    cut_string, applyDeduplicate)
            else:
                event_counts[selection_group][state] = writeNtupleToFile(tmpfile, tree, state, 
                    cut_string, applyDeduplicate)
                tree = tmpfile.Get("%s/ntuple" % state)
        if tmpfile:
            tmpfile.Close()
    writeMetaTreeToFile(output_file, metaTree)
    event_info = PrettyTable(["Selection", "eee", "eem", "emm", "mmm"])
    for selection, events in event_counts.items():
        event_info.add_row([selection, events["eee"], events["eem"], events["emm"], events["mmm"]])
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
    skimNtuple(args['selections'], args['analysis'], args['trigger'], args['filelist'], 
        args['output_file_name'], not args['no_deduplicate'])
    exit(0)
if __name__ == "__main__":
    main()
