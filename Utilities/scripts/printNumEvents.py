#!/usr/bin/env python3
import ROOT
import argparse
import os
from python import ConfigureJobs,ApplySelection
from python.prettytable import PrettyTable
import datetime

parser = argparse.ArgumentParser() 
parser.add_argument("-f", "--filelist", 
                    type=lambda x : [i.strip() for i in x.split(',')],
                    required=True, help="List of input file names "
                    "to be processed (separated by commas)")
parser.add_argument("-s", "--selection", required=True)
parser.add_argument("--output_selection", required=False, default="")
parser.add_argument("-p", "--printEventNums", action='store_true')
parser.add_argument("--latex", action='store_true', help='table in latex format')
parser.add_argument("-t", "--printTrigger", action='store_true')
parser.add_argument("--printDetail", action='store_true')
parser.add_argument("-d", "--checkDuplicates", action='store_true')
parser.add_argument("-m", "--cut_string", required=False, type=str,
                    default="")
parser.add_argument("-c", "--channels", required=False, type=str,
                    default="eee,eem,emm,mmm")
parser.add_argument("-o", "--output_dir", required=False, type=str,
                    #default="/eos/user/k/kelong/WZAnalysisData/SyncWithJakob")
                    default="/eos/user/k/kelong/WZAnalysisData/SyncWithCarlos")
args = parser.parse_args()
isfile = any(os.path.isfile(name) or os.path.exists(name.rstrip("/*")) 
                for name in args.filelist)
filelist = ConfigureJobs.getListOfFiles(args.filelist, args.selection) if \
    not isfile else args.filelist
states = [x.strip() for x in args.channels.split(",")]
state_yields = dict((i,0) for i in ["eee", "emm", "eem", "mmm"])
totals = dict((i,0) for i in ["eee", "emm", "eem", "mmm"])
totals["processed"] = 0
total = 0
if args.checkDuplicates:
    eventArray = []
metaChain = ROOT.TChain("metaInfo/metaInfo")

if args.output_selection == "":
    args.output_selection = args.selection
output_dir = ""
if args.printEventNums:
    output_dir = '/'.join([args.output_dir, 
            "EventYields_Kenneth_{:%Y-%m-%d}".format(datetime.date.today()),
            args.output_selection])

event_info = PrettyTable(["Filename", "eee", "eem", "emm", "mmm", "All states", "Total processed"])
for name in filelist:
    if not isfile:
        try:
            file_path = ConfigureJobs.getInputFilesPath(name, 
                args.selection, "WZxsec2016")
        except ValueError as e:
            print(e)
            continue
    else:
        file_path = name
    if output_dir != "":
        try:
            os.makedirs(output_dir + "/" + name)
        except OSError as e:
            print(e)
            pass
    print("Results for file %s" % name)
    print("File path is %s" % file_path)
    metaChain.Add(file_path)
    state_yields["processed"] = 0
    for state in states:
        state = state.strip()
        chain = ROOT.TChain("%s/ntuple" % state)
        chain.Add(file_path)
        ApplySelection.setAliases(chain, state, "Cuts/WZxsec2016/aliases.json")
        cut_tree = chain
        num_events = cut_tree.GetEntries(args.cut_string)
        print("Number of events in state %s is %i" % (state, num_events))
        if args.printEventNums or args.printDetail or args.printTrigger or args.checkDuplicates:
            cut_tree = chain.CopyTree(args.cut_string) if args.cut_string != "" \
                else chain
            file_name = 'WZEvents_{selection}_{name}_{chan}.txt'.format(
                    selection=args.output_selection, name=name, chan=(state if args.channels != "" else ""))
            output_file = file_name if output_dir == "" else "/".join([output_dir, name, file_name])
            if args.printEventNums:
                outfile = open(output_file, "wa")
            outfile.write("# Made with cut: %s\n" % args.cut_string)
            for row in cut_tree:
                eventId = '{0}:{1}:{2}'.format(row.run, row.lumi,row.evt)
                if args.printEventNums:
                    outfile.write(eventId+'\n')
                if args.printTrigger or args.printDetail:
                    print("-"*20 + eventId + "_"*20)
                    if args.printTrigger:
                        print("singleMu: ", row.singleMuPass)
                        print("singleIsoMu: ", row.singleIsoMuPass)
                        print("singleE: ", row.singleEPass)
                        print("doubleE: ", row.doubleEPass)
                        print("doubleMu: ", row.doubleMuPass)
                    if args.printDetail:
                        if state == "emm":
                            print("ePt :", row.ePt)
                            print("m1Pt :", row.m1Pt)
                            print("m2Pt :", row.m2Pt)
                            print("Zmass :", row.m1_m2_Mass)
                if args.checkDuplicates:
                    if eventId in eventArray:
                        print("Duplicate: %s" % eventId)
                    else:
                        eventArray.append(eventId)
        state_yields[state] = num_events
        totals[state] += num_events
        total += num_events
    for row in metaChain:
        state_yields["processed"] += row.nevents
        totals["processed"] += row.nevents
    event_info.add_row([name, state_yields["eee"], state_yields["eem"], state_yields["emm"],
        state_yields["mmm"], sum(list(state_yields.values())[:-1]), state_yields["processed"]])
    print("Number of events in all states is %i" % total)
event_info.add_row(["All files", totals["eee"], totals["eem"], totals["emm"], totals["mmm"], sum(list(totals.values())[:-1]), totals["processed"]])

print("")
print("Results for all files:")
total = 0
for state, count in totals.items():
    if state == "processed": continue
    print("Summed events for all files in %s state is %i" % (state, count))
    total += count
print("Summed events for all files in all states is %i" % total)
print("A total of %i events were processed from the dataset" % totals["processed"])
if args.latex:
    print(event_info.get_latex_string(hrules=0))
else:
    print(event_info)

if args.printEventNums:
    file_name = "summary.txt"
    summary_file = file_name if output_dir == "" else "/".join([output_dir, file_name])
    with open(summary_file, "wa") as summary:
        summary.write(str(event_info))

