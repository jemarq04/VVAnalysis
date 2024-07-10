# coding: utf-8
import ROOT
import glob

def checkduplicates(events):
    print("Number of not deduplicated events in all datasets", len(events))
    print("Number of deduplicated events in all datasets", len(set(events)))

def buildevents(state, datasets, deduplicate=False):
    chain = ROOT.TChain("%s/ntuple" % state)
    for i in glob.glob(datasets):
        chain.Add(str(i)+"/*")
    
    events = []
    event_map = {}
    for i in chain:
        if deduplicate:
            if "DoubleMuon" in datasets:
                if not (i.doubleMuPass):
                    continue
            elif "MuonEG" in datasets:
                if not ((i.singleESingleMuPass or i.singleMuSingleEPass) and not i.doubleMuPass):
                    continue
            elif "SingleMuon" in datasets:
                if not ((i.singleMuPass or i.singleIsoMuPass) and not (i.doubleMuPass or i.singleESingleMuPass or i.singleMuSingleEPass)):
                    continue
            else:
                if not (i.singleESingleMuPass or i.singleMuSingleEPass or i.doubleMuPass or i.singleMuPass or i.singleIsoMuPass):
                    continue
        events.append('{0}:{1}:{2}'.format(i.run,i.lumi,i.evt))
        event_map.update({'{0}:{1}:{2}'.format(i.run,i.lumi,i.evt) : 
            i.GetFile().GetName() +
            "\n\tPass DoubleMuon = %s" % i.doubleMuPass +
            "\n\tPass DoubleMuDZ = %s" % i.doubleMuDZPass +
            "\n\tPass SingleMuon = %s" % i.singleMuPass +
            "\n\tPass SingleIsoMuon = %s" % i.singleIsoMuPass +
            "\n\tPass SingleMuSingleE = %s" % i.singleMuSingleEPass +
            "\n\tPass SingleESingleMu = %s" % i.singleESingleMuPass
    })
    return events,event_map

allevents = []
events,event_map = buildevents("mmm", "Wselection/2017-05-29-data_*Muon*")
checkduplicates(events)
    
print("\n", "-"*80)
print("DoubleMuon")
events, _ = buildevents("mmm", "Wselection/2017-05-29-data_DoubleMuon*")
checkduplicates(events)
print("    DoubleMuon Deduplicated")
events, _ = buildevents("mmm", "Wselection/2017-05-29-data_DoubleMuon*", True)
checkduplicates(events)
allevents += events

print("\n", "-"*80)
print("MuonEG")
events, _ = buildevents("mmm", "Wselection/2017-05-29-data_MuonEG*")
checkduplicates(events)
print("    MuonEG Deduplicated")
events, _ = buildevents("mmm", "Wselection/2017-05-29-data_MuonEG*", True)
checkduplicates(events)
allevents += events

print("\n", "-"*80)
print("SingleMuon")
events, _ = buildevents("mmm", "Wselection/2017-05-29-data_SingleMuon*")
checkduplicates(events)
print("    MuonEG Deduplicated")
events, _ = buildevents("mmm", "Wselection/2017-05-29-data_SingleMuon*", True)
checkduplicates(events)
allevents += events

print("*"*80)
print("    For all files")
checkduplicates(allevents)

missingevents = set(event_map.keys()).difference(set(allevents))
with open("details.txt", "w") as eventfile:
    for i in missingevents:
        eventfile.write("{0} -- {1}\n".format(i,event_map[i]))
